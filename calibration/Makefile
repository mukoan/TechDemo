##
# Makefile for Calibration
# Lyndon Hill
# 2025.12.08

.PHONY: all clean

CPP            = g++
CFLAGS         = -std=c++17 -O3
INCLUDES      += -I. `pkg-config --cflags opencv4`
LIBS          += `pkg-config --libs opencv4`

all: calibrate_mono calibrate_stereo calibrate_check dedistort rectify

calibrate_mono: calibrate_mono.cc calibration_file.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

calibrate_stereo: calibrate_stereo.cc calibration_file.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

calibrate_check: calibrate_check.cc calibration_file.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

dedistort: dedistort.cc calibration_file.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

rectify: rectify.cc calibration_file.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

clean:
	rm -f calibrate_mono
	rm -f calibrate_stereo
	rm -f calibrate_check
	rm -f dedistort
	rm -f rectify
	rm -f temp*.jpg
	rm -f temp*.png
	rm -f temp*.yaml
