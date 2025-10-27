##
# Makefile for Block Matching
# Lyndon Hill
# 2025.10.01

.PHONY: all clean

CPP            = g++
CFLAGS         = -I. -std=c++20 -O3
INCLUDES      += -I/usr/local/include/opencv4
LIBS          += -L/usr/local/lib -L/usr/local/cuda/lib64
OPENCV         = -lopencv_core -lopencv_imgcodecs

all: bma bmc

bma: bma.cc fullsearch.cc pmvfast.cc subpixel.cc bmsupport.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS) $(OPENCV)

bmc: bmc.cc blockcompensate.cc subpixel.cc bmsupport.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS) $(OPENCV)

clean:
	rm -f bma
	rm -f bmc
	rm -f temp*.mv
	rm -f temp*.jpg
	rm -f temp*.png
