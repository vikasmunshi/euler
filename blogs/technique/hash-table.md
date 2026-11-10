<!-- tags: [hash-table] -->
<!-- status: final 2026-11-09T12:39Z -->
# Hash table

A [hash table](https://en.wikipedia.org/wiki/Hash_table) turns a key into an array index by
computing a number from it. That is the entire trick, and it converts "have I seen this before?" and
"which group does this belong to?" from a scan of everything into a single probe. Python spells it
`dict` and `set` and puts it in the language; C has neither, so half the problems below carry a
hand-written table at the top of the file. What makes the technique recur is not the constant factor
— it is that these problems keep producing keys that are not small integers, and a hash is what lets
an array be indexed by a string, a tuple, or a pair of coordinates.

## The idea

A [hash function](/blogs/technique/hash-function) maps a key to a bucket index; the table is an
array of buckets; a lookup hashes, jumps, and compares. Two keys will eventually collide, and the
policy for handling that is the one structural decision. Both standard answers appear in this tree.

**Separate chaining** keeps a linked list per bucket. Problem 29 uses it for a set of big-integer
decimal strings, problem 62 for a map from a sorted-digit key to the cubes that share it:

```c
static unsigned int hash_str(const char *s) {
    unsigned int h = 5381;
    while (*s) {
        h = ((h << 5) + h) + (unsigned char)(*s++);
    }
    return h & (HASH_SIZE - 1);
}
```

Two details in three lines. The mixing is djb2 — a multiply and an add per character, chosen because
it is short and adequate, not because it is strong. And the fold into range is a bitwise `&` rather
than a `%`, which works only because `HASH_SIZE` is a power of two. That is why every table here is
declared as a shift — `1 << 16`, `1 << 20`, `1 << 22`: a mask is a single instruction where a modulo
is a division, and on the hot path of a few hundred million lookups the difference is measurable.

**Open addressing** stores entries directly in the array and, on collision, walks to the next free
slot. Problem 10's third solution needs it because it does something chaining makes easy and open
addressing makes delicate — it *deletes*:

```c
e->used = 0;
ht->count--;
/* Rehash subsequent entries in the cluster */
size_t j = (idx + 1) % ht->cap;
while (ht->entries[j].used) {
    HEntry tmp = ht->entries[j];
    ht->entries[j].used = 0;
    ht->count--;
    htable_set(ht, tmp.key, tmp.value);
    j = (j + 1) % ht->cap;
}
```

Clearing a slot in an open-addressed table breaks every probe sequence that ran *through* it: a later
key that had to walk past this slot to find its home is now unreachable, because the search stops at
the first empty slot. The fix is either a tombstone marker or, as here, reinserting the rest of the
cluster. This is the single most common way a hand-rolled hash table is subtly wrong, and it only
shows up once deletions and collisions coincide — which is to say, on large inputs, in production, and
not in the small test case.

The same file shows the other invariant: `if (ht->count * 2 >= ht->cap) htable_grow(ht);`. Open
addressing degrades sharply as the table fills, because clusters merge and probe sequences lengthen;
keeping the load factor at or below one half and doubling on the way past it is what preserves the
$O(1)$ expectation.

Deletion has a second way out: never delete. Problem 983 scans radii one after another and runs a
backtracking search at each, and its tables — one of them $2^{22}$ slots — must start empty for every
radius and every search node. Rather than `memset` four million slots thousands of times, each slot
carries a stamp, and a slot counts as occupied only if its stamp equals the table's current
generation:

```c
static void map_clear(map_t *m) { m->gen++; }
/* probe: while (m->stamp[h] == m->gen) { ... } */
```

Clearing becomes one increment, stale entries become empty slots in place, and the
probe-chain-through-a-deleted-slot bug cannot arise because nothing is ever removed one at a time.
The same file also picks its bucket differently from djb2-and-mask: it multiplies the 64-bit key by
$2^{64}/\varphi$ (`0x9E3779B97F4A7C15`) and keeps the **top** bits —
[Fibonacci hashing](https://en.wikipedia.org/wiki/Hash_function#Fibonacci_hashing). A mask keeps
the low bits, which is fine after djb2 has stirred them; for a raw integer key whose low bits are
patterned, the multiply carries every input bit into the high end, and the shift reads them out.

## What it is actually used for

Five roles cover nearly every appearance below, and naming which one you are in tends to answer the
design questions that follow.

**Membership and de-duplication.** The set is the whole data structure: problem 125 collects
palindromes reachable as sums of consecutive squares and wants each once; problem 29 counts distinct
values of $a^b$ by inserting a canonical string per value and reading off the size; problem 49 tests
whether a digit permutation of a prime is itself prime by probing the set of $n$-digit primes.

**Grouping under a canonical key.** Map each item to a
[canonical form](/blogs/technique/canonical-form) that is equal exactly when the items are related,
and let the table do the partitioning. Problem 62's key is the cube's digits sorted, which is
identical for every digit permutation; problem 98 keys words the same way to find anagrams; problem 49
groups primes into permutation families and then buckets the pairwise differences, so that a bucket
holding exactly three values *is* an arithmetic progression. The interesting work in all three is
choosing the key, not the table.

**Joining on a shared key.** Grouping has a second payoff when the question is about *pairs*: two
items can only be related if they land in the same bucket, so the table cuts the candidate pairs
before any test runs. Problem 309 wants pairs of Pythagorean triples that share a leg. It enumerates
every triple once, files each one under its legs with `partners.setdefault(leg, []).append(other)`,
and then compares pairs only inside a bucket. The cost drops from $N^2$ over all triples to
$\sum_w d_w^2$ over the bucket sizes, and since most buckets hold a handful of triples that sum is
small. Problem 928 joins two *different* collections the same way, as a
[meet in the middle](/blogs/technique/meet-in-the-middle-attack). It counts cribbage hands. It splits
the ranks into Ace–9 and 10–K, enumerates each half on its own, and collapses each half into a
`Counter` keyed by what the other half needs to know: the low half's trailing run and its count of
five-sums, the high half's leading run and its count of ten-cards. The join then makes one
`balances.get(need, 0)` probe per pair of keys. Neither half ever sees the other's individual hands;
the equality the hand must satisfy is solved by a lookup. It is the same move as a database hash
join, and the design work is the same too: find the smallest interface the two halves have to share,
and use it as the key.

**Memoisation and sparse dynamic programming.** [Memoisation](/blogs/technique/memoization) is a
hash table under a decorator — problem 14 caches Collatz chain lengths so that the shared tails of
half a million sequences are each computed once:

```python
@functools.lru_cache(maxsize=None)
def collatz_length(number: int) -> int:
```

Collatz's key is the whole argument, so the cache hits only when a number repeats exactly. Problem
551 shows what to do when that never happens. Its walk adds a number's digit sum to the number, about
$10^{15}$ times, and no value occurs twice. The memo is keyed instead on
`(k, c, low)`: the number of low digits, the digit sum of the high part, and the low part itself. A
run of steps that carries the low $k$ digits past $10^k$ depends on nothing else, because the high
digits only ever enter through their sum. Dropping $H$ from the key is what makes the same state
come up again and again. The same dependency rule decides what may be stored: a run cut short by
the step budget depends on that budget, so only completed runs are cached, and a cached run is
reused only when it fits inside the caller's remaining limit. A memo key has to contain exactly what
the answer depends on. If you leave out something it depends on, you get wrong answers. If you leave
in something it does not depend on, you get no hits.

The sparse-DP case is the more interesting one. When the state is a tuple and the *reachable* states
are a vanishing fraction of the possible ones, a dense array indexed by state is unaffordable and a
dict keyed by the tuple is the whole solution. Problem 208's robot walk carries a dict keyed on
(direction, the four arc counts) and rolls it forward one step at a time; problems 153 and 259 key on
values and frozensets that no array could be indexed by. Problem 987 follows the same plan, keyed on
the last four straights that still overlap the current rank. Problem 990 shows what to do when the DP
has no step counter to roll forward on. It counts balanced addition strings column by column, and a
column consumes a variable number of characters. So it keeps a *list* of dicts indexed by remaining
character budget, keys each dict on `(active left terms, active right terms, carry)`, and drains the
buckets from the largest budget down. The budget strictly falls, so a bucket is never written after
it has been read. Any dimension that only ever decreases can move out of the key and into the list
index, and that gives you the processing order for nothing. The pattern to recognise: the state space
is astronomical, the state *count* is not.

**A map with no dense index available.** Problem 10's incremental sieve keeps composites mapped to
the prime that will next strike them, and the keys it needs are scattered across the whole range with
no bound known in advance — precisely the case where an array cannot be allocated. Problem 816 hashes
points into grid cells by dividing their coordinates, so that a closest-pair search only compares
points in neighbouring cells; the key is a coordinate pair, the table is the spatial index.

## How to reason about it

- **A hash table is what you use when an array will not do.** Not the other way round. Problem 10
  measures the gap exactly: on the same input, the C dict-based incremental sieve takes `0.097 s`
  where the C array sieve takes `0.0037 s` — twenty-six times slower for the same primes. A hash
  lookup is a random access to a large block plus a comparison; an array sieve is a sequential stride
  the prefetcher handles for free. If your key is an integer in a known, reasonably dense range, index
  an array and do not think about it again.
- **The key is the design; the table is plumbing.** A canonical key that is cheap to compute and
  compares equal exactly when you want it to is what makes the technique work. Sorting a number's
  digits into a string, as problem 62 does, is $O(d \log d)$ per key; a ten-element digit-frequency
  count would be $O(d)$ and hashes just as well. When a hash-based grouping is the bottleneck, look at
  the key first. A key can also be chosen for its *algebra*: problem 983 packs a lattice vector
  $(x, y)$ into the integer $x \cdot 2^{21} + y$, which is injective over its coordinate range and
  linear — the key of $u + v$ is the sum of the keys. Every relation it tests ("is this signed sum
  equal to $2u$ for some $u$?", "is it some $u + v$?") becomes plain integer addition followed by one
  probe, with no tuple ever built.
- **A table can hand out identities, not just answers.** Problem 674 has to solve many equations
  between deeply nested `I(…, …)` terms, and it parses every expression into one
  [hash-consed](/blogs/technique/hash-consing) DAG. The table maps a variable name, or an
  `(left id, right id)` pair, to a node id. A subterm that has been seen before gets its existing
  id back instead of a new node. Because a node's children are interned before the node itself, two
  subterms are structurally equal exactly when their ids are equal. So the
  [unification](/blogs/technique/unification-computer-science) that follows only ever compares
  integers, never trees, and work done on a shared subterm is done once. The table builds the
  canonical form instead of just storing it. The same file has a second lesson in its union-find:
  `parent` is a plain `dict`, made fresh for each pair of equations, and it holds only the nodes that
  pair actually merges. That is the Python counterpart of problem 983's generation stamp. When most
  of the structure goes unused on any one query, an empty sparse table is a cheaper reset than
  clearing a dense array.
- **Pre-size it, and use a power of two.** These tables are declared at their final size — `1 << 20`
  buckets for problem 60's pair cache, `1 << 22` for problem 29's set — because the entry count is roughly
  known and rehashing millions of entries mid-run is pure waste. Powers of two additionally allow the
  mask instead of a modulo. Python's dict does the same growth internally, and `dict.fromkeys` or a
  comprehension over a known iterable lets it size once.
- **Expected $O(1)$ is not worst-case $O(1)$.** Every key landing in one bucket degrades a chained
  table to a linked list and an open-addressed one to a linear scan. With adversarial input this is an
  attack; with mathematical input it is usually a hash that ignores the structure of the keys — hashing
  a coordinate pair as `x + y`, for instance, collides every point on an anti-diagonal. Mix both
  components multiplicatively, as problem 60's `cache_hash` does, or pack them injectively into one
  integer and run that through a multiplicative hash, as problem 983 does.
- **At small $n$, sorted array plus binary search wins.** Problem 49's C port replaces the Python
  set membership test with `qsort` and a binary search over the prime strings, and says so in a
  comment. $O(\log n)$ with no allocation, no hash function and no collision policy beats $O(1)$ with
  all three when $n$ is a few thousand and the set is built once and never mutated. The build-once,
  query-many, no-deletions case is exactly where a hash table is *not* the obvious answer in C.
  Vectorised Python reaches the same conclusion for a different reason: problem 983's NumPy version
  keeps its key sets as sorted arrays and tests a whole batch of thousands of sums at once with
  `np.isin` and `np.searchsorted`, because a `set` can only be probed one Python-level call at a time.
  Its C port, free of that interpreter cost, goes back to open-addressed tables — the same key sets,
  the right structure chosen per language.
- **Keys must be hashable, which means immutable.** Python enforces it: tuples and `frozenset`s are
  valid keys, lists and sets are not — which is why problem 259 canonicalises its reachable values
  into a `frozenset` before caching on them. The rule behind the error message is that mutating a key
  after insertion moves its bucket without moving the entry, and the entry is then invisible to every
  future lookup. In C nothing enforces it and the same bug is silent.
- **Reach for `collections` before writing the loop.** `defaultdict(list)` is the grouping idiom,
  `defaultdict(int)` and [`Counter`](/blogs/technique/collections-counter) the tallying one, and
  `dict.get(key, default)` the one-off. They are the same hash table with the bookkeeping removed, and
  the C port is where you will write that bookkeeping back out by hand.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0083](/solutions/0083/) — Path Sum: Four Ways
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0309](/solutions/0309/) — Integer Ladders
- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ● [0768](/solutions/0768/) — Chandelier
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0928](/solutions/0928/) — Cribbage
- ● [0949](/solutions/0949/) — Left vs Right II
- ● [0983](/solutions/0983/) — Consonant Circle Crossing
- ● [0987](/solutions/0987/) — Straight Eight
- ● [0990](/solutions/0990/) — Addition Equations

<!-- /problems -->
