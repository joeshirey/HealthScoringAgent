import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict

class CriteriaBreakdown(BaseModel):
    criterion_name: str
    score: int
    weight: float
    assessment: str
    recommendations_for_llm_fix: List[str]
    generic_problem_categories: List[str]

class Evaluation(BaseModel):
    """A model for evaluating a code sample against a set of criteria."""
    product_category: str
    product_name: str
    overall_compliance_score: int
    criteria_breakdown: List[CriteriaBreakdown]
    llm_fix_summary_for_code_generation: List[str]
    identified_generic_problem_categories: List[str]

with open("agents/prompts/evaluation_agent.md", "r") as f:
    EVALUATION_AGENT_INSTRUCTIONS = f.read()

evaluation_agent = LlmAgent(
    name="evaluation_agent",
    instruction=EVALUATION_AGENT_INSTRUCTIONS,
    model=os.environ.get("VERTEXAI_MODEL_NAME", "gemini-2.5-pro"),
    tools=[google_search],
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json"
    ),
)
