#!/bin/bash

INPUT_DIR=$1
OUTPUT_FILE=$2

if [ -z "$INPUT_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "Usage: ./merge_root.sh <input_directory> <output_file.root>"
  exit 1
fi

hadd -f "$OUTPUT_FILE" "$INPUT_DIR"/*.root

# run this 
# hadd -f UL2017_ScaleFactors.root ./ScaleFactors/*.root