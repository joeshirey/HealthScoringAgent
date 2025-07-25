from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class ApiAnalysisAgent(LlmAgent):
    """
    An agent that analyzes code for API effectiveness and correctness.

    This agent uses a large language model to analyze a code snippet and
    determine whether it is using APIs effectively and correctly. It is
    designed to be used as part of a larger code analysis workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the ApiAnalysisAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to analyze the code for API
        effectiveness and correctness.
        """
        super().__init__(model="gemini-1.5-flash", tools=[google_search], **kwargs)
        with open("agentic_code_analyzer/prompts/api_analysis_prompt.md", "r") as f:
            self.instruction = f.read()
