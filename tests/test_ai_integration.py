import os

import pytest

from app.services.ai import call_llm


def supervise_answer(question, expected_answer, candidate_answer):
    prompt = f"""
    Independently check the candidate answer to the academic question below.
    Compare it with the expected answer and allow equivalent wording.
    Reply with exactly CORRECT or INCORRECT, with no explanation.

    Question: {question}
    Expected answer: {expected_answer}
    Candidate answer: {candidate_answer}
    """
    return call_llm(prompt)["answer"].strip().upper()


@pytest.mark.ai_integration
@pytest.mark.skipif(
    os.getenv("RUN_AI_INTEGRATION_TESTS") != "1",
    reason="Set RUN_AI_INTEGRATION_TESTS=1 to enable live AI integration tests.",
)
def test_ai_answer_is_checked_by_live_supervisor():
    question = "What is 17 multiplied by 19? Give the answer."
    candidate_answer = call_llm(question)["answer"]
    assert candidate_answer.strip(), "The AI returned an empty answer."

    verdict = supervise_answer(
        question=question,
        expected_answer="323",
        candidate_answer=candidate_answer,
    )

    assert verdict == "CORRECT", (
        f"The supervisor judged the candidate answer incorrect. "
        f"Candidate: {candidate_answer!r}; verdict: {verdict!r}"
    )
