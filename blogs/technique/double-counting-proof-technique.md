<!-- tags: [double-counting-proof-technique] -->
<!-- status: final 2026-11-09T12:29Z -->
# Double counting (proof technique)

[Double counting](https://en.wikipedia.org/wiki/Double_counting_(proof_technique)) means
counting one set in two different ways and setting the two counts equal. In a proof it gives an
identity for free. In a Project Euler solution it does something more useful: the question asks
for the count the slow way, and the second count is the one I can actually compute. Every
problem below has the same turning point. The direct sum runs over objects there are far too
many of (polygons, subsets, bases, game histories), and swapping the order of counting turns it
into a sum over something small and well structured.

## The idea

The usual setting is a set of **pairs** `(a, b)` that satisfy some relation: a polygon and one
of its crossings, a subset and one of its elements, a tree and one of its edges. Counting the
pairs row by row gives the quantity the problem defines. Counting them column by column gives
the same number, grouped differently:

$$\sum_{a} \#\{b : a \sim b\} \;=\; \#\{(a,b) : a \sim b\} \;=\; \sum_{b} \#\{a : a \sim b\}.$$

That is all there is to it. It is the
[handshaking lemma](https://en.wikipedia.org/wiki/Handshaking_lemma) and the "swap the order of
summation" step from analysis, seen from the combinatorics side. The work is in choosing the
pairs so that the right-hand inner count depends on very little: a single parameter, a local
shape, or a quotient that takes few values. In code the change is a loop interchange, and the
win comes from the new inner loop collapsing into a formula:

```python
# row-major: what the problem asks for, hopeless when `objects` is huge
total = sum(len(features(obj)) for obj in objects)
# column-major: same pairs, grouped by feature; owners(f) has a closed form
total = sum(count_owners(f) for f in feature_classes)
```

## What the second count buys, problem by problem

**Per-element contributions (944).** S(n) adds `sev(E)` over every subset of `{1..n}`, which
is 2ⁿ terms for n = 10¹⁴. The pairs are `(E, x)` with x an elevisor of E. Grouped by x, the
question is how many subsets contain x together with at least one proper multiple of x. That is
a power of two minus a power of two, depending only on ⌊n/x⌋. The exponential sum turns into a
sum over x, and since ⌊n/x⌋ takes only O(√n) values, a
[divisor-block](https://en.wikipedia.org/wiki/Divisor_summatory_function) sweep finishes it.
This is the most common form of the technique: work out what one element contributes across
all configurations, rather than what each configuration contains.

**Swapping the index of an infinite sum (926).** The total roundness R(N) adds the trailing-zero
count of N over *every* base b > 1. A trailing-zero count is itself a count, of the k with
bᵏ | N, so R(N) counts the pairs `(b, k)`. Grouping them by k instead of b turns an unbounded
sum over bases into a finite sum over exponents. For each k, the number of bases with bᵏ | N
is a product of `⌊e_p/k⌋ + 1` over the prime exponents of N. The rewrite also exposes floor
quotients that are constant on long runs of k. Those runs are what make N = 10⁷! feasible.

**Counting per feature instead of per object (842).** T(n) adds the self-intersection points
of all (n−1)!/2 star polygons, about 10⁸⁰ of them at n = 60. The pairs are
`(polygon, crossing point)`. Grouped by point, each interior point lies on some k pairwise
disjoint chords, and it counts for a polygon exactly when the polygon uses at least two of
them. How many Hamiltonian cycles do that depends only on k and n, and
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle) over
fixed matchings gives it in closed form. The astronomical enumeration becomes a histogram: how
many points of the regular n-gon lie on exactly k diagonals. That histogram is a geometry
question over the C(n,4) crossings.

**A normalising identity (475).** Here double counting gives an equation rather than a
regrouped sum. Label the trios, so each arrangement is counted (4n)! times, and map every
labelled arrangement to its quartet-by-trio incidence matrix, a 0/1 matrix with row sums 4 and
column sums 3. Each matrix comes from exactly 4! assignments per row. Counting labelled
arrangements both ways gives `f · (4n)! = 24^(3n) · M`, where M counts the matrices. The
individual musicians are gone. M depends only on the shape of the matrix, so a dynamic
programme over column-fill counts handles it in polynomial time.

**Pairs with a symmetric overcount (960).** This one uses the technique twice. Counting stones
in a connected component of the game's move graph, first by piles and then by turns, gives
k(n−1) = mn. Coprimality then forces every successful game to be a spanning tree, with each
edge's score fixed by the sizes of the two sides it separates. The sum over games then becomes
a sum over `(tree, edge)` pairs, and those I count by the split instead: choose the s-side,
a tree on each side by [Cayley's formula](https://en.wikipedia.org/wiki/Cayley%27s_formula),
and the bridging edge. Seen from both sides, every pair is counted twice, so the result has a
factor of ½, the same correction as the handshaking lemma.

**Regrouping a convolution (1006).** In Fibonacci Subwords the double count is one step inside a
longer argument. A cross term sums over pairs of ones, one from each half of a near-palindrome
built from the Fibonacci word. Taken position by position it looks like a two-dimensional
convolution. The ones sit on a [Beatty sequence](https://en.wikipedia.org/wiki/Beatty_sequence),
so grouping the pairs by the *sum of their indices* u = t + t′ means each group lands on only
two possible positions, and the split between them is itself a count with a closed form. The
2-D sum collapses to a 1-D one, and the matrix walks over Zeckendorf blocks handle that.

## How to reason about it

- **Reach for it when the direct sum runs over configurations and the summand is a count.**
  "Sum over all X of the number of Y in X" is the signal. Write the summand as a count of
  pairs, then ask which grouping makes the inner count depend on the fewest parameters.
- **The new inner count should be uniform.** In 842 it depends only on k, in 944 only on ⌊n/x⌋,
  and in 960 only on s. If the swapped count still depends on the whole configuration, the
  regrouping has bought nothing. Pick different pairs.
- **Track the multiplicities explicitly.** Most bugs here are a missing factor: the (4n)! from
  labelling in 475, the ½ from two-sided edges in 960, the C(k,2) chord pairs that each report
  the same point in 842. 842 turns that multiplicity into a guard: a point on k chords must
  show up a triangular number of times, so a non-triangular count means the floating-point
  grouping broke and the solution stops rather than return a wrong total.
- **Check the identity on tiny cases by brute force.** The regrouped formula is a claim about a
  bijection, so it is easy to be off by a constant or an edge case. The given small values
  are the first check (f(12) = 576 drops straight out of the identity in 475). For 842, 960
  and 1006 I also checked against direct enumeration (cycles, a memoised game simulation, and
  distinct substrings respectively) before trusting the fast count.
- **Expect a second technique to finish the job.** Double counting rarely gives the answer by
  itself. It reshapes the sum into something that a floor-quotient sweep (926, 944), a DP
  (475), a geometric histogram (842) or a matrix power (1006) can evaluate. The swap is what
  makes the rest of the solution possible.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0475](/solutions/0475/) — Music Festival
- ● [0842](/solutions/0842/) — Irregular Star Polygons
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0960](/solutions/0960/) — Stone Game Solitaire
- ● [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
