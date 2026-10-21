
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# ==================================
# AI-BASED TOOL ROUTER
# ==================================

def ai_choose_tool(issue: str) -> str:

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are an IT support routing assistant. "
            "Decide whether the user's problem should "
            "use the internal IT knowledge base. "
            "The knowledge base covers Wi-Fi, network, "
            "login, passwords, computer performance, "
            "printers, and email issues. "
            "Return exactly one word: "
            "knowledge_search or diagnosis. "
            "Do not include explanations."
        ),
        input=issue,
        temperature=0
    )

    decision = response.output_text.strip().lower()

    # Validate the AI decision
    if decision not in (
        "knowledge_search",
        "diagnosis"
    ):
        return "diagnosis"

    return decision
