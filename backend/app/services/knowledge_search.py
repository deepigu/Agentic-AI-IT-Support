
import json
from pathlib import Path


# Find the knowledge base JSON file
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base.json"


def search_knowledge_base(issue: str):
    """
    Search IT troubleshooting articles using keywords.
    """

    # Open and read the knowledge base
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Convert the user's issue to lowercase
    issue = issue.lower()

    # Search each article
    for article in data["articles"]:

        # Check whether any keyword matches
        if any(
            keyword.lower() in issue
            for keyword in article["keywords"]
        ):
            return {
                "article_id": article["id"],
                "category": article["category"],
                "title": article["title"],
                "solutions": article["solutions"]
            }

    # Return this if no matching article exists
    return {
        "article_id": None,
        "category": "Unknown",
        "title": "No matching knowledge base article",
        "solutions": [
            "Collect more information about the issue.",
            "Contact IT support for further assistance."
        ]
    }
