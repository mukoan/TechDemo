/**
 * @file   calibration_file.cc
 * @brief  Load and save calibration files
 * @author Lyndon Hill
 * @date   2025.12.08
 */

#include "calibration_file.h"

#include <fstream>
#include <opencv2/core/quaternion.hpp>

// Load intrinsics file
bool load_intrinsics(const std::string &filename, cv::Mat &k, cv::Mat &d)
{
  cv::FileStorage fs(filename, cv::FileStorage::READ);
  if(!fs.isOpened())
    return(false);

  fs["camera_matrix"] >> k;
  fs["distortion_coefficients"] >> d;

  return(true);
}

// Save intrinsics
void save_intrinsics(const std::string &filename, const cv::Mat &k, const cv::Mat &d)
{
  cv::FileStorage fs(filename, cv::FileStorage::WRITE);
  fs << "camera_matrix" << k;
  fs << "distortion_coefficients" << d;
  fs.release();
}

// Load extrinsics
bool load_extrinsics(const std::string &filename, cv::Mat &rot, cv::Mat &trans)
{
  cv::FileStorage fs(filename, cv::FileStorage::READ);
  if(!fs.isOpened())
    return(false);

  fs["R"] >> rot;
  fs["T"] >> trans;

  return(true);
}

// Save extrinsics
void save_extrinsics(const std::string &filename, cv::Mat &rot, cv::Mat &trans)
{
  cv::FileStorage fs(filename, cv::FileStorage::WRITE);
  fs << "R" << rot;
  fs << "T" << trans;
  fs.release();
}

// Save extrinsics as a rig file
bool save_rig(const std::string &filename, const std::string &rig_directory,
              cv::Mat &r, cv::Mat &t)
{
  // Convert rotation to quaternions
  cv::Quatd q = cv::Quatd::createFromRotMat(r);

  // Open a file and write...
  std::ofstream output(filename);
  if(!output)
    return(false);

  output << "[\n"
         << "  {\n"
         << "    \"cameras\": [\n"
         << "      {\n"
         << "        \"image_prefix\": \"" << rig_directory << "/left/\",\n"
         << "        \"ref_sensor\": true\n"
         << "      },\n"
         << "      {\n"
         << "        \"image_prefix\": \"" << rig_directory << "/right/\",\n"
         << "        \"cam_from_rig_rotation\": [\n"
         << "            " << q[0] << ",\n"
         << "            " << q[1] << ",\n"
         << "            " << q[2] << ",\n"
         << "            " << q[3] << "\n"
         << "        ],\n"
         << "        \"cam_from_rig_translation\": [\n"
         << "            " << t.at<double>(0,0) << ",\n"
         << "            " << t.at<double>(1,0) << ",\n"
         << "            " << t.at<double>(2,0) << "\n"
         << "        ]\n"
         << "      }\n"
         << "    ]\n"
         << "  },\n"
         << "]\n";

  return(true);
}
