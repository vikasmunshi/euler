---
name: claude-euler-solver
description: Use when Claude is invoked from *inside* a running SolverShell via
  `claude -p /claude-euler-solver <problem_number> <action> [additional_prompt]`
  to perform an action on the already-locked `workspace/`. The parent SolverShell
  holds the workspace lock and Claude inherits it through the `solver_workspace_lock`
  environment variable, so `solver` subcommands run directly. Two actions —
  `solve` (write and verify a Python solution, translate it to C, then document and
  summarise) and `review` (audit an existing solution for C↔Python algorithmic
  parity, in-source documentation, and `notes.html` standards). Do NOT activate for
  a generic "solve this" or for codebase questions.
version: 0.2.0
model: opus
---

# Claude Euler Solver (in-shell)

A skill that runs **inside** a live `solver` shell. A SolverShell that is already
running — and already holds the workspace lock — launches Claude with:

```
claude -p /claude-euler-solver <problem_number> <action> [additional_prompt]
```

`<action>` is `solve` or `review`; `[additional_prompt]` is optional free-form
guidance to factor into that action. Claude does the work, prints a short summary,
and **returns control to the SolverShell**, which keeps running.

## Read first — the guides and conventions

The shell, its commands, and the solution interface are documented in the
repository's guides (all paths are relative to the project root, which is the
working directory — see [Start](#phase-1--start)):

- **[docs/solver-guide.md](docs/solver-guide.md)** — the solution interface
  (`@runner.main` / `runner.h`), test cases, the file layout, and the
  `init → eval → benchmark → stack` solve workflow.
- **[docs/commands-index.md](docs/commands-index.md)** — every `solver` command's
  exact usage (aliases, flags, arguments).
- **[docs/user-guide.md](docs/user-guide.md)** — the shell itself: invocation,
  command blocks (`;` `&&` `||` `{ }`), variables, and the workspace lock.

The **standards** each action must meet live in the `convention_*.md` guides under
`docs/` (each is also injected into the matching generation prompt — they are the
single source of truth):

- **[convention_python_solution.md](docs/convention_python_solution.md)** — Python `solve()`.
- **[convention_c_translation.md](docs/convention_c_translation.md)** — the C port.
- **[convention_source_documentation.md](docs/convention_source_documentation.md)** — in-source docstrings/comments.
- **[convention_documentation.md](docs/convention_documentation.md)** — `notes.html`.
- **[convention_test_cases.md](docs/convention_test_cases.md)** — `test_cases.json`.

## Execution model — the inherited lock

The running SolverShell acquired the workspace lock and published its PID in the
`solver_workspace_lock` environment variable. That variable is inherited by every
process the shell spawns — including this `claude` process and any `solver`
subcommand it runs — so `solver/core/lock.py` treats the lock as **held** by us
(see [the workspace lock](docs/user-guide.md#the-workspace-lock)). Run `solver`
subcommands directly (`solver ls`, `solver "eval lang=py"`, …); `PATH` already
includes `solver`. The lock belongs to the parent shell, so finishing simply means
ending the turn, which returns control to the still-running shell with its lock
intact.

### Permissions and paths

These Bash commands run without user confirmation; the skill also relies on
`Edit`/`Write` on `workspace/**` and `Read` on the project tree (`./**`). All are
granted in `.claude/settings.local.json`.

    - bash autoflake *
    - bash autopep8 *
    - bash black *
    - bash chmod +x workspace/*
    - bash chmod -x workspace/*
    - bash echo:*
    - bash env
    - bash flake8 *
    - bash gcc *
    - bash isort *
    - bash ls:*
    - bash mypy *
    - bash pip:*
    - bash python:*
    - bash rm -f workspace/*
    - bash rm -rf workspace/*
    - bash rm workspace/*
    - bash scripts/c/compile.sh:*
    - bash scripts/git/status.sh:*
    - bash scripts/linters/check.sh:*
    - bash solver *
    - bash stat:*
    - bash workspace/* *
    - bash workspace/*

**Path convention.** Every command runs from the project root. No command is
prefixed with `./` unless it would not otherwise resolve — the allowlisted paths
all contain a slash, so bash runs them relative to the cwd; `PATH`-resolved tools
(`solver`, `flake8`, `gcc`, `python`, …) take no path at all; solution files run as
`workspace/pNNNN_sK…` (no `./`). Keep each invocation byte-for-byte in this form so
it matches the allowlist — a stray `./` or `cd` misses the pattern and is
auto-denied in a headless run.

---

## Phase 1 — Start

**Always begin by confirming the inherited lock:**

```bash
solver lock-status
```

It must return **0** (`Workspace lock inherited from PID …`). Any non-zero exit
means we are **not** running inside a lock-holding SolverShell (`2` = this process
acquired the lock standalone, `1` = the workspace is not locked) — **abort
immediately**: report that this skill must be invoked as
`claude -p /claude-euler-solver <problem_number> <action> [additional_prompt]`
from inside a running, lock-holding SolverShell, and do nothing else.

Once the lock is confirmed, **initialize and list the workspace**:

```bash
solver "init <problem_number>; ls"
```

Confirm both: (1) the problem number matches the `ls` header line, and (2)
`statement.html` exists and holds a real statement. If either fails, **stop and
report — do not improvise.** (See [`init`](docs/commands-index.md#command-init) /
[`ls`](docs/commands-index.md#command-ls-list).)

---

## Phase 2 — Action

Dispatch on `<action>`. If an `[additional_prompt]` was given, treat it as extra
caller guidance (an algorithm hint, a constraint, an aspect to focus on) and factor
it in without overriding the action's contract or the conventions.

> **Note:** implement any required analysis/brute-force scripts in `workspace/` as
> **non-executable** files. The `eval` / `benchmark` harness only discovers
> executable `pNNNN_sK…` files, so keeping these scratch scripts non-executable
> leaves them out of the run set; preserve them (do not delete them) as a record
> of the working.

### `solve`

Write and verify a Python solution, translate it to C, then document and summarise,
following the [solve workflow](docs/solver-guide.md#7-the-solve-workflow):

1. **Understand the problem.** Read `workspace/statement.html` and any data file it
   references from `workspace/resources/`.
2. **Test cases.** If `test_cases.json` is missing, create it with `solver "new --tc"`;
   then make it correct and complete per
   [convention_test_cases.md](docs/convention_test_cases.md) — every `dev` case has a
   non-null `answer`, exactly one `main` case, `extra` optional.
3. **Implement `solve()`.** Add a Python file with `solver "new --py"` if needed,
   then implement it per [convention_python_solution.md](docs/convention_python_solution.md)
   (build sieves/caches **inside** `solve()` for benchmark fidelity; never print
   after the harness line or rewrite the scaffolding). Test directly:
   `workspace/pNNNN_sK.py <arg>... --runs=1 [--show]` — the last output line is
   `<runs> <average> <result>`, and each `dev` result must equal its `answer`.
   Brute-force cross-check small inputs where possible. Once it is right, run the
   `main` case and record its (sanity-checked) answer into `test_cases.json`; do the
   same for any `extra` case that is feasible to run.
4. **Verify Python.** `solver "eval lang=py solution_index=K"` (add `all` to include
   `extra`) until the verdict is `correct`.
5. **Translate to C.** `solver "new --c"` adds a `.c` sibling for each `.py`.
   Implement it per [convention_c_translation.md](docs/convention_c_translation.md) — the
   *same* algorithm as the Python. Compile with
   `scripts/c/compile.sh workspace/pNNNN_sK.c`, then verify with
   `solver "eval lang=c solution_index=K"` until `correct`. If a faithful C port is
   impractical, leave the template in place with a remark explaining why.
6. **Document & summarise.** Bring the in-source docs to
   [convention_source_documentation.md](docs/convention_source_documentation.md), run
   `solver benchmark` to record fresh timings, then write/refresh
   `workspace/notes.html` per [convention_documentation.md](docs/convention_documentation.md),
   using the recorded `results.json` values for every timing claim.

### `review`

Audit an **existing** solution and bring it up to standard. **Precondition:** at
least one solution file (`pNNNN_sK.py` or `.c`) must exist — if none does, stop and
report that this is a `solve` job, not a `review`. Then, in order:

1. **C ↔ Python parity.** For each solution index, read the `.py` and its `.c` and
   judge whether the C implements the **same algorithm** (same approach, complexity,
   and data structures in spirit — not line-for-line). Find unimplemented/broken C
   with `solver "eval lang=c"` (a `(no solve)` or `incorrect` verdict). Where the C
   is missing or has diverged, **fix it** per
   [convention_c_translation.md](docs/convention_c_translation.md): `solver "new --c"` to
   add any missing sibling, implement, compile
   (`scripts/c/compile.sh workspace/pNNNN_sK.c`), and verify with
   `solver "eval lang=c solution_index=K"` until `correct`. Leave a `.c` that already
   matches its Python **untouched**, and do **not** change any algorithm.
2. **In-source documentation.** Read each `pNNNN_sK.py` / `.c` and bring its module
   and function docstrings and comments up to
   [convention_source_documentation.md](docs/convention_source_documentation.md). This is
   a documentation pass only — **do not** change algorithm or behaviour. A `solve()`
   left with the template placeholder (or no docstring) is below the floor; add the
   missing approach-and-complexity note. Do not pad past the floor.
3. **`notes.html`.** Ensure `results.json` is present and newer than every solution
   source (`solver ls` shows the mtimes); if it is missing or stale, run
   `solver benchmark` to refresh it. Then bring `workspace/notes.html` to
   [convention_documentation.md](docs/convention_documentation.md), using the recorded
   `results.json` values for every timing or comparison claim — never invent numbers.

---

## Phase 3 — Finalize (always last)

Persist **once**, at the end (individual steps above do not persist). Each step is
gated on the previous one — **if any command fails (non-zero exit), or you hit a
lint error you cannot fix, stop and report; do not run the later steps.** (`ls` is
the exception: `→ 1` means *has changes* — proceed.)

1. **Check for unsaved changes:** `solver ls`. `ls() → 0` means nothing stackable is
   unsaved — stop, the workspace is already persisted. Continue only on `ls() → 1`.
2. **Lint and fix:** `solver "lint --auto-fix"`. It clears the mechanical `flake8`
   issues automatically; fix any remaining `mypy`/`flake8` errors by hand (we own
   `workspace/`) and re-run until `lint(...) → 0`. If you cannot make it pass, stop
   and report.
3. **Stack, reset, and commit:** `solver "stack && reset && git-commit"`. Confirm
   the canonical echoes `stack() → 0` and `git-commit() → 0`.

Then **summarise the session** in one or two sentences (the action, and what was
found or done — including where persistence stopped, if it did) and end the turn,
returning control to the SolverShell.

---

## Notes & failure modes to avoid

- **Do not** proceed past a failed `solver lock-status` — abort, as above.
- **Do not** change `cwd`; the allowlist assumes the project root is the cwd.
- **Do not** read stack files for problems > 100 directly — they are encrypted; work
  only through the `workspace/` that `init` populated.
- In `solve`: code against the actual `test_cases.json` `input` schema; verify `dev`
  before computing `main`; build caches **inside** `solve()`; never print after the
  harness's final line; write the computed answer into **every** `null` `answer`.
- In `review`: do **not** rewrite a `.c` that already matches its Python, and do
  **not** change any algorithm; keep `.c` files non-executable (only the compiled
  `_c` is `+x`). Take only the corrective steps the audit actually requires — a
  solution already in parity, documented, and summarised is a valid "nothing to do".
- In [Finalize](#phase-3--finalize-always-last): the steps are **gated** — a
  non-zero exit at lint / stack / commit, or an unfixable lint error, is a
  stop-and-report, never a reason to push on.
