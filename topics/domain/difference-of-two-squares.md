<!-- tags: [difference-of-two-squares] -->
<!-- status: final -->
# Difference of two squares

The [difference of two squares](https://en.wikipedia.org/wiki/Difference_of_two_squares) is
the factorisation $a^2 - b^2 = (a - b)(a + b)$. It is a one-line identity, but in integer problems it
does a lot of work. It turns "$n$ is a difference of two squares" into "$n$ has a factor pair of the
same parity", so *counting representations* becomes *counting divisors*. It also explains which
numbers can be represented at all. The solved problems below use it to count tile layouts (174), to
count right triangles with a given leg (176), and, in its cubic form, to pin down a family of primes
(131).

## The idea — representations are factor pairs

Set $u = a - b$ and $v = a + b$. Then $n = uv$ and $a = (u+v)/2$, $b = (v-u)/2$, so $a, b$ are integers exactly
when **$u$ and $v$ have the same parity**. That gives a bijection:

$$\{(a, b) : a > b \ge 0,\quad a^2 - b^2 = n\} \;\longleftrightarrow\; \{(u, v) : uv = n,\quad u \le v,\quad u \equiv v \pmod 2\}.$$

Everything follows from the parity condition:

| $n \bmod 4$ | factor pairs of equal parity | representable? |
|---|---|---|
| odd | every pair is odd–odd | yes, $\lceil \tau(n)/2 \rceil$ ways (counting $b = 0$ when $n$ is square) |
| $\equiv 2$ | one factor even, one odd, always | **never** |
| $\equiv 0$ | both even: $u = 2u'$, $v = 2v'$ with $u'v' = n/4$ | yes, as many as the factor pairs of $n/4$ |

So the numbers that are *not* differences of two squares are exactly those $\equiv 2 \pmod 4$
([OEIS A016825](https://oeis.org/A016825)), and the number of representations is a
[divisor](/topics/domain/divisor-function) count. A related identity is that consecutive squares differ by
odd numbers, $(b+1)^2 - b^2 = 2b + 1$, and the step $a \to a + 2$ adds $4a + 4$. Those increments
let a loop walk differences of squares without multiplying.

The same move works for higher powers: $a^3 - b^3 = (a - b)(a^2 + ab + b^2)$, and for consecutive
cubes it gives $3a^2 + 3a + 1$. The quartic difference factors twice:
$x^4 - y^4 = (x - y)(x + y)(x^2 + y^2)$.

## Three uses across the problems

**174, hollow square laminae: enumerate the pairs, tally the totals.** A lamina is an $a \times a$
square with a centred $b \times b$ hole. Symmetry forces $a \equiv b \pmod 2$, and it uses
$t = a^2 - b^2$ tiles. "How many laminae use $t$ tiles" is the number of same-parity factor pairs
of $t$, but the solution never factors anything. It runs the bijection the other way: walk every
$(b, a)$ with $a = b + 2, b + 4, \dots$, add the difference incrementally ($t \mathrel{+}= 4a + 4$),
and increment `counts[t]`. The thinnest ring for hole $b$ uses $4b + 4$ tiles, which bounds the
outer loop, and the total work is the number of laminae, $O(L \log L)$. A pass over the count
table then gives how many $t$ have each type.

**176, common cathetus: a leg's triangles are the factor pairs of its square.** For a right
triangle with leg $L$, $L^2 = c^2 - b^2 = (c - b)(c + b)$. By the table, the number of triangles is
$(\tau(L^2) - 1)/2$ for odd $L$, and $(\tau((L/2)^2) - 1)/2$ for even $L$, after dividing out the
forced factor of 2 from each side. The statement's example checks it: $L = 12$, $\tau(36) = 9$, giving
4 triangles. Asking for *exactly* $N$ triangles becomes $\tau(M^2) = 2N + 1$, and the smallest
such $M$ comes from a search over the factorisations of $2N + 1$, with exponents placed in
non-increasing order on increasing primes, the same argument as for
[highly composite numbers](/topics/domain/highly-composite-number). See
[cathetus](/topics/domain/cathetus).

**131, prime cube partnership: the cubic difference.** $n^3 + n^2p = n^2(n + p)$ is a cube when
$n = a^3$ and $n + p = (a+1)^3$. Then $p$ is the difference of consecutive cubes,
$(a+1)^3 - a^3 = 3a^2 + 3a + 1$, so the qualifying $p$ are the
[cuban primes](/topics/domain/cuban-prime). The search becomes one quadratic and one primality test per
$a \le \sqrt{L/3}$. Factoring the difference is again what turned an open condition into a
one-parameter family.

**291, Panaitopol primes**, not yet solved here, asks when $(x^4 - y^4)/(x^3 + y^3)$ is prime. The
first step is the quartic factorisation above, which cancels against $x^3 + y^3 = (x+y)(x^2 - xy + y^2)$.

## Python and C

- **174**: Python keeps the tallies in an `array('I')`, compact 32-bit unsigned counters rather than
  a list of `int` objects, and counts qualifying buckets with a generator. C `calloc`s an
  `unsigned int` array. Each version maintains $t$ by adding $4a + 4$ rather than computing $a^2 - b^2$.
- **176**: the search over factorisations of $2N + 1$ tries branches like a single factor
  $f = 2N + 1$, which produces $2^{N}$, a number with thousands of digits, before rejecting it.
  Python's `int` handles that without effort. C runs the whole recursion in GMP (`mpz_pow_ui`, `mpz_cmp`) for the same reason.
- **131**: the candidates stay small, but Miller–Rabin squares residues near $p$, so C promotes
  each modular product to `__int128`. Python's `pow(a, d, n)` needs nothing.

## How to reason about it

- **See $a^2 - b^2$, think $(a-b)(a+b)$.** Squares that differ by a target, such as triangle legs, tile
  rings or $c^2 - b^2$, are factor pairs in disguise.
- **Check parity first.** $n \equiv 2 \pmod 4$ has no representation. For $n \equiv 0 \pmod 4$,
  divide out the forced 2s and count pairs of $n/4$.
- **Count representations with $\tau$.** The number of ways is about half the divisor count, so
  questions like "exactly $N$ ways" become questions about exponent patterns.
- **To tabulate many $n$, enumerate pairs rather than factoring each $n$.** A double loop over
  $(a, b)$ with incremental differences fills a count table in $O(L \log L)$ (174).
- **Try the same factorisation on cubes and fourth powers.** Differences of consecutive cubes, and
  $x^4 - y^4$, factor just as usefully.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ○ [0291](/solutions/0291/) — Panaitopol Primes

<!-- /problems -->
