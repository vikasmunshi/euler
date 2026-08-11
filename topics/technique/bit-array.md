<!-- tags: [bit-array] -->
<!-- status: final -->
# Bit array

A [bit array](https://en.wikipedia.org/wiki/Bit_array) stores one boolean per *bit* — a set of
integers held as the bit pattern of a machine word, or of a run of them. It recurs across the
problems below for two quite different reasons, and only one of them is memory. The other is that a
single 64-bit `|` unions sixty-four elements at once, which is a change of algorithm, not a change of
footprint.

## The idea

Every flag array sits somewhere on a density spectrum:

| container | bytes per flag | test costs |
| --- | --- | --- |
| `list` of `bool` | 8 (pointer) + the object | a dereference |
| [`bytearray`](/topics/technique/bytearray) / `char *` / NumPy `bool` | 1 | a load |
| packed bit array | 1/8 | a load, a shift, a mask |

Moving right is 8× denser each step and slightly more expensive per *individual* access. That trade
only pays when the array outgrows cache, so density alone is a weak argument. The strong argument is
that once flags share a word, the CPU's [bitwise operators](/topics/technique/bitwise-operation)
become set operators over 64 elements per instruction: `|` is union, `&` is intersection, `& ~` is
difference, `<<` translates the whole set by a constant, and `.bit_count()` (the
[Hamming weight](/topics/technique/hamming-weight)) is its cardinality.

**In Python you do not write the bitset.** `int` is already an arbitrary-precision one:
`<<`, `>>`, `|`, `&`, `~`, `^`, `.bit_count()`, `.bit_length()`, and `x & -x` to isolate the lowest
set bit. There is no packing code, no word indexing, and no bug in the word indexing. The canonical
use is subset-sum, where the entire reachability table is one integer:

```python
reach = 1                    # bit s set <=> some subset sums to s
for v in elements:
    reach |= reach << v      # shift-or: every old sum, plus every old sum + v
```

Problem 201 is that idea taken one step further. Counting subsets is out of reach, but
*distinguishing "reachable once" from "reachable more than once"* is not: carry a second bitset
alongside the first, set a bit in it exactly where a shifted branch overlaps what was already
reachable, and the sums hit by a unique subset are what survives `reach & ~twice`. The
[knapsack](/topics/technique/knapsack-problem) recurrence over subset sizes then runs entirely in
big-integer word operations.

The comparison with its C sibling is the interesting part. Both solve the same recurrence over the
same bitsets; the C version hand-writes the shift as a loop splicing each `uint64_t` across the word
boundary, and takes `0.049 s` against the Python's `0.028 s`. CPython's big-integer shift is a tuned
C loop over a contiguous digit array, so the Python code buys a well-optimised implementation of the
inner loop for free, while the C code pays for a naive one. A bitset is one of the few places where
the interpreter is not the bottleneck ([algorithm beats
language](/topics/takeaway/algorithm-beats-language)).

## Rotation, and the shape of a periodic set

When the index axis is periodic, the bitset should rotate rather than shift. Problem 238 works over
a purely periodic digit stream: the set of achievable prefix sums repeats with the period's digit
sum $T$, so every start position is the same set of $T$ bits, rotated. In Python that is an
expression:

```python
mask = (1 << total) - 1
rotated = ((bits >> r) | (bits << (total - r))) & mask
```

Two shifts, an or, and a mask — $O(T/64)$ words per start position, against $O(T)$ for anything
element-wise. The remaining residues are then `uncovered &= mask ^ rotated`, and how many are left
is `uncovered.bit_count()`. The C sibling reaches the same place differently: it stores the period
*twice* end to end, so a rotation by $r < T$ is a plain 64-bit window read at offset $r$ with no
wrap-around splice at all. Python's integers are rigid, so you spell the rotation; C's memory is
yours, so you can spend a factor of two in space to make the rotation disappear.

## Where it is C's answer to a Python built-in

A technique tag attaches to a solution *index*, and an index spans both languages — which is why
several problems here carry `bit-array` with no bit array in the Python file. Reading the pair side
by side is the point:

- **Problem 143** collects distinct triangle perimeters. Python uses a `set` of integers; C, knowing
  every perimeter lies in $[0, L]$, uses `sums_bits[s / 64] |= 1ULL << (s % 64)` over a `calloc`'d
  array of words. Same set, no hashing, no allocation per insert — because the key space is dense
  and bounded, which is exactly the condition under which a bit array replaces a
  [hash table](/topics/technique/hash-table).
- **Problem 772** sieves primes up to $k$. Python calls out to `primesieve`; C hand-rolls a
  bit-packed [sieve](/topics/technique/sieve-of-eratosthenes) behind two macros,
  `((comp[(n) >> 6] >> ((n) & 63)) & 1ULL)` to test and `comp[(n) >> 6] |= 1ULL << ((n) & 63)` to
  set — one bit per number, about $k/8$ bytes.

The other direction is just as instructive. Problems 35, 50 and 196 all keep one *byte* (or one
NumPy `bool`) per flag rather than one bit, in both languages. That is the right call whenever the
array fits comfortably in memory: packing costs interpreted shifting in Python, and in C it costs
three instructions per access to save space you were not short of.

## How to reason about it

- **Density is the lesser prize.** Reach for a bit array when you want to operate on *many flags at
  once* — union two candidate sets, translate a whole reachability set, count survivors — not merely
  to shrink an array you can already afford.
- **In Python, `int` is the bitset.** Never hand-pack into a `bytearray`; you would be writing in
  Python the loop CPython already runs in C.
- **Know the big-integer cost model.** Every operation is $O(W)$ in words *and allocates a new
  object*: `reach |= reach << v` copies the whole bitset twice. That is cheap when $W$ is small and
  the loop is short, and ruinous when a per-element loop touches a huge bitset once per element. A
  `bytearray` with strided [slice assignment](/topics/technique/extended-slice) is the better shape
  when the updates are regular strides rather than data-dependent shifts.
- **Extraction is where the loop comes back.** Reading the answer out of a bitset is one iteration
  per set bit: `low = x & -x; pos = low.bit_length() - 1; x ^= low` in Python
  ([find first set](/topics/technique/find-first-set)), `__builtin_ctzll` plus `bits &= bits - 1` in
  C. Design so that the set bits at the end are few.
- **One bit means one bit.** The moment a slot needs a count, a distance, or a parent pointer, this
  is the wrong container — go back to a [`bytearray`](/topics/technique/bytearray), an
  [`array`](/topics/technique/array), or [NumPy](/topics/technique/numpy).
- **In C, hide the index arithmetic behind macros.** `n >> 6` and `n & 63` written inline at six call
  sites is six chances to write `n & 64`, and the resulting bug is silent: a flag set on the wrong
  neighbour, an answer slightly wrong, no crash. Both C solutions above define `IS_*` / `SET_*` and
  never index the words directly.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0035](/solutions/0035/) — Circular Primes
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions

<!-- /problems -->
