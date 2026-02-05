import streamlit as st
from src.features.object_detection.ui import render_ui

st.set_page_config(page_title="Audial.ai", layout="centered")
st.title("Welcome to Audial.ai")

render_ui()