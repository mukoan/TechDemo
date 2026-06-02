/**
 * @file   calibrate_check.cc
 * @brief  Check a given calibration for a camera
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

// Calibration validation parameters
struct ValidationParams
{
  bool   fisheye;      ///< fisheye lens model
  double square_size;  ///< calibration chart square size (mm)
  int    board_wide;   ///< number of corners horizontally
  int    board_high;   ///< number of corners vertically
  bool   diagnostics;  ///< save diagnostic images
};

/**
 * @brief Find image files
 * @param image_path  directory to check
 * @param filenames   list of all files with png or jpg extension
 * @return true if image files were found
 */
bool get_image_files(const std::string &image_path,
                     std::vector<std::string> &filenames);

/**
 * @brief Evaluate RMS reprojection error for intrinsics
 * @param images_dir        directory with validation chessboard images
 * @param calibration_file  intrinsics YAML filename
 * @param params            validation parameters structure, see ValidationParams
 * @return true if image files with detected chart found, false if no image files
 *              or no charts were detected
 */
bool check_intrinsics(const std::string &images_dir,
                      const std::string &calibration_file,
                      const ValidationParams &params);

/**
 * @brief Evaluate RMS reprojection error for extrinsics
 * @param image_dir         directory containing left/ and right/ subdirs with
 *                          validation images
 * @param left_intrinsics   left intrinsics YAML filename
 * @param right_intrinsics  right intrinsics YAML filename
 * @param calibration_file  extrinsics YAML filename
 * @param params            validation parameters structure, see ValidationParams
 * @return true if pairs of image files with detected chart found, false if no
 *              pairs of image files found, no charts were detected or missing
 *              calibration files
 */
bool check_extrinsics(const std::string &image_dir,
                      const std::string &left_intrinsics,
                      const std::string &right_intrinsics,
                      const std::string &calibration_file,
                      const ValidationParams &params);

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -i  directory of calibration chart images\n"
            << " -c  calibration yaml file (mono/stereo)\n"
            << " -x  calibration chart corners horizontally\n"
            << " -y  calibration chart corners vertically\n"
            << " -s  calibration chart square size (mm)\n"
            << " -t  perform stereo calibration check\n"
            << " -a  intrinsics file for left camera (if stereo check)\n"
            << " -b  intrinsics file for right camera (if stereo check)\n"
            << " -f  use fisheye lens model\n"
            << " -d  save diagnostic images\n"
            << " -h  help; this message\n";
}

int main(int argc, char** argv)
{
  bool check_mono        = true;
  std::string images_dir, alt_images_dir;
  std::string calibration_filename;
  std::string intrinsics_left, intrinsics_right;
  int board_corners_wide = 8;
  int board_corners_high = 6;
  float square_size      = 24.0f;
  bool fisheye           = false;
  bool diagnostics       = false;

  int c;
  while((c = getopt(argc, argv, "i:c:x:y:s:a:b:tfdh")) != -1)
  {
    switch(c) {
      case 'i': images_dir           = optarg;            break;
      case 'c': calibration_filename = optarg;            break;
      case 'a': intrinsics_left      = optarg;            break;
      case 'b': intrinsics_right     = optarg;            break;
      case 'x': board_corners_wide   = std::atoi(optarg); break;
      case 'y': board_corners_high   = std::atoi(optarg); break;
      case 's': square_size          = std::atof(optarg); break;
      case 't': check_mono           = false;             break;
      case 'f': fisheye              = true;              break;
      case 'd': diagnostics          = true;              break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);     break;
    }
  }

  // Check input directory exists
  if(images_dir.empty()) {
    std::cout << "Error: images directory was not specified\n";
    return(EXIT_FAILURE);
  }

  ValidationParams params;
  params.fisheye     = fisheye;
  params.square_size = square_size;
  params.board_wide  = board_corners_wide;
  params.board_high  = board_corners_high;
  params.diagnostics = diagnostics;

  if(check_mono) {
    if(!check_intrinsics(images_dir, calibration_filename, params))
      return(EXIT_FAILURE);
  } else {
    if(!check_extrinsics(images_dir, intrinsics_left, intrinsics_right,
                         calibration_filename, params))
      return(EXIT_FAILURE);
  }

  return(EXIT_SUCCESS);
}

// Get image files in directory
bool get_image_files(const std::string &image_path,
                     std::vector<std::string> &filenames)
{
  cv::glob(image_path + "/*.png", filenames);
  if(filenames.empty()) {
    cv::glob(image_path + "/*.jpg", filenames);
  }

  return(!filenames.empty());
}

// Check the images using the calibration file
bool check_intrinsics(const std::string &image_dir,
                      const std::string &calibration_file,
                      const ValidationParams &params)
{
  cv::Mat K, D;
  if(!load_intrinsics(calibration_file, K, D)) {
    std::cerr << "Could not load intrinsics " << calibration_file << std::endl;
    return(false);
  }

  // Prepare 3D object points
  std::vector<cv::Point3f> object_points;
  cv::Size board_size(params.board_wide, params.board_high);

  for(int i = 0; i < params.board_high; ++i)
    for(int j = 0; j < params.board_wide; ++j)
      object_points.push_back(cv::Point3f(j*params.square_size, i*params.square_size, 0.0f));

  cv::Mat rvec = cv::Mat::zeros(3, 3, CV_64F);
  cv::Mat tvec = cv::Mat::zeros(3, 1, CV_64F);
  std::vector<cv::Point2f> projected_points;

  double meanmean_error = 0.0;
  int image_count = 0;

  std::vector<std::string> image_files;
  get_image_files(image_dir, image_files);

  for(const auto &file : image_files)
  {
    cv::Mat img = cv::imread(file.c_str());
    std::vector<cv::Point2f> detected_points;
    bool found = cv::findChessboardCorners(img, board_size, detected_points);

    if(found) {
      if(params.fisheye) {
        std::vector<cv::Point2f> undistorted_points;
        cv::fisheye::undistortPoints(detected_points, undistorted_points, K, D, cv::noArray(), K);

        cv::solvePnP(object_points, undistorted_points, K, cv::noArray(), rvec, tvec);

        cv::fisheye::projectPoints(object_points, projected_points, rvec, tvec, K, D);
      } else {
        // Solve for extrinsic parameters (rvec and tvec) for an image
        cv::solvePnP(object_points, detected_points, K, D, rvec, tvec);

        // Project 3D points back to 2D
        cv::projectPoints(object_points, rvec, tvec, K, D, projected_points);
      }

      if(params.diagnostics)
      {
        // Draw projected points on images
        for(size_t i = 0; i < detected_points.size(); ++i)
          cv::drawMarker(img, projected_points[i], cv::Scalar(0,255,255), cv::MARKER_CROSS, 10);

        std::filesystem::path ipath = std::filesystem::path(file);
        std::string target = ipath.filename().string();
        cv::imwrite(std::string("proj_")+target, img);
      }

      // Calculate the error
      double totalError = 0;
      for (size_t i = 0; i < detected_points.size(); ++i) {
        // Euclidean distance between observed and projected point
        double error = cv::norm(detected_points[i] - projected_points[i]);
        totalError += error * error;
      }

      // Mean squared error or root mean squared error
      double meanError = std::sqrt(totalError / detected_points.size());
      // std::cout << file << ", intrinsics RMS error = " << meanError << std::endl;
      meanmean_error += meanError;
      image_count++;
    } else {
      std::cerr << "No corners found in " << file << ", skipping\n";
    }
  }

  if(image_count > 0) {
    std::cout << "Intrinsics RMS error = " << meanmean_error/image_count << "\n";
    return(true);
  } else {
    std::cerr << "No suitable images found\n";
    return(false);
  }
}

// Check stereo images using calibration file
bool check_extrinsics(const std::string &image_dir,
                      const std::string &intrinsics_left,
                      const std::string &intrinsics_right,
                      const std::string &calibration_file,
                      const ValidationParams &params)
{
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

  // Load extrinsics

  cv::Mat R, T;

  if(!load_extrinsics(calibration_file, R, T)) {
    std::cerr << "Could not load extrinsics " << calibration_file << std::endl;
    return(false);
  }

  cv::Size board_size(params.board_wide, params.board_high);

  std::vector<cv::Point3f> object_points;
  for(int i = 0; i < board_size.height; i++) {
    for(int j = 0; j < board_size.width; j++) {
      object_points.push_back(cv::Point3f(j*params.square_size, i*params.square_size, 0.0f));
    }
  }

  int image_pairs = 0;
  double mean_error = 0;

  std::vector<std::string> left_files;
  get_image_files(image_dir+"/left", left_files);
  for(const auto &left_filename : left_files)
  {
    cv::Mat left_img = cv::imread(left_filename.c_str());
    std::filesystem::path lpath = std::filesystem::path(left_filename);
    std::string right_filename = image_dir + "/right/" + lpath.filename().string();
    cv::Mat right_img = cv::imread(right_filename);

    // Check both images loaded
    if(left_img.empty() || right_img.empty()) {
      std::cerr << "Filename " << left_filename << " not an image pair\n";
      continue;
    }

    std::vector<cv::Point2f> left_points, right_points;
    bool found_left = cv::findChessboardCorners(left_img, board_size, left_points);
    bool found_right = cv::findChessboardCorners(right_img, board_size, right_points);

    if(found_left && found_right)
    {
      // Refine detected corner positions

      cv::Mat left_grey, right_grey;
      cv::cvtColor(left_img, left_grey, cv::COLOR_BGR2GRAY);
      cv::cvtColor(right_img, right_grey, cv::COLOR_BGR2GRAY);

      cv::Size winSize = cv::Size( 5, 5 );
      cv::Size zeroZone = cv::Size( -1, -1 );
      cv::TermCriteria criteria = cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::COUNT, 40, 0.001);
      cv::cornerSubPix(left_grey, left_points, winSize, zeroZone, criteria);
      cv::cornerSubPix(right_grey, right_points, winSize, zeroZone, criteria);

      cv::Mat rvecLeft = cv::Mat::zeros(3, 3, CV_64F);
      cv::Mat tvecLeft = cv::Mat::zeros(3, 1, CV_64F);
      cv::Mat rvecRight, tvecRight;
      cv::Mat R_left_to_right = R;
      cv::Mat T_left_to_right = T;

      std::vector<cv::Point2f> projected_left, projected_right;

      if(params.fisheye)
      {
        // Undistort points for the pose estimation (using fisheye intrinsics)
        std::vector<cv::Point2f> left_pts_undist, right_pts_undist;
        cv::fisheye::undistortPoints(left_points, left_pts_undist, K1, D1, cv::noArray(), K1);

        // Solve PnP in the rectified (pinhole-equivalent) space
        cv::solvePnP(object_points, left_pts_undist, K1, cv::noArray(), rvecLeft, tvecLeft);

        // Project back using the fisheye model for validation
        cv::fisheye::projectPoints(object_points, projected_left, rvecLeft, tvecLeft, K1, D1);
      }
      else
      {
        // Solve the board pose for the left camera
        cv::solvePnP(object_points, left_points, K1, D1, rvecLeft, tvecLeft);

        // Project
        cv::projectPoints(object_points, rvecLeft, tvecLeft, K1, D1, projected_left);
      }

      // Project 3D object points into right camera

      // Transform the board pose
      cv::Mat rotMatLeft;
      cv::Rodrigues(rvecLeft, rotMatLeft);
      cv::Mat rotMatRight = R_left_to_right * rotMatLeft;
      cv::Rodrigues(rotMatRight, rvecRight);

      tvecRight = R_left_to_right * tvecLeft + T_left_to_right;

      if(params.fisheye)
        cv::fisheye::projectPoints(object_points, projected_right, rvecRight, tvecRight, K2, D2);
      else
        cv::projectPoints(object_points, rvecRight, tvecRight, K2, D2, projected_right);

      // Compute RMS error
      double frame_error = 0;
      for(size_t i = 0; i < left_points.size(); ++i) {
        // Euclidean distance between observed and projected point
        double error = cv::norm(left_points[i] - projected_left[i]) +
                       cv::norm(right_points[i] - projected_right[i]);
        frame_error += error*error;
      }
      mean_error += std::sqrt(frame_error/left_points.size());
      image_pairs++;

      if(params.diagnostics)
      {
        // Draw projected points on images
        for(size_t i = 0; i < left_points.size(); ++i) {
          cv::drawMarker(left_img, projected_left[i], cv::Scalar(0,255,255), cv::MARKER_CROSS, 10);
          cv::drawMarker(right_img, projected_right[i], cv::Scalar(0,255,255), cv::MARKER_CROSS, 10);
        }

        std::string target = lpath.filename().string();
        cv::imwrite(std::string("proj_l_")+target, left_img);
        cv::imwrite(std::string("proj_r_")+target, right_img);
      }
    } else {
      std::string target = lpath.filename().string();
      std::cerr << "Image pair " << target << ", no suitable corners\n";
    }
  }

  if(image_pairs > 0) {
    mean_error /= image_pairs;
    std::cout << "Extrinsics RMS error = " << mean_error << std::endl;
    // std::cout << image_pairs << " images\n";
    return(true);
  } else {
    std::cerr << "No suitable image pairs found\n";
    return(false);
  }
}
