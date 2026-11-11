from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from backend.app.services import ai
from backend.app.services.ai import AIServiceError
from backend.app.services.models import FlashCardsResponse, QuizzResponse, SummarizeResponse
from backend.app.services import flashcard, quizz, summarize


def parsed_client(parsed):
    client = Mock()
    client.beta.chat.completions.parse.return_value.choices = [
        SimpleNamespace(message=SimpleNamespace(parsed=parsed))
    ]
    return client


@patch("app.services.ai.OpenAI")
def test_get_client_requires_api_key(openai):
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(AIServiceError) as error:
            ai.get_client()

    assert error.value.kind == "api_key"
    openai.assert_not_called()


@patch("app.services.ai.OpenAI")
def test_get_client_uses_openrouter_configuration(openai):
    openai.return_value = object()

    with patch.dict("os.environ", {"OPEN_ROUTER_KEY": "test-key"}):
        client = ai.get_client()

    assert client is openai.return_value
    openai.assert_called_once_with(
        api_key="test-key", base_url="https://openrouter.ai/api/v1"
    )


def test_call_llm_builds_request_and_handles_optional_values():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None))],
        usage=None,
        model=None,
    )
    client = Mock()
    client.chat.completions.create.return_value = response
    with patch("app.services.ai.get_client", return_value=client):
        result = ai.call_llm("Explain algebra")

    assert result == {"answer": "", "model": "No model", "tokens_used": 0}
    call = client.chat.completions.create.call_args.kwargs
    assert call["model"] == "openrouter/free"
    assert call["messages"][-1] == {
        "role": "user",
        "content": "Explain algebra",
    }


def test_call_llm_returns_answer_and_token_count():
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Answer"))],
        usage=SimpleNamespace(total_tokens=23),
        model="provider-model",
    )
    client = Mock()
    client.chat.completions.create.return_value = response
    with patch("app.services.ai.get_client", return_value=client):
        result = ai.call_llm("Question")

    assert result == {
        "answer": "Answer",
        "model": "provider-model",
        "tokens_used": 23,
    }


@pytest.mark.parametrize(
    ("module", "invoke", "response_type", "prompt_fragment"),
    [
        (
            flashcard,
            lambda: flashcard.generate_flashcard("math", 7),
            FlashCardsResponse,
            "7",
        ),
        (
            quizz,
            lambda: quizz.generate_quizz("math", 3, 4),
            QuizzResponse,
            "3",
        ),
        (
            summarize,
            lambda: summarize.generate_summarize("A long enough text", 3),
            SummarizeResponse,
            "A long enough text",
        ),
    ],
)
def test_structured_services_return_parsed_response(
    module, invoke, response_type, prompt_fragment
):
    parsed = object()
    client = parsed_client(parsed)
    with patch.object(module, "get_client", return_value=client):
        result = invoke()

    assert result is parsed
    call = client.beta.chat.completions.parse.call_args.kwargs
    assert call["model"] == "openrouter/free"
    assert call["response_format"] is response_type
    assert prompt_fragment in " ".join(
        message["content"] for message in call["messages"]
    )


@pytest.mark.parametrize(
    ("module", "invoke", "error_name", "expected_kind", "expected_message"),
    [
        (
            ai,
            lambda: ai.call_llm("math"),
            "AuthenticationError",
            "auth",
            "Invalid API key",
        ),
        (
            ai,
            lambda: ai.call_llm("math"),
            "RateLimitError",
            "rate_limit",
            "Rate limited by the provider",
        ),
        (
            flashcard,
            lambda: flashcard.generate_flashcard("math", 7),
            "AuthenticationError",
            "auth",
            "Invalid API key",
        ),
        (
            flashcard,
            lambda: flashcard.generate_flashcard("math", 7),
            "RateLimitError",
            "rate_limit",
            "Rate limited by the provider",
        ),
        (
            quizz,
            lambda: quizz.generate_quizz("math", 3, 4),
            "AuthenticationError",
            "auth",
            "Invalid API key",
        ),
        (
            quizz,
            lambda: quizz.generate_quizz("math", 3, 4),
            "RateLimitError",
            "rate_limit",
            "Rate limited by the provider",
        ),
        (
            summarize,
            lambda: summarize.generate_summarize("A long enough text", 3),
            "AuthenticationError",
            "auth",
            "Invalid Authentification",
        ),
        (
            summarize,
            lambda: summarize.generate_summarize("A long enough text", 3),
            "RateLimitError",
            "rate_limit",
            "Too many Request Please try later",
        ),
    ],
)
def test_services_translate_authentication_and_rate_limit_errors(
    module, invoke, error_name, expected_kind, expected_message, monkeypatch
):
    class FakeProviderError(Exception):
        pass

    client = Mock()
    if module is ai:
        client.chat.completions.create.side_effect = FakeProviderError("provider error")
    else:
        client.beta.chat.completions.parse.side_effect = FakeProviderError(
            "provider error"
        )
    monkeypatch.setattr(module, error_name, FakeProviderError)
    with patch.object(module, "get_client", return_value=client):
        with pytest.raises(AIServiceError) as error:
            invoke()

    assert error.value.kind == expected_kind
    assert error.value.message == expected_message


@pytest.mark.parametrize(
    ("module", "invoke", "expected_kind", "expected_message"),
    [
        (
            flashcard,
            lambda: flashcard.generate_flashcard("math", 7),
            "Unkown",
            "provider unavailable",
        ),
        (
            quizz,
            lambda: quizz.generate_quizz("math", 3, 4),
            "Unkown",
            "provider unavailable",
        ),
        (
            summarize,
            lambda: summarize.generate_summarize("A long enough text", 3),
            "unkown",
            "Unexpected Error Please try agin!!!",
        ),
    ],
)
def test_structured_services_translate_unexpected_errors(
    module, invoke, expected_kind, expected_message
):
    client = Mock()
    client.beta.chat.completions.parse.side_effect = RuntimeError(
        "provider unavailable"
    )
    with patch.object(module, "get_client", return_value=client):
        with pytest.raises(AIServiceError) as error:
            invoke()

    assert error.value.kind == expected_kind
    assert error.value.message == expected_message


def test_chat_service_translates_unexpected_errors():
    client = Mock()
    client.chat.completions.create.side_effect = RuntimeError("provider unavailable")
    with patch("app.services.ai.get_client", return_value=client):
        with pytest.raises(AIServiceError) as error:
            ai.call_llm("Question")

    assert error.value.kind == "Unkown"
    assert error.value.message == "provider unavailable"
