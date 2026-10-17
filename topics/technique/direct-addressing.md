<!-- tags: [direct-addressing] -->
<!-- status: final 2026-10-17T06:39Z -->
# Direct addressing

Direct addressing is the plainest map there is: when every key is a small non-negative integer,
use the key itself as the array index. No hash, no probing, no collisions — `table[key]` is the
whole lookup. It keeps coming back in these problems because Project Euler's keys so often *are*
bounded integers: chain values that never pass `7·9!`, sums below `5·10⁷`, minimal products below
`2k`, digit-sum tuples whose components live in `[0, 2M]`. Once you can name the bound, a flat
array beats any general-purpose map by a constant factor that is usually large.

## The idea

A [direct-address table](https://en.wikipedia.org/wiki/Direct_addressing) over a universe
`U = {0, …, m−1}` is an array of `m` slots; key `k` lives in slot `k`. Insert, lookup and delete
are each a single memory access, worst case, not just on average. The price is space
proportional to the **universe**, not to the number of keys actually stored — so the technique is
right exactly when `m` is small enough to allocate and the keys are dense enough in it that the
empty slots are not mostly waste. When they are not, you want a
[hash table](/topics/technique/hash-table), which is direct addressing after a compression step.

The table takes four shapes across the problems below:

| Shape | Slot holds | Problems |
| --- | --- | --- |
| **Membership flag** | `0/1` — "seen" or "used" | 68, 87, 88 |
| **Memo / value** | a computed result per key | 74, 95 |
| **Counter** | a tally per key | 135, 166 |
| **Bucket index** | a list per cell of a coarse grid | 212 |

The first is a [bit array](/topics/technique/bit-array) in spirit (the solutions spend a byte per
slot for simpler indexing); the second is [memoization](/topics/technique/memoization) with an
array for its cache; the third is the counting half of
[counting sort](/topics/technique/counting-sort); the fourth is a
[grid spatial index](/topics/technique/grid-spatial-index).

## Finding the bound

Everything hinges on proving the key range before you allocate. The bounds here are each a
one-line argument, and each is worth writing down in the code:

- **[74](/solutions/0074/)** — the digit-factorial successor of any number below 10⁷ is at most
  `7·9! = 2,540,160`, so every value on every chain fits in a 3,000,000-slot array.
- **[87](/solutions/0087/)** — every sum `p² + q³ + r⁴` that counts is below `N`, so a byte
  array of `N` slots deduplicates them.
- **[88](/solutions/0088/)** — the minimal product-sum number for set size `k` lies in
  `[k, 2k]` (the set `{2, k, 1, …, 1}` always works), so the distinct minima fit a `2·k_max`
  array.
- **[95](/solutions/0095/)** — proper-divisor sums are only followed while they stay `≤ N`;
  anything larger leaves the chain, so `seen` and `in_path` are `N + 1` slots.
- **166** — a cell holds a digit in `[0, M]`, so a sum of two cells is in `[0, 2M]` and a
  five-component key is a [mixed-radix](/topics/technique/mixed-radix) number in base `2M + 1`:
  `w⁵` slots, dense enough to allocate.

A bound you cannot prove is a buffer overrun waiting to happen in C; 74's C solution still guards
each access with `current < cache_size` and falls back to recomputing past the edge.

## Where C and Python part ways

This is the clearest C/Python split in the collection, and it runs one way: **C reaches for the
array, Python reaches for `dict` or `set`.**

In C there is no built-in map, and `calloc` hands you a zeroed table for free — zero doubles as
"empty", so 74 reads `chain_length_cache[n] != 0` as "cached". Problem 87 is the textbook case;
the dedup is one test and one store:

```c
unsigned char *seen = calloc((size_t)max_num, 1);
/* … inside the triple loop … */
if (!seen[number]) {
    seen[number] = 1;
    count++;
}
```

Python's 87 writes `numbers.add(number)` and returns `len(numbers)`. Its 74 keeps
`chain_length_cache: dict[int, int]`, its 95 a `seen: dict[int, int]`, its 166 a
`defaultdict(int)` keyed by a 5-tuple, its 212 a `defaultdict(list)` keyed by `(bx, by, bz)`.
That is the right call in Python, not laziness: a `list` index and a `dict` lookup are both a
few dozen nanoseconds of interpreter overhead, so the array saves little, while the dict stores
only the keys that occur and needs no bound at all. The asymptotics are the same; the constant
that direct addressing wins in C is swallowed by the interpreter.

Python does use direct addressing when the table is **the output**, not a lookup structure:
88's `min_prod: list[int] = [2 * max_k] * max_k` is indexed by `k` because every `k` gets an
answer, and 95 sieves its divisor sums into a `[0] * (max_num + 1)` list. And when it needs a
counter over a dense range at C speed it hands the whole job to numpy — 135 builds every
candidate `n` as one array and tallies them with
[`np.bincount`](/topics/technique/np-bincount), which *is* a direct-address counter written in C.

## Tricks the tables enable

- **Generation stamps instead of clearing.** 212's C solution must ask, for each new cuboid,
  "have I already tested neighbour `p`?" Rather than zeroing a `seen` array per cuboid, it
  stores the current cuboid's index: `if (seen[p] == idx) continue; seen[p] = idx;`. A stale
  stamp from an earlier cuboid simply never matches, so the reset is free.
- **Touched lists for sparse resets.** 74's second C variant flags `visited_flag[n]` during
  one walk and records each flagged slot in `visited_list`, then clears just those — a few dozen
  stores instead of a 3,000,000-byte `memset`.
- **Flattened multi-dimensional keys.** 166 folds five sums into one index,
  `((((a·w + b)·w + c)·w + d)·w + e)`, and 212 folds a bucket triple into
  `(bx·NB + by)·NB + bz` — the same Horner evaluation in both, giving a single contiguous
  allocation instead of nested arrays or tuple keys.
- **Fixed alphabets.** 68's C solution tracks the digits already placed on the ring in a
  `static int used[25]` with set/unset around each recursive step — backtracking with an
  `O(1)` undo, where the Python builds `set`s of remaining candidates.

## When to reach for it

Reach for a direct-address table when the key is an integer (or a tuple you can flatten into one)
with a bound you can **prove** and afford — tens of millions of bytes is fine, billions is not —
and when the lookup sits in the hot loop. Prefer a hash map when the universe is large and the
occupied keys are sparse, when you cannot bound the key, or when you are in Python and the table
is a lookup rather than the answer itself. The [lookup table](/topics/technique/lookup-table) page
covers the adjacent idea of tabulating a *function* ahead of time; this page is about using the
key as the address.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0135](/solutions/0135/) — Same Differences
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids

<!-- /problems -->
