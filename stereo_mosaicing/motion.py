import cv2
import numpy as np

from .config import LK_PARAMS, MOSAIC_CONFIG, ST_PARAMS


def compute_motion(frames):
    Ts = []
    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
    h, w = prev_gray.shape

    mask = np.zeros_like(prev_gray)
    mask[10 : h - 10, 10 : w - 10] = 255

    p0 = cv2.goodFeaturesToTrack(prev_gray, mask=mask, **ST_PARAMS)

    for i in range(len(frames) - 1):
        curr_gray = cv2.cvtColor(frames[i + 1], cv2.COLOR_RGB2GRAY)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(
            prev_gray, curr_gray, p0, None, **LK_PARAMS
        )

        if p1 is not None and st is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]
        else:
            good_new, good_old = [], []

        T = np.eye(3, dtype=np.float64)
        if len(good_new) >= 4:
            dx = np.median(good_new[:, 0] - good_old[:, 0])
            dy = np.median(good_new[:, 1] - good_old[:, 1])
            T[0, 2] = dx
            T[1, 2] = dy

        Ts.append(T)
        prev_gray = curr_gray.copy()

        if len(good_new) < MOSAIC_CONFIG["MIN_TRACKING_POINTS"]:
            p0 = cv2.goodFeaturesToTrack(prev_gray, mask=mask, **ST_PARAMS)
        else:
            p0 = good_new.reshape(-1, 1, 2)

    return Ts


def compute_global_alignment(Ts, num_frames):
    ref_idx = num_frames // 2
    abs_transforms = [np.eye(3, dtype=np.float64)] * num_frames

    curr = np.eye(3, dtype=np.float64)
    for i in range(ref_idx - 1, -1, -1):
        curr = curr @ Ts[i]
        abs_transforms[i] = curr

    curr = np.eye(3, dtype=np.float64)
    for i in range(ref_idx, num_frames - 1):
        T_inv = np.linalg.inv(Ts[i])
        curr = curr @ T_inv
        abs_transforms[i + 1] = curr

    return abs_transforms
