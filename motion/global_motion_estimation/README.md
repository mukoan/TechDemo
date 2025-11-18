# Global Motion Estimation Demonstration

You can run these scripts and programs using my [techdemo docker image](https://github.com/mukoan/Docker).

## Phase Correlation

### Dependencies
- OpenCV package for Python
- NumPy
- Matplotlib
- argparse
- pathlib

### Usage
Estimate global translation between two images using phase correlation:
```
pc.py --current current.png --previous previous.png
```
Use the `--show` parameter can be added to generate a plot of the correlation surface.


Compensate global motion by combining 2 overlapping images given the offset
between them:
```
globalmc.py --current current.png --previous previous.png --xoff 5 --yoff -3 --output compensated.png
```
The `--outline` parameter can be added to draw a box around the previous image.


## Global Feature Matching

### Dependencies
- OpenCV

### Usage
Build the `gfm` program using `make`.

Estimate global translation between two images by detecting features and matching
them:
```
gfm -c current.png -p previous.png
```

The `globalmc.py` script (see above) can be used to make a visualisation of the
translation by combining images.
