#!/usr/bin/env python3
"""Evaluate motion compensated video frames.
This script extracts frames from a video file, performs motion compensation
using block matching, and evaluates the quality of the reconstructed frames
against the original frames using PSNR.
"""

import os
import subprocess
from subprocess import PIPE
import cv2
import re


# Extract frames from video using ffmpeg
def extract_images_from_video(video_path, output_dir):
  command = [
      'ffmpeg',
      '-i', video_path,
      os.path.join(output_dir, 'frame_%05d.png')
  ]
  subprocess.run(command, check=True)

# Evaluate image quality
def evaluate_image_quality(image_path1, image_path2):
  # Use OpenCV to read images as greyscale
  img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
  img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

  if img1 is None or img2 is None:
    raise FileNotFoundError("One of the image files was not found or could not be opened.")

  # Calculate PSNR
  psnr_value = cv2.PSNR(img1, img2)

  return psnr_value

# Evaluate motion compensated video frames
def evaluate_memc(images_path, vectors_path, reconstruct_path, method, blocksize=16):
  # Loop over each consecutive image pair using number in filenames
  current_index = 2
  previous_index = 1
  time_taken_list = []
  psnr_list = []

  while True:
    print(f'Processing frame {current_index:05d}...')
    current_image_path = os.path.join(images_path, f'frame_{current_index:05d}.png')
    previous_image_path = os.path.join(images_path, f'frame_{previous_index:05d}.png')

    if not os.path.exists(current_image_path) or not os.path.exists(previous_image_path):
      break

    vectors_output_path = os.path.join(vectors_path, f'vectors_{current_index:05d}.mv')

    # Construct command to perform block matching
    command = [
        './bma',
        '-a', method,
        '-c', current_image_path,
        '-p', previous_image_path,
        '-v', vectors_output_path,
        '-b', str(blocksize),
        '-t'
    ]
    result = subprocess.run(command, stdout=PIPE, check=True)

    # Extract string matching "Time taken: xxxx microseconds" from result
    if result.returncode != 0:
      print(f"Block matching failed for frame {current_index:05d}.")
      break

    time_taken = int(re.search(r'Time taken: (\d+) microseconds', result.stdout.decode()).group(1))
    time_taken_list.append(time_taken)

    # Reconstruct current image using motion vectors
    reconstructed_image_path = os.path.join(reconstruct_path, f'reconstructed_{current_index:05d}.png')
    command = [
        './bmc',
        '-p', previous_image_path,
        '-v', vectors_output_path,
        '-o', reconstructed_image_path,
        '-b', str(blocksize)
    ]
    subprocess.run(command, check=True)

    # Evaluate quality between original current image and reconstructed image
    psnr = evaluate_image_quality(current_image_path, reconstructed_image_path)
    psnr_list.append(psnr)

    current_index += 1
    previous_index += 1

  # Save results to a CSV file
  with open('evaluation_results.csv', 'w') as f:
    f.write('FrameIndex,PSNR,TimeTakenMicroseconds\n')
    for i in range(len(psnr_list)):
      f.write(f'{i+2},{psnr_list[i]},{time_taken_list[i]}\n')
  print("Evaluation results saved to evaluation_results.csv")


# Main function to run the process
def main(video_path, frames_dir, vectors_dir, reconstruct_dir, method, blocksize=16):
  print("Extracting images from video...")
  extract_images_from_video(video_path, frames_dir)

  print("Evaluating motion estimation with motion compensation...")
  evaluate_memc(frames_dir, vectors_dir, reconstruct_dir, method, blocksize)


if __name__ == "__main__":
  # Get parameters
  video_path = 'PXL_20251009_091240731.TS.mp4'
  frames_dir = 'extracted_frames'
  mc_dir = 'mc_frames'
  vectors_dir = 'vectors'
  method = 'pmvfast'
  blocksize = 8

  # Check if video file exists
  if not os.path.exists(video_path):
    raise FileNotFoundError(f"Video file {video_path} not found.")

  # Make sure vectors directory exists (it is an output)
  if not os.path.exists(vectors_dir):
    os.makedirs(vectors_dir)

  # Make sure extracted images directory exists
  if not os.path.exists(frames_dir):
    os.makedirs(frames_dir)

  # Make sure extracted images directory exists
  if not os.path.exists(mc_dir):
    os.makedirs(mc_dir)

  main(video_path, frames_dir, vectors_dir, mc_dir, method, blocksize)
