from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from agentic_code_analyzer.tools.code_cleaning import remove_comments

class InitialAnalysisAgent(LlmAgent):
    """An agent that performs the initial, detailed analysis of the code."""

    def __init__(self, **kwargs):
        with open("agentic_code_analyzer/prompts/system_instructions.txt", "r") as f:
            system_instructions = f.read()
        with open("agentic_code_analyzer/prompts/consolidated_eval.txt", "r") as f:
            prompt_template = f.read()
        instruction = f"{system_instructions}\n\n{prompt_template}"
        super().__init__(
            instruction=instruction,
            tools=[google_search],
            **kwargs
        )

    def _pre_run(self, ctx):
        pass