import pytest
from unittest.mock import MagicMock
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import Session, BaseSessionService
from agentic_code_analyzer.agents.validation_agent import ValidationAgent
import json


@pytest.mark.asyncio
async def test_validation_agent_no_region_tags():
    """
    Tests that the validation agent correctly identifies when there are no region tags.
    """
    agent = ValidationAgent(name="test_validation_agent")
    session_service = MagicMock(spec=BaseSessionService)
    ctx = InvocationContext(
        invocation_id="test_invocation",
        agent=agent,
        session=Session(
            id="test_session",
            app_name="test_app",
            user_id="test_user",
            state={
                "region_tag_extraction_agent_output": "",
                "language_detection_agent_output": "Python",
            },
        ),
        session_service=session_service,
    )

    events = [event async for event in agent._run_async_impl(ctx)]
    assert len(events) == 1
    assert events[0].turn_complete
    assert json.loads(events[0].content.parts[0].text) == {"error": "No Region Tags"}


@pytest.mark.asyncio
async def test_validation_agent_unsupported_language():
    """
    Tests that the validation agent correctly identifies an unsupported language.
    """
    agent = ValidationAgent(name="test_validation_agent")
    session_service = MagicMock(spec=BaseSessionService)
    ctx = InvocationContext(
        invocation_id="test_invocation",
        agent=agent,
        session=Session(
            id="test_session",
            app_name="test_app",
            user_id="test_user",
            state={
                "region_tag_extraction_agent_output": "some_tag",
                "language_detection_agent_output": "Cobol",
            },
        ),
        session_service=session_service,
    )

    events = [event async for event in agent._run_async_impl(ctx)]
    assert len(events) == 1
    assert events[0].turn_complete
    assert json.loads(events[0].content.parts[0].text) == {
        "error": "Unsupported language"
    }


@pytest.mark.asyncio
async def test_validation_agent_success():
    """
    Tests that the validation agent correctly handles a successful validation.
    """
    agent = ValidationAgent(name="test_validation_agent")
    session_service = MagicMock(spec=BaseSessionService)
    ctx = InvocationContext(
        invocation_id="test_invocation",
        agent=agent,
        session=Session(
            id="test_session",
            app_name="test_app",
            user_id="test_user",
            state={
                "region_tag_extraction_agent_output": "some_tag",
                "language_detection_agent_output": "Python",
            },
        ),
        session_service=session_service,
    )

    events = [event async for event in agent._run_async_impl(ctx)]
    assert len(events) == 0
