import os
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

MODEL = os.getenv("VERTEXAI_MODEL_NAME", "gemini-2.5-flash")

# Instruction for the first agent
instruction_path = os.path.join(os.path.dirname(__file__), "code_eval_agent_instruction.md")
with open(instruction_path, "r") as f:
    instruction = f.read()

# Agent 1: Code Evaluation with Google Search
code_eval_agent = Agent(
    name="code_eval_agent",
    model=MODEL,
    instruction=instruction,
    description="Evaluates code using Google Search and generates a JSON report.",
    tools=[google_search]
)

# Pydantic schema for the second agent
class CriteriaBreakdown(BaseModel):
    criterion_name: str = Field(..., description="A specific, computer-friendly name for the criterion.")
    score: int = Field(..., description="0-100 for this specific criterion")
    weight: float = Field(..., description="The weight of this criterion in the overall score")
    assessment: str = Field(..., description="Your detailed assessment for this criterion, explaining the score given.")
    recommendations_for_llm_fix: List[str] = Field(..., description="Specific, actionable instructions an LLM could use to directly modify the code.")
    generic_problem_categories: List[str] = Field(..., description="Keywords or phrases categorizing the types of issues found.")

class EvaluationResult(BaseModel):
    overall_compliance_score: int = Field(..., description="integer (0-100)")
    criteria_breakdown: List[CriteriaBreakdown] = Field(..., description="A list of detailed assessments for each criterion.")
    llm_fix_summary_for_code_generation: List[str] = Field(..., description="A list of all 'recommendations_for_llm_fix' from the breakdowns.")
    identified_generic_problem_categories: List[str] = Field(..., description="A unique list of all 'generic_problem_categories' identified across all criteria.")

# Agent 2: JSON Formatter
json_formatter_agent = Agent(
    name="json_formatter_agent",
    model=MODEL,
    instruction="Format the incoming JSON to conform to the provided schema. Do not add, remove, or change any of the content.",
    output_schema=EvaluationResult,
    description="Formats JSON output to a strict schema.",
)

# Sequential Agent Workflow
root_agent = SequentialAgent(
    name="health_scoring_agent",
    sub_agents=[code_eval_agent, json_formatter_agent],
    description="A sequential agent that first evaluates code and then formats the output."
)
