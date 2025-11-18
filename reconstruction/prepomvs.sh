#!/usr/bin/env bash
# File  : prepomvs.sh
# Brief : Script to prepare COLMAP project for OpenMVS processing
# Author: Lyndon Hill
# Date  : 2025.10.01
#
# Description:
# Detect dense/images directory exists and has images in it.
# This implies that undistorted images have been generated;
# if not, run colmap image undistorter

# Check number of arguments
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <project_directory>"
  exit 1
fi

PROJECT_DIR=$1
cd ${PROJECT_DIR} || { echo "Project directory not found!"; exit 1;

# Make sure directories have been created dense and dense/images
mkdir -p dense/images

# Check if dense/images is empty
# If empty, run colmap image_undistorter
if [ -z "$(ls -A dense/images)" ]; then
  echo "dense/images is empty. Running colmap image_undistorter..."
  colmap image_undistorter --image_path images --input_path sparse/0  --output_path dense --output_type COLMAP
else
  echo "${PROJECT_DIR}/dense/images is not empty. Skipping colmap image_undistorter."
fi

echo "Preparation for OpenMVS processing done."
