import os
from pathlib import Path

APP_NAME = "Audial.ai"
APP_TAGLINE = "Conference-ready accessibility features for live video calls."
CONFIDENCE_THRESHOLD = 0.5
DEFAULT_PUBLIC_APP_URL = os.getenv("PUBLIC_APP_URL", "").rstrip("/")
JITSI_DOMAIN = os.getenv("JITSI_DOMAIN", "meet.jit.si")
WEBRTC_ICE_SERVERS = [{"urls": ["stun:stun.l.google.com:19302"]}]

PROJECT_ROOT = Path(__file__).resolve().parent.parent

YOLO_MODEL_CANDIDATES = [
    PROJECT_ROOT / "models" / "yolo" / "custom_yolo.pt",
    PROJECT_ROOT / "src" / "models" / "yolo" / "custom_yolo.pt",
    PROJECT_ROOT / "src" / "models" / "yolo" / "yolov8n.pt",
    PROJECT_ROOT / "yolov8n.pt",
]

FEATURES = {
    "Object Detection": {
        "id": "object_detection",
        "description": "Highlight objects from the local participant's shared camera feed.",
    },
    "Speech Translation": {
        "id": "speech_translation",
        "description": "Translate speech in real time into each listener's preferred language.",
    },
    "Sign Language Assist": {
        "id": "sign_language",
        "description": "Convert detected signing into speech-ready text for other participants.",
    },
}


def resolve_yolo_model_path() -> str:
    for candidate in YOLO_MODEL_CANDIDATES:
        if candidate.exists():
            return str(candidate)
    return str(YOLO_MODEL_CANDIDATES[-1])
