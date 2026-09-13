import { Search, SlidersHorizontal, X } from "lucide-react";
import { motion } from "framer-motion";

export default function SearchBar({
  value,
  onChange,
  onSubmit,
  onClear,
  loading = false,
}) {
  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      onSubmit?.();
    }

    if (event.key === "Escape") {
      onClear?.();
    }
  };

  return (
    <motion.div
      className="search-section"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="search-box">
        <Search size={20} className="search-icon" />

        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search your photos..."
          aria-label="Search photos"
        />

        {value && (
          <button
            type="button"
            className="search-clear"
            onClick={onClear}
            aria-label="Clear search"
          >
            <X size={18} />
          </button>
        )}

        <button
          type="button"
          className="search-filter-button"
          aria-label="Search filters"
          title="More search options coming soon"
        >
          <SlidersHorizontal size={18} />
        </button>

        <button
          type="button"
          className="search-submit"
          onClick={onSubmit}
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <p className="search-hint">
        Try things like <strong>"people at the beach"</strong>,{" "}
        <strong>"Nisha"</strong>, or <strong>"photos from 2022"</strong>
      </p>
    </motion.div>
  );
}