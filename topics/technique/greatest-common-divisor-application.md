<!-- tags: [greatest-common-divisor-application] -->
<!-- status: final -->
# Greatest common divisor (application)

The [greatest common divisor](https://en.wikipedia.org/wiki/Greatest_common_divisor) is usually met
as something you *compute*. In the problems below it is more often something you *know*: a fact about
a pair of integers that decides whether an enumeration double-counts, what a canonical key looks
like, which residues a step can reach, and how many solutions an equation has. The
[Euclidean algorithm](/topics/technique/euclidean-algorithm) page covers the computation — three
lines, logarithmic, effectively free. This page is about the modelling above it: what having the gcd
lets you *say*. In one of these problems the gcd decides the answer and never appears in the code at
all.

## The identities worth knowing by heart

Everything below is an application of one of these, so they are worth stating once:

| identity | what it buys |
| --- | --- |
| $\gcd(a, b) = \gcd(a, b - a) = \gcd(a, b \bmod a)$ | one gcd can answer a question phrased about a different pair |
| $\gcd(ka, kb) = k \gcd(a, b)$ | scaling and primitivity: every object is a primitive one times its gcd |
| $\gcd(a,b) \cdot \operatorname{lcm}(a,b) = ab$ | the lcm, and with it the realignment of two cycles |
| $\{ks \bmod m\} = $ multiples of $\gcd(s, m)$ | which residues a repeated step can reach |
| $\gcd(a,b) = 1 \wedge a \mid c \wedge b \mid c \Rightarrow ab \mid c$ | why coprime factors can be handled independently |

## Coprimality is a bijection condition

The most common reason a gcd appears inside a loop is that it turns a parametrisation into a
*bijection*. Problem 143 needs every pair $(a,b)$ with $a^2 + ab + b^2$ a perfect square; rather than
testing pairs it generates them from the Eisenstein analogue of Euclid's formula, over $m > n > 0$
with $\gcd(m, n) = 1$ and $(m - n) \not\equiv 0 \pmod 3$. Those two side conditions are not
decoration — they are exactly what makes each primitive triple appear once. Every other pair is then
$k$ times a primitive one, by $\gcd(ka, kb) = k\gcd(a,b)$, so the non-primitive cases come for free
from a multiplication instead of a search. Drop the guard and you emit each object once per scaling,
and the count is wrong in a way that is very hard to see from the output.

The better move, when you can make it, is not to test coprimality but to *construct* it. Problem 157
enumerates coprime pairs $(s,t)$ whose product divides $10^n$; since the only primes in play are 2
and 5, each prime is assigned wholly to $s$, wholly to $t$, or to neither, and coprimality holds by
construction. No candidates are generated only to be rejected. That is the general pattern: when the
prime support of your objects is small and known, partition the primes rather than filter the pairs.

## One gcd can settle several conditions

Problem 127 asks for triples with $a + b = c$ and all three pairs coprime — apparently three tests.
By the subtraction identity they collapse to one:

```python
# gcd(a, b) = gcd(a, c - a) = gcd(a, c), and gcd(b, c) = gcd(c - a, c) = gcd(a, c)
if math.gcd(a, c) != 1:
    continue
```

A related trick is coprimality against a *constant*. Problem 130's scan opens with
`gcd(n, 30) != 1`, which eliminates the multiples of 2, 3 and 5 in a single call — a compact way to
say "$n$ has no small prime factor", and the same idea the problem's own statement uses when it
requires $\gcd(n, 10) = 1$ (the condition under which $1/n$ has a purely periodic decimal expansion,
so that a repunit divisible by $n$ exists at all). Whether one gcd beats three modulo tests depends
on the constant and the language; that it states the intent in one place is the durable win.

The same identity has a purely mechanical use. In problem 5's C solution the running lcm outgrows a
64-bit word and is carried as a small bignum, but the gcd never needs to be: $\gcd(a, y) = \gcd(a
\bmod y, y)$ reduces the big operand to a machine word first, and the ordinary word-sized loop
finishes the job. A gcd against a huge number is a remainder away from a gcd against a small one.

## The reachable set of a step is the multiples of its gcd

Stepping by $s$ in $\mathbb{Z}/m$ visits exactly the multiples of $g = \gcd(s, m)$, and there are
$m/g$ of them; the walk covers everything precisely when $s$ and $m$ are coprime. Problem 120 turns
on this and nothing else. A binomial reduction collapses its remainder to $a \cdot (2n \bmod a)$, so
the question becomes which residues $2n \bmod a$ can attain — the multiples of $\gcd(2, a)$. For odd
$a$ that is every residue and the maximum is $a - 1$; for even $a$ only the even ones survive and the
maximum is $a - 2$. The whole problem is then a parity test in a loop, and the finished code calls no
gcd at all. This is the cleanest example in the stack of a gcd doing its work at the desk rather than
at runtime.

The cyclic reading of the same fact is the lcm: two cycles of lengths $a$ and $b$ realign after
$\operatorname{lcm}(a,b)$ steps, which is why the identity in the table above is the one you reach
for whenever periods have to be combined.

## Divide by the gcd to get a canonical key

Dividing a tuple through by the gcd of its parts, then fixing a sign convention, makes equal objects
into equal keys — which is how "count the distinct things" becomes "put them in a set". Three
problems here do it with three different shapes of tuple:

- Problem 165 represents an intersection point as an integer triple $(x, y, d)$ standing for
  $(x/d, y/d)$, reduced by the gcd of all three with $d > 0$. Distinct geometric points then
  correspond one-to-one with distinct triples, and the answer is a set size.
- Problem 259 normalises every rational its interval DP produces to lowest terms with a positive
  denominator, so that values reached by different expressions collapse into one set entry rather
  than accumulating as duplicates.
- Problem 184 divides a lattice point by the gcd of its coordinates to get its primitive direction,
  bucketing every point on one ray together — which is what makes its collinear and antipodal cases
  countable exactly.

Two things make this work. `math.gcd` has been variadic since Python 3.9, so a three-part key is one
call; and the arithmetic must be *exact*. A canonical form is only as trustworthy as the equality
test underneath it, and floating point has no such test — this is precisely why these solutions keep
integer numerators and denominators instead of dividing.

## When the gcd is the quantity

Sometimes it is not a filter or a normaliser but the number you are after.

Problem 91 counts right triangles on a lattice grid, and $m = \gcd(x, y)$ supplies two things at
once: the primitive perpendicular step $(-y/m, x/m)$, and how far that step fits inside the grid.
Both divisions are exact *because* $m$ is the gcd — the public solution says so in one expression:

```python
min(x * m // y, m * (coordinate_limit - y) // x)
for x in range(1, coordinate_limit + 1)
for y in range(1, coordinate_limit)
for m in [math.gcd(x, y)]
```

Problem 182 is the purest case: the number of unconcealed messages for an RSA exponent $e$ is
$(1 + \gcd(e - 1, p - 1))(1 + \gcd(e - 1, q - 1))$ — a fixed-point count that *is* a product of gcds,
tabulated rather than tested. And problem 183 uses the gcd to answer a question about decimals: the
denominator of $N/k$ in lowest terms is $k / \gcd(N, k)$, and the fraction terminates exactly when
that denominator's only prime factors are 2 and 5. Reduce, strip 2s and 5s, check for 1.

Problem 545 shows the lcm in the same role, as a *stride*: every $k$ it cares about is a multiple of
the lcm of a small set, so it iterates $k = \text{step} \cdot t$ instead of every $k$ — shrinking the
search by a factor of the step, and making a later membership check redundant because the stride
already guarantees it. Problem 5 is the same identity at its simplest, folded across a range:

```python
functools.reduce(lambda x, y: x * y // math.gcd(x, y), range(2, n + 1), 1)
```

In Python that intermediate product is harmless. In C, write it as `a / gcd(a, b) * b` — dividing
first — or the product overflows before the division ever runs.

## How to reason about it

- **A gcd in the problem statement is a hint about structure, not an instruction.** It usually marks
  a primitivity or coprimality condition that has consequences — a bijection, a subgroup, a period —
  and those consequences are where the algorithm comes from. Problems 127, 130 and 182 all state a
  gcd condition; none of them wants you to simply evaluate it as written.
- **Construct, don't filter, when the primes are known.** Testing $\gcd(s,t)=1$ over all pairs is
  $O(\text{pairs})$; assigning each prime to one side is $O(\text{results})$. The gap is the whole
  cost of problem 157.
- **Prefer exact integers for any canonical form.** Reduce by the gcd, force the sign onto one
  component, and only then hash or compare. A key normalised in floating point is not a key.
- **Watch the degenerate inputs.** $\gcd(0, n) = n$ and $\gcd(0, 0) = 0$ — the second will divide by
  zero if you normalise blindly, and the origin is exactly the point a lattice sweep will hand you.
  Python's `math.gcd` returns a non-negative result; a hand-written C loop does not, since `%` takes
  the sign of the dividend, so take absolute values on entry.
- **Reduce before coding.** Problem 120 is the argument for it: the gcd fact that fixes its answer is
  a line of reasoning on paper, and the code that survives is a parity test. If a gcd appears in
  every iteration of your loop, ask what it would tell you if you evaluated it symbolically once.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0127](/solutions/0127/) — abc-hits
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0165](/solutions/0165/) — Intersections
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0545](/solutions/0545/) — Faulhaber's Formulas

<!-- /problems -->
