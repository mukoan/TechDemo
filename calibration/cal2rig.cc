/**
 * @file   cal2rig.cc
 * @brief  Make COLMAP rig file from extrinsics calibration
 * @author Lyndon Hill
 * @date   2025.12.08
 */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <filesystem>

#include <opencv2/opencv.hpp>

#include "calibration_file.h"

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -c  extrinsics file\n"
            << " -i  images directory; containing left/ and right/\n"
            << " -r  rig file, default = rig_config.json\n";
}

int main(int argc, char** argv)
{
  std::string extrinsics_filename;
  std::string rig_dir;
  std::string rig_filename("rig_config.json");

  int  c;
  while((c = getopt(argc, argv, "c:i:r:h")) != -1)
  {
    switch(c) {
      case 'c': extrinsics_filename  = optarg;            break;
      case 'i': rig_dir              = optarg;            break;
      case 'r': rig_filename         = optarg;            break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);     break;
    }
  }

  cv::Mat R, T;

  if(!load_extrinsics(extrinsics_filename, R, T)) {
    std::cerr << "Could not load extrinsics " << extrinsics_filename << std::endl;
    return(EXIT_FAILURE);
  }

  if(!save_rig(rig_filename, rig_dir, R, T)) {
    std::cerr << "Could not write rig data to " << rig_filename << "\n";
    return(EXIT_FAILURE);
  }

  return(EXIT_SUCCESS);
}
