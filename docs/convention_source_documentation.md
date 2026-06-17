# Source documentation conventions

These govern the in-source docstrings and comments of the `pNNNN_sK.py` / `.c` solution sources.
They are distinct from the
[Documentation conventions](convention_documentation.md),
which govern the `notes.html` article.

The house style is **lean but never absent** — every solution must make its *algorithm* legible
from the source alone, then stop. The mechanics (benchmarking, I/O, argument parsing) live in the
runner, and the depth, narrative, and references live in `notes.html`; what belongs *here* is a
short, accurate statement of **what approach this file takes and why it works**. A source carrying
only the one-line module/top comment is **under-documented** — `solve()` is never left bare.

**Shared principles (`.py` and `.c`):**

- **Document the approach, not the code.** Name the algorithm and give its time complexity, and
  explain any non-obvious mathematical identity, invariant, or bound. Never restate what a line
  plainly does — descriptive names and full type hints already carry the *mechanics*; the
  docstring/comment carries the *idea* the names cannot.
- **Replace the template's placeholder docstring** ("Name the approach and its complexity here … then
  replace this placeholder with the real approach.") with the real approach. Do not keep it verbatim,
  and do not delete it leaving nothing in its place.
- **No first person, no narrative, no hyperlinks** — those are `notes.html`'s job.
- **Leave the runner scaffolding alone.** The benchmarking, `--runs=` / `--show` parsing, timing,
  and `"<runs> <avg_seconds> <result>"` output now live in the runner — `@runner.main` (Python)
  and `#include "runner.h"` (C), not in the solution file. Keep the `from solver.runners import
  runner` import and `@runner.main` decorator (Python) and the `#include "runner.h"` (C) exactly
  as the template provides, and do not editorialize them.

**Python:**

- Module docstring, one line: `""" Solution to Euler Problem <N>: <Title> [Level <L>]. """`.
- **`solve()` — a required docstring**, one to three lines: name the approach and its asymptotic
  complexity, stating *what makes it work* rather than paraphrasing the body (e.g.
  `"""Inclusion–exclusion on the closed-form arithmetic-series sum for multiples of 3, 5, 15; O(1)."""`).
- **Each non-trivial helper — a one-line docstring** of what it computes. A genuine one-liner whose
  name says everything (e.g. `is_even`) may stay bare.

**C:**

- Top comment, one line: `/* Solution to Euler Problem <N>: <Title>. */`.
- **`solve()` — a brief `/* ... */`** stating the *same* approach and complexity as the Python
  sibling, so the correspondence is visible at a glance.
- Mirror the Python sibling's helper names and structure; give each non-trivial helper a one-line
  `/* ... */`, and add a *why* comment on a non-obvious step (an overflow-avoidance cast, a
  memory-layout choice).

**Rule of thumb:** the floor is an accurate approach-and-complexity note on `solve()` (plus a line
per non-trivial helper); the ceiling is anything that starts to *narrate* — that belongs in
`notes.html`. Documenting an already-clean solution is **not** automatically a no-op: if `solve()`
carries no approach note, the source is below the floor and one must be added.