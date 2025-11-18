/**
 * @file   bmc.cc
 * @brief  Block Motion Compensation
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>

#include "blockcompensate.h"
#include "bmsupport.h"


// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -p  previous image filename\n"
            << " -v  input motion vectors filename\n"
            << " -b  block size (default = 16)\n"
            << " -o  output image filename\n"
            << " -h  help; this message\n";
}

int main(int argc, char *argv[])
{
  std::string previous_filename, motion_filename;
  std::string output_filename;
  int blocksize = 16;

  int c;
  while((c = getopt(argc, argv, "p:v:b:o:h")) != -1)
  {
    switch(c) {
      case 'p': previous_filename = optarg;            break;
      case 'v': motion_filename   = optarg;            break;
      case 'b': blocksize         = std::stoi(optarg); break;
      case 'o': output_filename   = optarg;            break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);  break;
    }
  }

  // Check inputs

  if(previous_filename.empty() || motion_filename.empty() ||
     output_filename.empty())
  {
    std::cout << "Error: filename was not specified\n";
    return(EXIT_FAILURE);
  }

  // Load input image

  cv::Mat previous_img;
  previous_img = cv::imread(previous_filename.c_str());

  // Load motion vectors

  std::vector<cv::Vec2f> mv;
  if(!load_vectors(motion_filename, mv))
  {
    std::cout << "Error: could not load motion vectors\n";
    return(EXIT_FAILURE);
  }

  // Check motion vectors match dimensions
  if(mv.size() != (previous_img.cols/blocksize)*(previous_img.rows/blocksize))
  {
    std::cout << "Error: motion vectors do not match images with the specified "
              << "block size\n";
    return(EXIT_FAILURE);
  }

  // Block motion compensation

  cv::Mat output_img;

  if(previous_img.channels() == 1)
    block_compensate(previous_img, mv, blocksize, output_img);
  else
  {
    // Split into separate colour channels and process individually

    std::vector<cv::Mat> channels(previous_img.channels());
    cv::split(previous_img, channels);

    for(int chan = 0; chan < channels.size(); chan++)
    {
      block_compensate(channels[chan], mv, blocksize, output_img);
      channels[chan] = output_img;
    }

    // Join channels together
    cv::merge(channels, output_img);
  }

  // Save output image

  cv::imwrite(output_filename.c_str(), output_img);

  return(EXIT_SUCCESS);
}
