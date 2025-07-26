from google.adk.agents import LlmAgent

class LanguageDetectionAgent(LlmAgent):
    """
    An agent that detects the programming language of a code snippet.

    This agent uses a large language model to identify the programming language
    of a given code snippet. It is designed to be fast and accurate, and it
    supports a wide range of popular programming languages.
    """

    def __init__(self, **kwargs):
        """
        Initializes the LanguageDetectionAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to identify the programming language of
        a code snippet.
        """
        with open("agentic_code_analyzer/prompts/language_detection.md", "r") as f:
            instruction = f.read()
        super().__init__(
            instruction=instruction,
            **kwargs
        )
