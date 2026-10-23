#!/usr/bin/env bash
# File:   setup.sh
# Brief:  Script to build asymmetric stereo ORBSLAM3 example
# Author: Lyndon Hill
# Date:   2026.09.29

# Copy source file to ORBSLAM3 directory
cp stereo_asym.cc ~/ORB_SLAM_COMMUNITY/Examples/Stereo

# Patch CMakeFile to add a build target for stereo_asym
cp asym.patch ~/ORB_SLAM_COMMUNITY
cd ~/ORB_SLAM_COMMUNITY
git apply asym.patch

# Build code
cd build
cmake ..
make -j$(nproc)

