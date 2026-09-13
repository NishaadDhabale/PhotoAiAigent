import { motion } from "framer-motion";
import { Bot } from "lucide-react";

export default function ThinkingIndicator() {
  return (
    <motion.div
      className="agent-message-row assistant"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="agent-avatar">
        <Bot size={17} />
      </div>

      <div className="agent-thinking">
        <span />
        <span />
        <span />
      </div>
    </motion.div>
  );
}