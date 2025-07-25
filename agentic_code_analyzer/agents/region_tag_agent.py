from google.adk.agents import LlmAgent

class RegionTagExtractionAgent(LlmAgent):
    """
    An agent that extracts region tags from a code snippet.

    This agent uses a large language model to identify and extract all the unique
    region tags from a given code snippet. Region tags are used to identify and
    group related code blocks, and they typically appear in comments in the format
    `[START tag_name]` and `[END tag_name]`.
    """

    def __init__(self, **kwargs):
        """
        Initializes the RegionTagExtractionAgent.

        This method initializes the `LlmAgent` with a specific model and a
        prompt that instructs the model to extract all the unique region tags
        from a code snippet.
        """
        super().__init__(
            instruction="You are an expert programmer and your task is to extract all the unique region tags from the provided code snippet. Region tags are used to identify and group related code blocks, and they typically appear in comments in the format `[START tag_name]` and `[END tag_name]`. Your task is to identify all such tags and return a comma-separated list of the tag names. For example, if you find `[START vision_quickstart]` and `[END vision_quickstart]`, you should extract `vision_quickstart`. Do not include the `[START ...]` or `[END ...]` brackets in your response. If no region tags are found, return an empty string. The code snippet is: {code_snippet}",
            **kwargs
        )
