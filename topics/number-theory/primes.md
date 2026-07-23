<!-- tags: [prime-number, sieve-of-eratosthenes, trial-division, wheel-factorization, miller-rabin-primality-test] -->
<!-- status: final -->
# Generating and testing primes

A [prime number](https://en.wikipedia.org/wiki/Prime_number) is a whole number
greater than 1 whose only divisors are 1 and itself — the multiplicative atoms every
other integer factors into. They are the single most recurrent object in Project
Euler, and a prime-heavy problem almost always reduces to one of three questions:
*give me every prime up to some bound*, *is this one number prime*, or *what are the
prime factors of this number*. Each has its own right tool, and reaching for the
wrong one is the usual reason a prime-heavy solution is slow.

## The three questions, and their tools

The tools sort cleanly by which question you are asking.

**Enumerate every prime up to N — the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes).**
Write down every number from 2 to `N`; walk the list, and each time you meet a number
still standing, cross out all of its multiples. What survives is exactly the primes.
Two observations make it fast: start crossing out from `p*p` (every smaller multiple
of `p` already carries a smaller factor), and stop sieving once `p*p > N`. The whole
pass runs in `O(N log log N)` — very nearly linear — so whenever a problem needs *all*
the primes below a known ceiling, the sieve is almost always the answer. In
`solutions/public/p0010/` the core is three lines of `bytearray` strided assignment:

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

The subtlety a sieve carries into Euler work is the *bound*. You often want "the first
`n` primes" rather than "primes below `N`", and you must size the sieve before you
know where the `n`-th prime lands. The
[prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem) supplies
the estimate: the `n`-th prime is near `n·ln n`, so sieving `[1, n·ln n]` is enough —
exactly the ceiling `solutions/public/p0007/` uses to reach the 10 001st prime. When
even that range will not fit in memory, a *segmented* sieve processes the interval in
cache-sized windows, and an *incremental* sieve — a generator keyed on each prime's
next multiple — yields primes endlessly with no upper bound fixed in advance.

**Factor or test a single number — [trial division](https://en.wikipedia.org/wiki/Trial_division).**
When you have one number, not a range, sieving the whole space below it is wasteful.
To factor `n`, divide by 2, 3, 4, … and peel off each divisor you find; to test
primality, divide by candidates up to `√n` and call it prime if none divide it. The
`√n` cutoff is the crux: a composite `n` must have a factor no larger than its square
root, so nothing above `√n` can be its *smallest* factor. A second saving is to divide
each factor out completely as you go — then every divisor you meet is automatically
prime and needs no separate primality check. Problem 3 in `solutions/public/p0003/`
does exactly this, recomputing the `√`-ceiling against the shrinking remainder so the
loop ends early once only a large prime cofactor is left.

**Skip the numbers that can't be prime — [wheel factorization](https://en.wikipedia.org/wiki/Wheel_factorization).**
Trial division spends most of its time dividing by numbers that are themselves
composite. Every prime past 2 is odd, so stepping by 2 halves the work; every prime
past 3 is `≡ 1` or `5 (mod 6)`, so walking the pattern `6k ± 1` skips two-thirds. A
*wheel* generalises this: fix a few small primes (2, 3, 5, …) and visit only the
residues coprime to their product. It does not change the asymptotics — it shaves a
constant factor off both trial division and the sieve — but on a factoriser's hot
loop that constant is worth having.

**Test a *large* single number — the [Miller–Rabin primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test).**
Trial division to `√n` is fine up to perhaps `10^12`; past that its cost explodes.
Miller–Rabin instead asks a witness question: write `n − 1 = 2^s · d` and check, for a
chosen base `a`, whether the repeated squarings of `a^d (mod n)` betray `n` as
composite. A single base can be fooled, but each independent base that passes
multiplies your confidence — and for `n` below fixed thresholds a *specific small set
of bases* makes the test **deterministic**, exactly correct with no probability left.
Its cost is `O(k log³ n)` for `k` bases: effectively instant even for numbers with
dozens of digits, which is why the higher-numbered primality problems reach for it
rather than a sieve.

## How to reason about which one

The decision is almost mechanical:

- Need **many** primes below a **known** bound? → sieve. Size it to the inputs
  (`n·ln n` for "the `n`-th prime"), and build it *inside* `solve()`, not at module
  level, so the benchmark counts its cost honestly.
- Need to **factor** one number, or the numbers in a modest range? → trial division
  with the `√n` cutoff and full division-out, sped up by a `6k ± 1` wheel.
- Need a **yes/no** on one **large** number? → Miller–Rabin, with a deterministic base
  set when the number fits the known thresholds.

The classic mistake is to answer a range question one number at a time — calling a
primality test in a loop where a single sieve would produce the whole set in one
`O(N log log N)` pass — or to answer a single-number question with a sieve, building a
table of millions of primes to check just one. Match the tool to the shape of the
question and most prime problems become straightforward. The problems below all turn
on that choice.

<!-- problems (generated by update-tags) -->
## Problems

- [0003](/solutions/0003/) — Largest Prime Factor · solved
- [0007](/solutions/0007/) — 10 001st Prime · solved
- [0010](/solutions/0010/) — Summation of Primes · solved
- [0012](/solutions/0012/) — Highly Divisible Triangular Number · solved
- [0021](/solutions/0021/) — Amicable Numbers · solved
- [0023](/solutions/0023/) — Non-Abundant Sums · solved
- [0027](/solutions/0027/) — Quadratic Primes · solved
- [0029](/solutions/0029/) — Distinct Powers · solved
- [0035](/solutions/0035/) — Circular Primes · solved
- [0037](/solutions/0037/) — Truncatable Primes · solved
- [0041](/solutions/0041/) — Pandigital Prime · solved
- [0046](/solutions/0046/) — Goldbach's Other Conjecture · solved
- [0047](/solutions/0047/) — Distinct Primes Factors · solved
- [0049](/solutions/0049/) — Prime Permutations · solved
- [0050](/solutions/0050/) — Consecutive Prime Sum · solved
- [0051](/solutions/0051/) — Prime Digit Replacements · solved
- [0058](/solutions/0058/) — Spiral Primes · solved
- [0060](/solutions/0060/) — Prime Pair Sets · solved
- [0069](/solutions/0069/) — Totient Maximum · solved
- [0070](/solutions/0070/) — Totient Permutation · solved
- [0072](/solutions/0072/) — Counting Fractions · solved
- [0075](/solutions/0075/) — Singular Integer Right Triangles · solved
- [0077](/solutions/0077/) — Prime Summations · solved
- [0087](/solutions/0087/) — Prime Power Triples · solved
- [0097](/solutions/0097/) — Large Non-Mersenne Prime · solved
- [0108](/solutions/0108/) — Diophantine Reciprocals I · solved
- [0111](/solutions/0111/) — Primes with Runs · solved
- [0118](/solutions/0118/) — Pandigital Prime Sets · solved
- [0123](/solutions/0123/) — Prime Square Remainders · solved
- [0124](/solutions/0124/) — Ordered Radicals · solved
- [0127](/solutions/0127/) — abc-hits · solved
- [0128](/solutions/0128/) — Hexagonal Tile Differences · solved
- [0130](/solutions/0130/) — Composites with Prime Repunit Property · solved
- [0131](/solutions/0131/) — Prime Cube Partnership · solved
- [0132](/solutions/0132/) — Large Repunit Factors · solved
- [0133](/solutions/0133/) — Repunit Nonfactors · solved
- [0134](/solutions/0134/) — Prime Pair Connection · solved
- [0136](/solutions/0136/) — Singleton Difference · solved
- [0146](/solutions/0146/) — Investigating a Prime Pattern  · solved
- [0152](/solutions/0152/) — Sums of Square Reciprocals · solved
- [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal · solved
- [0170](/solutions/0170/) — Pandigital Concatenating Products · solved
- [0171](/solutions/0171/) — Square Sum of the Digital Squares · solved
- [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles · solved
- [0187](/solutions/0187/) — Semiprimes · solved
- [0188](/solutions/0188/) — Hyperexponentiation · solved
- [0193](/solutions/0193/) — Squarefree Numbers · solved
- [0196](/solutions/0196/) — Prime Triplets · solved
- [0200](/solutions/0200/) — Prime-proof Squbes · solved
- [0202](/solutions/0202/) — Laserbeam · solved
- [0203](/solutions/0203/) — Squarefree Binomial Coefficients · solved
- [0204](/solutions/0204/) — Generalised Hamming Numbers · solved
- [0214](/solutions/0214/) — Totient Chains · solved
- [0216](/solutions/0216/) — The Primality of $2n^2 - 1$ · solved
- [0221](/solutions/0221/) — Alexandrian Integers · solved
- [0228](/solutions/0228/) — Minkowski Sums · solved
- [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients · solved
- [0234](/solutions/0234/) — Semidivisible Numbers · unsolved
- [0239](/solutions/0239/) — Twenty-two Foolish Primes · unsolved
- [0243](/solutions/0243/) — Resilience · solved
- [0249](/solutions/0249/) — Prime Subset Sums · unsolved
- [0263](/solutions/0263/) — An Engineers' Dream Come True · unsolved
- [0266](/solutions/0266/) — Pseudo Square Root · unsolved
- [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100 · unsolved
- [0273](/solutions/0273/) — Sum of Squares · unsolved
- [0274](/solutions/0274/) — Divisibility Multipliers · unsolved
- [0291](/solutions/0291/) — Panaitopol Primes · unsolved
- [0293](/solutions/0293/) — Pseudo-Fortunate Numbers · solved
- [0304](/solutions/0304/) — Primonacci · solved
- [0308](/solutions/0308/) — An Amazing Prime-generating Automaton · unsolved
- [0313](/solutions/0313/) — Sliding Game · solved
- [0315](/solutions/0315/) — Digital Root Clocks · unsolved
- [0329](/solutions/0329/) — Prime Frog · unsolved
- [0333](/solutions/0333/) — Special Partitions · unsolved
- [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes · solved
- [0355](/solutions/0355/) — Maximal Coprime Subset · unsolved
- [0357](/solutions/0357/) — Prime Generating Integers · solved
- [0365](/solutions/0365/) — A Huge Binomial Coefficient · unsolved
- [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial · solved
- [0387](/solutions/0387/) — Harshad Numbers · solved
- [0425](/solutions/0425/) — Prime Connection · unsolved
- [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors · solved
- [0437](/solutions/0437/) — Fibonacci Primitive Roots · unsolved
- [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime · unsolved
- [0467](/solutions/0467/) — Superinteger · unsolved
- [0478](/solutions/0478/) — Mixtures · solved
- [0487](/solutions/0487/) — Sums of Power Sums · solved
- [0492](/solutions/0492/) — Exploding Sequence · unsolved
- [0501](/solutions/0501/) — Eight Divisors · solved
- [0515](/solutions/0515/) — Dissonant Numbers · unsolved
- [0517](/solutions/0517/) — A Real Recursion · unsolved
- [0518](/solutions/0518/) — Prime Triples and Geometric Sequences · unsolved
- [0521](/solutions/0521/) — Smallest Prime Factor · unsolved
- [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators · unsolved
- [0543](/solutions/0543/) — Prime-Sum Numbers · unsolved
- [0545](/solutions/0545/) — Faulhaber's Formulas · solved
- [0552](/solutions/0552/) — Chinese Leftovers II · unsolved
- [0565](/solutions/0565/) — Divisibility of Sum of Divisors · solved
- [0569](/solutions/0569/) — Prime Mountain Range · unsolved
- [0574](/solutions/0574/) — Verifying Primes · unsolved
- [0593](/solutions/0593/) — Fleeting Medians · unsolved
- [0603](/solutions/0603/) — Substring Sums of Prime Concatenations · unsolved
- [0609](/solutions/0609/) — $\pi$ Sequences · unsolved
- [0633](/solutions/0633/) — Square Prime Factors II · unsolved
- [0635](/solutions/0635/) — Subset Sums · unsolved
- [0650](/solutions/0650/) — Divisors of Binomial Product · solved
- [0659](/solutions/0659/) — Largest Prime · unsolved
- [0687](/solutions/0687/) — Shuffling Cards · unsolved
- [0694](/solutions/0694/) — Cube-full Divisors · solved
- [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences · unsolved
- [0717](/solutions/0717/) — Summation of a Modular Formula · unsolved
- [0734](/solutions/0734/) — A Bit of Prime · unsolved
- [0753](/solutions/0753/) — Fermat Equation · unsolved
- [0758](/solutions/0758/) — Buckets of Water · unsolved
- [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions · solved
- [0773](/solutions/0773/) — Ruff Numbers · unsolved
- [0779](/solutions/0779/) — Prime Factor and Exponent · unsolved
- [0800](/solutions/0800/) — Hybrid Integers · solved
- [0801](/solutions/0801/) — $x^y \equiv y^x$ · unsolved
- [0808](/solutions/0808/) — Reversible Prime Squares · solved
- [0810](/solutions/0810/) — XOR-Primes · unsolved
- [0817](/solutions/0817/) — Digits in Squares · unsolved
- [0826](/solutions/0826/) — Birds on a Wire · unsolved
- [0834](/solutions/0834/) — Add and Divide · solved
- [0845](/solutions/0845/) — Prime Digit Sum · solved
- [0853](/solutions/0853/) — Pisano Periods 1 · solved
- [0869](/solutions/0869/) — Prime Guessing · unsolved
- [0874](/solutions/0874/) — Maximal Prime Score · unsolved
- [0926](/solutions/0926/) — Total Roundness · solved
- [0927](/solutions/0927/) — Prime-ary Tree · unsolved
- [0932](/solutions/0932/) — $2025$ · solved
- [0934](/solutions/0934/) — Unlucky Primes · solved
- [0942](/solutions/0942/) — Mersenne's Square Root · unsolved
- [0946](/solutions/0946/) — Continued Fraction Fraction · unsolved
- [0952](/solutions/0952/) — Order Modulo Factorial · unsolved
- [0971](/solutions/0971/) — Modular Polynomial Composition · unsolved
- [0975](/solutions/0975/) — A Winding Path · unsolved
- [0995](/solutions/0995/) — A Particular Pair of Polynomials · unsolved
- [1005](/solutions/1005/) — Median Prime List · unsolved

<!-- /problems -->
