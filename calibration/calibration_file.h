/**
 * @file   calibration_file.h
 * @brief  Load and save calibration files
 * @author Lyndon Hill
 * @date   2025.12.08
 */

#ifndef calibration_file_h
#define calibration_file_h

#include <opencv2/opencv.hpp>

/**
 * Load intrinsics
 * @param filename  Filename to load intrinsics as a YAML type file
 * @param k         Camera matrix
 * @param d         Distortion coefficients
 * @return true if successful
 */
bool load_intrinsics(const std::string &filename, cv::Mat &k, cv::Mat &d);

/**
 * Save intrinsics
 * @param filename  Filename to save intrinsics as a YAML type file
 * @param k         Camera matrix
 * @param d         Distortion coefficients
 */
void save_intrinsics(const std::string &filename, const cv::Mat &k, const cv::Mat &d);

/**
 * Load extrinsics
 * @param filename  Filename to load extrinsics as a YAML type file
 * @param rot       Rotation matrix
 * @param trans     Translation vector
 * @return true if successful
 */
bool load_extrinsics(const std::string &filename, cv::Mat &rot, cv::Mat &trans);

/**
 * Save extrinsics
 * @param filename  Filename to save extrinsics as a YAML type file
 * @param rot       Rotation matrix
 * @param trans     Translation vector
 */
void save_extrinsics(const std::string &filename, cv::Mat &rot, cv::Mat &trans);

/**
 * Save extrinsics as a COLMAP rig file (JSON)
 * @param filename       Filename, usually rig_config.json
 * @param rig_directory  Directory containing the rig structure
 * @param rot            Rotation matrix
 * @param trans          Translation vector
 * @return true if successful
 */
bool save_rig(const std::string &filename, const std::string &rig_directory,
              cv::Mat &rot, cv::Mat &trans);

#endif    // calibration_file_h

