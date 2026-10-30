<!-- tags: [primesieve] -->
<!-- status: final 2026-10-30T06:40Z -->
# primesieve

[primesieve](https://github.com/kimwalisch/primesieve) is Kim Walisch's C/C++ library for
generating primes, and it is my default answer to "I need the primes up to N, and the primes are
not the interesting part." The solutions below delegate to it for exactly that reason. In each of
them the primes are only the raw material: a sum for problem 10, a set of rotations to check in 35,
a semiprime count in 187, a Fibonacci-mod stream in 304, a vector of residues in 381 and 421. A
tuned library that fills that one need cleanly frees the solution to spend its code on the actual
problem. This page is about the library as a **tool**: what it does for you, the calls the
solutions make from C and Python, and when a hand-written sieve is still the right call. For the
theory, see [generation of primes](/topics/technique/generation-of-primes) and the
[Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes).

## What the library actually does

Under the API, primesieve runs a [segmented](/topics/technique/segmented-sieve) Sieve of
Eratosthenes. It has three engineering choices a ten-line sieve doesn't:

- **Wheel factorisation.** Multiples of 2, 3, 5 (and, in the pre-sieve, of a few more small primes)
  are never stored. The bit array holds only residues coprime to 30, so one byte covers 30 integers.
- **Cache-sized segments.** The sieve walks the range in windows sized to the CPU's L1/L2 cache.
  Memory therefore stays at about √N no matter how far you sieve, and every crossing-off hits
  cache. A flat `bytearray(N)` loses on both counts once N grows past a few million.
- **Bucket sieving for large primes.** Sieving primes far bigger than the segment hit it at most
  once, so they are kept in per-segment buckets (Tomás Oliveira e Silva's algorithm) and do no
  work in windows they skip.

Counting is also **multithreaded** by default. Generating is not: it fills one array in order.

The repository's own timings for problem 10 show what this is worth. Summing the primes below
10⁷ with the hand-written Eratosthenes (`p0010_s0`) takes about 30 ms in C and 310 ms in Python;
the primesieve variant (`p0010_s4`) takes about 3 ms in C and 12 ms in Python. The Python figure
is the more telling one. The Python version is a single library call, so no interpreter loop
touches each prime, and it ends up faster than the hand-written *C* sieve. At the dev input N = 10
the order flips: the C library call (~10 µs) is an order of magnitude slower than the plain loop
(~1 µs), because setting up the sieve costs more than the tiny job does.

## The APIs the solutions use

There are four shapes. Choose by how many primes you need and whether you know where they end.

| Need | C | Python |
|---|---|---|
| all primes in `[a, b]`, as an array | `primesieve_generate_primes(a, b, &size, TYPE)` | `primesieve.primes(a, b)` / `primesieve.numpy.primes(a, b)` |
| the first *n* primes ≥ `a` | `primesieve_generate_n_primes(n, a, TYPE)` | `primesieve.n_primes(n, a)` |
| stream primes, end unknown | `primesieve_iterator` + `primesieve_next_prime` | `primesieve.Iterator().next_prime()` |
| how many primes in `[a, b]` | `primesieve_count_primes(a, b)` | `primesieve.count_primes(a, b)` |

**Arrays from C.** The generate calls return a `void *` that the library allocated. You state its
element type (`INT_PRIMES`, `INT64_PRIMES`, `UINT64_PRIMES`, `LONGLONG_PRIMES`, …), cast to match,
and release it with `primesieve_free` (not `free`). Problem 10 is the whole idiom:

```c
size_t size = 0;
uint64_t *primes = (uint64_t *)primesieve_generate_primes(
    2, (uint64_t)(max_num - 1), &size, UINT64_PRIMES);
/* ... use primes[0 .. size-1] ... */
primesieve_free(primes);
```

The type tag is the one place to be careful. It is the width the library *writes*, so a cast that
disagrees with it reads garbage instead of failing to compile. Choose it the way
[watch integer width](/topics/takeaway/watch-integer-width) advises: from the largest value the
array will hold, which for an `INT_PRIMES` array that later gets squared is not the largest prime.

**Arrays from Python.** `primesieve.primes(stop)` or `primesieve.primes(start, stop)` returns an
`array('Q')` of unsigned 64-bit integers. It supports the buffer protocol, so 565 wraps it with
`np.frombuffer(..., dtype=np.int64)` and copies nothing. The `primesieve.numpy` submodule returns
an `ndarray` directly, which 274, 381 and 421 hand straight to [NumPy](/topics/technique/numpy) for
[vectorised](/topics/technique/vectorized) modular arithmetic. In this repo the submodule is an
optional extension. The PyPI build does not include it, and it is rebuilt from source against
NumPy 2 by `scripts/setup/primesieve_numpy_extension.sh`. Plain `primesieve.primes` is always
available.

**Iterators.** When you don't know where the primes stop, use the iterator, which sieves lazily
one segment at a time. Problem 304 needs a fixed number of primes just past 10¹⁴: far too high to
sieve from 2, and with no closed form for where the run ends. The iterator handles it in a few
lines:

```c
primesieve_iterator it;
primesieve_init(&it);
primesieve_jump_to(&it, start, stop_hint);   /* stop_hint sizes the first segment */
uint64_t p = primesieve_next_prime(&it);     /* ... repeat as needed ... */
primesieve_free_iterator(&it);
```

`primesieve_prev_prime` walks the same iterator downwards. Problem 808 streams its candidate primes
the same way, from 2 upwards, until it has found enough. The `stop_hint` matters: a tight hint
avoids sieving a large first segment the loop never reaches, and `UINT64_MAX` just says "no idea."

**Counting.** `primesieve_count_primes(a, b)` gives π(b) − π(a−1) by sieving, with no array
materialised and on every core. That is a sieve, not a [prime-counting
algorithm](/topics/domain/prime-counting-function). It is O(N) work, fine to around 10¹¹ and
hopeless at 10¹⁵. Past that point you need the combinatorial methods
([Meissel–Lehmer](/topics/domain/meissel-lehmer-algorithm), or Walisch's companion library
[primecount](https://github.com/kimwalisch/primecount)). Problem 808 also uses
`count_primes(x, x) == 1` as a one-off primality test on a square root. It's correct and convenient
for a rare check, but each call sets up a sieve, so a test inside a hot loop should be a real
primality test or a lookup.

## When a hand-written sieve is still better

primesieve answers one question: *which numbers are prime?* Use your own sieve when you need more
than that, or something different.

- **You need a function of n, not a list of primes.** Smallest prime factor, Möbius μ, φ, σ, Ω:
  these are [multiplicative](/topics/domain/multiplicative-function) tables indexed by n. Build them
  with a [linear sieve](/topics/technique/linear-sieve) or a
  [divisor-sum sieve](/topics/technique/divisor-sum-sieve), which work at every n anyway. Problem
  464 shows the hybrid: primesieve supplies the primes and the solution's own loop spreads each one
  over the μ table it actually needs. Once you are writing that loop, the library has only saved you
  the primality bits. Problem 675 is the same hybrid, with one extra benefit. It builds a
  per-step multiplier table for factorials by spreading each prime over its own multiples. Because
  the library returns the primes as a *sorted array*, a single `np.searchsorted` divides them at
  max(√n, n/301). Below that point each prime gets its own strided pass. Above it every prime has
  valuation 1 at all of its multiples, so they are batched by multiple index k: about 300
  fancy-indexed updates replace 660 000 per-prime Python calls. A bitmap sieve can't be split like
  that without first being turned into a list. Compare 484, which never needs a table. It walks a DFS over the primes up to
  √N, and a plain prime list is exactly what that DFS takes.
- **You need O(1) membership.** primesieve hands back primes, not a bitmap. Problem 35 has to test
  whether each rotation is prime, so it rebuilds an indexed flag array (C) or a `set` (Python) from
  the list. If lookup is all you need, a sieve that *is* the bitmap avoids building it twice.
- **The bound is tiny.** For N in the thousands, library setup outweighs the work (see the N = 10
  timing above). It doesn't matter, but it's no reason to add a dependency either.
- **The sieve is the lesson, or the oracle.** Several problems keep a hand-written variant alongside
  the primesieve one: 10 has four, 304 a segmented sieve, 565 a direct σ-sieve kept as a validation
  oracle. The independent implementation is what makes the fast one trustworthy.
- **Dependencies.** C sources that `#include <primesieve.h>` are linked with `-lprimesieve` by
  `scripts/c/compile.sh`, and Python needs the `primesieve` wheel. Both are part of this project's
  setup, but a solution meant to run anywhere has to bring its own sieve.

One rule applies whichever you choose. Call the library **inside `solve()`**, sized to the input,
just as you would build a hand-written sieve there. A module-level `primesieve.primes(10**8)` is
computed once at import, so the timed `--runs` loop never pays for it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0304](/solutions/0304/) — Primonacci
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
