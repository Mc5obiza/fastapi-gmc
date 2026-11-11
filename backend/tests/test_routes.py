from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.services.ai import AIServiceError
from backend.app.services.models import (
    FlashCard,
    FlashCardsResponse,
    Quizz,
    QuizzResponse,
    SummarizeResponse,
)


async def request(method, path, **kwargs):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await getattr(client, method)(path, **kwargs)


@pytest.mark.asyncio
async def test_public_information_endpoints():
    root = await request("get", "/")
    about = await request("get", "/about")
    health = await request("get", "/health")

    assert root.status_code == 200
    assert root.json()["status"] == "ok"
    assert about.status_code == 200
    assert about.json()["Title"] == "AI Student assistant"
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["version"] == "0.2.0"
    assert health.json()["timestamp"]


@pytest.mark.asyncio
async def test_chat_strips_message_and_returns_response():
    result = {"answer": "The answer", "model": "test-model", "tokens_used": 5}
    with patch("app.routers.chat.call_llm", return_value=result) as call_llm:
        response = await request("post", "/chat/", json={"message": "  explain math  "})

    assert response.status_code == 200
    assert response.json() == result
    call_llm.assert_called_once_with("explain math")


@pytest.mark.asyncio
async def test_chat_rejects_whitespace_message_without_calling_provider():
    with patch("app.routers.chat.call_llm") as call_llm:
        response = await request("post", "/chat/", json={"message": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Message can not be empty"
    call_llm.assert_not_called()


@pytest.mark.asyncio
async def test_quiz_route_trims_subject_and_forwards_options():
    result = QuizzResponse(
        topic="math",
        nb_questions=3,
        quizz=[
            Quizz(question="Q", options=["A", "B"], correct="A")
        ],
    )
    with patch("app.routers.quizz.generate_quizz", return_value=result) as generate:
        response = await request(
            "post",
            "/quizz/",
            json={"subject": " math ", "number_quizzes": 3, "number_options": 4},
        )

    assert response.status_code == 200
    assert response.json()["topic"] == "math"
    generate.assert_called_once_with("math", 3, 4)


@pytest.mark.asyncio
async def test_summarize_route_trims_text_and_forwards_bullet_limit():
    result = SummarizeResponse(summary=["Point"], word_count=1)
    with patch(
        "app.routers.summarize.generate_summarize", return_value=result
    ) as generate:
        response = await request(
            "post",
            "/summarize/",
            json={"text": "  " + "Useful text " * 2 + "  ", "max_bullets": 4},
        )

    assert response.status_code == 200
    assert response.json() == {"summary": ["Point"], "word_count": 1}
    generate.assert_called_once_with("Useful text Useful text", 4)


@pytest.mark.asyncio
async def test_flashcard_route_returns_generated_cards():
    result = FlashCardsResponse(
        topic="math",
        flashcards=[FlashCard(front="What is 1 + 1?", back="2")],
    )
    with patch(
        "app.routers.flashcard.generate_flashcard", return_value=result
    ) as generate:
        response = await request(
            "post",
            "/flashcard/",
            json={"topic": "math", "number_flashcards": 7},
        )

    assert response.status_code == 200
    assert response.json()["flashcards"][0]["back"] == "2"
    generate.assert_called_once_with("math", 7)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "patch_target", "payload"),
    [
        ("/chat/", "app.routers.chat.call_llm", {"message": "Explain math"}),
        (
            "/quizz/",
            "app.routers.quizz.generate_quizz",
            {"subject": "math", "number_quizzes": 3, "number_options": 4},
        ),
        (
            "/summarize/",
            "app.routers.summarize.generate_summarize",
            {"text": "This text is long enough to summarize.", "max_bullets": 3},
        ),
        (
            "/flashcard/",
            "app.routers.flashcard.generate_flashcard",
            {"topic": "math", "number_flashcards": 7},
        ),
    ],
)
@pytest.mark.parametrize(
    ("kind", "status_code"), [("rate_limit", 429), ("auth", 500)]
)
async def test_ai_errors_are_translated_for_every_ai_route(
    path, patch_target, payload, kind, status_code
):
    with patch(patch_target, side_effect=AIServiceError(kind, "provider error")):
        response = await request("post", path, json=payload)

    assert response.status_code == status_code
    assert response.json()["detail"] == "provider error"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/chat/", {"message": ""}),
        ("/chat/", {"message": "x" * 2001}),
        ("/quizz/", {"subject": "x"}),
        ("/quizz/", {"subject": "math", "number_quizzes": 2}),
        ("/quizz/", {"subject": "math", "number_options": 7}),
        ("/summarize/", {"text": "too short"}),
        ("/summarize/", {"text": "x" * 20, "max_bullets": 11}),
        ("/flashcard/", {"topic": "xy"}),
        ("/flashcard/", {"topic": "math", "number_flashcards": 19}),
    ],
)
async def test_routes_reject_invalid_request_bodies(path, payload):
    response = await request("post", path, json=payload)

    assert response.status_code == 422
