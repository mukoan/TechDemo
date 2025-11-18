#!/usr/bin/env python3
#
# File  : ocv-of-sequence.py
# Brief : Find the optical flow for a sequence of images, using OpenCV
# Author: Lyndon Hill
# Date  : 2025.10.01

import os
import subprocess
from subprocess import PIPE
import re
import argparse
from pathlib import Path


# Extract frames from video using ffmpeg
def extract_images_from_video(video_path, output_dir):
  command = [
      'ffmpeg',
      '-i', video_path,
      os.path.join(output_dir, 'frame_%05d.png')
  ]
  subprocess.run(command, check=True)


# Estimate optical flow estimation from consecutive image pairs
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

        command = [
            './ocv-of-single.py',
            '--current', current_image_path,
            '--previous', previous_image_path,
            '--output', flow_output_path
        ]
        subprocess.run(command, check=True)

        current_index += 1
        previous_index += 1


# Main function to run the process
def main(video_path, frames_dir, output_dir):
  print("Extracting images from video...")
  extract_images_from_video(video_path, frames_dir)

  print("Estimating optical flow...")
  estimate_optical_flow(frames_dir, output_dir)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='ocv-of-sequence',
                      description='Estimate optical Flow')

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
