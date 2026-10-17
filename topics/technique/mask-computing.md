<!-- tags: [mask-computing] -->
<!-- status: final -->
# Mask (computing)

A [mask](https://en.wikipedia.org/wiki/Mask_(computing)) is an integer whose bits are read as a row
of independent yes/no flags, and *masking* is the handful of operations that set, clear, flip or
test those flags in one instruction. The operations themselves are covered on
[bitwise operation](/topics/technique/bitwise-operation) and
[bit manipulation](/topics/technique/bit-manipulation); this page is about the other half of the
idea — **deciding what each bit means**. In every problem below the mask is the state of a search or
a dynamic programme, and the choice of what to put in it is the whole design: it fixes how many
states there are, whether they can be stored in a flat array, and whether the transitions are a
single `|` or `^`.

## The idea

Four operations do all the work, and every solution here uses some of them:

```python
m | (1 << i)        # set flag i          (C: m | (1u << i))
m & ~(1 << i)       # clear flag i
m ^ (1 << i)        # toggle flag i
m >> i & 1          # test flag i         (or: m & (1 << i), nonzero when set)
m & ((1 << k) - 1)  # keep only the low k flags — the mask in the original sense
```

That last line is where the name comes from: `(1 << k) - 1` is a run of $k$ ones, and AND-ing with
it lets the low $k$ bits through and blocks the rest, like a stencil. The other lines generalise it
to one bit at a time.

What makes masks worth reaching for is that a set of $n$ flags *is* an integer in $[0, 2^n)$. That
integer can index an array directly, be compared and hashed in one step, and be iterated in numeric
order — and numeric order is often exactly the topological order a DP needs. The problems split
cleanly by what the flags record.

**A subset of things.** Problem 105 tests whether a set of up to twelve numbers is a "special sum
set", which means checking every pair of disjoint subsets. Each subset is a 12-bit mask, and the
subsets disjoint from `B` are exactly the submasks of its complement, `full ^ B`. Walking those with
`c = (c - 1) & comp` visits each element in one of three buckets (in `B`, in `C`, in neither), so
the scan costs $3^n$ pairs rather than $4^n$. Problem 345, the maximum-weight
[assignment](/topics/domain/assignment-problem) over a $15 \times 15$ matrix, records the set of
*columns already used*. The order they were used in does not matter, and dropping it is what turns
$15!$ permutations into $2^{15}$ states. The mask even encodes the row for free: if $k$ columns are
taken, rows $0..k-1$ are placed, so the next row is the
[popcount](/topics/technique/hamming-weight) of the mask.

**A window of occupancy.** Problem 161 counts triomino tilings of a grid with a
[broken-profile](/topics/domain/broken-profile) DP. There, bit $i$ means "the cell $i$ places ahead
of the scan position is already covered". Placing a piece ORs in its cells. Advancing one cell is
`mask >> 1`, which drops the cell just passed and realigns everything else. The mask has to be as
wide as the farthest cell a piece can reach, so the solution scans along the shorter side to keep
that width small.

**A vector of saturating counters.** Problem 679 counts words over a four-letter alphabet that
contain each of four keywords *exactly* once, running a DP over the states of an
[Aho–Corasick](/topics/technique/aho-corasick-algorithm) automaton. Two masks meet here. Each
automaton node carries an output mask of the keywords that end there, merged along failure links
with `|=`. The DP state carries a 4-bit "seen once" mask. On each transition, a keyword in the
output whose bit is already set in the state means a second occurrence, and that branch dies, so
the counter saturates at one and never needs a second bit. Accept at `0b1111`.

**A vector of parities.** Problem 974 asks for the $n$th number made of odd digits, divisible by 105,
with every odd digit appearing an odd number of times. "Odd number of times" is a parity, and a
parity is a bit that flips on each occurrence. Appending digit $i$ is `parity ^ (1 << i)`, and the
accept condition is the mask `0x1F`. Together with a residue mod 7 and a digit sum mod 3 that gives
$7 \cdot 3 \cdot 32 = 672$ states per length for a
[digit DP](/topics/technique/dynamic-programming) and its unranking walk. Problem 943 uses the same
XOR algebra one level up. A subtree of a Kolakoski-style derivation tree is fixed by its value, its
height $h$, and an $(h+1)$-bit mask of the position parities of its leftmost descendant on each
level. Bit $h$ (`mask >> h & 1`) picks the children's symbol. `mask & ((1 << h) - 1)` is the key
the children inherit. The next sibling's mask is this one XORed with the subtree's own node-count
parities. Because the masks repeat after a short prefix, a long run of identical siblings can be
compressed by cycle detection.

## How to reason about it

- **Put in the mask only what the future depends on.** The state count is $2^{\text{bits}}$ times
  whatever else you carry. Problem 345 forgets the column order, 161 forgets everything behind the
  frontier, 679 caps each count at one, and 974 keeps only parities. Each of these is a claim that
  the dropped information cannot change any later decision, and that claim is the correctness
  argument for the DP. Check it before you code.
- **Pick the operator that matches the flag's algebra.** Membership is set-once, so use `|`.
  Parity flips, so use `^`. A window slides, so use `>>`. Choose wrong and the mask stops meaning
  what you think: XOR-ing a membership bit turns a second occurrence into "absent".
- **Numeric order is often a free topological order.** Setting a bit only increases a mask, so in
  345 a plain `for mask in range(1 << n)` finalises every state before anything reads it. Problem
  105 builds every subset's sum with the same trick, `s[m] = s[m ^ low] + x[i]` where
  `low = m & -m`, because `m ^ low < m` is always filled already.
- **Mind the width.** Eight flags fit in a byte and 32 in an `unsigned`. Past 31, a C `1 << i`
  overflows a signed `int` and has to become `1ULL << i`. Python never overflows, but a mask
  wider than one internal 30-bit digit pays multi-digit arithmetic on every operation. That is one
  more reason to keep the state narrow.

## C and Python

The bit expressions are character-for-character identical in the two languages. What differs is
everything around them:

- **Storage.** A mask that indexes a dense range wants a flat array. The C ports of 105, 345 and
  974 `calloc` one, and 974 linearises a four-index table as
  `((r * 7 + m7) * 3 + m3) * 32 + parity`. Python gets the same effect from lists. Where only a
  sparse subset of masks is ever reached, Python's `functools.lru_cache` (161) or a dict keyed by
  `(c, h, mask)` (943) stores just the visited states. C has to choose. Problem 161 allocates the
  full `(cells + 1) × 2^width` table with a `-1` sentinel, trading memory for branch-free lookups.
  Problem 943 uses open-addressed hash tables stamped with a per-run generation counter so they never
  need clearing.
- **Bit queries.** Popcount and lowest-set-bit are `__builtin_popcount` / `__builtin_ctz` in C and
  `int.bit_count()` / `(m & -m).bit_length() - 1` in Python 3.10+. In C each builtin is
  typically a single instruction. In Python each is one call into C, which is still far cheaper
  than looping over the bits.
- **The values the masks index.** The mask stays small, but the counts stored against it may not.
  Problems 943 and 974 keep their counts in `__int128` in C, while Python's integers grow on
  their own.

Masks are one of several ways to give a DP a compact key. [Memoization](/topics/technique/memoization)
covers the cache side. [Subset-sum](/topics/domain/subset-sum-problem) is where 105's
subset-as-mask encoding comes from.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0161](/solutions/0161/) — Triominoes
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0679](/solutions/0679/) — Freefarea
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
