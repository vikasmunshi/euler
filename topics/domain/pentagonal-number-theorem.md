<!-- tags: [pentagonal-number-theorem] -->
<!-- status: final 2026-10-14T11:46Z -->
# Pentagonal number theorem

Euler's [pentagonal number theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem) says
that an infinite product with a term for every positive integer collapses to a series with almost
no terms at all:

    ∏ (1 − xᵏ) = 1 − x − x² + x⁵ + x⁷ − x¹² − x¹⁵ + x²² + x²⁶ − …
      (k ≥ 1)

The surviving exponents are the *generalised pentagonal numbers*, and the signs come in pairs. The
theorem matters here for two separate reasons. Read as an identity of generating functions, it
gives the fastest simple recurrence for the partition function p(n), which is how Problems 76 and
78 are solved. Read as a statement about *which numbers* appear, it puts the pentagonal numbers in
a family with a clean membership test, which is what Problem 45 needs. This page is the companion
to [Partition (number theory)](/topics/domain/partition-number-theory): that article shows *when* to switch
from the knapsack DP to the recurrence; this one shows *where the recurrence comes from*, and why
it is correct.

## Generalised pentagonal numbers

The pentagonal numbers are P(k) = k(3k − 1)/2 for k = 1, 2, 3, …: 1, 5, 12, 22, 35, …. Let *k*
run over all the integers and you get the generalised pentagonal numbers
g(k) = k(3k − 1)/2, k = 0, ±1, ±2, … ([OEIS A001318](https://oeis.org/A001318)). Taken in the order
k = 1, −1, 2, −2, 3, −3, … they increase monotonically:

| k | 1 | −1 | 2 | −2 | 3 | −3 | 4 | −4 |
|---|---|---|---|---|---|---|---|---|
| g(k) | 1 | 2 | 5 | 7 | 12 | 15 | 22 | 26 |
| sign (−1)ᵏ⁺¹ in the recurrence | + | + | − | − | + | + | − | − |

The negative half is just g(−k) = k(3k + 1)/2, the ordinary pentagonal number plus *k*. Code that
walks this sequence — both public solutions do — computes g(k) and g(−k) as a pair from the same
*k*, which is also how the paired signs fall out: one sign per *k*, shared by both members.

## Why the product collapses: Franklin's involution

Expand ∏(1 − xᵏ) and each term of the result picks a *set* of distinct exponents, with a factor −1
for each one picked. So the coefficient of xⁿ is

    (partitions of n into an even number of distinct parts) − (those into an odd number)

The theorem says this difference is almost always 0. The cleanest proof is
[Franklin's](https://en.wikipedia.org/wiki/Pentagonal_number_theorem#Bijective_proof): pair up
the even and odd partitions so that they cancel. Draw a distinct-part partition as a Ferrers
diagram, largest row first, and look at two features:

- the **base** *s* — the smallest part (the bottom row);
- the **slope** *σ* — the run of rows, starting from the top, that each shrink by exactly one.

If s ≤ σ, remove the bottom row and put its *s* cells one each at the end of the top *s* rows.
If s > σ, do the reverse: take one cell off each of the σ slope rows and make them a new bottom
row. Both moves keep the parts distinct, preserve *n*, change the number of parts by exactly one —
so they flip parity — and undo each other. Every partition cancels against its partner, *except*
where neither move is legal. That happens only when the base and the slope share the bottom row
and s = σ or s = σ + 1, i.e. the partition is a staircase of *k* consecutive parts

    k, k+1, …, 2k−1   (summing to k(3k − 1)/2 = g(k))
    k+1, k+2, …, 2k   (summing to k(3k + 1)/2 = g(−k))

Each such *n* has exactly one unpaired partition, with *k* parts, so it contributes (−1)ᵏ. That
is the whole theorem — and the picture explains the "pentagonal" name better than any formula.

## From the theorem to the recurrence for p(n)

The partition generating function is the reciprocal: Σ p(n) xⁿ = ∏ 1/(1 − xᵏ), because each factor
1/(1 − xᵏ) = 1 + xᵏ + x²ᵏ + … chooses how many parts of size *k* to use. Multiply the two series
and you get exactly 1:

    (Σ p(n) xⁿ) · (Σ (−1)ᵏ x^g(k)) = 1

For every n ≥ 1 the coefficient of xⁿ on the left must therefore vanish:
Σₖ (−1)ᵏ p(n − g(k)) = 0. The k = 0 term is p(n) itself; move everything else across and

    p(n) = Σ_{k ≠ 0} (−1)ᵏ⁺¹ p(n − g(k))
         = p(n−1) + p(n−2) − p(n−5) − p(n−7) + p(n−12) + p(n−15) − …

with p(0) = 1 and p(m) = 0 for m < 0. Because g(k) grows like 3k²/2, only about 2√(2n/3) terms
are non-zero — about 16 for n = 100, and a few hundred near Problem 78's answer — so each value
costs O(√n) instead of the O(n) of the knapsack DP.

The two public solutions are the same recurrence in its two natural forms:

- **[Problem 76](/solutions/0076/)** asks for p(100) − 1 (a "sum" needs two terms, so the
  partition "100" itself is excluded). The solution recurses top-down with `lru_cache`, adding each
  pair as `(-1, +1)[n % 2] * (p_1 + p_2)` and stopping when both p(n − g(k)) and p(n − g(−k)) are
  0, i.e. both indices have gone negative.
- **[Problem 78](/solutions/0078/)** asks for the least *n* with 10⁶ | p(n), so the bound is
  unknown. The solution fills a list bottom-up, appending p(n) mod 10⁶ until it hits 0, and stops
  the inner loop when g(k) > n — safe because g(−k) > g(k), so the partner is out of range too.

Those two stopping rules are not interchangeable, and the difference is the useful lesson. "Stop
when both terms are zero" relies on p(m) > 0 for every m ≥ 0, which is true of the exact values
in Problem 76 — but once you reduce mod *m*, as Problem 78 must, a real term can be ≡ 0 and the
loop would quit early with a wrong sum. Under a modulus, bound the loop by the *index*, never by
the *value*.

The same product identity gives other recurrences of the identical shape: the
[sum-of-divisors function](https://en.wikipedia.org/wiki/Divisor_function) satisfies
σ(n) = σ(n−1) + σ(n−2) − σ(n−5) − σ(n−7) + … (with a correction term when g(k) = n), found by
taking the logarithmic derivative of the product. Worth knowing, if only to recognise the pattern.

## Membership: the discriminant 24x + 1

Solving x = k(3k − 1)/2 for *k* gives 3k² − k − 2x = 0, whose discriminant is 24x + 1, and

    24 · g(k) + 1 = (6k − 1)²

So the right test for *any* generalised pentagonal number is: **24x + 1 is a perfect square.**
Every odd square not divisible by 3 is ≡ 1 (mod 24), so the root *r* is ≡ ±1 (mod 6), and the
residue says which half of the family *x* belongs to:

- r ≡ 5 (mod 6) → r = 6k − 1 with k ≥ 1 → *x* is an ordinary pentagonal number P(k);
- r ≡ 1 (mod 6) → r = 6k + 1 → *x* = g(−k), a generalised one only.

That is exactly the check in [Problem 45](/solutions/0045/), which wants the next number after
40755 that is triangular, pentagonal and hexagonal. The solution walks the triangular numbers and
asks `(1 + 24 * t) ** 0.5 % 6 == 5.0` — the square-root test plus the residue that excludes the
g(−k) half. (Hexagonal numbers come free, since H(n) = T(2n − 1); see
[Triangular number](/topics/domain/triangular-number) for that half of the argument and the float-precision
caveat on `** 0.5`.) Dropping the `% 6` check would accept 2, 7, 15, 26, … as "pentagonal" — the
generalised members — which is the classic bug in this test.

The discriminant map is also the way into the private [Problem 799](/solutions/0799/), which asks
for the smallest pentagonal number expressible as a sum of two pentagonal numbers in more than a
hundred ways. Searching over triples of indices is hopeless at that size; rewriting each P(k) as
((6k − 1)² − 1)/24 turns P(a) + P(b) = P(c) into an equation between squares, and representations
of a number as a sum of two squares are a well-charted subject. The theorem itself is not used —
only its vocabulary — which is why recognising the 24x + 1 form is worth more than memorising
the series.

## How to reason about it

- **Every part allowed → pentagonal recurrence.** The theorem is about the full product over all
  k ≥ 1. Restrict the parts (coins, primes, distinct parts) and the cancellation is gone; use the
  knapsack DP from the [partition article](/topics/domain/partition-number-theory) instead.
- **Generate g(k) in pairs.** Iterate k = 1, 2, … and handle g(k) and g(−k) together; that keeps
  the sequence increasing, the sign per pair, and the stopping test simple.
- **Under a modulus, bound by index.** And in C, keep the running sum signed or add the modulus
  before `%` — the recurrence subtracts.
- **Pentagonal membership = 24x + 1 is a square *and* its root ≡ 5 (mod 6).** Use
  [`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) once values pass 2⁵³.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle

<!-- /problems -->
