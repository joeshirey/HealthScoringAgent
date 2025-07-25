from google.adk.agents import LlmAgent

class JsonFormattingAgent(LlmAgent):
    """An agent that formats the raw text analysis into a JSON object."""

    def __init__(self, **kwargs):
        with open("agentic_code_analyzer/prompts/json_conversion.txt", "r") as f:
            prompt_template = f.read()
        super().__init__(
            instruction=prompt_template,
            **kwargs
        )

    def _pre_run(self, ctx):
        pass