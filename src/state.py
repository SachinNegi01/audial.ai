import secrets

import streamlit as st

from src.config import CONFIDENCE_THRESHOLD, FEATURES


def _generate_room_id() -> str:
    return secrets.token_urlsafe(6).lower()


def init_state() -> None:
    if "active_feature" not in st.session_state:
        st.session_state.active_feature = next(iter(FEATURES))

    if "confidence_threshold" not in st.session_state:
        st.session_state.confidence_threshold = CONFIDENCE_THRESHOLD

    if "meeting_room_id" not in st.session_state:
        st.session_state.meeting_room_id = _generate_room_id()

    if "display_name" not in st.session_state:
        st.session_state.display_name = "Host"

    if "preferred_language" not in st.session_state:
        st.session_state.preferred_language = "English"

    if "joined_call" not in st.session_state:
        st.session_state.joined_call = False

    if "call_status" not in st.session_state:
        st.session_state.call_status = "Lobby"

    if "start_with_mic_muted" not in st.session_state:
        st.session_state.start_with_mic_muted = False

    if "start_with_camera_off" not in st.session_state:
        st.session_state.start_with_camera_off = False
