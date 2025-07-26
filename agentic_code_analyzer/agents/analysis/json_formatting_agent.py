from google.adk.agents import LlmAgent

class JsonFormattingAgent(LlmAgent):
    """
    An agent that formats the raw text analysis into a JSON object.

    This agent uses a large language model to take the raw text output from the
    initial analysis and format it into a clean, structured JSON object. It is
    designed to be used as the final step in the evaluation workflow.
    """

    def __init__(self, **kwargs):
        """
        Initializes the JsonFormattingAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to format the raw text analysis into a
        JSON object.
        """
        with open("agentic_code_analyzer/prompts/json_conversion.md", "r") as f:
            prompt_template = f.read()
        super().__init__(
            instruction=prompt_template,
            **kwargs
        )

    def _pre_run(self, ctx):
        """
        A placeholder for any pre-run logic.

        This method is called before the agent is run, and it can be used to
        perform any necessary setup or initialization.
        """
        pass
