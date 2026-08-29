#!/usr/bin/env bash
#
# File  : select.sh
# Brief : Select frames from directory of numbered images
# Author: Lyndon Hill
# Date  : 2026.06.16

# Check if the correct number of arguments are provided
if [ "$#" -ne 5 ]; then
  echo "Usage: $0 <input_format> <output_directory> <start_frame> <increment> <end_frame>"
  echo "Example: $0 'image%05d.jpg' 'output' 200 10 300"
  exit 1
fi

# Assign arguments to variables
INPUT_FORMAT="$1"
OUTPUT_DIR="$2"
CURRENT_FRAME=$3
INCREMENT=$4
END_FRAME=$5

# Validate that start frame and increment are positive integers
if ! [[ "$CURRENT_FRAME" =~ ^[0-9]+$ ]] || ! [[ "$INCREMENT" =~ ^[0-9]+$ ]]; then
  echo "Error: Start frame and increment must be positive integers."
  exit 1
fi

# Validate that end frame is a positive integer and greater than or equal to start frame
if ! [[ "$END_FRAME" =~ ^[0-9]+$ ]] || [ "$END_FRAME" -lt "$CURRENT_FRAME" ]; then
  echo "Error: End frame must be a positive integer and greater than or equal to start frame."
  exit 1
fi

# Create the output directory if it doesn't already exist
if [ ! -d "$OUTPUT_DIR" ]; then
  echo "Output directory '$OUTPUT_DIR' does not exist. Creating it..."
  mkdir -p "$OUTPUT_DIR"
fi

echo "Starting selection and copy operation..."
echo "----------------------------------------"

COPIED_COUNT=0

# Loop indefinitely until a file is not found
while true; do
  # Generate the source filename
  SRC_FILE=$(printf "$INPUT_FORMAT" "$CURRENT_FRAME")

  # Check if the source file exists
  if [ -f "$SRC_FILE" ]; then
    # Copy the file to the target output directory
    cp "$SRC_FILE" "$OUTPUT_DIR/"
    echo "Copied: $SRC_FILE -> $OUTPUT_DIR/"

    # Increment the counter and the frame number
    ((COPIED_COUNT++))
    ((CURRENT_FRAME += INCREMENT))

    # Exit loop if beyond end frame
    if [ $CURRENT_FRAME -gt $END_FRAME ]; then
      break
    fi
  else
    # Break the loop if the file does not exist
    echo "----------------------------------------"
    echo "File not found: $SRC_FILE"
    echo "Sequence broken or reached the end of available files."
    break
  fi
done

echo "Successfully copied $COPIED_COUNT files to '$OUTPUT_DIR'."
