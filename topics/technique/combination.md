<!-- tags: [combination] -->
<!-- status: final -->
# Combination

A combination is a selection where order does not matter: k items chosen from n, with
`C(n, k) = n! / (k! (n − k)!)` ways to do it. I keep reaching for it for one reason. The
problem's natural objects are usually *ordered* (digit strings, step sequences, triangles named by
their vertices), but the property being tested depends only on *which* items appear. Once I see
that, the search space shrinks from `n^k` or `n!/(n−k)!` arrangements to `C(n, k)` selections,
and sometimes it shrinks to a single closed-form count with nothing listed at all.

## The idea

There are two counts to keep in mind
([Wikipedia](https://en.wikipedia.org/wiki/Combination)):

- **Without repetition**: k distinct items from n gives `C(n, k)`. This is a *k*-subset, which is
  the same as a length-*k* strictly increasing index sequence.
- **With repetition** (a *multiset*): k items from n kinds, with repeats allowed, gives
  `C(n + k − 1, k)` by [stars and bars](/topics/technique/stars-and-bars-combinatorics). This is
  the same as a length-*k* **non-decreasing** sequence.

The "same as" in each bullet is the working part. Writing an unordered selection as its sorted
sequence gives it a single canonical form. So "enumerate each selection exactly once" becomes
"enumerate the increasing (or non-decreasing) sequences", and that is a small loop in either
language. The canonical form is the third job on the
[lexicographic order](/topics/technique/lexicographic-order) page. This page is about the decision
that comes before it: *when* to collapse order away, and what to do with `C(n, k)` once you have
it.

These problems use combinations in three ways.

## 1. Enumerate the selection, not the arrangement

If the quantity being tested is symmetric in its inputs, every permutation of a selection gives
the same answer. Testing each permutation repeats the same work `k!` times.

**[Problem 30](/solutions/0030/)** (numbers equal to the sum of the fifth powers of their digits)
and **[problem 34](/solutions/0034/)** (equal to the sum of the factorials of their digits) both
have this shape. The digit-power sum of `4150` is the same as that of `0145`, so the code loops
over digit **multisets** with `itertools.combinations_with_replacement`. For each multiset it
computes the sum `s` once and asks a single question: do the digits of `s` form this same
multiset? For problem 30 that means `C(15, 6) = 5005` multisets instead of a million numbers. For
problem 34, summed over lengths 2 to 7, it means about 19 thousand instead of ten million.

The two problems differ in one detail, and the difference shows why the canonical form matters:

- In problem 30, `0⁵ = 0`, so padding with zeros adds nothing to the sum. One fixed length of six
  digits therefore covers every shorter number as well: `0145` *is* `145`.
- In problem 34, `0! = 1`, so a padding zero *does* change the sum. The solution has to loop over
  each length separately and check that `len(s)` equals the length of the multiset. Without that
  check, a padded multiset would be credited with a number that does not contain its zeros.

**[Problem 90](/solutions/0090/)** applies the same idea to physical objects. A cube is a set of
six faces, so it is a 6-subset of the ten digits: `C(10, 6) = 210` cubes. An *arrangement* of two
cubes is an unordered pair, possibly the same cube twice. The double loop `j ≥ i` visits each such
pair once, `210·211/2 = 22 155` of them, and none twice. The 6/9 flip stays out of the
enumeration and goes in the predicate (`can_display`), which keeps the selections clean.

## 2. Choose the positions, then fill them

Some objects are a fixed background with k positions that differ from it. Choosing those
positions is a combination, and filling them is a separate, independent loop.

**[Problem 111](/solutions/0111/)** asks, for each digit `d`, for the n-digit primes that repeat
`d` as many times as possible. A number with exactly `n − m` copies of `d` is determined by
*which* `m` positions differ (`C(n, m)` choices) and what goes in them (`9^m` fillings). The
solution walks `m` upward from 0 and stops at the first `m` that produces any prime. So only the
shapes near the top are ever built, and each is tested with deterministic
[Miller–Rabin](/topics/technique/miller-rabin-primality-test). Because each chosen position must
get a digit *other than* `d`, every number is produced exactly once. The Python `set` and the C
sort-and-skip of duplicates are defensive, not needed for correctness.

**[Problem 247](/solutions/0247/)** has the same structure in a geometric setting. The squares
packed under `y = 1/x` form a binary tree: each region produces one square, a region to its right
and a region above it. A square's *index* `(left, below)` counts the right steps and up steps on
its path from the root. So the squares sharing an index are exactly the `C(left + below, left)`
[lattice paths](/topics/domain/lattice-path) with that many right steps. The solution enumerates
those paths to find the smallest square of that index, then uses that side length as the pruning
bound for a depth-first count of every larger square.

## 3. Count the selections instead of listing them

If what you need is *how many*, a selection argument often yields a product of binomials, and
nothing gets enumerated at all.

**[Problem 106](/solutions/0106/)** asks how many pairs of disjoint subsets of an n-element set
actually need an equality test. Pairs of different sizes are already settled by the problem's
second rule. That leaves equal-size pairs: choose the `2k` elements involved, then split them into
two halves of size `k`. A pair escapes testing when one half dominates the other element by
element once both are sorted. Counting those dominated splits is a ballot problem, so it is a
[Catalan number](/topics/domain/catalan-number). The answer is a sum over `k` of products of
binomials with the Catalan term subtracted. The run time is `O(n²)`, against the roughly
`3^n / 2` disjoint subset pairs a brute-force solution would check.

**[Problem 184](/solutions/0184/)** counts lattice triangles that strictly contain the origin. It
starts from `C(N, 3)`, the number of all vertex triples, and subtracts the triples that miss the
origin. For a triple lying in an open half-plane, anchor it at its clockwise-most vertex. The
other two vertices are then *any 2* of the `w` points in that vertex's forward half-turn, which
gives `C(w, 2)`. The `w` values come from a [two-pointer](/topics/technique/two-pointer-technique)
sweep over the points sorted by angle. Triples with the origin on an edge are counted with
`p·q·(N − 2)` per antipodal direction pair, with an
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) term for triples that
contain two antipodal pairs. In this problem the combination is the *unit of counting*: work out
how many vertices are free, and `C(free, k)` turns that into a count.

## How to reason about it

- **Test for symmetry before you write a loop.** If permuting the inputs cannot change the
  predicate, enumerate selections. The saving is up to `k!` per selection, more with repetition.
  The work then moves into one membership test: does the output's multiset equal the input's?
- **Watch the identity element.** Padding a short selection up to a fixed length only works if the
  padding value adds nothing to the result (`0⁵ = 0` works, `0! = 1` does not).
- **Choose the unit you count.** "Any 2 of these w" and "the 2k elements, then a split" are both
  ways of finding where the free choice actually lies. Anchoring each object at a canonical vertex
  or element is what keeps the count from repeating.
- **Know the size before you commit.** `C(n, k)` peaks near `k = n/2`. `C(20, 10)` is about
  185 thousand, which is fine to enumerate. `C(40, 20)` is about 1.4 × 10¹¹, which is not. When
  enumeration is out of reach, look for a count.

## C and Python

| Need | Python | C |
|---|---|---|
| `C(n, k)` as a number | `math.comb`, exact at any size (106, 184) | multiplicative loop `r = r·(n−i)/(i+1)`, exact at every step because each partial product is a binomial times `i+1` (106). `C(m, 2)` written in closed form; `C(N, 3)` through `__int128` so `N(N−1)(N−2)` cannot overflow before the division (184) |
| k-subsets | `itertools.combinations` (90, 111, 247) | six nested strictly increasing loops when k is fixed (90). Recursive `choose_positions(start, k)` with globals in place of a closure (111). For small depth, scan every bitmask and keep those with `__builtin_popcountll(mask) == k` (247) |
| multisets | `itertools.combinations_with_replacement` (30, 34) | non-decreasing index array: bump the rightmost slot below its maximum and fill everything to its right with the new value (30, 34) |

Two points from the table deserve a closer look. First, the multiplicative loop in C is exact
only if you multiply *before* dividing, and the multiplication is where overflow happens. A safe
cap is to keep `C(n, k)·k` within 63 bits, or to divide by a gcd first. Second, the popcount
filter in problem 247 visits `2^depth` masks to keep `C(depth, k)` of them. That is wasteful in
principle but harmless at the depths the problem needs. For deeper trees,
[Gosper's hack](https://graphics.stanford.edu/~seander/bithacks.html#NextBitPermutation) steps
directly from one k-bit mask to the next (see [bit manipulation](/topics/technique/bit-manipulation)
and [Hamming weight](/topics/technique/hamming-weight)).

For the counting identities themselves (Pascal's rule, Vandermonde, symmetry), see
[binomial coefficient](/topics/domain/binomial-coefficient). The wider map of counting arguments
is on [combinatorics](/topics/domain/combinatorics).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola

<!-- /problems -->
