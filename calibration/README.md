# Camera Calibration Demonstration

You can build these programs using my [techdemo docker image](https://github.com/mukoan/Docker).

All of these programs have help output, use the `-h` option.

Calibration images are expected to contain a chessboard.
Suitable calibration charts can be generated at
https://calib.io/pages/camera-calibration-pattern-generator and printed on a
regular printer.

Typically you will need round 10-30 images taken at different angles and distances.
They should be in focus and have good contrast. Make sure the chart is at flat
as possible.

See my [technical explanation](https://www.lyndonhill.com/techdemo/calibration)
for examples of using these tools, with images.


## Fisheye Lenses
For fisheye lenses, including action cameras with fisheye lenses then
use the `-f` option in the programs. As the model used is different, then
ensure that you consistently use `-f` for `dedistort`, `rectify`, etc.

Be careful when using the RMS error to compare calibration quality
using the standard model to the fisheye model. The fisheye model is more
sensitive to points on the edges of the image (where there is more warping) and
this may increase the error.


## Dependencies
- OpenCV (libraries and headers for C++, package for Python)
- FFmpeg, Python 3, argparse, subprocess (for the video undistorter script)


## Calibration Charts
These tools support chessboard type charts only. Note that when defining
the dimensions of the chart by number of corners then you need to ignore the
outer corners. For example, a chart 10 squares across by 8 squares high will have
9x7 corners.


## Single Camera Calibration
To calibrate a single (mono) camera:
```
calibrate_mono -i input_images_dir -c calibration.yaml
```

where `input_images_dir` is a directory contains images of a suitable chessboard
calibration pattern; output will be written to `calibration.yaml`.

The RMS error reported by `calibrate_mono` should be around 1.0 or lower.
Higher errors mean that the calibration is not good.

To de-distort images,
```
dedistort -i image.jpg -o dedistorted.jpg -c calibration.yaml
```

where `image.jpg` is an image taken with the same camera and lens and
`calibration.yaml` is the output of `calibrate_mono` above.

In the output image, lines that are straight in the real world that have become
curved by lens distortion should now be straight again.


## Stereo Camera Calibration
To calibrate a stereo camera, first calibrate the left and right cameras
separately using `calibrate_mono` and save the calibration files, e.g.
```
calibrate_mono -i left_images_dir -c left_intrinsics.yaml
calibrate_mono -i right_images_dir -c right_intrinsics.yaml
```

Run stereo calibration:
```
calibrate_stereo -i input_dir -a left_intrinsics.yaml -b right_intrinsics.yaml -c stereo_calibration.yaml -r stereo_rig.json
```

where `input_dir` is a directory containing subdirectories `left` and `right`;

```
input_dir
├── left
│   ├── frames00001.jpg
│   ├── frames00002.jpg
│   ├── ...
│   └── frames00050.jpg
└── right
    ├── frames00001.jpg
    ├── frames00002.jpg
    ├── ...
    └── frames00050.jpg
```
The assumption is that frames with the same number form synchronised stereo pairs.


To rectify images use,
```
rectify -l left.jpg -r right.jpg -a left_intrinsics.yaml -b right_intrinsics.yaml -e stereo_calibration.yaml -o rectified
```

This will produce `rectified_l.jpg` and `rectified_r.jpg`. The `-s` option
can be used to adjust the cropping to remove visible border after
rectification and should be in the range 0.0 to 1.0.

If you have an extrinsics calibration and need a rig file for COLMAP, `cal2rig`
will create it from the calibration with the correct formatting:
```
cal2rig -c stereo_calibration.yaml -i images -r rig_config.json
```

The `-i` parameter specifies the path to the rig directory containing
subdirectories for `left/` and `right/` and those contain the images.
The path will not be checked by `cal2rig` but it should match up to the
images paths stored in the COLMAP project database.


## Remove Distortion from Video
Use `calibrate_mono` to generate a calibration file for your camera.

Use this script to remove distortion from a video,
```
video_undistorter.py --input video.mp4 --calibration calibration.yaml --mode pad --output new_video.mp4
```

This script uses FFmpeg; the lenscorrection filter's lens model is not as
sophisticated as the OpenCV lens model therefore the output will not be
distortion free.

The `mode` option can be either "pad" or "scale". Pad will crop the border created
by removing distortion and make the border black to fill the frame, scale will
scale the video to fit the frame.


## Checking a Calibration
Use `calibrate_check` to verify calibration for your camera.
This tool works for both mono and stereo cameras.

### Mono Calibration Check

Example:
```
calibrate_check -i images -c calibration.yaml
```

In this example,
* `-i images` : sets the directory with validation images
* `-c calibration.yaml` : sets the calibration file containing intrinsics to be checked

Additional options,
* `-d` : project the 3D calibration points to the validation images
* `-f` : sets the lens to be fisheye type
* `-s N` : sets the chessboard square size to N mm
* `-x X` : sets the number of corners horizontally on the chessboard to X
* `-y Y` : sets the number of corners vertically on the chessboard to Y

Using the `-d` option allows you to check the fit of the model to individual
images.

### Stereo Calibration Check

Example:
```
calibrate_check -i rig -c extrinsics.yaml -a left_intrinsics.yaml -b right_intrinsics.yaml -t
```

In this example,
* `-i rig` : sets the directory containing subdirectories `left` and `right` containing validation images
* `-c extrinsics.yaml` : sets the calibration file containing extrinsics to be checked
* `-a left_intrinsics.yaml` : sets the calibration file containing intrinsics for the left camera
* `-b right_intrinsics.yaml` : sets the calibration file containing intrinsics for the right camera
* `-t` : sets this to be a stereo calibration check

The additional options in the mono example can also be used.


Example:
```
calibrate_check -i test_rig -c extrinsics.yaml -a left.yaml -b right.yaml -t -f -x 10 -y 8 -s 20.5
```

In this example we are testing a stereo rig that uses fisheye lenses and
specifies a different calibration chart.
