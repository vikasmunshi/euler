<!-- tags: [hamming-weight] -->
<!-- status: final -->
# Hamming weight

The [Hamming weight](https://en.wikipedia.org/wiki/Hamming_weight) of an integer is the number of
1 bits in its binary representation, also called its *population count* or *popcount*. On its own
it is a small operation. It keeps turning up because so many solutions store a set as a bitmask,
and once a set is an integer, "how many elements?" is a popcount. The rest of the time it turns up
because the binary digit sum s₂(n) shows up in number theory: in the 2-adic valuation of factorials
and binomial coefficients, and in counting the odd entries of Pascal's triangle. In both cases I
want the count in one machine instruction, not a loop.

## The idea

For `x = 0b1011_0010`, the popcount is 4. Every language spells it differently, and the
differences matter:

| | Spelling | Notes |
|---|---|---|
| Python ≥ 3.10 | `x.bit_count()` | Arbitrary precision; counts the bits of `abs(x)`. |
| Python, older idiom | `bin(x).count('1')` | Builds a string. Same answer, several times slower. |
| NumPy ≥ 2.0 | `np.bitwise_count(arr)` | Elementwise popcount over an integer array. |
| GCC / Clang | `__builtin_popcount`, `…l`, `…ll` | One builtin per width: `unsigned int`, `long`, `long long`. |
| C23 | `stdc_count_ones(x)` in `<stdbit.h>` | Type-generic, portable replacement for the builtins. |
| Hand-rolled | `while (x) { x &= x - 1; c++; }` | [Kernighan's loop](https://graphics.stanford.edu/~seander/bithacks.html#CountBitsSetKernighan): one iteration per set bit. |

In C the GCC builtin compiles to the x86 `POPCNT` instruction only when the target has it
(`-mpopcnt`, or `-march=native` on any CPU from the last fifteen years). Without that flag it
compiles to a library call doing the [SWAR](https://en.wikipedia.org/wiki/Hamming_weight#Efficient_implementation)
bit-parallel sum: still branch-free, just slower. Python's `int.bit_count()` is a C loop over the
bignum's digits, so on a single machine word it costs one method call, about the same as any other
int operation. The thing to stop writing is `bin(x).count('1')`, which allocates a string to answer
a question about bits.

The commonest **pitfall** is integer width in C. `__builtin_popcount` takes an `unsigned int`, so
passing it a `long long` mask quietly truncates it to the low 32 bits and the count comes out
wrong. Match the suffix to the type (p0238 and p0961 use `__builtin_popcountll` on 64-bit codes;
p0096 and p0345 use the plain form on masks that fit in 32 bits). Cast signed values to unsigned
first, as p0315 and p0345 do. See
[watch integer width](/topics/takeaway/watch-integer-width).

## What the count is *for*

Across the solutions below, the popcount answers one of four questions.

**How big is this set?** This is the bitmask-as-set reading. Problem 96's
constraint-propagation Sudoku keeps each cell's candidate digits as a 9-bit mask.
`values[c].bit_count() == 1` is the naked-single test, and the search branches on the cell with the
smallest popcount (the minimum-remaining-values heuristic):

```python
count = values[c].bit_count()
if count > 1 and count < best:
    best, cell = count, c
```

For the narrow "exactly one?" test, `x and not (x & (x - 1))` works too. The popcount reads better
and is just as fast. p0238 uses the count the same way, to say how many residues are still
uncovered in a mask. p0315 uses it on seven-segment displays: a digit is a 7-bit mask of lit
segments, so `popcount(a & b)` is the number of segments two digits share, and
`popcount(a ^ b)` (the [Hamming distance](https://en.wikipedia.org/wiki/Hamming_distance)) is the
number that have to toggle.

**Which step of a DP am I on?** In the assignment DP behind p0345 (a maximum-weight matching over
a matrix), `dp[mask]` is the best sum after rows `0 … k−1` have taken the columns in `mask`. The row
index `k` is not stored at all, because it equals `popcount(mask)`. This is the standard trick of
[bitmask DP](/topics/technique/dynamic-programming) over subsets: subsets of the same size form one
layer of the DP, and the popcount says which layer a mask is in. p0105 needs every subset's size
too, and shows both ways to get it. The Python builds the table with `bin(mask).count("1")`. The C
derives it from a smaller mask, `size[m] = size[m ^ lsb] + 1`, which costs O(1) per entry and needs
no popcount at all. When you are filling a 2ⁿ table in order anyway, the recurrence comes for free.

**What does the number theory say?** Here the popcount is s₂(n), the binary digit sum, and two
classical identities rest on it:

- [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) in base 2:
  v₂(n!) = n − s₂(n).
- [Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem): v₂(C(n, m)) is the number of
  carries when m and n − m are added in binary, which equals s₂(m) + s₂(n − m) − s₂(n).

p0704 builds on Kummer. The largest power of two dividing any entry of row n depends only on n's
bit length and popcount, so its sum over a range of n collapses into a sum over binary blocks,
with a popcount correction at the top block. p0242 builds on the parity side of
[Lucas's theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem): C(n, k) is odd exactly when
k's bits are a subset of n's, so row n of Pascal's triangle holds 2^popcount(n) odd entries
([OEIS A001316](https://oeis.org/A001316)). Summing 2^popcount(t) up to a bound is then a digit DP
over the bits, because a free block of b bits contributes 3ᵇ (each bit is either 0, worth 1, or 1,
worth 2).

**How many objects share this pattern?** p0961 reduces a number to the zero/nonzero pattern of its
digits and solves a game on the patterns. A pattern with a nonzero positions stands for 9ᵃ actual
numbers, so the popcount is the exponent: `pow9[code.bit_count()]`. p0872 uses the popcount as a
cost rather than a value: its parent walk clears one bit of the gap per step, so the walk is
`popcount(n − K)` steps long. That is the same reason Kernighan's loop runs popcount times and not
bit-length times.

## How to reason about it

- **Reach for it whenever a mask means a set.** If you find yourself writing a loop that tests each
  bit and increments a counter, that loop is a popcount. Say so and use the builtin.
- **In C, match the builtin to the width, and say why.** p0704's C carries a portable shift-and-add
  `popcount_ll` loop. It is correct, but it runs in O(bit length) where `__builtin_popcountll` is one
  instruction. It doesn't matter there because it is called once, but inside an inner loop it
  would.
- **For a whole array of flags, count the array, not each bit.** p0229 intersects four
  "representable" sieves and counts the survivors. In Python that is `np.count_nonzero` over a
  boolean array, in C a plain sum of bytes. If the flags were packed into a
  [bit array](/topics/technique/bit-array), the count would become a popcount per 64-bit word, the
  same idea one level up.
- **Precompute only when it pays.** A table `size[0 … 2ⁿ)` built by the recurrence makes sense
  when the DP visits every mask anyway. For scattered lookups the builtin is already O(1), and a
  table only adds memory traffic.
- **Remember what Python's `bit_count` does with negatives.** `(-5).bit_count()` is 2, the count for
  `abs(-5)`, not the infinite run of ones in two's complement. Mask to a width first
  (`x & 0xFFFF_FFFF`) if you mean the C answer.

For the surrounding toolbox (isolating the low bit, iterating submasks), see
[bit manipulation](/topics/technique/bit-manipulation) and
[bit-length](/topics/technique/bit-length).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0096](/solutions/0096/) — Su Doku
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0961](/solutions/0961/) — Removing Digits

<!-- /problems -->
