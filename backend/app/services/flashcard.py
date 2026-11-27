from openai import OpenAI,AuthenticationError,RateLimitError
from .ai import AIServiceError,get_client
from backend.app.routers.models import FlashCardsResponse
import asyncio
async def _generate_flashcard(topics,number_flashcards):
    try:
        client = get_client()
        SYSTEM_PROMPT = f"""
        You are a flashcard generator.
        Generate educational flashcards with a front (question/prompt) and a back (answer/explanation).
        Generate exactly {number_flashcards} flashcards about the requested topic.
        Make them clear, concise, and factually accurate."""
        user_message = f"Generate {number_flashcards} FlashCards about {topics}"
        response = await client.beta.chat.completions.parse(
            model = "openrouter/free",
            messages=[{
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":user_message
            }],
            response_format=FlashCardsResponse
        )
    except AuthenticationError as error:
        raise AIServiceError("auth","Invalid API key")
    except RateLimitError as error:
        raise AIServiceError("rate_limit","Rate limited by the provider")
    except Exception as e:
        raise AIServiceError("Unkown",str(e))
    event = response.choices[0].message.parsed
    return event
async def generate_flashcard(topics,numb):
    try:
        return await asyncio.wait_for(_generate_flashcard(topics,numb),timeout=20)
    except asyncio.TimeoutError:
        raise AIServiceError(kind="timeout",message="Time out")
if __name__ == "__main__":
    print(generate_flashcard("math","4"))
