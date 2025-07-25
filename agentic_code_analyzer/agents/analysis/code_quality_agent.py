from google.adk.agents import LlmAgent

class CodeQualityAgent(LlmAgent):
    """An agent that analyzes code for quality."""

    def __init__(self, **kwargs):
        super().__init__(model="gemini-1.5-flash", **kwargs)
        with open("agentic_code_analyzer/prompts/code_quality_prompt.md", "r") as f:
            self.instruction = f.read()
