<!-- tags: [primesieve] -->
<!-- status: final 2026-11-04T03:36Z -->
# primesieve

[primesieve](https://github.com/kimwalisch/primesieve) is Kim Walisch's C/C++ library for
generating primes, and it is my default answer to "I need the primes up to N, and the primes are
not the interesting part." The solutions below delegate to it for exactly that reason. In each of
them the primes are only the raw material: a sum for problem 10, a set of rotations to check in 35,
a semiprime count in 187, a Fibonacci-mod stream in 304, a vector of residues in 381 and 421, the
points at which 635 reads a running factorial, the outer loop's index set in 517, a digit stream in
705, the terms of a convergent series in 779. A tuned library that fills that one need cleanly frees the solution to spend its code on the actual
problem. This page is about the library as a **tool**: what it does for you, the calls the
solutions make from C and Python, and when a hand-written sieve is still the right call. For the
theory, see [generation of primes](/blogs/technique/generation-of-primes) and the
[Sieve of Eratosthenes](/blogs/technique/sieve-of-eratosthenes).

## What the library actually does

Under the API, primesieve runs a [segmented](/blogs/technique/segmented-sieve) Sieve of
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
[watch integer width](/blogs/takeaway/watch-integer-width) advises: from the largest value the
array will hold, which for an `INT_PRIMES` array that later gets squared is not the largest prime.

**Arrays from Python.** `primesieve.primes(stop)` or `primesieve.primes(start, stop)` returns an
`array('Q')` of unsigned 64-bit integers. It supports the buffer protocol, so 565 wraps it with
`np.frombuffer(..., dtype=np.int64)` and copies nothing. The `primesieve.numpy` submodule returns
an `ndarray` directly, which 274, 381 and 421 hand straight to [NumPy](/blogs/technique/numpy) for
[vectorised](/blogs/technique/vectorized) modular arithmetic. In this repo the submodule is an
optional extension. The PyPI build does not include it, and it is rebuilt from source against
NumPy 2 by `scripts/setup/primesieve_numpy_extension.sh`. Plain `primesieve.primes` is always
available.

The two forms are not interchangeable, and the per-prime arithmetic decides between them. The
ndarray holds `int64`, so it suits work that fits in 63 bits and takes the same steps in every lane.
Problem 437 qualifies: with p < 10⁸ every product of two residues stays below 10¹⁶, and its ring
exponentiation squares in all lanes at once, with a mask choosing which lanes also multiply. Problem
457 does not, for two reasons. It works modulo p², so its Hensel step multiplies two residues near
10¹⁴, and its Tonelli–Shanks square root loops a different number of times for each prime. Iterating
the `array('Q')` hands out Python integers, which absorb that width, so a plain `for p in
primesieve.primes(limit)` is the right call there. The C port needs `__int128` for the same products.

**Back to a table.** A prime list is also the index list of a bitmap, so one scatter turns it into
O(1) membership:

```python
is_prime = np.zeros(n + 1, dtype=np.bool_)
is_prime[primesieve.numpy.primes(n)] = True
```

That makes membership a poor reason to write your own sieve. At n = 10⁸ on this machine the two
lines above take about 40 ms, and a hand-written strided NumPy sieve over odd numbers takes about
510 ms. Problem 518 is built on this table: its inner loop is nothing but scattered lookups. Problem
35 makes the same conversion by hand, into a flag array in C and a `set` in Python. Problem 423
takes one more step. `np.cumsum` of the mask gives π(n) for every n at once, which is the form its
binomial terms read. The counting call below answers one interval per sieve, so it is the wrong tool
for a table of π.

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

An unknown end is not the only reason to stream. Problem 705 knows exactly where it stops, but its
C port still uses the iterator, because each prime is consumed once and then forgotten: its digits
update nine running counts, with no large array anywhere. The Python port has to vectorise, so it
materialises all 4·10⁷ digits and pays for a prefix-sum pass per digit value, at 5.08 s against
0.286 s. A one-pass fold wants the iterator, even when the bound is known. Random access or vector
lanes want the array.

**Order is part of the contract.** The array calls and `next_prime` deliver primes in ascending order,
and some solutions depend on it. In 705 the order *is* the sequence being measured. Problem 779 keeps
∏(1 − 1/q) over the primes below p as a single running product, which only works if the primes
arrive smallest first.

**Counting.** `primesieve_count_primes(a, b)` gives π(b) − π(a−1) by sieving, with no array
materialised and on every core. That is a sieve, not a [prime-counting
algorithm](/blogs/domain/prime-counting-function). It is O(N) work, fine to around 10¹¹ and
hopeless at 10¹⁵. Past that point you need the combinatorial methods
([Meissel–Lehmer](/blogs/domain/meissel-lehmer-algorithm), or Walisch's companion library
[primecount](https://github.com/kimwalisch/primecount)). Problem 808 also uses
`count_primes(x, x) == 1` as a one-off primality test on a square root. It's correct and convenient
for a rare check, but each call sets up a sieve, so a test inside a hot loop should be a real
primality test or a lookup.

## Sizing the call: the bound comes from the argument

The call is cheap, and that tempts you to pass the problem's headline N. Usually the right bound is
smaller, and you get it by reasoning about the problem.

- **A window, not a prefix.** Problem 492 sums over the primes in `[x, x+y]` with x = 10⁹ and
  y = 10⁷. `primesieve.numpy.primes(x, x + y)` never sieves from 2. It finds the base primes up to
  √(x+y) ≈ 3·10⁴ and then sieves the window, so the cost scales with y, not x + y. The returned
  ndarray then becomes a set of vector lanes, and each lane works modulo its own prime: the
  exponent is reduced mod p − 1 or mod p + 1, chosen per lane with `np.where` by a Legendre symbol,
  before a vectorised Lucas ladder runs. When you know where the window *ends*, use this array
  form. When you only know *how many* primes you need, use the iterator, as in 304.
- **Only the roots of the range.** Problem 632 runs its own segmented sieve over d ≤ √N = 10⁸, but
  it asks the library for primes only up to N^¼ = 10⁴. Every d in range has at most one prime
  factor above 10⁴. So when a squarefree d's product of small prime factors falls short of d, the
  missing part is exactly one large prime, and ω(d) is the small count plus one. The large primes
  are never listed. One comparison per entry replaces a sieve 10⁴ times longer.
- **A bound you prove first.** Problem 615 walks a DFS over odd prime factorisations. Its
  head-of-list bound n·2^s means the smallest odd prime in any candidate is at most 2n, so it
  calls `primes(3, 2 * n)`, a figure that comes from the pruning argument and appears nowhere in
  the statement. Problem 659 sieves the values 4k² + 1 for k ≤ N using primes up to 2N + 1, which
  is √(4N² + 1) rounded up. After those primes have been divided out, the cofactor left is 1 or a
  single prime. It also drops every p ≢ 1 (mod 4), because −1 is not a square modulo those primes,
  so they can never divide 4k² + 1.
- **Two calls, two bounds.** Problem 437 needs p − 1 factored for about 2.9 million primes, so the
  library supplies both sides of a trial division: primes up to N become the lanes, and primes up to
  √N become the divisors. The loop is transposed. Python walks the divisors, each one tests every
  surviving lane in a single array operation, and lanes that can no longer qualify are dropped as it
  goes. What remains above 1 is the one prime factor beyond √N, the same leftover argument as 632.
  The price is that no single lane can stop early. The C port walks one prime at a time, stops at
  q² > rem, and takes 3.81 s against Python's 19.57 s.
- **A bound you choose.** The bounds above are forced by the mathematics. Two others are decisions.
  In 625 any sieve limit L past √N gives the right answer. L only moves work between the sieve and
  the recursion over large quotients, and N^⅔ is where those two costs balance. In 779 the sum runs
  over every prime, so nothing in the statement says where to stop, and the limit comes from the
  tolerance instead. The tail past P is below 1/(2P²), and P = 10⁷ was chosen because the result
  sits unusually close to a rounding boundary at the twelfth decimal. That bound is only worth having
  if the summation keeps up with it, which is why the terms go through `math.fsum` (`long double` in
  C) and not a plain running total.

In every case the library is asked one clear question. Deciding which question to ask is still
the solution's job.

## When a hand-written sieve is still better

primesieve answers one question: *which numbers are prime?* Use your own sieve when you need more
than that, or something different.

- **You need a function of n, not a list of primes.** Smallest prime factor, Möbius μ, φ, σ, Ω:
  these are [multiplicative](/blogs/domain/multiplicative-function) tables indexed by n. Build them
  with a [linear sieve](/blogs/technique/linear-sieve) or a
  [divisor-sum sieve](/blogs/technique/divisor-sum-sieve), which work at every n anyway. Problem
  464 shows the hybrid: primesieve supplies the primes and the solution's own loop spreads each one
  over the μ table it actually needs. Problem 875 does the same for φ in NumPy: one strided slice
  update per prime. Once you are writing that loop, the library has only saved you the primality
  bits. Sometimes the loop is one no library could run. In 659's
  [polynomial sieve](/blogs/technique/polynomial-sieve), a prime does not strike its multiples. It
  strikes the two residue classes of k where p divides 4k² + 1, and those classes are
  [Hensel-lifted](/blogs/technique/hensels-lemma) to p², p³, … to remove full powers. The library
  can only supply the p. Problem 675 is the same hybrid, with one extra benefit. It builds a
  per-step multiplier table for factorials by spreading each prime over its own multiples. Because
  the library returns the primes as a *sorted array*, a single `np.searchsorted` divides them at
  max(√n, n/301). Below that point each prime gets its own strided pass. Above it every prime has
  valuation 1 at all of its multiples, so they are batched by multiple index k: about 300
  fancy-indexed updates replace 660 000 per-prime Python calls. A bitmap sieve can't be split like
  that without first being turned into a list. Problem 625 avoids the large primes altogether. For
  its φ table up to L ≈ 2·10⁷ it asks only for primes up to √L, roughly 600 strided passes where 875's
  shape would need 1.4 million, and divides every power of each prime out of a parallel remainder
  array. Whatever survives in that array is 1 or the single large prime factor of n, so one masked
  update applies all the large primes together, and the solution never lists them. Compare 484,
  which never needs a table. It walks a DFS over the primes up to √N, and a plain prime list is
  exactly what that DFS takes.
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
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0632](/solutions/0632/) — Square Prime Factors
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ● [0875](/solutions/0875/) — Quadruple Congruence

<!-- /problems -->
