<!-- tags: [pseudorandom-number-generator] -->
<!-- status: final -->
# Pseudorandom number generator

A [pseudorandom number generator](https://en.wikipedia.org/wiki/Pseudorandom_number_generator)
(PRNG) is a deterministic recurrence whose output *looks* random: a hidden state, a step function
that scrambles it, and a projection from state to output. Nothing about it is random — fix the seed
and you get the same stream on every machine, in every language, forever. That is precisely why the
archive uses one so often. When a problem needs two million points, ten million array entries, or a
string of unbounded length, it cannot ship a data file; instead it ships three lines of recurrence
and lets you generate the input yourself. The generator is a **compressed input format**, and the
problems on this page are the ones that read it.

## The generators in play

Four families cover almost everything here.

| Family | Shape | Where it shows up |
| --- | --- | --- |
| Quadratic / [Blum Blum Shub](https://en.wikipedia.org/wiki/Blum_Blum_Shub) | $s_{n+1} = s_n^2 \bmod M$ | the house generator, $s_0 = 290797$, $M = 50515093$ — problems 252, 288, 375, 630, 790, 793, 816, 839, 917; problem 238 uses its own modulus |
| [Linear congruential](https://en.wikipedia.org/wiki/Linear_congruential_generator) | $a_n = (A a_{n-1} + C) \bmod M$ | 803 (Rand48, $M = 2^{48}$), 941 ($M = 10^{12}$), 980 (multiplicative, prime modulus) |
| [Lagged Fibonacci](https://en.wikipedia.org/wiki/Lagged_Fibonacci_generator) | $s_k = (s_{k-24} + s_{k-55} + C) \bmod M$ | 149, seeded by a cubic polynomial |
| Shift-and-xor | halve; xor a constant when odd | 334, a [linear-feedback](https://en.wikipedia.org/wiki/Linear-feedback_shift_register)-flavoured stream |

Problem 456 is the outlier that proves the rule: its points come from $x_n = 1248^n \bmod 32323$,
a plain [modular exponentiation](/topics/technique/modular-exponentiation) whose successive powers
scatter across the range well enough to serve as pseudorandom coordinates.

Whatever the family, the raw state is rarely the payload. A **projection** narrows it to the range
the problem wants — $S_n \bmod p$ for a base-$p$ digit (288), $(S_n \bmod 2000) - 1000$ for a
coordinate in a square (252, 630), $\lfloor a_n / 2^{16} \rfloor \bmod 52$ for a letter (803),
$a_n \bmod 3$ for one of three symbols (980). Pairing consecutive outputs, $(s_{2n}, s_{2n+1})$,
turns a scalar stream into a stream of points (816, 917).

## Reproducing the stream is a correctness problem

The generator is given, so getting it wrong is not a slow answer but a wrong one — and a wrong
answer with no symptom, since a corrupted pseudorandom stream still looks pseudorandom. Three
things go wrong in practice.

**Indexing.** Sequences start at $s_0$ or $s_1$ depending on the problem, and "the first $n$ points"
may consume $2n$ terms. Check the worked example the statement gives (it always gives one) before
trusting a single downstream number.

**Overflow in C.** The house generator squares a state below $50515093$, and $50515093^2 \approx
2.6 \times 10^{15}$ fits comfortably in a 64-bit integer — but only just, and the same code with a
larger modulus silently wraps. An LCG is the sharper trap: `A * state` for Rand48-sized constants
overflows 64 bits outright. It happens to be harmless there, because the modulus is a power of two
and unsigned wraparound is itself a reduction modulo $2^{64}$, so the low 48 bits survive intact.
That is a property of that modulus, not a general licence. For a non-power-of-two modulus you need a
wider type or a reduction that never forms the full product.

**Materialising what you could stream.** Some problems genuinely need the whole array — problem 149
scans four million entries in four directions, so the grid is built. Most do not: 375, 793 and 839
consume their streams once, in order, and the right shape is a loop that keeps one state variable.

```python
state = seed
for _ in range(n):
    state = (state * state) % MOD      # one 64-bit state, no array
    consume(state % span - offset)     # project as the statement specifies
```

## What "random" buys you

Once you accept the stream as random, its **statistics become part of the algorithm** — and this is
where these problems get interesting, because the intended solutions do not merely tolerate the
randomness, they exploit it.

*Uniformity.* Problem 288 needs the base-$p$ digits of an unimaginably large number, and the digits
are $S_n \bmod p$ — uniform by construction, so the digit sum that [Legendre's
formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) wants is accumulated in one pass with
no representation of the number itself. Problems 252, 456 and 630 scatter points over a rectangle
uniformly enough that geometric structure — a convex hull, an angular sort, a line arrangement —
behaves as the average case rather than an adversarial one.

*Random order.* This is the strongest gift and the easiest to miss. Several classical algorithms are
fast in expectation only when the input arrives in random order, and normally you pay for that with
an explicit shuffle. A PRNG stream is already shuffled. Problem 816 asks for the
[closest pair](/topics/domain/closest-pair-of-points-problem) among two million generated points;
the [randomized incremental algorithm](/topics/technique/randomized-incremental-algorithm) inserts
points one at a time into a [uniform grid](/topics/technique/grid-spatial-index) whose cell size is
the current best distance, and runs in expected $O(k)$ — better than the $O(k \log k)$
divide-and-conquer method — *because* the arrival order is random. No shuffle, no cost.

*Bounded magnitude.* A projection into $[0, M)$ caps every value, which is what makes counting
sorts, bucket structures and fixed-width arithmetic safe. Knowing the range is knowing the data
structure.

## When the generator becomes the subject

A PRNG has finite state and a deterministic step, so its orbit is eventually periodic — the classic
$\rho$ shape, a tail leading into a cycle. Usually the period is far beyond the terms you consume
and you can ignore it. Sometimes it *is* the problem. Problem 238 concatenates a Blum Blum Shub
stream into an infinite string and asks a question over $2 \times 10^{15}$ positions; the sequence
turns out to be a pure cycle with no tail, and the whole solution rests on finding that period and
reasoning about one repeating block. That is [cycle detection](/topics/technique/cycle-detection) —
Floyd, Brent, or simply iterating back to the seed — promoted from footnote to method.

The other way the generator becomes the subject is **inversion**. Problem 803 gives you a Rand48
stream and a prefix of its output and asks you to recover the seed. An LCG is trivially invertible
when you know its constants: the step is an affine map modulo $M$, so run it backwards with the
[modular inverse](/topics/domain/modular-multiplicative-inverse) of the multiplier. Note what that
problem's projection is doing — it discards the low 16 bits, because in an LCG with modulus $2^{48}$
the bottom $k$ bits have period only $2^k$ and are visibly non-random. The generator is designed
around its own weakness, and the problem is designed around that design.

## Randomness as a tool, not just as input

The tag also covers the reverse direction: a solution that reaches for a PRNG the statement never
mentions. Problem 185 (Number Mind) is a constraint-satisfaction puzzle with a $10^{16}$ search
space and no PRNG anywhere in its statement; the practical attack is
[simulated annealing](/topics/technique/simulated-annealing) — score a candidate by squared
deviation from the clue counts, mutate one digit at a time, and accept an uphill move with
probability $e^{-\Delta/T}$. That needs a stream of random numbers, and the discipline is to make it
a *seeded* one:

```python
rng = random.Random(SEED)   # reproducible run, reproducible benchmark
```

An unseeded search gives a different runtime, and possibly a different failure, on every run — which
makes it untestable and unbenchmarkable. Fix the seed and a stochastic algorithm becomes an ordinary
deterministic program that happens to explore cleverly.

## How to reason about it

- **Read the generator as an input format.** Transcribe the recurrence, the seed, the start index
  and the projection exactly, then verify against the statement's worked example before writing
  anything downstream.
- **Stream unless you must store.** One state variable and a loop is the default; materialise the
  full sequence only when the algorithm genuinely needs random access to it.
- **Watch the width.** Squaring or multiplying the state is where fixed-width arithmetic breaks.
  Bound the intermediate product on paper; do not assume a power-of-two modulus will save you.
- **Ask what the randomness lets you assume.** Uniform values, uniform positions, and random arrival
  order each unlock a different class of expected-case algorithm. That assumption is usually the
  intended solution, not a shortcut.
- **Consider the period.** Finite state means eventual repetition. If the term count is astronomical
  while the modulus is merely large, find the cycle — the answer is on it.
- **Seed anything you randomise yourself.** Reproducibility is worth more than entropy in a
  benchmarked solution.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0185](/solutions/0185/) — Number Mind
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0375](/solutions/0375/) — Minimum of Subsequences
- ○ [0426](/solutions/0426/) — Box-Ball System
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0630](/solutions/0630/) — Crossed Lines
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0790](/solutions/0790/) — Clock Grid
- ○ [0793](/solutions/0793/) — Median of Products
- ○ [0803](/solutions/0803/) — Pseudorandom Sequence
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ○ [0839](/solutions/0839/) — Beans in Bowls
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ○ [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ● [0980](/solutions/0980/) — The Quaternion Group I

<!-- /problems -->
