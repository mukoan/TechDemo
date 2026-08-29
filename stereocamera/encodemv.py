#!/usr/bin/env python3

"""
Encode synced images as MV-HEVC.

Assumptions:
  Input frames are synced and 50 fps, output will be 25 fps
  Recording on left camera started first
"""


import os
import argparse
import logging
import subprocess
from pathlib import Path
import cv2
import numpy as np
import addsvboxes

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Global variables
bin_x265 = "x265_4.2/build/x265"
bin_mp4box = "gpac-26.02.0/bin/gcc/MP4Box"
bin_ffmpeg8 = "ffmpeg-8.1.2/ffmpeg"
ld_ffmpeg8 = "ffmpeg-8.1.2/libdir"
config_x265 = "mvhevc.cfg"


"""
Defaults
  fps:  change if you use a different frame rate - see assumptions
"""
fps = 25


def load_intrinsics(yaml_path):
  """
  Loads and parses calibration intrinsics for camera parameters

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


def load_extrinsics(yaml_path):
  """
  Loads and parses calibration extrinsics for camera parameters

  Params
    yaml_path:  path to calibration file

  Return
    rotation matrix, translation vector
  """

  fs = cv2.FileStorage(yaml_path, cv2.FILE_STORAGE_READ)
  rot = fs.getNode("R").mat()
  trans = fs.getNode("T").mat()
  fs.release()

  if rot is None or trans is None:
    raise IOError(f"Error: Could not find calibration data in {yaml_path}")

  return rot, trans


def make_streams(input_dir, left_intrinsics, right_intrinsics, extrinsics, scale):
  """
  Load all images from input_dir/left, rectify and output as raw YUV stream,
  load all images from input_dir/right, rectify and output as raw YUV stream.
  You can verify the streams using
    vlc --rawvid-fps 25 --rawvid-width 1920 --rawvid-height 1080 --rawvid-chroma I420 right_view.yuv

  Params
    input_dir:  directory containing image rig, with left and right subdirs
    left_intrinsics:  intrinsics file for left camera
    right_intrinsics:  intrinsics file for right camera
    extrinsics:  extrinsics filename
    scale:  amount of scale to crop border (value should be <= 1.0)
  """

  # Load intrinsics
  K1, D1 = load_intrinsics(left_intrinsics)
  K2, D2 = load_intrinsics(right_intrinsics)

  # Load extrinsics
  R, T = load_extrinsics(extrinsics)

  width, height = 1920, 1080
  img_size = (width, height)

  # Generate rectification mapping
  R1, R2, P1, P2, Q = cv2.fisheye.stereoRectify(K1, D1, K2, D2, img_size, R, T, 0, fov_scale=scale)
  map11, map12 = cv2.fisheye.initUndistortRectifyMap(K1, D1, R1, P1, img_size, cv2.CV_16SC2)
  map21, map22 = cv2.fisheye.initUndistortRectifyMap(K2, D2, R2, P2, img_size, cv2.CV_16SC2)

  # Open output videos

  command_left = [
    'ffmpeg',
    '-y', # Overwrite output file
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{width}x{height}',
    '-pix_fmt', 'bgr24',
    '-r', str(fps),
    '-i', '-', # Input from pipe
    '-pix_fmt', 'yuv420p',
    '-f', 'rawvideo',
    "left_view.yuv"
  ]

  proc_left = subprocess.Popen(command_left, stdin=subprocess.PIPE)

  command_right = [
    'ffmpeg',
    '-y', # Overwrite output file
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{width}x{height}',
    '-pix_fmt', 'bgr24',
    '-r', str(fps),
    '-i', '-', # Input from pipe
    '-pix_fmt', 'yuv420p',
    '-f', 'rawvideo',
    "right_view.yuv"
  ]

  proc_right = subprocess.Popen(command_right, stdin=subprocess.PIPE)

  # Find all images
  frames_list = []
  for left_image in sorted((input_dir / "left").glob("*.png")) + sorted((input_dir / "left").glob("*.jpg")):
    right_image = input_dir / "right" / left_image.name
    if right_image.exists():
      frames_list.append(left_image.name)

  # Downsample to half frame rate
  frames_list = frames_list[::2]

  # Process all images
  for frame in frames_list:
    left_filename = input_dir / "left" / frame
    right_filename = input_dir / "right" / frame

    left_img = cv2.imread(left_filename)
    right_img = cv2.imread(right_filename)

    left_img_rect = cv2.remap(left_img, map11, map12, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    right_img_rect = cv2.remap(right_img, map21, map22, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    proc_left.stdin.write(left_img_rect.tobytes())
    proc_right.stdin.write(right_img_rect.tobytes())


  # Clean up
  proc_left.stdin.close()
  proc_right.stdin.close()
  proc_left.wait()
  proc_right.wait()


def encode_video(output_file):
  """
  Encode video using x265 and mux video into container with timing data
  using MP4Box
  """

  cmd = [
          bin_x265,
          '--multiview-config', config_x265,
          '--fps', str(fps),
          '--input-res', '1920x1080',
          '--output', 'mvhevc_output.hevc',
          '--profile', 'main',
          '--colorprim', 'bt709',
          '--transfer', 'bt709',
          '--colormatrix', 'bt709' ]

  subprocess.run(cmd, check=True)

  cmd_fix = [
          bin_mp4box,
          '-add', f"mvhevc_output.hevc:fps={fps}:colr=nclx,bt709,bt709,bt709,off",
          '-new', str(output_file) ]

  subprocess.run(cmd_fix, check=True)


def mux_audio(original_audio, offset, output_filename):
  """
  Mux in audio from another video, with an offset for the audio,
  use previously encoded stereo video

  Params
    original_audio:  file containing audio to use in final video
    offset:  offset to audio (seconds)
    output_filename:  filename for final output video

  Note
    Uses ffmpeg "-shortest" option to trim video to end of audio
  """

  # Use ffmpeg libraries
  env_var = { "LD_LIBRARY_PATH": ld_ffmpeg8 }

  cmd = [
          bin_ffmpeg8,
          '-i', 'output-gpac.mp4',
          '-i', str(original_audio),
          '-filter:a', f"atrim=start={offset},asetpts=PTS-STARTPTS",
          '-map', '0:v',
          '-map', '1:a',
          '-c:v', 'copy',
          '-c:a', 'aac',
          '-tag:v', 'hvc1',
          '-shortest',
          str(output_filename) ]

  subprocess.run(cmd, env=env_var, check=True)


def clean_up():
  """
  Remove intermediate files
  """
  os.unlink("left_view.yuv")
  os.unlink("right_view.yuv")
  os.unlink("mvhevc_output.hevc")

  if os.path.isfile("output-gpac.mp4"):
    os.unlink("output-gpac.mp4")


def process(args):
  """
  Main processing

  Params
    args:  command line arguments
  """

  LOG.info("Rectifying images into intermediate video streams")
  make_streams(args.input, args.leftcal, args.rightcal,
               args.extcal, args.scale)


  intermediate_output = "output-gpac.mp4"
  if args.audio is None:
    intermediate_output = args.output

  LOG.info("Running video encoder")
  encode_video(intermediate_output)

  if args.audio is not None:
    LOG.info("Muxing audio with video")
    mux_audio(args.audio, args.offset, args.output)

  clean_up()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
                      prog='encodemv',
                      description='Encode MV-HEVC')

  parser.add_argument("--input", type=Path, help="Input rig directory")
  parser.add_argument("--audio", type=Path, help="Left input video, for audio")
  parser.add_argument("--leftcal", type=Path, help="Left intrinsics YAML file")
  parser.add_argument("--rightcal", type=Path, help="Right intrinsics YAML file")
  parser.add_argument("--extcal", type=Path, help="Extrinsics YAML file")
  parser.add_argument("--offset", type=float, default=0.0, help="Offset start of left file (seconds)")
  parser.add_argument("--scale", type=float, default=0.95, help="Scale to remove border")
  parser.add_argument("--output", type=Path, help="Output file")

  args = parser.parse_args()
  process(args)
