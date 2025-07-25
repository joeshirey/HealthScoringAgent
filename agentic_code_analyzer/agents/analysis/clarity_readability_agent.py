from google.adk.agents import LlmAgent

class ClarityReadabilityAgent(LlmAgent):
    """
    An agent that analyzes code for clarity and readability.

    This agent uses a large language model to analyze a code snippet and
    determine whether it is clear, readable, and easy to understand. It is
    designed to be used as part of a larger code analysis workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the ClarityReadabilityAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to analyze the code for clarity and
        readability.
        """
        super().__init__(model="gemini-1.5-flash", **kwargs)
        with open("agentic_code_analyzer/prompts/clarity_readability_prompt.md", "r") as f:
            self.instruction = f.read()
