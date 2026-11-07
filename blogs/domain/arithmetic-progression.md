<!-- tags: [arithmetic-progression] -->
<!-- status: final 2026-10-16T07:31Z -->
# Arithmetic progression

An [arithmetic progression](https://en.wikipedia.org/wiki/Arithmetic_progression) (AP) is a
sequence in which each term differs from the previous one by a fixed **common difference** `d`:
`a, a + d, a + 2d, …`. It is the simplest non-trivial sequence there is, and that is exactly why
it keeps surfacing across the archive. An AP shows up in three quite different guises — as
something to **sum**, as a rigid **three-term constraint** that couples variables, and as a
**pattern to find or to avoid** — and the useful move is almost always to recognise which one you
are looking at, because each has its own closed-form escape hatch.

## The three faces of an AP

### A thing to sum

The oldest trick in the book. The sum of the first `n` terms of an AP is `n` times the average of
the first and last term — [Gauss's schoolboy
insight](https://en.wikipedia.org/wiki/1_%2B_2_%2B_3_%2B_4_%2B_%E2%8B%AF), pairing the ends inward
so every pair has the same total. That collapses a loop into arithmetic. The multiples of a fixed
`k` below a bound form an AP, so [Problem 1](/solutions/0001/) never iterates at all:

```python
def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
    """Closed-form sum of 0, d, 2d, ... below max_limit: d*n(n+1)/2."""
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2
```

The whole problem is then three closed-form sums combined by
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
(`3 + 5 − 15`) — `O(1)` instead of `O(N)`. The same instinct pays off wherever an AP hides inside
a geometric arrangement. In [Problem 28](/solutions/0028/) the four corners of each ring of a
number spiral are equally spaced, so the diagonal sum telescopes to a closed form; in
[Problem 58](/solutions/0058/) the four corners of layer `k` are again an AP stepping down by
`2k` from the odd square `(2k+1)²`, which is how the code generates them without walking the grid.
Whenever you can name the sequence you are summing as an AP, reach for the formula before the loop.

### A rigid three-term constraint

Three numbers form an AP exactly when the middle one is the average of the outer two — equivalently,
when you can write them as `m − d, m, m + d`. That parametrisation is worth its weight, because it
**eliminates a variable**: three unknowns collapse to a centre and a spread. [Problem 135](/solutions/0135/)
and [Problem 136](/solutions/0136/) both take `x, y, z` as consecutive terms of an AP and ask about
`x² − y² − z² = n`. Substitute the `m ± d` form and the quadratic melts:

$$ (m + d)^2 - m^2 - (m - d)^2 = m(4d - m) $$

So every solution is a way of writing `n` as a product `m · (4d − m)` — the problem has quietly
turned into a [divisor](https://en.wikipedia.org/wiki/Divisor)-counting exercise, and the AP
constraint is what made the reduction possible. Counting `n` with *exactly* one (Problem 136) or
*exactly* ten (Problem 135) representations is then a sieve over that factored form, not a search
over triples.

### A pattern to find, or to avoid

Because an AP is so structured, "does one exist here?" is a natural question — in both directions.
[Problem 49](/solutions/0049/) asks you to *find* one: three four-digit primes that are permutations
of each other and equally spaced (the known example `1487, 4817, 8147` steps by `3330`). The AP
condition is the strong filter — once you fix two terms, the third is forced, so you check a
candidate rather than search a third dimension.

The mirror image is *avoidance*. [Problem 720](/solutions/0720/) calls a permutation
**unpredictable** when no three of its values, read left to right, form an AP — an
[AP-free (Salem–Spencer) condition](https://en.wikipedia.org/wiki/Salem%E2%80%93Spencer_set) on the
sequence of values. Forbidding a three-term progression is a surprisingly deep combinatorial
constraint (it is the setting of Szemerédi-type theorems), and problems built on it reward counting
the surviving structures cleverly rather than generating and testing permutations.

## The arithmetic–geometric variant

An AP rarely travels alone. Multiply its terms by a geometric sequence and you get an
[arithmetic–geometric sequence](https://en.wikipedia.org/wiki/Arithmetico-geometric_sequence), whose
partial sums also have a closed form (found by the same "shift and subtract" telescoping that proves
the [geometric series](https://en.wikipedia.org/wiki/Geometric_series) formula).
[Problem 235](/solutions/0235/) is exactly this: `u(k) = (900 − 3k)·r^{k−1}`, an AP `900 − 3k` riding
a geometric `r^{k−1}`. The sum splits along the AP's two parts — the constant `a` multiplies a plain
geometric series, the step `d` multiplies the `k`-weighted one, which is just the derivative of the
geometric series in `r`:

$$ \sum_{k=1}^{n} r^{k-1} = \frac{r^n - 1}{r - 1}, \qquad
   \sum_{k=1}^{n} k\,r^{k-1} = \frac{1 - (n+1)r^n + n\,r^{n+1}}{(r-1)^2}. $$

So `s(5000)` costs one exponentiation instead of a five-thousand-term loop, and solving
`s(5000) = −6·10¹¹` becomes a one-dimensional root find rather than any kind of search. Working it
through taught three things the bare formula does not:

- **The AP decides the shape of the curve.** The coefficients `900 − 3k` are positive only up to
  `k = 300` and negative for the 4,700 terms after, and those late terms carry the *largest* powers
  of `r`. So for `r ≥ 1` the negative tail dominates and only grows with `r`: `s` falls
  monotonically from `s(1)` (above the target) without bound, and exactly one root exists. Where an
  AP changes sign is the first thing to look at when you need to know what its weighted sum does.
- **`r = 1` is the plain AP again.** Every denominator vanishes there, and the degenerate case is
  just the first section's sum, `n·a − d·n(n+1)/2` — a free exact value that also makes a natural
  lower end for the bisection bracket.
- **Arrange the closed form for the machine.** Collecting the `r^n` terms into `r^n·high + low`
  confines the one enormous factor to a single product, so the evaluation never subtracts two huge
  nearly-equal quotients. And the steepness that makes the sum hard to eyeball (it moves by
  roughly `10¹⁵` per unit of `r` near the root) is what makes the twelfth decimal of `r` cheap:
  bisection on the *sign* of `s − target` — sixty halvings, no derivative, no risk of divergence —
  is all the numerics it needs.

Recognising the arithmetic–geometric shape is what tells you a closed form, and therefore a clean
numerical solve, is available.

## How to reason about it

- **Name the sequence before you loop.** If the thing you are summing steps by a constant, it is an
  AP — use `n × (first + last) / 2` and drop the loop to `O(1)`.
- **Write three equally spaced terms as `m − d, m, m + d`.** The symmetry cancels cross-terms and
  usually eliminates a variable, often turning a quadratic constraint into a factorisation or
  divisor question.
- **Ask which direction the pattern runs.** Finding an AP fixes the third term from the first two (a
  check, not a search); forbidding one is a genuine combinatorial restriction with its own theory —
  don't brute-force it.
- **Watch for an AP hiding under a geometric factor.** An arithmetic–geometric sum still has a closed
  form, so a problem that looks like it needs simulation may only need a root find — and where the
  AP's terms change sign tells you whether that root is unique.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ○ [0828](/solutions/0828/) — Numbers Challenge

<!-- /problems -->
