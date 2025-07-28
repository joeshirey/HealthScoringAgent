"""
This module defines the Pydantic data models that structure the output of the
Health Scoring Agent. These models ensure that the JSON output is consistent,
well-defined, and easy to parse by downstream consumers.
"""

from typing import List, Literal, Union

from pydantic import BaseModel, Field

# Using a Literal type for criterion names ensures that the output conforms to
# a predefined set of categories, preventing unexpected or misspelled names.
CriterionName = Literal[
    "runnability_and_configuration",
    "api_effectiveness_and_correctness",
    "comments_and_code_clarity",
    "formatting_and_consistency",
    "language_best_practices",
    "llm_training_fitness_and_explicitness",
]


# --- Structured Assessment Models ---
# These models provide detailed, structured information for specific criteria,
# offering more than just a simple string evaluation.


class SyntaxValidity(BaseModel):
    """Model for syntax validity checks."""

    is_valid: bool = Field(..., description="Whether the code syntax is valid.")
    reasoning: str = Field(..., description="Explanation for the validity status.")


class DependencyManagement(BaseModel):
    """Model for dependency management checks."""

    has_dependencies: bool = Field(
        ..., description="Whether the code has external dependencies."
    )
    are_declared: Literal["Yes", "No", "NA"] = Field(
        ..., description="Whether dependencies are declared in a manifest file."
    )
    reasoning: str = Field(
        ..., description="Explanation of the dependency management status."
    )


class ConfigurationManagement(BaseModel):
    """Model for configuration management checks."""

    uses_env_vars: bool = Field(
        ...,
        description="Whether the code uses environment variables for configuration.",
    )
    are_documented: Literal["Yes", "No", "NA"] = Field(
        ..., description="Whether the required environment variables are documented."
    )
    reasoning: str = Field(
        ..., description="Explanation of the configuration management status."
    )


class HardcodedValues(BaseModel):
    """Model for identifying hardcoded, non-trivial values."""

    contains_hardcoded_values: bool = Field(
        ...,
        description="Whether the code contains hardcoded values like project IDs or keys.",
    )
    details: str = Field(..., description="Details about the hardcoded values found.")


class RunnabilityChecks(BaseModel):
    """A composite model for all runnability and configuration checks."""

    syntax_validity: SyntaxValidity
    dependency_management: DependencyManagement
    configuration_management: ConfigurationManagement
    hardcoded_values: HardcodedValues


class ApiEvaluationDetail(BaseModel):
    """Model for the evaluation status of a specific API check."""

    status: Literal["Pass", "Fail", "NA"] = Field(
        ..., description="The result of the check (Pass, Fail, or Not Applicable)."
    )
    reasoning: str = Field(
        ..., description="The reasoning behind the evaluation status."
    )


class ApiCallEvaluation(BaseModel):
    """A composite model for evaluating a single API call."""

    method_existence_check: ApiEvaluationDetail
    parameter_check: ApiEvaluationDetail
    response_handling_check: ApiEvaluationDetail
    error_handling_check: ApiEvaluationDetail


class ApiCallAnalysis(BaseModel):
    """Model for the analysis of a specific API call found in the code."""

    method_name: str = Field(
        ..., description="The name of the API method being called."
    )
    line_number: int = Field(
        ..., description="The line number where the API call is made."
    )
    evaluation: ApiCallEvaluation


# --- Main Evaluation Schema ---


class CriteriaBreakdown(BaseModel):
    """
    Represents the detailed evaluation for a single criterion.
    """

    criterion_name: CriterionName = Field(
        ..., description="The name of the criterion being assessed."
    )
    score: int = Field(
        ..., ge=0, le=100, description="The score for this criterion, from 0 to 100."
    )
    weight: float = Field(
        ..., description="The weight of this criterion in the overall final score."
    )
    evaluation: str = Field(
        ..., description="A high-level summary of the evaluation for this criterion."
    )
    evaluation_details: Union[str, RunnabilityChecks, List[ApiCallAnalysis]] = Field(
        ...,
        description="Detailed evaluation, which can be a simple string or a structured object for specific criteria.",
    )
    recommendations_for_llm_fix: List[str] = Field(
        default=[],
        description="Actionable recommendations for an LLM to automatically fix the identified issues.",
    )
    generic_problem_categories: List[str] = Field(
        default=[],
        description="A list of generic categories for the identified problems.",
    )


class Citation(BaseModel):
    """Represents a citation used in the analysis."""

    citation_number: int = Field(..., description="The unique number of the citation.")
    url: str = Field(..., description="The URL of the cited source material.")


class EvaluationOutput(BaseModel):
    """
    The main Pydantic model for the final, structured output of the entire
    evaluation workflow. This is the object that is ultimately returned to the
    user.
    """

    overall_compliance_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="The final, weighted overall compliance score for the code sample.",
    )
    criteria_breakdown: List[CriteriaBreakdown] = Field(
        ...,
        min_length=1,
        description="A detailed breakdown of the score by each criterion.",
    )
    llm_fix_summary_for_code_generation: List[str] = Field(
        default=[],
        description="A summary of all recommendations that an LLM could use to fix the code.",
    )
    identified_generic_problem_categories: List[str] = Field(
        default=[],
        description="A unique list of all generic problem categories identified across all criteria.",
    )
    citations: List[Citation] = Field(
        default=[], description="A list of all citations used to support the analysis."
    )
