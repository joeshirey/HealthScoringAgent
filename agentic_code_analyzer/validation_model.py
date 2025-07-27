from pydantic import BaseModel, Field

class EvaluationValidationOutput(BaseModel):
    """
    Represents the output of the evaluation validation agent.
    """
    validation_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="A score from 1-10 indicating the quality and correctness of the original evaluation."
    )
    reasoning: str = Field(
        ...,
        description="A detailed explanation of the validation score, highlighting any discrepancies or confirmations found."
    )
