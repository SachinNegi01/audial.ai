import streamlit as st


def render_ui() -> None:
    st.subheader("Speech-to-Speech Translation")
    st.write(
        "This panel is where live translation settings live for each participant during the call."
    )

    left_col, right_col = st.columns(2)
    with left_col:
        st.selectbox(
            "Speaker language",
            ["Auto-detect", "English", "Hindi", "Spanish", "French", "German"],
        )
    with right_col:
        st.selectbox(
            "Listener output language",
            ["English", "Hindi", "Spanish", "French", "German", "Japanese"],
            index=0,
        )

    st.toggle("Translate incoming speech live", value=True)
    st.toggle("Play translated speech audio", value=True)
    st.toggle("Show bilingual captions", value=True)

    st.info(
        "Implementation path: microphone capture -> streaming ASR -> translation model -> "
        "TTS per listener -> return translated audio/captions through the call."
    )
