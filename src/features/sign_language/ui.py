import streamlit as st


def render_ui() -> None:
    st.subheader("Sign Language to Speech")
    st.write(
        "Use this feature when one participant communicates through signing and the others need "
        "speech or text output."
    )

    left_col, right_col = st.columns(2)
    with left_col:
        st.selectbox(
            "Input source",
            ["Primary camera", "Secondary camera", "Screen-shared video"],
        )
    with right_col:
        st.selectbox(
            "Output mode",
            ["Speech and captions", "Speech only", "Captions only"],
        )

    st.toggle("Detect signing continuously", value=True)
    st.toggle("Speak converted output for listeners", value=True)
    st.toggle("Show signer transcript in the call", value=True)

    st.info(
        "Implementation path: webcam frames -> hand/body landmark extraction -> sign recognition "
        "model -> sentence post-processing -> optional text-to-speech for listeners."
    )
