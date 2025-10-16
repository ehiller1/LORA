"""Dataset builder for LoRA training."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Single training example."""
    messages: List[Dict[str, str]]
    metadata: Optional[Dict[str, Any]] = None


class DatasetBuilder:
    """Builds training datasets for LoRA adapters."""
    
    @staticmethod
    def build_retailer_adapter_dataset(
        retailer_id: str,
        mapping_examples: List[Dict[str, Any]],
        policy_examples: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """Build dataset for retailer adapter.
        
        Args:
            retailer_id: Retailer identifier
            mapping_examples: Schema mapping examples
            policy_examples: Policy interpretation examples
            output_path: Output JSONL path
            
        Returns:
            Number of examples created
        """
        examples = []
        
        # Schema mapping examples
        for mapping in mapping_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a data harmonization expert for {retailer_id}. Map native schemas to RMIS."
                },
                {
                    "role": "user",
                    "content": f"Map the following {retailer_id} fields to RMIS:\n{json.dumps(mapping['input'], indent=2)}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps(mapping['output'], indent=2)
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Policy examples
        for policy in policy_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a policy expert for {retailer_id}. Interpret and enforce retailer policies."
                },
                {
                    "role": "user",
                    "content": policy['question']
                },
                {
                    "role": "assistant",
                    "content": policy['answer']
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Write to file
        DatasetBuilder._write_jsonl(examples, output_path)
        logger.info(f"Created {len(examples)} examples for retailer adapter: {retailer_id}")
        
        return len(examples)
    
    @staticmethod
    def build_brand_adapter_dataset(
        brand_name: str,
        tone_examples: List[Dict[str, Any]],
        product_examples: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """Build dataset for brand adapter.
        
        Args:
            brand_name: Brand name
            tone_examples: Brand tone examples
            product_examples: Product description examples
            output_path: Output JSONL path
            
        Returns:
            Number of examples created
        """
        examples = []
        
        # Tone examples
        for tone in tone_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a copywriter for {brand_name}. Write in the brand's voice and tone."
                },
                {
                    "role": "user",
                    "content": tone['prompt']
                },
                {
                    "role": "assistant",
                    "content": tone['response']
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Product examples
        for product in product_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are a product expert for {brand_name}. Describe products accurately and compellingly."
                },
                {
                    "role": "user",
                    "content": f"Describe this product: {json.dumps(product['attributes'])}"
                },
                {
                    "role": "assistant",
                    "content": product['description']
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Write to file
        DatasetBuilder._write_jsonl(examples, output_path)
        logger.info(f"Created {len(examples)} examples for brand adapter: {brand_name}")
        
        return len(examples)
    
    @staticmethod
    def build_task_adapter_dataset(
        task_name: str,
        tool_examples: List[Dict[str, Any]],
        reasoning_examples: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """Build dataset for task adapter.
        
        Args:
            task_name: Task name (budgeting, measurement, creative, etc.)
            tool_examples: Tool usage examples
            reasoning_examples: Reasoning examples
            output_path: Output JSONL path
            
        Returns:
            Number of examples created
        """
        examples = []
        
        # Tool usage examples
        for tool in tool_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert at {task_name}. Use tools to accomplish objectives."
                },
                {
                    "role": "user",
                    "content": tool['objective']
                },
                {
                    "role": "assistant",
                    "content": json.dumps(tool['tool_call'], indent=2)
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Reasoning examples
        for reasoning in reasoning_examples:
            messages = [
                {
                    "role": "system",
                    "content": f"You are an expert at {task_name}. Provide clear reasoning and explanations."
                },
                {
                    "role": "user",
                    "content": reasoning['question']
                },
                {
                    "role": "assistant",
                    "content": reasoning['answer']
                }
            ]
            examples.append(TrainingExample(messages=messages))
        
        # Write to file
        DatasetBuilder._write_jsonl(examples, output_path)
        logger.info(f"Created {len(examples)} examples for task adapter: {task_name}")
        
        return len(examples)
    
    @staticmethod
    def build_dpo_dataset(
        chosen_examples: List[Dict[str, Any]],
        rejected_examples: List[Dict[str, Any]],
        output_path: Path
    ) -> int:
        """Build DPO (Direct Preference Optimization) dataset.
        
        Args:
            chosen_examples: Preferred responses
            rejected_examples: Rejected responses
            output_path: Output JSONL path
            
        Returns:
            Number of examples created
        """
        if len(chosen_examples) != len(rejected_examples):
            raise ValueError("Chosen and rejected examples must have same length")
        
        examples = []
        
        for chosen, rejected in zip(chosen_examples, rejected_examples):
            example = {
                "prompt": chosen['prompt'],
                "chosen": chosen['response'],
                "rejected": rejected['response']
            }
            examples.append(example)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example) + '\n')
        
        logger.info(f"Created {len(examples)} DPO examples")
        
        return len(examples)
    
    @staticmethod
    def create_synthetic_examples(
        example_type: str,
        num_examples: int,
        seed: int = 42
    ) -> List[Dict[str, Any]]:
        """Create synthetic training examples.
        
        Args:
            example_type: Type of examples (mapping, budgeting, creative, etc.)
            num_examples: Number of examples to create
            seed: Random seed
            
        Returns:
            List of synthetic examples
        """
        random.seed(seed)
        examples = []
        
        if example_type == "mapping":
            for i in range(num_examples):
                examples.append({
                    "input": {
                        "evt_id": f"evt_{i}",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "placement": random.choice(["onsite_prod", "display_onsite", "offsite"]),
                        "spend": random.uniform(10, 1000),
                        "conv": random.randint(0, 50)
                    },
                    "output": {
                        "event_id": f"evt_{i}",
                        "ts": "2024-01-01T00:00:00Z",
                        "placement_type": random.choice(["sponsored_product", "onsite_display", "offsite_display"]),
                        "cost": random.uniform(10, 1000),
                        "attributed_conversions": random.randint(0, 50)
                    }
                })
        
        elif example_type == "budgeting":
            for i in range(num_examples):
                budget = random.uniform(100000, 5000000)
                examples.append({
                    "objective": f"Allocate ${budget:,.0f} to maximize incremental margin with ROAS >= 3.0",
                    "tool_call": {
                        "type": "tool_call",
                        "tool": "allocate_budget",
                        "args": {
                            "total_budget": budget,
                            "hierarchy": ["rmn", "placement", "audience"],
                            "constraints": {
                                "min_roas": 3.0,
                                "reserve_for_experiments": 0.1
                            },
                            "objective": "maximize_incremental_margin"
                        }
                    }
                })
        
        elif example_type == "creative":
            products = ["Premium Coffee", "Organic Yogurt", "Wireless Headphones", "Running Shoes", "Vitamin C Serum"]
            for i in range(num_examples):
                product = random.choice(products)
                examples.append({
                    "prompt": f"Write a compelling headline for {product}",
                    "response": f"Experience the Best: {product} - Quality You Can Trust"
                })
        
        return examples
    
    @staticmethod
    def _write_jsonl(examples: List[TrainingExample], output_path: Path) -> None:
        """Write examples to JSONL file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for example in examples:
                # Convert to dict
                example_dict = {
                    "messages": example.messages
                }
                if example.metadata:
                    example_dict["metadata"] = example.metadata
                
                f.write(json.dumps(example_dict) + '\n')


def main():
    """CLI entry point for dataset builder."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Training Datasets")
    parser.add_argument("--type", required=True, choices=["retailer", "brand", "task", "dpo", "synthetic"])
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL path")
    
    # For synthetic
    parser.add_argument("--example-type", help="Type of synthetic examples")
    parser.add_argument("--num-examples", type=int, default=100, help="Number of synthetic examples")
    
    # For specific types
    parser.add_argument("--name", help="Retailer/brand/task name")
    parser.add_argument("--input-dir", type=Path, help="Input directory with examples")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if args.type == "synthetic":
        if not args.example_type:
            parser.error("--example-type required for synthetic dataset")
        
        examples = DatasetBuilder.create_synthetic_examples(
            args.example_type,
            args.num_examples
        )
        
        # Convert to training examples
        if args.example_type == "mapping":
            training_examples = []
            for ex in examples:
                messages = [
                    {"role": "system", "content": "You are a data harmonization expert."},
                    {"role": "user", "content": f"Map: {json.dumps(ex['input'])}"},
                    {"role": "assistant", "content": json.dumps(ex['output'])}
                ]
                training_examples.append(TrainingExample(messages=messages))
            
            DatasetBuilder._write_jsonl(training_examples, args.output)
        
        elif args.example_type in ["budgeting", "creative"]:
            training_examples = []
            for ex in examples:
                if "objective" in ex:
                    messages = [
                        {"role": "system", "content": "You are a planning expert."},
                        {"role": "user", "content": ex['objective']},
                        {"role": "assistant", "content": json.dumps(ex['tool_call'])}
                    ]
                else:
                    messages = [
                        {"role": "system", "content": "You are a creative expert."},
                        {"role": "user", "content": ex['prompt']},
                        {"role": "assistant", "content": ex['response']}
                    ]
                training_examples.append(TrainingExample(messages=messages))
            
            DatasetBuilder._write_jsonl(training_examples, args.output)
        
        print(f"\n=== Dataset Created ===")
        print(f"Type: {args.example_type}")
        print(f"Examples: {len(examples)}")
        print(f"Output: {args.output}")
    
    else:
        print("For non-synthetic datasets, use the build_*_adapter_dataset methods programmatically")


if __name__ == "__main__":
    main()
