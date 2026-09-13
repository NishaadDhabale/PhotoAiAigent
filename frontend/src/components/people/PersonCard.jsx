import { motion } from "framer-motion";
import { Camera, UserRound } from "lucide-react";
import { getPersonThumbnailUrl } from "../../api/photoApi";

export default function PersonCard({
  person,
  index,
  onClick,
}) {
  const isKnown = !person.name.startsWith("Person ");

  return (
    <motion.button
      type="button"
      className="person-card"
      onClick={onClick}
      initial={{
        opacity: 0,
        y: 16,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.3,
        delay: Math.min(index * 0.035, 0.35),
      }}
      whileHover={{
        y: -5,
      }}
      whileTap={{
        scale: 0.985,
      }}
    >
      <div className="person-card-image-wrap">
        {person.representative_photo_id ? (
          <img
            src={getPersonThumbnailUrl(person.group_id)}
            alt={person.name}
            className="person-card-image"
            loading="lazy"
          />
        ) : (
          <div className="person-card-placeholder">
            <UserRound size={36} />
          </div>
        )}

        <div className="person-card-badge">
          <Camera size={12} />
          {person.photo_count}
        </div>
      </div>

      <div className="person-card-info">
        <div className="person-card-name-row">
          <h3>{person.name}</h3>

          {isKnown && (
            <span className="known-badge">
              Known
            </span>
          )}
        </div>

        <p>
          {person.face_count}{" "}
          {person.face_count === 1 ? "appearance" : "appearances"}
        </p>
      </div>
    </motion.button>
  );
}