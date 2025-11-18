##
# Makefile for Global Motion Estimation
# Lyndon Hill
# 2025.11.16

.PHONY: clean

CPP            = g++
CFLAGS         = -std=c++17 -O3
INCLUDES      += -I. `pkg-config --cflags opencv4`
LIBS          += `pkg-config --libs opencv4`

gfm: gfm.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

clean:
	rm -f gfm
	rm -f temp*.jpg
	rm -f temp*.png
