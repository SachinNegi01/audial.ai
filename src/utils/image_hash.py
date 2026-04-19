import hashlib
import numpy as np

def hash_image(image_np: np.ndarray) -> str:
    return hashlib.md5(image_np.tobytes()).hexdigest()