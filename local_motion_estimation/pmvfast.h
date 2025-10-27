/**
 * @file   pmvfast.h
 * @brief  Block Matching Algorithm: PMVFAST
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#ifndef pmvfast_h
#define pmvfast_h

#include <vector>

#include <opencv2/core.hpp>


/**
 * pmvfast
 * @brief PMVFAST block matching algorithm,
 *        "Predictive Motion Vector Field Adaptive Search Technique (PMVFAST)
 *        - Enhancing Block Based Motion Estimation", 2001,
 *        A.M. Tourapis, O.C. Au and M.L. Liou, Proceedings of SPIE,
 *        doi 10.1117/12.411871
 * @param current    current image
 * @param previous   previous image
 * @param blk_size   block size
 * @return  motion vectors
 */
std::vector<cv::Vec2f> pmvfast(const cv::Mat &current, const cv::Mat &previous,
                               int blk_size);

// Large diamond search: search pattern is 4-neighbours at distance 2 pixels
// plus 4 diagonal neighbours at 1 pixel
void large_diamond_search(const cv::Mat &current, const cv::Mat &previous,
                          int blockx, int blocky, int blk_size,
                          std::vector<cv::Vec2f> &mv);

// Small diamond search: search pattern is 4-neighbours at distance 1 pixel
void small_diamond_search(const cv::Mat &current, const cv::Mat &previous,
                          int blockx, int blocky, int blk_size,
                          std::vector<cv::Vec2f> &mv);

#endif    // pmvfast_h

