<!-- tags: [geometric-progression] -->
<!-- status: final 2026-10-19T06:42Z -->
# Geometric progression

A [geometric progression](https://en.wikipedia.org/wiki/Geometric_progression) is a sequence
with a constant ratio between consecutive terms: $a, ar, ar^2, \dots$. Its *sum* is the
[geometric series](/topics/technique/geometric-series), which has its own page. This page is about
the progression itself: what integer progressions look like, how to parametrise them, and why
their exponential growth makes them cheap to enumerate. In the solved problems below, a progression
is the hidden structure in a division (141), a factor of a sequence whose sum must be inverted
(235), and the digits of a repunit (346).

## The idea — integer progressions have a rigid shape

Three facts carry most of the weight.

**The middle term is the geometric mean.** Three positive numbers $x < y < z$ are consecutive terms
of a progression iff $y^2 = xz$. That one equation is usually how a problem states, or hides, the
condition.

**An integer progression with rational ratio is fully parametrised.** Write the ratio in lowest terms
as $p/q$ with $\gcd(p, q) = 1$. Then $a \cdot (p/q)^i$ is an integer for $i = 0, \dots, m-1$ only if
$q^{m-1} \mid a$. So every $m$-term integer progression is

$$k\,q^{m-1},\quad k\,q^{m-2}p,\quad \dots,\quad k\,p^{m-1} \qquad (k \ge 1,\quad \gcd(p,q) = 1).$$

For three terms that is $kq^2, kpq, kp^2$. Enumerating coprime $(p, q)$ and a scale $k$ visits each
progression exactly once. That replaces a search for triples satisfying $y^2 = xz$ with a
direct construction.

**Growth bounds the enumeration.** With ratio $r > 1$ the $m$-th term is $ar^{m-1}$, so below a limit
$L$ there are only $O(\log_r L)$ terms. If the progression needs at least $m$ terms, the ratio is
bounded by $L^{1/(m-1)}$. Generating the terms by repeated multiplication, $t \leftarrow t \cdot r$, is
both the cheapest way to produce them and a built-in stopping test.

## Three appearances across the problems

**141, square progressive numbers: parametrise the hidden progression.** $n$ divided by $d$ has
quotient $q$ and remainder $r$ in a geometric progression, in some order. The remainder is less
than the divisor, so it is the smallest of the three. That fixes the order, and the
parametrisation above gives $r = kb^2$, $d = kab$, $q = ka^2$ for a coprime ratio $a/b > 1$.
Substituting into $n = dq + r$ gives a closed form,
$n = k^2a^3b + kb^2$. The search becomes a sweep over $(a, b, k)$, where $a^3 < L$ bounds the
ratio at the cube root and the quadratic in $k$ gives its range directly. Each $n$ is then tested
for being a perfect square, with a set to merge squares reached from more than one triple. Two
solution indices differ only in which of $a, b$ is the outer loop.

**235, an arithmetic geometric sequence: invert in the ratio.** The terms
$(900 - 3k)\,r^{k-1}$ multiply an arithmetic progression by a geometric one
([arithmetico-geometric sequence](/topics/domain/arithmetico-geometric-sequence)), and the problem
asks which ratio $r$ makes the 5000-term sum equal $-6 \times 10^{11}$. The sum has a closed form
(see [geometric series](/topics/technique/geometric-series) for the derivation of both pieces), so
the task is a root-find *in the ratio*. The progression's growth is what makes it well-conditioned.
$r^{5000}$ amplifies any change in $r$ so strongly that the sum moves about $3 \times 10^{15}$ per
unit of $r$, and bisection pins twelve decimals easily. The solution arranges the closed form as
$r^n \cdot \text{high} + \text{low}$ so the one huge factor appears in a single product, which
avoids [catastrophic cancellation](/topics/technique/catastrophic-cancellation).

**346, strong repunits: a progression as the digits of a number.** A base-$b$ repunit with $k$ ones
is $1 + b + \dots + b^{k-1}$, the sum of a progression with ratio $b$. Every $N \ge 3$ is already
$11$ in base $N - 1$, so "a repunit in two bases" means "a repunit with at least three digits in
some base". The growth bound does the rest. The smallest three-digit repunit is $b^2 + b + 1$, so
only bases up to about $\sqrt L$ matter, and within a base the next repunit is
$t \leftarrow tb + 1$: append a digit, extend the progression by one term. That is
[Horner's method](/topics/technique/horners-method) applied to all-ones digits.

The unsolved problems on the list use the same parametrisation. In **370** the sides of a
triangle satisfy $b^2 = ac$, so they are $kq^2, kpq, kp^2$, constrained by the triangle inequality. In **518**, $a+1, b+1, c+1$
are consecutive terms of a progression.

## Python and C

- **141**: both deduplicate squares reached by several triples. Python uses a `set`, and C a
  65536-bucket chained hash table that it frees while summing. The quadratic bound on $k$ has
  discriminant $b^4 + 4a^3b(L-1)$, about $4 \times 10^{24}$, so C computes it in `__int128` with a
  corrected float-seeded integer root. Python just calls `math.isqrt`.
- **235**: Python bisects in `decimal` at 80 significant digits. $r^n$ can then grow past any
  float range, and rounding to 12 places is a `quantize`. C uses `long double`, about 19 digits,
  which the sensitivity argument shows is ample. If `powl` overflows during the bracket search, it
  returns a signed infinity, so the sign test still works.
- **346**: Python collects repunits in a `set` seeded with 1. C fills a growable array, `qsort`s it,
  and sums while skipping equal neighbours. The doubling `realloc` keeps appends amortised $O(1)$.

## How to reason about it

- **Translate "in geometric progression" into $y^2 = xz$, then parametrise.** Write the ratio in
  lowest terms as $p/q$, so an $m$-term integer progression is $k q^{m-1}, \dots, k p^{m-1}$, and
  enumerate coprime pairs and the scale.
- **Use ordering facts to fix the ratio's direction.** A remainder is smaller than its divisor (141),
  and triangle sides obey the triangle inequality (370). Each such fact removes a case.
- **Bound by growth.** A progression of $m$ terms below $L$ has ratio at most $L^{1/(m-1)}$. Three
  terms give the square root, and 141's cube makes it the cube root. The loops are small.
- **Generate terms by multiplication, not powers.** $t \leftarrow t \cdot r$ (or $tb + 1$ for
  repunits) is exact, cheap, and stops naturally at the limit, with no overflow past the next term.
- **Deduplicate.** Different parameter triples can produce the same number (141, 346). Collect into
  a set, or sort and skip repeats.
- **For sums, see the series page.** Once the question is about $\sum ar^i$ rather than the terms,
  the closed form and its division by $r - 1$ are covered on
  [geometric series](/topics/technique/geometric-series).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0346](/solutions/0346/) — Strong Repunits
- ○ [0370](/solutions/0370/) — Geometric Triangles
- ○ [0394](/solutions/0394/) — Eating Pie
- ○ [0479](/solutions/0479/) — Roots on the Rise
- ○ [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0542](/solutions/0542/) — Geometric Progression with Maximum Sum
- ○ [0770](/solutions/0770/) — Delphi Flip
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0894](/solutions/0894/) — Spiral of Circles

<!-- /problems -->
