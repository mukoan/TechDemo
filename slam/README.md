# Sparse Reconstruction using ORBSLAM3

This directory contains tools and scripts for running ORBSLAM3 on the
stereo video obtained from my asymmetrical stereo camera.

## Prerequisites

Build my ORBSLAM3 docker image:
This is patched to compile with C++14, fix a couple of bugs in Settings and
to add an API to save the map as a PLY file.
You can use this docker image for experimenting with ORBSLAM3; there is nothing
that makes it only suitable for my stereo camera.

Synchronised images a stereo rig in individual folders for left and right
images.

## `create_dataset.py`

pip install tqdm

Converts synchronised images from the stereocamera into a dataset that can
be used with ORBSLAM3:
- rectifies the images
- generates a timestamps file
- creates a configuration file

## `setup.sh`

To be run from within my ORBSLAM3 docker image.
- Copies stereo_asym.cc to /home/user/ORB_SLAM3/Examples/Stereo
- Modifies the CMakeLists.txt file using the asym.patch file
- Builds the stereo_asym tool

## Running ORBSLAM3

1. Grab some stereo video
2. If you are running a camera like my asymmetrical stereo camera then use
stsync.py to synchronise images; otherwise create a rig folder containing
subdirectories named left and right
3. Run the `create_dataset.py` script
4. Build my ORBSLAM3 docker image
5. Run the docker image, making sure that this directory is in the workspace path
6. Run setup.sh from inside this directory
7. `cd ~/ORB_SLAM3/Examples/Stereo`
8. Run `./stereo_asym ../../Vocabulary/ORBvoc.txt /path/to/dataset/config.yaml /path/to/dataset /path/to/dataset/timestamps.txt`

