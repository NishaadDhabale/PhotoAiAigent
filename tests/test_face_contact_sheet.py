from pathlib import Path

import cv2
import matplotlib.pyplot as plt

from app.face_detection import detect_faces


PHOTO_FOLDER = Path(r"D:\project\PhotoAgent\Images")


def main():
    face_crops = []

    for photo_path in PHOTO_FOLDER.iterdir():
        if photo_path.suffix.lower() not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:
            continue

        image = cv2.imread(str(photo_path))

        if image is None:
            continue

        faces = detect_faces(photo_path)

        for index, face in enumerate(faces, start=1):
            x, y, width, height = face["box"]

            crop = image[
                y:y + height,
                x:x + width,
            ]

            if crop.size == 0:
                continue

            crop = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2RGB,
            )

            face_crops.append(
                (
                    crop,
                    f"{photo_path.name}\nface {index}",
                )
            )

    columns = 5
    rows = (len(face_crops) + columns - 1) // columns

    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(15, rows * 3),
    )

    axes = axes.flatten()

    for axis, (crop, label) in zip(
        axes,
        face_crops,
    ):
        axis.imshow(crop)
        axis.set_title(label, fontsize=8)
        axis.axis("off")

    for axis in axes[len(face_crops):]:
        axis.axis("off")

    plt.tight_layout()

    output_path = PHOTO_FOLDER / "face_contact_sheet.jpg"

    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
    )

    print(f"Faces included: {len(face_crops)}")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()