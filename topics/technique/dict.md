<!-- tags: [dict] -->
<!-- status: final -->
# dict

Python's [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) is a
[hash table](/topics/technique/hash-table) with average $O(1)$ lookup, insertion and deletion, keyed
by anything hashable. Next to [`set`](/topics/technique/set), which answers *have I seen this?*, a
dict answers *what did I associate with it?* — and that second question turns out to be the one most
of the problems below are really asking. The tag is worth having because the answer takes five
recognisably different shapes, and picking the wrong one is how a dict becomes the slowest line in
the program.

## Five jobs

**A table you write out by hand.** Sometimes the map *is* the data, and the honest thing is to
declare it. Problem 17 spells numbers in English from a literal `{1: "one", …, 90: "ninety"}`; problem
89 carries Roman numerals both ways, `{"I": 1, "V": 5, …}` for parsing and value → numeral for
emitting. Irregular domain knowledge — English has "eleven" but not "onety-one" — belongs in a
declarative table rather than a chain of `if`s, where each entry is checkable by eye. The dispatch
variant maps a key to a *function*: problem 61 keeps three parallel dicts from a figurate-number
[enum](/topics/technique/enum) to its generator, its predicate and its closed form, which is a
[switch statement](/topics/technique/switch-statement) that you can also iterate over.

**A memo keyed on state.** The distinguishing feature against a set is that the stored value carries
the work. Problem 74 memoises digit-factorial chain lengths so each node in the
[functional graph](/topics/domain/functional-graph) is resolved once; problem 17 uses
[`lru_cache`](/topics/technique/functools-lru-cache) on the triplet speller and — importantly —
clears it at the top of `solve()`, so the timed loop measures the real word-building cost rather than
a cache warmed by the previous run. Problem 95's `seen` dict is the sharpest version, because the
value it stores is not just a marker:

```python
if i not in seen:
    ch, c, path = ({i}, divisor_sum[i], [i])
    while i <= c <= max_num and c not in ch:
        ...
    if c == i:
        for x in path:
            seen[x] = len_ch
```

The set `ch` tracks the current path; the dict records, for every node the walk touched, the length
of the chain it belongs to — so the whole graph is traversed once overall rather than once per start.
A set could have prevented the re-walk, but only the dict makes the earlier work reusable.

**A histogram.** The word "exactly once", "distinct count", or "how many ways" in a statement, where
you need the multiplicity and not just the membership. Problem 75 sieves Pythagorean perimeters and
counts the ones reached a single time:

```python
perimeter_count[perimeter] = perimeter_count.get(perimeter, 0) + 1
...
return str(sum((count == 1 for count in perimeter_count.values())))
```

Problem 926 counts how many primes share each exponent in $n!$, collapsing an enormous
factorisation into a handful of exponent classes. Problem 219 is the clever extreme: a greedy
leaf-splitting process over a billion leaves is stored as *cost level → number of leaves at that
level*, so what reads as a priority queue over $n$ items becomes a dict over $O(\log n)$ distinct
keys, and the run finishes in a few hundred steps.

**A sparse state table for dynamic programming.** This is the job that recurs most across the
problems below, and the most transferable. When the DP state is a tuple rather than an index — a
carry plus a set of pending digits (problem 145), a vector of paper sizes in the envelope (problem
151), the last two digits chosen (problem 164), one running remainder per candidate root (problem
269) —
there is no array to index. A dict holds only the *reachable* states, and each step builds a fresh
one:

```python
nxt[key] = nxt.get(key, 0) + ways
```

Two things make this work. Distinct histories that arrive at the same key **merge**, which is the
entire reason the frontier stays small instead of branching exponentially; and building `nxt` fresh
rather than mutating in place prevents a state produced by this step from being advanced again within
it. Problem 152 uses the join form instead — [meet in the
middle](/topics/technique/meet-in-the-middle-attack), with two dicts of partial sums and a lookup of
`target - value` in the other half, which is a hash join by another name.

**A key you compute.** The last job keys the dict on something derived, so that a structural
question becomes a lookup. [Adjacency lists](/topics/technique/adjacency-list) are the common case —
problem 143 stores `dict[int, set[int]]` and finds triangles by intersecting neighbourhoods, problem
79 keeps a successor set per character and reads the passcode off a
[topological sort](/topics/technique/topological-sorting) — and they exist because the vertex labels
are values, not indices $0..n-1$. Problem 816 keys on a *quantised coordinate*, bucketing points into
a [spatial grid](/topics/technique/grid-spatial-index) of cell width $\delta$ so a closest-pair scan
inspects only neighbouring cells. Problem 28's spiral is a `dict[tuple[int, int], int]` read with
`coordinate_map.get((col, row), 0)` — a sparse 2-D array with a default. And problem 926 keys a dict
on *segment boundaries*, multiplying in a factor at the start of each constant-quotient run and its
inverse just past the end, then sweeping `sorted(events)` with a running product: a
[difference array](/topics/technique/prefix-sum) over a sparse key set, with multiplication in place
of addition.

## How to reason about it

- **Choosing the key is the design decision.** Keys must be hashable, so tuples and `frozenset`s
  qualify and lists do not — which forces you to name what the state actually *is*. Problem 151 keys
  on a [`NamedTuple`](/topics/technique/namedtuple) rather than a bare 5-tuple: it hashes identically
  and the DP body reads as `sheets.a3` instead of `state[1]`. Never use floats as keys (equal values
  can hash to two entries after different rounding — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality)); floats as
  *values*, accumulating probabilities, are fine, and problem 151 does exactly that.
- **The frontier size *is* the complexity.** A dict-based DP is fast only when key merging keeps the
  live state count bounded. If it doesn't, you have written an exponential search wearing a DP's
  clothes, and the tell is a `len(state)` that grows every step. Design the key to be the coarsest
  thing that still determines the future — that is the same instinct as
  [canonical form](/topics/technique/canonical-form).
- **`get` with a default, not `defaultdict`, on a read path.**
  [`defaultdict`](/topics/technique/collections-defaultdict-list) inserts on a mere lookup, which can
  silently grow the table — including during iteration. `d.get(k, 0)` reads without mutating, and
  `setdefault` is the right tool when you genuinely want the container created on first touch (the
  adjacency-list idiom in problems 143 and 816).
  [`Counter`](/topics/technique/collections-counter) earns its place when you want `most_common` or
  arithmetic on histograms; a bare dict is smaller and faster when you don't.
- **If the keys are dense small integers, use a list.** A dict entry costs a hash, a key pointer and
  a value pointer; a `list` indexed by $0..n$ is several times smaller and faster, and a
  [`bytearray`](/topics/technique/bytearray) more so again. The dict earns its keep when the key space
  is sparse, unbounded, or not an integer at all — which is why problem 95 sieves divisor sums into a
  *list* and only the chain-length memo is a dict. Getting this backwards is the most common way a
  sieve blows up in memory ([right tool per cost](/topics/takeaway/right-tool-per-cost)).
- **Insertion order is guaranteed; hash order is not.** Unlike a set, a dict iterates in insertion
  order, which is worth relying on for reproducible output. Do not rely on the *hash* order of
  anything, and sort explicitly when the answer depends on an ordering — problem 926 sorts its event
  keys before sweeping them.
- **A dict is often lazy scheduling in disguise.** Problems 37 and 69 generate primes with Eppstein's
  incremental sieve, where `composites` maps *the next composite each prime will strike* to that
  prime. It behaves like a priority queue but needs no heap, because a dict lookup at $n$ asks "is
  anything scheduled here?" in $O(1)$. When a structure is only ever queried at the current position,
  a dict beats an ordered one.
- **It is the most expensive thing to translate to C.** C has no associative container, so every one
  of these five jobs must be rebuilt — a hand-rolled hash table, a sort-and-scan, or an array indexed
  by a [mixed-radix](/topics/technique/mixed-radix) encoding of the tuple key. That last option is
  often the *better* algorithm and worth folding back into the Python; when it isn't, expect the
  C sibling to be several times the length for the same behaviour, and say so in the notes
  ([parity across languages](/topics/takeaway/parity-across-languages)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
