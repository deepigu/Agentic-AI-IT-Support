
from typing import TypedDict, Any, NotRequired

from langgraph.graph import StateGraph, START, END

from backend.app.agents.ai_diagnosis import ai_diagnose_issue
from backend.app.services.knowledge_search import search_knowledge_base
from backend.app.agents.ai_router import ai_choose_tool
from backend.app.agents.ticket_decision import ai_decide_ticket


# ==================================
# DEFINE AGENT STATE
# ==================================

class SupportState(TypedDict):
    issue: str
    knowledge_base: NotRequired[Any]
    ai_response: str
    ticket_recommendation: NotRequired[str]


# ==================================
# KNOWLEDGE BASE SEARCH NODE
# ==================================

def knowledge_search_node(state: SupportState):

    # Get the user's IT problem
    issue = state["issue"]

    # Search the internal knowledge base
    knowledge = search_knowledge_base(issue)

    # Return the matching knowledge article
    return {
        "knowledge_base": knowledge
    }


# ==================================
# AI-POWERED ROUTING DECISION
# ==================================

def decide_knowledge_search(state: SupportState):

    # Get the user's IT problem
    issue = state["issue"]

    # Ask OpenAI which path to follow
    decision = ai_choose_tool(issue)

    # Display the selected path in the terminal
    print(f"AI selected path: {decision}")

    return decision


# ==================================
# AI DIAGNOSIS NODE
# ==================================

def diagnosis_node(state: SupportState):

    # Get the user's IT problem
    issue = state["issue"]

    # Get knowledge base information if available
    knowledge = state.get("knowledge_base")

    # Prepare the AI prompt
    if knowledge is not None:

        prompt = (
            f"User IT problem: {issue}\n\n"
            f"Internal knowledge base information:\n{knowledge}\n\n"
            "Use the relevant knowledge base information "
            "to provide clear and safe troubleshooting steps. "
            "If more information is needed, ask useful questions. "
            "Do not claim to have performed any actions."
        )

    else:

        prompt = (
            f"User IT problem: {issue}\n\n"
            "No internal knowledge base article was retrieved. "
            "Analyze the problem and provide clear, safe, "
            "step-by-step troubleshooting instructions. "
            "Ask useful questions if more information is needed. "
            "Do not claim to have performed any actions."
        )

    # Send the prompt to OpenAI
    response = ai_diagnose_issue(prompt)

    # Return the AI-generated diagnosis
    return {
        "ai_response": response
    }


# ==================================
# AI TICKET RECOMMENDATION NODE
# ==================================

def ticket_decision_node(state: SupportState):

    # Get the original IT problem
    issue = state["issue"]

    # Get the AI troubleshooting response
    ai_response = state["ai_response"]

    # Ask OpenAI whether a ticket is recommended
    recommendation = ai_decide_ticket(
        issue,
        ai_response
    )

    # Display the recommendation in the terminal
    print(f"AI ticket recommendation: {recommendation}")

    # Return the recommendation
    return {
        "ticket_recommendation": recommendation
    }


# ==================================
# CREATE LANGGRAPH WORKFLOW
# ==================================

workflow = StateGraph(SupportState)


# ==================================
# REGISTER WORKFLOW NODES
# ==================================

workflow.add_node(
    "knowledge_search",
    knowledge_search_node
)

workflow.add_node(
    "diagnosis",
    diagnosis_node
)

workflow.add_node(
    "ticket_decision",
    ticket_decision_node
)


# ==================================
# AI-POWERED CONDITIONAL ROUTING
# ==================================

workflow.add_conditional_edges(
    START,
    decide_knowledge_search,
    {
        "knowledge_search": "knowledge_search",
        "diagnosis": "diagnosis"
    }
)


# ==================================
# CONNECT WORKFLOW NODES
# ==================================

# After knowledge search, run AI diagnosis
workflow.add_edge(
    "knowledge_search",
    "diagnosis"
)

# After diagnosis, evaluate ticket requirement
workflow.add_edge(
    "diagnosis",
    "ticket_decision"
)

# Finish after ticket recommendation
workflow.add_edge(
    "ticket_decision",
    END
)


# ==================================
# COMPILE LANGGRAPH WORKFLOW
# ==================================

support_graph = workflow.compile()
