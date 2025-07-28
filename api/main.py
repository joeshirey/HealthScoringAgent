"""
This module defines the FastAPI application that serves as the main entry point
for the Health Scoring Agent. It exposes REST API endpoints for analyzing code,
validating evaluations, and serving a simple web UI.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from agentic_code_analyzer.agents.evaluation_validation_agent import (
    ValidationOrchestrator,
)
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
from agentic_code_analyzer.validation_model import (
    EvaluationValidationOutput,
    FinalValidatedAnalysisWithHistory,
    ValidationAttempt,
)
from config.logging_config import setup_logging

# Load environment variables from .env file and set up logging.
load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Initialize the FastAPI application.
app = FastAPI(
    title="Health Scoring Agent API",
    description="An API for analyzing and evaluating code samples for quality, correctness, and adherence to best practices.",
    version="1.0.0",
)

# --- Pydantic Request Models ---


class CodeRequest(BaseModel):
    """Defines the request body for the /analyze endpoint."""

    code: str
    github_link: Optional[str] = None


class GitHubLinkRequest(BaseModel):
    """Defines the request body for the /analyze_github_link endpoint."""

    github_link: str


class ValidationRequest(BaseModel):
    """Defines the request body for the /validate endpoint."""

    github_link: str
    evaluation: Dict[str, Any]


@app.post(
    "/analyze",
    response_model=FinalValidatedAnalysisWithHistory,
    summary="Analyze a code sample with iterative validation",
    tags=["Analysis"],
)
async def analyze_code(request: CodeRequest) -> FinalValidatedAnalysisWithHistory:
    """
    Analyzes a code sample and validates the analysis.

    This endpoint implements an iterative refinement loop:
    1.  It runs the main `CodeAnalyzerOrchestrator` to get an initial analysis.
    2.  It runs the `ValidationOrchestrator` to score the quality of the analysis.
    3.  If the validation score is below a threshold (default 7/10), it re-runs
        the analysis, providing the validation feedback to the analyzer.
    4.  This loop continues until the validation score is satisfactory or the
        maximum number of attempts is reached.

    Args:
        request: A `CodeRequest` object containing the code to analyze.

    Returns:
        A `FinalValidatedAnalysisWithHistory` object containing the final
        analysis and a history of all validation attempts.
    """
    max_loops = int(os.environ.get("MAX_VALIDATION_LOOPS", 3))
    validation_history: List[ValidationAttempt] = []
    current_analysis_json: Dict[str, Any] = {}
    feedback_for_next_loop = ""
    session_service = InMemorySessionService()
    session_id = "iterative_session"

    for i in range(max_loops):
        logger.info(f"--- Starting Analysis Iteration {i + 1}/{max_loops} ---")

        # --- STAGE 1: Run the main Code Analyzer ---
        analysis_orchestrator = CodeAnalyzerOrchestrator(
            name=f"code_analyzer_orchestrator_iter_{i}"
        )
        initial_state = {
            "code_snippet": request.code,
            "github_link": request.github_link or "",
            "feedback_from_validation": feedback_for_next_loop,
        }
        await session_service.create_session(
            app_name="agentic_code_analyzer",
            user_id="api_user",
            session_id=session_id,
            state=initial_state,
        )
        analysis_runner = Runner(
            agent=analysis_orchestrator,
            app_name="agentic_code_analyzer",
            session_service=session_service,
        )

        final_response = "{}"
        async for event in analysis_runner.run_async(
            user_id="api_user",
            session_id=session_id,
            new_message=types.Content(parts=[types.Part(text=request.code)]),
        ):
            if (
                event.is_final_response()
                and event.content
                and event.content.parts
                and event.content.parts[0].text
            ):
                final_response = event.content.parts[0].text

        try:
            current_analysis_json = json.loads(final_response)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, detail="Failed to parse analysis JSON from the orchestrator."
            )

        # --- STAGE 2: Run the Validation Orchestrator ---
        validation_result = await _run_validation(
            session_service=session_service,
            session_id=session_id,
            code=request.code,
            evaluation=current_analysis_json,
            iteration=i,
        )
        validation_history.append(
            ValidationAttempt(
                validation_score=validation_result.validation_score,
                reasoning=validation_result.reasoning,
            )
        )

        # --- STAGE 3: Check the validation score ---
        if validation_result.validation_score > 7:
            logger.info(
                f"Validation passed with score {validation_result.validation_score}. Exiting loop."
            )
            break  # Exit the loop if the analysis is good enough.
        else:
            logger.warning(
                f"Validation failed with score {validation_result.validation_score}. Preparing for re-evaluation."
            )
            feedback_for_next_loop = validation_result.reasoning
            if i == max_loops - 1:
                logger.warning("Max validation loops reached. Returning final result regardless of score.")

    if not current_analysis_json:
        raise HTTPException(
            status_code=500, detail="Analysis failed to produce any result after all attempts."
        )

    return FinalValidatedAnalysisWithHistory(
        analysis=current_analysis_json,
        validation_history=validation_history,
    )


async def _run_validation(
    session_service: InMemorySessionService,
    session_id: str,
    code: str,
    evaluation: Dict[str, Any],
    iteration: int,
) -> EvaluationValidationOutput:
    """
    A helper function to run the validation workflow.

    This function encapsulates the logic for invoking the `ValidationOrchestrator`
    and processing its output.

    Args:
        session_service: The session service instance.
        session_id: The ID of the current session.
        code: The original code being analyzed.
        evaluation: The analysis JSON produced by the main orchestrator.
        iteration: The current iteration number of the validation loop.

    Returns:
        An `EvaluationValidationOutput` object with the validation score and reasoning.

    Raises:
        HTTPException: If the validation workflow fails to produce a valid result.
    """
    logger.info(f"Starting validation of the evaluation (Iteration {iteration + 1})...")
    validation_orchestrator = ValidationOrchestrator(
        name=f"validation_orchestrator_iter_{iteration}"
    )
    validation_runner = Runner(
        agent=validation_orchestrator,
        app_name="agentic_code_analyzer",
        session_service=session_service,
    )

    # The validation input is a combination of the original code and the analysis.
    validation_input = f"""
Original Code:
```
{code}
```

Original Evaluation JSON:
```json
{json.dumps(evaluation, indent=2)}
```
"""
    logger.info("Starting validation agent workflow...")
    async for _ in validation_runner.run_async(
        user_id="api_user",
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=validation_input)]),
    ):
        pass  # Run the agent to completion.

    logger.info("Validation agent workflow finished.")

    # Retrieve the final session state to get the validation output.
    final_session = await session_service.get_session(
        app_name="agentic_code_analyzer", user_id="api_user", session_id=session_id
    )
    if not final_session:
        raise HTTPException(
            status_code=500, detail="Failed to retrieve session after validation."
        )

    validation_data = final_session.state.get("validation_output")

    # Validate the output against the Pydantic model.
    validation_response_model = None
    if validation_data and isinstance(validation_data, dict):
        try:
            validation_response_model = EvaluationValidationOutput.model_validate(
                validation_data
            )
        except Exception as e:
            logger.error(f"Pydantic validation failed for validation output: {e}", exc_info=True)

    if not validation_response_model:
        logger.error("Evaluation validation agent did not return a valid output.")
        raise HTTPException(
            status_code=500,
            detail="Evaluation validation failed to produce a valid, structured result.",
        )
    return validation_response_model


# This standalone endpoint can be removed or kept depending on use case.
# For now, we will keep it but ensure it uses a unique session_id.
@app.post(
    "/validate",
    response_model=EvaluationValidationOutput,
    summary="Validate an existing evaluation (standalone)",
    tags=["Validation"],
)
async def validate_evaluation(request: ValidationRequest) -> EvaluationValidationOutput:
    """
    Validates an existing evaluation against a code sample from a GitHub link.

    This standalone endpoint is useful for testing the validation workflow
    independently of the main analysis loop.

    Args:
        request: A `ValidationRequest` object containing the GitHub link and
            the evaluation JSON to validate.

    Returns:
        An `EvaluationValidationOutput` object with the validation score and reasoning.
    """
    logger.info(f"Received request to validate evaluation for: {request.github_link}")
    code = await _fetch_code_from_github(request.github_link)

    session_service = InMemorySessionService()
    session_id = "standalone_validation_session"
    await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="api_user",
        session_id=session_id,
        state={"code_snippet": code, "github_link": request.github_link},
    )

    return await _run_validation(
        session_service=session_service,
        session_id=session_id,
        code=code,
        evaluation=request.evaluation,
        iteration=0,
    )


# A set of allowed domains to prevent requests to arbitrary URLs.
ALLOWED_DOMAINS = {"github.com", "raw.githubusercontent.com"}


async def _fetch_code_from_github(github_link: str) -> str:
    """
    Fetches the raw content of a code file from a GitHub link.

    This function converts a standard GitHub file link (e.g., with `/blob/`)
    into its raw content equivalent on `raw.githubusercontent.com`.

    Args:
        github_link: The GitHub URL to the file.

    Returns:
        The raw text content of the file.

    Raises:
        HTTPException: If the domain is not allowed, or if the file cannot be
            fetched.
    """
    try:
        parsed_url = urlparse(github_link)
        if parsed_url.hostname not in ALLOWED_DOMAINS:
            logger.error(f"Invalid GitHub domain: {parsed_url.hostname}")
            raise HTTPException(status_code=400, detail="Invalid or unsupported GitHub domain.")

        # Convert the standard GitHub URL to the raw content URL.
        raw_url = github_link.replace(
            "github.com", "raw.githubusercontent.com"
        ).replace("/blob/", "/")

        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()  # Raise an exception for bad status codes.
            code = response.text
        logger.info(f"Successfully fetched code from {raw_url}")
        return code
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching code from GitHub: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Error fetching code from GitHub: {e.response.text}"
        )


@app.post(
    "/analyze_github_link",
    response_model=FinalValidatedAnalysisWithHistory,
    summary="Analyze a code sample from a GitHub link",
    tags=["Analysis"],
)
async def analyze_github_link(
    request: GitHubLinkRequest,
) -> FinalValidatedAnalysisWithHistory:
    """
    Fetches a code sample from a GitHub link and then analyzes it.

    This is a convenience endpoint that first fetches the code from the given
    URL and then passes it to the main `/analyze` endpoint for processing.

    Args:
        request: A `GitHubLinkRequest` object containing the URL.

    Returns:
        The result of the analysis, same as the `/analyze` endpoint.
    """
    logger.info(f"Received request to analyze GitHub link: {request.github_link}")
    code = await _fetch_code_from_github(request.github_link)
    return await analyze_code(CodeRequest(code=code, github_link=request.github_link))


app.mount("/", StaticFiles(directory="api/ui", html=True), name="ui")
