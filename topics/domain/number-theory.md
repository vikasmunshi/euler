<!-- tags: [number-theory] -->
<!-- status: final -->
# Number theory

[Number theory](https://en.wikipedia.org/wiki/Number_theory) is the study of the integers on their
own terms — divisibility, primes, remainders, and the arithmetic functions built on top of them.
With 142 problems it is the third-largest domain tag in the archive, behind only
[combinatorics](/topics/domain/combinatorics) and
[modular arithmetic](/topics/domain/modular-arithmetic), and it is the one most often paired with
something sharper: 35 of these problems also carry `modular-arithmetic`, 24
[prime factorization](/topics/domain/prime-factorization), 21
[Diophantine equation](/topics/domain/diophantine-equation), 19
[multiplicative function](/topics/domain/multiplicative-function), 16
[divisor function](/topics/domain/divisor-function). Those pages describe the *objects*. This one
is about what all 142 have in common — the shape the question takes, and the small set of moves
that turn it from impossible into a few seconds of work.

## The question is almost always a summatory function

Strip the story away and a number-theory problem here nearly always reduces to

$$S(N) = \sum_{n \le N} f(n)$$

for some arithmetic function $f$ — a totient, a divisor count, a radical, an indicator that $n$ is
squarefree — with $N$ chosen large enough that evaluating $f$ once per $n$ is out of the question.
That framing is worth internalising, because it says exactly where the difficulty is. Computing
$f$ at a single point is usually easy and usually irrelevant. It is the $N$ of them that kills
you, and every technique below is a way of not doing them one at a time.

Problem 72 (public, `solutions/public/p0072/`) is the domain in miniature. It asks how many reduced
proper fractions have a denominator up to one million — a question about fractions, with no
$\sum$ in sight. But for a fixed denominator $d$ the numerators that survive reduction are exactly
those coprime to $d$, and counting them *is*
[Euler's totient](/topics/domain/eulers-totient-function) $\varphi(d)$. So the answer is
$\sum_{d=2}^{N} \varphi(d)$, and the entire solve is that recognition; what remains is arithmetic.

Learning to perform that translation — from the problem's language into a sum of a named arithmetic
function — is most of the skill this domain teaches. Problem 243 asks for the first denominator
whose "resilience" drops below a given ratio; resilience is $\varphi(d)/(d-1)$. Problem 179 counts
$n$ where $n$ and $n+1$ have equally many divisors; that is the divisor function $\tau$, twice.
Problem 124 sorts integers by their radical; the radical is a multiplicative function. Once the
function has a name, its literature — and its algorithms — come with it.

## Move 1 — build the whole table in one pass

$\varphi(d)$ for a single $d$ costs a factorization. $\varphi(d)$ for *every* $d \le N$ costs one
sieve, and the reason is [multiplicativity](/topics/domain/multiplicative-function): $\varphi$ is
determined by prime powers, via $\varphi(d) = d \prod_{p \mid d} (1 - 1/p)$. That product is over
primes dividing $d$, so instead of pulling each $d$'s primes in, you push each prime out to its
multiples. Problem 72's whole solution is nine lines:

```python
euler_totients: list[int] = list(range(max_d + 1))
result: int = 0
for n in range(2, max_d + 1):
    if euler_totients[n] == n:                       # untouched cell ⇒ n is prime
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
    result += euler_totients[n]                      # φ(n) is final by the time we read it
```

Two details generalise well beyond this problem. The first is that the sieve carries its own
primality test — a cell still equal to its index has been touched by no smaller prime, so its index
is prime — which means no separate boolean array. The second is the ordering argument on the last
line: every prime factor of $n$ is at most $n$, so cell $n$ is finished by the time the outer loop
arrives at it, and the sum can be accumulated in the same pass. Total cost is
$O(N \log \log N)$ against the $O(N \sqrt{N})$ of factoring each $d$ separately.

The pattern recurs with a different payload each time. Problem 124 sieves radicals by multiplying
each cell by each prime once. Problem 179 sieves divisor counts, and pairs divisors $(a, n/a)$ so
the outer loop only runs to $\sqrt{N}$. Problem 834 does the algebra first (below) and then sieves
divisor sums. The rule of thumb is blunt: **if you find yourself factoring inside a loop over a
range, you have the loop inside out.** Invert it — iterate over primes or divisors and push into an
array. See [sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) and
[precompute once, reuse](/topics/takeaway/precompute-once-reuse).

## Move 2 — swap the order of summation

A sieve needs an array of size $N$, so it dies when $N$ is large enough that you cannot hold one.
Problem 193 asks for the count of [squarefree](/topics/domain/square-free-integer) integers below
$2^{50} \approx 1.13 \times 10^{15}$ — six orders of magnitude past any array you will allocate.

The escape is to write the property as a sum over divisors and then exchange the two summations.
An integer is squarefree exactly when no $d^2$ with $d > 1$ divides it, and the
[Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function) packages the
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over square divisors into an
indicator, $\sum_{d^2 \mid n} \mu(d)$. Summing that over $n \le M$ and swapping the order gives

$$Q(M) = \sum_{d=1}^{\lfloor \sqrt{M} \rfloor} \mu(d) \left\lfloor \frac{M}{d^2} \right\rfloor,$$

because each $d$ contributes $\mu(d)$ once for every multiple of $d^2$, and there are exactly
$\lfloor M/d^2 \rfloor$ of those. The outer variable is now $d \le \sqrt{M}$, about 33.5 million —
a sieve you *can* build. Work drops from $10^{15}$ to $3.4 \times 10^7$, and the only thing that
changed is which index sits on the outside.

That is the general move, and it is worth stating in the abstract because it applies far past
squarefree counting. Whenever a condition reads "gcd is 1", "squarefree", "has exactly $k$ prime
factors", or "is divisible by no …", express it as a sum over divisors of something simpler, then
exchange the sums so the *small* variable is the outer one. The machinery has a name —
[Möbius inversion](/topics/technique/mobius-inversion-formula), the inverse operation to
[Dirichlet convolution](https://en.wikipedia.org/wiki/Dirichlet_convolution) — and problem 153
(sums over [Gaussian integer](https://en.wikipedia.org/wiki/Gaussian_integer) divisors) is the
archive's fullest workout of it.

## Move 3 — there are only $O(\sqrt{N})$ distinct quotients

The identity above leaves a floor function in the sum, and floors have an exploitable property:
as $d$ runs from $1$ to $N$, the value $\lfloor N/d \rfloor$ takes at most $2\sqrt{N}$ distinct
values. For $d \le \sqrt{N}$ the quotient is large and changes at every step; past that, the
quotient is below $\sqrt{N}$ and each value persists over a long run of consecutive $d$.

So a sum $\sum_{d \le N} g(\lfloor N/d \rfloor)$ need not be evaluated $N$ times. Group the $d$
that share a quotient — for a given $d$, the last index with the same quotient is
$\lfloor N / \lfloor N/d \rfloor \rfloor$ — evaluate $g$ once per block, and multiply by the block
width. The loop shrinks from $N$ iterations to $O(\sqrt{N})$:

```python
d = 1
while d <= n:                        # blocks of constant q = n // d
    q = n // d
    hi = n // q                      # last index sharing this quotient
    total += g(q) * (hi - d + 1)     # one evaluation for the whole block
    d = hi + 1
```

This is [quotient blocking](/topics/technique/quotient-blocking); paired with a partial sieve for
the small range it becomes the
[Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method), which computes
summatory functions like $\sum \tau(n)$ or $\sum \varphi(n)$ in sublinear time. Problems 153 and
926 both lean on it. It is the standard finishing move once move 2 has produced a floor-laden sum,
and the pair together is the reason $N = 10^{15}$ is not automatically hopeless.

## Move 4 — reduce the algebra before you write the loop

The three moves above are all mechanical once the sum exists. Getting to the sum is not, and the
most common route is ordinary algebra applied before any code is written — the archive's
[reduce before coding](/topics/takeaway/reduce-before-coding) takeaway is the most frequent one on
this list.

Problem 834 is a clean case. Its sequence is defined by a step rule, and simulating it is hopeless
at the stated scale; but the $m$-th term telescopes to a closed form in $m$ and $n$, and once the
divisibility test is rewritten in terms of $n + m$ it becomes a condition a divisor sieve answers
in bulk. The problem never gets easier — the *representation* does.

Problem 800 shows the same instinct against a different obstacle. It counts integers $p^q q^p$ up
to $800800^{800800}$, a bound with millions of digits, so the comparison itself is the problem.
Take logarithms of both sides and $p^q q^p \le N$ becomes $q \ln p + p \ln q \le \ln N$: ordinary
floating-point arithmetic in machine words. Monotonicity in $q$ then turns the count into a
[binary search](/topics/technique/binary-search-algorithm) per prime.

Problem 243 reduces the *search space* rather than the arithmetic. Since $\varphi(d)/d$ is a
product over the distinct primes dividing $d$, it ignores multiplicity entirely — so the ratio
depends only on which primes appear, and the cheapest way to push it down is to use the smallest
ones. The candidates collapse to multiples of a
[primorial](https://en.wikipedia.org/wiki/Primorial), and an unbounded search becomes a handful of
checks. Three problems, three different things reduced: the formula, the comparison, the candidate
set.

## Exactness is the discipline

Number theory asks questions whose answers are exact integers, and the characteristic bug in this
domain is a correct algorithm ruined by an inexact intermediate.

Comparing ratios is where it bites first. Problem 243 needs $\varphi(d)/(d-1) < 15499/94744$;
computing either side as a float and comparing invites a wrong answer at the boundary, where the
problem's answer lives by construction. Cross-multiply and compare integers instead. The same
applies to $\sqrt{\cdot}$: use `math.isqrt`, not `int(math.sqrt(x))`, which starts losing integers
around $2^{52}$ — problems 179 and 193 both depend on an exact integer square root. Where floats
are genuinely the right tool, as in problem 800's logarithms, treat a near-boundary comparison as
undecided and re-check it exactly. See
[use exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).

The second trap is width, and it is language-shaped. Python's integers are arbitrary-precision, so
a solution that works in Python can overflow silently the moment it is ported to C — problems 241
and 251 both need `__int128` or a reduction that keeps intermediates small, and problems 168 and
321 need [GMP](https://gmplib.org/) outright. The Python version gives no warning that the C
version is about to be wrong. See [watch integer width](/topics/takeaway/watch-integer-width).

## Knowing which move to reach for

The tells are reasonably reliable:

| What you see | What it usually means |
| --- | --- |
| "for every $n$ up to $N$", $N \le 10^8$ | sieve the whole table (move 1) |
| $N \ge 10^{12}$, or "below $2^{50}$" | find a summatory identity; sieve only $\sqrt{N}$ (moves 2–3) |
| "coprime", "gcd is 1", "squarefree", "exactly $k$ prime factors" | Möbius / inclusion–exclusion over divisors (move 2) |
| $\lfloor N/d \rfloor$ anywhere in the derived sum | quotient blocking (move 3) |
| $f$ is multiplicative | build $f$ from prime powers; a sieve exists |
| the number is too large to write down | work in logs, or modulo whatever the question actually asks for |
| a ratio, a root, or an equality test | integers only — cross-multiply, `isqrt`, check the width |

What the moves buy is asymptotic, not constant: $N \to N \log \log N$ in move 1, $N \to \sqrt{N}$
in moves 2 and 3. That is why a rewrite in C rarely rescues a number-theory problem and a change of
representation almost always does. The cost is that each move demands the derivation be right
before a line is written — a sieve indexed off by one, or a Möbius identity with the wrong bound,
produces a plausible number rather than an error. Verify on the small case the statement gives you;
it exists for exactly that reason.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0243](/solutions/0243/) — Resilience
- ● [0251](/solutions/0251/) — Cardano Triplets
- ○ [0254](/solutions/0254/) — Sums of Digit Factorials
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ○ [0271](/solutions/0271/) — Modular Cubes, Part 1
- ○ [0272](/solutions/0272/) — Modular Cubes, Part 2
- ○ [0273](/solutions/0273/) — Sum of Squares
- ○ [0276](/solutions/0276/) — Primitive Triangles
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ○ [0309](/solutions/0309/) — Integer Ladders
- ● [0321](/solutions/0321/) — Swapping Counters
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ● [0346](/solutions/0346/) — Strong Repunits
- ○ [0350](/solutions/0350/) — Constraining the Least Greatest and the Greatest Least
- ○ [0354](/solutions/0354/) — Distances in a Bee's Honeycomb
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ○ [0359](/solutions/0359/) — Hilbert's New Hotel
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0370](/solutions/0370/) — Geometric Triangles
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ○ [0379](/solutions/0379/) — Least Common Multiple Count
- ○ [0388](/solutions/0388/) — Distinct Lines
- ○ [0407](/solutions/0407/) — Idempotents
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0433](/solutions/0433/) — Steps in Euclid's Algorithm
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0443](/solutions/0443/) — GCD Sequence
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ○ [0451](/solutions/0451/) — Modular Inverses
- ○ [0452](/solutions/0452/) — Long Products
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ○ [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0462](/solutions/0462/) — Permutation of 3-smooth Numbers
- ○ [0466](/solutions/0466/) — Distinct Terms in a Multiplication Table
- ○ [0485](/solutions/0485/) — Maximum Number of Divisors
- ○ [0489](/solutions/0489/) — Common Factors Between Two Sequences
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ○ [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0513](/solutions/0513/) — Integral Median
- ○ [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ○ [0556](/solutions/0556/) — Squarefree Gaussian Integers
- ○ [0561](/solutions/0561/) — Divisor Pairs
- ○ [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0580](/solutions/0580/) — Squarefree Hilbert Numbers
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0586](/solutions/0586/) — Binary Quadratic Form
- ○ [0596](/solutions/0596/) — Number of Lattice Points in a Hyperball
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ○ [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0616](/solutions/0616/) — Creative Numbers
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ○ [0625](/solutions/0625/) — Gcd Sum
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ○ [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ○ [0641](/solutions/0641/) — A Long Row of Dice
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ○ [0659](/solutions/0659/) — Largest Prime
- ○ [0672](/solutions/0672/) — One More One
- ○ [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0700](/solutions/0700/) — Eulercoin
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0714](/solutions/0714/) — Duodigits
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0789](/solutions/0789/) — Minimal Pairing Modulo $p$
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0792](/solutions/0792/) — Too Many Twos
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0821](/solutions/0821/) — 123-Separable
- ○ [0822](/solutions/0822/) — Square the Smallest
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0827](/solutions/0827/) — Pythagorean Triple Occurrence
- ○ [0832](/solutions/0832/) — Mex Sequence
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0858](/solutions/0858/) — LCM
- ○ [0864](/solutions/0864/) — Square + 1 = Squarefree
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0884](/solutions/0884/) — Removing Cubes
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0915](/solutions/0915/) — Giant GCDs
- ○ [0920](/solutions/0920/) — Tau Numbers
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0931](/solutions/0931/) — Totient Graph
- ○ [0937](/solutions/0937/) — Equiproduct Partition
- ○ [0954](/solutions/0954/) — Heptaphobia
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0986](/solutions/0986/) — Another Infinite Game
- ○ [0999](/solutions/0999/) — Alternating Recurrence

<!-- /problems -->
