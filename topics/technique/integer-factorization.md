<!-- tags: [integer-factorization] -->
<!-- status: final -->
# Integer factorization

[Integer factorization](https://en.wikipedia.org/wiki/Integer_factorization) is the decomposition
of a positive integer into the product of its [prime factors](/topics/domain/prime-factor) — the
one operation that number theory leans on constantly and that nobody knows how to do quickly. Its
presumed hardness is what RSA is built on. At Project Euler's scale the cryptographic algorithms
never come out; what matters instead is a much more practical question, and it is the one this page
is about: *how do I arrange the computation so that I factor as few numbers as possible, and each
of those as cheaply as possible?*

## The idea — factoring one number versus factoring many

The textbook method is [trial division](/topics/technique/trial-division): walk the candidate
divisors upward, dividing out each one that fits, and stop at $\sqrt{n}$ — because if $n$ has any
factor above its square root it has a matching one below, so whatever survives the walk is either
$1$ or a prime. That is $O(\sqrt{n})$ per number, and at $n \approx 10^8$ it costs ten thousand
divisions each. Do it once and you will not notice. Do it ten million times and it is the whole
program.

Two adjustments make that gap disappear, and between them they cover almost every use in this
repository.

**Restrict the trial divisors to primes.** A composite candidate can never divide what its own
prime factors have already been divided out of, so dividing by $4$, $6$, $8$, … is pure waste. A
[sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) built once to $\sqrt{N}$ supplies
the prime list for every subsequent factorization, and by the
[prime number theorem](/topics/domain/prime-number-theorem) it cuts the inner loop by a factor of
about $\ln \sqrt{N}$ — roughly nine at $N = 10^8$. This is the shape problems 251 and 357 both use:
one sieve, then a near-linear pass that factorises many numbers against it.

**Ask the sieve when to stop early.** The expensive case for trial division is $n = 2q$ with $q$ a
large prime: nothing divides it, so the loop runs the full $\sqrt{n}$ and then reports the obvious.
If the sieve already covers $n$, you can consult it directly — after dividing out each small prime,
test whether the remaining cofactor is itself prime, and if so record it and stop:

```
for p in primes:
    while n % p == 0: n //= p; record(p)
    if sieve[n]: record(n); break      # cofactor is prime — done
    if p * p > n: break
```

Problem 357 does exactly this, and it is why factoring a hundred-million-scale survivor there takes
a single step rather than ten thousand. The trick costs nothing but the sieve you already built,
and it turns the worst case into the best one.

## Not every factorization has to be recovered

The sharpest saving is not a faster factoring routine but a restructuring that removes the need to
factor at all. If you are searching for numbers *with a given multiplicative shape*, generating
factorizations forward is enormously cheaper than generating integers and decomposing each one
backward.

Problem 88 is the clean example. Every product-sum set reduces, after the algebra, to a
factorization into factors $\ge 2$ — so instead of testing $N = 1, 2, 3, \dots$ and factoring each,
the solution recurses over non-decreasing factor sequences and reads off the set size each one
implies:

```python
def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
    """Relax min_prod for the set size implied by this factorization, then extend it."""
    k = prod - total + count
    if k < max_k:
        min_prod[k] = min(min_prod[k], prod)
        for i in range(start, max_k // prod * 2 + 1):
            find_product_sum(prod * i, total + i, count + 1, i)
```

No number is ever factorised. The non-decreasing constraint (`start`, passed down as `i`) makes
each factorization reachable by exactly one path, so there is no deduplication to do; the bound on
the loop prunes any branch whose product has already passed the useful range. The cost becomes
proportional to the number of factorizations in range rather than to the range itself. That
inversion — enumerate the structure, don't recover it — is the same one that
[depth-first search](/topics/technique/depth-first-search) exploits everywhere.

Problem 251 pushes the same idea further. Its Cardano triplets are governed by a divisibility
condition $b^2 \mid n^2(8n-3)$, and the naive reading is to walk $n$ into the tens of millions and
factorise $8n-3$ each time. Splitting $b$ against $n$ by their
[greatest common divisor](/topics/domain/greatest-common-divisor) re-parametrises the whole family
so that most of it is counted by a congruence and one division — no factorization at all — leaving
trial division to run only on the sparse tail where the parametrisation runs thin.

## Factorization as a route to something else

Factoring is rarely the goal. It is the step that unlocks a multiplicative property, and the
property usually determines how much of the factorization you actually need.

- **Divisors.** The [divisors](/topics/domain/divisor) of $n$ are the products over all exponent
  choices in its factorization. For a [square-free](/topics/domain/square-free-integer) $n$ with
  $\omega$ distinct primes that is exactly the power set — $2^{\omega}$ divisors, generated by
  doubling a list as each prime is folded in. Problem 357 relies on this: its survivors are
  square-free with at most eight distinct primes, so the divisor list never exceeds $256$ entries.
- **Predicates.** If you only need a yes/no answer, abandon the factorization the moment it is
  decided. Problem 357 rejects a candidate as soon as any prime appears twice, without ever
  finishing the decomposition — most rejections happen on the first or second divisor.
- **Cheap filters first.** Problem 357's dominant saving is not in the factoring at all: a single
  array lookup (`is 2 + n/2 prime?`) discards the overwhelming majority of candidates *before* any
  factorization runs. Order the tests by cost per unit of discrimination, and the expensive step
  ends up running on almost nothing.

## How to reason about it

When factorization shows up in a problem, work down this list in order:

1. **Can you avoid it?** If you are searching for numbers of a given multiplicative shape,
   enumerate factorizations forward instead of decomposing candidates backward.
2. **How many numbers must you factor, and can you shrink that set first?** A cheap necessary
   condition applied to the whole candidate set is worth more than any speed-up to the factoring
   routine.
3. **Are you factoring every number below $N$, or a scattered few?** Every number below $N$ wants a
   *sieve* — a smallest-prime-factor table, or a
   [divisor-sum sieve](/topics/technique/divisor-sum-sieve) if the aggregate is all you need —
   which amortises to near-constant time per number at the price of $O(N)$ memory. A scattered few
   wants trial division against a precomputed prime list, which costs nothing to set up.
4. **Does the sieve already cover your numbers?** Then use the cofactor-primality exit; it is the
   single highest-value line in a trial-division loop.
5. **How much of the factorization do you need?** Stop at the first repeated prime, at the first
   factor above a bound, at the largest prime factor — whatever the predicate decides on.

The floor on all of this is memory. A byte-per-entry sieve to $10^8$ is a hundred megabytes, which
is affordable; to $10^{10}$ it is not, and the shape of the solution has to change — segment the
sieve, or find the parametrisation that removes the need for it. And, as everywhere in this
repository, build the sieve *inside* `solve()`, sized to the input: the harness times repeated
calls, and a table built once at import is free on every run but the first.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0357](/solutions/0357/) — Prime Generating Integers

<!-- /problems -->
