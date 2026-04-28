import streamlit as st
from ultralytics import YOLO

from src.config import YOLO_MODEL_CANDIDATES, resolve_yolo_model_path

@st.cache_resource
def load_yolo_model(model_path: str | None = None):
    resolved_model_path = model_path or resolve_yolo_model_path()
    return YOLO(resolved_model_path)


def list_available_yolo_models() -> list[str]:
    return [str(candidate) for candidate in YOLO_MODEL_CANDIDATES if candidate.exists()]
