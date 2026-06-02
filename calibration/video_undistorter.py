#!/usr/bin/env python3
#
# File : video_undistorter.py
# Brief: Undistort video
#
# Applies lens correction and crops video to remove image borders.
# Do not use fisheye model during calibration.

import cv2
import argparse
import subprocess

def load_calibration(yaml_path):
  """
  Loads and parses calibration file for camera parameters

  Params
    yaml_path:  path to calibration file

  Return
    camera intrinsic matrix, distortion coefficients
  """

  fs = cv2.FileStorage(yaml_path, cv2.FILE_STORAGE_READ)
  camera_matrix = fs.getNode("camera_matrix").mat()
  dist_coeffs = fs.getNode("distortion_coefficients").mat()
  fs.release()

  if camera_matrix is None or dist_coeffs is None:
    raise IOError(f"Error: Could not find calibration data in {yaml_path}")

  return camera_matrix, dist_coeffs


def get_video_resolution(video_path):
  """
  Open input video and access properties

  Params
    video_path:  path to input video

  Return
    width and height of video
  """

  cap = cv2.VideoCapture(video_path)
  if not cap.isOpened():
    raise IOError(f"Error: Could not open video {video_path}")

  w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  cap.release()
  return w, h


def undistort_video(input_file, calibration_file, mode, output_file):
  """
  Uses calibration to process input video to created undistorted output video

  Params
    input_file:  path to input video
    calibration_file:  path to calibration file (intrinsics)
    mode:  either pad or scale final video to input video resolution
    output_file:  output filename
  """

  # Load calibration parameters
  cam_mtx, dist = load_calibration(calibration_file)
  width, height = get_video_resolution(input_file)

  # Extract distortion coefficients
  k1 = dist[0][0]
  k2 = dist[0][1]

  # Calculate relative centres for FFmpeg (0.5 is middle)
  cx = cam_mtx[0, 2] / width
  cy = cam_mtx[1, 2] / height

  # Calculate crop to remove black borders
  new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(cam_mtx, dist, (width, height), 0, (width, height))
  x, y, w_crop, h_crop = roi

  # Build FFmpeg filter string
  filter_chain = (
      f"lenscorrection=cx={cx}:cy={cy}:k1={k1}:k2={k2},"
      f"crop={w_crop}:{h_crop}:{x}:{y}"
  )

  if args.mode == 'scale':
    # Scale the cropped image back to original dimensions using bicubic interpolation
    filter_chain += f",scale={width}:{height}:flags=bicubic"
  else:
    # Pad back to original dimensions with black borders
    filter_chain += f",pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"

  # Compose FFmpeg command line options
  command = [
      "ffmpeg", "-y",
      "-i", input_file,
      "-vf", filter_chain,
      "-c:v", "libx264",
      "-crf", "18",
      "-preset", "slow",
      "-c:a", "copy",
      output_file
  ]

  try:
    subprocess.run(command, check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error running FFmpeg: {e}")
  except FileNotFoundError:
    print("Error: FFmpeg is not installed or not in your PATH.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Undistort video using FFmpeg.")
  parser.add_argument("--input", help="Path to input video file")
  parser.add_argument("--calibration", help="Path to calibration file")
  parser.add_argument("--output", help="Path for output video file")
  parser.add_argument("--mode", choices=['pad', 'scale'], default='pad',
                       help="pad with black borders or scale to fit original resolution.")

  args = parser.parse_args()

  undistort_video(args.input, args.calibration, args.mode, args.output)
