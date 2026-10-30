<!-- tags: [logarithm] -->
<!-- status: final -->
# Logarithm

The [logarithm](https://en.wikipedia.org/wiki/Logarithm) is the inverse of exponentiation:
`log_b x` is the power you must raise `b` to in order to get `x`. On a page about programming
techniques I care about two of its properties more than its definition. It is a
**homomorphism**, turning multiplication into addition and powers into multiplication. And it is
**strictly increasing**, so it never changes the order of two positive numbers. Between them
these let a logarithm stand in for a number that is too large to store, too awkward to compare,
or tangled up in a product. The problems below each use one of these: counting digits, solving
for an exponent, comparing numbers that cannot be written down, and turning a multiplicative
structure into a linear one.

## The idea: change the scale, keep the order

Everything here follows from three identities and one inequality:

$$ \log(xy) = \log x + \log y, \qquad \log x^k = k \log x, \qquad \log_b x = \frac{\ln x}{\ln b}, $$

$$ 0 < x < y \iff \log x < \log y . $$

The first two say that a logarithm moves a problem one level down the ladder of operations.
Products become sums, powers become products, and towers of powers become ordinary powers.
The third says the base is only a constant factor, so pick whichever base makes the arithmetic
read naturally: base 10 for decimal digits, base 2 for bits and repeated squaring, `e` for
calculus. The inequality is what makes the trade safe. Any question about *which is larger* gets
the same answer on the log scale.

### Digits are a logarithm

A positive integer `N` has exactly `⌊log₁₀ N⌋ + 1` decimal digits, because
`10^(d−1) ≤ N < 10^d` is the definition of having `d` digits, and taking `log₁₀` of that sandwich
gives `d − 1 ≤ log₁₀ N < d`. So whenever a search space is described by *how many digits* a number
has, a logarithm turns a size bound into a length bound.

[Problem 30](/solutions/0030/) shows this best. It looks for numbers equal to the sum of the
fifth powers of their digits, and the set of integers is infinite, so the first job is a ceiling.
A `k`-digit number is at least `10^(k−1)`, but its digit-power sum is at most `k · 9⁵`, which grows
only linearly in `k`. The largest sum any candidate can produce has `⌈log₁₀(n · 9ⁿ)⌉` digits, and
that is the most digits a solution can have:

```python
upper_bound_num_digits = math.ceil(math.log(n * 9**n, 10))
```

For `n = 5` that is 6 digits. The logarithm turned an unbounded search into a fixed width, and
from there the solution enumerates digit multisets rather than integers.

### Solve for the exponent

The digit count runs the other way too. If a quantity shrinks like `yⁿ` with `0 < y < 1`, the
number of leading zeros after the decimal point — or, equivalently, of leading nines in `1 − yⁿ` —
is a digit count of `1/yⁿ`, and asking for at least `d` of them means solving `yⁿ ≤ 10^(−d)`.
Take logs and the exponent drops out as a quotient:

$$ n \ge \frac{d}{-\log_{10} y}, \qquad n_{\min} = \left\lceil \frac{d}{-\log_{10} y} \right\rceil . $$

[Problem 318](/solutions/0318/) is built on exactly this. It asks how many leading nines the
fractional part of `(√p + √q)^(2n)` has. The conjugate `y = √q − √p` makes
`x^(2n) + y^(2n)` an integer, so whenever `y < 1` the fractional part is `1 − y^(2n)`, and the
smallest `n` giving `d` nines is the ceiling above, with `2 log y` in the denominator. No power is
ever expanded: each of tens of thousands of `(p, q)` pairs costs one logarithm.

The catch is where `y` sits. For many pairs `y` is barely below 1, `log y` is tiny, `n` runs into
the millions, and the relative error in `log y` becomes the relative error in `n`. Computing
`√q − √p` and then `math.log` of it loses most of the significant digits twice over: once in the
subtraction of two nearly equal roots, and again because `log` near 1 sees only the digits of
`1 + (y − 1)` that survive rounding. The fix is to compute the small quantity `ε = 1 − y` directly,
from a rearranged expression whose denominator is a sum of positive terms, and hand it to
[`log1p`](https://docs.python.org/3/library/math.html#math.log1p), which evaluates `ln(1 + x)`
accurately for small `x`:

```python
n = d * math.log(10) / (-2 * math.log1p(-eps))   # not math.log(y)
```

A ceiling is only fragile when its argument lands near an integer, so the remaining guard is
cheap: re-derive just those borderline cases in arbitrary precision.

### Compare through the log when the numbers cannot exist

Monotonicity means you never need a number itself to know where it ranks — its logarithm will do.
That matters when the number is far too large to form. Take `x^(2^k)`: a value that has been
squared `k` times. One logarithm gives `2^k · log x`, which is still astronomical for large `k`.
A second gives

$$ \log_2 \log_2 x^{2^k} = k + \log_2 \log_2 x , $$

a small float that goes up by exactly 1 per squaring. [Problem 822](/solutions/0822/) repeatedly
squares the smallest entry of a list, about `10¹²` squarings per entry, and asks for the final sum
modulo a prime. The values have around `2^(10¹²)` digits, but a min-heap keyed by this double
logarithm still decides every comparison correctly. The same key also reveals the steady state.
Once squaring the minimum always makes it the new maximum (in log terms, `min key + 1 ≥ max key`),
the process becomes a fixed rotation and the rest is arithmetic. The logarithm handles the
*ordering*. The *value* is computed separately with modular exponentiation, because a float
logarithm cannot give you the residue.

### Linearise a multiplicative structure

The homomorphism property matters more than any single calculation. If the objects in a problem
combine by multiplication, then in log coordinates they combine by addition. Addition is linear:
lines stay lines, and sets become lattices and sumsets. [Problem 957](/solutions/0957/) is a
geometry problem about points spreading along lines through three fixed points. After a
projective change of coordinates, those lines become `y = c`, `x = c` and `x/y = c`. These are
multiplicative conditions, and with `u = log x`, `v = log y` they become three families of
*parallel* lines, `u = c`, `v = c` and `u − v = c`. The incidence geometry turns into exact integer
arithmetic on the lattice `ℤ²`, where counting is possible. The logarithm is never evaluated
numerically in that solution. It is used only as a change of variables, to show that the problem
was additive all along.

## How to reason about it

- **Reach for it when** a bound involves `aᵏ` against a polynomial in `k`, or you need the least
  `k` with `yᵏ` past a threshold (take logs and solve for `k`), when you must rank quantities you
  cannot store, or when a structure is built from products, ratios or powers and would be simpler
  as sums.
- **It buys** a smaller scale (huge numbers become modest floats), linearity (products become
  sums, and a multiplicative group becomes an additive lattice), and a direct digit count.
- **Floating-point is the trap.** `math.log10(1000)` can come out a hair under 3, so
  `⌈log₁₀ N⌉` and `⌊log₁₀ N⌋ + 1` can be off by one exactly at powers of ten. A bound that is used
  as a ceiling (as in Problem 30) tolerates being one too large. An exact digit count does not, so
  use `len(str(N))` or `N.bit_length()` for that, or check the neighbours with integers.
- **The logarithm is ill-conditioned near 1.** When the argument is `1 + x` with `x` small, form
  `x` itself without cancellation and call `log1p(x)` (and `expm1` for the inverse). Dividing by a
  tiny logarithm, as in Problem 318, magnifies whatever error it carries.
- **Log keys rank, they don't identify.** Two values whose logarithms differ by less than the
  float error look equal. That is harmless when distinct values are provably far apart on the log
  scale, or when a tie can be broken either way without changing the answer (both true in Problem
  822). Otherwise, confirm close calls with exact integer or modular arithmetic.
- **Keep the value and the order separate.** A logarithm tells you *which* number is larger or
  *how long* it is, never its last digits. Pair it with
  [modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation) when you need
  both.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0822](/solutions/0822/) — Square the Smallest
- ● [0957](/solutions/0957/) — Point Genesis

<!-- /problems -->
