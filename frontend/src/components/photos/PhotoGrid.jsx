import { motion } from "framer-motion";
import PhotoCard from "./PhotoCard";
import { getPhotoImageUrl } from "../../api/photoApi";

export default function PhotoGrid({ photos, onPhotoClick }) {
  return (
    <motion.div
      className="photo-grid"
      layout
      initial="hidden"
      animate="visible"
    >
      {photos.map((photo, index) => (
        <PhotoCard
          key={photo.id}
          photo={photo}
          imageUrl={getPhotoImageUrl(photo.id)}
          index={index}
          onClick={() => onPhotoClick(photo)}
        />
      ))}
    </motion.div>
  );
}