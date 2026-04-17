from .io import load_frames
from .motion import compute_motion, compute_global_alignment
from .render import crop_jitter, render_panoramas
from .stabilize import stabilize_frames


def generate_panorama(input_frames_path, n_out_frames):
    frames = load_frames(input_frames_path)
    if not frames:
        return []

    h_orig, w_orig = frames[0].shape[:2]

    Ts = compute_motion(frames)
    abs_transforms = compute_global_alignment(Ts, len(frames))
    stabilized_frames, h_stab, y_offset = stabilize_frames(frames, abs_transforms)
    panoramas, canvas_w, slit_start, slit_range = render_panoramas(
        stabilized_frames, abs_transforms, h_stab, h_orig, y_offset, n_out_frames
    )
    final_panoramas = crop_jitter(
        panoramas, canvas_w, slit_start, slit_range, w_orig, n_out_frames
    )

    return final_panoramas
