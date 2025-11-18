#!/usr/bin/env python3
#
# File  : ocv-of-single.py
# Brief : Estimate optical flow between a single pair of images, using OpenCV
# Author: Lyndon Hill
# Date  : 2025.10.01

import cv2
import numpy as np
import argparse
from pathlib import Path
from flowimage import render_image, compensate_image


def compute_optical_flow(img2_filename, img1_filename, flowvis_filename):
  if img1_filename is None or img2_filename is None:
    raise FileNotFoundError("One or both images could not be loaded. Check the file paths.")

  # Load images
  img1 = cv2.imread(str(img1_filename))
  img2 = cv2.imread(str(img2_filename))

  # Convert to grayscale
  grey1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
  grey2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

  # Convert to float32
  f1 = np.float32(grey1)
  f2 = np.float32(grey2)

  # Calculate dense optical flow using Farnebäck method
  flow = cv2.calcOpticalFlowFarneback(
    f2, f1, None,
    pyr_scale=0.5,  # pyramid scale (<1 for finer scales)
    levels=3,       # number of pyramid levels
    winsize=15,     # averaging window size
    iterations=3,   # iterations at each pyramid level
    poly_n=5,       # size of the pixel neighborhood
    poly_sigma=1.2, # std dev for smoothing
    flags=0
  )

  # Render flow field and save
  flow_vis = render_image(flow)
  cv2.imwrite(flowvis_filename, flow_vis)

  """ Enable this code to generate optical flow compensated image
      using the previous image:
  # Compensate previous image using flow
  compensated_img = compensate_image(img1, flow)
  cv2.imwrite("compensated-ocv.png", compensated_img)
  """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='ocv-of-single',
                        description='Estimate optical Flow')

    parser.add_argument("--current", type=Path, help="Current image")
    parser.add_argument("--previous", type=Path, help="Previous image")
    parser.add_argument("--output", type=Path, help="Flow field image")

    args = parser.parse_args()
    compute_optical_flow(args.current, args.previous, args.output)
