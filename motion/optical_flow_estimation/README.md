# Optical Flow Estimation

## Dependencies
- OpenCV package for Python
- NumPy
- PyTorch
- torchvision
- ffmpeg

You can run these scripts using my [techdemo docker image](https://github.com/mukoan/Docker).

## Usage
Estimate dense optical flow between two images using Farneback's method:
```
ocv-of-single.py --current current.png --previous previous.png --output flow.png
```
The output is a visualisation of the optical flow.
The `--compensate` parameter can be added to apply flow compensation to the
previous image.


Estimate dense optical flow for a video sequence using Farneback's method:
```
ocv-of-sequence.py --video input_video.mp4 --images extracted_frames --flow flow_fames
```
The specified video will have all frames extracted to the `extracted_frames` directory
and images visualising the flow will be stored in the `flow_frames` directory.
If either directory does not exist it will be created.


Estimate dense optical flow between two images using RAFT (requires PyTorch and torchvision):
```
raft-of-single.py --current current.png --previous previous.png --output flow.png
```
The `--compensate` parameter can be added to apply flow compensation to the
previous image.

Estimate dense optical flow for a video sequence using RAFT (requires PyTorch and torchvision):
```
raft-of-sequence.py --video input.mp4 --images extracted_frames --output flow_frames
```

