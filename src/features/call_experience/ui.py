import json
import re

import streamlit as st
import streamlit.components.v1 as components

from src.config import APP_NAME, DEFAULT_PUBLIC_APP_URL, FEATURES, JITSI_DOMAIN
from src.features.object_detection.ui import render_ui as render_object_detection
from src.features.realtime_translation.ui import render_ui as render_translation
from src.features.sign_language.ui import render_ui as render_sign_language


def _normalize_room_id(room_id: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "-", room_id.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip("-_")
    return cleaned or "audial-room"


def _room_name(room_id: str) -> str:
    return f"audial-ai-{_normalize_room_id(room_id)}"


def _room_link(room_id: str) -> str:
    normalized_room = _normalize_room_id(room_id)
    if DEFAULT_PUBLIC_APP_URL:
        return f"{DEFAULT_PUBLIC_APP_URL}?room={normalized_room}"
    return f"?room={normalized_room}"


def _activate_room_from_query() -> None:
    query_room = st.query_params.get("room")
    if query_room:
        normalized_room = _normalize_room_id(str(query_room))
        if normalized_room != st.session_state.meeting_room_id:
            st.session_state.meeting_room_id = normalized_room


def _render_top_bar() -> None:
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### Call Room")
        st.write(
            "Participants can join the same room by link, and the live meeting runs inside the app "
            "through Jitsi's embedded conferencing API."
        )

    with right_col:
        st.metric("Room ID", st.session_state.meeting_room_id)
        st.caption(f"Join link: `{_room_link(st.session_state.meeting_room_id)}`")


def _render_lobby_controls() -> None:
    with st.container(border=True):
        st.markdown("#### Join Call")
        with st.form("join_call_form", border=False):
            room_col, name_col, lang_col = st.columns([1.2, 1, 1])

            with room_col:
                room_value = st.text_input(
                    "Room ID",
                    value=st.session_state.meeting_room_id,
                )

            with name_col:
                st.text_input("Display name", key="display_name")

            with lang_col:
                st.selectbox(
                    "Preferred language",
                    options=[
                        "English",
                        "Hindi",
                        "Spanish",
                        "French",
                        "German",
                        "Japanese",
                    ],
                    key="preferred_language",
                )

            settings_col, action_col, info_col = st.columns([1.3, 1, 2])
            with settings_col:
                st.toggle("Start muted", key="start_with_mic_muted")
                st.toggle("Start with camera off", key="start_with_camera_off")
            with action_col:
                submitted = st.form_submit_button("Join Room", use_container_width=True)
            with info_col:
                st.info(
                    "Share the room link with others. Everyone who opens the same `?room=` link joins "
                    "the same live video meeting."
                )

        if submitted:
            normalized_room = _normalize_room_id(room_value)
            st.session_state.meeting_room_id = normalized_room
            st.session_state.joined_call = True
            st.session_state.call_status = "Live"
            st.query_params["room"] = normalized_room


def _render_live_meeting() -> None:
    meeting_col, side_col = st.columns([3, 1.15])

    with meeting_col:
        with st.container(border=True):
            st.markdown("#### Live Meeting")
            if not st.session_state.joined_call:
                st.warning("Join the room to start the real-time audio and video call.")
            else:
                st.success(
                    f"Connected room: `{_room_name(st.session_state.meeting_room_id)}` on `{JITSI_DOMAIN}`"
                )
                _render_jitsi_meeting()

    with side_col:
        _render_call_sidebar()


def _render_jitsi_meeting() -> None:
    room_name = _room_name(st.session_state.meeting_room_id)
    display_name = st.session_state.display_name or "Guest"
    language = st.session_state.preferred_language
    start_muted = "true" if st.session_state.start_with_mic_muted else "false"
    start_video_muted = "true" if st.session_state.start_with_camera_off else "false"

    meeting_html = f"""
    <div id="jaas-container" style="width: 100%; min-height: 720px;"></div>
    <script src="https://{JITSI_DOMAIN}/external_api.js"></script>
    <script>
      const container = document.querySelector('#jaas-container');
      container.innerHTML = '';
      const domain = {json.dumps(JITSI_DOMAIN)};
      const options = {{
        roomName: {json.dumps(room_name)},
        parentNode: container,
        width: '100%',
        height: 720,
        lang: 'en',
        userInfo: {{
          displayName: {json.dumps(display_name)}
        }},
        configOverwrite: {{
          prejoinPageEnabled: false,
          startWithAudioMuted: {start_muted},
          startWithVideoMuted: {start_video_muted},
          disableModeratorIndicator: true
        }},
        interfaceConfigOverwrite: {{
          TILE_VIEW_MAX_COLUMNS: 2
        }}
      }};
      const api = new JitsiMeetExternalAPI(domain, options);
      window.jitsiApi = api;
    </script>
    """
    components.html(meeting_html, height=760)
    st.caption(
        f"Display name: `{display_name}` | Preferred language: `{language}` | "
        f"Share link: `{_room_link(st.session_state.meeting_room_id)}`"
    )


def _render_call_sidebar() -> None:
    with st.container(border=True):
        st.markdown("#### Call Details")
        st.write(f"Provider: `{JITSI_DOMAIN}`")
        st.write(f"Room name: `{_room_name(st.session_state.meeting_room_id)}`")
        st.write(f"Join URL: `{_room_link(st.session_state.meeting_room_id)}`")
        st.caption(
            "Camera, microphone, tile layout, screen share, and participant presence are managed "
            "inside the embedded meeting itself."
        )

    with st.container(border=True):
        st.markdown("#### AI Layer")
        st.write("The live call now works independently of the AI features.")
        st.write(
            "Object detection, translation, and sign-language assist remain separate app panels "
            "that we can connect to live media streams next."
        )
        st.info(
            "This is a practical architecture split: conferencing is real now, while the feature "
            "pipeline can evolve without rebuilding the call stack."
        )


def _render_active_feature() -> None:
    feature_name = st.session_state.get("active_feature") or next(iter(FEATURES))
    st.session_state.active_feature = feature_name
    feature_id = FEATURES[feature_name]["id"]

    with st.container(border=True):
        st.markdown(f"#### Active Feature: {feature_name}")
        st.caption(FEATURES[feature_name]["description"])

        if feature_id == "object_detection":
            render_object_detection()
        elif feature_id == "speech_translation":
            render_translation()
        elif feature_id == "sign_language":
            render_sign_language()


def _render_bottom_feature_dock() -> None:
    st.markdown("---")
    st.markdown("### Feature Dock")
    current_feature = st.session_state.get("active_feature") or next(iter(FEATURES))
    st.session_state.active_feature = current_feature
    st.segmented_control(
        "Choose the AI feature that should run for this call",
        options=list(FEATURES.keys()),
        key="active_feature",
        default=current_feature,
        selection_mode="single",
    )


def render_call_experience() -> None:
    _activate_room_from_query()
    _render_top_bar()
    _render_lobby_controls()
    _render_live_meeting()
    _render_active_feature()
    _render_bottom_feature_dock()

    st.caption(
        f"{APP_NAME} now uses an embedded conferencing backend for real multi-user calls. "
        "The next step is connecting the AI features to the live meeting streams."
    )
