import streamlit as st

from src.config import APP_NAME, FEATURES
from src.features.object_detection.ui import render_ui as render_object_detection
from src.features.realtime_translation.ui import render_ui as render_translation
from src.features.sign_language.ui import render_ui as render_sign_language


def _room_link(room_id: str) -> str:
    return f"https://audial.local/call/{room_id}"


def _activate_room_from_query() -> None:
    query_room = st.query_params.get("room")
    if query_room and query_room != st.session_state.meeting_room_id:
        st.session_state.meeting_room_id = str(query_room)


def _render_top_bar() -> None:
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### Call Room")
        st.write(
            "This Streamlit version now behaves like a conferencing workspace: "
            "participants join with a room link and can enable live AI features during the call."
        )

    with right_col:
        st.metric("Room ID", st.session_state.meeting_room_id)
        st.caption(f"Join link: `{_room_link(st.session_state.meeting_room_id)}`")


def _render_lobby_controls() -> None:
    with st.container(border=True):
        st.markdown("#### Join Call")
        name_col, lang_col = st.columns(2)

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

        action_col, info_col = st.columns([1, 2])
        with action_col:
            if st.button("Join Room", use_container_width=True):
                st.session_state.joined_call = True
                st.session_state.call_status = "Live"
        with info_col:
            st.info(
                "Share the room link with others. For actual multi-user media streaming, "
                "the next backend step is WebRTC signaling plus STUN/TURN."
            )


def _render_video_stage() -> None:
    local_name = st.session_state.display_name or "Host"
    language = st.session_state.preferred_language
    participants = [
        {
            "name": local_name,
            "status": "Camera preview ready",
            "meta": f"Preferred language: {language}",
        },
        {
            "name": "Remote participant",
            "status": "Waiting for join link connection",
            "meta": "When you add WebRTC, remote audio/video will appear here.",
        },
    ]

    video_col, side_col = st.columns([3, 1.25])

    with video_col:
        with st.container(border=True):
            st.markdown("#### Live Stage")
            if st.session_state.joined_call:
                st.success("You are in the room. Feature outputs appear below the stage.")
            else:
                st.warning("You are in the lobby. Join the room to start the AI-assisted call.")

            stage_cols = st.columns(2)
            for index, participant in enumerate(participants):
                with stage_cols[index]:
                    with st.container(border=True):
                        st.markdown(f"**{participant['name']}**")
                        st.caption(participant["status"])
                        st.write(participant["meta"])
                        st.progress(100 if index == 0 else 20)

    with side_col:
        with st.container(border=True):
            st.markdown("#### Call Controls")
            mute = st.toggle("Mute microphone", value=False)
            camera = st.toggle("Camera on", value=True)
            captions = st.toggle("Live captions", value=True)

            st.caption(
                f"Mic: {'Muted' if mute else 'Live'} | "
                f"Camera: {'On' if camera else 'Off'} | "
                f"Captions: {'Enabled' if captions else 'Disabled'}"
            )
            st.caption("Bottom dock controls which AI feature is active in the call.")


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
    _render_video_stage()
    _render_active_feature()
    _render_bottom_feature_dock()

    st.caption(
        f"{APP_NAME} is now structured like a meeting room. The current build handles UI flow, "
        "feature orchestration, and room-link UX; true live calling will come from a realtime backend."
    )
