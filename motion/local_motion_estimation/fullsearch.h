/**
 * @file   2dfs.h
 * @brief  Block Matching Algorithm: 2 dimensional full search
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#ifndef fullsearch_h
#define fullsearch_h

#include <vector>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>

/// Search range for full search
#define RANGE 16


/**
 * fullsearch
 * @brief 2D Full Search block matching algorithm
 * @param current    current image
 * @param previous   previous image
 * @param blk_size   block size
 * @return  motion vectors
 */
std::vector<cv::Vec2f> fullsearch(const cv::Mat &current, const cv::Mat &previous,
                                  int blk_size);

#endif    // fullsearch_h

