"""Enrollment — побудова бази облич з фото-папки (InsightFace ArcFace).

Структура входу:
    data/photos/<ім'я_людини>/*.jpg|jpeg|png

Вихід:
    data/db/face_db.npz  (names: list[str], embeddings: float32[N, 512] — нормовані)

Запуск:
    python program2_face_id/enroll.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

import config

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def largest_face(faces):
    """Обличчя з найбільшою площею bbox (на фото беремо головну особу)."""
    def area(f):
        x1, y1, x2, y2 = f.bbox
        return (x2 - x1) * (y2 - y1)
    return max(faces, key=area)


def main() -> None:
    parser = argparse.ArgumentParser(description="Побудова бази ембедингів облич.")
    parser.add_argument("--photos", default=str(config.PHOTOS_DIR), help="Тека з фото")
    parser.add_argument("--out", default=str(config.DB_PATH), help="Куди зберегти базу (.npz)")
    parser.add_argument("--det-size", type=int, default=640, help="Розмір входу детектора")
    args = parser.parse_args()

    photos_dir = Path(args.photos)
    if not photos_dir.exists():
        print(f"Немає теки {photos_dir}. Створіть її і покладіть підпапки на кожну людину.")
        return

    person_dirs = sorted(d for d in photos_dir.iterdir() if d.is_dir())
    if not person_dirs:
        print(f"У {photos_dir} немає підпапок. Очікую data/photos/<ім'я>/*.jpg")
        return

    # Імпорт тут, щоб помилка відсутнього пакета не заважала підказці вище
    from insightface.app import FaceAnalysis

    print("Ініціалізація InsightFace (buffalo_l) ...")
    app = FaceAnalysis(name=config.FACE_MODEL, providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=0, det_size=(args.det_size, args.det_size))

    names: list[str] = []
    embeddings: list[np.ndarray] = []
    for person_dir in person_dirs:
        imgs = [p for p in person_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
        if not imgs:
            print(f"  [пропуск] {person_dir.name}: немає зображень")
            continue

        vecs: list[np.ndarray] = []
        for img_path in sorted(imgs):
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"  [пропуск] не читається: {img_path.name}")
                continue
            faces = app.get(img)
            if not faces:
                print(f"  [пропуск] обличчя не знайдено: {img_path.name}")
                continue
            vecs.append(largest_face(faces).normed_embedding)

        if not vecs:
            print(f"  [пропуск] {person_dir.name}: жодного обличчя")
            continue

        mean = np.mean(vecs, axis=0)
        mean = mean / np.linalg.norm(mean)  # перенормування після усереднення
        names.append(person_dir.name)
        embeddings.append(mean.astype(np.float32))
        print(f"  [+] {person_dir.name}: {len(vecs)} фото")

    if not names:
        print("База порожня — жодного обличчя не зібрано.")
        return

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out_path, names=np.array(names), embeddings=np.array(embeddings, dtype=np.float32))
    print(f"\nЗбережено базу: {out_path}  ({len(names)} осіб)")


if __name__ == "__main__":
    main()
