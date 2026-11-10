<!-- tags: [digit-dp] -->
<!-- status: final -->
# Digit DP

[Digit DP](https://en.wikipedia.org/wiki/Digit_DP) counts numbers by walking their digits instead of
by visiting the numbers themselves. It applies whenever a question ranges over an interval far too
large to enumerate — below $10^{20}$, below $10^{40}$, the $10^{16}$-th number with some property —
but the property being asked about can be decided while reading the digits left to right, carrying
only a small amount of information forward. The bound stops being a count of candidates and becomes a
count of *positions*: a limit of $10^{40}$ is forty steps, not $10^{40}$ tests. That trade is why
this tag recurs across the problems below, which otherwise have nothing in common — balanced numbers,
step numbers, Nim, Pascal's triangle modulo 7, whole addition equations. And when even the positions
are too many — problem 529 asks about numbers with up to $10^{18}$ digits, problem 294 about
$11^{12}$ — the same DP turns into something you can jump along instead of walk: a linear recurrence
in one case, a table that doubles in the other.

## The idea

A property is *digit-local* when a partial number — a prefix of digits — can be summarised by a small
state such that (a) the state is computable from the prefix alone, and (b) the state plus the
remaining positions is enough to decide the property. Those two conditions are the whole precondition;
everything else is bookkeeping. Given them, the count over an astronomically large range is a
[dynamic program](/blogs/technique/dynamic-programming) over three coordinates:

- **Position** — how many digits have been placed. This is the DP's time axis, and it is
  $O(\log_{B} N)$ long, which is where the collapse comes from.
- **State** — what the prefix must remember. A running sum, a remainder, a carry, the last digit, a
  handful of booleans. Choosing it is the entire design problem, exactly as in
  [dynamic programming](/blogs/technique/dynamic-programming) generally.
- **Tight** — whether the prefix still matches the bound's prefix digit for digit. While tight, the
  next digit is capped by the bound's digit at this position; the moment a strictly smaller digit is
  placed, the number is *free* and every remaining position ranges over the full digit set. This one
  boolean is what lets the DP count over $[0, N]$ for an arbitrary $N$ rather than only over a power
  of ten.

The canonical shape, top-down with [memoization](/blogs/technique/memoization), is:

```python
@cache
def count(pos: int, state: int, tight: bool) -> int:
    if pos == len(digits):
        return 1 if accepts(state) else 0
    top = digits[pos] if tight else 9
    return sum(count(pos + 1, step(state, d), tight and d == top)
               for d in range(top + 1))
```

`step` and `accepts` are the whole problem; the rest is the same every time. The cost is
$O(L \cdot |\text{states}| \cdot B)$ for $L$ positions and base $B$ — independent of the magnitude of
the bound, which is the point. Bottom-up is the same recurrence with the loop turned inside out and
is what the C siblings in this repository usually do: a flat array indexed by
$(\text{position}, \text{state})$, no recursion, no hashing.

## Choosing the state

The state is where the thinking happens, and it is always a compression: many prefixes, one state.
What these problems carry is worth reading as a catalogue of the moves available.

| Problem | What a prefix must remember | State count |
| --- | --- | --- |
| 178 (step numbers) | last digit, reached-0?, reached-9? | 40 |
| 171 (digit squares) | running sum of digit squares | $\le 20 \cdot 81$ |
| 217 (balanced) | [digit sum](/blogs/domain/digit-sum) of a half-block | $\le 9m$ |
| 725 (DS-numbers) | digit sum, capped at 18 | 19 |
| 974 (very odd) | value mod 7, digit sum mod 3, five occurrence parities | $7 \cdot 3 \cdot 2^5 = 672$ |
| 612 (friend numbers) | the set of digits used so far | $2^{10}$ |
| 290 (digital signature) | carry of $137n$, signed digit-sum difference | $\le 137 \cdot 18L$ |
| 145 (reversible) | carry, plus a stack of pending mirror-column sums | small |
| 990 (addition equations) | active terms per side, signed column carry | $O(T^3)$ |
| 269 (integer roots) | one running quotient per candidate root | hundreds |
| 301 (Nim) | previous bit | 2 |
| 529 (10-substrings) | mask of suffix sums $\le 10$, sum since the earliest uncovered digit | 5630 reachable |

Two of these earn their place by a reduction made *before* the DP was written, and they are the ones
worth studying ([reduce before coding](/blogs/takeaway/reduce-before-coding)). Problem 178 asks for
step numbers that are pandigital, and "which of the ten digits have I seen?" looks like a $2^{10}$
subset mask. But a step number's digits move by $\pm 1$, so the set of digits visited is always a
contiguous interval — containing all ten is therefore just *touched 0* and *touched 9*, two booleans
instead of a mask. Problem 974 has the mirror-image experience: it genuinely needs five parity bits,
because "each odd digit occurs an odd number of times" is five independent facts, and 32 is small
enough to pay for. Problem 612 pays the full $2^{10}$ without complaint: two numbers are "friends" when
they share a digit, so the digit set is exactly what the question is about and there is nothing to
collapse — 1024 states across eighteen positions is still trivial. Knowing which case you are in is the
skill.

Problem 529 shows the reduction working on a condition that does not look digit-local at all: every
digit must lie inside *some* contiguous run summing to 10. Two observations make it finite. Any future
run must start inside a current suffix whose sum is still at most 10, so the prefix need only keep the
*set* of such suffix sums — an 11-bit mask, updated per digit $d$ by a shift left by $d$, setting bit
$d$, and dropping everything above bit 10, the same shift-and-mask move as a
[bitwise](/blogs/technique/bitwise-operation) string matcher. And of all the digits not yet covered,
only the earliest matters: a run ending here that covers it covers every later one too, so a single
running sum from that digit (dead once it passes 10) replaces a set of pending obligations.

The rest of the catalogue is the standard vocabulary. A **running remainder** handles divisibility,
because $v \mapsto 10v + d$ is well defined modulo anything; 974 tracks the value mod 7 that way while
tracking the digit sum mod 3 separately, since divisibility by 3 is a digit-sum property. A **carry**
handles arithmetic performed on the digits: problem 145 adds a number to its reversal, so each column
sum is shared with its mirror column but resolved at a different moment — the state is the carry plus
a stack of pair sums chosen on the left and not yet spent on the right, which is
[carry arithmetic](/blogs/technique/carry-arithmetic) made explicit as DP state. Problem 269 pushes
this furthest: the constraint "$P_n(r) = 0$" becomes a running quotient updated by a division that
either divides exactly or kills the branch, so the divisibility test doubles as the pruning that keeps
the state space finite. It then wraps the DP in
[inclusion–exclusion](/blogs/technique/inclusion-exclusion-principle) over the eleven possible
integer roots, because "has at least one root" is a union.

## Reading several numbers at once

The carry is also how a digit DP reads more than one number in the same pass — and then the direction
flips. Arithmetic propagates carries from the least significant digit upward, so a DP that simulates
arithmetic walks the columns **low to high**, where the tight flag has nothing to hug and the bound is
simply a length.

Problem 290 asks how many $n < 10^{18}$ satisfy $s(n) = s(137n)$, a comparison between a number and a
function of itself. Reading $n$ from the bottom, one digit $d$ and the incoming carry fix exactly one
output digit of $137n$ — $(137d + \text{carry}) \bmod 10$ — and the next carry. So the state is the
carry (below 137) and a **signed difference** of the two running digit sums, rather than both sums:
the question is whether they agree, and one integer says that. When the digits of $n$ run out, the
leftover carry *is* the top of $137n$, and its digit sum settles the last of the difference. The same
move — track the gap, not the two quantities — is what makes any "is $f(n)$ like $n$?" question a
small DP.

Problem 990 takes this as far as it goes: it counts strings like `77=7+70` that form true addition
equations, which means summing an unknown number of terms of unknown lengths on both sides. Right-align
every term and walk the columns from the bottom: a column adds the left-hand digits, subtracts the
right-hand ones, and passes a signed carry; the equation balances when every term has ended and the
carry is zero. The state is *how many terms are still active on each side* plus the carry — never the
terms' values or even their lengths. Which of the active terms ends in this column is a binomial
choice, which is what keeps the ordered lists of terms counted exactly once, and a no-leading-zero rule
is simply "a term's last digit is nonzero". The column's digit sum is then one lookup in a precomputed
polynomial, after a reflection ($d \mapsto 9 - d$ on the right-hand side) turns "sum of left minus sum of
right" into a plain sum of digits. Problem 145's number-plus-its-reversal and problem 1000's three
coordinates are the same pattern on a fixed number of operands; 990 shows the operand count can itself
be part of the state.

## Carrying more than a count

The DP table need not hold counts. Any aggregate that is *linear* over the numbers being counted can
ride along in a parallel table, and the one that matters most is the **sum of the values themselves**
— problems 171, 217 and 725 all want a sum, not a tally. Keep `cnt[s]` and `val[s]` side by side; when
a digit $d$ is appended as a new least-significant digit,

$$\text{cnt}'[s+d] \mathrel{+}= \text{cnt}[s], \qquad
  \text{val}'[s+d] \mathrel{+}= 10\,\text{val}[s] + d\cdot\text{cnt}[s].$$

The $d \cdot \text{cnt}[s]$ term is the part people forget: every one of the numbers already in that
state acquires the same new digit, so the new digit contributes $d$ once *per number*, not once. When
the digit is prepended at a known place value $p$ instead, the same logic gives
$\text{val}'[s+d] \mathrel{+}= \text{val}[s] + p\,d\,\text{cnt}[s]$. Everything stays reduced
[modulo](/blogs/technique/modular-arithmetic-application) $M$ throughout when the answer is modular,
which these problems' answers usually are — a sum over $10^{47}$ numbers has no other tractable form.

Once values are in the table, the aggregates compose. Problem 217 splits a balanced number into two
half-blocks, notes that on odd lengths the shared middle digit cancels out of the balance condition
entirely, and convolves the two halves by equal digit sum — $\sum_s (\text{val}_L \text{cnt}_R +
\text{cnt}_L \text{val}_R)$, because each left half pairs with every right half. Problem 725 gets its
"one digit equals the sum of the others" condition from the observation that such a number's total
digit sum is $2h$, then counts "contains at least one $h$" by complementary counting: all numbers of
that digit sum, minus those built from the other nine digits.

The linearity restriction is weaker than it looks, because it only binds *inside* a state. Problem 776
wants $\sum_{n \le N} n / s(n)$, and dividing by the digit sum is not linear in anything — but within
the class of numbers whose digit sum is $s$ it is a constant factor. So the DP collects
$T(s) = \sum \{ n \le N : s(n) = s \}$ with the count-and-value pair above, and the nonlinear weight is
applied once per final state: $\sum_s T(s)/s$, about $9L$ terms, computed as exact rationals. The
general move: **make whatever the weight depends on part of the state**, and the weight becomes a
post-processing step over a short histogram.

That histogram is often the real output. Problem 612 counts unordered pairs $p < q < 10^{18}$ sharing a
digit, which is not a property of one number at all. The DP never sees a pair: it only sorts the
numbers below the bound into 1023 classes by exact digit set. Pairs are then a question about classes
— two numbers are strangers exactly when their sets are disjoint, i.e. one set lies inside the
complement of the other — and a [subset-sum (zeta) transform](https://codeforces.com/blog/entry/45223)
over the masks answers "how many numbers have a digit set inside $M$?" for every $M$ at once, so the
disjoint pairs, and by complement the friends, cost $10 \cdot 2^{10}$ more operations. The
leading-zero subtlety shows up here in a clean form: a leading zero must leave the set empty rather
than add digit 0, so the empty mask doubles as "no digit placed yet".

## From counting to constructing

A digit DP that counts also *unranks*. If you can answer "how many valid numbers have this prefix?",
you can find the $n$-th valid number without listing any of them: fix digits from the most significant
down, and at each position try candidate digits in increasing order, subtracting each one's completion
count from the running rank until the rank fits. That is [unranking](/blogs/technique/unranking), and
it is how problems 845 and 974 answer "give me the $10^{16}$-th number such that…". The counting table
is built once; the construction is one pass of $L \times B$ table lookups. The prerequisite is that the
DP counts *completions* of a prefix (a suffix-indexed table) rather than prefixes reaching a state —
the same recurrence, indexed from the other end.

The two ideas combine. Problem 912 lists the binary strings without three consecutive ones and asks
for $\sum n^2$ over the ranks $n \le 10^{16}$ whose string is odd — a sum over *ranks*, not over values.
Unranking the $10^{16}$-th string walks down the bits, and every time it takes the 1-branch it steps
over the entire 0-branch: a block of consecutive ranks, all below the target. The suffix table carries,
besides the count, the count of odd strings and the sums $\sum o$ and $\sum o^2$ of their ordinals
within the block, so a skipped block starting at offset $c$ contributes
$\sum (c + o)^2 = c^2 \cdot \#\text{odd} + 2c \sum o + \sum o^2$ in closed form. This is the
count-and-value pair one moment further: a quadratic needs the zeroth, first and second moments, and
shifting moments is just a binomial expansion.

## It is not only base 10

Nothing above mentions ten except the digit range, and several of these problems are digit DPs in
another base — usually binary, which is where the technique stops looking like a trick about decimal
digits and starts looking like what it is: a
[finite-state machine](/blogs/technique/finite-state-machine) reading a numeral.

Problem 301 reduces a question about three-heap Nim to counting integers below $2^{30}$ with no two
adjacent set bits, which is a two-state DP over bits ("previous bit was 1") with a tight flag against
the bound. Problem 169 counts representations of $n$ as a sum of powers of two using each at most
twice; the count depends only on $n$'s binary expansion, so a pair of running values is folded bit by
bit in a single high-to-low sweep — DP state as a small vector rather than a table. Problems 148 and
242 both go through [Lucas's theorem](/blogs/domain/lucass-theorem), which is itself a statement that
binomial coefficients modulo a prime $p$ factor across base-$p$ digits — a digit-local property by
construction. Problem 148 counts entries of Pascal's triangle not divisible by 7 by a base-7 digit
recurrence in which a complete block of $7^m$ rows contributes a fixed factor; problem 242 reduces a
parity question about subset sums to a weighted popcount sum over binary digits, where a block of $b$
free bits contributes $3^b$. Problem 1000's Nim sub-problem counts triples whose coordinates all share
the top bit of their XOR — three tight flags at once, one per coordinate.

## When the length is the bound

The collapse from magnitude to positions is only a collapse if the positions are few. Problem 529
counts qualifying numbers below $10^{n}$ for $n = 10^{18}$, so the DP's time axis is itself
astronomically long, and walking it one digit at a time is exactly the enumeration digit DP was meant
to avoid. What rescues it is that the bound is a power of the base: there is no tight flag, so every
step applies the *same* transition — the DP is a fixed matrix $A$ over the automaton's states, and the
count at length $L$ is a fixed linear functional of $A^{L}$. By
[Cayley–Hamilton](https://en.wikipedia.org/wiki/Cayley%E2%80%93Hamilton_theorem), any such sequence
satisfies a [linear recurrence](/blogs/technique/linear-recurrence-with-constant-coefficients) of order
at most the number of states, so the question becomes "find the recurrence, then jump to term
$10^{18}$".

With thousands of states, [matrix exponentiation](/blogs/technique/matrix-exponentiation) is cubic
and out of reach, so 529 never builds the matrix power. It
[minimises the automaton](/blogs/technique/dfa-minimization) — only to obtain a *rigorous* bound on the
recurrence order, which says how many terms are enough — runs the ordinary forward digit DP for twice
that many lengths, lets [Berlekamp–Massey](/blogs/technique/berlekamp-massey-algorithm) recover the
recurrence from those terms, and extracts the one far coefficient of the resulting rational generating
function by Bostan–Mori with [FFT](/blogs/technique/fast-fourier-transform) products. The digit DP is
still the part that encodes the problem; it has simply become a term generator for a
[small-cases-reveal-the-recurrence](/blogs/takeaway/small-cases-reveal-recurrence) pipeline, and
everything that does depend on $n$ costs $O(\log n)$ polynomial products.

Problem 294 has the same shape with a twist that rules out the matrix view: it counts $k < 10^{n}$,
$n = 11^{12}$, with digit sum 23 and $k \equiv 0 \pmod{23}$. The state is (residue mod 23, digit sum
$\le 23$), but the digit at position $i$ contributes $d \cdot 10^i$ to the residue, so the transition
*does* depend on the position and there is no single $A$ to raise to a power. What survives is
**associativity of concatenation**. Summarise a block of $L$ digit positions by its whole table — how
many length-$L$ strings land on each (residue, sum) — and two blocks join by a convolution: residues
of the upper block are scaled by $10^{L} \bmod 23$ and added cyclically, digit sums add and truncate
at 23. A table for length $2L$ is one join of the length-$L$ table with itself, so
[binary exponentiation](/blogs/technique/exponentiation-by-squaring) over $n$'s bits reaches length
$11^{12}$ in about eighty joins. The lesson generalises: when the per-step transition varies, look for
a *block* summary that composes, and double the block instead of powering the step.

## How to reason about it

- **Ask whether the property is digit-local first.** If deciding it needs the whole number — its
  factorisation, its primality — digit DP does not apply, however large the range. If it needs only a
  sum, a remainder, a carry, a comparison with a neighbour, or a bounded set of flags, it does.
- **Count the state space before writing anything.** Multiply out the components. If the product is in
  the hundreds or thousands, the DP is instant; if it is $2^{10}$ per position and climbing, look for
  the reduction that collapses it (problem 178's two booleans) before accepting the cost.
- **Count the positions too.** $O(L)$ is only cheap while $L$ is a digit count of a bound you were
  handed. If the problem hands you the length itself and it is huge, check that the transition is
  position-independent (no tight flag, no per-position rule) and go looking for the recurrence instead
  of the loop, as 529 does; if it is not, look for a block summary that composes and double it, as
  294 does.
- **Pick the direction from the arithmetic.** Most-significant-first is natural for a bound and for
  unranking; least-significant-first is forced as soon as the DP simulates a carry (290, 990).
- **You may not need the tight flag at all.** It is only for hugging an arbitrary bound. Half of these
  problems ask about "all numbers with at most $L$ digits", which — with leading zeros allowed — is
  exactly "all length-$L$ digit strings", so the DP is a plain
  [composition count](/blogs/domain/composition-combinatorics) with no bound-tracking at all. Decide
  which question you are answering; the leading-zero convention follows from it, and it is the usual
  source of off-by-one errors (a length-$L$ string starting with 0 *is* a shorter number, so either
  forbid it at the first position or subtract the shorter count afterwards).
- **Reduce inside the recurrence, not at the end.** Sums and products are all that feed the table, so
  a modular answer stays correct under reduction at every step, and the intermediates stay small.
- **Watch the width in C.** Completion counts overflow easily: 974's C sibling needs
  `unsigned __int128` for its table, and 217's C sibling reduces every product through a 128-bit
  intermediate. Python's unbounded integers hide the problem until the port
  ([watch integer width](/blogs/takeaway/watch-integer-width)).
- **Build the table inside `solve()`.** With `--runs=N` the harness times repeated calls, so a table
  kept at module level is warm from the second run onward and the reported average measures lookups
  rather than the algorithm ([size work to the input](/blogs/takeaway/size-work-to-the-input)).
- **Top-down when the reachable states are sparse, bottom-up otherwise.** The `@cache` recursion above
  is the fastest thing to write and only visits reachable states, which is what 269 wants, where the
  state is a tuple of quotients and most transitions die. When nearly every state is reached, a flat
  array in the natural order is faster and cannot overflow the stack — and in C, where a tuple-keyed
  dict means writing an [open-addressing hash table](/blogs/technique/hash-table) by hand (as 145 and
  269 do, 145 packing its pending stack into one integer in
  [mixed radix](/blogs/technique/mixed-radix)), it is worth some effort to arrange.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0290](/solutions/0290/) — Digital Signature
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0301](/solutions/0301/) — Nim
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0612](/solutions/0612/) — Friend Numbers
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0912](/solutions/0912/) — Where are the Odds?
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0990](/solutions/0990/) — Addition Equations
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
