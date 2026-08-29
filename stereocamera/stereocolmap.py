#!/usr/bin/env python3
#
# File  : stereocolmap.py
# Brief : Run COLMAP on calibrated stereo rig
# Author: Lyndon Hill
# Date  : 2026.06.16

"""
 Script to run COLMAP on a stereo rig
 Prerequisites:
 a. Make synchronised images
 b. Obtain intrinsic calibrations for both cameras and extrinsics as rig_config.json
    and copy extrinsics to project dir
 c. All calibrations are with the fisheye lens model

 Set up:
 1. mkdir project_dir
 2. mkdir -p project_dir/images/left
 3. mkdir -p project_dir/images/right
 4. Copy synchronised images to project_dir/images, left and right subdirs
 5. Check rig file has correct paths to images/cameras
"""

import os
import argparse
import logging
import subprocess
from pathlib import Path
import cv2

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def make_image_lists(project_dir):
  """
  Create lists of images to use in project

  Params
    project_dir:  path to the directory for the project
  """

  left_images = 0
  with open(str(project_dir / "left_list.txt"), "w") as outfile:
    for x in sorted(os.listdir(str(project_dir / "images/left"))):
      if x.endswith(".jpg") or x.endswith(".png"):
        outfile.write(f"images/left/{x}\n")
        left_images += 1

  right_images = 0
  with open(str(project_dir / "right_list.txt"), "w") as outfile:
    for x in sorted(os.listdir(str(project_dir / "images/right"))):
      if x.endswith(".jpg") or x.endswith(".png"):
        outfile.write(f"images/right/{x}\n")
        right_images += 1

  LOG.info(f"Found {left_images} left images, {right_images} right images")


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


def extract_features(project_dir, left_cal_path, right_cal_path):
  """
  Extract features from input images

  Params
    project_dir:  path to the project directory
    left_cal_path:  path to the left camera intrinsics
    right_cal_path:  path to the right camera intrinsics
  """

  # Load calibration intrinsics
  left_K, left_D = load_calibration(left_cal_path)
  right_K, right_D = load_calibration(right_cal_path)

  LOG.info("Extracting features...")

  left_lens_model = "OPENCV_FISHEYE"
  left_params = f"{left_K[0,0]},{left_K[1,1]},{left_K[0,2]},{left_K[1,2]},{left_D[0][0]},{left_D[1][0]},{left_D[2][0]},{left_D[3][0]}"

  cmd_left = [
    'colmap', 'feature_extractor',
    '--database_path', 'project.db',
    '--image_path', '.',
    '--image_list_path', 'left_list.txt',
    '--ImageReader.single_camera', '1',
    '--ImageReader.camera_model', left_lens_model,
    '--ImageReader.camera_params', left_params
  ]
  subprocess.run(cmd_left, cwd=str(project_dir), check=True)

  right_lens_model = "OPENCV_FISHEYE"
  right_params = f"{right_K[0,0]},{right_K[1,1]},{right_K[0,2]},{right_K[1,2]},{right_D[0][0]},{right_D[1][0]},{right_D[2][0]},{right_D[3][0]}"

  cmd_right = [
    'colmap', 'feature_extractor',
    '--database_path', 'project.db',
    '--image_path', '.',
    '--image_list_path', 'right_list.txt',
    '--ImageReader.single_camera', '1',
    '--ImageReader.camera_model', right_lens_model,
    '--ImageReader.camera_params', right_params
  ]
  subprocess.run(cmd_right, cwd=str(project_dir), check=True)


def configure_rig(project_dir):
  """
  Set up stereo rig - inform COLMAP about it

  Params
    project_dir:  path to the project directory
  """

  LOG.info("Configure rig...")
  cmd = [
      'colmap', 'rig_configurator',
      '--database_path', str(project_dir / 'project.db'),
      '--rig_config_path', str(project_dir / 'rig_config.json')
  ]
  subprocess.run(cmd, check=True)


def run_matching(project_dir):
  """
  Run feature matching (slow)

  Params
    project_dir:  path to the project directory
  """

  LOG.info("Matching features...")

  cmd = [
    'colmap', 'exhaustive_matcher',
    '--database_path', str(project_dir / 'project.db')
  ]
  subprocess.run(cmd, check=True)


def sparse_reconstruction(project_dir):
  """
  Build a sparse reconstruction, save it to a PLY file

  Params
    project_dir:  path to the project directory
  """

  # Create sparse directory here (if it doesn't exist)
  (project_dir/"sparse").mkdir(exist_ok=True)

  LOG.info("Sparse reconstruction...")
  cmd_mapper = [
    'colmap', 'mapper',
    '--database_path', 'project.db',
    '--image_path', '.',
    '--output_path', 'sparse',
    '--Mapper.ba_refine_focal_length', '0',
    '--Mapper.ba_refine_principal_point', '0',
    '--Mapper.ba_refine_extra_params', '0',
    '--Mapper.ba_refine_sensor_from_rig', '0'
  ]
  subprocess.run(cmd_mapper, cwd=str(project_dir), check=True)

  LOG.info("Exporting model...")
  cmd_convertor = [
    'colmap', 'model_converter',
    '--input_path', str(project_dir / "sparse/0"),
    '--output_path', str(project_dir / 'sparse.ply'),
    '--output_type', 'PLY'
  ]
  subprocess.run(cmd_convertor, check=True)


def run_sfm(project_dir, left_cal_path, right_cal_path):
  """
  Set up and run COLMAP
  """

  make_image_lists(project_dir)
  extract_features(project_dir, left_cal_path, right_cal_path)
  configure_rig(project_dir)
  run_matching(project_dir)
  sparse_reconstruction(project_dir)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run COLMAP on stereo images.")
  parser.add_argument("--project", type=Path, help="Path to project dir", required=True)
  parser.add_argument("--leftcal", type=Path, help="Path to left intrinsics file", required=True)
  parser.add_argument("--rightcal", type=Path, help="Path to right intrinsics file", required=True)

  args = parser.parse_args()

  # Check calibration files exist
  if not args.leftcal.exists():
    raise FileNotFoundError("Left calibration file not found")

  if not args.rightcal.exists():
    raise FileNotFoundError("Right calibration file not found")

  run_sfm(args.project, args.leftcal, args.rightcal)
