import { ImageOff, SearchX } from "lucide-react";
import { motion } from "framer-motion";

export default function EmptyState({ searching = false, onClear }) {
  return (
    <motion.div
      className="empty-state"
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <div className="empty-icon">
        {searching ? <SearchX size={30} /> : <ImageOff size={30} />}
      </div>

      <h2>{searching ? "No photos found" : "No photos yet"}</h2>

      <p>
        {searching
          ? "Try a different search or clear your filters."
          : "Your photo library is currently empty."}
      </p>

      {searching && onClear && (
        <button type="button" className="secondary-button" onClick={onClear}>
          Clear search
        </button>
      )}
    </motion.div>
  );
}