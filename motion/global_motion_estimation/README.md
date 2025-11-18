# Global Motion Estimation Demonstration

## Phase Correlation

## Dependencies
- OpenCV package for Python
- NumPy
- Matplotlib
- argparse
- pathlib

You can run these scripts using my [techdemo docker image](https://github.com/mukoan/Docker).

## Usage
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

