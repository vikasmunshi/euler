<!-- tags: [golden-ratio] -->
<!-- status: final 2026-10-28T08:05Z -->
# Golden ratio

The [golden ratio](https://en.wikipedia.org/wiki/Golden_ratio) $\varphi = (1 + \sqrt5)/2 \approx
1.618$ is the positive root of $x^2 = x + 1$. That one equation is why it keeps turning up in
problems that never mention it. It is the growth rate of the
[Fibonacci sequence](/topics/domain/fibonacci-sequence), so it controls the *size* of Fibonacci
numbers. It is the fundamental unit of the ring $\mathbb{Z}[\varphi]$, so it controls the
solutions of Pell equations in $\sqrt5$. And it can serve as the radix of a positional number
system, so it controls the *digits* of numbers written in base $\varphi$. The three solved
problems below use one face each: 104 measures a Fibonacci number by its logarithm, 138 rides a
Pell recurrence whose step is a power of $\varphi$, and 473 counts palindromes in base $\varphi$.
Seeing that all three are the same number is what lets each one be reduced, rather than searched.

## The idea — one quadratic, three readings

Everything follows from $\varphi^2 = \varphi + 1$ and its conjugate root
$\psi = 1 - \varphi = -1/\varphi \approx -0.618$. Multiply the equation by $\varphi^{n-1}$ and
induct, and every power collapses to a linear form with Fibonacci coefficients:

$$\varphi^n = F_n\,\varphi + F_{n-1}, \qquad \psi^n = F_n\,\psi + F_{n-1}.$$

Subtracting the two gives [Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Closed-form_expression),
and adding them gives the [Lucas numbers](/topics/technique/lucas-number):

$$F_n = \frac{\varphi^n - \psi^n}{\sqrt5}, \qquad L_n = \varphi^n + \psi^n, \qquad
2\varphi^n = L_n + F_n\sqrt5.$$

Three facts carry the problems.

- **$|\psi| < 1$, so $\psi^n$ vanishes.** $F_n$ is the nearest integer to $\varphi^n/\sqrt5$,
  and the error shrinks geometrically. For magnitudes, a Fibonacci number *is* a power of
  $\varphi$.
- **$\varphi\psi = -1$, so $\varphi$ is a unit.** Its [norm](https://en.wikipedia.org/wiki/Field_norm)
  in $\mathbb{Q}(\sqrt5)$ is $-1$: multiplying by $\varphi$ is invertible inside
  $\mathbb{Z}[\varphi]$ and preserves $|a^2 - 5b^2|$ up to sign. Every unit of that ring is
  $\pm\varphi^k$, which is why every Pell-type equation in $\sqrt5$ is solved by powers of
  $\varphi$.
- **Every element of $\mathbb{Z}[\varphi]$ is $a + b\varphi$ with integer $a, b$.** That includes
  negative powers, since $\varphi^{-1} = \varphi - 1$. So any finite sum of powers of $\varphi$ is
  held *exactly* as a pair of integers (equivalently $\tfrac12(a + b\sqrt5)$, a
  [quadratic irrational](/topics/technique/quadratic-irrational-number)), and it is an ordinary
  integer exactly when the $\sqrt5$ part cancels.

The [continued fraction](/topics/domain/continued-fraction) $\varphi = [1; 1, 1, 1, \dots]$ is a
fourth reading of the same equation. Its convergents are ratios of consecutive Fibonacci numbers,
and since the partial quotients are as small as they can be, $\varphi$ is the irrational that rational
numbers approximate *worst* ([Hurwitz's theorem](https://en.wikipedia.org/wiki/Hurwitz%27s_theorem_(number_theory))).
Games built on the Euclidean algorithm, such as the Euclid game behind Problem 325, switch from
winning to losing at a pile ratio of exactly $\varphi$ for that reason.

## Face 1 — the golden ratio as a magnitude

**Problem 104** asks for the first Fibonacci number whose first nine and last nine digits are
both [pandigital](/topics/domain/pandigital-number). The numbers involved have tens of thousands
of digits, so building them in full inside the search loop is the trap. The two ends decouple.
The tail is $F_k \bmod 10^9$, which the recurrence maintains in a 64-bit word because it is
linear ([modular arithmetic](/topics/domain/modular-arithmetic)). The head comes from the
[logarithm](/topics/domain/common-logarithm). Since $\psi^k/\sqrt5$ is negligible,

$$\log_{10} F_k \approx k\log_{10}\varphi - \log_{10}\sqrt5,$$

and the leading nine digits are $\lfloor 10^{\,8 + \{\log_{10} F_k\}} \rfloor$, where $\{\cdot\}$ is
the fractional part. Each step is $O(1)$ on both ends. Testing the cheap tail first and the
logarithm only when the tail passes keeps the floating-point work almost entirely out of the loop.

The same estimate turns public **Problem 25** (the first Fibonacci number with $n$ digits) into
a [closed form](/topics/technique/closed-form-expression). $F_k$ has
$\lfloor k\log_{10}\varphi - \log_{10}\sqrt5 \rfloor + 1$ digits, so the index can be solved for
directly. The published solution loops over big integers instead, which is the honest
"generate and test" version and still fast at $n = 1000$:

```python
a, b = (1, 1)
i = 2
while b < 10 ** (n - 1):
    a, b = (b, a + b)
    i += 1
```

The pitfall is precision. A `double` carries about 16 significant digits. Of those,
$k\log_{10}\varphi$ spends five on the integer part when $k$ is in the hundreds of thousands,
which leaves about eleven for the fractional part. Nine digits of head fit, but not by much. A
version that wanted, say, fifteen leading digits at the same $k$ would need extended precision,
or a Fibonacci recurrence carried in floating point and renormalised.

## Face 2 — the golden ratio as a unit

**Problem 138** asks for isosceles triangles whose height differs from the base by one. Halving
the triangle with the [Pythagorean theorem](/topics/domain/pythagorean-theorem) and
[completing the square](https://en.wikipedia.org/wiki/Completing_the_square) turns the condition
into the negative [Pell equation](/topics/technique/pells-equation) $x^2 - 5y^2 = -1$, with the
leg $L = y$. That reduction is the usual [Pell equation in disguise](/topics/number-theory/pells-equation-in-disguise).
The golden ratio is what explains its solution set. The fundamental solution is
$2 + \sqrt5$, and

$$2 + \sqrt5 = \varphi^3, \qquad 9 + 4\sqrt5 = \varphi^6.$$

Every solution of $x^2 - 5y^2 = \pm 1$ is a power of $\varphi^3$, with the sign alternating
because $\varphi^3$ has norm $-1$. Stepping by $\varphi^6$ keeps only the $-1$ solutions. That is
the recurrence $(x, y) \mapsto (9x + 20y,\ 4x + 9y)$, which visits only the solutions that can be
triangles. Read through $2\varphi^n = L_n + F_n\sqrt5$, it also says the legs are (halved)
Fibonacci numbers at evenly spaced indices. Each new triangle is about $\varphi^6 \approx 17.9$
times the last, so the twelve the problem wants take a dozen steps. A larger $n$ pushes the legs
past 64 bits, which is a job for [arbitrary-precision arithmetic](/topics/technique/arbitrary-precision-arithmetic):
Python's native integers, or a small base-$10^9$ big-integer type in C.

## Face 3 — the golden ratio as a radix

In [base $\varphi$](https://en.wikipedia.org/wiki/Golden_ratio_base) the digits are 0 and 1,
the place values are $\varphi^k$ for integer $k$, and no two adjacent digits are both 1. The
identity $\varphi^{k+1} + \varphi^k = \varphi^{k+2}$ rewrites `011` as `100`, so the rule is
exactly what makes the representation unique. It is the same rule, for the same reason, as
[Zeckendorf's theorem](/topics/domain/zeckendorfs-theorem), where $F_{k+1} + F_k = F_{k+2}$ makes
each positive integer a unique sum of non-consecutive Fibonacci numbers. The two systems are one
idea with different place values. The Zeckendorf page covers the integer side; this one covers
what happens when the place values are irrational.

**Problem 473** sums the integers up to $N$ whose base-$\varphi$ representation is a palindrome.
Because the point is part of the string, a palindrome mirrors exponent $k$ onto $-(k+1)$, so it
is a sum of mirrored pairs $\varphi^k + \varphi^{-(k+1)}$ over a non-adjacent set of $k \ge 1$
(plus the lone palindrome $1$). Written as $\tfrac12(a + b\sqrt5)$ with Lucas and Fibonacci
coefficients, each pair contributes a $\sqrt5$ coefficient whose sign alternates with the parity
of $k$. The number is an integer exactly when those coefficients cancel. Counting subsets is
hopeless, since there are about Fibonacci-many of them. But the coefficients grow like
$\varphi^k$, so once a large pair is chosen only a narrow band of smaller pairs can restore the
balance. A [depth-first search](/topics/technique/depth-first-search) from the largest pair down,
with [branch and bound](/topics/technique/branch-and-bound) cuts on the remaining reachable
balance and on the running value, makes the search output-sensitive.

Two details are general lessons. The pruning bound on the value may use floating point, because
it only discards branches. The decision "is this an integer?" must not, because an
irrational sum that is nearly an integer is exactly the case that floats get wrong. Acceptance
uses the exact integer pair, the point of [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
And the doubled rational parts reach about $4 \times 10^{18}$, close to $2^{62}$, while totals
for larger $N$ pass $2^{64}$. So the C port keeps its running values in
[`__int128`](/topics/technique/int128), a limit Python never shows.

## How to reason about it

- **See $\sqrt5$, think $\varphi$.** A Pell equation $x^2 - 5y^2 = \pm 1$ or $\pm 4$, a
  recurrence with characteristic polynomial $x^2 - x - 1$, a ratio that tends to $1.618$: each is
  the golden ratio. Its unit structure tells you the full solution set and how fast it grows.
- **For size, use Binet; for value, use the recurrence.** $\varphi^n/\sqrt5$ gives a Fibonacci
  number's digit count and leading digits in $O(1)$. It never gives its exact value or its low
  digits. Those come from the recurrence, mod $m$ or in big integers.
- **Represent $\mathbb{Z}[\varphi]$ as integer pairs.** $a + b\varphi$, or $\tfrac12(a + b\sqrt5)$
  to keep the Lucas/Fibonacci form, makes sums of powers of $\varphi$, including negative ones,
  exact. Use floats only as a bound, never as the test.
- **Non-adjacent 1s mean a Fibonacci-like count.** Whether the place values are $F_k$ or
  $\varphi^k$, the number of valid digit strings of length $k$ is itself Fibonacci, so a search
  over them needs pruning or a digit DP. Plain enumeration grows like $\varphi^k$.
- **Mind the growth in C.** Anything that multiplies by $\varphi^c$ per step outgrows 64 bits
  after about $90/c$ steps. Plan for `__int128` or a big-integer type before the numbers arrive,
  not after they overflow.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ● [0473](/solutions/0473/) — Phigital Number Base
- ○ [0691](/solutions/0691/) — Long Substring with Many Repetitions
- ○ [0921](/solutions/0921/) — Golden Recurrence
- ○ [0989](/solutions/0989/) — Fibonacci Sum

<!-- /problems -->
