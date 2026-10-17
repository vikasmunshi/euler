<!-- tags: [periodic-sequence] -->
<!-- status: final -->
# Periodic sequence

A [periodic sequence](https://en.wikipedia.org/wiki/Periodic_sequence) satisfies
$a_{n+T} = a_n$ for some period $T \ge 1$. It is *eventually* periodic if that holds only past
some index $\mu$. Periodicity is worth looking for because it is the most direct way to turn an
infinite question, or one with an absurd index like $10^{11}$ or $2 \times 10^{15}$, into a finite
one. Once you know $T$, everything about the sequence is decided by one period. The solved problems
below each make that move, but they find the period in three different ways, and they use it for
four different things. This page is about those two choices. How to *detect* a cycle in an
arbitrary iteration (Floyd, Brent, the rho shape) belongs to
[cycle detection](/topics/technique/cycle-detection) and
[functional graph](/topics/domain/functional-graph).

## Where the period comes from

**It is built into the problem.** Days of the week repeat with period 7. **Problem 19** counts
first-of-month Sundays, and it never handles an absolute date at all, only a residue mod 7 pushed
forward by each month's length. The C solution is exactly that sentence:

```c
for (int y = start_year; y <= end_year; y++) {
    for (int m = 1; m <= 12; m++) {
        if (dow == 6) count++;                    /* Sunday, with Monday = 0 */
        dow = (dow + days_in_month(y, m)) % 7;
    }
}
```

A second period hides in the calendar too. A Gregorian 400-year cycle has
$146\,097 = 7 \times 20\,871$ days, so the whole weekday pattern repeats every 400 years. A span of
a million years would reduce to 2 500 copies of one cycle plus a remainder. Problem 19's century
is small enough that the solution never needs this second period, but it is the same move one
level up.

**It is forced by finiteness and invertibility.** A deterministic recurrence over a finite state
space must eventually repeat, by the [pigeonhole principle](/topics/domain/pigeonhole-principle).
If the step map is also a [bijection](/topics/domain/bijection), the sequence has no tail: it is
*purely* periodic, and the seed state is the first state to come back. Three of these problems
rely on that:

| problem | state | why the step is invertible |
|---|---|---|
| 167 Ulam sequences | the last $h$ membership bits of the odd numbers | the recurrence $b_j = b_{j-1} \oplus b_{j-h}$ includes the oldest bit, so it can be solved for it: a [linear feedback shift register](/topics/domain/linear-feedback-shift-register) over GF(2) |
| 225 Tribonacci non-divisors | $(T_{n-2}, T_{n-1}, T_n) \bmod m$ | $T_{n-3} = T_n - T_{n-1} - T_{n-2}$ needs no division, so the state can be run backwards: the [Pisano period](/topics/domain/pisano-period) idea for [Tribonacci](/topics/domain/tribonacci-number) |
| 238 infinite string tour | the [Blum Blum Shub](/topics/domain/blum-blum-shub) state $s \mapsto s^2 \bmod M$ | not guaranteed by the algebra; the solution *observes* that the orbit returns to the seed |

The practical payoff is the stopping rule. With a pure period there is no visited set and no
Floyd/Brent: you walk until the seed reappears, in $O(1)$ memory. Problem 238 is the cautionary
case. Squaring mod $M$ is not a bijection in general, so purity is a fact about this particular
seed, not a theorem. A seed-recurrence loop on a different input could run forever on a rho, which
is where you need [cycle detection](/topics/technique/cycle-detection) after all.

**It is derived from a constraint.** **Problem 743** counts $2 \times n$ binary matrices in which
every $2 \times k$ window sums to $k$. Two windows that overlap in all but one column share all but
one column sum, so the column sums satisfy $c_i = c_{i+k}$. The sequence of column sums is periodic
with period $k$, and nothing in the statement says so. This is the most reusable of the three
sources. Any "every window of length $k$ has property $P$" condition, when $P$ is a sum (or an XOR,
or any group operation), forces period $k$.

## What the period buys

**Index reduction.** Once you know $T$, the term at index $n$ is the term at index $n \bmod T$.
Problem 167 wants the $10^{11}$-th Ulam term. After one period of the bit recurrence, the work no
longer depends on $k$ at all. Its sequence is periodic *up to a shift*, though: the member values
in the next period are the previous ones plus $L$. So a lookup is a residue plus a translation.
Here it is in general form:

```python
# head: terms before the periodic part; block: one period; L: the shift per period
q, r = divmod(k - len(head) - 1, len(block))
term = block[r] + (q + 1) * L
```

The head needs care. Problem 167's two even members sit once at the start, outside the repeating
odd block. Merging them in, and counting how many terms come before the first full period, is the
off-by-one that the whole solution turns on.

**A finite decision.** Problem 225 asks whether $m$ divides *any* term of an infinite sequence.
Under periodicity that is a finite check: a zero residue either appears within one period or never
appears. The loop has exactly two exits (a zero, or the seed again), and purity guarantees that one
of them is reached.

**Shift-invariance of a derived quantity.** In problem 238 the periodicity is in the *digits*. What
the problem asks about is digit sums of substrings, and those are [prefix-sum](/topics/technique/prefix-sum)
differences. One block advances every prefix sum by the block's digit sum $S$, so
$P_{t+L} = P_t + S$, and so the function being summed satisfies $p(k) = p(k + S)$. The single
period of the generator becomes a period of $p$ in $k$, and a sum over $k$ up to $2 \times 10^{15}$
becomes a count over $S$ residue classes, each weighted by how often it occurs below $K$.

**Counting with multiplicities.** Problem 743 never builds a matrix. One period of $k$ slots carries
all the choices, and each slot recurs $q$ or $q+1$ times when $n = qk + s$. A slot with column sum 1
has two realisations per occurrence, so its weight is $2^{\text{occurrences}}$. The count is a
[generating function](/topics/domain/generating-function) over the period's slots, here a power of
a trinomial $(1 + bx + x^2)$. In general, when a structure is periodic, *count one period and give
each position its multiplicity*.

## How to reason about it

- **Look for the period before you look for the algorithm.** The giveaway is an index far beyond
  any loop ($10^{11}$, $10^{15}$), a finite state, or a sliding-window condition. Print the first
  few hundred terms. A period, or a period-up-to-shift, often shows up at once (see
  [small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence)).
- **Pure or eventually periodic?** Prove invertibility if you can, because it buys the
  seed-recurrence stop and removes the head. If you can't, keep a visited map or use Floyd/Brent,
  and handle the tail explicitly.
- **Know which unit the period is in.** Problem 167's period is $T$ steps in odd-index space, but
  $L = 2T$ in value space, with $C$ members per period. Problem 238's period is $L$ digits but $S$
  in digit-sum space. Confusing them gives answers that are right for small inputs and wrong once
  something wraps. The 238 notes record exactly this trap: deriving $S$ from `int.bit_length()` of
  the packed bit array is off by the trailing clear bits of the last digit's run. That is invisible
  until $K > S$.
- **Minimal period, or just a period?** For index reduction any period works. For "count per
  period" or "average over a period" it must be the period you actually measured, not a multiple.
  Problem 167 stops at the first recurrence of the seed, which is the minimal period.

## C and Python

Most of these ports are line for line, because a period walk is a tight loop over a few integers.
In problem 225 both sides keep three residues and test the same two exits. In problem 167 the
$h$-bit window is a `uint64_t` in C (with $h \le 22$) and a plain `int` in Python, and the shift,
XOR and mask are identical.

They differ where the languages offer different shortcuts:

- **Problem 19.** C carries the mod-7 residue itself, along with the leap-year rule. Python calls
  `datetime.date(y, m, 1).isoweekday()` and never sees the period. That is fine at 1 200 months.
  The C form is the one that scales to the 400-year reduction.
- **Problem 238.** Python packs one period's prefix-sum set into a single big integer. It builds
  that integer with one `str.translate` (each digit becomes a fixed run of bits) and rotates it with
  `(x >> p) | (x << (S - p))`, so CPython's big-int shifts do the per-word work. C has no
  arbitrary-width rotate. It stores the bit array twice, end to end, and reads each rotated word as
  a 64-bit window that spans two adjacent words. Doubling the period is the standard way to make
  the wrap-around into plain indexing. The same trick works for any cyclic buffer.
- **Problem 743.** Python reduces with `pow(x, MOD - 2, MOD)` on big integers. C uses a hand-rolled
  `power_mod` on `long long`. The period analysis leaves an $O(k)$ loop, and at that point the
  constant factor is the whole difference between the two.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0238](/solutions/0238/) — Infinite String Tour
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ○ [0349](/solutions/0349/) — Langton's Ant
- ○ [0426](/solutions/0426/) — Box-Ball System
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ○ [0729](/solutions/0729/) — Range of Periodic Sequence
- ● [0743](/solutions/0743/) — Window into a Matrix
- ○ [0843](/solutions/0843/) — Periodic Circles
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0993](/solutions/0993/) — Banana Beaver

<!-- /problems -->
