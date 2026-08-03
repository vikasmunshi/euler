<!-- tags: [eulers-totient-function] -->
<!-- status: final -->
# Euler's totient function

[Euler's totient function](https://en.wikipedia.org/wiki/Euler%27s_totient_function) $\varphi(n)$
counts the integers in $[1, n]$ that are [coprime](/topics/domain/coprime-integers) to $n$ ([OEIS
A000010](https://oeis.org/A000010)). That one-line definition undersells it. $\varphi$ is the size
of the multiplicative group $(\mathbb{Z}/n\mathbb{Z})^\times$, the count of reduced fractions with
denominator $n$, the number of lattice directions a grid of size $n$ can point in, and the
exponent that makes powers repeat modulo $n$ — so it turns up in problems about fractions,
geometry, cryptography and towers of exponents that share no vocabulary at all. It earns a
*domain* page rather than a formula footnote because the hard part is almost never computing
$\varphi$; it is recognising that the quantity you are counting *is* $\varphi$, and then deciding
which of its several faces you need.

## The idea

Everything comes out of one closed form. $\varphi$ is
[multiplicative](/topics/domain/multiplicative-function) — $\varphi(ab) = \varphi(a)\varphi(b)$
when $\gcd(a,b) = 1$ — and on a prime power $\varphi(p^a) = p^{a-1}(p-1)$. Multiply those together
over the factorisation of $n$:

$$\varphi(n) = n \prod_{p \mid n} \left(1 - \frac{1}{p}\right)
            = \prod_{i} p_i^{a_i - 1}(p_i - 1).$$

The left form is the one to internalise, because of what is *missing* from it: the exponents. The
ratio $\varphi(n)/n$ depends only on the **set** of distinct primes dividing $n$ — its
[radical](https://en.wikipedia.org/wiki/Radical_of_an_integer) — not on their multiplicities.
Every extremal question about that ratio therefore collapses into a question about which primes to
include, and since $\frac{n}{\varphi(n)} = \prod_{p \mid n} \frac{p}{p-1}$ is a product of factors
that shrink towards $1$ as $p$ grows, the cheapest way to push the ratio up is always to take the
smallest primes, once each — a [primorial](/topics/technique/primorial). Problem 69 is that
observation and nothing else; problem 243 is the same observation with a threshold attached, and
problem 70 is its mirror image (minimise the ratio, so use as few and as large primes as possible
— a semiprime $pq$ near $\sqrt{n}$).

Two identities do most of the remaining work:

$$\sum_{d \mid n} \varphi(d) = n, \qquad \varphi = \mu * \mathrm{id},
  \quad\text{i.e.}\quad \varphi(n) = \sum_{d \mid n} \mu(d)\,\frac{n}{d}.$$

The first says the integers $1..n$ partition by their $\gcd$ with $n$: each $d \mid n$ contributes
the $\varphi(n/d)$ values whose gcd is exactly $d$. That partition is why gcd- and lcm-flavoured
sums keep resolving into $\varphi$ — problem 625 sums $\gcd(i,j)$ and lands on
$\sum_{d \mid n} d\,\varphi(n/d)$; problem 448 does the same for $\operatorname{lcm}$. The second
is the [Möbius](/topics/domain/mobius-function) view: $\varphi$ is inclusion–exclusion over the
primes dividing $n$, which is exactly what "coprime to $n$" means. It also makes $\varphi$ a
[Dirichlet convolution](/topics/domain/dirichlet-convolution) of two simple functions, which is
what the heavy summatory machinery below actually consumes.

## Computing it

**A table up to $N$**: seed $\varphi[d] = d$ and apply each prime's factor to its multiples — a
[sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) that multiplies instead of
striking. From the public problem 72:

```python
euler_totients = list(range(max_d + 1))
for n in range(2, max_d + 1):
    if euler_totients[n] == n:              # untouched cell ⇒ n is prime
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
```

The trick worth stealing is the primality test: a cell still equal to its index has had no prime
factor applied, so it is prime. The integer division comes *first* so the arithmetic stays exact.
Cost is $O(N \log \log N)$; a [linear sieve](/topics/technique/linear-sieve) gets $O(N)$ if the
$\log \log$ matters. This is the right tool up to roughly $10^8$ cells, and it is what problems 72,
214 and 337 are built on.

**A single $\varphi(n)$** needs a factorisation, so it costs whatever factoring costs — fine for
one number, hopeless for $10^{11}$ of them.

**The summatory $\Phi(N) = \sum_{n \le N} \varphi(n)$ past sieve range** is the recurring wall.
Sum the first identity over $n \le N$ and it inverts into

$$\Phi(N) = \frac{N(N+1)}{2} - \sum_{q = 2}^{N} \Phi\!\left(\left\lfloor N/q \right\rfloor\right),$$

which, with [quotient blocking](/topics/technique/quotient-blocking) (only $O(\sqrt N)$ distinct
values of $\lfloor N/q \rfloor$ exist) plus a sieved base case and memoisation, evaluates in about
$O(N^{2/3})$. That is the standard escape for problems 432, 512 and 931, and the same skeleton as
the [Meissel–Lehmer](/topics/domain/meissel-lehmer-algorithm) prime count. When the summand is a
messier multiplicative function than $\varphi$ itself, the generalisation is the
[Min-25 sieve](/topics/technique/min-25-sieve) or the
[Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method).

## How a problem reaches it

Three routes, and it is worth learning to recognise which one you are on.

**Counting coprime things.** The statement is about reduced fractions, visible lattice points, or
directions — problems 72, 243, 245, 351, 228, 441. Nothing here needs group theory; you need the
closed form and a fast table. The tell is a $\gcd(\cdot,\cdot) = 1$ condition, explicit or
disguised: problem 351 hides it as "hidden from the centre" (a lattice point $(x,y)$ is visible
exactly when $\gcd(x,y) = 1$), and problem 228 hides it as "distinct edge directions" of a
[Minkowski sum](https://en.wikipedia.org/wiki/Minkowski_addition), a direction $p/q$ in lowest
terms being contributed by exactly the $\varphi(q)$ choices of $p$.

**Order of the multiplicative group.** Here $\varphi$ is not being counted, it is being used as an
exponent. [Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem) gives
$a^{\varphi(m)} \equiv 1 \pmod m$ for $\gcd(a, m) = 1$, and the generalised (lifting) form

$$a^{x} \equiv a^{(x \bmod \varphi(m)) + \varphi(m)} \pmod m \qquad (x \ge \log_2 m)$$

drops the coprimality requirement, which is what lets problem 188 peel a
[tetration](https://en.wikipedia.org/wiki/Tetration) tower one level at a time under a descending
chain of moduli $m, \varphi(m), \varphi(\varphi(m)), \dots$ — a chain that reaches $1$ in
$O(\log m)$ steps, so the astronomically tall tower has only a handful of *effective* levels.
Problem 182 uses the same group in RSA's clothing, counting unconcealed messages via
$\gcd(e-1, p-1)$ over each prime factor. The caveat this family teaches: $\varphi(m)$ is a
multiple of the true group exponent, the [Carmichael
function](/topics/technique/carmichael-function) $\lambda(m)$, not necessarily equal to it —
harmless when you only need *some* period, fatal when the problem asks for the smallest
(problem 533).

**$\varphi$ as the object of study.** The statement asks about $\varphi$'s own behaviour: iterate
it (problem 214 — $\varphi(n) < n$ always, so the chain descends to $1$, and chain length is a
[dynamic-programming](/topics/technique/dynamic-programming) table over the sieve, with
$L(p) = 1 + L(p-1)$ for primes), invert it (problem 248 — solve $\varphi(n) = 13!$ by searching
over *factorisations of the target* into factors $p^{a-1}(p-1)$ rather than over candidate $n$),
or constrain its value's shape (problems 342, 302 and 516 want $\varphi(n)$ to be a cube, an
Achilles number, or [5-smooth](/topics/domain/smooth-number)). These are the hardest of the three,
because the sieve gives you no leverage: the search space is the *structure* of the factorisation,
and the algorithm is usually a recursive walk over prime choices with hard pruning.

## How to reason about it

- **Look for $\varphi$ before you look for a sieve.** Most of these problems are a two-step: an
  awkward count collapses to $\sum \varphi$ or $\sum_{d \mid n} \varphi(d)$, and only then does the
  computational question begin. Getting the collapse wrong is far more expensive than getting the
  sieve slow.
- **Exponents are invisible to $\varphi(n)/n$, and that cuts both ways.** It makes extremal
  searches tiny (only the radical matters, so candidates are primorial multiples), and it makes
  $\varphi$ badly non-injective — many $n$ share a totient, which is exactly why inverting it is
  a search rather than a formula.
- **Multiplicative, not completely multiplicative.** $\varphi(2)\varphi(2) = 1 \ne \varphi(4) = 2$.
  Every convolution identity you use needs its coprimality hypothesis checked; the prime-power case
  must be handled separately in any recursive build.
- **Know your ceiling before you write the sieve.** A `list` of $10^7$ totients is comfortable;
  $10^{11}$ is not, and the moment the bound crosses about $10^8$ the answer is a quotient-blocked
  recurrence or a structural search, never a bigger array. Problems 245, 432 and 448 all fail on
  this point first.
- **A modulus in the question does not license a modulus in the middle.** When a problem asks for
  $\Phi(N) \bmod m$, reduce only the final additive accumulation. $\varphi$ itself is defined by
  divisibility and factorisation, and comparisons, divisions and gcds inside the derivation are all
  invalid on residues.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0243](/solutions/0243/) — Resilience
- ● [0245](/solutions/0245/) — Coresilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ○ [0302](/solutions/0302/) — Strong Achilles Numbers
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ○ [0351](/solutions/0351/) — Hexagonal Orchards
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ● [0478](/solutions/0478/) — Mixtures
- ○ [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0516](/solutions/0516/) — $5$-smooth Totients
- ○ [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0625](/solutions/0625/) — Gcd Sum
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ○ [0931](/solutions/0931/) — Totient Graph

<!-- /problems -->
