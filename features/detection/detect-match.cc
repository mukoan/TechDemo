/**
 * @file   detect-match.cc
 * @brief  Demonstrate feature detection and matching.
 * @author Lyndon Hill
 * @date   2025.10.28
 * */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <chrono>
#include <vector>

#include <opencv2/opencv.hpp>
#include <opencv2/features2d.hpp>

#ifdef HAVE_SURF
#include <opencv2/xfeatures2d.hpp>
#endif

using namespace std::chrono;


enum FeatureType {
  SIFT,
  SURF,
  ORB
};

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -c  current image filename\n"
            << " -p  previous image filename\n"
            << " -k  keypoints image filename\n"
            << " -m  matches image filename\n"
            << " -n  number of features to detect (default = 2000)\n"
            << " -a  algorithm, either sift (default), surf, or orb\n"
            << " -t  time the algorithm\n"
            << " -h  help; this message\n";
}

int main(int argc, char *argv[])
{
  std::string current_filename;
  std::string previous_filename;
  std::string matches_filename   = "matches.jpg";
  std::string keypoints_filename = "keypoints.jpg";
  std::string algorithm          = "sift";

  int  feature_type = SIFT;
  int  num_features = 2000;
  bool timing       = false;

  // Parse command line arguments
  int  c;
  while((c = getopt(argc, argv, "c:p:k:m:n:a:th")) != -1)
  {
    switch(c) {
      case 'c': current_filename   = optarg;            break;
      case 'p': previous_filename  = optarg;            break;
      case 'k': keypoints_filename = optarg;            break;
      case 'm': matches_filename   = optarg;            break;
      case 'n': num_features       = std::stoi(optarg); break;
      case 'a': algorithm          = optarg;            break;
      case 't': timing = true;                          break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS);   break;
    }
  }

  // Determine feature type
  std::transform(algorithm.begin(), algorithm.end(), algorithm.begin(), ::tolower);
  if(algorithm == "sift")
    feature_type = SIFT;
  else if(algorithm == "surf")
    feature_type = SURF;
  else if(algorithm == "orb")
    feature_type = ORB;
  else
  {
    std::cout << "Error: unknown algorithm type '" << algorithm << "'\n";
    return(EXIT_FAILURE);
  }

  // Check inputs
  if(current_filename.empty() || previous_filename.empty())
  {
    std::cout << "Error: missing filename, check input filenames are specified\n";
    return(EXIT_FAILURE);
  }

  // Load images
  cv::Mat current_img  = cv::imread(current_filename,  cv::IMREAD_GRAYSCALE);
  cv::Mat previous_img = cv::imread(previous_filename, cv::IMREAD_GRAYSCALE);

  if(current_img.empty() || previous_img.empty())
  {
    std::cout << "Error: unable to load one or both input images\n";
    return(EXIT_FAILURE);
  }

  // Create feature detector
  cv::Ptr<cv::Feature2D> detector;
  switch(feature_type)
  {
    case SIFT:
    detector = cv::SIFT::create(num_features);
    break;

    case SURF:
#ifdef HAVE_SURF
    detector = cv::xfeatures2d::SURF::create(num_features);
#else
    std::cerr << "SURF is not available\n";
    return(EXIT_FAILURE);
#endif
    break;

    case ORB:
    detector = cv::ORB::create(num_features);
    break;

    default:
    std::cout << "Error: unknown feature type\n";
    return(EXIT_FAILURE);
  }

  time_point<steady_clock> start;
  if(timing) start = steady_clock::now();

  // Keypoints and descriptors for current and previous images
  std::vector<cv::KeyPoint> keypoints_c, keypoints_p;
  cv::Mat descriptors_c, descriptors_p;

  // Detect keypoints and compute descriptors
  detector->detectAndCompute(current_img,  cv::noArray(), keypoints_c, descriptors_c);
  detector->detectAndCompute(previous_img, cv::noArray(), keypoints_p, descriptors_p);

  // Match features
  std::vector<cv::DMatch> matches;
  cv::BFMatcher matcher(cv::NORM_L2);
  matcher.match(descriptors_c, descriptors_p, matches);

  if(timing) {
    time_point<steady_clock> stop = steady_clock::now();
    auto duration = duration_cast<microseconds>(stop - start);
    std::cout << "Time taken: " << duration.count() << " microseconds\n";
  }

  std::cout << "Matched " << matches.size() << " features\n";

  cv::Scalar blue  = cv::Scalar(255, 0, 0);  // keypoint colour
  cv::Scalar green = cv::Scalar(0, 255, 0);  // good match colour
  cv::Scalar red   = cv::Scalar(0, 0, 255);  // unmatched keypoint colour

  // Draw keypoints on current image
  cv::Mat current_keypoints_img;
  cv::drawKeypoints(current_img, keypoints_c, current_keypoints_img, blue);
  cv::imwrite(keypoints_filename, current_keypoints_img);

  // Draw matches
  cv::Mat matches_img;
  cv::drawMatches(current_img, keypoints_c, previous_img, keypoints_p,
                  matches, matches_img, green, red);
  cv::imwrite(matches_filename, matches_img);

  return(EXIT_SUCCESS);
}
