#!/usr/bin/env python3
#
# File  : raft-of-single.py
# Brief : Estimate optical flow between a single pair of frames, using RAFT
# Author: Lyndon Hill
# Date  : 2025.10.01
# Note  : Based on https://docs.pytorch.org/vision/main/auto_examples/others/plot_optical_flow.html

import numpy as np
import torch
import torchvision.transforms.functional as F
from torchvision.models.optical_flow import Raft_Large_Weights
from torchvision.models.optical_flow import raft_large
from torchvision.utils import flow_to_image
from torchvision.io import decode_image, write_png
import os
import subprocess
import argparse
from pathlib import Path
import cv2
from flowimage import render_image, compensate_image


# If you can, run this example on a GPU, it will be a lot faster.
device = "cuda" if torch.cuda.is_available() else "cpu"

# Set up
weights = Raft_Large_Weights.DEFAULT
transforms = weights.transforms()
model = raft_large(weights=Raft_Large_Weights.DEFAULT, progress=False).to(device)
model = model.eval()


# Extract frames from video using ffmpeg
def extract_images_from_video(video_path, output_dir):
  command = [
      'ffmpeg',
      '-i', video_path,
      os.path.join(output_dir, 'frame_%05d.png')
  ]
  subprocess.run(command, check=True)


def preprocess(img1_batch, img2_batch):
  img1_batch = F.resize(img1_batch, size=[520, 960], antialias=False)
  img2_batch = F.resize(img2_batch, size=[520, 960], antialias=False)
  return transforms(img1_batch, img2_batch)


def estimate_optical_flow(current_path, previous_path, output_path):

  if not os.path.exists(current_path) or not os.path.exists(previous_path):
    raise FileNotFoundError("One or both images could not be loaded. Check the file paths.")

  # Load a pair of images
  img1 = decode_image(previous_path)
  img2 = decode_image(current_path)

  img1, img2 = preprocess(img1, img2)
  img1 = img1.unsqueeze(0)  # (N, C, H, W)
  img2 = img2.unsqueeze(0)  # (N, C, H, W)

  # Predict the flow
  list_of_flows = model(img1.to(device), img2.to(device))
  predicted_flows = list_of_flows[-1]

  # Visualise the predicted flow
  nflow = predicted_flows[0].permute(1, 2, 0).to("cpu").detach().numpy()
  flow_image = render_image(nflow)
  cv2.imwrite(output_path, flow_image)

  """ Enable this code to generate optical flow compensated image
      using the previous image:
  # Compensate previous image using flow

  numpy_image = np.transpose(img1[0].numpy(), (1, 2, 0))
  numpy_image = ((numpy_image + 1) / 2.0) * 255
  numpy_image = np.clip(numpy_image, 0, 255)
  numpy_image = numpy_image.astype(np.uint8)

  # Convert RGB to BGR for OpenCV
  numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

  compensated_img = compensate_image(numpy_image, nflow)
  cv2.imwrite("compensated-raft.png", compensated_img)
  """

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='raft-of-single',
                      description='Estimate optical flow by RAFT')

  parser.add_argument("--current", type=Path, help="Current image")
  parser.add_argument("--previous", type=Path, help="Previous image")
  parser.add_argument("--output", type=Path, help="Flow field image")

  args = parser.parse_args()

  estimate_optical_flow(args.current, args.previous, args.output)
