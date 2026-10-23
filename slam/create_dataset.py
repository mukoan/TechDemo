#!/usr/bin/env python3
#
# File:   create_dataset.py
# Brief:  Create dataset for use with ORBSLAM 3
# Author: Lyndon Hill
# Date:   2026.09.24

import argparse
from pathlib import Path
import logging
import cv2
from typing import Tuple
from tqdm import tqdm

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def load_intrinsics(yaml_path: Path) -> Tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
    """
    Loads and parses calibration intrinsics for camera parameters

    Params
      yaml_path:  path to calibration file

    Return
      camera intrinsic matrix, distortion coefficients
    """

    fs = cv2.FileStorage(str(yaml_path), cv2.FILE_STORAGE_READ)
    camera_matrix = fs.getNode("camera_matrix").mat()
    dist_coeffs = fs.getNode("distortion_coefficients").mat()
    fs.release()

    if camera_matrix is None or dist_coeffs is None:
        raise IOError(f"Error: Could not find calibration data in {yaml_path}")

    return camera_matrix, dist_coeffs


def load_extrinsics(yaml_path: Path) -> Tuple[cv2.typing.MatLike, cv2.typing.MatLike]:
    """
    Loads and parses calibration extrinsics for camera parameters

    Params
      yaml_path:  path to calibration file

    Return
      rotation matrix, translation vector
    """

    fs = cv2.FileStorage(str(yaml_path), cv2.FILE_STORAGE_READ)
    rot = fs.getNode("R").mat()
    trans = fs.getNode("T").mat()
    fs.release()

    if rot is None or trans is None:
        raise IOError(f"Error: Could not find calibration data in {yaml_path}")

    return rot, trans


def process(input_path: Path, left_calibration: Path, right_calibration: Path,
            stereo_calibration: Path, scale: float, width: int, height: int,
            settings_path: Path, output_path: Path):
    """
    Main processing function

    Params
      input_path:  directory containing input image rig
      left_calibration:  left intrinsics file path
      right_calibration:  right intrinsics file path
      stereo_calibration:  extrinsics file path
      settings_path:  settings file path
      scale:  scale to use for rectification focal length to hide image border
      width:  input image width
      height:  input image height
      output_path:  directory to store output image rig
    """

    # Get sorted list of png or jpg images in input directory
    frames_list = []
    for left_image_filename in sorted(
            list((input_path / "left").glob("*.png")) +
            list((input_path / "left").glob("*.jpg"))
            ):
        right_image_filename = input_path / "right" / left_image_filename.name
        if right_image_filename.exists():
            frames_list.append(left_image_filename.name)
        else:
            LOG.warning(
                f"Right image {right_image_filename} does not exist for left image {left_image_filename}"
            )

    # Load calibrations
    K1, D1 = load_intrinsics(left_calibration)
    K2, D2 = load_intrinsics(right_calibration)
    R, T = load_extrinsics(stereo_calibration)

    # Create rectification mapping
    img_size = (width, height)

    # cv2.CALIB_ZERO_DISPARITY needed for ORBSLAM3
    R1, R2, P1, P2, Q = cv2.fisheye.stereoRectify(
        K1, D1, K2, D2, img_size, R, T, cv2.CALIB_ZERO_DISPARITY,
        fov_scale=scale
    )
    map11, map12 = cv2.fisheye.initUndistortRectifyMap(
        K1, D1, R1, P1, img_size, cv2.CV_16SC2
    )
    map21, map22 = cv2.fisheye.initUndistortRectifyMap(
        K2, D2, R2, P2, img_size, cv2.CV_16SC2
    )

    """
    Output settings file
    ORBSLAM3 YAML uses a period in label but OpenCV FileStorage does not
    support it so we write manually as it is fairly simple.
    """

    params = {
        "File.version": "1.0",
        "Camera.type": "Rectified",
        "Camera1.fx": float(P1[0,0]),
        "Camera1.fy": float(P1[1,1]),
        "Camera1.cx": float(P1[0,2]),
        "Camera1.cy": float(P1[1,2]),
        "Camera.width": int(width),
        "Camera.height": int(height),
        "Camera.fps": int(50),
        "Camera.RGB": 0,
        "Stereo.b": float(0.001*-P2[0,3]/P2[0,0]),
        "Stereo.ThDepth": 60.0,
        "ORBextractor.nFeatures": 2000,
        "ORBextractor.scaleFactor": 1.2,
        "ORBextractor.nLevels": 8,
        "ORBextractor.iniThFAST": 20,
        "ORBextractor.minThFAST": 7,
        "Viewer.KeyFrameSize": 0.05,
        "Viewer.KeyFrameLineWidth": 1.0,
        "Viewer.GraphLineWidth": 0.9,
        "Viewer.PointSize": 2.0,
        "Viewer.CameraSize": 0.08,
        "Viewer.CameraLineWidth": 3.0,
        "Viewer.ViewpointX": 0.0,
        "Viewer.ViewpointY": -0.7,
        "Viewer.ViewpointZ": -1.8,
        "Viewer.ViewpointF": 500.0,
    }

    with open(str(settings_path), "w") as f:
        f.write("%YAML:1.0\n\n")

        for key, value in params.items():
            if isinstance(value, str):
                f.write(f'{key}: "{value}"\n')
            else:
                f.write(f"{key}: {value}\n")

    # Initialise
    frame_number = 0
    timestamp = 0.0

    ts_file = open(str(output_path/"timestamps.txt"), "w")

    # Rectify images

    LOG.info(f"Processing {len(frames_list)} frames from {input_path}")

    for filename in tqdm(frames_list):
        left_filename = input_path / "left" / filename
        right_filename = input_path / "right" / filename

        left_img = cv2.imread(str(left_filename))
        right_img = cv2.imread(str(right_filename))

        if left_img is None:
            LOG.warning(f"Could not open image {left_filename}, skipping stereo pair")
            continue

        if right_img is None:
            LOG.warning(f"Could not open image {right_filename}, skipping stereo pair")
            continue

        left_img_rect = cv2.remap(
            left_img,
            map11,
            map12,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
        )
        right_img_rect = cv2.remap(
            right_img,
            map21,
            map22,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
        )

        cv2.imwrite(str(output_path/f"left/{frame_number:05d}.png"), left_img_rect)
        cv2.imwrite(str(output_path/f"right/{frame_number:05d}.png"), right_img_rect)

        ts_file.write(f"{frame_number:05d} {timestamp}\n")

        frame_number += 1
        timestamp += 0.02

    LOG.info("Wrote rectified frames")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                      prog='create_dataset',
                      description='Create a stereo dataset for ORBSLAM 3')

    parser.add_argument("--input", type=Path, help="Input rig directory")
    parser.add_argument("--leftcal", type=Path, help="Left intrinsics YAML file")
    parser.add_argument("--rightcal", type=Path, help="Right intrinsics YAML file")
    parser.add_argument("--extcal", type=Path, help="Extrinsics YAML file")
    parser.add_argument("--scale", type=float, default=0.9, help="Scale for rectification")
    parser.add_argument("--width", type=int, default=1920, help="Image width")
    parser.add_argument("--height", type=int, default=1080, help="Image height")
    parser.add_argument("--output", type=Path, help="Output directory")

    args = parser.parse_args()

    # Make sure output rig directory exists
    for folder in ["left", "right"]:
        (args.output / folder).mkdir(parents=True, exist_ok=True)

    settings_out = args.output / "settings.yaml"
    process(args.input, args.leftcal, args.rightcal, args.extcal, args.scale, args.width, args.height, settings_out, args.output)
