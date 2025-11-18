# Feature Detection and Matching Demonstration

## Dependencies
- OpenCV
- LightGlue code from [CVG](https://github.com/cvg/LightGlue]) (Computer Vision
  and Geometry Lab, ETH Zurich)

You can build and run this code using my [techdemo docker image](https://github.com/mukoan/Docker).


## Summary

`detect-match` will detect features in two images and match them.
`splg.py` will use SuperPoint and LightGlue to detect and match features in two images.

## SIFT, SURF, ORB

After running the techdemo docker image, you can build the code here using
`make`.

Usage:

```bash
detect-match -c path/to/current_image.jpg -p path/to/previous_image.jpg -k image_of_keypoints.jpg -m image_of_matches.jpg -a algorithm
```

Where `algorithm` is one of `sift`, `surf`, or `orb`.

The `workfeatures.py` script will extract frames from a video and run
`detect-match` for you, e.g.

```bash
workfeatures.py --video video.mp4 --images_dir images --output_dir sift --method sift
```

In this example, both keypoints and matches images will be written to the `sift`
directory. Any missing directories will be created for you.

## SuperPoint and LightGlue

Run the techdemo docker image,

```bash
rundocker.sh techdemo /path/to/TechDemo
```

where `TechDemo` is the directory where you pulled this repo to.

Next, set up LightGlue:

```bash
cd ~
git clone https://github.com/cvg/LightGlue.git
pip install "kornia>=0.6.11"
export QT_QPA_PLATFORM=offscreen
cd /work/features/detection
```

Make sure you extract some images to a suitable path inside the docker container,
e.g.

```bash
ffmpeg -i video.mp4 path/to/images/frame_%05d.png
```

Make a directory to store results,

```bash
mkdir results
```

Run the following command to detect and match features using SuperPoint and LightGlue:

```bash
splg.py --images_dir path/to/images --output_dir path/to/results
```

This will generate keypoints and matches images in the `results` directory.

