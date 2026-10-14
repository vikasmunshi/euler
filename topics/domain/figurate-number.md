<!-- tags: [figurate-number] -->
<!-- status: final -->
# Figurate number

A [figurate number](https://en.wikipedia.org/wiki/Figurate_number) counts the dots in a regular
shape: triangles, squares, pentagons, and so on. The *polygonal* families that Project Euler keeps
coming back to are all quadratics in their index. Going **forward** (index → value) is a
one-line closed form. The interesting direction is **backward**: *is this number in the family,
and at which index?* Solving the quadratic answers that with one square root, and almost every
problem below is built on that inversion. Sometimes it is the whole solution (42, 44, 45),
sometimes it seeds a search (61), and sometimes it turns a question about polygonal numbers into
one about squares (647, 799).

## One formula, one inverse

The *n*-th *s*-gonal number is

    P(s, n) = ((s − 2)·n² − (s − 4)·n) / 2

so s = 3 gives the triangular numbers n(n + 1)/2, s = 4 the squares, s = 5 the pentagonal
numbers n(3n − 1)/2, and s = 6 the hexagonal numbers n(2n − 1)
([MathWorld: Polygonal Number](https://mathworld.wolfram.com/PolygonalNumber.html)). Set
P(s, n) = x and treat it as a quadratic in *n*. The
[quadratic formula](/topics/technique/quadratic-formula) gives

    n = ((s − 4) + √D) / (2(s − 2)),    D = 8(s − 2)·x + (s − 4)²

So *x* is *s*-gonal **iff D is a perfect square and the numerator divides evenly**. Written out
for the families that come up most:

| family | D | x is a member iff |
|---|---|---|
| triangular (3) | 8x + 1 | 8x + 1 is a square (its root is automatically odd) |
| square (4) | 16x | x is a square |
| pentagonal (5) | 24x + 1 | 24x + 1 = r² with r ≡ 5 (mod 6) |
| hexagonal (6) | 4(8x + 1) | 8x + 1 = r² with r ≡ 3 (mod 4) |
| heptagonal (7) | 40x + 9 | 40x + 9 = r² with r ≡ 7 (mod 10) |
| octagonal (8) | 4(12x + 4) | 12x + 4 = r² with r ≡ 4 (mod 6) |

The congruence matters. The square test alone also accepts the
[generalised pentagonal numbers](/topics/domain/pentagonal-number-theorem) k(3k + 1)/2 (2, 7, 15,
…), where 24x + 1 = r² with r ≡ 1 (mod 6). The residue is what keeps only the positive index. The
whole table fits in one exact test:

```python
from math import isqrt

def is_polygonal(s: int, x: int) -> bool:
    d = 8 * (s - 2) * x + (s - 4) ** 2
    r = isqrt(d)
    return r * r == d and (r + s - 4) % (2 * (s - 2)) == 0
```

The same inversion, rounded, also gives the *position* of any number among the members. Its floor
and ceiling are the indices of the members on either side, which is how you enumerate a family
within a range without scanning that range.

## Where it shows up

**Triangular numbers, the base case.** [Problem 42](/solutions/0042/) is the 8x + 1 test applied
to word scores. [Problem 12](/solutions/0012/) goes forward instead: it looks for the first T(n)
with more than 500 divisors, and the useful part is the factored form n(n + 1)/2. Because n and
n + 1 are coprime, the divisor count splits into two small factorisations. Both are covered in
more depth on [Triangular number](/topics/domain/triangular-number).

**Pentagonal pairs (Problem 44).** [Problem 44](/solutions/0044/) wants pentagonal P(j), P(k)
whose sum and difference are both pentagonal. Without an O(1) membership test you would have to
keep a growing set of pentagonals and look values up in it. With the test, the search is a plain
double loop over indices, with two inversions per pair. The public solution tests
`((1 + sqrt(1 + 24n)) / 6).is_integer()`. That one expression checks both the square and the
residue, because the division by 6 comes out whole only for r ≡ 5 (mod 6).

**Three families at once (Problem 45).** [Problem 45](/solutions/0045/) asks for the next number
after 40755 that is triangular, pentagonal and hexagonal. There are two reductions. First,
H(n) = n(2n − 1) = T(2n − 1): every hexagonal number is triangular, so one of the three conditions
is free. Second, there is no need to intersect sequences. You can walk one family forward and
invert the other two. The public solution walks T(n) and keeps candidates whose 24x + 1 root is
≡ 5 (mod 6) and whose 8x + 1 root is ≡ 3 (mod 4), which are exactly the pentagonal and hexagonal
rows of the table above. Walking the *hexagonal* numbers is better still: they are the sparsest of
the three, and only the pentagonal test is then needed.

**The cyclic chain (Problem 61).** [Problem 61](/solutions/0061/) asks for an ordered cycle of six
4-digit numbers, one from each family from triangular to octagonal, where the last two digits of
each number are the first two of the next. In this problem the inverse is used for *enumeration*
rather than testing. Inverting 1000 and 9999 gives each family's index range directly: 96
triangular numbers, 40 octagonal, about 300 four-digit candidates in all. The rest is a graph
problem. Make each number a node and draw an edge a → b when `a % 100 == b // 100`; the answer is
a cycle of length six that uses every family once, found by
[depth-first search](/topics/technique/depth-first-search) with backtracking. Two details catch
people:

- **A number can belong to more than one family.** 1225 is triangular, square *and* hexagonal.
  The family assignment along the cycle has to be a matching, not just "each number is in some
  family". It is simplest to label the nodes as (family, value) and require each family to be
  used once on the path.
- **Prune by family, not by value.** If the DFS carries the set of families already used, the
  search fans out only into unused families, and it finishes instantly.

**Turning polygonal equations into square equations.** The discriminant does more than test
membership: it is a change of variable. For pentagonal numbers, 24·P(n) + 1 = (6n − 1)², so a
relation like P(a) + P(b) = P(c) becomes (6a − 1)² + (6b − 1)² = (6c − 1)² + 1. That is a
sum-of-two-squares problem, and counting its representations is how Problem 799 (a pentagonal
number written as a sum of two pentagonals in many ways) avoids a quadratic pair search. Problem
647 applies the same move to affine maps: asking when A·P + B stays *s*-gonal for every
*s*-gonal P becomes, under D, a question about which linear maps send squares to squares, and
that forces A to be a square. Problem 348 (palindromes with exactly four representations as a
square plus a cube) is the plainest use of the idea: for each cube, the test is whether the
remainder is a square, i.e. one `isqrt`.

## Pitfalls

- **Float square roots stop being exact.** The public solutions to 42, 44 and 45 use
  `x ** 0.5`, which is safe at their sizes. A double has 53 bits, though, and once D passes about
  10¹⁵ a non-square can round to a whole number. Use [`math.isqrt`](/topics/technique/math-isqrt)
  and check `r * r == d`; see
  [Use exact arithmetic for equality checks](/topics/takeaway/exact-arithmetic-for-equality).
- **The square test without the residue lets in negative indices.** This is easy to miss for
  pentagonal numbers, because the false positives (2, 7, 15, 26, …) are genuine members of a
  nearby, well-known sequence.
- **Look for containment before intersecting.** Hexagonal ⊂ triangular: the odd-indexed
  triangular numbers are exactly the hexagonal ones. Knowing such a relation can remove a whole
  condition.
- **Generate from the inverse.** To enumerate an *s*-gonal family over [lo, hi], start at the
  index ⌈n(lo)⌉ and stop at ⌊n(hi)⌋. Filtering every integer in the range does on the order of
  √hi times more work, since the members thin out like √x.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle

<!-- /problems -->
