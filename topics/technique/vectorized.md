<!-- tags: [vectorized] -->
<!-- status: final 2026-11-04T03:42Z -->
# Vectorized computation

Python's per-operation overhead is the tax that decides most of these problems. An
interpreted loop that touches a hundred million integers is hopeless; the *same* arithmetic
expressed as a handful of whole-array operations, each dispatched once into compiled code,
finishes in seconds. [Vectorization](https://numpy.org/doc/stable/glossary.html#term-vectorization)
is the discipline of restating a computation so the loop lives in C instead of in the
interpreter — and the thinking it forces (what is the array, what is the index, what is the
mask) is usually clarifying in its own right.

## The idea

A [NumPy](https://numpy.org/doc/stable/) array is a flat, typed block of memory. Every
operation on it — `a + b`, `a > 3`, `a[::k] += 1` — is a
[ufunc](https://numpy.org/doc/stable/reference/ufuncs.html) that loops over that block in
compiled code, paying the interpreter's dispatch cost **once for the whole array** rather than
once per element. That single fact is the whole technique. A Python `for` over ten million
values costs ten million bytecode dispatches, ten million boxed integers, ten million
reference-count updates. The array form costs one dispatch and a tight machine loop over
contiguous memory that the CPU can prefetch and often auto-vectorize into SIMD instructions.
The asymptotic complexity is identical; the constant factor is one to two orders of magnitude.

The technique is therefore not an algorithm but a *rewrite*: take the loop you would naturally
write, and find the array expression that performs the same work in bulk.

**Strided slices are sieves.** The canonical move is `array[start::step] op= value`, which
touches every `step`-th element in one call. [Problem 23](/solutions/0023/) builds a
divisor-sum table this way — the outer loop runs over divisors (a few tens of thousands of
iterations), and each iteration credits *all* of that divisor's multiples at once:

```python
div_sums = np.zeros(limit + 1, dtype=int)
for i in range(1, limit // 2 + 1):
    div_sums[2 * i: limit + 1: i] += i
abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))
```

[Problem 179](/solutions/0179/) sieves the divisor *count* with the same shape, but pairs
divisors so the interpreter loop runs only `√N` times instead of `N` times; the arithmetic
still costs `O(N log √N)`, but almost none of it is interpreted.
A strided slice is also a *view*, so it can be written through: [problem 407](/solutions/0407/)
takes `best[s*(s+1)::s]` — every multiple of the small factor `s` — and folds a whole array of
candidates into it with `np.maximum(view, candidates, out=view)`, one call per `s`.
[Problem 675](/solutions/0675/) runs one strided pass per small prime, building that prime's
valuations at its multiples with nested slices for `p²`, `p³`, … and then a `cumsum` that
turns them into the prime's exponent in every factorial at once; the many large primes, which
each have valuation 1 at every multiple, are batched *across* primes by multiple index instead,
so the Python loop runs a few hundred times rather than once per prime.
[Problem 625](/solutions/0625/) sidesteps the large primes entirely. It sieves Euler's totient
with primes up to `√N` only, and alongside `phi` keeps a `rest` array from which strided slices
divide out each small prime's powers. Whatever survives in `rest` is `1` or the one prime factor
above `√N`, so a single masked statement, `phi[big] -= phi[big] // rest[big]`, applies every
large prime at once.
[Problem 668](/solutions/0668/)'s
[Lucy_Hedgehog prime count](https://en.wikipedia.org/wiki/Prime-counting_function#Algorithms_for_evaluating_%CF%80(x))
is the same shape on the `√N` table of `π(N // k)`: each sieving prime updates the whole
table in two slice expressions. [Problem 521](/solutions/0521/) runs it with a second table of
prime *sums* beside the counts, and shows where the update reads from. For `i·p ≤ √N` the
value `⌊N/(ip)⌋` sits in the large table at index `i·p`, which is a strided slice
`large[p::p]`. For larger `i` it lands in the small table at a computed index, so those
entries are gathered with fancy indexing. One split point decides which form handles each
entry.

**Flatten ragged work.** A strided slice costs one Python call per progression, which is a
bargain only while each progression is long. A
[polynomial sieve](/topics/technique/polynomial-sieve) breaks that assumption: a prime divides a
quadratic's values on at most two residue classes, the classes start at arbitrary roots, and
hundreds of thousands of large primes have only a handful of hits each.
[Problem 291](/solutions/0291/) keeps slices for primes up to `N/64` and splits the rest into
octave bands `[lo, 2·lo)`. Every prime in a band has about the same number of hits, so the loop
turns inside out: it runs over the hit number `k`, and `start + k * q` strikes the `k`-th hit of
every prime in the band at once. [Problem 621](/solutions/0621/) drops that loop too. Given
progressions of unequal lengths `counts`, three lines write them all out as one flat array:

```python
offsets = np.cumsum(counts) - counts                          # where each run begins
steps = np.arange(counts.sum()) - np.repeat(offsets, counts)  # 0, 1, 2, 0, 1, 0, 1, 2, 3, …
index = np.repeat(starts, counts) + np.repeat(moduli, counts) * steps
```

`np.repeat` copies each run's parameters onto its lanes, and subtracting the repeated offsets
numbers the lanes within their run. That is the general way to make ragged work rectangular,
and it brings two obligations. The flat array is as long as the total work, so batches must be
cut by work, not by item count: problem 621 runs `searchsorted` over the cumulative hit counts
to take progressions about four million hits at a time. And two primes in a batch can strike
the same index, so the updates go through `np.floor_divide.at` and `np.multiply.at`, the
unbuffered scatter that problem 967 uses below. The same idiom also enumerates.
[Problem 749](/solutions/0749/) builds every digit multiset as a row of digit counts, one digit
per step. A partial row with `r` digits left has `r + 1` children, so
`np.repeat(rows, choices, axis=0)` copies the parents and the lane numbering supplies each
child's count. Nine array steps walk a tree with two million leaves, level by level, with no
recursion.

**Invert the loop nest.** When you have nested loops, vectorize the *inner* one and leave the
outer in Python. This is the single most common shape across these problems, because it needs
no cleverness: whichever loop runs more often becomes the array axis. Problem 23 marks every
pairwise sum of abundant numbers by adding one abundant number to the whole remaining slice;
[problem 165](/solutions/0165/) tests one line segment against all later segments in a single
pass of cross-product arithmetic; [problem 757](/solutions/0757/) enumerates one factor in
Python and sweeps the co-factor as an `int64` array; [problem 257](/solutions/0257/) loops
over a denominator `q` and sweeps every numerator `p` at once, filtering to coprime pairs with
`np.gcd` and summing the floor divisions `limit // span` in one reduction. The Python loop
survives — it just runs `√N` times instead of `N` times, and that is enough. The outer loop
need not even be a loop: [problem 983](/solutions/0983/) runs a
[depth-first search](/topics/technique/depth-first-search) in plain Python, but each node
carries the array of every signed subset sum chosen so far, so the test that decides whether
to descend is a handful of array operations over all of them. When you want to erase *both* levels,
[broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) does it: an
`(m, 1)` column against a `(1, n)` row produces the full `m × n` grid of combinations in one
expression, at the price of materialising it. The two styles combine: [problem 518](/solutions/0518/)
keeps a Python loop over the ratio's denominator `q` and builds, for each `q`, a small
`np.outer` grid of multipliers `k` against coprime numerators `p`. It masks the grid through a
primality table, and `np.nonzero` on the 2-D mask returns the `(row, col)` coordinates of every
hit, which recover exactly which `(k, p)` pairs to sum.

**Masks replace `if`.** A comparison yields a boolean array, and boolean arrays index, count,
and combine. `mask = n <= limit` then `n[mask]` is the vectorized `if`;
[`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html)
turns a predicate into the indices satisfying it, and `count_nonzero` turns it into a tally.
This is what lets a filter-heavy computation stay in array form: you do not skip the failing
elements, you compute them and discard them — cheaper than branching per element, provided the
discarded work is cheap. When the filter has several stages, compact between them rather than
`&`-ing the masks together: [problem 348](/solutions/0348/) tests palindromes one digit pair at
a time, outermost first, and keeps only the survivors after each comparison, so every pass runs
on roughly a tenth of the previous array and the whole filter costs little more than its first
pass — [cheap checks first](/topics/takeaway/cheap-checks-first), in array form.

**Tables replace functions.** When a per-element function depends on only a small piece of
its input, compute it once in plain Python for every value of that piece and let
[fancy indexing](https://numpy.org/doc/stable/user/basics.indexing.html#advanced-indexing)
apply it. [Problem 274](/solutions/0274/) needs a branch on each prime's last digit; a
ten-entry array indexed by `primes % 10` *is* that branch, for all primes at once.
[Problem 315](/solutions/0315/) pushes it further: everything it needs about a prime below
`10**10` reduces to its last two digits and its digit sum (which is under 100), so a
`100 × 100` table built with ordinary loops is indexed as `first[p % 100, s]` across every
sieved prime. The digit sums themselves come from the bounded-iteration shape below — one
`np.divmod(rem, 10)` per digit position, ten array steps instead of a Python loop per prime.
The slow, readable code runs over the tiny domain; only the indexing touches the big one.

**Linear maps are matrix products.** When the per-element function is *linear* in some small
vector the element carries, a weight vector computes it and a weight *matrix* computes many
variants at once. [Problem 637](/solutions/0637/) needs every way of putting plus signs between
a number's digits. Each placement gives every digit a weight, a power of the base counted from
the end of its block, so that placement's sum is `digits · w`. Stack every placement's `w` as a
column and `digits @ W` returns every split sum of every number in one matrix product. The same
problem shows the companion trick for sets: a boolean row of width `64k` packed with
[`np.packbits`](https://numpy.org/doc/stable/reference/generated/numpy.packbits.html) and
viewed as `uint64` is `k` machine words. "Do these two sets meet?" then becomes `(a & b).any()`,
which runs 64 membership tests per operation, and a broadcast over a block of rows answers it
for a whole grid of pairs.

**Batch the lookups.**
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
does a whole vector of binary searches in one call, which quietly converts "for each `x`, look
`x` up in a sorted table" into a single operation. [Problem 187](/solutions/0187/) counts
semiprimes by turning the prime-counting function `π` into two array lookups over a sorted
prime array; [problem 461](/solutions/0461/) uses it as the join step of a
[meet-in-the-middle](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) search, locating
the nearest partner for every candidate at once. The lookup can also choose *which formula* a
lane evaluates. [Problem 341](/solutions/0341/) builds a few tens of thousands of block tables
serially, in exact Python integers, then answers a million queries without returning to Python:
one `searchsorted` finds each query's block, fancy indexing gathers that block's coefficients,
and every lane solves its own quadratic — a float `sqrt` for the guess, two masked integer
nudges to make it exact. The serial work runs over the small table, the bulk work over the
queries. Sorting once and searching in bulk is often
faster than a dictionary, because the search never leaves compiled code. The same holds for
the other dictionary and set idioms: `np.unique(values, return_counts=True)` is a bulk
`Counter` (problem 348 tallies how many square-plus-cube representations each palindrome has
with it), and [`np.isin`](https://numpy.org/doc/stable/reference/generated/numpy.isin.html)
is bulk set membership. Both want flat scalar keys, so when the items are tuples, pack them:
problem 983 stores each lattice vector `(x, y)` as the single integer `x * 2**21 + y`. The
encoding is *linear*, so adding two vectors is adding their keys, and the whole search runs on
one-dimensional `int64` arrays. A key can also forget order on purpose. Problem 749 compares
digit multisets, so its key is the count vector read as a base-`(d + 1)` numeral: `counts @ weight`
for the rows, and for a candidate number one `weight[digit]` gather per digit position, summed.
Addition discards the order of the digits, so one integer comparison per lane decides whether
two numbers are anagrams.

Sorting and searching in bulk also builds graphs. [Problem 425](/solutions/0425/) links primes
that differ in one digit. Its edge list comes from array passes: one per digit position and
decrement, masked by a prime lookup. A stable `argsort` by endpoint and two `searchsorted`
calls then give each vertex its slice of the edge array, which is a
[CSR](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format))
adjacency built without a Python loop over vertices. `np.cumsum(is_prime) - 1` provides the
inverse map from a prime's value to its index. The union-find that follows is genuinely serial
and stays in Python, but it only walks slices the arrays have already prepared.
[Problem 705](/solutions/0705/) uses the same grouping to count *ordered pairs*. Its input, the
digits of every prime below `N` written end to end, is ragged; laying it out as a fixed-width
`primes × width` digit table makes it rectangular, and since the problem drops zero digits
anyway, one mask on the flattened table removes the padding with them. Then, for each digit
`x`, `np.cumsum(digits == x)` counts the `x`s before every position; gathered through a stable
`argsort` by digit, each digit `y`'s slice sums to how many `x`s precede a `y`. Nine
[prefix sums](/topics/technique/prefix-sum) build the whole 9 × 9 table of ordered pairs, with
no pass over the pairs themselves.

The bulk forms of "group by" and "for each subset" are just as short.
[Problem 967](/solutions/0967/) needs every squarefree product of the large primes below a
bound. It grows that set one prime at a time: `ds = np.concatenate((ds, ds[keep] * p))`
appends every product that still fits, so the Python loop runs once per prime, not once per
product. Each product carries a class label, and
[`np.add.at`](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.at.html)`(acc, cls, values)`
sums the values class by class in one unbuffered scatter. A plain `acc[cls] += values` would
keep only one write per repeated index. The same problem turns a *periodic* function into a
table: its small-prime part repeats with period `Q`, a product of a few primes, so it is
tabulated once over `[0, Q)` with prefix sums. Then `np.divmod(n // ds, Q)` splits every
query into whole periods and a remainder, which costs one multiply and one lookup per lane.

**Advance the whole ensemble.** When many independent processes share one update rule, make
the process an *axis* and step them in lockstep. [Problem 213](/solutions/0213/) tracks the
probability distribution of every flea on the board simultaneously — one ring of the simulation
is four shifted, boundary-clipped array additions over a `(fleas, n, n)` grid, so the entire
board advances in a constant number of NumPy calls per step. [Problem 149](/solutions/0149/)
runs [Kadane's algorithm](https://en.wikipedia.org/wiki/Maximum_subarray_problem) down every
row of a grid at once: one vector update per column, all rows in parallel. A dynamic program
whose states at step `k` depend only on step `k-1` is exactly this shape — the DP table row
becomes the array, and the recurrence becomes one array expression per step. The axis need not
be space or time. [Problem 400](/solutions/0400/) runs its DP over *Grundy values*: each level of
the game tree holds a weight vector indexed by the value a move must reach. XOR with a constant
permutes `[0, 2**b)`, so pushing a whole level down to a child is a single scatter through the
index array `(idx ^ mask) - 1`.

The state can be two-dimensional as well. [Problem 475](/solutions/0475/) reduces to counting
0/1 matrices row by row, and all that matters is how many columns already hold two ones and how
many hold three; the rest follows from the row number. So the state is a 2-D table, and an
`arange` column against an `arange` row gives every state's coordinates by broadcasting. Each of
the 15 ways a new row can spread over the columns moves the whole table by a fixed offset: one
shifted slice, scaled by a weight array gathered from a binomial table at those coordinates.
Unreachable states have impossible coordinates, some of them negative, so `np.clip` forces them
into range before the gather. The nonsense weight fetched for such a state is multiplied by a
table entry of zero. When the lanes a clamp corrupts are already dead, it does the work of a
mask for less.

A recurrence that looks serial along its own index can still be stepped in blocks, if every
entry depends only on entries well below it. [Problem 333](/solutions/0333/) counts partitions
into terms `2^i·3^j`. Its recurrence sends `n` to indices below `n/2`, so the whole block
`[2^k, 2^{k+1})` depends only on blocks already filled, and the table fills in `log₂ N` vector
steps instead of `N` scalar ones. The block boundaries come from the dependency structure, not
from the index order. The ensemble can also shrink as it runs. [Problem 437](/solutions/0437/)
keeps one lane per candidate prime and folds in the prime factors of `p − 1` one at a time.
Each fold settles some lanes for good, and those lanes are dropped: one `keep` mask compacts
the candidate array *and* every per-lane state array alongside it. Later factors then work on
a shrinking array, as in problem 348's staged filter, except that here the survivors carry
state from step to step. When each lane's lifetime is known in advance, even the mask can go.
Problem 749 sorts its rows once by the last exponent each can use, so the rows still alive at
exponent `k` are always a prefix, and `counts[:live]` is a free view where a mask would copy two
million rows.

**Vectorize the modular arithmetic too.** Nothing about the technique is limited to `+` and
`*`. [Problem 944](/solutions/0944/) computes `2**e mod m` for a whole array of exponents by
running [square-and-multiply](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) over
the exponent *bits*, masking the odd-bit lanes at each step — 64 array operations instead of a
per-element `pow`. The pattern generalises: any bounded, data-independent iteration can be
unrolled across the array, with a boolean mask selecting which lanes act.
[Problem 455](/solutions/0455/) gives every lane its own exponent and iterates a power tower
to its fixed point modulo `10**9`, for a million bases at once, stopping when
`np.array_equal` says no lane moved. [Problem 721](/solutions/0721/) lifts the same loop into
the ring `ℤ_p[√a]`: each element `u + v√a` is *two* arrays, the ring product is a few lines of
array arithmetic, and the square-and-multiply sweep raises every `c + √a` to its own power
`a²` in about 45 steps. When every lane shares the base and the exponents are bounded, the
ladder can be paid for in advance. [Problem 921](/solutions/0921/) raises one element of such a
ring to over a million unrelated exponents. It splits each exponent into its low 15 bits and the
rest, and tabulates the base's powers for each half, a few tens of thousands of serial
multiplications. Then `high[x >> 15] * low[x & 0x7fff]` is two gathers and one ring product per
lane, in place of about 29 squarings. Problem 980's power tables, below, use the same split to
produce a consecutive run of powers; here it gives random access to them.
The lanes need not share a modulus either.
[Problem 492](/solutions/0492/) gives every lane its own *prime* modulus, a whole sieved range of
them. Each lane's exponent is reduced modulo `p − 1` or `p + 1`, and a quadratic-residue mask
picks which, before a [Lucas-sequence](https://en.wikipedia.org/wiki/Lucas_sequence) ladder
runs on all of them. A ladder step has two branches depending on the exponent bit. The array
form computes both candidate pairs for every lane and keeps one with `np.where(bit, …)`, so
the branch becomes a select. The other modular staple vectorizes as well: problem 675 gets the
[Fermat inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Using_Euler's_theorem)
of every odd number up to `2n + 1` from one array-wide `pow(·, p − 2)`, and problem 407 builds
a table of inverses modulo `s` the same way with exponent `φ(s) − 1`, then applies it with
fancy indexing as `inv[large % s]` — a lookup table, as above.

## How to reason about it

- **Vectorize the loop the input size drives, not every loop.** The win comes from the loop
  that runs millions of times; a surrounding loop of a few thousand iterations can stay plain
  Python and cost nothing measurable. Chasing the outer loop into array form usually buys
  little and costs a lot of readability. This is
  [match the abstraction to the hot path](/topics/takeaway/right-tool-per-cost) applied to
  arithmetic.
- **Watch the dtype.** NumPy integers are fixed-width machine words, not Python's
  [arbitrary-precision integers](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic),
  and `int64` overflow wraps **silently** — no exception, just a wrong answer. Before writing a
  product into an array, bound it: keep every intermediate under `2**63`, reduce modulo `m`
  before multiplying when `m*m` fits, and say so in a comment. See
  [watch integer width](/topics/takeaway/watch-integer-width). Better still, put the bound in
  code: problem 348 scans palindromes by digit count and raises `OverflowError` past 18
  digits, the last length whose sums still fit, instead of letting a 19th band wrap silently.
  Packed keys need the same accounting, since each field must fit its share of the 64 bits,
  sums included. An entry that would overflow can be dropped if no live lane reads it: problem
  749's table of digit powers zeroes every power above the limit, because a digit with such a
  power cannot appear in a row still alive at that exponent. Masks help with the accounting too.
  [Problem 401](/solutions/0401/) needs
  `x(x+1)(2x+1)/6 mod m` for `x` up to `10**15`, where the raw product would overflow and `6`
  has no inverse modulo the composite `m`. So it divides the `2` and the `3` out of whichever factor
  they divide, using masks such as `a[x % 3 == 0] //= 3`, and reduces only after that.
  Choosing the *smallest*
  sufficient dtype is also a speed decision: an `int8` Möbius table
  ([problem 193](/solutions/0193/)) is eight times more cache-friendly than `int64`, and
  bandwidth is what these loops are limited by. Sometimes the question itself makes the small
  dtype possible. Problem 333 only asks whether a count is *exactly one*, so it clamps every
  count at 2 with `np.minimum(acc, 2, out=acc)`. The partition counts, which would grow without
  bound, fit in a `uint8` table. Overflow can even be harmless if it is planned for. Arithmetic on
  `int64` is exact modulo `2**64`, so when the *final* value is known to fit, intermediate
  wraparound cancels out. [Problem 558](/solutions/0558/) depends on this in its fixed-point
  evaluation.
- **Memory is the real ceiling, and chunking is the fix.** Vectorization trades memory for
  speed: materialising an intermediate of `N` elements needs `N` elements of RAM, and the
  natural array form of an `O(N)` sum can be an `O(N)` allocation. Sweep the range in
  cache-sized blocks instead — problems 193 and 210 both accumulate over chunks of about four
  million entries, which keeps the working set inside cache *and* bounds memory. Chunking costs
  one extra loop level and usually makes the code faster, not just smaller.
- **Serial dependence is the real obstacle — and often only apparent.** If element `k` cannot
  be computed without element `k-1`, there is nothing to batch, and a genuinely serial scan
  (problem 165's [Blum Blum Shub](https://en.wikipedia.org/wiki/Blum_Blum_Shub) stream) stays a
  Python loop. But look for slack before conceding: problem 149's
  [lagged Fibonacci](https://en.wikipedia.org/wiki/Lagged_Fibonacci_generator) generator has a
  smallest lag of 24, so 24 terms can be produced per vectorized step without the output
  aliasing its own input. If the recurrence is a running sum, minimum or maximum, it is a
  [scan](/topics/technique/prefix-maximum-scan), and `np.add.accumulate` /
  `np.maximum.accumulate` compute it in compiled code — along any axis, so every row of a
  matrix gets its own scan in one call. [Problem 252](/solutions/0252/) uses this to test
  whole rows of fan triangles for emptiness: a triangle is empty exactly when one direction
  rank is a running maximum of the ranks before it, so one prefix scan per row replaces a
  scan over every third point. Even a sliding window reduces to scans. The textbook window
  maximum keeps a monotonic deque, as serial as code gets, but
  [problem 485](/solutions/0485/) uses the
  [van Herk–Gil-Werman](/topics/technique/sliding-window-maximum) decomposition instead. It
  reshapes the array into aligned blocks of the window length `k` and scans each row twice,
  forwards for prefix maxima and over `grid[:, ::-1]` for suffix maxima. Every window spans at
  most two blocks, so its maximum is `max(suffix[n], prefix[n + k - 1])`, and one more
  `np.maximum` over two shifted arrays answers all the windows at once.
  A recurrence that is only *almost* a scan can often be
  shifted into one. [Problem 718](/solutions/0718/) walks a residue cycle on which
  `w_i = min(base_i, w_{i−1} + z)`; subtracting `i·z` from both sides gives
  `t_i = min(base_i − i·z, t_{i−1})`, a plain running minimum that `np.minimum.accumulate`
  computes chunk by chunk, carrying the last value into the next chunk. Better still, look for
  a closed form. A
  [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator)
  looks hopelessly sequential, yet its `k`-th term is `a**k` times the seed, so
  [problem 980](/solutions/0980/) generates its stream in bulk with a baby-step/giant-step
  outer product of power tables — the serial recurrence becomes one broadcast multiply.
  Whenever the recurrence is linear, the dependence chain can usually be broken.
  A scan NumPy cannot run directly can still be split. A *modular* prefix product has no
  ufunc (`np.multiply.accumulate` would overflow long before it reduced), so
  [problem 739](/solutions/0739/) reshapes each chunk into a `rows × cols` grid, scans it one
  column at a time across all rows, then multiplies each row by the carried product of the rows
  before it. That costs about `2√chunk` Python steps per chunk instead of one per element; a
  plain product is a pairwise tree, `a[0::2] * a[1::2] % m`, halving each step. Once the scan
  exists it yields more than factorials. [Problem 423](/solutions/0423/) gets a power table as
  the prefix product of a constant array, and every inverse factorial from a *single* modular
  inverse: the prefix product of the descending sequence `top, top − 1, …`, reversed, is
  `top! / i!`, so one multiply by `1 / top!` turns it into every `1 / i!`. That is one scalar
  `pow`, against problem 675's array-wide one. Two refinements
  extend the split scan. When only *some* prefixes are needed, the full scan never has to be
  stored. [Problem 635](/solutions/0635/) wants factorials at a scattered set of points, so it
  sorts them, runs the chunked scan, and in each chunk gathers just the queries that fall inside
  it (`grid[off % rows, block] * carry[block]`) before moving on. When the product runs over a
  *masked* subset, substitute the identity rather than compacting: `np.where(mask, d, 1)` turns a
  product over the selected elements into a product over all of them, which the same scan
  handles. [Problem 754](/solutions/0754/) does this twice per sieve segment, once for `μ = +1`
  and once for `μ = −1`, threading three carries (two products and a running sum) across
  segments.
- **`np.vectorize` is not vectorization.** It is a convenience wrapper that calls your Python
  function once per element — the documentation says as much. It buys broadcasting semantics,
  not speed. [Problem 56](/solutions/0056/) uses it only inside a diagnostic path, which is the
  right place for it.
- **Floating point buys speed and costs exactness.** Array arithmetic in `float64` is fast, but
  equality and near-misses become delicate: problem 461 uses
  [`expm1`](https://numpy.org/doc/stable/reference/generated/numpy.expm1.html) to avoid
  catastrophic cancellation and widens its search with an epsilon before deciding. Floats and
  integers can also split the work. Problem 252 sorts direction vectors with `np.arctan2`,
  but decides which directions are *equal* by comparing the integer vectors reduced by
  `np.gcd`, so the float only ever has to order directions that it can safely tell apart.
  [Problem 641](/solutions/0641/) uses the same split for roots: `np.cbrt` makes a guess for
  every `⌊∛x⌋` at once, and two masked integer corrections (`cs -= cs**3 > x`,
  `cs += (cs+1)**3 <= x`) make each one exact.
  When an approximate test is fast but occasionally wrong, *certify* it rather than abandoning
  it. Problem 558 expands every square greedily in an irrational base. The remainder is held
  exactly as three integer coefficients over `(1, r, r²)`, and each digit decision is made by a
  fixed-point evaluation in every lane at once. Beside it, a rounding-error bound is computed
  from the largest coefficients. Lanes whose value clears the bound are decided. The few inside
  the bound fall back to an exact test in Python integers (the sign of a field norm), and the
  exact zeros among them are settled in bulk first. The array pass decides nearly every lane,
  and Python only handles the ones near the boundary.
  When the answer depends on exact equality, keep integers — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
- **In C, this problem does not exist.** Every one of these solutions has a C counterpart that
  simply writes the nested loops, because a compiled loop already has no interpreter tax and
  the compiler auto-vectorizes what it can. That is the honest framing: vectorization is how
  Python reaches the performance C gets for free, and comparing the two versions of the same
  problem — problems 187, 213 and 501 all have both — is the clearest way to see exactly what
  the interpreter was costing.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0135](/solutions/0135/) — Same Differences
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0304](/solutions/0304/) — Primonacci
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0333](/solutions/0333/) — Special Partitions
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0407](/solutions/0407/) — Idempotents
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0425](/solutions/0425/) — Prime Connection
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0475](/solutions/0475/) — Music Festival
- ● [0478](/solutions/0478/) — Mixtures
- ● [0485](/solutions/0485/) — Maximum Number of Divisors
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ● [0558](/solutions/0558/) — Irrational Base
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0632](/solutions/0632/) — Square Prime Factors
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0688](/solutions/0688/) — Piles of Plates
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0749](/solutions/0749/) — Near Power Sums
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ● [0921](/solutions/0921/) — Golden Recurrence
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
