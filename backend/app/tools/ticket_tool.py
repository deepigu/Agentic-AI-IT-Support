
from backend.app.services.ticket_service import create_ticket


# ==================================
# IT SUPPORT TICKET TOOL
# ==================================

def create_support_ticket(issue: str, category: str):

    # Use our existing database ticket service
    ticket = create_ticket(
        issue=issue,
        category=category
    )

    # Return the newly created ticket
    return ticket
