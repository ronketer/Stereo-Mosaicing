import cv2

from .config import MOSAIC_CONFIG


def stabilize_frames(frames, abs_transforms):
    h, w = frames[0].shape[:2]

    all_y = [T[1, 2] for T in abs_transforms]
    min_y, max_y = min(all_y), max(all_y)

    h_stab = int(h + (max_y - min_y) + MOSAIC_CONFIG["STAB_PADDING_H"])
    y_offset = -min_y + MOSAIC_CONFIG["STAB_OFFSET_Y"]

    stabilized = []
    for i, frame in enumerate(frames):
        M_global = abs_transforms[i]
        M_stab = M_global.copy()

        # Isolate Y-shift; zero out X-shift to preserve horizontal scanning motion
        M_stab[0, 2] = 0
        M_stab[1, 2] += y_offset

        stab_img = cv2.warpAffine(frame, M_stab[:2], (w, h_stab))
        stabilized.append(stab_img)

    return stabilized, h_stab, y_offset
