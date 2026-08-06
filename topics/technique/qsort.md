<!-- tags: [qsort] -->
<!-- status: final -->
# qsort

[`qsort`](https://en.cppreference.com/w/c/algorithm/qsort) is the only sort the C standard
library gives you, and in this repository it is the C port's answer to a single line of Python.
Every problem below has a Python sibling that wrote `sorted(...)` and moved on; the C side has to
supply a comparator, decide what the array elements actually are, and find somewhere to put the
context the comparator needs. That gap — one call versus a design decision — is why `qsort` shows
up as a technique tag at all, and why the same handful of mistakes recur.

## The idea

The signature is deliberately type-blind:

```c
void qsort(void *base, size_t nmemb, size_t size, int (*cmp)(const void *, const void *));
```

`qsort` knows nothing about your elements except how many bytes each occupies. It reorders them by
copying `size` bytes at a time, and it asks your comparator, through a function pointer, which of
two elements comes first: **negative** if the left one sorts earlier, **zero** if they are
equivalent, **positive** otherwise. The standard requires only that the result be `O(n log n)` on
average — the name is historical, and a modern libc typically runs
[introsort](https://en.wikipedia.org/wiki/Introsort) or a merge sort rather than plain
[quicksort](https://en.wikipedia.org/wiki/Quicksort).

What the ports use it *for* is almost never "produce a sorted list". Three jobs cover nearly all of
them:

- **Count or collapse duplicates.** C has no `set` and no `dict`. When the Python sibling wrote
  `len(set(values))`, the C port sorts the array and counts the places where an element differs
  from its predecessor. Problems 757, 221 and 165 all end this way; problem 203 does it over GMP
  integers, summing each distinct value once as it scans.
- **Bring equal keys into contiguous runs.** Once sorted by a key, a `while` loop can walk one
  group at a time. Problems 142, 926 and 1000 all use this run-scan: gather the block of records
  sharing a key, process it as a unit, advance. Problem 1000 depends on it for *correctness*: it
  walks edges in increasing weight, and all the edges of one weight must be applied as a single
  snapshot so that two of them never chain — only the sort puts them adjacent to be grouped.
- **Create the monotonicity a later search relies on.** Problem 143 sorts each adjacency list so
  membership becomes a binary search instead of a scan; problem 127 sorts candidates by radical so
  an inner loop can `break` at the first failure; problem 768 sorts *both* halves of a
  meet-in-the-middle table so they can be joined by one two-pointer merge instead of an all-pairs
  sweep. The sort's `n log n` is bought to change the *inner* loop's asymptotics, not to tidy the
  data.

Problem 52 is the smallest complete example, and it is public, so here it is whole. The digits of
`n` are extracted least-significant-first and sorted into a canonical fingerprint — order out of
the extraction is irrelevant precisely because a sort follows:

```c
static int cmp_char(const void *a, const void *b) {
    return (*(const char *)a) - (*(const char *)b);
}
...
qsort(tmp, (size_t)len, 1, cmp_char);
```

Note the element size of `1`: `qsort` sorts an array of anything, including raw `char`s, and a
digit-permutation test becomes `strcmp`.

## Writing the comparator

**Do not subtract, except on small types.** `return *(int *)a - *(int *)b;` is the textbook
one-liner and it is wrong the moment the values are wide: the difference of two large `int`s
overflows, which is undefined behaviour, and the comparator silently reports the opposite order.
Problem 52's `cmp_char` above gets away with it because digits are `char`s; every comparator in
this repository over `long long`, `int128` or a struct field instead uses the branch-free
three-way idiom:

```c
return (x > y) - (x < y);   /* -1, 0, or +1 — no subtraction, no overflow */
```

Both parenthesised comparisons yield `0` or `1`, so the difference is exactly the sign, and the
compiler emits it without a branch. Problems 118, 757, 221, 926, 768 and 1000 all carry this exact
line. It is worth making a habit — it costs nothing and removes an entire class of bug.

**Give the comparator a total order if you want determinism.** `qsort` is **not stable**: elements
your comparator calls equivalent may come out in any order, and the order can differ between libc
versions. When the downstream code cares, add tie-breakers until the order is total. Problem 127
compares by radical and then by index for exactly this reason; problem 165 compares its
three-field rational key lexicographically, returning `0` only for genuine equality, which is what
makes the following distinct-count scan correct.

**Sort indices when the data is in parallel arrays.** Problem 464 keeps its points as several
`long long` arrays and sorts an array of `int` indices, with the comparator dereferencing the key
array. Nothing large is copied, the parallel arrays stay aligned, and one array can be sorted by
several different keys in turn.

**There is nowhere to put context.** `qsort`'s comparator takes two element pointers and nothing
else — no user-data parameter. Three ways out appear here:

| approach | seen in | cost |
| --- | --- | --- |
| a file-scope variable the comparator reads | 464 (`g_key`), 252 (`sort_base`) | not reentrant; fine in a single-threaded `solve()` |
| a [GCC nested function](https://gcc.gnu.org/onlinedocs/gcc/Nested-Functions.html) closing over locals | 127, 142 | a GNU extension, not ISO C |
| [`qsort_r`](https://man7.org/linux/man-pages/man3/qsort_r.3.html) / C11 `qsort_s` | — | correct, but the argument order differs between glibc and BSD |

Problem 464's declaration says the quiet part out loud: `qsort has no context pointer without
qsort_r; single-threaded solve() only`. Writing that comment is the honest version of using a
global here — it is a deliberate, scoped exception, not an accident.

## After the sort

Sorting is the setup; the scan that follows is where the answer comes from, and it has two shapes
worth knowing by heart. Counting distinct values:

```c
for (size_t i = 0; i < len; i++)
    if (i == 0 || vals[i] != vals[i - 1]) distinct++;
```

and compacting in place, which is the same loop writing as it goes (`if (i == 0 || v[i] != v[u-1])
v[u++] = v[i];`, leaving `u` as the new length). Problems 221, 180 and 143 use the compacting form
because they need the deduplicated array afterwards; 757, 165 and 203 only need the count or the
sum, so they scan without writing.

The third shape is the run walk: an outer `while` that finds the end of the current key's block
with an inner `while`, handles the block, then jumps `i` to the block's end. It costs one pass and
it is how 142, 926, 1000 and 464 all consume their sorted arrays.

If what you want is a lookup rather than a pass, the standard library's
[`bsearch`](https://en.cppreference.com/w/c/algorithm/bsearch) takes the **same comparator** —
sort once, search many times, with one function serving both. Problem 184 pairs them directly.

## How to reason about it

**The constant factor is the function pointer.** Every comparison is an indirect call that cannot
be inlined, which is the price of a type-erased sort in C — C++'s `std::sort` is faster mainly
because it inlines the comparison. On a few million elements this is a real but tolerable cost; if
the sort is genuinely hot and the keys are small bounded integers, a
[counting](https://en.wikipedia.org/wiki/Counting_sort) or
[radix sort](https://en.wikipedia.org/wiki/Radix_sort) beats it outright. Keep the elements small
for the same reason: `qsort` physically moves `size` bytes per swap, so sorting an array of fat
structs is slower than sorting indices into them.

**Elements must survive a byte-wise move.** `qsort` relocates elements with raw copies, so
anything holding a pointer *into itself* breaks. GMP's `mpz_t` is fine — it is a struct holding a
pointer to separately allocated limbs, so the pointer travels with the struct, which is why
problem 203 can `qsort` an array of them with `sizeof(mpz_t)` and a `mpz_cmp` wrapper. A struct
with an interior self-reference would not be.

**The comparator must be consistent.** A comparator that is not a valid ordering — one that says
`a < b` and `b < a`, or whose result depends on state that changes mid-sort — is undefined
behaviour, not merely a wrong answer; `qsort` may read out of bounds. The globals-for-context
pattern above is safe only because the global is set *before* the call and left alone during it.

**Sort inside `solve()`.** A table built and sorted at file scope or in a `static` initialised
once is free from the second benchmark run onward, and the reported timing will understate the
real cost. Every array here is allocated, filled, sorted and freed within the call.

**And check whether you need the sort at all.** For a bounded integer range, a bit array or a
direct-indexed counter answers "distinct?" in one linear pass with no comparator — problem 143
uses exactly that for its sum bitset while still sorting its adjacency lists, because the two
questions have different shapes. `qsort` is the general tool; reach for it when the key space is
too large or too structured to index directly.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0127](/solutions/0127/) — abc-hits
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0165](/solutions/0165/) — Intersections
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0768](/solutions/0768/) — Chandelier
- ● [0926](/solutions/0926/) — Total Roundness
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
