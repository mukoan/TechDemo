/**
 * @file   subpixel.cc
 * @brief  Sub pixel block matching
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include "subpixel.h"


// Subpixel motion estimation
void subpixel_search(const cv::Mat &current, const cv::Mat &previous,
                     int blk_size, std::vector<cv::Vec2f> &motion)
{
  int blocks_wide = current.cols/blk_size;
  int blocks_high = current.rows/blk_size;

  for(int by = 0; by < blocks_high; by++)
  {
    for(int bx = 0; bx < blocks_wide; bx++)
    {
      int ox = bx*blk_size;
      int oy = by*blk_size;

      cv::Vec2f integer_vec = motion[by*blocks_wide + bx];
      cv::Vec2f best_vec = integer_vec;

      int x, y;
      float error;
      float best = 1e7;

      // Set up limits

      int minx, miny, maxx, maxy;
      minx = -3; maxx = 3; miny = -3; maxy = 3;

      if(ox+integer_vec[0]+blk_size >= previous.cols)
        maxx = 0;
      if(oy+integer_vec[1]+blk_size >= previous.rows)
        maxy = 0;

      if(ox+integer_vec[0] <= 0)
        minx = 0;
      if(oy+integer_vec[1] <= 0)
        miny = 0;

      // Find best subpixel match

      for(y = miny; y <= maxy; y++)
      {
        for(x = minx; x <= maxx; x++)
        {
          float dx = integer_vec[0]+(x*0.25);
          float dy = integer_vec[1]+(y*0.25);
          error = SAD(current, previous, ox, oy, ox+dx, oy+dy, blk_size);

          if(error < best)
          {
            best = error;
            best_vec[0] = dx;
            best_vec[1] = dy;
          }
        }
      }

      motion[by*blocks_wide + bx] = best_vec;
    }
  }
}
