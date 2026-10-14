<!-- tags: [trial-division] -->
<!-- status: final 2026-10-12T14:50Z -->
# Primes

Most of the problems below are not *about* primes in the way problem 7 is. Nobody asks for the
primes themselves. They ask for a quadratic that stays prime for a long run (27), the largest
pandigital number that happens to be prime (41), a spiral whose diagonals thin out (58), a set of
primes that stay prime when glued together pairwise (60), or a number whose every divisor pair sums
to a prime (357). In each one, primality is a **predicate**: a yes/no filter applied to a stream of
candidates that some other structure produces. [Prime Numbers](/topics/number-theory/prime-numbers)
covers what the primes are, and [Trial division](/topics/technique/trial-division) covers the loop
that tests them. This page is about the shape these problems share, a *generator* feeding a *test*,
and about where the engineering effort pays off in that shape.

## Generator and predicate

Every one of these searches costs roughly

$$\text{cost} \approx (\text{number of candidates}) \times (\text{cost of one primality test}).$$

That gives two levers. The tempting one is the second: a faster test, a wheel, Miller–Rabin. The one
that pays more is nearly always the first. A primality test is a *general* tool: it knows nothing
about where the number came from. The generator knows everything about that, and most of that
knowledge can be turned into an argument that whole families of candidates are composite before
any of them is tested. Do that arithmetic first, then choose the test to fit whatever candidates
are left.

## Kill candidates with arithmetic first

The cheapest primality test is the one you prove you never need to run. The same few arguments
come back again and again:

| Argument | What it rules out | Where |
| --- | --- | --- |
| **Boundary values.** Plug in the trivial input. | $n^2 + an + b$ at $n = 0$ is $b$, so $b$ must itself be prime: 2001 values of $b$ shrink to the 168 primes below 1000. | 27 |
| **Digit sum mod 3.** A number's residue mod 3 is its digit sum's residue. | A $1..n$ pandigital has digit sum $n(n+1)/2$ whatever the order, which is divisible by 3 for every $n$ except 1, 4 and 7. Of nine lengths, two survive. | 41 |
| **Digit sum mod 3, again.** | Replacing $k$ digit positions with $0..9$ moves the digit sum through ten values in steps of $k$. Unless $3 \mid k$, at least three of the ten are divisible by 3, so an eight-prime family has to replace a multiple of three positions. | 51 |
| **Algebraic form.** Factor the expression. | The spiral's bottom-right corner is $(2k+1)^2$, never prime. $n^3 + n^2p = n^2(n+p)$ forces $p$ into the one-parameter family $3a^2 + 3a + 1$. | 58, 131 |
| **Parity and tiny differences.** 1 is not prime, and 2 is the only even prime. | On the hexagonal spiral, neighbours at distance 1 and even differences rule out every tile except the first two in each ring. | 128 |
| **The trivial divisor pair.** $(1, n)$ divides every $n$. | "$d + n/d$ prime for all $d \mid n$" forces $n + 1$ to be prime, $n$ to be squarefree and (for $n > 1$) even, and $2 + n/2$ to be prime. That cuts $10^8$ candidates to a few million, most of them rejected by one lookup. | 357 |

The pattern is the same each time. Ask what the generator *guarantees* about its output (a fixed
digit sum, a factorable form, a forced small divisor), then ask which primes could survive that
guarantee. The search that is left is often small enough that the choice of test hardly matters.
Problem 41 is the clearest public example. One line of number theory does the work of the search
before the loop starts:

```python
pandigital_primes = (
    number
    for length in (7, 4)                       # digit-sum mod 3 kills every other length
    for number in gen_n_digit_pandigital_numbers(length, descending=True)
    if fast_is_prime(number)
)
return str(next(pandigital_primes))
```

## Choose the test by the candidate stream

Once the candidates are pruned, the right test depends on what they look like as a *stream*: how
many there are, how large they get, and whether their ceiling is known in advance.

- **Dense candidates under a known ceiling: sieve once, look up in $O(1)$.** Problem 128's
  differences are linear in the ring index, and problem 357's candidates are all below $10^8$. A
  [sieve](/topics/technique/sieve-of-eratosthenes) to that ceiling turns every test into an array
  read, and the build cost is shared by all of them.
- **Sparse candidates spread over a large range: test each one.** Problem 58 makes the contrast
  plain. Its corners reach about $7 \times 10^8$, but there are only four per layer, a few tens of
  thousands of tests in total. A sieve to $7 \times 10^8$ would mark hundreds of millions of cells
  to answer those few queries. Trial division costs at most about 13 000 divisions per corner, so
  it wins easily. Problems 27 and 41 are in the same position.
- **Large individual candidates: Miller–Rabin.** Once single candidates pass roughly $10^{12}$,
  $\sqrt{n}$ divisions per test is too slow, and a
  [deterministic Miller–Rabin](/topics/technique/miller-rabin-primality-test) settles each one in a
  few modular exponentiations. Problem 131 uses it even for candidates in the tens of millions, because its cost barely grows with $n$. Problems 248 and
  293 put a cheap small-prime prefilter in front of it.
- **No ceiling known in advance: grow the sieve as you go.** Problem 46 walks upward looking for a
  counterexample whose size it cannot predict. An *incremental* sieve, a dictionary from each
  upcoming composite to the primes that reach it, classifies each integer as it arrives and never
  commits to a bound.
- **The same predicate asked repeatedly: cache it or precompute it.** Problem 60's clique search
  asks "do $p$ and $q$ concatenate to primes both ways?" for the same pairs many times, so the pair
  test is memoised. Problem 118 goes further: before the search starts it builds a table of the
  primes formed by each of the 511 non-empty digit subsets, and during the search primality is
  never tested again.

## Order the search so the first hit is the answer

A predicate search often wants an extreme: the largest, the smallest, the first. Generate the
candidates in that order and you can stop at the first one that passes. Problem 41 enumerates
permutations in descending order, length 7 before length 4, so the first prime it finds is the
maximum. Problem 51 walks the primes in ascending order, so the first qualifying family is the
smallest. Problem 118 uses ordering for a different goal: it requires each chosen prime to exceed
the previous one, so every unordered partition is produced by exactly one path and needs no
deduplication. In all three cases the order of generation does work that would otherwise need a
sort, a max over the results, or a set.

## Details that bite

- **Size the sieve for the largest *candidate*, not the largest input.** Problem 27's coefficients
  stay below 1000, but $n^2 + an + b$ reaches about $2 \times 10^6$. Problem 60's primes stay below
  $10^4$, but their concatenations reach $10^8$. A sieve sized from the inputs fails silently, by
  reading past its end or by calling every out-of-range value composite.
- **Reject everything below 2.** Constructed values can be 0, 1 or negative ($n^2 + an + b$ with a
  large negative $a$; the length-1 pandigital "1"). Every `is_prime` in these solutions opens with
  `if num < 2: return False`. A test that only works for the inputs you expected is the one that
  turns an off-by-one into a wrong answer.
- **Prove the pruning, then encode it.** A hard-coded `(7, 4)` or "replace three digits" is only
  as good as the argument behind it. Put that argument in a comment next to the constant. Then a
  reader, or the C translation, can check it, and if the parameters change, the claim is
  re-derived rather than copied.
- **Build tables inside `solve()`.** A sieve, prime list or memo table built once at import is free
  from the second `--runs` iteration onwards, so the benchmark understates the real cost. Size it
  to the input and build it in the function.

The idea to take away is that the primality test is rarely where a prime-filter problem is won.
The win comes from what the generator can *prove* about its candidates before the test runs.

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
