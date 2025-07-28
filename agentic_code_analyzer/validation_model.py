"""
This module defines the Pydantic data models used in the validation workflow
and for the final API response.
"""
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class EvaluationValidationOutput(BaseModel):
    """
    Represents the structured output of the validation workflow.

    This model contains the score and reasoning produced by the
    `ValidationOrchestrator`.
    """

    validation_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="A score from 1-10 indicating the quality and correctness of the original evaluation.",
    )
    reasoning: str = Field(
        ...,
        description="A detailed explanation for the validation score, highlighting any discrepancies or confirmations found during the fact-checking process.",
    )


class ValidationAttempt(BaseModel):
    """
    Stores the result of a single validation attempt in the iterative loop.
    """

    validation_score: int = Field(
        ..., description="The validation score for this attempt."
    )
    reasoning: str = Field(
        ..., description="The reasoning provided for this validation score."
    )


class FinalValidatedAnalysisWithHistory(BaseModel):
    """
    Defines the final structure of the API response for the `/analyze` and
    `/analyze_github_link` endpoints.
    """

    analysis: Dict[str, Any] = Field(
        ..., description="The final, validated code analysis object."
    )
    validation_history: List[ValidationAttempt] = Field(
        ..., description="A list of all validation attempts made during the analysis."
    )
