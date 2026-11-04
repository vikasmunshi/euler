<!-- tags: [recurrence-relation-application] -->
<!-- status: final -->
# Recurrence relation (application)

This is the **technique** side of the [recurrence relation](/topics/domain/recurrence-relation) —
not problems that are *about* a sequence, but problems about binomial coefficients, Pell equations,
tilings, permutations, factorials and elimination games, whose solutions all reach for the same
implementation move: stop evaluating a quantity at each index and start *stepping* it from the
previous one. The recurrence is nowhere in the statement. Finding one is the optimisation.

The domain page covers where recurrences come from and how to evaluate one at an enormous index.
This page is about the smaller, more frequent decision: recognising that the thing you are about to
recompute in a loop differs from the last value by something cheap.

## Step a formula instead of evaluating it

Problem 53 counts binomial coefficients above a threshold. Computing each $\binom{n}{r}$ from
factorials is an enormous amount of arithmetic thrown away immediately; adjacent entries in a Pascal
row are related by a ratio, so the row is one multiply and one divide per step:

```python
c = 1
for r in range(0, n // 2 + 1):
    if c > threshold:
        count += n - 2 * r + 1
        break
    else:
        c = c * (n - r) // (r + 1)
```

Two details carry more weight than they look. The division is **exact at every step** — the
intermediate $\binom{n}{r}(n-r)$ is always divisible by $r+1$ — so `//` is safe and no
`fractions.Fraction` is needed; and the multiplication must come *first*, because
`c // (r + 1) * (n - r)` truncates. The same move appears in problem 650, which advances a prime
power $p^{e}$ across successive $k$ by the *change* in its valuation rather than recomputing the
valuation, letting one vectorised multiply update every prime at once; and in problem 720, whose
factorial-base rank is accumulated by Horner's rule, `acc = (d + mult * acc) % m`, so the factorials
themselves are never formed.

Sometimes a quantity steps cleanly only after it is rescaled. Problem 374's block sums need the
[harmonic numbers](https://en.wikipedia.org/wiki/Harmonic_number) $H_j$ modulo a prime, and stepping
$H_j$ directly costs a modular inverse of $j$ at every index. The product $A_j = j!\,H_j$ has no
such problem. It is an integer, and

$$A_j = j\,A_{j-1} + (j-1)!,$$

so one pass that carries $j!$ alongside it produces both, with no division anywhere in a loop of
some $10^7$ steps. A sequence of fractions is expensive because of its denominators, so multiply
them out before you recur, not after.

A formula with two indices steps too, one axis at a time. Problem 423 needs the truncated binomial
sum $F(m, k) = \sum_{c \le k} \binom{m}{c} x^{m-c}$ for every $n$ up to $5 \times 10^7$, at
$m = n - 1$ and $k = \pi(n)$. Evaluated afresh, that is millions of terms per $n$. Treat $(m, k)$ as
a point in the plane instead, and each axis has a cheap move. Pascal's rule advances $m$, and raising
the cut-off adds one term:

$$F(m+1, k) = (x+1)\,F(m, k) - T(m, k), \qquad F(m, k+1) = F(m, k) + T(m, k+1),$$

where $T(m, k) = \binom{m}{k} x^{m-k}$ is the boundary term, a single lookup in a factorial table.
The input then dictates the path: $m$ moves on every step, $k$ only when $n + 1$ is prime. A sum of
unbounded width costs $O(1)$ per step, because each move only touches its edge. What the solution
does with the resulting first-order recurrence is the
[unrolling](/topics/domain/recurrence-relation) trick on the domain page.

## Walk the solution set instead of searching it

The largest family here. When a constraint reduces to a quadratic form, its integer solutions are
not scattered — they form an orbit under a fixed linear map, so you enumerate the *answers* instead
of filtering candidates. Problem 100 is the public exhibit: the probability condition rearranges to
the [Pell equation](/topics/technique/pells-equation) $x^2 - 2y^2 = -1$, and

```python
x, y = (1, 1)
while True:
    x, y = (3 * x + 4 * y, 2 * x + 3 * y)
```

reaches $10^{12}$ in about forty iterations. The alternative — scan $n$, test whether a
discriminant is a perfect square — is $O(N)$ against $O(\log N)$, and the *same* substitution
underlies problems 137, 138 and 321, each with a different fundamental unit and a different
extraction of the answer from $(x, y)$. Problem 137 is the pretty case: the orbit turns out to be
consecutive Fibonacci products, so the ladder collapses to plain addition.

Problem 582 runs the same walk with a right-hand side that is not $\pm 1$, which raises the question
of where to start. Fixing the difference $d$ of two sides turns the law of cosines into
$X^2 - 3Y^2 = d^2$, one equation per $d$, each with one or more orbits of the map
$(X, Y) \mapsto (2X + 3Y,\ X + 2Y)$. The [Pell page](/topics/technique/pells-equation) bounds such
seeds with classical theory, but here the map bounds them itself. A square right-hand side hands
you the trivial solution $(d, 0)$, whose image has $Y = d$. Since the map preserves the order of $Y$
along the branch, the strip $0 \le Y < d$ holds exactly one point of every orbit, and testing those
$d$ values for a perfect square finds every seed. The walk also passes through points that are not
triangles (wrong parity, or a side that is not positive), so the code checks each point as it goes
rather than deriving which orbits qualify. A check costs one comparison. A missed parity case costs
the answer.

Convergents of a [continued fraction](/topics/domain/continued-fraction) are the same idea without
the Diophantine framing. Problem 57 advances the $\sqrt 2$ convergents with
`numerator, denominator = (numerator + 2 * denominator, numerator + denominator)`, and problem 65
builds the convergents of $e$ from its partial-quotient pattern. In both, the recurrence replaces an
expression that would otherwise be rebuilt from scratch at every index.

## Recur on the index's digits

A recurrence whose arguments are $2m$ and $2m+1$ — or whose quantity decomposes over positional
digits — costs $O(\log n)$, not $O(n)$. Problem 169 counts representations of $n$ as sums of powers
of two using each power at most twice; it reads the bits of $n$ from the top down, carrying the pair
$(f(m), f(m-1))$ for the prefix built so far and applying one of two linear maps per bit. Problem 148
does the base-7 version for Pascal entries not divisible by 7, keeping a running "value so far" and a
running block weight; problem 230 descends the *lengths* of a self-similar string rather than the
string. The tell is a quantity that is a function of a number's representation in some base — then
the recurrence runs over digits, and the index size stops mattering.

When the question is a *sum* over $0 \le n < N$ rather than one value, the recurrence moves from the
digits to the **blocks** they delimit. Problems 297 and 692 both work in the
[Zeckendorf](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem) (Fibonacci) base. Every $n$ in
$[F_i, F_{i+1})$ is $F_i + m$ with $m < F_{i-1}$, so the block is a shifted copy of a smaller
prefix, and the prefix sums $T_i$ over $[0, F_i)$ obey a three-term recurrence. The limit $N$ is
then peeled greedily, one Zeckendorf term at a time, and each term adds a whole $T_i$ plus a
correction for the numbers that carry $F_i$ as their leading term:

$$S(N) = T_i + c(F_i, N) + S(N - F_i).$$

The two problems share this skeleton line for line and differ only in $c$. Problem 297 counts terms,
so every $n \ge F_i$ gains exactly one and $c = N - F_i$. Problem 692 sums the *least* term, which
the leading $F_i$ only sets when nothing lies below it, so the correction collapses to the single
number $n = F_i$ and $c = F_i$. That is the reusable part: the block
recurrence and the greedy peel are fixed, and the problem's function only enters through how one
leading digit changes it. Problem 148's base-7 count has the same shape with powers of 7 for the
blocks. In every case about $\log_\varphi N$ (or $\log_7 N$) steps replace $N$ evaluations.

A halving recurrence offers a second route to the sum, with no blocks at all: **sum the recurrence
itself**. Problem 539's survivor comes from a process, not a formula. One sweep of the elimination
game leaves $2, 4, \dots, 2M$ with $M = \lfloor n/2 \rfloor$, and the next sweep runs the other way,
which is the original game on $M$ items read backwards. Mirroring the position and doubling the
value gives

$$P(n) = 2\bigl(M + 1 - P(M)\bigr).$$

The statement wants $\sum_k P(k)$ up to $10^{18}$. Because $2m$ and $2m + 1$ share the half $m$, they
contribute the same term, so summing the recurrence over $k \le n$ expresses $S(n)$ through $S(M)$,
$P(M)$ and a triangular number. The pair $(P, S)$ is closed under halving, and the whole computation
is one chain of sixty levels.

Problem 463 is the same move on harder ground. Its sum does not close on its own: the substitution
produces a sum over the odd indices, which has to join the state as a companion, and the arguments
now touch both $n$ and $n - 1$. The chain widens to two values per level and needs a memo to stay
that narrow. So the working procedure is mechanical. Write the sum, substitute the recurrence, and
look at what appears. If only the value and the sum itself appear, carry a pair. If a new sum
appears, name it and repeat until nothing new does.

## Condition on the last piece

The [dynamic programming](/topics/technique/dynamic-programming) flavour: classify every complete
object by its final move and remove that move, so counts of size $i$ are sums of counts of smaller
sizes. Problems 115, 116 and 117 are the tiling family; the derivation and the pitfalls of the case
analysis are covered on the [recurrence relation](/topics/domain/recurrence-relation) page.

The last piece can be last in *time* rather than in space, and then removing it leaves two objects.
Problem 866 lays pieces down in a random order, and every placement multiplies a running product by
a weight $w(k)$ of the segment it forms. Averaging over $N!$ orders is hopeless, but look at the final
placement. Its position $j$ is uniform, it always forms the full segment, and until that moment
nothing can cross $j$. The two sides therefore evolve independently, each in a uniform order of its
own, so the product factorises and so does its expectation:

$$E(N) = \frac{w(N)}{N} \sum_{j=1}^{N} E(j-1)\,E(N-j).$$

That is the self-convolution behind the
[Catalan numbers](https://en.wikipedia.org/wiki/Catalan_number), with a weight. The cost changes
character with it. A split into two parts is quadratic in the sequence, so there is no fixed window
and no matrix to exponentiate: every term reads the whole table, and the evaluation is $O(N^2)$.

Sometimes the quantity asked for has no recurrence, but its **inverse** does. Problem 887 wants
$Q(N, d)$, the least height of a comparison tree that finds any secret $x \in \{1..N\}$ within
$x + d$ questions, summed over hundreds of millions of $N$. Minimising a height over trees for each
$N$ is hopeless; asking the converse — how many leaves can a tree of height $h$ serve? — conditions
cleanly on the root's split. The left subtree inherits a tighter budget, the right a looser one by
exactly as many leaves as went left, so with a *slack* $c$ carried in the state the capacity obeys

$$F(h, c) = F(h-1, c-1) + F\bigl(h-1,\ c-1 + F(h-1, c-1)\bigr),$$

with the left side filled greedily because $F$ only grows with slack. $Q$ is then the least $h$ whose
capacity reaches $N$, and because capacity is monotone in $N$, the sum over every $N$ turns into a
sum over the few dozen heights — $\sum_h \max(0, M - F(h, c_0))$. The move generalises: when the
answer is "the smallest resource that suffices", recur on what each resource level buys, and let the
monotonicity do the inversion.

## How to reason about it

- **The design decision is the state, not the formula.** Ask what the update needs that the previous
  step already knew. If the answer is "more than one number", widen the tuple — problem 169 carries a
  pair because a single value cannot advance itself. If it is "something I discarded", carry that
  too; the state is usually two or three integers regardless. Problem 887 widens it differently: a
  slack parameter makes every subtree look like the whole problem, so one function recurs on itself.
  Problem 866 is the honest exception: a convolution reads every earlier term, so the state is the
  table.
- **Write the update as a tuple assignment.** `a, b = b, a + b` evaluates the whole right-hand side
  first, which removes the temporaries and the classic sequential-assignment bug where the second
  line reads the value the first line just overwrote.
- **Verify the exactness before you use `//`.** A ratio recurrence is only an integer recurrence when
  every intermediate is divisible; when it is not, integer division does not fail, it drifts, and the
  answer is quietly wrong a hundred terms later. If in doubt, run the first twenty terms against a
  direct computation. Better still, choose a form with no division to check. Problem 374's scaled
  $A_j$ is one, and problem 866's weight happens to be divisible by $N$, so its $1/N$ cancels and the
  recurrence stays in integers under the modulus.
- **Seed from an index you have checked.** These recurrences frequently do not hold at the first one
  or two terms, and the small cases are exactly the ones a test case will not cover.
- **Watch the growth, in both languages.** The terms usually grow geometrically, so an $O(n)$ loop is
  $O(n^2)$ in digit operations — problem 57's counter is dominated by big-integer addition, and it
  also has to lift Python 3.11's `int`-to-`str` conversion cap when the numerators get long enough.
  In C the same ladder overflows instead: problem 141's discriminant needs `__int128` because the
  intermediate exceeds $2^{63}$. Problem 297's block sums show a quieter case: the step and the limit
  fit in 64 bits, but the running total for a $10^{18}$ limit does not, so only the accumulator moves
  to `unsigned __int128` (printed by hand, since `printf` has no format for it). See
  [watch integer width](/topics/takeaway/watch-integer-width).
- **Know the alternative you are beating.** If the direct formula is cheap and the index count is
  small, a recurrence is extra code and extra places to be wrong. The move pays when the index is
  large, when the direct evaluation is superlinear (factorials, powers, valuations), or when it
  converts a search into a walk. When none of those holds, write the formula.
- **When the index is too large even to step, the shape picks the method.** Matrix exponentiation,
  periodicity, telescoping — all on the
  [recurrence relation](/topics/domain/recurrence-relation) page.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ● [0539](/solutions/0539/) — Odd Elimination
- ● [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0866](/solutions/0866/) — Tidying Up B
- ● [0887](/solutions/0887/) — Bounded Binary Search

<!-- /problems -->
