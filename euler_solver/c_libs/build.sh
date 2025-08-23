#!/usr/bin/env bash
set -euo pipefail

# Move to the directory where this script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Directories
SRC_DIR="src"
BUILD_DIR="build"

# Compilation flags
CFLAGS="-Wall -Wextra -O3 -g -fPIC"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Compile source file into object file with debugging and analysis flags
gcc $CFLAGS -c "$SRC_DIR/digit_factorial_chains.c" -o "$BUILD_DIR/digit_factorial_chains.o"

# Create shared library (.so)
gcc -shared "$BUILD_DIR/digit_factorial_chains.o" -o "$BUILD_DIR/digit_factorial_chains.so"

# Create executable with debugging and analysis flags
gcc $CFLAGS "$BUILD_DIR/digit_factorial_chains.o" -o "$BUILD_DIR/digit_factorial_chains"

echo "Build completed successfully: both shared library and executable produced at $BUILD_DIR/"
