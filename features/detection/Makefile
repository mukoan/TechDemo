##
# Makefile for Features
# Lyndon Hill
# 2025.10.28

.PHONY: all clean

CPP            = g++
CFLAGS         = -std=c++17 -O3
INCLUDES      += -I. `pkg-config --cflags opencv4`
LIBS          += `pkg-config --libs opencv4`

# Uncomment next lines if OpenCV was compiled with non-free option to gain SURF support
# LIBS          += -lopencv_xfeatures2d
# CFLAGS        += -DHAVE_SURF

detect-match: detect-match.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

clean:
	rm -f detect-match
	rm -f temp*.jpg
	rm -f temp*.png
