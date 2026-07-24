<!-- tags: [eulers-totient-function, partition-number-theory, pentagonal-number-theorem, continued-fraction, amicable-numbers, eulerian-path, eulerian-number, linear-sieve] -->
<!-- status: final -->
# Euler

More of the mathematics behind these problems traces to one man than to any other. [Leonhard
Euler](https://en.wikipedia.org/wiki/Leonhard_Euler) did not just prove theorems; he built the
tools we still reach for — the totient function, the theory of partitions, continued fractions,
the first theorem of graph theory. The problems collected here are not a biography. They are the
places where one of Euler's constructions is the *shortest path to the answer*, and where knowing
his identity turns a search into a formula.

The thread running through almost all of them is the same instinct: **replace a count you cannot
enumerate with a structure you can compute.** A generating function becomes a recurrence; a
multiplicative function becomes a product over primes; an irrational becomes a periodic sequence
of integers. Each section below is one instance of that move.

## Multiplicativity: the totient

[Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function) `φ(n)` counts the
integers up to `n` that are coprime to `n`. Its power is that it is *multiplicative* and has a
closed product form,

```
φ(n) = n · ∏ (1 - 1/p)     over the distinct primes p | n
```

so you never enumerate the coprime residues — you factor `n` and multiply. Problem 69 (Totient
Maximum) is this identity read backwards: since `n/φ(n) = ∏ p/(p-1)`, the ratio is maximised by
piling in the *smallest* primes, so the answer under a bound is a primorial and the loop is a
handful of multiplications:

```python
result = 1
for prime_num in primes_generator():
    if (result := result * prime_num) > limit:
        result //= prime_num
        break
```

The same function carries [Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem) —
`a^φ(n) ≡ 1 (mod n)` for `gcd(a, n) = 1`, the generalisation of Fermat's little theorem — which is
what lets the RSA problem (182) and the hyperexponentiation problem (188) collapse an astronomical
exponent down modulo `φ(n)`. When a problem needs `φ` across a whole range rather than at one
point, compute it with a sieve (a modified Sieve of Eratosthenes seeding `φ(p) = p-1`), not by
factoring each number in turn.

## Generating functions: partitions and the pentagonal number theorem

Euler founded the theory of [integer partitions](https://en.wikipedia.org/wiki/Partition_(number_theory))
by writing the count `p(n)` as a generating function, `∏ 1/(1-x^k) = Σ p(n) x^n`. The naïve
recurrence from that product is a full convolution. His
[pentagonal number theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem) makes it
*sparse*: the reciprocal product has almost all coefficients zero, leaving

```
p(n) = Σ (-1)^(k-1) · [ p(n - g(k)) + p(n - g(-k)) ],   g(k) = k(3k-1)/2
```

where `g(k)` runs over the generalized pentagonal numbers. Only `O(√n)` terms per `n` survive, so
`p(n)` up to `N` costs `O(N√N)` instead of `O(N²)`. Problem 78 (Coin Partitions) is that
recurrence almost verbatim — the whole solve is the inner loop over pentagonal `g(k)`, reduced
mod the divisor:

```python
while (pent := pentagonal(k)) <= n:
    partition_value += (-1) ** (k - 1) * partitions[n - pent]
    # ... and the paired term for g(-k)
    k += 1
```

Problems 76 and 77 are partitions under a constraint (which parts are allowed); 45 and 76/78 are
where the pentagonal (and its cousin figurate) numbers show up directly.

## Continued fractions

In *De fractionibus continuis* Euler put [continued
fractions](https://en.wikipedia.org/wiki/Continued_fraction) on a systematic footing: every
rational terminates, quadratic irrationals become *periodic*, and the truncations — the
*convergents* — are the best rational approximations for their size. His discovery that

```
e = [2; 1, 2, 1, 1, 4, 1, 1, 6, ...]
```

has a clean pattern is the whole of problem 65, where you build the `n`-th convergent with exact
rational arithmetic and read a digit off its numerator. The `√2` and Pell-equation problems (57,
64, 66) walk the *periodic* expansion of `√D`, and generate convergents with the standard
recurrence `hₙ = aₙ·hₙ₋₁ + hₙ₋₂` rather than re-evaluating the nested fraction each step.

## The rest of the reach

Euler's fingerprints are wider than number theory:

- **Amicable numbers.** Before Euler only three [amicable pairs](https://en.wikipedia.org/wiki/Amicable_numbers)
  were known; in one 1750 memoir he found fifty-eight more. Problems 21 and 95 chase the same
  divisor-sum function `d(n)` — 21 for the pairs, 95 for the longer "sociable" chains.
- **Graph theory.** The [Seven Bridges of Königsberg](https://en.wikipedia.org/wiki/Eulerian_path)
  gave the subject its first theorem: a connected graph has an Eulerian path iff it has at most two
  odd-degree vertices. Problem 289 counts such trails on a grid of loops.
- **Eulerian numbers.** Distinct from the paths, the
  [Eulerian numbers](https://en.wikipedia.org/wiki/Eulerian_number) `⟨n k⟩` count permutations by
  their number of ascents; they surface in problem 158.
- **The linear sieve.** Euler's refinement of Eratosthenes crosses off each composite *exactly
  once*, via its smallest prime factor, giving both the primes and a smallest-prime-factor table in
  a genuine `O(n)` pass — the workhorse behind problems 153, 549 and 745.

## How to reason about it

The lesson is not "memorise Euler's results" but recognising the shape that invites one:

- A count that is **multiplicative** — factor and take a product; never enumerate. The totient is
  the archetype.
- A sequence with a **product generating function** — look for a sparse recurrence. The pentagonal
  number theorem is the model: an infinite product whose reciprocal is almost all zeros.
- A **best rational approximation** or a **Pell equation** — reach for continued fractions and their
  convergents.
- A **huge exponent modulo `n`** — reduce the exponent mod `φ(n)` by Euler's theorem before you
  compute anything.

The pitfall in every case is doing the brute-force version first. These identities exist precisely
because the direct count is infeasible; the win comes from spotting the structure *before* writing
the loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0031](/solutions/0031/) — Coin Sums
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0243](/solutions/0243/) — Resilience
- ○ [0245](/solutions/0245/) — Coresilience
- ○ [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ○ [0289](/solutions/0289/) — Eulerian Cycles
- ○ [0302](/solutions/0302/) — Strong Achilles Numbers
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0333](/solutions/0333/) — Special Partitions
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ○ [0351](/solutions/0351/) — Hexagonal Orchards
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ● [0478](/solutions/0478/) — Mixtures
- ○ [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ○ [0591](/solutions/0591/) — Best Approximations by Quadratic Integers
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0625](/solutions/0625/) — Gcd Sum
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0656](/solutions/0656/) — Palindromic Sequences
- ○ [0688](/solutions/0688/) — Piles of Plates
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ● [0745](/solutions/0745/) — Sum of Squares II
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0859](/solutions/0859/) — Cookie Game
- ○ [0890](/solutions/0890/) — Binary Partitions
- ○ [0911](/solutions/0911/) — Khinchin Exceptions
- ○ [0922](/solutions/0922/) — Young's Game A
- ○ [0931](/solutions/0931/) — Totient Graph
- ○ [0939](/solutions/0939/) — Partisan Nim
- ○ [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0958](/solutions/0958/) — Euclid's Labour

<!-- /problems -->
