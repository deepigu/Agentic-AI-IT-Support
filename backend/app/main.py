
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.agents.conversation_agent import chat_with_it_agent
import os
# ==========================================
# IMPORT AI AGENTS
# ==========================================

from backend.app.agents.ai_diagnosis import ai_diagnose_issue
from backend.app.agents.support_graph import support_graph
from backend.app.agents.priority_agent import classify_ticket_priority

# ==========================================
# IMPORT IT SUPPORT TOOLS
# ==========================================

from backend.app.tools.diagnosis import diagnose_issue

# ==========================================
# IMPORT KNOWLEDGE BASE
# ==========================================

from backend.app.services.knowledge_search import search_knowledge_base

# ==========================================
# IMPORT DATABASE TICKET FUNCTIONS
# ==========================================

from backend.app.services.ticket_service import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket_status,
    update_ticket_priority,
    delete_ticket,
)

# ==========================================
# CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Agentic AI IT Support Agent",
    description=(
        "AI-powered IT troubleshooting, ticket management, "
        "and intelligent priority classification"
    ),
    version="1.1.0",
)


# ==========================================
# CONFIGURE CORS FOR REACT AND NETLIFY
# ==========================================

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://agentic-ai-it-support.netlify.app",
]

# Optional: support a different frontend URL configured on Render.
netlify_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
if netlify_url and netlify_url not in allowed_origins:
    allowed_origins.append(netlify_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# ==========================================
# REQUEST MODELS
# ==========================================

class ITSupportRequest(BaseModel):
    issue: str = Field(min_length=1)


class TicketStatusUpdate(BaseModel):
    status: str


class TicketPriorityUpdate(BaseModel):
    priority: str


class ConfirmTicketRequest(BaseModel):
    issue: str = Field(min_length=1)
    category: str = Field(min_length=1)
    confirmed: bool = False


from typing import Literal

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ConversationRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)

# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to Agentic AI IT Support Agent",
        "status": "running",
        "version": "1.1.0",
    }


# ==========================================
# LEGACY IT SUPPORT REQUEST
# ==========================================

@app.post("/api/support")
def create_support_request(request: ITSupportRequest):
    """
    Legacy endpoint.

    Diagnoses an issue, searches the knowledge base,
    and creates a ticket with Medium priority.

    Note: This endpoint automatically creates a ticket.
    The React confirmation workflow should use
    /api/agent/support and /api/tickets/confirm instead.
    """

    diagnosis = diagnose_issue(request.issue)

    knowledge = search_knowledge_base(request.issue)

    ticket = create_ticket(
        issue=request.issue,
        category=diagnosis["category"],
        priority="Medium",
    )

    return {
        "issue": request.issue,
        "category": diagnosis["category"],
        "suggestion": diagnosis["suggestion"],
        "knowledge_base": knowledge,
        "ticket": ticket,
        "status": "diagnosed",
    }


# ==========================================
# GET ALL SUPPORT TICKETS
# ==========================================

@app.get("/api/tickets")
def list_support_tickets():

    tickets = get_all_tickets()

    return {
        "total_tickets": len(tickets),
        "tickets": tickets,
    }


# ==========================================
# GET SUPPORT TICKET BY ID
# ==========================================

@app.get("/api/tickets/{ticket_id}")
def retrieve_support_ticket(ticket_id: int):

    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return ticket


# ==========================================
# UPDATE SUPPORT TICKET STATUS
# ==========================================

@app.patch("/api/tickets/{ticket_id}/status")
def change_ticket_status(
    ticket_id: int,
    request: TicketStatusUpdate,
):

    try:
        updated_ticket = update_ticket_status(
            ticket_id=ticket_id,
            new_status=request.status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if updated_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return {
        "message": "Ticket status updated successfully",
        "ticket": updated_ticket,
    }


# ==========================================
# UPDATE SUPPORT TICKET PRIORITY
# ==========================================

@app.patch("/api/tickets/{ticket_id}/priority")
def change_ticket_priority(
    ticket_id: int,
    request: TicketPriorityUpdate,
):
    """
    Allow IT staff to manually update ticket priority.
    """

    try:
        updated_ticket = update_ticket_priority(
            ticket_id=ticket_id,
            new_priority=request.priority,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    if updated_ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return {
        "message": "Ticket priority updated successfully",
        "ticket": updated_ticket,
    }


# ==========================================
# DELETE SUPPORT TICKET
# ==========================================

@app.delete("/api/tickets/{ticket_id}")
def remove_support_ticket(ticket_id: int):

    deleted = delete_ticket(ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Support ticket not found",
        )

    return {
        "message": "Support ticket deleted successfully",
        "ticket_id": ticket_id,
    }


# ==========================================
# AI-POWERED IT DIAGNOSIS
# ==========================================

@app.post("/api/ai-diagnosis")
def create_ai_diagnosis(request: ITSupportRequest):

    ai_response = ai_diagnose_issue(request.issue)

    return {
        "issue": request.issue,
        "ai_response": ai_response,
        "status": "completed",
    }


# ==========================================
# LANGGRAPH IT SUPPORT WORKFLOW
# ==========================================

@app.post("/api/agent/support")
def agent_support_request(request: ITSupportRequest):

    initial_state = {
        "issue": request.issue,
        "ai_response": "",
    }

    result = support_graph.invoke(initial_state)

    return {
        "issue": result["issue"],
        "ai_response": result["ai_response"],
        "ticket_recommendation": result.get(
            "ticket_recommendation",
            "no_ticket",
        ),
        "status": "completed",
    }


# ==========================================
# AI PRIORITY CLASSIFICATION
# ==========================================

@app.post("/api/agent/priority")
def analyze_ticket_priority(request: ITSupportRequest):

    priority = classify_ticket_priority(request.issue)

    return {
        "issue": request.issue,
        "priority": priority,
        "status": "completed",
    }


# ==========================================
# USER-CONFIRMED TICKET CREATION
# ==========================================

@app.post("/api/tickets/confirm")
def create_confirmed_ticket(request: ConfirmTicketRequest):
    """
    Create a support ticket only after the user
    explicitly confirms ticket creation.

    The AI classifies priority before saving.
    """

    # Step 1: Check user confirmation
    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail=(
                "User confirmation is required "
                "to create a ticket."
            ),
        )

    # Step 2: Determine AI priority
    try:
        priority = classify_ticket_priority(request.issue)

    except Exception:
        # If AI classification is unavailable,
        # keep ticket creation working with a
        # provisional Medium priority.
        priority = "Medium"

    # Step 3: Create ticket in the configured database
    ticket = create_ticket(
        issue=request.issue,
        category=request.category,
        priority=priority,
    )

    # Step 4: Return saved ticket
    return {
        "message": "Support ticket created successfully",
        **ticket,
        "priority_source": (
            "AI" if priority != "Medium"
            else "AI or default"
        ),
    }

# ==========================================
# AI IT SUPPORT CONVERSATION
# ==========================================

@app.post("/api/agent/chat")
def agent_chat(request: ConversationRequest):

    messages = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in request.messages
    ]

    if messages[-1]["role"] != "user":
        raise HTTPException(
            status_code=400,
            detail="The last message must be from the user."
        )

    try:
        ai_response = chat_with_it_agent(messages)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI conversation service is temporarily unavailable."
        )

    return {
        "reply": ai_response,
        "status": "completed"
    }
