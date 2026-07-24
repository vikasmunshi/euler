<!-- tags: [exact-arithmetic-for-equality] -->
<!-- status: final -->
# Use exact arithmetic for equality checks

Floating point is built for *approximation* — it trades a little accuracy for speed and range,
and most of the time that trade is invisible. But a whole family of Project Euler problems asks
a question where the trade is fatal: **is this value equal to that one?** The moment the answer
turns on an exact equality — two fractions being the same, a number being *exactly* a perfect
square, a point lying *exactly* on a line — a rounded value is worse than useless. `0.1 + 0.2`
is not `0.3` in binary floating point, and a test built on that difference will either merge two
values that are genuinely distinct or split two that are genuinely equal. The fix is a habit, not
a trick: when equality decides the answer, represent your values so that equality is decided
*exactly* — as integers, as reduced fractions, or as some other canonical form — and never let a
`float` into the comparison.

## The idea

The recurring move is to **rephrase the equality as one between integers**, because integer
equality is exact by construction. Three shapes cover almost every case below.

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

**Decide geometry with integer cross products.** "Which side of this line is the point on?" and
"do these two segments properly cross?" are sign-of-an-equality questions — the boundary case is
exact collinearity. The 2-D [cross product](https://en.wikipedia.org/wiki/Cross_product)
$u_x v_y - u_y v_x$ answers them with nothing but integer multiply and subtract, so the
degenerate case (a zero) is detected without a tolerance. [Problem 102](/solutions/0102/)
(point-in-triangle) and [Problem 165](/solutions/0165/) (proper segment intersections over
integer endpoints) both ride on it.

A close cousin is the **canonical form**: replace an "equal up to reordering" relation with exact
equality of a normalised key. [Problem 62](/solutions/0062/) decides "these two cubes are digit
permutations" by sorting each number's digits into a string and comparing strings — an exact,
hashable key standing in for a fuzzy equivalence.

## How to reason about it

Reach for exact arithmetic the instant the answer depends on `==`, on counting *distinct* values,
or on the sign of a difference at its boundary — because the boundary *is* an equality, ordering
tests inherit the same fragility. The cost is real but usually cheap: cross-multiplication doubles
the width of the integers you compare, and exact fractions or arbitrary-precision integers grow as
the computation runs — [Problem 57](/solutions/0057/) generates its convergents with an
integer-only recurrence whose numerator and denominator become bignums, paying an $O(n^2)$ price
for perfect equality. That price buys certainty: a `float`-based version can be *fast and wrong*,
and on an equality test there is no partial credit.

Two pitfalls worth naming. First, "I'll just use a small epsilon" replaces one bug with a subtler
one — pick the tolerance too tight and you split equal values, too loose and you merge distinct
ones, and the right value drifts with the magnitude of the inputs. If the true relation is exact,
model it exactly and delete the epsilon. Second, watch the *whole* pipeline: it is not enough to
compute exactly and then compare a `float` at the end (Problem 44's `is_integer()` is exactly this
seam). The rule is simple — if equality decides the answer, no rounded value may touch the
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
- ● [0243](/solutions/0243/) — Resilience
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0800](/solutions/0800/) — Hybrid Integers

<!-- /problems -->
