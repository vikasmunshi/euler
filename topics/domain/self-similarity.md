<!-- tags: [self-similarity] -->
<!-- status: final 2026-10-17T06:56Z -->
# Self-similarity

An object is self-similar when it is built from smaller copies of itself: a dragon curve made of two
dragon curves, a circle packing whose every gap holds a smaller packing, a sequence that describes
its own run lengths. Project Euler likes these objects because they are effectively infinite. The
string, the tree or the packing has far too many parts to build, yet the rule that makes it is a
single line. Every solution below works the same way. It never builds the object. It works with the
rule, and it computes a quantity for a whole copy in one step so that copy never has to be expanded.

## The idea

[Self-similarity](https://en.wikipedia.org/wiki/Self-similarity) in the strict sense means that the
object S satisfies an equation

    S = f₁(S) ∪ f₂(S) ∪ … ∪ f_k(S)

for a fixed set of maps fᵢ, usually similarities (scale, rotate, shift). This is an
[iterated function system](https://en.wikipedia.org/wiki/Iterated_function_system), and S is its
attractor. Grammars have the discrete analogue: an [L-system](/topics/domain/l-system) rewrites each
symbol into a string that contains the same symbols, so the level-n expansion of a symbol is made of
level-(n−1) expansions. A [fractal](/topics/domain/fractal) is the special case in which the copies
shrink forever.

What makes this useful in code is that the self-similarity equation becomes a recursion for **any
quantity that behaves well under the maps**. Suppose Q(f(S)) can be computed from Q(S) and f alone.
Displacement, rotation, area, a bounding extent, a leaf count and a sum all have this property. Then

    Q(S) = combine( g(f₁, Q(S)), …, g(f_k, Q(S)) )

and Q at level n costs one combine over the k children's level-(n−1) values. The six solved
problems use this one fact in three ways.

| problem | the copies | what one copy is summarised by |
|---|---|---|
| 199 Iterative Circle Packing | each curvilinear gap holds a circle and three smaller gaps | the gap's curvature triple |
| 220 Heighway Dragon | `a → aRbFR`, `b → LFaLb` | net displacement and net rotation |
| 226 A Scoop of Blancmange | Takagi curve on a dyadic interval = chord + scaled Takagi curve | exact integral and a height bound |
| 297 Zeckendorf Representation | numbers in [Fᵢ, Fᵢ₊₁) are Fᵢ + (numbers below Fᵢ₋₁) | the block total of z(n) |
| 395 Pythagorean Tree | the tree = square + two similar trees | the support (extent) in four directions |
| 943 Self Describing Sequences | each element is the parent of one run in a derivation tree | leaf count, leaf sum, parity mask |

## Summarise a copy instead of drawing it

**220** is the clearest example. The level-50 dragon string has 2⁵⁰ draw steps, but the effect of
expanding `a` or `b` to level n is just a displacement and a turn, measured in a frame where the
copy starts heading east. Because the copy can start in any orientation, the solution stores
headings and displacements as Gaussian integers and rotates by multiplying them:

```python
def mul(u, v):                    # (x, y) as x + iy: rotate u by v
    return (u[0]*v[0] - u[1]*v[1], u[0]*v[1] + u[1]*v[0])
```

The level-n summary of `a` is then the five-symbol rule `aRbFR` read with the level-(n−1) summaries
substituted for `a` and `b`. Building the table is O(n). The coordinates are exact integers, so the
answer has no rounding error to worry about.

**395** does the same with a continuous attractor. The Pythagorean tree is the unit square plus its
images under two complex similarities z ↦ i + w·z and z ↦ i + w + (1 − w)·z, with w fixed by the
3-4-5 triangle. The quantity it needs is the
[support function](/topics/technique/support-function) h(d) = max Re(z·d̄) over the tree in each
axis direction d. The support function satisfies the self-similarity equation directly: the
support of f(S) in direction d is Re(shift·d̄) + |scale|·h_S(rotated d). One extra fact keeps the
state small. arg(1 − w) = arg(w) − π/2, so a subtree's orientation depends only on its depth and on
its number of right turns mod 4. That makes it a DP over depth with four values per level.

**226** uses self-similarity to integrate exactly. The
[blancmange curve](/topics/domain/blancmange-curve) T satisfies a two-scale identity: on any dyadic
interval [a, b] of width w, T equals the straight chord between T(a) and T(b) plus a copy of T
scaled by w in both directions. Since ∫₀¹ T = ½, this gives

    ∫ₐᵇ T = w·(T(a) + T(b))/2 + w²/2,       T ≤ chord + 2w/3 on [a, b]

which is an exact integral and a rigorous upper bound at the cost of two point evaluations. A
dyadic point i/2ᵏ also has an exact Takagi value, because its series stops after k terms. The
quadrature therefore never samples the fractal. It certifies whole dyadic intervals as inside or
outside the circle, and subdivides only the thin band where the curve crosses the circle's
boundary.

## Count the copies, not the instances

Self-similar objects repeat themselves, so many of the subproblems are identical. In **199** every
gap is determined by the three curvatures that bound it, and the
[Descartes circle theorem](/topics/technique/descartes-circle-theorem) gives the new circle's
curvature k₄ = k₁ + k₂ + k₃ + 2√(k₁k₂ + k₂k₃ + k₃k₁) from that triple alone. After n iterations
there are 4·3ⁿ gaps but far fewer distinct triples. The Python side keys a dictionary by the sorted
triple and carries a multiplicity count, so each iteration costs one step per distinct gap shape.

**943** takes the same idea much further. A generalised [Kolakoski](/topics/domain/kolakoski-sequence)
sequence is the leaf level of a derivation tree in which each element is the parent of one run. Two
subtrees are identical when their value, their height and the parities of their leftmost
descendants' positions all match. That triple is the
[memo key](/topics/takeaway/memo-key-is-the-full-state), and leaving out the parity mask would give
wrong answers. A node with a large value has a long run of children whose masks evolve
deterministically. That chain soon repeats, so [cycle detection](/topics/technique/cycle-detection)
replaces k children with q whole periods plus a remainder. This is self-similarity inside a single
level as well as across levels.

## Descend to a prefix

Problems 220, 297 and 943 ask about a **prefix** of the object: the position after 10¹² steps, the
sum of z(n) below 10¹⁷, the sum of the first n elements. All three use the same walk. Start at the
root. At each child, ask whether the whole copy fits in the remaining budget. If it does, take its
cached summary in O(1) and subtract its size. If it does not, go down into it:

```python
while budget:
    for child in children(node):
        if size(child) <= budget:
            acc = combine(acc, summary(child))      # a whole copy: O(1)
            budget -= size(child)
        else:
            node = child                            # the frontier: descend
            break
```

Only one root-to-leaf path is expanded, so the cost is the depth: O(n) for the dragon and
O(log N) for Zeckendorf. In **297** the "children" are Fibonacci blocks. Every n in [Fᵢ, Fᵢ₊₁)
is Fᵢ plus some m < Fᵢ₋₁, so z(n) = 1 + z(m). That gives each block's total from the two blocks
before it, and the descent is exactly the greedy [Zeckendorf](/topics/domain/zeckendorfs-theorem)
decomposition of the limit. In 943 a run is too long to scan child by child, so the walk uses a
bisection over the chain's prefix sums. Past the stored prefix it first skips whole periods with
one `divmod`.

## Where the infinite recursion stops

A finite combinatorial object has a natural bottom (level 0 of the grammar, the leaves of the
tree). A true fractal does not, and the solution has to choose where to stop and show that the
choice is safe:

- **199** stops after the number of iterations the problem specifies. Nothing is truncated.
- **395** picks the depth at which the tree's invariant disk, scaled by the contraction ratio
  max(|w|, |1 − w|) to that depth, falls below 10⁻¹⁵. It then runs the DP twice. Replacing the
  deeper tree with the bare square gives a lower bound on the support, and replacing it with the
  whole disk gives an upper bound. The gap between the two is the error bound.
- **226** stops subdividing at 2⁻⁴⁵. By then the band left uncertified contributes less than the
  eighth decimal.

The general rule is that a contraction ratio r gives depth ⌈log ε / log r⌉, with the bounding
radius included in ε. It should be derived from the ratio rather than tuned until the digits stop
changing.

## Python and C

The algorithms are the same on both sides. The differences come from what each language makes
cheap:

- **Collapsing duplicates.** Python's `dict` makes memoisation almost free, and 199's multiset of
  gap triples is four lines. The C side of 199 drops the dedup and recurses over every gap, which
  is O(3ⁿ) but only a few hundred thousand calls at the iteration count asked. In 943 dropping the
  memo is not an option, so the C side writes two open-addressed hash tables (nodes and chains)
  with a generation counter. Moving to the next (a, b) pair then empties both tables without
  clearing them. Chain prefix arrays live in one growable pool.
- **Width.** A self-similar count grows geometrically with depth. 297's block totals overflow 64
  bits, so they are `unsigned __int128` in C. 943's leaf counts and sums use `__int128`, because a
  deep subtree of the larger value can hold far more leaves than the prefix asks for. Python's
  integers handle both without help.
- **Complex arithmetic.** 395 maps directly onto C99 `<complex.h>`: `cabs`, `conj`, `creal` and
  `cpow` replace Python's built-in `complex`. 220 uses integer pairs on both sides, with a two-line
  `vmul` in C.
- **Recursion vs. explicit stack.** 220 recurses in both languages, since its depth is the level
  count. 226 already uses an explicit stack in Python, and its C side uses fixed arrays of 128
  entries. That is enough because a depth-first walk to `kmax = 45` never holds more than one
  pending sibling per level.

## Pitfalls

- **Exact keys.** 199 memoises on floats. Equal triples always produce equal children because the
  key is sorted before k₄ is computed. Congruent gaps reached by different arithmetic paths may
  differ in the last bit and fail to merge. That costs time, not correctness, but it means a
  float-keyed memo is only an optimisation and cannot be relied on to deduplicate.
- **Frames.** A cached summary is only valid in the frame it was computed in. 220 and 395 both
  record summaries for a copy entering in a standard orientation, and rotate them on use. Forgetting
  the rotation produces a curve that looks plausible but is wrong.
- **Hidden state.** If two copies look the same but differ in some context the rule depends on,
  such as 943's position parities, a memo keyed on their appearance alone silently merges them.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0220](/solutions/0220/) — Heighway Dragon
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ○ [0570](/solutions/0570/) — Snowflakes
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ○ [0702](/solutions/0702/) — Jumping Flea
- ○ [0894](/solutions/0894/) — Spiral of Circles
- ● [0943](/solutions/0943/) — Self Describing Sequences

<!-- /problems -->
