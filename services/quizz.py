from dotenv import load_dotenv
from openai import OpenAI,AuthenticationError,RateLimitError
from ai import AIServiceError,get_client
from models import QuizzResponse

def generate_quizz(subject,number_quizzes,number_options):
    try:
        client = get_client()
        SYSTEM_PROMPT = f"""
        You are a quiz generator.
Generate multiple-choice quiz questions.fr
Each question must have exactly {number_options} options and exactly one correct answer.
Make the questions relevant to the requested topic and factually accurate"""
        user_message = f"Generate {number_quizzes} questions about {subject}"
        response = client.beta.chat.completions.parse(
            model = "openrouter/free",
            messages=[{
                "role":"system",
                "content":SYSTEM_PROMPT
            },
            {
                "role":"user",
                "content":user_message
            }],
            response_format=QuizzResponse
        )
    except AuthenticationError as error:
        raise AIServiceError("auth","Invalid API key")
    except RateLimitError as error:
        raise AIServiceError("rate_limit","Rate limited by the provider")
    except Exception as e:
        raise AIServiceError("Unkown",str(e))
    event = response.choices[0].message.parsed
    return event
if __name__ == "__main__":
    print(generate_quizz("math","4","4"))
