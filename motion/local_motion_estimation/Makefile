##
# Makefile for Block Matching
# Lyndon Hill
# 2025.10.01

.PHONY: all clean

CPP            = g++
CFLAGS         = -std=c++17 -O3
INCLUDES      += -I. `pkg-config --cflags opencv4`
LIBS          += `pkg-config --libs opencv4`

all: bma bmc

bma: bma.cc fullsearch.cc pmvfast.cc subpixel.cc bmsupport.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

bmc: bmc.cc blockcompensate.cc subpixel.cc bmsupport.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

clean:
	rm -f bma
	rm -f bmc
	rm -f temp*.mv
	rm -f temp*.jpg
	rm -f temp*.png
