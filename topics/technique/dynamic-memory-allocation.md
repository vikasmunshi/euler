<!-- tags: [dynamic-memory-allocation] -->
<!-- status: final -->
# Dynamic memory allocation

[Dynamic memory allocation](https://en.wikipedia.org/wiki/Dynamic_memory_allocation) is what the C
port has to say out loud where the Python sibling wrote `[0] * n` and moved on. Python's list grows
itself, sizes itself from the input, and disappears when the last reference does; C makes every one
of those three things a decision you write down — how many bytes, where they come from, and who
frees them. The problems below are the ones where that decision was interesting enough to be worth
indexing: a table too large for the stack, a buffer whose length is not known until it is filled, a
structure whose rows each need their own block.

## The idea

The C standard library gives four functions, and this repository uses all of them:

| call | what it does |
| --- | --- |
| [`malloc(n)`](https://en.cppreference.com/w/c/memory/malloc) | `n` bytes, contents **indeterminate** |
| [`calloc(k, n)`](https://en.cppreference.com/w/c/memory/calloc) | `k × n` bytes, **zeroed**, with the multiplication itself checked for overflow |
| [`realloc(p, n)`](https://en.cppreference.com/w/c/memory/realloc) | resize a block, copying the contents; may return a different address |
| [`free(p)`](https://en.cppreference.com/w/c/memory/free) | hand it back |

The reason they appear at all is that the alternatives do not stretch. An automatic array lives on
the stack, which is about 8 MB by default — problem 149 builds a $2000 \times 2000$ grid of
`long long`, 32 MB, and problem 161's memoisation table is one slot per (cell, mask) pair, which for
the $9 \times 12$ board is roughly $10^8$ entries, near a gigabyte. Neither fits, and neither has a
size known at compile time. A file-scope array would fit the second objection no better: its bound
would have to be a fixed worst case, and — the reason it is banned here — a table built once outside
`solve()` is free from the benchmark's second run onward, so the reported timing would understate
the real cost. Everything is allocated inside the call, sized to that call's input.

`calloc` versus `malloc` is not a style choice. A sieve wants zeroed memory and gets it from
`calloc` in one step, with the kernel often supplying already-zero pages; a buffer about to be
overwritten in full wants `malloc`, because zeroing it first is a wasted pass. Problem 23 uses both
within a dozen lines, and the pairing is deliberate — `calloc` for the two arrays it accumulates
into, `malloc` for the one it fills:

```c
long long *div_sums = calloc((size_t)(limit + 1), sizeof(long long));
if (!div_sums) { ... }
...
int *abundant = malloc((size_t)(limit + 1) * sizeof(int));
if (!abundant) { free(div_sums); ... }
```

Note the second line of each pair. `malloc` returns `NULL` on failure, and every early return after
the first allocation has to free what is already held — which is why the failure paths get longer
the further into a function you are. It is tedious and it is the job.

## Where the size comes from

Four shapes cover almost every allocation here, and choosing among them is the actual technique.

**The size is known.** The best case: one `malloc`, no growth, no waste. Problem 23's sieve is
`limit + 1` entries because that is exactly what a sieve to `limit` needs; problem 725's digit-sum
DP allocates `n + 1` rows of `SMAX + 1`. When a bound falls out of the problem statement, take it.

**The size is bounded, then trimmed.** Sieve first into a byte array, count what survived, then
allocate the exact array of primes. Problem 196 does this to build its prime lists, and it is the
common shape whenever a cheap pass over a superset precedes the real structure.

**Count in one pass, allocate, fill in a second.** When the count is expensive to bound but cheap to
compute, run the loop twice. Problem 461 says so in a comment — *"Pass 1: count pairs so a single
exact `malloc` can replace a growing buffer"* — and then repeats its binary search verbatim to fill
the block. Two passes of arithmetic buy one allocation of exactly the right size, with no copying
and no slack; on tens of millions of records that is the better trade.

**Grow by doubling.** When neither pass is available, start at a guess and double. Problem 70
estimates its prime count from the [prime-counting
approximation](https://en.wikipedia.org/wiki/Prime-counting_function) $\pi(x) \approx x / (\ln x -
1.1)$, then grows defensively if the estimate was low:

```c
if (n >= cap) {
    cap *= 2;
    int *tmp = realloc(primes, (size_t)cap * sizeof(int));
    if (!tmp) { free(primes); free(is_composite); *count = 0; return NULL; }
    primes = tmp;
}
```

Doubling is what makes this cheap: each element is copied a bounded number of times on average, so
appending stays $O(1)$ amortised — the same growth policy behind Python's `list.append`. Assigning
into a **temporary** is what makes it correct, and it is the single most-repeated mistake in this
tree. `p = realloc(p, n)` overwrites the only pointer to the old block with `NULL` when the resize
fails, and the block is leaked with no way back. Problem 56's big-integer growth is written the
short way and problem 70's is written the long way; the long way is the one to copy.

Not everything that grows uses `realloc`. Problem 720 doubles the length of two parallel arrays each
round, but the new contents are a *transformation* of the old rather than an extension of them — a
head, a seam, and a tail written from different formulas. So it allocates the new pair, fills them
from the old, frees the old, and swaps the pointers. `realloc` would have copied bytes that were all
about to be overwritten.

## Rows, and how many blocks that costs

For a two-dimensional table there are two layouts, and they are not equivalent.

A **flat block** with computed indices — `grid[r * N + c]` — is one allocation, one `free`, and one
contiguous run of memory the prefetcher can follow. Problem 149 uses it for its 32 MB grid, which
matters: it scans that grid by row, by column, and along both diagonals, and the flat layout keeps
the row scans at stride 1.

An **array of pointers** — `int **triangle` — costs one allocation for the spine plus one per row,
and the rows may land anywhere. What it buys is ragged rows and rows that can be
built independently. Problem 18's triangle has row $i$ of length $i + 1$, so ragged is the natural
fit; problem 163 allocates one block per family of lines, each sized to that family. Problem 171
builds its DP one layer at a time — each layer a fresh `calloc`, because the recurrence reads
unvisited states as zero and depends on getting them that way — and hangs the layers off a spine of
pointers.

The rule of thumb is the obvious one — flat unless the rows genuinely differ in length or lifetime —
and the cost of getting it wrong is a loop you must remember to write:

```c
for (int i = 0; i < rows; i++) free(triangle[i]);
free(triangle);
```

Freeing the spine without the rows leaks every row, and it compiles silently.

The third layout worth knowing is the one that avoids the table altogether. Problem 196 needs three
adjacent rows of a triangle at a time, not the triangle, so it allocates exactly three row buffers
and slides them. Memory becomes a function of the window rather than of the input — which is often
the difference between an allocation that works and one that does not.

## Freeing, and why it is not optional here

The runner is what makes leaks visible. `main()` calls `solve()` in a timed loop — `--runs=N` runs
it `N` times — so a block leaked per call is leaked `N` times, and a benchmark at `--runs=100` over
a 32 MB grid is asking for 3.2 GB. The contract in `runner.h` is explicit about the one place this
bites hardest, the answer itself:

> The returned pointer is owned by `solve()` and must stay valid until the next call — return a
> string literal or write into a `static` buffer; do not return a per-call `malloc`'d buffer (it
> would leak across `--runs`).

That is why every solution ends by formatting into `static char _answer[32]` rather than returning
allocated memory. Within `solve()`, the discipline that follows is: allocate on entry, free before
every `return`, and free in the error paths too. A helper that returns an allocated block —
problem 13's decimal-string builder, problem 70's prime array, the runner's own `get_text_file` and
`parse_list` — documents that the **caller** frees it, and the caller does.

## How to reason about it

**Size to the input, not to a worst case.** The house convention is that sieves, tables and caches
are built inside `solve()`, sized from the arguments. Dynamic allocation is what makes that possible:
a `#define MAX 10000000` array is the thing you write when you have given up on the input telling you
how big it should be.

**Allocation is not free, but it is rarely the cost.** One `malloc` of 32 MB is a `mmap` and some
bookkeeping — noise against the loop that fills it. A `malloc` *inside* the loop is a different
story. The pattern to watch for is a per-iteration scratch buffer of fixed size; hoist it out of the
loop and reuse it. Problem 96's Sudoku solver allocates one per branch of its backtracking search,
which is the deliberate version of that trade: it copies the candidate set before mutating it so the
caller's set survives for the next branch, and the copy shrinks by one cell at every level.

**Cast the operands, not the result.** `malloc(n * sizeof(int))` with `n` an `int` overflows before
`malloc` ever sees the number, and on a 32-bit `int` that happens at 2 GB — well inside the range
some of these tables occupy. Every allocation in this tree writes `(size_t)n * sizeof(int)`, widening
first. `calloc(k, n)` gets this right for you: it takes the count and the element size separately,
and every mainstream implementation detects an overflowing product and returns `NULL` rather than a
short block.

**Use `sizeof *p`, not `sizeof(type)`.** `long long *stack = malloc((size_t)capacity * sizeof *stack)`
— problem 218's line, and problem 223 writes the same idiom for its `Triple` stack — stays correct
when the element type changes. `sizeof(long long)` does not, and the resulting bug is a silent buffer
that is the wrong size.

**`realloc` invalidates the old pointer.** Anything else pointing into the block — an index kept as
a pointer, a cached `end` — is dangling the moment the resize moves the data. Keep offsets, not
pointers, across a growth point. This is the same hazard as holding an iterator across a
`std::vector::push_back`, and it fails the same way: usually not at all, until it does.

**Reach for it when the size depends on the input, and not before.** A fixed small buffer on the
stack is faster, cannot leak, and cannot fail. Problem 70's digit-permutation test uses a
ten-element frequency count and says so in its comment — *"an allocation-free 10-bucket frequency
count"*. The heap is for the things that genuinely do not fit.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0013](/solutions/0013/) — Large Sum
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0096](/solutions/0096/) — Su Doku
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0127](/solutions/0127/) — abc-hits
- ● [0135](/solutions/0135/) — Same Differences
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0161](/solutions/0161/) — Triominoes
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
