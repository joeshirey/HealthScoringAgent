from google.adk.agents import LlmAgent

class CodeQualityAgent(LlmAgent):
    """An agent that analyzes code for quality."""

    def __init__(self, **kwargs):
        super().__init__(
            model="gemini-1.5-flash",
            instruction="You are an expert programmer and your task is to analyze the provided code snippet for code quality, including formatting, consistency, and adherence to language best practices. Provide your analysis in a JSON format. The code snippet is: {code_snippet}",
            **kwargs
        )
