<!-- tags: [modular-multiplicative-inverse] -->
<!-- status: final -->
# Modular multiplicative inverse

The [modular multiplicative inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
of $a$ modulo $m$ is the residue $a^{-1}$ with $a \cdot a^{-1} \equiv 1 \pmod m$. It exists exactly
when $\gcd(a, m) = 1$. How to *use* one is covered on
[modular multiplicative inverse (application)](/topics/technique/modular-multiplicative-inverse-application):
solving linear congruences, gluing CRT residues, dividing exactly under a modulus, and making
inverses cheap in bulk. That page also covers the solved problems here in detail. This page is
about the problems where the inverse is the *subject*: the statement asks about inverses, or the
answer turns out to be one. Seen that way, three structural facts recur: inversion is a pairing,
an inverse relation is symmetric, and a fixed rational number has a residue modulo every prime that
does not divide its denominator.

## Inversion is a pairing

On the units modulo $m$, the map $a \mapsto a^{-1}$ is an
[involution](https://en.wikipedia.org/wiki/Involution_(mathematics)): applying it twice gives back
$a$. So it splits the units into pairs $\{a, a^{-1}\}$, plus the **self-inverse** elements, those
with $a^2 \equiv 1$. Two consequences follow:

- **Wilson's theorem.** Modulo a prime $p$, the only self-inverse elements are $\pm 1$, since
  $a^2 - 1 = (a - 1)(a + 1)$ and a field has no zero divisors. In $(p - 1)!$ every other factor
  cancels against its partner, leaving $1 \cdot (-1)$. That is
  [Wilson's theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem), $(p - 1)! \equiv -1$, and it
  is the starting point of problem 381. Peeling factors off the top, $(p - 1) \equiv -1$,
  $(p - 2) \equiv -2$, and so on, writes each $(p - k)!$ as an inverse:
  $(p - 3)! \equiv (-2)^{-1}$, $(p - 4)! \equiv 6^{-1}$, $(p - 5)! \equiv (-24)^{-1}$. A sum of huge
  factorials becomes a sum of small inverses.
- **Composite moduli have more fixed points.** Modulo $n = \prod p_i^{e_i}$, the solutions of
  $a^2 \equiv 1$ combine by the [CRT](/topics/technique/chinese-remainder-theorem): $\pm 1$ modulo
  each odd prime power gives $2^{\omega}$ of them, with more from a factor of 8. Problem 451 asks
  for the largest self-inverse $m < n - 1$ for every $n$ up to $2 \times 10^7$. The $\pm 1$ are the
  trivial ones, so the question is about this composite-only structure. In $\mathbb{Z}/15$, for
  example, 4 and 11 are self-inverse.

## An inverse relation is symmetric

$ab \equiv 1 \pmod m$ is symmetric in $a$ and $b$, and
[Bézout's identity](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity) $bx - ay = 1$ is
symmetric across both moduli. Reduce it modulo $b$ and $-ay \equiv 1$. Reduce it modulo $y$ and
$bx \equiv 1$. One integer equation is a pair of inverse statements.

Problem 198 is built on this. Two fractions $a/b < c/d$ are
[Farey neighbours](https://en.wikipedia.org/wiki/Farey_sequence) when $bc - ad = 1$. Fix the
smaller-denominator fraction and the partner's denominator is pinned to one residue class,
$d \equiv -a^{-1} \pmod b$ or $b \equiv c^{-1} \pmod d$. Counting neighbour pairs whose midpoint is
small enough becomes counting an arithmetic progression in an interval, which takes $O(1)$ per
fraction. Problem 784, which is still open here, states the symmetry outright: $(p, q)$ is a
*reciprocal pair* if one $r < p$ is both $p^{-1} \bmod q$ and $q^{-1} \bmod p$. Bézout says when
that can happen.

Problem 134 is the asymmetric case. $n$ ends in the digits of $p_1$ and is divisible by $p_2$, so
$n = p_1 + 10^d k$ and $k \equiv -p_1 \cdot (10^d)^{-1} \pmod{p_2}$. The inverse of a power of ten
is what turns "these are its last digits" into arithmetic. The statement excludes the one pair
$(3, 5)$ because 5 divides $10^d$, so the inverse does not exist there.

## A rational number lives modulo every prime

A fraction $u/v$ with $p \nmid v$ has a residue $u \cdot v^{-1} \bmod p$. Reduction is a ring
homomorphism, so sums and products of fractions map to sums and products of residues. You can
therefore **do the algebra in $\mathbb{Q}$ and reduce once**.

381 shows this. The five inverses above sum, as rationals, to
$-1 + 1 - \tfrac12 + \tfrac16 - \tfrac1{24} = -\tfrac38$, so $S(p) \equiv -3 \cdot 8^{-1}$ for
*every* prime $p \ge 5$. That is one rational number evaluated modulo millions of primes. Problem
274 is the same idea with a different constant: its "divisibility multiplier" is
$10^{-1} \bmod p$ itself. In both cases the denominator is a small constant and the modulus
varies, so the residue has an integer formula:

$$c^{-1} \bmod p = \frac{t p + 1}{c}, \qquad t \equiv -p^{-1} \pmod c,$$

so $t$ depends only on $p \bmod c$. 274 tabulates $t$ by $p$'s last digit and 381 by $p \bmod 8$.
Neither runs an extended Euclid per prime. The
[application page](/topics/technique/modular-multiplicative-inverse-application) shows the
vectorised form.

Two open problems use the same representation. 624 reports a probability as
$Q(a/b, p)$, the residue of the reduced fraction, which is how Project Euler asks for an exact
rational too large to print. 515 iterates prefix sums of the inverses $1^{-1}, 2^{-1}, \dots$
modulo a prime, which are harmonic-number partial sums evaluated in $\mathbb{F}_p$.

## C and Python

The solved problems need only one inverse each, or none at all, so the language difference lies in
how that inverse is spelled:

- **The inverse itself.** Python writes `pow(a, -1, m)` (134, 198), which raises `ValueError` if
  no inverse exists. The C writes a short extended Euclid, returning the Bézout coefficient
  normalised into $[0, m)$.
- **Signs.** 134's C normalises $-p_1$ with `((-(long long)p1 % p2) + p2) % p2` before multiplying.
  198's C adds a floor-division helper for its progression count, because `/` truncates toward
  zero and a negative numerator would otherwise be off by one. Python's `%` and `//` floor, so they
  need neither.
- **No inverse at all.** 274 and 381 replace the inverse with a table lookup and an exact
  division by a constant. The Python vectorises it over the sieve's NumPy array of primes
  (`(t_for_residue[primes % 8] * primes - 3) // 8`). The C runs the same expression in a loop over primesieve's output.
  Both are dominated by the sieve.

## How to reason about it

- **Pair inverses to collapse products.** A product over all units, or over a symmetric range,
  cancels in pairs. What is left is the self-inverse elements, $\pm 1$ modulo a prime.
- **Self-inverse means $a^2 \equiv 1$.** Modulo a prime that is just $\pm 1$. Modulo a composite,
  combine $\pm 1$ per prime power by CRT.
- **Read Bézout both ways.** One equation $bx - ay = 1$ gives an inverse modulo $b$ and another
  modulo $y$. Fixing the smaller side turns the other into a residue class.
- **Do the fraction first, reduce last.** If the expression is a fixed rational for every prime,
  compute it exactly in $\mathbb{Q}$ and reduce once per prime.
- **A small constant's inverse has a formula.** $(tp + 1)/c$, with $t$ looked up from $p \bmod c$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ○ [0451](/solutions/0451/) — Modular Inverses
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0784](/solutions/0784/) — Reciprocal Pairs

<!-- /problems -->
