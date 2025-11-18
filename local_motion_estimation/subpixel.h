/**
 * @file   subpixel.h
 * @brief  Sub pixel block matching
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#ifndef subpixel_h
#define subpixel_h

#include <vector>
#include <opencv2/core.hpp>

#include "bmsupport.h"


/**
 * Subpixel motion estimation
 * @param current    current frame
 * @param previous   previous frame
 * @param blk_size   block size
 * @param mv         integer motion vectors
 */
void subpixel_search(const cv::Mat &current, const cv::Mat &previous,
                     int blk_size, std::vector<cv::Vec2f> &mv);

#endif    // subpixel_h

