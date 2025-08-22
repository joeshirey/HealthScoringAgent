import pytest
from agentic_code_analyzer.orchestrator import CodeAnalyzerOrchestrator


def test_code_analyzer_orchestrator_initialization():
    """
    Tests that the CodeAnalyzerOrchestrator can be initialized without errors.
    """
    try:
        orchestrator = CodeAnalyzerOrchestrator(name="test_orchestrator")
        assert orchestrator is not None
        assert orchestrator.name == "test_orchestrator"
        assert len(orchestrator.sub_agents) == 5
    except Exception as e:
        pytest.fail(f"CodeAnalyzerOrchestrator initialization failed: {e}")
