<!-- tags: [open-addressing] -->
<!-- status: final -->
# Open addressing

Python gives every solution a `dict` and a `set` at no cost. C gives you nothing like them. Each
time a Python solution reaches for a hash table, its C translation has to build one. In this
repository that table is always the same thing: a flat array of slots, a mixing hash, and
[open addressing](https://en.wikipedia.org/wiki/Open_addressing) with linear probing. That pattern
covers memoising a recursion (77, 153, 755, 943), deduplicating values (125, 155, 259), merging
DP states that collide (145, 152, 208, 269), and the composite → prime map of an incremental sieve
(10, 37). The table is never the interesting part of those problems. It is still the place the C
port most often goes slow or goes wrong. This page covers the few decisions that matter: the
probing scheme, the hash, the size, the load factor, and what an "empty" slot means.

## The idea

A table with *open addressing* stores every entry in the slot array itself. There are no linked
lists of colliding entries (that alternative is
[separate chaining](https://en.wikipedia.org/wiki/Hash_table#Separate_chaining)). A key hashes to a
home slot. If another key already holds that slot, you walk a fixed *probe sequence* until you
reach the key or an empty slot. A lookup and an insert follow the same walk, so an empty slot
proves the key is absent. That one invariant explains every rule below.

Problem 37's composite map is the whole thing in about ten lines:

```c
#define HASH_SIZE (1 << 20)  /* must be power of 2 */
#define HASH_MASK (HASH_SIZE - 1)

static void hash_insert(int key, int val) {
    unsigned int h = (unsigned int)key & HASH_MASK;
    while (htable[h].key != 0 && htable[h].key != key)
        h = (h + 1) & HASH_MASK;
    htable[h].key = key;
    htable[h].val = val;
}
```

A lookup is the same loop: it returns the value when it reaches `key`, and reports a miss when
it reaches `0`.

### Probing: linear, on purpose

The textbook schemes are [linear probing](https://en.wikipedia.org/wiki/Linear_probing) (step 1),
[quadratic probing](https://en.wikipedia.org/wiki/Quadratic_probing) (steps 1, 2, 3, …), and
[double hashing](https://en.wikipedia.org/wiki/Double_hashing) (a step that comes from a second
hash). All thirteen solutions use linear probing. Its known weakness is *primary clustering*: runs
of occupied slots merge, and every key that lands inside a run has to walk to its end. Its
strength is that the walk reads adjacent memory, often from the same cache line. On a modern CPU
that usually beats the theoretical advantage of the other schemes. The clustering cost has two
fixes, and both are cheap: a hash that scatters keys (next section) and a load factor kept well
below 1 (the one after).

### The hash: mix, then mask

A power-of-two capacity turns `% cap` into `& (cap - 1)`. The mask is one AND instead of a
division, and doubling the table keeps it a power of two. The cost is that the mask keeps only the
**low bits** of the hash. A hash whose low bits are weak gives a table whose clusters are weak.
Euler keys are exactly that kind of key: multiples of a prime, a budget times 128 plus an index,
pairs packed into a word. So every solution that masks first runs the key through a mixer:

| Mixer | Shape | Used in |
|---|---|---|
| [Fibonacci hashing](https://en.wikipedia.org/wiki/Hash_function#Fibonacci_hashing) | `(k * 0x9E3779B97F4A7C15) >> (64 - BITS)` | 755 |
| [SplitMix64](https://prng.di.unimi.it/splitmix64.c) finaliser | xor-shift, multiply by `0xBF58476D1CE4E5B9`, … | 155, 208 |
| [MurmurHash3](https://en.wikipedia.org/wiki/MurmurHash) `fmix64` | xor-shift, multiply by `0xff51afd7ed558ccd`, … | 259 |
| 32-bit xor-shift-multiply | `h ^= h >> 16; h *= 0x45d9f3b; h ^= h >> 16` | 77, 145 |

All of them follow one rule. A multiplication pushes information **upward**: the low bits of
`k * C` depend only on the low bits of `k`. So you either take the *high* bits (Fibonacci hashing
shifts right instead of masking) or xor-shift the high bits back down before you mask. The
mistake to avoid is `key * C & mask`, which looks mixed but keeps exactly the low-bit pattern the
key arrived with. Problem 37 gets away with the identity hash only because its keys are odd
composites spread over a large table. Change the key distribution and that table degrades without
any visible sign.

### Load factor and sizing

The *load factor* α is entries ÷ slots. For linear probing with a good hash,
[Knuth's analysis](https://en.wikipedia.org/wiki/Linear_probing#Analysis) gives about
½(1 + 1/(1−α)) probes for a hit and ½(1 + 1/(1−α)²) for a miss or an insert:

| α | hit | miss / insert |
|---|---|---|
| 0.50 | 1.5 | 2.5 |
| 0.70 | 2.2 | 6.1 |
| 0.75 | 2.5 | 8.5 |
| 0.90 | 5.5 | 50.5 |

The miss column climbs much faster than the hit column, and memo tables and dedup sets mostly
*miss*: they look a key up just before inserting it. That is why the growing tables here double at
α = ½ (10, 269, 943) or at about 0.7 (152, 155, 259 at ¾). The test stays in integers, as in
`if (count * 10 >= cap * 7) grow();`. Growing means allocating the doubled array and re-inserting
every live entry, because each entry's home slot depends on `cap`.

The alternative is a **fixed** table sized once: `1 << 18` for 77's memo, `1 << 22` for 208's
states. That is simpler and faster, and it is correct only while the entry count stays below the
size. Derive the size from the input bound (the next power of two ≥ 2 × the most entries the
input can produce) and write the bound in a comment. "Should be plenty" is a guess that a larger
input will break. A fixed table that fills up does something worse than slow down: an insert loop
with no exit spins forever. If you cannot prove the bound, either grow the table or cap the probe
count with a fallback, as 153's memo does by computing the value directly once the table is full.

### What "empty" means

A slot needs a way to say "nothing here". There are three idioms:

- **A sentinel key** that cannot occur: `0` for 37's composites, `-1` for 77's `(number, slots)`
  pairs. This is the most compact choice, and it is a trap if the sentinel ever becomes a legal key.
- **A `used` flag**, either in the entry (10, 153) or as a parallel byte array (125, 755). It costs
  memory and makes no assumption about keys.
- **A generation stamp** (943). Each slot records the generation that wrote it, and a slot whose
  stamp is not the current generation counts as empty. Clearing the whole table is then
  `gen++`, which matters when `solve()` rebuilds its memo for each of many sub-problems. It also
  keeps the house rule that caches are built fresh inside `solve()` without paying to `memset` a
  large table every time.

### Deletion, and why you rarely need it

Removing an entry by blanking its slot breaks the invariant: the blank cuts the probe chain of
every key stored past it. There are two standard fixes. A *tombstone* marks the slot as "deleted,
keep walking". *Backward-shift deletion* removes the entry and re-seats the rest of its cluster.
The incremental sieves (10, 37) delete constantly, because each composite leaves the map once it
is reached, and both use the re-seat approach: blank the slot, then pull out and re-insert each
following entry until the first empty slot. Every other table here is **insert-only**. Memos and
dedup sets never forget anything. That is the main reason a hand-rolled table is short enough to
write inline: without deletion, the hard part of open addressing disappears.

## How to reason about it

- **First ask whether you need a hash at all.** If the keys are dense integers in a range known in
  advance, a plain array indexed by the key is a perfect hash with no collisions. If you only need
  the distinct values at the end, collecting them and running `qsort` plus a unique pass is often
  simpler than a set. Reach for open addressing when keys are sparse, composite, or arrive in an
  order you cannot predict. Those are the cases where the Python version used a `dict`.
- **Pack composite keys into one word when you can.** 755 encodes `(i, budget)` as
  `budget * 128 + i` (injective because `i < 128`), and 943 packs several fields into a `u64`. One
  integer compare per probe is cheaper than comparing a struct field by field. When the key cannot
  fit, as with 152's multi-limb integers or 269's variable-length coefficient vectors, store it out
  of line, compare it in full, and still hash it to one word.
- **Keep the slots small.** For 155 the slot array holds only `entry index + 1` (`0` = empty),
  and the `(num, den)` pairs live in a dense, insertion-ordered list. That is the layout of
  [CPython's own compact dict](https://github.com/python/cpython/blob/main/Objects/dictobject.c).
  Probing touches 4-byte slots, and iterating the set walks a packed array instead of skipping
  holes.
- **Accumulate on collision for DP.** A state map (145, 208, 269) does not reject a duplicate
  key. It adds the new count onto the existing value, which is the C form of
  `d[k] = d.get(k, 0) + v`.
- **Re-probe after recursing.** A memoised recursion that finds a free slot, recurses, and then
  writes to that slot is wrong. The recursion may have filled the slot, or grown the table and
  freed the array the slot pointed into. 755 probes again for the store after the recursive calls
  return. Treat any slot pointer as invalid across a call that can insert.
- **Mirror Python's semantics, not just its speed.** A `dict` overwrites on assignment and
  `set.add` ignores duplicates. Decide explicitly which one your insert does (77's `memo_set`
  overwrites, 125's set skips), so that the C port and the Python version agree for each key.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0943](/solutions/0943/) — Self Describing Sequences

<!-- /problems -->
