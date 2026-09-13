import { motion } from "framer-motion";
import { Menu } from "lucide-react";

export default function Header({ onMenuClick }) {
  return (
    <motion.header
      className="app-header"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      <button
        className="mobile-menu-button"
        onClick={onMenuClick}
        aria-label="Open navigation"
      >
        <Menu size={22} />
      </button>

      <div className="header-title">
        <span className="header-title-main">Your Library</span>
      </div>
    </motion.header>
  );
}