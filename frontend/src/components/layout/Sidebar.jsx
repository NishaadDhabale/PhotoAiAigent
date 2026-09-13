import { NavLink } from "react-router-dom";
import {
  Images,
  Users,
  CalendarDays,
  Map,
  Bot,
  Settings,
  Sparkles,Copy,FolderTree
} from "lucide-react";
import { motion } from "framer-motion";

const navigation = [
  {
    label: "Photos",
    path: "/photos",
    icon: Images,
  },
  {
    label:'Organize',
    path:'/organization',
    icon: FolderTree,
  },
  {
    label: "People",
    path: "/people",
    icon: Users,
  },
  {
    label: "Timeline",
    path: "/timeline",
    icon: CalendarDays,
  },
  {
    label: "Places",
    path: "/places",
    icon: Map,
  },
  {
    label: "AI Agent",
    path: "/agent",
    icon: Bot,
  },
  {
  label: "Duplicates",
  path: "/duplicates",
  icon: Copy,
}
];

export default function Sidebar({ onNavigate }) {
  return (
    <motion.aside
      className="sidebar"
      initial={{ x: -30, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.35 }}
    >
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Sparkles size={20} />
        </div>

        <div>
          <div className="sidebar-title">PhotoAgent</div>
          <div className="sidebar-subtitle">Local AI photo manager</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-title">Library</div>

        {navigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            onClick={onNavigate}
            to={path}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <Icon size={19} strokeWidth={1.8} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <button className="sidebar-link sidebar-settings">
          <Settings size={19} strokeWidth={1.8} />
          <span>Settings</span>
        </button>

        <div className="privacy-card">
          <div className="privacy-dot" />

          <div>
            <strong>Local & Private</strong>
            <span>Your photos stay on your SSD.</span>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}