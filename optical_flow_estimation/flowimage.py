# File  : flowimage.py
# Brief : Support functions for optical flow image rendering and compensation
# Author: Lyndon Hill
# Date  : 2025.10.01

import cv2
import numpy as np


def render_image(flow):
  """Render optical flow as a colour image"""
  magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
  hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
  hsv[..., 1] = 255

  # Hue = flow direction
  hsv[..., 0] = angle * 180 / np.pi / 2

  # Value = flow magnitude
  hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)

  flow_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

  return flow_image


def compensate_image(image, flow):
  """Compensate an image using the provided optical flow"""
  h, w = flow.shape[:2]
  flow_map = -flow.copy()
  flow_map[..., 0] += np.arange(w)
  flow_map[..., 1] += np.arange(h)[:, np.newaxis]

  compensated_image = cv2.remap(image, flow_map[..., 0], flow_map[..., 1], interpolation=cv2.INTER_LINEAR)

  return compensated_image
