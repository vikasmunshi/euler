<!-- tags: [counting-sort] -->
<!-- status: final 2026-10-19T09:39Z -->
# Counting sort

[Counting sort](https://en.wikipedia.org/wiki/Counting_sort) sorts integers from a small range
$[0, K)$ without comparing them. It counts how often each value occurs in an array indexed by the
value, turns those counts into starting positions with a prefix sum, and scatters each item into its
slot. It runs in $O(n + K)$, beating the $O(n \log n)$ lower bound for comparison sorts because it
never compares. In Project Euler the full sort is rare, but its **first phase**, the value-indexed
tally, is everywhere. "Which perimeter has the most triangles?" and "how many tile counts arise exactly
$n$ times?" are both [histograms](/topics/domain/histogram) over a bounded integer key. The three solved
problems below use that tally, and one of them goes on to do the full scatter.

## The idea — the key is the index

Counting sort applies when the **key is a small non-negative integer**. Then:

1. **Count**: `count[key(x)] += 1` for every item. This is
   [direct addressing](/topics/technique/direct-addressing): no hashing, no comparisons, one array
   write.
2. **Prefix-sum**: `start[k] = count[0] + … + count[k-1]` gives each key's first slot
   ([prefix sum](/topics/technique/prefix-sum)).
3. **Scatter**: write each item to `out[start[key]++]`. Items with equal keys keep their input
   order, so the sort is *stable*, which is what makes it usable as a pass inside radix sort.

In a counting problem you usually stop after step 1. The array *is* the answer, read by a linear
scan for the maximum, or for every key whose count falls in some range. The cost to accept is
$O(K)$ memory and an $O(K)$ scan even if most keys never occur, which is cheap when $K$ is the
problem's limit ($10^3$ or $10^6$) and too much when $K$ is $10^{12}$.

## Three problems across the range

**39, integer right triangles: a histogram of perimeters.** Generate every
[Pythagorean triple](/topics/domain/pythagorean-triple) with perimeter $\le 1000$ from Euclid's
formula, primitive perimeter $p_0 = 2m(m + n)$ and every multiple $kp_0$, and count by perimeter. The
public C does exactly the tally:

```c
counts[p0]++;
for (int k = 2; k < k_limit; k++) counts[k * p0]++;
```

then scans `counts[1..P]` for the maximum. One caution, visible in the code: `k < P / p0` (and
`range(2, P // p0)` in Python) stops **one multiple short**. The largest multiple $\lfloor P/p_0 \rfloor p_0$
is never counted, so 33 perimeters below 1000 are under-counted. The winning perimeter has
eight triangles but is credited with seven. The answer survives only because the runner-up is not
close. The bound should be `k <= P / p0`.

**166, criss cross: the full counting sort.** A meet-in-the-middle count over 4×4 digit grids needs
all four-digit rows grouped by their digit sum $s \in [0, 4M]$, a small key. The C does the
textbook three passes: count rows per sum into `off[s+1]`, prefix-sum `off` into block starts, then
place each row at `cursor[s]++`. The rows end up in one contiguous array with each sum's rows in
one block, `rows[off[s] .. off[s+1])`, which the inner loops then sweep. The same solution also uses
direct addressing for its second stage. Each half-grid is keyed by five partial sums, each in
$[0, 2M]$, so for $M = 9$ a dense $19^5$-entry table of counts replaces a hash map.

**174, hollow square laminae II: a histogram of tile counts.** A lamina with outer side $a$ and hole
$b$ uses $t = a^2 - b^2$ tiles. The solution enumerates every lamina with $t \le 10^6$, bumps
`counts[t]`, and finally counts the $t$ whose tally lies in $[1, 10]$. It never stores laminae, only
how many land on each $t$. That is the counting phase alone, with the key being the problem's own
quantity.

## Python and C

- **The tally structure.** C always uses a dense array: `calloc` of $K + 1$ counters. The Python
  solutions vary. 39 appends every perimeter to a list and calls
  [`collections.Counter`](/topics/technique/collections-counter)`(...).most_common()`, which is a hash-map
  histogram plus a sort. 174 uses `array('I', ...)`, a dense typed array, the faithful counterpart of
  the C. For a key range the size of the limit, the dense array is both faster and smaller than a
  `Counter`.
- **166**: here the languages differ most. Python groups rows with `defaultdict(list)` (bucketing by
  hash) and tallies half-grids in `defaultdict(int)` keyed by 5-tuples. C counting-sorts the rows and
  flattens the 5-tuple into a mixed-radix index $(((c_1 w + c_2) w + c_3) w + d_1) w + d_2$ with
  $w = 2M + 1$. It also keeps a `touched` list, so that combining the halves visits only the keys that
  actually occurred instead of all 2.5 million slots. Resetting the table with `memset` for each $s$ is
  the cost of that dense layout.
- **Counter width.** C picks the counter type deliberately (`int` in 39, `unsigned int` in 174). Python
  never has to, but `array('I')` brings the question back: a 32-bit unsigned counter that overflowed
  would raise `OverflowError`, not wrap.

## How to reason about it

- **Bounded integer key → array, not dict.** If the key fits in memory as an index, a list or array
  beats a hash map on speed and memory, in both languages.
- **You rarely need the sort.** For "most common", "how many with count $n$", or "group by key", the
  count array is the result. Do the prefix-sum and scatter only when you need the items laid out by key
  (166).
- **Stable placement for free.** The scatter preserves input order within a key, which matters when a
  later pass sorts by a second key.
- **Watch the range, not the count.** Cost is $O(n + K)$. A handful of items with keys up to $10^{12}$
  is a job for a hash map or a comparison sort, not this.
- **Check the loop bounds of the tally.** An off-by-one in "every multiple up to $P$" silently drops
  counts and still often gives the right answer (39), so test against brute force on small limits.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0174](/solutions/0174/) — Hollow Square Laminae II

<!-- /problems -->
