import streamlit as st
import numpy as np
import cv2
from PIL import Image

from src.utils.colors import get_color_for_label
from src.features.object_detection.model import load_yolo_model
from src.features.object_detection.inference import run_detection

def render_ui():
    st.subheader("Object Detection (YOLO)")

    st.slider(
        "confidence Threshold",
          min_value = 0.1,
          max_value = 1.0,
          step = 0.05,
          value = st.session_state.confidence_threshold,
          key = "confidence_threshold"      
    )

    uploaded_files = st.file_uploader(
        "Upload Image",
        type = ["jpg", "png", "jpeg"]
    )
    if not uploaded_files:
        return

    image = Image.open(uploaded_files).convert("RGB")
    image_np = np.array(image)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("Run Object Detection"):
        with st.spinner("Loading model..."):
            model = load_yolo_model()
            detection = run_detection(model, image_np, st.session_state.confidence_threshold)
        
        if not detection:
            st.warning("No objects detected.")
            return
        
        for det in detection:
            st.success(
                f"{det['label']} - Confidence: {det['confidence']:.2f}"
            )
        
        draw_img = image_np.copy()
        for det in detection:
            x1, y1, x2, y2 = det['box']
            label = det['label']
            conf = det['confidence']
            color = get_color_for_label(label)
            cv2.rectangle(draw_img, (x1, y1), (x2, y2), color, thickness=2)
            
            text = f"{label}: {conf:.2f}"

            (text_w, text_h), baseline = cv2.getTextSize(
                text, 
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1
            )

            cv2.rectangle(
                draw_img,
                (x1, y1 -text_h - 2),
                (x1 + text_w + 2, y1),
                color,
                -1
            )

            cv2.putText(
                draw_img,
                text,
                (x1 + 2, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 0),
                1
            )
        
        st.image(draw_img, caption="Detection Result", use_container_width=True)

