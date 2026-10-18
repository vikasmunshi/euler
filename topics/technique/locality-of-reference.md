<!-- tags: [locality-of-reference] -->
<!-- status: final 2026-10-18T12:40Z -->
# Locality of reference

[Locality of reference](https://en.wikipedia.org/wiki/Locality_of_reference) is the observation
that programs tend to touch memory near what they touched recently (*spatial* locality) and to
touch the same memory again soon (*temporal* locality). Hardware is built around that bet: a cache
line brings in 64 neighbouring bytes, the prefetcher streams ahead of a linear scan, and the TLB
covers a few megabytes of recently used pages. Code that matches the bet runs at memory-bandwidth
speed. Code that breaks it waits about a hundred cycles for each miss. Two algorithms with the same
operation count can therefore differ several-fold in run time, and in Project Euler that gap tends
to open on exactly the problems with huge flat arrays: tables indexed by $n$ up to $10^9$ and
sweeps over boards with $2^{31}$ rows. The three solutions below show the three usual remedies: a
flat array instead of a hash, blocking scattered writes, and shrinking the working set to a window.

## The idea — the cost of a memory access depends on where it lands

A rough hierarchy, enough to reason with:

| level | typical size | latency |
|---|---|---|
| L1 cache | 32–48 KB | ~4 cycles |
| L2 cache | 1–2 MB | ~14 cycles |
| L3 cache | tens of MB, shared | ~40–60 cycles |
| DRAM | GB | ~200+ cycles, plus a TLB miss if the page is cold |

The question to ask of an inner loop is not "how many operations?" but "**how many distinct cache
lines does it touch, and in what order?**". A sequential pass over an array touches each line once,
and the prefetcher hides the latency. A pass that jumps by a growing stride touches a new line, and
often a new page, on every access. The remedies all aim to make the touched set either sequential
or small enough to stay resident.

## Three remedies across the problems

**A flat array instead of a hash table (problem 14).** The Collatz solution memoises chain lengths.
Python uses `functools.lru_cache`, a hash table. The C side uses a `calloc`'d array indexed by $n$,
with 0 as the "not computed" [sentinel](/topics/technique/sentinel-value):

```c
if (n < cache_size && cache[n] != 0) return cache[n];
...
if (n < cache_size) cache[n] = result;
```

[Direct addressing](/topics/technique/direct-addressing) wins twice. There is no hashing, and the
entries are 8-byte slots packed together, where a Python dict entry points to separately allocated
`int` objects. Collatz lookups jump about ($n \to n/2$, $n \to 3n+1$), so locality is not perfect,
but the scan over starting values walks the array in order, and the chains keep falling into the
same small, heavily reused values at the bottom of the table, which stay cached. The other side of the trade-off is that values above
the limit (the $3n+1$ excursions) are not cached at all, since the array has no slot for them. That
costs a little recomputation and keeps the table compact.

**Blocking scattered writes (problem 229).** The solution sieves four quadratic forms
$a^2 + d\,b^2$ into byte masks over $[0, N]$, with $N$ in the billions, and intersects them. Written
naively (for each $b$, mark every $a^2 + d b^2$), the writes for one $b$ jump quadratically across a
multi-gigabyte array: each write is a cache miss *and* a TLB miss. The fix is
[loop tiling](https://en.wikipedia.org/wiki/Loop_nest_optimization). Sweep the output in windows
$[lo, hi)$ of $3.2 \times 10^7$ bytes. For each window and each $b$, compute the sub-range of $a$
whose marks fall inside it, $a \in [\lceil\sqrt{lo - c}\rceil, \lfloor\sqrt{hi - 1 - c}\rfloor]$, and
mark only those. The total work is unchanged, since every mark is still written once, but every
write in a window now lands in the same resident span. The notes record that this one change cut
the Python run from about 75 s to about 52 s. It is the same move as a
[segmented sieve](/topics/technique/segmented-sieve): reorder the loops so the *output* is the outer
loop and the scattered source is the inner one.

**Shrinking the working set to a window (problem 331).** The board has $N = 2^i - i$ rows, with $i$
up to 31, so a per-row array is already gigabytes, and the solution needs, for every odd-width row,
the number of odd-width *positions* inside its black interval. Each row's black cells form one
interval $[L_b, R_b]$, and both ends move monotonically as $b$ falls. So the positions that matter
at any moment lie in a window of about $4\sqrt{2N}$ entries that slides in one direction. Nothing
outside the window is ever needed again. At the largest board the window is about 256 KB of byte
flags, which fits in L2.

## The C side and the Python side solve it differently

The same principle leads to different code in the two languages, because what is expensive differs.

- **In C the constraint is the memory system.** 331's C side keeps the window as a
  [ring buffer](/topics/technique/circular-buffer) whose capacity is rounded up to a power of two, so
  the index is `pos & (capacity - 1)` with no division. It also uses temporal locality in the
  arithmetic itself. Both square roots that bound a row fall monotonically, so each is carried
  forward and nudged by a `while` loop instead of being recomputed with `sqrtl`, and every
  position's width is computed exactly once. The whole sweep is $O(N)$ time with a working set the
  size of that window. 229's C side applies the same window blocking to a plain scalar `for` loop, and 14's
  is the flat array above.
- **In Python the constraint is the interpreter, so the work moves into NumPy, and then NumPy's
  temporaries become the locality problem.** A
  [vectorised](/topics/technique/vectorized) expression over a whole window allocates several
  full-size intermediate arrays (squares, differences, roots, parities), and each one is written to
  memory and read back. 331 therefore processes rows in blocks of $2^{14}$ elements, small enough
  that every temporary stays in cache, which its comments put at about a factor of three over
  whole-window arrays. It builds a [prefix count](/topics/technique/prefix-sum) of odd positions per
  window rather than a ring buffer, because a per-element ring update would be a Python-level loop.
  229 does its marking as one [fancy-indexed](/topics/technique/fancy-indexing) assignment
  `mark[a * a + c] = True` per (window, $b$) pair, so the blocking and the vectorisation work
  together.
- **14 is the exception:** it is not vectorisable, and in Python the hash table's cost is small
  next to the interpreter overhead of the recursion itself. Locality is a C-side advantage there.

## How to reason about it

- **Estimate the working set of the inner loop.** If it fits in L2, the loop's speed is limited by
  arithmetic. If it is a random walk over gigabytes, the loop's speed is limited by memory latency,
  and no amount of arithmetic tuning will help.
- **Prefer arrays over hash tables when the keys are dense integers.** Lower constant factors,
  better packing, and no hashing. Check the bound first: a slot per key must actually fit in
  memory.
- **Tile scattered writes by output range.** If an inner loop's writes jump across a large array,
  swap the loop order so a window of the output is fixed and the source is scanned for what lands
  in it. The extra cost is computing the source sub-range per window, here one `isqrt` each way.
- **Slide a window when the access pattern is monotone.** Two monotone pointers into a sequence
  mean the live data is a window. Keep only that, in a ring buffer in C or a per-block array in
  NumPy.
- **In NumPy, block to keep temporaries small.** Whole-array expressions are simple to write but
  stream every intermediate through DRAM. Blocks of $10^4$–$10^5$ elements usually stay in cache
  while still amortising the per-call overhead.
- **Measure.** Locality gains are real but hardware-dependent. 229's 30% and 331's factor of three
  were measured, not predicted. Benchmark both versions before accepting the more complex one.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0331](/solutions/0331/) — Cross Flips

<!-- /problems -->
