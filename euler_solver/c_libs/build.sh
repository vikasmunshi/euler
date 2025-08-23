#!/usr/bin/env bash
set -euo pipefail

# Move to the directory where this script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Directories
SRC_DIR="src"
BUILD_DIR="build"
LIBS_DIR="libs"

# Compilation flags
CFLAGS="-Wall -Wextra -O3 -g"
PICFLAGS="-fPIC"

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Create libs directory if it doesn't exist
mkdir -p "$LIBS_DIR"


build_c_file() {
    local c_file="$1"
    local base_name=$(basename "$c_file" .c)
    
    # Compile source for shared library (without main)
    gcc $CFLAGS $PICFLAGS -c "$SRC_DIR/$c_file" -o "$BUILD_DIR/${base_name}_lib.o"

    # Create shared library (.so)
    gcc -shared "$BUILD_DIR/${base_name}_lib.o" -o "$BUILD_DIR/lib${base_name}.so"

    # Copy shared library to libs directory
    cp "$BUILD_DIR/lib${base_name}.so" "$LIBS_DIR/"

    # Compile source for executable (with main)
    gcc $CFLAGS -DDFCHAINS_BUILD_MAIN -c "$SRC_DIR/$c_file" -o "$BUILD_DIR/${base_name}_main.o"

    # Create executable 
    gcc $CFLAGS "$BUILD_DIR/${base_name}_main.o" -o "$BUILD_DIR/$base_name"

    echo "Build completed successfully:"
    echo " - Shared library: $BUILD_DIR/lib${base_name}.so"
    echo " - Executable    : $BUILD_DIR/$base_name"
}

# Find and build all .c files in src directory
mapfile -t c_files < <(find "$SRC_DIR" -name "*.c")

if [ ${#c_files[@]} -eq 0 ]; then
    echo "No .c files found in $SRC_DIR"
    exit 1
fi

for c_file in "${c_files[@]}"; do
    build_c_file "$(basename "$c_file")"
done
    
echo "All builds completed successfully"

