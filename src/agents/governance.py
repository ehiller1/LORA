"""Governance Agent - Enforces PII and policy guardrails."""

import logging
import re
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class PIIDetection:
    """PII detection result."""
    detected: bool
    pii_types: List[str]
    locations: List[Dict[str, Any]]
    redacted_text: str


class PIIDetector:
    """Detects and redacts PII from text and data."""
    
    # Regex patterns for common PII
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        "zip_code": r'\b\d{5}(-\d{4})?\b',
    }
    
    @staticmethod
    def detect_pii(text: str) -> PIIDetection:
        """Detect PII in text.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            PII detection result
        """
        detected_types = []
        locations = []
        redacted_text = text
        
        for pii_type, pattern in PIIDetector.PATTERNS.items():
            matches = list(re.finditer(pattern, text))
            
            if matches:
                detected_types.append(pii_type)
                
                for match in matches:
                    locations.append({
                        "type": pii_type,
                        "start": match.start(),
                        "end": match.end(),
                        "value": match.group()
                    })
                    
                    # Redact
                    redacted_text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", redacted_text)
        
        return PIIDetection(
            detected=len(detected_types) > 0,
            pii_types=detected_types,
            locations=locations,
            redacted_text=redacted_text
        )
    
    @staticmethod
    def hash_identifier(identifier: str, salt: str = "") -> str:
        """Hash an identifier for privacy-safe storage.
        
        Args:
            identifier: Identifier to hash (email, user_id, etc.)
            salt: Optional salt for hashing
            
        Returns:
            Hashed identifier
        """
        combined = f"{identifier}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()


class PolicyChecker:
    """Checks content against retailer policies."""
    
    @staticmethod
    def check_creative_policy(
        creative_text: str,
        disallowed_terms: List[str],
        required_disclaimers: List[str],
        placement_type: str
    ) -> Dict[str, Any]:
        """Check creative content against policy.
        
        Args:
            creative_text: Creative text to check
            disallowed_terms: List of disallowed terms
            required_disclaimers: Required disclaimer phrases
            placement_type: Placement type for context
            
        Returns:
            Policy check results
        """
        violations = []
        warnings = []
        
        text_lower = creative_text.lower()
        
        # Check disallowed terms
        for term in disallowed_terms:
            if term.lower() in text_lower:
                violations.append({
                    "type": "disallowed_term",
                    "term": term,
                    "severity": "error"
                })
        
        # Check required disclaimers
        missing_disclaimers = []
        for disclaimer in required_disclaimers:
            if disclaimer.lower() not in text_lower:
                missing_disclaimers.append(disclaimer)
        
        if missing_disclaimers:
            violations.append({
                "type": "missing_disclaimer",
                "disclaimers": missing_disclaimers,
                "severity": "error"
            })
        
        # Check for common issues
        if len(creative_text) > 1000:
            warnings.append({
                "type": "length_warning",
                "message": "Creative text is unusually long",
                "severity": "warning"
            })
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in creative_text if c.isupper()) / len(creative_text) if creative_text else 0
        if caps_ratio > 0.5:
            warnings.append({
                "type": "excessive_caps",
                "message": "Excessive use of capital letters",
                "severity": "warning"
            })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "checked_at": "utc_timestamp"
        }
    
    @staticmethod
    def check_data_access_policy(
        query: str,
        allowed_tables: Set[str],
        allowed_fields: Set[str],
        require_aggregation: bool = True
    ) -> Dict[str, Any]:
        """Check if data access query complies with policy.
        
        Args:
            query: SQL query to check
            allowed_tables: Set of allowed table names
            allowed_fields: Set of allowed field names
            require_aggregation: Whether aggregation is required
            
        Returns:
            Policy check results
        """
        violations = []
        
        query_lower = query.lower()
        
        # Check for raw user-level data access
        if "select *" in query_lower and require_aggregation:
            violations.append({
                "type": "raw_data_access",
                "message": "SELECT * not allowed - must use aggregation",
                "severity": "error"
            })
        
        # Check for aggregation functions
        agg_functions = ["sum(", "avg(", "count(", "min(", "max("]
        has_aggregation = any(func in query_lower for func in agg_functions)
        
        if require_aggregation and not has_aggregation and "group by" not in query_lower:
            violations.append({
                "type": "no_aggregation",
                "message": "Query must include aggregation or GROUP BY",
                "severity": "error"
            })
        
        # Check for PII fields (simplified)
        pii_fields = ["email", "phone", "ssn", "address", "name"]
        for field in pii_fields:
            if field in query_lower:
                violations.append({
                    "type": "pii_field_access",
                    "field": field,
                    "message": f"Direct access to PII field '{field}' not allowed",
                    "severity": "error"
                })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "has_aggregation": has_aggregation
        }


class DataPrivacyEnforcer:
    """Enforces data privacy constraints."""
    
    @staticmethod
    def apply_k_anonymity(
        data: List[Dict[str, Any]],
        k: int = 50,
        quasi_identifiers: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Apply k-anonymity to data.
        
        Args:
            data: List of data records
            k: Minimum group size
            quasi_identifiers: Fields that are quasi-identifiers
            
        Returns:
            Filtered data meeting k-anonymity
        """
        if not quasi_identifiers:
            return data
        
        # Group by quasi-identifiers
        groups = {}
        for record in data:
            key = tuple(record.get(qi) for qi in quasi_identifiers)
            if key not in groups:
                groups[key] = []
            groups[key].append(record)
        
        # Filter groups with size < k
        filtered_data = []
        suppressed_count = 0
        
        for group in groups.values():
            if len(group) >= k:
                filtered_data.extend(group)
            else:
                suppressed_count += len(group)
        
        logger.info(f"K-anonymity: kept {len(filtered_data)} records, suppressed {suppressed_count}")
        
        return filtered_data
    
    @staticmethod
    def apply_differential_privacy(
        value: float,
        epsilon: float = 1.0,
        sensitivity: float = 1.0
    ) -> float:
        """Apply differential privacy noise to a value.
        
        Args:
            value: Original value
            epsilon: Privacy parameter (smaller = more private)
            sensitivity: Sensitivity of the query
            
        Returns:
            Noised value
        """
        import numpy as np
        
        # Laplace mechanism
        scale = sensitivity / epsilon
        noise = np.random.laplace(0, scale)
        
        return value + noise


class GovernanceAgent:
    """Agent for enforcing governance, PII, and policy guardrails."""
    
    def __init__(
        self,
        min_cell_size: int = 50,
        enable_pii_detection: bool = True,
        enable_policy_checks: bool = True
    ):
        """Initialize Governance Agent.
        
        Args:
            min_cell_size: Minimum cell size for k-anonymity
            enable_pii_detection: Enable PII detection
            enable_policy_checks: Enable policy checking
        """
        self.min_cell_size = min_cell_size
        self.enable_pii_detection = enable_pii_detection
        self.enable_policy_checks = enable_policy_checks
        
        logger.info(
            f"Governance Agent initialized: "
            f"min_cell_size={min_cell_size}, "
            f"pii_detection={enable_pii_detection}, "
            f"policy_checks={enable_policy_checks}"
        )
    
    def check_text(self, text: str) -> Dict[str, Any]:
        """Check text for PII and policy violations.
        
        Args:
            text: Text to check
            
        Returns:
            Check results
        """
        results = {
            "text_safe": True,
            "pii_detected": False,
            "redacted_text": text
        }
        
        if self.enable_pii_detection:
            pii_result = PIIDetector.detect_pii(text)
            results["pii_detected"] = pii_result.detected
            results["pii_types"] = pii_result.pii_types
            results["redacted_text"] = pii_result.redacted_text
            
            if pii_result.detected:
                results["text_safe"] = False
                logger.warning(f"PII detected: {pii_result.pii_types}")
        
        return results
    
    def check_creative(
        self,
        creative_text: str,
        disallowed_terms: List[str],
        required_disclaimers: List[str],
        placement_type: str
    ) -> Dict[str, Any]:
        """Check creative content for policy compliance.
        
        Args:
            creative_text: Creative text to check
            disallowed_terms: Disallowed terms
            required_disclaimers: Required disclaimers
            placement_type: Placement type
            
        Returns:
            Compliance check results
        """
        # Check PII first
        pii_check = self.check_text(creative_text)
        
        if not pii_check["text_safe"]:
            return {
                "approved": False,
                "reason": "PII detected in creative",
                "pii_check": pii_check
            }
        
        # Check policy
        if self.enable_policy_checks:
            policy_check = PolicyChecker.check_creative_policy(
                creative_text,
                disallowed_terms,
                required_disclaimers,
                placement_type
            )
            
            return {
                "approved": policy_check["compliant"],
                "policy_check": policy_check,
                "pii_check": pii_check
            }
        
        return {
            "approved": True,
            "pii_check": pii_check
        }
    
    def check_data_query(
        self,
        query: str,
        allowed_tables: Optional[Set[str]] = None,
        allowed_fields: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Check data query for policy compliance.
        
        Args:
            query: SQL query to check
            allowed_tables: Allowed table names
            allowed_fields: Allowed field names
            
        Returns:
            Query check results
        """
        if not self.enable_policy_checks:
            return {"approved": True}
        
        policy_check = PolicyChecker.check_data_access_policy(
            query,
            allowed_tables or set(),
            allowed_fields or set(),
            require_aggregation=True
        )
        
        return {
            "approved": policy_check["compliant"],
            "policy_check": policy_check
        }
    
    def enforce_privacy(
        self,
        data: List[Dict[str, Any]],
        quasi_identifiers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Enforce privacy constraints on data.
        
        Args:
            data: Data records
            quasi_identifiers: Quasi-identifier fields
            
        Returns:
            Privacy enforcement results
        """
        original_count = len(data)
        
        # Apply k-anonymity
        filtered_data = DataPrivacyEnforcer.apply_k_anonymity(
            data,
            k=self.min_cell_size,
            quasi_identifiers=quasi_identifiers
        )
        
        suppressed_count = original_count - len(filtered_data)
        
        return {
            "data": filtered_data,
            "original_count": original_count,
            "filtered_count": len(filtered_data),
            "suppressed_count": suppressed_count,
            "suppression_rate": suppressed_count / original_count if original_count > 0 else 0
        }


def main():
    """CLI entry point for Governance Agent."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Governance Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Check text for PII
    pii_parser = subparsers.add_parser("check-pii", help="Check text for PII")
    pii_parser.add_argument("--text", required=True, help="Text to check")
    
    # Check creative
    creative_parser = subparsers.add_parser("check-creative", help="Check creative compliance")
    creative_parser.add_argument("--input", type=Path, required=True, help="Input JSON file")
    
    # Check query
    query_parser = subparsers.add_parser("check-query", help="Check data query")
    query_parser.add_argument("--query", required=True, help="SQL query to check")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    agent = GovernanceAgent()
    
    if args.command == "check-pii":
        result = agent.check_text(args.text)
        
        print("\n=== PII Check ===")
        print(f"Text Safe: {result['text_safe']}")
        print(f"PII Detected: {result['pii_detected']}")
        
        if result['pii_detected']:
            print(f"PII Types: {', '.join(result['pii_types'])}")
            print(f"\nRedacted Text:\n{result['redacted_text']}")
    
    elif args.command == "check-creative":
        with open(args.input, 'r') as f:
            input_data = json.load(f)
        
        result = agent.check_creative(
            input_data["creative_text"],
            input_data.get("disallowed_terms", []),
            input_data.get("required_disclaimers", []),
            input_data.get("placement_type", "unknown")
        )
        
        print("\n=== Creative Check ===")
        print(f"Approved: {result['approved']}")
        
        if not result['approved']:
            print(f"Reason: {result.get('reason', 'Policy violations')}")
            
            if "policy_check" in result:
                print("\nViolations:")
                for violation in result["policy_check"]["violations"]:
                    print(f"  - {violation}")
    
    elif args.command == "check-query":
        result = agent.check_data_query(args.query)
        
        print("\n=== Query Check ===")
        print(f"Approved: {result['approved']}")
        
        if not result['approved']:
            print("\nViolations:")
            for violation in result["policy_check"]["violations"]:
                print(f"  - {violation['message']}")


if __name__ == "__main__":
    from pathlib import Path
    main()
