
from backend.app.database import SessionLocal
from backend.app.models.ticket import SupportTicket


# ==========================================
# VALID TICKET PRIORITIES AND STATUSES
# ==========================================

ALLOWED_PRIORITIES = {
    "Low",
    "Medium",
    "High",
    "Critical"
}

ALLOWED_STATUSES = {
    "Open",
    "In Progress",
    "Resolved",
    "Closed"
}


# ==========================================
# CONVERT DATABASE TICKET TO DICTIONARY
# ==========================================

def ticket_to_dict(ticket):
    """
    Convert a database ticket into a dictionary
    that FastAPI can return as JSON.
    """

    return {
        "ticket_id": ticket.id,
        "issue": ticket.issue,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "created_at": (
            ticket.created_at.isoformat()
            if ticket.created_at
            else None
        )
    }


# ==========================================
# CREATE AND SAVE SUPPORT TICKET
# ==========================================

def create_ticket(
    issue: str,
    category: str,
    priority: str = "Medium"
):
    """
    Create a support ticket with a priority.

    The default priority is Medium so older
    code that calls create_ticket(issue, category)
    will continue working.
    """

    if not issue or not issue.strip():
        raise ValueError("Ticket issue cannot be empty.")

    if not category or not category.strip():
        raise ValueError("Ticket category cannot be empty.")

    if priority not in ALLOWED_PRIORITIES:
        raise ValueError("Invalid ticket priority.")

    db = SessionLocal()

    try:
        new_ticket = SupportTicket(
            issue=issue.strip(),
            category=category.strip(),
            priority=priority,
            status="Open"
        )

        db.add(new_ticket)
        db.commit()
        db.refresh(new_ticket)

        return ticket_to_dict(new_ticket)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# RETRIEVE ALL SUPPORT TICKETS
# ==========================================

def get_all_tickets():
    """
    Return all tickets, newest first.
    """

    db = SessionLocal()

    try:
        tickets = (
            db.query(SupportTicket)
            .order_by(SupportTicket.id.desc())
            .all()
        )

        return [
            ticket_to_dict(ticket)
            for ticket in tickets
        ]

    finally:
        db.close()


# ==========================================
# GET SUPPORT TICKET BY ID
# ==========================================

def get_ticket_by_id(ticket_id: int):
    """
    Return one ticket using its ID.
    """

    db = SessionLocal()

    try:
        ticket = (
            db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            return None

        return ticket_to_dict(ticket)

    finally:
        db.close()


# ==========================================
# UPDATE SUPPORT TICKET STATUS
# ==========================================

def update_ticket_status(
    ticket_id: int,
    new_status: str
):
    """
    Update the status of an existing ticket.
    """

    if new_status not in ALLOWED_STATUSES:
        raise ValueError(
            "Invalid ticket status. "
            "Choose Open, In Progress, Resolved, or Closed."
        )

    db = SessionLocal()

    try:
        ticket = (
            db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            return None

        ticket.status = new_status

        db.commit()
        db.refresh(ticket)

        return ticket_to_dict(ticket)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# UPDATE TICKET PRIORITY
# ==========================================

def update_ticket_priority(
    ticket_id: int,
    new_priority: str
):
    """
    Update the priority of an existing ticket.
    """

    if new_priority not in ALLOWED_PRIORITIES:
        raise ValueError("Invalid ticket priority.")

    db = SessionLocal()

    try:
        ticket = (
            db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            return None

        ticket.priority = new_priority

        db.commit()
        db.refresh(ticket)

        return ticket_to_dict(ticket)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================
# DELETE SUPPORT TICKET
# ==========================================

def delete_ticket(ticket_id: int):
    """
    Delete a support ticket using its ID.
    """

    db = SessionLocal()

    try:
        ticket = (
            db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id)
            .first()
        )

        if ticket is None:
            return False

        db.delete(ticket)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
