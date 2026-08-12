<!-- tags: [array-data-structure] -->
<!-- status: final -->
# Array data structure

An [array](https://en.wikipedia.org/wiki/Array_data_structure) is a block of memory holding
equal-width elements, addressed by arithmetic: element $i$ lives at `base + i × width`, found with
no comparison, no pointer chase, no hash. Every other property follows from those two words —
*contiguous* and *homogeneous* — and so does everything interesting on this page. The tag lands on
problems with nothing else in common because the array is rarely the *point* of a solution; it is
the substrate the point is expressed on, and the decisions it forces — what the index means, how
many dimensions collapse into one, how wide an element is — are made early and are hard to change
later.

## The idea

Three neighbouring pages divide the subject, and it is worth saying which is which.
[Lookup table](/topics/technique/lookup-table) is about *what you put in the slots* and whether
building them pays. [Dynamic array](/topics/technique/dynamic-array) is about *what happens when you
run out of them* — geometric growth and its amortised cost. This page is about the **addressing**:
the fact that a subscript is arithmetic rather than a search, and the design that follows from
wanting it to stay that way.

The precondition is strict, and it is the whole trade. Every element must be the same width, or
`base + i × width` is not computable; the length must be known before you index, or the arithmetic
is unchecked. In exchange you get $O(1)$ access with a constant so small it disappears, and
**[locality of reference](/topics/technique/locality-of-reference)** — a sequential scan pulls whole
cache lines of useful data, which on the problems below is worth more than the asymptotics.

## The index is the data

The sharpest use of an array stores nothing you could not have computed, because the *position*
carries the meaning and the payload is a single bit of judgement about it.

Problem 7 finds the 10 001st prime with a [sieve of Sundaram](/topics/technique/sieve-of-sundaram),
and the array is the sieve:

```python
max_expected_value = int(n * math.log(n))
numbers = list(range(0, max_expected_value + 1))
for i in numbers[1:]:
    for j in range(i, max_expected_value + 1):
        numbers[i + j + 2 * i * j] = 0      # index k denotes the odd number 2k+1
```

Index $k$ *is* the odd number $2k+1$; the stored value only records whether it survived. That the
list is initialised to `range(...)` — every slot holding its own index — is the redundancy made
visible: the payload could be one bit, which is what a [bit array](/topics/technique/bit-array)
would exploit. The bound is the other half of the design. `n · ln n` is the prime-number-theorem
estimate of the $n$-th prime, so the array is [sized to the input](/topics/takeaway/size-work-to-the-input)
rather than to a guessed constant — the only way to allocate exactly once and never check again.

The same shape recurs wherever a range of integers is being tallied. Problems 135 and 136 both reduce
to counting how many factorisations $n = u \cdot v$ satisfy a congruence, and both answer it by
sweeping generator pairs and incrementing `count[u * v]` — an array indexed by the value being
counted, then scanned once for the entries equal to a target. Problem 122 fills `m[k]` with the
minimal addition-chain length for $k$, written by an iterative-deepening search that reaches targets
in increasing depth order; the array is where a tree search deposits its results, keyed by the
target itself. In all three the array is doing what a [hash table](/topics/technique/hash-table)
would do at ten times the cost per probe, and it can only do so because the key is already a dense
integer.

## Flattening: many dimensions, one allocation

C has no true multidimensional array beyond a fixed shape, and the habit that fills the gap is worth
having in any language: compute the address yourself.

Problem 83 walks a grid with Dijkstra. Python keys its distance and visited maps on `(row, col)`
tuples; the C sibling flattens the same grid to **[row-major](https://en.wikipedia.org/wiki/Row-_and_column-major_order)**
indices and allocates one array per quantity:

```c
int n = size * size;
long long *dist = malloc((size_t)n * sizeof(long long));
...
int ni = nr * size + nc;      /* (row, col) -> one integer */
```

Two pointer dereferences and a tuple hash per neighbour become one multiply-add. Problem 504 does
the same for its $\gcd$ table — a single `malloc` of $(m+1)^2$ ints indexed `g[i * (m + 1) + j]`,
where the Python side builds a list of lists. Problem 151 pushes it furthest: five sheet counts, each
$0..16$, pack into one integer by repeated `idx * 17 + count`, giving a dense array over the entire
state space that the search addresses directly.

Problem 150 shows the version worth stealing. Its data is a **triangle**, and the natural
rectangular array wastes half its cells on zeros above the diagonal. The C solution stores row $r$ at
offset $r(r+1)/2$ in one flat block, and — because that division would otherwise land in the hot
loop — precomputes the offsets into a small side array:

```c
for (int r = 0; r < n; r++)
    T_off[r] = r * (r + 1) / 2;   /* ragged rows, one allocation, no per-access division */
```

That is the general recipe for a ragged array: **one contiguous block plus a table of row starts**.
It keeps every row's scan sequential, costs one extra indirection, and is how sparse-matrix and
adjacency-list ([CSR](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_%28CSR%2C_CRS_or_Yale_format%29))
formats are laid out. The Python side, using [NumPy](/topics/technique/numpy), pads to a square
instead and pays memory to keep the slicing expressible — a defensible trade in the other direction.

## The element type is a design decision

Because an array is homogeneous, choosing its element width is choosing its footprint, and at scale
that choice is the difference between fitting in cache, fitting in RAM, and not fitting at all.

Problem 136 sweeps to fifty million and needs, for each $n$, only whether it has zero, one, or more
than one representation. The tally is declared accordingly:

```python
count = np.zeros(max_limit, dtype=np.int8)   # 0, 1, "2 or more" — one byte is enough
```

Fifty megabytes. The same fifty million counters in a Python list would be an array of *pointers* to
integer objects — 400 MB of pointers before the objects they point at, and no possibility of a
vectorised final scan. The C sibling makes the identical call with `signed char`, and the comment
says the same thing. Problem 504 shows the other end of the same reasoning: its Python keeps perfect
squares in a `set`, while its C keeps a `calloc`'d `char` array with a `1` at every square index —
sparse data, but over a bounded range where one byte per slot is cheaper than any hash. When the
range is bounded, a characteristic vector beats a set; see also [`bytearray`](/topics/technique/bytearray).

## What a Python list is not

A Python `list` is an array — of pointers. The pointers are contiguous; the objects are not. That
single fact explains most of the Python-to-C ratios on this page, and one idiom that mitigates it.

A list of lists is a list of *pointers to rows*, so `g[b][a]` costs two dereferences, and hoisting
the row out of the inner loop removes one of them:

```python
for b in range(1, m + 1):
    gb = g[b]                 # bind the row once
    for a in range(1, m + 1):
        ...gb[a]...           # one dereference instead of two
```

Problem 504 does exactly this, and its C sibling writes the same optimisation as
`const int *gb = &g[b * (m + 1)]` — the identical idea, one language admitting that a row is an
address. It still runs 7.06 s against 0.097 s, a factor of 73, because the remaining per-element cost
is interpreter overhead the idiom cannot touch.

The spread across these problems is instructive about *when* the gap bites. Problem 7's sieve, a
tight scalar loop over a list, runs 106× slower than C; problem 109's board enumeration, 174×;
problem 14's memo — an `lru_cache` dict in Python against a flat `calloc`'d array in C — 44×. Where
the array work is handed to NumPy the gap narrows to what the surrounding Python costs: problem 150,
whose inner two loops become [vectorised](/topics/technique/vectorized) `cumsum` and fancy-indexed
gathers, sits at 9×. And problem 28, which discards the array entirely for a closed form, lands at
1.4× — the reminder that the fastest array is the one you did not allocate.

Problem 25 makes the inverse point. Its Python is six lines because arbitrary-precision integers are
built in; the C sibling has to *become* the array — a `BigInt` of base-$10^9$ limbs with explicit
carry propagation — to say the same thing. The array did not appear because C is lower level; it was
always there, inside CPython's `int`.

## Clearing costs what filling costs

The one array operation that is not $O(1)$ is the one people forget: touching all of it. Zeroing an
array is linear in its length, not in the number of cells you used, and if that happens inside a loop
it can dominate everything else.

Problem 151 is the clean illustration. Its state space packs into $17^5 \approx 1.4$ million slots, but at
most about a dozen states are live in any batch. The C solution allocates the dense array anyway —
`calloc` leaves untouched pages lazily zeroed, so the unused bulk is never faulted in — and keeps an
explicit list of live indices beside it, so each batch iterates only those and, crucially, **zeroes
only the cells it wrote** before swapping buffers. Dense addressing with sparse traversal: the array
gives $O(1)$ access, the side list gives $O(\text{live})$ iteration, and neither pays for the
1.4 million slots. That is the same information the Python dict carries implicitly, spelled out.

## How to reason about it

- **Decide what the index means before what the slot holds.** If the index already carries the
  answer — a sieve, a tally, a state code — the payload shrinks to a flag and often to a bit.
- **A dense integer key wants an array; anything else wants a hash.** Density, not taste, chooses the
  container, and re-encoding a sparse key into a dense one is a legitimate move.
- **Flatten deliberately.** Row-major `r * ncols + c` for rectangles, a block plus a row-offset table
  for ragged shapes. One allocation, sequential scans, no per-access division.
- **Pick the narrowest element type that can hold the value.** At $10^7$ elements and beyond it is
  the difference between cache-resident and not; `int8` when three outcomes is all you need.
- **In Python, remember the pointers.** A list of lists is a list of addresses — hoist the row out
  of the inner loop; reach for NumPy or `bytearray` when you want an array of *values*.
- **Size it to the input and allocate once**, inside the timed function; a bound computed from the
  argument (problem 7's `n · ln n`) beats a guessed constant.
- **Count the cost of clearing.** If the array is large and the live set is small, track what you
  dirtied and clean only that.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0083](/solutions/0083/) — Path Sum: Four Ways
- ● [0109](/solutions/0109/) — Darts
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0504](/solutions/0504/) — Square on the Inside

<!-- /problems -->
