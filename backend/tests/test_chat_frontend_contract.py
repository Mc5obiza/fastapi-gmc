from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.app.routers.chat import router
from backend.app.services.db.database import get_db


app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_db] = lambda: None


@pytest.mark.asyncio
async def test_chat_response_includes_conversation_id_for_follow_up_messages():
    with (
        patch(
            "backend.app.routers.chat.add_message",
            side_effect=[(1, 42), (2, 42)],
        ),
        patch(
            "backend.app.routers.chat.call_llm",
            return_value={
                "answer": "The answer",
                "model": "test-model",
                "tokens_used": 5,
            },
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/chat/", json={"message": "Hello"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "The answer",
        "model": "test-model",
        "tokens_used": 5,
        "conversation_id": 42,
    }
