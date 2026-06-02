/**
 * @file   calibrate_stereo.cc
 * @brief  Calibrate camera from stereo image pairs
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
  std::cout << " -i  input image directory, containing left/ and right/\n"
            << " -a  input intrinsics file for left camera\n"
            << " -b  input intrinsics file for right camera\n"
            << " -c  output calibration file, e.g. stereo.yaml\n"
            << " -r  rig file for COLMAP, e.g. rig_config.json\n"
            << " -x  calibration chart corners horizontally\n"
            << " -y  calibration chart corners vertically\n"
            << " -s  calibration chart square size (mm)\n"
            << " -f  use fisheye lens model\n"
            << " -h  help; this message\n";
}

int main(int argc, char** argv)
{
  std::string input_directory;
  std::string intrinsics_left, intrinsics_right;
  std::string extrinsics_filename;
  std::string rig_filename;
  int board_corners_wide = 8;
  int board_corners_high = 6;
  float square_size      = 24.0f;
  bool fisheye           = false;

  int  c;
  while((c = getopt(argc, argv, "i:a:b:c:r:x:y:s:fh")) != -1)
  {
    switch(c) {
      case 'i': input_directory      = optarg;            break;
      case 'a': intrinsics_left      = optarg;            break;
      case 'b': intrinsics_right     = optarg;            break;
      case 'c': extrinsics_filename  = optarg;            break;
      case 'r': rig_filename         = optarg;            break;
      case 'x': board_corners_wide   = std::atoi(optarg); break;
      case 'y': board_corners_high   = std::atoi(optarg); break;
      case 's': square_size          = std::atof(optarg); break;
      case 'f': fisheye              = true;              break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);     break;
    }
  }

  // Check input directory exists
  if(input_directory.empty()) {
    std::cout << "Error: input directory was not specified\n";
    return(EXIT_FAILURE);
  }

  // Load intrinsics

  cv::Mat K1, K2, D1, D2;

  if(!load_intrinsics(intrinsics_left, K1, D1)) {
    std::cerr << "Intrinsics file " << intrinsics_left << " could not be opened\n";
    return(EXIT_FAILURE);
  }

  if(!load_intrinsics(intrinsics_right, K2, D2)) {
    std::cerr << "Intrinsics file " << intrinsics_right << " could not be opened\n";
    return(EXIT_FAILURE);
  }

  // Find all images in the left directory

  std::vector<std::string> image_files;
  cv::glob(input_directory + "/left/" + "*.png", image_files);
  if(image_files.empty()) {
    cv::glob(input_directory + "/left/" + "*.jpg", image_files);
  }

  // Find chessboard corners in all image pairs

  std::vector<std::vector<cv::Point2f>> left_image_points;
  std::vector<std::vector<cv::Point2f>> right_image_points;
  cv::Size board_size(board_corners_wide, board_corners_high);

  for(size_t i = 0; i < image_files.size(); ++i) {
    cv::Mat left_img = cv::imread(image_files[i]);
    std::filesystem::path lpath = std::filesystem::path(image_files[i]);
    std::string right_filename = input_directory + "/right/" + lpath.filename().string();
    cv::Mat right_img = cv::imread(right_filename);

    // Check both images loaded
    if(left_img.empty() || right_img.empty())
      continue;

    std::vector<cv::Point2f> left_points, right_points;
    bool found_left  = cv::findChessboardCorners(left_img, board_size, left_points);
    bool found_right = cv::findChessboardCorners(right_img, board_size, right_points);

    if(found_left && found_right) {
      left_image_points.push_back(left_points);
      right_image_points.push_back(right_points);
    }
  }

  if(left_image_points.empty() || right_image_points.empty()) {
    std::cout << "Error: no chessboard corners found in image pairs\n";
    return(EXIT_FAILURE);
  }

  // Prepare object points

  std::vector<std::vector<cv::Point3f>> object_points;
  std::vector<cv::Point3f> objp;

  for(int i = 0; i < board_size.height; i++) {
    for(int j = 0; j < board_size.width; j++) {
      objp.push_back(cv::Point3f(j*square_size, i*square_size, 0.0f));
    }
  }
  object_points.resize(left_image_points.size(), objp);

  // Calibrate stereo camera

  cv::Mat R = cv::Mat::zeros(3, 3, CV_64F);
  cv::Mat T = cv::Mat::zeros(3, 1, CV_64F);
  cv::Size image_size = cv::imread(image_files[0]).size();
  double rms;

  if(fisheye) {
    rms = cv::fisheye::stereoCalibrate(
              object_points,
              left_image_points,
              right_image_points,
              K1, D1,
              K2, D2,
              image_size,
              R, T,
              cv::fisheye::CALIB_FIX_INTRINSIC,
              cv::TermCriteria(cv::TermCriteria::COUNT + cv::TermCriteria::EPS, 100, 1e-5)
          );
  } else {
    cv::Mat E, F;
    rms = cv::stereoCalibrate(
              object_points,
              left_image_points,
              right_image_points,
              K1, D1,
              K2, D2,
              image_size,
              R, T, E, F,
              cv::CALIB_FIX_INTRINSIC,
              cv::TermCriteria(cv::TermCriteria::COUNT + cv::TermCriteria::EPS, 100, 1e-5)
          );
  }

  std::cout << "RMS error for stereo calibration: " << rms << "\n";

  // Save calibration to file if specified
  if(!extrinsics_filename.empty())
    save_extrinsics(extrinsics_filename, R, T);
  else {
    std::cout << "Rotation matrix between cameras:\n" << R << "\n";
    std::cout << "Translation vector between cameras:\n" << T << "\n";
  }

  // Save stereo rig file for COLMAP if specified
  if(!rig_filename.empty())
    if(!save_rig(rig_filename, input_directory, R, T))
      std::cerr << "Could not write rig data to " << rig_filename << "\n";

  return(EXIT_SUCCESS);
}
