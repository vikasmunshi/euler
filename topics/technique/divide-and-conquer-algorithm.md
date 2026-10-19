<!-- tags: [divide-and-conquer-algorithm] -->
<!-- status: final -->
# Divide-and-conquer algorithm

A [divide-and-conquer algorithm](https://en.wikipedia.org/wiki/Divide-and-conquer_algorithm)
solves a problem by splitting it into smaller instances of the *same* problem, solving those, and
combining the results. Textbooks show it with merge sort and binary search. In Project Euler it
looks different: the input is an object defined by a self-referential rule, such as a curve built
from scaled copies of itself, a string made by concatenating its predecessors, or a sequence
indexed by the bits of $n$. That rule *is* the split. The three solved problems below each answer
a question about an object far too large to build, by descending through its definition and
following only the parts that matter.

## The idea — let the definition do the splitting

Every divide-and-conquer algorithm has three parts: a **split** into subproblems, a **base case**
solved directly, and a **combine** step. Its cost follows from the shape of the split. Write $T(n)$
for the cost on an input of size $n$ ([master theorem](https://en.wikipedia.org/wiki/Master_theorem_(analysis_of_algorithms))):

| recursion | cost | example |
|---|---|---|
| $T(n) = T(n/2) + O(1)$, one branch survives | $O(\log n)$ | binary search, 230, 918 |
| $T(n) = 2T(n/2) + O(n)$, both branches, linear combine | $O(n \log n)$ | merge sort |
| both branches, but most pruned at the first level | ≈ the size of the boundary | 226 |

The useful cases here are the first and the last. When only **one** subproblem is relevant to the
question, recursion becomes a loop down a single path, and an input of size $10^{17}$ takes about
60 steps. When **both** subproblems are kept but most of them can be *settled* without recursing,
by a closed form or a bound, the work concentrates on the few pieces where the answer is unclear.

Self-similar objects fit this well. The rule that defines them already says how a big instance
is made of smaller ones, so you do not have to invent the split. You only have to recognise it.

## Three descents across the problems

**226, a scoop of blancmange: split an interval, prune with bounds.** The question is the area
inside a small circle and under the [blancmange curve](/topics/domain/blancmange-curve)
$T(x) = \sum s(2^n x)/2^n$, which is continuous but nowhere differentiable. Ordinary quadrature on a
fractal converges only linearly. The curve's self-similarity gives a better split. On any dyadic
interval $[i/2^k, (i+1)/2^k]$, $T$ is the chord between its endpoints plus a copy of the whole
curve scaled by $2^{-k}$. That one fact supplies both things a pruning recursion needs. It gives a
**closed form**: the integral of $T$ over the interval is the trapezoid plus $\tfrac12 w^2$, exactly.
It also gives a **bound**: $T$ sits between the chord and the chord plus $\tfrac23 w$. Each interval
is therefore *interior* (the curve lies within the disk, so the area is closed form minus a
circular-segment integral), *empty* (the curve lies below the disk), or *ambiguous*, and only
ambiguous intervals are halved. Those lie in the thin band where the curve crosses the lower arc,
so the recursion visits fewer than a thousand intervals. Both languages drive it with an explicit
stack of `(k, i)` pairs instead of call recursion.

**230, Fibonacci words: one branch, by length alone.** The terms are
$T_k = T_{k-2}T_{k-1}$, seeded with two 100-digit strings, and digits are wanted at positions near
$10^{17}$. The split comes from the definition. Position $n$ of $T_k$ lies in the prefix $T_{k-2}$
if $n \le |T_{k-2}|$; otherwise it is position $n - |T_{k-2}|$ of $T_{k-1}$. Only one side holds
the digit, so the descent is a loop over a table of about 80 lengths, which grow as Fibonacci
numbers. The string itself is never built. This is the same move as binary search, except the
split is at Fibonacci proportions instead of halves. See [Fibonacci word](/topics/domain/fibonacci-word).

**918, recursive sequence summation: one branch per bit, carrying a pair.** The sequence
$a_{2n} = 2a_n$, $a_{2n+1} = a_n - 3a_{n+1}$ is indexed in binary, and a telescoping argument
reduces $S(10^{12})$ to a single term $a_m$. Evaluating $a_m$ is the divide-and-conquer step,
with one wrinkle. The odd case needs *two* subproblems, $a_n$ and $a_{n+1}$, so recursing on a
single value would branch. The fix is to make the subproblem the pair $(a_n, a_{n+1})$. Both
children of the pair are linear in it, and each bit of $m$ after the leading 1 selects one. The
descent then has one branch again and runs in $\lfloor \log_2 m \rfloor$ steps. Recursion with
two overlapping calls becomes linear-time descent once the state is widened. It is the same trick
that makes [Fibonacci fast doubling](/topics/technique/fibonacci-fast-doubling) logarithmic.

## Python and C

The algorithms are the same in both languages; they differ in how the recursion's state is held.

- **226** uses a Python `list` of tuples as a stack. C uses two fixed `long long`/`int` arrays of
  128 entries. That is safe because a depth-first walk keeps at most about one pending sibling per
  level, and the depth is capped at 45.
- **230** grows a Python list of lengths until it passes the largest position. C fills a
  fixed `long long lengths[128]`. Fibonacci growth overflows 64 bits long before 128 terms, so
  the bound can never be reached. Python finds the starting term with `next(...)` over
  `enumerate`; C uses a `while` scan.
- **918** reads the bits as a string, `bin(m)[3:]` (dropping `0b1`), in Python. C scans down
  from bit 63 for the leading 1 and then tests `(m >> b) & 1`. The values stay inside `int64`, so
  C needs no wider type.

## How to reason about it

- **Look for the split in the definition.** A self-similar curve, a concatenation rule, or a
  recurrence on $2n$ and $2n+1$ already tells you how a large instance decomposes. Do not build the
  object; walk its definition.
- **Ask how many branches survive.** If the question touches only one subproblem, as with a single
  digit or a single term, the recursion is a loop and the cost is the depth: $O(\log n)$.
- **Widen the state to stop the branching.** When one value needs two children (918), recurse on a
  tuple of values that is closed under the split.
- **Prune with closed forms and bounds.** When both halves matter (226), settle whole subproblems
  exactly where you can and subdivide only where the bound cannot decide. The work then tracks the
  boundary, not the input.
- **Prefer an explicit stack or loop.** A descent of depth 45 or 80 would fit Python's recursion
  limit. An explicit stack still makes the state visible and maps directly onto a fixed C array.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0918](/solutions/0918/) — Recursive Sequence Summation

<!-- /problems -->
