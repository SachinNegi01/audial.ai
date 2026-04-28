from __future__ import annotations

from pathlib import Path
import threading
import time

import cv2
import streamlit as st
try:
    from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    VideoProcessorBase = object
    WebRtcMode = None
    webrtc_streamer = None

try:
    import av
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    av = None

from src.config import WEBRTC_ICE_SERVERS
from src.features.object_detection.inference import run_detection
from src.features.object_detection.knowledge import lookup_object_info
from src.features.object_detection.knowledge import is_filterable_label
from src.features.object_detection.model import load_yolo_model
from src.utils.colors import get_color_for_label


class LiveObjectDetectionProcessor(VideoProcessorBase):
    def __init__(self, model_path: str | None = None) -> None:
        self.model = load_yolo_model(model_path)
        self._lock = threading.Lock()
        self.confidence_threshold = 0.5
        self.latest_detections: list[dict[str, object]] = []
        self.latest_update = 0.0

    def set_confidence_threshold(self, value: float) -> None:
        with self._lock:
            self.confidence_threshold = float(value)

    def get_latest_detections(self) -> list[dict[str, object]]:
        with self._lock:
            return [dict(item) for item in self.latest_detections]

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        if av is None:
            raise RuntimeError(
                "PyAV is not installed. Install project requirements before using live detection."
            )

        image = frame.to_ndarray(format="bgr24")
        with self._lock:
            threshold = float(self.confidence_threshold)

        detections = run_detection(self.model, image, threshold)
        visible_detections = [
            det for det in detections if not is_filterable_label(str(det["label"]))
        ]

        annotated = image.copy()
        for det in visible_detections:
            x1, y1, x2, y2 = det["box"]
            label = str(det["label"])
            confidence = float(det["confidence"])
            color = get_color_for_label(label)

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness=2)
            text = f"{label}: {confidence:.2f}"
            (text_w, text_h), _ = cv2.getTextSize(
                text,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                1,
            )
            label_top = max(0, y1 - text_h - 6)
            cv2.rectangle(
                annotated,
                (x1, label_top),
                (x1 + text_w + 8, y1),
                color,
                -1,
            )
            cv2.putText(
                annotated,
                text,
                (x1 + 4, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        with self._lock:
            self.latest_detections = visible_detections
            self.latest_update = time.time()

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")


def render_live_object_detection(model_path: str, stream_key: str) -> None:
    st.caption(
        "This live detector uses the browser camera while the meeting room stays open in the call area."
    )
    st.caption(f"Using model: `{Path(model_path).name}`")

    if av is None:
        st.error(
            "Live object detection needs PyAV (`av`). Install the updated requirements and restart the app."
        )
        st.caption("The rest of the meeting app can still run, but the live camera detector is disabled.")
        return

    if webrtc_streamer is None or WebRtcMode is None:
        st.error(
            "Live object detection needs `streamlit-webrtc`. Install the updated requirements and restart the app."
        )
        st.caption("The rest of the meeting app can still run, but the live camera detector is disabled.")
        return

    control_col, info_col = st.columns([1.15, 1.0])

    with control_col:
        confidence = st.slider(
            "Confidence threshold",
            min_value=0.1,
            max_value=1.0,
            step=0.05,
            value=float(st.session_state.confidence_threshold),
            key="confidence_threshold",
        )

        ctx = webrtc_streamer(
            key=stream_key,
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=lambda: LiveObjectDetectionProcessor(model_path),
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration={"iceServers": WEBRTC_ICE_SERVERS},
            async_processing=True,
        )

        if ctx.video_processor:
            ctx.video_processor.set_confidence_threshold(confidence)

        if not ctx.state.playing:
            st.info("Start the camera feed to detect objects in real time.")

    with info_col:
        info_placeholder = st.empty()
        if ctx.state.playing and ctx.video_processor:
            while ctx.state.playing:
                detections = ctx.video_processor.get_latest_detections()
                with info_placeholder.container():
                    _render_detection_panel(detections)
                time.sleep(0.25)
        else:
            with info_placeholder.container():
                st.markdown("#### Detected Object Info")
                st.write("Live object details will appear here after the camera starts.")
                st.caption(
                    "Only non-human and non-animal objects are used for the web lookup panel."
                )


def _render_detection_panel(detections: list[dict[str, object]]) -> None:
    st.markdown("#### Detected Object Info")

    if not detections:
        st.info("No eligible objects detected yet.")
        st.caption("The panel updates when the live camera sees a supported object.")
        return

    st.write(f"Active objects: {len(detections)}")

    displayed_labels: set[str] = set()
    for detection in detections[:3]:
        label = str(detection["label"])
        if label in displayed_labels:
            continue
        displayed_labels.add(label)

        confidence = float(detection["confidence"])
        context = lookup_object_info(label)

        with st.container(border=True):
            st.markdown(f"**{context['title']}**")
            st.caption(f"Confidence: {confidence:.2f}")
            st.write(context["summary"])
            if context.get("url"):
                st.markdown(f"[Open source link]({context['url']})")
