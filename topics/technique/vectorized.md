<!-- tags: [vectorized] -->
<!-- status: final -->
# Vectorized computation

Python's per-operation overhead is the tax that decides most of these problems. An
interpreted loop that touches a hundred million integers is hopeless; the *same* arithmetic
expressed as a handful of whole-array operations, each dispatched once into compiled code,
finishes in seconds. [Vectorization](https://numpy.org/doc/stable/glossary.html#term-vectorization)
is the discipline of restating a computation so the loop lives in C instead of in the
interpreter — and the thinking it forces (what is the array, what is the index, what is the
mask) is usually clarifying in its own right.

## The idea

A [NumPy](https://numpy.org/doc/stable/) array is a flat, typed block of memory. Every
operation on it — `a + b`, `a > 3`, `a[::k] += 1` — is a
[ufunc](https://numpy.org/doc/stable/reference/ufuncs.html) that loops over that block in
compiled code, paying the interpreter's dispatch cost **once for the whole array** rather than
once per element. That single fact is the whole technique. A Python `for` over ten million
values costs ten million bytecode dispatches, ten million boxed integers, ten million
reference-count updates. The array form costs one dispatch and a tight machine loop over
contiguous memory that the CPU can prefetch and often auto-vectorize into SIMD instructions.
The asymptotic complexity is identical; the constant factor is one to two orders of magnitude.

The technique is therefore not an algorithm but a *rewrite*: take the loop you would naturally
write, and find the array expression that performs the same work in bulk.

**Strided slices are sieves.** The canonical move is `array[start::step] op= value`, which
touches every `step`-th element in one call. [Problem 23](/solutions/0023/) builds a
divisor-sum table this way — the outer loop runs over divisors (a few tens of thousands of
iterations), and each iteration credits *all* of that divisor's multiples at once:

```python
div_sums = np.zeros(limit + 1, dtype=int)
for i in range(1, limit // 2 + 1):
    div_sums[2 * i: limit + 1: i] += i
abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))
```

[Problem 179](/solutions/0179/) sieves the divisor *count* with the same shape, but pairs
divisors so the interpreter loop runs only `√N` times instead of `N` times; the arithmetic
still costs `O(N log √N)`, but almost none of it is interpreted.

**Invert the loop nest.** When you have nested loops, vectorize the *inner* one and leave the
outer in Python. This is the single most common shape across these problems, because it needs
no cleverness: whichever loop runs more often becomes the array axis. Problem 23 marks every
pairwise sum of abundant numbers by adding one abundant number to the whole remaining slice;
[problem 165](/solutions/0165/) tests one line segment against all later segments in a single
pass of cross-product arithmetic; [problem 757](/solutions/0757/) enumerates one factor in
Python and sweeps the co-factor as an `int64` array. The Python loop survives — it just runs
`√N` times instead of `N` times, and that is enough. When you want to erase *both* levels,
[broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) does it: an
`(m, 1)` column against a `(1, n)` row produces the full `m × n` grid of combinations in one
expression, at the price of materialising it.

**Masks replace `if`.** A comparison yields a boolean array, and boolean arrays index, count,
and combine. `mask = n <= limit` then `n[mask]` is the vectorized `if`;
[`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html)
turns a predicate into the indices satisfying it, and `count_nonzero` turns it into a tally.
This is what lets a filter-heavy computation stay in array form: you do not skip the failing
elements, you compute them and discard them — cheaper than branching per element, provided the
discarded work is cheap.

**Batch the lookups.**
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
does a whole vector of binary searches in one call, which quietly converts "for each `x`, look
`x` up in a sorted table" into a single operation. [Problem 187](/solutions/0187/) counts
semiprimes by turning the prime-counting function `π` into two array lookups over a sorted
prime array; [problem 461](/solutions/0461/) uses it as the join step of a
[meet-in-the-middle](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) search, locating
the nearest partner for every candidate at once. Sorting once and searching in bulk is often
faster than a dictionary, because the search never leaves compiled code.

**Advance the whole ensemble.** When many independent processes share one update rule, make
the process an *axis* and step them in lockstep. [Problem 213](/solutions/0213/) tracks the
probability distribution of every flea on the board simultaneously — one ring of the simulation
is four shifted, boundary-clipped array additions over a `(fleas, n, n)` grid, so the entire
board advances in a constant number of NumPy calls per step. [Problem 149](/solutions/0149/)
runs [Kadane's algorithm](https://en.wikipedia.org/wiki/Maximum_subarray_problem) down every
row of a grid at once: one vector update per column, all rows in parallel. A dynamic program
whose states at step `k` depend only on step `k-1` is exactly this shape — the DP table row
becomes the array, and the recurrence becomes one array expression per step.

**Vectorize the modular arithmetic too.** Nothing about the technique is limited to `+` and
`*`. [Problem 944](/solutions/0944/) computes `2**e mod m` for a whole array of exponents by
running [square-and-multiply](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) over
the exponent *bits*, masking the odd-bit lanes at each step — 64 array operations instead of a
per-element `pow`. The pattern generalises: any bounded, data-independent iteration can be
unrolled across the array, with a boolean mask selecting which lanes act.

## How to reason about it

- **Vectorize the loop the input size drives, not every loop.** The win comes from the loop
  that runs millions of times; a surrounding loop of a few thousand iterations can stay plain
  Python and cost nothing measurable. Chasing the outer loop into array form usually buys
  little and costs a lot of readability. This is
  [match the abstraction to the hot path](/topics/takeaway/right-tool-per-cost) applied to
  arithmetic.
- **Watch the dtype.** NumPy integers are fixed-width machine words, not Python's
  [arbitrary-precision integers](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic),
  and `int64` overflow wraps **silently** — no exception, just a wrong answer. Before writing a
  product into an array, bound it: keep every intermediate under `2**63`, reduce modulo `m`
  before multiplying when `m*m` fits, and say so in a comment. See
  [watch integer width](/topics/takeaway/watch-integer-width). Choosing the *smallest*
  sufficient dtype is also a speed decision: an `int8` Möbius table
  ([problem 193](/solutions/0193/)) is eight times more cache-friendly than `int64`, and
  bandwidth is what these loops are limited by.
- **Memory is the real ceiling, and chunking is the fix.** Vectorization trades memory for
  speed: materialising an intermediate of `N` elements needs `N` elements of RAM, and the
  natural array form of an `O(N)` sum can be an `O(N)` allocation. Sweep the range in
  cache-sized blocks instead — problems 193 and 210 both accumulate over chunks of about four
  million entries, which keeps the working set inside cache *and* bounds memory. Chunking costs
  one extra loop level and usually makes the code faster, not just smaller.
- **Serial dependence is the real obstacle — and often only apparent.** If element `k` cannot
  be computed without element `k-1`, there is nothing to batch, and a genuinely serial scan
  (problem 165's [Blum Blum Shub](https://en.wikipedia.org/wiki/Blum_Blum_Shub) stream) stays a
  Python loop. But look for slack before conceding: problem 149's
  [lagged Fibonacci](https://en.wikipedia.org/wiki/Lagged_Fibonacci_generator) generator has a
  smallest lag of 24, so 24 terms can be produced per vectorized step without the output
  aliasing its own input. Better still, look for a closed form. A
  [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator)
  looks hopelessly sequential, yet its `k`-th term is `a**k` times the seed, so
  [problem 980](/solutions/0980/) generates its stream in bulk with a baby-step/giant-step
  outer product of power tables — the serial recurrence becomes one broadcast multiply.
  Whenever the recurrence is linear, the dependence chain can usually be broken.
- **`np.vectorize` is not vectorization.** It is a convenience wrapper that calls your Python
  function once per element — the documentation says as much. It buys broadcasting semantics,
  not speed. [Problem 56](/solutions/0056/) uses it only inside a diagnostic path, which is the
  right place for it.
- **Floating point buys speed and costs exactness.** Array arithmetic in `float64` is fast, but
  equality and near-misses become delicate: problem 461 uses
  [`expm1`](https://numpy.org/doc/stable/reference/generated/numpy.expm1.html) to avoid
  catastrophic cancellation and widens its search with an epsilon before deciding. When the
  answer depends on exact equality, keep integers — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
- **In C, this problem does not exist.** Every one of these solutions has a C counterpart that
  simply writes the nested loops, because a compiled loop already has no interpreter tax and
  the compiler auto-vectorizes what it can. That is the honest framing: vectorization is how
  Python reaches the performance C gets for free, and comparing the two versions of the same
  problem — problems 187, 213 and 501 all have both — is the clearest way to see exactly what
  the interpreter was costing.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0135](/solutions/0135/) — Same Differences
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0304](/solutions/0304/) — Primonacci
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0980](/solutions/0980/) — The Quaternion Group I

<!-- /problems -->
