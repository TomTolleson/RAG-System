import pytest
from unittest.mock import Mock


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")


def test_llm_handler_initializes_and_prompt(mocker):
    mock_llm = Mock()
    mocker.patch('src.llm.llm_handler.ChatOpenAI', return_value=mock_llm)

    from src.llm.llm_handler import LLMHandler

    handler = LLMHandler()
    assert handler.get_llm() is mock_llm

    prompt = handler.get_rag_prompt()
    rendered = prompt.format(context="ctx", question="q?")
    assert "ctx" in rendered
    assert "q?" in rendered

