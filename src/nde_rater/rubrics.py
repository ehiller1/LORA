"""Rubrics and checklists for NDE rating tasks."""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class RubricCriterion:
    """Single rubric criterion."""
    id: str
    description: str
    weight: float = 1.0
    is_required: bool = True


@dataclass
class Rubric:
    """Complete rubric for a task type."""
    task_type: str
    criteria: List[RubricCriterion]
    reason_codes: List[Dict[str, str]]
    examples: List[Dict[str, Any]]


# Tool Call QA Rubric
TOOL_CALL_QA_RUBRIC = Rubric(
    task_type="tool_call_qa",
    criteria=[
        RubricCriterion(
            id="valid_json",
            description="JSON/SQL is syntactically valid (passes auto-lint)",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="correct_function",
            description="Calls the correct function/API for the intent",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="complete_params",
            description="All required parameters are present",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="correct_types",
            description="Parameter types match schema",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="handles_edge_cases",
            description="Handles null/empty/boundary cases appropriately",
            weight=1.0,
            is_required=False
        ),
        RubricCriterion(
            id="efficient",
            description="Uses efficient approach (no unnecessary calls)",
            weight=0.5,
            is_required=False
        )
    ],
    reason_codes=[
        {"code": "syntax_error", "label": "Syntax error in JSON/SQL"},
        {"code": "wrong_function", "label": "Wrong function called"},
        {"code": "missing_params", "label": "Missing required parameters"},
        {"code": "wrong_types", "label": "Incorrect parameter types"},
        {"code": "incomplete", "label": "Doesn't fully address intent"},
        {"code": "edge_case_fail", "label": "Fails on edge cases"},
        {"code": "inefficient", "label": "Unnecessarily complex"},
        {"code": "both_good", "label": "Both are valid (tie)"},
        {"code": "both_bad", "label": "Both have critical issues"}
    ],
    examples=[
        {
            "intent": "Query campaign performance for last 30 days",
            "good": {
                "function": "query_clean_room",
                "args": {
                    "query": "SELECT * FROM performance WHERE date >= DATE_SUB(NOW(), INTERVAL 30 DAY)",
                    "filters": {}
                }
            },
            "bad": {
                "function": "query_clean_room",
                "args": {
                    "query": "SELECT * FROM performance",  # Missing date filter
                    "filters": {}
                }
            },
            "reason": "Good version includes required date filter"
        }
    ]
)


# Schema Mapping Rubric
SCHEMA_MAPPING_RUBRIC = Rubric(
    task_type="schema_mapping",
    criteria=[
        RubricCriterion(
            id="field_match",
            description="Retailer field correctly maps to canonical field",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="type_compatible",
            description="Data types are compatible",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="transformation_correct",
            description="Transformation logic is correct (if needed)",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="complete_coverage",
            description="All required canonical fields are mapped",
            weight=1.0,
            is_required=True
        ),
        RubricCriterion(
            id="handles_nulls",
            description="Handles null/missing values appropriately",
            weight=1.0,
            is_required=False
        ),
        RubricCriterion(
            id="preserves_semantics",
            description="Preserves semantic meaning during transformation",
            weight=1.0,
            is_required=True
        )
    ],
    reason_codes=[
        {"code": "wrong_field", "label": "Maps to wrong canonical field"},
        {"code": "type_mismatch", "label": "Incompatible data types"},
        {"code": "bad_transformation", "label": "Incorrect transformation logic"},
        {"code": "missing_fields", "label": "Missing required fields"},
        {"code": "null_handling", "label": "Poor null/missing value handling"},
        {"code": "semantic_loss", "label": "Loses semantic meaning"},
        {"code": "both_valid", "label": "Both mappings are valid"},
        {"code": "needs_expert", "label": "Ambiguous - needs expert"}
    ],
    examples=[
        {
            "retailer_field": "evt_timestamp",
            "canonical_field": "ts",
            "good_mapping": {
                "from": "evt_timestamp",
                "to": "ts",
                "transform": "to_utc"
            },
            "bad_mapping": {
                "from": "evt_timestamp",
                "to": "ts"
                # Missing timezone conversion
            },
            "reason": "Good version includes UTC conversion"
        }
    ]
)


# Policy Compliance Rubric
POLICY_COMPLIANCE_RUBRIC = Rubric(
    task_type="policy_compliance",
    criteria=[
        RubricCriterion(
            id="no_disallowed_terms",
            description="Contains no disallowed terms from policy",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="required_disclaimers",
            description="Includes all required disclaimers",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="length_compliant",
            description="Meets length requirements (headline, body)",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="format_compliant",
            description="Follows format specifications",
            weight=1.0,
            is_required=True
        ),
        RubricCriterion(
            id="brand_safe",
            description="Brand-safe and appropriate tone",
            weight=1.0,
            is_required=True
        ),
        RubricCriterion(
            id="claim_substantiated",
            description="Claims are substantiated (if applicable)",
            weight=1.0,
            is_required=False
        )
    ],
    reason_codes=[
        {"code": "disallowed_term", "label": "Contains disallowed term"},
        {"code": "missing_disclaimer", "label": "Missing required disclaimer"},
        {"code": "too_long", "label": "Exceeds length limit"},
        {"code": "too_short", "label": "Below minimum length"},
        {"code": "format_violation", "label": "Format violation"},
        {"code": "inappropriate_tone", "label": "Inappropriate tone"},
        {"code": "unsubstantiated_claim", "label": "Unsubstantiated claim"},
        {"code": "both_compliant", "label": "Both pass policy"},
        {"code": "both_violate", "label": "Both violate policy"}
    ],
    examples=[
        {
            "policy_excerpt": "Max headline length: 80 chars. Disallowed: 'guaranteed', 'miracle'",
            "good": "Premium Quality Snacks - Award-Winning Taste",
            "bad": "Guaranteed Best Snacks - Miracle Formula!",
            "reason": "Bad version uses disallowed terms 'guaranteed' and 'miracle'"
        }
    ]
)


# Plan Quality Rubric
PLAN_QUALITY_RUBRIC = Rubric(
    task_type="plan_quality",
    criteria=[
        RubricCriterion(
            id="addresses_objective",
            description="Directly addresses the stated objective",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="respects_constraints",
            description="Respects all stated constraints (budget, ROAS, etc.)",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="clear_structure",
            description="Clear, logical structure and flow",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="actionable_steps",
            description="Steps are concrete and actionable",
            weight=1.5,
            is_required=True
        ),
        RubricCriterion(
            id="includes_metrics",
            description="Includes relevant metrics and KPIs",
            weight=1.0,
            is_required=False
        ),
        RubricCriterion(
            id="rationale_provided",
            description="Provides rationale for key decisions",
            weight=1.0,
            is_required=False
        )
    ],
    reason_codes=[
        {"code": "misses_objective", "label": "Doesn't address objective"},
        {"code": "violates_constraints", "label": "Violates constraints"},
        {"code": "unclear", "label": "Unclear or confusing"},
        {"code": "not_actionable", "label": "Steps not actionable"},
        {"code": "missing_metrics", "label": "Missing key metrics"},
        {"code": "no_rationale", "label": "No rationale provided"},
        {"code": "both_good", "label": "Both are good plans"},
        {"code": "both_weak", "label": "Both have significant issues"}
    ],
    examples=[
        {
            "objective": "Allocate $100k across 3 RMNs with min 2.5x ROAS",
            "good": "Allocate: Amazon $45k (3.2x ROAS), Walmart $35k (2.8x ROAS), Target $20k (2.6x ROAS). Reserve $10k for experiments. Expected blended ROAS: 2.9x.",
            "bad": "Split evenly: $33k each to Amazon, Walmart, Target.",
            "reason": "Good version considers ROAS targets and includes rationale"
        }
    ]
)


# Tagging Normalization Rubric
TAGGING_NORMALIZATION_RUBRIC = Rubric(
    task_type="tagging_normalization",
    criteria=[
        RubricCriterion(
            id="correct_category",
            description="Tag matches correct category in taxonomy",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="consistent_format",
            description="Uses consistent format/casing",
            weight=1.0,
            is_required=True
        ),
        RubricCriterion(
            id="handles_variants",
            description="Correctly handles variants/synonyms",
            weight=1.0,
            is_required=True
        ),
        RubricCriterion(
            id="preserves_meaning",
            description="Preserves original semantic meaning",
            weight=1.5,
            is_required=True
        )
    ],
    reason_codes=[
        {"code": "wrong_category", "label": "Wrong category in taxonomy"},
        {"code": "format_inconsistent", "label": "Inconsistent format"},
        {"code": "variant_mismatch", "label": "Doesn't handle variant correctly"},
        {"code": "meaning_lost", "label": "Loses semantic meaning"},
        {"code": "both_correct", "label": "Both normalizations are correct"},
        {"code": "uncertain", "label": "Uncertain - needs expert"}
    ],
    examples=[
        {
            "raw_tag": "sp_ad",
            "taxonomy": {"sponsored_product": ["sp", "sp_ad", "sponsored product"]},
            "good": "sponsored_product",
            "bad": "sp_ad",
            "reason": "Good version uses canonical taxonomy term"
        }
    ]
)


# Edge Case Red Team Rubric
EDGE_CASE_RED_TEAM_RUBRIC = Rubric(
    task_type="edge_case_red_team",
    criteria=[
        RubricCriterion(
            id="handles_edge_case",
            description="Correctly handles the edge case",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="no_errors",
            description="Doesn't crash or produce errors",
            weight=2.0,
            is_required=True
        ),
        RubricCriterion(
            id="graceful_degradation",
            description="Degrades gracefully if can't handle",
            weight=1.5,
            is_required=False
        ),
        RubricCriterion(
            id="appropriate_fallback",
            description="Uses appropriate fallback behavior",
            weight=1.0,
            is_required=False
        )
    ],
    reason_codes=[
        {"code": "fails_edge_case", "label": "Fails on edge case"},
        {"code": "crashes", "label": "Crashes or errors"},
        {"code": "poor_degradation", "label": "Poor graceful degradation"},
        {"code": "bad_fallback", "label": "Inappropriate fallback"},
        {"code": "both_handle", "label": "Both handle edge case well"},
        {"code": "both_fail", "label": "Both fail on edge case"}
    ],
    examples=[
        {
            "edge_case": "Empty product list",
            "good": "Returns empty array with success status",
            "bad": "Throws NullPointerException",
            "reason": "Good version handles empty input gracefully"
        }
    ]
)


# Rubric registry
RUBRICS = {
    "tool_call_qa": TOOL_CALL_QA_RUBRIC,
    "schema_mapping": SCHEMA_MAPPING_RUBRIC,
    "policy_compliance": POLICY_COMPLIANCE_RUBRIC,
    "plan_quality": PLAN_QUALITY_RUBRIC,
    "tagging_normalization": TAGGING_NORMALIZATION_RUBRIC,
    "edge_case_red_team": EDGE_CASE_RED_TEAM_RUBRIC
}


def get_rubric(task_type: str) -> Rubric:
    """Get rubric for task type."""
    return RUBRICS.get(task_type)


def calculate_rubric_score(
    rubric: Rubric,
    criterion_scores: Dict[str, float]
) -> float:
    """
    Calculate weighted rubric score.
    
    Args:
        rubric: Rubric definition
        criterion_scores: Dict of criterion_id -> score (0-1)
    
    Returns:
        Weighted score (0-1)
    """
    total_weight = sum(c.weight for c in rubric.criteria)
    weighted_sum = sum(
        criterion_scores.get(c.id, 0.0) * c.weight
        for c in rubric.criteria
    )
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def check_required_criteria(
    rubric: Rubric,
    criterion_scores: Dict[str, float],
    threshold: float = 0.5
) -> bool:
    """
    Check if all required criteria pass threshold.
    
    Args:
        rubric: Rubric definition
        criterion_scores: Dict of criterion_id -> score (0-1)
        threshold: Minimum passing score
    
    Returns:
        True if all required criteria pass
    """
    for criterion in rubric.criteria:
        if criterion.is_required:
            score = criterion_scores.get(criterion.id, 0.0)
            if score < threshold:
                return False
    return True
