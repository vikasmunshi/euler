<!-- tags: [modular-arithmetic, modular-multiplicative-inverse, modular-arithmetic-application, modular-exponentiation, modular-multiplicative-inverse-application] -->
<!-- status: final -->
# Modular Arithmetic

[Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) is the arithmetic of
remainders: instead of tracking a number's full value, you track only what is left after dividing
by a fixed **modulus** $m$. It is the single most useful trick in the Euler toolbox, because a
huge fraction of problems ask a question that only depends on a remainder — *the last ten digits
of a number*, *is this divisible by that*, *how many arrangements up to a symmetry* — and the full
value is astronomically large while its residue fits in a machine word. Learn to spot when a
problem is secretly modular, and a computation with millions of digits collapses to one that never
leaves the range $[0, m)$.

## The arithmetic of remainders

Two integers are [**congruent**](https://en.wikipedia.org/wiki/Modular_arithmetic) modulo $m$,
written $a \equiv b \pmod m$, when they leave the same remainder on division by $m$ — equivalently,
when $m$ divides $a - b$. The reason this is *arithmetic* and not just notation is that congruence
is preserved by addition, subtraction, and multiplication:

$$(a + b) \bmod m = ((a \bmod m) + (b \bmod m)) \bmod m,$$

and the same for $a - b$ and $a \times b$. So you may reduce at every step and never let an
intermediate value grow. That single closure property is what powers the classic reframe: "the last
$k$ decimal digits of $N$" is exactly $N \bmod 10^k$. Problem 97 asks for the last ten digits of
$28433 \times 2^{7830457} + 1$ — a number with over two million digits — but working modulo
$10^{10}$ throughout, it never handles anything bigger than $10^{20}$. Problem 19 (public,
`solutions/public/p0019/`) is the same idea wearing a calendar: the day of the week is a residue
modulo 7, so counting how often the first of a month is a Sunday is pure arithmetic mod 7, no date
library required.

The same closure makes huge **counts** cheap. Problems 249 and 250 count subsets of a set — $2^{669}$
and $2^{250250}$ of them — by a property of their sum, and ask only for the last sixteen digits. A
subset-sum dynamic programme only ever adds and multiplies counts, so every table entry can live
modulo $10^{16}$ from the first step. Problem 250 goes one level further: "the sum is divisible by
250" depends only on each element's residue, so the $250250$ elements collapse to a census of how
many land on each residue mod 250, and the generating function is multiplied out in
$\mathbb{Z}[x]/(x^{250} - 1)$ — a ring where $x^{250} = 1$, so the *exponents* wrap modulo 250 on
their own. Reducing both the coefficients and the exponents keeps the whole computation to a
250-slot array.

Residues can also be taken twice, of two different things. Problem 706 asks how many $10^5$-digit
numbers have a count of substrings divisible by 3 that is itself divisible by 3. A substring is
divisible by 3 exactly when the digit prefix sums at its two ends agree mod 3. So the count is
$\sum_r \binom{c_r}{2}$ over the numbers $c_r$ of prefixes in each residue class $r$. Only that count
mod 3 matters, so the $c_r$ can be kept mod 3 as well. The state shrinks to 81 values, small enough
for a [transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) raised to the
$10^5$th power.

The catch is that congruence is preserved by $+$, $-$, and $\times$ **but not by division** — and
not, in general, by exponentiation done naively. Those two operations are what most of this page is
about.

## Exponentiation: square-and-multiply

Computing $a^b \bmod m$ by multiplying $a$ into a running product $b$ times is $O(b)$, and $b$ is
often the very thing that is astronomically large ($b = 7830457$ in problem 97; $b = i$ up to $1000$
per term in problem 48). [**Modular exponentiation**](https://en.wikipedia.org/wiki/Modular_exponentiation)
via [exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) reads the
exponent's binary digits instead: repeatedly square the base, and fold it into the result only where
a bit of $b$ is set. That computes the power in $O(\log b)$ multiplications — about 23 instead of 7.8
million for problem 97, and about 60 for exponents near $10^{18}$, the size of the hook-length
multiplicities that problem 1010 raises its factors to.

In Python you almost never write the loop yourself; the built-in three-argument `pow` does the
reduction *inside* the squaring loop, so the full power is never materialised. Problem 48 (public,
`solutions/public/p0048/`) — the sum $1^1 + 2^2 + \dots + 1000^{1000}$ modulo $10^{10}$ — is three
lines because of it:

```python
result = 0
for i in range(1, limit + 1):
    result = (result + pow(i, i, modulo)) % modulo   # note: pow(i, i, modulo), not pow(i, i) % modulo
```

The parenthetical matters: `pow(i, i) % modulo` first builds the multi-thousand-digit power and only
then reduces, throwing away the entire benefit. Two further levers keep the *exponent* itself small.
By [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), if $p$ is
prime and $\gcd(a, p) = 1$ then $a^{p-1} \equiv 1 \pmod p$, so exponents may be reduced modulo
$p - 1$; its generalisation, [Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem),
does the same modulo any $m$ using [Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function)
$\varphi(m)$. That is how "tower of powers" problems (188's hyperexponentiation) stay finite: you
reduce each exponent modulo the totient of the modulus one level up.

The sharper version of that lever is the [Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function)
$\lambda(m)$, the smallest exponent that sends *every* unit to 1, and it turns "exponents repeat" into
"the whole sequence repeats". Problem 250's elements are $k^k$ for $k \le 250250$. Split
$250 = 2 \cdot 5^3$: the residue mod 2 depends only on the parity of $k$, and mod 125 neither the
base ($500 \equiv 0$) nor the exponent ($\lambda(125) = 100$ divides $500$) changes under
$k \mapsto k + 500$. So $k^k \bmod 250$ is periodic with period 500 (from $k = 3$ on), and one block
of 500 powers stands in for all quarter-million.

Iterate the Carmichael function and the chain $m, \lambda(m), \lambda(\lambda(m)), \dots$ shrinks to 1
within a handful of steps, which is why a power tower reduced modulo $m$ eventually stops changing.
Problem 455 makes that the whole solution: it wants the $x$ with $n^x \equiv x \pmod{10^9}$, a
fixed point of $x \mapsto n^x \bmod 10^9$. Iterating the map from $x = 1$ builds the tower
$n, n^n, n^{n^n}, \dots$ modulo $10^9$. Once it is constant, its value *is* the fixed point. For
$10^6$ bases every tower settles within about a dozen rounds, so nothing searches the $10^9$
candidates. Problem 822 has the
same move in its simplest form: a number squared $k$ times is $x^{2^k}$ with $k$ near $10^{12}$, and
because the modulus is prime the exponent $2^k$ is itself reduced modulo $p - 1$ first. That makes
two modular exponentiations, one inside the other.

### Square-and-multiply works in any monoid

Square-and-multiply needs nothing from the integers except an **associative** multiplication, so
it computes powers in any [monoid](https://en.wikipedia.org/wiki/Monoid). Problem 721 needs
$\lfloor(\lceil\sqrt a\rceil + \sqrt a)^{a^2}\rfloor$. The conjugate $\lceil\sqrt a\rceil - \sqrt a$
lies in $[0, 1)$, so the floor is the integer $x^n + y^n$ less one, and that integer is computed in
the ring $\mathbb{Z}_p[\sqrt a]$. Its elements are pairs $(u, v)$ standing for $u + v\sqrt a$, multiplied
by a two-line rule and raised to the power by the usual loop. You need not always carry the
whole element. Problem 492 wants only the trace $V_k = \alpha^k + \alpha^{-k}$ of a power of a
quadratic unit, and traces obey $V_{2k} = V_k^2 - 2$ and $V_{2k+1} = V_k V_{k+1} - V_1$. A
[Lucas](https://en.wikipedia.org/wiki/Lucas_sequence) ladder on the pair $(V_k, V_{k+1})$ walks the
exponent's bits with two residue products per bit, and $\alpha$ itself is never formed. Problem 778 uses an even stranger
monoid. The carry-free "freshman's product" acts on each decimal place separately, so one place's
distribution of digit products is a ten-entry histogram. Combining $R$ independent factors is
then a convolution over the digits under multiplication mod 10, and the $R$-fold convolution power
takes $O(\log R)$ convolutions. Once you have spotted an associative step, the exponent can be as
large as the problem likes.

## Division: the modular inverse

You cannot divide by $a$ modulo $m$ directly, but you can multiply by its
[**modular multiplicative inverse**](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) —
the number $a^{-1}$ with $a \cdot a^{-1} \equiv 1 \pmod m$. It exists **precisely when $a$ and $m$
are [coprime](https://en.wikipedia.org/wiki/Coprime_integers)** ($\gcd(a, m) = 1$); otherwise $a$ has
no inverse and division is genuinely undefined. There are two standard ways to compute it:

- The [extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
  finds $x, y$ with $a x + m y = \gcd(a, m)$; when the gcd is 1, that $x$ is $a^{-1} \bmod m$. This
  works for **any** modulus.
- When the modulus is prime, Fermat's little theorem gives it for free: $a^{-1} \equiv a^{p-2}
  \pmod p$, one modular exponentiation.

In Python both collapse to `pow(a, -1, m)` (a negative exponent asks for the inverse); the C ports
here write out one or the other. The inverse is what turns a
[**linear congruence**](https://en.wikipedia.org/wiki/Linear_congruence_theorem) into a closed form:
to solve $a x \equiv c \pmod m$ you write $x \equiv c \cdot a^{-1} \pmod m$ — no search. Problem 134
does exactly this: "the number ending in the digits of prime $p_1$ and divisible by $p_2$" becomes
$10^d k \equiv -p_1 \pmod{p_2}$, solved in one line as `k = (-p1 * pow(d, -1, p2)) % p2`; the inverse
exists because $p_2 > 5$ shares no factor with $10^d$. Sometimes the inverse *is* the answer:
problem 274's "divisibility multiplier" for a prime $p$ turns out to be exactly $10^{-1} \bmod p$.
Because the number being inverted is the fixed 10, it even has a closed form keyed by $p$'s last
digit — $(kp + 1)/10$ with $k = 9, 3, 7, 1$ for $p \equiv 1, 3, 7, 9 \pmod{10}$ — which vectorises
over a NumPy array of primes where a per-prime `pow` call could not. Inverses also appear as the
object of study — problem 451 hunts for *self-inverse* residues ($m$ with $m^2 \equiv 1 \pmod n$).
Problem 700 shows the inverse's algorithm instead of its value. Its sequence $n a \bmod m$, with
$m$ prime, reaches its final record low of 1 at $n = a^{-1} \bmod m$. The records on the way are
found by keeping the smallest term and the smallest gap below $m$ and subtracting the smaller from
the larger. That is the subtractive Euclidean algorithm on $(a, m)$. Once runs of repeated
subtractions are collapsed, a walk over quadrillions of terms costs one step per record plus
$O(\log m)$.

### Check the modulus before you divide

Whether you may divide is a property of the **modulus**, and it is worth checking before writing the
first line. A prime modulus makes the residues a [field](https://en.wikipedia.org/wiki/Finite_field):
every non-zero element is invertible, so anything you would compute with fractions over the
rationals can be computed modulo $p$. That is what licenses the hook length formula in problem 1010 —
$f^\lambda = n!/\prod h(c)$, with a prime modulus larger than $n$ so that no hook length is a multiple
of it — and the binomial coefficients of problem 996, each a falling product times $(n!)^{-1}$. It
also licenses whole algorithms: [Berlekamp–Massey](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm),
which problem 529 uses to recover a linear recurrence of order 2772 from a digit automaton's counts,
divides by a discrepancy at every step and so only works over a field — there, modulo $10^9 + 7$.
Problem 860 is the same licence at its most ordinary. It reduces to a sum of products of binomials,
read off a factorial table modulo a prime larger than $n$. So does problem 517, a recursion
$g_a(x) = g_a(x-1) + g_a(x-a)$ on the irrational step $a = \sqrt n$. Unrolled, it counts lattice
paths and telescopes to one binomial $\binom{\lfloor x - ja \rfloor + j}{j}$ per count $j$ of
$a$-steps. The real number survives only inside that floor, and $\lfloor n - j\sqrt n\rfloor$ comes
exactly from an integer square root of $j^2 n$. The modulus never meets a float.

Even over a field an inverse costs a modular exponentiation, so how many you take is worth
planning. Problem 739 needs about $10^8$ binomial coefficients modulo $10^9 + 7$. It multiplies
the sum through by $(n-1)(n-2)!$, which turns every $1/j!$ into a suffix product, so each term
becomes a prefix product times a suffix product and the sum needs only **one** inversion, taken at
the end. The factorial tables behind 517 and 860 use the same economy. Invert only the largest
factorial, then walk down with $(k-1)!^{-1} = k!^{-1} \cdot k$, so a whole table of inverse
factorials costs one exponentiation. Problem 675 cannot fold its inverses away: it needs the inverse of every odd number up to
$2 \cdot 10^7 + 1$. It computes all of them at once, as $a^{p-2}$ by one vectorised
square-and-multiply over a NumPy array, about thirty array multiplications for ten million inverses.
Sometimes the structure removes the inverse altogether. Problem 682 extracts one coefficient of a
rational generating function $N(y)/D(y)$ with the
[Bostan–Mori](https://arxiv.org/abs/2008.08822) halving step, which multiplies top and bottom by
$D(-y)$. The only division left is by the final denominator's constant term. That constant is
$D(0)^{2^r}$ after $r$ rounds, and since $D(0) = 1$ it is still 1, so the C port takes no inverse
at all.

A **composite** modulus is the opposite case. Problem 250 needs binomial coefficients modulo
$10^{16}$, and the natural row recurrence $\binom{c}{i+1} = \binom{c}{i} \cdot \frac{c-i}{i+1}$
divides by $i + 1$, which for most $i$ shares a factor with $10^{16}$ and has no inverse there. The
division is exact over the integers but meaningless in the residues. The Python carries each binomial
as an exact big integer and reduces only when storing it; the C, without that luxury, writes it as
$2^{e_2} \cdot 5^{e_5} \cdot u$ — the primes of the modulus tracked as exponents, the remaining unit
$u$ coprime to 10 and therefore safely invertible. That factor-out-the-modulus's-primes move is the
general repair; the general lesson is that with a composite modulus, every division in your
derivation is a bug waiting for an input that shares a factor with it.

The commonest version is also the easiest to miss: "the last nine digits" means modulo $10^9$, and
$10^9$ is even. Both problems 340 and 401 end in closed forms with a small fixed denominator.
Problem 340 has the triangular numbers $b(b+1)/2$, and problem 401 has the square pyramidal numbers
$x(x+1)(2x+1)/6$ with $x$ up to $10^{15}$. Since $2$ has no inverse modulo $10^9$, the cure is to
**divide before reducing**. One of $x, x+1$ is even, and exactly one of $x, x+1, 2x+1$ is a
multiple of 3. Dividing those factors exactly leaves integers that each fit in 64 bits; only then
are they reduced and multiplied.

### Counting the solutions of a congruence

A congruence also *counts*. Its solutions form an
[arithmetic progression](https://en.wikipedia.org/wiki/Arithmetic_progression) with step $m$, so the
number of them in an interval is two floor divisions, not a loop — and that turns many searches into
sums of closed forms. Problem 251 reduces Cardano triplets to a parameter $d$ pinned by
$8 d n_1 \equiv 3 \pmod{b_1^2}$: one inverse gives the smallest $d$, one division counts every
admissible $d$ below a ceiling, and a whole family of triplets is counted in constant time. Problem
305 counts the occurrences of a digit string that straddle two consecutive integers of the
Champernowne stream by demanding that the left integer end in a given suffix — a congruence modulo
$10^i$ that absorbs any carry automatically. (In C, `/` truncates towards zero; a progression count
whose bounds can go negative needs a true floor division.)

## The unit group: roots of unity, and how many there are

Some problems ask not for a residue but for **how many** residues solve a polynomial congruence, and
the answer comes from the structure of the
[multiplicative group of integers modulo $n$](https://en.wikipedia.org/wiki/Multiplicative_group_of_integers_modulo_n).
Modulo a prime $p$ (and an odd prime power) that group is **cyclic**, of order $\varphi(p^e)$, and a
cyclic group of order $N$ has exactly $\gcd(r, N)$ solutions of $x^r = 1$. That one fact settles a
family of problems without testing a single residue:

- Problem 272 wants the $n$ with exactly 242 nontrivial cube roots of unity. $\gcd(3, p-1)$ is 3 for
  $p \equiv 1 \pmod 3$ and 1 otherwise, so each such prime triples the count (as does a factor of 9),
  the total is $3^k$, and "242 roots" means "exactly five such factors" — the problem becomes a
  depth-first enumeration of products rather than a root count per $n$.
- Problem 421 sums the primes $p \le 10^8$ dividing $n^{15} + 1$. The solutions of
  $n^{15} \equiv -1 \pmod p$ are the negatives of the 15th roots of unity, and there are
  $\gcd(15, p-1) \in \{1, 3, 5, 15\}$ of them, decided by $p \bmod 3$ and $p \bmod 5$. A root of
  unity of order $r$ is $a^{(p-1)/r}$ for any base $a$ that does not give 1 — one modular
  exponentiation per prime.
- Problem 245 needs the roots of $x^2 - x + 1 \equiv 0 \pmod \ell$; they are $-\omega$ for a primitive
  cube root of unity $\omega$, found the same way and cheaper than a general modular square root.

Problem 421 also shows the swap that makes such problems feasible at all: instead of factoring
$10^{11}$ numbers of up to 165 digits, exchange the order of summation and ask, per prime, how many
$n \le N$ fall in its few residue classes — the progression count from above, one division per root.

### Orders, and where they live

The [**multiplicative order**](https://en.wikipedia.org/wiki/Multiplicative_order) of a unit $u$ is
the least $e$ with $u^e = 1$, and it is what an exponent may be reduced by. Computing it follows one
recipe. Start from a known multiple $d$, usually the group order. For each prime $q \mid d$, divide
$d$ by $q$ as long as $u^{d/q}$ is still 1. What remains is the order, and the cost is a
factorisation of $d$ plus a few modular exponentiations. That is why problem 752 builds a
smallest-prime-factor sieve one past its bound: the same table factors every $p - 1$ and $p + 1$
it will reduce.

Those two group orders come from the two shapes a quadratic ring $\mathbb{F}_p[\sqrt c]$ can take.
If $c$ is a quadratic residue mod $p$, the ring splits as $\mathbb{F}_p \times \mathbb{F}_p$ through
$\sqrt c \mapsto (s, -s)$ with $s^2 \equiv c$. An element's order is then the lcm of two orders that
divide $p - 1$. If $c$ is a non-residue, the ring is the field $\mathbb{F}_{p^2}$, whose units number
$p^2 - 1$. But [Frobenius](https://en.wikipedia.org/wiki/Frobenius_endomorphism), $y \mapsto y^p$, is
conjugation there, so $u^{p+1} = u\bar u = N(u)$, the [norm](https://en.wikipedia.org/wiki/Field_norm).
An element of norm 1 therefore has order dividing $p + 1$. Problem 492 lives on this: its root
$\alpha$ has norm 1, so the astronomical exponent $2^{n-1}$ is reduced modulo $p - 1$ or $p + 1$.
[Quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity) decides which from
$p \bmod 13$, a table lookup per prime. Problem 752's $u = 1 + \sqrt 7$ has norm $-6$, so it first
takes $o = \operatorname{ord}_p(-6)$ inside $\mathbb{F}_p$. Then $u^o$ has norm 1, and only $p + 1$
remains to reduce against, not the much richer $p^2 - 1$. Most of the work never leaves the prime
field.

The norm also says whether there is an order at all. It is multiplicative, so $u$ is a unit modulo
$x$ exactly when $N(u)$ is, and in problem 752 that removes every $x$ sharing a factor with 6
before any power is taken. And orders lift cheaply from primes to prime powers. Every element of
the kernel $1 + p^{k-1}R$ of reduction mod $p^{k-1}$ has order dividing $p$. So the order mod
$p^k$ is either the order mod $p^{k-1}$ or $p$ times it, and one power decides which. CRT (below)
then makes the order modulo a composite the lcm of its prime-power orders.

## Combining moduli: the Chinese Remainder Theorem

When a modulus factors into coprime pieces, the
[**Chinese Remainder Theorem**](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) (CRT) says a
system of congruences with pairwise-coprime moduli has a unique solution modulo the product:

$$x \equiv a_1 \pmod{m_1}, \quad x \equiv a_2 \pmod{m_2} \;\Longrightarrow\; \text{a unique } x
\pmod{m_1 m_2}.$$

This is a workhorse for two reasons. First, it lets you *combine* separately-derived residues.
Problem 365 wants $\binom{10^{18}}{10^9}$ — over nine billion digits — modulo $pqr$ for every triple of
primes between 1000 and 5000. [Lucas's theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem)
gives the binomial modulo each prime from its base-$p$ digits, and CRT lifts the three residues to one
modulo $pqr$. With twenty million triples the lift must be cheap, and it is once you notice that
$(qr)^{-1} \bmod p = q^{-1} r^{-1} \bmod p$: every inverse the sum needs is a *pairwise* one,
tabulated once.

Coprimality is what makes CRT unconditional. Drop it and the theorem gains a hypothesis. With
$d = \gcd(m_1, m_2)$, the system is solvable **exactly when $d \mid a_2 - a_1$**, and then it has
one solution modulo $\operatorname{lcm}(m_1, m_2)$ rather than the product. Problem 531 is that
generalised form at its barest. For every pair of neighbouring $n < m$ in a window of a few thousand
integers near $10^6$, it wants the least $x \equiv \varphi(n) \pmod n$, $x \equiv \varphi(m) \pmod m$,
or $0$ when there is none. Write $x = \varphi(n) + n t$. The second congruence becomes
$n t \equiv \varphi(m) - \varphi(n) \pmod m$. Test that $d$ divides the right-hand side; if it does,
divide all three terms by $d$. That leaves $n/d$ coprime to $m/d$, and one inverse gives $t$.
Neighbouring integers make the gcd cheap, since $\gcd(n, m) = \gcd(n, m - n)$ and $m - n$ is small.

Second, it lets you *decompose* a hard modulus: answer the question modulo each prime power, where the
structure is simple, and glue the answers back together. The number of solutions of a polynomial
congruence is therefore **multiplicative** across the factors — which is why $x^3 \equiv 1 \pmod{91}$
has $3 \times 3 = 9$ solutions (8 besides $x = 1$) in problems 271 and 272, and why the $3^k$ count
above works at all. Problem 271 also needs the roots themselves, not only their count. The modulus
is the primorial $2 \cdot 3 \cdots 43$, so the roots are found modulo each prime, and a non-squarefree
modulus would add one more step: [Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma)
lifts a root mod $p$ uniquely to $p^k$ whenever the derivative is a unit. The prime 3 is the
exception, since $3x^2$ vanishes mod 3. CRT then assembles the $3^6$ combinations. Problem 250
uses the same split for a proof rather than a computation: the period of $k^k \bmod 250$ was
established modulo 2 and modulo 125 separately.

The decomposition can also *be* the object. A residue with $a^2 \equiv a \pmod n$ (an
[idempotent](https://en.wikipedia.org/wiki/Idempotent_(ring_theory))) is $0$ or $1$ modulo each
prime power of $n$, because $a$ and $a - 1$ are coprime. So the idempotents correspond one-to-one
with the ways to split $n$ into a coprime pair $d \cdot e$, and there are $2^{\omega(n)}$ of them.
Problem 407 wants the largest for every $n \le 10^7$. It therefore enumerates coprime pairs instead
of residues, solving each pair's two congruences by CRT. Because the smaller factor $s$ of a pair
is at most $\sqrt N$, it always inverts modulo $s$, and one table of inverses mod $s$ serves every
partner.

## Reduce what the problem reduces — and nothing else

Reducing early is only sound when the quantity you reduce is the one the statement reduces. Problem
244's checksum is a rolling hash taken modulo $100\,000\,007$ for each shortest path, and the answer
is the **plain, unreduced** sum of those checksums. The tempting dynamic programme carries
$(\text{count}, \text{sum of hashes})$ through the search layers — but that sum would be known only
modulo $100\,000\,007$, because once the individual hashes have wrapped, modular arithmetic cannot
tell how many of them did. The correct route is to produce each shortest path and add its reduced
hash as an ordinary integer. Problem 271 has the same trap in a quieter form: it sums the cube
roots of unity as integers in $[0, n)$. That sum is hundreds of times $n$, so adding the CRT
combinations modulo $n$ would give only its residue. Read the statement for exactly where the
modulus applies; a `% m` one level too high gives a plausible, wrong number.

When the order matters but the numbers are too big to compare, split each one into a part that
decides the order and a part that only sets the scale. Problem 615 wants the millionth integer
with at least a million prime factors. Every early member of that list carries a common power
$2^{k-s}$ with $s = 36$, and dividing it out keeps them in the same order. The selection then runs
over ordinary 64-bit integers, and the modulus touches only the scale factor, as one
$2^{k-s} \bmod m$ at the end.

The converse is a gift: a modulus written into a *definition* is often there to simplify it. Problem
512 sums $\varphi(n^i)$ for $i = 1, \dots, n$, taken modulo $n + 1$. Modulo $n + 1$, $n \equiv -1$,
and $\varphi(n^i) = n^{i-1}\varphi(n)$, so the terms alternate in sign and cancel in pairs. Each
$f(n)$ is just $\varphi(n)$ for odd $n$ and $0$ for even $n$, and the problem becomes a sum of
totients before any code is written.

## The overflow trap

Modular arithmetic's other sharp edge is a language pitfall, not a mathematical one. Two residues
below $m$ multiply to a product approaching $m^2$; with $m = 10^{10}$ that is $10^{20}$, past the
$\approx 9.2 \times 10^{18}$ ceiling of a signed 64-bit integer. Python's arbitrary-precision integers
make this invisible, but in C the intermediate product overflows and silently corrupts the answer.
The rule of thumb: **a modular multiply is safe in 64 bits only while $m < 2^{32}$** (about
$3 \times 10^9$ for a signed type). Past that, the fix used throughout the C solutions here is to
widen just the multiply — cast one operand to `__int128`, form the product at 128-bit precision, and
reduce back to 64 bits immediately — so the oversized value is transient and never stored. The
[Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) tests in problems
245 and 248 hit exactly this: their candidates pass $3 \times 10^9$, and squaring one overflows a
signed 64-bit word.

Three variations on the same budget:

- **Guard the input, and size the total.** Problem 421 multiplies residues below $p \le M$, so it
  rejects $M \ge 2^{32}$ up front rather than let a larger input corrupt the result quietly — and its
  *total*, which grows like $4 N \pi(M)$, approaches the 64-bit ceiling although no single residue
  comes close. Estimate the size of the answer, not only of its terms. Problem 531's answer is not
  reduced at all: it sums CRT solutions of up to $\operatorname{lcm}(n, m) \approx 10^{12}$ over
  millions of pairs, so its C port accumulates in `unsigned __int128`.
- **Reduce lazily when you can prove headroom.** Problem 529's C port accumulates a polynomial
  product's terms in an unsigned 64-bit word and subtracts $8m^2$ whenever the sum reaches it, taking
  one `%` per output coefficient instead of one per term.
- **Know which operations multiply.** Problem 996's polynomial DP only shifts, adds and doubles —
  never multiplies two residues — so NumPy `int64` arrays stay exact modulo its $1.2 \times 10^9$
  prime, where a product of two residue vectors would not. When the vectors *do* multiply, a prime
  below $2^{30}$ buys the headroom. Problems 675 and 721 run square-and-multiply over whole NumPy
  arrays because each product of two residues stays below $2^{60}$, and NumPy has no `__int128`
  to fall back on. A matrix product is worse, because it sums 81 such products before any
  reduction. Problem 706 splits one factor into 15-bit halves and multiplies each half separately,
  which keeps every dot product inside `int64`. The bound is a tight one: problem 492's primes sit
  just above $10^9$, so its residue products reach about $1.03 \times 10^{18}$, still below $2^{63}$.
- **A comparison can overflow too.** Not every oversized product is reduced. Problem 615's C port
  prunes a depth-first search when a candidate $V \cdot p$ exceeds a bound, and that product can
  briefly pass 64 bits. A wrapped value would look small and slip past the test. So it is formed in
  `__int128` and compared there, although nothing is ever reduced modulo anything.

## How to reason about it

The recurring cue is a question that depends only on a remainder — *last digits*, *divisibility*,
*a count modulo a prime*, *a periodic or cyclic structure* — attached to a value too large to form
directly. When you see it:

- Reduce **early and often** — counts, and where the question allows, elements and exponents too —
  but only the quantity the statement actually reduces.
- Need a **power**? Use modular exponentiation ($O(\log b)$), and shrink the exponent itself with
  Fermat, Euler or Carmichael; a periodic exponent can make a whole sequence periodic. Any
  associative product (a ring extension, a convolution) can be powered the same way.
- Need to **divide**? Multiply by the modular inverse — extended Euclid for any modulus, $a^{p-2}$
  for a prime one — and remember it exists only when $\gcd(a, m) = 1$. A prime modulus is a field;
  under a composite one, audit every division — including the $/2$ and $/6$ of a closed form
  modulo $10^9$. Where you can, defer all the divisions to a single inverse at the end.
- Need an **order**? Start from the group order ($p - 1$; $p + 1$ for a norm-one element of
  $\mathbb{F}_{p^2}$) and strip primes while the power stays 1. Lift to $p^k$ by at most a factor
  $p$ per step, and take the lcm across a composite modulus.
- Need to **count** solutions? A linear congruence's solutions are a progression (two divisions);
  the roots of $x^r \equiv 1 \pmod p$ number $\gcd(r, p - 1)$.
- Facing **several congruences** or a **composite modulus**? Combine or decompose with the Chinese
  Remainder Theorem, working prime power by prime power; solution counts multiply. If the moduli
  share a factor $d$, check that $d$ divides the difference of the residues before solving.
- Writing **C** (or any fixed-width language)? Widen every modular multiply once $m \ge 2^{32}$, and
  bound the accumulated total as well as each product, including products you only compare.

The classic mistake is to compute the honest quantity first and reduce at the end — materialising the
million-digit power, or the true factorial, before taking the remainder. The whole point is that you
never have to: reduce as you go, and a problem that looks like big-integer arithmetic becomes a
handful of operations on small numbers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0048](/solutions/0048/) — Self Powers
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0244](/solutions/0244/) — Sliders
- ● [0245](/solutions/0245/) — Coresilience
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ● [0251](/solutions/0251/) — Cardano Triplets
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ○ [0282](/solutions/0282/) — The Ackermann Function
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ○ [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ● [0304](/solutions/0304/) — Primonacci
- ● [0305](/solutions/0305/) — Reflexive Position
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ● [0319](/solutions/0319/) — Bounded Sequences
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0330](/solutions/0330/) — Euler's Number
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ● [0340](/solutions/0340/) — Crazy Function
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ○ [0402](/solutions/0402/) — Integer-valued Polynomials
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ● [0407](/solutions/0407/) — Idempotents
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0411](/solutions/0411/) — Uphill Paths
- ○ [0412](/solutions/0412/) — Gnomon Numbering
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ○ [0422](/solutions/0422/) — Sequence of Points on a Hyperbola
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0427](/solutions/0427/) — $n$-sequences
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0451](/solutions/0451/) — Modular Inverses
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ● [0478](/solutions/0478/) — Mixtures
- ○ [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0498](/solutions/0498/) — Remainder of Polynomial Division
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0517](/solutions/0517/) — A Real Recursion
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0528](/solutions/0528/) — Constrained Sums
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0537](/solutions/0537/) — Counting Tuples
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ○ [0554](/solutions/0554/) — Centaurs on a Chess Board
- ○ [0559](/solutions/0559/) — Permuted Matrices
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0593](/solutions/0593/) — Fleeting Medians
- ○ [0602](/solutions/0602/) — Product of Head Counts
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0628](/solutions/0628/) — Open Chess Positions
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ○ [0635](/solutions/0635/) — Subset Sums
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0672](/solutions/0672/) — One More One
- ○ [0673](/solutions/0673/) — Beds and Desks
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0696](/solutions/0696/) — Mahjong
- ● [0700](/solutions/0700/) — Eulercoin
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0709](/solutions/0709/) — Even Stevens
- ● [0710](/solutions/0710/) — One Million Members
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ○ [0728](/solutions/0728/) — Circle of Coins
- ○ [0732](/solutions/0732/) — Standing on the Shoulders of Trolls
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0745](/solutions/0745/) — Sum of Squares II
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0767](/solutions/0767/) — Window into a Matrix II
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ● [0778](/solutions/0778/) — Freshman's Product
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0789](/solutions/0789/) — Minimal Pairing Modulo $p$
- ○ [0790](/solutions/0790/) — Clock Grid
- ○ [0797](/solutions/0797/) — Cyclogenic Polynomials
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0803](/solutions/0803/) — Pseudorandom Sequence
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ○ [0809](/solutions/0809/) — Rational Recurrence Relation
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0813](/solutions/0813/) — XOR-Powers
- ○ [0814](/solutions/0814/) — Mezzo-forte
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0822](/solutions/0822/) — Square the Smallest
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0824](/solutions/0824/) — Chess Sliders
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ○ [0837](/solutions/0837/) — Amidakuji
- ○ [0839](/solutions/0839/) — Beans in Bowls
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0849](/solutions/0849/) — The Tournament
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0851](/solutions/0851/) — SOP and POS
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0858](/solutions/0858/) — LCM
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ○ [0866](/solutions/0866/) — Tidying Up B
- ○ [0871](/solutions/0871/) — Drifting Subsets
- ○ [0873](/solutions/0873/) — Words with Gaps
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ○ [0875](/solutions/0875/) — Quadruple Congruence
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0892](/solutions/0892/) — Zebra Circles
- ○ [0902](/solutions/0902/) — Permutation Powers
- ○ [0903](/solutions/0903/) — Total Permutation Powers
- ○ [0909](/solutions/0909/) — L-expressions I
- ○ [0910](/solutions/0910/) — L-expressions II
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0916](/solutions/0916/) — Restricted Permutations
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ○ [0921](/solutions/0921/) — Golden Recurrence
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ○ [0977](/solutions/0977/) — Iterated Functions
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ○ [0984](/solutions/0984/) — Knights and Horses
- ○ [0989](/solutions/0989/) — Fibonacci Sum
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ● [0996](/solutions/0996/) — Overtakes
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1001](/solutions/1001/) — Connections I
- ○ [1004](/solutions/1004/) — Balanced Integer
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
