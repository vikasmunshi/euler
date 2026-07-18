#!/usr/bin/env bash
# Derive the next SemVer release from Conventional Commits, then bump and tag it.
#
# This script is the SINGLE writer of the version. `solver/version.py` (tracked)
# is the source of truth: pyproject.toml stamps it into the wheel at build time
# and `config.version` / the `version` shell command report it at runtime. A
# release rewrites that file, commits it, and tags the commit `vX.Y.Z` — so the
# file, the tag, and the wheel metadata always agree. There is no hand-edited
# number and no build-time git.
#
# Bump rule — scan `<last-tag>..HEAD` subjects/bodies for Conventional-Commit
# markers and take the highest present:
#   * `feat!:` / `fix!:` / a `BREAKING CHANGE:` body  → MAJOR
#   * any `feat:` / `feat(scope):`                     → MINOR
#   * anything else (fix, perf, refactor, …)           → PATCH
#
# Tagging is a deliberate release step, run by a maintainer from a clean checkout
# — not automatic on push. Pass --dry-run to preview the computed tag and exit.
#
# Usage:
#   scripts/version/bump.sh [--dry-run]
set -uo pipefail

declare dry_run=0
[[ "${1:-}" == "--dry-run" ]] && dry_run=1

# The last release anchor, or v0.0.0 when none exists yet (the pre-first-tag case).
last=$(git describe --tags --abbrev=0 --match 'v*' 2>/dev/null || echo v0.0.0)

IFS=. read -r major minor patch <<<"${last#v}"
if [[ -z "${major:-}" || -z "${minor:-}" || -z "${patch:-}" ]]; then
    echo "bump: cannot parse last tag '$last' as vMAJOR.MINOR.PATCH" >&2
    exit 1
fi

# The commit log to classify: everything since the last tag (all of history when
# there is no tag yet, so the very first release still classifies correctly).
if [[ "$last" == "v0.0.0" ]] && ! git rev-parse -q --verify "$last" >/dev/null 2>&1; then
    range="HEAD"
else
    range="${last}..HEAD"
fi
log=$(git log --format='%s%n%b' "$range")

if [[ -z "$log" ]]; then
    echo "bump: no commits since $last — nothing to release" >&2
    exit 1
fi

if grep -qE '^[a-z]+(\([^)]+\))?!:|BREAKING CHANGE' <<<"$log"; then
    major=$((major + 1)); minor=0; patch=0
elif grep -qE '^feat(\([^)]+\))?:' <<<"$log"; then
    minor=$((minor + 1)); patch=0
else
    patch=$((patch + 1))
fi
new="v${major}.${minor}.${patch}"
number="${new#v}"
version_file="$(git rev-parse --show-toplevel)/solver/version.py"

if (( dry_run )); then
    echo "[dry-run] $last -> $new (writes $number to solver/version.py, commits, then tags)"
    exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "bump: working tree is dirty — commit or stash before releasing $new" >&2
    exit 1
fi

# Rewrite ONLY the number in the source of truth (leaving the docstring and the
# `version = __version__` alias intact), commit it, then tag THAT commit — so the
# tag, solver/version.py, and the wheel built from it all name $number.
if ! grep -qE "^__version__ = '[^']*'" "$version_file"; then
    echo "bump: cannot find the __version__ line in $version_file" >&2
    exit 1
fi
sed -i -E "s/^__version__ = '[^']*'/__version__ = '${number}'/" "$version_file"
git add "$version_file"
git commit -q -m "chore(release): $new"
git tag -a "$new" -m "release $new"
echo "released $new — solver/version.py bumped, committed, and tagged"
echo "push with: git push origin HEAD $new"
