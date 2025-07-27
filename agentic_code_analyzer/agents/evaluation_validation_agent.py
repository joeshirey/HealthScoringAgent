import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from agentic_code_analyzer.validation_model import EvaluationValidationOutput


class EvaluationVerificationAgent(LlmAgent):
    """
    Performs the verification step of the validation workflow. It uses Google
    Search to check the claims of the original evaluation and produces a raw
    text analysis.
    """

    def __init__(self, **kwargs):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "evaluation_validation_prompt.md",
        )
        with open(prompt_path, "r") as f:
            instruction = f.read()

        super().__init__(
            instruction=instruction,
            tools=[google_search],
            **kwargs,
        )


class ValidationFormattingAgent(LlmAgent):
    """
    Formats the raw text output from the verification agent into a structured
    JSON object according to the EvaluationValidationOutput schema.
    """

    def __init__(self, **kwargs):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "validation_formatting_prompt.md",
        )
        with open(prompt_path, "r") as f:
            instruction = f.read()

        super().__init__(
            instruction=instruction,
            output_schema=EvaluationValidationOutput,
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True,
            **kwargs,
        )


class ValidationOrchestrator(SequentialAgent):
    """
    Orchestrates the two-step validation workflow.
    """

    def __init__(self, **kwargs):
        verification_agent = EvaluationVerificationAgent(
            name="evaluation_verification_agent",
            output_key="raw_validation_output",
            model=os.environ.get("GEMINI_PRO_MODEL", "gemini-1.5-pro-latest"),
        )
        formatting_agent = ValidationFormattingAgent(
            name="validation_formatting_agent",
            output_key="validation_output",
            model=os.environ.get("GEMINI_FLASH_LITE_MODEL", "gemini-1.5-flash-latest"),
        )

        super().__init__(
            name=kwargs.get("name", "validation_orchestrator"),
            sub_agents=[
                verification_agent,
                formatting_agent,
            ],
        )
