from google.adk.agents import LlmAgent
from google.adk.tools import google_search

class InitialAnalysisAgent(LlmAgent):
    """
    An agent that performs the initial, detailed analysis of the code.

    This agent uses a large language model to perform a detailed analysis of the
    code, using a combination of system instructions and a prompt template to
    guide the analysis. It is designed to be used as part of a larger code
    analysis workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the InitialAnalysisAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to perform a detailed analysis of the
        code.
        """
        with open("agentic_code_analyzer/prompts/system_instructions.md", "r") as f:
            system_instructions = f.read()
        with open("agentic_code_analyzer/prompts/consolidated_eval.md", "r") as f:
            prompt_template = f.read()
        instruction = f"{system_instructions}\n\n{prompt_template}"
        super().__init__(
            instruction=instruction,
            tools=[google_search],
            **kwargs
        )

    def _pre_run(self, ctx):
        """
        A placeholder for any pre-run logic.

        This method is called before the agent is run, and it can be used to
        perform any necessary setup or initialization.
        """
        pass
