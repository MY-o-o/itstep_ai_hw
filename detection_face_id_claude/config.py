"""Спільна конфігурація для обох програм (дефолти CLI можна перевизначити)."""
from pathlib import Path

# --- Шляхи ---
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PHOTOS_DIR = DATA_DIR / "photos"          # вхід для enrollment: data/photos/<ім'я>/*.jpg
DB_DIR = DATA_DIR / "db"
DB_PATH = DB_DIR / "face_db.npz"          # згенерована база ембедингів
MODELS_DIR = ROOT / "models"
INCIDENTS_DIR = DATA_DIR / "incidents"    # скріншоти незнайомих осіб
REPORTS_DIR = DATA_DIR / "reports"        # звіти про порушення

# --- Камера ---
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# --- Детекція об'єктів (YOLO / COCO) ---
YOLO_MODEL = "yolo11n.pt"                 # nano — швидко на CPU; ваги тягнуться при 1-му запуску
YOLO_IMGSZ = 512                          # менший вхід → швидше (бокси все одно в координатах кадру)
CONF = 0.4                                # поріг впевненості детекції
PHONE_CLASS_ID = 67                       # COCO class 67 = "cell phone"

# --- Обличчя (InsightFace ArcFace) ---
FACE_MODEL = "buffalo_l"
FACE_THRESHOLD = 0.35                      # косинусна схожість: <поріг → "Unknown"
FACE_DET_SIZE = 480                        # менший детектор → більше FPS (для близьких облич достатньо)
FACE_EVERY = 3                            # важкий інференс кожні N кадрів (кеш між ними → плавність)

# --- Контроль порушень ---
INTRUSION_SECONDS = 1.0                    # незнайома особа довше за це → скріншот + запис у звіт
