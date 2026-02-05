import numpy as np
from src.config import CONFIDENCE_THRESHOLD

def run_detection(model, image):
    results = model(image)[0]
    detection = []

    for box in results.boxes:
        score = float(box.conf[0])
        if score < CONFIDENCE_THRESHOLD:
            continue
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        detection.append({
            "label": label,
            "confidence": score,
            "box": [x1, y1, x2, y2]
        })
    return detection