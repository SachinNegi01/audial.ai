import streamlit as st
from ultralytics import YOLO

from src.config import resolve_yolo_model_path

@st.cache_resource
def load_yolo_model():
    return YOLO(resolve_yolo_model_path())
