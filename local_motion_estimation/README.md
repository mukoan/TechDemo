# Local Matching Estimation Demonstration

## Block Matching
- `bma` can run two block matching algorithms: 2D Full Search (2DFS) and PMVFAST.
  2DFS will always give the best results but will be slower.
- The Block Distortion Metric (BDM) that has been implemented is SAD (Sum of
  Absolute Differences). There are many BDMS that could have been used, e.g.
  MAD, MSE, SSE, etc.
- The default block size is 16. The dimensions of your test images must be a
  multiple of block size. The PMVFAST algorithm uses several thresholds and
  the implementation only handles block sizes of 8 and 16; other block sizes
  will give unexpected results.
- Motion vectors are saved as a binary blob. You must make sure to use the
  same block size parameter with both bma and bmc.
  
## Dependencies
- C++ 20
- OpenCV v4
- ffmpeg
- Python with OpenCV and matplotlib packages

You can build this code and run everything using my [techdemo docker image](https://github.com/mukoan/Docker).

## Instructions
`make` builds `bma` and `bmc`.


### Motion Estimation
```
$ ./bma -h
./bma usage:
 -c  current image filename
 -p  previous image filename
 -v  output motion vectors filename
 -b  block size (default = 16)
 -a  algorithm, either 2dfs (default) or pmvfast
 -t  time the algorithm
 -h  help; this message
```

Examples:

```
# Run 2DFS at block size 8x8
$ ./bma -c current.png -p previous.png -v motion.mv -b 8
```


```
# Run PMVFAST at block size 16x16
$ ./bma -c current.png -p previous.png -v motion.mv -b 16 -a pmvfast
```

### Motion Compensation
```
$ ./bmc -h
./bmc usage:
 -p  previous image filename
 -v  input motion vectors filename
 -b  block size (default = 16)
 -o  output image filename
 -h  help; this message
```

```
# Compensate an image with motion vectors estimated with block size 8x8
$ ./bmc -p previous.png -v motion.mv -b 8 -o compensated.png
```

## Video Evaluation
To run `bma` and `bmc` over a video sequence the `evaluate.py` script has been
provided.

- Edit `evaluate.py` to set the input video filename, block matching algorithm, block size and paths
- Run `evaluate.py`
- Results are output to the `evaluation_results.csv` file
- Use `plot_results.py` to plot the results
