
# ==========================================
# AGENTIC AI IT SUPPORT
# AI Ticket Priority Classification Agent
# ==========================================

from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ==========================================
# STEP 1: LOAD ENVIRONMENT VARIABLES
# ==========================================

# Find the main project folder
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Load the OpenAI API key from .env
load_dotenv(PROJECT_ROOT / ".env")


# ==========================================
# STEP 2: INITIALIZE OPENAI CLIENT
# ==========================================

client = OpenAI()


# ==========================================
# STEP 3: CLASSIFY TICKET PRIORITY
# ==========================================

def classify_ticket_priority(issue: str) -> str:
    """
    Analyze an IT support issue using OpenAI.

    Return one of four priority levels:

    Low
    Medium
    High
    Critical
    """

    if not isinstance(issue, str) or not issue.strip():
        raise ValueError("IT issue cannot be empty.")

    response = client.responses.create(
        model="gpt-4.1-mini",

        instructions=(
            "You are an experienced IT Service Desk "
            "Priority Classification Agent. "

            "Your responsibility is to analyze IT support "
            "issues and assign the appropriate priority. "

            "Classify each issue into exactly one of "
            "these four categories: "

            "Low, Medium, High, Critical. "

            "PRIORITY RULES: "

            "Critical: Company-wide network outages, "
            "major security incidents, ransomware attacks, "
            "or widespread business-critical service failures. "

            "High: Important individual account lockouts, "
            "critical employee access problems, "
            "or major departmental service disruptions. "

            "Medium: Slow computers, application errors, "
            "intermittent connectivity, or ordinary "
            "operational problems. "

            "Low: General IT questions, minor software "
            "requests, or nonurgent assistance. "

            "Use only the information provided. "
            "Do not assume a company-wide outage "
            "unless the issue indicates one. "

            "Return ONLY one word: "
            "Low, Medium, High, or Critical. "
            "Do not include explanations."
        ),

        input=issue.strip(),

        max_output_tokens=20,
    )

    # ======================================
    # STEP 4: READ AI RESPONSE
    # ======================================

    priority = response.output_text.strip().title()

    # ======================================
    # STEP 5: VALIDATE PRIORITY
    # ======================================

    allowed_priorities = {
        "Low",
        "Medium",
        "High",
        "Critical",
    }

    if priority not in allowed_priorities:
        return "Medium"

    return priority
