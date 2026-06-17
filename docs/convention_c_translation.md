# C translation conventions

The goal is a **faithful port, not a redesign**. For reference, see the template at
`new.c`. For the in-source comments themselves, follow the
[Source documentation conventions](convention_source_documentation.md).

- **Filenames.** The C source mirrors its Python sibling's stem, swapping the extension:
  `pNNNN_sK.py` → `pNNNN_sK.c` (same problem number, same index `K`); `solver compile` produces
  the `pNNNN_sK_c` executable. Never hand-write or edit the `_c` artifact — only the `.c` source.
  The `.c` is **source**, so it must **not** be executable (`chmod -x` if one ends up `+x`); only
  the compiled `_c` is.
- **Include the runner; write only `solve()`.** Begin the file with
  `/* Solution to Euler Problem <N>: <Title>. */` then `#include "runner.h"`. The header
  (`solver/runners/runner.h`, found via the `-I` that `scripts/c/compile.sh` adds) supplies
  `main()`, the `--runs=N` / `--show` parsing, the timing loop, the cross-run consistency check,
  and the result printing — do **not** redefine `main()` or re-implement any of it. Write only
  `solve()` and its helpers.
- **Translate faithfully — same algorithm, same complexity.** Do not change the approach during
  the port. A `.c` is "correct" precisely when its algorithm matches the Python sibling's.
- **`solve` always returns a string** — `const char *solve(int argc, char *argv[])`, mirroring the
  Python `-> str`. Format the answer into a buffer that outlives the call and return it; for a
  numeric answer:
  `static char answer[32]; snprintf(answer, sizeof answer, "%lld", result); return answer;`. For a
  `list`/other, build the literal form the recorded `answer` parses back as (e.g. `"[1, 2, 3]"`).
  The returned pointer is **owned by `solve()` and must stay valid until the next call** — a string
  literal or a `static` buffer, **never** a per-call `malloc` (the runner copies it for its
  cross-run check); return `NULL` to signal failure. `main()` (from `runner.h`) passes only the
  problem inputs to `solve()` (`argv[1]` = first input, …).
- **Argument parsing:** prefer the runner helpers from `runner.h` — `parse_int(argv[i])` (plain
  ints, `2**20` power notation, `_` separators; mirrors `runner.parse_int`) and
  `parse_list(argv[i], &count)` (a `"[1,2,3]"` literal → a `malloc`'d `long long` array you
  `free()`). `atoll` / `atof` remain fine for a plain `long long` / `double`.
- **primesieve:** if the Python uses `primesieve`, the C must use the C library —
  `#include <primesieve.h>` (the compile script auto-adds `-lprimesieve`). Useful functions:
  `primesieve_nth_prime`, `primesieve_count_primes`, and
  `primesieve_generate_primes(start, stop, &size, INT_PRIMES)` (free the result with
  `primesieve_free`).
- **Arbitrary-precision arithmetic:** Python ints are unbounded and its floats can be widened with
  `decimal`/`fractions`, so when a result or intermediate **overflows C's 64-bit `long long`** (or
  `__int128`), port it with a bignum library rather than silently truncating. The compile script
  auto-links each from its `#include`:
    - **GMP** — `#include <gmp.h>` (`-lgmp`): `mpz_t` integers, `mpq_t` rationals; the default
      choice for big-integer work.
    - **MPFR** — `#include <mpfr.h>` (`-lmpfr -lgmp`): arbitrary-precision floats with correct
      rounding, for the rare problem needing fractional precision beyond `double`.
    - **OpenSSL BIGNUM** — `#include <openssl/bn.h>` (`-lcrypto`): the `BIGNUM` type, convenient
      when the Python leans on modular arithmetic (`BN_mod_exp`, `BN_mod_mul`, …).
  Reach for these **only when the Python genuinely needs the range** — a value that fits in
  `long long` stays in `long long` (it is far faster). Free everything you allocate:
  `mpz_clear` / `mpz_clears`, `mpfr_clear` / `mpfr_clears`, `BN_free` / `BN_CTX_free`.
- **Bignum is also a *speed* tool, not only a range tool.** Reach for GMP even when the values
  still fit in `__int128`, if the hot path does **repeated modular multiply/exponentiation** on
  operands wider than 64 bits — Miller–Rabin, `pow(a, d, n)`, modular-power loops. A hand-rolled
  `unsigned __int128` `mulmod` has no 256-bit product to hold the intermediate, so it degrades to a
  bit-by-bit add-and-shift loop (O(bits) per multiply) and loses to Python's `pow(a, d, n)` (which
  is itself fast bignum modexp); `mpz_powm` stays fast. The faithful, fast port keeps a native
  `__int128` fast path for moduli ≤ 2⁶⁴ (where the single-instruction product is unbeatable) and
  routes anything larger through GMP — mirroring exactly what CPython's `pow(a, d, n)` does.
- **Resource files:** if the Python reads the `file_url` input, mirror it — call the runner's
  `get_text_file(src)` (declared in `runner.h`) with the projecteuler.net file URL; it serves the
  locally cached `resources/` copy (avoiding a re-fetch), returning a heap buffer you `free()`.
  Mirror the empty-`file_url` branch too: when it is `""`, use the data embedded in the source as a
  variable instead of reading a file.
- **Heap ownership cuts the other way for the result.** `get_text_file` and `parse_list` hand back
  `malloc`'d buffers that `solve()` must `free()`; but the string `solve()` *returns* must **not**
  be heap — return a string literal or a `static` buffer, never a per-call `malloc` (see above).
- **Headers:** `runner.h` already pulls in `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<time.h>`,
  and `<unistd.h>`; add another header only for something you use beyond those (e.g. `<math.h>`,
  `<primesieve.h>`, `<gmp.h>`, `<mpfr.h>`, `<openssl/bn.h>`). Compilation is `-Werror`, so anything
  unused or implicit still fails.
- **OverflowError guard:** if the Python raises `OverflowError(msg)` above some threshold,
  replicate it — print `OverflowError: <msg>` to **stderr** and exit with status 1.
- **No reasonable C equivalent** (e.g. `sympy`, `networkx`, or anything beyond `numpy` /
  `primesieve` / the bignum libraries above — GMP, MPFR, OpenSSL BIGNUM): do **not** fabricate a
  port. Skip that index and tell the user why, rather than emitting a broken translation.
- **Build and verify:** `solver "compile --clean"`, then `solver "eval all lang=c"`; the compiled
  `pNNNN_sK_c` must match every recorded `answer`.