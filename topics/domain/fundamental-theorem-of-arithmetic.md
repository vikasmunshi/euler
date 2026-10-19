<!-- tags: [fundamental-theorem-of-arithmetic] -->
<!-- status: final 2026-10-19T09:41Z -->
# Fundamental theorem of arithmetic

The [fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic)
says every integer $n > 1$ is a product of primes in **exactly one way**, up to order:
$n = p_1^{e_1} p_2^{e_2} \cdots p_k^{e_k}$. Existence is easy. **Uniqueness** is the part that
earns its keep in code, and it can be used in two directions. Read one way, the exponent vector
$(e_1, e_2, \dots)$ is a faithful *name* for $n$: two numbers are equal iff their vectors are. Read the
other way, every exponent vector names a *different* number. So you can generate numbers by choosing
exponents, and never produce the same one twice. The three solved problems below use one direction
or the other, and in each, uniqueness is what lets the solution skip a check that would otherwise
be needed.

## The idea — a number is its exponent vector

The [prime factorisation](/topics/domain/prime-factorization) is a bijection between the positive
integers and finitely supported vectors of non-negative exponents. Arithmetic becomes vector
arithmetic:

| on numbers | on exponent vectors |
|---|---|
| $a \times b$ | $e(a) + e(b)$ |
| $a^k$ | $k \cdot e(a)$ |
| $a \mid b$ | $e(a) \le e(b)$ componentwise |
| $\gcd$, $\operatorname{lcm}$ | componentwise $\min$, $\max$ |

Two uses follow:

- **As a key.** To test equality, or to deduplicate, compare exponent vectors instead of values. This
  helps most when the values are enormous but the vectors are short.
- **As a generator.** To list every number with some property of its factorisation ("all prime factors
  $\le 100$", "exactly the primes $p$ and $q$"), enumerate exponent vectors. Uniqueness guarantees
  each number appears once, so no `set` is needed.

## Three problems, three uses of uniqueness

**29, distinct powers: the vector as a deduplication key.** Count the distinct values of $a^b$ for
$2 \le a, b \le 100$. Collisions such as $2^4 = 4^2$ are exactly the cases where two exponent
vectors scaled by $b$ coincide. For the stated bounds the public Python simply puts the big
integers in a set. For larger bounds it switches to the canonical
[signature](/topics/technique/canonical-form) (prime, exponent × b):

```python
signature = tuple(((prime, power * b) for prime, power in prime_factors))
unique_powers.add(signature)
```

$1000^{1000}$ has 3,001 digits. Its signature is two pairs. Uniqueness of factorisation is what makes
"equal signatures ⇔ equal powers" true, so the short key loses nothing.

**204, generalised Hamming numbers: the vector as a generator.** Count the 100-smooth numbers up to
$10^9$, those whose prime factors are all at most 100 (see [smooth number](/topics/domain/smooth-number)
and [regular number](/topics/domain/regular-number)). The solution never tests numbers for smoothness.
It walks the exponent vectors over the 25 primes below 100 depth first: at depth $i$ it multiplies by
successive powers of the $i$-th prime while the product stays within the limit, then recurses on the
next prime. Because each product has one factorisation, it is reached along exactly one path, so
the count needs no deduplication and the work equals the answer.

**347, largest integer divisible by exactly two primes: a two-coordinate vector.** For each prime
pair $p < q$, $M(p, q, N)$ is the largest $p^a q^b \le N$ with $a, b \ge 1$. A number divisible by *only*
$p$ and $q$ is exactly one with exponent vector supported on those two coordinates, so the search
for each pair is a small 2-D walk: for each power $q^b$, push $p^a$ as high as it fits. Different
pairs can never produce the same number, so summing over all pairs with $pq \le N$ counts each
qualifying value once.

## Python and C

- **29**: the languages split on representation. Python's small-bound path is a one-line set of
  big integers. C has no big integers, so it carries its own base-$10^9$ multiply-by-small routine,
  serialises each power to a decimal string, and deduplicates those strings in a hand-written chained
  hash set. Its large-bound path encodes the signature as a `"p:e,p:e"` string in the same set. The
  factorisation lets C avoid the bignum entirely for large bounds, and it could just as well use it for
  small bounds.
- **204**: identical depth-first walk. C keeps the running product in `long long`. With the limit at
  $10^9$ and every prime below 100, `v *= p` peaks below $10^{11}$, so there is no overflow
  question. Python never has one.
- **347**: the same double power walk. Both take the primes from
  [primesieve](/topics/technique/primesieve): the Python binding's `primesieve.primes(n // 2)` and the
  C library's `primesieve_generate_primes`. That is the one place where these solutions call a library
  rather than implement the step themselves.

## How to reason about it

- **When values are huge but their factorisations are short, compare factorisations.** Equality,
  divisibility, gcd and powers all become cheap operations on exponent vectors.
- **When a property is about prime factors, generate by exponents instead of filtering by test.** Smooth
  numbers, numbers with a given radical, and numbers with $k$ distinct prime factors are all enumerated
  without duplicates, in work proportional to the output.
- **Uniqueness is the deduplication.** If you find yourself adding to a `set` while generating products
  of distinct prime powers, the set is redundant.
- **Pick the iteration order that prunes.** In 204 and 347, iterate primes or powers so that the
  "still $\le N$" test cuts a whole branch at once.
- **Factor by the cheapest adequate method.** [Trial division](/topics/technique/trial-division) up to
  $\sqrt{a}$ is plenty for $a \le 10^4$ (29). A smallest-prime-factor sieve pays off when you factor
  many numbers up to $10^6$ or more.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes

<!-- /problems -->
