<!-- tags: [dirichlet-hyperbola-method] -->
<!-- status: final -->
# Dirichlet hyperbola method

The [Dirichlet hyperbola method](https://en.wikipedia.org/wiki/Dirichlet_hyperbola_method) sums a
[Dirichlet convolution](/topics/domain/dirichlet-convolution) `h = f * g` up to `n` by counting
lattice points under the hyperbola `d·q = n` — and noticing that the region is symmetric enough to
be swept from *both* axes, each sweep stopping at `√n`. What would be an `O(n)` loop over `m ≤ n`
(or worse, a loop over every divisor of every `m`) becomes two `O(√n)` loops and one correction
term. It recurs in the problems below because each of them, once the combinatorics or the dice or
the sequences are stripped away, turns out to be "sum a divisor-shaped function up to `10¹⁰`–`10¹⁸`",
and that is precisely the shape the method was built for.

## The idea

Any sum of a convolution is a sum over pairs:

```
Σ_{m≤n} (f*g)(m)  =  Σ_{m≤n} Σ_{d·q=m} f(d)·g(q)  =  Σ_{d·q≤n} f(d)·g(q).
```

The pairs `(d, q)` with `d·q ≤ n` are the [lattice points](/topics/technique/lattice-point) on or
under a hyperbola. Write `F` and `G` for the prefix sums of `f` and `g`, and pick a split
`u` with `v = ⌊n/u⌋`. Every point has `d ≤ u` or `q ≤ v` (it cannot have both coordinates large), so the
region is a vertical strip plus a horizontal strip, overlapping in a `u × v` rectangle:

```
Σ_{d·q≤n} f(d)·g(q)  =  Σ_{d≤u} f(d)·G(⌊n/d⌋)  +  Σ_{q≤v} g(q)·F(⌊n/q⌋)  −  F(u)·G(v).
```

With the symmetric choice `u = v = ⌊√n⌋` (an [integer square root](/topics/technique/math-isqrt),
never a float one) each strip has `√n` terms. The textbook instance is the
[divisor summatory function](/topics/domain/divisor-summatory-function), `f = g = 1`:

```python
s = isqrt(n)
D = 2 * sum(n // k for k in range(1, s + 1)) - s * s
```

That is the whole method. Its price is the requirement it puts on the two factors: **`F` and `G`
must be cheap to evaluate at the arguments `⌊n/k⌋`** — in closed form, or from a table computed
once for every such quotient.

### Relation to quotient blocking

[Quotient blocking](/topics/technique/quotient-blocking) gets the same `O(√n)` from the other
direction: walk `k` and jump over runs of constant `⌊n/k⌋`. The two are one geometry seen twice.
Blocking is a single sweep that collapses the far half of the axis into runs; the hyperbola method
reflects that far half onto the other axis, so both halves become plain loops with no run
boundaries to compute — which is also what makes it trivially vectorisable. Several solutions here
mix the two: they sum the near half term by term and the far half by blocks.

## How it plays out across the problems

**Problem 401** is the canonical case, and the place the two divisor articles meet.
`SIGMA₂(n) = Σ σ₂(m)` is the convolution of `f(d) = d²` with `g = 1`, so `F` is the sum of the first
`x` squares — closed form `x(x+1)(2x+1)/6` — and `G(x) = x`. Both strips are closed-form term by
term, and the bound `10¹⁵` leaves `√n ≈ 3·10⁷` terms, which numpy runs in fixed-size chunks. The
divisor-summatory page treats the *function* being summed; this page is the *machine* that sums it.

**Problem 944** does not announce a convolution at all. A double-counting argument turns the subset
sum into `Σ_x x · 2^(n − ⌊n/x⌋)` — the weight depends on `x` only through `⌊n/x⌋`, which is the
hyperbola's signature. The solution splits at `√n`: small `x` are summed one by one, large `x` are
grouped by their quotient with triangular-number block sums. It is the hyperbola split in its
mixed, blocked form — and a reminder to look for `⌊n/x⌋` *after* the combinatorics, not before.

**Problem 641** uses the method with an **unbalanced** split. The dice showing 1 reduce to counting
pairs `c³·q² ≤ X` with `q` squarefree and `μ(q) = +1` (see the
[Möbius function](/topics/domain/mobius-function)). That is a lattice count under a curve — a
"hyperbola" of shape `c³q² = X` — and its two axes cost very different amounts: for a fixed `q`,
the number of valid `c` is one integer cube root; for a fixed `c`, the number of valid `q` needs a
signed squarefree count, i.e. the squarefree counting function plus the Mertens function. So the
split sits not at a symmetric `√` but at `q ≈ 4·X^(1/3)`: small `q` are summed directly over a sieve,
and only a handful of small `c` reach the expensive side. Choosing `u ≠ v` to balance *cost*, not
term count, is the general form of the method.

**Problem 319** shows the method applied recursively. After the sequence constraints collapse to
counting cells cut by roots `m^(1/i)`, Möbius inversion gives `t(n) = 1 + Σ_{d≤n} μ(d)·F(⌊n/d⌋)` with
a closed-form `F` — a convolution with `μ`. Grouping by `⌊n/d⌋` needs the prefix sum of `μ`, the
[Mertens function](/topics/technique/mertens-function-application), at every quotient. And Mertens
is itself computed by the hyperbola identity for `μ * 1 = ε`: `M(v) = 1 − Σ_{j≥2} M(⌊v/j⌋)`. Sieving
`μ` up to `n^(2/3)` and recursing above it is the standard balance and gives the `O(n^(2/3))` total
— the same tool, this time producing the prefix sums it then consumes.

## How to reason about it

- **Reach for it when** the target is `Σ_{m≤n} h(m)` with `n` far past sieving range and `h` splits
  as `f * g` (divisor sums `σ_k = idᵏ * 1`, divisor counts, `φ = μ * id`, anything from Möbius
  inversion), or when the summand depends on its index through `⌊n/x⌋`. If you can write
  "sum over `d·q ≤ n`", the method applies.
- **The cost is in the prefix sums.** When both `F` and `G` are closed-form, you get a clean
  `O(√n)`. When one of them is not (Mertens, squarefree counts, prime counts), evaluate it at every
  `⌊n/k⌋` by a sieve below `n^(2/3)` plus a memoised recursion above — and move the split point
  toward whichever side is cheaper.
- **Mind the overlap term.** Forgetting `F(u)·G(v)` double-counts the rectangle; taking `v` as
  anything other than `⌊n/u⌋` miscounts its edge. Both errors are off by a little, so the answer
  looks plausible — check against a brute force at `n ≤ 10⁴`, which takes seconds.
- **Modular closed forms need care.** `x(x+1)(2x+1)/6` and `x(x+1)/2` at `x ≈ 10¹⁵` overflow 64 bits
  before the division; divide the 2 and the 3 out of whichever factor they divide *first*, then
  reduce (see [watch integer width](/topics/takeaway/watch-integer-width)). That also avoids
  needing a modular inverse of 6 when the modulus is not coprime to it.
- **It vectorises.** Both strips are independent loops over `1..√n` with no data dependence, so they
  map straight onto numpy arrays (or a tight C loop) — unlike the jump loop of quotient blocking,
  whose next index depends on the current one.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0944](/solutions/0944/) — Sum of Elevisors

<!-- /problems -->
