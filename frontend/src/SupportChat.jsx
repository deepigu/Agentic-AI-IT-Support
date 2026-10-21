
import { useEffect, useRef, useState } from "react";
import "./SupportChat.css";

// ==========================================
// FASTAPI BACKEND
// ==========================================

const API_URL = "http://127.0.0.1:8000";

// ==========================================
// LOCAL STORAGE KEY
// ==========================================

const STORAGE_KEY = "it_support_chat_history";

// ==========================================
// LOAD SAVED CHAT HISTORY
// ==========================================

function loadSavedMessages() {
  try {
    const savedMessages = localStorage.getItem(STORAGE_KEY);

    if (!savedMessages) {
      return [];
    }

    const parsedMessages = JSON.parse(savedMessages);

    if (!Array.isArray(parsedMessages)) {
      return [];
    }

    // Only restore valid chat messages.
    return parsedMessages.filter(
      (message) =>
        message &&
        (message.role === "user" ||
          message.role === "assistant") &&
        typeof message.content === "string" &&
        message.content.trim().length > 0
    );
  } catch (error) {
    console.error("Unable to load chat history:", error);
    return [];
  }
}

// ==========================================
// AI SUPPORT CHAT COMPONENT
// ==========================================

function SupportChat() {
  // ==========================================
  // REACT STATE
  // ==========================================

  const [messages, setMessages] = useState(
    loadSavedMessages
  );

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const messagesEndRef = useRef(null);

  // ==========================================
  // SAVE CHAT HISTORY AUTOMATICALLY
  // ==========================================

  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(messages)
      );
    } catch (error) {
      console.error("Unable to save chat history:", error);
    }
  }, [messages]);

  // ==========================================
  // SCROLL TO LATEST MESSAGE
  // ==========================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "nearest",
    });
  }, [messages, loading]);

  // ==========================================
  // SEND MESSAGE TO AI AGENT
  // ==========================================

  async function sendMessage(event) {
    event.preventDefault();

    const text = input.trim();

    if (!text || loading) {
      return;
    }

    // Add the user's message.
    const updatedMessages = [
      ...messages,
      {
        role: "user",
        content: text,
      },
    ];

    setMessages(updatedMessages);
    setInput("");
    setLoading(true);
    setError("");

    try {
      // Send the conversation to FastAPI.
      const response = await fetch(
        `${API_URL}/api/agent/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: updatedMessages,
          }),
        }
      );

      if (!response.ok) {
        let errorMessage =
          `Chat request failed: HTTP ${response.status}`;

        try {
          const errorData = await response.json();

          if (typeof errorData.detail === "string") {
            errorMessage = errorData.detail;
          }
        } catch {
          // Use the default error message.
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      if (
        typeof data.reply !== "string" ||
        !data.reply.trim()
      ) {
        throw new Error(
          "The AI assistant returned an empty response."
        );
      }

      // Add the AI assistant's response.
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: data.reply,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ==========================================
  // START NEW CHAT
  // ==========================================

  function clearChat() {
    if (loading) {
      return;
    }

    setMessages([]);
    setInput("");
    setError("");

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error(
        "Unable to clear saved chat history:",
        error
      );
    }
  }

  // ==========================================
  // USER INTERFACE
  // ==========================================

  return (
    <section className="chat-container">

      {/* CHAT HEADER */}

      <div className="chat-header">
        <div>
          <h2>🤖 AI IT Support Chat</h2>

          <p>
            Describe your issue and troubleshoot
            step by step.
          </p>

          <small>
            Conversation history is saved in this browser.
          </small>
        </div>

        <button
          type="button"
          onClick={clearChat}
          disabled={loading}
          className="clear-chat-button"
        >
          New Chat
        </button>
      </div>

      {/* CHAT MESSAGES */}

      <div
        className="chat-messages"
        aria-live="polite"
      >

        {/* EMPTY CHAT */}

        {messages.length === 0 && (
          <p className="chat-empty">
            Hello! 👋
            {"\n"}
            How can I help with your IT issue today?
          </p>
        )}

        {/* CONVERSATION HISTORY */}

        {messages.map((message, index) => (
          <div
            key={index}
            className={
              message.role === "user"
                ? "chat-message user-message"
                : "chat-message ai-message"
            }
          >
            <strong>
              {message.role === "user"
                ? "You"
                : "AI Assistant"}
            </strong>

            <p>{message.content}</p>
          </div>
        ))}

        {/* AI LOADING INDICATOR */}

        {loading && (
          <p className="chat-typing">
            🤖 AI Assistant is thinking...
          </p>
        )}

        {/* SCROLL TARGET */}

        <div ref={messagesEndRef} />
      </div>

      {/* ERROR MESSAGE */}

      {error && (
        <p role="alert" className="chat-error">
          {error}
        </p>
      )}

      {/* CHAT INPUT */}

      <form
        onSubmit={sendMessage}
        className="chat-input-area"
      >
        <input
          type="text"
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          placeholder="Type your IT support question..."
          disabled={loading}
          aria-label="Chat message"
        />

        <button
          type="submit"
          disabled={!input.trim() || loading}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </form>

    </section>
  );
}

export default SupportChat;
