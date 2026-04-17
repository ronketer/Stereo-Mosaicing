from pathlib import Path

import cv2


def load_frames(input_path):
    files = sorted(
        Path(input_path).glob("frame_*.jpg"),
        key=lambda p: int(p.stem.split("_")[-1]),
    )
    frames = []
    for f in files:
        img = cv2.imread(str(f))
        if img is not None:
            frames.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return frames
