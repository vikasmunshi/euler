<!-- tags: [modulo] -->
<!-- status: final 2026-10-16T15:46Z -->
# Modulo

This page is about the [modulo operation](https://en.wikipedia.org/wiki/Modulo) as an *operator* —
the `%` you type — not about congruences. The mathematics of residues lives on the [modular
arithmetic](/topics/domain/modular-arithmetic) page and in the deeper [Modular
Arithmetic](/topics/number-theory/modular-arithmetic) note; the engineering decision to work in
residues at all is [modular arithmetic (application)](/topics/technique/modular-arithmetic-application),
and the big machines built on it have their own pages ([exponentiation](/topics/technique/modular-exponentiation),
[inverses](/topics/technique/modular-multiplicative-inverse-application), the [Chinese Remainder
Theorem](/topics/technique/chinese-remainder-theorem)). What is left for here is smaller and more
treacherous: what `%` actually returns when an operand is negative, what it costs, and where in a
loop to put it. Every problem below uses `%` for something mundane — peeling a digit, wrapping a
ring, filtering a candidate, keeping a generator in range — and each of those is a place where a
Python solution and its C translation can quietly disagree.

## Two definitions of the remainder

Every language agrees on the [division identity](https://en.wikipedia.org/wiki/Euclidean_division)
`a == (a / b) * b + a % b`. They disagree on how the quotient is rounded, and the remainder inherits
the choice:

| expression | Python (`//`, `%`) | C99 (`/`, `%`) |
| --- | --- | --- |
| `-7 / 3`, `-7 % 3` | `-3`, `2` | `-2`, `-1` |
| `7 / -3`, `7 % -3` | `-3`, `-2` | `-2`, `1` |
| rounding of the quotient | floor (toward −∞) | truncation (toward 0) |
| sign of the remainder | follows the **divisor** | follows the **dividend** |

Python's [floored division](https://docs.python.org/3/reference/expressions.html#binary-arithmetic-operations)
means `x % n` is always in `[0, n)` for a positive modulus — the mathematician's residue, no
questions asked. C99 (§6.5.5) fixed truncation, so `x % n` lands in `(−n, n)` and takes the sign of
`x`; before C99 the rounding of a negative quotient was implementation-defined, which is why older
code is so defensive about it. Two more C corners: `INT_MIN % -1` is undefined behaviour (the
matching quotient overflows), and `fmod` follows C's truncating rule while Python's float `%` follows
floor — `math.fmod` is the one to reach for when porting C float code to Python verbatim.

For non-negative operands the two agree, which is why most of the archive never notices. The
difference surfaces in exactly two shapes.

**Wrapping backwards.** Problem 84 walks a 40-square Monopoly board, and the "go back three squares"
card subtracts. The Python is simply `resolve((landing - 3) % board_size)`; the C has to write
`(landing - 3 + BOARD_SIZE) % BOARD_SIZE`, because `landing - 3` is negative near Go and C would hand
back an index of −1, −2 or −3. Adding one modulus works because the deficit is known to be smaller
than `n`. When it is not, the general fix is the double reduction `((x % n) + n) % n`, which
problem 149's C port uses on its [lagged Fibonacci
generator](https://en.wikipedia.org/wiki/Lagged_Fibonacci_generator) seed — and its recurrence step
uses the cheaper bias form instead: the two summands each lie in `[−500000, 500000)`, so adding
10⁶ before the `%` guarantees a non-negative operand and costs one addition rather than a second
division. Knowing the operand's range is what lets you pick the cheap fix.

**Testing a residue.** `x % 2 == 1` is an oddness test in Python and a bug in C, where a negative odd
`x` gives `-1`. Test against zero (`x % 2 != 0`) or use the bit (`x & 1`), which are right in both
languages for any sign. Problem 139's parity check `(m - n) % 2 == 0` is safe for that reason as well
as because `m > n` — it compares with zero, so the sign of the remainder never matters.

The rule I use when translating: **if any operand of `%` can be negative, the C line needs a
comment saying why it is correct**, and the parity test in the C↔Python review should look for it.

## What the division costs

`%` is a division. On x86-64 a 64-bit `idiv` has historically cost tens of cycles of latency — an
order of magnitude more than a multiply — though recent cores have narrowed the gap considerably
([Agner Fog's instruction tables](https://www.agner.org/optimize/instruction_tables.pdf) give the
numbers per microarchitecture). Three facts decide whether that matters:

- **A constant divisor is not a division.** When `n` is a compile-time constant the compiler
  replaces `x % n` with a multiply by a precomputed reciprocal and a shift
  ([Granlund–Montgomery](https://gmplib.org/~tege/divcnst-pldi94.pdf)). `num % 10` in problem 30's
  digit loop never executes a `div`. Hoisting a runtime modulus into a `#define` or `const` is
  therefore a real optimisation in C, not a style choice.
- **Quotient and remainder come together.** The hardware produces both at once, and compilers fuse
  `n % 10` with the neighbouring `n /= 10` into one operation — so the digit-peeling loops of
  problems 30 and 34 pay for one division per digit, not two. Python will not fuse the operators for
  you; [`divmod`](https://docs.python.org/3/library/functions.html#divmod) returns both from one call,
  which pays off on large integers where each division is a multi-limb operation, and is roughly a
  wash on small ones where interpreter overhead dominates.
- **A power of two is a mask — for unsigned values.** `x % 8` on an `unsigned` is `x & 7`. On a
  signed type the compiler must add a fix-up for negative `x` to honour truncation, so declaring a
  never-negative counter `unsigned` (or masking explicitly) buys the single instruction.

In Python, by contrast, the dominant cost of a small-int `%` is the bytecode around it, and the thing
that grows is the *size* of the operand: `%` on a thousand-digit integer is a long division. That
changes the question from "how often do I divide" to "how big do I let the number get".

## When to reduce

Reducing is never wrong for `+`, `−`, `×` (that is the number theory, and it lives elsewhere); the
engineering question is *where* the `%` goes.

- **Reduce before the operation that would overflow, not after it.** In C the product of two
  residues must fit the type: with `n < 2³²` two residues multiply safely in `uint64_t`; beyond that
  you need `__int128` or a mulmod (the overflow trap is worked through in the [number-theory
  note](/topics/number-theory/modular-arithmetic)). A `%` placed after an overflowed multiply reduces
  garbage. In Python the same placement keeps the operands in one machine-word-sized digit, so the
  multiply stays cheap.
- **Reduce the inputs when the test depends only on residues.** Problem 218 asks whether an
  expression in two generator parameters is divisible by 84; since divisibility depends only on the
  parameters mod 84, the solution reduces them first (`u, v = a % 84, b % 84`) and evaluates a
  degree-four polynomial on numbers below 84 instead of on numbers whose product would be enormous.
- **Additions can be reduced lazily.** If each term is below `n` and the accumulator has headroom for
  `k` of them, a `%` every `k` additions is as correct as one per addition and `k` times cheaper; the
  bias trick in problem 149 is the one-step version of the same range argument.
- **Use `%` as a cheap filter ahead of expensive work.** Problem 1's loop asks `term % 3 == 0 or
  term % 5 == 0`; problem 719 rejects most candidate square roots with `k % 9` (splitting a number's
  digits preserves its value mod 9, so only `k ≡ 0, 1` can survive) before attempting the costly
  recursive digit split. The residue test is one division; the work it skips is a search.
- **Prefer a stride to a test when the residue is known in advance.** If you know the survivors are
  exactly the multiples of 3, step by 3 rather than testing every integer — problem 1's closed-form
  solution takes this to its limit and never runs `%` at all.
- **Don't reduce when the question wants the exact value.** A modulus is a lossy projection; see
  [exact sums resist modular shortcuts](/topics/takeaway/exact-sums-resist-modular-shortcuts).

Two less obvious uses round out the list. Problem 73 computes the next [Farey
sequence](https://en.wikipedia.org/wiki/Farey_sequence) denominator as `max_d - (max_d + prev_d) % d`:
the textbook form is `⌊(n + b)/d⌋·d − b`, and since `⌊y/d⌋·d = y − y % d`, one remainder replaces a
floor division followed by a multiply. And problem 45 uses float modulo — `fmod(s, 6.0) != 5.0` on a
square root — as a perfect-square test and a residue test in one: a non-integral root can never
compare equal to an integer, so the check folds both conditions into one comparison. That is only
sound while the root is exact in a `double` (below 2⁵³); past that, use an integer square root and an
integer `%`.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0719](/solutions/0719/) — Number Splitting

<!-- /problems -->
