#!/usr/bin/bash
#
# Brief : Create and set up COLMAP project
# Usage : ./setup.sh /path/to/project /path/to/video.mp4
# Author: Lyndon Hill
# Date  : 2025.10.01
#
# Description:
#
# This script sets up a COLMAP project directory structure and extracts images
# from a video file. The project directory will be created if it does not exist.
#
# The project will have the structure as follows:
#
# /path/to/project
# -  project.db
# +- images
#    +- image00001.jpg
#    +- image00002.jpg
#    +- ...
#    +- imageNNNNN.jpg
# +- sparse
#    +- 0
#       +- cameras.bin
#       +- images.bin
#       +- points3D.bin
#
# The sparse/0 directory will be populated after running the runcolmap.sh script.

PROJECT_DIR=$1
mkdir -p $PROJECT_DIR

INPUT_VIDEO=$2

mkdir -p $PROJECT_DIR/images
mkdir -p $PROJECT_DIR/sparse

# Extract images to images

# Set this to 1 for low resolution at low frame rate
# Note: if your video is portrait and you want low resolution then you will have
#       to swap the scale parameter, e.g. scale=720:1280
LOW_RESOLUTION=1

if [ $LOW_RESOLUTION -eq 1 ]; then
    echo "Extracting low resolution images from video..."
    ffmpeg -i ${INPUT_VIDEO} -vf fps=5,scale=1280:720 "${PROJECT_DIR}/images/image%05d.jpg"
else
    echo "Extracting full resolution images from video..."
    ffmpeg -i ${INPUT_VIDEO} "${PROJECT_DIR}/images/image%05d.jpg"
fi

echo "Original video file was located at ${INPUT_VIDEO}" > ${PROJECT_DIR}/readme.txt
