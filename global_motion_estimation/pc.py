#!/usr/bin/env python3
#
# File : pc.py
# Brief: Phase correlation
#
# Find the offset between 2 overlapping images using Phase Correlation.

import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

def load_image_grey(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IOError(f"Could not read image: {path}")
    return img

def compute_phase_correlation(img1, img2):
    # Convert to float32
    f1 = np.float32(img1)
    f2 = np.float32(img2)

    # Apply Hann window to reduce edge effects
    hann = cv2.createHanningWindow(f1.shape[::-1], cv2.CV_32F)
    shift, correlation = cv2.phaseCorrelate(f1, f2, hann)
    print(f"Detected shift: {shift}, Correlation: {correlation}")

    return shift, correlation

def plot_phase_correlation_surface(img1, img2):
    # Find 2D FFT
    f1 = np.fft.fft2(img1)
    f2 = np.fft.fft2(img2)

    # Compute the cross power spectrum
    R = (f1 * f2.conj()) / np.abs(f1 * f2.conj())
    r = np.fft.ifft2(R)
    r = np.fft.fftshift(r)
    correlation_surface = np.abs(r)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.imshow(correlation_surface, cmap='viridis')
    plt.title('Phase Correlation Surface')
    plt.colorbar(label='Correlation Strength')
    plt.xlabel('X Shift')
    plt.ylabel('Y Shift')
    plt.show()
    # plt.savefig("pcsurf.png")

def main(image1_path, image2_path, show):

    """ Replace with your image paths
    image1_path = '../images/crop1.png'
    image2_path = '../images/crop2.png'
    """

    img1 = load_image_grey(image1_path)
    img2 = load_image_grey(image2_path)

    compute_phase_correlation(img1, img2)
    if show:
        plot_phase_correlation_surface(img1, img2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='pc',
                        description='Phase correlation for image alignment')

    parser.add_argument("--current", type=Path, help="Current image")
    parser.add_argument("--previous", type=Path, help="Target image")
    parser.add_argument('--show', help="Show PC surface", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    main(args.current, args.previous, args.show)
