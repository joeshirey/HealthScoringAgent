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
        super().__init__(
            model="gemini-1.5-flash",
            instruction="You are an expert programmer and your task is to identify the programming language of the provided code snippet. Your response should only be one of the following supported languages: Javascript, Typescript, Python, Java, Go, Rust, Ruby, C#, C++, PHP. Do not provide any other information in your response. If you cannot determine the language, respond with \"Unknown\". The code snippet is: {code_snippet}",
            **kwargs
        )
