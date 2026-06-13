"""FaceIdentifier — детекція та ідентифікація облич (InsightFace ArcFace) проти бази."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class FaceResult:
    xyxy: tuple
    name: str
    score: float


class FaceIdentifier:
    """Завантажує базу ембедингів і матчить обличчя з кадру по косинусній схожості."""

    def __init__(self, db_path, model_name: str = "buffalo_l",
                 threshold: float = 0.35, det_size: int = 640) -> None:
        from insightface.app import FaceAnalysis

        data = np.load(Path(db_path), allow_pickle=True)
        self.names = list(data["names"])
        self.embs = data["embeddings"].astype(np.float32)
        self.threshold = threshold

        self.app = FaceAnalysis(name=model_name, providers=["CPUExecutionProvider"])
        self.app.prepare(ctx_id=0, det_size=(det_size, det_size))

    @property
    def size(self) -> int:
        return len(self.names)

    def identify(self, frame) -> list[FaceResult]:
        results: list[FaceResult] = []
        for face in self.app.get(frame):
            name, score = self._match(face.normed_embedding)
            x1, y1, x2, y2 = (float(v) for v in face.bbox)
            results.append(FaceResult((x1, y1, x2, y2), name, score))
        return results

    def _match(self, embedding) -> tuple[str, float]:
        if not self.names:
            return "Unknown", 0.0
        sims = self.embs @ embedding  # вектори нормовані → dot == cosine
        idx = int(np.argmax(sims))
        score = float(sims[idx])
        return (self.names[idx], score) if score >= self.threshold else ("Unknown", score)
