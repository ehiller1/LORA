"""Creative Agent - Generates policy-compliant creative copy."""

import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

from ..schemas.tools import (
    GenerateCopyInput,
    GenerateCopyOutput,
    CopyVariant,
)

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Checks creative copy for policy compliance."""
    
    @staticmethod
    def check_compliance(
        copy: str,
        disallowed_terms: List[str],
        max_length: Optional[int] = None,
        required_disclaimers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Check if copy meets compliance requirements.
        
        Args:
            copy: Copy text to check
            disallowed_terms: List of disallowed terms
            max_length: Maximum length constraint
            required_disclaimers: Required disclaimer phrases
            
        Returns:
            Compliance check results
        """
        issues = []
        
        # Check length
        if max_length and len(copy) > max_length:
            issues.append(f"Exceeds maximum length of {max_length} characters")
        
        # Check disallowed terms
        copy_lower = copy.lower()
        for term in disallowed_terms:
            if term.lower() in copy_lower:
                issues.append(f"Contains disallowed term: '{term}'")
        
        # Check required disclaimers
        if required_disclaimers:
            for disclaimer in required_disclaimers:
                if disclaimer.lower() not in copy_lower:
                    issues.append(f"Missing required disclaimer: '{disclaimer}'")
        
        # Calculate compliance score
        compliance_score = 1.0 - (len(issues) * 0.2)
        compliance_score = max(0.0, min(1.0, compliance_score))
        
        return {
            "compliant": len(issues) == 0,
            "score": compliance_score,
            "issues": issues
        }


class CreativeAgent:
    """Agent for generating compliant creative copy."""
    
    def __init__(
        self,
        base_model_path: Optional[str] = None,
        adapter_paths: Optional[List[Path]] = None,
        device: str = "auto"
    ):
        """Initialize Creative Agent.
        
        Args:
            base_model_path: Path or HF model ID for base model
            adapter_paths: List of LoRA adapter paths (brand, creative task)
            device: Device to run on
        """
        self.base_model_path = base_model_path
        self.adapter_paths = adapter_paths or []
        self.device = device
        
        if base_model_path:
            logger.info(f"Loading base model: {base_model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map=device,
                trust_remote_code=True
            )
            
            # Load adapters
            for adapter_path in self.adapter_paths:
                if adapter_path.exists():
                    logger.info(f"Loading adapter: {adapter_path}")
                    self.model = PeftModel.from_pretrained(
                        self.model,
                        str(adapter_path),
                        is_trainable=False
                    )
            
            self.model.eval()
        else:
            self.tokenizer = None
            self.model = None
            logger.info("Creative Agent initialized in template mode (no LLM)")
    
    def generate_copy(self, input_data: GenerateCopyInput) -> GenerateCopyOutput:
        """Generate creative copy variants.
        
        Args:
            input_data: Copy generation input
            
        Returns:
            Generated copy variants with compliance checks
        """
        logger.info(f"Generating {input_data.num_variants} copy variants for SKU: {input_data.sku_id}")
        
        if self.model:
            variants = self._generate_with_llm(input_data)
        else:
            variants = self._generate_with_templates(input_data)
        
        # Check compliance for all variants
        compliance_checks = []
        all_compliant = True
        
        for i, variant in enumerate(variants):
            # Check headline
            headline_check = ComplianceChecker.check_compliance(
                variant.headline,
                input_data.retailer_specs.disallowed_terms,
                input_data.retailer_specs.max_headline_length
            )
            
            # Check body
            body_check = ComplianceChecker.check_compliance(
                variant.body,
                input_data.retailer_specs.disallowed_terms,
                input_data.retailer_specs.max_body_length,
                input_data.retailer_specs.required_disclaimers
            )
            
            # Update variant compliance score
            variant.compliance_score = (headline_check["score"] + body_check["score"]) / 2
            
            if not headline_check["compliant"] or not body_check["compliant"]:
                all_compliant = False
                compliance_checks.append(
                    f"Variant {i+1}: {', '.join(headline_check['issues'] + body_check['issues'])}"
                )
        
        if all_compliant:
            compliance_checks.append("All variants meet compliance requirements")
        
        # Generate recommendations
        recommendations = []
        if not all_compliant:
            recommendations.append("Review flagged variants for compliance issues")
            recommendations.append("Consider regenerating non-compliant variants")
        
        avg_score = sum(v.compliance_score for v in variants) / len(variants)
        if avg_score < 0.8:
            recommendations.append("Overall compliance score is low - review brand guidelines")
        
        return GenerateCopyOutput(
            variants=variants,
            compliance_checks=compliance_checks,
            all_compliant=all_compliant,
            recommendations=recommendations if recommendations else None
        )
    
    def _generate_with_llm(self, input_data: GenerateCopyInput) -> List[CopyVariant]:
        """Generate copy using LLM."""
        variants = []
        
        # Build prompt
        prompt = self._build_creative_prompt(input_data)
        
        # Generate multiple variants
        for i in range(input_data.num_variants):
            messages = [
                {"role": "system", "content": "You are a creative copywriter for retail media ads."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate
            response = self._generate(messages)
            
            # Parse response (simplified - would need more robust parsing)
            variant = self._parse_creative_response(response, input_data)
            variants.append(variant)
        
        return variants
    
    def _generate_with_templates(self, input_data: GenerateCopyInput) -> List[CopyVariant]:
        """Generate copy using templates (fallback when no LLM)."""
        variants = []
        
        # Extract key attributes
        product_name = input_data.attributes.get("name", "Product")
        benefits = input_data.attributes.get("benefits", [])
        size = input_data.attributes.get("size", "")
        
        # Template variations
        templates = [
            {
                "headline": f"Premium {product_name}",
                "body": f"Experience quality with {product_name}. {benefits[0] if benefits else 'Perfect for your needs.'}",
                "cta": "Shop Now"
            },
            {
                "headline": f"Save on {product_name}",
                "body": f"Get the best value on {product_name}. {size}",
                "cta": "Add to Cart"
            },
            {
                "headline": f"New: {product_name}",
                "body": f"Discover our latest {product_name}. Limited time offer.",
                "cta": "Learn More"
            },
            {
                "headline": f"{product_name} - Top Rated",
                "body": f"Join thousands who love {product_name}. {benefits[0] if benefits else ''}",
                "cta": "Buy Now"
            },
            {
                "headline": f"Try {product_name} Today",
                "body": f"Perfect for everyday use. {product_name} delivers results.",
                "cta": "Shop Now"
            }
        ]
        
        for i in range(min(input_data.num_variants, len(templates))):
            template = templates[i]
            
            # Add required disclaimers
            body = template["body"]
            for disclaimer in input_data.retailer_specs.required_disclaimers:
                body += f" {disclaimer}"
            
            variant = CopyVariant(
                headline=template["headline"],
                body=body,
                call_to_action=template["cta"],
                reasons_to_believe=benefits[:3] if benefits else ["Quality product", "Great value"],
                compliance_score=0.0  # Will be calculated later
            )
            variants.append(variant)
        
        return variants
    
    def _build_creative_prompt(self, input_data: GenerateCopyInput) -> str:
        """Build prompt for creative generation."""
        prompt_parts = [
            f"Generate creative copy for: {input_data.attributes.get('name', 'Product')}",
            f"\nBrand tone: {input_data.brand_tone}",
            f"\nPlacement: {input_data.retailer_specs.placement_type}",
        ]
        
        if input_data.target_audience:
            prompt_parts.append(f"\nTarget audience: {input_data.target_audience}")
        
        prompt_parts.append(f"\nProduct attributes: {input_data.attributes}")
        
        # Constraints
        prompt_parts.append("\nConstraints:")
        if input_data.retailer_specs.max_headline_length:
            prompt_parts.append(f"- Headline max {input_data.retailer_specs.max_headline_length} chars")
        if input_data.retailer_specs.max_body_length:
            prompt_parts.append(f"- Body max {input_data.retailer_specs.max_body_length} chars")
        if input_data.retailer_specs.disallowed_terms:
            prompt_parts.append(f"- Avoid: {', '.join(input_data.retailer_specs.disallowed_terms)}")
        if input_data.retailer_specs.required_disclaimers:
            prompt_parts.append(f"- Include: {', '.join(input_data.retailer_specs.required_disclaimers)}")
        
        prompt_parts.append("\nGenerate: headline, body, call-to-action, and 3 reasons to believe.")
        
        return "\n".join(prompt_parts)
    
    def _generate(self, messages: List[Dict[str, str]], max_new_tokens: int = 512) -> str:
        """Generate response from model."""
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
            prompt += "\n\nassistant:"
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
    
    def _parse_creative_response(
        self,
        response: str,
        input_data: GenerateCopyInput
    ) -> CopyVariant:
        """Parse LLM response into CopyVariant."""
        # Simplified parsing - would need more robust implementation
        lines = response.split("\n")
        
        headline = ""
        body = ""
        cta = "Shop Now"
        rtb = []
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith("headline:"):
                headline = line.split(":", 1)[1].strip()
            elif line.lower().startswith("body:"):
                body = line.split(":", 1)[1].strip()
            elif line.lower().startswith("cta:") or line.lower().startswith("call to action:"):
                cta = line.split(":", 1)[1].strip()
            elif line.lower().startswith("reason"):
                rtb.append(line.split(":", 1)[1].strip() if ":" in line else line)
        
        return CopyVariant(
            headline=headline or "Premium Product",
            body=body or "Experience quality and value.",
            call_to_action=cta,
            reasons_to_believe=rtb[:3],
            compliance_score=0.0
        )


def main():
    """CLI entry point for Creative Agent."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Creative Agent")
    parser.add_argument("--base-model", help="Base model path (optional)")
    parser.add_argument("--adapters", nargs="*", help="Adapter paths to load")
    parser.add_argument("--input", type=Path, required=True, help="Input JSON file")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load input
    with open(args.input, 'r') as f:
        input_dict = json.load(f)
    
    input_data = GenerateCopyInput(**input_dict)
    
    # Initialize agent
    adapter_paths = [Path(p) for p in args.adapters] if args.adapters else []
    agent = CreativeAgent(args.base_model, adapter_paths)
    
    # Generate copy
    output = agent.generate_copy(input_data)
    
    # Print results
    print("\n=== Generated Copy Variants ===")
    for i, variant in enumerate(output.variants, 1):
        print(f"\nVariant {i} (Compliance: {variant.compliance_score:.2f}):")
        print(f"  Headline: {variant.headline}")
        print(f"  Body: {variant.body}")
        print(f"  CTA: {variant.call_to_action}")
        print(f"  RTB: {', '.join(variant.reasons_to_believe)}")
    
    print(f"\n=== Compliance ===")
    print(f"All Compliant: {output.all_compliant}")
    for check in output.compliance_checks:
        print(f"  - {check}")
    
    if output.recommendations:
        print(f"\n=== Recommendations ===")
        for rec in output.recommendations:
            print(f"  - {rec}")
    
    # Save output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output.model_dump(), f, indent=2)
        print(f"\nOutput saved to {args.output}")


if __name__ == "__main__":
    main()
