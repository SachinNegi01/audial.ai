import streamlit as st
from src.config import CONFIDENCE_THRESHOLD

def init_state():
    if "confidence_threshold" not in st.session_state:
        st.session_state.confidence_threshold = CONFIDENCE_THRESHOLD