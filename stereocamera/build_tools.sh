#!/usr/bin/env bash
# Brief : Build tools for encoding MV-HEVC from stereo video
# Author: Lyndon Hill
# Date  : 2026.07.22


# Build x265
curl -LO https://bitbucket.org/multicoreware/x265_git/downloads/x265_4.2.tar.gz
tar xfz x265_4.2.tar.gz
cd x265_4.2/build
cmake -DENABLE_MULTIVIEW=ON ../source
make
cd ../..
rm x265_4.2.tar.gz

# Build MP4Box
curl -LO https://github.com/gpac/gpac/archive/refs/tags/v26.02.0.tar.gz
tar xfz v26.02.0.tar.gz
cd gpac-26.02.0
./configure
make
cd ..
rm v26.02.0.tar.gz

# Build ffmpeg v8
sudo apt update
sudo apt install nasm
curl -LO https://ffmpeg.org/releases/ffmpeg-8.1.2.tar.xz
tar -xf ffmpeg-8.1.2.tar.xz
cd ffmpeg-8.1.2/
./configure --enable-nonfree --disable-static --enable-shared
make
# Set up libraries so we don't have to install
mkdir libdir
cd libdir
ln -s ../libavcodec/libavcodec.so.62 .
ln -s libavcodec.so.62 libavcodec.so
ln -s ../libavdevice/libavdevice.so.62 .
ln -s libavdevice.so.62 libdevice.so
ln -s ../libavfilter/libavfilter.so.11 .
ln -s libavfilter.so.11 libfilter.so
ln -s ../libavformat/libavformat.so.62 .
ln -s libavformat.so.62 libformat.so
ln -s ../libavutil/libavutil.so.60 .
ln -s libavutil.so.60 libutil.so
ln -s ../libswresample/libswresample.so.6 .
ln -s libswresample.so.6 libswresample.so
ln -s ../libswscale/libswscale.so.9 .
ln -s libswscale.so.9 libswscale.so
cd ../..
rm ffmpeg-8.1.2.tar.xz

echo "Script finished."
