import pytest
from fastapi import HTTPException

from app.services.ai import AIServiceError
from app.services.errors import ai_error_http


@pytest.mark.parametrize(
    ("kind", "status_code", "detail"),
    [
        ("rate_limit", 429, "Try later"),
        ("auth", 500, "Invalid key"),
        ("provider", 500, "The AI Service failed. Please try again :3"),
    ],
)
def test_ai_error_http_mapping(kind, status_code, detail):
    error = AIServiceError(kind, "Try later" if kind == "rate_limit" else "Invalid key")

    response = ai_error_http(error)

    assert isinstance(response, HTTPException)
    assert response.status_code == status_code
    assert response.detail == detail
