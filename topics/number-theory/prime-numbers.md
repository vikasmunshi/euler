<!-- tags: [coprime-integers, cuban-prime, prime-counting-function, prime-factor, prime-factorization, prime-number, prime-number-theorem, prime-power, prime-proof-number, semiprime, truncatable-prime, generation-of-primes, prime-factorization-application, primesieve, sieve-of-sundaram, sieve-of-eratosthenes, linear-sieve, sieve-theory, divisor-sum-sieve, min-25-sieve] -->
<!-- status: final -->
# Prime Numbers

A [prime number](https://en.wikipedia.org/wiki/Prime_number) is an integer greater than $1$ whose
only positive divisors are $1$ and itself. That one-line definition hides the deepest object in
number theory: the primes are the *multiplicative atoms* from which every other integer is built,
their individual behaviour is erratic while their collective behaviour is astonishingly regular, and
the gap between how easily you can *multiply* them and how hard it is to *un-multiply* a number back
into them is the foundation the modern digital economy is quietly standing on. This page covers the
primes end to end — the mathematics of what is true of them and how that truth was won, the
[algorithms](#generating-and-testing-primes) that generate, test, and factor them in code, and where
both are put to work.

## A short history

The primes are one of the oldest studied objects in mathematics, and a handful of results mark the
road from antiquity to the present:

- **Euclid, c. 300 BC.** *Elements* Book IX contains the first two theorems that still anchor the
  subject: that every integer factors into primes, and — Proposition 20 — that
  [there are infinitely many primes](https://en.wikipedia.org/wiki/Euclid%27s_theorem). His proof is
  the model of elegance: if $p_1, \dots, p_k$ were all of them, then $p_1 p_2 \cdots p_k + 1$ is
  divisible by none of them, so either it is a new prime or has a prime factor outside the list —
  a contradiction. A generation later [Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)
  gave the sieve that still bears his name.
- **Fermat and Euler, 17th–18th c.** [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem)
  ($a^{p-1} \equiv 1 \pmod p$ for a prime $p \nmid a$) exposed the arithmetic *structure* of a prime
  modulus. Euler proved it, generalised it through his
  [totient function](https://en.wikipedia.org/wiki/Euler%27s_totient_function) $\varphi(n)$, and
  recast Euclid's infinitude as an analytic fact — the sum $\sum 1/p$ over primes *diverges* — the
  first hint that the primes could be studied with the tools of continuous mathematics.
- **Gauss, Legendre, Riemann, 19th c.** As teenagers, Gauss and Legendre independently conjectured
  the [prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem): the primes thin out
  like $1/\ln x$. Gauss's *Disquisitiones Arithmeticae* (1801) also gave the first rigorous proof of
  unique factorisation. In 1859 [Riemann](https://en.wikipedia.org/wiki/Riemann_hypothesis) tied the
  fine distribution of the primes to the complex zeros of the zeta function — the
  [Riemann hypothesis](https://en.wikipedia.org/wiki/Riemann_hypothesis), still unproven, is a
  statement about how evenly the primes are spread.
- **1896 and after.** Hadamard and de la Vallée Poussin independently *proved* the prime number
  theorem. The 20th century then made the primes *computational*: fast primality tests, the 1977
  arrival of [RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem), and in 2002 the
  [AKS test](https://en.wikipedia.org/wiki/AKS_primality_test) — the first deterministic,
  polynomial-time proof of primality. Much remains open:
  [Goldbach's conjecture](https://en.wikipedia.org/wiki/Goldbach%27s_conjecture), the
  [twin prime conjecture](https://en.wikipedia.org/wiki/Twin_prime), and the Riemann hypothesis are
  all still unresolved.

## The one structural fact: unique factorisation

Everything else rests on the [fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic):
every integer $n > 1$ is a product of primes in exactly one way, up to order —

$$n = p_1^{a_1} p_2^{a_2} \cdots p_k^{a_k}.$$

This is why a prime problem is so often *really* a factorisation problem. The exponent vector
$(a_1, \dots, a_k)$ is the true "shape" of a number, and almost every multiplicative quantity is a
simple function of it: the number of divisors is $\prod (a_i + 1)$, their sum is a product of
geometric series, Euler's totient is $n \prod (1 - 1/p_i)$, and two numbers are
[coprime](https://en.wikipedia.org/wiki/Coprime_integers) exactly when their factorisations share no
prime. Whole families of Euler problems are built on reading a number through this lens — counting
divisors (problem 12), summing totients, working with [semiprimes](https://en.wikipedia.org/wiki/Semiprime)
$n = pq$ (problem 187), [prime powers](https://en.wikipedia.org/wiki/Prime_power) $p^k$ (problem 87),
or the largest prime factor of a number (problem 3, public in `solutions/public/p0003/`). The
uniqueness is what lets you compute a global answer prime-by-prime and multiply the pieces together —
the same decompose-and-recombine move that the [Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
performs on the modulus side.

Unique factorisation also explains the exotic *shapes* the problems name. A
[truncatable prime](https://en.wikipedia.org/wiki/Truncatable_prime) (problem 37) stays prime as you
strip digits; a [cuban prime](https://en.wikipedia.org/wiki/Cuban_prime) (problem 131) is a prime
difference of consecutive cubes; a [prime-proof number](https://projecteuler.net/problem=200)
(problem 200) can never be *made* prime by changing one digit. Each is a constraint layered on top of
primality, and each is tractable precisely because primality is the atom underneath.

## How the primes are distributed

Individually the primes look random — the gaps between them are unpredictable, and no simple formula
generates them — yet *in aggregate* they obey the prime number theorem with great precision. Writing
$\pi(x)$ for the [prime-counting function](https://en.wikipedia.org/wiki/Prime-counting_function), the
number of primes $\le x$,

$$\pi(x) \sim \frac{x}{\ln x}, \qquad \text{equivalently the } n\text{-th prime } p_n \sim n \ln n.$$

This asymptotic is not a curiosity — it is a practical sizing tool. When a problem asks for "the
$n$-th prime" you must allocate a sieve *before* you know where that prime lands, and $n \ln n$ (with
a small safety margin) is the estimate that tells you how far to reach; problem 7 in
`solutions/public/p0007/` sizes its sieve exactly this way. The same law tells you roughly how many
primes, semiprimes, or smooth numbers live below a bound — the density argument behind problems like
187 (counting semiprimes) and 304 (walking the primes just past $10^{16}$, whose spacing near
$n \ln n$ makes a sieve hopeless and a per-candidate test essential). A sharper count replaces
$x/\ln x$ with the [logarithmic integral](https://en.wikipedia.org/wiki/Logarithmic_integral_function)
$\mathrm{Li}(x) = \int_2^x \mathrm{d}t/\ln t$, which tracks $\pi(x)$ far more closely — and the
question of *how closely* is where the shallow-looking business of counting primes plunges into the
deepest water in mathematics.

### From counting to the zeta function

The bridge from the discrete, unruly primes to the smooth machinery of analysis is a single identity
Euler wrote down in 1737. For a real (later complex) variable $s > 1$, the
[Riemann zeta function](https://en.wikipedia.org/wiki/Riemann_zeta_function) is the sum over *all*
integers

$$\zeta(s) = \sum_{n=1}^{\infty} \frac{1}{n^s} = \prod_{p \text{ prime}} \frac{1}{1 - p^{-s}}.$$

The right-hand side — the [Euler product](https://en.wikipedia.org/wiki/Euler_product) — is unique
factorisation restated in analytic form: expand each factor as a geometric series
$1 + p^{-s} + p^{-2s} + \cdots$, multiply them out, and every term $n^{-s}$ appears *exactly once*,
because every $n$ has exactly one prime factorisation. That one equals sign carries all the arithmetic
of the primes into a single analytic object. Set $s = 1$ and the left side is the divergent harmonic
series, so the product over primes must diverge too — which forces infinitely many primes, and even
that $\sum 1/p$ diverges: Euler's analytic reproof of Euclid, and the first time the primes were
studied as the raw material of a continuous function rather than one at a time.

### The Riemann hypothesis

Riemann's 1859 memoir took the decisive step: he extended $\zeta(s)$ from the half-plane
$\Re(s) > 1$, where the sum converges, to a single [analytic function](https://en.wikipedia.org/wiki/Analytic_continuation)
on the whole complex plane (bar a simple pole at $s = 1$), and discovered that the distribution of
the primes is encoded in the *zeros* of that continuation. The zeta function vanishes at the negative
even integers $-2, -4, -6, \dots$ — the "trivial" zeros — and at infinitely many complex points, all
lying in the **critical strip** $0 < \Re(s) < 1$. The
[Riemann hypothesis](https://en.wikipedia.org/wiki/Riemann_hypothesis) is the assertion, still
unproven after more than a century and one of the [Millennium Prize Problems](https://en.wikipedia.org/wiki/Millennium_Prize_Problems),
that every one of these non-trivial zeros lies exactly on the **critical line** $\Re(s) = \tfrac12$.

Why should an engineer counting primes care where a complex function happens to vanish? Because of
Riemann's [explicit formula](https://en.wikipedia.org/wiki/Explicit_formulae_for_L-functions), which
writes $\pi(x)$ — the jagged prime staircase — as the smooth term $\mathrm{Li}(x)$ *minus a sum of
correction waves, one per zero $\rho$ of the zeta function*:

$$\pi(x) \approx \mathrm{Li}(x) - \sum_{\rho} \mathrm{Li}(x^{\rho}).$$

Each zero $\rho = \beta + i\gamma$ contributes an oscillation whose *amplitude* is governed by its
real part $\beta$ and whose *frequency* is its imaginary part $\gamma$ — the zeros are literally the
harmonics of the primes, which is why the subject is often called the
"[music of the primes](https://en.wikipedia.org/wiki/Music_of_the_Primes)". The Riemann hypothesis
says every one of these waves has the *same* real part $\tfrac12$, so none of them grows faster than
$\sqrt{x}$, and the error in the prime number theorem is as small as it could possibly be:

$$\bigl|\pi(x) - \mathrm{Li}(x)\bigr| = O\!\left(\sqrt{x}\,\ln x\right).$$

A single off-line zero would let one correction wave swell out of proportion and the primes would
cluster more erratically than anyone has ever observed. So the hypothesis is not idle: it is the
precise statement that the primes are distributed *as regularly as possible*, and a vast body of
number theory — sharp bounds on prime gaps, the reliability of fast primality tests, the running time
of factorisation algorithms — is proved conditionally on it, waiting for a proof. It also warns
against trusting small data: $\mathrm{Li}(x)$ overshoots $\pi(x)$ for every $x$ anyone has ever
computed, yet [Littlewood proved](https://en.wikipedia.org/wiki/Skewes%27s_number) the difference
changes sign infinitely often, the first crossing hiding somewhere near the almost unimaginable
Skewes bound — a standing reminder that an asymptotic law is not a promise about the numbers you can
reach.

### Order inside the randomness

The tension between local chaos and global law runs right through the open problems. The gaps between
consecutive primes average $\ln p$ by the prime number theorem, yet
[Bertrand's postulate](https://en.wikipedia.org/wiki/Bertrand%27s_postulate) guarantees one always
falls before $2p$, prime "deserts" of arbitrary length exist (the run $n! + 2, \dots, n! + n$ is all
composite), and the [twin prime conjecture](https://en.wikipedia.org/wiki/Twin_prime) — that $p$ and
$p + 2$ are both prime infinitely often — remains open even though Zhang's 2013 breakthrough proved
*some* bounded gap recurs forever. [Goldbach's conjecture](https://en.wikipedia.org/wiki/Goldbach%27s_conjecture)
(every even number $> 2$ is a sum of two primes) is another century-old statement about additive
structure that the multiplicative theory has never cracked. Project Euler mines exactly this seam:
problem 46 tests Goldbach's *other* conjecture, problem 196 hunts twin- and triplet-prime
neighbourhoods, and problem 50 chases the longest run of consecutive primes that sums to a prime —
each a small window onto the same theme, that the primes are random enough to be endlessly surprising
and structured enough that the surprises obey laws.

## Generating and testing primes

Knowing what the primes *are* is one thing; getting the ones you need into a program is another, and
a prime-heavy problem almost always reduces to one of three questions — *give me every prime up to a
bound*, *is this one number prime*, or *what are the prime factors of this number*. Each has its own
right tool, and reaching for the wrong one is the usual reason a prime solution is slow.

**Enumerate every prime up to $N$ — the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes).**
Write down every integer from $2$ to $N$; walk the list, and each time you meet a number still
standing, cross out all of its multiples. What survives is exactly the primes. Two observations make
it fast: start crossing out from $p^2$ (every smaller multiple of $p$ already carries a smaller
factor), and stop once $p^2 > N$. The whole pass runs in $O(N \log \log N)$ — very nearly linear — so
whenever a problem needs *all* the primes below a known ceiling, the sieve is almost always the
answer. In `solutions/public/p0010/` the core is three lines of `bytearray` strided assignment:

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

The subtlety the sieve carries is the *bound*. You often want "the first $n$ primes" rather than
"primes below $N$", and must size the array before you know where the $n$-th prime lands — which is
exactly where the prime number theorem above earns its keep: $p_n \sim n \ln n$, so sieving up to
$n \ln n$ (with a small margin) suffices, the ceiling problem 7 uses to reach the 10 001st prime.
When even that range will not fit in memory, a [*segmented* sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve)
processes the interval in cache-sized windows, and an *incremental* sieve — a generator keyed on each
prime's next multiple — yields primes endlessly with no ceiling fixed in advance. Variants trade the
same idea around: the [Sieve of Sundaram](https://en.wikipedia.org/wiki/Sieve_of_Sundaram) sieves odd
numbers through a different indexing, and a [linear sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Euler's_sieve)
crosses each composite off exactly once (via its smallest prime factor), handing you a factorisation
table as a by-product — useful when a problem needs the least prime factor of every $n \le N$, not
just a primality flag.

**Factor or test a single number — [trial division](https://en.wikipedia.org/wiki/Trial_division).**
When you have one number, not a range, sieving the whole space below it is wasteful. To factor $n$,
divide by $2, 3, 4, \dots$ and peel off each divisor you find; to test primality, divide by
candidates up to $\sqrt{n}$ and call it prime if none divide it. The $\sqrt{n}$ cutoff is the crux: a
composite $n$ must have a factor no larger than its square root, so nothing above $\sqrt{n}$ can be
its *smallest* factor. A second saving is to divide each factor out completely as you go — then every
divisor you meet is automatically prime and needs no separate check. Problem 3
(`solutions/public/p0003/`) does exactly this, recomputing the $\sqrt{}$-ceiling against the shrinking
remainder so the loop ends early once only a large prime cofactor is left. [Wheel
factorization](https://en.wikipedia.org/wiki/Wheel_factorization) sharpens the constant: every prime
past $2$ is odd and every prime past $3$ is $\equiv \pm 1 \pmod 6$, so stepping through $6k \pm 1$
skips two-thirds of the candidates — it does not change the asymptotics, but on a factoriser's hot
loop that factor is worth having.

**Test a *large* single number — the [Miller–Rabin primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test).**
Trial division to $\sqrt{n}$ is fine up to perhaps $10^{12}$; past that its cost explodes.
Miller–Rabin instead asks a witness question rooted in Fermat's little theorem: write
$n - 1 = 2^s \cdot d$ and check, for a chosen base $a$, whether the repeated squarings of $a^d
\pmod n$ betray $n$ as composite. A single base can be fooled, but each independent base that passes
multiplies your confidence — and for $n$ below fixed thresholds a *specific small set of bases* makes
the test **deterministic**, exactly correct with no probability left. Its cost is $O(k \log^3 n)$ for
$k$ bases: effectively instant even for numbers with dozens of digits, which is why the
higher-numbered primality problems (and RSA key generation) reach for it rather than a sieve. It is
this cheap, one-sided test — easy to *confirm* a prime, hard to *factor* a composite — that the next
section turns into a lever.

## The asymmetry that pays the modern bills

Here is the fact the applications turn on: **multiplying primes is easy, and factoring their product
is hard.** Given two large primes you can multiply them in microseconds, but given only the product —
a [semiprime](https://en.wikipedia.org/wiki/Semiprime) $n = pq$ — recovering $p$ and $q$ is, as far as
anyone knows, infeasible once the primes are a few hundred digits long. No polynomial-time
[integer-factorisation](https://en.wikipedia.org/wiki/Integer_factorization) algorithm is known
(on classical hardware), yet *checking* primality is cheap. That gap between an easy forward operation
and an intractable inverse is a **one-way function**, and it is the engine of modern public-key
cryptography:

- **[RSA](https://en.wikipedia.org/wiki/RSA_cryptosystem).** A public key is a semiprime $n = pq$
  built from two secret large primes. Encryption and decryption are modular exponentiations whose
  correctness is guaranteed by Fermat's and Euler's theorems — you work in the exponent modulo
  $\varphi(n) = (p-1)(q-1)$ — and the scheme is secure precisely because an attacker who cannot factor
  $n$ cannot recover $\varphi(n)$. Generating the keys means *manufacturing* large primes, which is
  where fast probabilistic primality tests earn their keep.
- **[Diffie–Hellman](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange) and the
  [discrete logarithm](https://en.wikipedia.org/wiki/Discrete_logarithm).** Arithmetic modulo a large
  prime $p$ forms a cyclic group; exponentiating a generator is easy but inverting it (the discrete
  log) is hard, giving a second one-way function that underlies key exchange and signatures. The same
  idea over the points of an [elliptic curve](https://en.wikipedia.org/wiki/Elliptic-curve_cryptography)
  gives equivalent security with far smaller keys.

The reach of the mathematics goes well past cryptography, because a prime modulus has the cleanest
possible arithmetic — the integers modulo $p$ form a [finite field](https://en.wikipedia.org/wiki/Finite_field),
where every non-zero element is invertible:

- **Hashing.** [Hash tables](https://en.wikipedia.org/wiki/Hash_table) size their bucket arrays to a
  prime and reduce keys modulo it, because a prime shares no factor with the strides that real-world
  keys tend to arrive on, spreading them evenly instead of piling them into a few buckets. Polynomial
  "rolling" hashes evaluate a string as a polynomial modulo a large prime for the same reason.
- **Pseudo-random numbers.** The classic [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator)
  MINSTD uses the Mersenne prime $2^{31} - 1$ as its modulus to attain full period, and the
  [Mersenne Twister](https://en.wikipedia.org/wiki/Mersenne_Twister) — the default generator in
  Python, and in problem 213's kind of stochastic simulation — takes its name and its period
  $2^{19937} - 1$ from a Mersenne prime.
- **Error correction and signal processing.** [Reed–Solomon codes](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)
  behind QR codes, CDs, and deep-space links do their arithmetic in a finite field; prime-length
  [fast Fourier transforms](https://en.wikipedia.org/wiki/Rader%27s_FFT_algorithm) exploit the
  multiplicative group of $\mathbb{Z}/p\mathbb{Z}$ to reindex a transform.

## How to reason about it

The through-line across the problems below is that a prime is never *just* a prime — it is the atom
that makes some larger quantity computable:

- **See a multiplicative quantity** — a divisor count, a totient, a coprimality condition, a "product
  of two primes" — and reach for the factorisation. The exponent vector is the object you actually
  manipulate; the answer is a product over the primes dividing $n$.
- **Need a bound or a density** — how many primes below $N$, how large the $n$-th prime, how many
  semiprimes in a range — and the prime number theorem ($\pi(x) \sim x/\ln x$, $p_n \sim n \ln n$) is
  your estimate. Use it to *size* a sieve, not to replace an exact count.
- **See a one-way structure** — a public key, a semiprime to be split, a discrete log — and recognise
  that its security *is* the hardness of a prime problem. The Euler problems that touch cryptography
  (RSA-flavoured factorisation, modular inverses) are miniatures of the same asymmetry.
- **Then pick the tool by the shape of the question.** Many primes below a known bound → sieve, sized
  to the inputs ($n \ln n$ for "the $n$-th prime") and built *inside* `solve()` so the benchmark
  counts it honestly. Factor one number, or a modest range → trial division to $\sqrt{n}$ with
  full division-out and a $6k \pm 1$ wheel. A yes/no on one *large* number → Miller–Rabin with a
  deterministic base set. The classic mistake is answering a range question one number at a time — a
  primality test in a loop where a single $O(N \log \log N)$ sieve would produce the whole set — or
  answering a single-number question with a sieve of millions of primes to check just one.

Match the mathematics and the algorithm to the shape of the question and the erratic surface of the
primes gives way to a small set of reliable laws — the same laws that, four centuries after Fermat,
keep the world's secrets. The problems below all turn on that fit.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
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
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
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
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ○ [0233](/solutions/0233/) — Lattice Points on a Circle
- ○ [0234](/solutions/0234/) — Semidivisible Numbers
- ○ [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0243](/solutions/0243/) — Resilience
- ○ [0245](/solutions/0245/) — Coresilience
- ○ [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ○ [0249](/solutions/0249/) — Prime Subset Sums
- ○ [0251](/solutions/0251/) — Cardano Triplets
- ○ [0263](/solutions/0263/) — An Engineers' Dream Come True
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ○ [0272](/solutions/0272/) — Modular Cubes, Part 2
- ○ [0273](/solutions/0273/) — Sum of Squares
- ○ [0274](/solutions/0274/) — Divisibility Multipliers
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ○ [0291](/solutions/0291/) — Panaitopol Primes
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ○ [0302](/solutions/0302/) — Strong Achilles Numbers
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0308](/solutions/0308/) — An Amazing Prime-generating Automaton
- ● [0313](/solutions/0313/) — Sliding Game
- ○ [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0333](/solutions/0333/) — Special Partitions
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0351](/solutions/0351/) — Hexagonal Orchards
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ○ [0362](/solutions/0362/) — Squarefree Factors
- ○ [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ○ [0386](/solutions/0386/) — Maximum Length of an Antichain
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0388](/solutions/0388/) — Distinct Lines
- ○ [0399](/solutions/0399/) — Squarefree Fibonacci Numbers
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ○ [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0425](/solutions/0425/) — Prime Connection
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0451](/solutions/0451/) — Modular Inverses
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0468](/solutions/0468/) — Smooth Divisors of Binomial Coefficients
- ● [0478](/solutions/0478/) — Mixtures
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ○ [0492](/solutions/0492/) — Exploding Sequence
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ● [0501](/solutions/0501/) — Eight Divisors
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ○ [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0517](/solutions/0517/) — A Real Recursion
- ○ [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0526](/solutions/0526/) — Largest Prime Factors of Consecutive Numbers
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators
- ○ [0543](/solutions/0543/) — Prime-Sum Numbers
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ○ [0548](/solutions/0548/) — Gozinta Chains
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ○ [0556](/solutions/0556/) — Squarefree Gaussian Integers
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0561](/solutions/0561/) — Divisor Pairs
- ○ [0563](/solutions/0563/) — Robot Welders
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0569](/solutions/0569/) — Prime Mountain Range
- ○ [0574](/solutions/0574/) — Verifying Primes
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0580](/solutions/0580/) — Squarefree Hilbert Numbers
- ○ [0590](/solutions/0590/) — Sets with a Given Least Common Multiple
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0593](/solutions/0593/) — Fleeting Medians
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0606](/solutions/0606/) — Gozinta Chains II
- ○ [0609](/solutions/0609/) — $\pi$ Sequences
- ○ [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0616](/solutions/0616/) — Creative Numbers
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ○ [0635](/solutions/0635/) — Subset Sums
- ○ [0636](/solutions/0636/) — Restricted Factorisations
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ○ [0646](/solutions/0646/) — Bounded Divisors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0659](/solutions/0659/) — Largest Prime
- ○ [0668](/solutions/0668/) — Square Root Smooth Numbers
- ○ [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ○ [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0727](/solutions/0727/) — Triangle of Circular Arcs
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ● [0745](/solutions/0745/) — Sum of Squares II
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0777](/solutions/0777/) — Lissajous Curves
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0787](/solutions/0787/) — Bézout's Game
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0810](/solutions/0810/) — XOR-Primes
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0821](/solutions/0821/) — 123-Separable
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0826](/solutions/0826/) — Birds on a Wire
- ○ [0829](/solutions/0829/) — Integral Fusion
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0841](/solutions/0841/) — Regular Star Polygons
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ○ [0846](/solutions/0846/) — Magic Bracelets
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ○ [0861](/solutions/0861/) — Products of Bi-Unitary Divisors
- ○ [0869](/solutions/0869/) — Prime Guessing
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0886](/solutions/0886/) — Coprime Permutations
- ○ [0920](/solutions/0920/) — Tau Numbers
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ○ [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ○ [0958](/solutions/0958/) — Euclid's Labour
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ○ [0975](/solutions/0975/) — A Winding Path
- ○ [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ○ [1005](/solutions/1005/) — Median Prime List

<!-- /problems -->
