# File:   load_settings.py
# Author: Lyndon Hill
# Date:   2026.10.10

""" Load and parse ORB-SLAM settings file """

import argparse
from pathlib import Path


def read_file(filename: Path):
    """ Read line by line, must be "Rectified" camera type """

    valid_type = False

    with open(filename, "r") as f:
        line = f.readline()
        while line:
            label = ""
            value = ""
            results = line.strip().split(" ")
            if len(results) == 2:
                label, value = results
            else:
                pass

            if label is None or value is None:
                continue
            if label == "Camera.type:":
                valid_type = value == '"Rectified"'
            if label == "Camera1.fx:":
                fx = float(value)
            if label == "Camera1.fy:":
                fy = float(value)
            if label == "Camera1.cx:":
                cx = float(value)
            if label == "Camera1.cy:":
                cy = float(value)
            if label == "Camera.width:":
                width = int(value)
            if label == "Camera.height:":
                height = int(value)

            line = f.readline()

    if not valid_type:
        raise Exception("Not a Rectified camera")

    return fx, fy, cx, cy, width, height


def read_baseline(filename: Path):

    # default baseline = 0.1m
    baseline = float(100)

    with open(filename, "r") as f:
        line = f.readline()
        while line:
            label = ""
            value = ""
            results = line.strip().split(" ")
            if len(results) == 2:
                label, value = results
            else:
                pass

            if label is None or value is None:
                continue
            if label == "Stereo.b:":
                baseline = float(value)
                break

            line = f.readline()

    return baseline

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse ORB-SLAM settings file")
    parser.add_argument("--input", required=True, help="path to settings file")

    args = parser.parse_args()

    fx, fy, cx, cy, w, h = read_file(args.input)

    print(f"Read calibration; fx: {fx}, fy: {fy}, cx: {cx}, cy: {cy}, {w}x{h}")
