/**
 * @file   calibrate_mono.cc
 * @brief  Find intrinsic calibration for a camera
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
  std::cout << " -i  directory of calibration chart images\n"
            << " -c  calibration yaml file (optional)\n"
            << " -x  calibration chart corners horizontally\n"
            << " -y  calibration chart corners vertically\n"
            << " -s  calibration chart square size (mm)\n"
            << " -f  use fisheye lens model\n"
            << " -h  help; this message\n";
}

int main(int argc, char** argv)
{
  std::string images_dir;
  std::string calibration_filename;
  int board_corners_wide = 8;
  int board_corners_high = 6;
  float square_size      = 24.0f;
  bool fisheye           = false;

  int c;
  while((c = getopt(argc, argv, "i:c:x:y:s:fh")) != -1)
  {
    switch(c) {
      case 'i': images_dir           = optarg;            break;
      case 'c': calibration_filename = optarg;            break;
      case 'x': board_corners_wide   = std::atoi(optarg); break;
      case 'y': board_corners_high   = std::atoi(optarg); break;
      case 's': square_size          = std::atof(optarg); break;
      case 'f': fisheye              = true;              break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);     break;
    }
  }

  // Check input directory exists
  if(images_dir.empty()) {
    std::cout << "Error: images directory was not specified\n";
    return(EXIT_FAILURE);
  }

  // Load and process images, in either PNG or JPG format

  std::vector<std::string> image_files;
  cv::glob(images_dir + "/*.png", image_files);
  if(image_files.empty()) {
    cv::glob(images_dir + "/*.jpg", image_files);
  }

  if(image_files.empty()) {
    std::cout << "Error: no images found in directory " << images_dir << "\n";
    return(EXIT_FAILURE);
  }

  // Find chessboard corners in images

  std::vector<std::vector<cv::Point2f>> image_points;
  cv::Size board_size(board_corners_wide, board_corners_high);

  for(const auto &file : image_files) {
    cv::Mat img = cv::imread(file);
    std::vector<cv::Point2f> points;
    if(cv::findChessboardCorners(img, board_size, points))
      image_points.push_back(points);
  }

  // Prepare object points

  std::vector<std::vector<cv::Point3f>> object_points(1);

  for(int i = 0; i < board_size.height; ++i)
    for(int j = 0; j < board_size.width; ++j)
      object_points[0].push_back(cv::Point3f(j*square_size, i*square_size, 0.0f));
  object_points.resize(image_points.size(), object_points[0]);

  // Load first image to get size

  cv::Mat  first_img  = cv::imread(image_files[0]);
  cv::Size image_size = first_img.size();

  // Calibrate camera (assume all images are the same size)

  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  cv::Mat dist_coeffs;
  std::vector<cv::Mat> rvecs, tvecs;
  double rms;

  if(fisheye) {
    dist_coeffs = cv::Mat::zeros(4, 1, CV_64F);
    int flags = cv::fisheye::CALIB_FIX_SKEW | cv::fisheye::CALIB_RECOMPUTE_EXTRINSIC;
    rms = cv::fisheye::calibrate(object_points, image_points, image_size,
                                 camera_matrix, dist_coeffs, rvecs, tvecs, flags);
  } else {
    rms = cv::calibrateCamera(object_points, image_points, image_size,
                              camera_matrix, dist_coeffs, rvecs, tvecs);
  }

  std::cout << "RMS error for calibration: " << rms << "\n";

  // Output calibration
  if(calibration_filename.empty()) {
    std::cout << "Camera matrix:\n" << camera_matrix << "\n";
    std::cout << "Distortion coefficients:\n" << dist_coeffs << "\n";
  } else {
    save_intrinsics(calibration_filename, camera_matrix, dist_coeffs);
  }

  return(EXIT_SUCCESS);
}
