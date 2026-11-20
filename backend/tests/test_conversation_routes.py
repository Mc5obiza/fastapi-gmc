from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.app.routers.conversation import router
from backend.app.services.db.database import get_db


app = FastAPI()
app.include_router(router)
app.dependency_overrides[get_db] = lambda: None


async def request(path):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


@pytest.mark.asyncio
async def test_get_all_conversations_returns_owned_conversation_summaries():
    conversations = [
        SimpleNamespace(
            id=5,
            title="Study session",
            created_at=datetime(2026, 11, 20, 10, 0),
            updated_at=datetime(2026, 11, 20, 10, 30),
        )
    ]
    with patch(
        "backend.app.routers.conversation.crud.get_all_cnv",
        return_value=conversations,
    ) as get_all:
        response = await request("/conversations/")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5,
            "title": "Study session",
            "created_at": "2026-11-20T10:00:00",
            "updated_at": "2026-11-20T10:30:00",
        }
    ]
    get_all.assert_called_once_with(None, 1)


@pytest.mark.asyncio
async def test_get_conversation_messages_returns_messages_for_owned_conversation():
    messages = [{"role": "user", "content": "Hello"}]
    with (
        patch(
            "backend.app.routers.conversation.crud.get_conversation",
            return_value=SimpleNamespace(id=7),
        ) as get_conversation,
        patch(
            "backend.app.routers.conversation.crud.get_messages",
            return_value=messages,
        ) as get_messages,
    ):
        response = await request("/conversations/7/messages")

    assert response.status_code == 200
    assert response.json() == messages
    get_conversation.assert_called_once_with(None, 7, 1)
    get_messages.assert_called_once_with(None, 7, 1)


@pytest.mark.asyncio
async def test_get_conversation_messages_returns_404_for_unowned_conversation():
    with (
        patch(
            "backend.app.routers.conversation.crud.get_conversation",
            return_value=None,
        ) as get_conversation,
        patch("backend.app.routers.conversation.crud.get_messages") as get_messages,
    ):
        response = await request("/conversations/7/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Conversation not found"
    get_conversation.assert_called_once_with(None, 7, 1)
    get_messages.assert_not_called()
