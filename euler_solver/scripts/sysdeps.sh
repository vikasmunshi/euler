#!/usr/bin/env bash
set -euo pipefail

detect_os() {
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt >/dev/null; then echo "debian"; return; fi
    if command -v dnf >/dev/null; then echo "fedora"; return; fi
    if command -v pacman >/dev/null; then echo "arch"; return; fi
    echo "linux-unknown"; return
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"; return
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "windows"; return
  fi
  echo "unknown"
}

os="$(detect_os)"
case "$os" in
  debian)
    sudo apt update
    sudo apt install -y python3-tk g++ primesieve libprimesieve-dev python3.12-dev
    ;;
  fedora)
    sudo dnf install -y python3-tkinter gcc-c++ primesieve primesieve-devel python3.12-devel
    ;;
  arch)
    sudo pacman -S --needed tk gcc primesieve python
    ;;
  macos)
    if ! command -v brew >/dev/null; then
      echo "Homebrew not found. Install from https://brew.sh" >&2; exit 1
    fi
    brew install python-tk primesieve
    ;;
  windows)
    echo "Windows: Tkinter ships with official Python; primesieve wheel usually suffices."
    ;;
  *)
    echo "Unsupported/unknown OS. Please install dependencies manually." >&2; exit 2
    ;;
esac

echo "System dependencies installed."