<!-- tags: [euclidean-algorithm] -->
<!-- status: final -->
# Euclidean algorithm

The [Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm) computes the greatest
common divisor of two integers in a handful of divisions, and it is about two thousand three hundred
years old. What is worth noticing about the problems below is that hardly any of them wanted a common
divisor. The gcd appears as a coprimality test, as a normaliser, as a way to build the lcm, and
occasionally as a count in its own right — four different jobs, one three-line loop.

## The algorithm

Replace $(a, b)$ with $(b,\ a \bmod b)$ until the second term is zero; the first term is then the gcd.

```python
while b:
    a, b = b, a % b
```

It terminates because the remainder strictly decreases, and it is correct because any divisor of $a$
and $b$ also divides $a - qb$, so the pair's set of common divisors is unchanged by the step. The
speed is the surprising part: by [Lamé's theorem](https://en.wikipedia.org/wiki/Lam%C3%A9%27s_theorem)
the number of steps is $O(\log \min(a, b))$, and the worst case is exactly a pair of consecutive
[Fibonacci numbers](https://en.wikipedia.org/wiki/Fibonacci_number) — the inputs on which every
quotient is 1 and the remainder shrinks as slowly as it possibly can. Even then, `gcd(a, b)` for
64-bit inputs is bounded by about ninety iterations. It is, for practical purposes, free.

The subtractive form Euclid actually wrote — repeatedly subtract the smaller from the larger — is the
same algorithm with the division unrolled, and it is $O(a/b)$ in the bad case rather than
$O(\log b)$. `gcd(10**9, 1)` is one modulo or a billion subtractions. Use the remainder.

Python has it built in as [`math.gcd`](https://docs.python.org/3/library/math.html#math.gcd), which
since 3.9 is variadic and returns a non-negative result, plus
[`math.lcm`](https://docs.python.org/3/library/math.html#math.lcm) alongside it. C has neither, so
every C solution here carries the same five-line helper near the top of the file:

```c
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}
```

When a Python solution in this stack is one expression and its C sibling opens with that function,
this is the whole of the difference.

## The four jobs

**A coprimality predicate.** This is by far the most common use, and it usually appears inside a
parametrisation. [Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple) generates every
primitive Pythagorean triple exactly once from a pair $m > n > 0$ that is coprime and of opposite
parity, so the enumeration is a double loop with a gcd guard at its centre — problem 75 writes it
plainly:

```python
for m in range(2, int((max_perimeter / 2) ** 0.5)):
    for n in range(m % 2 + 1, m, 2):
        if math.gcd(m, n) != 1:
            continue
```

Problems 39 and 139 use the same generator, and problems 141, 195 and 420 each enumerate over a
coprime pair $(p, q)$ that parametrises their own family. The shared idea is that the gcd condition is
what makes the parametrisation a *bijection*: drop it and you generate every triple once for each of
its scalings, and the count is wrong in a way that is very hard to see. A second flavour of the same
job is coprimality to a fixed modulus — problems 26 and 129 both filter on $\gcd(n, 10) = 1$, because
the decimal expansion of $1/n$ only becomes purely periodic once $n$ shares no factor with the base.

**A normaliser.** Dividing both parts of something by their gcd puts it in canonical form: a fraction
in lowest terms, a direction vector reduced to its primitive step, a ratio reduced to its
representative. Problem 175 divides a numerator and denominator by their gcd for exactly this reason.
Python's [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html) does it for you on
every operation — which is why problems 33 and 71 use the gcd without ever naming it, and why their
final answers can be read straight off `.numerator` or `.denominator` with no reduction step of their
own.

**The lcm.** From $\gcd(a,b) \cdot \mathrm{lcm}(a,b) = ab$ comes the one identity worth memorising,
including the placement of the division:

```python
return a // gcd(a, b) * b
```

Divide *first*. `a * b // gcd(a, b)` is mathematically identical and forms an intermediate product
that can be enormous — harmless in Python, an overflow in C. Problem 5 folds this across a range to
get the smallest number divisible by everything in it, and problem 853 uses it to combine periods,
which is the recurring reason to want an lcm at all: two cycles of lengths $a$ and $b$ realign after
$\mathrm{lcm}(a, b)$ steps.

**A quantity in its own right.** The one that is easy to miss. The line segment from the origin to a
lattice point $(x, y)$ passes through exactly $\gcd(x, y) - 1$ interior lattice points, and the
primitive step along it is $(x/g,\ y/g)$. Problem 91 uses both facts at once — $m = \gcd(x, y)$ gives
the primitive perpendicular direction, and the same $m$ scales how far that direction can be walked
inside the grid:

```python
min(x * m // y, m * (coordinate_limit - y) // x)
for x in range(1, coordinate_limit + 1)
for y in range(1, coordinate_limit)
for m in [math.gcd(x, y)]
```

Problem 504 needs the same count on all four sides of a quadrilateral, because
[Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem) converts an area plus a boundary
count into an interior lattice-point count, and the boundary count is a sum of gcds. Problem 182
counts RSA exponents whose number of unconcealed messages is minimal, and that number is a product of
two gcd terms — here the gcd is not a filter or a normaliser but the actual value being tabulated.

One more use is worth knowing even though it fits none of the four: the *quotients* the loop throws
away are themselves data. The sequence $q_1, q_2, \dots$ produced by successive divisions is exactly
the [continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) expansion of $a/b$, and
running the algorithm to collect them is how you convert a rational into that form. Problem 175 does
precisely this — it reduces its fraction by the gcd and then keeps walking, emitting one run per
Euclidean quotient, because the quotient sequence is the answer's structure rather than a by-product.

## How to reason about it

- **Put the cheap test first.** A gcd is a few divisions, which is cheap but not nothing when it sits
  inside a double loop over millions of pairs. Problem 139's parity check runs *before* its gcd
  precisely so that half the pairs never reach it, and the source says so. Ordering a filter chain by
  ascending cost is the most reliable easy win in this whole family of enumerations.
- **Tabulate when the same small pairs recur.** Problem 504 needs $\gcd(i, j)$ for every pair up to a
  small bound and computes the full $O(m^2)$ table once, up front. When your operands are bounded and
  the query count exceeds the table size, precompute — and note that the table can itself be filled by
  a sieve rather than by $m^2$ calls, if that ever becomes the bottleneck.
- **Enumerate the primitives and scale.** The deeper move behind the coprimality guard: instead of
  enumerating every object and deduplicating, enumerate one representative per equivalence class and
  multiply out the scalings. Problems 75 and 139 both generate each primitive triple once and then
  count its multiples in $O(1)$, turning an $O(L^2)$ search into an $O(L)$ one. When a gcd condition
  appears in a loop, this is usually the reason.
- **Know the edge cases.** $\gcd(0, n) = n$ and $\gcd(0, 0) = 0$; the loop above already gives both.
  Python's `math.gcd` always returns a non-negative value, but a hand-written C version does not:
  C's `%` takes the sign of the dividend, so a negative operand yields a negative gcd unless you take
  the absolute value on entry. Problems that only ever pass positive counts will never notice, which
  is exactly why the C helper gets copied into the next problem unfixed.
- **If you need the coefficients, you need the other algorithm.** The plain loop discards the
  information that answers "*which* combination of $a$ and $b$ gives the gcd". When the goal is a
  modular inverse or a linear Diophantine equation, reach for the
  [extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm), which runs the same
  divisions and keeps the bookkeeping. When it is not, do not pay for it.
- **Do not hand-optimise it.** The [binary GCD](https://en.wikipedia.org/wiki/Binary_GCD_algorithm)
  replaces division with shifts and subtractions and was a real win on machines with slow dividers;
  on current hardware, against a compiler that knows the idiom, it is roughly a wash. `math.gcd` is
  implemented in C with a fast path for machine-word operands and will beat anything written in
  Python. The gcd is almost never the bottleneck — the loop that calls it is.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0127](/solutions/0127/) — abc-hits
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0853](/solutions/0853/) — Pisano Periods 1

<!-- /problems -->
