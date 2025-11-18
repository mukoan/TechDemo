#!/usr/bin/env python3
#
# File : globalmc.py
# Brief: Global motion compensation
#
# Join together 2 overlapping images given the offset that aligns them.

import cv2
import numpy as np
import argparse
from pathlib import Path

def overlay_images(previous_path, current_path, x_offset, y_offset, show_box, output_path):
    # Read images
    previous = cv2.imread(previous_path, cv2.IMREAD_COLOR)
    current  = cv2.imread(current_path, cv2.IMREAD_UNCHANGED)

    if previous is None or current is None:
        raise ValueError("Error loading images. Check file paths.")

    # Ensure image has alpha channel
    if current.shape[2] == 3:
        current = cv2.cvtColor(current, cv2.COLOR_BGR2BGRA)

    bh, bw = previous.shape[:2]
    oh, ow = current.shape[:2]

    # Compute new canvas size
    min_x = min(0, np.floor(x_offset).astype(int))
    min_y = min(0, np.floor(y_offset).astype(int))
    max_x = max(bw, int(np.ceil(x_offset + ow)))
    max_y = max(bh, int(np.ceil(y_offset + oh)))

    new_w = max_x - min_x
    new_h = max_y - min_y

    # Create expanded canvas
    expanded = np.ones((new_h, new_w, 3), dtype=np.uint8) * 255

    # Place background
    bg_x = -min_x
    bg_y = -min_y
    expanded[bg_y:bg_y+bh, bg_x:bg_x+bw] = previous

    # Prepare affine translation matrix for overlay
    M = np.float32([[1, 0, x_offset - min_x],
                    [0, 1, y_offset - min_y]])

    # Warp current to expanded canvas size
    warped_current = cv2.warpAffine(
        current,
        M,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_TRANSPARENT
    )

    # Split overlay into RGB + alpha
    current_rgb = warped_current[:, :, :3]
    mask = warped_current[:, :, 3:] / 255.0

    # Blend
    expanded = (1.0 - mask) * expanded + mask * current_rgb
    expanded = expanded.astype(np.uint8)

    if show_box:
      # Draw box around background for visualisation
      cv2.rectangle(expanded, (bg_x, bg_y), (bg_x + bw - 1, bg_y + bh - 1), (0, 255, 255), 1)

    # Save result
    cv2.imwrite(output_path, expanded)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='globalmc',
                        description='Join images with given alignment')

    parser.add_argument("--previous", type=Path, help="Previous image")
    parser.add_argument("--current", type=Path, help="Current image")
    parser.add_argument("--xoff", type=float, help="x offset")
    parser.add_argument("--yoff", type=float, help="y offset")
    parser.add_argument("--outline", action=argparse.BooleanOptionalAction, help="Show box around previous image")
    parser.add_argument("--output", type=Path, help="Output image")

    args = parser.parse_args()
    overlay_images(args.previous, args.current, args.xoff, args.yoff, args.outline, args.output)
