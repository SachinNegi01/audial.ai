from ultralytics import YOLO
from src.config import YOLO_MODEL_NAME
import streamlit as st

@st.cache_resource
def load_yolo_model():
    return YOLO(YOLO_MODEL_NAME)