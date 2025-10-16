"""Auto-checks for rating tasks (free shaping signals)."""

import json
import re
import sqlparse
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AutoCheckResult:
    """Result of an auto-check."""
    
    def __init__(self, check_name: str, passed: bool, details: str = ""):
        self.check_name = check_name
        self.passed = passed
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "details": self.details
        }


class AutoCheckEngine:
    """Engine for running auto-checks on candidates."""
    
    def __init__(self):
        """Initialize auto-check engine."""
        self.checks = {
            "tool_call_qa": self._check_tool_call,
            "schema_mapping": self._check_schema_mapping,
            "policy_compliance": self._check_policy_compliance,
            "plan_quality": self._check_plan_quality,
            "tagging_normalization": self._check_tagging,
            "edge_case_red_team": self._check_edge_case
        }
    
    def run_checks(
        self,
        task_type: str,
        candidate: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> List[AutoCheckResult]:
        """
        Run auto-checks for a candidate.
        
        Args:
            task_type: Type of task
            candidate: Candidate to check
            context: Additional context
        
        Returns:
            List of check results
        """
        check_func = self.checks.get(task_type)
        if not check_func:
            return []
        
        try:
            return check_func(candidate, context or {})
        except Exception as e:
            logger.error(f"Auto-check error: {e}")
            return [AutoCheckResult("error", False, str(e))]
    
    def _check_tool_call(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check tool call validity."""
        results = []
        
        # Check JSON validity
        try:
            if isinstance(candidate, str):
                json.loads(candidate)
            results.append(AutoCheckResult("json_valid", True, "Valid JSON"))
        except json.JSONDecodeError as e:
            results.append(AutoCheckResult("json_valid", False, f"Invalid JSON: {e}"))
            return results  # Can't continue if JSON is invalid
        
        # Check if it's a dict
        if not isinstance(candidate, dict):
            results.append(AutoCheckResult("is_dict", False, "Not a dictionary"))
            return results
        
        # Check for required fields
        if "function" in candidate or "tool" in candidate:
            results.append(AutoCheckResult("has_function", True, "Function specified"))
        else:
            results.append(AutoCheckResult("has_function", False, "No function specified"))
        
        if "args" in candidate or "arguments" in candidate:
            results.append(AutoCheckResult("has_args", True, "Arguments present"))
        else:
            results.append(AutoCheckResult("has_args", False, "No arguments"))
        
        # Check SQL if present
        args = candidate.get("args", candidate.get("arguments", {}))
        if isinstance(args, dict) and "query" in args:
            sql = args["query"]
            try:
                parsed = sqlparse.parse(sql)
                if parsed:
                    results.append(AutoCheckResult("sql_valid", True, "Valid SQL"))
                else:
                    results.append(AutoCheckResult("sql_valid", False, "Empty SQL"))
            except Exception as e:
                results.append(AutoCheckResult("sql_valid", False, f"SQL error: {e}"))
        
        return results
    
    def _check_schema_mapping(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check schema mapping validity."""
        results = []
        
        # Check required fields
        required_fields = ["from", "to"]
        for field in required_fields:
            if field in candidate:
                results.append(AutoCheckResult(f"has_{field}", True, f"Has {field} field"))
            else:
                results.append(AutoCheckResult(f"has_{field}", False, f"Missing {field} field"))
        
        # Check type compatibility
        if "type" in candidate:
            valid_types = ["string", "integer", "float", "boolean", "datetime", "json"]
            if candidate["type"] in valid_types:
                results.append(AutoCheckResult("valid_type", True, f"Valid type: {candidate['type']}"))
            else:
                results.append(AutoCheckResult("valid_type", False, f"Invalid type: {candidate['type']}"))
        
        # Check transformation validity
        if "transform" in candidate:
            valid_transforms = ["to_utc", "to_fraction", "normalize", "lowercase", "uppercase"]
            if candidate["transform"] in valid_transforms:
                results.append(AutoCheckResult("valid_transform", True, f"Valid transform: {candidate['transform']}"))
            else:
                results.append(AutoCheckResult("valid_transform", False, f"Unknown transform: {candidate['transform']}"))
        
        return results
    
    def _check_policy_compliance(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check policy compliance."""
        results = []
        
        # Get text to check
        text = ""
        if isinstance(candidate, str):
            text = candidate
        elif isinstance(candidate, dict):
            text = candidate.get("headline", "") + " " + candidate.get("body", "")
        
        # Check disallowed terms
        disallowed_terms = context.get("disallowed_terms", [])
        found_disallowed = []
        for term in disallowed_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                found_disallowed.append(term)
        
        if found_disallowed:
            results.append(AutoCheckResult(
                "no_disallowed_terms",
                False,
                f"Found disallowed terms: {', '.join(found_disallowed)}"
            ))
        else:
            results.append(AutoCheckResult("no_disallowed_terms", True, "No disallowed terms"))
        
        # Check length limits
        if isinstance(candidate, dict):
            if "headline" in candidate:
                headline = candidate["headline"]
                max_length = context.get("max_headline_length", 100)
                if len(headline) <= max_length:
                    results.append(AutoCheckResult("headline_length", True, f"{len(headline)}/{max_length} chars"))
                else:
                    results.append(AutoCheckResult("headline_length", False, f"{len(headline)}/{max_length} chars (too long)"))
            
            if "body" in candidate:
                body = candidate["body"]
                max_length = context.get("max_body_length", 250)
                if len(body) <= max_length:
                    results.append(AutoCheckResult("body_length", True, f"{len(body)}/{max_length} chars"))
                else:
                    results.append(AutoCheckResult("body_length", False, f"{len(body)}/{max_length} chars (too long)"))
        
        # Check required disclaimers
        required_disclaimers = context.get("required_disclaimers", [])
        missing_disclaimers = []
        for disclaimer in required_disclaimers:
            if disclaimer.lower() not in text.lower():
                missing_disclaimers.append(disclaimer)
        
        if missing_disclaimers:
            results.append(AutoCheckResult(
                "has_disclaimers",
                False,
                f"Missing disclaimers: {', '.join(missing_disclaimers)}"
            ))
        else:
            results.append(AutoCheckResult("has_disclaimers", True, "All disclaimers present"))
        
        return results
    
    def _check_plan_quality(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check plan quality."""
        results = []
        
        # Get plan text
        plan_text = ""
        if isinstance(candidate, str):
            plan_text = candidate
        elif isinstance(candidate, dict):
            plan_text = candidate.get("plan", "") + " " + candidate.get("rationale", "")
        
        # Check for budget mention
        if re.search(r'\$[\d,]+|\d+k', plan_text, re.IGNORECASE):
            results.append(AutoCheckResult("mentions_budget", True, "Mentions budget"))
        else:
            results.append(AutoCheckResult("mentions_budget", False, "No budget mentioned"))
        
        # Check for ROAS mention
        if re.search(r'roas|return on ad spend|\d+\.?\d*x', plan_text, re.IGNORECASE):
            results.append(AutoCheckResult("mentions_roas", True, "Mentions ROAS"))
        else:
            results.append(AutoCheckResult("mentions_roas", False, "No ROAS mentioned"))
        
        # Check for structure
        if isinstance(candidate, dict):
            if "allocations" in candidate or "steps" in candidate:
                results.append(AutoCheckResult("has_structure", True, "Has structured format"))
            else:
                results.append(AutoCheckResult("has_structure", False, "Missing structure"))
        
        # Check constraints
        constraints = context.get("constraints", {})
        if constraints:
            mentions_constraints = False
            for key in constraints.keys():
                if key.replace("_", " ") in plan_text.lower():
                    mentions_constraints = True
                    break
            
            if mentions_constraints:
                results.append(AutoCheckResult("addresses_constraints", True, "Addresses constraints"))
            else:
                results.append(AutoCheckResult("addresses_constraints", False, "Doesn't address constraints"))
        
        return results
    
    def _check_tagging(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check tagging normalization."""
        results = []
        
        # Get tag
        tag = candidate if isinstance(candidate, str) else candidate.get("tag", "")
        
        # Check format (lowercase, underscores)
        if tag.islower() and "_" in tag:
            results.append(AutoCheckResult("correct_format", True, "Correct format (lowercase_underscore)"))
        else:
            results.append(AutoCheckResult("correct_format", False, "Incorrect format"))
        
        # Check against taxonomy
        taxonomy = context.get("taxonomy", {})
        if taxonomy:
            found_in_taxonomy = False
            for category, variants in taxonomy.items():
                if tag in variants or tag == category:
                    found_in_taxonomy = True
                    results.append(AutoCheckResult("in_taxonomy", True, f"Found in category: {category}"))
                    break
            
            if not found_in_taxonomy:
                results.append(AutoCheckResult("in_taxonomy", False, "Not found in taxonomy"))
        
        return results
    
    def _check_edge_case(
        self,
        candidate: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[AutoCheckResult]:
        """Check edge case handling."""
        results = []
        
        # Check for error handling
        if isinstance(candidate, dict):
            if "error" in candidate or "status" in candidate:
                results.append(AutoCheckResult("has_error_handling", True, "Has error handling"))
            else:
                results.append(AutoCheckResult("has_error_handling", False, "No error handling"))
            
            # Check for null handling
            if "null" in str(candidate).lower() or "none" in str(candidate).lower():
                results.append(AutoCheckResult("handles_nulls", True, "Handles null values"))
        
        # Check for empty array/object handling
        if isinstance(candidate, (list, dict)):
            if len(candidate) == 0:
                results.append(AutoCheckResult("handles_empty", True, "Handles empty input"))
        
        return results


def run_auto_checks_for_task(
    task_type: str,
    candidate_a: Dict[str, Any],
    candidate_b: Dict[str, Any],
    context: Dict[str, Any] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Run auto-checks for both candidates.
    
    Args:
        task_type: Type of task
        candidate_a: First candidate
        candidate_b: Second candidate
        context: Additional context
    
    Returns:
        Dict with results for both candidates
    """
    engine = AutoCheckEngine()
    
    results_a = engine.run_checks(task_type, candidate_a, context)
    results_b = engine.run_checks(task_type, candidate_b, context)
    
    return {
        "candidate_a": [r.to_dict() for r in results_a],
        "candidate_b": [r.to_dict() for r in results_b],
        "summary": {
            "a_passed": sum(1 for r in results_a if r.passed),
            "a_failed": sum(1 for r in results_a if not r.passed),
            "b_passed": sum(1 for r in results_b if r.passed),
            "b_failed": sum(1 for r in results_b if not r.passed)
        }
    }
