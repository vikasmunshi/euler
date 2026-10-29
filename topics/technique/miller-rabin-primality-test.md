<!-- tags: [miller-rabin-primality-test] -->
<!-- status: final -->
# Miller–Rabin primality test

The [Miller–Rabin primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)
answers "is this one number prime?" in a few modular exponentiations, without factoring it and
without knowing anything about its neighbours. That last clause is the whole reason it keeps
appearing below. The [Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) is the better
tool when you want *every* prime under a bound you can afford to allocate; Miller–Rabin is what you
reach for when the candidates are too large to sieve to, or too scattered to be worth sieving
through — a handful of digit patterns, one cofactor left after trial division, six offsets around
`n²`, the `d + 1` for each divisor `d` of a target, the pieces a factoring routine has split off.

## The idea

[Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) says that if `n`
is prime then `a^(n-1) ≡ 1 (mod n)` for any `a` not divisible by `n`. Testing that directly is the
[Fermat test](https://en.wikipedia.org/wiki/Fermat_primality_test), and it has a fatal flaw: the
[Carmichael numbers](https://en.wikipedia.org/wiki/Carmichael_number) (561, 1105, 1729, …) pass it
for *every* coprime base, so no amount of retrying catches them.

Miller–Rabin patches the hole with a second fact. Modulo a prime, the only square roots of 1 are
`±1`. So write `n - 1 = 2^s · d` with `d` odd, and instead of jumping straight to `a^(n-1)`, climb
there by squaring: compute `a^d`, then square it `s` times. If `n` is prime that chain must reach 1,
and the step just before it must be `n - 1`. Concretely, `n` passes base `a` when

- `a^d ≡ 1 (mod n)`, or
- `a^(2^r · d) ≡ -1 (mod n)` for some `0 ≤ r < s`.

A composite that satisfies this is a *strong* pseudoprime to base `a`, and unlike the Fermat
version there is no Carmichael-style universal impostor: at most a quarter of the bases below `n`
can lie for a given composite, so `k` random bases leave a `4^-k` error. The loop is a direct
transcription:

```python
d, s = n - 1, 0
while d % 2 == 0:
    d //= 2
    s += 1
for a in witnesses:
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        continue                 # this base is satisfied
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            break
    else:
        return False             # a proves n composite
return True
```

Each base costs `O(log n)` modular multiplications, so the whole test is `O(k log³ n)` bit
operations with schoolbook arithmetic — logarithmic in `n`, where trial division is `O(√n)`. That
gap is the point: testing a 19-digit number costs about what testing a 10-digit one does.

## Deterministic below a bound

The `4^-k` bound is what earns Miller–Rabin the "probabilistic" label, and for Project Euler
work that label is misleading — nobody here uses random bases. Below a known ceiling, a **fixed**
witness set has been verified exhaustively to have no strong pseudoprimes at all, which makes the
test a proof rather than a bet:

| Witness set | Proven correct for all `n <` |
| --- | --- |
| `2, 3, 5, 7` | 3 215 031 751 (≈3.2·10⁹) |
| `2, 3, 5, 7, 11, 13, 17` | 341 550 071 728 321 (≈3.4·10¹⁴) |
| `2, 3, 5, 7, 11, 13, 17, 19, 23` | 3 825 123 056 546 413 051 (≈3.8·10¹⁸) |
| `2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37` | 318 665 857 834 031 151 167 461 (≈3.2·10²³) |
| `2, 325, 9375, 28178, 450775, 9780504, 1795265022` | 2⁶⁴ |

The last row is Sinclair's set — seven arbitrary-looking bases found by search, covering the whole
64-bit range at roughly half the cost of the twelve-prime set. (The values are in the
[OEIS/known-bases literature](https://oeis.org/A014233), which tabulates the smallest strong
pseudoprime to the first `k` prime bases; each threshold above is one of those numbers.)

The engineering decision, then, is: **bound your candidates, pick the smallest set that covers
them, and stop there.** Problem 293 and problem 487 both cap out near 3.2·10⁹ and use four bases;
problem 516 tests candidates just above 10¹² and takes the seven-prime row, the smallest that
covers them; problem 245 tests cofactors that can approach 2⁶⁴ and uses Sinclair's seven; the digit-pattern
problems (111, 200, 387) go wider and take the twelve small primes. Using twelve bases where four
suffice is a 3× tax on the hottest loop in the program.

That tax only counts when the test *is* the hot loop. Problem 248 inverts Euler's totient, and
its candidate primes all sit below 3.12·10⁹, so they would fit under the four-base row. It runs all
twelve anyway, and that is the right call: it makes 1584 calls in total, all of them during setup,
next to a search that emits hundreds of thousands of solutions. Spending more on the witness set
than the bound requires is fine when the test runs a few thousand times. Only tune it when the
profile shows the test dominating.

## Making the test rare

Miller–Rabin is fast per call and slow per million calls. Every solution below spends its effort
on the same thing: **arranging for the test to run as seldom as possible.** Four layers, cheapest
first:

1. **Trial-divide by the small primes.** One `n % 3` rejects a third of the survivors of `n % 2` for
   the price of a division. A dozen small primes strip out roughly 80% of random candidates before
   a single `pow` is issued.
2. **Sieve the small range, test only the tail.** When the problem needs both — all primes up to
   some working bound *and* primality of a few huge numbers — build the sieve for the bound and call
   Miller–Rabin only above it. Problems 200, 245 and 545 all carry both a sieve and an `is_prime`
   for exactly this split: the sieve factors and enumerates, Miller–Rabin adjudicates the leftover
   cofactor.
3. **Prefilter with residue arithmetic.** Problem 146 is the extreme case: it needs `n² + k` prime
   for six offsets simultaneously, which is six tests per `n`. Instead of testing, it precomputes a
   wheel modulo `2·3·5·7·11·13 = 30030` listing the residues that can possibly work, then rejects
   further on `n² mod p` for `p` up to 37 — a fixed-set membership check per prime. Only a few
   candidates per thousand ever reach a `pow`, and the six tests are chained with `and` so the first
   failure aborts the rest.
4. **Let the structure generate the candidates.** Sometimes the best filter is to build only the
   numbers that could possibly work. Problem 248 needs every prime `p` with `(p − 1) | 13!`, since
   only those can appear in an `n` with `φ(n) = 13!`. Scanning integers for that property would be
   hopeless. Instead it expands the factorisation of `13!` into its 1584 divisors and tests each
   `d + 1`. That comes to 1584 tests, and 459 of them pass. The largest passing candidate is above
   3·10⁹, so a sieve would allocate billions of entries just to answer about fifteen hundred
   questions. This is the case where Miller–Rabin clearly beats sieving: the candidates are few,
   large, and come from the problem's algebra rather than from an interval.
   Problem 516 has the same shape at a larger scale. A prime `q > 5` can divide an `n` whose totient
   is 5-smooth only if `q − 1` is itself 5-smooth, so the candidates are `h + 1` for the
   [Hamming numbers](https://en.wikipedia.org/wiki/Regular_number) `h ≤ 10¹²`. There are only 3429
   of those, and 543 of the `h + 1` are prime. A sieve to 10¹² is out of the question, while 3429
   tests take a few milliseconds.

The general shape is a funnel: cheap arithmetic filters at the top, the modular exponentiation only
at the bottom. If your profile shows Miller–Rabin dominating, the fix is usually a better filter,
not a faster test.

## The stopping rule for factoring

Miller–Rabin never hands you a factor, but it is half of the standard way to get one. The other
half is [Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm). Rho finds *some*
non-trivial divisor of a composite in about `O(n^¼)` steps. It gives no guarantee that the divisor
is prime, and run on a prime it never finishes. So the factoring loop keeps a stack of unresolved
pieces. For each piece, Miller–Rabin decides what happens next: a prime goes into the
factorisation, and a composite goes to rho and is split into two more pieces:

```python
while stack:
    m = stack.pop()
    if is_prime(m):
        factors.add(m)
    else:
        d = pollard_rho(m)
        stack += [d, m // d]
```

Problems 271 and 443 both use this loop, each for its own reason. Problem 271 has to factor one
17-digit modulus (`13082761331670030`, given in the statement). Its cube roots of unity are then
built prime power by prime power and recombined through the CRT. Trial division up to 1000
removes the small primes, and the rho-plus-Miller–Rabin loop handles the cofactor. Problem 443
needs a fresh factorisation of `d − 1` at each of the sequence's gcd jumps. The jumps grow
geometrically, so there are only `O(log n)` of them, but the numbers being factored grow too, and
trial division to their square roots would dominate the run. In both problems the test is cheap
compared with rho, so its cost hardly matters. What matters is that it is *deterministic*. A
false "prime" would put a composite into the factorisation without any error, and a false
"composite" would send rho into a loop that never ends.

## Details that bite

- **Guard the small cases.** `n < 2`, and `a ≥ n` (the base must be reduced or skipped — for `n = 3`
  a witness of 3 is `0 mod n` and fails a prime). The clean idiom is to trial-divide by the small
  primes first and return `n == small` on a hit, which disposes of every degenerate case before the
  main loop.
- **`x * x % n` vs `pow(x, 2, n)`.** Both are correct; the explicit multiply is measurably faster in
  CPython for the squaring step, since `pow`'s three-argument path has setup cost that a single
  square does not amortise. The initial `pow(a, d, n)` should of course stay a `pow`.
- **The square overflows long before the modulus does.** Python never notices. In C, `x * x % n`
  for a 64-bit `n` overflows once `n` passes √2⁶³ ≈ 3.04·10⁹, which is a modulus that easily fits
  in an `int64_t`. Problem 248's largest candidate is about 3.11·10⁹, only just over that line. Its
  C port therefore does every modular multiply through an `__int128` product,
  `(long long)((__int128)a * b % m)`. So do the C solutions here for problems 111, 131, 293, 487 and 516,
  among others. Going unsigned only raises the limit to 2³². The test gives no sign of the overflow: it just
  returns the wrong verdict. Whenever a candidate can exceed about 3·10⁹, widen the multiply.
- **Read the witness table one row at a time.** The thresholds in
  [A014233](https://oeis.org/A014233) are indexed by how many prime bases you use. Twelve primes
  (up to 37) are proven correct below about 3.2·10²³. The bound of about 3.3·10²⁴ belongs to
  thirteen primes, which adds 41. The two are easy to swap in a docstring: the Python solutions to
  problems 271 and 443 both claim the larger bound for twelve bases. That costs nothing while
  the candidates stay well inside 64 bits, as theirs do. It matters a great deal when the claim is what tells you
  the test is safe for larger candidates.
- **Build tables inside `solve()`.** A wheel or a small sieve belongs in the function, sized to the
  inputs — not at module level. With `--runs=N` the harness times repeated `solve()` calls, and
  anything built at import is free from the second run onward, which flatters the benchmark.
- **`is_prime` is not `factor`.** Miller–Rabin says composite without saying *why*; it hands you no
  factor. When a problem needs the factorisation rather than the verdict, the test alone is the
  wrong tool. Reach for a smallest-prime-factor sieve when the range is small, or for Pollard's rho
  with Miller–Rabin as its stopping rule (above) when it is not.
- **The determinism has a ceiling.** The fixed witness sets are verified up to their stated bound
  and nowhere beyond it. If a candidate can exceed the bound you designed for, either widen the set
  or accept the probabilistic reading — silently running four bases against a 10³⁰ candidate is a
  wrong answer waiting to happen.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0245](/solutions/0245/) — Coresilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0443](/solutions/0443/) — GCD Sequence
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0545](/solutions/0545/) — Faulhaber's Formulas

<!-- /problems -->
