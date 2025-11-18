/**
 * @file   pmvfast.cc
 * @brief  Block Matching Algorithm: PMVFAST
 * @author Lyndon Hill
 * @date   2025.10.01
 */

#include <iostream>
#include <algorithm>
#include <numeric>

#include "pmvfast.h"
#include "bmsupport.h"


// Check that location (sx, sy) is valid for a block within the image bounds
bool is_valid(float sx, float sy, int blk_size, const cv::Mat &img);

// pmvfast
std::vector<cv::Vec2f> pmvfast(const cv::Mat &current, const cv::Mat &previous,
                               int blk_size)
{
  int blocks_wide = current.cols/blk_size;
  int blocks_high = current.rows/blk_size;

  std::vector<cv::Vec2f> motion(blocks_wide*blocks_high);

  int medx, medy;
  float min_sad;
  int T1, T2;

  int K = 1536;            // See section 4, paragraph 3 of paper for value of K
  int med_vec_stop = 256;
  float T1_min  = 512.0;
  float T1_max  = 1024.0;
  int T2_offset = 256;

  if(blk_size == 8) {
    K = 384;
    med_vec_stop = 64;
    T1_min = 128;
    T1_max = 256;
    T2_offset = 64;
  }

  // Main algorithm

  for(int by = 0; by < blocks_high; by++)
  {
    for(int bx = 0; bx < blocks_wide; bx++)
    {
      int ox = bx*blk_size;
      int oy = by*blk_size;

      // 1. Check SAD of median vector; if less than 256 then stop
      //    Predictors are left, top and top right blocks

      std::vector<cv::Vec2f> predictors;
      if(bx > 0) predictors.push_back(motion[by*blocks_wide + (bx-1)]);
      if(by > 0) {
        predictors.push_back(motion[(by-1)*blocks_wide + bx]);
        if(bx < blocks_wide-1)
          predictors.push_back(motion[(by-1)*blocks_wide + (bx+1)]);
      }

      switch(predictors.size())
      {
        case 0:
        medx = 0; medy = 0;
        break;

        case 1:
        medx = predictors[0][0]; medy = predictors[0][1];
        break;

        case 2:
        medx = (predictors[0][0] + predictors[1][0])/2;
        medy = (predictors[0][1] + predictors[1][1])/2;
        break;

        default:
        std::vector<float> px, py;
        for(auto v : predictors)
        {
          px.push_back(v[0]);
          py.push_back(v[1]);
        }
        std::sort(px.begin(), px.end());
        std::sort(py.begin(), py.end());
        medx = px[px.size()/2];
        medy = py[py.size()/2];
      }

      // Check median vector is valid

      if(is_valid(ox+medx, oy+medy, blk_size, previous))
      {
        float med_sad = SAD(current, previous, ox, oy,
                            ox+medx, oy+medy, blk_size);
        if(med_sad < med_vec_stop)
        {
          // Early termination
          motion[by*blocks_wide + bx] = cv::Vec2f(medx, medy);
          continue;
        }
      }

      // 2. Calculate minimum SAD of predictors

      cv::Vec2f best_predictor;
      min_sad = 10000;

      for(int p = 0; p < predictors.size(); p++)
      {
        if(is_valid(ox+predictors[p][0], oy+predictors[p][1], blk_size, previous))
        {
          float pred_sad = SAD(current, previous, ox, oy,
                               ox+predictors[p][0], oy+predictors[p][1], blk_size);

          if(pred_sad < min_sad) {
            best_predictor = predictors[p];
            min_sad = pred_sad;
          }
        }
      }

      T1 = std::clamp(min_sad, T1_min, T1_max);   // See section 4, paragraph 1
      T2 = min_sad + T2_offset;                   // Section 4, paragraph 3

      // Best predictor is used as centre of search in next step
      motion[by*blocks_wide + bx] = best_predictor;

      // 3. Check predictors to decide search type:
      //    Calculate magnitude of median vector = magmed
      //     If magmed = 0 and T2 is large then use large diamond search,
      //     else use small diamond
      bool use_small_diamond = false;

      float magmed = sqrt((medx*medx)+(medy*medy));

      if((magmed < 0.1) && (T2 < K)) {
        use_small_diamond = true;
      }

      // 4. Diamond search from best predictor
      if(use_small_diamond)
        small_diamond_search(current, previous, bx, by, blk_size, motion);
      else
        large_diamond_search(current, previous, bx, by, blk_size, motion);
    }
  }

  return(motion);
}

void large_diamond_search(const cv::Mat &current, const cv::Mat &previous,
                          int blockx, int blocky, int blk_size,
                          std::vector<cv::Vec2f> &mv)
{
  int blocks_wide = current.cols/blk_size;
  int ox = blockx*blk_size;
  int oy = blocky*blk_size;
  int mv_block_index = blocky*blocks_wide + blockx;

  // We keep a list of which candidate positions to check because when the
  // search pattern moves we only need to calculate new positions.

  std::vector<cv::Vec2f> search_mv(9);
  std::vector<int> candidate_pos(9);
  std::iota(candidate_pos.begin(), candidate_pos.end(), 0);

  float best_sad = 1e7;
  int   best_mv_pos = 0;
  bool  process = true;

  while(process)
  {
    cv::Vec2f centre_mv = mv[mv_block_index];
    search_mv[0] = centre_mv;
    search_mv[1] = centre_mv; search_mv[1][1] -= 2;  // up
    search_mv[2] = centre_mv; search_mv[2][0] += 2;  // right
    search_mv[3] = centre_mv; search_mv[3][1] += 2;  // down
    search_mv[4] = centre_mv; search_mv[4][0] -= 2;  // left
    search_mv[5] = centre_mv; search_mv[5][0]++; search_mv[5][1]--; // right-up
    search_mv[6] = centre_mv; search_mv[6][0]++; search_mv[6][1]++; // right-down
    search_mv[7] = centre_mv; search_mv[7][0]--; search_mv[7][1]++; // left-down
    search_mv[8] = centre_mv; search_mv[8][0]--; search_mv[8][1]--; // left-up

    // std::cout << " (L) current vector " << centre_mv << "\n";

    // Get SAD for each candidate

    for(int cand_no : candidate_pos)
    {
      // std::cout << " (L) evaluate candidate " << cand_no << "\n";

      if(is_valid(ox+search_mv[cand_no][0], oy+search_mv[cand_no][1], blk_size, previous))
      {
        float bdm = SAD(current, previous, ox, oy,
                        ox+search_mv[cand_no][0], oy+search_mv[cand_no][1],
                        blk_size);

        // std::cout << "    sad[" << cand_no << "] = " << bdm << "\n";
        if(bdm < best_sad) {
          best_mv_pos = cand_no;
          best_sad = bdm;
        }
      }
      // else
        // std::cout << "    invalid\n";
    }

    // std::cout << "    best sad = " << best_sad << "\n";
    // std::cout << "    best pos = " << best_mv_pos << "\n";

    // Update next candidate search positions

    candidate_pos.clear();

    switch(best_mv_pos)
    {
      case 0:  // centre
      process = false;
      break;

      case 1:  // move up
      candidate_pos.assign({4,8,1,5,2});
      break;

      case 2:  // move right
      candidate_pos.assign({1,5,2,6,3});
      break;

      case 3:  // move down
      candidate_pos.assign({2,6,3,7,4});
      break;

      case 4:  // move left
      candidate_pos.assign({3,7,4,8,1});
      break;

      case 5:  // move up-right
      candidate_pos.assign({1,5,2});
      break;

      case 6:  // move down-right
      candidate_pos.assign({2,6,3});
      break;

      case 7:  // move down-left
      candidate_pos.assign({3,7,4});
      break;

      case 8:  // move up-left
      candidate_pos.assign({4,8,1});
      break;
    }

    if(process) mv[mv_block_index] = search_mv[best_mv_pos];
    best_mv_pos = 0;
  }
}

void small_diamond_search(const cv::Mat &current, const cv::Mat &previous,
                          int blockx, int blocky, int blk_size,
                          std::vector<cv::Vec2f> &mv)
{
  int  blocks_wide = current.cols/blk_size;
  int  ox = blockx*blk_size;
  int  oy = blocky*blk_size;
  int  mv_block_index = blocky*blocks_wide + blockx;

  // We keep a list of which candidate positions to check because when the
  // search pattern moves we only need to calculate new positions.

  std::vector<cv::Vec2f> search_mv(5);
  std::vector<int> candidate_pos(5);
  std::iota(candidate_pos.begin(), candidate_pos.end(), 0);

  float best_sad = 1e7;
  int   best_mv_pos = 0;
  bool  process = true;

  while(process)
  {
    cv::Vec2f centre_mv = mv[mv_block_index];
    search_mv[0] = centre_mv;
    search_mv[1] = centre_mv; search_mv[1][1]--;  // up
    search_mv[2] = centre_mv; search_mv[2][0]++;  // right
    search_mv[3] = centre_mv; search_mv[3][1]++;  // down
    search_mv[4] = centre_mv; search_mv[4][0]--;  // left

    // std::cout << " (S) current vector " << centre_mv << "\n";

    // Get SAD for each candidate

    for(int cand_no : candidate_pos)
    {
      //std::cout << " (S) evaluate candidate " << cand_no << "\n";
      // int cand_no = candidate_pos[m];

      if(is_valid(ox+search_mv[cand_no][0], oy+search_mv[cand_no][1], blk_size, previous))
      {
        float bdm = SAD(current, previous, ox, oy,
                        ox+search_mv[cand_no][0], oy+search_mv[cand_no][1],
                        blk_size);

        // std::cout << "    sad[" << cand_no << "] = " << bdm << "\n";
        if(bdm < best_sad) {
          best_mv_pos = cand_no;
          best_sad = bdm;
        }
      }
      // else
        // std::cout << "    invalid\n";
    }

    // std::cout << "    best sad = " << best_sad << "\n";
    // std::cout << "    best pos = " << best_mv_pos << "\n";

    // Update next candidate search positions

    candidate_pos.clear();

    switch(best_mv_pos)
    {
      case 0:  // centre
      process = false;
      break;

      case 1:  // move up
      candidate_pos.assign({1,2,4});
      break;

      case 2:  // move right
      candidate_pos.assign({1,2,3});
      break;

      case 3:  // move down
      candidate_pos.assign({2,3,4});
      break;

      case 4:  // move left
      candidate_pos.assign({3,4,1});
      break;
    }

    if(process) mv[mv_block_index] = search_mv[best_mv_pos];
    best_mv_pos = 0;
  }
}

// Check search location is valid
bool is_valid(float sx, float sy, int blk_size, const cv::Mat &img)
{
  if((sx >= 0) && (sy >= 0) &&
     (sx+blk_size < img.cols) &&
     (sy+blk_size < img.rows))
    return(true);
  else
    return(false);
}
