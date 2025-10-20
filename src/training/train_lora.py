"""LoRA training infrastructure using PEFT and QLoRA."""

import logging
import torch
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType,
)
from datasets import load_dataset, Dataset
import bitsandbytes as bnb

logger = logging.getLogger(__name__)


@dataclass
class LoRATrainingConfig:
    """Configuration for LoRA training."""
    
    # Model
    base_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    
    # LoRA parameters
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    
    # Quantization
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    use_nested_quant: bool = True
    
    # Training
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    max_grad_norm: float = 0.3
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    
    # Optimization
    optim: str = "paged_adamw_8bit"
    weight_decay: float = 0.001
    
    # Logging
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 100
    
    # Output
    output_dir: str = "./models/adapters"
    
    # Data
    max_seq_length: int = 2048


class LoRATrainer:
    """Trainer for LoRA adapters."""
    
    def __init__(self, config: LoRATrainingConfig):
        """Initialize LoRA trainer.
        
        Args:
            config: Training configuration
        """
        self.config = config
        self.tokenizer = None
        self.model = None
        
        logger.info(f"Initializing LoRA Trainer with base model: {config.base_model}")
    
    def load_model(self) -> None:
        """Load and prepare model for training."""
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        logger.info("Loading base model...")
        
        # Quantization config
        if self.config.use_4bit:
            from transformers import BitsAndBytesConfig
            
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
                bnb_4bit_compute_dtype=getattr(torch, self.config.bnb_4bit_compute_dtype),
                bnb_4bit_use_double_quant=self.config.use_nested_quant,
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.base_model,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.base_model,
                device_map="auto",
                trust_remote_code=True,
            )
        
        # Prepare for k-bit training
        if self.config.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
        
        # Configure LoRA
        logger.info("Configuring LoRA...")
        peft_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
        )
        
        self.model = get_peft_model(self.model, peft_config)
        self.model.print_trainable_parameters()
        
        logger.info("Model loaded and configured for LoRA training")
    
    def prepare_dataset(
        self,
        dataset_path: Path,
        dataset_type: str = "sft"
    ) -> Dataset:
        """Prepare dataset for training.
        
        Args:
            dataset_path: Path to dataset file (jsonl)
            dataset_type: Type of dataset (sft, dpo)
            
        Returns:
            Prepared dataset
        """
        logger.info(f"Loading dataset from {dataset_path}")
        
        # Load dataset
        if dataset_path.suffix == ".jsonl":
            dataset = load_dataset("json", data_files=str(dataset_path), split="train")
        else:
            raise ValueError(f"Unsupported dataset format: {dataset_path.suffix}")
        
        logger.info(f"Loaded {len(dataset)} examples")
        
        # Tokenize dataset
        if dataset_type == "sft":
            dataset = self._prepare_sft_dataset(dataset)
        elif dataset_type == "dpo":
            dataset = self._prepare_dpo_dataset(dataset)
        else:
            raise ValueError(f"Unsupported dataset type: {dataset_type}")
        
        return dataset
    
    def _prepare_sft_dataset(self, dataset: Dataset) -> Dataset:
        """Prepare supervised fine-tuning dataset.
        
        Args:
            dataset: Raw dataset with 'messages' field
            
        Returns:
            Tokenized dataset
        """
        def tokenize_function(examples):
            # Format messages using chat template
            texts = []
            for messages in examples["messages"]:
                if isinstance(messages, str):
                    import json
                    messages = json.loads(messages)
                
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
                texts.append(text)
            
            # Tokenize
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length",
                return_tensors=None,
            )
            
            # Labels are the same as input_ids for causal LM
            tokenized["labels"] = tokenized["input_ids"].copy()
            
            return tokenized
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing dataset"
        )
        
        return tokenized_dataset
    
    def _prepare_dpo_dataset(self, dataset: Dataset) -> Dataset:
        """Prepare DPO (Direct Preference Optimization) dataset.
        
        Args:
            dataset: Raw dataset with 'prompt', 'chosen', 'rejected' fields
            
        Returns:
            Tokenized dataset
        """
        # DPO requires special handling - simplified version
        def tokenize_function(examples):
            prompts = examples["prompt"]
            chosen = examples["chosen"]
            rejected = examples["rejected"]
            
            # Tokenize chosen and rejected responses
            chosen_tokens = self.tokenizer(
                [f"{p}\n{c}" for p, c in zip(prompts, chosen)],
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length",
            )
            
            rejected_tokens = self.tokenizer(
                [f"{p}\n{r}" for p, r in zip(prompts, rejected)],
                truncation=True,
                max_length=self.config.max_seq_length,
                padding="max_length",
            )
            
            return {
                "input_ids_chosen": chosen_tokens["input_ids"],
                "attention_mask_chosen": chosen_tokens["attention_mask"],
                "input_ids_rejected": rejected_tokens["input_ids"],
                "attention_mask_rejected": rejected_tokens["attention_mask"],
            }
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing DPO dataset"
        )
        
        return tokenized_dataset
    
    def train(
        self,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        adapter_name: str = "adapter"
    ) -> None:
        """Train LoRA adapter.
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset (optional)
            adapter_name: Name for the adapter
        """
        if self.model is None:
            self.load_model()
        
        output_dir = Path(self.config.output_dir) / adapter_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting training, output dir: {output_dir}")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=self.config.num_train_epochs,
            per_device_train_batch_size=self.config.per_device_train_batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            max_grad_norm=self.config.max_grad_norm,
            warmup_ratio=self.config.warmup_ratio,
            lr_scheduler_type=self.config.lr_scheduler_type,
            optim=self.config.optim,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            eval_steps=self.config.eval_steps if eval_dataset else None,
            evaluation_strategy="steps" if eval_dataset else "no",
            save_total_limit=3,
            fp16=True,
            report_to=["tensorboard"],
            load_best_model_at_end=True if eval_dataset else False,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
        )
        
        # Train
        logger.info("Starting training...")
        trainer.train()
        
        # Save final model
        logger.info(f"Saving adapter to {output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info("Training complete!")


def main():
    """CLI entry point for LoRA training."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Train LoRA Adapter")
    parser.add_argument("--base-model", default="meta-llama/Llama-3.1-8B-Instruct", help="Base model")
    parser.add_argument("--dataset", type=Path, required=True, help="Training dataset (jsonl)")
    parser.add_argument("--eval-dataset", type=Path, help="Evaluation dataset (jsonl)")
    parser.add_argument("--adapter-type", required=True, help="Adapter type (retailer, brand, task)")
    parser.add_argument("--adapter-name", required=True, help="Adapter name")
    parser.add_argument("--output-dir", type=Path, default="./models/adapters", help="Output directory")
    parser.add_argument("--config", type=Path, help="Training config JSON")
    
    # LoRA params
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout")
    
    # Training params
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-4, help="Learning rate")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load or create config
    if args.config and args.config.exists():
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = LoRATrainingConfig(**config_dict)
    else:
        config = LoRATrainingConfig(
            base_model=args.base_model,
            lora_r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            num_train_epochs=args.epochs,
            per_device_train_batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            output_dir=str(args.output_dir),
        )
    
    # Initialize trainer
    trainer = LoRATrainer(config)
    trainer.load_model()
    
    # Prepare datasets
    train_dataset = trainer.prepare_dataset(args.dataset, dataset_type="sft")
    eval_dataset = None
    if args.eval_dataset:
        eval_dataset = trainer.prepare_dataset(args.eval_dataset, dataset_type="sft")
    
    # Train
    adapter_full_name = f"{args.adapter_type}_{args.adapter_name}"
    trainer.train(train_dataset, eval_dataset, adapter_full_name)
    
    print(f"\n=== Training Complete ===")
    print(f"Adapter saved to: {args.output_dir / adapter_full_name}")


if __name__ == "__main__":
    main()
