<!-- tags: [closed-form-over-iteration] -->
<!-- status: final 2026-10-29T02:13Z -->
# Prefer closed form over iteration

A loop that adds up a structured sequence is doing arithmetic the sequence has
already promised. When the terms follow a rule — an [arithmetic](https://en.wikipedia.org/wiki/Arithmetic_progression)
or [geometric progression](https://en.wikipedia.org/wiki/Geometric_progression),
a count of lattice paths, the corners of a spiral — that rule usually collapses
into a [closed-form expression](https://en.wikipedia.org/wiki/Closed-form_expression):
a fixed formula whose cost does not grow with the number of things it counts.
Often that means a constant number of operations; sometimes it means a short sum
— a few dozen terms standing in for $10^{12}$ cases. Across the problems below
the same move recurs — spot the structure, write the formula, delete the loop —
and it is the single highest-leverage habit these puzzles teach.

## What a closed form buys

The classic case is the sum $1 + 2 + \dots + n$. The obvious program is an
$O(n)$ accumulation; the [Gauss summation](https://en.wikipedia.org/wiki/1_%2B_2_%2B_3_%2B_4_%2B_%E2%8B%AF)
pairs the ends — $1 + n$, $2 + (n-1)$, … — to give $\tfrac{n(n+1)}{2}$ in a
handful of operations that never grow with $n$. That $n$-th
[triangular number](https://en.wikipedia.org/wiki/Triangular_number) is the seed
of a whole family. [Multiples of 3 or 5](/solutions/0001/) sums three arithmetic
runs with it and combines them by
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
($3 + 5 - 15$), turning a scan of the whole range into one line:

```python
def sum_arithmetic_series(d, *, max_limit):
    n = (max_limit - 1) // d
    return d * (n * (n + 1)) // 2
```

[Sum Square Difference](/solutions/0006/) folds the same triangular number
together with the [square-pyramidal](https://en.wikipedia.org/wiki/Square_pyramidal_number)
sum $\tfrac{n(n+1)(2n+1)}{6}$, so $\left(\sum k\right)^2 - \sum k^2$ becomes a
single expression evaluated in $O(1)$. [Lattice Paths](/solutions/0015/) reads
the grid as a counting problem — every route is a sequence of moves, so the
number of them through an $n \times n$ grid is the
[central binomial coefficient](https://en.wikipedia.org/wiki/Central_binomial_coefficient)
$\binom{2n}{n}$ — and [Number Spiral Diagonals](/solutions/0028/) sums each
ring's four corners into $\tfrac{N(N(4N+3)+8)-9}{6}$ instead of laying out the
$N \times N$ grid.

The payoff is not a constant factor. Dropping from $O(n)$ (or an $O(n^2)$
enumeration) to $O(1)$ changes the shape of the running time — it is the same
lever the [algorithm-beats-language](/topics/takeaway/algorithm-beats-language)
takeaway pulls, taken to its limit, where the work stops growing with the input
at all. Larger problems reach for heavier closed forms — a matrix recurrence
solved by [fast exponentiation](https://en.wikipedia.org/wiki/Exponentiation_by_squaring),
a [generating function](https://en.wikipedia.org/wiki/Generating_function), a
combinatorial identity — but the principle is one and the same: let the
structure do the counting.

## Closed forms as building blocks

In the harder problems the formula rarely *is* the answer. It is a component —
the part of the computation that would otherwise be the inner loop — and the
surrounding algorithm is designed around having it. Five shapes recur.

**A formula per item, in place of a search per item.**
[Divisibility Multipliers](/solutions/0274/) asks, for every prime $p$ coprime
to 10, for the smallest multiplier $m$ that preserves divisibility under a
digit-shuffling map. The obvious program tries $m = 1, 2, \dots$ for each prime.
A line of algebra shows the condition is $10m \equiv 1 \pmod p$ — $m$ is the
[modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
of 10 — and that inverse has a closed form, $(kp+1)/10$, with $k$ read off a
four-entry table by $p$'s last digit. The outer sum over primes remains; the
per-prime search is gone, and what is left vectorises into one array expression.

**A formula for the full blocks, iteration only along the boundary.** Counting
up to an arbitrary bound $N$ rarely closes in one formula, but the count over a
*complete* block — all $b$-bit numbers, all $D$-digit numbers — usually does.
[Odd Triplets](/solutions/0242/) reduces, through
[Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem), to summing
$2^{\operatorname{popcount}(t)}$ over $t \le T$; over a free block of $b$ bits
that sum is exactly $3^b$ (each bit contributes a factor $1 + 2$). Walking the
bits of $T$ from the top, every 1-bit closes off one full block, so a sum over
a quarter of a trillion values takes under forty steps. [Reflexive Position](/solutions/0305/)
uses the same split on decimal digits: occurrences of a string inside a
$D$-digit integer at a fixed offset leave the other digits free, a power of 10
apiece, and only the top length needs a comparison against $N$. This is the
skeleton of a [digit DP](https://en.wikipedia.org/wiki/Dynamic_programming),
with the closed form doing the work the memo table would.

**A cheap count you can invert.** Once "how many up to $N$" costs
$O(\log N)$, "where is the $n$-th one" is a
[binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) over a
monotone function — which is how Reflexive Position locates the $n$-th
occurrence of $n$ in the Champernowne string without ever writing the string
out. The closed form did not answer the question; it made the question
searchable.

**A formula at the leaves of a quotient recursion.**
[Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula)
over the floor quotients $\lfloor n/d \rfloor$ — the engine behind
[Primitive Triangles](/solutions/0276/) and [Bounded Sequences](/solutions/0319/)
— evaluates some summatory function at only $O(\sqrt n)$ distinct arguments,
which is sublinear *only if* each evaluation is cheap. Primitive Triangles needs
the count of all integer triangles with perimeter $\le v$: that is a prefix sum
of [Alcuin's sequence](https://oeis.org/A005044), $\operatorname{round}(k^2/12)$,
and the rounding, being periodic in $k \bmod 12$, folds into the
square-pyramidal sum as a correction term — $O(1)$ per quotient, $O(n^{3/4})$
overall. Bounded Sequences reduces its count to $F(m) = \sum_{h \le m} (3^h - 2^h - 1)$,
two geometric series evaluated with modular exponentiation at each large
quotient. Without these leaf formulas each method would be a linear scan in
disguise.

**A formula for a process, read off a small run of it.** Some problems do not
hand you a sequence at all. They hand you a *procedure*, a recursion or a greedy
rule, and the closed form is something you discover. [Crazy Function](/solutions/0340/)
generalises the [McCarthy 91 function](https://en.wikipedia.org/wiki/McCarthy_91_function):
above a threshold $b \approx 5.6 \times 10^{17}$ it subtracts a constant, and
below it the call nests four deep. Taken literally that is unbounded recursion
summed over $b+1$ arguments. A memoised brute force on small parameters shows
the pattern. Cut $[0, b]$ into blocks of width $a$ counted down from $b$. Then
$F(n)$ is $n$ plus a fixed offset plus one constant increment per block, and
induction on the block index proves it. Summing an affine function block by
block brings back the Gauss sum, and the whole problem becomes $O(1)$.
[Hilbert's New Hotel](/solutions/0359/) is the greedy version. Guests take the
first floor where they sum to a perfect square with the previous occupant, and
the question needs occupants of order $10^{27}$. Simulating forty thousand
guests shows the rigid structure. Neighbouring rooms sum to *consecutive*
squares, so two rooms apart the squares telescope,
$P(f, r+2) - P(f, r) = (s+1)^2 - s^2 = 2s + 1$, which is linear in $r$. That
makes each floor a quadratic in the room number, and the requested sum shrinks
to a few hundred formula evaluations over the divisors of $N$. In both problems
the brute force is a microscope rather than the solution. It shows you the
pattern, a proof makes the pattern safe to use, and the formula replaces the
process.

The plainest variant is a sum that is short rather than constant.
[Twenty-two Foolish Primes](/solutions/0239/) asks a probability over all $100!$
permutations; [inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
over which displaced discs are nevertheless fixed gives an alternating sum of
binomial-times-factorial terms — the
[derangement](https://en.wikipedia.org/wiki/Derangement) formula, generalised —
with as many terms as there are displaced discs. Twenty-three exact
big-integer terms replace an enumeration no computer could finish.

## How to reason about it

Reach for a closed form when the quantity you are accumulating is *structured* —
the terms obey a recurrence or an algebraic rule, not arbitrary data. The tells
are concrete: an arithmetic or geometric run, a triangular / pyramidal / binomial
count, a sum over a regular grid, a linear recurrence with constant coefficients,
a count over all numbers with a fixed number of digits or bits, or a term that
is a polynomial up to a periodic wobble (floors and rounds of $k^2/c$).
When the summand is genuinely irregular — the rectangle counts scanned in
[Counting Rectangles](/solutions/0085/), where the search stops at the shape
nearest a target — no formula collapses the whole thing, and iteration is the
honest answer. The skill is telling the two apart: derive on paper first, and if
the algebra does not close, do not force it.

Four cautions earn their keep:

- **Derive, then verify.** A closed form is only as good as its derivation; an
  off-by-one in the bounds or a dropped term is silent. Keep a brute-force
  version as an oracle and check them against each other on small inputs —
  [Number Spiral Diagonals](/solutions/0028/) ships exactly that, running an
  $O(N^2)$ spiral simulation under `--show` purely to confirm the formula.
  When the formula came *from* the brute force, as in Crazy Function and
  Hilbert's New Hotel, checking it on the same few cases proves nothing. Test
  it on fresh ones: Crazy Function was checked on 400 random parameter
  triples, and Hilbert's New Hotel on every room the simulation filled.
- **Mind the arithmetic.** Formulas multiply before they divide, so intermediate
  values can be far larger than the answer — a real overflow risk in C, and a
  reason to prefer exact integer arithmetic (Python's big integers, or careful
  ordering so the division is exact) over anything that rounds. Division is the
  sharp edge. Under a modulus the halving in $(3^{m+1} - 3)/2$ is not a plain
  division; Bounded Sequences works modulo $2M$, where the residue stays even,
  and halves that. Crazy Function, working modulo $10^9$ where 2 has no
  inverse, halves whichever factor of $n(n+1)$ is even *before* it reduces. A `round` inside the summand, as in Alcuin's sequence, is
  not something to evaluate in floating point term by term; Primitive Triangles
  folds it into a periodic integer correction. Twenty-two Foolish Primes keeps
  its probability as an exact ratio of two big integers and rounds to twelve
  decimals in integer arithmetic.
- **A formula is worth deriving once and reusing.** The triangular and
  pyramidal-number identities recur across many of the problems below; naming
  them as small helpers, as these solutions do, keeps each new use a one-liner
  rather than a fresh derivation.
- **Closed form is not always cheaper per call.** When you need a formula at
  every small argument in order, a running total costs $O(1)$ per step, while
  re-evaluating the formula can cost more (a modular power each time). Bounded
  Sequences accumulates $F$ incrementally below $\sqrt n$ and switches to the
  closed form only for the scattered large quotients. Use the formula where it
  lets you skip arguments, and plain iteration where you visit every one
  anyway.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0099](/solutions/0099/) — Largest Exponential
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0232](/solutions/0232/) — The Race
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0868](/solutions/0868/) — Belfry Maths
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0932](/solutions/0932/) — $2025$
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
