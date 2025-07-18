import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict

from agents.evaluation_agent import Evaluation

class Validation(BaseModel):
    """A model for validating the evaluation of a code sample."""
    is_evaluation_correct: bool = Field(
        description="Whether the evaluation is correct."
    )
    agreement_score: int = Field(
        description="An agreement score between the evaluation and validation."
    )
    summary: str = Field(
        description="A concise summary of the validation findings."
    )
    discrepancies: List[Dict[str, str]] = Field(
        description="""A list of discrepancies between the evaluation and
        validation."""
    )

VALIDATION_AGENT_INSTRUCTIONS = "You are a critical reviewer of code evaluations."

validation_agent = LlmAgent(
    name="validation_agent",
    instruction=VALIDATION_AGENT_INSTRUCTIONS,
    model=os.environ.get("VERTEXAI_MODEL_NAME", "gemini-2.5-pro"),
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json"
    ),
)
