/**
 * @file   dedistort.cc
 * @brief  Remove lens distortion from an image
 * @author Lyndon Hill
 * @date   2025.12.08
 */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include <opencv2/opencv.hpp>

#include "calibration_file.h"

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -i  input image filename\n"
            << " -c  calibration yaml file\n"
            << " -o  undistorted output image filename\n"
            << " -f  use fisheye lens model\n"
            << " -h  help; this message\n";
}

int main(int argc, char** argv)
{
  std::string input_filename;
  std::string calibration_filename;
  std::string output_filename = "dedistorted.png";
  bool fisheye = false;

  int c;
  while((c = getopt(argc, argv, "i:c:o:fh")) != -1)
  {
    switch(c) {
      case 'i': input_filename       = optarg;         break;
      case 'c': calibration_filename = optarg;         break;
      case 'o': output_filename      = optarg;         break;
      case 'f': fisheye              = true;           break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);  break;
    }
  }

  // Load image

  cv::Mat input_img = cv::imread(input_filename.c_str());
  if(input_img.empty()) {
    std::cerr << "Input image was not loaded\n";
    return(EXIT_FAILURE);
  }

  // Load calibration

  cv::Mat camera_matrix, dist_coeffs;
  if(!load_intrinsics(calibration_filename, camera_matrix, dist_coeffs)) {
    std::cerr << "Calibration file could not be opened\n";
    return(EXIT_FAILURE);
  }

  // Undistort image and save

  cv::Mat undistorted_img;

  if(fisheye) {
    cv::Mat new_camera_matrix;
    double balance = 0.0;

    cv::fisheye::estimateNewCameraMatrixForUndistortRectify(
        camera_matrix,
        dist_coeffs,
        input_img.size(),
        cv::Matx33d::eye(),
        new_camera_matrix,
        balance
    );

    cv::fisheye::undistortImage(input_img, undistorted_img,
                                camera_matrix, dist_coeffs, new_camera_matrix);
  } else {
    cv::undistort(input_img, undistorted_img, camera_matrix, dist_coeffs);
  }

  cv::imwrite(output_filename.c_str(), undistorted_img);

  return(EXIT_SUCCESS);
}
