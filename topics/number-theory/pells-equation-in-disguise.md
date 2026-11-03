<!-- tags: [pells-equation, recurrence-relation-application, pythagorean-triple, diophantine-equation] -->
<!-- status: final -->
# Pell equation in disguise

Some Euler problems are about a probability, some about triangles, some about tiling a floor, and
one about a generating function. None of them mentions
[Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation). Yet golden nuggets (137, 140),
near-equilateral and near-isosceles triangles (94, 138), Pythagorean tiles (139), the
almost-right triangles (223, 224), the disc-drawing probability (100) and the counter-swapping
puzzle (321) all reduce to $X^2 - D Y^2 = N$ with $D \in \{2, 3, 5\}$ and a tiny $N$. After that,
each is the same short loop: a three-term recurrence that jumps from one solution to the next.
One more, smooth triangular numbers (581), wears the disguise the other way round: thousands of
Pell equations at once, used to prove a search is finite rather than to walk a sequence. And two
more, the $k$-Markov numbers (844) and a triangle-hunting sequence (955), keep the walk but change
the step: one jumps across a tree instead of along a line, the other finds each next solution by
factoring.
The [technique page](/topics/technique/pells-equation) explains how to *solve* Pell equations.
This page is about *recognising* one, and about why so many of these problems end up walking
literally the same sequence of numbers.

## Taking off the disguise

The reduction is always the same three moves:

1. **Find the perfect-square condition.** A side, height or area must be an integer, or a
   quadratic must have a rational root. Either way, some quadratic expression $q(n)$ must be a
   square: $q(n) = m^2$.
2. **Complete the square.** Multiply through by the leading coefficient and shift the variable,
   so that $q(n) = m^2$ becomes $X^2 - D Y^2 = N$. Here $X$ is an affine image of $n$, such as
   $2n - 1$, $3h \pm 2$ or $5k + 1$.
3. **Keep the map back.** A Pell solution only counts if it maps back to an integer in range
   (the right residue, positive, non-degenerate).

Run that on each problem and they line up:

| Problem | Hidden square condition | Pell form |
|---|---|---|
| 100 — two blue discs, probability exactly $\tfrac12$ | $2b(b-1) = n(n-1)$ | $(2n-1)^2 - 2(2b-1)^2 = -1$ |
| 139 — hole of the pinwheel divides $c$ | primitive triple with $\lvert a-b\rvert = 1$ | $(a+b)^2 - 2c^2 = -1$ |
| 223 — $a^2+b^2 = c^2+1$, on the diagonal $a=b$ | $2a^2 - 1 = c^2$ | $c^2 - 2a^2 = -1$ |
| 224 — $a^2+b^2+1 = c^2$, on the diagonal $a=b$ | $2a^2 + 1 = c^2$ | $c^2 - 2a^2 = 1$ |
| 321 — $n(n+2)$ moves is triangular | $8(n^2+2n)+1$ square | $(2k+1)^2 - 8(n+1)^2 = -7$ |
| 94 — sides $a, a, a\pm1$, integral area | height$^2 = a^2 - h^2$, $a = 2h\mp1$ | $(3h\mp2)^2 - 3H^2 = 1$ |
| 138 — isosceles, height $= b \pm 1$ | $L^2 = (2k\pm1)^2 + k^2$ | $(5k\pm2)^2 - 5L^2 = -1$ |
| 137 — $A_F(x) = k$ has rational $x$ | discriminant $5k^2+2k+1$ square | $(5k+1)^2 - 5m^2 = -4$ |
| 140 — the same for $A_G$ | discriminant $5k^2+14k+1$ square | $(5k+7)^2 - 5m^2 = 44$ |

Two of these hide more deeply. Problem 139 starts as a divisibility test, $\lvert a-b\rvert$
divides $c$, and only becomes Pell once you see that for a *primitive* triple the hole can only
be $1$. Problems 223 and 224 are not Pell problems as a whole: their full solution sets are trees
under the [Barning–Hall matrices](/topics/technique/tree-of-primitive-pythagorean-triples).
But the symmetric spine $a = b$ of each tree is a Pell sequence, and the middle matrix restricted
to that spine is exactly the Pell step $(c, a) \mapsto (3c + 4a,\ 2c + 3a)$.

## One recurrence underneath

If a norm-$1$ unit $u = x_1 + y_1\sqrt D$ steps from one solution to the next, then every
coordinate of the solutions satisfies the same recurrence, whose multiplier is the unit's *trace*
$T = u + u^{-1} = 2x_1$:

$$s_{k+1} = T\,s_k - s_{k-1}.$$

The problem's own variable is an affine image $p = (s - c)/d$ of a Pell coordinate. It obeys the
same recurrence plus a constant, $p_{k+1} = T p_k - p_{k-1} + c(T-2)/d$. That is all the
"magic" constants in these solutions are:

- **$D = 2$, unit $3 + 2\sqrt2$, $T = 6$.** Problem 100 has blue counts $3, 15, 85, 493$ with
  $b_{k+1} = 6b_k - b_{k-1} - 2$. Problem 139 has tiling hypotenuses $5, 29, 169, 985$ with
  $c_{k+1} = 6c_k - c_{k-1}$. Problem 321 has $u = n + 1$ in each family following
  $u_{k+1} = 6u_k - u_{k-1}$, because $8u^2 = 2(2u)^2$ puts it in the same ring.
- **$D = 3$, unit $2 + \sqrt3$, $T = 4$.** Problem 94 has equal sides $5, 17, 65, 241$.
  Consecutive Pell solutions alternate between the two families (base $a+1$, base $a-1$), so a
  single $T = 4$ recurrence with an alternating correction walks both.
- **$D = 5$, units built from the golden ratio $\varphi$.** Problem 138 steps by
  $\varphi^6 = 9 + 4\sqrt5$, so $T = 18$: legs $17, 305, \dots$ with $L_{k+1} = 18L_k - L_{k-1}$.
  The golden nuggets of 137 are $2, 15, 104, 714$, with $g_{k+1} = 7g_k - g_{k-1} + 1$. Here
  $T = 7 = \varphi^4 + \varphi^{-4}$ comes from the half-integer unit $\varphi^4$.

The $D = 2$ cluster is more than an analogy. The solutions of $x^2 - 2y^2 = \pm1$ are exactly the
[convergents of $\sqrt2$](/topics/domain/convergent-continued-fraction) from
[Problem 57](/solutions/0057/): $\tfrac11, \tfrac32, \tfrac75, \tfrac{17}{12}, \tfrac{41}{29},
\tfrac{99}{70}, \dots$, with norms alternating $-1, +1$. The norm $-1$ convergents have
denominators $1, 5, 29, 169, 985$. Those numbers are $2b - 1$ in Problem 100, the hypotenuses in
Problem 139 and the diagonal legs in Problem 223, all at once. The norm $+1$ convergents
$\tfrac32, \tfrac{17}{12}, \tfrac{99}{70}$ are the diagonal of Problem 224. Four problems, one
sequence. The $D = 5$ cluster is the same story with Fibonacci numbers: the nuggets are
$F_{2n}F_{2n+1}$, and the legs in 138 are $F_{6k+3}/2$.

The public solution to Problem 94 shows how little code is left once the disguise is off. It is
the whole algorithm, with the two families folded into one sign alternator:

```python
s, s1, s2, m, p = (0, 1, 1, 1, 0)
while p <= max_perimeter:
    s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
    p = 3 * s2 - m
```

## Many equations, few solutions

Every problem above has one fixed $D$ and asks for the $k$-th solution or all solutions below a
bound. Problem 581 turns this around. It asks for every $n$ whose triangular number
$n(n+1)/2$ is $47$-smooth, which means $n$ and $n+1$ must both be smooth. There is no bound in the
statement, and no single equation to walk. The square condition is still there, though. Put
$x = 2n + 1$, so $x^2 - 1 = 4n(n+1)$, and split $n(n+1)$ into its squarefree part $q$ times a square.
That gives

$$x^2 - 2q\,y^2 = 1,$$

where $q$ ranges over the products of subsets of the fifteen primes up to $47$. The disguise hides
a *family* of $2^{15}$ Pell equations, and every answer is a solution of one of them. This is
[Størmer's theorem](/topics/technique/stormers-theorem). Two facts from Lehmer make it finite and
cheap:

- **Divisibility runs down the orbit.** $y_1$ divides every $y_k$. If the fundamental solution's
  $y_1$ is not smooth, no later solution can be, and the whole equation is discarded after one
  continued-fraction expansion. That filter removes all but a few percent of the equations.
- **Only the first few powers can matter.** A smooth $y_k$ forces $k \le \max(3, (p+1)/2)$, so
  each surviving equation is walked a fixed, small number of steps, not up to a numeric bound.

So the Pell structure still does the work, but it does a different job. In Problems 94–321 it
*generates* answers. In 581 it *bounds* the search: an open-ended question about consecutive
smooth numbers becomes a finite loop over subsets. The practical difference shows up in the
fundamental solutions. For a fixed small $D$ the unit is something like $3 + 2\sqrt2$. Across
thousands of $d = 2q$ values, many units are astronomically large, because the continued fraction
of $\sqrt d$ can have a period near $\sqrt d$. The solution abandons any expansion once $y$ passes
a cap, on the grounds that a huge $y_1$ has essentially no chance of being smooth. It does not just
assume that: the notes check that the answers don't change when the cap is raised by twenty orders
of magnitude.

## The step itself, undisguised

Why does a Pell orbit obey $s_{k+1} = T s_k - s_{k-1}$? Look at consecutive pairs. The recurrence
keeps the quantity $s_k^2 - T s_k s_{k-1} + s_{k-1}^2$ fixed, so every pair lies on the conic

$$x^2 - Txy + y^2 = N,$$

which, with $T = 2t$, is $(x - ty)^2 - (t^2 - 1)y^2 = N$: Pell with $D = t^2 - 1$ ($T = 6$ gives
$D = 8$, $T = 4$ gives $D = 3$, $T = 18$ gives $D = 80 = 5 \cdot 4^2$). Fix $y$, and $x$ is a root
of a quadratic whose roots sum to $Ty$. So the other root is $Ty - x$. The Pell step replaces one
coordinate by its partner root, and that move is
[Vieta jumping](/topics/technique/vieta-jumping). Seen this way, the unit is just a
way to package two jumps at once.

Problem 844 is that move with more variables. The equation
$\sum x_i^2 = k \prod x_i$ is quadratic in each $x_i$ separately, so any entry can jump to
$kP - x_i$, where $P$ is the product of the others. Freeze all but two entries and you are back on
the conic above, with trace $kP$. For classical [Markov](https://en.wikipedia.org/wiki/Markov_number)
triples, every branch that holds $z$ fixed is a Pell walk with $T = 3z$. Because any coordinate can
jump, the solutions form a **tree** rather than an orbit. Jumping the largest entry downward always
shrinks the tuple, and the descent ends at the all-ones root. That plays the role the fundamental
solution plays for Pell: one seed, and every solution reachable from it. Jumping any other entry
produces a new maximum, so a depth-first search pruned at the bound lists everything. The new
difficulty in 844 is a second parameter, $k$ up to $10^{18}$. It is handled by noticing that for
large $k$ each node is a fixed polynomial in $k$. The tree is walked once symbolically, and each
polynomial is summed over its range of $k$ with power sums.

Problem 955 keeps the walk but loses the unit. Its sequence restarts its differences at every
triangular number, so the next triangle after $t(x)$ is the least $j$ with $t(x) + t(j) = t(y)$.
Completing the square gives $(2x+1)^2 + (2j+1)^2 = (2y+1)^2 + 1$. That is not Pell, because the
squares that must cancel give a difference of two squares, and the equation factors:
$x(x+1) = pq$ with $q - p = 2j + 1$. So the next solution is the factor pair of $x(x+1)$ closest to
the trivial one $(x, x+1)$. That is a divisor search, done by factoring $x$ and $x + 1$ separately
and merging the factorisations, since the two are coprime. The walk still jumps from solution to
solution without visiting the terms in between. But each step costs a factorisation, not a
multiplication by a fixed unit, and the steps grow irregularly rather than geometrically.

## How to reason about it

- **Smell it from the statement.** Watch for "integral area" or "integer height" (Heron's
  formula, an altitude splitting an isosceles triangle), "exactly one half", "rational value of a
  series", or "is triangular / square". Then look for a search bound like $10^{12}$ or "the 15th
  such number", which no scan can reach. That combination almost always means a quadratic that
  must be a square, and that means Pell.
- **Brute-force the first few, then fit.** Brute force has a legitimate job here: generating the
  first four or five solutions. Then solve for $T$ and $c$ in
  $p_{k+1} = Tp_k - p_{k-1} + c$, and check the fit against a sixth term. $T$ should come out as
  $2x_1$ for a recognisable unit. If it doesn't, you have more than one family interleaved
  (Problem 94, Problem 321).
- **Know when the costume doesn't fit.** The tags put problems near this page that have no
  quadratic in them. Problem 455 asks for $n^x \equiv x \pmod{10^9}$. The unknown sits in the
  exponent, so there is no square to complete, and the tool is a power tower iterated to its fixed
  point. Problem 887 is driven by a recurrence, but it is a nested one,
  $F(h, c) = F(h-1, c-1) + F(h-1,\ c-1+F(h-1, c-1))$, and no constant trace fits it. So the test
  runs in both directions: no perfect-square condition means no Pell equation, and a fit that
  needs more than $T$ and a constant means you are holding some other kind of recurrence. The
  newer neighbours fail the fit in instructive ways. Problem 463 halves its index
  ($f(4n+1) = 2f(2n+1) - f(n)$), so it is divide-and-conquer, not a linear walk. Problem 866
  convolves the sequence with itself, $E(N) = (2N-1)\sum E(i)E(N-1-i)$, which is quadratic in its
  own terms. Problem 718 is a min-plus recurrence over residues, $w_i = \min(b_i, w_{i-1} + z)$,
  and its equation $17^p a + 19^p b + 23^p c = n$ is linear: a Frobenius problem, with no square
  anywhere. Problem 374's $A_j = j A_{j-1} + (j-1)!$ (factorial times harmonic number) has a
  multiplier that changes with $j$, so no trace exists. Problem 539 halves its index as 463 does,
  and sums by carrying the pair $(P, S)$ down the halving together. Problem 423 is the closest
  miss. Pascal's rule gives $G(n+1) = 6G(n) - A(n) + [n+1 \text{ prime}]A(n+1)$, which has a constant
  multiplier but a forcing term that is neither constant nor periodic. Since nothing repeats, the
  solution does not walk it. It unrolls it: each increment reaches every later term with weight
  $6^{n-j}$, so the whole sum becomes one dot product against geometric weights.
- **Check whether $D$ is a square.** A perfect-square condition is necessary for Pell, but not
  sufficient. If completing the square leaves $X^2 - s^2 Y^2 = N$, the left side factors as
  $(X - sY)(X + sY)$, and divisor arguments replace the Pell machinery. Problem 764 is the clean
  example: $16x^2 + y^4 = z^2$ is a Pythagorean triple whose odd leg $y^2 = (m - n)(m + n)$ is a
  product of two coprime factors, so each factor must itself be a square. That gives two
  closed-form [parametrisations](/topics/technique/euclids-formula), enumerated in $O(\sqrt N)$
  pairs, with no unit and no orbit. Problem 518 is the same principle with nothing to complete:
  $a+1, b+1, c+1$ in geometric progression means $(b+1)^2 = (a+1)(c+1)$. Write the ratio in lowest
  terms, $q/p$, and the triple must be $kp^2, kpq, kq^2$. The search then runs over $(k, p, q)$,
  not over pairs of primes. Problem 955 (above) is the walking version of this degenerate case.
  Problem 581 meets the same degenerate case inside its family
  ($q = 2$ gives $d = 4$) and simply skips it, because $x^2 - 4y^2 = 1$ has no positive solution.
- **A square in the statement need not be a condition.** Problem 674's operator
  $\mathcal{I}(x, y) = (1 + x + y)^2 + y - x$ looks like it invites completing the square. But the
  square is there to pack pairs into disjoint windows between consecutive squares, which makes
  $\mathcal{I}$ injective. Equations between $\mathcal{I}$-expressions are then
  [unification](/topics/technique/unification-computer-science) problems, not Diophantine
  arithmetic. Before reducing to Pell, ask what job the square is doing in the statement.
- **A completed square is useful modulo $q$ too.** Problem 291 first cancels
  $(x^4 - y^4)/(x^3 + y^3)$ down to the primes $f(n) = n^2 + (n+1)^2$. Then it completes the
  square, $2f(n) = (2n+1)^2 + 1$, but never solves $f(n) = m^2$. The square answers a different
  question: which primes $q$ divide some $f(n)$? Exactly those for which $-1$ is a square mod $q$,
  that is $q \equiv 1 \pmod 4$, and each hits two residue classes of $n$. That turns a primality
  test per value into a [sieve over the polynomial's values](/topics/technique/sieve-of-eratosthenes).
  A quadratic that has to be *prime* rather than *square* still gets its square completed, just
  for a sieve instead of a Pell walk.
- **Two square conditions sharing a variable are not one Pell equation.** In Problem 309 the
  ladders give $x^2 = w^2 + a^2$ and $y^2 = w^2 + b^2$ with the same width $w$. Eliminating $w$
  leaves $x^2 - a^2 = y^2 - b^2$, a quadric in four unknowns rather than a conic in two. The working move is to generate every triple with
  [Euclid's formula](/topics/technique/euclids-formula), group the triples by shared leg, and test
  the third condition, $(a+b) \mid ab$, on pairs inside each group.
- **Count the families.** For $N = \pm1$ there is one orbit. For $N = 44$ (Problem 140) or
  $N = -7$ (Problem 321) there are several, and a missed seed silently drops every answer in that
  family. Compare the merged sequence against all the terms the statement gives.
- **Filter on the original variables.** Divisibility ($5 \mid X \mp 2$), positivity and
  degeneracy ($k = 0$ in 138, $n = 0$ in 321) all belong to the problem, not to the Pell
  equation. Apply them after mapping back.
- **Expect geometric growth.** With $T$ between $4$ and $18$, the twelfth or fifteenth term is
  already past 64 bits. Use Python integers, or a wider type in C, as Problem 137 does with
  `__int128`.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0257](/solutions/0257/) — Angular Bisectors
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0283](/solutions/0283/) — Integer Sided Triangles with Integral Area/perimeter Ratio
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ○ [0292](/solutions/0292/) — Pythagorean Polygons
- ○ [0295](/solutions/0295/) — Lenticular Holes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ● [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0373](/solutions/0373/) — Circumscribed Circles
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0404](/solutions/0404/) — Crisscross Ellipses
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0428](/solutions/0428/) — Necklace of Circles
- ○ [0438](/solutions/0438/) — Integer Part of Polynomial Equation's Solutions
- ○ [0450](/solutions/0450/) — Hypocycloid and Lattice Points
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0482](/solutions/0482/) — The Incenter of a Triangle
- ○ [0496](/solutions/0496/) — Incenter and Circumcenter of Triangle
- ○ [0510](/solutions/0510/) — Tangent Circles
- ○ [0513](/solutions/0513/) — Integral Median
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0528](/solutions/0528/) — Constrained Sums
- ● [0539](/solutions/0539/) — Odd Elimination
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ○ [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0613](/solutions/0613/) — Pythagorean Ant
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ○ [0681](/solutions/0681/) — Maximal Area
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ○ [0723](/solutions/0723/) — Pythagorean Quadrilaterals
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0753](/solutions/0753/) — Fermat Equation
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle
- ○ [0827](/solutions/0827/) — Pythagorean Triple Occurrence
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ● [0866](/solutions/0866/) — Tidying Up B
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0880](/solutions/0880/) — Nested Radicals
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ○ [0904](/solutions/0904/) — Pythagorean Angle
- ○ [0914](/solutions/0914/) — Triangles inside Circles
- ○ [0919](/solutions/0919/) — Fortunate Triangles
- ● [0932](/solutions/0932/) — $2025$
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ● [0955](/solutions/0955/) — Finding Triangles
- ○ [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ○ [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0991](/solutions/0991/) — Fruit Salad
- ○ [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
