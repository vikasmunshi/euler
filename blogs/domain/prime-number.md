<!-- tags: [prime-number] -->
<!-- status: final 2026-11-03T22:31Z -->
# Prime number

A [prime number](https://en.wikipedia.org/wiki/Prime_number) is an integer greater than $1$ divisible
only by $1$ and itself. What makes this tag cohere is not the definition but the *role* primality
plays in the problems below: in almost none of them is a prime the object of study. Primality is a
**predicate** — a condition bolted onto some other structure (a digit pattern, a quadratic, a run of
consecutive sums, a spiral diagonal, a Fibonacci index) — and the problem is a search over that
structure, filtered by the predicate. Where it is not a filter, it is a **domain**: the problem
asks for some quantity attached to each prime and summed over all of them, and the prime is just the
index of the sum (and often the modulus inside it). Occasionally it is a **structure**, the vertex
set of a graph, or a **hypothesis**, a fact handed to you inside an equation that can be factored. In
every role, the question to ask is which property of primality the problem actually uses. The mathematics of *what primes are* is covered on
[Prime Numbers](/blogs/number-theory/prime-numbers), and the decomposition view — a number read
through its factors — on [prime factorisation](/blogs/domain/prime-factorization). This page is
about the other half: what happens to a program when "and it must be prime" is added to a search, or
"for every prime below $N$" is put in front of a computation.

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
a table with a [sieve](/blogs/technique/sieve-of-eratosthenes) and turn the test into an array
lookup. The rule of thumb is blunt: if the candidates all live below a bound you can name, sieve to
that bound and index; if they are few, unbounded, or enormous, test them one at a time with
[trial division](/blogs/technique/trial-division) or
[Miller–Rabin](/blogs/technique/miller-rabin-primality-test). Problem 37 (truncatable primes) shows
the middle path — an *incremental* sieve as a generator, because the eleven answers are known to
exist but their ceiling is not, so no bound can be chosen in advance.

The second consequence is subtler and matters more: **the predicate has almost no algebra**. You
cannot solve for a prime, invert it, or propagate it through an equation. It does not even survive a
recurrence. Problem 333 sums the primes with exactly one partition of a restricted kind, but the
partition count at $q$ is assembled from counts at indices below $q/2$, and those are not prime. So
the table has to be filled for every integer, and primality is only a mask read at the end.
Everything you can prove about a candidate before testing it, you must prove some *other* way —
which is why the decisive step in these problems is almost never the primality test.

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

Construction raises a question of its own when a family carries several prime conditions at once:
which one goes first? Problem 518 wants prime triples whose successors $a + 1, b + 1, c + 1$ form a
geometric sequence. Writing the ratio in lowest terms as $v/u$ parametrises every triple uniquely as
$(ku^2, kuv, kv^2)$, and each of those, less one, must be prime. The three conditions do not depend
on the same variables. The largest term needs only $(k, v)$, so it is tested once per pair, *outside*
the loop over $u$. At $n = 10^8$ that alone cuts about $5 \times 10^8$ parameter triples to about
$5 \times 10^7$ before $u$ is looked at. This is
[loop-invariant code motion](https://en.wikipedia.org/wiki/Loop-invariant_code_motion) applied to a
filter: test each condition at the outermost level where its variables are bound.

## When the prime is given, factor the equation

The predicate does have one piece of algebra: a prime has no non-trivial factorisation. So when a
problem *states* that some expression equals a prime, primality stops being a test and becomes a
hypothesis, and the way to use it is to factor the expression. However many factors come out, all but
one must be $1$.

Problem 291 looks like a search over two unbounded variables: the primes of the form
$(x^4 - y^4)/(x^3 + y^3)$. Cancelling the common factor and dividing out $\gcd(x, y)$ leaves $p$ as a
product of three positive integers. Two of them are forced to $1$, and what remains is a one-variable
family, the primes of the form $n^2 + (n + 1)^2$. Problem 131 reaches the same place faster: its $p$
is a difference of two cubes, so the factor $b - a$ must be $1$ and only consecutive cubes remain.
Each factor pinned this way removes a whole dimension of the search, which no congruence filter can
do. What is left is primality on a polynomial, and that is the next section's problem.

## When the candidates are too big, or too many

Past a certain scale a sieve over the candidates is not available, and each problem answers that in
one of four ways.

**Sieve something else.** Problem 216 asks how many values of $2n^2 - 1$ are prime for $n$ up to
$5 \times 10^7$ — values reaching $5 \times 10^{15}$, hopeless to test individually. The move is to
invert the question: rather than asking "is $t(n)$ prime?", ask which primes $p$ can divide
$t(n)$ and at which indices. Solving $2n^2 \equiv 1 \pmod p$ is a
[quadratic residue](https://en.wikipedia.org/wiki/Quadratic_residue) condition that yields the
arithmetic progressions of $n$ to cross out, so the sieve runs over the *index space* rather than
the value space. This polynomial sieve is the standard escape whenever a problem imposes primality
on a sequence rather than on an interval.

Problem 659 runs the same sieve for a different question: the *largest* prime factor of $4k^2 + 1$
for every $k \le 10^7$, with values up to $4 \times 10^{14}$. Each prime $p \equiv 1 \pmod 4$ divides
the polynomial along two progressions of $k$, which come from a square root of $-1$ modulo $p$.
[Hensel lifting](https://en.wikipedia.org/wiki/Hensel%27s_lemma) carries those roots up to $p^2, p^3, \dots$,
so repeated factors are divided out along finer progressions. The part worth taking away is how the
sieve stops. Once every prime up to $2N + 1$ has been divided out, whatever is left of $f(k)$ is
either $1$ or a single prime, because two factors above $2N + 1$ would multiply to more than $f(k)$.
That **size bound certifies primality with no test at all**. It is the same fact about factorisations
seen from the other side, and it is what limits the sieve to $\sqrt{\max f}$ rather than $\max f$.

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

**Sieve the counters, not the numbers.** Problem 187's array of $\pi$ values runs out eventually.
Problem 521 sums the smallest prime factor of every integer up to $10^{12}$, where even one bit per
integer is over a hundred gigabytes. The [Lucy_Hedgehog sieve](/blogs/technique/lucy-hedgehog-sieve)
runs the sieve of Eratosthenes on counters instead of cells. It stores how many integers up to $v$
are still standing, for only the $O(\sqrt n)$ values $v = \lfloor n/k \rfloor$, and each prime
$p \le \sqrt n$ updates those counters in one step. Its final state is $\pi$ at every stored point.
What problem 521 adds is that the **history is worth as much as the result**. Step $p$ of a sieve
strikes exactly the composites whose smallest factor is $p$, so the size of that step, read off the
counters as the sieve runs, says how many integers contribute $p$ to the sum. A second table with the
same update, carrying sums instead of counts, supplies the primes' own contribution. About $10^9$
updates replace $10^{12}$ cells. Only the primes below $10^6$ are ever identified, and the other
$3.8 \times 10^{10}$ are never seen individually. When a quantity is defined by what a sieve does,
look for it in the sieve's intermediate states before computing it afterwards.

## When the primes are the domain, not the filter

A second family has no search to prune at all. The primes are given, all of them below a bound, and
the work is a per-prime quantity summed over the lot. Problem 274 (divisibility multipliers) asks,
for each prime $p$ coprime to $10$, for the multiplier $m$ that makes "drop the last digit, add $m$
times it" a test for divisibility by $p$. Problem 315 (digital root clocks) feeds every prime in a
range to two seven-segment clocks and asks how many segment transitions one saves over the other
while each clock steps down the prime's digit-sum chain. Here the sieve is not a lookup table the
search consults. It is the loop itself, and it runs exactly once per prime.

That changes where the effort goes. The congruence reflex of the previous sections has almost
nothing to throw away, because every prime counts. What is left is the per-prime body, and the aim is
to make it so cheap that the sieve is the whole cost. These problems get there by finding that the
per-prime quantity depends on far less than the prime:

- In 274 the multiplier turns out to be the
  [inverse of $10$ modulo $p$](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse). Here
  the prime plays its other usual part, as a modulus. The obvious body is a
  [`pow(10, -1, p)`](/blogs/technique/extended-euclidean-algorithm) per prime. Since the modulus
  is $10$, though, the inverse has a closed form $m = (kp + 1)/10$, where $k$ is picked by the last
  digit of $p$ alone. That is four cases, a ten-entry table, and an expression that vectorises over
  the whole prime array.
- In 315 the saving for one prime depends only on its last two digits and its digit sum. The digit
  sum of a number below $10^{10}$ has at most two digits, so on a right-aligned display it only
  overlaps the prime's units and tens, and every later step depends on the digit sum alone. So
  $\Delta(p)$ is a function of $(p \bmod 100,\ s(p))$, a few thousand table entries computed once.
  The per-prime work drops to one digit sum and two lookups.
- Problem 492 asks, for every prime in a window near $10^9$, for the $10^{15}$-th term of an exploding
  quadratic recurrence modulo $p$. Completing the square turns the recurrence into the doubling rule
  of a [Lucas sequence](https://en.wikipedia.org/wiki/Lucas_sequence), so the term is
  $\alpha^{2^{n-1}} + \alpha^{-2^{n-1}}$ for a root $\alpha$ of a fixed quadratic. Here the prime
  gives something more than a modulus: a **finite group whose order it fixes**. If the discriminant
  is a square mod $p$, then $\alpha \in \mathbb{F}_p^*$ and its order divides $p - 1$. Otherwise
  $\alpha$ lives in $\mathbb{F}_{p^2}$, where the Frobenius map sends it to $\alpha^{-1}$, and its
  order divides $p + 1$. [Quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity)
  turns "is the discriminant a square mod $p$" into "is $p \bmod 13$ a square mod $13$". So the
  small key is $p \bmod 13$. It chooses $p \mp 1$, the astronomical exponent shrinks modulo that
  value, and one Lucas ladder per prime finishes the job.

The same "every prime counts" shape also allows a second saving: **share the work across primes**
instead of redoing it per prime. Problems 517 and 635 both reduce to binomial coefficients at
arguments set by $p$, for hundreds or millions of primes. Both build one factorial table, or one
running factorial scan, out to the largest argument and read every prime's terms from it. Problem 635
also inverts all its denominators in one vectorised Fermat exponentiation instead of one inversion
per prime.

When nothing can be shared, the per-prime bodies are at least independent, and that makes the prime
an **array axis**. Problem 291 takes a modular power for two million primes at once, in one vectorised
square-and-multiply. Problem 437 gives each candidate prime a lane in a set of NumPy arrays, and it
compacts a lane away as soon as its prime is ruled out, so later passes touch only primes that can
still qualify. The interpreter then loops over bit positions and trial divisors, not over primes.

The lesson is the counterpart of "the win is upstream of the test": when nothing can be pruned,
**find the small key the per-prime answer depends on**, and tabulate over the key instead of
computing over the prime. After that the remaining cost is just generating the primes. The benchmarks
of 274 and 315 are almost all sieve, which means it is the sieve that is worth optimising: an
odd-only array that halves the memory traffic, or a segmented library sieve such as
[primesieve](https://github.com/kimwalisch/primesieve).

## When every prime gets an equation to solve

A narrower family poses the same polynomial congruence at every prime. Problem 457 wants the least
$n$ with $p^2 \mid n^2 - 3n - 1$ for each prime up to $10^7$. Problem 437 wants the primes at which a
root of $x^2 - x - 1$ is a [primitive root](/blogs/domain/primitive-root). The number theory is on
[Prime Numbers](/blogs/number-theory/prime-numbers) and
[quadratic residue](/blogs/technique/quadratic-residue). What carries over as engineering is four
questions to ask, whatever the polynomial:

- **Which primes take part?** Here the congruence reflex comes back, one level up. A quadratic has
  roots modulo $p$ only when its discriminant is a quadratic residue, and
  [reciprocity](/blogs/domain/quadratic-reciprocity) turns that into a residue class of $p$: six
  values of $p \bmod 13$ in 457, and $p \equiv \pm 1 \pmod{10}$ in 437. The same test restricts the
  sieving primes of 291 and 659 to $q \equiv 1 \pmod 4$. About half the primes go, for the price of a
  table lookup.
- **Which primes are exceptions?** The argument that serves every other prime breaks at $2$, and at
  primes dividing the discriminant, where any root is a double root. Those primes are a short list,
  so decide each by hand. They can go either way. At $p = 13$, problem 457 has a root modulo $13$ that
  does not lift, so there is no solution modulo $169$. At $p = 5$, problem 437's double root $3$ is a
  primitive root, so $5$ qualifies. The residue filter rejects both. It is right about $13$ by luck,
  and wrong about $5$, which the solution has to add back.
- **Is the modulus really prime?** $\mathbb{Z}/p^2$ is not a field, and $p^2$ reaches $10^{14}$, far
  too far to scan. So solve in $\mathbb{F}_p$, where the whole toolkit applies, and carry a simple root
  up with one [Hensel](/blogs/technique/hensels-lemma) step. The step divides by the derivative, which
  is exactly what vanishes at the exceptional primes.
- **Does the answer need the root at all?** Three problems give three prices. Problem 291 needs a
  square root of $-1$, which has a closed form: any non-residue raised to the power $(q - 1)/4$. In
  problem 457 the answer *is* the root, so
  [Tonelli–Shanks](/blogs/technique/tonelli-shanks-algorithm) has to be paid. Problem 437 asks only
  about a *property* of the root, so it never takes one. It raises a formal root $x$ in the
  [quotient ring](/blogs/technique/quotient-ring-arithmetic) $\mathbb{Z}_p[x]/(x^2 - x - 1)$, where
  every power reduces to $ax + b$. "This power of $r$ is $1$" then becomes the linear condition
  $ar + b = 1$, which names the one candidate that fails. Kept as an unreduced fraction, that
  candidate costs no inverse either, and about $2.9$ million modular square roots disappear.

Problem 437 is also the exception to "the sieve is what you are left paying for". The primitivity test
needs the prime factors of $p - 1$, so the real per-prime cost is factoring the prime's *neighbour*.
Problem 492 only reduced an exponent modulo the group order. Here the structure of that order is
the question, and the trial division that exposes it dominates the Python run.

## Ask which property of primality is actually used

"For every prime $p$" in a statement does not mean the proof needs primality. Before building on it,
find the one property the argument uses. There are three possible answers:

- **Essential.** Problem 635 counts the $p$-element subsets of $\{1, \dots, qp\}$ whose sum is
  divisible by $p$. A [roots-of-unity filter](https://en.wikipedia.org/wiki/Root_of_unity#Summation)
  writes the count as an average over all $p$-th roots of unity. Because $p$ is prime, every
  non-trivial root is *primitive*, so all $p - 1$ non-trivial terms are equal and the sum collapses to
  $\left(\binom{qp}{p} + q(p-1)\right)/p$. For composite $n$ the roots split by order and the closed
  form is lost. Here primality carries the whole argument.
- **Incidental.** Problem 517 sums a real-step recurrence $G(p) = g_{\sqrt p}(p)$ over primes in a
  window. The recurrence unrolls into a sum of binomials, and the only fact about $p$ the computation
  needs is that it is not a perfect square: then $j\sqrt p$ is irrational, and
  $\lfloor p - j\sqrt p \rfloor$ is exact through an integer square root. Every non-square $n$ would
  do. The solution accepts a non-prime mode, which is how the statement's $G(90)$ becomes a test case.
- **Decorative.** Problem 946 expands a Möbius transform of a continued fraction whose runs of $1$s
  have prime lengths. [Gosper's algorithm](https://en.wikipedia.org/wiki/Continued_fraction#Generalized_continued_fraction)
  turns out to visit only $32$ states. A run of $p$ ones is therefore a walk that enters a cycle
  within $32$ steps, and the run is consumed through $p$ modulo the cycle length, with the whole cycles
  skipped by multiplication. The primes are just a list of run lengths. Any other sequence would cost
  the same, and the sieve feeding it is the least of the work. Problem 705 goes further: its primes
  are only a source of digits.
  [Linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Properties) reduces the
  inversion total over all divided sequences to ordered digit-pair counts, so the whole concatenation
  matters only through an $81$-entry table. The primes need not even exist together. The C port
  streams them from a primesieve iterator into running counters and keeps no array at all.

The payoff is practical. An essential use is where the closed form comes from, so look for it
deliberately: primitive roots, $\mathbb{F}_p$ being a field, Fermat and Frobenius. An incidental or
decorative use frees the solution from primality entirely. It can be tested on small composite inputs
and checked against the statement's examples even when those are not prime.

## When the primes are the vertices

One problem here uses the primes as neither filter nor domain but as **structure**. Problem 425
links two primes when they differ in one digit or when one is the other with a digit prepended. A
prime $P$ qualifies if a chain from $2$ reaches it using no prime above $P$. That is a
[bottleneck path](https://en.wikipedia.org/wiki/Widest_path_problem) condition whose cap is the vertex
being tested. So the order of the primes *is* the algorithm. Insert the primes in increasing order,
union each one with its already-present smaller neighbours in a
[disjoint-set](https://en.wikipedia.org/wiki/Disjoint-set_data_structure) structure, and $P$ qualifies
exactly when it shares a root with $2$ at the moment it arrives. This is Kruskal's algorithm with each
edge weighted by its larger endpoint. Each edge is generated once, from its larger end, and the sieve
supplies both the vertex set and a value-to-index map. Whenever a condition on a prime is "using only
primes up to this one", sweep the primes in order and keep the answer incrementally, instead of
re-searching for each prime.

## How to reason about it

When primality appears as a condition in a problem, work through it in this order:

1. **Find the congruences first.** What must be true modulo $2$, $3$, $5$, $10$ for a candidate to
   have any chance? This is where the orders of magnitude are won, and it costs nothing but algebra —
   [reduce before coding](/blogs/takeaway/reduce-before-coding). If the prime is *given* in an
   equation, factor the equation: all factors but one must be $1$.
2. **Ask whether to filter or to construct.** If the survivors are a thin, describable set, build
   them directly rather than sieving a haystack and rejecting it. If several prime conditions apply,
   test each at the outermost loop whose variables it needs.
3. **Count the queries, then pick the test.** Many tests below a known bound → sieve once into a
   lookup table, sized to the input and built inside `solve()` so the benchmark counts it honestly
   ([size the work to the input](/blogs/takeaway/size-work-to-the-input)). Bound not known in
   advance → an incremental sieve. A handful of large candidates → Miller–Rabin.
4. **If the values are too large to sieve, sieve their indices.** Primality on a polynomial or a
   sequence is a sieve over $n$, driven by the congruence conditions that let $p \mid f(n)$.
5. **If the answer is a count, look for a formula over the primes** instead of a scan over the
   integers — $\pi(x)$ differences, a digit-sum reformulation, a telescoping sum. Past the reach of
   an array, run the sieve on counters at the quotients $\lfloor n/k \rfloor$ and read what each step
   strikes.
6. **If every prime counts, shrink the per-prime body.** Look for the few residues or digits the
   quantity actually depends on, and replace the work with a closed form or a table over that key.
   The sieve should be what you are left paying for. If the prime is a modulus, its group order
   ($p - 1$, or $p + 1$ in $\mathbb{F}_{p^2}$) reduces any huge exponent. Work that depends only on
   magnitude, such as a factorial table, is built once and shared by every prime.
7. **If every prime gets an equation, settle its edges first.** Filter the primes by reciprocity,
   decide $2$ and the discriminant's primes by hand, solve in $\mathbb{F}_p$ and lift, and compute
   the root only if the answer is the root.
8. **Name the property of primality the argument uses.** If it is essential, that property is where
   the closed form comes from. If it is incidental, drop it and test on composites too.
9. **If the condition caps a chain at the prime itself, sweep the primes in increasing order** and
   keep the answer incrementally, as union–find does for problem 425.

The recurring mistake is to reach for a faster primality test when the real problem is that too many
candidates are being tested at all. Almost every filtered search below that is fast is fast because
of step one, not step three. The domain problems follow the same rule from the other side: they are
fast because the work done per prime has been cut down to almost nothing, not because anything
clever was done with the primes themselves.

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
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0308](/solutions/0308/) — An Amazing Prime-generating Automaton
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0329](/solutions/0329/) — Prime Frog
- ● [0333](/solutions/0333/) — Special Partitions
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0425](/solutions/0425/) — Prime Connection
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0467](/solutions/0467/) — Superinteger
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0521](/solutions/0521/) — Smallest Prime Factor
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
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0659](/solutions/0659/) — Largest Prime
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
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
- ● [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ● [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0975](/solutions/0975/) — A Winding Path
- ● [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ○ [1005](/solutions/1005/) — Median Prime List

<!-- /problems -->
