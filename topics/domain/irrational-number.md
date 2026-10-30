<!-- tags: [irrational-number] -->
<!-- status: final 2026-10-29T07:50Z -->
# Irrational number

An [irrational number](https://en.wikipedia.org/wiki/Irrational_number) is a real number that
cannot be written as a ratio of two integers. Its decimal expansion never ends and never settles
into a repeating cycle. That is a problem for a computer, which only has integers and floats, and
a float is just a rational number with 53 bits of mantissa. So when an irrational number such as
`√2`, `φ` or `1/√m` turns up in a Project Euler problem, it is almost never something you
evaluate. The problem asks for an **integer fact** about it: a prefix of its digits, the floor of
one of its powers, which side of a threshold it falls on. The work is in finding the exact
integer computation that settles that fact. A float answer is wrong exactly when it matters.

## The idea: never hold the number, hold an integer that pins it down

Most of these problems reduce to one question: what is `⌊α⌋` (or `⌈α⌉`, or the sign of `α − β`)
for an irrational `α` that you cannot store? See the [floor function](/topics/domain/floor-function)
page for that half of the story. The archive uses three ways to answer it without rounding error.
Each one turns the irrational quantity into an integer you can compute exactly.

### Scale it into an integer square root

The square root of a non-square integer is irrational, which is
[a classic proof](https://en.wikipedia.org/wiki/Square_root_of_2#Proofs_of_irrationality). It is
also the easiest irrational to pin down, because one identity moves the decimal point for free:

$$ 10^d \sqrt{n} = \sqrt{n \cdot 10^{2d}} $$

So the first `d` significant digits of `√n` are the
[integer square root](https://en.wikipedia.org/wiki/Integer_square_root) `⌊√(n · 10^{2d})⌋`.
That is a question about big integers and has nothing to do with real-number precision.
[Problem 80](/solutions/0080/) wants the first hundred digits of `√n` for every non-square
`n ≤ 100`, and the whole solution is that identity plus Heron's (Newton's) iteration on Python's
arbitrary-precision `int`:

```python
number *= 10 ** (2 * digits)
sqrt = number
while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
    pass
return str(sqrt)[:digits]
```

Every operation is exact, and the loop stops at the fixed point, which is `⌊√S⌋` exactly. This
works for any precision. You choose the scale, and the integers grow to fit it.

### Pair it with its conjugate

For powers of a [quadratic irrational](/topics/technique/quadratic-irrational-number), scaling is
hopeless: `(c + √a)^n` with `n` in the trillions has trillions of digits. The way in is the
[algebraic conjugate](https://en.wikipedia.org/wiki/Conjugate_(square_roots)). If
`x = c + √a` and `y = c − √a`, then both are roots of `t² − 2ct + (c² − a)`, and the power sum
`x^n + y^n` is an **integer** that satisfies a linear recurrence. In the binomial expansions the
odd powers of `√a` cancel. When the conjugate is small, `0 < y < 1`, the irrational part of `x^n`
is squeezed into a sliver below an integer:

$$ x^n = (x^n + y^n) - y^n \quad\Rightarrow\quad \lfloor x^n \rfloor = (x^n + y^n) - 1 $$

[Problem 721](/solutions/0721/) is built around exactly this. `c = ⌈√a⌉` is chosen so that the
conjugate lands in `[0, 1)`. After that, the floor of an astronomically large irrational power is
an integer you can compute *modulo a prime*, by exponentiation by squaring in the ring of pairs
`u + v√a`. The irrational number never appears in the arithmetic, only its integer coordinates.
The perfect-square case (`y = 0`, no `−1`) is the edge case to watch.

[Problem 318](/solutions/0318/) asks about the other end of the same identity. Its powers
`(√p + √q)^{2n}` have fractional parts that run `…9.99999…`, and it wants the first `n` at which
2011 nines appear. With `x² = (p+q) + 2√(pq)` and conjugate `y² = (√q − √p)²`, the fractional part
of `x^{2n}` is exactly `1 − y^{2n}`. So the count of nines has nothing to do with the digits of
`x`. It depends only on how fast `y^{2n}` shrinks, and `y^{2n} ≤ 10^{-d}` gives `N` in closed form
as a ceiling of `d / (−2 log₁₀ y)`. The condition "the fractional part tends to 1" is just
`0 < y < 1`, i.e. `√q < √p + 1`. Squaring twice turns it into the integer test
`(q − p − 1)² < 4p`, so the qualifying pairs are found without a single square root.

### Square both sides and compare integers

Sometimes the irrational number is a **parameter**, not the thing you are asked about. In
[Problem 950](/solutions/0950/) every pirate's bloodthirstiness is `p = 1/√m`, so a payoff is
`c + w/√m`. Two facts come out of that. The first is structural: since `√m` is irrational, two
different integer pairs `(c, w)` can never give the same payoff. **No voter is ever exactly
indifferent**, so the tie-breaking rule that complicates every pirate puzzle never comes into
play. Irrationality is doing real work here. It makes the game well defined. The second fact is
computational: the vote prices need `⌊x/√m⌋`, and a non-negative quantity has the same floor
under squaring, so

$$ \left\lfloor \frac{x}{\sqrt m} \right\rfloor = \left\lfloor \sqrt{\left\lfloor x^2 / m \right\rfloor} \right\rfloor $$

which is one integer division and one `math.isqrt`. Because `q²m` is never a perfect square, a
boundary like "the smallest integer above `q√m`" is also always `isqrt(q*q*m) + 1`, and that
holds exactly with no `≤`-versus-`<` worries.

## How to reason about it

- **Ask which integer fact the problem actually wants.** A digit prefix suggests scaling. A floor
  of a power suggests the conjugate. A comparison or a threshold suggests squaring. It is very
  rare that you need the number itself.
- **Do not trust a float to decide a floor or a tie.** A `double` holds about 16 significant
  digits. Problem 80 needs 100. Problem 721's powers have trillions of digits. Problem 950's
  floors involve `x` up to `10^16`, which sits right at the edge of a `double`'s 53 bits. A
  quotient that falls just below an integer can round up and change the floor.
  `math.isqrt` (or a float estimate corrected by an exact integer check, as the C ports do) is the
  safe default.
- **When a float is the right tool, keep the cancellation out of it.** Problem 318 needs a
  logarithm, so it cannot stay in integers. But `y = √q − √p` sits just below `1` for the hardest
  pairs, and `log(√q − √p)` computed naively loses most of its digits to
  [catastrophic cancellation](https://en.wikipedia.org/wiki/Catastrophic_cancellation). The fix is
  the conjugate again: rationalize `1 − y` so that its numerator is the exact integer
  `4p − (q − p − 1)²` and its denominator is a sum of positive terms, then take `log1p(−ε)`.
  Irrationality also says the ceiling's argument is never an integer, so the remaining risk is a
  quotient that lands *near* one; recomputing just those few pairs at high precision closes it.
- **Irrationality is a guarantee you can use.** "Never an integer" means `⌊α⌋ = ⌈α⌉ − 1`,
  `y^n` is never exactly `0` or `1`, and two expressions `a + b√m` agree only when their parts
  agree. Problems use this to rule out ties and boundary cases. Notice when they do, and drop the
  code that handles a case that cannot happen.
- **Watch the rational exceptions.** The guarantee only holds when the number really is
  irrational. Perfect squares (Problem 80 skips them, Problem 721 handles them as a separate
  branch) are the classic place where an "irrational" formula quietly becomes rational and an
  off-by-one gets in.
- **Mind the integer width.** Squaring to stay exact doubles the bit length. Problem 950's `x²`
  reaches about `10^36`, past 64 bits, which is why its C port uses `__int128`.

For the shared machinery, see [floor function](/topics/domain/floor-function) (exact floors of
real expressions, and summing them) and
[quadratic irrational number](/topics/technique/quadratic-irrational-number) (computing in
`ℤ[√a]`, conjugates, and the continued fractions behind Pell equations).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0517](/solutions/0517/) — A Real Recursion
- ○ [0558](/solutions/0558/) — Irrational Base
- ○ [0566](/solutions/0566/) — Cake Icing Puzzle
- ○ [0576](/solutions/0576/) — Irrational Jumps
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0656](/solutions/0656/) — Palindromic Sequences
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ○ [0731](/solutions/0731/) — A Stoneham Number
- ○ [0911](/solutions/0911/) — Khinchin Exceptions
- ● [0950](/solutions/0950/) — Pirate Treasure

<!-- /problems -->
