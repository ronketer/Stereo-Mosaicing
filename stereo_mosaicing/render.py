import cv2
import numpy as np
from PIL import Image

from .config import MOSAIC_CONFIG


def render_panoramas(stabilized_frames, abs_transforms, h_stab, h_orig, y_offset, n_out):
    h_frame = h_orig
    w_frame = stabilized_frames[0].shape[1]

    all_tx = [T[0, 2] for T in abs_transforms]
    min_tx, max_tx = min(all_tx), max(all_tx)
    canvas_w = int(max_tx - min_tx + w_frame)
    offset_tx = -min_tx

    movements = [
        abs(abs_transforms[i][0, 2] - abs_transforms[i - 1][0, 2])
        for i in range(1, len(abs_transforms))
    ]
    max_move = max(movements) if movements else 10
    strip_w = int(max_move) + MOSAIC_CONFIG["STRIP_OVERLAP"]
    if strip_w % 2 != 0:
        strip_w += 1

    panoramas = []
    slit_start = w_frame * MOSAIC_CONFIG["SLIT_START_RATIO"]
    slit_range = w_frame * MOSAIC_CONFIG["SLIT_WIDTH_RATIO"]

    for p_idx in range(n_out):
        canvas = np.zeros((h_stab, canvas_w, 3), dtype=np.uint8)

        ratio = p_idx / (n_out - 1) if n_out > 1 else 0.5
        src_col = slit_start + ratio * slit_range

        for i in range(len(stabilized_frames)):
            tx = abs_transforms[i][0, 2]

            exact_dest_center = tx + offset_tx + src_col
            dest_cx_int = int(round(exact_dest_center))

            start_x = dest_cx_int - strip_w // 2
            end_x = start_x + strip_w

            src_cx_float = dest_cx_int - offset_tx - tx
            src_cy_float = h_stab / 2.0

            patch = cv2.getRectSubPix(
                stabilized_frames[i], (strip_w, h_stab), (src_cx_float, src_cy_float)
            )

            pad_left = -start_x if start_x < 0 else 0
            pad_right = end_x - canvas_w if end_x > canvas_w else 0

            final_start_x = max(0, start_x)
            final_end_x = min(canvas_w, end_x)

            if final_end_x <= final_start_x:
                continue

            valid_width = strip_w - pad_left - pad_right
            if valid_width <= 0:
                continue

            patch_cropped = patch[:, pad_left : strip_w - pad_right]

            if patch_cropped.dtype != np.uint8:
                patch_cropped = patch_cropped.astype(np.uint8)

            canvas[:, final_start_x:final_end_x] = patch_cropped

        crop_y = int(y_offset)
        crop_y = max(0, min(crop_y, h_stab - h_frame))
        result_img = canvas[crop_y : crop_y + h_frame, :]

        panoramas.append(Image.fromarray(result_img))

    return panoramas, canvas_w, slit_start, slit_range


def crop_jitter(panoramas, canvas_w, slit_start, slit_range, original_w, n_out):
    aligned_panoramas = []
    min_src = int(slit_start)
    max_src = int(slit_start + slit_range)
    shift_range = max_src - min_src

    final_width = canvas_w - shift_range

    for i, p in enumerate(panoramas):
        ratio = i / (n_out - 1) if n_out > 1 else 0.5
        current_src = int(slit_start + ratio * slit_range)

        crop_x = current_src - min_src

        img_np = np.array(p)
        h, w_img, c = img_np.shape

        start_col = crop_x
        end_col = start_col + final_width

        if end_col > w_img:
            diff = end_col - w_img
            start_col -= diff
            end_col -= diff

        if start_col < 0:
            start_col = 0
            end_col = final_width

        cropped = img_np[:, start_col:end_col, :]
        aligned_panoramas.append(Image.fromarray(cropped))

    return aligned_panoramas
