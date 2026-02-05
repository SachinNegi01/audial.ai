import streamlit as st
import numpy as np
import cv2
from PIL import Image

from src.features.object_detection.model import load_yolo_model
from src.features.object_detection.inference import run_detection

def render_ui():
    st.subheader("Object Detection (YOLO)")
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
            detection = run_detection(model, image_np)
        
        if not detection:
            st.warning("No objects detected.")
            return
        
        for det in detection:
            st.success(
                f"{det['label']} - Confidence: {det['confidence']:.2f}"
            )
        
        dear_img = image_np.copy()
        for det in detection:
            x1, y1, x2, y2 = det['box']
            cv2.rectangle(dear_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                dear_img,
                det["label"],
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        st.image(dear_img, caption="Detection Result", use_container_width=True)

