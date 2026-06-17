#!/bin/bash
# Fix for PyCharm translucent overlay issue on WSL2
# This script disables problematic graphics backends (Metal and Compose rendering)
# and forces X11 rendering, which is more stable on WSL2.

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fixes to apply
declare -a FIXES=(
    "-Dsun.java2d.metal=false"
    "-Dcompose.swing.render.on.graphics=false"
    "-Dawt.toolkit.name=xlib"
)

fix_vmoptions_file() {
    local file=$1

    if [[ ! -f "$file" ]]; then
        echo -e "${YELLOW}File not found: $file${NC}"
        return 1
    fi

    echo "Processing: $file"
    local modified=false

    for fix in "${FIXES[@]}"; do
        if grep -q "^${fix}$" "$file"; then
            echo -e "${GREEN}  ✓ Already present: $fix${NC}"
        else
            echo "$fix" >> "$file"
            echo -e "${GREEN}  ✓ Added: $fix${NC}"
            modified=true
        fi
    done

    if [[ "$modified" == true ]]; then
        echo -e "${GREEN}  Modified: $file${NC}"
    fi

    return 0
}

main() {
    echo "PyCharm WSL2 Dimmed Overlay Fix"
    echo "================================"
    echo ""

    # Find PyCharm config directories
    local config_dir="$HOME/.config/JetBrains"

    if [[ ! -d "$config_dir" ]]; then
        echo -e "${RED}Error: PyCharm config directory not found at $config_dir${NC}"
        exit 1
    fi

    echo "Found PyCharm config directory: $config_dir"
    echo ""

    # Process all PyCharm versions
    local found_any=false
    for pycharm_version_dir in "$config_dir"/PyCharm*/; do
        if [[ -d "$pycharm_version_dir" ]]; then
            local version_name=$(basename "$pycharm_version_dir")
            local vmoptions_file="$pycharm_version_dir/pycharm64.vmoptions"

            echo "Version: $version_name"

            if [[ ! -f "$vmoptions_file" ]]; then
                echo -e "${YELLOW}  vmoptions file not found, creating it${NC}"
                touch "$vmoptions_file"
            fi

            if fix_vmoptions_file "$vmoptions_file"; then
                found_any=true
            fi
            echo ""
        fi
    done

    if [[ "$found_any" == false ]]; then
        echo -e "${YELLOW}No PyCharm installations were modified${NC}"
        exit 1
    fi

    echo -e "${GREEN}Fix applied successfully!${NC}"
    echo ""
    echo "Please restart PyCharm for changes to take effect."
    echo ""
    echo "What this fix does:"
    echo "  • Disables Metal rendering (macOS only, incompatible with WSL2)"
    echo "  • Disables Compose graphics rendering (unstable on WSL2)"
    echo "  • Forces X11 rendering (stable on WSL2)"
    echo ""
}

main "$@"
