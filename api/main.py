import json
import logging
import re
import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Optional, Union, Dict, Any
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
from agentic_code_analyzer.agents.evaluation_validation_agent import (
    ValidationOrchestrator,
)
from agentic_code_analyzer.validation_model import (
    EvaluationValidationOutput,
    ValidationAttempt,
    FinalValidatedAnalysisWithHistory,
)
from agentic_code_analyzer.models import EvaluationOutput
from config.logging_config import setup_logging
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
setup_logging()

# Get a logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Health Scoring Agent API",
    description="An API for analyzing and evaluating code samples for quality, correctness, and adherence to best practices.",
    version="1.0.0",
)


def remove_comments(code: str, language: str) -> str:
    """
    Removes comments from a code string based on the language.

    This function takes a code string and a language as input, and returns the code
    string with all comments removed. It supports a wide range of popular
    programming languages, including Python, JavaScript, Java, C++, and more.

    Args:
        code: The code string to remove comments from.
        language: The programming language of the code string.

    Returns:
        The code string with all comments removed.
    """
    if language.lower() in ["python", "shell", "ruby"]:
        # Removes single-line comments starting with #
        return re.sub(r"#.*", "", code)
    elif language.lower() in [
        "javascript",
        "java",
        "c",
        "c++",
        "c#",
        "go",
        "swift",
        "typescript",
        "kotlin",
        "rust",
        "php",
        "terraform",
    ]:
        # Removes single-line // comments and multi-line /* ... */ comments
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        return code
    elif language.lower() in ["html", "xml"]:
        # Removes <!-- ... --> comments
        return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
    else:
        # Return original code if language is not supported
        return code


class CodeRequest(BaseModel):
    """
    A request to analyze a code sample.
    """

    code: str
    github_link: Optional[str] = None


class GitHubLinkRequest(BaseModel):
    """
    A request to analyze a code sample from a GitHub link.
    """

    github_link: str


@app.post(
    "/analyze",
    response_model=FinalValidatedAnalysisWithHistory,
    summary="Analyze a code sample",
)
async def analyze_code(request: CodeRequest):
    """
    Analyzes a code sample, validates the analysis, and iteratively
    re-evaluates if the validation score is below a threshold.
    """
    max_loops = int(os.environ.get("MAX_VALIDATION_LOOPS", 3))
    validation_history = []
    current_analysis_json = {}
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
            raise HTTPException(status_code=500, detail="Failed to parse analysis JSON.")

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

        # --- STAGE 3: Check the condition ---
        if validation_result.validation_score > 7:
            logger.info(
                f"Validation passed with score {validation_result.validation_score}. Exiting loop."
            )
            break
        else:
            logger.warning(
                f"Validation failed with score {validation_result.validation_score}. Preparing for re-evaluation."
            )
            feedback_for_next_loop = validation_result.reasoning
            if i == max_loops - 1:
                logger.warning("Max validation loops reached. Returning final result.")

    if not current_analysis_json:
        raise HTTPException(
            status_code=500, detail="Analysis failed to produce any result."
        )

    return FinalValidatedAnalysisWithHistory(
        analysis=EvaluationOutput.model_validate(current_analysis_json),
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
    Runs the validation workflow on a given code sample and its evaluation.
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
        pass  # Run to completion

    logger.info("Validation agent workflow finished.")

    final_session = await session_service.get_session(
        app_name="agentic_code_analyzer", user_id="api_user", session_id=session_id
    )
    validation_data = final_session.state.get("validation_output")

    validation_response_model = None
    if validation_data and isinstance(validation_data, dict):
        try:
            validation_response_model = EvaluationValidationOutput.model_validate(
                validation_data
            )
        except Exception as e:
            logger.error(f"Pydantic validation failed for validation output: {e}")

    if not validation_response_model:
        logger.error("Evaluation validation agent did not return a valid output.")
        raise HTTPException(
            status_code=500,
            detail="Evaluation validation failed to produce a result.",
        )
    return validation_response_model


# This standalone endpoint can be removed or kept depending on use case.
# For now, we will keep it but ensure it uses a unique session_id.
@app.post(
    "/validate",
    response_model=EvaluationValidationOutput,
    summary="Validate an existing evaluation",
)
async def validate_evaluation(request: ValidationRequest):
    """
    Validates an existing evaluation against the source code from a GitHub link.
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

    validation_result = await _run_validation(
        session_service=session_service,
        session_id=session_id,
        code=code,
        evaluation=request.evaluation,
        iteration=0,
    )
    return validation_result


async def _fetch_code_from_github(github_link: str) -> str:
    """
    Fetches code from a GitHub link.
    """
    try:
        parsed_url = urlparse(github_link)
        if parsed_url.hostname not in ALLOWED_DOMAINS:
            logger.error(f"Invalid GitHub domain: {parsed_url.hostname}")
            raise HTTPException(status_code=400, detail="Invalid GitHub domain.")

        raw_url = github_link.replace(
            "github.com", "raw.githubusercontent.com"
        ).replace("/blob/", "/")
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            code = response.text
        logger.info(f"Successfully fetched code from {raw_url}")
        return code
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching code from GitHub: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error fetching code from GitHub: {e}"
        )


ALLOWED_DOMAINS = {"github.com", "raw.githubusercontent.com"}


@app.post(
    "/analyze_github_link",
    response_model=FinalValidatedAnalysisWithHistory,
    summary="Analyze a code sample from a GitHub link",
)
async def analyze_github_link(request: GitHubLinkRequest):
    """
    Analyzes a code sample from a GitHub link and returns a detailed analysis of its health.
    """
    logger.info(f"Received request to analyze GitHub link: {request.github_link}")
    code = await _fetch_code_from_github(request.github_link)
    return await analyze_code(CodeRequest(code=code, github_link=request.github_link))


app.mount("/", StaticFiles(directory="api/ui", html=True), name="ui")
