<!-- tags: [exact-arithmetic-for-equality] -->
<!-- status: final 2026-10-15T10:37Z -->
# Use exact arithmetic for equality checks

Floating point is built for *approximation*. It gives up a little accuracy to gain speed and
range, and usually you never notice. But a whole family of Project Euler problems asks a
question where that loss is fatal: **is this value equal to that one?** The moment the answer
turns on an exact equality — two fractions being the same, a number being *exactly* a perfect
square, a point lying *exactly* on a line, a sum of unit vectors being *exactly* zero — a rounded
value is worse than useless. `0.1 + 0.2` is not `0.3` in binary floating point, and a test built
on that difference will either merge two values that are genuinely distinct or split two that are
genuinely equal. The fix is a habit, not a trick: when equality decides the answer, represent your
values so that equality is decided *exactly* — as integers, as reduced fractions, or in some other
canonical form — and never let a `float` into the comparison.

## The idea

The recurring move is to **rephrase the equality as one between integers**, because integer
equality is exact by construction. Five shapes cover almost every case below.

**Compare fractions by cross-multiplication.** Two rationals are equal, $\dfrac{p}{q} =
\dfrac{r}{s}$, exactly when the integers $p\,s$ and $r\,q$ are equal — no division, no rounding.
[Problem 33](/solutions/0033/) (digit-cancelling fractions) is the pure form: the "cancellation"
$\dfrac{10a + x}{10x + b} = \dfrac{a}{b}$ is tested as the exact integer identity, with the
qualifying fractions then folded as Python `Fraction`s so the final reduction is exact too:

```python
if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator:
    ...
```

The same identity underlies every "does this sum of reciprocals hit a target?" problem: scale by
a common denominator and the rational question becomes an integer one. [Problem 152](/solutions/0152/)
turns "these squared reciprocals sum to exactly $\tfrac12$" into a subset-sum over the integers
$D/k^2$ (with $D$ the LCM of the squares) hitting $D/2$; [Problem 155](/solutions/0155/) keeps
each reachable capacitance as a reduced fraction so that *distinct* means distinct; and
[Problem 243](/solutions/0243/) compares a totient ratio against a target fraction the same way.
[Problem 241](/solutions/0241/) (half-integer abundancy $\sigma(n)/n$) shows that the reduced
fraction is worth more than correctness. Its search carries the remaining ratio $a/b$ in lowest
terms, and the fact that the denominator must divide what is still to be built ($b \mid m$) becomes
its strongest pruning rule: one `gcd` against the primes already passed. A float version of $a/b$
would have no denominator to read that from.

**Test membership by inverting, then re-checking in integers.** "Is $m$ a perfect square?" /
"is $m$ pentagonal?" is an equality in disguise — does some integer $n$ satisfy $n^2 = m$, or
$n(3n-1)/2 = m$? The robust idiom computes an integer candidate and squares it *back*:

```python
r = math.isqrt(m)
if r * r == m:          # exact: no float ever touches the comparison
    ...
```

[Problem 44](/solutions/0044/) inverts the pentagonal quadratic for its $O(1)$ membership test,
and [Problem 211](/solutions/0211/) leans on a perfect-square check over a sieved divisor-square
sum. (Problem 44's published code takes the float shortcut `math.sqrt(...).is_integer()`, which
is fine *only* because its magnitudes are small — push $m$ past $2^{53}$ and that test starts
lying. `isqrt` never does.)

The same holds for **floors and ceilings of roots**, because "which integer is the boundary?" is a
pair of equalities and inequalities at that integer. [Problem 331](/solutions/0331/) needs
$\lceil\sqrt{N^2 - b^2}\rceil$ for $N$ near $2^{31}$, so the radicand is near $2^{62}$, where a
`float64` root can land one off either side. One wrong endpoint flips a parity and with it the
answer, so every root is corrected against the exact comparison. [Problem 950](/solutions/0950/)
goes further and takes floors of *irrational* quantities, $\lfloor x/\sqrt{m}\rfloor$, with no
irrational number ever stored:
$\lfloor x/\sqrt{m}\rfloor = \lfloor\sqrt{\lfloor x^2/m\rfloor}\rfloor$, one `isqrt`.

**Decide geometry with integer cross products.** "Which side of this line is the point on?" and
"do these two segments properly cross?" are sign-of-an-equality questions — the boundary case is
exact collinearity. The 2-D [cross product](https://en.wikipedia.org/wiki/Cross_product)
$u_x v_y - u_y v_x$ answers them with nothing but integer multiply and subtract, so the
degenerate case (a zero) is detected without a tolerance. [Problem 102](/solutions/0102/)
(point-in-triangle) and [Problem 165](/solutions/0165/) (proper segment intersections over
integer endpoints) both ride on it. [Problem 252](/solutions/0252/) (largest empty convex polygon
on 500 pseudo-random lattice points) shows the degenerate case is not hypothetical: a few exactly
collinear triples really occur, and the statement treats a point *on* an edge differently from
one *inside*. Each predicate must be strict on one side and inclusive on the other, which only
works if a zero means zero. Its areas are kept *doubled* (the shoelace sum before the halving),
so even the trailing $.5$ of the answer is exact.

When the geometry carries a square root, **square it away, minding signs.** [Problem 246](/solutions/0246/)
asks where an ellipse subtends more than $45^\circ$. The isoptic formula gives
$\tan\theta = 2ab\sqrt{S_1}/D$. Comparing it with $1$ splits on the sign of $D$: when $D \le 0$
the angle is obtuse and the test passes outright; when $D > 0$ it becomes the radical-free
$4a^2b^2 S_1 > D^2$. Every lattice point is then classified by integer arithmetic. That matters
most for points exactly on the ellipse, where only one tangent exists and the strict inequality
must reject them.

**Represent algebraic numbers in an integer basis.** Sometimes the values are not rational at all
— but they may still live in a ring with an integer basis, and there equality is coordinate-wise
integer equality. [Problem 768](/solutions/0768/) counts subsets of the $n$-th
[roots of unity](https://en.wikipedia.org/wiki/Root_of_unity) that sum to zero (a balanced
chandelier). Summing `cos`/`sin` and testing against a tolerance would be guesswork, and wrong
guesswork in a way that is hard to notice. Instead each root becomes its integer coordinate vector
in $\mathbb{Z}[\zeta_r]$, and "balanced" becomes "the vectors sum to the zero vector". The solution
then packs each vector into a single integer, with enough headroom per coordinate that no carry
can cross. A balanced subset is then exactly a packed sum of `0` — one integer comparison, used
as a hash key in a meet-in-the-middle.

**Stay exact to the last digit, then round in integers.** Problems that ask for a decimal answer
still have an equality inside them: the twelfth digit is decided by whether the value is above or
below a rounding boundary. [Problem 239](/solutions/0239/) computes a probability by
inclusion–exclusion, an alternating sum of factorial-sized terms that cancel catastrophically. Done
in `float`, that cancellation loses every significant digit. Kept as the exact rational $N/n!$,
the result is rounded half-up as the integer
$\left\lfloor (2N\cdot 10^{12} + n!)\,/\,(2\,n!)\right\rfloor$, and only then formatted.

A close cousin is the **canonical form**: replace an "equal up to reordering" relation with exact
equality of a normalised key. [Problem 62](/solutions/0062/) decides "these two cubes are digit
permutations" by sorting each number's digits into a string and comparing strings — an exact,
hashable key standing in for a fuzzy equivalence.

## How to reason about it

Reach for exact arithmetic the instant the answer depends on `==`, on counting *distinct* values,
on the sign of a difference at its boundary, or on a rounded digit. The boundary *is* an equality,
so ordering tests inherit the same fragility. The cost is real but usually cheap: cross-multiplication
doubles the width of the integers you compare (in C that can mean `__int128`, as in Problem 950,
where the squared terms reach $10^{36}$), and exact fractions or arbitrary-precision integers grow
as the computation runs. [Problem 57](/solutions/0057/) generates its convergents with an
integer-only recurrence whose numerator and denominator become bignums, paying an $O(n^2)$ price
for perfect equality. That price buys certainty: a `float`-based version can be *fast and wrong*,
and on an equality test there is no partial credit.

The rule is not "never use a float", though. **Floats may propose; integers decide.** A float is
a fine *estimate* as long as an exact check has the final word. Problem 331 vectorises its roots
with NumPy's `float64` `sqrt` and then nudges each by exact integer comparisons; Problem 246 seeds
its boundary from an `isqrt` estimate, overshoots by two, and walks down until the exact test
passes:

```python
r = int(math.sqrt(v))           # an estimate: may be off by one either way
while r * r > v: r -= 1         # the integers settle it
while (r + 1) * (r + 1) <= v: r += 1
```

Problem 241 goes a step further and lets floats into a *pruning bound*: a prefix sum of logarithms
estimates the most the remaining primes could raise the ratio. That is safe because the bound is
inflated by a small slack, so rounding can only make it keep a branch it could have cut, never
cut one it should keep. The hit test itself, $a = b$, stays exact.

Exactness also pays off in *reasoning*. Problem 950's pirates weigh coins against a payoff of
$1/\sqrt{m}$ per walk. Because $\sqrt{m}$ is irrational, no two outcomes can ever tie, so the
puzzle's usual tie-breaking question disappears. That argument holds only if the code computes
the floors exactly. A float could create a tie that the mathematics rules out.

Two pitfalls worth naming. First, "I'll just use a small epsilon" replaces one bug with a subtler
one. Make the tolerance too tight and you split equal values; too loose and you merge distinct
ones; and the right value drifts with the magnitude of the inputs. If the true relation is exact,
model it exactly and delete the epsilon. Keep tolerances for one-sided bounds like Problem 241's,
where an error can only cost time. Second, watch the *whole* pipeline: it is not enough to
compute exactly and then compare a `float` at the end (Problem 44's `is_integer()` is exactly this
seam, and so would be dividing Problem 239's exact numerator by $n!$ in floating point before
rounding). The rule is simple — if equality decides the answer, no rounded value may touch the
decision.


<!-- problems (generated by update-tags) -->
## Problems

- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0102](/solutions/0102/) — Triangle Containment
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0165](/solutions/0165/) — Intersections
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0205](/solutions/0205/) — Dice Game
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0243](/solutions/0243/) — Resilience
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0768](/solutions/0768/) — Chandelier
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0950](/solutions/0950/) — Pirate Treasure

<!-- /problems -->
