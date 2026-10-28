<!-- tags: [expected-value-application] -->
<!-- status: final -->
# Expected value (application)

This page is about the *mechanics*: what it looks like, in code, to actually turn "expected value
of …" into a number that is exact to the last place asked for. The concept itself — what an
expectation is, and the families of problems that ask for one — is covered on the
[expected value](/topics/domain/expected-value) domain page. The three problems here share a working
method: take the random quantity apart into pieces whose averages are easy, put it back together
with [linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity) or an exact
recurrence, and keep every intermediate value a fraction until the final rounding.

## The idea

There are only two ways to avoid summing over every outcome, and these problems use both.

**Decompose, then add.** Write the target $X$ as a sum $X = \sum_i X_i$ of pieces, each of which
depends on far less of the randomness than $X$ does. Then
$\mathbb{E}[X] = \sum_i \mathbb{E}[X_i]$ — with no independence needed between the pieces. Two
decompositions recur:

- *Over objects* — one [indicator](https://en.wikipedia.org/wiki/Indicator_function) per thing that
  might be counted. Problem 493 counts distinct colours among balls drawn from an urn; the count is
  a sum of one indicator per colour, each colour looks the same by symmetry, and the whole
  expectation becomes the colour count times a single probability — that one colour is drawn at
  all, i.e. one minus the chance every draw avoids it, a ratio of two
  [binomial coefficients](https://en.wikipedia.org/wiki/Binomial_coefficient). The joint
  [multivariate hypergeometric](https://en.wikipedia.org/wiki/Hypergeometric_distribution#Multivariate_hypergeometric_distribution)
  distribution never has to be written down.
- *Over time* — one piece per step of a process. Problem 523's odd restart-from-the-front sort is
  [insertion sort](/topics/technique/insertion-sort) in disguise, so its total move count is a sum of
  one cost per inserted element. Each element's cost depends only on its rank among the elements
  before it, and in a [uniformly random permutation](https://en.wikipedia.org/wiki/Random_permutation)
  that rank is uniform — so each piece's expectation is a short average, and the total is a single
  sum over positions.

**Condition, then recur.** When a piece is itself the output of a process, define its value by
what happens next and solve the resulting [recurrence](https://en.wikipedia.org/wiki/Recurrence_relation).
In 523 the cost of one insertion is self-similar — the moved element displaces some smaller ones,
each of which must then be re-inserted by the same procedure — so the cost satisfies
$T(s) = 1 + \sum_{i<s} T(i)$, which closes in one line. The general shape, first-step analysis, is

```
E[state] = cost(state) + Σ  P[state → next] · E[next]      # terminal states pinned
```

and when the states are ordered it is a single [DP](/topics/technique/dynamic-programming) sweep.

**When the target is not a sum,** neither move applies directly. Problem 253 asks for the
expected *maximum* segment count while forty pieces fill a row in random order — and
$\mathbb{E}[\max]$ is not the max of expectations. The fix is to put the running peak into the state
and push the full probability *distribution* forward through a
[Markov chain](https://en.wikipedia.org/wiki/Markov_chain), taking the expectation only at the end.
Linearity still earns its place one level down: the next step depends on the empty-gap widths, and a
symmetry argument shows those widths are a uniform random composition independent of the history, so
they can be replaced by their averages — legitimate precisely because the transition counts are
*linear* in the widths.

## Exactness is part of the technique

An expectation over a finite, uniform space is a ratio of integers, so the true answer is a
[rational number](/topics/technique/rational-number-application). These problems ask for it to two,
six, or nine decimals, and that format is where most wrong answers come from:

- 523's given $E(10)$ lies *exactly* on a rounding half. Any floating-point drift can push such a
  value either way, and Python's `round` would apply banker's rounding to it besides. Summing the
  terms as `fractions.Fraction` (GMP `mpq_t` in C) and rounding with an integer
  $\lfloor 100E + \tfrac12 \rfloor$ makes the last digit deterministic.
- 493's answer is a ratio of two binomials near $10^{18}$; printing it to nine places from a
  `double` would be guessing. Keeping numerator and denominator as integers (`math.comb`, or
  `__int128` with the multiplicative formula in C) and rounding by scaled integer division costs
  nothing.
- 253 shows the other side of the judgement: a forward pass that only adds and multiplies
  non-negative probabilities is numerically benign, so it runs in `double` — after one exact
  rational run confirmed the error sits far below the sixth place.

The rounding helper is generic and worth having once:

```python
def round_fraction(num: int, den: int, places: int) -> str:
    q = (2 * num * 10**places + den) // (2 * den)       # half-up, integers only
    whole, frac = divmod(q, 10**places)
    return f'{whole}.{frac:0{places}d}'
```

## How to reason about it

- **Name the pieces first.** "Expected number of X" → one indicator per possible X. "Expected cost
  of a process" → one term per step, or per element. If you can name the pieces and each one's
  average is a short computation, linearity finishes the job however the pieces interact.
- **Use symmetry to collapse identical pieces.** Seven colours that look alike give one probability
  times seven; a uniformly random rank gives a plain average over its range.
- **Check linearity applies before reaching for it.** Max, min, "ever exceeds", products — carry
  the distribution in the state instead (253), and let linearity work on whatever *is* linear inside
  the transitions.
- **Verify the derivation, not just the code.** Each of these was cross-checked against brute force
  on small sizes, compared *as exact fractions* — a decomposition argument that is subtly wrong
  still produces a plausible-looking number. A [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method)
  run is a sanity check on the real parameters, never the source of the answer.
- **Round once, in integers, at the end.** Ask how many places the output wants, and whether a half
  can occur; if either makes you hesitate, keep the value a fraction.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0523](/solutions/0523/) — First Sort I

<!-- /problems -->
