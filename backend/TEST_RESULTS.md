# Test Results

## Final run

- **Command:** `pytest -q`
- **Result:** 87 passed, 1 skipped
- **Runtime:** 1.37 seconds
- **Environment:** Conda `gmc-backend`

The requested `gmcAI-fastapi` Conda environment was not present on the machine. The test run used `gmc-backend` after approval.

## Coverage added

- Request and response model validation, including minimum, maximum, and invalid input boundaries.
- Root, about, and health endpoints.
- Chat, quiz, summarize, and flashcard routes: request forwarding, response shape, invalid requests, and AI error-to-HTTP mapping.
- AI client configuration, missing API key behavior, provider request construction, parsed responses, and authentication, rate-limit, and unexpected error handling.
- Live answer verification with a separate AI supervisor is available as an opt-in integration test.

Unit tests mock AI provider interactions and do not require live API calls. The optional supervisor integration test in [tests/test_ai_integration.py](./tests/test_ai_integration.py) makes two real API calls and is skipped by default. To run it in PowerShell after activating the Conda environment, use:

```powershell
$env:RUN_AI_INTEGRATION_TESTS = "1"
pytest -q tests/test_ai_integration.py
```

The integration test requires `OPEN_ROUTER_KEY` and can incur provider costs.
It was skipped during the recorded run; no live AI answer was evaluated.

## Issues corrected

- `AIServiceError` now stores its message, allowing service errors to be translated into HTTP responses.
- Pytest now discovers `tests/test1.py`.
- The existing divide-by-zero test now uses a zero divisor.

## Test files

- [tests/test_models.py](./tests/test_models.py)
- [tests/test_routes.py](./tests/test_routes.py)
- [tests/test_ai_services.py](./tests/test_ai_services.py)
- [tests/test_errors.py](./tests/test_errors.py)
- [tests/test1.py](./tests/test1.py)
- [tests/test_health.py](./tests/test_health.py)
