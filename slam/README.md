# Sparse Reconstruction using SLAM

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

## Running ORBSLAM3

1. Grab some stereo video
2. If you are running a camera like my asymmetrical stereo camera then use
stsync.py to synchronise images; otherwise create a rig folder containing
subdirectories named left and right
3. Run the `create_dataset.py` script
4. Build my ORBSLAM3 docker image
5. Run the docker image, making sure that this directory is in the workspace path
6. Run setup.sh from inside this directory
7. `cd ~/ORB_SLAM_COMMUNITY/Examples/Stereo`
8. Run `./stereo_asym ../../Vocabulary/ORBvoc.txt /path/to/dataset/settings.yaml /path/to/dataset /path/to/dataset/timestamps.txt`

### `setup.sh`

To be run from within my ORBSLAM3 docker image.
- Copies stereo_asym.cc to /home/user/ORB_SLAM_COMMUNITY/Examples/Stereo
- Modifies the CMakeLists.txt file using the asym.patch file
- Builds the `stereo_asym` tool

## Running DROID-SLAM

Follow steps 1-3 from the ORBSLAM3 instructions above.

1. Run my techdemo docker image
2. Run the installation instructions; there is a version on my 
[project page](https://www.lyndonhill.com/TechDemo/slam.html) modified
for this docker image
3. Copy the Python files in the `droid_slam` directory to `DROID_SLAM/evaluation_scripts`
4. Run `python3 evaluation_scripts/test_asym.py --datapath /work/project/dataset --stereo --ply map.ply`
