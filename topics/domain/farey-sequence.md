<!-- tags: [farey-sequence] -->
<!-- status: final -->
# Farey sequence

The [Farey sequence](https://en.wikipedia.org/wiki/Farey_sequence) `F_n` is every reduced fraction
in `[0, 1]` whose denominator is at most `n`, in increasing order. `F_5` is
`0/1, 1/5, 1/4, 1/3, 2/5, 1/2, 3/5, 2/3, 3/4, 4/5, 1/1`. Problems reach for it whenever they say
"fractions with bounded denominator", which is more often than it sounds: the nearest fraction to a
target (71), the fractions in an interval (73), best rational approximations (198), the minimum of
`{nx}` over `n ≤ N` (965). What makes `F_n` useful in code is that consecutive terms are tied by an
exact integer identity. Because of that identity I can walk the sequence, jump to a neighbour, or
count a range without ever listing the fractions or calling `gcd`.

## Neighbours and the mediant

Two fractions `a/b < c/d` are adjacent in some Farey sequence exactly when

```
b·c − a·d = 1
```

Everything below follows from that one line.

- **The gap is `1/(bd)`.** Subtract the fractions and the numerator is the determinant, which is 1.
  Nothing of denominator `≤ max(b, d)` fits inside a gap this small.
- **The first newcomer is the mediant.** As `n` grows, the first fraction to land between two
  neighbours is their [mediant](https://en.wikipedia.org/wiki/Mediant_(mathematics))
  `(a + c)/(b + d)`. Adding numerators to numerators is wrong as fraction arithmetic, but here it
  gives exactly the right point. The mediant forms a neighbour pair with each parent (both
  determinants are still 1), and it shows up at order `b + d` and no earlier. So two neighbours in
  `F_n` stay neighbours until `n` reaches `b + d`.
- **The next term has a closed form.** Given consecutive `a/b, c/d` in `F_n`, the next term is
  `(k·c − a)/(k·d − b)` with `k = ⌊(n + b)/d⌋`. Here `k` is how many mediant steps toward `c/d` fit
  under the denominator cap. That gives a constant-memory walker over the whole sequence:

```python
def farey(n: int):
    a, b, c, d = 0, 1, 1, n
    yield a, b
    while c <= n:
        k = (n + b) // d
        a, b, c, d = c, d, k * c - a, k * d - b
        yield a, b
```

The sequence has `1 + Σ_{q ≤ n} φ(q) ≈ 3n²/π²` terms (each denominator `q` contributes its
[totient](eulers-totient-function.md) worth of numerators). Walking it is quadratic in `n`. That's
fine at `n = 10⁴`, and at `n = 10⁶` it's time to count instead of enumerate.

## Problem 71: one neighbour, no walk

[Problem 71](/solutions/0071/) asks for the fraction immediately left of `3/7` in `F_{10⁶}`. Walking
a sequence of about `3·10¹¹` terms to reach one point is out of the question. The neighbour
identity skips the walk. The left neighbour `p/q` must satisfy `3q − 7p = 1`, so its distance to
`3/7` is

```
3/7 − p/q = 1/(7q)
```

Closest means the largest admissible `q`: the largest `q ≤ N` with `3q ≡ 1 (mod 7)`, i.e.
`q ≡ 5 (mod 7)`. Then `p = (3q − 1)/7`. For `N = 8` that gives `q = 5`, `p = 2`, which is the `2/5`
from the statement. It's `O(1)`, it works for any target `a/b` (solve `aq ≡ −1 (mod b)` with a
modular inverse), and the result is already reduced, because the determinant identity forbids a
common factor.

The pitfall is to take `q` as the largest *multiple* of 7 and write `3/7 − 1/(7⌊N/7⌋)`. That
fraction lies left of `3/7`, but it isn't adjacent, because its denominator fails the congruence.
At `N = 20` the true neighbour is `8/19` and the shortcut gives `5/14`. Worse, at `N = 8` and
`N = 10⁶` the two fractions share a numerator (`2/5` against `2/7`, `428570/999997` against
`428570/999999`), so a test that only checks the numerator passes either one. Check the
determinant, not just the answer.

## Problem 73: three ways to count a range

[Problem 73](/solutions/0073/) counts the fractions strictly between `1/3` and `1/2` in
`F_{12000}`. The three solutions are three readings of the same structure, and they show the cost
model clearly.

1. **Walk the neighbours** (`s0`). Start at the term just after `1/3` and apply the next-term
   recurrence until you reach `1/2`. Both boundaries have numerator 1, so the numerators are
   determined by the denominators and the loop tracks only `d`:
   `d_next = N − (N + d_prev) mod d`. That is `O(answer)`.
2. **Split by mediants** (`s1`). Count `(L, R)` as zero if the mediant's denominator exceeds `N`,
   otherwise as one plus the counts of the two halves. Again only denominators matter:

   ```python
   def count(lo: int, hi: int) -> int:
       m = lo + hi
       return 0 if m > N else 1 + count(lo, m) + count(m, hi)
   ```

   Also `O(answer)`, with recursion depth up to about `N`.
3. **Count by rank** (`s2`). `rank(x)` is the number of terms of `F_N` that are `≤ x`, and the
   answer is `rank(1/2) − rank(1/3) − 1`. Rank needs no enumeration. `⌊q·x⌋` counts every fraction
   `≤ x` with denominator `q`, reduced or not. [Möbius inversion](../technique/mobius-inversion-formula.md),
   done as a subtractive sieve over multiples, removes the non-reduced ones. That is
   `O(N log N)`.

The answer grows like `N²`, so the first two are quadratic and the third is nearly linear. At
`N = 10⁵` the notes measure tens of seconds in Python for the recursion against a tenth of a second
for the sieve. My rule: **walk the sequence when each term contributes something different; rank it
when you only need how many.**

## The Stern–Brocot tree: every Farey sequence at once

Take the mediant of every neighbour pair, again and again, starting from `0/1` and `1/0`. The
fractions this generates form the [Stern–Brocot tree](stern-brocot-tree.md): a binary search tree
that holds every positive rational exactly once, already in lowest terms. `F_n` is that tree (the
`[0, 1]` half) cut off at denominator `n` and read in order. Each node is the mediant of the two
nearest ancestors that bracket it, and the path from the root down to `p/q` spells
out its [continued fraction](continued-fraction.md). So the 73 recursion above is a depth-first
traversal of the tree, and the 965 walker that follows advances through it one in-order step at a
time.

Two private problems are really questions about this tree.

- **[Problem 198](/solutions/0198/) (Ambiguous Numbers)** counts fractions below `1/100` that have
  two equally good best approximations for some denominator bound. The characterisation that cracks
  it: `x` is ambiguous exactly when it is the midpoint of a neighbour pair `a/b, c/d`, so both ends
  are at distance `1/(2bd)`. Because the determinant is 1, that midpoint `(2ad + 1)/(2bd)` is
  already reduced, which turns the bound on `x`'s denominator into the clean condition `bd ≤ Q/2`.
  The search over values becomes an enumeration of neighbour pairs. Fix the smaller denominator
  (at most `√(Q/2)` of them), and the partner denominators form one arithmetic progression,
  pinned by a modular inverse, which can be counted in `O(1)`. The whole thing is `O(√Q)`.
- **[Problem 965](/solutions/0965/) (Expected Minimal Fractional Value)** integrates
  `f_N(x) = min_{n ≤ N} {nx}` over `[0, 1]`. Since `{nx} = n·(x − p/n)`, this is a weighted
  one-sided rational approximation, and the Farey gaps are where it becomes linear. On a gap
  `(a/b, c/d)` of `F_N` the minimum is always attained by the left endpoint, `f_N(x) = bx − a`, a
  ramp from 0 up to `1/d`. The integral is then a sum of triangle areas, one per gap, collected by
  the constant-memory walker above. A function that looks hopeless pointwise becomes one closed-form
  term per neighbour pair.

The unsolved problems on the list follow the same pattern. In [Problem 787](/solutions/0787/) a
legal move is defined by `ad − bc = ±1`, which is the neighbour identity, so the game is played on
the tree. In [Problem 604](/solutions/0604/) a strictly convex lattice path needs edge vectors with
distinct slopes, the cheapest of which are coprime pairs, i.e. Farey fractions taken in slope order.

## How to reason about it

- **Spot it from the wording.** "Reduced fraction", "denominator at most N", "closest fraction",
  "best approximation", or a determinant `±1` in the statement all point to `F_n`.
- **Use the identity, not `gcd`.** `bc − ad = 1` gives you reducedness, gap width, the next term,
  and the mediant, all in exact integer arithmetic.
- **Pick the cost model up front.** One neighbour: `O(1)` via a congruence. A sum of something
  per gap: walk in `O(n²)`. A count: rank with a Möbius sieve in `O(n log n)`. Pairs under a
  product bound: enumerate the smaller denominator and count the progression, `O(√Q)`.
- **Recursion over mediants is elegant but deep.** The tree's left spine has length `n`. Python
  needs a raised recursion limit and pays per call, while C handles it comfortably. Prefer the
  iterative walker when the depth tracks `n`.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ○ [0604](/solutions/0604/) — Convex Path in Square
- ○ [0787](/solutions/0787/) — Bézout's Game
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value

<!-- /problems -->
