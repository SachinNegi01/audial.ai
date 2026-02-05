import random

_COLOR_CACHE = {}

def get_color_for_label(label: str):

    if label not in _COLOR_CACHE:
        random.seed(hash(label) % 2**32)
        _COLOR_CACHE[label] = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )
    return _COLOR_CACHE[label]