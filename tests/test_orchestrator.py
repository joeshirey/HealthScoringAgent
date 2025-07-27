import pytest
from agentic_code_analyzer.orchestrator import ResultProcessingAgent


# Test cases for _safe_json_load
@pytest.mark.parametrize(
    "input_data, expected_output, test_id",
    [
        ('{"key": "value"}', {"key": "value"}, "valid_json_string"),
        ({"key": "value"}, {"key": "value"}, "valid_json_dict"),
        ('```json\n{"key": "value"}\n```', {"key": "value"}, "markdown_json"),
        ('```{"key": "value"}```', {"key": "value"}, "markdown_json_no_lang"),
        ("invalid json", {}, "invalid_json_string"),
        (None, {}, "none_input"),
        (123, {}, "integer_input"),
        ('{"key": "value"}', {"key": "value"}, "demjson_valid_fallback"),
        ('{key: "value"}', {"key": "value"}, "demjson_lenient_keys"),
        # demjson3 can handle trailing commas
        ('{"key": "value",}', {"key": "value"}, "demjson_trailing_comma"),
    ],
)
def test_safe_json_load(input_data, expected_output, test_id):
    """
    Tests the _safe_json_load method with various inputs.
    """
    agent = ResultProcessingAgent(name="test_agent")
    assert agent._safe_json_load(input_data) == expected_output, (
        f"Test failed for: {test_id}"
    )


# Test cases for _enforce_single_penalty_hierarchy
@pytest.mark.parametrize(
    "input_data, expected_output, test_id",
    [
        (
            {
                "criteria_breakdown": [
                    {
                        "criterion_name": "api_effectiveness_and_correctness",
                        "recommendations_for_llm_fix": ["rec_A", "rec_B"],
                    },
                    {
                        "criterion_name": "language_best_practices",
                        "recommendations_for_llm_fix": [
                            "rec_A",
                            "rec_C",
                        ],  # rec_A is a duplicate
                    },
                ]
            },
            {
                "criteria_breakdown": [
                    {
                        "criterion_name": "api_effectiveness_and_correctness",
                        "recommendations_for_llm_fix": ["rec_A", "rec_B"],
                    },
                    {
                        "criterion_name": "language_best_practices",
                        "recommendations_for_llm_fix": ["rec_C"],  # rec_A removed
                    },
                ]
            },
            "simple_deduplication",
        ),
        (
            {
                "criteria_breakdown": [
                    {
                        "criterion_name": "comments_and_code_clarity",
                        "recommendations_for_llm_fix": ["rec_X"],
                    },
                    {
                        "criterion_name": "formatting_and_consistency",
                        "recommendations_for_llm_fix": ["rec_X"],  # Duplicate
                    },
                ]
            },
            {
                "criteria_breakdown": [
                    {
                        "criterion_name": "formatting_and_consistency",
                        "recommendations_for_llm_fix": ["rec_X"],
                    },
                    {
                        "criterion_name": "comments_and_code_clarity",
                        "recommendations_for_llm_fix": [],  # rec_X removed
                    },
                ]
            },
            "hierarchy_respected",
        ),
        (
            {"criteria_breakdown": "not_a_list"},
            {"criteria_breakdown": "not_a_list"},
            "malformed_criteria_breakdown_string",
        ),
        (
            {},  # No criteria_breakdown key
            {},
            "missing_criteria_breakdown",
        ),
        (
            {
                "criteria_breakdown": [
                    "just_a_string",  # malformed item
                    {
                        "criterion_name": "api_effectiveness_and_correctness",
                        "recommendations_for_llm_fix": "not_a_list",  # malformed recommendations
                    },
                ]
            },
            {
                "criteria_breakdown": [
                    {
                        "criterion_name": "api_effectiveness_and_correctness",
                        "recommendations_for_llm_fix": [],
                    }
                ]
            },
            "malformed_input_robustness",
        ),
    ],
)
def test_enforce_single_penalty_hierarchy(input_data, expected_output, test_id):
    """
    Tests the _enforce_single_penalty_hierarchy method.
    """
    agent = ResultProcessingAgent(name="test_agent")
    result = agent._enforce_single_penalty_hierarchy(input_data)

    # Sort criteria_breakdown lists for comparison to ensure test is deterministic
    if "criteria_breakdown" in result and isinstance(
        result["criteria_breakdown"], list
    ):
        # The agent internally sorts, but we sort here again to be safe
        result["criteria_breakdown"] = sorted(
            result["criteria_breakdown"],
            key=lambda x: x.get("criterion_name", "") if isinstance(x, dict) else "",
        )
    if "criteria_breakdown" in expected_output and isinstance(
        expected_output["criteria_breakdown"], list
    ):
        expected_output["criteria_breakdown"] = sorted(
            expected_output["criteria_breakdown"],
            key=lambda x: x.get("criterion_name", "") if isinstance(x, dict) else "",
        )

    assert result == expected_output, f"Test failed for: {test_id}"
