import {
  useEffect,
  useState,
} from "react";
import { sendAgentMessage } from "../../api/photoApi";
import MessageBubble from "./MessageBubble";
import ThinkingIndicator from "./ThinkingIndicator";
import ExamplePrompts from "./ExamplePrompts";
import ChatInput from "./ChatInput";
import AgentResultGrid from "./AgentResultGrid";

export default function AgentChat({
  onPhotoClick,
  clearRef,
}) {
  const [messages, setMessages] = useState([]);
  const [results, setResults] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
  if (!clearRef) {
    return;
  }

  clearRef.current = () => {
    setMessages([]);
    setResults([]);
    setInput("");
    setError("");
  };

  return () => {
    clearRef.current = null;
  };
}, [clearRef]);
  async function sendMessage(customMessage = null) {
    const text = (
      customMessage ?? input
    ).trim();

    if (!text || loading) {
      return;
    }

    setError("");
    setInput("");

    const userMessage = {
      role: "user",
      content: text,
    };

    const previousMessages = messages;

    const nextMessages = [
      ...previousMessages,
      userMessage,
    ];

    setMessages(nextMessages);
    setLoading(true);

    try {
      const response = await sendAgentMessage({
        message: text,
        history: previousMessages,
      });

      const assistantMessage = {
        role: "assistant",
        content:
          response.answer ||
          "I couldn't generate a response.",
      };

      setMessages([
        ...nextMessages,
        assistantMessage,
      ]);

      setResults(response.results || []);
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong while contacting the agent."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage();
  }

function clearChat() {
  setMessages([]);
  setResults([]);
  setInput("");
  setError("");
  onClear?.();
}
  const hasMessages = messages.length > 0;

  return (
    <>
      {!hasMessages && (
        <ExamplePrompts
          onSelect={sendMessage}
        />
      )}

      <section className="agent-chat">
        {messages.map((message, index) => (
          <MessageBubble
            key={`${message.role}-${index}`}
            role={message.role}
            content={message.content}
          />
        ))}

        {loading && <ThinkingIndicator />}

        {error && (
          <div className="agent-error">
            {error}
          </div>
        )}

        <AgentResultGrid
          results={results}
          onPhotoClick={onPhotoClick}
        />
      </section>

      {messages.length > 0 && (
  <button
    type="button"
    className="agent-chat-clear"
    onClick={clearChat}
  >
    Clear conversation
  </button>
)}
      <ChatInput
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        disabled={loading}
      />
    </>
  );
}