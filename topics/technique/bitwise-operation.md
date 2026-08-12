<!-- tags: [bitwise-operation] -->
<!-- status: final -->
# Bitwise operation

A [bitwise operation](https://en.wikipedia.org/wiki/Bitwise_operation) acts on an integer one bit at
a time, in parallel, with no carries between positions. That last clause is the whole subject.
Ordinary arithmetic couples the bits of its operands — a carry out of position 3 changes position 4
— and almost everything interesting about `&`, `|`, `^`, `~` and the shifts follows from their
refusal to do that. Across the problems below they turn up in two guises: as a *faster spelling* of
arithmetic the compiler could have done anyway, and — far more often — as an *algebra of their own*,
where the answer is a theorem about carries rather than about numbers.

## The idea

**XOR is addition without carrying; AND is where the carries would have been.** The identity worth
memorising is

```python
a + b == (a ^ b) + 2 * (a & b)        # sum = carry-less sum + carries, shifted left
a ^ b == a + b - 2 * (a & b)
a | b == (a ^ b) + (a & b)
```

`a & b` marks exactly the positions where both operands have a 1 — the positions that would generate
a carry — so `a & b == 0` is precisely the statement "adding these two numbers carries nowhere", and
in that case `a + b`, `a | b` and `a ^ b` all agree. Problem 301 is this identity and nothing else.
Its Nim position has value `n ^ 2n ^ 3n`, and since `n + 2n = 3n` is an identity of arithmetic, the
XOR vanishes exactly when that addition is carry-free — that is, when `n & 2n == 0`, meaning `n` has
no two adjacent set bits. A game-theory question about
[nim-values](/topics/domain/nimber) collapses into counting
[fibbinary numbers](/topics/domain/fibbinary-numbers) below a bound, which is a fifteen-line
[digit DP](/topics/technique/dynamic-programming) over $\log N$ positions instead of a walk over
$N$ of them. Problem 899's analysis of a distributed Nim variant turns on the same kind of statement
about binary structure — a condition on one player's low bits being all ones, which is
`(b + 1) % 2**k == 0` written as a fact about bit patterns.

**A shift is exact multiplication or division by a power of two, and the exactness is the point.**
`x << k` is $x \cdot 2^k$ and `x >> k` is $\lfloor x / 2^k \rfloor$ — never a rounding error, never a
float. Problem 122 bounds the best possible remaining progress of an addition chain by
`current << (max_depth - depth)`, because doubling at every remaining step is the most a chain can
do; the bound is a shift, and the branch is pruned. Problem 899 enumerates the dyadic ranges
$[2^{k-1}, 2^k - 1]$ directly as `lo = 1 << (k - 1)`, `hi = (1 << k) - 1`, and counts partners with
`(n + 1) >> k`. In [Tonelli–Shanks](https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm)
(problem 216) every exponent is a halving — `(p + 1) >> 2`, `(q + 1) >> 1`, and the factor-out loop
`while not q & 1: q >>= 1` — because the algorithm is *defined* on the 2-adic structure of $p - 1$,
so the shifts are the mathematics being transcribed, not an optimisation of `// 2`.

**`x & (2**k - 1)` is `x % 2**k`, and it is better behaved than `%` on negatives.** Masking off the
low $k$ bits is the remainder, for free. In C this matters twice over: `%` on a negative left operand
yields a *negative* remainder (truncation toward zero), whereas `& 3` always yields $0$–$3$. Python's
`%` already returns the non-negative representative, so `(-y) & 3` and `(-y) % 4` agree there —
problem 136 writes the former to find the first member of the residue class $m \equiv -y \pmod 4$
that its sieve must start from, once per outer iteration of an $O(N \log N)$ sweep. Problem 216 reads
`p & 3` and `p & 7` to branch on $p \bmod 4$ and $p \bmod 8$, the residues that govern
[quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity)'s supplements. The
companion idiom is `x & (x - 1)`, which clears the lowest set bit and so tests
[powers of two](/topics/technique/power-of-two-application) in one operation.

**`|` and `^` are set union and symmetric difference — over sets that may be enormous.** Because
Python's integers are unbounded, one `int` is a bitset of arbitrary width, and a shift on it means
"add a constant to every element of the set at once". Problem 201 uses exactly that: `reach[j]` is
the set of sums reachable by $j$-element subsets, held as one giant integer, and extending it by a
new value `v` is `reach[j] |= reach[j - 1] << v`. Sums hit twice are tracked in parallel
(`twice[j] |= (twice[j - 1] << v) | (reach[j] & shifted)`), so the answer set is
`reach[k] & ~twice[k]` — union, shift, intersection and difference standing in for a
subset-sum DP whose inner loop would otherwise be Python-level. Problem 229 does the set-theoretic
version across four quadratic forms: sieve each form into its own mask and `res &= form_mask(...)`
to intersect, then popcount. Problem 238 needs a *rotation* rather than a shift, which is the
standard pair-of-shifts idiom:

```python
mask = (1 << width) - 1
rot  = ((bits >> k) | (bits << (width - k))) & mask     # rotate right by k within `width` bits
```

**Complement is the operator that does not survive the move to Python.** In C, `~x` on a fixed-width
unsigned type is the complement you want. In Python, integers are conceptually two's-complement with
infinite sign extension, so `~x == -x - 1` — a *negative* number with infinitely many leading ones,
which is correct and almost never what a bitset wants. Inside a known width, complement with
`mask ^ x` (or `mask & ~x`), as problem 238 does with `uncovered &= mask ^ shifted`. The same care
applies to `-x`: `x & -x` isolates the lowest set bit and works in Python precisely *because* the
infinite sign extension makes two's complement come out right, which is a good illustration that the
model is consistent even where it surprises. Problem 201 leans on it —
`low = unique & -unique; unique ^= low` walks the set bits one at a time, each step costing one
isolate and one clear.

**In NumPy the operators go elementwise, and that is how you vectorise them.** `&`, `|`, `^`, `<<`
and `>>` broadcast over arrays where `and`/`or` would raise; boolean arrays combine with `&` and `|`,
never with the keywords. Problem 944 runs
[binary exponentiation](/topics/technique/exponentiation-by-squaring) over a whole array of exponents
at once — `odd = (e & 1).astype(bool)` selects the rows to multiply, `e >>= 1` advances all of them —
so a per-element `pow()` loop becomes $O(\log)$ vectorised passes. Problem 177 packs eight 16-bit
angle values into two `uint64` keys with `<<` and `|`, reducing a
[canonical-form](/topics/technique/canonical-form) comparison over a dihedral orbit to an integer
comparison the CPU does in one instruction, and combines the tie-break conditions as
`(hi < best_hi) | ((hi == best_hi) & (lo < best_lo))` — note every comparison parenthesised, which is
not style but necessity (see below).

## How to reason about it

- **Parenthesise everything.** In both C and Python, `&`, `|` and `^` bind *looser* than the
  comparison operators. `x & 1 == 0` parses as `x & (1 == 0)` and is silently always `0`; in NumPy
  `a > 1 & b > 2` is a broadcast error or worse. Write `(x & 1) == 0` and `(a > 1) & (b > 2)`. This
  is the single most common bitwise bug and it produces plausible wrong answers, not crashes.
- **Reach for the operator when it *is* the statement, not to save a cycle.** Any compiler turns
  `n / 2` into a shift when it can prove the type is unsigned. Writing `n >> 1` buys nothing there,
  and costs readability. It earns its place when the claim is about bits — "no carries", "low $k$
  bits clear", "these two sets are disjoint" — because then the code says what the proof says.
- **Watch the width of the literal in C.** `1 << 40` shifts an `int`: that is
  [undefined behaviour](/topics/takeaway/watch-integer-width), not a big number. Write `1ULL << 40`
  and give the mask a 64-bit type ([int64](/topics/technique/int64)). Shifting by more than the
  width, or by a negative amount, is likewise undefined; right-shifting a *negative* signed value is
  implementation-defined. Keep masks unsigned and the intent stays defined.
- **Python's `>>` on a negative int floors, it does not truncate.** `-7 >> 1 == -4`, while
  `int(-7 / 2) == -3`. That is the arithmetic shift being consistent with `//`, and it is another
  reason to keep bitwise reasoning on non-negative values.
- **Wide is free to write and not free to run.** A Python bitset of a million bits is one expression,
  but every `|` or `<<` on it copies $O(\text{width})$ words. That is a win when it replaces a
  million interpreter steps (problem 201) and a loss inside a hot loop over small values, where a
  [NumPy](/topics/technique/numpy) array or a word-array [bit array](/topics/technique/bit-array)
  belongs instead.
- **Name the packing where you define it.** `hi = a << 48 | b << 32 | c << 16 | d` is unreadable
  without a comment stating the field widths, and an off-by-one in a shift silently corrupts a
  neighbouring field. One line of comment at the definition is the only defence.
- **For state-in-an-integer — bitmask DP, boards, sliding windows — see
  [bit manipulation](/topics/technique/bit-manipulation).** This page is about the operators and
  their algebra; that one is about the representation they serve.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0301](/solutions/0301/) — Nim
- ● [0679](/solutions/0679/) — Freefarea
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0944](/solutions/0944/) — Sum of Elevisors

<!-- /problems -->
