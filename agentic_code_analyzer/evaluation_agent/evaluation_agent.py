from google.adk.agents import LlmAgent

class EvaluationReviewAgent(LlmAgent):
    """An agent that reviews the code analysis and provides a score for its accuracy."""

    def __init__(self, **kwargs):
        super().__init__(
            instruction="You are an expert software engineering manager and your task is to review the provided code analysis and provide a score for its accuracy. Provide your review in a JSON format.",
            **kwargs
        )