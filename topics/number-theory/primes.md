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

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ○ [0234](/solutions/0234/) — Semidivisible Numbers
- ○ [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0243](/solutions/0243/) — Resilience
- ○ [0249](/solutions/0249/) — Prime Subset Sums
- ○ [0263](/solutions/0263/) — An Engineers' Dream Come True
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ○ [0273](/solutions/0273/) — Sum of Squares
- ○ [0274](/solutions/0274/) — Divisibility Multipliers
- ○ [0291](/solutions/0291/) — Panaitopol Primes
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0308](/solutions/0308/) — An Amazing Prime-generating Automaton
- ● [0313](/solutions/0313/) — Sliding Game
- ○ [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0333](/solutions/0333/) — Special Partitions
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ○ [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0425](/solutions/0425/) — Prime Connection
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0467](/solutions/0467/) — Superinteger
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ○ [0492](/solutions/0492/) — Exploding Sequence
- ● [0501](/solutions/0501/) — Eight Divisors
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ○ [0517](/solutions/0517/) — A Real Recursion
- ○ [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators
- ○ [0543](/solutions/0543/) — Prime-Sum Numbers
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0569](/solutions/0569/) — Prime Mountain Range
- ○ [0574](/solutions/0574/) — Verifying Primes
- ○ [0593](/solutions/0593/) — Fleeting Medians
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0609](/solutions/0609/) — $\pi$ Sequences
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0635](/solutions/0635/) — Subset Sums
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0659](/solutions/0659/) — Largest Prime
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0758](/solutions/0758/) — Buckets of Water
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0810](/solutions/0810/) — XOR-Primes
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0826](/solutions/0826/) — Birds on a Wire
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ○ [0869](/solutions/0869/) — Prime Guessing
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ○ [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ○ [0975](/solutions/0975/) — A Winding Path
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ○ [1005](/solutions/1005/) — Median Prime List

<!-- /problems -->
