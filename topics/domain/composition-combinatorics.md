<!-- tags: [composition-combinatorics] -->
<!-- status: final 2026-10-14T07:25Z -->
# Composition (combinatorics)

A [composition](https://en.wikipedia.org/wiki/Composition_(combinatorics)) of $n$ is an *ordered*
tuple of positive integers that sums to $n$. $(1,2)$ and $(2,1)$ are different compositions of $3$,
where they would be the same [partition](/topics/domain/partition-number-theory). That one word,
*ordered*, makes compositions far easier to count than partitions, and it is why they keep turning
up. Hardly any of the problems below says "composition". They talk about a string of digits cut
into pieces, a caterpillar half put together, a shuffled deck of red and black cards, a row of
tennis players. Each of these, once you look closely, is a line of things cut into consecutive
blocks, and the block lengths form a composition.

## The idea

Lay $n$ unit cells in a row. There are $n-1$ gaps between neighbours, and a composition is just a
choice of which gaps to cut. Every count I need follows from that picture:

| Object | Count | Why |
| --- | --- | --- |
| compositions of $n$ | $2^{n-1}$ | each of the $n-1$ gaps is cut or not |
| into exactly $k$ parts | $\binom{n-1}{k-1}$ | choose $k-1$ of the $n-1$ gaps |
| *weak* (parts $\ge 0$), $k$ parts | $\binom{n+k-1}{k-1}$ | [stars and bars](/topics/technique/stars-and-bars-combinatorics) |
| palindromic | $2^{\lfloor n/2 \rfloor}$ | the cuts must be symmetric, so only half are free |
| parts drawn from a set $S$ | $c(n) = \sum_{s \in S} c(n-s)$ | condition on the first part |

The last row is the general one. Conditioning on the first part turns any restriction on part
*values* into a short [dynamic programme](/topics/technique/dynamic-programming), or equivalently
into the [generating function](/topics/domain/generating-function) $1/(1 - S(x))$, where $S(x)$ is
the sum of $x^s$ over the allowed part sizes:

```python
c = [1] + [0] * n                 # c[0] = 1: the empty composition
for m in range(1, n + 1):
    c[m] = sum(c[m - s] for s in allowed if s <= m)
```

When $S$ is finite, or "all integers except a few", that recurrence is a
[linear recurrence with constant coefficients](/topics/technique/linear-recurrence-with-constant-coefficients),
and huge $n$ is reached by matrix power or by working modulo the requested modulus.

## Where it hides

The work in these problems is mostly *seeing* the composition. Three shapes come up again and
again.

**A string cut into pieces.** Problem 719 asks whether the decimal digits of $k^2$ can be split
into contiguous groups that sum to $k$. The ways to split a $d$-digit string are the compositions
of $d$, so there are $2^{d-1}$ of them. That is tiny for $d \le 12$, and it tells you a
backtracking search over cuts is the right tool. Problem 845 runs it the other way round: the
length-$L$ digit strings whose digits sum to $s$ are the weak compositions of $s$ into $L$ parts,
each part at most $9$. Counting those with a table indexed by position and sum is
[digit DP](/topics/technique/digit-dp) in its plainest form. Problem 862 keeps only the digit
*counts* $(c_0,\dots,c_9)$, a weak composition of the length $k$ into ten parts, and enumerates
all $\binom{k+9}{9}$ of them in place of the $10^k$ numbers.

**Runs.** Every sequence over a small alphabet is described by its
[run-length encoding](/topics/technique/run-length-encoding), and the run lengths form a
composition. Problem 929 says this outright (compositions whose runs all have odd length). In the
others you have to find it yourself:

- In problem 951 the deck of $n$ red and $n$ black cards alternates colour from one run to the
  next, so it is a pair of compositions of $n$ (red run lengths and black run lengths), interleaved.
  No turn ever spans two runs, so the game's parity bias *factorises* over the runs. The question
  then becomes counting compositions that do or do not contain a part equal to $2$.
- In problem 253 a half-built caterpillar is $s$ placed runs alternating with empty gaps. Once the
  number of pieces, the number of segments and the two boundary flags are fixed, every fill state
  is a composition of the placed count into run lengths paired with an independent composition of
  the empty count into gap widths. The state that seemed to need an integer partition collapses
  to a few small integers and a [binomial coefficient](/topics/domain/binomial-coefficient).
- In problem 996 a player with zero overtakes is a wall nobody can pass, so the count tuple splits
  at its zeros into independent runs. Each run then gets its own constraint (length at least
  $2$, even sum, no entry above half the sum).

**A symmetric or restricted composition.** Problem 710 counts palindromic compositions that
contain a $2$. A palindrome is fixed by its first half plus an optional middle part, so it is
an ordinary composition of the half-sum. "At least one $2$" is handled by
[complement](/topics/technique/inclusion-exclusion-principle): all of them, minus those that avoid
$2$, where the second count is the restricted-parts recurrence above. Problem 606 meets
compositions through divisor chains: for a prime power $p^a$, a chain $1 \mid d_1 \mid \dots \mid
p^a$ with strict steps is a composition of the exponent $a$, so there are $2^{a-1}$ of them.
General $n$ turns this into compositions of an exponent *vector*. Problem 398 is the continuous
version: $m-1$ random cuts in a rope give a uniformly random point on the simplex of
real compositions of the length, and the order statistics of those spacings are what the
problem asks about.

## How to reason about it

- **Look for a line cut into consecutive blocks.** Digit strings, card decks, seat rows, run
  lengths, gaps between occupied cells. If order matters and the blocks are contiguous, you are
  counting compositions, and $2^{n-1}$ and $\binom{n-1}{k-1}$ are already known.
- **Check whether the parts can be zero.** Compositions (parts $\ge 1$) and weak compositions
  (parts $\ge 0$) differ by a shift of $k$, so an off-by-one there quietly changes every count.
  Digit vectors and gap widths at a boundary are usually weak. Runs are not.
- **Turn "at least one" into a complement.** "Contains a $2$", "has a run of length $2$" and
  "some part is odd" are awkward. "Avoids" is a clean restricted-parts recurrence, so subtract.
- **Factor over the blocks.** When a process acts on each block independently, as in problems
  951 and 996, the weight of the whole is a product over the parts. A product over the parts of a
  composition is exactly what $1/(1 - W(x))$ adds up, with $W$ the weight of one part.
- **Separate independent halves.** Alternating structures (runs and gaps, red and black) are
  often a *pair* of compositions chosen independently. Count each half on its own and multiply,
  as problem 253 does.
- **Know when it is not a composition.** If $(1,2)$ and $(2,1)$ should count once, you have a
  partition, and none of the easy formulas apply.

The common thread: once a problem's line of objects is seen as cuts between cells, the counting
is mostly done. The remaining work is the one constraint that makes the problem its own, whether
on part sizes, run lengths or symmetry.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0253](/solutions/0253/) — Tidying Up A
- ○ [0398](/solutions/0398/) — Cutting Rope
- ○ [0502](/solutions/0502/) — Counting Castles
- ○ [0606](/solutions/0606/) — Gozinta Chains II
- ● [0710](/solutions/0710/) — One Million Members
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
