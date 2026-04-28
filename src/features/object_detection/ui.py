from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.features.object_detection.inference import cached_detection
from src.features.object_detection.knowledge import is_filterable_label
from src.features.object_detection.live import render_live_object_detection
from src.features.object_detection.model import list_available_yolo_models
from src.features.object_detection.model import load_yolo_model
from src.utils.colors import get_color_for_label
from src.utils.image_hash import hash_image


def render_ui() -> None:
    st.subheader("Object Detection")
    st.write(
        "This feature now runs on a live browser camera feed while the meeting is active. "
        "The side panel shows short web summaries for detected objects."
    )

    model_options = list_available_yolo_models()
    if not model_options:
        st.error("No YOLO model files were found in the models folder.")
        return

    default_model = next(
        (path for path in model_options if path.endswith("custom_yolo.pt")),
        model_options[0],
    )
    selected_model_path = st.selectbox(
        "YOLO model",
        options=model_options,
        index=model_options.index(default_model),
        format_func=lambda path: Path(path).name,
        key="selected_yolo_model",
    )
    stream_key = f"live-object-detection-{Path(selected_model_path).stem}"

    live_tab, image_tab = st.tabs(["Live camera", "Image test"])

    with live_tab:
        render_live_object_detection(selected_model_path, stream_key)

    with image_tab:
        _render_image_detection(selected_model_path)


def _render_image_detection(selected_model_path: str) -> None:
    st.caption("Use this section to test the same model on a single uploaded image.")

    confidence = st.slider(
        "Confidence threshold",
        min_value=0.1,
        max_value=1.0,
        step=0.05,
        value=float(st.session_state.confidence_threshold),
        key="image_confidence_threshold",
    )

    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["jpg", "png", "jpeg"],
        key="object_detection_upload",
    )
    if not uploaded_file:
        return

    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Run Object Detection on Image", key="run_image_object_detection"):
        with st.spinner("Loading model and running detection..."):
            model = load_yolo_model(selected_model_path)
            image_hash = hash_image(image_np)
            detections = cached_detection(
                image_hash,
                confidence,
                image_np,
                model,
            )

        _render_image_results(image_np, detections)


def _render_image_results(image_np: np.ndarray, detections: list[dict[str, object]]) -> None:
    filtered_detections = [
        det for det in detections if not is_filterable_label(str(det["label"]))
    ]

    if not filtered_detections:
        st.warning("No eligible objects detected.")
        return

    for det in filtered_detections:
        st.success(f"{det['label']} - Confidence: {float(det['confidence']):.2f}")

    draw_img = image_np.copy()
    for det in filtered_detections:
        x1, y1, x2, y2 = det["box"]
        label = str(det["label"])
        confidence = float(det["confidence"])
        color = get_color_for_label(label)
        cv2.rectangle(draw_img, (x1, y1), (x2, y2), color, thickness=2)

        text = f"{label}: {confidence:.2f}"
        (text_w, text_h), _ = cv2.getTextSize(
            text,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            1,
        )
        cv2.rectangle(
            draw_img,
            (x1, max(0, y1 - text_h - 6)),
            (x1 + text_w + 8, y1),
            color,
            -1,
        )
        cv2.putText(
            draw_img,
            text,
            (x1 + 4, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    st.image(draw_img, caption="Detection Result", use_container_width=True)
