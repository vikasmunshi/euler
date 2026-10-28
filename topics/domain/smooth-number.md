<!-- tags: [smooth-number] -->
<!-- status: final -->
# Smooth number

A number is [`y`-smooth](https://en.wikipedia.org/wiki/Smooth_number) when none of its prime
factors exceeds `y`. The 5-smooth numbers `2^a 3^b 5^c` are the classic
[Hamming numbers](https://en.wikipedia.org/wiki/Regular_number). Smoothness keeps coming back for
one reason: smooth numbers are **rare and highly structured**. Below a large bound there are far
too many integers to test one at a time, but only a small set of smooth ones, and each is fixed
by a short vector of exponents. So the problems below never scan the integers. Either they
generate the smooth numbers directly from their factorisations (204, 516, and in effect 108), or
they count the *non*-smooth numbers, which turn out to have the simpler description (668).

## The idea: a smooth number is an exponent vector

By the [fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic),
a `y`-smooth number `n ≤ L` is the same thing as a vector `(e₁, e₂, …, e_k)` of non-negative
exponents over the `k = π(y)` primes up to `y`, with `∏ pᵢ^eᵢ ≤ L`. For `y = 100` there are 25
primes, so the vectors are short and the product constraint prunes them hard. The standard
notation for the count is `Ψ(L, y)`. When `y` is fixed and `L` grows, it is roughly
`(log L)^k / (k! · ∏ log pᵢ)`, which is polylogarithmic in `L`. There are only a few thousand
5-smooth numbers below 10¹², and a few million 100-smooth ones below 10⁹. When the bound grows
with `L`, as in `y = L^(1/u)`, the fraction of smooth numbers is given by the
[Dickman function](https://en.wikipedia.org/wiki/Dickman_function) `ρ(u)`. That fraction is a
constant, not a vanishing one, which is why the "count the complement" route below is needed for 668.

Fixing the prime order makes the enumeration a [depth-first search](../technique/depth-first-search.md)
with no duplicates. From a running product `v` and a prime index `i`, I count `v` itself, then
for each later prime multiply in `p, p², p³, …` while the product stays within the bound:

```
count(v, i) = 1 + Σ_{k ≥ i} Σ_{e ≥ 1, v·p_k^e ≤ L} count(v·p_k^e, k+1)
```

Each smooth number has exactly one path from the root, so I need no set and no de-duplication.
The `≤ L` test cuts off every branch that cannot produce a valid number, so the cost is
proportional to the output and not to `L`. That is problem 204 in full: the 100-smooth
numbers up to 10⁹, counted by this recursion over a sieved list of the 25 primes.

## Smoothness as a filter on structure

The more interesting problems don't ask about smooth `n`. They ask for `f(n)` to be smooth, or
they use smoothness without naming it. The move is to push the condition through the
factorisation of `n` until it becomes a condition on a small set of primes.

- **Smooth totients (516).** [Euler's totient](eulers-totient-function.md) is
  [multiplicative](multiplicative-function.md), `φ(n) = ∏ p^(e−1)(p−1)`, so `φ(n)` is 5-smooth
  exactly when every factor is. For `p ∈ {2, 3, 5}` any exponent works. For a larger prime the
  `p^(e−1)` forces `e = 1`, and `p − 1` must itself be a Hamming number. The admissible `n` are
  therefore a Hamming number times a square-free product of the primes `h + 1`. I generate both
  sets with the DFS above, test each `h + 1` with
  [Miller–Rabin](../technique/miller-rabin-primality-test.md), and combine them with a prefix sum
  over the sorted Hamming numbers. Smoothness appears twice here: as the target property, and as
  the reason the candidate primes are so few.
- **Most divisors for the least `n` (108).** The question is about the
  [divisor function](divisor-function.md) `τ(n²) = ∏(2eᵢ + 1)`, and smoothness enters through
  the optimum. Exponents are what buy divisors, and small primes buy them cheaply, so the
  minimiser uses the smallest primes with non-increasing exponents: a
  [highly composite](highly-composite-number.md)-style number, which is smooth over a handful of
  primes. That turns a linear scan with trial division into a DFS over a tiny exponent tree, the
  same generator as 204 with an exchange argument added to prune it.

## When the smooth side is the hard side: count the complement

Problem 668 takes the bound relative to `n` itself: `n` is square-root smooth when its largest
prime factor `P(n)` satisfies `P(n)² < n`. These numbers have no convenient generator, and a
fixed fraction of all integers qualify, so enumerating them is the wrong way round. The failures
are easy to describe, though. Write `n = p·m` with `p = P(n)`. Then `n` fails exactly when `m ≤ p`,
and every pair `(p, m ≤ min(p, N/p))` is a distinct failure. Counting them gives

```
F(N) = Σ_{p ≤ √N} p  +  Σ_{p > √N} ⌊N/p⌋
```

and the answer is `N − F(N)`. The second sum groups by the quotient `⌊N/p⌋`
([quotient blocking](../technique/quotient-blocking.md)), so I only need the
[prime-counting function](prime-counting-function.md) at the `≈ 2√N` values `⌊N/k⌋`. That is
precisely the table a Lucy_Hedgehog / [Meissel–Lehmer](meissel-lehmer-algorithm.md) sieve builds
in `O(N^(3/4))` time. A smoothness question ends up as a prime-counting question.

## How to reason about it

- **Fixed small `y`, large `L`:** enumerate. `Ψ(L, y)` is tiny, the DFS costs time proportional
  to the output, and fixing the prime order rules out duplicates. If the problem needs the values
  sorted (prefix sums, binary search, "the k-th Hamming number"), generate them and sort, or use
  the classic [three-pointer merge](https://en.wikipedia.org/wiki/Regular_number#Algorithms) for
  5-smooth numbers in order.
- **Smoothness of `f(n)` for a multiplicative `f`:** factor the condition prime by prime. It
  usually forces exponents to 1 for the large primes, and leaves a short list of special primes
  (`p − 1` smooth, `p + 1` smooth, …) that are cheap to find by testing `h ± 1` for each smooth
  `h`, instead of sieving up to `L`.
- **Bound growing with `n` (`P(n) < n^(1/u)`):** the smooth numbers are a constant fraction
  `ρ(u)`, so enumeration is hopeless. Split `n = P(n)·m`, count the complement, and reduce to
  sums over primes. Those sums are a prime-counting problem.
- **Pitfalls:** guard `v · p ≤ L` as `p ≤ L / v` in C so the product never overflows; and decide
  whether 1 counts as smooth, because it is the empty product and the DFS root, and an off-by-one
  there shifts every count.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ○ [0468](/solutions/0468/) — Smooth Divisors of Binomial Coefficients
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ○ [0627](/solutions/0627/) — Counting Products
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ○ [0682](/solutions/0682/) — $5$-Smooth Pairs

<!-- /problems -->
