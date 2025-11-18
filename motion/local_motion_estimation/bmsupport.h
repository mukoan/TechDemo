/**
 * @file   bmsupport.h
 * @brief  Block matching support functions
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#ifndef bmsupport_h
#define bmsupport_h

#include <vector>
#include <string>
#include <opencv2/core.hpp>


/**
 * Interpolate pixel using bilinear interpolation
 * @param img       input image; must be single channel uchar, i.e. CV_8U or CV_8UC1
 * @param fx        x co-ordinate to interpolate
 * @param fy        y co-ordinate to interpolate
 * @return interpolated pixel value
 */
unsigned char interpolate(const cv::Mat &img, float fx, float fy);

/**
 * SAD (sum of absolute differences)
 * Calculate block distortion metric for block in reference
 * image at integer co-ordinates with block in search image
 * at floating point co-ordinates
 * @param ref       reference image (luminance)
 * @param search    search image (luminance)
 * @param rx        origin of ref image block
 * @param ry        origin of ref image block
 * @param sx        origin of search image block
 * @param sy        origin of search image block
 * @param size      block size
 * @return SAD for block
 */
float SAD(const cv::Mat &ref, const cv::Mat &search,
          int rx, int ry, float sx, float sy, int size);

/**
 * Save motion vectors
 * @param mv                 the motion vectors to save
 * @param output_filename    name of file to save vectors to
 * @return true if success
 */
bool save_vectors(const std::vector<cv::Vec2f> &mv,
                  const std::string &output_filename);

/**
 * Load motion vectors
 * @param mv_filename        name of the motion vectors file to load
 * @param mv                 the loaded motion vectors
 * @return true if success
 */
bool load_vectors(const std::string &mv_filename,
                  std::vector<cv::Vec2f> &mv);

#endif    // bmsupport_h

