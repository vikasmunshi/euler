# Python solution conventions

Implement `solve()` in the canonical Python solution template; for reference, see
`new.py`. For the in-source docstrings and comments themselves, follow the
[Source documentation conventions](convention_source_documentation.md).

- **Match the schema, not an assumption.** `solve(*args: str)` receives the `test_cases.json`
  `input` values as positional string arguments, **in the order of the `input` keys** — parse each
  with the `runner` helpers as its type needs (`runner.parse_int` for ints/power notation,
  `runner.parse_list` for a `[1, 2, 3]` literal, `runner.get_text_file` for the `file_url` input —
  pass its projecteuler.net URL and it reads the locally cached copy in `resources/`). By
  convention a statement-linked file is always the `file_url` input; an empty `file_url` (`""`)
  means the data is embedded in the module as a variable, so branch on it rather than reading.
  The return annotation is always `-> str`; return the answer's string form (the harness coerces it
  back to the recorded `answer`'s type to compare, so a `list` answer must `str()` to a literal
  `ast.literal_eval` round-trips).
- **Keep the harness scaffolding byte-compatible.** The `#!/usr/bin/env python3.14` shebang,
  `# -*- coding: utf-8 -*-`, `from __future__ import annotations`, the
  `from solver.runners import runner` import, the `@runner.main` decorator on `solve()`, and the
  `if __name__ == "__main__": raise SystemExit(solve())` block are the project's test harness —
  leave them exactly as the template provides. Implement `solve()`'s body and the module-level
  helpers above it.
- **Output contract.** `@runner.main` (in `solver/runners/runner.py`) benchmarks `solve()` and
  prints the final stdout line the harness reads — `<runs> <avg_seconds> <result>`. `solve()` only
  *returns* the answer string; it must never print that line itself. Gate any diagnostic output
  behind `runner.show` (the global set by `--show`), and never print *after* `solve()` returns.
- **Full type annotations** on every signature, parameter, and notable local — mypy is strict.
- **Libraries:** the Python standard library only, plus `numpy` for numerical work and
  `primesieve` for sieve-based prime generation where warranted. Nothing else.
- **Build all computation inside `solve()` — for a truthful benchmark.** Sieves, precomputed
  tables, and any caching (`@functools.cache` / `@lru_cache`, memo dicts) must be built or reset
  **inside** `solve()` (or in helpers it calls fresh on each call), **not** at module level. With
  `--runs=N` the harness times the repeated `solve()` calls; anything built once at import (or a
  cache that stays warm between runs) is excluded from the first run and free thereafter, so the
  reported average understates the real cost. Size any sieve bound to the inputs rather than to a
  fixed, oversized `M`. (This mirrors the build-inside-`solve()` rule in `CLAUDE.md`; the
  benchmarking rationale is why both insist on it.)
- **A different algorithm per index.** If a `pNNNN_s*.py` already exists, the new index must use
  a genuinely different approach, not a rephrasing of the existing one.
- **Verify before trusting the result:** the `dev` case must match first; brute-force cross-check
  a small input where the problem admits direct simulation (this catches off-by-one, parity, and
  boundary slips); and benchmark scaling on smaller sizes, then extrapolate before the main run —
  if the projected runtime is unreasonable (more than a few minutes), revisit the algorithm. **If
  there is no `dev` case** (only a `main` case with `answer: null`), these checks carry the full
  verification weight — do not treat the absence of a `dev` case as licence to skip them.
- **Record the answer.** Write the computed value into every `null` `answer` in
  `test_cases.json`, preserving all other fields, and confirm with `solver "eval main"`.