# Prime numbers

Primes are the most common thread in Project Euler: dozens of problems reduce to
generating them fast, testing membership, or counting them. This page collects the
techniques the solutions in this repo actually use.

## Sieve of Eratosthenes

The workhorse. To enumerate every prime below `n`, mark the multiples of each prime
starting at its square; what stays unmarked is prime. Time `O(n log log n)`, memory
one flag per candidate — practical well past `10^8` with a byte- or bit-array.

Two habits worth copying from the public solutions:

- **Size the sieve to the inputs.** For the *k*-th prime, the bound
  `k (ln k + ln ln k)` overshoots only slightly (see problem 7's solution).
- **Build the sieve inside `solve()`**, not at module import — the benchmark
  harness times repeated `solve()` calls, and a module-level sieve would be
  excluded from the measurement.

A **segmented** sieve (fixed-size windows over `[lo, hi)`) keeps the memory bounded
when only a far range of primes is needed.

## Primality testing

When candidates are sparse or huge, sieving is waste; test each candidate instead:

- **Trial division** by primes up to `√n` — fine below ~`10^12` with a pre-sieved
  base set.
- **Miller–Rabin** — with the fixed witness set
  `{2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}` the test is *deterministic* for
  every 64-bit integer. This is the right default for big scattered candidates.

## Counting and summing primes

`π(n)` for large `n` (problems in the Meissel–Mertens–Lucy family) does not need
every prime: the **Lucy_Hedgehog method** computes `π(n)` — or the sum of primes —
in roughly `O(n^{3/4})` time and `O(√n)` memory by dynamic programming over the
distinct values of `⌊n/k⌋`.

## Where to look

- `solutions/public/p0007/` — sieve sized to the prime-counting bound.
- `solutions/public/p0035/` — sieve + rotation membership tests (circular primes).
- `solutions/public/p0010/` — summing primes below two million.
