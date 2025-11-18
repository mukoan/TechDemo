#!/usr/bin/env python3
# File  : splg.py
# Date  : 2025.10.28
# Brief : Find features in images using SuperPoint and match between
#         consecutive images using LightGlue
# Author: Based on https://github.com/cvg/LightGlue/blob/main/demo.ipynb
#         Edited by Lyndon Hill
#
# Notes:
# Assumes LightGlue repository cloned at home directory of user "user".
# Input images should be in the specified directory and named
# frame_00001.png, frame_00002.png, etc
#
# Usage:
#  splg.py --images_dir <input image directory> --output_dir <output images directory>

import os
import sys
import argparse
from pathlib import Path
import torch
import cv2
import time
import matplotlib.pyplot as plt

sys.path.append("/home/user/LightGlue")
from lightglue import LightGlue, SuperPoint
from lightglue.utils import load_image, rbd
from lightglue import viz2d

# Measure time taken for feature detection and matching
measure_time = False

# Save keypoints only for current frame image (optional)
#  if false, save keypoints for pairs of frames
save_single_keypoints = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.set_grad_enabled(False)

def detect_and_match(image0_filename, image1_filename, matches_filename,
                     keypoints_filename):
  # SuperPoint+LightGlue
  extractor = SuperPoint(max_num_keypoints=2000).eval().to(device)
  matcher   = LightGlue(features='superpoint').eval().to(device)

  # Load each image as a torch.Tensor on GPU with shape (3,H,W), normalized in [0,1]
  image0 = load_image(image0_filename)
  image1 = load_image(image1_filename)

  # Start measuring time
  start_time = time.time()

  # Extract local features
  feats0 = extractor.extract(image0.to(device))
  feats1 = extractor.extract(image1.to(device))

  # Match the features
  matches01 = matcher({'image0': feats0, 'image1': feats1})
  feats0, feats1, matches01 = [
    rbd(x) for x in [feats0, feats1, matches01]
  ] # remove batch dimension

  if measure_time:
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

  kpts0, kpts1, matches = feats0["keypoints"], feats1["keypoints"], matches01["matches"]
  m_kpts0, m_kpts1 = kpts0[matches[..., 0]], kpts1[matches[..., 1]]

  # print(f"Matches {len(matches)}")

  axes = viz2d.plot_images([image0, image1], pad=0)
  viz2d.plot_matches(m_kpts0, m_kpts1, color="lime", lw=0.2)
  # viz2d.add_text(0, f'Stop after {matches01["stop"]} layers', fs=20)
  viz2d.save_plot(matches_filename)
  plt.close()

  kpc0, kpc1 = viz2d.cm_prune(matches01["prune0"]), viz2d.cm_prune(matches01["prune1"])
  viz2d.plot_images([image0, image1])
  viz2d.plot_keypoints([kpts0, kpts1], colors=[kpc0, kpc1], ps=10)
  viz2d.save_plot(keypoints_filename)
  plt.close()

  if save_single_keypoints:
    # Simply crop the output image to show current image keypoints only
    keypoints_img = cv2.imread(keypoints_filename)
    h,w = keypoints_img.shape[:2]
    crop_img = keypoints_img[0:h, int(w/2):w]
    cv2.imwrite(keypoints_filename, crop_img)

def main(images_path, output_path):
  if not os.listdir(images_path):
    print(f'No images found in {images_path}')
    return

  current_index = 2
  previous_index = 1

  while True:
    print(f'Processing frame {current_index:05d}...')
    current_image_path  = os.path.join(images_path,
                                       f'frame_{current_index:05d}.png')
    previous_image_path = os.path.join(images_path,
                                       f'frame_{previous_index:05d}.png')

    if not os.path.exists(current_image_path) or not os.path.exists(previous_image_path):
      break

    keypoints_output_path = os.path.join(output_path,
                                         f'keypoints_{current_index:05d}.png')
    matches_output_path   = os.path.join(output_path,
                                         f'matches_{current_index:05d}.png')

    detect_and_match(previous_image_path, current_image_path,
                     matches_output_path, keypoints_output_path)

    current_index += 1
    previous_index += 1

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='splg.py',
                      description='SuperPoint + LightGlue feature detection and matching')

  parser.add_argument("--images_dir", type=Path, required=True,
                      help="Directory to store extracted images")
  parser.add_argument("--output_dir", type=Path, required=True,
                      help="Directory to store output keypoint and matches images")

  args = parser.parse_args()

  main(args.images_dir, args.output_dir)
