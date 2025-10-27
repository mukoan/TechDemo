/**
 * @file   bma.cc
 * @brief  Block Matching Algorithm tool
 * @author Lyndon Hill
 * @date   2025.10.01
 *
 * Note on conventions used here:
 * 1. The motion field defines where a block in the current image
 *    maps to a block in the previous image.
 * 2. The motion vector is added to the co-ordinates in the current frame
 *    to get the position in the previous frame.
 */

#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <iostream>
#include <string>
#include <vector>
#include <chrono>

#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>

#include "fullsearch.h"
#include "pmvfast.h"
#include "subpixel.h"
#include "bmsupport.h"

using namespace std;
using namespace std::chrono;


// Help user
void usage(const char *exe)
{
  cout << exe << " usage:\n";
  cout << " -c  current image filename\n"
       << " -p  previous image filename\n"
       << " -v  output motion vectors filename\n"
       << " -b  block size (default = 16)\n"
       << " -a  algorithm, either 2dfs (default) or pmvfast\n"
       << " -t  time the algorithm\n"
       << " -h  help; this message\n";
}

int main(int argc, char *argv[])
{
  string current_filename, previous_filename;
  string output_filename("motion_vectors.mv");

  int  blocksize = 16;
  bool alg_pmvfast = false;
  bool timing = false;
  int  c;

  while((c = getopt(argc, argv, "c:p:v:b:a:th")) != -1)
  {
    switch(c) {
      case 'c': current_filename  = optarg;           break;
      case 'p': previous_filename = optarg;           break;
      case 'v': output_filename   = optarg;           break;
      case 'b': blocksize         = atoi(optarg);     break;
      case 'a':
      {
        if(!strncmp(optarg, "pmvfast", 7))
          alg_pmvfast = true;
        break;
      }
      case 't': timing = true;                        break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS); break;
    }
  }

  // Check inputs

  if(current_filename.empty() || previous_filename.empty())
  {
    cout << "Error: image filename was not specified\n";
    return(EXIT_FAILURE);
  }

  // Load images

  cv::Mat current_img, previous_img;
  current_img  = cv::imread(current_filename.c_str(), cv::IMREAD_GRAYSCALE);
  previous_img = cv::imread(previous_filename.c_str(), cv::IMREAD_GRAYSCALE);

  // Check image dimensions

  if((current_img.rows != previous_img.rows) ||
     (current_img.cols != previous_img.cols))
  {
    cout << "Error: image dimensions do not match\n";
    return(EXIT_FAILURE);
  }

  // Make sure images can be represented by block size
  if((current_img.rows % blocksize) || (current_img.cols % blocksize))
  {
    cout << "Error: image dimensions must be a multiple of block size.\n";
    cout << "       Try setting the -b parameter\n";
    return(EXIT_FAILURE);
  }

  // Run block matching

  vector<cv::Vec2f> mv;

  time_point<steady_clock> start;
  if(timing) start = steady_clock::now();

  if(alg_pmvfast)
    mv = pmvfast(current_img, previous_img, blocksize);
  else
    mv = fullsearch(current_img, previous_img, blocksize);

  if(timing) {
    time_point<steady_clock> stop = steady_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    cout << "Time taken: " << duration.count() << " microseconds\n";
  }

  // Subpixel refinement of motion vectors
  subpixel_search(current_img, previous_img, blocksize, mv);

  if(!save_vectors(mv, output_filename))
  {
    cout << "Error saving output vectors\n";
    return(EXIT_FAILURE);
  }

  return(EXIT_SUCCESS);
}
