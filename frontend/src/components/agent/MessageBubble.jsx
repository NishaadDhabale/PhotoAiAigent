import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";

export default function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <motion.div
      className={`agent-message-row ${
        isUser ? "user" : "assistant"
      }`}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="agent-avatar">
        {isUser ? <User size={17} /> : <Bot size={17} />}
      </div>

      <div className="agent-message-bubble">
        {content}
      </div>
    </motion.div>
  );
}