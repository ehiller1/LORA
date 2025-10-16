"""Evaluation harness for LoRA adapters."""

import logging
import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    """Evaluation metrics."""
    exact_match: float
    json_parse_success: float
    tool_call_accuracy: float
    constraint_satisfaction: float
    avg_response_length: float
    metadata: Dict[str, Any]


class EvaluationHarness:
    """Harness for evaluating LoRA adapters."""
    
    def __init__(
        self,
        base_model_path: str,
        adapter_path: Optional[Path] = None,
        device: str = "auto"
    ):
        """Initialize evaluation harness.
        
        Args:
            base_model_path: Path to base model
            adapter_path: Path to LoRA adapter (optional)
            device: Device to run on
        """
        self.base_model_path = base_model_path
        self.adapter_path = adapter_path
        self.device = device
        
        logger.info(f"Loading model for evaluation: {base_model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=device,
            trust_remote_code=True
        )
        
        if adapter_path and adapter_path.exists():
            logger.info(f"Loading adapter: {adapter_path}")
            self.model = PeftModel.from_pretrained(
                self.model,
                str(adapter_path),
                is_trainable=False
            )
        
        self.model.eval()
    
    def evaluate_dataset(
        self,
        test_dataset_path: Path,
        output_path: Optional[Path] = None
    ) -> EvaluationMetrics:
        """Evaluate model on test dataset.
        
        Args:
            test_dataset_path: Path to test dataset (jsonl)
            output_path: Path to save detailed results
            
        Returns:
            Evaluation metrics
        """
        logger.info(f"Evaluating on {test_dataset_path}")
        
        # Load test dataset
        test_examples = []
        with open(test_dataset_path, 'r') as f:
            for line in f:
                test_examples.append(json.loads(line))
        
        logger.info(f"Loaded {len(test_examples)} test examples")
        
        # Evaluate each example
        results = []
        exact_matches = 0
        json_successes = 0
        tool_call_correct = 0
        constraint_satisfied = 0
        response_lengths = []
        
        for i, example in enumerate(test_examples):
            if i % 10 == 0:
                logger.info(f"Evaluating example {i+1}/{len(test_examples)}")
            
            result = self._evaluate_example(example)
            results.append(result)
            
            # Aggregate metrics
            if result.get("exact_match"):
                exact_matches += 1
            if result.get("json_parse_success"):
                json_successes += 1
            if result.get("tool_call_correct"):
                tool_call_correct += 1
            if result.get("constraint_satisfied"):
                constraint_satisfied += 1
            
            response_lengths.append(result.get("response_length", 0))
        
        # Calculate metrics
        n = len(test_examples)
        metrics = EvaluationMetrics(
            exact_match=exact_matches / n if n > 0 else 0,
            json_parse_success=json_successes / n if n > 0 else 0,
            tool_call_accuracy=tool_call_correct / n if n > 0 else 0,
            constraint_satisfaction=constraint_satisfied / n if n > 0 else 0,
            avg_response_length=np.mean(response_lengths) if response_lengths else 0,
            metadata={
                "total_examples": n,
                "adapter_path": str(self.adapter_path) if self.adapter_path else None
            }
        )
        
        logger.info(f"Evaluation complete: EM={metrics.exact_match:.3f}, JSON={metrics.json_parse_success:.3f}")
        
        # Save detailed results
        if output_path:
            self._save_results(results, metrics, output_path)
        
        return metrics
    
    def _evaluate_example(self, example: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate single example.
        
        Args:
            example: Test example with messages and expected output
            
        Returns:
            Evaluation result
        """
        messages = example.get("messages", [])
        expected_output = example.get("expected_output")
        
        # Generate response
        generated = self._generate_response(messages)
        
        result = {
            "input": messages,
            "expected": expected_output,
            "generated": generated,
            "response_length": len(generated)
        }
        
        # Exact match
        if expected_output:
            result["exact_match"] = generated.strip() == expected_output.strip()
        
        # JSON parse success
        try:
            parsed = json.loads(generated)
            result["json_parse_success"] = True
            result["parsed_output"] = parsed
            
            # Tool call correctness
            if expected_output:
                try:
                    expected_parsed = json.loads(expected_output)
                    result["tool_call_correct"] = self._compare_tool_calls(
                        parsed,
                        expected_parsed
                    )
                except:
                    result["tool_call_correct"] = False
            
        except json.JSONDecodeError:
            result["json_parse_success"] = False
            result["tool_call_correct"] = False
        
        # Constraint satisfaction (simplified)
        result["constraint_satisfied"] = result.get("json_parse_success", False)
        
        return result
    
    def _generate_response(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 1024
    ) -> str:
        """Generate response for messages.
        
        Args:
            messages: List of message dicts
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated response
        """
        # Format messages
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
            prompt += "\n\nassistant:"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.1,  # Low temperature for evaluation
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
    
    def _compare_tool_calls(
        self,
        generated: Dict[str, Any],
        expected: Dict[str, Any]
    ) -> bool:
        """Compare generated and expected tool calls.
        
        Args:
            generated: Generated tool call
            expected: Expected tool call
            
        Returns:
            Whether they match
        """
        # Check tool name
        if generated.get("tool") != expected.get("tool"):
            return False
        
        # Check critical args (simplified - would need schema-aware comparison)
        gen_args = generated.get("args", {})
        exp_args = expected.get("args", {})
        
        # Check if all expected keys are present
        for key in exp_args:
            if key not in gen_args:
                return False
        
        return True
    
    def _save_results(
        self,
        results: List[Dict[str, Any]],
        metrics: EvaluationMetrics,
        output_path: Path
    ) -> None:
        """Save evaluation results.
        
        Args:
            results: Detailed results
            metrics: Aggregate metrics
            output_path: Output path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "metrics": {
                "exact_match": metrics.exact_match,
                "json_parse_success": metrics.json_parse_success,
                "tool_call_accuracy": metrics.tool_call_accuracy,
                "constraint_satisfaction": metrics.constraint_satisfaction,
                "avg_response_length": metrics.avg_response_length,
            },
            "metadata": metrics.metadata,
            "detailed_results": results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
    
    def evaluate_mapping_accuracy(
        self,
        test_mappings: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate schema mapping accuracy.
        
        Args:
            test_mappings: List of test mapping examples
            
        Returns:
            Mapping accuracy metrics
        """
        correct_fields = 0
        total_fields = 0
        
        for mapping in test_mappings:
            input_data = mapping["input"]
            expected_output = mapping["output"]
            
            # Generate mapping
            messages = [
                {"role": "system", "content": "You are a data harmonization expert."},
                {"role": "user", "content": f"Map to RMIS: {json.dumps(input_data)}"}
            ]
            
            generated = self._generate_response(messages)
            
            try:
                generated_output = json.loads(generated)
                
                # Compare fields
                for field, expected_value in expected_output.items():
                    total_fields += 1
                    if field in generated_output:
                        # Simplified comparison
                        if generated_output[field] == expected_value:
                            correct_fields += 1
            except:
                total_fields += len(expected_output)
        
        return {
            "field_accuracy": correct_fields / total_fields if total_fields > 0 else 0,
            "total_fields": total_fields,
            "correct_fields": correct_fields
        }


def main():
    """CLI entry point for evaluation harness."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate LoRA Adapter")
    parser.add_argument("--base-model", required=True, help="Base model path")
    parser.add_argument("--adapter", type=Path, help="Adapter path")
    parser.add_argument("--test-dataset", type=Path, required=True, help="Test dataset (jsonl)")
    parser.add_argument("--output", type=Path, help="Output results path")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize harness
    harness = EvaluationHarness(
        args.base_model,
        args.adapter
    )
    
    # Evaluate
    metrics = harness.evaluate_dataset(
        args.test_dataset,
        args.output
    )
    
    # Print results
    print("\n=== Evaluation Results ===")
    print(f"Exact Match: {metrics.exact_match:.3f}")
    print(f"JSON Parse Success: {metrics.json_parse_success:.3f}")
    print(f"Tool Call Accuracy: {metrics.tool_call_accuracy:.3f}")
    print(f"Constraint Satisfaction: {metrics.constraint_satisfaction:.3f}")
    print(f"Avg Response Length: {metrics.avg_response_length:.1f}")
    
    if args.output:
        print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    main()
