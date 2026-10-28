<!-- tags: [meissel-lehmer-algorithm] -->
<!-- status: final -->
# Meissel–Lehmer algorithm

The [Meissel–Lehmer algorithm](https://en.wikipedia.org/wiki/Meissel%E2%80%93Lehmer_algorithm)
computes `π(x)` without listing the primes up to `x`. It counts the integers that survive a
*partial* sieve, then subtracts the few composites that got through. Every solution below uses
its simplest descendant, the Lucy_Hedgehog DP. The [Prime-counting
function](/topics/domain/prime-counting-function) page explains how that DP runs and how a problem
is rewritten as `π` queries, so I won't repeat that here. This page covers the algorithm the DP
comes from: Legendre's `φ`, the corrections Meissel and Lehmer added, and why the stripped-down
version is the one that suits these problems.

## Legendre's φ

Everything rests on one function. Let `p₁ < p₂ < …` be the primes and define

```
φ(x, a) = #{ 1 ≤ n ≤ x : n has no prime factor among p₁ … pₐ }
```

the count of integers that a sieve using only the first `a` primes leaves standing. It obeys a
two-term recurrence. The survivors of `a − 1` primes either avoid `pₐ` or are `pₐ` times a
survivor of `x/pₐ`:

```
φ(x, 0) = ⌊x⌋
φ(x, a) = φ(x, a−1) − φ(⌊x/pₐ⌋, a−1)
```

**Legendre (1808)** sieves with every prime up to `√x`. If `a = π(√x)`, then every survivor
except 1 is a prime greater than `√x`, so

```
π(x) = φ(x, a) + a − 1
```

That formula is correct, but evaluated as a plain recursion it expands into roughly
`x / log x` leaves, which is no better than a sieve.

## Meissel and Lehmer: stop sieving early, correct for what slips through

**Meissel (1870)** sieves with fewer primes, `a = π(x^{1/3})`. Then the survivors greater than 1
are the primes above `pₐ`, plus composites with *exactly two* prime factors, both greater than
`pₐ`. Three such factors would exceed `x`. The two-factor count is

```
P₂(x, a) = Σ_{pₐ < p ≤ √x} ( π(x/p) − π(p) + 1 )
```

which counts the pairs `p ≤ q` with `pq ≤ x`, and so

```
π(x) = φ(x, a) + a − 1 − P₂(x, a)
```

At `x = 100`, `a = π(4) = 2`. Then `φ(100, 2) = 33` (the integers not divisible by 2 or 3), and
`P₂` counts the products `5·{5,7,11,13,17,19}` and `7·{7,11,13}`, which makes 9. That gives
`π(100) = 33 + 1 − 9 = 25`. The `π(x/p)` values inside `P₂` have arguments at most `x^{2/3}`, so a
sieve to `x^{2/3}` answers them all. The `φ` recursion now goes much less deep, because each
level divides `x` by a larger prime.

**Lehmer (1959)** takes `a = π(x^{1/4})` and adds a `P₃` term for three-factor survivors. The
modern line, Lagarias–Miller–Odlyzko and then Deléglise–Rivat, keeps Meissel's split, truncates
the `φ` tree with a rule for discarding its "special leaves", and evaluates those leaves with a
segmented sieve. That gets `π(x)` down to `O(x^{2/3} / log² x)` time. For production work,
[primecount](https://github.com/kimwalisch/primecount) implements this line, and it is what you
reach for when you need a single `π(10²⁰)`.

## Lucy's DP is Legendre, memoised

Lucy's sweep looks like a different algorithm, but it is Legendre's recurrence with a memo table.
Write `S_j(v)` for its table after the first `j` primes have been processed. The survivors in
`[2, v]` are the `j` primes already used plus the `φ(v, j) − 1` survivors greater than 1, so

```
S_j(v) = φ(v, j) + j − 1
```

Substitute that into `φ(v, j) = φ(v, j−1) − φ(v/pⱼ, j−1)`, and use `S_{j−1}(pⱼ − 1) = j − 1`.
You get exactly Lucy's update:

```
S_j(v) = S_{j−1}(v) − ( S_{j−1}(⌊v/pⱼ⌋) − S_{j−1}(pⱼ − 1) )
```

The reason it scales is that `⌊⌊x/a⌋/b⌋ = ⌊x/(ab)⌋`, so every argument the recursion can reach is
a quotient `⌊n/k⌋`. There are only about `2√n` of those (see
[quotient blocking](/topics/technique/quotient-blocking)), and the exponential tree collapses onto
them. The DP fills every node of a table that has `2√n` rows. It also skips the rows with
`v < pⱼ²`, because `pⱼ` strikes nothing there and `φ` is unchanged. The work comes to about
`n^{3/4} / log n` in `O(√n)` memory.

| Variant | Sieving primes | Correction | Time | Gives |
| --- | --- | --- | --- | --- |
| Legendre, memoised (Lucy) | up to `√x` | none | `O(x^{3/4} / log x)` | `π` at **every** `⌊x/k⌋` |
| Meissel | up to `x^{1/3}` | `P₂` | about `O(x^{2/3})` | `π(x)` |
| Lehmer | up to `x^{1/4}` | `P₂`, `P₃` | about `O(x^{2/3})` | `π(x)` |
| LMO / Deléglise–Rivat | up to `x^{1/3}` | `P₂` + special leaves | `O(x^{2/3} / log² x)` | `π(x)` |

The last column decides the choice here. Meissel–Lehmer is faster because it answers one question.
The problems below ask about a thousand or more, all of the form `⌊N/k⌋`. Lucy produces all of
them in one pass, at a cost not much above what a single `π(N)` would take. Running the faster
algorithm once per quotient would be far slower.

## Why the quotients keep showing up

All three problems take an integer `n` apart by its **largest prime factor**, `n = m · P` (this is
where the page meets [Prime factor](/topics/domain/prime-factor)). Once the cofactor `m` is fixed,
the prime `P` ranges over an interval that ends at `⌊N/m⌋`, which is a quotient, so it is already
a row in the table.

- **668 (square-root smooth numbers)** counts the *complement*. `n = pm` fails the smoothness test
  exactly when `m ≤ p`, so the failures are pairs `(p, m)`. The large primes contribute
  `Σ_{p > √N} ⌊N/p⌋`. Grouped by `k = ⌊N/p⌋`, that becomes a sum of `π(⌊N/k⌋) − π(√N)`, which is
  the table summed down one column.
- **642 (sum of largest prime factors)** walks the smooth parts `m` and adds every prime in
  `(P(m), ⌊N/m⌋]`. It needs the *sum* of the primes in each range, so it runs a second table with
  weight `p` beside the count table. The recurrence is the same, because `φ`'s logic only needs a
  completely multiplicative weight.
- **501 (eight divisors)** splits by divisor shape, not by `P(n)`. Its arguments are still
  `n/p³` and `n/(pq)`, which are quotients again.

## How to reason about it

- **One value or many?** If you need a single `π(x)` beyond about `10¹³`, use
  Meissel–Lehmer/LMO, ideally primecount. If you need `π` at every `⌊N/k⌋`, use the memoised
  Legendre table. It costs more per value but answers them all.
- **Check that the arguments are closed.** The table only answers questions about `⌊N/k⌋`. A
  query like `π(N/k + 1)`, or a quotient of a *different* `N`, falls outside it. Rewrite the sum
  so that every upper bound is a floor of `N` over something.
- **Meissel's `P₂` is a pattern you can reuse.** "Sieve partway, then subtract the survivors with
  exactly two large factors" is the same move 668 makes when it counts the failures as pairs
  `(p, m)`. A large prime greater than `√N` can appear at most once in a factorisation, and both
  calculations rely on that.
- **The pitfalls are in the boundaries.** The `+1` in each `P₂` term counts `q = p`. The
  `S(pⱼ − 1)` term must be read *before* the round updates it. And `√N` must be exact (an integer
  square root, not a float), otherwise a quotient goes missing from the table and the answers
  drift without any error being raised.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers

<!-- /problems -->
