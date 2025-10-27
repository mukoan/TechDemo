/**
 * @file   blockcompensate.cc
 * @brief  Block Motion Compensation
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include <iostream>

#include "blockcompensate.h"
#include "bmsupport.h"


// Apply motion to image
void block_compensate(const cv::Mat &previous_image,
                      const std::vector<cv::Vec2f> &mv,
                      int blk_size,
                      cv::Mat &output_image)
{
  // Set up output image
  output_image = cv::Mat(previous_image.rows, previous_image.cols,
                         previous_image.type());


  // Calculate dimensions of motion field

  int blocks_wide = previous_image.cols/blk_size;
  int blocks_high = previous_image.rows/blk_size;

  if(mv.size() != blocks_wide*blocks_high)
  {
    std::cerr << "Error: wrong motion field size\n";
    return;
  }

  // Compensate blocks

  int x, y;
  int boff;

  for(int by = 0; by < blocks_high; by++)
  {
    for(int bx = 0; bx < blocks_wide; bx++)
    {
      for(int j = 0; j < blk_size; j++)
      {
        y = by*blk_size+j;

        for(int i = 0; i < blk_size; i++)
        {
          x = bx*blk_size+i;
          boff = by*blocks_wide;

          output_image.at<unsigned char>(y, x) =
                interpolate(previous_image, x+mv[boff+bx][0], y+mv[boff+bx][1]);
        }
      }
    }
  }
}
