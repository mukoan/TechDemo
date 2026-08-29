#!/usr/bin/env python3
#
# File:   apply_lut.py
# Brief:  Use 3D LUT for colour correction of directory of images
# Author: Lyndon Hill
# Date:   2026.07.01

import argparse
import logging
from pathlib import Path

import cv2
import numpy as np
import colour

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def process_lut(input_image, lut):
  """
  Apply a LUT to an image using trilinear interpolation

  Params
    input_image:  the input image
    lut:  the look up table

  Return
    processed image
  """

  image_float = input_image.astype(np.float32) / 255.0
  return lut.apply(image_float)


def process_images(input_dir, lut_path, output_dir):
  """
  Process images

  Params
    input_dir:  input directory with image files
    lut_path:  path to the LUT file (.cube)
    output_dir:  output directory for processed files
  """

  if output_dir == input_dir:
    raise ValueError(f"Output directory cannot be same as input directory {str(input_dir)}")

  # Read LUT
  lut = colour.io.read_LUT(lut_path)

  # Process all files in input directory; work in RGB
  for filename in input_dir.iterdir():
    extension = filename.suffix.lower()
    if extension == ".jpg" or extension == ".png":
      LOG.info(f"Processing {filename}")
      # Load image
      input_img = cv2.imread(filename)
      input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB)

      # Process
      output_float = process_lut(input_img, lut)
      output_img = (np.clip(output_float, 0.0, 1.0) * 255.0).astype(np.uint8)
      output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)

      # Save
      image_file = Path(filename).name
      LOG.info(f"Writing {str(output_dir / image_file)}")
      cv2.imwrite(str(output_dir / image_file), output_img)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='correct_images',
                      description='Apply a 3D LUT to a directory of images')

  parser.add_argument("--input", type=Path, help="Input directory")
  parser.add_argument("--lut", type=Path, help="LUT cube file")
  parser.add_argument("--output", type=Path, help="Output directory")

  args = parser.parse_args()
  process_images(args.input, args.lut, args.output)
