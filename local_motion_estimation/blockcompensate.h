/**
 * @file   blockcompensate.h
 * @brief  Block Motion Compensation
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#ifndef blockcompensate_h
#define blockcompensate_h

#include <vector>
#include <opencv2/core.hpp>


/**
 * Apply motion to image
 * @param previous_image    previous image
 * @param mv                motion vector field
 * @param blk_size          block size
 * @param output_image      block motion compensated image output
 */
void block_compensate(const cv::Mat &previous_image,
                      const std::vector<cv::Vec2f> &mv,
                      int blk_size,
                      cv::Mat &output_image);

#endif    // blockcompensate_h

