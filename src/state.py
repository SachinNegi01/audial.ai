import streamlit as st
from src.config import CONFIDENCE_THRESHOLD, FEATURES

def init_state():
    if "active_feature" not in st.session_state:
        st.session_state.active_feature = list(FEATURES.keys())[0]
    
    if "confidence_threshold" not in st.session_state:
        st.session_state.confidence_threshold = CONFIDENCE_THRESHOLD