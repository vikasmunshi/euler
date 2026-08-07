<!-- tags: [hash-table] -->
<!-- status: final -->
# Hash table

A [hash table](https://en.wikipedia.org/wiki/Hash_table) turns a key into an array index by
computing a number from it. That is the entire trick, and it converts "have I seen this before?" and
"which group does this belong to?" from a scan of everything into a single probe. Python spells it
`dict` and `set` and puts it in the language; C has neither, so half the problems below carry a
hand-written table at the top of the file. What makes the technique recur is not the constant factor
— it is that these problems keep producing keys that are not small integers, and a hash is what lets
an array be indexed by a string, a tuple, or a pair of coordinates.

## The idea

A [hash function](/topics/technique/hash-function) maps a key to a bucket index; the table is an
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

## What it is actually used for

Four roles cover nearly every appearance below, and naming which one you are in tends to answer the
design questions that follow.

**Membership and de-duplication.** The set is the whole data structure: problem 125 collects
palindromes reachable as sums of consecutive squares and wants each once; problem 29 counts distinct
values of $a^b$ by inserting a canonical string per value and reading off the size; problem 49 tests
whether a digit permutation of a prime is itself prime by probing the set of $n$-digit primes.

**Grouping under a canonical key.** Map each item to a
[canonical form](/topics/technique/canonical-form) that is equal exactly when the items are related,
and let the table do the partitioning. Problem 62's key is the cube's digits sorted, which is
identical for every digit permutation; problem 98 keys words the same way to find anagrams; problem 49
groups primes into permutation families and then buckets the pairwise differences, so that a bucket
holding exactly three values *is* an arithmetic progression. The interesting work in all three is
choosing the key, not the table.

**Memoisation and sparse dynamic programming.** [Memoisation](/topics/technique/memoization) is a
hash table under a decorator — problem 14 caches Collatz chain lengths so that the shared tails of
half a million sequences are each computed once:

```python
@functools.lru_cache(maxsize=None)
def collatz_length(number: int) -> int:
```

The sparse-DP case is the more interesting one. When the state is a tuple and the *reachable* states
are a vanishing fraction of the possible ones, a dense array indexed by state is unaffordable and a
dict keyed by the tuple is the whole solution. Problem 208's robot walk carries a dict keyed on
(direction, the four arc counts) and rolls it forward one step at a time; problems 153 and 259 key on
values and frozensets that no array could be indexed by. The pattern to recognise: the state space is
astronomical, the state *count* is not.

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
  the key first.
- **Pre-size it, and use a power of two.** These tables are declared at their final size — `1 << 20`
  buckets for problem 60's pair cache, `1 << 22` for problem 29's set — because the entry count is roughly
  known and rehashing millions of entries mid-run is pure waste. Powers of two additionally allow the
  mask instead of a modulo. Python's dict does the same growth internally, and `dict.fromkeys` or a
  comprehension over a known iterable lets it size once.
- **Expected $O(1)$ is not worst-case $O(1)$.** Every key landing in one bucket degrades a chained
  table to a linked list and an open-addressed one to a linear scan. With adversarial input this is an
  attack; with mathematical input it is usually a hash that ignores the structure of the keys — hashing
  a coordinate pair as `x + y`, for instance, collides every point on an anti-diagonal. Mix both
  components multiplicatively, as problem 60's `cache_hash` does.
- **At small $n$, sorted array plus binary search wins.** Problem 49's C port replaces the Python
  set membership test with `qsort` and a binary search over the prime strings, and says so in a
  comment. $O(\log n)$ with no allocation, no hash function and no collision policy beats $O(1)$ with
  all three when $n$ is a few thousand and the set is built once and never mutated. The build-once,
  query-many, no-deletions case is exactly where a hash table is *not* the obvious answer in C.
- **Keys must be hashable, which means immutable.** Python enforces it: tuples and `frozenset`s are
  valid keys, lists and sets are not — which is why problem 259 canonicalises its reachable values
  into a `frozenset` before caching on them. The rule behind the error message is that mutating a key
  after insertion moves its bucket without moving the entry, and the entry is then invisible to every
  future lookup. In C nothing enforces it and the same bug is silent.
- **Reach for `collections` before writing the loop.** `defaultdict(list)` is the grouping idiom,
  `defaultdict(int)` and [`Counter`](/topics/technique/collections-counter) the tallying one, and
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
- ● [0768](/solutions/0768/) — Chandelier
- ● [0816](/solutions/0816/) — Shortest Distance Among Points

<!-- /problems -->
