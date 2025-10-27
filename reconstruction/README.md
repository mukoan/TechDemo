# 3D Reconstruction

This repository contains scripts for running COLMAP and OpenMVS for 3D reconstruction.

## Dependencies
- COLMAP
- OpenMVS
- FFMPEG

## COLMAP Scripts

1. Set up your project directory and extract images from video using `setup.sh`
2. Run a sparse reconstruction using `runcolmap.sh`
3. Run a dense reconstruction using `dense.sh` (optional)

`setup.sh` takes 2 arguments:
- Path to your project directory, e.g., `/path/to/project`
- Path to your video file, e.g., `/path/to/video.mp4`

Example: `./setup.sh /path/to/project /path/to/video.mp4`

`runcolmap.sh` takes 1 argument:
- Path to your project directory

Example: `./runcolmap.sh /path/to/project`

`dense.sh` takes 1 argument:
- Path to your project directory

Example: `./dense.sh /path/to/project`

## OpenMVS Scripts

1. Prepare a COLMAP project with a sparse reconstruction by undistorting images using `prepomvs.sh`
2. Run OpenMVS tools on the project to generate a dense point cloud, mesh, refined mesh and textured mesh using `runomvs.sh`

`prepomvs.sh` takes 1 argument:
- Path to the project directory

Example: `./prepomvs /path/to/project`

`runomvs.sh` takes 1 argument
- Path to the project directory

Example: `./runomvs /path/to/project`


