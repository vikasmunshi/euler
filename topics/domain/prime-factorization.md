<!-- tags: [prime-factorization] -->
<!-- status: final -->
# Prime factorization

[Prime factorization](https://en.wikipedia.org/wiki/Integer_factorization) is what an integer
*is*, as opposed to what it looks like written down. The
[fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic)
says every $n > 1$ has exactly one decomposition $n = p_1^{e_1} p_2^{e_2} \cdots p_k^{e_k}$, and
the seventy-odd problems below are, almost without exception, problems about that decomposition
rather than about the number. This page is about the *object* — what the exponent vector tells you
and how to reason in it. The mechanics of obtaining one are
[trial division](/topics/technique/trial-division) and
[integer factorization](/topics/technique/integer-factorization), which have their own pages.

## The exponent vector is the real object

Write the factorization as a list of `(prime, exponent)` pairs and you have a coordinate system.
The public solution to problem 47 carries the canonical routine:

```python
def prime_factorization(n: int) -> tuple[tuple[int, int], ...]:
    factors = []
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
    return tuple(factors)
```

Uniqueness is what makes that tuple worth having: it is a *canonical form*, so two numbers are
equal exactly when their vectors are. Problem 29 turns that into its whole solution — comparing
$a^b$ values with a thousand digits is expensive, but $a^b$'s vector is just $a$'s vector with
every exponent multiplied by $b$, so the collision test becomes a hash-set insert of a handful of
small integers. Whenever a problem asks whether two monstrous expressions are the same number, the
vector is the cheap answer.

The vocabulary the problem titles use is all predicates on this vector, and it is worth being
fluent in it: $\omega(n)$ is its length (the count of *distinct* primes), $\Omega(n)$ the sum of
its exponents, a [square-free](/topics/domain/square-free-integer) number has every exponent $1$,
a [$B$-smooth](/topics/domain/smooth-number) number has every prime $\le B$, the
[radical](/topics/domain/radical-of-an-integer) is the vector with every exponent flattened to
$1$, and a [highly composite](/topics/domain/highly-composite-number) number is one whose
exponents are non-increasing over an initial run of primes. Problem 47 wants $\omega = 4$ four
times running; 615 wants $\Omega \ge 10^6$; 362, 632 and 668 constrain exponents and smoothness
directly.

## Multiplicative functions read straight off the vector

The reason to factor at all is almost never the factors. It is that a
[multiplicative function](/topics/domain/multiplicative-function) — one where
$f(ab) = f(a)f(b)$ for coprime $a, b$ — is determined entirely by its values on prime powers, so
once you have the vector the function is a product over $k$ terms rather than a search over $n$:

| Function | From $n = \prod p_i^{e_i}$ | Where it does the work |
| --- | --- | --- |
| [divisor count](/topics/domain/divisor-function) $\tau(n)$ | $\prod (e_i + 1)$ | 12, 108, 920 |
| divisor sum $\sigma(n)$ | $\prod \frac{p_i^{e_i+1} - 1}{p_i - 1}$ | 650 |
| [totient](/topics/domain/eulers-totient-function) $\varphi(n)$ | $n \prod \left(1 - \frac{1}{p_i}\right)$ | 69, 248, 342 |
| [radical](/topics/domain/radical-of-an-integer) $\mathrm{rad}(n)$ | $\prod p_i$ | 124 |
| $\sum_{d \mid n} 2^{\omega(d)}$ | $\prod (2e_i + 1)$ | 675 |
| solutions of $x^3 \equiv 1 \pmod n$ | $3^{\#\{p_i \equiv 1 \ (3)\}}$, times $3$ if $9 \mid n$ | 272 |

Two habits follow from that table. The first is that "count the divisors of $n$" is never a
divisor-counting loop; it is a factorization and a product. Problem 108 goes one step further and
never forms its number at all — the question is $\tau(n^2)$, and squaring $n$ means doubling every
exponent, so $\tau(n^2) = \prod (2e_i + 1)$ falls out of $n$'s own vector. That same product turns
up in problem 675 under a different name: $\sum_{d \mid n} 2^{\omega(d)}$ is a
[Dirichlet convolution](https://en.wikipedia.org/wiki/Dirichlet_convolution) of two multiplicative
functions, and on a prime power $p^e$ it is $1 + 2e$. Written as sums the two look unrelated;
written on the vector they are visibly one function, $\tau(n^2)$ — and recognising that is the kind
of identity the vector hands you for free.

The second is that multiplicative is *not* completely multiplicative: the identity needs the
arguments coprime, and getting that coprimality is often the design move. Problem 12 wants
$\tau$ of the triangular number $n(n+1)/2$; rather than factor a number of size $n^2$, it observes
that consecutive integers are [coprime](/topics/domain/coprime-integers), folds the halving into
whichever of $n, n+1$ is even, and multiplies two $\tau$ values computed on numbers half the size.
Problem 69 leans on the same structure from the other end: $n/\varphi(n) = \prod p_i/(p_i - 1)$
depends only on the *set* of primes, never the exponents, so raising any prime above the first
power inflates $n$ and buys nothing — and the maximiser under a bound is forced to be a
[primorial](https://en.wikipedia.org/wiki/Primorial), collapsing a million-element search to about
seven multiplications. Read the formula to see which coordinates matter, and the search space
usually collapses with it.

The trick generalises past the textbook functions. Problem 233 counts lattice points on a circle,
which reduces to $r_2(m)$, the number of representations of $m$ as an ordered sum of two squares —
and [Jacobi's two-square theorem](https://en.wikipedia.org/wiki/Sum_of_two_squares_theorem) makes
*that* a product over the exponents of the primes $\equiv 1 \pmod 4$. A great many counting
questions that look geometric or combinatorial are multiplicative functions in disguise.

The last row of the table is the most reusable shape of all: *the number of solutions of a
congruence modulo $n$*. The [Chinese remainder theorem](/topics/technique/chinese-remainder-theorem)
splits a solution modulo $n$ into independent solutions modulo each $p_i^{e_i}$, so the count is
multiplicative whatever the congruence. Problem 272 counts cube roots of unity; for an odd prime the
[unit group](/topics/domain/cyclic-group) modulo $p^e$ is cyclic of order $p^{e-1}(p - 1)$, and a
cyclic group of order $m$ holds exactly $\gcd(3, m)$ solutions of $x^3 = 1$. Notice which
coordinate that reads. Not the exponent, which is irrelevant everywhere except at $p = 3$, but the
*residue class of the prime itself*: every $p \equiv 1 \pmod 3$ triples the count, and every other
prime contributes nothing. A target such as "exactly 242 non-trivial roots" therefore becomes
"exactly five tripling factors", which is a constraint on the support of the vector, and the search
proceeds from there (below).

## Valuations: coordinates of numbers you cannot write down

One coordinate of the vector is the
[$p$-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation) $v_p(n)$ — the exponent of
$p$ in $n$. Treating it as a quantity in its own right is the single most productive idea on this
page, because valuations are computable for numbers that can never be formed.
[Legendre's formula](/topics/domain/legendres-formula) is the lever:

$$v_p(N!) = \sum_{i \ge 1} \left\lfloor \frac{N}{p^i} \right\rfloor
          = \frac{N - s_p(N)}{p - 1},$$

where $s_p(N)$ is the digit sum of $N$ in base $p$. That is $O(\log_p N)$ integer divisions for
the exponent of $p$ in a number with astronomically many digits, and valuations subtract, so
$v_p\binom{n}{m} = v_p(n!) - v_p(m!) - v_p((n-m)!)$ comes free.

The problems built on this all share the same silhouette: *the answer is a function of a
factorization; the number itself is never formed*. Problem 231 sums $p \cdot e_p$ over the
factorization of $\binom{20000000}{15000000}$ — a coefficient with a million digits — by evaluating
Legendre's formula once per prime. Problem 650 needs $\sigma$ of a product of binomial coefficients,
so it accumulates the exponent vector by telescoping valuations and feeds it to the $\sigma$
product. Problem 288 is handed $N$ as its own base-$p$ digits and uses the digit-sum form directly,
never assembling $N$. Problem 549 asks for the least $m$ with $n \mid m!$, and because the
constraint $v_p(m!) \ge e_p$ is independent for each prime power, the answer is a maximum over
prime powers — reducing $10^8$ separate questions to a table indexed by $p^e$.

When the question runs over a whole *sequence* of factorials, even Legendre per term is too much:
problem 675 needs $\prod_p (2 e_p(i!) + 1)$ for every $i$ up to $10^7$, and re-evaluating it costs
$\pi(i)$ factors each time. But $i!$ and $(i-1)!$ have vectors that differ only at the primes
dividing $i$, so the product changes by at most $\omega(i)$ ratios — replace the factor
$2(e - v) + 1$ by $2e + 1$ wherever $p^v \parallel i$. Under a prime modulus those ratios are
modular inverses, and the whole sequence becomes one running product. Maintain the vector
incrementally, and update the function only on the coordinates that moved.

If a problem's numbers are factorials, binomials, or products of them, do not reach for
[bignums](/topics/technique/arbitrary-precision-arithmetic). Reach for valuations.

## Factoring a whole family: walk the primes, not the numbers

Valuations read one prime's coordinate of one huge number. The same move scales to a *family* of
numbers whose factorizations you want in aggregate: fix the prime, and ask which members of the
family it divides. Problem 421 sums the prime factors below $M = 10^8$ of $n^{15} + 1$ for every
$n \le 10^{11}$ — $10^{11}$ factorizations of numbers up to 165 digits, if read literally. Exchanging
the order of summation,

$$\sum_{n \le N} \; \sum_{\substack{p \le M \\ p \mid n^{15}+1}} p
  \;=\; \sum_{p \le M} p \cdot \#\{\, n \le N : n^{15} \equiv -1 \pmod p \,\},$$

trades those factorizations for one question per prime, and that question is again about a cyclic
group: the solutions of $n^{15} \equiv -1$ are the negatives of the
[15th roots of unity](/topics/domain/root-of-unity) modulo $p$, of which there are exactly
$\gcd(15, p - 1)$. As in 272, the count is decided by the prime's residue class — here modulo $3$
and modulo $5$ — and each root contributes a floor division's worth of $n$. The cost is linear in
$\pi(M)$ and independent of $N$; the factorization of $n^{15}+1$ is never computed for any $n$.

That is the general pattern whenever the numbers come from a polynomial: $p \mid f(n)$ depends only
on $n \bmod p$, so the primes that divide the family are found by solving $f(x) \equiv 0 \pmod p$
once per prime, not by factoring $f(n)$ once per $n$. It is the
[sieve](/topics/technique/sieve-of-eratosthenes) idea transplanted from the integers to the values
of $f$.

## Constraints on the vector, not on the number

The other recurring inversion is generative. If a problem's condition is really a condition on the
exponent vector, stop testing integers and start enumerating vectors — there are vastly fewer of
them, and each one you build already satisfies the condition.

- **Constrain the support.** Problem 293 calls $N$ admissible when its distinct primes are
  consecutive from $2$, which means the support is a *prefix* of the prime sequence — so instead of
  filtering $10^9$ even numbers, it generates the few thousand numbers of the form
  $2^{a_1} 3^{a_2} 5^{a_3} \cdots$ directly. Problem 347 fixes the support at exactly two primes,
  and uniqueness of factorization then guarantees the resulting values are distinct with no
  deduplication needed. Problems 668 and 682 constrain the support by smoothness.
- **Split the vector into a constrained part and a free part.** In problem 272 only the primes
  $\equiv 1 \pmod 3$ (and $9$) are constrained — exactly five of them — while the rest of $n$ is a
  cofactor drawn from the remaining primes. So $n = A \cdot m$ uniquely, a depth-first search
  enumerates the few products $A$, and the cofactors are never enumerated at all: a
  [prefix sum](/topics/technique/prefix-sum) of the admissible $m$ answers
  $\sum m \le \lfloor L/A \rfloor$ in one lookup per $A$.
- **Invert a multiplicative function by factoring its value.** Problem 248 wants every $n$ with
  $\varphi(n) = 13!$. Since $\varphi(n) = \prod p_i^{e_i - 1}(p_i - 1)$, each factor divides the
  target, so a prime may appear in $n$ only when $p - 1$ divides $13!$ — a small candidate
  alphabet, and the search becomes an enumeration of factorizations of the target rather than of
  values of $n$. Problem 516 combines this with the split above: it wants every $n \le 10^{12}$
  whose $\varphi(n)$ is [5-smooth](/topics/domain/smooth-number), and reading the condition factor
  by factor says that $2, 3, 5$ may appear to any power, while any larger prime $q$ must appear
  exactly once (else $q \mid \varphi(n)$) with $q - 1$ itself 5-smooth. So
  $n = h \cdot q_1 \cdots q_k$ — a [Hamming number](https://en.wikipedia.org/wiki/Regular_number)
  times a square-free product of a few hundred
  "good" primes — and the search walks those products, answering the free Hamming part with a
  prefix sum. Problems 342 and 533 reason backwards from a condition on $\varphi$ and on the
  Carmichael function in the same spirit — the condition constrains the factorization, and the
  factorization is what you enumerate.
- **Use exponent parity as an argument.** A prime above $\sqrt{B}$ can appear at most once among
  the numbers up to $B$, which in problem 152 forces every large prime's contributions to cancel
  within its own multiples and splits an infeasible $2^{79}$ subset search into independent small
  ones. Problem 619 makes the parity vector over $\mathbb{F}_2$ the whole object.
- **Turn divisibility into a divisor enumeration.** Problem 221 rewrites its condition as
  $d_1 d_2 = p^2 + 1$, so each Alexandrian integer is a divisor pair; problem 834 reduces its
  divisibility test to "the divisors of $n(n-1)/2$ exceeding $n$", which a sieve answers in bulk.

## How to reason about it

When a problem smells multiplicative, work down this list.

1. **Restate the question on the vector.** "Divisible by", "square-free", "$k$ distinct primes",
   "smooth", "a perfect square", "coprime to" — every one of these is a statement about exponents.
   Write it that way before writing any code; the algorithm usually falls out of the restatement.
2. **Ask which coordinates the answer actually depends on.** $\varphi$'s ratio ignores exponents;
   $\tau$ ignores the primes themselves; $\mathrm{rad}$ ignores multiplicity; a root count reads
   only each prime's residue class. Whatever the formula discards, the search can discard too.
3. **Ask whether you need the number at all.** If it is a factorial or a binomial, valuations give
   you its factorization without it. If it is one of many values of a polynomial, loop over the
   primes and solve the congruence instead.
4. **Ask whether to enumerate forward.** Generating numbers of a prescribed multiplicative shape is
   almost always cheaper than generating integers and decomposing them.
5. **Only then decide how to factor.** One number or a scattered few: trial division against a
   prime list. Every number below $N$: a smallest-prime-factor or
   [divisor-sum sieve](/topics/technique/divisor-sum-sieve), which computes the whole range for
   about the cost of one pass — problem 124 sieves a hundred thousand radicals this way without
   factoring anything.

Two things bite in practice. Exponent vectors are cheap but their *products* are not: reconstructing
$n$ from its vector overflows a 64-bit word long before the vector itself is inconvenient, so keep
comparisons in log space or in the exponents. And be precise about $\omega$ versus $\Omega$ — the
count of distinct primes and the count with multiplicity are different numbers, the problems below
ask for both, and a factoriser that returns pairs makes the distinction impossible to get wrong.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ○ [0302](/solutions/0302/) — Strong Achilles Numbers
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ○ [0362](/solutions/0362/) — Squarefree Factors
- ○ [0386](/solutions/0386/) — Maximum Length of an Antichain
- ○ [0399](/solutions/0399/) — Squarefree Fibonacci Numbers
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0468](/solutions/0468/) — Smooth Divisors of Binomial Coefficients
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0548](/solutions/0548/) — Gozinta Chains
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ○ [0556](/solutions/0556/) — Squarefree Gaussian Integers
- ○ [0561](/solutions/0561/) — Divisor Pairs
- ○ [0563](/solutions/0563/) — Robot Welders
- ○ [0574](/solutions/0574/) — Verifying Primes
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0590](/solutions/0590/) — Sets with a Given Least Common Multiple
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0606](/solutions/0606/) — Gozinta Chains II
- ○ [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0616](/solutions/0616/) — Creative Numbers
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0636](/solutions/0636/) — Restricted Factorisations
- ○ [0646](/solutions/0646/) — Bounded Divisors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0821](/solutions/0821/) — 123-Separable
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0829](/solutions/0829/) — Integral Fusion
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0840](/solutions/0840/) — Sum of Products
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ○ [0861](/solutions/0861/) — Products of Bi-Unitary Divisors
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0920](/solutions/0920/) — Tau Numbers
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ○ [0956](/solutions/0956/) — Super Duper Sum

<!-- /problems -->
