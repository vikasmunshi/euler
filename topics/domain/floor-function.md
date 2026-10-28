<!-- tags: [floor-function] -->
<!-- status: final 2026-10-28T08:28Z -->
# Floor function

The [floor function](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) `⌊x⌋` is the
largest integer not greater than `x`. It is where real numbers meet integers, and that is why
it keeps turning up. A problem stated over the reals (a sequence bounded by powers, a payoff
scaled by `1/√m`, a ratio of squares) becomes a counting problem as soon as a floor is applied
to it. The floor discards almost all of the information in `x`, and the problems below rely on
that. What survives is an integer you can compute exactly, a step function whose jumps you can
list, or a quotient that takes surprisingly few distinct values. This page is about the floor
itself. The companion pages, [irrational number](/topics/domain/irrational-number) and
[quadratic irrational number](/topics/technique/quadratic-irrational-number), deal with the hard
case where the `x` inside is irrational and cannot be stored.

## The idea: a floor is a pair of inequalities

Everything useful about the floor follows from its definition, written as a sandwich:

$$ \lfloor x \rfloor = n \iff n \le x < n + 1 \iff x - 1 < n \le x $$

Read from left to right, this computes a floor: find the integer `n` that satisfies two
inequalities. Read from right to left, it **eliminates** one: a constraint of the form
`n ≤ x < n + 1` is just `n = ⌊x⌋` written out. The problems in this archive use the floor in
three ways.

### Recognising a floor that the problem never wrote

[Problem 319](/solutions/0319/) never says "floor". It asks for sequences
`2 = x₁ < x₂ < … < xₙ` with `x_i^j < (x_j + 1)^i` for every pair `i, j`, which is `n²` coupled
inequalities. Taking `ij`-th roots splits them into `max_i x_i^{1/i} < min_j (x_j + 1)^{1/j}`.
Name the left side `t`, and each term is caught in the sandwich `t^i − 1 < x_i ≤ t^i`. That is
`x_i = ⌊t^i⌋`. A family of integer sequences turns out to be a single real parameter
`t ∈ [2, 3)` seen through a floor. Whenever a problem pins an integer between `y − 1` and `y`,
or between `y` and `y + 1`, look for the floor it is hiding.

### A floor of a real parameter is a step function, so count its steps

Once the floor is visible, the second property takes over. As `t` varies, `⌊f(t)⌋` stays
constant and jumps only where `f(t)` crosses an integer. A tuple of floors
`(⌊f₁(t)⌋, …, ⌊fₙ(t)⌋)` is therefore constant on intervals, and the number of distinct tuples is
one more than the number of **distinct** breakpoints. In Problem 319 the breakpoints are the roots
`t = m^{1/i}` with `2^i < m < 3^i`. The whole problem is then deciding when two of them are the
same real number (`8^{1/2} = 64^{1/4}`), which is a job for
[Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula) over minimal
exponents.

[Problem 950](/solutions/0950/) uses the same idea in a smaller form. It needs the largest `j`
whose cost `Σ (vᵢ + ⌊(s − 2j)/√m⌋ + 1)` fits within a budget. That sum looks like a search over
`j`, but the floor is constant on runs of `j`, and so is the histogram piece being bought. On
each (piece, floor value) cell the cost is linear in `j`, so the largest affordable `j` in a cell
is one division. Cutting the domain at the floor's jumps replaces a scan with a short loop over
cells. [Problem 372](/solutions/0372/) asks about the parity of `⌊y²/x²⌋`, and has the same
structure in two dimensions. The value changes only across the rays `y = x√k`, so the plane
breaks into wedges and the count becomes a sum, over wedges, of lattice points under a line of
irrational slope. Sums such as `Σ ⌊x√k⌋` are
[Beatty sequence](https://en.wikipedia.org/wiki/Beatty_sequence) sums, and they have their own
fast recursions.

### `⌊n/d⌋` takes only about `2√n` values

The most frequently used floor fact in number theory is about integer division. For `d ≤ √n`
there are at most `√n` values of `d`. For `d > √n` the quotient `⌊n/d⌋` is below `√n`. So
`⌊n/d⌋` takes `O(√n)` distinct values over `1 ≤ d ≤ n`, and each value is held on a contiguous
block of `d`. The block that starts at `d` ends at `n // (n // d)`:

```python
d = 1
while d <= n:
    v = n // d
    hi = n // v              # last d with the same quotient
    total += (G(hi) - G(d - 1)) * F(v)
    d = hi + 1
```

Any sum `Σ_d g(d) · F(⌊n/d⌋)` collapses to `O(√n)` terms as long as you can get the prefix sums
`G` of `g` quickly. Problem 319 reaches exactly this shape,
`t(n) = 1 + Σ_d μ(d) F(⌊n/d⌋)`, with `G` the
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function). Computing `M` at every
`⌊n/d⌋` is itself the same block trick applied recursively, using the nesting identity
`⌊⌊n/a⌋/b⌋ = ⌊n/(ab)⌋`. That identity is what keeps the set of needed arguments closed. This is
the standard route to `O(n^{2/3})` summatory functions, and it is
[Dirichlet's hyperbola method](https://en.wikipedia.org/wiki/Dirichlet_hyperbola_method) in
code.

### Computing a floor exactly

The floor is unforgiving at its jumps: if `x` is a hair below an integer and the float rounds
it up, the answer is off by one. The exact recipes depend on what is inside the floor:

| Inside the floor | Exact computation |
| --- | --- |
| `a / b`, integers | `a // b` in Python. In C, `/` truncates toward zero, so fix it up for negative operands |
| `√n` | `math.isqrt(n)` |
| `x / √m`, `x ≥ 0` | `isqrt(x*x // m)`, because squaring preserves floors of non-negatives (950) |
| `(c + √a)^n`, `0 < c − √a < 1` | `(x^n + y^n) − 1`, an integer recurrence through the conjugate (721) |
| `⌈x⌉` | `−⌊−x⌋`, or `(a + b − 1) // b` for positive integer division |

[Problem 721](/solutions/0721/) is the extreme case. It needs `⌊(⌈√a⌉ + √a)^n⌋` for `n` in the
trillions, a number with trillions of digits. The conjugate trick is explained on the
[irrational number](/topics/domain/irrational-number#pair-it-with-its-conjugate) page, and the
pair arithmetic that carries it out mod a prime is on the
[quadratic irrational number](/topics/technique/quadratic-irrational-number) page. What matters
here is that the floor is the *reason* the problem can be solved at all. `x^n` is irrational,
but its floor is an integer with a closed form.

## How to reason about it

- **Write the floor as its sandwich.** `n ≤ x < n + 1` is usually more useful than `⌊x⌋`. It
  turns floor equations into ranges for the variables and exposes floors hidden inside
  inequality systems (319).
- **Count jumps, not points.** When a floor depends on a continuous parameter, the answer lives
  at the breakpoints. List them, merge the ones that coincide, and the count of distinct values
  follows. Coincident breakpoints are where the real difficulty is.
- **Group by quotient.** Whenever `⌊n/d⌋` appears in a sum over `d`, iterate over its `O(√n)`
  blocks instead of over `d`. The same applies to `⌊(s − 2j)/√m⌋` or any monotone floor: cut the
  index range where the floor changes and solve each piece in closed form (950).
- **Never let a float decide a floor near an integer.** Use `//` and `isqrt`, or use a float
  estimate and correct it with an exact integer check, as the C ports do. Irrationality helps:
  when `q²m` is never a perfect square, `⌈q√m⌉ = isqrt(q*q*m) + 1` with no boundary case.
- **Mind the open and closed ends.** `⌊x⌋ ≤ x` but `⌈x⌉ ≥ x`, and "strictly between `2^h` and
  `3^h`" contains `3^h − 2^h − 1` integers, not `3^h − 2^h`. Off-by-one errors in floor problems
  almost always come from the wrong end of the sandwich. Check the first few terms against a brute
  force before trusting a closed form.
- **Mind the language.** Python's `//` floors toward `−∞`. C's `/` truncates toward zero. They
  agree on non-negative operands and disagree on everything else. Squared terms such as `x²` in
  `isqrt(x*x // m)` can exceed 64 bits (950 needs `__int128`).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0319](/solutions/0319/) — Bounded Sequences
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0950](/solutions/0950/) — Pirate Treasure

<!-- /problems -->
