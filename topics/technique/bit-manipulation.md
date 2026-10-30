<!-- tags: [bit-manipulation] -->
<!-- status: final 2026-10-15T10:50Z -->
# Bit manipulation

[Bit manipulation](https://en.wikipedia.org/wiki/Bit_manipulation) is what you reach for when a
problem's state is small enough to live inside a single integer. An `int` stops being a number and
becomes a container — a set, a board, a window of history, a row of a grid — and the operations you
already have (`&`, `|`, `^`, `<<`, `>>`) become set intersection, union, symmetric difference, and
sliding. Nothing here is an optimisation trick bolted onto a finished program: in almost every
problem below, the bit representation *is* the algorithm, and the speed is a side effect of having
picked the right container.

## The idea

**A set of at most 64 things is one integer.** Bit $i$ set means element $i$ is in the set. Union
is `a | b`, intersection `a & b`, membership `mask >> i & 1`, adding an element `mask | 1 << i`,
removing one `mask &= ~(1 << i)`, and "are these two sets disjoint?" is `a & b == 0` — one
instruction, whatever the size. Once that identification is made, *enumerating all subsets* becomes
counting: `for mask in range(1 << n)`. Problem 152 walks the $2^n$ subsets of a candidate group of
denominators; problem 202 walks the subsets of a prime set for an
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) sum; problem 269 walks
subsets of a root set; problem 215 models each wall row as the mask of its internal brick
boundaries, so "no crack runs through" reduces to `a & b == 0` between adjacent rows.

**That identification is what makes bitmask dynamic programming possible.** If the DP state is "the
set of columns already used", then the state *is* an array index, and the whole
[DP table](/topics/technique/dynamic-programming) is a flat list of length $2^n$ rather than a
dictionary of frozensets. Problem 345's maximum-weight assignment is the canonical shape:

```python
dp = [-1] * (1 << n)                      # dp[mask]: best sum using exactly the columns in mask
for mask in range(1 << n):
    row = mask.bit_count()                # rows are assigned in order, so the row index is free
    for col in range(n):
        if not (mask >> col) & 1:
            dp[mask | 1 << col] = max(dp[mask | 1 << col], dp[mask] + matrix[row][col])
```

Two things are worth noticing beyond the speed. `mask.bit_count()` recovers the row index from the
state, so the DP needs no second dimension — the population count *is* the depth. And the
transition `mask | 1 << col` is guaranteed to be a larger integer than `mask`, so iterating masks in
numeric order is already a topological order of the state graph. Neither of those falls out of a
set-of-columns representation.

**A packed integer is a hash key that costs nothing to hash.** When several small fields make up a
state, shift them into disjoint bit ranges and the composite is an array index. Problem 244 encodes
a $4 \times 4$ slider board as `blank << 16 | red-cell-mask`, which lets the
[BFS](/topics/technique/breadth-first-search) hold its distance table in a flat `bytearray` of
$2^{20}$ entries instead of a dictionary keyed by strings — and a move becomes
`nxt = cell << CELLS | mask ^ swap`, where the XOR swaps the two involved cells in one operation.
The general rule: pack when the total width is small enough for a dense array, because a
[hash table](/topics/technique/hash-table) of tuples costs an allocation, a hash, and a pointer
chase per lookup, and a `bytearray` index costs none of the three.

**A packed integer can also be a vector you add.** If every field is wide enough to hold the
largest sum it will ever see, adding two packed integers adds every field at once, and no carry
crosses a field boundary. That is
[SWAR](https://en.wikipedia.org/wiki/SWAR) ("SIMD within a register") arithmetic. Problem 963
reduces each number to a game value with an integer part, a star, and a coefficient for each
$\uparrow^k$ (the "up" infinitesimals). It packs the coefficients into 5-bit fields above a
single star bit. Summing two values' infinitesimal parts is then one integer addition for the
coefficients and one XOR for the star: `((a >> 1) + (b >> 1)) << 1 | (a ^ b) & 1`. The packed
sum is also a dictionary key, so values with equal sums group together without building a
tuple. The width is the one thing to prove. The solution's comment says why five bits suffice:
a coefficient counts digits, and a pair sum is at most twice the digit count. Undersize the
field and the overflow lands silently in its neighbour.

**A bitset is a set of integers at one bit apiece.** Where the universe is millions of values but
membership is all you need, a word array holds it 64× denser than a byte array and 512× denser than
a list of Python ints — `bits[v >> 6] |= 1 << (v & 63)` sets, `bits[v >> 6] >> (v & 63) & 1` tests.
Problem 143 collects the distinct achievable totals this way, then sweeps the set with the two
idioms every bitset loop uses:

```c
while (w) {
    int bit = __builtin_ctzll(w);   /* index of the lowest set bit */
    total += i * 64 + bit;
    w &= w - 1;                     /* clear it, and only it */
}
```

`w & -w` isolates the lowest set bit, `w & (w - 1)` clears it, and the loop therefore runs once per
*set* bit rather than once per position. Problem 105 uses the same `mask & -mask` to build all
$2^n$ subset sums in $O(2^n)$ total: peel off the lowest element and add its value to the sum of the
rest, which is a smaller mask and so already computed.

**A shift register is a fixed window of history.** `state = (state << 1 | new_bit) & mask` keeps the
last $h$ bits of a binary sequence in one integer, dropping the oldest for free. Problem 167's Ulam
sequences hinge on a recurrence whose next bit is `(state >> (h - 1)) ^ (state & 1)`, so membership
of the whole sequence is generated by shifting an $h$-bit window — and since the state space is
finite, the sequence must eventually cycle, which is exactly the observation that lets a
$10^{11}$-th term be found without enumerating one. Problem 265 runs the window the other way,
as a search rather than a recurrence: a binary circle in which every $N$-bit window appears exactly
once is a [de Bruijn sequence](https://en.wikipedia.org/wiki/De_Bruijn_sequence). The
[depth-first search](/topics/technique/depth-first-search) appends one bit at a time with
`nxt = (window << 1 | bit) & mask` and records the windows it has already used in a $2^N$-bit
mask. The test "is this window new?" is then `used >> nxt & 1`, and the circle's numeric value
grows by the same shift as the window. Problem 209's circular
logic is literally a
[nonlinear feedback shift register](https://en.wikipedia.org/wiki/Nonlinear-feedback_shift_register),
`((state << 1) & mask) | (x0 ^ (x1 & x2))`, and finding its cycle structure *is* the problem. The
same window shows up in tiling: problem 161's broken-profile DP carries the frontier of filled cells
as a mask, and advancing one cell is `mask >> 1`.

**Sometimes the bits are the mathematics, not the encoding.** A number's binary expansion is a real
object with real theorems attached, and several problems collapse from a search to a formula once
you see it. [Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem) says the exponent
of 2 in $\binom{n}{k}$ counts the carries when adding $k$ and $n-k$ in base 2, which turns problem
704 into an expression in `n.bit_length()` and `n.bit_count()` alone.
[Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) makes $\binom{n}{k}$ odd exactly
when $k$'s bits are a submask of $n$'s, so a count that looked like a double sum becomes
$\sum 2^{\text{popcount}(t)}$ and then an $O(\log n)$ digit DP over the bits (problem 242). Problems
169, 872, 961, 974 and 1000 all decompose along the binary expansion in the same spirit, and the
even-simpler cases — problem 36's double-base palindromes, problem 162's hexadecimal digit masks —
are just reading a number in base 2 and asking a question about the digits.

**XOR shows where two numbers disagree.** `(a ^ b).bit_length() - 1` gives the highest bit where
`a` and `b` differ, so everything above that bit is their shared binary prefix. Problem 882 makes
this the core of a [combinatorial game](https://en.wikipedia.org/wiki/Combinatorial_game_theory).
In each position, Dr. One deletes a 1 bit from some number and Dr. Zero deletes a 0 bit. Deleting
bit $i$ splices it out of the integer: `(x >> (i + 1)) << i | x & ((1 << i) - 1)`. Each number's
game value is a [dyadic rational](https://en.wikipedia.org/wiki/Dyadic_rational), so the solution
stores it [exactly](/topics/takeaway/exact-arithmetic-for-equality) as an integer scaled by
$2^B$. Conway's simplicity rule sets a position's value to the *simplest* number strictly between
its best Left option and its best Right option, and in binary that is a prefix question. Look at
the highest bit where the two bounds differ. Keep the shared bits above it, clear everything
below, and the result is the simplest number in the gap — no search over denominators. Problem
963 is the ternary sequel. Deleting the 2s from a number's digits leaves a binary string, and
882's value table is reused unchanged on that string.

**XOR is addition when only parity matters.** A concatenation's parity is the XOR of the parts'
parities, so a mask of parities is a vector over
[GF(2)](https://en.wikipedia.org/wiki/GF(2)) that composes in one instruction. Problem 943's
self-describing sequences (a generalised
[Kolakoski sequence](https://en.wikipedia.org/wiki/Kolakoski_sequence)) form a derivation tree.
Each subtree is summarised by (leaf count, leaf sum, parity mask), where bit $k$ records the
parity of the subtree's node count at level $k$. Placing one subtree after another updates the
next sibling's starting mask with `mask ^= parity`. A run of equal-valued siblings is therefore a
deterministic walk on a finite set of masks, so it must cycle, and whole periods can be skipped
— the same finite-state argument as problem 167, applied to a mask rather than a window. The star
in problem 963 obeys the same rule: $* + * = 0$, so its bit combines by XOR while the other
fields add.

**In C the operations are single instructions with names.** GCC and Clang expose
`__builtin_popcountll` (count set bits), `__builtin_ctzll` (count trailing zeros — index of the
lowest set bit) and `__builtin_clzll` (leading zeros, so $\lfloor\log_2 n\rfloor$ is
`63 - __builtin_clzll(n)`). Python's equivalents are `int.bit_count()` and `int.bit_length()`, and
`(x & -x).bit_length() - 1` stands in for `ctz`. Problem 96's third Su Doku solution holds each
cell's nine candidate digits in a 9-bit mask and reads exactly like the constraint propagation it
is:

```python
values[cell] &= ~bit                  # eliminate one candidate digit
remaining = values[cell]
if remaining == 0:
    return False                      # contradiction: nothing left
if remaining.bit_count() == 1:        # naked single -> propagate to this cell's peers
    only = remaining.bit_length()
```

with the C port swapping in the intrinsics — `__builtin_popcount(remaining) == 1` and
`__builtin_ctz(remaining) + 1`. The payoff is language-dependent, and honestly so: in C the bitmask
solver runs in 1.0 ms against 6.4 ms for the set-and-array backtracker, a 6× win; in Python all
three solutions land near 50 ms and the bitmask one is marginally the *slower*, because the
interpreter's per-operation overhead swamps the difference between `popcount` and a set lookup. Bits
buy the most where the instructions are real.

## How to reason about it

- **Reach for it when the state is a small set, a small board, or a small window.** The trigger is
  "at most 20-ish independent yes/no facts" (a $2^n$ DP), or "a dense subset of a large range" (a
  bitset), or "the last $h$ steps of a sequence" (a shift register). If the state is none of those,
  a mask is obfuscation.
- **$2^n$ is the ceiling, and it arrives suddenly.** $n = 20$ is a million states, $n = 25$ is 33
  million, $n = 30$ is a gigabyte of `int32`. Subset DP is exponential — it is only ever a win
  because $n$ is small and the alternative is $n!$. Check the exponent before you write the loop.
- **Parenthesise. `&`, `|` and `^` bind looser than comparison in both C and Python.** `x & 1 == 0`
  parses as `x & (1 == 0)` and is silently always `0`; `mask >> i & 1` happens to be right because
  shift binds tighter than `&`, but nobody reading it should have to know that. Write
  `(mask >> i) & 1`.
- **Watch the width of the literal in C.** `1 << 40` shifts an `int` and is
  [undefined behaviour](/topics/takeaway/watch-integer-width); `1LL << 40` is the value you meant.
  Any mask wider than 31 bits needs the suffix — see [int64](/topics/technique/int64). And
  `__builtin_ctz(0)` is undefined, so guard the empty mask rather than relying on it returning 32.
- **Python's ints are unbounded, which is a licence and a trap.** A mask can be thousands of bits
  wide with no ceremony and no overflow, but each operation is then $O(\text{width})$, not $O(1)$ —
  a shift of a huge int copies it. Wide masks are fine as *state*; they are not fine inside the hot
  loop of an $O(2^n)$ enumeration, where a `bytearray` or [NumPy](/topics/technique/numpy) array of
  narrow masks beats one giant integer.
- **Name the encoding once, in a comment, at the point of definition.** `blank << CELLS | mask` is
  unreadable and a one-line comment makes it obvious. Every solution here that packs a state says
  what the layout is; that is not politeness, it is the only defence against an off-by-one in a
  shift, which produces a plausible wrong answer rather than a crash.
- **Prefer the idiom over the loop.** `w &= w - 1` to iterate set bits, `x & -x` to isolate the
  lowest, `(a ^ b).bit_length()` for the highest differing bit, `(1 << n) - 1` for a full mask,
  `sub = (sub - 1) & mask` to walk submasks (which problem
  118 uses to partition digits, and which visits all $3^n$ (mask, submask) pairs in total, not
  $4^n$). These are the vocabulary; code that spells them out with a `for` loop over bit positions
  is both slower and harder to read.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0096](/solutions/0096/) — Su Doku
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0161](/solutions/0161/) — Triominoes
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0244](/solutions/0244/) — Sliders
- ● [0265](/solutions/0265/) — Binary Circles
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0571](/solutions/0571/) — Super Pandigital Numbers
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0768](/solutions/0768/) — Chandelier
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0961](/solutions/0961/) — Removing Digits
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
