/**
 * @file   bmsupport.cc
 * @brief  Block matching support functions
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include <cmath>
#include <iostream>
#include <fstream>

#if __cplusplus >= 202002L
#include <span>
#endif

#include "bmsupport.h"


// Bilinear interpolation
unsigned char interpolate(const cv::Mat &img, float fx, float fy)
{
  if(img.channels() != 1) return(0);                  // Wrong image type
  if((fx >= img.cols) || (fy >= img.rows)) return(0); // Off image

  int ix, iy;
  float a, b;

  ix = (int)(std::floor(fx));
  iy = (int)(std::floor(fy));
  a  = fx - (float)(ix);
  b  = fy - (float)(iy);

  float g, h, i, j;     // Neighbouring pixel values
  g = 0.0; h = 0.0; i = 0.0; j = 0.0;

  int wide = img.cols; int high = img.rows;
  int ix1 = ix+1;
  int iy1 = iy+1;

  if((ix >= 0) || (ix < wide))
  {
    if(iy >= 0)
    {
      if(iy < high)  g = img.at<unsigned char>(iy, ix);
      if(iy1 < high) h = img.at<unsigned char>(iy1, ix);
    }
  }

  if((ix1 >= 0) && (ix1 < wide))
  {
    if(iy >= 0)
    {
      if(iy < high)  i = img.at<unsigned char>(iy, ix1);
      if(iy1 < high) j = img.at<unsigned char>(iy1, ix1);
    }
  }

  float oma, omb, omab;
  oma = 1.0-a;
  omb = 1.0-b;
  omab = oma*omb;

  float ab = a*b;
  float aomb = a*omb;
  float boma = b*oma;

  return(std::roundf(omab*g + boma*h + aomb*i + ab*j));
}

// Calculate block distortion metric
float SAD(const cv::Mat &ref, const cv::Mat &search,
          int rx, int ry, float sx, float sy, int size)
{
  int x, y;
  float sad = 0.0;

  for(y = 0; y < size; y++)
  {
    for(x = 0; x < size; x++)
    {
      sad += std::abs(ref.at<unsigned char>(ry+y, rx+x) -
                      interpolate(search, sx+x, sy+y));
    }
  }

  return(sad);
}

// Save motion vectors
bool save_vectors(const std::vector<cv::Vec2f> &mv,
                  const std::string &output_filename)
{
  std::ofstream output(output_filename, std::ios_base::binary);
  if(!output) return(false);

#if __cplusplus >= 202002L
  const std::span<const cv::Vec2f> blob = mv;

  output.write(reinterpret_cast<const char *>(blob.data()),
               blob.size()*sizeof(cv::Vec2f));
#else
  for(size_t i = 0; i < mv.size(); i++)
  {
    output.write(reinterpret_cast<const char *>(&mv[i]),
                 sizeof(cv::Vec2f));
  }
#endif

  return(static_cast<bool>(output));
}

// Load motion vectors
bool load_vectors(const std::string &mv_filename, std::vector<cv::Vec2f> &mv)
{
  std::ifstream input(mv_filename, std::ios_base::binary);
  if(!input) return(false);

  while(true)
  {
    cv::Vec2f vec;
    if(!input.read(reinterpret_cast<char *>(&vec), sizeof(cv::Vec2f))) break;
    mv.push_back(vec);
  }

  return(true);
}
