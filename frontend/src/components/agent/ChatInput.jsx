import { useEffect, useRef } from "react";
import { Send } from "lucide-react";

export default function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled = false,
}) {
  const inputRef = useRef(null);

  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  }, [disabled]);

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit(event);
    }
  }

  return (
    <form
      className="agent-input-container"
      onSubmit={onSubmit}
    >
      <textarea
        ref={inputRef}
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        onKeyDown={handleKeyDown}
        placeholder="Ask something about your photos..."
        disabled={disabled}
        rows={1}
      />

      <button
        type="submit"
        disabled={!value.trim() || disabled}
        aria-label="Send message"
      >
        <Send size={18} />
      </button>
    </form>
  );
}