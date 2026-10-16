<!-- tags: [generation-of-primes] -->
<!-- status: final -->
# Generation of primes

Almost every prime problem starts with the same step: get hold of some primes. The
[ways of producing them](https://en.wikipedia.org/wiki/Generation_of_primes) differ less
in *what* they produce than in what they assume you already know: a bound, a count, or
only a stopping condition. Picking the generator is a question about the shape of the
problem, not about which algorithm is fastest in the abstract, and that is why the choice
keeps coming up across the problems below. This page maps the options and how I choose
between them. The mechanics of the workhorse are on the
[Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) page, and the library I
usually delegate to is on the [primesieve](/topics/technique/primesieve) page; neither is
repeated here.

## Three questions decide the generator

Before writing a line, I answer three questions:

1. **Do I know where the primes end?** A value bound ("primes below `N`") calls for a
   sieve over an array. A count ("the first `n` primes") becomes a value bound through
   the [prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem): the
   `n`-th prime is close to `n·ln n`. A bare condition ("primes until something holds")
   calls for a stream.
2. **Do I need all of them, or a verdict on a few?** Enumerating a range is sieve
   territory. Asking "is *this* number prime?" about scattered or huge numbers is a
   [primality test](https://en.wikipedia.org/wiki/Primality_test).
3. **Is the bound in memory?** Up to about `10⁸`–`10⁹` a flat array fits. Beyond that you
   segment the sieve, or shrink it to `√N` and let something else handle the big primes.

Those answers point at one of a handful of tools.

| Situation | Tool | Cost |
|---|---|---|
| all primes `≤ N`, `N` fits in memory | array sieve (Eratosthenes, or primesieve) | `O(N log log N)` time, `O(N)` space |
| all primes in `[a, b]`, `b` too large for an array | [segmented sieve](/topics/technique/segmented-sieve) | same time, `O(√b + window)` space |
| primes in order, no bound known | incremental sieve, or a library iterator | roughly sieve cost per prime, memory grows with the primes seen |
| a few dozen small primes | trial division against the primes found so far | trivial at that size |
| is one number `n` prime? (`n` small) | [trial division](/topics/technique/trial-division) to `√n` | `O(√n)` |
| is one number `n` prime? (`n` large) | [Miller–Rabin](/topics/technique/miller-rabin-primality-test) | `O(log³ n)` |

## The bound is usually derived, not given

The bound a sieve needs is rarely the number in the problem statement. Finding the right
one is most of the design work, and getting it wrong in either direction costs: too low
gives wrong answers, too high wastes time and memory.

- **Larger than the input.** Problem 187 counts semiprimes `p·q < N`. The second factor
  can be as large as `N/2` (when `p = 2`), so the prime list has to reach `N/2`, not
  `√N`. Once it does, `π(x)` for any `x` in range is a binary search on the sorted array,
  and the count becomes a sum of differences `π(N/p) − π(p−1)` over the small primes.
- **Smaller than the input.** Problem 193 counts squarefree numbers below `2⁵⁰`, but only
  primes up to `√N` can contribute a square factor, so it sieves the Möbius function to
  `2²⁵` and never touches the rest. Problem 464 sieves the same function but needs the
  whole range, because it uses every value of the running sums. Problem 772 takes every prime `≤ k`, but only those
  `≤ √k` appear with exponent above one in `lcm(1..k)`. Splitting at `√k` splits the work
  into two simple loops.
- **Exactly the input.** Problem 231 applies
  [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) to a binomial
  coefficient, and every prime `≤ n` can divide `n!`, so the list runs to `n`. Problem 381
  takes every prime below its limit and evaluates a closed form for each, vectorised over
  the whole array at once.
- **Only a band of it.** Problem 49 wants four-digit primes, so it sieves below `10⁴` and
  drops everything under `10³`. The public solution (`solutions/public/p0049/`) uses the
  Sieve of Sundaram for this. At that size the algorithm does not matter; the band does.

## When there is no bound: streams

Some searches stop on a condition, and no honest bound exists in advance. Then a
generator that yields primes forever is the right shape. The classic is the
**incremental sieve**: a dictionary maps each upcoming composite to the prime that will
strike it, so memory grows with the primes found rather than with a guessed ceiling.
`solutions/public/p0070/` carries this generator:

```python
composites: dict[int, int] = {}
n = 3
while True:
    if n not in composites:
        yield n
        composites[n * n] = n      # first multiple worth striking
    else:
        p = composites.pop(n)
        m = n + 2 * p              # next odd multiple
        while m in composites:
            m += 2 * p
        composites[m] = p
    n += 2
```

Two small tricks are already in it. Registering `n*n` instead of `2n` postpones every
prime until its square is reached, so the dictionary holds only the primes up to `√n`.
Stepping by 2 on both `n` and the strikes is the smallest
[wheel](/topics/technique/wheel-factorization): it never even looks at an even number.

Problem 808 uses the library equivalent, `primesieve.Iterator`, to stream primes until it
has collected enough reversible prime squares. That is the same pattern with a segmented,
wheel-based sieve behind it.

The cheapest stream of all is **trial division against the primes found so far**. It is
quadratic and you should not use it for thousands of primes. But problem 243 needs only
the first ten or so primes to build a [primorial](/topics/technique/primorial), and at that
size the simplest generator is the right one. Sizing the tool to the work goes in both
directions.

A pitfall here: a generator has no memory between calls. `solutions/public/p0070/`
restarts `primes_generator()` inside its outer loop, so each outer prime re-sieves from 3
up to its inner bound. That is correct, and fast enough at `10⁷`, but it repeats the same
prefix many times. Since both factors there are bounded by `2√N`, one array sieved once
and sliced per iteration would do the same work exactly once. A stream is for when you do
not know the bound. When you do, use an array.

## Wheels: never store what you know is composite

A [wheel](https://en.wikipedia.org/wiki/Wheel_factorization) skips the multiples of the
first few primes before any sieving starts. The odd-only trick is the 2-wheel: half the
memory, half the strikes. A 2·3·5 wheel keeps only the 8 residues mod 30 coprime to 30,
which is about 27% of the integers, and that is how primesieve fits 30 numbers into one
byte. The returns fall off quickly. Adding 7 keeps 23% instead of 27%, at the cost of a
48-spoke index table. So in hand-written code I stop at odd-only unless the sieve is the
whole cost of the program. The same idea speeds up trial division: test 2 and 3, then
only divisors of the form `6k ± 1`.

## Testing instead of generating

When the question is about a few numbers rather than a range, generating a range is
waste. Under about `10¹²`, trial division by primes up to `√n` is simple and adequate for
occasional checks. Above that, or in a hot loop, deterministic Miller–Rabin with a fixed
witness set is exact for 64-bit integers and costs a handful of modular exponentiations.
A middle path appears in problem 808: it asks primesieve to count the primes in the
one-element interval `[r, r]`, which amounts to sieving a tiny segment. That is a fine
test when `r` is moderate and a sieve library is already loaded.

A problem can mix both approaches. A common pattern on the
[Eratosthenes page](/topics/technique/sieve-of-eratosthenes)
is to sieve the small primes and *test* the one large prime that is left: every `n ≤ N`
has at most one prime factor above `√N`.

## Rules of thumb

- **Count the primes before you generate them.** `π(x) ≈ x / ln x` tells you whether a
  list fits in memory (about 5.1·10⁷ primes below `10⁹`, roughly 400 MB as `int64`) and
  how long a stream will run.
- **Prefer a library once the primes are only raw material.** Problems 187, 193, 231,
  381, 464 and 772 all hand generation to primesieve and spend their code on the actual
  idea.
- **Build inside `solve()`, sized to the inputs.** A module-level prime table is free
  after the first timed run and hides the real cost (see the
  [Eratosthenes page](/topics/technique/sieve-of-eratosthenes)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0243](/solutions/0243/) — Resilience
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
