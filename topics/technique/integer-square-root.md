<!-- tags: [integer-square-root] -->
<!-- status: final -->
# Integer square root

The [integer square root](https://en.wikipedia.org/wiki/Integer_square_root) of $n$ is the unique
$r$ with $r^2 \le n < (r+1)^2$ — a floor, computed entirely in integers. Almost none of the problems
below actually wants a square root. It appears as a loop bound, as a perfect-square predicate, as an
integer quadratic solver, and as a lattice-row count. The reason it deserves a tag rather than a
mention is the other half of the story: the floating-point version is *nearly* right, and nearly
right is a wrong answer with no traceback attached.

## The function, and the trap

[`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) (Python 3.8+) is exact for
arbitrarily large integers. It uses an adaptive-precision Newton iteration, so it costs about one
big-integer multiplication and never touches a `double`.

`int(n ** 0.5)` is a different function that usually agrees. `n ** 0.5` converts $n$ to a `double`
first — 53 bits of mantissa — so above $2^{53}$ the input itself is rounded before the square root
is taken, and the result can land on either side. Both directions of failure are real:

```python
>>> r = 9288565190841939
>>> n = r * r
>>> int(n ** 0.5) ** 2 == n          # n IS a perfect square
False
>>> math.sqrt(n + 1).is_integer()    # n + 1 is NOT
True
```

One value, two opposite mistakes: a genuine square rejected, and a non-square accepted. In a
predicate that decides whether a candidate counts, either one changes the total. In a loop bound it
is subtler still — an off-by-one ceiling drops the last candidate, and the program prints a
plausible number. `math.isqrt(n) ** 2 == n` has neither problem at any size.

## What it is actually used for

**A loop bound.** The most common use by far, resting on the fact that divisors pair up around
$\sqrt n$. Problem 3 factors by trial division and recomputes the ceiling from the *shrinking*
remainder each time a factor is stripped out, which is what makes the loop finish early on numbers
with a large prime cofactor:

```python
search_limit = int(remaining_number**0.5)
while remaining_number > 1 and current_factor <= search_limit:
    if remaining_number % current_factor == 0:
        remaining_number = reduce(remaining_number, current_factor)
        search_limit = int(remaining_number**0.5)
```

Problems 152, 179 and 932 use the same ceiling for divisor and factor enumeration. Problem 501 takes
it further into the $\sqrt n$ *decomposition* of the divisor lattice: every value of
$\lfloor n/k \rfloor$ is either at most $\sqrt n$ or of the form $n/k$ for $k \le \sqrt n$, so two
arrays of length $\sqrt n$ index the whole range — a standard device for prime-counting sums.

**A perfect-square predicate.** `s = isqrt(n); s * s == n`. Problem 141 tests each generated
candidate this way, problems 140 and 932 test discriminants, and problem 142 wraps it in a named
helper used throughout. Problem 64, which needs $a_0 = \lfloor \sqrt n \rfloor$ for the continued
fraction of $\sqrt n$, uses `math.isqrt` for the value but a float test to skip perfect squares —
safe only because its inputs stay in the low thousands, which is the sort of assumption worth
writing down.

**An integer quadratic solver.** When an inner loop's bound is the root of a quadratic, `isqrt` of
the discriminant gives it exactly, so the range is *computed* rather than discovered by a `while`
with a break:

```python
max_k = (-b_coeff + isqrt(disc)) // (2 * a_coeff)
```

Problems 141, 140, 932 and 229 all take this shape — the last one deriving both ends of a range from
two integer square roots. It converts a search with a termination test into an arithmetic range,
which is both faster and easier to reason about.

**Counting lattice points.** The number of integers $y$ with $y^2 \le r^2 - x^2$ is
$\lfloor \sqrt{r^2 - x^2} \rfloor$, so the count of lattice points inside a circle is a *sum* of
integer square roots, one per row. Problems 210 and 153 both do this. Here `isqrt` is the summand
rather than a bound, and it runs millions of times, which changes the engineering: problem 210
vectorises it over a NumPy `int64` array with a float square root plus an integer fix-up, since NumPy
has no exact `isqrt`.

**High precision, by scaling.** $\lfloor \sqrt{n \cdot 10^{2d}} \rfloor$ is the first $d$ significant
digits of $\sqrt n$ — an arbitrary-precision square root built from an integer one. Problem 80 is the
public exhibit and carries both classical algorithms. Heron's method, which is
[Newton's method](/topics/technique/newtons-method) on $x^2 - n$ and converges quadratically, so
about seven iterations reach a hundred digits:

```python
number *= 10 ** (2 * digits)
sqrt = number
while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
    pass
```

and the [binary search](/topics/technique/binary-search-algorithm) alternative, which is simpler to
prove and gains one bit per iteration instead of doubling them. Both are `isqrt`; `math.isqrt` is
the same idea, implemented once, in C.

## How to reason about it

- **Use `math.isqrt`, and only fall back deliberately.** The exceptions in this collection are
  vectorised code and C, and both then need the correction. Problem 501 hand-rolls the float seed
  followed by two adjustment loops — `while s*s > n: s -= 1` and
  `while (s+1)*(s+1) <= n: s += 1` — because it feeds a NumPy `int64` pipeline. That is the correct
  pattern: seed cheaply, correct exactly.
- **The C helper is five lines, and it copies badly.** C has no integer square root, so every C
  sibling here opens with the same float-seed-plus-fix-up function. Two things go wrong with it. The
  correction loop's own `(r + 1) * (r + 1)` overflows for $n$ near $2^{63}$ — problem 141 guards by
  comparing against `n / (s + 1)` instead of squaring — and the seed is a `double`, so for
  128-bit inputs the fix-up may need many steps rather than one or two. Problem 141 carries a
  separate `__int128` version for exactly this reason.
- **Guard the sign.** `math.isqrt` raises `ValueError` on a negative argument. A discriminant that
  can go negative needs its own branch, and in C — where `sqrt` of a negative returns `NaN` and the
  cast is undefined — it needs one even more.
- **Hoist it, unless the argument is shrinking.** For big integers `isqrt` is not free, and a bound
  recomputed inside a hot loop is pure waste. Problem 3's recomputation is deliberate and pays,
  because each stripped factor cuts the remainder by a large factor; problem 152 computes its ceiling
  once. The distinction is whether the argument changes.
- **Round outward when you must approximate.** If you are stuck with a float bound — for legibility,
  or because the exact one is expensive — add one and let the loop body reject the extra candidate.
  An over-wide bound costs one iteration; an under-wide one costs the answer.
- **Then ask whether you need the root at all.** Testing $n$ for squareness a few million times is
  much cheaper if you first reject on residues: a square is $0$ or $1$ mod $4$, and only 12 of the
  64 residues mod 64 are possible, which throws out over 80% of candidates with a mask before any
  square root runs. That is the same
  [cheap checks first](/topics/takeaway/cheap-checks-first) discipline the
  [generate and test](/topics/technique/generate-and-test) problems use everywhere else.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ● [0932](/solutions/0932/) — $2025$

<!-- /problems -->
