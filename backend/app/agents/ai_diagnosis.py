
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==================================
# AI-POWERED IT DIAGNOSIS
# ==================================

def ai_diagnose_issue(issue: str):

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are a professional IT support assistant. "
            "Analyze the user's IT problem. "
            "Explain the likely cause and provide clear, "
            "safe, step-by-step troubleshooting instructions. "
            "If information is missing, ask a useful question. "
            "Do not claim to have performed any actions."
        ),
        input=issue
    )

    return response.output_text
