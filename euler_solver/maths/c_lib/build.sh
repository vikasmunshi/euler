#!/usr/bin/env bash
cd "$(dirname "$0")" && {
  python setup.py build_ext --inplace
  rm -rf build/
  rm -f ./*.c
}
