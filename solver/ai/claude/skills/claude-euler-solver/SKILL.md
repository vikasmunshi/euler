---
name: claude-euler-solver
description: Use when Claude is launched by the `claude-skill` command via
  `claude -p /claude-euler-solver <problem_number> <action> [additional_prompt]`
  to perform an action on a single Project Euler problem's solution files under
  `solutions/`. Claude runs headless at the repository root and edits the problem's
  solution directory directly — there is no separate workspace and no lock. Two
  actions — `solve` (write and verify a Python solution, translate it to C, then
  document and summarise) and `review` (audit an existing solution for C↔Python
  algorithmic parity, in-source documentation, and `notes.html` standards). Do NOT
  activate for a generic "solve this" or for codebase questions.
version: 0.3.0
model: opus
---

# Claude Euler Solver (headless)

A skill that runs **headless** against a single problem's solution files. The
`claude-skill` shell command launches Claude with:

```
claude -p /claude-euler-solver <problem_number> <action> [additional_prompt]
```

`<problem_number>` selects the problem, `<action>` is `solve` or `review`, and
`[additional_prompt]` is optional free-form guidance to factor into that action.
Claude does the work, prints a short summary, and **ends the turn**, returning
control to the caller.

## Read first — the conventions

The **standards** each action must meet live in the `convention_*.md` guides under
`docs/` (each is also injected into the matching generation prompt — they are the
single source of truth). All paths are relative to the project root, which is the
working directory.

- **[convention_python_solution.md](docs/convention_python_solution.md)** — Python `solve()`.
- **[convention_c_translation.md](docs/convention_c_translation.md)** — the C port.
- **[convention_source_documentation.md](docs/convention_source_documentation.md)** — in-source docstrings/comments.
- **[convention_documentation.md](docs/convention_documentation.md)** — `notes.html`.
- **[convention_test_cases.md](docs/convention_test_cases.md)** — `test_cases.json`.

For exact `solver` command usage (aliases, flags, arguments), see
**[docs/commands-index.md](docs/commands-index.md)** — e.g. [`ls`](docs/commands-index.md#command-ls),
[`new`](docs/commands-index.md#command-new), [`evaluate`/`eval`](docs/commands-index.md#command-evaluate-eval),
[`benchmark`](docs/commands-index.md#command-benchmark), [`lint`](docs/commands-index.md#command-lint),
and [`mark`](docs/commands-index.md#command-mark-mark-solved). The solution interface
(`@runner.main` / `runner.h`) is documented in
**[docs/solver-guide.md](docs/solver-guide.md)**.

## Execution model

The skill runs at the repository root and operates **directly** on the problem's
solution files — there is no separate workspace and no lock to acquire or inherit.
`solver` is on `PATH`; run subcommands directly and pass the problem number
(`solver "ls 42"`, `solver "eval 42 lang=py"`, …). Every command takes an optional
leading problem number and otherwise defaults to the last one used, so once a step
names the problem the rest can omit it. Finishing simply means ending the turn.

Every problem's files live in its own solution directory:

- problems **≤ 100**: `solutions/public/pNNNN/` — plaintext.
- problems **> 100**: the private solution tree — transparently encrypted at rest,
  plaintext in the working tree (the git clean/smudge filter handles it), so you
  read and edit them like any other file.

Run `solver "ls <n>"` to print the exact file paths and sizes for the problem; call
that directory the **solution directory** below (e.g. `solutions/public/p0007/`). A
solution runs directly from there, e.g.
`solutions/public/p0007/p0007_s0.py <arg>... --runs=1 [--show]` — the last output
line is `<runs> <average> <result>`.

### Permissions and paths

These Bash commands run without user confirmation; the skill also relies on
`Edit`/`Write` on the solution directory and `Read` on the project tree (`./**`).
These must be granted in `.claude/settings.local.json` — keep the two in sync.

    - bash autoflake *
    - bash autopep8 *
    - bash black *
    - bash echo:*
    - bash env
    - bash flake8 *
    - bash gcc *
    - bash isort *
    - bash ls:*
    - bash mypy *
    - bash pip:*
    - bash python:*
    - bash scripts/c/compile.sh:*
    - bash scripts/git/status.sh:*
    - bash scripts/linters/check.sh:*
    - bash solver *
    - bash stat:*
    - bash solutions/**            # run a solution binary/script from its directory
    - edit/write solutions/**      # create and edit solution files

**Path convention.** Every command runs from the project root. No command is
prefixed with `./` — the allowlisted paths all contain a slash, so bash runs them
relative to the cwd; `PATH`-resolved tools (`solver`, `flake8`, `gcc`, `python`, …)
take no path at all; a solution file runs as its `solver ls`-reported path
(`solutions/public/pNNNN/pNNNN_sK…`, no `./`). Keep each invocation in this form so
it matches the allowlist — a stray `./` or `cd` misses the pattern and is
auto-denied in a headless run.

---

## Phase 1 — Start

The problem number is the first argument. Locate its files and confirm they exist:

```bash
solver "ls <problem_number>"
```

This lists the solution directory (e.g. `solutions/public/p0042/…`). Confirm
`statement.html` is present and **read it** (plus any data file it references from
the directory's `resources/`). If the solution directory has no `statement.html`,
**abort and report** that the problem is not initialised — the shell's `claude-skill`
command is expected to hand this skill an existing problem.

---

## Phase 2 — Action

Dispatch on `<action>`. If an `[additional_prompt]` was given, treat it as extra
caller guidance — an algorithm hint, a constraint, an aspect to focus on, or an
additional step to perform — and factor it in without overriding the action's
contract or the conventions.

> **Note:** implement any required analysis/brute-force scripts in the solution
> directory as **non-executable** files. The `eval` / `benchmark` harness only
> discovers executable `pNNNN_sK…` files, so keeping these scratch scripts
> non-executable leaves them out of the run set; preserve them (do not delete them)
> as a record of the working.

### `solve`

Write and verify a Python solution, translate it to C, then document and summarise:

1. **Understand the problem.** Read the solution directory's `statement.html` and
   any data file it references from `resources/`.
2. **Test cases.** If `test_cases.json` is missing, create it with
   `solver "new <n> --tc"`; then make it correct and complete per
   [convention_test_cases.md](docs/convention_test_cases.md) — every `dev` case has a
   non-null `answer`, exactly one `main` case, `extra` optional.
3. **Implement `solve()`.** Add a Python file with `solver "new <n> --py"` if needed,
   then implement it per [convention_python_solution.md](docs/convention_python_solution.md)
   (build sieves/caches **inside** `solve()` for benchmark fidelity; never print
   after the harness line or rewrite the scaffolding). Test directly:
   `<solution_dir>/pNNNN_sK.py <arg>... --runs=1 [--show]` — the last output line is
   `<runs> <average> <result>`, and each `dev` result must equal its `answer`.
   Brute-force cross-check small inputs where possible. Once it is right, run the
   `main` case and record its (sanity-checked) answer into `test_cases.json`; do the
   same for any `extra` case that is feasible to run.
4. **Verify Python.** `solver "eval <n> lang=py solution_index=K"` (add `all` to
   include `extra`) until the verdict is `correct`.
5. **Translate to C.** `solver "new <n> --c"` adds a `.c` sibling for each `.py`.
   Implement it per [convention_c_translation.md](docs/convention_c_translation.md) — the
   *same* algorithm as the Python. Compile with
   `scripts/c/compile.sh <solution_dir>/pNNNN_sK.c`, then verify with
   `solver "eval <n> lang=c solution_index=K"` until `correct`. If a faithful C port
   is impractical, leave the template in place with a remark explaining why.
6. **Document.** Replace the template's placeholder module and function docstrings
   with the real approach. Bring the in-source docs to
   [convention_source_documentation.md](docs/convention_source_documentation.md).
7. **Summarise.** Run `solver "benchmark <n>"` to record fresh timings, then
   write/refresh the solution directory's `notes.html` per
   [convention_documentation.md](docs/convention_documentation.md), using the recorded
   `results.json` values for every timing claim.

### `review`

Audit an **existing** solution and bring it up to standard. **Precondition:** at
least one Python solution file (`pNNNN_sK.py`) must exist — if none does, stop and
report that this is a `solve` job, not a `review`. Then, in order:

1. **C ↔ Python parity.** For each solution index, read the `.py` and its `.c` and
   judge whether the C implements the **same algorithm** (same approach, complexity,
   and data structures in spirit — not line-for-line). Find unimplemented/broken C
   with `solver "eval <n> lang=c"` (a `(no solve)` or `incorrect` verdict). Where the
   C is missing or has diverged, **fix it** per
   [convention_c_translation.md](docs/convention_c_translation.md): `solver "new <n> --c"`
   to add any missing sibling, implement, compile
   (`scripts/c/compile.sh <solution_dir>/pNNNN_sK.c`), and verify with
   `solver "eval <n> lang=c solution_index=K"` until `correct`. Leave a `.c` that
   already matches its Python **untouched**, and do **not** change any algorithm.
2. **In-source documentation.** Read each `pNNNN_sK.py` / `.c` and bring its module
   and function docstrings and comments up to
   [convention_source_documentation.md](docs/convention_source_documentation.md). This is
   a documentation pass only — **do not** change algorithm or behaviour. A `solve()`
   left with the template placeholder (or no docstring) is below the floor; add the
   missing approach-and-complexity note.
3. **`notes.html`.** Ensure `results.json` is present and newer than every solution
   source (`solver "ls <n>"` shows the mtimes); if it is missing or stale, run
   `solver "benchmark <n>"` to refresh it. Then bring the solution directory's
   `notes.html` to [convention_documentation.md](docs/convention_documentation.md),
   using the recorded `results.json` values for every timing or comparison claim —
   never invent numbers.

---

## Phase 3 — Finalize (always last)

Files are edited in place in the solution directory, so there is no separate persist
step. Just make sure the work is clean, then summarise:

1. **Lint and fix:** `solver "lint <n> --auto-fix"`. It clears the mechanical
   `flake8` issues automatically; fix any remaining `mypy`/`flake8` errors by hand
   and re-run until `lint(...) → 0`. If you cannot make it pass, **stop and report**;
   do not paper over it.
2. **(solve only) Confirm the verdict.** Re-run `solver "eval <n>"` and make sure
   every solution's verdict is `correct` and `results.json` reflects the latest
   sources.

Then **summarise the session** in one or two sentences (the action, and what was
found or done) and end the turn.

---

## Notes & failure modes to avoid

- **Do not** change `cwd`; the allowlist assumes the project root is the cwd.
- Work on the problem you were handed — its files live in the solution directory
  `solver "ls <n>"` reports; do not touch other problems.
- In `solve`: code against the actual `test_cases.json` `input` schema; verify `dev`
  before computing `main`; build caches **inside** `solve()`; never print after the
  harness's final line; and write the computed answer into **every** `null` `answer`.
- In `solve`: create any required analysis/brute-force artifacts as **non-executable**
  files in the solution directory so the harness ignores them.
- In `review`: do **not** rewrite a `.c` that already matches its Python, and do
  **not** change any algorithm; keep `.c` files non-executable (only the compiled
  `_c` is `+x`). Take only the corrective steps the audit actually requires — a
  solution that is already in parity, documented, and summarised is a valid
  "nothing to do".
- In [Finalize](#phase-3--finalize-always-last): a non-zero `lint` exit, or an
  unfixable lint error, is a stop-and-report, never a reason to push on.
