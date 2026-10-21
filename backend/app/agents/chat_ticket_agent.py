
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

client = OpenAI()


def recommend_chat_ticket(messages: list) -> bool:
    """
    Decide whether an IT support conversation
    should be escalated to a human support ticket.
    """

    if not messages:
        return False

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are an IT support escalation classifier. "
            "Review the conversation and decide whether "
            "a human IT support ticket should be recommended. "
            "Recommend a ticket for unresolved issues, "
            "repeated troubleshooting failures, "
            "security incidents, or major service outages. "
            "Return exactly YES or NO. "
            "Do not provide an explanation."
        ),
        input=conversation,
        max_output_tokens=50,
    )

    decision = response.output_text.strip().upper()

    return decision == "YES"
