/**
 * @file   klt-tracker.cc
 * @brief  Demonstrate KLT tracking.
 * @author Lyndon Hill
 * @date   2025.10.28
 * */

#include <stdlib.h>
#include <unistd.h>
#include <iostream>
#include <string>
#include <vector>

#include <opencv2/opencv.hpp>
#include <opencv2/features2d.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/video.hpp>

// Help user
void usage(const char *exe)
{
  std::cout << exe << " usage:\n";
  std::cout << " -i  input video filename\n"
            << " -o  output video filename\n"
            << " -n  number of features to track\n"
            << " -l  draw track lines\n"
            << " -h  help; this message\n";
}

/**
 * Detect features using Shi-Tomasi corner detection
 * @param image          input image
 * @param points         detected features
 * @param num_features   number of features to detect
 * @param mask           mask where to detect features
 */
void DetectFeatures(const cv::Mat &image,
                    std::vector<cv::Point2f> &points,
                    int num_features,
                    cv::Mat mask = cv::Mat())
{
  double quality_level = 0.3;
  double min_distance = 7;
  int    block_size = 7;
  bool   use_Harris_detector = false;
  double k = 0.04;

  cv::goodFeaturesToTrack(image, points, num_features, quality_level,
                          min_distance, mask, block_size,
                          use_Harris_detector, k);
}

/**
 * Track features using Lucas-Kanade method
 * @param previous_frame  previous image
 * @param next_frame      next image
 * @param previous_points points previously detected
 * @param next_points     position where previous points were tracked to
 * @param status          status of track
 */
void Track(const cv::Mat &previous_frame,
           const cv::Mat &next_frame,
           const std::vector<cv::Point2f> &previous_points,
           std::vector<cv::Point2f> &next_points,
           std::vector<uchar> &status)
{
  std::vector<float> err;
  cv::TermCriteria criteria = cv::TermCriteria((cv::TermCriteria::COUNT) +
                                             (cv::TermCriteria::EPS), 10, 0.03);
  cv::calcOpticalFlowPyrLK(previous_frame, next_frame,
                           previous_points, next_points,
                           status, err, cv::Size(15, 15), 2, criteria);
}

int main(int argc, char *argv[])
{
  std::string input_filename, output_filename;
  int num_features = 400;
  int min_features = 100;
  int max_frames_between_detect = 10;
  bool draw_lines  = false;

  // Parse command line arguments
  int  c;
  while((c = getopt(argc, argv, "i:o:n:lh")) != -1)
  {
    switch(c) {
      case 'i': input_filename  = optarg;             break;
      case 'o': output_filename = optarg;             break;
      case 'n': num_features    = std::stoi(optarg);  break;
      case 'l': draw_lines      = true;               break;
      case 'h': usage(argv[0]); return(EXIT_SUCCESS); break;
    }
  }

  // Check input parameters
  if(input_filename.empty() || output_filename.empty())
  {
    std::cout << "Error: missing filename, check input and output filenames are specified\n";
    return(EXIT_FAILURE);
  }

  // Open the input video
  cv::VideoCapture capture(input_filename.c_str());
  if(!capture.isOpened())
  {
    std::cerr << "Unable to open file " << input_filename << std::endl;
    return(EXIT_FAILURE);
  }

  // Open the output video
  cv::VideoWriter out;
  auto fourcc = cv::VideoWriter::fourcc('m','p','4','v');
  out = cv::VideoWriter(output_filename.c_str(), fourcc,
                        capture.get(cv::CAP_PROP_FPS),
                        cv::Size((int)capture.get(cv::CAP_PROP_FRAME_WIDTH),
                                 (int)capture.get(cv::CAP_PROP_FRAME_HEIGHT)));

  if(!out.isOpened())
  {
    std::cerr << "Could not open file for writing, " << output_filename << std::endl;
    return(EXIT_FAILURE);
  }

  // Simplified colour map from the Turbo scheme
  std::vector<cv::Scalar> colour_map;
  colour_map.push_back(cv::Scalar(59, 18, 48));
  colour_map.push_back(cv::Scalar(162, 64, 64));
  colour_map.push_back(cv::Scalar(220, 122, 70));
  colour_map.push_back(cv::Scalar(239, 180, 50));
  colour_map.push_back(cv::Scalar(211, 228, 15));
  colour_map.push_back(cv::Scalar(154, 250, 69));
  colour_map.push_back(cv::Scalar(79, 249, 148));
  colour_map.push_back(cv::Scalar(40, 212, 222));
  colour_map.push_back(cv::Scalar(36, 142, 253));
  colour_map.push_back(cv::Scalar(51, 65, 252));

  cv::Mat previous_frame, previous_grey;
  std::vector<cv::Point2f> previous_pts, next_pts;
  std::vector<int> pts_colour;       // colour map index for each point
  int colour_index = 0;              // colour is changed when points are refreshed

  // Grab first frame and detect features in it
  capture >> previous_frame;
  cv::cvtColor(previous_frame, previous_grey, cv::COLOR_BGR2GRAY);
  DetectFeatures(previous_grey, previous_pts, num_features);
  int frames_since_detect = 0;

  pts_colour = std::vector<int>(previous_pts.size(), colour_index);
  cv::Mat overlay = cv::Mat::zeros(previous_frame.size(), previous_frame.type());

  // Main loop
  while(true)
  {
    cv::Mat next_frame, next_grey;
    capture >> next_frame;
    if(next_frame.empty()) break;

    cv::cvtColor(next_frame, next_grey, cv::COLOR_BGR2GRAY);

    std::vector<uchar> status;
    Track(previous_grey, next_grey, previous_pts, next_pts, status);
    std::vector<cv::Point2f> selected_pts;
    std::vector<int> selected_colour;

    if(!draw_lines)
      overlay = cv::Mat::zeros(previous_frame.size(), previous_frame.type());

    for(size_t i = 0; i < previous_pts.size(); i++)
    {
      // Select good points
      if(status[i] == 1)
      {
        selected_pts.push_back(next_pts[i]);

        cv::Scalar colour = colour_map[pts_colour[i]];
        selected_colour.push_back(pts_colour[i]);

        // Draw the tracks
        if(draw_lines) line(overlay, next_pts[i], previous_pts[i], colour, 2);
        circle(next_frame, next_pts[i], 5, colour, -1);
      }
    }
    frames_since_detect++;

    // Detect new features if there are not enough or it's been too long
    // since last detection (refresh)
    if((selected_pts.size() < min_features) ||
       (frames_since_detect >= max_frames_between_detect))
    {
      // Make a mask where there are already features
      // to avoid detecting features too close to each other
      cv::Mat pt_mask = cv::Mat::ones(next_grey.size(), CV_8UC1) * 255;
      for(auto &p : selected_pts)
        cv::circle(pt_mask, p, 15, cv::Scalar(0), -1);

      std::vector<cv::Point2f> new_features;
      DetectFeatures(next_grey, new_features, num_features - selected_pts.size(),
                     pt_mask);
      colour_index++;
      if(colour_index >= colour_map.size()) colour_index = 0;

      for(auto &p : new_features)
      {
        selected_pts.push_back(p);
        selected_colour.push_back(colour_index);
        circle(next_frame, p, 5, colour_map[colour_index], -1);
      }
      frames_since_detect = 0;
    }

    // Overlay the points/tracks on the frame
    cv::Mat img;
    cv::add(next_frame, overlay, img);
    out.write(img);

    // Update the previous frame and points
    previous_grey = next_grey.clone();
    previous_pts.swap(selected_pts);
    pts_colour.swap(selected_colour);
  }

  out.release();
  capture.release();

  return(EXIT_SUCCESS);
}
