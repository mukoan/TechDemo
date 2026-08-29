# Stereo Camera Demonstration

This repo dir contains files for dealing with files from a stereo camera
composed of a GoPro Hero 10 and GoPro Hero 3+ Silver. It could easily
be modified to work with combinations of other camera types.

## Synchronisation

### Dependencies
The following packages should be installed:
- pathlib
- logging
- scipy
- numpy
- subprocess
- matplotlib (for visualisation of cross-correlation)

Additionally FFmpeg must be installed.

### stsync.py

This is a script designed to synchronise video frames captured from an
asymmetrical stereo camera made from a GoPro Hero 10 and GoPro
Hero 3+ Silver.

Ensure that you clap your hands within a few seconds of starting recording.
Extracts frames from video and synchronise them using audio cross
correlation.

Usage Example:

```bash
stsync.py --left GX000001.mp4 --right GOPR0001.MP4 --output stereo
```

#### Trim Frames

I noticed that when extracting frames from 1920x1080 @ 50fps video on my
Hero 3+ Silver, FFmpeg would repeat some frames near the start. To compensate for
this I added "trim" frames.

The number of trim frames required depends on whether you start recording with
the left or right camera first. I assume that anyone using this script will
have the Hero 3+ as the right side camera.

You may need to adjust, so use `--trimleft` and `--trimright` parameters
to change the number of trim frames. The default values are 2 frames for
left first recording and 4 for right first recording.

## Frame Selection

The `select.sh` bash script is for selecting frames after synchronisation;
for example, for camera calibration or for stereo reconstruction.

Usage:
```bash
select.sh <input_format> <output_directory> <start_frame> <increment> <end_frame>
```

Input format should be in standard C string style; e.g. `image%06d.png`

## Colour Correction

### Dependencies
The following packages should be installed:
- pathlib
- logging
- opencv
- numpy
- scipy
- colour-science

### Generating a 3D LUT
The `generate_lut.py` script generates a 3D LUT for colour correction of the
stereo camera. It uses frames from video of a colourful scene to find the colour
mapping between the two cameras.

```bash
generate_lut.py --input test-rig --output lut.cube
```

The `test-rig` directory should contain a set of images from the left and right
cameras, named `left/frame00001.png`, `right/frame00001.png`, etc.

### Using the LUT
The `apply_lut.py` script applies the LUT to a set of images.

```bash
apply_lut.py --input test-rig --output corrected --lut lut.cube
```

The cube file can also be used in FFmpeg for colour correction of video streams.
e.g.:
```bash
ffmpeg -i input.mp4 -vf lut3d=lut.cube output.mp4
```


## Reconstruction

### Dependencies
The following packages should be installed in a venv:
- pathlib
- logging
- subprocess
- opencv

### stereo_colmap.py

To run a stereo reconstruction using COLMAP,
1. Calibrate the camera (intrinsics and extrinsics)
2. Capture synced stereo video for the reconstruction
3. Assuming you want to create a project directory called `project`:
 - `mkdir project`
 - `mkdir -p project/images/left`
 - `mkdir -p project/images/right`
4. Copy the synced images to `project/left` and `project/right`; suggest using `select.sh` to copy every 10th image pair
5. Copy the `rig_config.json` from extrinsics calibration to the project directory
 - Make sure the paths in the json match
6. Run the script, as below:

```bash
stereo_colmap.py --project project --leftcal left_intrinsics.yaml --rightcal right_intrinsics.yaml
```

## Encode Stereo Video as MV-HEVC

### Dependencies
- x265
- MP4Box
- a recent version of FFmpeg

Running `build.sh` (no parameters required) will download and build the above
tools. It can be run inside my `techdemo` docker image.

A recent version of ffmpeg is required in order to support multiview video.

### `encodemv.py`

This script will take the synchronised frames, with synced frames having the same
number in the filename; as output from stsync.py. x265 will be used to encode
the video. The sound from the left video will be added to the output file.
Atoms to make the output compatible with Apple Spatial Video can
be added to the output file.

The script will downsample the frame rate by half; for example, resulting in a
stereo 1920x1080 @ 25fps video. Please note, this is not meant to be production
quality but a proof of concept for the workflow and the technical solution.

For simplification, it is assumed that recording on the stereo rig was started
by pressing the shutter button on the left camera first. The audio source will
usually be the video for the left images.

If you start video encoding from a frame later in the video don't forget to
adjust the offset value to sync audio properly.

```bash
encodemv.py --input <rig directory> --leftcal <left intrinsics YAML> --rightcal <right intrinsics YAML> --extcal <extrinsics YAML> --audio <audio source> --offset <synchronisation offset (seconds)> --scale <scaling factor to crop border> --output <output file>
```

Explanation of parameters:

- --input: the rig directory should contain left/ and right/ subdirectories
containing synchronised images
- --audio: this should be the left video file used with stsync.py
- --offset: this should be the time offset reported by stsync.py, to delay the audio
- --scale: this should be 1.0 if no cropping is required after rectification;
smaller if cropping is required
- --output: this should be the output file

