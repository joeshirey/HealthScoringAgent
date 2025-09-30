from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from agentic_code_analyzer.agents.shared_config import GENERATION_CONFIG


def create_api_analysis_agent() -> LlmAgent:
    """Creates the API Analysis Agent."""
    with open("agentic_code_analyzer/prompts/api_analysis_prompt.md", "r") as f:
        prompt = f.read()

    return LlmAgent(
        name="api_analysis",
        instruction=prompt,
        tools=[google_search],
        generation_config=GENERATION_CONFIG,
    )
