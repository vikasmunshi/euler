<!-- tags: [prime-number] -->
<!-- status: final -->
# Prime number

A [prime number](https://en.wikipedia.org/wiki/Prime_number) is an integer greater than $1$ divisible
only by $1$ and itself. What makes this tag cohere is not the definition but the *role* primality
plays in the problems below: in almost none of them is a prime the object of study. Primality is a
**predicate** — a condition bolted onto some other structure (a digit pattern, a quadratic, a run of
consecutive sums, a spiral diagonal, a Fibonacci index) — and the problem is a search over that
structure, filtered by the predicate. The mathematics of *what primes are* is covered on
[Prime Numbers](/topics/number-theory/prime-numbers), and the decomposition view — a number read
through its factors — on [prime factorisation](/topics/domain/prime-factorization). This page is
about the other half: what happens to a program when "and it must be prime" is added to a search.

## Why the predicate is the hard part

There is no formula for the primes. You cannot enumerate them the way you enumerate squares or
triangular numbers; you can only produce candidates and ask each one a question, and by the
[prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem) roughly one candidate in
$\ln N$ survives. Two consequences follow, and between them they set the shape of every solution
under this tag.

The first is that **the predicate is queried far more often than the answer is used**. Problem 35
(circular primes) tests every cyclic rotation of every candidate; problem 60 (prime pair sets) tests
both concatenations of every pair of primes it considers; problem 27 (quadratic primes) walks a run
of values per coefficient pair, each needing its own test. So the question is never "how do I test
one number" but "how do I amortise a million tests", and the answer is almost always to precompute
a table with a [sieve](/topics/technique/sieve-of-eratosthenes) and turn the test into an array
lookup. The rule of thumb is blunt: if the candidates all live below a bound you can name, sieve to
that bound and index; if they are few, unbounded, or enormous, test them one at a time with
[trial division](/topics/technique/trial-division) or
[Miller–Rabin](/topics/technique/miller-rabin-primality-test). Problem 37 (truncatable primes) shows
the middle path — an *incremental* sieve as a generator, because the eleven answers are known to
exist but their ceiling is not, so no bound can be chosen in advance.

The second consequence is subtler and matters more: **the predicate has no algebra**. You cannot
solve for a prime, invert it, or propagate it through an equation. Everything you can prove about a
candidate before testing it, you must prove some *other* way — which is why the decisive step in
these problems is almost never the primality test.

## The win is upstream of the test

Look at what actually collapses the search in the problems below, and it is a divisibility argument
that throws candidates away before any test runs:

| Problem | The pruning observation | Effect |
| --- | --- | --- |
| 41 (pandigital prime) | an $n$-digit pandigital has digit sum $n(n+1)/2$, divisible by $3$ for all $n$ but $4$ and $7$ | nine lengths → two |
| 35 (circular primes) | any rotation ending in $0,2,4,5,6,8$ is composite, so the digits must come from $\{1,3,7,9\}$ | almost the entire range |
| 27 (quadratic primes) | $n^2 + an + b$ at $n = 0$ is $b$, so $b$ itself must be prime | $2001$ values of $b$ → $168$ magnitudes |
| 51 (prime digit replacements) | replacing digit $d$ admits only $10 - d$ family members, so an $8$-family needs $d \le 2$ | ten digit values → three |
| 146 (investigating a prime pattern) | $n$ must be $\equiv 0 \pmod{10}$, and further residues knock out most of what is left | a $1.5 \times 10^8$ scan made feasible |

The shape is always the same. Primality is expensive and opaque, but *compositeness is cheap and
witnessed* — a single small modulus that divides a whole family of candidates disqualifies all of
them at once, with no test performed. So the reflex is: before writing the search, ask which
congruence classes can contain an answer at all. Problem 41's argument is the purest example,
because it is the whole solution; the search that remains is $5040$ permutations checked by trial
division, and would have been fast even done badly.

The same reflex has a constructive form: instead of filtering a stream of candidates, *generate only
the ones that can qualify*. Problem 111 (primes with runs) does this — rather than sieving the
$9$ billion ten-digit numbers and bucketing them by repeated digit, it fixes the target shape,
chooses which few positions deviate, and enumerates just those numbers. Problem 35's filter and
problem 111's construction are the same idea seen from either end, and the constructive one wins
whenever the surviving fraction is small enough to make enumeration of the survivors cheaper than
rejection of the rest.

## When the candidates are too big, or too many

Past a certain scale a sieve over the candidates is not available, and each problem answers that in
one of three ways.

**Sieve something else.** Problem 216 asks how many values of $2n^2 - 1$ are prime for $n$ up to
$5 \times 10^7$ — values reaching $5 \times 10^{15}$, hopeless to test individually. The move is to
invert the question: rather than asking "is $t(n)$ prime?", ask which primes $p$ can divide
$t(n)$ and at which indices. Solving $2n^2 \equiv 1 \pmod p$ is a
[quadratic residue](https://en.wikipedia.org/wiki/Quadratic_residue) condition that yields the
arithmetic progressions of $n$ to cross out, so the sieve runs over the *index space* rather than
the value space. This polynomial sieve is the standard escape whenever a problem imposes primality
on a sequence rather than on an interval.

**Sieve a window.** The primes near $10^{14}$ are spaced about $\ln(10^{14}) \approx 32$ apart, so
the $100{,}000$ consecutive primes problem 304 needs occupy a window of only a few million integers.
A [segmented sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve) over that
window — crossing out multiples of the primes below $10^7$ — beats per-candidate testing by a wide
margin, and the prime number theorem is what tells you in advance how wide to make the window.

**Do not enumerate at all.** When the question is a *count* rather than a *list*, the primes can
often be consulted wholesale. Problem 187 counts semiprimes below $10^8$ not by factoring anything
but by fixing the smaller factor $p$ and adding $\pi\!\left(\lfloor (N-1)/p \rfloor\right) - \pi(p-1)$
— differences of the
[prime-counting function](https://en.wikipedia.org/wiki/Prime-counting_function) over an array the
sieve already produced. Problem 845 goes further and never tests a number for primality at all: an
integer qualifies according to its *digit sum*, so the search over $10^{16}$ integers becomes a count
over the $\sim 150$ possible digit sums, of which the prime ones are found once by a trivial sieve.
Problem 934 reorders a sum over $10^{17}$ integers into a sum over the primes consulted. In each
case the primes shrink from the thing being searched to a small lookup table on the side.

## How to reason about it

When primality appears as a condition in a problem, work through it in this order:

1. **Find the congruences first.** What must be true modulo $2$, $3$, $5$, $10$ for a candidate to
   have any chance? This is where the orders of magnitude are won, and it costs nothing but algebra —
   [reduce before coding](/topics/takeaway/reduce-before-coding).
2. **Ask whether to filter or to construct.** If the survivors are a thin, describable set, build
   them directly rather than sieving a haystack and rejecting it.
3. **Count the queries, then pick the test.** Many tests below a known bound → sieve once into a
   lookup table, sized to the input and built inside `solve()` so the benchmark counts it honestly
   ([size the work to the input](/topics/takeaway/size-work-to-the-input)). Bound not known in
   advance → an incremental sieve. A handful of large candidates → Miller–Rabin.
4. **If the values are too large to sieve, sieve their indices.** Primality on a polynomial or a
   sequence is a sieve over $n$, driven by the congruence conditions that let $p \mid f(n)$.
5. **If the answer is a count, look for a formula over the primes** instead of a scan over the
   integers — $\pi(x)$ differences, a digit-sum reformulation, a telescoping sum.

The recurring mistake is to reach for a faster primality test when the real problem is that too many
candidates are being tested at all. Almost every solution below that is fast is fast because of step
one, not step three.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ○ [0263](/solutions/0263/) — An Engineers' Dream Come True
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ○ [0273](/solutions/0273/) — Sum of Squares
- ○ [0274](/solutions/0274/) — Divisibility Multipliers
- ○ [0291](/solutions/0291/) — Panaitopol Primes
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0308](/solutions/0308/) — An Amazing Prime-generating Automaton
- ● [0313](/solutions/0313/) — Sliding Game
- ○ [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0333](/solutions/0333/) — Special Partitions
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0425](/solutions/0425/) — Prime Connection
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0467](/solutions/0467/) — Superinteger
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ○ [0492](/solutions/0492/) — Exploding Sequence
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
- ○ [0659](/solutions/0659/) — Largest Prime
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0810](/solutions/0810/) — XOR-Primes
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0826](/solutions/0826/) — Birds on a Wire
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ○ [0869](/solutions/0869/) — Prime Guessing
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ● [0934](/solutions/0934/) — Unlucky Primes
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ○ [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ○ [0975](/solutions/0975/) — A Winding Path
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ○ [1005](/solutions/1005/) — Median Prime List

<!-- /problems -->
