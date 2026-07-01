# Solver Guide — writing solutions

This guide is for someone using the framework to **solve Project Euler
problems**. It explains the solution interface — the `@runner.main` decorator and
its C counterpart — and the workflow from scaffolding a solution to benchmarking it.

If you want the shell and command reference, read the [User Guide](user-guide.md).
If you want to add commands to the framework, read the
[Developer Guide](developer-guide.md).

---

## 1. The contract: you write `solve()`, the runner does the rest

A solution file implements exactly **one** function, `solve()`. Everything else —
parsing arguments, running the timed loop, checking the answer is stable across
runs, and printing the line the test harness reads — is supplied by the **runner
framework** (`solver/runners/`). You never write a `main()`, an argument parser,
or a timing loop.

- **Python:** decorate `solve(*args: str) -> str` with `@runner.main`.
- **C:** write `const char *solve(int argc, char *argv[])` and
  `#include "runner.h"`.

The runner passes each test case's `input` values as positional arguments in
order, runs `solve()`, and prints a single stdout line:

```
<runs> <avg_seconds> <result>
```

`solve()` only **returns** the answer as a string. It must never print that final
line itself, and it should exit nonzero on error.

---

## 2. The `@runner.main` decorator (Python)

```python
from solver.runners import runner


@runner.main
def solve(*args: str) -> str:
    n = runner.parse_int(args[0])
    return str(sum(range(n)))


if __name__ == '__main__':
    raise SystemExit(solve())
```

`@runner.main` wraps `solve` into a zero-argument `main()` that:

1. **Parses `--runs=N`** from the command line (default `1`; non-positive or
   missing falls back to `1`).
2. **Parses `--show`**, setting the module-level `runner.show` flag (see §4).
3. **Collects positional args** — everything in `argv[1:]` that is not a `--flag`
   — and forwards them to `solve(*args)` as strings, in order.
4. **Runs the timed loop** `N` times, recording `perf_counter()` around each
   call. Only the `solve()` call is timed.
5. **Checks consistency** — every run must return the same result; a differing or
   `None` result is an error written to stderr with exit code `1`.
6. **Prints** `<runs> <average_seconds> <result>` to stdout.

Because the call is repeated `N` times under `--runs=N`, **anything you build
once and keep warm between runs is mistimed.** Build sieves, tables, and caches
*inside* `solve()` (or in helpers it calls fresh each time), sized to the inputs
— not at module level with a fixed bound. A module-level `@lru_cache` or a
precomputed global is excluded from the first run and free thereafter,
understating the real cost. See `solutions/0/0/0/7/p0007_s0.py` (a sieve sized to
`n·ln n`) for the pattern.

### Argument helpers

`solve` receives raw strings; the runner provides parsers so every solution
reads its inputs the same way:

| helper                      | parses                                                          |
|-----------------------------|-----------------------------------------------------------------|
| `runner.parse_int(tok)`     | an int, with power notation (`2**20`) and `_` separators        |
| `runner.parse_list(tok)`    | a list literal, `'[1, 2, 3]'` → `[1, 2, 3]`                     |
| `runner.get_text_file(src)` | a statement-linked file, read from the cached `resources/` copy |

`get_text_file` resolves relative to the solution script's own location (via
`argv[0]`), so it works regardless of the working directory the harness runs it
from.

---

## 3. The C counterpart (`runner.h`)

```c
#include "runner.h"

const char *solve(int argc, char *argv[]) {
    long long n = parse_int(argv[1]);          /* argv[0] is the program name */
    static char answer[32];
    snprintf(answer, sizeof answer, "%lld", n * (n - 1) / 2);
    return answer;
}
```

`runner.h` supplies `main()` (the `--runs`/`--show` parsing, the timing loop, the
consistency check, and the output line), plus C versions of the same helpers:
`parse_int`, `parse_list` (returns a heap array; free it), `get_text_file`
(returns a heap string; free it), and the `show` flag.

Return the answer as a **NUL-terminated string that outlives the call** — a
`static` buffer or a string literal, never a stack-local. Positional arguments
start at `argv[1]` (`argv[0]` is the program name; flags are stripped by the
runner).

A C solution must be compiled before it can run — `compile-c` in the shell, or
`eval --clean` / `benchmark` which rebuild as needed.

---

## 4. `--show` — diagnostics without polluting the result

The harness reads one line of stdout. To emit intermediate output (a chart, trace
values) **only when asked**, gate it behind the show flag:

```python
from solver.runners import runner

if runner.show:  # Python; set by --show
    print(f'partial sums: ...')
```

```c
if (show) {                           /* C; set by --show */
    printf("partial sums: ...\n");
}
```

Graphical output needs the `show` dependency group (`pip install -e ".[show]"`).

---

## 5. Test cases

Each problem directory carries a `test_cases.json` listing inputs and expected
answers, tagged by category:

| tag     | meaning                                     |
|---------|---------------------------------------------|
| `dev`   | small examples from the problem statement   |
| `main`  | the real input — its answer is *the* answer |
| `extra` | additional edge cases for extra validation  |

Each case's `input` is a list of strings handed to `solve()` as positional args,
and `output` is the expected return value (compared as a string). `eval` checks
`dev main` by default (`eval all` adds `extra`); `benchmark` runs every category.

`new --tc` scaffolds an empty `test_cases.json`. You can also generate candidate
cases with `claude-api test-cases` — useful when the statement's examples are
implicit.

---

## 6. The `new` command

`new` scaffolds solution files for a problem, named after it and numbered after
any solutions already present (`p0042_s0.py`, `p0042_s1.py`, …). Pass the problem
number, or let it default to the current problem (the last one a command named).

```bash
solver <<'EOF'
new 42         # the next Python solution + a matching .c sibling for problem 42
new --py       # a Python solution only (for the current problem)
new --c        # add a .c sibling for every .py that lacks one
new --tc       # create a template test_cases.json (only if one is missing)
EOF
```

Each generated solution is the thin runner template from §1–2: it implements only
`solve()`, decorated with `@runner.main` (Python) or backed by `#include "runner.h"`
(C), and the runner framework supplies the harness. `new` does **not** create
`test_cases.json` unless you pass `--tc`.

---

## 7. The solve workflow

```bash
solver <<'EOF'
show 42            # read the statement, test_cases, results, and notes in the browser
ls                 # list the problem's files
# ...read the problem statement, review the test cases...
new --tc           # scaffold test_cases.json if needed
new --py           # scaffold p0042_s0.py
# ...implement solve() in py...
# ...implement any analysis/brute-force scripts in the solution dir as non-executable files...
eval               # check correctness against dev + main test cases
eval all           # check correctness against dev + main + extra test cases
# check and record answers in test_cases.json
lint               # check and fix linter errors
benchmark          # measure timings (max 21 runs each) and record to results.json
mark               # mark solved (checks the problem is solved)
new --c            # scaffold p0042_s0.c
# ...implement solve() in c...
eval lang=c        # check correctness against dev + main test cases
eval all lang=c    # check correctness against dev + main + extra test cases
benchmark lang=c   # measure timings (max 21 runs each) and record to results.json
benchmark          # benchmark all solutions and all test cases
# ...write up the mathematical insight in notes.html...
commit             # commit the changes to the repo (git-commit)
EOF
```

`show 42` selects problem 42 as the current problem, so the later commands act on
it without repeating the number. Files are edited in place in the problem's
solution directory — there is no workspace to populate, persist, or clear.

Two complementary checks:
**`eval`** answers *is it right* and *how fast*,
**`benchmark`** persists the answers in `results.json`.
Run `eval` until it passes, then `benchmark` to compare approaches and languages.

- `eval` is the fast correctness loop.
- `benchmark` always records to `results.json` and repeats each case an adaptive
  number of times — up to 21 for sub-second cases, scaling down toward 1 for slow
  ones (from prior recorded timings) — to average out noise without an unbounded
  runtime.

See the [User Guide](user-guide.md) for the full options of each command and
[`commands-index.md`](commands-index.md) for exact usage strings.

---

## 8. File layout and naming

Solutions live under `solutions/`, one directory per problem: plaintext problems
in `solutions/public/pNNNN/` (problem 42 → `solutions/public/p0042/`) and encrypted
problems in `solutions/private/pXXXX_YYYY/pNNNN/`, bucketed by century (problem 101
→ `solutions/private/p0100_0199/p0101/`). Within a directory:

| file              | contents                                                 |
|-------------------|----------------------------------------------------------|
| `p<NNNN>_s<K>.py` | a Python solution (`NNNN` = problem, `K` = index from 0) |
| `p<NNNN>_s<K>.c`  | a C solution                                             |
| `test_cases.json` | the inputs and expected answers                          |
| `results.json`    | recorded benchmark timings                               |
| `notes.html`      | the write-up                                             |
| `statement.html`  | the scraped problem statement                            |
| `resources/`      | statement-linked data files (`get_text_file`)            |

Multiple solutions per problem are supported — `new` numbers the next index for
you (`p0042_s0`, `p0042_s1`, …).

**Problems under `solutions/public/` are plain text; those under
`solutions/private/` are encrypted at rest** (AES-256) by a transparent git
clean/smudge filter — ciphertext in git, but plaintext in your working tree once
you hold the master key (see the [Git Filter Guide](gitfilter-guide.md) and the
User Guide's key-exchange section). Without the key the private files stay
ciphertext. For code structure and patterns, reference the plaintext solutions
under `solutions/public/`.

---
