import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

const EXAMPLES = [
  "Show me photos of Nisha",
  "Find my beach photos",
  "Show me photos from 2022",
  "Find photos of Nisha from 2022",
];

export default function ExamplePrompts({
  onSelect,
}) {
  return (
    <motion.section
      className="agent-examples"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="agent-examples-heading">
        <Sparkles size={17} />
        <span>Try asking</span>
      </div>

      <div className="agent-example-grid">
        {EXAMPLES.map((example) => (
          <motion.button
            key={example}
            type="button"
            className="agent-example-card"
            onClick={() => onSelect(example)}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            {example}
          </motion.button>
        ))}
      </div>
    </motion.section>
  );
}