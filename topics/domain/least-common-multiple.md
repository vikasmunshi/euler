<!-- tags: [least-common-multiple] -->
<!-- status: final -->
# Least common multiple

The [least common multiple](https://en.wikipedia.org/wiki/Least_common_multiple)
$\operatorname{lcm}(a_1, \dots, a_n)$ is the smallest positive integer every $a_i$ divides. The
[gcd page](/topics/technique/greatest-common-divisor-application) covers the identity
$\operatorname{lcm}(a, b) = ab / \gcd(a, b)$ and the lcm's role as a stride and as the realignment
period of two cycles. This page treats the lcm as the *object*. It is the answer to "smallest
number divisible by all of these", a common denominator, the exponent-wise maximum of
factorisations, and a number that grows exponentially in the size of its range. Of those, the
last two decide how the problems below compute it.

## Two ways to compute it

Factor each $a_i = \prod_p p^{e_{i,p}}$. Then

$$\operatorname{lcm}(a_1, \dots, a_n) = \prod_p p^{\max_i e_{i,p}}, \qquad
\gcd(a_1, \dots, a_n) = \prod_p p^{\min_i e_{i,p}}.$$

The lcm keeps the *largest* exponent of each prime. That gives two algorithms:

| form | how | needs | used in |
| --- | --- | --- | --- |
| **pairwise fold** | `acc = acc // gcd(acc, a) * a` over the list | exact division, so exact integers | 5, 545, 152 (Python) |
| **max exponent** | track $\max e_p$ per prime, multiply the prime powers | the factorisations, or a prime list | 772, 152 (C) |

The fold is the natural default when the numbers are given and the result fits, or when the
language has big integers. Python has `math.lcm(*xs)`, variadic since 3.9, which is what 152 uses
for its common denominator. The max-exponent form wins in two situations.

**Under a modulus.** Problem 772 shows that every $k$-bounded partition of $N$ is balanceable
exactly when $N/2$ is a multiple of $1, \dots, k$, so $f(k) = 2 \cdot \operatorname{lcm}(1, \dots, k)$.
For $k = 10^8$ the lcm has about $4 \times 10^7$ digits and is wanted modulo a prime. The fold
cannot run there: dividing by $\gcd(\text{acc}, a)$ needs the true accumulator, not its residue.
The prime-power form needs no division:

$$\operatorname{lcm}(1, \dots, k) = \prod_{p \le k} p^{\lfloor \log_p k \rfloor}.$$

Only primes up to $\sqrt k$ have exponent above 1, so the solution handles those 1229 primes with a
short power loop and multiplies the other 5.76 million in once each. The whole cost is a sieve and
one modular product. **When a result is wanted modulo $m$, write the lcm as a product of prime
powers.**

**Without big integers.** Problem 152 turns $\sum 1/k^2$ into an integer sum over the common
denominator $D = \operatorname{lcm}\{k^2\}$. The Python writes `lcm(*[k * k for k in involved])`.
The C has no big integers, so it records, for each prime, the maximum exponent over the involved
$k$ and doubles it for the square. It builds $D$ once from prime powers in a fixed 384-bit integer.
Problem 5 (public) takes the other route in C. It folds pairwise into a small limb-array bignum and
avoids a big-integer gcd by reducing first, $\gcd(\text{acc}, y) = \gcd(\text{acc} \bmod y, y)$.
That is one bignum-by-word remainder per step.

## How big it gets

$\operatorname{lcm}(1, \dots, n) = e^{\psi(n)}$, where $\psi$ is the
[second Chebyshev function](https://en.wikipedia.org/wiki/Chebyshev_function), and the prime
number theorem gives $\psi(n) \sim n$. So the lcm of the first $n$ integers grows like $e^n$:

| $n$ | $\operatorname{lcm}(1, \dots, n)$ |
| --- | --- |
| 20 | 232792560, fits 32 bits |
| 47 | first exceeds $2^{64}$ |
| 100 | about $7 \times 10^{40}$ |
| $10^8$ | about $10^{4.3 \times 10^7}$ |

That table predicts the implementation. Problem 5's main case fits a machine word, but its extra
cases (up to 100) force the C into a bignum. 152's denominator over squares up to 80 is at most
$\operatorname{lcm}(1..80)^2$, about 230 bits, which the C's 384-bit fixed type holds with room
left for the sums. 772 can only be done modularly. Before writing an lcm
loop in C, estimate $\psi$ of the range: $n \log_2 e \approx 1.44n$ bits.

## The lcm as a constraint

The other half of these problems uses the lcm as a *condition* rather than as a number to output.
"$k$ is divisible by every element of $R$" is the same as "$k$ is a multiple of
$\operatorname{lcm}(R)$". Problem 545 needs every $k$ whose Bernoulli denominator is a given
squarefree number. By von Staudt–Clausen, $k$ must be divisible by $p - 1$ for each prime $p$ in
that number. So the search runs over $k = \operatorname{lcm}(R) \cdot t$. That shrinks the scan
by the stride, and the membership check for $R$ becomes unnecessary, since the stride already
guarantees it. 772 is the same move in its proof: the uniform partition into copies of $d$
misses the target exactly when $d \nmid T$, so "every $d \le k$ divides $T$" is the condition, and
the smallest such $T$ is an lcm.

The open problems on this tag count *pairs and sets by their lcm*: 379 counts pairs with
$\operatorname{lcm}(x, y) = n$, 590 counts sets with a given lcm, 448 averages $\operatorname{lcm}(n, i)$,
858 sums the lcm over every subset of $\{1, \dots, N\}$, and 483 is about the order of a
permutation, which is the lcm of its cycle lengths. All of these factor over primes, because lcm and gcd are max and min on
each exponent separately. That makes the counts multiplicative.

## C and Python

- **Big results.** Python folds with `math.lcm` or `x * y // gcd(x, y)` and lets integers grow. C
  either writes a fixed-width or limb-array bignum (5, 152) or works modulo a prime (772, where
  $m < 1.1 \times 10^9$ keeps each product of two residues below $2^{64}$, so no `__int128` is
  needed).
- **Fold order in C.** 545 computes `a / gcd(a, b) * b`, dividing *before* multiplying, which
  keeps the intermediate at the size of the result instead of $a \cdot b$. Python writes the
  textbook `a * b // gcd(a, b)`, since its integers do not overflow.
- **Prime lists.** 772's Python gets primes from `primesieve.numpy` and finds the $\sqrt k$ boundary
  with `searchsorted`. The C sieves itself into a bit array, 12.5 MB for $10^8$ instead of 100 MB as
  bytes.

## How to reason about it

- **"Divisible by all of them" means a multiple of the lcm.** Iterate over multiples of it, or take
  the smallest one.
- **Estimate the size first.** $\operatorname{lcm}(1..n) \approx e^n$. From $n = 47$ on it no
  longer fits 64 bits.
- **Under a modulus, use prime powers.** The gcd fold needs the true value. The exponent-max form
  needs only multiplication.
- **A common denominator is an lcm.** It turns rational sums into exact integer sums, and its size
  tells you what integer type the sum needs.
- **Counting by lcm factors over primes.** Max of exponents per prime makes lcm-indexed counts
  multiplicative.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ○ [0350](/solutions/0350/) — Constraining the Least Greatest and the Greatest Least
- ○ [0379](/solutions/0379/) — Least Common Multiple Count
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ○ [0483](/solutions/0483/) — Repeated Permutation
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ○ [0590](/solutions/0590/) — Sets with a Given Least Common Multiple
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0858](/solutions/0858/) — LCM

<!-- /problems -->
