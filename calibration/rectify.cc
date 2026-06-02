/**
 * @file   rectify.cc
 * @brief  Rectify stereo images
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

namespace fs = std::filesystem;

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -l  left image filename\n"
            << " -r  right image filename\n"
            << " -a  intrinsics file for left camera\n"
            << " -b  intrinsics file for right camera\n"
            << " -c  extrinsics filename\n"
            << " -o  rectified images filename stem (no extension)\n"
            << " -f  use fisheye lens model\n"
            << " -s  FoV scale (less than 1.0)\n"
            << " -h  help; this message\n";
}

int main(int argc, char** argv)
{
  std::string left_filename, right_filename;
  std::string intrinsics_left, intrinsics_right, extrinsics_filename;
  std::string output_filename = "rectified";
  double fov_scale = 0.9;
  bool fisheye = false;

  int c;
  while((c = getopt(argc, argv, "l:r:a:b:c:o:s:fh")) != -1)
  {
    switch(c) {
      case 'l': left_filename       = optarg;            break;
      case 'r': right_filename      = optarg;            break;
      case 'a': intrinsics_left     = optarg;            break;
      case 'b': intrinsics_right    = optarg;            break;
      case 'c': extrinsics_filename = optarg;            break;
      case 'o': output_filename     = optarg;            break;
      case 'f': fisheye             = true;              break;
      case 's': fov_scale           = std::atof(optarg); break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);    break;
    }
  }

  // Load images

  cv::Mat left_img = cv::imread(left_filename.c_str());
  if(left_img.empty()) {
    std::cerr << "Left image could not be loaded\n";
    return(EXIT_FAILURE);
  }

  cv::Mat right_img = cv::imread(right_filename.c_str());
  if(right_img.empty()) {
    std::cerr << "Right image could not be loaded\n";
    return(EXIT_FAILURE);
  }

  cv::Size img_size = left_img.size();

  // Load calibration

  cv::Mat K1, D1, K2, D2, R, T;

  load_intrinsics(intrinsics_left, K1, D1);
  load_intrinsics(intrinsics_right, K2, D2);
  load_extrinsics(extrinsics_filename, R, T);

  // Rectify images

  cv::Mat R1, R2, P1, P2, Q;
  cv::Mat left_rectified_img, right_rectified_img;
  cv::Mat rmap[2][2];

  if(fisheye)
  {
    // balance and fov_scale work together to ensure that the border is
    // cropped from the final image
    double balance = 0.0;

    cv::fisheye::stereoRectify(K1, D1, K2, D2, img_size, R, T, R1, R2, P1, P2, Q,
        cv::fisheye::CALIB_ZERO_DISPARITY, img_size, balance, fov_scale);
    cv::fisheye::initUndistortRectifyMap(K1, D1, R1, P1, img_size, CV_16SC2,
                                         rmap[0][0], rmap[0][1]);
    cv::fisheye::initUndistortRectifyMap(K2, D2, R2, P2, img_size, CV_16SC2,
                                         rmap[1][0], rmap[1][1]);
  }
  else
  {
    cv::stereoRectify(K1, D1, K2, D2, img_size, R, T, R1, R2, P1, P2, Q);
    cv::initUndistortRectifyMap(K1, D1, R1, P1, img_size, CV_16SC2,
                                rmap[0][0], rmap[0][1]);
    cv::initUndistortRectifyMap(K2, D2, R2, P2, img_size, CV_16SC2,
                                rmap[1][0], rmap[1][1]);
  }

  cv::remap(left_img, left_rectified_img, rmap[0][0], rmap[0][1],
            cv::INTER_LINEAR, cv::BORDER_CONSTANT, cv::Scalar(0));
  cv::remap(right_img, right_rectified_img, rmap[1][0], rmap[1][1],
            cv::INTER_LINEAR, cv::BORDER_CONSTANT, cv::Scalar(0));

  // Save images

  std::filesystem::path file_path = left_filename;
  std::string extension = file_path.extension().string();

  std::string output_l_filename = output_filename + "_l" + extension;
  std::string output_r_filename = output_filename + "_r" + extension;
  cv::imwrite(output_l_filename.c_str(), left_rectified_img);
  cv::imwrite(output_r_filename.c_str(), right_rectified_img);

  return(EXIT_SUCCESS);
}
