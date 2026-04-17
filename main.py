import argparse
import sys
from pathlib import Path

from stereo_mosaicing import generate_panorama


def main():
    parser = argparse.ArgumentParser(
        description="Generate pushbroom panoramas from a directory of video frames."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        metavar="DIR",
        help="Directory containing frame_XXXXX.jpg files",
    )
    parser.add_argument(
        "-o", "--output",
        default="output",
        metavar="DIR",
        help="Output directory for panorama JPGs (default: ./output)",
    )
    parser.add_argument(
        "-n", "--n-frames",
        type=int,
        default=1,
        metavar="N",
        help="Number of panorama views to generate (default: 1)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.is_dir():
        print(f"Error: input path '{input_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    panoramas = generate_panorama(str(input_dir), args.n_frames)

    if not panoramas:
        print("Error: no frames found in input directory.", file=sys.stderr)
        sys.exit(1)

    for idx, img in enumerate(panoramas):
        out_path = output_dir / f"panorama_{idx}.jpg"
        img.save(str(out_path))
        print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
