/**
 * @file   fullsearch.cc
 * @brief  Block Matching Algorithm: 2 dimensional full search
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include "fullsearch.h"
#include "bmsupport.h"


// 2D Full Search
std::vector<cv::Vec2f> fullsearch(const cv::Mat &current, const cv::Mat &previous,
                                  int blk_size)
{
  std::vector<cv::Vec2f> mv;

  int blocks_wide = current.cols/blk_size;
  int blocks_high = current.rows/blk_size;

  int xmin, xmax, ymin, ymax;    // bounds of search origin
  float bdm, bestbdm;            // BDM = block distortion measure
  cv::Vec2f bestvec;

  // Process image by block

  for(int by = 0; by < blocks_high; by++)
  {
    for(int bx = 0; bx < blocks_wide; bx++)
    {
      bestvec = cv::Vec2f(0.0, 0.0);
      bestbdm = 1e7;

      int ox = bx*blk_size;
      int oy = by*blk_size;

      // Find bounds of search

      xmin = ox - RANGE; xmax = ox + RANGE;
      ymin = oy - RANGE; ymax = oy + RANGE;

      xmin = std::clamp(xmin, 0, previous.cols);
      xmax = std::clamp(xmax, 0, previous.cols - blk_size);
      ymin = std::clamp(ymin, 0, previous.rows);
      ymax = std::clamp(ymax, 0, previous.rows - blk_size);

      // Search

      for(int y = ymin; y <= ymax; y++)
      {
        for(int x = xmin; x <= xmax; x++)
        {
          bdm = SAD(current, previous, ox, oy, x, y, blk_size);

          // Prefer a (0,0) motion vector; if all is equal
          if((bdm < bestbdm) || ((bdm == bestbdm) && (x == ox) && (y == oy)))
          {
            bestbdm = bdm;
            bestvec[0] = x-ox;
            bestvec[1] = y-oy;
          }
        }
      }

      mv.push_back(bestvec);
    }
  }

  return(mv);
}
