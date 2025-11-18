##
# Makefile for Tracking
# Lyndon Hill
# 2025.10.28

.PHONY: clean

CPP            = g++
CFLAGS         = -std=c++17 -O3
INCLUDES      += -I. `pkg-config --cflags opencv4`
LIBS          += `pkg-config --libs opencv4`

klt-tracker: klt-tracker.cc
	$(CPP) $^ -o $@ $(CFLAGS) $(INCLUDES) $(LIBS)

clean:
	rm -f klt-tracker
