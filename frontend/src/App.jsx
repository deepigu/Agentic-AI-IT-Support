
import { useEffect, useState } from "react";
import "./App.css";

import SupportChat from "./SupportChat";

// ==========================================
// FASTAPI BACKEND URL
// ==========================================

const API_URL = "http://127.0.0.1:8000";

function App() {
  // ==========================================
  // REACT STATE
  // ==========================================

  const [issue, setIssue] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [ticketRecommendation, setTicketRecommendation] =
    useState("");

  const [tickets, setTickets] = useState([]);

  const [loading, setLoading] = useState(false);
  const [ticketLoading, setTicketLoading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [ticketDeclined, setTicketDeclined] =
    useState(false);

  const [updatingTicket, setUpdatingTicket] =
    useState(null);

  // ==========================================
  // SEND REQUESTS TO FASTAPI
  // ==========================================

  async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      let detail = `Request failed: HTTP ${response.status}`;

      try {
        const data = await response.json();

        if (typeof data.detail === "string") {
          detail = data.detail;
        }
      } catch {
        // Keep the default error message.
      }

      throw new Error(detail);
    }

    return response.json();
  }

  // ==========================================
  // LOAD SUPPORT TICKETS
  // ==========================================

  async function loadTickets() {
    try {
      const data = await apiRequest("/api/tickets");

      setTickets(
        Array.isArray(data)
          ? data
          : data.tickets || []
      );
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadTickets();
  }, []);

  // ==========================================
  // AI IT SUPPORT ANALYSIS
  // ==========================================

  async function analyzeIssue() {
    if (!issue.trim() || loading) return;

    setLoading(true);
    setError("");
    setMessage("");
    setAiResponse("");
    setTicketRecommendation("");
    setTicketDeclined(false);

    try {
      const data = await apiRequest(
        "/api/agent/support",
        {
          method: "POST",
          body: JSON.stringify({
            issue: issue.trim(),
          }),
        }
      );

      setAiResponse(data.ai_response || "");

      setTicketRecommendation(
        data.ticket_recommendation || ""
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ==========================================
  // IDENTIFY IT ISSUE CATEGORY
  // ==========================================

  function categorizeIssue(text) {
    const value = text.toLowerCase();

    if (
      value.includes("password") ||
      value.includes("login") ||
      value.includes("account") ||
      value.includes("locked")
    ) {
      return "Authentication";
    }

    if (
      value.includes("wifi") ||
      value.includes("network") ||
      value.includes("internet")
    ) {
      return "Network";
    }

    if (
      value.includes("slow") ||
      value.includes("performance") ||
      value.includes("freezing")
    ) {
      return "Performance";
    }

    if (
      value.includes("printer") ||
      value.includes("printing")
    ) {
      return "Printer";
    }

    if (
      value.includes("email") ||
      value.includes("outlook")
    ) {
      return "Email";
    }

    return "General IT Issue";
  }

  // ==========================================
  // CREATE SUPPORT TICKET
  // ==========================================

  async function createTicket() {
    if (
      ticketLoading ||
      !issue.trim() ||
      ticketRecommendation !== "create_ticket" ||
      ticketDeclined
    ) {
      return;
    }

    setTicketLoading(true);
    setError("");
    setMessage("");

    try {
      const ticket = await apiRequest(
        "/api/tickets/confirm",
        {
          method: "POST",
          body: JSON.stringify({
            issue: issue.trim(),
            category: categorizeIssue(issue),
            confirmed: true,
          }),
        }
      );

      setMessage(
        `Support ticket #${ticket.ticket_id} created successfully with ${ticket.priority} priority.`
      );

      setTicketRecommendation("ticket_created");

      await loadTickets();
    } catch (err) {
      setError(err.message);
    } finally {
      setTicketLoading(false);
    }
  }

  // ==========================================
  // UPDATE TICKET STATUS
  // ==========================================

  async function updateTicketStatus(ticketId, status) {
    setError("");
    setMessage("");
    setUpdatingTicket(ticketId);

    try {
      await apiRequest(
        `/api/tickets/${ticketId}/status`,
        {
          method: "PATCH",
          body: JSON.stringify({ status }),
        }
      );

      setMessage(
        `Ticket #${ticketId} status updated to ${status}.`
      );

      await loadTickets();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdatingTicket(null);
    }
  }

  // ==========================================
  // UPDATE TICKET PRIORITY
  // ==========================================

  async function updateTicketPriority(ticketId, priority) {
    setError("");
    setMessage("");
    setUpdatingTicket(ticketId);

    try {
      await apiRequest(
        `/api/tickets/${ticketId}/priority`,
        {
          method: "PATCH",
          body: JSON.stringify({ priority }),
        }
      );

      setMessage(
        `Ticket #${ticketId} priority updated to ${priority}.`
      );

      await loadTickets();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdatingTicket(null);
    }
  }

  // ==========================================
  // DELETE SUPPORT TICKET
  // ==========================================

  async function deleteTicket(ticketId) {
    const confirmed = window.confirm(
      `Are you sure you want to delete ticket #${ticketId}?`
    );

    if (!confirmed) return;

    setError("");
    setMessage("");
    setUpdatingTicket(ticketId);

    try {
      await apiRequest(
        `/api/tickets/${ticketId}`,
        {
          method: "DELETE",
        }
      );

      setMessage(
        `Ticket #${ticketId} deleted successfully.`
      );

      await loadTickets();
    } catch (err) {
      setError(err.message);
    } finally {
      setUpdatingTicket(null);
    }
  }

  // ==========================================
  // PRIORITY COLORS
  // ==========================================

  function getPriorityStyle(priority) {
    const colors = {
      Critical: {
        backgroundColor: "#fee2e2",
        color: "#991b1b",
      },
      High: {
        backgroundColor: "#ffedd5",
        color: "#9a3412",
      },
      Medium: {
        backgroundColor: "#dbeafe",
        color: "#1e40af",
      },
      Low: {
        backgroundColor: "#dcfce7",
        color: "#166534",
      },
    };

    return {
      padding: "8px",
      borderRadius: "8px",
      fontWeight: "600",
      border: "1px solid #cbd5e1",
      ...(
        colors[priority] ||
        colors.Medium
      ),
    };
  }

  // ==========================================
  // DASHBOARD STATISTICS
  // ==========================================

  const totalTickets = tickets.length;

  const openTickets = tickets.filter(
    (ticket) =>
      ticket.status === "Open" ||
      ticket.status === "In Progress"
  ).length;

  const resolvedTickets = tickets.filter(
    (ticket) =>
      ticket.status === "Resolved" ||
      ticket.status === "Closed"
  ).length;

  const criticalTickets = tickets.filter(
    (ticket) => ticket.priority === "Critical"
  ).length;

  // ==========================================
  // REACT USER INTERFACE
  // ==========================================

  return (
    <div className="app-container">

      {/* HEADER */}

      <header className="app-header">
        <h1>🤖 Agentic AI IT Support</h1>

        <p>
          Intelligent Troubleshooting &
          Ticket Management
        </p>
      </header>

      <main
        style={{
          width: "min(1100px, 92%)",
          margin: "30px auto",
        }}
      >

        {/* AI SUPPORT SECTION */}

        <section className="dashboard">

          <div className="support-card">
            <h2>AI IT Support Assistant</h2>

            <p>
              Describe your IT issue and let the AI agent
              investigate it.
            </p>

            <label htmlFor="issue">
              Describe your IT issue
            </label>

            <textarea
              id="issue"
              rows="6"
              placeholder="Example: My work account is locked."
              value={issue}
              onChange={(event) =>
                setIssue(event.target.value)
              }
              disabled={loading || ticketLoading}
            />

            <button
              type="button"
              onClick={analyzeIssue}
              disabled={
                !issue.trim() ||
                loading ||
                ticketLoading
              }
            >
              {loading
                ? "Analyzing..."
                : "Analyze IT Issue"}
            </button>
          </div>

          {/* AI RESULTS */}

          <div className="results-card">
            <h2>AI Analysis Results</h2>

            {loading && (
              <p>AI agent is investigating...</p>
            )}

            {aiResponse ? (
              <>
                <h3>Troubleshooting Instructions</h3>

                <p
                  style={{
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {aiResponse}
                </p>

                <h3>Support Ticket Recommendation</h3>

                {ticketRecommendation === "create_ticket" &&
                !ticketDeclined ? (
                  <>
                    <p>
                      Human IT support is recommended.
                      Would you like to create a ticket?
                    </p>

                    <button
                      type="button"
                      onClick={createTicket}
                      disabled={ticketLoading}
                    >
                      {ticketLoading
                        ? "Creating Ticket..."
                        : "Create Support Ticket"}
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        setTicketDeclined(true)
                      }
                      disabled={ticketLoading}
                      style={{
                        marginTop: "10px",
                      }}
                    >
                      No, Thanks
                    </button>
                  </>
                ) : ticketRecommendation === "ticket_created" ? (
                  <p>
                    Support ticket created successfully.
                  </p>
                ) : ticketDeclined ? (
                  <p>
                    Ticket creation declined.
                    No ticket was created.
                  </p>
                ) : ticketRecommendation === "no_ticket" ? (
                  <p>
                    A support ticket is not currently
                    recommended.
                  </p>
                ) : (
                  <p>
                    No ticket recommendation available.
                  </p>
                )}
              </>
            ) : (
              !loading && (
                <p>
                  Your AI results will appear here.
                </p>
              )
            )}
          </div>
        </section>

        {/* ERROR MESSAGE */}

        {error && (
          <p
            role="alert"
            style={{
              color: "#dc2626",
              marginTop: "20px",
            }}
          >
            Error: {error}
          </p>
        )}

        {/* SUCCESS MESSAGE */}

        {message && (
          <p
            role="status"
            style={{
              color: "#15803d",
              marginTop: "20px",
            }}
          >
            {message}
          </p>
        )}

        {/* TICKET DASHBOARD */}

        <section
          className="results-card"
          style={{
            marginTop: "25px",
          }}
        >
          <h2>IT Support Dashboard</h2>

          {/* DASHBOARD METRICS */}

          <div
            style={{
              display: "flex",
              gap: "20px",
              flexWrap: "wrap",
              marginBottom: "20px",
            }}
          >
            <p>
              <strong>Total Tickets:</strong>{" "}
              {totalTickets}
            </p>

            <p>
              <strong>Open Tickets:</strong>{" "}
              {openTickets}
            </p>

            <p>
              <strong>Resolved Tickets:</strong>{" "}
              {resolvedTickets}
            </p>

            <p>
              <strong>Critical Tickets:</strong>{" "}
              {criticalTickets}
            </p>
          </div>

          <button
            type="button"
            onClick={loadTickets}
            style={{
              padding: "10px 16px",
              cursor: "pointer",
              marginBottom: "20px",
            }}
          >
            Refresh Tickets
          </button>

          {/* TICKET TABLE */}

          {tickets.length === 0 ? (
            <p>No support tickets found.</p>
          ) : (
            <div
              style={{
                overflowX: "auto",
              }}
            >
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  textAlign: "left",
                }}
              >
                <thead>
                  <tr>
                    <th>Ticket ID</th>
                    <th>Issue</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {tickets.map((ticket) => (
                    <tr key={ticket.ticket_id}>

                      <td>
                        #{ticket.ticket_id}
                      </td>

                      <td>
                        {ticket.issue}
                      </td>

                      <td>
                        {ticket.category}
                      </td>

                      {/* EDITABLE PRIORITY */}

                      <td>
                        <select
                          aria-label={
                            `Priority for ticket ${ticket.ticket_id}`
                          }
                          value={
                            ticket.priority || "Medium"
                          }
                          onChange={(event) =>
                            updateTicketPriority(
                              ticket.ticket_id,
                              event.target.value
                            )
                          }
                          disabled={
                            updatingTicket === ticket.ticket_id
                          }
                          style={getPriorityStyle(
                            ticket.priority || "Medium"
                          )}
                        >
                          <option value="Low">
                            Low
                          </option>

                          <option value="Medium">
                            Medium
                          </option>

                          <option value="High">
                            High
                          </option>

                          <option value="Critical">
                            Critical
                          </option>
                        </select>
                      </td>

                      {/* CURRENT STATUS */}

                      <td>
                        <select
                          aria-label={
                            `Status for ticket ${ticket.ticket_id}`
                          }
                          value={ticket.status}
                          onChange={(event) =>
                            updateTicketStatus(
                              ticket.ticket_id,
                              event.target.value
                            )
                          }
                          disabled={
                            updatingTicket === ticket.ticket_id
                          }
                          style={{
                            padding: "8px",
                            borderRadius: "8px",
                          }}
                        >
                          <option value="Open">
                            Open
                          </option>

                          <option value="In Progress">
                            In Progress
                          </option>

                          <option value="Resolved">
                            Resolved
                          </option>

                          <option value="Closed">
                            Closed
                          </option>
                        </select>
                      </td>

                      {/* DELETE BUTTON */}

                      <td>
                        <button
                          type="button"
                          onClick={() =>
                            deleteTicket(
                              ticket.ticket_id
                            )
                          }
                          disabled={
                            updatingTicket === ticket.ticket_id
                          }
                          style={{
                            padding: "8px 12px",
                            background: "#dc2626",
                            color: "white",
                            border: "none",
                            borderRadius: "6px",
                            cursor: "pointer",
                          }}
                        >
                          Delete
                        </button>
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* AI CONVERSATIONAL SUPPORT */}

        <SupportChat />
      </main>

      {/* FOOTER */}

      <footer className="app-footer">
        Agentic AI IT Support Agent | Python • FastAPI •
        LangGraph • OpenAI • React
      </footer>
    </div>
  );
}

export default App;
