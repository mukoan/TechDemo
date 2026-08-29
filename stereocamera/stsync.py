#!/usr/bin/env python3
#
# File:   stsync.py
# Brief:  Synchronise stereo videos using audio
# Author: Lyndon Hill
# Date:   2026.06.17

"""
Extracts frames from 2 videos with synchronised filenames,
e.g. sync.py --left left.mp4 --right right.mp4 --output synced_rig

The following structure will be created:
 synced_rig/
 synced_rig/left/
 synced_rig/left/frame00001.jpg
 synced_rig/left/frame00002.jpg
 synced_rig/left/...
 synced_rig/left/frameNNNNN.jpg
 synced_rig/right/
 synced_rig/right/frame00001.jpg
 synced_rig/right/frame00002.jpg
 synced_rig/right/...
 synced_rig/right/frameNNNNN.jpg

where frames with the same number in the filename are synced
"""

import argparse
import logging
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# Constants
SAMPLE_RATE = 16000
ANALYSIS_DURATION = 10

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def setup_output(output_dir):
  """
  Create output directory structure:
    output directory and left and right subdirectories

  Params
    output_dir:  name of output directory
  """

  for folder in ["left", "right"]:
    (output_dir / folder).mkdir(parents=True, exist_ok=True)


def get_video_fps(video):
  """
  Get frame rate of video file

  Params
    video:  path to video

  Return
    frame rate
  """

  cmd = [
      'ffprobe', '-v', 'error',
      '-select_streams', 'v:0',
      '-show_entries', 'stream=avg_frame_rate',
      '-of', 'default=noprint_wrappers=1:nokey=1', str(video)
  ]
  result = subprocess.run(cmd, capture_output=True, text=True, check=True)

  num, den = map(float, result.stdout.strip().split("/"))
  return num / den


def extract_audio(file_path):
  """
  Extract mono audio from a video file using FFmpeg.

  Params
    file_path: path to video file that contains audio

  Return:
    audio as numpy array
  """

  cmd = [
      "ffmpeg", "-hide_banner", "-loglevel", "error",
      "-i", str(file_path),
      "-t", str(ANALYSIS_DURATION),
      "-ac", "1",                    # mono
      "-ar", str(SAMPLE_RATE),       # sample rate
      "-f", "f32le",                 # 32-bit float PCM
      "-"                            # output to stdout
  ]
  result = subprocess.run(cmd, capture_output=True, check=True)

  # Convert raw bytes to numpy array
  audio = np.frombuffer(result.stdout, dtype=np.float32)
  return audio


def plot_correlation(raw_left, raw_right):
  """
  Plot the cross-correlation in the region of the peak correlation

  Params
    raw_left:  raw audio samples from left video
    raw_right:  raw audio samples from right video
  """

  corr = signal.correlate(raw_left, raw_right, mode='full')
  lags = signal.correlation_lags(len(raw_left), len(raw_right), mode='full')

  peak = np.argmax(corr)
  plt.plot(lags[peak-2000:peak+2000], corr[peak-2000:peak+2000])
  plt.show()


def find_offset(raw_left, raw_right):
  """
  Find offset between audio using cross-correlation.
  Positive offset means that the left video starts before the right.

  Params
    raw_left:  raw audio samples from left video
    raw_right:  raw audio samples from right video

  Return:
    offset (seconds) and confidence of result
  """

  correlation = signal.correlate(raw_left, raw_right, mode='full')
  peak_index = np.argmax(correlation)

  lag_samples = peak_index - (len(raw_right) - 1)
  offset = lag_samples / SAMPLE_RATE

  confidence = np.abs(correlation[peak_index]) / np.mean(np.abs(correlation))
  return offset, confidence


def extract_frames(video_file, frame_rate, offset, output_dir, lut_file = None):
  """
  Extract all frames from a video and save as image files

  Params
    video_file:  input video file
    frame_rate:  frame rate of video (assumed constant)
    offset:  offset in seconds before starting decoding
    output_dir:  path to write output frames
  """

  cmd = [
      "ffmpeg", "-hide_banner", "-loglevel", "error",
      "-i", str(video_file),
      "-r", str(frame_rate),
      "-ss", str(offset),
      "-start_number", "1",
      str(output_dir / "frame%05d.png")
  ]

  if lut_file is not None:
    cmd.insert(6, "-vf")
    cmd.insert(7, f"lut3d={str(lut_file)}")

  subprocess.run(cmd, check=True)


def audio_sync(left, right, trimleft, trimright, lut, output):
  """
  Extract audio and use it to sync videos

  Params
    left: left video file
    right: right video file
    trimleft: additional frames for offset
    trimright: additional frames for offset
    output: path to directory for synchronised output frames
  """

  setup_output(output)

  # Extract audio from both videos
  left_audio = extract_audio(left)
  right_audio = extract_audio(right)

  # plot_correlation(left_audio, right_audio)

  # Use cross-correlation to estimate offset
  offset, confidence = find_offset(left_audio, right_audio)

  LOG.info(f"{offset}s offset to the right video, confidence {confidence}")

  if confidence < 40:
    LOG.warning("Low confidence warning!")

  fps = get_video_fps(left)

  # Round offset; FFmpeg will output next frame after given time
  new_offset_frames = np.floor(np.abs(offset)*fps-0.5)
  new_offset = new_offset_frames/fps

  if offset >= 0:
    LOG.info("Extracting frame from left video; left recording first")
    trim3 = trimleft*(1.0/fps)
    extract_frames(left, fps, max(0, new_offset-trim3), output / "left")
    LOG.info("Extracting frames from right video")
    extract_frames(right, fps, 0, output / "right", lut)
  else:
    LOG.info("Extracting frames from left video, right recording first")
    trim3 = trimright*(1.0/fps)
    extract_frames(left, fps, 0, output / "left")
    LOG.info("Extracting frames from right video")
    extract_frames(right, fps, max(0, new_offset+trim3), output / "right", lut)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Synchronise two videos using audio.")
  parser.add_argument("--left", type=Path, help="Path to left video file", required=True)
  parser.add_argument("--right", type=Path, help="Path to right video file, required=True")
  parser.add_argument("--output", type=Path, help="Path for output frames, required=True")
  parser.add_argument("--trimleft", type=int, default=2, help="Trim amount if left recording started first")
  parser.add_argument("--trimright", type=int, default=4, help="Trim amount if right recording started first")
  parser.add_argument("--lut", type=Path, help="Look Up Table for colour correction of right camera")

  args = parser.parse_args()

  audio_sync(args.left, args.right, args.trimleft, args.trimright,
             args.lut, args.output)
