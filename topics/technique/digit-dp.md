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
step numbers, Nim, Pascal's triangle modulo 7.

## The idea

A property is *digit-local* when a partial number — a prefix of digits — can be summarised by a small
state such that (a) the state is computable from the prefix alone, and (b) the state plus the
remaining positions is enough to decide the property. Those two conditions are the whole precondition;
everything else is bookkeeping. Given them, the count over an astronomically large range is a
[dynamic program](/topics/technique/dynamic-programming) over three coordinates:

- **Position** — how many digits have been placed. This is the DP's time axis, and it is
  $O(\log_{B} N)$ long, which is where the collapse comes from.
- **State** — what the prefix must remember. A running sum, a remainder, a carry, the last digit, a
  handful of booleans. Choosing it is the entire design problem, exactly as in
  [dynamic programming](/topics/technique/dynamic-programming) generally.
- **Tight** — whether the prefix still matches the bound's prefix digit for digit. While tight, the
  next digit is capped by the bound's digit at this position; the moment a strictly smaller digit is
  placed, the number is *free* and every remaining position ranges over the full digit set. This one
  boolean is what lets the DP count over $[0, N]$ for an arbitrary $N$ rather than only over a power
  of ten.

The canonical shape, top-down with [memoization](/topics/technique/memoization), is:

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
| 217 (balanced) | [digit sum](/topics/domain/digit-sum) of a half-block | $\le 9m$ |
| 725 (DS-numbers) | digit sum, capped at 18 | 19 |
| 974 (very odd) | value mod 7, digit sum mod 3, five occurrence parities | $7 \cdot 3 \cdot 2^5 = 672$ |
| 145 (reversible) | carry, plus a stack of pending mirror-column sums | small |
| 269 (integer roots) | one running quotient per candidate root | hundreds |
| 301 (Nim) | previous bit | 2 |

Two of these earn their place by a reduction made *before* the DP was written, and they are the ones
worth studying ([reduce before coding](/topics/takeaway/reduce-before-coding)). Problem 178 asks for
step numbers that are pandigital, and "which of the ten digits have I seen?" looks like a $2^{10}$
subset mask. But a step number's digits move by $\pm 1$, so the set of digits visited is always a
contiguous interval — containing all ten is therefore just *touched 0* and *touched 9*, two booleans
instead of a mask. Problem 974 has the mirror-image experience: it genuinely needs five parity bits,
because "each odd digit occurs an odd number of times" is five independent facts, and 32 is small
enough to pay for. Knowing which case you are in is the skill.

The rest of the catalogue is the standard vocabulary. A **running remainder** handles divisibility,
because $v \mapsto 10v + d$ is well defined modulo anything; 974 tracks the value mod 7 that way while
tracking the digit sum mod 3 separately, since divisibility by 3 is a digit-sum property. A **carry**
handles arithmetic performed on the digits: problem 145 adds a number to its reversal, so each column
sum is shared with its mirror column but resolved at a different moment — the state is the carry plus
a stack of pair sums chosen on the left and not yet spent on the right, which is
[carry arithmetic](/topics/technique/carry-arithmetic) made explicit as DP state. Problem 269 pushes
this furthest: the constraint "$P_n(r) = 0$" becomes a running quotient updated by a division that
either divides exactly or kills the branch, so the divisibility test doubles as the pruning that keeps
the state space finite. It then wraps the DP in
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over the eleven possible
integer roots, because "has at least one root" is a union.

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
[modulo](/topics/technique/modular-arithmetic-application) $M$ throughout when the answer is modular,
which these problems' answers usually are — a sum over $10^{47}$ numbers has no other tractable form.

Once values are in the table, the aggregates compose. Problem 217 splits a balanced number into two
half-blocks, notes that on odd lengths the shared middle digit cancels out of the balance condition
entirely, and convolves the two halves by equal digit sum — $\sum_s (\text{val}_L \text{cnt}_R +
\text{cnt}_L \text{val}_R)$, because each left half pairs with every right half. Problem 725 gets its
"one digit equals the sum of the others" condition from the observation that such a number's total
digit sum is $2h$, then counts "contains at least one $h$" by complementary counting: all numbers of
that digit sum, minus those built from the other nine digits.

## From counting to constructing

A digit DP that counts also *unranks*. If you can answer "how many valid numbers have this prefix?",
you can find the $n$-th valid number without listing any of them: fix digits from the most significant
down, and at each position try candidate digits in increasing order, subtracting each one's completion
count from the running rank until the rank fits. That is [unranking](/topics/technique/unranking), and
it is how problems 845 and 974 answer "give me the $10^{16}$-th number such that…". The counting table
is built once; the construction is one pass of $L \times B$ table lookups. The prerequisite is that the
DP counts *completions* of a prefix (a suffix-indexed table) rather than prefixes reaching a state —
the same recurrence, indexed from the other end.

## It is not only base 10

Nothing above mentions ten except the digit range, and several of these problems are digit DPs in
another base — usually binary, which is where the technique stops looking like a trick about decimal
digits and starts looking like what it is: a
[finite-state machine](/topics/technique/finite-state-machine) reading a numeral.

Problem 301 reduces a question about three-heap Nim to counting integers below $2^{30}$ with no two
adjacent set bits, which is a two-state DP over bits ("previous bit was 1") with a tight flag against
the bound. Problem 169 counts representations of $n$ as a sum of powers of two using each at most
twice; the count depends only on $n$'s binary expansion, so a pair of running values is folded bit by
bit in a single high-to-low sweep — DP state as a small vector rather than a table. Problems 148 and
242 both go through [Lucas's theorem](/topics/domain/lucass-theorem), which is itself a statement that
binomial coefficients modulo a prime $p$ factor across base-$p$ digits — a digit-local property by
construction. Problem 148 counts entries of Pascal's triangle not divisible by 7 by a base-7 digit
recurrence in which a complete block of $7^m$ rows contributes a fixed factor; problem 242 reduces a
parity question about subset sums to a weighted popcount sum over binary digits, where a block of $b$
free bits contributes $3^b$. Problem 1000's Nim sub-problem counts triples whose coordinates all share
the top bit of their XOR — three tight flags at once, one per coordinate.

## How to reason about it

- **Ask whether the property is digit-local first.** If deciding it needs the whole number — its
  factorisation, its primality — digit DP does not apply, however large the range. If it needs only a
  sum, a remainder, a carry, a comparison with a neighbour, or a bounded set of flags, it does.
- **Count the state space before writing anything.** Multiply out the components. If the product is in
  the hundreds or thousands, the DP is instant; if it is $2^{10}$ per position and climbing, look for
  the reduction that collapses it (problem 178's two booleans) before accepting the cost.
- **You may not need the tight flag at all.** It is only for hugging an arbitrary bound. Half of these
  problems ask about "all numbers with at most $L$ digits", which — with leading zeros allowed — is
  exactly "all length-$L$ digit strings", so the DP is a plain
  [composition count](/topics/domain/composition-combinatorics) with no bound-tracking at all. Decide
  which question you are answering; the leading-zero convention follows from it, and it is the usual
  source of off-by-one errors (a length-$L$ string starting with 0 *is* a shorter number, so either
  forbid it at the first position or subtract the shorter count afterwards).
- **Reduce inside the recurrence, not at the end.** Sums and products are all that feed the table, so
  a modular answer stays correct under reduction at every step, and the intermediates stay small.
- **Watch the width in C.** Completion counts overflow easily: 974's C sibling needs
  `unsigned __int128` for its table, and 217's C sibling reduces every product through a 128-bit
  intermediate. Python's unbounded integers hide the problem until the port
  ([watch integer width](/topics/takeaway/watch-integer-width)).
- **Build the table inside `solve()`.** With `--runs=N` the harness times repeated calls, so a table
  kept at module level is warm from the second run onward and the reported average measures lookups
  rather than the algorithm ([size work to the input](/topics/takeaway/size-work-to-the-input)).
- **Top-down when the reachable states are sparse, bottom-up otherwise.** The `@cache` recursion above
  is the fastest thing to write and only visits reachable states, which is what 269 wants, where the
  state is a tuple of quotients and most transitions die. When nearly every state is reached, a flat
  array in the natural order is faster and cannot overflow the stack — and in C, where a tuple-keyed
  dict means writing an [open-addressing hash table](/topics/technique/hash-table) by hand (as 145 and
  269 do, 145 packing its pending stack into one integer in
  [mixed radix](/topics/technique/mixed-radix)), it is worth some effort to arrange.

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
- ● [0301](/solutions/0301/) — Nim
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
