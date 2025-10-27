#!/usr/bin/env python3
"""Open evaluation results CSV files and plot comparison.
"""

import numpy as np
import matplotlib.pyplot as plt

def load_csv(filename):
  # Read CSV file in format "Frame index, PSNR, time taken"
  with open(filename, 'r') as f:
    lines = f.readlines()[1:]  # Skip header
    time_taken_list = []
    psnr_list = []
    for line in lines:
      parts = line.strip().split(',')
      psnr_list.append(float(parts[1]))
      time_taken_list.append(int(parts[2]))

    return psnr_list, time_taken_list

def main():

  psnr_2dfs, time_taken_2dfs = load_csv('results_2dfs.csv')
  psnr_pmvfast, time_taken_pmvfast = load_csv('results_pmvfast.csv')

  # Plot PSNR vs frame index
  plt.figure(figsize=(10, 5))
  plt.plot(range(2, 2 + len(psnr_2dfs)), psnr_2dfs, label='2DFS', color='blue')
  plt.plot(range(2, 2 + len(psnr_pmvfast)), psnr_pmvfast, label='PMVFAST', color='red')
  plt.xlabel('Frame Index')
  plt.ylabel('PSNR (dB)')
  plt.title('Motion Compensation Evaluation - Quality')
  plt.legend(loc='upper right')
  plt.grid()
  plt.show()
  # plt.savefig('psnr_comparison.png')

  # Plot time taken vs frame index
  plt.figure(figsize=(10, 5))
  plt.plot(range(2, 2 + len(time_taken_2dfs)), time_taken_2dfs, label='2DFS', color='blue')
  plt.plot(range(2, 2 + len(time_taken_pmvfast)), time_taken_pmvfast, label='PMVFAST', color='red')
  plt.xlabel('Frame Index')
  plt.ylabel('Time Taken (microseconds)')
  plt.title('Motion Compensation Evaluation - Speed')
  plt.legend(loc='upper right')
  plt.grid()
  plt.show()
  # plt.savefig('time_comparison.png')

  psnr_np_2dfs = np.array(psnr_2dfs)
  psnr_np_pmvfast = np.array(psnr_pmvfast)
  time_np_2dfs = np.array(time_taken_2dfs)
  time_np_pmvfast = np.array(time_taken_pmvfast)
  print(f"2DFS: Average PSNR = {np.mean(psnr_np_2dfs):.2f} dB, Average Time = {np.mean(time_np_2dfs):.2f} us")
  print(f"PMVFAST: Average PSNR = {np.mean(psnr_np_pmvfast):.2f} dB, Average Time = {np.mean(time_np_pmvfast):.2f} us")


if __name__ == "__main__":
  main()
