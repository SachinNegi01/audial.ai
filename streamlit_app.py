import streamlit as st

from src.state import init_state
from src.config import FEATURES
from src.features.object_detection.ui import render_ui as render_object_detection

st.set_page_config(page_title="Audial.ai", layout="centered")
st.title("Welcome to Audial.ai")
init_state()

st.sidebar.header("Features")

st.sidebar.radio(
    "Select Features",
    options = list(FEATURES.keys()),
    key = 'active_features'
)

if st.session_state.active_features == "Object Detection":
    render_object_detection()
else:
    st.info("Feature coming soon")
