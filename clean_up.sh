#!/bin/bash

# Script to clear all __pycache__ directories
# Usage: ./clear_pycaches.sh [start_directory]

# If no argument is provided, start from the current directory
START_DIR=${1:-.}

echo "Searching for __pycache__ directories in: $START_DIR"

# Use 'find' to locate all __pycache__ directories and delete them
find "$START_DIR" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null

if [ $? -eq 0 ]; then
    echo "All __pycache__ directories have been successfully removed."
else
    echo "An error occurred while clearing __pycache__ directories."
fi