#!/usr/bin/env bash
# Flip the front-end symlinks the web server serves:
#
#   code.css / code.html / code.js  ->  <editor>/code.*   (codejar | codemirror)
#   solver-theme.css                ->  solver-theme-<variant>.css   (dark | light)
#
# The app serves these names verbatim (see app.py `_STATIC_FILES`), following the
# symlink, so repointing the link swaps the implementation with no code change.
#
# Usage:
#   ./switch.sh                       show the current targets
#   ./switch.sh editor [codejar|codemirror]   set (or toggle) the code editor
#   ./switch.sh theme  [dark|light]           set (or toggle) the terminal theme
set -euo pipefail

# Operate relative to this script so it works from any working directory.
cd "$(dirname "$(readlink -f "$0")")"

# editor key -> directory holding code.css / code.html / code.js
declare -A EDITOR_DIR=( [codejar]=code-jar [codemirror]=code-mirror-6 )
CODE_FILES=(code.css code.html code.js)

die() { echo "switch.sh: $*" >&2; exit 1; }

# Echo the editor key currently targeted by the code.* links (or 'unknown').
current_editor() {
    local target dir
    target=$(readlink code.html 2>/dev/null) || { echo unknown; return; }
    dir=${target%/*}
    for key in "${!EDITOR_DIR[@]}"; do
        [[ ${EDITOR_DIR[$key]} == "$dir" ]] && { echo "$key"; return; }
    done
    echo unknown
}

# Echo the theme variant currently targeted by solver-theme.css (or 'unknown').
current_theme() {
    local target
    target=$(readlink solver-theme.css 2>/dev/null) || { echo unknown; return; }
    case $target in
        solver-theme-dark.css) echo dark ;;
        solver-theme-light.css) echo light ;;
        *) echo unknown ;;
    esac
}

set_editor() {
    local key=$1 dir=${EDITOR_DIR[$1]}
    for f in "${CODE_FILES[@]}"; do
        [[ -f $dir/$f ]] || die "missing $dir/$f"
        ln -sfn "$dir/$f" "$f"
    done
    echo "editor -> $key ($dir/)"
}

set_theme() {
    local variant=$1 file="solver-theme-$1.css"
    [[ -f $file ]] || die "missing $file"
    ln -sfn "$file" solver-theme.css
    echo "theme -> $variant ($file)"
}

status() {
    echo "editor: $(current_editor)   (code.* -> $(readlink code.html 2>/dev/null || echo '?'))"
    echo "theme : $(current_theme)   (solver-theme.css -> $(readlink solver-theme.css 2>/dev/null || echo '?'))"
}

case "${1:-status}" in
    editor)
        choice=${2:-}
        if [[ -z $choice ]]; then  # no explicit target: toggle
            [[ $(current_editor) == codejar ]] && choice=codemirror || choice=codejar
        fi
        [[ -n ${EDITOR_DIR[$choice]:-} ]] || die "unknown editor '$choice' (codejar|codemirror)"
        set_editor "$choice"
        ;;
    theme)
        choice=${2:-}
        if [[ -z $choice ]]; then  # no explicit target: toggle
            [[ $(current_theme) == dark ]] && choice=light || choice=dark
        fi
        [[ $choice == dark || $choice == light ]] || die "unknown theme '$choice' (dark|light)"
        set_theme "$choice"
        ;;
    status|'')
        status
        ;;
    -h|--help|help)
        sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
        ;;
    *)
        die "unknown command '$1' (editor|theme|status)"
        ;;
esac