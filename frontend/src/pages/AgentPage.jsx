import { useState } from "react";
import { Bot } from "lucide-react";
import { motion } from "framer-motion";

import AgentChat from "../components/agent/AgentChat";
import PhotoViewer from "../components/photos/PhotoViewer";

export default function AgentPage() {
  const [selectedPhoto, setSelectedPhoto] =
    useState(null);

  return (
    <div className="agent-page">
      <section className="agent-hero">
        <motion.div
          className="agent-hero-icon"
          initial={{
            scale: 0.8,
            opacity: 0,
          }}
          animate={{
            scale: 1,
            opacity: 1,
          }}
        >
          <Bot size={28} />
        </motion.div>

        <div>
          <p className="eyebrow">
            PHOTOAGENT
          </p>

          <h1>Ask your photos.</h1>

          <p>
            Search your local photo library
            using natural language.
          </p>
        </div>
      </section>

      <AgentChat
        onPhotoClick={setSelectedPhoto}
      />

      {selectedPhoto && (
        <PhotoViewer
          photo={selectedPhoto}
          onClose={() =>
            setSelectedPhoto(null)
          }
        />
      )}
    </div>
  );
}