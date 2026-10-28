<!-- tags: [multiplicative-function] -->
<!-- status: final 2026-10-14T07:13Z -->
# Multiplicative function

An arithmetic function $f$ is [multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function)
when $f(1) = 1$ and $f(mn) = f(m)\,f(n)$ whenever $\gcd(m, n) = 1$. That one rule is the most
useful structural fact in computational number theory, because it says the function has no global
behaviour at all: $f(n)$ is the product of what it does on each prime power of $n$ separately. The
thirty-eight problems below ask about divisor counts, totients, radicals, Möbius signs, unitary
divisors and stranger things built just for the problem, but they share one move. Find the local
rule $f(p^a)$, and the rest is bookkeeping in one of a handful of shapes.

## The idea: a function is its prime powers

By the [fundamental theorem of arithmetic](/topics/domain/fundamental-theorem-of-arithmetic),
$n = p_1^{a_1} \cdots p_k^{a_k}$ splits into pairwise coprime prime powers, so a multiplicative
$f$ satisfies

$$f(n) = \prod_{i} f\!\left(p_i^{a_i}\right).$$

Writing down $f(p^a)$ is the whole specification. The functions that recur here:

| function | $f(p^a)$ | where it shows up |
| --- | --- | --- |
| number of divisors $d(n)$ | $a + 1$ | 12, 108, 110, 501 |
| divisor sum $\sigma_k(n)$ | $1 + p^k + \dots + p^{ak}$ | 211, 241, 565 |
| [Euler's totient](/topics/domain/eulers-totient-function) $\varphi(n)$ | $p^{a-1}(p - 1)$ | 72, 243, 248, 342, 432 |
| [Möbius](/topics/domain/mobius-function) $\mu(n)$ | $-1$ if $a = 1$, else $0$ | 464, 633, 745 |
| [radical](/topics/domain/radical-of-an-integer) $\operatorname{rad}(n)$ | $p$ | 124, 127 |
| $2^{\omega(n)}$ (squarefree divisors) | $2$ | 675 |
| [unitary](/topics/domain/unitary-divisor) square sum | $1 + p^{2a}$ | 429 |

Two cautions belong right next to the definition. First, the coprimality condition is not
decoration: $d(4) = 3$ but $d(2)^2 = 4$. Only a *completely* multiplicative function ($n$, $n^k$,
the [Liouville function](https://en.wikipedia.org/wiki/Liouville_function)) ignores it, and almost
nothing on this list is one. Second, the problems often invent a function and leave you to discover
that it is multiplicative. Problem 484's $\gcd(k, k')$, the gcd of $k$ and its
[arithmetic derivative](/topics/domain/arithmetic-derivative), looks hopeless until a
[$p$-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation) argument, one prime at a
time, shows that each prime contributes $p^{a-1}$, or $p^a$ when $p \mid a$. Once you have shown that,
the problem is the same kind as the others. Problem 429's unitary divisors are the same story: a
unitary divisor takes each prime power whole or not at all, so the sum of their squares is
$\prod(1 + p^{2a})$.

## Three shapes of computation

What you do with the local rule depends on how many values the problem needs.

**One value: factor, then multiply.** For a single $n$, or a handful,
[factor](/topics/technique/prime-factorization-application) it and multiply the local factors.
Problem 12 needs $d(T)$ for triangular numbers $T = n(n+1)/2$, and its fast solution uses
multiplicativity before any factoring: $n$ and $n+1$ are coprime, so after the $2$ is folded into
whichever is even, $d(T)$ is the product of two divisor counts on numbers half the size.

```python
# p0012: T(i) = (i/2) * (i+1) or i * ((i+1)/2), and the two factors are coprime
d_T = num_factors(i // 2) * num_factors(i + 1) if i % 2 == 0 else num_factors(i) * num_factors((i + 1) // 2)
```

Problem 429 never factors anything. The exponents of a factorial come from
[Legendre's formula](/topics/domain/legendres-formula), so $\prod_p (1 + p^{2e_p})$ over the primes up
to $10^8$ is a sieve plus one modular power per prime.

**Every value up to $N$: sieve it.** When the problem needs $f(1), \dots, f(N)$, put the local rule
into a sieve. The [Eratosthenes](/topics/technique/sieve-of-eratosthenes)-style form lets each prime
apply its factor to its multiples. Problem 72 sums $\varphi(2..N)$ this way, and the whole totient
is two lines:

```python
# p0072: a cell still equal to its index is prime; it applies (p-1)/p to every multiple
if phi[n] == n:
    for j in range(n, N + 1, n):
        phi[j] = phi[j] // n * (n - 1)
```

Additive divisor functions such as $\sigma_2$ in problem 211 suit a
[divisor-sum sieve](/topics/technique/divisor-sum-sieve) better: add $d^2$ to every multiple of $d$,
$O(N \log N)$ total. A [linear sieve](/topics/technique/linear-sieve) visits each composite exactly
once through its smallest prime factor and works for any multiplicative $f$. The catch is the case
where the sieving prime $p$ already divides $i$: then $i \cdot p$ and $p$ are *not* coprime, and
$f(ip) \ne f(i)f(p)$. Problem 745 handles it by tracking the full $p$-power block of each index and
multiplying $f(p^a)$ into the coprime cofactor. That branch is where linear-sieve bugs live.

**The sum up to a huge $N$: convolve.** When $N$ is $10^{11}$ or $10^{15}$ you cannot touch each $n$,
and the summatory function $F(N) = \sum_{n \le N} f(n)$ has to come from structure. The tool is
[Dirichlet convolution](/topics/domain/dirichlet-convolution),
$(g * h)(n) = \sum_{d \mid n} g(d)\,h(n/d)$, which turns multiplicative functions into multiplicative
functions. Write $f = g * h$ with $g$ easy to sum, and

$$\sum_{n \le N} f(n) = \sum_{d \le N} h(d)\, G\!\left(\lfloor N/d \rfloor\right).$$

The work depends on how sparse $h$ is. In problem 745, $h = \mu * \mathrm{id}^2$ lives on squares, so
the sum is $\sum_{m \le \sqrt N} h(m) \lfloor N/m^2 \rfloor$, which is $10^7$ terms instead of $10^{14}$.
In problem 484, $g(p) = 1$ forces $h(p) = 0$, so $h$ is supported on
[powerful numbers](https://en.wikipedia.org/wiki/Powerful_number). There are only
$\Theta(\sqrt N)$ of them, and a [depth-first search](/topics/technique/depth-first-search) over
prime exponents $\ge 2$ visits each one once. This is the "powerful number trick", and it fits any
$f$ that agrees with a simple function on the primes. When $h$ is not sparse, the
[Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method) splits the sum at
$\sqrt N$, and
[Möbius inversion](/topics/technique/mobius-inversion-formula) with a
[totient summatory recursion](/topics/technique/totient-summatory-recursion) gets $\sum \varphi$ in
about $O(N^{2/3})$ (problems 432 and 448). The fully general tool is the
[Min_25 sieve](/topics/technique/min-25-sieve), which is what problem 639 is named for.

## Running it backwards: search over exponent signatures

Sometimes the problem gives $f(n)$ and asks for $n$. Multiplicativity turns that into a search over
prime-power factorisations, and the local rule tells you how to prune it.

Problems 108 and 110 reduce, through
[Simon's factoring trick](https://artofproblemsolving.com/wiki/index.php/Simon%27s_Favorite_Factoring_Trick),
to the smallest $n$ with $d(n^2) = \prod (2a_i + 1)$ above a target. Since $d$ depends only on the
multiset of exponents, the cheapest $n$ for a given signature puts the largest exponent on the
smallest prime. That means a DFS over $2, 3, 5, \dots$ with non-increasing exponents, which is the
same argument that defines a [highly composite number](/topics/domain/highly-composite-number).
Problem 248 inverts the totient: $\varphi(n) = 13!$ means each prime power $p^a \| n$ contributes
$p^{a-1}(p-1)$, which must divide what is left of the target. So the candidate primes are exactly the
$p$ with $p - 1 \mid 13!$, and the DFS divides the remaining target down as it goes.

## Local to global beyond arithmetic functions

The same idea applies to counts modulo $n$. By the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem), $\mathbb{Z}/n$ splits into
the product of $\mathbb{Z}/p^a$. So the number of solutions of a polynomial congruence mod $n$ is
multiplicative in $n$: count the cube roots of unity mod each prime power and multiply (problem 271),
or the solutions of a four-variable congruence (problem 875). The
[Pisano period](/topics/domain/pisano-period) of problem 853 combines the same way, except the prime-power
periods meet in an $\operatorname{lcm}$ instead of a product.

## How to reason about it

- **Test for multiplicativity early.** If the quantity is defined through divisors, gcds, or
  solutions mod $n$, ask whether it splits over coprime factors. If it does, the problem gets much
  smaller. Check it numerically on small coprime pairs before building on it.
- **Derive $f(p^a)$ and verify it.** The local rule is the entire specification, so a wrong
  exponent case silently corrupts everything. Compare the product formula against brute force for
  $n \le 1000$. The $p \mid a$ case in problem 484 and the $a = 1$ versus $a \ge 2$ split of $\mu$
  are where errors hide.
- **Choose the shape from $N$.** One value: factor. All values to $10^7$–$10^8$: sieve, inside
  `solve()`, sized to the input ([size the work to the input](/topics/takeaway/size-work-to-the-input)).
  A sum to $10^{12}$ and beyond: find a convolution $f = g * h$ with sparse $h$, or a sublinear
  summatory method.
- **Respect the coprimality condition in sieves.** A linear sieve's "$p$ divides $i$" branch and a
  coprime split that forgets the shared factor of $2$ are the same bug: multiplying across a shared
  prime.
- **Search signatures, not numbers.** When $f(n)$ is given and $n$ is wanted, enumerate exponent
  patterns over small primes with monotone exponents, and prune with the local rule.
- **Watch the width.** $\sigma_2(n)$ reaches $1.6\,n^2$, convolution sums approach
  $N \log N$, and products of local factors mod $10^9+7$ need a 128-bit intermediate in C
  ([watch integer width](/topics/takeaway/watch-integer-width)).

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
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
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
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ● [0745](/solutions/0745/) — Sum of Squares II
- ○ [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ○ [0875](/solutions/0875/) — Quadruple Congruence

<!-- /problems -->
