<!-- tags: [periodic-sequence] -->
<!-- status: final 2026-11-10T23:29Z -->
# Periodic sequence

A [periodic sequence](https://en.wikipedia.org/wiki/Periodic_sequence) satisfies
$a_{n+T} = a_n$ for some period $T \ge 1$. It is *eventually* periodic if that holds only past
some index $\mu$. Periodicity is worth looking for because it is the most direct way to turn an
infinite question, or one with an absurd index like $10^{14}$ or $10^{18}$, into a finite one.
Once you know $T$, everything about the sequence is decided by one period. The solved problems
below all make that move, but they get the period from five different places, they spend it in
several different ways, and in one of them the period is not a tool at all but the thing being
asked for. This page is about those choices. How to *detect* a cycle in an arbitrary iteration
(Floyd, Brent, the rho shape) belongs to [cycle detection](/blogs/technique/cycle-detection) and
[functional graph](/blogs/domain/functional-graph).

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
level up. Problem 506 is the same situation with the two periods interacting: its digit stream
`123432` repeats every 6 digits, but what matters is where each term *starts*, and that is a
running digit-sum offset. Every 6-digit window sums to 15, and the triangular offsets
$n(n-1)/2$ come back to the same residue mod 15 every 15 steps, so the *phase* of term $n$ has
period 15 even though the stream's period is 6.

**It is forced by finiteness.** A deterministic recurrence over a finite state space must
eventually repeat, by the [pigeonhole principle](/blogs/domain/pigeonhole-principle). If the step
map is also a [bijection](/blogs/domain/bijection), the sequence has no tail: it is *purely*
periodic, and the seed state is the first state to come back. Three of these problems rely on
that:

| problem | state | why the step is invertible |
|---|---|---|
| 167 Ulam sequences | the last $h$ membership bits of the odd numbers | the recurrence $b_j = b_{j-1} \oplus b_{j-h}$ includes the oldest bit, so it can be solved for it: a [linear feedback shift register](/blogs/domain/linear-feedback-shift-register) over GF(2) |
| 225 Tribonacci non-divisors | $(T_{n-2}, T_{n-1}, T_n) \bmod m$ | $T_{n-3} = T_n - T_{n-1} - T_{n-2}$ needs no division, so the state can be run backwards: the [Pisano period](/blogs/domain/pisano-period) idea for [Tribonacci](/blogs/domain/tribonacci-number) |
| 238 infinite string tour | the [Blum Blum Shub](/blogs/domain/blum-blum-shub) state $s \mapsto s^2 \bmod M$ | not guaranteed by the algebra; the solution *observes* that the orbit returns to the seed |

The practical payoff is the stopping rule. With a pure period there is no visited set and no
Floyd/Brent: you walk until the seed reappears, in $O(1)$ memory. Problem 238 is the cautionary
case. Squaring mod $M$ is not a bijection in general, so purity is a fact about this particular
seed, not a theorem. A seed-recurrence loop on a different input could run forever on a rho, which
is where you need [cycle detection](/blogs/technique/cycle-detection) after all.

The same argument covers any recurrence with **bounded lookback over a bounded alphabet**, even
one that is not a formula. **Problem 649** is a coin game on a board, and each axis is the
[subtraction game](https://en.wikipedia.org/wiki/Subtraction_game) with moves $\{2,3,5,7\}$. Its
[Grundy values](/blogs/technique/sprague-grundy-theorem) are defined by a mex over the previous 7
values, each of which is at most 4, so the window of the last 7 values is a finite state and the
sequence must cycle. Here it is $0,0,1,1,2,2,3,3,4$ repeating with period 9. The solution does not
hard-code that; it runs the mex rule until the opening window reappears. A mex is not invertible,
so this is the 238 caveat again: subtraction games are eventually periodic in general, and a
solution that only waits for the *opening* window is betting that the tail is empty.

**It is derived from a constraint.** **Problem 743** counts $2 \times n$ binary matrices in which
every $2 \times k$ window sums to $k$. Two windows that overlap in all but one column share all but
one column sum, so the column sums satisfy $c_i = c_{i+k}$. The sequence of column sums is periodic
with period $k$, and nothing in the statement says so. This is the most reusable source. Any "every
window of length $k$ has property $P$" condition, when $P$ is a sum (or an XOR, or any group
operation), forces period $k$. **Problem 767** applies it to every adjacent pair of rows of a
$16 \times n$ matrix, so each of the 15 pair-sum sequences is $k$-periodic at once.

**It is the arithmetic of a rational number.** A fraction $a/q$ has an eventually periodic
expansion in any base $b$, with period $\operatorname{ord}_q(b)$ when $\gcd(q, b) = 1$, the
[multiplicative order](/blogs/domain/multiplicative-order) of the base. The quick
way to see the digits is to rewrite the denominator as $b^N - 1$: then the numerator, written in
$N$ digits, *is* the repeating block. **Problem 889** evaluates the blancmange function at
$a/(2^k+1)$, and since $\frac{1}{2^k+1} = \frac{2^k-1}{2^{2k}-1}$, the binary expansion has period
$2k$: the $k$-bit form of $a-1$ followed by its complement. With $k \approx 10^{18}$ that period is
not something you walk, but knowing its exact shape is what the whole solution stands on.

**It is manufactured.** Any arithmetic function that depends only on *which of a fixed set of
primes* divide $n$ is periodic in $n$ with period their product, by the
[Chinese remainder theorem](/blogs/technique/chinese-remainder-theorem). **Problem 967**
needs, for every $n \le 10^{18}$, the sum mod 3 of the primes $\le 120$ that divide $n$. That is not
usefully periodic as stated (the product of all 30 primes is astronomical), so the solution
*chooses* where to cut. The seven smallest relevant primes have product $Q = 3\,233\,230$, so their
contribution is a periodic sequence with a table-sized period; the 22 larger primes go through a
sparse divisor sum. Moving the cut trades table size against the number of divisor terms. That is
the lesson: when a problem is not periodic, look for a part of it that is, and split there.

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

**Periodic up to an affine map.** Problem 506 generalises the translation. Because the phase
repeats every 15 terms, $v_{n+15}$ is read from the same place in the stream as $v_n$: it is $v_n$'s
digits followed by exactly one more full 6-digit block. So within each residue class mod 15,
$v_{n+15} = 10^6 v_n + Q_{n \bmod 15}$, an [affine](https://en.wikipedia.org/wiki/Affine_transformation)
recurrence rather than a shift. Unrolling it gives a [geometric series](/blogs/technique/geometric-series),
and *summing* the unrolled terms gives a second one, so $S(10^{14})$ is fifteen closed forms, one
per class, each a modular exponentiation. The pattern to recognise is "one period later, the term
is a fixed function of the term one period earlier": translation (167), scaling, or both (506) all
reduce to a per-class closed form, and a general affine step can always fall back to a $2 \times 2$
matrix power.

**A finite decision.** Problem 225 asks whether $m$ divides *any* term of an infinite sequence.
Under periodicity that is a finite check: a zero residue either appears within one period or never
appears. The loop has exactly two exits (a zero, or the seed again), and purity guarantees that one
of them is reached.

**Shift-invariance of a derived quantity.** In problem 238 the periodicity is in the *digits*. What
the problem asks about is digit sums of substrings, and those are [prefix-sum](/blogs/technique/prefix-sum)
differences. One block advances every prefix sum by the block's digit sum $S$, so
$P_{t+L} = P_t + S$, and so the function being summed satisfies $p(k) = p(k + S)$. The single
period of the generator becomes a period of $p$ in $k$, and a sum over $k$ up to $2 \times 10^{15}$
becomes a count over $S$ residue classes, each weighted by how often it occurs below $K$.

**An infinite sum folded onto one period.** Problem 889 does the same thing to an *infinite*,
geometrically weighted sum. It rewrites the blancmange function as $T(x) = \sum_q 2^{-q} c_q$,
where $c_q$ counts the earlier binary digits that disagree with digit $q$. Each period of the
expansion holds exactly $k$ ones and $k$ zeros, so every later period adds exactly $k$ to every
$c_q$. The copies of the period then sum as a geometric series, and the whole infinite sum
collapses to $k$ plus a weighted sum over the first $2k$ digits. That leaves one period which is
itself far too long to walk, and the second idea is to stop treating it as digits: $c_q$ is
constant along any run of equal digits, so each run contributes one closed-form term. The period
has $2 \times 10^{18}$ digits but only a few thousand runs. **When one period is too long, look
for structure inside it** — runs, blocks, a sparse set of positions — rather than a shorter period.

**Counting with multiplicities.** Problem 743 never builds a matrix. One period of $k$ slots carries
all the choices, and each slot recurs $q$ or $q+1$ times when $n = qk + s$. A slot with column sum 1
has two realisations per occurrence, so its weight is $2^{\text{occurrences}}$. The count is a
[generating function](/blogs/domain/generating-function) over the period's slots, here a power of
a trinomial $(1 + bx + x^2)$. In general, when a structure is periodic, *count one period and give
each position its multiplicity*. Two later problems stretch the move in different directions:

- **Problem 767** keeps the slots but makes each one richer. A residue class of $m$ columns, read
  down 16 rows, is either *mixed* (its rows alternate, $2^m - 2$ ways, and it adds exactly 1 to
  every pair sum) or *constant* in every row. The class weights depend only on $m \in \{q, q+1\}$,
  and the constant classes reduce to a Franel-type binomial sum, so the count is a pair of
  convolutions over the number of constant classes: $O(k \log k)$, with $n = 10^{16}$ appearing
  only inside the exponent $q$.
- **Problem 649** throws the positions away entirely. A coin's Grundy value depends on its
  coordinates only through $i \bmod 9$, so a board of side $10^7$ becomes an 8-entry *histogram*
  of values: each residue occurs $q$ or $q+1$ times, exactly as in 743. The 100 coins then combine
  by XOR-convolution powers of that histogram, and the board size never enters the loop. When only
  the *value* matters and the value is periodic, the period turns a coordinate space into a
  frequency table.

**Prefix sums in $O(1)$.** Problem 967 uses its manufactured period as an oracle. With one table of
partial sums over a single period,

$$G(y) = \lfloor y/Q \rfloor \, G(Q) + G(y \bmod Q),$$

any prefix count is two lookups. The outer divisor sum then calls $G(\lfloor N/d \rfloor)$ about
$1.4 \times 10^6$ times, which would be hopeless without it. This is the [prefix-sum](/blogs/technique/prefix-sum)
version of index reduction, and it composes: a periodic inner function makes *any* outer sum over
floor quotients cheap.

## When the period is the question

**Problem 843** turns the whole page around. A circle of $n$ integers is repeatedly replaced by the
absolute differences of each entry's neighbours; the orbit always becomes periodic, and the problem
asks for *every period that can occur*. Simulating starting circles cannot answer that, because
there are infinitely many, so the periods have to be derived.

Once periodic, every entry is $0$ or one common value, so the dynamics become a *linear* map over
GF(2): multiplication by $y = x + x^{-1}$ in $\mathrm{GF}(2)[x]/(x^n - 1)$. A linear map on a
finite space splits into a part where it is
[nilpotent](https://en.wikipedia.org/wiki/Nilpotent) and a part where it is invertible
([Fitting's lemma](https://en.wikipedia.org/wiki/Fitting_lemma)). The nilpotent part is the
*tail* — whatever lives there dies, which is why the sequence is only eventually periodic. The
invertible part is the *cycle*, and on each irreducible piece the period is the multiplicative
order of $y$ there, which the solution computes in finite fields $\mathrm{GF}(2^k)$. A state's
period is then the lcm of its components' periods, so the set of possible periods is the set of
lcms of subsets of those orders (times a power of two from the repeated factors).

Two general lessons fall out, and both apply backwards to the easier problems above. The period
of a linear recurrence over a finite ring is a **multiplicative order** — the Pisano period of
problem 225 is the order of a companion matrix. And periods of independent components **combine
by lcm**, so a period set is built from a few prime-power pieces rather than searched for.

## How to reason about it

- **Look for the period before you look for the algorithm.** The giveaway is an index far beyond
  any loop ($10^{11}$, $10^{18}$), a finite state, a sliding-window condition, or a rational
  argument. Print the first few hundred terms. A period, or a period-up-to-a-map, often shows up at
  once (see [small cases reveal the recurrence](/blogs/takeaway/small-cases-reveal-recurrence)).
- **If there is no period, make one.** Split off the part that depends on finitely many residues
  (problem 967's small primes) and tabulate it; handle the rest another way. The cut is a tuning
  knob, and moving it is also the best correctness check — 967 gets the same answer at very
  different cuts.
- **Pure or eventually periodic?** Prove invertibility if you can, because it buys the
  seed-recurrence stop and removes the head. If you can't (238, 649), keep a visited map or use
  Floyd/Brent, and handle the tail explicitly. In the linear case the tail is exactly the nilpotent
  part (843).
- **Know which unit the period is in.** Problem 167's period is $T$ steps in odd-index space, but
  $L = 2T$ in value space, with $C$ members per period. Problem 238's period is $L$ digits but $S$
  in digit-sum space; problem 506's is 6 digits but 15 terms. Confusing them gives answers that
  are right for small inputs and wrong once something wraps. The 238 notes record exactly this
  trap: deriving $S$ from `int.bit_length()` of the packed bit array is off by the trailing clear
  bits of the last digit's run. That is invisible until $K > S$.
- **Minimal period, or just a period?** For index reduction any period works. For "count per
  period" or "average over a period" it must be the period you actually measured, not a multiple.
  Problem 167 stops at the first recurrence of the seed, which is the minimal period. When the
  periods themselves are the answer (843), minimality is the whole problem.
- **Test across the period boundary.** Brute-force checks are cheap here and should straddle the
  wrap: problem 506 was checked at $n = 15, 16, 29, 30, 31$, exactly where a residue-class
  off-by-one would show.

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
- **Problem 506.** The number of periods is the large quantity: a class count $K_r$ reaches about
  $6.7 \times 10^{16}$ on the $10^{18}$ extra case. Python never notices; C must reduce $K_r$ modulo the modulus before using it
  in a subtraction, or the 64-bit arithmetic silently goes wrong.
- **Problem 967.** The period table is a sieve in Python: one NumPy slice assignment per small
  prime, `residue[::p] += p % 3`, over an array of length $Q$. The C port builds the same table,
  walks the large-prime products by depth-first search instead of building arrays, and uses
  `__int128` for the final expansion, where intermediate coefficients outgrow 64 bits even though
  the count does not.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0238](/solutions/0238/) — Infinite String Tour
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ○ [0349](/solutions/0349/) — Langton's Ant
- ○ [0426](/solutions/0426/) — Box-Ball System
- ● [0506](/solutions/0506/) — Clock Sequence
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0729](/solutions/0729/) — Range of Periodic Sequence
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0767](/solutions/0767/) — Window into a Matrix II
- ● [0843](/solutions/0843/) — Periodic Circles
- ● [0889](/solutions/0889/) — Rational Blancmange
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0993](/solutions/0993/) — Banana Beaver

<!-- /problems -->
