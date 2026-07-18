#!/usr/bin/env bash
# Derive the next SemVer release from Conventional Commits, then bump, tag, and push it.
#
# This script is the SINGLE writer of the version. `solver/version.py` (tracked)
# is the source of truth: pyproject.toml stamps it into the wheel at build time
# and `config.version` / the `version` shell command report it at runtime. A
# release rewrites that file, commits it, tags the commit `vX.Y.Z`, and pushes the
# commit + tag to origin — so the file, the tag, and the wheel metadata always
# agree, and origin never lags a local-only release (which stranded collaborator
# clones behind a redeployed venv). There is no hand-edited number, no build-time
# git. Publishing the tag is the step most easily forgotten by hand, so it is not
# left to the caller.
#
# Bump rule — scan `<last-tag>..HEAD` subjects/bodies for Conventional-Commit
# markers and take the highest present:
#   * `feat!:` / `fix!:` / a `BREAKING CHANGE:` body  → MAJOR
#   * any `feat:` / `feat(scope):`                     → MINOR
#   * anything else (fix, perf, refactor, …)           → PATCH
#
# Releasing is a deliberate step, run by a maintainer from a clean checkout — not
# automatic on push. Pass --dry-run to preview the release and exit, or --no-push
# to bump/commit/tag locally but stop before publishing to origin.
#
# Usage:
#   scripts/version/bump.sh [--dry-run] [--no-push]
set -uo pipefail

declare dry_run=0 no_push=0
for arg in "$@"; do
    case "${arg}" in
        --dry-run) dry_run=1 ;;
        --no-push) no_push=1 ;;
        *) echo "bump: unknown argument '${arg}'" >&2; exit 1 ;;
    esac
done

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
    tail_action="commits, tags, then pushes to origin"
    (( no_push )) && tail_action="commits, then tags (no push)"
    echo "[dry-run] $last -> $new (writes $number to solver/version.py, ${tail_action})"
    exit 0
fi

# Cleanliness via `git status --porcelain`, NOT `git diff`: the transparent
# encryption filter (solutions/private/**) re-encrypts to fresh ciphertext on
# every read, so `git diff --quiet` reports phantom churn on an otherwise clean
# tree. `git status` refreshes the index and ignores that noise.
if [[ -n "$(git status --porcelain)" ]]; then
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

if (( no_push )); then
    echo "not pushed (--no-push); publish with: git push origin HEAD $new"
    exit 0
fi

# Push the release commit AND the tag together. Without the tag on origin, every
# collaborator clone's `git describe` anchors to the previous release and a
# redeployed venv runs ahead of what any clone can reach. A push failure is not
# rolled back — the commit and tag are valid locally; report and let the caller
# retry, since the tree is already the release state.
echo "pushing $new (commit + tag) to origin..."
if ! git push origin HEAD "$new"; then
    echo "bump: push FAILED — $new is committed and tagged locally but NOT on origin." >&2
    echo "  retry with: git push origin HEAD $new" >&2
    exit 1
fi
echo "pushed $new to origin — remember to 'make redeploy-web' to ship it"
