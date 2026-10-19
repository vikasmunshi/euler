<!-- tags: [find-first-set] -->
<!-- status: final 2026-10-19T09:32Z -->
# Find first set

[Find first set](https://en.wikipedia.org/wiki/Find_first_set) (ffs) returns the position of the lowest
1-bit in a word. Its close relative *count trailing zeros* (ctz) returns the same position counted from 0.
It sounds like trivia, but once a set is stored as a bitmask, ffs is how you get an
*element* back out of it: which digit is left in a Sudoku cell, which item a subset mask adds,
which sum a bitset marks. All three solved problems below keep sets as bits, and each needs ffs at
the point where the bits turn back into a number.

## The idea — isolate, then locate

Two identities do all the work. In two's complement $-x = \lnot x + 1$, so

- `x & -x` **isolates** the lowest set bit: it keeps that bit and clears everything else;
- `x & (x - 1)` **clears** the lowest set bit.

What remains is to turn the isolated bit $2^i$ into $i$. Hardware does this in one instruction
(`tzcnt`/`bsf` on x86, `rbit`+`clz` on ARM), and C compilers expose it as `__builtin_ctz`
(for `unsigned int`) and `__builtin_ctzll` (for 64-bit). Both are **undefined for 0**, so every call
site must know its argument is non-zero. Python has no ctz, but `int.bit_length()` returns the index
of the *highest* set bit plus one. On an isolated bit the highest and lowest bits are the same, so

```python
i = (x & -x).bit_length() - 1      # ctz(x) for x > 0
```

The common loop is "visit every element of the set" in $O(\text{popcount})$ steps rather than
$O(\text{width})$:

```c
while (bits) { int i = __builtin_ctzll(bits); /* use i */ bits &= bits - 1; }
```

## Three uses across the problems

**96, Su Doku (`s2`): a singleton mask back to a digit.** Each cell's candidates are a 9-bit mask,
bit $d-1$ for digit $d$. When propagation reduces a mask to one bit (a
[Hamming weight](/topics/technique/hamming-weight) of 1), ffs names the digit, which is then removed
from the cell's peers. Python writes it as `remaining.bit_length()`. That is correct *only* because the mask
has exactly one bit, so highest equals lowest. C writes the general form, `__builtin_ctz(remaining) + 1`.
The same call reads the final grid's top-left digits off their masks. See
[constraint propagation](/topics/technique/constraint-propagation) for the rest of the solver.

**105, special subset sums: fill a table over all submasks.** To test a set of up to twelve
numbers, the solution precomputes the sum of every one of the $2^n$ subsets in $O(2^n)$. The recurrence
peels off the lowest element: `subset_sum[mask] = subset_sum[mask ^ lsb] + elements[ctz(mask)]`, where
`mask ^ lsb` is smaller and already filled. ffs here is an index into the element array. The
[submask](/topics/technique/mask-computing) enumeration that follows, `c = (c - 1) & complement`,
belongs to the same family of tricks.

**201, unique subset sums: harvest a bitset.** The DP runs over
[bitsets](/topics/technique/bit-array) on the sum axis: bit $s$ of `reach[j]` means some $j$-subset sums
to $s$, and a second bitset marks sums reached twice. The answer is the sum of the *positions* of the
set bits in `reach[k] & ~twice[k]`. That is a loop of isolate, locate, clear, as above, where each
position found is a subset sum.

## Python and C

The two languages differ most here, because Python has no fixed word width.

- **The primitive.** C has `__builtin_ctz`/`ctzll`, a single instruction. Python composes
  `x & -x` and `bit_length()`, which works on integers of any size. In Python's two's-complement view
  of integers, `-x` behaves as if it had infinitely many leading 1s, so the identity carries over unchanged.
- **96**: Python's `bit_length()` shortcut and C's `ctz + 1` agree only on single-bit masks. That
  contract is implicit in the Python, so a later edit could break it without warning.
- **105**: the same recurrence line for line. Python's integer masks are small here, so the per-mask
  cost is interpreter overhead, not arithmetic. Python counts subset sizes with
  `bin(mask).count("1")` and C extends the recurrence: `size[mask] = size[mask ^ lsb] + 1`.
- **201**: here the cost models differ. Python keeps each bitset as **one big integer**, so the
  harvesting loop's `unique & -unique` and `unique ^= low` each touch every word of the integer. Extracting
  $b$ bits from a $W$-word integer is therefore $O(bW)$. C splits the bitset into `uint64_t` words and
  runs `ctzll` + `bits &= bits - 1` within one word, so the harvest is $O(W + b)$. For this problem the
  DP dominates in both, but on a dense result the Python loop would become the bottleneck. A
  `bin(x)`/string scan or a per-word split would be the fix.

## How to reason about it

- **Use it whenever a bitmask is a set.** Membership is `&`, size is popcount, and *an element* is ffs.
- **Guard zero.** `__builtin_ctz(0)` is undefined behaviour in C, and `(0).bit_length() - 1` is $-1$
  in Python. Every call site in these solutions is inside a `while (bits)` or after a non-empty test.
- **Match the width.** `__builtin_ctz` takes `unsigned int`. Pass a 64-bit word and the high half is
  silently truncated. Use `ctzll` for `uint64_t` (201 does).
- **Lowest vs highest.** `bit_length` gives the highest bit. It equals ffs only after isolating with
  `x & -x`, or when the mask has one bit by construction (96).
- **Iterate set bits, not positions.** `x &= x - 1` makes the loop proportional to the number of
  elements, which is what makes sparse bitsets cheap to read.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0096](/solutions/0096/) — Su Doku
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum

<!-- /problems -->
