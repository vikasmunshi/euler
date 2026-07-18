#!/usr/bin/env bash
# Derive the next SemVer release tag from Conventional Commits and create it.
#
# The tag is the project's single source of truth for its version: setuptools-scm
# reads it at build time and freezes the number into the wheel (see
# [tool.setuptools_scm] in pyproject.toml), which `config.version` and the
# `version` shell command then report at runtime. There is no hand-edited number.
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

if (( dry_run )); then
    echo "[dry-run] $last -> $new"
    exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "bump: working tree is dirty — commit or stash before tagging $new" >&2
    exit 1
fi

git tag -a "$new" -m "release $new"
echo "tagged $new (push with: git push origin $new)"
