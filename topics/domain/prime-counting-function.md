<!-- tags: [prime-counting-function] -->
<!-- status: final -->
# Prime-counting function

The [prime-counting function](https://en.wikipedia.org/wiki/Prime-counting_function) `π(x)` is the
number of primes `≤ x`. Its theory — the prime number theorem, `Li(x)`, the Riemann hypothesis as a
bound on the error — is on the [Prime Numbers](/topics/number-theory/prime-numbers) page, and I
won't repeat it here. This page covers the engineering side. In the problems below, `π` is rarely
the answer. It is a **query**: a solution rewrites the count it was asked for as a sum of `π`
values at a few structured arguments, and then needs those values cheaply. How cheaply depends on
how many arguments there are and how large they get, and that decides the algorithm.

## Rewriting a count as π values

The move that brings `π` in is always the same. Classify the numbers you are counting by
**prime factorisation shape**, fix the small factors, and let the largest prime factor range
freely. The count of choices for that free prime is a difference of two `π` values.

- **Semiprimes (187).** Each `n = pq < N` with `p ≤ q` is one pair. Fix `p ≤ √N`; `q` runs over
  the primes in `[p, ⌊(N−1)/p⌋]`, which number `π(⌊(N−1)/p⌋) − π(p−1)`. About a thousand terms
  replace a scan over `10⁸` integers.
- **Eight divisors (501).** `τ(k) = 8` forces one of three shapes, `p⁷`, `p³q` and `pqr`, so the
  count is `π(n^{1/7})`, plus `π(n/p³)` over small `p` (minus one when `q = p` would be counted),
  plus `π(n/(pq)) − π(q)` over pairs `p < q` with `pq² ≤ n`. The outer loops only reach
  `n^{1/3} ≈ 10⁴`. The real work is the `π` values at arguments up to `n/6`.
- **Largest prime factor (642).** Write every `i = m·P` with `P` its largest prime factor. For a
  fixed smooth part `m`, every prime `P` in `(largest prime of m, ⌊N/m⌋]` contributes. The answer
  needs the *sum* of those primes, not their count, so the query becomes a weighted `π`. The same
  DP serves both, as shown below.

The shape split must be **exhaustive and disjoint**, which unique factorisation guarantees when each
shape fixes a canonical order (`p < q < r`, `p ≤ q`). The off-by-one at the boundary is the usual
bug. `π(q)` or `π(q−1)`, and whether `q = p` is allowed, depend on whether the shape lets the free
prime equal a fixed one. 187 allows `q = p` (squares of primes are semiprimes) and subtracts
`π(p−1)`; 501's `pqr` needs `r > q` and subtracts `π(q)`.

The rewrite does not always win. Problem 347 also fixes `p ≤ √N` and lets `q` range up to `N/p`,
and `Σ_p (π(N/p) − π(p))` is exactly its number of pairs. But each pair contributes a *value*, the
largest `pᵃqᵇ ≤ N`, which depends on `q` individually. So 347 walks the pairs one by one. In that
problem `π` measures the cost, not the answer: a few million pairs at `N = 10⁷`, which is
affordable, and an enumeration rather than a count is the right call. Ask whether the free prime
enters the summand only through its *membership* in a range (or as a weight with a cheap prefix
sum). If it does, the count collapses to `π`. If it doesn't, you enumerate.

## Answering the queries: three regimes

| Arguments | Method | Cost | Problems |
| --- | --- | --- | --- |
| Up to a sieve you can afford | sieve to the largest argument, read `π` off the prime list | `O(X log log X)` once, then `O(log X)` or `O(1)` per query | 50, 187 |
| A few values beyond the sieve | count by segmented sieving ([primesieve](/topics/technique/primesieve) `count_primes`) | `O(X)` per value, no memory | — |
| Every `⌊n/k⌋`, with `n` up to about `10¹²` | Lucy_Hedgehog DP over the quotient set | `O(n^{3/4})` time, `O(√n)` memory | 501, 642 |

**Regime 1: the index is π.** In a dense ascending array of primes, the prime at index `i` has
exactly `i` primes before it, so `π(pᵢ − 1) = i` costs nothing. For any other `x`, `π(x)` is the
insertion point just past `x`, a [binary search](/topics/technique/binary-search-algorithm). Problem
187 uses both: the loop index gives the lower end of each interval, and a search gives the upper.
Problem 50 relies on the same fact without naming it. Its prefix-sum array is indexed by prime
*position*, so `S[i] − S[j]` sums `i − j` consecutive primes, and "longest run" is a difference of
indices. When queries are dense rather than scattered, a prefix count over the sieve's boolean
array (`π` as a [prefix sum](/topics/technique/prefix-sum)) turns each lookup into `O(1)`. It costs
one integer per cell, though, where the prime list costs one per prime. That is about `ln x` times
the memory, so at `5·10⁷` the list plus a search is the better choice.

**Regime 3: π at all the quotients at once.** Problem 501 has `n = 10¹²`. A sieve to `n/6` is out
of the question, but every argument it asks about has the form `⌊n/k⌋`, and that set has only
about `2√n` distinct members (see [quotient blocking](/topics/technique/quotient-blocking)). The
Lucy_Hedgehog DP, a simplification of [Meissel–Lehmer](/topics/domain/meissel-lehmer-algorithm),
runs Eratosthenes as a recurrence on counts instead of on cells. Let `S(v)` be the number of
integers in `[2, v]` that survive striking out by the primes processed so far. It starts at
`v − 1`, and processing prime `p` removes the survivors whose smallest prime factor is `p`:

```
S(v) ← S(v) − ( S(⌊v/p⌋) − S(p−1) )        for every key v ≥ p², largest v first
```

`S(⌊v/p⌋) − S(p−1)` counts the cofactors `m ∈ [p, v/p]` with no prime factor below `p`, which is
exactly the set of `pm` struck out at this step. After every `p ≤ √n` has been processed,
`S(v) = π(v)` at every key. Three details make it work:

- **Two arrays, one index space.** `small[v]` holds `v ≤ √n` directly. `large[k]` holds
  `v = ⌊n/k⌋`, indexed by the denominator `k ≤ √n`, because `⌊n/⌊n/k⌋⌋ = k` recovers it. The
  lookup is a single branch: `v ≤ √n ? small[v] : large[n/v]`.
- **The DP finds its own primes.** `p` is prime exactly when `small[p] > small[p−1]`, that is, when
  the survivor count rose at `p`. No separate sieve is needed.
- **Update order.** Each `v` reads `S(⌊v/p⌋)` from the *previous* round, and `⌊v/p⌋ < v`, so the
  sweep runs from the largest key down.

Swap the seed `v − 1` for `2 + 3 + … + v` and scale the removed block by `p`, and the same pass
yields the **sum of primes** `≤ v` at every key. Any completely multiplicative weight works,
because each struck `pm` weighs `p` times `m`. Problem 642 runs both tables side by side, counts
and sums, and a DFS over smooth parts then reads ranges like `(pⱼ, ⌊N/m⌋]` from them. Every
`⌊N/m⌋` it asks about is a key, so the tables answer every query. That closure is the whole point.
The full prime-and-composite version of this machinery is the
[Min_25 sieve](/topics/technique/min-25-sieve), and the wider family is on
[Summing Multiplicative Functions](/topics/number-theory/summing-multiplicative-functions).

## C and Python

The two languages agree on the algorithm everywhere; they diverge on where the inner loop lives.

- **Scattered lookups (187).** Python resolves every upper bound in one vectorised
  `np.searchsorted(primes, (limit−1)//small, side='right')` and subtracts `np.arange` for the
  `π(p−1)` side, with no Python loop over primes. C writes an explicit `upper_bound` and calls it
  once per small prime. That is the natural idiom without broadcasting, and the two are equivalent
  because `side='right'` *is* `upper_bound`. C also finds the `√limit` cutoff by binary searching
  on the predicate `p·p < limit`, which avoids a floating-point square root.
- **The Lucy sweep (501).** The `large[k]` update for one prime is independent across `k`, so
  Python vectorises it: compute `⌊n/k⌋/p` for all `k`, mask small from large, gather from each
  array, subtract in one batch. The `small[v]` update has to run in descending order and stays a
  Python loop. At `n = 10¹²` the C version runs in about 2 s and the Python in about 39 s, and most
  of that gap is the `small` loop the vectoriser cannot take. In C, all three regions are plain
  loops over `long long`.
- **Roots and widths.** `π(n^{1/7})` in 501 takes a floating-point seventh root and then corrects
  it up or down with overflow-safe multiplications. C's `isqrt_ll` gets the same treatment: a
  `sqrt((double)n)` estimate followed by correction loops. That costs nothing and stays exact even
  where a double can no longer represent `n` precisely, and an off-by-one in `√n` would silently
  drop a key from the table.
- **Weighted tables under a modulus (642).** Prime sums to `2·10¹¹` overflow 64 bits once squared
  into the seed, so both versions keep the tables mod `10⁹`. Range sums are then *differences* of
  table entries, which can go negative, so both add the modulus back before reducing. In C that
  step is required, because `%` keeps the sign of its left operand. 642's DFS is recursive in Python and an explicit frame stack in C. That is a recursion-depth
  concern, not a `π` concern, but it is where the two files look least alike.

## How to reason about it

- **Count by shape, not by scan.** If the question counts integers by their factorisation, list
  the shapes, fix all but the largest prime, and the remaining count is a `π` difference. Then
  check the boundaries: whether the free prime may equal a fixed one decides `π(q)` or `π(q−1)`.
- **Size the largest argument first.** It is usually `N/2` or `N/(smallest product of fixed
  primes)`. If a sieve reaches it, sieve and search. If not, check whether every argument is a
  `⌊n/k⌋`. If so, run Lucy. If not, the rewrite needs another look.
- **Count the queries.** Two or three isolated values beyond sieve range can be answered by
  segmented counting. A thousand or more, all of the form `⌊n/k⌋`, call for the DP, which answers
  all of them in one pass.
- **Weights come free.** Sums of primes, or of `p^k`, cost one more table in the same sweep. Reach
  for that before inventing a second algorithm.
- **Don't force π.** When each prime contributes something that depends on the prime itself
  (347), `π` only tells you how many iterations to budget.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0187](/solutions/0187/) — Semiprimes
- ○ [0308](/solutions/0308/) — An Amazing Prime-generating Automaton
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0501](/solutions/0501/) — Eight Divisors
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0609](/solutions/0609/) — $\pi$ Sequences
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0869](/solutions/0869/) — Prime Guessing

<!-- /problems -->
