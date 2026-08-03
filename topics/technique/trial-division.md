<!-- tags: [trial-division] -->
<!-- status: final -->
# Trial division

[Trial division](https://en.wikipedia.org/wiki/Trial_division) is the oldest factoring
method there is: to learn about `n`, divide it by 2, 3, 4, … and see what goes in evenly.
It is also the slowest — and it keeps appearing below anyway, because it is the only
elementary method that answers the question most of these problems actually ask. A sieve
tells you *which* numbers are prime. [Miller–Rabin](/topics/technique/miller-rabin-primality-test)
tells you *whether* one number is prime. Trial division tells you *what a number is made
of*, and hands you the factors while it works.

## Two jobs, one loop

The same loop does double duty, and it is worth being clear about which one you are
running.

As a **primality test**, the loop is a search for a counterexample: if no `d` in
`2 … √n` divides `n`, nothing above `√n` can either (a divisor `d > √n` would force a
cofactor `n/d < √n`, which the loop already ruled out), so `n` is prime. Cost is `O(√n)`
divisions.

As a **factorisation**, the loop peels: when `d` divides, strip *every* copy of it before
moving on. This is the version that carries most of the problems below, and it has a
property that is easy to miss — because factors come out in increasing order and each is
fully removed, every divisor the loop finds is *automatically prime*. No primality test is
needed anywhere in a trial-division factoriser. The canonical shape, from
`solutions/public/p0012/`:

```python
d = 2
while d * d <= n:
    if n % d == 0:
        exp = 0
        while n % d == 0:
            n //= d
            exp += 1
        factors.append((d, exp))
    d += 1
if n > 1:
    factors.append((n, 1))
```

That trailing `if n > 1` is the part people drop. When the loop ends, whatever is left is
either 1 or a single prime larger than `√n` — the largest prime factor, unfindable by the
loop itself because there is no room below the ceiling for its cofactor. Omitting it is
the classic trial-division bug: correct for `12`, silently wrong for `14`.

## The cuts that make it usable

Naive trial division is `O(n)`; a few observations bring it to something practical.

- **Stop at `√n`.** The single biggest win, and it is where the `O(√n)` comes from.
- **Shrink the ceiling as you go.** After dividing out a factor the remainder is smaller,
  so the ceiling should come down with it. `solutions/public/p0003/` recomputes it on every
  hit, which is what turns a 12-digit input into a few thousand divisions rather than a
  million:

  ```python
  if remaining_number % current_factor == 0:
      remaining_number = reduce(remaining_number, current_factor)
      search_limit = int(remaining_number ** 0.5)
  ```

- **Skip what cannot divide.** Handle 2 separately, then step by 2 through the odds — half
  the work for one special case. A [wheel](https://en.wikipedia.org/wiki/Wheel_factorization)
  goes further: after 2 and 3, every prime is `6k ± 1`, so stepping `d += 2, 4, 2, 4, …`
  covers the candidates in a third of the iterations. Problem 118 uses exactly that wheel,
  because it tests a great many nine-digit permutations and the constant factor is the
  whole budget.
- **Divide by primes, not by integers.** If you already have a prime list up to `√n` —
  which a sieve gives you cheaply — trial-dividing against it costs `O(π(√n))` rather than
  `O(√n)`, a further `ln` factor. `solutions/public/p0029/` carries both versions for
  contrast, and problems 157, 176 and 234 all sieve first specifically to feed the
  divider.

The asymptotics hide an important asymmetry: `O(√n)` is the **worst** case, and it is
reached only when `n` is prime or a semiprime with two large factors. On a smooth number
the loop exits almost immediately. Trial division is cheap exactly when the number has
small factors and expensive exactly when it does not — which is why it survives inside
otherwise sophisticated solutions whenever the numbers being factored are known to be
small or smooth. Problem 248 factorises `13!` this way without apology; problems 545 and
932 use it for a target and a step and nothing else.

## What you get beyond the verdict

Once you have the exponent vector `n = p₁^e₁ · p₂^e₂ · …`, the multiplicative functions
fall out arithmetically, and this is usually the real reason a solution factors at all:

| Wanted | From the factorisation |
| --- | --- |
| [divisor count](https://en.wikipedia.org/wiki/Divisor_function) `τ(n)` | `∏ (eᵢ + 1)` |
| divisor sum `σ(n)` | `∏ (pᵢ^(eᵢ+1) − 1) / (pᵢ − 1)` |
| [Euler's totient](/topics/domain/eulers-totient-function) `φ(n)` | `n · ∏ (1 − 1/pᵢ)` |
| [radical](https://en.wikipedia.org/wiki/Radical_of_an_integer) `rad(n)` | `∏ pᵢ` |

Problems 12, 108, 157 and 926 all want `τ`; 188 and 243 want `φ`; each computes it by
trial-dividing and then multiplying out. The pattern to internalise is that "count the
divisors of `n`" is never a divisor-counting loop — it is a factorisation followed by a
product over exponents.

A near relation worth naming separately is **divisor pairing**: the same `d ≤ √n` sweep,
but instead of dividing out, you record both `d` and `n/d` on each hit. That enumerates
*all* divisors (not just the prime ones) in `O(√n)`, which is what
`solutions/public/p0021/` uses for its proper-divisor sums. Same ceiling, same loop,
different payload — reach for pairing when you want the divisor list, for peeling when you
want the prime structure.

## When to reach for something else

Trial division is the default until one of three things is true.

- **You need the factorisations of a whole range.** Then `O(√n)` per number becomes
  `O(n√n)` overall, and a [smallest-prime-factor](/topics/technique/sieve-of-eratosthenes)
  sieve replaces it with one `O(n log log n)` build plus `O(log n)` lookups per number.
  Problems 130 and 545 both do this. The contrast is on display in `solutions/public/p0010/`,
  which solves the same problem four ways: the trial-division version is `O(n√n / log n)`
  and is there precisely to show what the sieve buys.
- **You only need the verdict, and `n` is large.** `√10¹⁸` is a billion divisions;
  Miller–Rabin settles the same number in a handful of modular exponentiations. Problems
  131, 248, 293 and 545 all pair a small-prime trial-division prefilter with Miller–Rabin
  behind it — the two are complements, not rivals. A dozen cheap `n % p` checks strip out
  most composites before any expensive test runs.
- **You need the factors of a large number.** Trial division cannot reach a 60-bit
  semiprime. That is [Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm)
  territory, or a proper sieve method.

## Details that bite

- **Prefer `d * d <= n` to `d <= int(n ** 0.5)`.** The comparison stays in exact integer
  arithmetic. Float `sqrt` is fine up to about `2⁵³`, but beyond that the rounding can put
  the ceiling one short and drop a factor — a bug that shows up only on the large inputs
  you were least likely to test.
- **Order the guards by cost.** `n < 2` and the even case before the loop, then odds only.
  Every branch you take before entering the loop is free relative to the loop.
- **Watch the loop condition after you divide.** If you shrink `n` inside the body, the
  `while d * d <= n` test re-reads the *new* `n` — which is the behaviour you want, but it
  means the loop bound is not what a reader assumes from the first line. Say so in a
  comment when it matters.
- **Build prime lists inside `solve()`.** A sieve used to feed the divider belongs in the
  function, sized to the input. With `--runs=N` the harness times repeated `solve()` calls,
  so a list built once at module import is free from the second run onward and the
  benchmark understates the real cost.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0243](/solutions/0243/) — Resilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0478](/solutions/0478/) — Mixtures
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$

<!-- /problems -->
