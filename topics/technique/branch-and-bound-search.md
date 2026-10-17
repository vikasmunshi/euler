<!-- tags: [branch-and-bound-search] -->
<!-- status: final 2026-10-17T07:33Z -->
# Branch and bound

A [branch-and-bound](https://en.wikipedia.org/wiki/Branch_and_bound) search is only as fast as the
moment its bound starts to bite, and that moment is decided by the order of the search: which node
is expanded next, which child is tried first, and where in a node the test sits. The sibling page,
[branch and bound](/topics/technique/branch-and-bound), is about finding a valid, cheap, tight
bound. This page takes the bound as given and is about the machinery around it. The five solutions
below all use the same search shape, a [depth-first](/topics/technique/depth-first-search) walk,
and differ in how they order children so that a failed test can end a whole loop, and in what they
do with a node once it is pruned.

## The idea

A search tree has three orders to choose, and each changes how much the same bound removes.

**Node order.** Branch and bound is usually taught with a best-first queue: always expand the node
with the most promising bound. None of these solutions does that. All five go depth-first, by
recursion (98, 103, 108, 233) or with an explicit stack (226). There are two reasons. A depth-first
walk reaches a complete candidate after $d$ steps, so an optimisation search has an incumbent to
prune against almost immediately. And its memory is $O(\text{depth})$, while a best-first or
[breadth-first](/topics/technique/breadth-first-search) frontier can hold a large fraction of the
tree. When the bound is good, the extra nodes a depth-first walk expands cost less than a priority
queue would.

**Child order.** This is the one that matters most. If the children of a node are tried in an order
along which the bound only gets worse, the first child that fails the test proves that every later
child fails too, so the loop can `break` instead of `continue`. Three of the solutions are built
that way:

| Problem | Loop variable and direction | Bound that fails monotonically |
|---|---|---|
| 103 | next element $v$, ascending | lower bound on the final sum grows with $v$ |
| 108 | exponent $e$ of the current prime, descending | the most $\tau(n^2)$ the remaining primes could reach shrinks with $e$ |
| 233 | prime $p$, ascending | $p^e$ against the remaining headroom grows with $p$ |

Problem 103 shows the gain clearly. The search builds a special sum set one strictly increasing
element at a time, each confined to a window of $\pm 5$ around a seed construction. Its lower bound
on the finished total is the partial sum plus the smallest possible tail:

```python
for v in range(mn, hi[idx] + 1):
    lb = s + v + rem * v + rem * (rem + 1) // 2   # every later element is > v, by at least 1 more each
    if lb >= best_sum:
        break                                     # larger v only raises lb
```

Because `lb` is increasing in `v`, one failed comparison discards the rest of the window and every
subtree below it.

**Goal order.** Sometimes the order can be arranged so that the first complete solution found is
the optimum, and the search simply stops. Problem 98 wants the largest square that maps, through a
letter-to-digit [bijection](https://en.wikipedia.org/wiki/Bijection), onto a pair of
[anagrams](/topics/technique/anagram). A longer square is always larger, so the solution visits word
lengths in descending order and returns at the first length that produces any pair. Every shorter
length is pruned without being examined, and no bound is computed at all: the order itself is the
proof.

## What a pruned node turns into

The textbook picture is an optimisation search that compares each node's bound with an incumbent.
Only two of the five work that way. The others show that the same skeleton serves three other
purposes, depending on what the test proves about the node.

- **Cut against an incumbent** (103, 108). The node cannot beat the best solution so far, so it is
  dropped. This is the only case where the result depends on finding good solutions early.
  Problem 103 seeds the incumbent before the search starts, with the sum of the construction it is
  refining whenever that construction is itself a valid special set. Problem 108 starts `best` at infinity and instead relies on child order: trying the
  largest exponent first on the small primes reaches a $\tau$ large enough at a shallow depth, so a
  first incumbent arrives within a few calls.
- **Cut by feasibility in a count** (233). The search enumerates every number below a limit with a
  given prime-exponent pattern, to sum over all of them, so there is no incumbent and nothing to
  improve. The bound is a budget: the product so far, times the smallest value the unfilled exponent
  slots could still take (precomputed as suffix minima per pattern), must stay under the limit. In
  a count the order cannot make the bound tighter; its only job is to make the cut a `break`.
- **Resolved in closed form** (226). The search covers $[0, \tfrac12]$ with
  [dyadic](https://en.wikipedia.org/wiki/Dyadic_rational) intervals to integrate the area between
  the [blancmange curve](/topics/domain/blancmange-curve) and a circle. On each interval the curve's
  self-similarity bounds it above and below. If those bounds put the curve entirely below the circle,
  the interval contributes nothing. If they put it entirely inside, its area is exact. Only an
  interval that straddles the boundary is split. Pruning here does not throw a node away: it settles
  it. This is the counting form described on the sibling page, applied to an integral.
- **Stop at the first hit** (98). As above, the order guarantees that the first success is the best,
  so the whole remaining tree is pruned at once.

## How to reason about it

**Earn every `break` with a monotonicity argument.** A `break` makes a claim about every remaining
child, so it needs a reason. Two tests in these solutions have no such reason and correctly stay
`continue`. In problem 233, the "prime already used in this core" test is not monotone in $p$. In
problem 108, the `new_n < best` test runs while $e$ decreases, so $n$ shrinks and a child that fails
may be followed by one that passes. Writing `break` there would compile, run and silently lose
answers.

**Put the cheap test first, wherever the test is.** Problem 103 checks a complete set against two
conditions: an $O(n^2)$ size test using prefix and suffix sums, and an $O(2^n)$ distinct-subset-sum
test. Its two solutions differ only in which one runs first. Since most leaves fail the cheap test,
running it first is worth 7.8× at $n=7$ and 3.6× at $n=9$ in C, and about 1.8× in Python. Problem
98 has the same structure at a finer grain: before building a letter-to-digit map, it compares the
sorted multiplicity patterns of the word and the square (a word with two repeated letters cannot
match a square with all digits distinct), which rejects almost every pair for the cost of a short
string compare.

**Feasibility at the leaves is a cost model, not a rule.** Problem 103 only tests the special-set
conditions at complete leaves, so every leaf that survives the sum bound pays for that test. When
the leaf check dominates, as it does there, the next step is to test a necessary condition on the
partial set, which turns a leaf rejection into an interior cut. Ordering the leaf check is the
cheaper fix, and the measurements above show how far it goes.

**Choose `>=` or `>` on purpose.** Problem 103 cuts at `lb >= best_sum`, which also prunes subtrees
that could only tie the incumbent. That is correct because one optimum is all that is wanted. A
search that needs every optimum, or the lexicographically first one under some other order, has to
cut only on `>`.

**Decide what "first hit" means.** Problem 98's two ports stop at different points. The Python
solution returns at the first word-to-square mapping that yields a pair at the longest length. The C
solution finishes the whole length, keeps the maximum, and only then lets its outer loop stop. On
the given word list the two agree, but only the C version is correct by construction if several
pairs could share the longest length. Descending length proves that the answer lies in the first
productive *level*, not in the first productive node, so the search should finish that level.

**Cap the depth when the tree is infinite.** Problem 226's subdivision never ends on its own near the
points where the curve crosses the circle. It stops at $k = 45$ halvings and takes a midpoint
estimate there, an interval of width $2^{-45}$ whose error is far below the eight decimals asked
for. Any certify-or-split search over a continuum needs such a floor, and it should be justified
against the required precision, not chosen by trial.

## C and Python

The search order is identical across every pair. The ports differ in how they carry state through
the recursion and in the arithmetic the bound needs.

| Concern | Python | C |
|---|---|---|
| Incumbent and counters | closure with `nonlocal best` / `nonlocal answer` (103, 108, 233) | file-scope statics or a `search_t` struct passed by pointer (103, 108, 233) |
| Depth-first stack | `list` of `(k, i)` tuples, `append`/`pop` (226) | two fixed arrays of 128 entries: popping one interval pushes two, so the stack never holds more than about $k_{\max}+1$ (226) |
| Primes already spent on the current path | `frozenset` built by `used \| {index}` per child (233) | a `size_t` array copied into a `nested` buffer per child and scanned linearly; the path is at most a few primes long (233) |
| Products checked against the bound | unbounded `int`, compared directly (108, 233) | divide instead of multiply, `new_n > best / p`, before forming the product (108); `__int128` for the product of the partial core and the minimal tail, and for the accumulated sum (233) |
| Reachability bound $\tau \cdot (2e+1)^{r}$ | `factor**remaining`, computed in full (108) | multiplied one factor at a time, stopping as soon as it reaches the target, so it never overflows (108) |
| Set membership at a leaf | `set` of square strings (98) | linear scan of a `char *` list, enough for the few thousand squares of one length (98) |

The [integer-overflow](/topics/technique/integer-overflow) row is where order and bound meet. In
problem 108, the first branch of the depth-first walk is the most extreme one, the largest
exponent on every prime, so it produces the largest products in the whole search before any
incumbent exists. A C port that multiplied first would overflow on its very first descent. With
`best` starting at `LLONG_MAX`, the division test is the overflow guard and the incumbent cut at
the same time.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0233](/solutions/0233/) — Lattice Points on a Circle

<!-- /problems -->
