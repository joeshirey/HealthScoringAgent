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
        with open("agentic_code_analyzer/prompts/region_tag_extraction.md", "r") as f:
            instruction = f.read()
        super().__init__(
            instruction=instruction,
            **kwargs
        )
