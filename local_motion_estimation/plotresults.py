#!/usr/bin/env python3
"""Open evaluation results CSV file and plot.   
"""

import matplotlib.pyplot as plt

def main():
  # Read CSV file in format "Frame index, PSNR, time taken"
  with open('evaluation_results.csv', 'r') as f:
    lines = f.readlines()[1:]  # Skip header
    time_taken_list = []
    psnr_list = []
    for line in lines:
      parts = line.strip().split(',')
      psnr_list.append(float(parts[1]))
      time_taken_list.append(int(parts[2]))

  # Plot PSNR and time taken vs frame index on the same graph
  plt.figure(figsize=(10, 5))
  plt.plot(range(2, 2 + len(psnr_list)), psnr_list, label='PSNR (dB)', color='blue')
  plt.xlabel('Frame Index')
  plt.ylabel('PSNR (dB)', color='blue')
  plt.twinx()
  plt.plot(range(2, 2 + len(time_taken_list)), time_taken_list, label='Time Taken (microseconds)', color='red')
  plt.ylabel('Time Taken (microseconds)', color='red')
  plt.title('Motion Compensation Evaluation')
  plt.legend(loc='upper right')
  plt.grid()
  plt.show()  


if __name__ == "__main__":
  main()
