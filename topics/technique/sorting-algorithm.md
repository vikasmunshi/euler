<!-- tags: [sorting-algorithm] -->
<!-- status: final -->
# Sorting algorithm

A [sorting algorithm](https://en.wikipedia.org/wiki/Sorting_algorithm) puts a sequence in
order, and in a Project Euler solution that is almost never the point. Look at the problems
below and the ordered list is a means every time: a way to make two things comparable, to
find the *k*-th of something, to let a greedy loop be correct, or to bring equal items next
to each other. `sorted()` is one call and one `n log n` line in the cost model — what
matters is which of those jobs you are buying.

## Sorting as a canonical form

The most Euler-typical use of a sort produces no ordering anyone reads. "Is `x` a
permutation of `y`?" is an awkward predicate; sort the digits of each and it collapses into
`==`. That sorted string is a **canonical form** — one representative per equivalence class,
so a set or dict can do the rest.

Problem 52 is the idea at its barest: `x` is the answer when `x, 2x, … 6x` all share one
digit fingerprint.

```python
if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
```

Problem 70 uses the same key to ask whether `n` and `φ(n)` are permutations of each other;
problem 49 sorts the members of a candidate triple so that the same three primes found in a
different order register as one sequence. Problem 98 canonicalises twice over, which is
worth seeing: `"".join(sorted(word))` groups the dictionary into anagram classes, and then a
*second* sort — character repeat counts, descending — gives a signature that survives any
relabelling of the letters:

```python
return "".join(map(str, sorted((s.count(c) for c in set(s)), reverse=True)))
```

Two words can only be a substitution match if those signatures agree, and the check costs
nothing next to trying the mappings. The general move: when a problem says "up to
reordering" or "up to renaming", find the sort that makes the class representative, and the
search over pairs becomes a lookup.

## Sorting to rank

The second family is problems whose answer is literally an index into an ordered list — the
*k*-th smallest of something you can generate but not directly address. Problem 22 is the
starter version, sorting a name file alphabetically because the position *is* half the
score:

```python
names = sorted(runner.get_text_file(file_url).split(","))
```

The harder ones share a shape: characterise the candidates mathematically, generate all of
them, sort, index. Problem 124 sieves the radical of every `n` up to a bound and sorts by
`(rad(n), n)` — a tuple key, so Python's lexicographic tuple comparison handles the stated
tie-break with no custom comparator. Problem 140 generates golden nuggets from a Pell-style
recurrence and sums the first `n` in order; problem 248 enumerates the solutions of
`φ(n) = 13!` and wants a particular one by rank; problem 119 filters powers by their digit
sum and sorts what survives.

The trap in this family is generating in an order that *looks* sorted. A recurrence emits
its own terms monotonically, so it is tempting to skip the sort — but the moment the
generation runs *several* families and concatenates them, the merged output is not ordered
and the error is silent. Problem 321 is the clean example: its candidates come from two
fundamental solutions of one Pell equation, each iterated independently, and the answer sums
the smallest few across both. Either family alone is already ascending; together they
interleave. Sorting explicitly costs one `n log n` on a list made of two ordered runs, which
[Timsort](https://en.wikipedia.org/wiki/Timsort) merges in nearly linear time precisely
because it detects runs. Pay it.

## Sorting so a greedy loop is correct

Here the order is load-bearing for correctness, not convenience. [Kruskal's
algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm) — the minimum spanning tree
behind problems 107 and 1000 — is a sort followed by a linear scan:

```python
edges.sort()
for w, u, v in edges:
    if find(u) != find(v):
        union(u, v)
```

The greedy choice is only optimal because the edges arrive lightest-first; the
[cut property](https://en.wikipedia.org/wiki/Minimum_spanning_tree#Cut_property) is what
licenses it. Note that the edges are `(weight, u, v)` tuples, so `sort()` needs no `key=` at
all — putting the comparison field first in a tuple is the cheapest way to express "order by
this" in Python.

Problem 96's Sudoku solver sorts for a different kind of correctness — not of the answer, but
of the search. Before each guess it reorders the unfilled cells by how many candidates they
have left:

```python
empty_cells.sort(key=lambda c: len(c[2]))
```

That is the [minimum-remaining-values](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem)
heuristic: always branch where the branching factor is smallest, so contradictions surface
near the top of the tree instead of after a deep fruitless descent. The sort is inside the
recursion and is pure overhead in the cost model, and it still wins by orders of magnitude,
because it prunes. When a backtracking search is too slow, "what should I sort the frontier
by?" is usually a better question than "how do I make the inner loop faster?".

## Sorting to group, dedup, and stop early

Sorting brings equal keys adjacent, which turns "count the distinct values" into one pass
with one comparison per element. Problem 165 generates every intersection point of a set of
segments as an exact rational and needs the number of *distinct* ones; problem 757 generates
`O(√N)` candidate values that repeat. Both sort and scan for changes rather than building a
hash set — in C that is the whole reason, since there is no `dict` in the standard library
and a `qsort` plus a scan is a dozen lines. Problem 177 does the same to fold a large key
list into its distinct classes.

Even in Python the choice is not automatic. A hash set is `O(n)` expected against
`O(n log n)`, but it pays a pointer and a hash per element; for tens of millions of fixed-width
values, sorting an array in place is more cache-friendly and uses a fraction of the memory.
Sort-and-scan also gives you the *multiplicities* for free, which a plain set discards.

The related trick is sorting so a scan can **stop**. Problem 127 sorts its candidates by
radical, which converts the filter `rad(a) < bound` into a prefix of the list — once one
element fails, every later one does too, and the inner loop breaks instead of running to the
end. Sorting to create monotonicity, so that a `break` becomes valid, is one of the highest-leverage
uses of `n log n` there is: it changes the inner loop's expected length, not its constant.

Problem 184 is the geometric member of the family, sorting lattice points by
`atan2(y, x)` — angular order. Once the points are arranged around the circle, "does this
triangle contain the origin?" becomes a question about angular spans, answerable by a
two-pointer sweep over the sorted list rather than a test per triple.

## How to reason about it

**The cost model.** Any comparison sort is `Ω(n log n)`; Python's `list.sort` and `sorted`
are Timsort — stable, adaptive, `O(n)` on data that is already ordered or reverse-ordered.
C's `qsort` is `O(n log n)` average but calls your comparator through a function pointer,
which is a real constant on tens of millions of elements. Sorting is rarely the bottleneck;
sorting *inside a loop* usually is.

**`key=` is computed once per element**, not once per comparison — Python decorates, sorts,
and undecorates. So an expensive key is fine, and writing `key=lambda x: expensive(x)` is
strictly better than a comparator that recomputes. Conversely, a trivial `key=` lambda still
costs one Python-level call per element; if the natural tuple order already says what you
mean, drop it.

**Stability is a guarantee you can spend.** Python's sort is stable, so sorting by a
secondary key and then by a primary key gives the compound order. `sorted(xs, key=...)` on a
tuple key does it in one pass and is clearer.

**Know when not to sort.** Four common escapes:

| Situation | Better than a full sort |
| --- | --- |
| you need the `k` smallest, `k ≪ n` | [`heapq.nsmallest`](https://docs.python.org/3/library/heapq.html) — `O(n log k)` |
| you need one element by rank | [quickselect](https://en.wikipedia.org/wiki/Quickselect) — `O(n)` average |
| keys are small bounded integers | [counting sort](https://en.wikipedia.org/wiki/Counting_sort) — `O(n + k)`, or just index an array |
| you only need membership, never order | a `set` — `O(1)` per lookup, no sort at all |
| you need repeated lookups in a static ordered list | sort once, then [`bisect`](https://docs.python.org/3/library/bisect.html) — `O(log n)` each |

That last row is the one worth internalising: the payoff for sorting is usually not the
ordered list itself but the binary searches it enables afterwards. One `n log n` up front
buys `log n` lookups forever, and that trade only makes sense if you are going to make many
of them.

**Do not sort floats you intend to compare for equality.** Problem 165 sorts exact rationals
(integer numerator/denominator pairs, reduced) precisely so that dedup is a comparison and
not a tolerance test. If a sort key is a float and you then check adjacent elements for
equality, you have written a bug that appears at scale.

**Build the list inside `solve()`.** A candidate list assembled and sorted at module import
is free from the second benchmark run onward, and the timing will lie about it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0022](/solutions/0022/) — Names Scores
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0096](/solutions/0096/) — Su Doku
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0107](/solutions/0107/) — Minimal Network
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
