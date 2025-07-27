from google.adk.agents import LlmAgent


class RunnabilityAgent(LlmAgent):
    """
    An agent that analyzes code for runnability.

    This agent uses a large language model to analyze a code snippet and
    determine whether it is runnable. It is designed to be used as part of a
    larger code analysis workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the RunnabilityAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to analyze the code for runnability.
        """
        super().__init__(**kwargs)
        with open("agentic_code_analyzer/prompts/runnability_prompt.md", "r") as f:
            self.instruction = f.read()
