#!/usr/bin/env python3
#
# File:   generate_lut.py
# Brief:  Make 3D LUT for colour correction for stereo video
# Author: Lyndon Hill
# Date:   2026.07.01

import argparse
import logging
from pathlib import Path

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge
import numpy as np
import cv2
import colour

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def make_lut(input_dir, output_file):
  """
  Build a LUT

  Future: Consider working in other colour spaces

  Params
    input_dir:  rig directory holding subdirectories of left and right images
  """

  # Get sorted list of png or jpg images in input directory
  frames_list = []
  for left_image in sorted((input_dir / "left").glob("*.png")) + sorted((input_dir / "left").glob("*.jpg")):
    right_image = input_dir / "right" / left_image.name
    if right_image.exists():
      frames_list.append(left_image.name)
    else:
      LOG.warning(f"Right image {right_image} does not exist for left image {left_image}")

  LOG.info(f"Processing {len(frames_list)} frames from {input_dir}")

  # Table of matched RGB values for right to left images
  rgb_matches = []

  for frame in frames_list:
    left_filename = input_dir / "left" / frame
    right_filename = input_dir / "right" / frame

    # Read frames using OpenCV
    left_image = cv2.imread(left_filename)
    right_image = cv2.imread(right_filename)

    # Work in RGB
    left_image = cv2.cvtColor(left_image, cv2.COLOR_BGR2RGB)
    right_image = cv2.cvtColor(right_image, cv2.COLOR_BGR2RGB)

    # Downsample images
    left_image_downsampled = cv2.resize(left_image, (0, 0), fx=0.5, fy=0.5)
    right_image_downsampled = cv2.resize(right_image, (0, 0), fx=0.5, fy=0.5)

    # Detect features
    detector = cv2.SIFT_create()
    keypoints_left, descriptors_left = detector.detectAndCompute(left_image_downsampled, None)
    keypoints_right, descriptors_right = detector.detectAndCompute(right_image_downsampled, None)

    # Match descriptors using FLANN-based matcher
    index_params = dict(algorithm=1, trees=5)  # FLANN_INDEX
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    flann_matches = flann.knnMatch(descriptors_left, descriptors_right, k=2)

    LOG.info(f"Found {len(flann_matches)} matches for frame {frame}")

    # Reject moving objects and objects that have large disparities
    # (matches that are too different)
    good_matches = []
    for m, n in flann_matches:
      if m.distance < 0.7 * n.distance:
        good_matches.append(m)

    flann_matches = good_matches
    LOG.info(f"Filtered to {len(flann_matches)} good matches for frame {frame}")

    # Convert downsampled images to float RGB
    left_float = left_image_downsampled.astype(float) / 255.0
    right_float = right_image_downsampled.astype(float) / 255.0

    # Find match values and add to table
    for match in flann_matches:
      left_idx = match.queryIdx
      right_idx = match.trainIdx
      left_kp = keypoints_left[left_idx]
      right_kp = keypoints_right[right_idx]

      # Get pixel coordinates
      left_x, left_y = int(left_kp.pt[0]), int(left_kp.pt[1])
      right_x, right_y = int(right_kp.pt[0]), int(right_kp.pt[1])

      # Get RGB values
      left_rgb = left_float[left_y, left_x, :]
      right_rgb = right_float[right_y, right_x, :]

      # Do not use matched pixels that are saturated, shadows or clipped highlights
      if (np.all(left_rgb > 0.05) and np.all(left_rgb < 0.95) and
          np.all(right_rgb > 0.05) and np.all(right_rgb < 0.95)):
        rgb_matches.append((right_rgb, left_rgb))
        # ^ matches are added for right to left

  LOG.info(f"Total matched RGB values: {len(rgb_matches)}")
  LOG.info("Fitting polynomial model to matched RGB values")

  # Fit nonlinear model to matched RGB values
  poly = PolynomialFeatures(degree=2)
  poly_features = poly.fit_transform([m[0] for m in rgb_matches])

  model = Ridge(alpha=1e-4)
  model.fit(poly_features, [m[1] for m in rgb_matches])

  LOG.info("Generating LUT")

  # Build RGB cube
  N = 33
  grid = np.linspace(0,1,N)
  r,g,b = np.meshgrid(grid, grid, grid, indexing="ij")
  cube = np.stack([r,g,b], axis=-1).reshape(-1,3)

  # Evaluate model
  cube_poly = poly.transform(cube)
  mapped = model.predict(cube_poly)
  mapped = np.clip(mapped,0,1)

  # Convert to table for Colour module
  table = mapped.reshape(N,N,N,3)

  # Create the LUT and write to file
  lut = colour.LUT3D(table, name="Hero3+_to_Hero10")
  colour.write_LUT(lut, str(output_file))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='generate_lut',
                      description='Build a 3D LUT from stereo video frames')

  parser.add_argument("--rig", type=Path, help="Path to stereo images")
  parser.add_argument("--output", type=Path, help="Output LUT file (.cube)")

  args = parser.parse_args()
  make_lut(args.rig, args.output)
