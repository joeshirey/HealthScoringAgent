from google.adk.agents import LlmAgent

class CodeQualityAgent(LlmAgent):
    """
    An agent that analyzes code for quality.

    This agent uses a large language model to analyze a code snippet and
    assess its overall quality. It is designed to be used as part of a larger
    code analysis workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the CodeQualityAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to analyze the code for quality.
        """
        super().__init__(**kwargs)
        with open("agentic_code_analyzer/prompts/code_quality_prompt.md", "r") as f:
            self.instruction = f.read()
