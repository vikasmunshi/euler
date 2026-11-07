<!-- tags: [functional-graph] -->
<!-- status: final 2026-10-14T12:06Z -->
# Functional graph

A [functional graph](https://en.wikipedia.org/wiki/Functional_graph) is what you get when you take
a map `f: S → S` on a finite set and draw an arrow from every `x` to `f(x)`. Every node has exactly
one outgoing edge. Project Euler builds these constantly, usually without saying so: "replace `n`
by the sum of the factorials of its digits" (74), "replace `n` by the sum of its proper divisors"
(95), "sort the digits and subtract" (414), "each floor powers some other floor" (522). Each one
asks some version of the same question: *if I keep applying the rule, where do I end up, and how
long does it take?* The answer always has the same shape, and once I recognise the shape the
algorithm mostly writes itself.

## The shape: rho, tails and cycles

Iterate `f` from any start `x₀` and the sequence `x₀, f(x₀), f(f(x₀)), …` lives in a finite set, so
by pigeonhole some value repeats. Since each value has only one successor, the walk is periodic from
the first repeat on. The trajectory is a **tail** of `μ` distinct values followed by a **cycle** of
length `λ`, which looks like the Greek letter ρ:

```
x₀ → x₁ → … → x_μ → … → x_{μ+λ−1}
                ↑               │
                └───────────────┘
```

Zoom out from one trajectory to the whole graph and the picture is just as regular. Each connected
component contains exactly one cycle, and every other node sits in a tree that hangs off that cycle
and points toward it. So a functional graph is a set of cycles with in-trees attached. Three facts
follow, and the problems lean on all three:

- **Paths merge and never split.** Once two walks reach the same node, they share everything that
  comes after it. That's what makes caching work.
- **Cycle nodes are exactly the nodes that come back to themselves.** Those are the nodes with
  `f^(m)(x) = x` for some `m ≥ 1`, which is the set Problem 971 asks you to count. For a
  [permutation](https://en.wikipedia.org/wiki/Cyclic_permutation), every node lies on a cycle;
  for a general map, most nodes are usually on tails.
- **The length of a walk is `μ + λ`.** "Number of distinct terms before a repeat", which is what
  74 counts, is that total.

What changes from problem to problem is the question asked of the structure. Problem 74 wants the
`μ + λ` of every start. Problem 95 wants the longest cycle and doesn't care about tails at all.
Problem 414 wants the time it takes to reach a known fixed point. Problems 522 and 871 ask
combinatorial questions about the cycle and tree structure of a given or random map. Problems 703
and 977 count functions that respect the graph. I'm still reading the same object in every case.

## Following one trajectory: Floyd and Brent

When I only care about a single trajectory and the state space is too large to index (big
integers, `x² + c mod n` in [Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm),
a long Kaprekar orbit), I can't afford an array over `S`. I may not even want a hash set of
everything visited. [Floyd's tortoise and hare](https://en.wikipedia.org/wiki/Cycle_detection#Floyd's_tortoise_and_hare)
finds `μ` and `λ` in O(1) memory. One pointer moves one step at a time and the other moves two;
once both are inside the cycle the gap between them shrinks by one per step, so they have to meet:

```python
def floyd(f, x0):
    slow, fast = f(x0), f(f(x0))
    while slow != fast:                        # meet somewhere on the cycle
        slow, fast = f(slow), f(f(fast))
    mu, slow = 0, x0
    while slow != fast:                        # equal speeds from x0 and the meet point
        slow, fast = f(slow), f(fast)          # converge on the cycle's entrance
        mu += 1
    lam, fast = 1, f(slow)
    while slow != fast:                        # one lap measures the period
        fast, lam = f(fast), lam + 1
    return mu, lam
```

The second phase works because the meeting point is a multiple of `λ` steps from `x₀`. Walking `μ`
more steps from there lands on the cycle entrance, and so does walking `μ` steps from `x₀`.
[Brent's variant](https://en.wikipedia.org/wiki/Cycle_detection#Brent's_algorithm) teleports the
tortoise to the hare at powers of two. It gives `λ` directly and calls `f` fewer times, which
matters when `f` is the expensive part.

To be honest, though, for the Euler problems in this tag Floyd is rarely the right tool. It is
built for *one* walk in a space I can't afford to index. These problems usually ask about *every*
start in a bounded range, and then memory is cheap and the work is shared.

## Following all trajectories: walk, mark, back-propagate

When the question covers every start `x ∈ [1, N]` and the reachable values fit in an array, the
merge property turns `N` walks into roughly `N` total steps. I walk forward from a start and record
the path until I hit one of two things:

1. **A node already solved** in an earlier walk. Its answer is known, so the answer for every node
   on my path follows by counting backwards: `path[i]` is `len(path) − i` steps ahead of the solved
   node.
2. **A node already on the current path.** That closes a new cycle. The nodes from that point on
   are the cycle, each with length `λ`, and the nodes before it are tail.

After either case I write every path node into the cache and never walk through it again. This is
the [memoization](../technique/memoization.md) pattern specialised to a graph with out-degree one.
It works for the same reason path compression works in union-find: one traversal fills in answers
for everything it touched. Problem 74's `p0074_s0.py` is the plain version:

```python
while current not in seen and current not in chain_length_cache:
    seen.append(current)
    current = graph[current]
length = len(seen) + chain_length_cache.get(current, 0)
for i, num in enumerate(seen):                 # seen[i] is i steps down the same chain
    chain_length_cache[num] = length - i
```

One subtlety: if the walk closes a cycle partway along, say at `seen[j]`, then every node from `j`
onward has length `λ`, not `length − i`. The snippet above skips that case. In 74 the only loops
are short (145, 169 → 363601 → 1454, 871 ↔ 45361, …), so the snippet can give a cycle node too
short a length, but those wrong lengths stay nowhere near the sixty being counted. The general
version stores each node's *position* in the current path, so the cycle start `j` falls out of a
lookup. That's what `p0095_s0.c` does with its `in_path` array, and it then marks the nodes before
`j` as tail.

The classic three-colour form of the same idea (unvisited / on the current path / finished, as in
depth-first search) labels every node of a functional graph as cycle or tail in O(|S|) total. The
labels can be lengths, cycle ids, distances to the cycle, or anything else that propagates one step
backward along an edge.

## Bounding the state space first

None of this works until I know the walk stays somewhere I can index, and that's usually the real
first step:

- **Digit maps shrink.** A `d`-digit number maps to at most `d · 9! ≤ 7 · 362880` under the
  digit-factorial rule, so every orbit from below a million stays below 2.6 million and a flat array
  covers it. The same kind of argument bounds digit-square sums ([Problem 92](/solutions/0092/)) and
  Kaprekar steps (414: the number of digits never grows).
- **Some walks leave the domain.** The aliquot map `s(n)` in 95 can exceed `N` or reach 1 and then
  0. A chain that leaves `[1, N]` is disqualified, so "out of range" works as a third stopping
  condition. I also don't need to know whether the [aliquot sequence](https://en.wikipedia.org/wiki/Aliquot_sequence)
  ever comes back.
- **Precompute `f` if it's the expensive part.** In 95, evaluating `s(n)` costs a factorisation,
  so the whole edge array comes from a [divisor-sum sieve](../technique/divisor-sum-sieve.md) in
  O(N log N). After that, the graph walk is the cheap part.

## Asking only about cycles

When the question is only about cycles (95's longest [amicable chain](amicable-numbers.md), 971's
count of periodic points), tails are wasted work, and there's a cheap way to avoid them. Iterate
the starts upward and abandon a walk the moment it drops below the start. Every cycle is then found
exactly once, from its smallest member, and that member is the one 95 asks you to report.
`p0095_s0.py` builds the bound into the loop condition, `while i <= c <= max_num and c not in ch`,
so the Python solution can drop tail bookkeeping almost entirely.

At larger scales the structure itself helps. When `f` is a polynomial map mod a prime, as in 971
and 871, the point is usually to understand `f`'s algebra (which values are hit, how many
preimages each has) well enough to count cycle nodes or tree shapes without walking `p` steps per
prime. That's the honest boundary of this page. Up to about 10⁷ nodes, walking and caching is the
whole method. Past that, the functional-graph picture still tells me *what* to count, and number
theory has to tell me how.

## Pitfalls

- **Off-by-one on "chain length".** Decide whether the repeated term counts. 74 counts distinct
  terms, so the start `69 → 363600 → 1454 → 169 → 363601 → 1454` has length 5.
- **Treating the first repeat as the start.** The node where a walk closes is the cycle entrance,
  not necessarily `x₀`. Tail nodes must not get the cycle's length.
- **Recursion depth.** A recursive memoised `length(x) = 1 + length(f(x))` is elegant but blows
  Python's stack on long tails. The explicit path list is the iterative form of the same recursion.
- **Caching across `--runs`.** The cache is the algorithm, so build it inside `solve()`. A module
  level cache would make every run after the first free.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0095](/solutions/0095/) — Amicable Chains
- ○ [0414](/solutions/0414/) — Kaprekar Constant
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0703](/solutions/0703/) — Circular Logic II
- ○ [0871](/solutions/0871/) — Drifting Subsets
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ○ [0977](/solutions/0977/) — Iterated Functions

<!-- /problems -->
