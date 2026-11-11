from .models import SummarizeResponse
from openai import OpenAI,AuthenticationError,RateLimitError
from .ai import AIServiceError,get_client


def generate_summarize(text,max_bullets):
    try:
        user_prompt = f"""
            You are a professional summarizer.
            Summarize the given text between ````into bullet points.
            ``
            {text}
            ``
            Generate a maximum of {max_bullets} bullet points in the summary list.
            Make it clear, concise, and factually accurate."""
        client = get_client()
        response = client.beta.chat.completions.parse(
            model ="openrouter/free",
            messages = [{
                "role":"user",
                "content":user_prompt
            }],
            max_tokens = 3000,
            temperature = 0.3,
            response_format = SummarizeResponse
        )
    except AuthenticationError as ae:
        raise AIServiceError(kind = "auth",message = "Invalid Authentification")
    except RateLimitError as re:
        raise AIServiceError(kind = "rate_limit",message = "Too many Request Please try later")
    except Exception:
        raise AIServiceError(kind = "unkown",message = "Unexpected Error Please try agin!!!")
    event = response.choices[0].message.parsed
    return event
if __name__ == "__main__":
    text = """
    A volcano is an opening in the Earth's crust that allows hot magma, volcanic ash, and gases to escape from a magma chamber below the surface.
Most volcanoes form along the boundaries of shifting tectonic plates, though some develop over hot spots in the middle of plates.
When pressure from gases and rising molten rock builds up deep underground, it forces its way through the crust and triggers an eruption.
Once the molten rock reaches the surface, it is called lava, which cools and hardens over time to build the volcano's cone-shaped mountain structure.
Scientists classify volcanoes as active, dormant, or extinct depending on their eruption history and the likelihood that they will erupt again in the future.
    """
    print(len(text))
    print(type(generate_summarize(text,3)))