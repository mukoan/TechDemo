/**
 * @file   gfm.cc
 * @brief  Find global translation between images by feature matching
 * @author Lyndon Hill
 * @date   2025.11.16
 */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

#include <opencv2/opencv.hpp>
#include <opencv2/features2d.hpp>

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -c  current image filename\n"
            << " -p  previous image filename\n"
            << " -n  number of features to detect (default 500)\n"
            << " -h  help; this message\n";
}


int main(int argc, char** argv)
{
  std::string current_filename, previous_filename;
  int num_features = 500;

  int  c;
  while((c = getopt(argc, argv, "c:p:n:h")) != -1)
  {
    switch(c) {
      case 'c': current_filename  = optarg;             break;
      case 'p': previous_filename = optarg;             break;
      case 'n': num_features      = std::stoi(optarg);  break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);   break;
    }
  }

  // Check inputs

  if(current_filename.empty() || previous_filename.empty()) {
    std::cout << "Error: image filename was not specified\n";
    return(EXIT_FAILURE);
  }

  // Load images

  cv::Mat current_img, previous_img;
  current_img  = cv::imread(current_filename.c_str(),  cv::IMREAD_GRAYSCALE);
  previous_img = cv::imread(previous_filename.c_str(), cv::IMREAD_GRAYSCALE);

  // Detect ORB features

  std::vector<cv::KeyPoint> keypoints_current, keypoints_previous;
  cv::Mat descriptors_current, descriptors_previous;
  cv::Ptr<cv::ORB> orb = cv::ORB::create(num_features);
  orb->detectAndCompute(current_img,  cv::noArray(), keypoints_current,  descriptors_current);
  orb->detectAndCompute(previous_img, cv::noArray(), keypoints_previous, descriptors_previous);

  // Match features

  std::vector<cv::DMatch> matches;
  cv::BFMatcher matcher(cv::NORM_HAMMING);
  matcher.match(descriptors_current, descriptors_previous, matches);

  if(matches.size() < 10) {
    std::cout << "Error: not enough matches found (" << matches.size() << ")\n";
    return(EXIT_FAILURE);
  }

  // Find the motion of each matched feature

  std::vector<double> mv_x, mv_y;
  for(const auto &match : matches)
  {
    cv::Point2f pt_current  = keypoints_current[match.queryIdx].pt;
    cv::Point2f pt_previous = keypoints_previous[match.trainIdx].pt;
    mv_x.push_back(pt_previous.x - pt_current.x);
    mv_y.push_back(pt_previous.y - pt_current.y);
  }

  // Compute median motion vector

  std::sort(mv_x.begin(), mv_x.end());
  std::sort(mv_y.begin(), mv_y.end());
  double median_x = mv_x[mv_x.size() / 2];
  double median_y = mv_y[mv_y.size() / 2];

  std::cout << "Estimated shift: (" << median_x << ", " << median_y << ")\n";

  return(EXIT_SUCCESS);
}
