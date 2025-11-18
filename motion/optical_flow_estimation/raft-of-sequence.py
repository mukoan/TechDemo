#!/usr/bin/env python3
#
# File  : raft-of-sequence.py
# Brief : Estimate optical flow using RAFT for a video sequence
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
from flowimage import render_image


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


def estimate_optical_flow(images_path, output_path):

  current_index = 2
  previous_index = 1

  while True:
    print(f'Processing frame {current_index:05d}...')
    current_image_path = os.path.join(images_path, f'frame_{current_index:05d}.png')
    previous_image_path = os.path.join(images_path, f'frame_{previous_index:05d}.png')

    if not os.path.exists(current_image_path) or not os.path.exists(previous_image_path):
      break

    flow_output_path = os.path.join(output_path, f'flow_{current_index:05d}.png')

    # Load a pair of images
    img1 = decode_image(previous_image_path)
    img2 = decode_image(current_image_path)

    img1, img2 = preprocess(img1, img2)
    img1 = img1.unsqueeze(0)  # (N, C, H, W)
    img2 = img2.unsqueeze(0)  # (N, C, H, W)

    list_of_flows = model(img1.to(device), img2.to(device))
    print(f"type = {type(list_of_flows)}")
    print(f"length = {len(list_of_flows)} = number of iterations of the model")

    predicted_flows = list_of_flows[-1]
    print(f"dtype = {predicted_flows.dtype}")
    print(f"shape = {predicted_flows.shape} = (N, 2, H, W)")
    print(f"min = {predicted_flows.min()}, max = {predicted_flows.max()}")

    # Visualise the predicted flow
    nflow = predicted_flows[0].permute(1, 2, 0).to("cpu").detach().numpy()
    flow_image = render_image(nflow)
    cv2.imwrite(flow_output_path, flow_image)

    current_index += 1
    previous_index += 1


def main(video_path, frames_dir, output_dir):
  print("Extracting images from video...")
  extract_images_from_video(video_path, frames_dir)

  print("Estimating optical flow...")
  estimate_optical_flow(frames_dir, output_dir)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='raft-of-sequence',
                      description='Estimate optical flow by RAFT')

  parser.add_argument("--video",  type=Path, required=True,
                      help="Input video")
  parser.add_argument("--images", type=Path, required=True,
                      help="Extracted images directory")
  parser.add_argument("--flow",   type=Path, required=True,
                      help="Flow visualisation images directory")

  args = parser.parse_args()

  # Check if video file exists
  if not os.path.exists(args.video):
    raise FileNotFoundError(f"Video file {args.video} not found.")

  # Make sure extracted images directory exists
  if not os.path.exists(args.images):
    os.makedirs(args.images)

  # Make sure flow images directory exists
  if not os.path.exists(args.flow):
    os.makedirs(args.flow)

  main(args.video, args.images, args.flow)
