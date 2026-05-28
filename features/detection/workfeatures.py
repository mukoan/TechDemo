#!/usr/bin/env python3
#
# File:  workfeatures.py
# Brief: Run feature detection and matching on a video
#
# Find keypoints for all images in sequence and finding consecutive matched
# points between images. Creates output directories if they do not exist.

import os
import subprocess
import argparse
from pathlib import Path

def extract_images_from_video(video_path, output_dir):
  """
  Extract all frames from video using ffmpeg

  Params
    video_path:  path to the video file
    output_dir:  directory to write extracted frames to, as png images
  """

  print("Extracting frames from video...")
  command = [
      'ffmpeg',
      '-i', video_path,
      os.path.join(output_dir, 'frame_%05d.png')
  ]
  subprocess.run(command, check=True)


def process(video_path, images_path, output_path, method):
  """
  Detect features and matches

  Extract frames from video, detect features and matches using detect-match,
  writes annotated images.

  Params
    video_path:  path to input video
    images_path:  directory to write extracted frames
    output_path:  directory to write images with keypoints and matches
    method:  feature detector to use (SIFT, SURF, ORB; - see detect-match)
  """

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
