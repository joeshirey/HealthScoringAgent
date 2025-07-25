from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class ApiAnalysisAgent(LlmAgent):
    """An agent that analyzes code for API effectiveness and correctness."""

    def __init__(self, **kwargs):
        super().__init__(model="gemini-1.5-flash", tools=[google_search], **kwargs)
        with open("agentic_code_analyzer/prompts/api_analysis_prompt.md", "r") as f:
            self.instruction = f.read()
