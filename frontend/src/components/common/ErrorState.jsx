import { AlertCircle, RefreshCw } from "lucide-react";
import { motion } from "framer-motion";

export default function ErrorState({ message, onRetry }) {
  return (
    <motion.div
      className="error-state"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <div className="error-icon">
        <AlertCircle size={28} />
      </div>

      <h2>Something went wrong</h2>

      <p>{message || "Unable to load your photos."}</p>

      {onRetry && (
        <button type="button" className="secondary-button" onClick={onRetry}>
          <RefreshCw size={16} />
          Try again
        </button>
      )}
    </motion.div>
  );
}