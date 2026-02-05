import numpy as np

def run_detection(model, image, confidence_threshold):
    results = model(image)[0]
    detection = []

    for box in results.boxes:
        score = float(box.conf[0])
        if score < confidence_threshold:
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