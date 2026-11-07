<!-- tags: [multiplicative-function] -->
<!-- status: final 2026-11-04T13:18Z -->
# Multiplicative function

An arithmetic function $f$ is [multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function)
when $f(1) = 1$ and $f(mn) = f(m)\,f(n)$ whenever $\gcd(m, n) = 1$. That one rule is the most
useful structural fact in computational number theory, because it says the function has no global
behaviour at all: $f(n)$ is the product of what it does on each prime power of $n$ separately. The
forty-odd problems below ask about divisor counts, totients, radicals, Möbius signs, unitary
divisors and stranger things built just for the problem, but they share one move. Find the local
rule $f(p^a)$, and the rest is bookkeeping in one of a handful of shapes.

## The idea: a function is its prime powers

By the [fundamental theorem of arithmetic](/blogs/domain/fundamental-theorem-of-arithmetic),
$n = p_1^{a_1} \cdots p_k^{a_k}$ splits into pairwise coprime prime powers, so a multiplicative
$f$ satisfies

$$f(n) = \prod_{i} f\!\left(p_i^{a_i}\right).$$

Writing down $f(p^a)$ is the whole specification. The functions that recur here:

| function | $f(p^a)$ | where it shows up |
| --- | --- | --- |
| number of divisors $d(n)$ | $a + 1$ | 12, 108, 110, 501 |
| $n$-fold divisor function $d_k(n)$ | $\binom{k+a-1}{a}$ | 452 |
| divisor sum $\sigma_k(n)$ | $1 + p^k + \dots + p^{ak}$ | 211, 241, 565 |
| [Euler's totient](/blogs/domain/eulers-totient-function) $\varphi(n)$ | $p^{a-1}(p - 1)$ | 72, 243, 248, 342, 432, 516 |
| [Möbius](/blogs/domain/mobius-function) $\mu(n)$ | $-1$ if $a = 1$, else $0$ | 464, 633, 745 |
| [radical](/blogs/domain/radical-of-an-integer) $\operatorname{rad}(n)$ | $p$ | 124, 127 |
| $2^{\omega(n)}$ (squarefree divisors) | $2$ | 675 |
| $\sum_{d \mid n} 2^{\omega(d)} = d(n^2)$ | $2a + 1$ | 675 |
| [unitary](/blogs/domain/unitary-divisor) square sum | $1 + p^{2a}$ | 429 |
| [two-square](/blogs/domain/sum-of-two-squares-theorem) count $r_2(n)/4$ | $a + 1$ if $p \equiv 1 \pmod 4$; for $p \equiv 3$, $1$ if $a$ is even, else $0$; $1$ at $p = 2$ | 621 |
| $x^{S(n)}$ with $x^3 = 1$, $S(n)$ the sum of the distinct primes of $n$ | $x^p$ | 967 |

Two cautions belong right next to the definition. First, the coprimality condition is not
decoration: $d(4) = 3$ but $d(2)^2 = 4$. Only a *completely* multiplicative function ($n$, $n^k$,
the [Liouville function](https://en.wikipedia.org/wiki/Liouville_function)) ignores it, and almost
nothing on this list is one. Second, the problems often invent a function and leave you to discover
that it is multiplicative. Problem 484's $\gcd(k, k')$, the gcd of $k$ and its
[arithmetic derivative](/blogs/domain/arithmetic-derivative), looks hopeless until a
[$p$-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation) argument, one prime at a
time, shows that each prime contributes $p^{a-1}$, or $p^a$ when $p \mid a$. Once you have shown that,
the problem is the same kind as the others. Problem 429's unitary divisors are the same story: a
unitary divisor takes each prime power whole or not at all, so the sum of their squares is
$\prod(1 + p^{2a})$. Problem 452 counts ordered $k$-tuples with product at most $m$. Grouping them by
their product turns the count into $\sum_{n \le m} d_k(n)$, and $d_k$ is multiplicative because the
tuple distributes each prime's exponent over the $k$ slots on its own. That is
[stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)), which gives the
binomial in the table.

## Four shapes of computation

What you do with the local rule depends on how many values the problem needs.

**One value: factor, then multiply.** For a single $n$, or a handful,
[factor](/blogs/technique/prime-factorization-application) it and multiply the local factors.
Problem 12 needs $d(T)$ for triangular numbers $T = n(n+1)/2$, and its fast solution uses
multiplicativity before any factoring: $n$ and $n+1$ are coprime, so after the $2$ is folded into
whichever is even, $d(T)$ is the product of two divisor counts on numbers half the size.

```python
# p0012: T(i) = (i/2) * (i+1) or i * ((i+1)/2), and the two factors are coprime
d_T = num_factors(i // 2) * num_factors(i + 1) if i % 2 == 0 else num_factors(i) * num_factors((i + 1) // 2)
```

Problem 429 never factors anything. The exponents of a factorial come from
[Legendre's formula](/blogs/domain/legendres-formula), so $\prod_p (1 + p^{2e_p})$ over the primes up
to $10^8$ is a sieve plus one modular power per prime. Problem 675 needs a whole sequence of these:
$\sum_{d \mid n} 2^{\omega(d)}$ for every factorial $i!$ up to $10^7$. That function is $1 * 2^{\omega}$, so
its local rule is $2a + 1$. Rebuilding the product for each $i$ would cost $\pi(i)$ factors per term.
The faster way uses the fact that $i!$ differs from $(i-1)!$ only at the primes dividing $i$. Each of
those primes swaps one local factor for another, and the update is the ratio of the two. With a prime
modulus, the division is a precomputed modular inverse, so the whole sequence comes from one running
product.

**Every value up to $N$: sieve it.** When the problem needs $f(1), \dots, f(N)$, put the local rule
into a sieve. The [Eratosthenes](/blogs/technique/sieve-of-eratosthenes)-style form lets each prime
apply its factor to its multiples. Problem 72 sums $\varphi(2..N)$ this way, and the whole totient
is two lines:

```python
# p0072: a cell still equal to its index is prime; it applies (p-1)/p to every multiple
if phi[n] == n:
    for j in range(n, N + 1, n):
        phi[j] = phi[j] // n * (n - 1)
```

Additive divisor functions such as $\sigma_2$ in problem 211 suit a
[divisor-sum sieve](/blogs/technique/divisor-sum-sieve) better: add $d^2$ to every multiple of $d$,
$O(N \log N)$ total. A [linear sieve](/blogs/technique/linear-sieve) visits each composite exactly
once through its smallest prime factor and works for any multiplicative $f$. The catch is the case
where the sieving prime $p$ already divides $i$: then $i \cdot p$ and $p$ are *not* coprime, and
$f(ip) \ne f(i)f(p)$. Problem 745 handles it by tracking the full $p$-power block of each index and
multiplying $f(p^a)$ into the coprime cofactor. That branch is where linear-sieve bugs live.

**Every value along a polynomial: sieve its roots.** Sometimes the values wanted are a thin,
structured subset, too many to factor one by one and too spread out for a sieve up to the largest.
Problem 621 counts the ways to write $n$ as three triangular numbers. Fix the first one and the other
two are a sum-of-two-squares question, so the answer is $\sum_a r_2(f(a))/4$ for a quadratic $f$. That
is a multiplicative function at about $\sqrt{2n}$ points, each as large as $4n$. What rescues it is
that a prime $p$ divides $f(a)$ only when $a$ lies in the residue classes of $f$'s roots mod $p$, and
there are at most two of those. So a [polynomial sieve](/blogs/technique/polynomial-sieve) walks
those progressions instead of the multiples of $p$, starting from
[modular square roots](/blogs/technique/quadratic-residue), and multiplies in the local factor at
each hit as the totient sieve does. A multiplicative target adds two duties. The local rule reads the
exponent, so each hit must divide $p$ out completely instead of just noting it. And sieving only to
the square root of the largest value leaves a cofactor that is $1$ or a single prime, whose factor
has to be applied at the end; here its residue mod 4 settles it.

**The sum up to a huge $N$: convolve.** When $N$ is $10^{11}$ or $10^{15}$ you cannot touch each $n$,
and the summatory function $F(N) = \sum_{n \le N} f(n)$ has to come from structure. The tool is
[Dirichlet convolution](/blogs/domain/dirichlet-convolution),
$(g * h)(n) = \sum_{d \mid n} g(d)\,h(n/d)$, which turns multiplicative functions into multiplicative
functions. Write $f = g * h$ with $g$ easy to sum, and

$$\sum_{n \le N} f(n) = \sum_{d \le N} h(d)\, G\!\left(\lfloor N/d \rfloor\right).$$

The work depends on how sparse $h$ is. In problem 745, $h = \mu * \mathrm{id}^2$ lives on squares, so
the sum is $\sum_{m \le \sqrt N} h(m) \lfloor N/m^2 \rfloor$, which is $10^7$ terms instead of $10^{14}$.
In problem 484, $g(p) = 1$ forces $h(p) = 0$, so $h$ is supported on
[powerful numbers](https://en.wikipedia.org/wiki/Powerful_number). There are only
$\Theta(\sqrt N)$ of them, and a [depth-first search](/blogs/technique/depth-first-search) over
prime exponents $\ge 2$ visits each one once. This is the "powerful number trick", and it fits any
$f$ that agrees with a simple function on the primes. When $h$ is not sparse, the
[Dirichlet hyperbola method](/blogs/technique/dirichlet-hyperbola-method) splits the sum at
$\sqrt N$, and
[Möbius inversion](/blogs/technique/mobius-inversion-formula) with a
[totient summatory recursion](/blogs/technique/totient-summatory-recursion) gets $\sum \varphi$ in
about $O(N^{2/3})$ (problems 432 and 448). The fully general tool is the
[Min_25 sieve](/blogs/technique/min-25-sieve), which is what problem 639 is named for. It needs two
things: the sum of $f$ over the primes, and the local rule for everything else. Problem 452 shows the
simplest case. Since $d_k(p) = k$ is constant on primes, the prime part is just $k \cdot \pi(v)$, and a
[Lucy–Hedgehog](https://en.wikipedia.org/wiki/Prime-counting_function#Algorithms_for_evaluating_%CF%80(x))
prime count supplies $\pi(v)$ at the $O(\sqrt m)$ floor values $\lfloor m/i \rfloor$. A recursion over
smallest prime factors then adds the composites, and both phases cost about $O(m^{3/4}/\log m)$.

## Running it backwards: search over exponent signatures

Sometimes the problem gives $f(n)$ and asks for $n$. Multiplicativity turns that into a search over
prime-power factorisations, and the local rule tells you how to prune it.

Problems 108 and 110 reduce, through
[Simon's factoring trick](https://artofproblemsolving.com/wiki/index.php/Simon%27s_Favorite_Factoring_Trick),
to the smallest $n$ with $d(n^2) = \prod (2a_i + 1)$ above a target. Since $d$ depends only on the
multiset of exponents, the cheapest $n$ for a given signature puts the largest exponent on the
smallest prime. That means a DFS over $2, 3, 5, \dots$ with non-increasing exponents, which is the
same argument that defines a [highly composite number](/blogs/domain/highly-composite-number).
Problem 248 inverts the totient: $\varphi(n) = 13!$ means each prime power $p^a \| n$ contributes
$p^{a-1}(p-1)$, which must divide what is left of the target. So the candidate primes are exactly the
$p$ with $p - 1 \mid 13!$, and the DFS divides the remaining target down as it goes.

The same reasoning works when the target is a *property* of $f(n)$ instead of a value. Problem 516
asks for every $n \le 10^{12}$ whose totient is 5-smooth. A product is 5-smooth exactly when each
factor is, so the condition holds one prime at a time. For $p \in \{2, 3, 5\}$ any exponent passes.
For $p > 5$, the factor $p^{a-1}$ forces $a = 1$, and $p - 1$ must itself be a
[Hamming number](https://en.wikipedia.org/wiki/Regular_number). So every admissible $n$ is a Hamming
number times a squarefree product of these "good" primes. The search space drops from $10^{12}$
integers to a few thousand Hamming numbers and a few million prime subsets.

Problem 342 shows where that argument stops. It asks when
$\varphi(n^2) = \prod_p p^{2e_p - 1}(p - 1)$ is a perfect cube, and a product can be a cube without
its factors being cubes, so the condition no longer holds one prime at a time. Worse, the factor
belonging to $p$ is not local to $p$: its $p - 1$ spills into the exponents of other primes. The
structure that survives is the direction of the spill, because $p - 1$ only reaches primes *smaller*
than $p$. So the search takes the primes of $n$ from the largest down and
[carries only the exponents owed mod 3](/blogs/takeaway/search-residues-not-values), and a prime is
[closed for good](/blogs/takeaway/order-search-so-constraints-close) once the search has passed it.
The largest prime receives nothing from the others, which forces its exponent to be $2 \bmod 3$ and
puts every prime involved below $\sqrt N$. The coupling also makes pruning harder than it looks. A
smaller owed prime can be paid off by some later $p - 1$ instead of entering $n$, so only the largest
owed prime gives a sound lower bound on what is still to come. Charging every owed prime at its forced
exponent looks like a stronger prune, but it discards real solutions, and only a brute-force
comparison showed it.

## Local to global beyond arithmetic functions

The same idea applies to counts modulo $n$. By the
[Chinese remainder theorem](/blogs/technique/chinese-remainder-theorem), $\mathbb{Z}/n$ splits into
the product of $\mathbb{Z}/p^a$. So the number of solutions of a polynomial congruence mod $n$ is
multiplicative in $n$: count the cube roots of unity mod each prime power and multiply (problem 271).
The local count still needs care. In 271 there are three roots modulo $p$ when $3 \mid p - 1$ and one otherwise, and
[Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma) lifts each root uniquely to $p^k$.
The exception is $p = 3$, where the derivative $3x^2$ vanishes: there is one root mod $3$ but three
mod $9$. A rule derived from the primes alone misses that case. Also, once the roots are combined
through CRT, the *sum* of the solutions is not multiplicative even though their *count* is, so 271
enumerates the combinations themselves. The
[Pisano period](/blogs/domain/pisano-period) of problem 853 combines the same way, except the prime-power
periods meet in an $\operatorname{lcm}$ instead of a product.

Lifting roots one at a time is no use when the solutions number about $n^7$. Problem 875 counts the
zeros mod $n$ of an eight-variable [quadratic form](/blogs/domain/quadratic-form), and a
[roots-of-unity filter](/blogs/technique/roots-of-unity-filter) skips the local analysis altogether.
The filter rewrites the count as $\frac1n \sum_t |G(t, n)|^8$ over
[quadratic Gauss sums](/blogs/technique/quadratic-gauss-sum), and grouping the $t$ by the reduced
denominator of $t/n$ gives a Dirichlet convolution outright: $q = \mathrm{Id}^7 * w$, where $w$ is a
multiplicative weight built from $\varphi$ and the size of the Gauss sum. That is more than a proof
that $q$ is multiplicative. It is the factorisation the summation needs, because the swap from the
convolution shape leaves $\sum_m w(m)\, S_7(\lfloor N/m \rfloor)$, with $S_7$ a closed form from
[Faulhaber's formula](/blogs/technique/faulhabers-formula). The awkward prime is again the one that
divides the derivative: $3$ for the cubes of 271, $2$ for the squares here. Every odd prime has
$q(p) = p^7 + p^4 - p^3$, which predicts $136$ at $p = 2$, but the true count is $128$. The Gauss sum
mod 2 vanishes, so $w$ needs its own rule at the powers of 2.

## The identity does not care what it sums

Nothing in $f = g * h$ or the swap of summation needs the values to be numbers. A commutative ring
is enough, and for products an abelian group, and two problems depend on that.

Problem 967 counts the $n \le 10^{18}$ for which $S(n)$, the sum of the distinct primes up to $B$
dividing $n$, is a multiple of 3. $S$ is additive, not multiplicative, and the target is a residue, not
a total. Exponentiating fixes both. In the [group ring](/blogs/technique/group-ring-arithmetic)
$\mathbb{Z}[x]/(x^3 - 1)$, the function $\chi(n) = x^{S(n)}$ is multiplicative, and the three
coefficients of $\sum_n \chi(n)$ count the $n$ in each residue class. Its local rule ignores the
exponent, $\chi(p^a) = x^p$ for every $a$, so $\chi = \mathbf 1 * h$ with $h$ supported on squarefree
numbers and $h(p) = x^p - 1$. That is the sparse-$h$ move from the convolution shape with ring elements
as values, and the prime 3 drops out by itself, since $h(3) = 0$.

The same problem also loosens that move, because $g$ does not have to be $\mathbf 1$. Enumerating every
squarefree $d$ means about $7 \times 10^7$ terms. Keep the seven smallest relevant primes inside $g$
instead: their part of $\chi$ is [periodic](/blogs/domain/periodic-sequence) in $n$, so a prefix table
over one period gives its partial sums in $O(1)$, and $h$ runs over the large primes alone, about
$1.4 \times 10^6$ terms. The split is a dial between table size and term count. And since $h(d)$
depends only on how many primes of $d$ are $1$ and $2 \bmod 3$, the ring products happen once per class,
not once per term.

Problem 754 is the multiplicative version, and it starts with a warning. The Gauss factorial
$\gamma(n)$, the product of the $k \le n$ coprime to $n$, is *not* a multiplicative function:
$\gamma(15) = 896896$ while $\gamma(3)\gamma(5) = 48$. A definition that mentions coprimality promises
nothing. The machinery applies one level up, in the group $(\mathbb{Z}/p)^\times$, where a convolution
is written as a product and $\mu$ moves into the exponent:

$$\gamma(n) = \prod_{d \mid n} \left(d^{\,n/d}\,(n/d)!\right)^{\mu(d)}.$$

The quotient blocks survive that translation, with one difference. Over a run of $d$ sharing
$\lfloor N/d \rfloor$, a base that depends only on the quotient takes a difference of the
[Mertens function](/blogs/technique/mertens-function-application) as its exponent, while the base $d$,
which changes inside the run, needs a prefix table of $\prod d^{\mu(d)}$. Exponents
[reduce mod $p - 1$](/blogs/takeaway/reduce-exponent-modulo-group-order), so a negative Mertens
difference needs no special case.

## How to reason about it

- **Test for multiplicativity early.** If the quantity is defined through divisors, gcds, or
  solutions mod $n$, ask whether it splits over coprime factors. If it does, the problem gets much
  smaller. Check it numerically on small coprime pairs before building on it.
- **Derive $f(p^a)$ and verify it.** The local rule is the entire specification, so a wrong
  exponent case silently corrupts everything. Compare the product formula against brute force for
  $n \le 1000$. The $p \mid a$ case in problem 484 and the $a = 1$ versus $a \ge 2$ split of $\mu$
  are where errors hide. The rule can also vary with $p$ itself: by residue class (problem 621), or at
  the prime dividing the derivative (3 in problem 271, 2 in problem 875).
- **Choose the shape from $N$.** One value: factor. All values to $10^7$–$10^8$: sieve, inside
  `solve()`, sized to the input ([size the work to the input](/blogs/takeaway/size-work-to-the-input)).
  The values of a polynomial: sieve its roots mod each prime. A sum to $10^{12}$ and beyond: find a
  convolution $f = g * h$ with sparse $h$, or a sublinear summatory method.
- **Ask where the values live.** A count by residue, or a product mod a prime, is still a convolution
  problem once the values move into a group ring or an exponent (problems 967 and 754).
- **Respect the coprimality condition in sieves.** A linear sieve's "$p$ divides $i$" branch and a
  coprime split that forgets the shared factor of $2$ are the same bug: multiplying across a shared
  prime.
- **Search signatures, not numbers.** When $f(n)$ is given and $n$ is wanted, enumerate exponent
  patterns over small primes with monotone exponents, and prune with the local rule. If the target
  couples the primes, find which way the coupling runs and search in that order (problem 342).
- **Watch the width.** $\sigma_2(n)$ reaches $1.6\,n^2$, convolution sums approach
  $N \log N$, and products of local factors mod $10^9+7$ need a 128-bit intermediate in C
  ([watch integer width](/blogs/takeaway/watch-integer-width)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0243](/solutions/0243/) — Resilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ○ [0362](/solutions/0362/) — Squarefree Factors
- ○ [0379](/solutions/0379/) — Least Common Multiple Count
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ● [0452](/solutions/0452/) — Long Products
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ○ [0466](/solutions/0466/) — Distinct Terms in a Multiplication Table
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0530](/solutions/0530/) — GCD of Divisors
- ○ [0548](/solutions/0548/) — Gozinta Chains
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers

<!-- /problems -->
