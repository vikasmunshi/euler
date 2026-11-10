<!-- tags: [modular-arithmetic, modular-multiplicative-inverse, modular-arithmetic-application, modular-exponentiation, modular-multiplicative-inverse-application] -->
<!-- status: final 2026-11-09T17:04Z -->
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

Closure also says exactly when a *recursive* state may be reduced early: every update must be built
from $+$, $-$ and $\times$ by integers. Problem 521 sums smallest prime factors up to $10^{12}$
with a sieve over the quotients $\lfloor n/k \rfloor$. Each step subtracts $p$ times a difference
of table entries, so its prime-sum tables live modulo $10^9$ from initialisation, though their
honest values reach $10^{22}$. Problem 539's elimination game obeys a halving recurrence in which
the sum of survivors depends on the half-size sum with integer coefficients, so that sum is reduced
at each of sixty levels. A division, a comparison or a floor applied to the state would break
this, and those cases are what the rest of this page is about.

Residues can also be taken twice, of two different things. Problem 706 asks how many $10^5$-digit
numbers have a count of substrings divisible by 3 that is itself divisible by 3. A substring is
divisible by 3 exactly when the digit prefix sums at its two ends agree mod 3. So the count is
$\sum_r \binom{c_r}{2}$ over the numbers $c_r$ of prefixes in each residue class $r$. Only that count
mod 3 matters, so the $c_r$ can be kept mod 3 as well. The state shrinks to 81 values, small enough
for a [transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) raised to the
$10^5$th power.

That is the general pattern: a residue is a complete **state**. Appending a digit $d$ to $x$ sends
$x \bmod n$ to $(10x + d) \bmod n$. The new remainder depends only on the old one, so two prefixes
with the same remainder behave alike from then on. Problem 303 wants the least multiple of $n$
written with the digits 0, 1 and 2. That multiple can run to twenty digits, but the search is a
breadth-first walk over the $n$ remainders, and it stops at the first visit to 0. Expanding digits
in ascending order makes the first path to each remainder the smallest numeral that reaches it. The
[pigeonhole principle](https://en.wikipedia.org/wiki/Pigeonhole_principle) also bounds the walk.
Two of the repunits $1, 11, \dots$ share a remainder within the first $n + 1$, and their difference
is a 0-1 multiple of $n$, so no search runs past $n$ states.

The state can be a carry instead of a remainder. Problem 990 counts the addition equations
$x_1 + \dots + x_k = y_1 + \dots + y_m$ that fit in a bounded length, with terms of up to 24 digits.
Checking one the way it is done on paper, column by column from the units, needs only a congruence
per column. The left digits minus the right digits plus the incoming carry must be
$\equiv 0 \pmod{10}$, and the quotient is the signed carry out. The values never matter, only the
carry and how many terms on each side still have digits. So a digit DP over those few numbers
replaces any table keyed by value. Writing each right-hand digit as $9 - d'$ makes every digit range
over an interval again. A column's digit sum then has one generating function per count of terms,
and the column condition picks its coefficients in one residue class mod 10.

Give the residue walk weights and it computes a shortest path. Problem 718 needs every $n$ that is
*not* $a x + b y + c z$ for three coprime powers. That is the gap set of a
[numerical semigroup](https://en.wikipedia.org/wiki/Numerical_semigroup), and it is read off the
[Apéry set](https://en.wikipedia.org/wiki/Ap%C3%A9ry_set): for each residue $r \bmod x$, the least
representable $w_r \equiv r$. Every larger member of that class is $w_r + kx$, so the class's
gaps are an arithmetic progression with a closed-form count and sum. In general $w_r$ is a
Dijkstra search over the $x$ residues. With two other generators there is a shortcut. The least
multiple of $y$ in class $r$ is $y \cdot (r y^{-1} \bmod x)$, one inverse. Visiting the classes in
the order $iz \bmod x$, a single cycle because $\gcd(z, x) = 1$, makes "add one more $z$" a step
to the next index. The minimum over both generators then becomes a running minimum of
$b_i - iz$, a single vectorised pass over $x$ residues for a semigroup whose gaps run into the
quadrillions.

The residue need not be of the number itself. A number is a perfect cube exactly when every
exponent in its factorisation is $\equiv 0 \pmod 3$. Problem 342 asks when $\varphi(n^2)$ is a
cube, so it tracks the exponent vector of $\varphi(n^2)$ modulo 3, and only the primes with a
non-zero residue are kept. Each prime $p$ of $n$ adds $2e - 1$ to its own exponent and the
factorisation of $p - 1$ to smaller primes. Placing primes from the largest down therefore settles
each residue for good, and the search follows that order.

Modulo 2 the exponent residues form a vector space, and then linear algebra counts for you. A
product is a perfect square exactly when every exponent is even, so problem 619 maps each number to
its exponent-parity vector over [$\mathbb{F}_2$](https://en.wikipedia.org/wiki/GF(2)).
Multiplication becomes vector addition, and the subsets with a square product are the kernel of a
linear map. If the $n$ vectors have [rank](https://en.wikipedia.org/wiki/Rank_(linear_algebra)) $r$,
there are $2^{n-r} - 1$ non-empty such subsets. The rank can be found without a matrix that has
one column per prime up to $10^6$. A number has at most one prime above $\sqrt b$, so each large
prime is pivoted away along the few numbers that share it, and each such prime adds one to the
rank. Elimination then runs on only the 186 small-prime columns.

"Last digits" generalises to digits *anywhere*. The ten digits starting at position $n$ of a real
number $A$ are $\lfloor 10^{n+9} A \rfloor \bmod 10^{10}$, and when $A$ is a sum of simple fractions
the floor splits term by term. Problem 731 does this for the Stoneham number
$\sum_i 3^{-i} 10^{-3^i}$ at position $10^{16}$. Each term's shifted value $10^e / 3^i$ divides
into an integer quotient, wanted only mod $10^{10}$, and a remainder $10^e \bmod 3^i$, one modular
exponentiation. The remainders' fractions add up to a small carry, and the tail of terms too small
to matter provably cannot cross an integer. It is the
[Bailey–Borwein–Plouffe](https://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula)
trick for $\pi$, and it costs $O(\log^2 n)$ where writing the expansion out is impossible.

Read the other way, a fractional part is a residue: $\{a/n\} = (a \bmod n)/n$. Problem 850 sums
$\{i^k/n\}$ over $i$, over odd $k$ and over $n$ up to about $3 \times 10^{13}$. For odd $k$ the map
$i \mapsto n - i$ sends $i^k$ to $-i^k \pmod n$, so the non-zero residues pair off into sums of
exactly $n$. Only the $i$ with $n \mid i^k$ escape the pairing, and the inner sum is
$(n - z_k(n))/2$. Here $z_k(n)$ counts the solutions of a congruence, so by CRT (below) it is
multiplicative, and modulo $p^e$ it is a power of $p$ fixed by $\lceil e/k \rceil$. The fractions
have become a count of roots, and the count is a multiplicative function.

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

The same number often plays two roles, and then it is needed modulo two different things. Problem
684 sums the smallest number with digit sum $f_i$ over Fibonacci $f_i$ up to about $3 \times 10^{18}$. Writing
$f = 9q + r$, that number is $(r + 1) \cdot 10^q - 1$, and the block sums add a linear term in $q$.
Modulo the prime $p$, the power needs $q \bmod (p - 1)$ while the linear term needs $q \bmod p$.
Neither can be read off a residue of $f$ modulo $p$, because $q$ is a quotient by 9. The fix is to
run the Fibonacci recurrence modulo $9p$ and again modulo $9(p - 1)$. Either residue gives
$r = f \bmod 9$, and subtracting $r$ and dividing by 9 is then exact and yields $q$ in each modulus. It is
the "work modulo $cm$" repair described under division below, applied to a recurrence rather than
a closed form.

Problem 520 meets the two roles inside a geometric series. Its counts are power sums
$\sum_k c_k k^L$, so summing over all lengths $L \le n$ gives one series
$\sum_L k^L = (k^{n+1} - k)/(k - 1)$ per base $k$. That is an inverse of $k - 1$ modulo the prime,
plus the degenerate ratio $k = 1$, whose sum is just the number of terms and so needs $n \bmod p$.
And when $n = b^u$ with $u$ as large as a thousand, the exponent is never formed at all. The power is
carried instead, $k^{b^u} = \bigl(k^{b^{u-1}}\bigr)^b$, one small exponentiation per step of $u$.
That keeps the C port in 64 bits without a bignum library.

Problem 921 carries a power along a stranger index. Its exponents are $5^{F_i}$ for Fibonacci $F_i$,
wanted modulo $M - 1$ by Fermat, and the index never has to be tracked at all, because
$5^{F_i} = 5^{F_{i-1}} \cdot 5^{F_{i-2}}$. The Fibonacci addition has become a multiplication of
the powers, so each reduced exponent is one modular product of the previous two. Only $\times$ is
used, so it does not matter that $M - 1$ is composite.

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
takes $O(\log R)$ convolutions. Problem 649 does the same with XOR in place of digit products.
Its game splits into independent coins whose
[Sprague–Grundy](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem) values combine by
XOR, so one coin's eight-entry value histogram is raised to the $c$-th XOR-convolution power. Once
you have spotted an associative step, the exponent can be as large as the problem likes.

Problem 294 builds its monoid out of digit strings. It counts the $n$-digit strings,
$n = 11^{12}$, whose value is divisible by 23 and whose digit sum is 23. A block of digits is
summarised by a $23 \times 24$ table, which records how many strings of that length have each
residue and each digit sum up to 23. Placing a block above one of length $L$ multiplies the upper
block's residues by $10^L \bmod 23$. Since 10 is a unit mod 23, that only permutes the rows. The two
tables are then convolved, cyclically in the residue and truncated in the digit sum. Each table
measures its residue from its own lowest digit, so it never depends on where it will sit, and the
single scalar $10^L$ is all the join needs. Concatenation is associative, so the $n$-digit table
takes about 80 joins.

The step need not be a power of one element. It can be a product of fixed matrices along a
structured word. Problem 1006 sums squared values of windows of the
[Fibonacci word](https://en.wikipedia.org/wiki/Fibonacci_word). Reading one letter is one matrix,
the matrix of each standard word $S_n = S_{n-1}S_{n-2}$ is the product of the previous two, and any
prefix of length $10^{18}$ is a [Zeckendorf](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem)
product of about ninety blocks. One state does not fit that mould: prepending a digit to $N$
multiplies it by a power of 10 that grows with the position, which no fixed matrix can do. The repair is
to carry $10^{-r} N$ and $100^{-r} N^2$ instead. The changing scale is absorbed by a modular
inverse, and the update becomes linear with constant coefficients again. Dividing a state by a
known power is a cheap way to make a step position-independent, and so composable.

The same composition removes a sequential loop. Problem 960 draws ten million values from a
[linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator)
$a \mapsto \alpha a + \gamma \pmod{10^{12}}$, where each value needs the one before it. Affine maps
compose into affine maps, so the step applied 4096 times is a single map $a \mapsto A a + C$. A row
of 4096 consecutive values then advances to the next row in one vectorised multiply-add. $A a$
reaches $10^{24}$, so $A$ is split into two $10^6$-sized halves to keep every partial product in
64 bits. That is the generator's jump-ahead, and it works for the same reason square-and-multiply
does.

With a fixed base and many exponents, square-and-multiply is the wrong tool, because it repeats the
same squarings for every exponent. Problem 921 raises the one element $\beta = 2 + \sqrt 5$ of
$\mathbb{Z}[\sqrt 5]/M$ to over a million exponents below $M < 2^{29}$. Split each exponent as
$x = h \cdot 2^{15} + l$ and tabulate $\beta^l$ and $\beta^{h \cdot 2^{15}}$, about $\sqrt M$
entries each. Then $\beta^x$ is two lookups and one ring multiplication, where the loop would take
some 29 squarings, and the lookups vectorise as array gathers. These are the two tables of
[baby-step giant-step](https://en.wikipedia.org/wiki/Baby-step_giant-step), used forwards: that
algorithm searches them for an unknown exponent, and here they apply known ones.

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

A field also lets you count with **probabilities**. Problem 705 totals the inversions over every
way of replacing each digit of a 42-million-digit string by one of its divisors. That total is the
number of choices $T$ times the expected inversion count, and the expectation splits over pairs of
positions by linearity. One pair of digit values $x, y$ contributes the fraction
$A(x, y) / (d(x)\,d(y))$, where $d$ counts divisors, and a fraction is just a residue modulo
$10^9 + 7$. So the 42 million positions collapse to an 81-entry table of digit-pair counts, a few
inverses of numbers up to 4, and $T$ as a product of powers.

A field can even hold an irrational closed form, if the irrational has a residue. Problem 1007
sums the values of every bracketing of $F_0 - F_1 - \dots - F_n$. Each leaf enters with a sign, so
the sum is a signed sum of Fibonacci numbers. [Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Binet's_formula)
$F_i = (\varphi^i - \psi^i)/\sqrt 5$ turns those weights into two geometric ones, and geometric
weights are what a generating function handles. Over the reals that needs $\sqrt 5$. But 5 is a
[quadratic residue](https://en.wikipedia.org/wiki/Quadratic_residue) modulo $10^9 + 9$, so
$\sqrt 5$, $\varphi$ and $\psi$ are ordinary elements of $\mathbb{F}_p$, found by Tonelli–Shanks.
The formula then holds there exactly. Before carrying a real-number identity into the residues,
check that every irrational it uses has a residue.

A field can also undo a symmetry. Problem 475 counts the ways to split $12n$ musicians into trios
that never reuse a quartet. Unordered trios are awkward to count, so it labels them, which
multiplies the count by exactly $(4n)!$ because the trios are distinct. A dynamic programme then
counts the labelled form in residues. Removing the labels is a division of a residue, one inverse
at the end, and it is valid because the prime exceeds $4n$. When a group acts freely on what you
are counting, count the labelled objects and divide by the group's size once. Problem 923 goes
the other way. It counts *ordered* tuples of staircases, but who wins depends only on the multiset
of their game values. So each class of $c$ pieces drawn from one value class enters as $F^c / c!$,
an [exponential generating function](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function),
and one factor $m!$ at the end puts the orderings back. Both directions need $c!$ to be a unit,
which a prime larger than the counts guarantees.

Even over a field an inverse costs a modular exponentiation, so how many you take is worth
planning. Problem 739 needs about $10^8$ binomial coefficients modulo $10^9 + 7$. It multiplies
the sum through by $(n-1)(n-2)!$, which turns every $1/j!$ into a suffix product, so each term
becomes a prefix product times a suffix product and the sum needs only **one** inversion, taken at
the end. The factorial tables behind 517 and 860 use the same economy. Invert only the largest
factorial, then walk down with $(k-1)!^{-1} = k!^{-1} \cdot k$, so a whole table of inverse
factorials costs one exponentiation. Sometimes you can avoid the inverses by changing what you carry.
Problem 374's block sums need the [harmonic numbers](https://en.wikipedia.org/wiki/Harmonic_number)
$H_j$, and as residues those cost one inverse per $j$. It carries $A_j = j!\,H_j$ instead. That is
an integer (a [Stirling number of the first kind](https://en.wikipedia.org/wiki/Stirling_numbers_of_the_first_kind))
with $A_j = j A_{j-1} + (j-1)!$, so a loop of fourteen million steps takes no inverse at all.
The same scaling works for any coefficient recurrence that divides by its index. The coefficients
of an algebraic or [holonomic](https://en.wikipedia.org/wiki/Holonomic_function) series typically
obey $(k+1)c_{k+1} = \alpha_k c_k + \beta_k c_{k-1}$, which costs one inverse per step. Carry
$d_k = k!\,c_k$ instead. The $k + 1$ cancels, and $d_{k+1} = \alpha_k d_k + k\beta_k d_{k-1}$ has
polynomial coefficients and no division. Problem 976 advances three such sequences and a binomial
numerator, all sharing the denominator $K!$, in one loop of $10^7$ steps. Problem 1007 does the
same for the Catalan and square-root series in its generating function, and one inverse of
$(n+1)!$ at the end undoes every scaling.
When the inverses really are needed one by one, a table of them costs $O(1)$ each. Problem 892
needs $1/m$ for every $m$ up to $5 \times 10^6$, and reads each off the identity
$i^{-1} \equiv -\lfloor p/i \rfloor \cdot (p \bmod i)^{-1} \pmod p$. Since $p \bmod i < i$, that
entry is already in the table, so the loop never exponentiates.
Problem 675 cannot fold its inverses away: it needs the inverse of every odd number up to
$2 \cdot 10^7 + 1$. It computes all of them at once, as $a^{p-2}$ by one vectorised
square-and-multiply over a NumPy array, about thirty array multiplications for ten million inverses.
Problem 635 does the same for its 5.76 million denominators, one per prime, and folds an extra
factor $p$ into each so that a single inverse serves both terms of its closed form.

Geometric series are where a field pays off most. Their sum $(x^K - 1)/(x - 1)$ needs one power
and one inverse, and the ratio may itself be a fraction. Problem 711 sums arithmetico-geometric
series $\sum m x^m$ in closed form with $x = 1/2$, which modulo $10^9 + 7$ is just the residue
$2^{-1}$. The degenerate ratio that problem 520 had to handle can sometimes be ruled out instead:
problem 479's ratio is $1 - k^2$, which is $\equiv 1$ only if $p \mid k$, and every $k$ is below
$p$. A first-order linear recurrence is a geometric series in disguise, and seeing that can remove a
sequential loop. Problem 423's count obeys $G(n+1) = 6G(n) + d(n)$, with increments $d(n)$
built from binomials. Unrolled, each $d(j)$ reaches every later term multiplied by a power of 6,
and summing over $n \le L$ gives it the weight $(6^{L-j+1} - 1)/5$. The running state disappears.
What is left is a dot product of independent terms, each a few table lookups, with one inverse of
5, and it vectorises over fifty million indices where the recurrence could only be walked.

Geometric sums also nest. Problem 968 sums the weight $2^{x_1}3^{x_2}5^{x_3}7^{x_4}11^{x_5}$ over the
lattice points of a five-dimensional polytope cut out by $x_i + x_j \le X_{ij}$, about $10^{40}$ of
them. Summing out one variable between bounds that are linear in another is one geometric series.
Its two end terms are again exponentials in the remaining variables, with new bases. The weight
keeps its shape, so [Fourier–Motzkin elimination](https://en.wikipedia.org/wiki/Fourier%E2%80%93Motzkin_elimination),
split into cases by which bound is tightest, reduces every piece to a constant. Each step costs a
power and an inverse of $r - 1$, however large the bounds are. The one thing to check is that no
base reaches $r \equiv 1$, where the closed form divides by zero.

Over a prime, the *exponent* is a residue too, modulo $p - 1$, and that includes negative ones:
$a^{-k} = a^{(-k) \bmod (p-1)}$. Problem 754 multiplies Gauss factorials, and Möbius inversion
writes each as a product of factorials and powers raised to $\mu(d) = \pm 1$. Grouped by the
$O(\sqrt N)$ values of $\lfloor N/d \rfloor$, each block's exponent becomes a difference of
[Mertens](https://en.wikipedia.org/wiki/Mertens_function) values, often negative, and reducing it
modulo $p - 1$ turns the inverse powers into ordinary ones. The $d^{\mu(d)}$ factors are handled
by keeping two running products, one for $\mu = +1$ and one for $\mu = -1$. One inverse per block
then replaces one per element.

Sometimes the structure removes the inverse altogether. Problem 866's expectation recurrence has a
$1/N$ that the hexagonal factor $H(N) = N(2N-1)$ cancels exactly, so the whole computation stays
in integers. Problem 682 extracts one coefficient of a
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
derivation is a bug waiting for an input that shares a factor with it. That holds for the divisions
hidden inside a standard algorithm as well. Problem 649 needs an XOR-convolution power modulo $10^9$,
and the [Walsh–Hadamard transform](https://en.wikipedia.org/wiki/Hadamard_transform) would make it
pointwise, but its inverse divides by the length 8, which has no inverse modulo $10^9$. With eight
entries the direct convolution costs nothing and uses only $+$ and $\times$, so it is the right
choice. A fast transform is only available when the modulus can undo it. Problem 922 has a
modulus that can. It needs an XOR convolution power modulo the prime $10^9 + 7$, where dividing by
the length is a single inverse. In the transformed domain each Walsh coefficient becomes a
polynomial (the problem also carries an ordinary sum alongside the XOR), raised to the $m$-th power.
Only the tuples whose XOR is 0 are wanted, so the inverse transform is evaluated at that one point,
$S^{-1} \sum_s$, and never in full.

The [number-theoretic transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform_over_a_ring)
has the same limit. It needs a $2^k$-th root of unity, so it works modulo primes like
$998244353 = 119 \cdot 2^{23} + 1$, and not modulo $10^9 + 7$. Problem 767 needs a convolution
of length $10^5$ modulo $10^9 + 7$, and gets round that by computing the *integer* convolution
and reducing it afterwards. Each 30-bit residue is split into three 10-bit limbs. One limb product
summed over $10^5$ terms stays below $2^{37}$, far inside a double's 53-bit mantissa, so a
floating-point FFT of the limbs rounds back to exact integers. Nine limb products, gathered by
shift into five spectra, rebuild the residue. The convolution itself comes from factorials. The
problem needs $F(K) = \sum_s \binom{K}{s}^{16}$ for every $K \le k$. Writing
$\binom{K}{s}^{16} = K!^{16} \cdot u_s u_{K-s}$ with $u_s = (s!)^{-16}$ makes $F(K)$ the $K$-th
term of $u * u$, so all $k$ sums cost one transform. Inverse factorials separate a binomial
into a factor for each index, and that is what lets a convolution compute it.

Problem 922 multiplies its polynomials a third way, by
[Kronecker substitution](https://en.wikipedia.org/wiki/Kronecker_substitution). The reduced
coefficients are packed into fixed-width slots of one big integer. Each slot is wide enough that no
coefficient of the exact product can spill into its neighbour. The two integers are multiplied, and
the slots are unpacked and reduced. The big-integer library's sub-quadratic multiplication does the
convolution, with no root of unity and no floating point.

The commonest version is also the easiest to miss: "the last nine digits" means modulo $10^9$, and
$10^9$ is even. Both problems 340 and 401 end in closed forms with a small fixed denominator.
Problem 340 has the triangular numbers $b(b+1)/2$, and problem 401 has the square pyramidal numbers
$x(x+1)(2x+1)/6$ with $x$ up to $10^{15}$. Since $2$ has no inverse modulo $10^9$, the cure is to
**divide before reducing**. One of $x, x+1$ is even, and exactly one of $x, x+1, 2x+1$ is a
multiple of 3. Dividing those factors exactly leaves integers that each fit in 64 bits; only then
are they reduced and multiplied. The bluntest cure is not to reduce until the division is done.
Problem 612 counts pairs as $(T^2 - D - T)/2$ with every quantity below $10^{36}$. Python forms it
exactly, the C port in `unsigned __int128`, and the modulus is applied once, to the quotient.
Sometimes a congruence is what proves the division is exact.
Problem 764's summand is $(5a^4 + 3b^4)/8 + ab$ for odd $a, b$. Every odd fourth power is
$\equiv 1 \pmod{16}$, so the numerator is $\equiv 8 \pmod{16}$. The division by 8 is therefore
exact, and it is taken on the integer before the term is reduced modulo $10^9$.

Two more repairs complete the set. An **exact** division by a number **coprime** to the modulus
is safe even when the modulus is composite. Problem 731 divides $10^e - r$ by $3^i$ modulo
$10^{10}$ by multiplying with $3^{-i}$, which exists because 3 shares nothing with 10. Problem
506 works modulo $123454321 = 41^2 \cdot 271^2$, but its digit stream has period 6, so the terms
obey an affine recurrence $v_{n+15} = 10^6 v_n + Q$ within each residue class of $n \bmod 15$. The
only divisor its geometric sums need is $10^6 - 1 = 3^3 \cdot 7 \cdot 11 \cdot 13 \cdot 37$. That
is coprime to the modulus, so the closed form is exact and fifteen modular exponentiations
replace $10^{14}$ terms. Factor the divisor as well as the modulus before reaching for a repair. And when
the divisor $c$ is not coprime, compute modulo $c \cdot m$ and divide the residue by $c$ at the
end. If $x \equiv y \pmod{cm}$ and $c \mid x$, then $x / c \equiv y / c \pmod m$. Problem 875's
C port evaluates a Faulhaber polynomial with denominator 24 this way, modulo $24m$ in `__int128`,
with no inverse at all. The same move recovers a floor. Problem 850's answer is $\lfloor S \rfloor$
for a half-integer total $S$. Its C port carries $2S$ modulo $2m$, which keeps its parity, so
halving that residue with a floor gives $\lfloor S \rfloor \bmod m$ without a big integer.

Problem 605 needs both repairs, and finding its divisor is a modular trick in its own right. Its
probability is a fraction with denominator $(2^n - 1)^2$, $n \approx 10^8$, and the answer wants
it in lowest terms. Every common factor $g$ also divides $\gcd(n, 2^n - 1)$. The first step of
Euclid's algorithm reduces the larger argument modulo the smaller, so that gcd is
$\gcd\bigl(n, (2^n \bmod n) - 1\bigr)$. One modular exponentiation replaces a thirty-million-digit
number. Each prime of the result has its multiplicity read off modulo a high power of that prime.
Since $g$ may share a factor 5 with $10^8$, the product is formed modulo $10^8 g^2$ and divided by
$g^2$ at the end.

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

### Filtering by a residue: roots of unity

When the congruence is a condition on a *sum*, there is a filter that turns "count the things
whose total is $\equiv 0 \pmod n$" into an average. With $\omega = e^{2\pi i/n}$,

$$\frac1n \sum_{j=0}^{n-1} \omega^{js} = [\, n \mid s \,],$$

so substituting $x = \omega^j$ into a generating function and averaging keeps exactly the
exponents divisible by $n$. This is the
roots-of-unity filter (or [series multisection](https://en.wikipedia.org/wiki/Series_multisection)), and it pays off when
the substituted products have a closed form. Problem 250 kept a residue census and multiplied it
out. Problem 635 counts the $p$-element subsets of $\{1, \dots, qp\}$ with sum divisible by a prime
$p$, and here the filter collapses. Every non-trivial $\omega^j$ is again a primitive $p$-th root,
so each of the $p - 1$ non-trivial terms is the same product $\prod_r (1 + rt) = 1 + t^p$. The
count becomes $\bigl(\binom{qp}{p} + q(p-1)\bigr)/p$, one binomial per prime.

Problem 875 runs the same filter over $\mathbb{Z}/n$ to count the zeros of an eight-variable
quadratic form, and the inner sums become
[quadratic Gauss sums](https://en.wikipedia.org/wiki/Quadratic_Gauss_sum)
$G(t, n) = \sum_x e(t x^2 / n)$. Their absolute values are classical ($|G|^2 = m$ for odd $m$,
with a separate rule for powers of 2), and only $|G|^8$ enters. The count is therefore a
[Dirichlet convolution](https://en.wikipedia.org/wiki/Dirichlet_convolution) of two multiplicative
functions, and a totient sieve plus quotient blocks finish it. The pattern: a congruence condition
becomes a character sum, and the character sum has structure that the condition hid.

The filter does not need complex numbers. Problem 967 counts the $n \le 10^{18}$ for which the
distinct primes up to 120 dividing $n$ sum to a multiple of 3. Rather than average over cube roots
of unity, it computes $\sum_n x^{S(n)}$ in the group ring $\mathbb{Z}[x]/(x^3 - 1)$, where problem
250 let exponents wrap. An element is a triple of exact integer counts, one per residue. Since
$x^{S(n)}$ is multiplicative, the sum is a Dirichlet convolution over square-free divisors. The
residue modulus helps a second time. The small primes' share of $S(n)$ depends only on
$n \bmod Q$, where $Q \approx 3.2 \times 10^6$ is their product, so its partial sums come from one
periodic prefix table. The convolution then runs only over the roughly $1.4 \times 10^6$ products
of the large primes.

At $n = 2$ the filter needs no roots at all, because $\omega = -1$ and the average is over signs.
Problem 973 sums, over every composition of $n$, the XOR of its parts, and it does so bit by bit.
Bit $b$ of an XOR is set when an odd number of parts have that bit. Giving each part the sign $-1$
when its bit $b$ is set, the signed count $E$ gives the odd-parity count as
$(2^{n-1} - E)/2$, one inverse of 2. The sign is periodic in the part, so the compositions'
generating function $1/(1 - C(x))$ is rational with a sparse denominator. Each bit then costs one
four-term recurrence.

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
- Problem 659 needs $\sqrt{-1} \bmod p$, a fourth root of unity, so it exists exactly for
  $p \equiv 1 \pmod 4$. For any non-residue $c$, [Euler's criterion](https://en.wikipedia.org/wiki/Euler%27s_criterion)
  gives $c^{(p-1)/2} = -1$, so $c^{(p-1)/4}$ squares to $-1$. Trying $c = 2, 3, \dots$ finds one
  within a few tries, which is far simpler than
  [Tonelli–Shanks](https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm).

Problem 421 also shows the swap that makes such problems feasible at all: instead of factoring
$10^{11}$ numbers of up to 165 digits, exchange the order of summation and ask, per prime, how many
$n \le N$ fall in its few residue classes — the progression count from above, one division per root.
Problem 659 takes the swap one step further and *factors* every value of $4k^2 + 1$ for
$k \le 10^7$. Each prime $p \equiv 1 \pmod 4$ divides it on exactly two residue classes of $k$, so
the primes are divided out along those two progressions, a sieve over a polynomial's values rather
than over the integers. Higher powers of $p$ are found by
[Hensel](https://en.wikipedia.org/wiki/Hensel%27s_lemma)-lifting the root to $p^2, p^3, \dots$, each
lift using an inverse modulo $p$ alone, so no intermediate grows past the values being sieved.
Problem 291 turns that sieve into a primality test. It wants the primes among
$f(n) = 2n^2 + 2n + 1$, and $2f(n) = (2n + 1)^2 + 1$, so once more only $q \equiv 1 \pmod 4$ can
divide a value and each such $q$ has two classes. Striking both classes for every such
$q \le \sqrt L$ leaves the primes, with one hazard a factoring sieve does not have. A class can
contain $q$ itself, as when $f(r) = q$, and that value is prime, so striking starts at $r + q$.

A general quadratic congruence reduces to a square root by the
[quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula), read modulo $m$. It needs
only 2 (strictly, $2a$) to be a unit. Problem 457 wants the least $n$ with
$p^2 \mid n^2 - 3n - 1$ for every prime up to $10^7$. Completing the square gives
$4f(n) = (2n - 3)^2 - 13$, and 4 is a unit modulo an odd $p^2$, so the roots are
$(3 \pm r) \cdot 2^{-1}$ with $r^2 \equiv 13 \pmod{p^2}$. Whether $r$ exists modulo $p$ is a
reciprocity lookup on $p \bmod 13$. $r$ itself comes from
[Tonelli–Shanks](https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm), or from
$13^{(p+1)/4}$ when $p \equiv 3 \pmod 4$. One Newton step $r \leftarrow r - (r^2 - 13)(2r)^{-1}$
then lifts it to $p^2$. The lift fails exactly where the derivative $2r$ vanishes, at $p = 13$
itself, and there a short divisibility argument shows there is no root modulo $169$ at all. The
two exceptional primes, the one that divides 2 and the one that divides the discriminant, are the
ones to check by hand.

Cyclicity also gives the unit group useful quotients. When $r \mid p - 1$, the value
$\chi(x) = x^{(p-1)/r}$ is an $r$-th root of unity, the
[power residue symbol](https://en.wikipedia.org/wiki/Power_residue_symbol) that generalises Euler's
criterion. It names the coset of $x$ modulo the subgroup of $r$-th powers, and every coset holds
$(p-1)/r$ elements. Problem 971 counts the periodic points of $x \mapsto x^k \bmod p$ for primes
$p = 5k - 4$. Then $k - 1 = (p-1)/5$, so the map is $x \mapsto x\,(1 + \chi(x))$ with a quintic
symbol. Every element of coset $j$ is multiplied by the same $1 + \zeta^j$ and lands in one common
coset, so the functional graph on $p$ points projects onto a map of five cosets. A coset on a cycle
of that small map comes back multiplied by one fixed unit, and multiplying by a unit is a bijection,
so every element of it is periodic. A graph walk over $p$ points becomes a few exponentiations per
prime.

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

A root can do its work in the proof alone. Problem 921 computes in $\mathbb{Z}[\sqrt 5]/M$ for a
prime $M \equiv 4 \pmod 5$, so reciprocity makes 5 a residue and this is the split case. Every unit
then has order dividing $M - 1$, which licenses reducing its enormous exponents. But the code never
finds $\sqrt 5 \bmod M$. It multiplies pairs $(q, p)$ standing for $q + p\sqrt 5$, and those two
coordinates are the very integers the problem asks about.

The norm also says whether there is an order at all. It is multiplicative, so $u$ is a unit modulo
$x$ exactly when $N(u)$ is, and in problem 752 that removes every $x$ sharing a factor with 6
before any power is taken. And orders lift cheaply from primes to prime powers. Every element of
the kernel $1 + p^{k-1}R$ of reduction mod $p^{k-1}$ has order dividing $p$. So the order mod
$p^k$ is either the order mod $p^{k-1}$ or $p$ times it, and one power decides which. CRT (below)
then makes the order modulo a composite the lcm of its prime-power orders.

The element whose order you test need not even be found. Problem 437 wants the primes below $10^8$
that have a Fibonacci primitive root, a root of $x^2 - x - 1$ that is also a
[primitive root](https://en.wikipedia.org/wiki/Primitive_root_modulo_n). Finding the roots would
take a modular square root of 5 for each of about three million primes. Instead it powers the
formal root in $\mathbb{Z}_p[x]/(x^2 - x - 1)$, where $x^m$ reduces to $ax + b$. Substituting either
root $r$ gives $r^m = ar + b$. When $a \ne 0$, the power $r^{(p-1)/q}$ is 1 only for the single
residue $r = (1 - b)/a$, and only if that residue really is a root. One ring power therefore tests
both candidates at once. The failing residue is kept as the fraction $(1 - b, a)$ and compared by
cross-multiplication, so the test never needs an inverse either.

The unit group can also be the whole problem. Problem 995 wants the least $s$ for which the
[cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial)
$\Phi_p = 1 + x + \dots + x^{p-1}$ divides $1 + \sum_{d \mid s} x^d$. Substitute a primitive
$p$-th root $\zeta$. Since $\zeta^p = 1$, the exponents are only residues mod $p$, and the only
linear relation among the powers of $\zeta$ is that they sum to zero. The divisibility therefore
says the divisors of $s$ hit every non-zero residue mod $p$ exactly once. Equivalently, the sets
$\{1, q, \dots, q^e\}$, one for each prime power of $s$, *factor* the cyclic group
$(\mathbb{Z}/p)^\times$. [Hajós's theorem](https://en.wikipedia.org/wiki/Haj%C3%B3s%27s_theorem)
says that in such a factorisation one factor is a subgroup. Applying it repeatedly turns any
valid $s$ into a chain of nested subgroups, each of order dividing $p - 1$, and each prime's exponent
is fixed by its multiplicative order modulo the subgroup reached so far. The least $s$ is then a
shortest path over the divisors of $p - 1$, priced by the smallest prime of each order. A
polynomial divisibility has become a question about orders.

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
$2^{k-s} \bmod m$ at the end. Problem 674 goes further and decides the order without any numbers.
It wants the least common value of two nested expressions in an operator $\mathcal{I}(x, y)$ whose
values grow doubly exponentially. $\mathcal{I}$ is injective, so the expressions agree only if
their trees unify. It is also increasing in each argument, so the least value sets every free
variable to 0. All of that is decided on the tree. Reduction modulo $10^9$ enters only in the final
evaluation, where nothing is compared any more.

Distinctness is the same kind of question as order, because equal residues say nothing about equal
values. Problem 844 sums, for each $k$ up to $10^{18}$, the *distinct* numbers up to $10^{18}$ in the
solutions of a Markov-type equation. For $k \ge 10$ each number is a fixed polynomial in $k$, so a
few dozen [power sums](https://en.wikipedia.org/wiki/Faulhaber%27s_formula) replace the loop over
$k$. But two polynomials could still agree at some $k$, and each polynomial stops at its own cutoff.
Both are questions about values, so they are settled on exact integers: the coincidences by
[Descartes' rule of signs](https://en.wikipedia.org/wiki/Descartes%27_rule_of_signs) on each
difference, the cutoffs by binary search. The power sums run to about $10^{340}$, which big integers
handle easily, and the modulus is applied once, to the final total.

The converse is a gift: a modulus written into a *definition* is often there to simplify it. Problem
512 sums $\varphi(n^i)$ for $i = 1, \dots, n$, taken modulo $n + 1$. Modulo $n + 1$, $n \equiv -1$,
and $\varphi(n^i) = n^{i-1}\varphi(n)$, so the terms alternate in sign and cancel in pairs. Each
$f(n)$ is just $\varphi(n)$ for odd $n$ and $0$ for even $n$, and the problem becomes a sum of
totients before any code is written.

A modulus can also be evidence. Problem 479 sums powers of $(a + b)(b + c)(c + a)$ over the roots
of a cubic, roots that are complex, and then reduces the total modulo a prime. A complex number has
no residue, so the statement is promising an integer, and that promise says where to look. The
product is unchanged by permuting the roots, so
[Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas) express it through the cubic's
coefficients, and it collapses to $1 - k^2$. The roots are never found.

A practical habit follows from all this: make the modulus an input. Problems 941 and 960 take it as
a parameter in which 0 means "do not reduce". So the statement's small unreduced examples run
through the same code path as the reduced answer, and a reduction placed one level too high shows
up as a failed example. In 941 the single division, halving a middle term whose
$\binom{n}{n/2}$ is even, is an exact integer division in one mode and a multiplication by
$2^{-1} = (p + 1)/2$ in the other.

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

Variations on the same budget:

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
- **A running product is sequential, and NumPy has no modular `cumprod`.** Problems 635 and 754
  need factorials modulo a prime up to $3 \cdot 10^8$ and $10^8$. Each lays a chunk out as a
  matrix and advances every row's running product at once, one vectorised multiply-and-reduce per
  column. A short scalar pass then gives each row its carry-in. That
  [blocked prefix scan](https://en.wikipedia.org/wiki/Prefix_sum#Parallel_algorithms) still does
  $O(L)$ multiplications, but only $O(\sqrt L)$ of them at interpreter speed. It works because
  multiplication mod $p$ is associative, the same property that powers square-and-multiply.
- **Mind the sign of `%`.** In C the remainder takes the sign of the dividend, so a residue
  formed from subtractions can come out negative. Problem 463's halving recursion combines
  memoised sums with coefficients such as $-3$ and $-2$, and an intermediate can dip to about
  $-4 \times 10^9$. Its C port adds a known multiple of the modulus before reducing, where
  Python's `%` would already be non-negative.
- **A comparison can overflow too.** Not every oversized product is reduced. Problem 615's C port
  prunes a depth-first search when a candidate $V \cdot p$ exceeds a bound, and that product can
  briefly pass 64 bits. A wrapped value would look small and slip past the test. So it is formed in
  `__int128` and compared there, although nothing is ever reduced modulo anything.
- **A difference can be small when its terms are not.** Problem 839's answer is
  $\sum i f_i - \sum i a_i$, two moments near $10^{21}$ whose difference fits easily in 64 bits. Its
  C port accumulates both in `__int128` and narrows only the difference. There is a second route,
  because unsigned wraparound *is* arithmetic modulo $2^{64}$: a value built from $+$, $-$ and
  $\times$ that is known to fit comes out right however often it wraps. The word must be unsigned,
  since signed overflow is undefined in C. The $/2$ in the block sums would have to be taken before
  multiplying, because 2 has no inverse modulo $2^{64}$.

## How to reason about it

The recurring cue is a question that depends only on a remainder — *last digits*, *divisibility*,
*a count modulo a prime*, *a periodic or cyclic structure* — attached to a value too large to form
directly. When you see it:

- Reduce **early and often** — counts, and where the question allows, elements and exponents too —
  but only the quantity the statement actually reduces. A recursive state may be reduced while
  its updates are integer-linear. If a choice depends on order or distinctness, settle it before
  reducing. A modulus applied to something that looks irrational or complex promises an integer,
  so look for the symmetry that makes it one. Make the modulus a parameter, with 0 meaning exact,
  so the statement's unreduced examples test the same code.
- Searching for a number with a divisibility property? Its residue is a complete state, so search
  the $n$ residues, not the numbers. With weights, the least member of each class (an Apéry set)
  describes everything the generators cannot reach. An equation between huge sums is checked
  column by column, with the carry as the state. A fractional part $\{a/n\}$ is a residue over $n$.
- Need a **power**? Use modular exponentiation ($O(\log b)$), and shrink the exponent itself with
  Fermat, Euler or Carmichael; a periodic exponent can make a whole sequence periodic. Any
  associative product (a ring extension, a convolution, a matrix per letter of a recursive word,
  a table per block of digits joined by a factor $10^L$, an affine step that jumps a generator
  ahead) can be powered the same way. A linear recurrence unrolls into geometric weights, and
  geometric sums nest across the variables of a polytope. A value used
  both as an exponent and as a factor is needed modulo $p - 1$ **and** modulo $p$. Many powers of
  one fixed base are two table lookups each, not a loop.
- Need to **divide**? Multiply by the modular inverse — extended Euclid for any modulus, $a^{p-2}$
  for a prime one — and remember it exists only when $\gcd(a, m) = 1$. A prime modulus is a field;
  under a composite one, audit every division — including the $/2$ and $/6$ of a closed form
  modulo $10^9$, and the division inside a fast transform's inverse. An exact division by a coprime
  divisor is still safe, and a stubborn $c$ can be divided out of a residue taken modulo $cm$, or
  the exact value kept until the division is done. Where you can, defer all the divisions to a single
  inverse at the end or carry a scaled quantity ($j!\,H_j$, not $H_j$; $k!\,c_k$ for a recurrence
  that divides by $k + 1$) that needs none. A table of inverses costs $O(1)$ per entry. Over a
  prime a negative exponent is just a residue mod $p - 1$, a symmetry can be counted labelled and
  divided out once, and an irrational such as $\sqrt 5$ is usable if it has a residue.
- Need a **convolution** modulo a prime with no $2^k$-th root of unity? Split the residues into
  limbs small enough for a floating-point FFT to stay exact, or pack them into the slots of one big
  integer (Kronecker substitution), and reduce afterwards.
- Need an **order**? Start from the group order ($p - 1$; $p + 1$ for a norm-one element of
  $\mathbb{F}_{p^2}$) and strip primes while the power stays 1. Lift to $p^k$ by at most a factor
  $p$ per step, and take the lcm across a composite modulus. To test a root you cannot cheaply
  find, power the formal root in $\mathbb{Z}_p[x]/(f)$. A map that multiplies by something
  depending only on $x^{(p-1)/r}$ acts on $r$ cosets, not on $p$ points.
- Need to **count** solutions? A linear congruence's solutions are a progression (two divisions);
  the roots of $x^r \equiv 1 \pmod p$ number $\gcd(r, p - 1)$. A condition "the sum is
  $\equiv 0 \pmod n$" is a roots-of-unity filter, or exactly a group-ring sum, and a closed form
  may be hiding behind it. For a parity, the filter is a signed count. Exponent parities are vectors over $\mathbb{F}_2$, so "the product is a
  square" counts as $2^{n-r} - 1$. A
  quadratic congruence is a modular square root plus the quadratic formula, Hensel-lifted to
  $p^k$; check the primes dividing 2 and the discriminant by hand.
- Facing **several congruences** or a **composite modulus**? Combine or decompose with the Chinese
  Remainder Theorem, working prime power by prime power; solution counts multiply. If the moduli
  share a factor $d$, check that $d$ divides the difference of the residues before solving.
- Writing **C** (or any fixed-width language)? Widen every modular multiply once $m \ge 2^{32}$, and
  bound the accumulated total as well as each product, including products you only compare. Keep
  `%` away from negative operands. A result known to fit survives unsigned wraparound, so long as
  no division happens after the wrap.

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
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0303](/solutions/0303/) — Multiples with Small Digits
- ● [0304](/solutions/0304/) — Primonacci
- ● [0305](/solutions/0305/) — Reflexive Position
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ● [0319](/solutions/0319/) — Bounded Sequences
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0330](/solutions/0330/) — Euler's Number
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
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
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0427](/solutions/0427/) — $n$-sequences
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0451](/solutions/0451/) — Modular Inverses
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ● [0475](/solutions/0475/) — Music Festival
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ● [0478](/solutions/0478/) — Mixtures
- ● [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0498](/solutions/0498/) — Remainder of Polynomial Division
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ● [0506](/solutions/0506/) — Clock Sequence
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0520](/solutions/0520/) — Simbers
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0528](/solutions/0528/) — Constrained Sums
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0537](/solutions/0537/) — Counting Tuples
- ● [0539](/solutions/0539/) — Odd Elimination
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
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0612](/solutions/0612/) — Friend Numbers
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ● [0619](/solutions/0619/) — Square Subsets
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ● [0625](/solutions/0625/) — Gcd Sum
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0627](/solutions/0627/) — Counting Products
- ● [0628](/solutions/0628/) — Open Chess Positions
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ● [0635](/solutions/0635/) — Subset Sums
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ● [0659](/solutions/0659/) — Largest Prime
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0672](/solutions/0672/) — One More One
- ○ [0673](/solutions/0673/) — Beds and Desks
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ● [0688](/solutions/0688/) — Piles of Plates
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0696](/solutions/0696/) — Mahjong
- ● [0700](/solutions/0700/) — Eulercoin
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0709](/solutions/0709/) — Even Stevens
- ● [0710](/solutions/0710/) — One Million Members
- ● [0711](/solutions/0711/) — Binary Blackboard
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0726](/solutions/0726/) — Falling Bottles
- ○ [0728](/solutions/0728/) — Circle of Coins
- ● [0731](/solutions/0731/) — A Stoneham Number
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
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0767](/solutions/0767/) — Window into a Matrix II
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
- ● [0839](/solutions/0839/) — Beans in Bowls
- ○ [0840](/solutions/0840/) — Sum of Products
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0849](/solutions/0849/) — The Tournament
- ● [0850](/solutions/0850/) — Fractions of Powers
- ○ [0851](/solutions/0851/) — SOP and POS
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0858](/solutions/0858/) — LCM
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ● [0866](/solutions/0866/) — Tidying Up B
- ○ [0871](/solutions/0871/) — Drifting Subsets
- ○ [0873](/solutions/0873/) — Words with Gaps
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ● [0892](/solutions/0892/) — Zebra Circles
- ○ [0902](/solutions/0902/) — Permutation Powers
- ○ [0903](/solutions/0903/) — Total Permutation Powers
- ○ [0909](/solutions/0909/) — L-expressions I
- ○ [0910](/solutions/0910/) — L-expressions II
- ● [0912](/solutions/0912/) — Where are the Odds?
- ○ [0916](/solutions/0916/) — Restricted Permutations
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ● [0921](/solutions/0921/) — Golden Recurrence
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0923](/solutions/0923/) — Young's Game B
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0939](/solutions/0939/) — Partisan Nim
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ● [0960](/solutions/0960/) — Stone Game Solitaire
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0968](/solutions/0968/) — 5D Summation
- ● [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0973](/solutions/0973/) — Random Dealings
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0976](/solutions/0976/) — XO Game
- ○ [0977](/solutions/0977/) — Iterated Functions
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ● [0984](/solutions/0984/) — Knights and Horses
- ○ [0989](/solutions/0989/) — Fibonacci Sum
- ● [0990](/solutions/0990/) — Addition Equations
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ● [0994](/solutions/0994/) — Counting Triangles
- ● [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ● [0996](/solutions/0996/) — Overtakes
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ● [1001](/solutions/1001/) — Connections I
- ○ [1004](/solutions/1004/) — Balanced Integer
- ● [1006](/solutions/1006/) — Fibonacci Subwords
- ● [1007](/solutions/1007/) — Alternating Difference
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
