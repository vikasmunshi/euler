<!-- tags: [c-dynamic-memory-allocation] -->
<!-- status: final -->
# calloc

Most C solutions here keep their working state on the heap. That state might be a sieve, a
memo table, or a DP layer. The size of the table depends on the input: a grid of `dim × dim`
cells, a sieve up to `N`, `3^rows` colourings, `2^n` subset masks. So the program can't
declare a fixed-size array. It asks the allocator at run time, with
[`malloc`](https://en.cppreference.com/w/c/memory/malloc) or, more often,
[`calloc`](https://en.cppreference.com/w/c/memory/calloc). The call itself is one line. What
matters is the three things around it: computing the size, checking the result, and freeing
it on every path out. This page is part of the language-idioms series. It covers the idiom,
why these solutions use it, and how it looks in Python.

## The idea

[Dynamic allocation](https://en.wikipedia.org/wiki/C_dynamic_memory_allocation) in C uses four
calls:

| Call | Gives you | Use it for |
|---|---|---|
| `malloc(bytes)` | uninitialised memory | buffers you fill completely before you read them |
| `calloc(count, size)` | `count × size` bytes, **all zero** | tables where 0 means "empty", "unvisited" or "probability 0" |
| `realloc(p, bytes)` | `p`'s contents in a block of the new size, possibly moved | growable lists |
| `free(p)` | gives the block back; `free(NULL)` does nothing | every block, exactly once |

`calloc` is the usual choice because nearly every table here starts at zero, and zero already
means something. In 28's spiral grid a `0` cell is free. In 74's chain cache a `0` length means
"not computed yet". In 87's dedup array a `0` byte means "this sum hasn't been seen". In the DP
tables of 189, 232 and 253, a zero entry is a probability or count that nothing has added to
yet. Using `calloc` replaces a `malloc` followed by a
[`memset`](https://en.cppreference.com/w/c/string/byte/memset) loop, and it can be cheaper than
that. For a large block the allocator takes fresh pages from the kernel that are already zero,
and a page is only backed by real memory when something writes to it. 151 relies on this. It
indexes a dense array by the full count tuple of five envelope sizes, about 1.4 million
`double`s per layer, while only a few dozen states are ever live. The untouched pages cost
next to nothing.

**Why the heap and not the stack.** A local array the size of 87's dedup table (one byte per
number below fifty million) would overflow the default 8 MB stack immediately. A C99
[variable-length array](https://en.cppreference.com/w/c/language/array#Variable-length_arrays)
has the same limit and fails without any error you can check. The heap has no such ceiling,
and it reports failure by returning `NULL`. The allocation also happens *inside* `solve()`, as
the house rule for every precomputed table requires. That way each `--runs` iteration pays for
the table it uses.

## Sizing: the multiplication is where it goes wrong

The size passed to the allocator is a product, and C does the multiplication in the type of
its operands. If those are `int`, the product overflows *before* any cast to `size_t` takes
effect. The solutions show the wrong placement and the right one:

```c
calloc((size_t)(dim * dim), sizeof(int));          /* 28: int product, cast too late   */
calloc((size_t)4 * (size_t)span * (size_t)span, …) /* 253: every factor widened first  */
```

28 is safe only because the grid is built for `size ≤ 10`, as a `--show` cross-check against
the closed form. If that guard were removed, a large enough `dim` would wrap the product to a
small or negative value, the allocation would succeed with the wrong size, and the loop would
write past its end. That is undefined behaviour with no error to catch. 232 does it correctly:
it computes `width = (size_t)target + 1` and squares that in `size_t`. 189 builds `3^rows` in a
`long long` by repeated multiplication, which is fine for any grid that fits in memory.

The second multiplication, `count × sizeof element`, is the reason to prefer `calloc(n, sizeof
*p)` over `malloc(n * sizeof *p)`. `calloc` receives the two factors separately, and glibc,
musl and the BSDs check the product and return `NULL` if it overflows. `malloc` only sees the
already-wrapped result. The `realloc` equivalent is
[`reallocarray`](https://man7.org/linux/man-pages/man3/reallocarray.3.html) (in glibc and
POSIX 2024). Two smaller habits also help: write `sizeof *p` instead of `sizeof(int)`, so the
element size follows the pointer's type if it changes, and remember that a shift such as
`1 << n` (105) or `(size_t)1 << digits` (961) is a multiplication too. Widen before you shift.
816 grows a power-of-two hash capacity in `unsigned int`. Doubling past 2³¹ wraps to zero and
the loop never ends, so the bound belongs in a 64-bit type or behind an explicit check.

A fixed size is fine when the mathematics, rather than the input, gives the bound. 74's cache
has 3,000,000 slots regardless of the limit, because the digit-factorial map never produces a
value above 7·9! = 2,540,160, whatever the starting number. What is wrong is a fixed size that
merely *guesses*.

## Checking and freeing

Every allocation can return `NULL`, and the solutions handle it in a few ways:

- **Allocate everything, check once, free everything.** 151, 189, 232, 253 and 816 request all
  their buffers, then test them in one `if`, and on failure call `free` on every pointer.
  This is correct because `free(NULL)` does nothing, so you don't need to know which allocation
  failed. It is the cleanest pattern here, and it extends to a single `goto cleanup` label when
  a function has several exits.
- **No check at all.** 105 and 743 write into `calloc`'s result straight away. On failure that
  is a null dereference: a crash rather than a reported error.
- **Exit.** 961 prints to `stderr` and calls `exit(1)`. That is acceptable at the top of
  `solve()`, but the `NULL` return that `runner.h` already treats as failure is better.

Freeing has two classic leaks, and 74 shows both. First, `seen = realloc(seen, …)` overwrites
the only pointer to the old block before checking the result. If `realloc` fails it returns
`NULL`, and the original buffer is unreachable. The safe form assigns to a temporary and
commits only on success. Second, its out-of-memory branches return early without freeing the
tables already allocated. Neither path runs in practice, but both are the kind of bug that
surfaces once the code is reused in a loop.

A real leak occurs in the *normal* path when a solution returns its answer in a buffer from
`malloc`, as 151 and 816 do. `runner.h` says the returned string belongs to `solve()` and must
be a literal or a `static` buffer: the harness `strdup`s it and never frees the original, so
every `--runs` iteration leaks one block. The `static char _answer[32]` that 28, 74 and 87 use
is what the contract asks for.

## The counterpart in Python

Python has no allocation call. The idioms that correspond to `calloc` are expressions:

| C | Python | Where |
|---|---|---|
| `calloc(n, 1)` byte flags | `bytearray(n)`: zeroed, one byte per slot | 87's sieve |
| `calloc(n, 1)` dedup flags | `set()` of the values seen | 87's sums |
| `calloc(n, sizeof(int))` | `[0] * n` | 105's subset sums, 189's DP layer |
| flat `calloc(w*h, …)` + index arithmetic | `[[0.0] * w for _ in range(h)]` | 232, 253 (four levels deep) |
| dense array sized by a bound | `dict`, sized by what is actually stored | 28's coordinate map, 74's cache, 151's states |

The last row is the real difference in design. Python solutions often use a `dict` where C
uses a dense array, and 151 shows both sides: Python keeps only the live states in a dict, and
C uses an oversized array that is zeroed lazily, plus an explicit list of live indices, to get
the same sparsity with O(1) indexing. 28 maps `(x, y)` tuples to values in Python, while C
shifts signed coordinates by `+half` into a flat grid.

The other C concerns don't carry over. Integers don't overflow, so the size can't wrap. A
request that is too large raises `MemoryError` instead of returning `NULL`, and reference
counting frees the table when `solve()` returns. Python has its own trap instead:
`[[0.0] * w] * h` creates `h` references to *one* row, so the comprehension form is required.
Python's lists also hold boxed object references, eight bytes a slot or more, against C's one
byte a flag. That is why 87's sieve is a `bytearray`. Its dedup, by contrast, is a `set` of the
sums actually hit, rather than C's fifty-million-byte flag array: the dense-versus-sparse choice
from the table above, made again.

## How to reason about it

- **Use `calloc` when zero means something**, which is nearly always for sieves, memo tables
  and DP layers. Use `malloc` only for buffers that are fully written before they are read.
- **Widen to `size_t` before multiplying or shifting**, not after. Let `calloc`, or
  `reallocarray`, multiply the element size for you, so the library checks the overflow.
- **Size from the input, or from a proven bound.** Write the bound in a comment next to the
  allocation, as 74 does.
- **Check every result, and free on every exit.** Allocate all buffers, test them together,
  and free all of them, relying on `free(NULL)` being a no-op. Never assign `realloc`'s result
  straight back to its argument.
- **Don't return heap memory from `solve()`.** Return a `static` buffer, as the runner contract
  requires.
- **In Python, choose `bytearray` or `[0] * n` for dense tables and a `dict` for sparse ones**,
  and build nested rows with a comprehension, never by multiplying a list of lists.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0232](/solutions/0232/) — The Race
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0961](/solutions/0961/) — Removing Digits

<!-- /problems -->
