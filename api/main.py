import json
import logging
import re
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
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


@app.post("/analyze", summary="Analyze a code sample")
async def analyze_code(request: CodeRequest):
    """
    Analyzes a code sample and returns a detailed analysis of its health.
    """
    logger.info(
        f"Received request to analyze code snippet. Link provided: {bool(request.github_link)}"
    )
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="agentic_code_analyzer",
        user_id="api_user",
        session_id="api_session",
        state={
            "code_snippet": request.code,
            "github_link": request.github_link or "",
        },
    )
    runner = Runner(
        agent=CodeAnalyzerOrchestrator(name="code_analyzer_orchestrator"),
        app_name="agentic_code_analyzer",
        session_service=session_service,
    )

    final_response = "{}"
    logger.info("Starting agent workflow...")
    async for event in runner.run_async(
        user_id="api_user",
        session_id="api_session",
        new_message=types.Content(parts=[types.Part(text=request.code)]),
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text

    logger.info("Agent workflow finished.")

    try:
        return json.loads(final_response)
    except json.JSONDecodeError:
        logger.error("Failed to parse final response from agent as JSON.")
        raise HTTPException(
            status_code=500, detail="Failed to parse agent's final response as JSON."
        )


ALLOWED_DOMAINS = {"github.com", "raw.githubusercontent.com"}


@app.post("/analyze_github_link", summary="Analyze a code sample from a GitHub link")
async def analyze_github_link(request: GitHubLinkRequest):
    """
    Analyzes a code sample from a GitHub link and returns a detailed analysis of its health.
    """
    logger.info(f"Received request to analyze GitHub link: {request.github_link}")
    try:
        parsed_url = urlparse(request.github_link)
        if parsed_url.hostname not in ALLOWED_DOMAINS:
            logger.error(f"Invalid GitHub domain: {parsed_url.hostname}")
            raise HTTPException(status_code=400, detail="Invalid GitHub domain.")

        raw_url = request.github_link.replace(
            "github.com", "raw.githubusercontent.com"
        ).replace("/blob/", "/")
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            code = response.text
        logger.info(f"Successfully fetched code from {raw_url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching code from GitHub: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error fetching code from GitHub: {e}"
        )

    return await analyze_code(CodeRequest(code=code, github_link=request.github_link))


app.mount("/", StaticFiles(directory="api/ui", html=True), name="ui")
