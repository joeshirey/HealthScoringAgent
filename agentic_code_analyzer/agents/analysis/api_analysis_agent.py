from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class ApiAnalysisAgent(LlmAgent):
    """An agent that analyzes code for API effectiveness and correctness."""

    def __init__(self, **kwargs):
        super().__init__(
            model="gemini-1.5-flash",
            instruction="You are an expert programmer and your task is to analyze the provided code snippet for API effectiveness and correctness. Provide your analysis in a JSON format. The code snippet is: {code_snippet}",
            tools=[google_search],
            **kwargs
        )
