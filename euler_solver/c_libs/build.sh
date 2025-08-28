#!/usr/bin/env bash
set -euo pipefail

# Move to the directory where this script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Directories
SRC_DIR="src"
BUILD_DIR="build"
LIBS_DIR="libs"

# Compilation flags
CFLAGS="-Wall -Wextra -O3 -g"
PICFLAGS="-fPIC"
# GMP include and library paths
GMP_INCLUDE="/usr/local/include"
GMP_LIB="/usr/local/lib"
LDFLAGS="-L${GMP_LIB} -lgmp"
CPPFLAGS="-I${GMP_INCLUDE}"

# Create build directory
mkdir -p "${BUILD_DIR}"

# Create libs directory if it doesn't exist
mkdir -p "${LIBS_DIR}"


build_c_file() {
    local c_file="$1"
    local base_name
    base_name=$(basename "$c_file" .c)

    echo "Start Build Shared Library : ${SRC_DIR}/${c_file} -> ${LIBS_DIR}/lib_${base_name}.so"

    # Compile source for shared library (without main)
    gcc ${CFLAGS} ${PICFLAGS} ${CPPFLAGS} -c "${SRC_DIR}/${c_file}" -o "${BUILD_DIR}/${base_name}.o"

    # Create shared library (.so)
    gcc -shared "${BUILD_DIR}/${base_name}.o" -o "${BUILD_DIR}/lib_${base_name}.so" ${LDFLAGS}

    # Copy shared library to libs directory
    cp "${BUILD_DIR}/lib_${base_name}.so" "${LIBS_DIR}/"

    echo "Done Build Shared Library  : ${SRC_DIR}/${c_file} -> ${LIBS_DIR}/lib_${base_name}.so"
    echo
}

# Find and build all .c files in src directory
mapfile -t c_files < <(find "${SRC_DIR}" -name "*.c")

if [ ${#c_files[@]} -eq 0 ]; then
    echo "No .c files found in ${SRC_DIR}"
    exit 1
fi

for c_file in "${c_files[@]}"; do
    build_c_file "$(basename "${c_file}")"
done

# Remove build directory
rm -rf "${BUILD_DIR}"

echo "All builds completed successfully"

