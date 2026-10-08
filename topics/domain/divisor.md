<!-- tags: [divisor] -->
<!-- status: final -->
# Divisor

A [divisor](https://en.wikipedia.org/wiki/Divisor) of `n` is an integer `d` with `n = d · e` for
some integer `e`. That one-line definition is about the most reused object in the archive. It
turns up as the thing being counted or summed (`σ₀`, `σ₁`, amicable pairs), as the structure a
problem quietly reduces to once the algebra is done (a Diophantine equation that becomes "count
the factorisations of `n²`"), and as a playing field: a lattice to find antichains in, a graph to
walk, a game where each move replaces `n` by one of its divisors. Each guise has its own standard
tools, and most of the work is recognising which one you are looking at.

## The idea

### Divisors come in pairs, and the pairs meet at √n

Every divisor `d ≤ √n` has a partner `n/d ≥ √n`. That is the whole basis of trial-division
enumeration: test up to `√n`, emit both halves of each pair, and don't count `√n` twice when `n` is
a square. [Problem 21](/solutions/0021/) uses exactly this to compute the sum of proper divisors
`s(n) = σ(n) − n` for its [amicable-pair](https://en.wikipedia.org/wiki/Amicable_numbers) test:

```python
@functools.lru_cache(maxsize=None)
def sum_factors(n: int) -> int:
    """Sum of the proper divisors of n, via square-root divisor pairing."""
    n_sqrt = int(n**0.5)
    return 1 + sum((i + n // i for i in range(2, n_sqrt + 1) if n % i == 0)) - (n_sqrt if n_sqrt**2 == n else 0)
```

It is `O(√n)` per number, which is fine for one number and wasteful for ten million of them.

### The factorisation is the divisor list

Write `n = p₁^e₁ · … · p_k^e_k`. Then every divisor is `p₁^f₁ · … · p_k^f_k` with `0 ≤ fᵢ ≤ eᵢ`,
and the [divisor functions](https://en.wikipedia.org/wiki/Divisor_function) are products over the
prime powers:

$$ \sigma_0(n) = \prod_i (e_i + 1), \qquad \sigma_1(n) = \prod_i \frac{p_i^{e_i+1} - 1}{p_i - 1}. $$

Both are [multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function), so once you have
the factorisation, counting or summing divisors is arithmetic, and *listing* them is a nested loop
over exponents. The cheap way to get many factorisations at once is a smallest-prime-factor sieve:
after one `O(N log log N)` pass, factoring any `x ≤ N` takes `O(log x)` steps. When the number you
need is a product of coprime pieces, factor the pieces separately and concatenate.
[Problem 834](/solutions/0834/) does this with `n(n − 1)`: consecutive integers share no prime, so
the factorisation of `n − 1` from the previous iteration is reused as-is.

### Turn the loop inside out: sieve over multiples

If you need a divisor statistic for *every* `n ≤ N`, don't ask each `n` for its divisors. Ask each
`d` for its multiples:

```python
for d in range(1, N + 1):
    for m in range(d, N + 1, d):
        sigma[m] += d          # or count[m] += 1, or any per-pair weight
```

The total work is `N/1 + N/2 + … + N/N`, the [harmonic sum](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics)),
`O(N log N)`, and there is no division anywhere. This inversion works for any quantity built from
divisor pairs `(d, n/d)`, not only `σ`. [Problem 256](/solutions/0256/) counts the factor pairs
`a × b = s` whose room passes a tiling test. Its sieve walks each width `a` and adds one to every
area `a · b` whose length `b` passes, which makes it an ordinary divisor sieve with a filter on
each pair.

### Floors of `n/d` take only `2√n` values

Summatory questions such as `Σ_{n ≤ N} σ₀(n)`, or anything weighted by how many multiples `d` has,
are sums over `⌊N/d⌋`. Swapping the order of summation gives

$$ \sum_{n \le N} \sigma_0(n) = \sum_{d \le N} \left\lfloor \frac{N}{d} \right\rfloor, $$

and `⌊N/d⌋` is constant on blocks of `d`: it takes at most `2√N` distinct values. Summing block by
block (the [Dirichlet hyperbola method](https://en.wikipedia.org/wiki/Dirichlet_hyperbola_method)
and its "divisor-block" cousin) brings `O(N)` down to `O(√N)`, which is what makes `N = 10¹⁴`
reachable. [Problem 944](/solutions/0944/) is this pattern exactly. A contribution argument shows
that each `x` counts in a number of subsets that depends only on how many proper multiples it has,
`⌊n/x⌋ − 1`. The resulting sum over `x` collapses into `O(√n)` blocks of equal quotient.

### Algebra that ends in "divisors of something"

A surprising number of problems that don't mention divisors reduce to them once you rearrange the
equation:

- **Reciprocal equations.** `1/x + 1/y = 1/n` rearranges to `(x − n)(y − n) = n²`, so the
  solutions are the divisor pairs of `n²` and their number is `σ₀(n²)`, read off the
  factorisation of `n` with every exponent doubled. This is
  [Problem 454](/solutions/0454/)'s starting point.
- **Divisibility conditions.** [Problem 834](/solutions/0834/) asks when the `m`-th term of a
  sequence is divisible by `n + m`. Substituting `q = n + m` reduces the condition to
  `q | n(n − 1)/2`, so the answer runs over the divisors of a single number.
- **Every divisor pair satisfies a property.** [Problem 357](/solutions/0357/) wants `d + n/d`
  prime for every `d | n`. Looking at particular pairs prunes the search hard: the pair `(1, n)`
  forces `n + 1` prime, a repeated prime factor `p` makes `p + n/p` a multiple of `p` (so `n` must
  be square-free), and the pair `(2, n/2)` gives a cheap array lookup that discards most of what is
  left. Only the survivors get their full divisor list checked.
- **Theorems stated through divisors.** By the
  [von Staudt–Clausen theorem](https://en.wikipedia.org/wiki/Von_Staudt%E2%80%93Clausen_theorem), the
  denominator of the Bernoulli number `B_k` is the product of the primes `p` with `(p − 1) | k`.
  [Problem 545](/solutions/0545/) needs exactly that denominator, so it becomes a search over `k`
  whose shifted divisors `d + 1` are prime.

### Divisibility as a structure

The divisors of `n`, ordered by divisibility, form a
[lattice](https://en.wikipedia.org/wiki/Divisor#Further_notions_and_facts) isomorphic to a product of chains, one
chain per prime of length `eᵢ + 1`. Several problems live on that object directly. Antichains in it
are the subject of [Problem 386](/solutions/0386/) (the
[de Bruijn–Tengbergen–Kruyswijk](https://en.wikipedia.org/wiki/Sperner_property_of_a_partially_ordered_set)
middle-layer result). Chains from `1` to `n` are
[ordered factorisations](https://en.wikipedia.org/wiki/Ordered_factorization)
([Problems 548](/solutions/0548/) and [606](/solutions/0606/)), and in the
[Divisor Game](/solutions/0550/) a move splits a pile into two of its proper divisors. What these
have in common is that the answer depends only on the **exponent signature**, the sorted multiset
`(e₁, …, e_k)`, and not on which primes carry it. That is what makes them feasible: `2³·5` and
`7³·11` have the same chain count and the same antichain size, so you compute each signature once
and memoise on it. Be careful before assuming this, though. In [Divisor Nim](/solutions/0509/) a
move *subtracts* a divisor (`n → n − d`), which ties the game to the actual value of `n`, so the
signature shortcut does not apply.

## How to reason about it

- **One number or all numbers?** For a single `n`, pair divisors up to `√n` or factor and expand.
  For every `n ≤ N`, invert the loop and sieve over multiples in `O(N log N)`, or build an SPF
  table once and factor in `O(log n)` per number.
- **A sum of divisor statistics is a sum of floors.** Swap the order of summation, then block on
  `⌊N/d⌋` for `O(√N)`. Reach for this before you reach for a bigger sieve.
- **Work from the factorisation.** `σ₀`, `σ₁` and the full divisor list all follow from the prime
  exponents. Factor coprime pieces separately; `n` and `n ± 1` are always coprime.
- **Memoise on the exponent signature.** If the question is about divisibility structure (chains,
  antichains, counts) and not the actual values, two numbers with the same exponent multiset have
  the same answer. Check that no step uses `n` itself (a subtraction, a bound) before relying on it.
- **Use the special pairs `(1, n)`, `(2, n/2)` and `(√n, √n)`.** When every divisor must satisfy
  something, these pairs usually kill most candidates before any enumeration happens.
- **Watch the boundaries.** `n` itself may or may not count ("proper" divisors exclude it), a
  perfect square has an unpaired middle divisor, and `d` and `n/d` coincide exactly once.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ○ [0263](/solutions/0263/) — An Engineers' Dream Come True
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ○ [0359](/solutions/0359/) — Hilbert's New Hotel
- ○ [0386](/solutions/0386/) — Maximum Length of an Antichain
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ○ [0462](/solutions/0462/) — Permutation of 3-smooth Numbers
- ○ [0468](/solutions/0468/) — Smooth Divisors of Binomial Coefficients
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0509](/solutions/0509/) — Divisor Nim
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ○ [0530](/solutions/0530/) — GCD of Divisors
- ○ [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ○ [0548](/solutions/0548/) — Gozinta Chains
- ○ [0550](/solutions/0550/) — Divisor Game
- ○ [0561](/solutions/0561/) — Divisor Pairs
- ○ [0563](/solutions/0563/) — Robot Welders
- ○ [0580](/solutions/0580/) — Squarefree Hilbert Numbers
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ○ [0606](/solutions/0606/) — Gozinta Chains II
- ○ [0608](/solutions/0608/) — Divisor Sums
- ○ [0646](/solutions/0646/) — Bounded Divisors
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0797](/solutions/0797/) — Cyclogenic Polynomials
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0896](/solutions/0896/) — Divisible Ranges
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ○ [0931](/solutions/0931/) — Totient Graph
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials

<!-- /problems -->
