import streamlit as st

from src.config import APP_NAME, APP_TAGLINE
from src.features.call_experience.ui import render_call_experience
from src.state import init_state

st.set_page_config(page_title=APP_NAME, layout="wide")
init_state()

st.title(APP_NAME)
st.caption(APP_TAGLINE)

render_call_experience()
