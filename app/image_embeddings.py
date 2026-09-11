from pathlib import Path

import numpy as np
import torch
import open_clip
from PIL import Image


class ImageEmbedder:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.model, _, self.preprocess = (
            open_clip.create_model_and_transforms(
                "MobileCLIP2-S0",
                pretrained="dfndr2b",
            )
        )

        self.tokenizer = open_clip.get_tokenizer(
            "MobileCLIP2-S0"
        )

        self.model = self.model.to(self.device)
        self.model.eval()

    def embed_image(self, image_path):
        image_path = Path(image_path)

        image = Image.open(
            image_path
        ).convert("RGB")

        image_tensor = self.preprocess(
            image
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():
            embedding = self.model.encode_image(
                image_tensor
            )

        embedding = embedding / embedding.norm(
            dim=-1,
            keepdim=True,
        )

        return (
            embedding[0]
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    def embed_text(self, text):
        if not isinstance(text, str):
            raise TypeError(
                "Text must be a string"
            )

        if not text.strip():
            raise ValueError(
                "Text cannot be empty"
            )

        tokens = self.tokenizer(
            [text]
        ).to(self.device)

        with torch.no_grad():
            embedding = self.model.encode_text(
                tokens
            )

        embedding = embedding / embedding.norm(
            dim=-1,
            keepdim=True,
        )

        return (
            embedding[0]
            .cpu()
            .numpy()
            .astype(np.float32)
        )


def cosine_similarity(
    embedding_a,
    embedding_b,
):
    a = np.asarray(
        embedding_a,
        dtype=np.float32,
    )

    b = np.asarray(
        embedding_b,
        dtype=np.float32,
    )

    return float(
        np.dot(a, b)
        / (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )
    )