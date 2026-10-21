
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ==================================
# AI TICKET DECISION FUNCTION
# ==================================

def ai_decide_ticket(issue: str, ai_response: str) -> str:

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are an IT support ticket triage assistant. "
            "Determine whether a support ticket should be "
            "recommended for human IT assistance. "
            "Recommend a ticket when the user reports an "
            "unresolved, recurring, or serious IT problem, "
            "or explicitly requests human support. "
            "Do not recommend a ticket for a simple "
            "informational question. "
            "Return exactly one value: "
            "create_ticket or no_ticket. "
            "Do not include explanations."
        ),
        input=(
            f"User issue: {issue}\n\n"
            f"AI troubleshooting advice: {ai_response}"
        ),
        temperature=0
    )

    decision = response.output_text.strip().lower()

    # Validate the AI output
    if decision not in ("create_ticket", "no_ticket"):
        return "no_ticket"

    return decision
