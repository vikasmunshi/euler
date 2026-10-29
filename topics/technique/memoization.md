<!-- tags: [memoization] -->
<!-- status: final 2026-10-29T07:05Z -->
# Memoization

[Memoization](https://en.wikipedia.org/wiki/Memoization) is the substitution of a table lookup for a
computation: remember what a function returned, keyed on what it was asked, and hand back the stored
value the next time the same question arrives. It is the cheapest large speed-up in this repository —
usually one decorator, sometimes one array — and it recurs across the problems below because the
short, obviously-correct statement of a counting or chain-following problem is almost always a
recurrence, and a recurrence evaluated literally asks the same question an enormous number of times.

## The idea

Two preconditions, both easy to state and easy to violate. The function must be **pure** — same
arguments, same result, no observable side effect — and its arguments must serve as a key: hashable
in Python, an integer index or a hash in C. Given those, the speed-up is a single ratio:

> **calls ÷ distinct arguments.**

That number is worth estimating before writing anything, because it is also the diagnosis when the
cache turns out to do nothing. What makes it large is always the same structural fact: **the map
from inputs to states is many-to-one.** Memoization does not make a computation cheaper; it makes
you pay for it once per *state* instead of once per *visit*, and the whole art is arranging for
there to be far fewer states than visits.

Problem 92 is that sentence with the numbers filled in. It classifies every number below $10^7$ by
whether its square-digit-sum chain ends at 89, but a chain depends only on the digit-square-sum, and
a 7-digit number has at most $81 \times 7 = 567$ of those. So the classification is computed once per
*sum* into a flat `is89` table and read $10^7$ times — 567 chain walks instead of ten million. The
input space is huge; the state space is a few hundred. Everything below is a variation on finding
that collapse.

## Where the repetition comes from

**Overlapping subproblems in a recurrence.** The dominant source, and the reason this tag and
[dynamic programming](/topics/technique/dynamic-programming) overlap so heavily. `F(n)` calls
`F(n-1)` and `F(n-k-1)`; the call tree is exponential, the set of distinct arguments is $O(n)$.
Problems 76, 77, 115, 161, 259, 301, 755, 887 and 1000 are all this shape, differing only in what
the state is — a remaining amount and a largest allowed part, a cell and a frontier mask, a position
and a digit-DP carry, a tree height and a slack.

**A functional graph.** When every value has exactly one successor, chains merge and then share a
tail. Problems 14 ([Collatz](/topics/domain/collatz-conjecture)), 74 (digit factorials) and 92
(square digit sums) all ask a question about $10^6$–$10^7$ chains that collectively visit only a
modest set of distinct nodes. Cache per node and each start costs amortised $O(1)$; see
[functional graph](/topics/domain/functional-graph).

**Repeated arguments in a sweep.** Sometimes the repetition is a theorem rather than a recursion.
Problem 153 memoises the divisor-sum summatory $D(x)$ in a plain dict because the nested
[quotient blocking](/topics/technique/quotient-blocking) only ever evaluates it at values of the
form $\lfloor N/k \rfloor$, of which there are $O(\sqrt N)$ however large $N$ is. Problem 641 leans
on the same fact for the [Mertens function](https://en.wikipedia.org/wiki/Mertens_function): the
recursion $M(x) = 1 - \sum_{k \ge 2} M(\lfloor x/k \rfloor)$ only ever recurses on quotients of $x$,
and a quotient of a quotient is again a quotient, so evaluating $M$ near $10^9$ fills only a few
hundred memo entries before it bottoms out. Problem 549 keeps a
per-prime list of $s(p^e)$, extended on demand as larger exponents appear, because the same prime
powers recur all the way up a linear sieve. Neither cache is a dynamic program; both convert a
quadratic-looking sweep into a linear one.

**Plain deduplication.** Least glamorous, often enough. Problem 60 memoises the edge predicate
"both concatenations of $a$ and $b$ are prime" across a clique search that revisits the same pairs
constantly; problem 21 memoises the $O(\sqrt n)$ proper-divisor sum because amicability asks for
$d(d(x))$ and so queries each value roughly twice. Here the cache is not the algorithm, only a way
of not repeating yourself.

**A self-similar tree.** Problem 943 is the extreme case of the opening sentence. It asks for prefix
sums of a two-symbol [Kolakoski](https://en.wikipedia.org/wiki/Kolakoski_sequence)-style sequence
whose run lengths are the sequence itself. Read backwards, each element is the parent of the run it
describes, so the first $2.2 \times 10^{13}$ terms are the leaves of a derivation tree only a few
dozen levels deep. The tree is far too big to walk, but most of its subtrees have the same shape,
so the memo is keyed on the subtree. The first key that comes to mind, (value, height), is not
enough. A node's children take their symbol from the parity of the node's *position*, and that
parity depends on everything to its left. The key that actually fixes a subtree adds a bitmask of
those parities, one bit per level. With it, the distinct keys peak near
$N^{\log 2 / \log(a+b)}$: a few million for the densest pair and a few dozen once $a+b$ is in the
hundreds. That is roughly $10^{13}$ leaves served from $10^6$ table entries, and the answer becomes
one root-to-leaf descent that adds up the cached totals of every whole subtree to the left.

## Four ways to write the table

**A decorator.** `@functools.lru_cache(maxsize=None)` (or `functools.cache`) in Python — the default,
and the subject of its own page: [functools.lru_cache](/topics/technique/functools-lru-cache), which
covers key construction, `cache_info()`, and the hazards specific to the decorator.

**An explicit dict.** What problem 153 does for $D(x)$: a `dict` in the enclosing scope, probed with
`.get` and filled on a miss. Worth the four lines when the cache is not merely an accelerator but
part of the algorithm's story — you can size it, inspect it, seed it, or clear it at a boundary the
decorator does not know about. Seeding can mean a whole second tier. Problem 641's `mertens_at` reads
any argument up to the sieve bound $L$ straight from a prefix-sum array of the Möbius sieve, and
uses the dict only above $L$. The array is the recursion's base case, and choosing $L$ above
$x^{2/3}$ is what keeps the dict tier down to a few hundred keys.

**An array — direct addressing.** When the key is a small integer, skip hashing entirely and index.
Problem 74's C sibling caches chain lengths in a flat `calloc`'d array of 3,000,000 `int`s (every
reachable digit-factorial value stays below $7 \times 9! = 2540160$), using `0` as the "absent"
marker; problem 115's C sibling keeps a `cache[]` alongside a parallel `cache_valid[]` flag array,
which is what you need when `0` is a legitimate stored value. Problem 887's C port is the in-between
case: a fixed $64 \times 64$ table where `0` can safely mean "empty", because every capacity it
stores is at least 1. This is
[direct addressing](/topics/technique/direct-addressing), and it is the reason the C solutions here
are typically an order of magnitude faster than the Python ones rather than merely twice as fast —
no hashing, no boxing, perfect
[locality](/topics/technique/locality-of-reference). Where the keys are large or sparse, C has to
build what Python handed you for free: problem 153's C solution hand-writes a 65,536-slot
open-addressing [hash table](/topics/technique/hash-table) purely to mirror one Python dict.

**Back-propagation along a walk.** The form worth knowing because it is not recursion at all.
Problem 74 walks forward from each start until it meets a node it already knows (or closes a cycle),
then fills in *every* node of the walk on the way out:

```python
seen: list[int] = []
current: int = start
while current not in seen and current not in chain_length_cache:
    seen.append(current)
    current = sum_of_digit_factorials(current)
length = len(seen) + chain_length_cache.get(current, 0)
for i, num in enumerate(seen):
    chain_length_cache[num] = length - i
```

One walk populates dozens of entries; there is no recursion, so no stack limit and no frame
overhead, and the loop is trivially portable to C. Whenever the recurrence is a *chain* rather than a
tree, this beats a memoised recursion on every axis.

## The four ways it goes wrong

**Not actually applying it.** Problem 115's Python `F(n)` carries the word "memoised" in its
docstring and no cache in its body, while the C version at the same index has the `cache` /
`cache_valid` pair. The gap is not subtle: `0.844 s` against `0.0000119 s` — about seventy thousand
times, where the language accounts for maybe fifty. Without the table the recursion does not
*count* the configurations, it *enumerates* them, so its cost is the number being computed
(over $10^6$) rather than the $O(n^2)$ the recurrence promises. Two lessons: a missing cache can
dwarf the entire language gap ([a better algorithm beats a faster
language](/topics/takeaway/algorithm-beats-language)), and a Python/C pair that disagrees this
loudly is a parity bug worth chasing
([parity across languages](/topics/takeaway/parity-across-languages)).

**Caching the wrong object.** Problem 74 solves the same problem three ways with the same
memoization strategy: index 0 stores one integer per node — the chain length — while indices 1 and 2
store the whole tail *list*. Identical asymptotics, and `0.914 s` against `2.53 s` and `2.57 s`,
with memory in a worse ratio still. Cache the number you need, not the objects it was derived from;
if the cached value is bigger than the computation that made it, the table has become the cost.
The exception proves the rule. Problem 943 *does* cache lists: for each run of same-valued
siblings it stores prefix sums of their counts and totals, plus the point where their mask sequence
starts to cycle. It does this because the questions that follow are "the first $k$ of them" for many
different $k$. A run up to 223 long would otherwise be re-walked on every query; with the stored
prefix and its period, each query is answered in $O(1)$ by counting whole periods. Storing a
structure is right when it answers a whole family of later queries. It is wrong when it only holds
one value, more expensively than a number would.

**Caching what is cheaper to recompute.** A cache hit is a hash, a probe and a function-call frame.
Problem 78 memoises `pentagonal(x)`, which is `x * (3 * x - 1) // 2` — two arithmetic operations,
comfortably cheaper than looking them up. Harmless here, but the habit is a real pessimisation in a
hot loop, and it is the mirror image of the previous mistake: measure the body against the lookup
before wrapping it.

**Outliving its inputs.** A cache is only valid for the parameters it was computed under, and this
repository has a second, sharper reason to care: `--runs=N` times repeated calls to `solve()`, so a
table that survives between runs is *warm* from the second run onward and the reported average
measures dict lookups instead of the algorithm. Problem 103 keeps its optimum-set cache in a
module-level `_CACHE` and never clears it; problem 17 keeps its speller at module level and calls
`cache_clear()` as the first statement of `solve()`; problems 14, 21, 161, 259, 301, 755 and 1000
sidestep the question entirely by defining the memoised function as a
[closure](/topics/technique/closure-computer-programming) inside `solve()`, which is both honest and
correct — a closure's results depend on what it captured, so a cache that outlives the capture can
answer a later call with a value computed under a different bound. Build the cache where the input
lives. Problem 943 shows the same rule at a finer grain. Its key leaves out the pair $(a, b)$, so the
memo is valid for one pair only, and the Python solution rebuilds it inside the per-pair function,
roughly fifty thousand times per call. The C port does not free and reallocate fifty thousand
tables. It stamps every slot with a generation counter and bumps the counter between pairs, so a
slot from an earlier pair reads as empty. That invalidates the whole cache in $O(1)$ with no clearing
pass. Problem 887 is the opposite case, and the same rule explains it. It sums over every bound $d$
with a single memo, created in `solve()` and shared across the whole loop over $d$. That is sound
because $d$ never hides in the function: it enters only as the starting slack, which is part of
the key. A table can outlive a loop iteration exactly when everything that iteration changes is
in the key.

## How to reason about it

- **Estimate the hit ratio first.** Calls divided by distinct arguments. If you cannot see why that
  ratio is large, memoization is not your optimisation.
- **Choosing the arguments is choosing the state.** Every parameter joins the key: a redundant one
  multiplies the table, a missing one is a correctness bug, and two spellings of the same state
  ([canonical form](/topics/technique/canonical-form) — an unsorted tuple, `1` versus `1.0`) split
  entries that should have merged. To find the key, ask what *fixes* the result, not what
  describes it. Problem 943's subtrees look like they depend on (value, height), but they actually
  depend on a parity mask as well.
- **Let the base cases bound the key space.** An argument that can grow without limit does not have
  to make the table grow too. Problem 887's tree capacity $F(h, c)$ recurses with a right-hand slack
  of $c - 1 + F(h-1, c-1)$, which grows exponentially. But once $c \ge h$ the constraint stops
  binding and $F = 2^h$, so that base case returns before touching the table. Only states with
  $0 < c < h$ are ever stored, $O(H^2)$ of them for $H = O(\log N)$, and the whole computation
  uses a few hundred entries. Look for the point where an argument saturates and stop there, so
  the saturated values never become keys.
- **Prefer an array when the keys are small integers.** A `dict` is the general answer; an indexed
  array is the fast one, and in C it is usually the only one you get without writing a hash table
  yourself.
- **Never mutate what the cache handed you** — the stored object is shared with every future hit.
  Returning an immutable value removes the hazard.
- **Top-down memoization is still recursion**, with Python's ~1000-frame limit and a frame's cost per
  miss. If every state will be visited anyway, a bottom-up table (problem 78) or a walk with
  back-propagation (problem 74) is faster and cannot overflow; top-down wins when the *reachable*
  state space is much smaller than the nominal one.
- **The table is your memory profile.** Entries are the state space, and the state space is the
  complexity. A healthy hit rate on a still-slow program means the recurrence is wrong, not the
  cache — problem 76's naive partition recursion and Euler's pentagonal recurrence are both fully
  memoised and a thousandfold apart ([reduce before coding](/topics/takeaway/reduce-before-coding)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0161](/solutions/0161/) — Triominoes
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0301](/solutions/0301/) — Nim
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
