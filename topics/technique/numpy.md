<!-- tags: [numpy] -->
<!-- status: final -->
# NumPy

[NumPy](https://numpy.org/doc/stable/) is what I reach for when a problem's work is
*uniform* — the same arithmetic applied to every integer in a dense range, the same
update applied to every cell of a table. Python's per-element cost is an interpreter
dispatch, an object allocation and a reference count; NumPy's is a machine
instruction on a packed buffer. Nothing about the algorithm changes. What changes is
where the innermost loop runs, and that is worth one to two orders of magnitude on
exactly the kind of loop these problems are made of.

## The idea

An [`ndarray`](https://numpy.org/doc/stable/reference/arrays.ndarray.html) is one
contiguous block of memory plus a
[dtype](https://numpy.org/doc/stable/reference/arrays.dtypes.html) and a shape. A
million `np.int64` entries are eight megabytes of packed integers — not a million
`PyObject` pointers to a million heap-allocated boxes. Every operation you write on
that array (`a + b`, `a % m`, `a > k`, `a[::p] = 0`) is a
[universal function](https://numpy.org/doc/stable/reference/ufuncs.html) that loops
over the buffer in compiled C. Your Python code stops describing *each step* and
starts describing *the whole step*.

Across these problems that collapses into a handful of recurring shapes.

**A strided slice is a sieve.** `flags[p*p::p] = False` marks every multiple of $p$
in one C loop. The Python-level loop that remains runs only $\pi(\sqrt{n})$ times, so
the interpreter is touched $O(\sqrt{n}/\log n)$ times to do $O(n \log \log n)$ work.
The same shape carries a divisor-sum sieve, and a
[Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function) sieve where the strided
slices are `mu[p::p] *= -1` followed by `mu[p*p::p] = 0`.

**A comparison is a mask, and a mask is an index.** `div_sums > np.arange(limit + 1)`
yields a boolean array;
[`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html)
turns it into the positions that passed, and the array itself can index another array
to select those entries. [Non-Abundant Sums](/solutions/0023/) — public, so here is
the real code — is that pipeline end to end, with
[broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) doing the
pairwise sums:

```python
div_sums = np.zeros(limit + 1, dtype=int)
for i in range(1, limit // 2 + 1):
    div_sums[2 * i: limit + 1: i] += i          # strided sieve
abundant = np.flatnonzero(div_sums > np.arange(limit + 1))   # mask -> indices
is_sum = np.zeros(limit + 1, dtype=bool)
for i in range(len(abundant)):
    sums = abundant[i] + abundant[i:]           # one scalar + a whole tail
    is_sum[sums[sums <= limit]] = True          # fancy-index assignment
```

**`arange` plus arithmetic is a closed form applied to a range.** Where the maths
gives a formula in $d$, evaluating it over $d = 1 \dots N$ is one expression:
`counts = upper // (d * d)`, then a dot product against a sieved table. That is the
whole inner loop of the squarefree count in [193](/solutions/0193/), and the
divisor-block sums in [944](/solutions/0944/) are the same move over the
$O(\sqrt{n})$ distinct values of $\lfloor n/x \rfloor$.

**`searchsorted` is a vectorised binary search.** Given a sorted array of primes,
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
evaluates $\pi(x)$ for a *whole array* of $x$ at once. [187](/solutions/0187/) counts
semiprimes as a sum of prime-counting differences and never writes a lookup loop at
all — the table is the array's own index, and the queries are one call.

**`cumsum` is the prefix sum, `bincount` the histogram.** The
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function) is literally
`np.cumsum(mu)`; the count of squarefree numbers up to each bound is
`np.cumsum(mu != 0)`. Both fall out of a Möbius sieve for free in
[464](/solutions/0464/), which then needs a
[Fenwick tree](https://en.wikipedia.org/wiki/Fenwick_tree) — and deliberately does
*not* build it in NumPy (see below).

**Shifted slices are stencils and DP layers.** A grid diffusion step is four
boundary-clipped additions of offset slices — `nxt[:, 1:, :] += share[:, :-1, :]` and
its three mirrors — which is how [213](/solutions/0213/) advances every flea's random
walk simultaneously instead of one walk at a time. The subtlest instance is the
[knapsack](https://en.wikipedia.org/wiki/Knapsack_problem) recurrence in
[249](/solutions/0249/): `counts[prime:] += counts[:-prime]` is the whole
"add this item to every reachable subset sum" pass. The two slices *overlap*, and
NumPy buffers the right-hand read before writing — which is exactly the
descending-index update the recurrence requires, and exactly what a hand-written
ascending Python loop would get wrong.

## How to reason about it

**Fixed-width dtypes are the price of the speed** — [watch the integer width](/topics/takeaway/watch-integer-width). Python's `int` is arbitrary
precision; `np.int64` wraps silently at $2^{63}$ and tells you nothing. Every
vectorised modular computation therefore needs an overflow argument before it needs a
correctness argument. [944](/solutions/0944/) does square-and-multiply on arrays with
the invariant that every partial product stays under $m^2 < 2^{63}$;
[249](/solutions/0249/) knows each pass at most doubles a count, so it can run ten
passes before reducing `mod` $10^{16}$, and sums a `uint64` array in chunks small
enough that no partial sum wraps. If you cannot state the bound, you do not have a
correct program — you have one that happens to work on the test case.

**The dtype is also the memory budget.** A Möbius array only ever holds $-1, 0, +1$,
so `int8` costs one byte per entry and a sieve to $2^{25}$ fits in 32 MB instead of
256 MB. When the range genuinely does not fit, chunk it: build `arange` a few million
at a time and accumulate, which keeps the vectorisation and bounds the footprint.

**Vectorising means *no Python per element*, not *NumPy somewhere*.**
[`np.vectorize`](https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html)
is a convenience wrapper around a Python loop and buys no speed — the docs say so
themselves. Indexing an array element-by-element in a Python loop is *slower* than a
list, because each read builds a fresh scalar object. This cuts both ways: when the
algorithm genuinely is scalar and branchy, the right move is `.tolist()` once and
loop over plain Python. [464](/solutions/0464/) does exactly that — NumPy for the
sieve, the prefix sums and the sort, then a hand-written Fenwick tree over Python
lists, because a pointer-chasing $O(\log n)$ update has nothing to vectorise.

**It is a constant factor, not a complexity class.** A $50\times$ speedup never
rescues the wrong exponent; see [algorithm beats language](/topics/takeaway/algorithm-beats-language).
Fix the asymptotics first, then vectorise the inner loop that survives. Conversely,
once the algorithm is right, NumPy is often the cheapest remaining win — it keeps the
solution in Python, readable and a dozen lines long, at a speed that would otherwise
mean rewriting in C.

**Build the arrays inside `solve()`.** The benchmark harness times repeated calls, so
a table built at module import is free on every run after the first and the reported
cost is a fiction. Size the sieve to the actual input and build it per call.

**When it does not apply:** irregular control flow, data-dependent recursion,
pointer-chasing structures, and anything needing exact arithmetic past 64 bits (where
Python's own bignums are the tool). NumPy wants the same operation, over a dense
contiguous range, with the branches expressed as masks rather than `if`s. When the
work has that shape, reach for it; when it does not, forcing it produces code that is
both slower and harder to read.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0304](/solutions/0304/) — Primonacci
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0980](/solutions/0980/) — The Quaternion Group I

<!-- /problems -->
