
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


def chat_with_it_agent(messages: list) -> str:
    """
    Continue an IT support conversation using
    the previous messages as context.
    """

    if not messages:
        raise ValueError("Conversation cannot be empty.")

    instructions = """
    You are a professional AI IT Support Assistant.

    Your responsibilities:
    1. Understand the user's IT problem.
    2. Ask relevant troubleshooting questions.
    3. Provide clear, beginner-friendly instructions.
    4. Remember details from earlier messages.
    5. Troubleshoot one step at a time.
    6. Recommend contacting human IT support when necessary.

    Safety requirements:
    - Never request passwords, MFA codes, or API keys.
    - Do not suggest disabling security protections.
    - Do not claim to have accessed or repaired a device.
    - Ask for human approval before recommending
      potentially disruptive actions.

    Keep responses clear and professional.
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=instructions,
        input=messages,
        max_output_tokens=500,
    )

    return response.output_text.strip()
