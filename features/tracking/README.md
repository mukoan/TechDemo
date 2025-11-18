# Feature Tracking Demonstration

## Dependencies
- OpenCV

You can build and run this code using my [techdemo docker image](https://github.com/mukoan/Docker).

## Summary

`klt-tracker` will detect features and track them across frames in a video.
`cotracker.py` will form a grid of features over a frame and track the grid
points across frames in a video.

## KLT Tracker

Build the `klt-tracker` executable by entering `make`.

Usage:
```bash
klt-tracker -i video.mp4 -o results.mp4 -n 1000 -l
```

Parameter explanation:
 - `-i video.mp4` = the input video you wish to track
 - `-o results.mp4` = output video of the tracks visualised over the input video
 - `-n 1000` = the number of features to track
 - `-l` = draw lines for each tracked feature (optional)

## CoTracker

Get my techdemo docker file if you haven't done so already,
`git clone https://github.com/mukoan/Docker.git`

Build and start the techdemo docker container,
`cd Docker`
`rundocker.sh techdemo <working directory>`
where `working directory` is where your input video is located.

Set up the environment,
```bash
cd ~
git clone https://github.com/facebookresearch/co-tracker.git
pip install imageio[ffmpeg]
```

Usage:
```bash
python3 online_demo.py --video_path /work/video.mp4 --grid_size 20
```
where `video.mp4` is your input video.
