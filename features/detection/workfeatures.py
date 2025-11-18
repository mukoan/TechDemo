#!/usr/bin/env python3
"""Find keypoints for all images in sequence and finding consecutive matched
points between images
"""

import os
import subprocess
import argparse
from pathlib import Path


# Extract frames from video using ffmpeg
def extract_images_from_video(video_path, output_dir):
  print("Extracting frames from video...")
  command = [
      'ffmpeg',
      '-i', video_path,
      os.path.join(output_dir, 'frame_%05d.png')
  ]
  subprocess.run(command, check=True)

# Detect features and matches
def process(video_path, images_path, output_path, method):
  # Check if there are images in images_path
  if not os.listdir(images_path):
    extract_images_from_video(video_path, images_path)

  # Loop over each consecutive image pair using number in filenames
  current_index = 2
  previous_index = 1

  while True:
    print(f'Processing frame {current_index:05d}...')
    current_image_path = os.path.join(images_path, f'frame_{current_index:05d}.png')
    previous_image_path = os.path.join(images_path, f'frame_{previous_index:05d}.png')

    if not os.path.exists(current_image_path) or not os.path.exists(previous_image_path):
      break

    keypoints_output_path = os.path.join(output_path, f'keypoints_{current_index:05d}.png')
    matches_output_path = os.path.join(output_path, f'matches_{current_index:05d}.png')

    # Construct command to perform block matching
    command = [
        './detect-match',
        '-a', method,
        '-c', current_image_path,
        '-p', previous_image_path,
        '-k', keypoints_output_path,
        '-m', matches_output_path,
        '-a', method
    ]
    subprocess.run(command, check=True)

    current_index += 1
    previous_index += 1

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='workfeatures.py',
                      description='Evaluate feature detection and matching')

  parser.add_argument("--video", type=Path, help="Input video")
  parser.add_argument("--images_dir", type=Path, help="Directory to store extracted images")
  parser.add_argument("--output_dir", type=Path, help="Directory to store output keypont and matches images")
  parser.add_argument("--method", type=str, default="sift", help="Feature detection method")

  args = parser.parse_args()

  video_path = args.video
  images_dir = args.images_dir
  output_dir = args.output_dir
  method = args.method

  # Check if video file exists
  if not os.path.exists(video_path):
    raise FileNotFoundError(f"Video file {video_path} not found.")

  # Make sure images directory exists
  if not os.path.exists(images_dir):
    os.makedirs(images_dir)

  # Make sure output directory exists
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  process(video_path, images_dir, output_dir, method)
