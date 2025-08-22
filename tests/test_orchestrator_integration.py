import pytest
import json

from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator
from agentic_code_analyzer.models import AnalysisResult


@pytest.fixture
def mock_llm_agents(mocker):
    """Mocks the agents that interact with LLMs."""
    mock_code_cleaning = mocker.patch(
        "agentic_code_analyzer.orchestrator.CodeCleaningAgent", autospec=True
    )
    mock_initial_analysis = mocker.patch(
        "agentic_code_analyzer.orchestrator.InitialAnalysisAgent", autospec=True
    )
    mock_json_formatting = mocker.patch(
        "agentic_code_analyzer.orchestrator.JsonFormattingAgent", autospec=True
    )
    mock_product_categorization = mocker.patch(
        "agentic_code_analyzer.orchestrator.ProductCategorizationAgent", autospec=True
    )
    mock_code_cleaning.return_value.parent_agent = None
    mock_initial_analysis.return_value.parent_agent = None
    mock_json_formatting.return_value.parent_agent = None
    mock_product_categorization.return_value.parent_agent = None
    return (
        mock_code_cleaning,
        mock_initial_analysis,
        mock_json_formatting,
        mock_product_categorization,
    )


@pytest.mark.asyncio
async def test_orchestrator_no_region_tags(mock_llm_agents):
    """
    Tests that the orchestrator halts and returns an error when no region tags are found.
    """
    orchestrator = CodeAnalyzerOrchestrator(name="test_orchestrator")
    session_service = InMemorySessionService()

    code_snippet = "import os"

    initial_state = {
        "code_snippet": code_snippet,
        "github_link": "http://mock.link",
    }

    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state=initial_state,
    )

    runner = Runner(
        agent=orchestrator,
        app_name="test_app",
        session_service=session_service,
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session",
        new_message=Content(parts=[Part(text=code_snippet)]),
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text

    assert final_response, "Final response should not be empty"
    final_data = json.loads(final_response)
    assert final_data == {"error": "No Region Tags"}


@pytest.mark.asyncio
async def test_orchestrator_unsupported_language(mock_llm_agents, mocker):
    """
    Tests that the orchestrator halts and returns an error for an unsupported language.
    """
    mock_run_async = mocker.patch(
        "agentic_code_analyzer.orchestrator.DeterministicLanguageDetectionAgent.run_async"
    )

    async def mock_side_effect(*args, **kwargs):
        if False:
            yield

    mock_run_async.side_effect = mock_side_effect
    orchestrator = CodeAnalyzerOrchestrator(name="test_orchestrator")
    session_service = InMemorySessionService()

    code_snippet = "# [START some_tag]\nimport os# [END some_tag]"

    initial_state = {
        "code_snippet": code_snippet,
        "github_link": "http://mock.link",
    }

    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session",
        state=initial_state,
    )

    # Manually set the language to an unsupported one
    session = await session_service.get_session(
        app_name="test_app", user_id="test_user", session_id="test_session"
    )
    session.state["language_detection_agent_output"] = "Cobol"
    await session_service.create_session(
        app_name="test_app",
        user_id="test_user",
        session_id="test_session_unsupported_language",
        state=session.state,
    )

    runner = Runner(
        agent=orchestrator,
        app_name="test_app",
        session_service=session_service,
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="test_user",
        session_id="test_session_unsupported_language",
        new_message=Content(parts=[Part(text=code_snippet)]),
    ):
        if (
            event.is_final_response()
            and event.content
            and event.content.parts
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text

    assert final_response, "Final response should not be empty"
    final_data = json.loads(final_response)
    assert final_data == {"error": "Unsupported Language"}
