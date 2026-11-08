<!-- tags: [diophantine-approximation, diophantine-equation] -->
<!-- status: final 2026-11-03T17:31Z -->
# Diophantine Equations

A [Diophantine equation](https://en.wikipedia.org/wiki/Diophantine_equation) is a polynomial
equation for which only **integer** solutions count. That single word — *integer* — changes
everything: an equation with a continuum of real solutions may have finitely many integer ones,
infinitely many arranged in a rigid pattern, or none at all, and finding them is a different craft
from solving the equation over the reals. Euler is thick with these, because so many of its
problems count physical things — discs in a box, sides of a triangle, tiles on a floor — where a
fractional answer is meaningless. The problems below split along two related tags: **solving** for
exact integer solutions, and **[Diophantine approximation](https://en.wikipedia.org/wiki/Diophantine_approximation)**
— getting as close as possible to an irrational with a rational of bounded size. Both turn out to
lean on the same machinery.

## Why you cannot just search

The defining trap is that the integer solutions can be enormous, and scattered so sparsely that
brute force never reaches the first one. Problem 66 asks for the minimal solution of
[Pell's equation](https://en.wikipedia.org/wiki/Pell%27s_equation) $x^2 - D y^2 = 1$; for
$D = 661$ the smallest $x$ already exceeds $10^{17}$, so any loop bounded by the *magnitude* of the
answer would run forever. The whole art of Diophantine problems is to replace search over values
with **structure** — a closed form, a parametrisation, or a recurrence that jumps directly from one
solution to the next. A handful of moves recur.

## The toolbox

**Eliminate a variable with a linear constraint.** When one of the equations is linear, use it to
remove an unknown and collapse the search dimension. Problem 9 (public, `solutions/public/p0009/`)
wants the Pythagorean triple $a^2 + b^2 = c^2$ with $a + b + c = 1000$. The linear constraint fixes
$c = S - a - b$, turning a three-dimensional search into a two-dimensional one, and the ordering
$a < b < c$ bounds the loops to $a \le S/4$, $b \le S/2$. Crucially it computes $c$ as an *integer*
expression and tests $a^2 + b^2 = c^2$ exactly — never a floating-point square root, which would
force a tolerance comparison and risk rounding the integrality check away.

A linear equation stops being easy once its unknowns must be **non-negative**. Then
$ax + by + cz = n$ is the [coin problem](https://en.wikipedia.org/wiki/Coin_problem), and the
question becomes which $n$ it *cannot* reach. Problem 718 sums those gaps for three generators whose
gaps run into the quadrillions, so listing them is out. The reachable values form a
[numerical semigroup](https://en.wikipedia.org/wiki/Numerical_semigroup), and its
[Apéry set](https://en.wikipedia.org/wiki/Numerical_semigroup#Ap%C3%A9ry_set) holds all the
information. For each residue $r$ modulo the smallest generator, find the least reachable value in
that class. Every value above it in the class is reachable and every value below it is a gap, so the
gaps in each class form one arithmetic progression with a closed-form count and sum. The work is
linear in the smallest generator, however far the gaps extend.

**Parametrise the solution set.** Many classic families have a formula that generates *every*
solution. Every primitive [Pythagorean triple](https://en.wikipedia.org/wiki/Pythagorean_triple) is
$(m^2 - n^2,\, 2mn,\, m^2 + n^2)$ for coprime $m > n$ of opposite parity; iterating the parameters
enumerates triples directly instead of testing candidate sides. When a parametrisation exists it is
almost always the right tool — it makes the infinite solution set walkable.

Most parametrisations come from one lemma: **if coprime factors multiply to a square, each factor is
a square** (up to a unit, or a factor of 2 handled separately). Problem 518 needs three primes-plus-one
in geometric progression, $y^2 = xz$. Writing the common ratio in lowest terms as $q/p$ forces $p^2$
to divide $x$, so every such progression is $(kp^2, kpq, kq^2)$ with $p, q$ coprime, exactly once. A
search over pairs becomes a walk over three small parameters. Problem 764 applies the lemma twice.
It reads $16x^2 + y^4 = z^2$ as the Pythagorean triple $(4x, y^2, z)$, then asks the Euclid parameters
to make the leg $y^2$ a square. Depending on the parity of $y$, that forces $m \pm n$, or $m$ and $2n$,
to be squares themselves, and the result is two quartic families in a coprime pair. Since $z$ grows
as the fourth power of the parameters, the enumeration costs only $O(N^{1/2})$.

A parametrised family can also be **joined against itself**. Problem 309's crossed ladders need two
Pythagorean triples sharing a leg, with a divisibility condition linking their other legs. You
generate every triple once, bucket the triples by leg, and pair them up only within a bucket. A leg
belongs to only a handful of triples, so the pairwise test inside each bucket is nearly free, where a
pairing over all triples would be quadratic.

**Bound the unknown before solving for it.** Some equations have a free integer on one side, such
as "the ratio is an integer $k$". An inequality can often pin $k$ to a few values before any search
starts. Problem 257 asks for triangles whose area ratio, $(a+b)(a+c)/(bc)$, is an integer. With
$a \le b \le c$ each factor $(a+b)/b$ and $(a+c)/c$ lies in $(1, 2]$, so $k \in \{2, 3, 4\}$. One
open-ended equation becomes three fixed ones, and each can be parametrised separately.

**Count families, not members.** When the question is *how many* solutions lie under a bound,
generating them one at a time is slow even after the algebra is done. A good parametrisation makes
each parameter choice stand for a whole family, and a family can be counted in $O(1)$. In problem
257, writing $(a+b)/b$ as a reduced fraction $p/q$ turns each primitive triangle into a
[coprime](https://en.wikipedia.org/wiki/Coprime_integers) pair. Every other triangle is that shape
scaled by an integer, so a pair whose smallest triangle has perimeter $L$ contributes
$\lfloor N/L \rfloor$ triangles in one division. Problem 251 (Cardano triplets) needs one more
step. Cubing away the nested cube roots gives $a = 3n - 1$ and $b^2 c = n^2(8n - 3)$. Splitting
$n$ and $b$ by their [gcd](https://en.wikipedia.org/wiki/Greatest_common_divisor) leaves a
coprime pair. For that pair the last free variable has a linear upper bound and must lie in a
single residue class modulo $b_1^2$. The class has a
[modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) as its first
member, and the count is how many members of that progression fall under the bound. The gcd split
is what makes the pair coprime, and coprimality is what makes the congruence solvable. Problem 251
also shows that the loop order is part of the design. When $b_1$ is small the residue class is dense,
so the solution walks the cofactor. When $b_1$ is large the class is nearly empty, so it walks the
quotient and tests divisors instead. Switching near $N^{1/4}$ balances the two halves.

**Factor, and read the solutions off the divisors.** If the equation can be forced into the form
*product = constant*, its solutions are factorisations. Adding $n^2$ to both sides of
$1/x + 1/y = 1/n$ gives $(x - n)(y - n) = n^2$
([Simon's Favorite Factoring Trick](https://artofproblemsolving.com/wiki/index.php/Simon%27s_Favorite_Factoring_Trick)),
so problems 108 and 110 count divisors of $n^2$ from the exponents of $n$ and never search $x$ at all.
The same view finds the *least* solution, not just the count. In problem 955 each step of a sequence
of triangular numbers jumps by the least $j \ge 1$ with $t(x) + t(j) = t(y)$. A difference of squares
turns this into a factor pair $pq = x(x+1)$ with $q - p = 2j + 1$. The trivial pair $(x, x+1)$ is
$j = 0$, so the least real jump comes from the divisor of $x(x+1)$ **nearest** below $x$. The cost is
a [Pollard rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm) factorisation of $x$ and
$x+1$, not a scan across a gap that may be trillions wide. Factoring also tames the word *prime*.
Problem 291 wants primes of the form $(x^4 - y^4)/(x^3 + y^3)$. After cancelling $x + y$ and splitting
off $g = \gcd(x, y)$, the prime equals a product of three positive integers, so two of them must be 1.
The two-variable equation collapses to $p = n^2 + (n+1)^2$. Counting primes among a quadratic's values
is then a [polynomial sieve](https://en.wikipedia.org/wiki/Sieve_theory): an odd prime $q$ divides
some value only when $-1$ is a square mod $q$, and then it strikes exactly two residue classes of $n$.

**Pell's equation and its recurrence.** The equation $x^2 - D y^2 = \pm 1$ (for non-square $D$) is
the workhorse. It has infinitely many integer solutions, and — this is the key fact — they are *not*
scattered: from a small **fundamental** solution, every other is produced by a fixed linear
[recurrence relation](https://en.wikipedia.org/wiki/Recurrence_relation). Problem 100 (public,
`solutions/public/p0100/`) reduces "arrange discs so two drawn blue has probability exactly $1/2$"
to $x^2 - 2y^2 = -1$ by [completing the square](https://en.wikipedia.org/wiki/Completing_the_square),
then generates solutions with

```python
x, y = 1, 1
while n < target:
    x, y = 3 * x + 4 * y, 2 * x + 3 * y   # compose with the fundamental (3, 2)
    n, b = (x + 1) // 2, (y + 1) // 2
```

Because each step multiplies the solution by roughly $3 + 2\sqrt{2} \approx 5.83$, about forty
iterations cross $10^{12}$: the open-ended search has become an $O(\log T)$ walk. The same shape
solves a whole cluster of geometry problems — problem 94's almost-equilateral triangles reduce, via
[Heron's formula](https://en.wikipedia.org/wiki/Heron%27s_formula), to a *Pell-like* equation
$x^2 - 3y^2 = 1$ and are enumerated by an analogous recurrence.

Pell equations can also prove that a search **ends**. Problem 581 wants every $n$ for which $n$ and
$n + 1$ are both 47-smooth, with no bound given. Put $x = 2n + 1$ and let $q$ be the squarefree part
of $n(n+1)$. Then $x^2 - 2q\,y^2 = 1$, and $q$ is a product of some subset of the fifteen primes up to
47. That leaves $2^{15}$ Pell equations, which is
[Størmer's theorem](https://en.wikipedia.org/wiki/St%C3%B8rmer%27s_theorem). Lehmer's refinement
supplies the stopping rules. If the fundamental $y_1$ is not smooth, no later $y_k$ is, because
$y_1$ divides every $y_k$. And a smooth $y_k$ needs $k \le \max(3, (p+1)/2)$. An open-ended question
about consecutive integers becomes a fixed, finite list of short recurrences.

**Continued fractions — where the fundamental solution comes from.** For a Pell equation with
awkward $D$ (problem 66's $D$ up to 1000), the fundamental solution is found among the convergents
of the [continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) expansion of
$\sqrt{D}$. A continued fraction writes a number as $a_0 + 1/(a_1 + 1/(a_2 + \cdots))$; for a
quadratic irrational the terms are eventually periodic, which is exactly what makes the computation
finite. One specific convergent — chosen by the parity of the period length — is the fundamental
solution, so you generate one periodic block rather than testing values.

**Read a self-referential equation as a fixed point.** Some equations put the unknown on both
sides in incompatible roles, so no algebra isolates it. Problem 455 asks, for each base $n$, for the
$x < 10^9$ whose power $n^x$ ends in the digits of $x$ itself. That is the exponential congruence
$n^x \equiv x \pmod{10^9}$, and scanning a billion candidates per base is hopeless. Read it instead
as $x = T_n(x)$ with $T_n(x) = n^x \bmod 10^9$. Iterating $T_n$ from $x = 1$ builds the
[power tower](https://en.wikipedia.org/wiki/Tetration) $n, n^n, n^{n^n}, \dots$ modulo $10^9$.
Such towers become eventually constant, because each level only matters modulo the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) of the level below, and
the chain $\lambda(m), \lambda(\lambda(m)), \dots$ shrinks to $1$ in a few steps. The limit is a
solution by construction, and a dozen rounds settle every base. The cheap case analysis still comes
first: a valuation argument rules out every multiple of ten before any iteration. Unlike Pell, this
is not a structure the textbooks hand you. Verify on scaled-down moduli that the limit really is the
solution the problem wants before trusting it at full size.

**Jump between the roots of a quadratic.** Some equations are quadratic in each variable taken
alone, and then every solution has a neighbour. Problem 844's Markov-type equation
$x_1^2 + \cdots + x_k^2 = k\,x_1 \cdots x_k$ is quadratic in $x_1$ once the others are fixed, so by
[Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas) the other root,
$k\,x_2 \cdots x_k - x_1$, is also a positive integer. Swapping one root for the other is
[Vieta jumping](https://en.wikipedia.org/wiki/Vieta_jumping). Always swapping out the largest entry
shrinks any solution down to the fundamental one (all ones). Run backwards, the same move hangs every
solution on a single tree whose values grow along each branch, so a depth-first search pruned at the
bound lists all of them. The values grow doubly exponentially, so the tree is tiny. The problem adds
a sum over $k$ up to $10^{18}$, and here the structure pays again. For large $k$ the tree has the
same shape, with each node a fixed polynomial in $k$, so the sum over $k$ becomes a few dozen
[power sums](https://en.wikipedia.org/wiki/Faulhaber%27s_formula).

**Check whether the arithmetic carries any information.** Problem 674 asks when two nested
expressions built from $I(x, y) = (1 + x + y)^2 + y - x$ are equal. For fixed $s = x + y$ the values
of $I$ fill a window around $(s + 1)^2$, and the windows never overlap. So $I$ is **injective**, like
a [pairing function](https://en.wikipedia.org/wiki/Pairing_function), and two expressions are equal
exactly when their trees match. The "equation" is really first-order
[unification](https://en.wikipedia.org/wiki/Unification_(computer_science)): union-find over a
hash-consed term graph, with an occurs check to reject cycles. Because $I$ increases in each argument,
the least solution sets every variable left free by the most general unifier to 0. No integer is
computed until the very end.

## The sibling: Diophantine approximation

Diophantine approximation is the same subject read the other way. Instead of asking which integers
solve an equation *exactly*, it asks how well an irrational can be *approximated* by a rational
$p/q$ with $q$ bounded — and the answer is again continued fractions. The convergents of a number's
continued fraction are its **best rational approximations**: no fraction with a smaller denominator
comes closer. This is why the two tags share a page. The convergents that give Pell's fundamental
solution are the *same* objects that give the best rational approximation to $\sqrt{D}$; the theory
of quadratic irrationals is one theory wearing two hats. Euler's approximation problems (192 and 198
on best and ambiguous approximations, for instance) are built on exactly this convergent machinery,
often with the [Stern–Brocot tree](https://en.wikipedia.org/wiki/Stern%E2%80%93Brocot_tree) or
[mediants](https://en.wikipedia.org/wiki/Mediant_(mathematics)) as the concrete way to walk between
approximations of increasing denominator.

The same conjugate pairs explain why some powers of irrationals land almost exactly on integers.
Problem 318 looks at $(\sqrt p + \sqrt q)^{2n}$ and asks how soon its fractional part starts with
2011 nines. Let $x = \sqrt p + \sqrt q$ and $y = \sqrt q - \sqrt p$. Then $x^2$ and $y^2$ are
[conjugates](https://en.wikipedia.org/wiki/Conjugate_(square_roots)) $(p+q) \pm 2\sqrt{pq}$, so
$x^{2n} + y^{2n}$ is an integer, just as Pell solutions come from $(x_1 + y_1\sqrt D)^k$ and its
conjugate. When $0 < y < 1$ the fractional part of $x^{2n}$ is exactly $1 - y^{2n}$, so the count of
nines has a closed form in $\log y$. The algebra is short, and the hard part is numerical. Near the
top of the range $y$ sits just under $1$. Computing $\sqrt q - \sqrt p$ and then taking its logarithm
cancels away most of the significant digits. The solution rewrites $1 - y$ as a fraction with an
exact integer numerator and a denominator of positive terms, feeds it to `log1p`, and keeps the
qualifying test $\sqrt q < \sqrt p + 1$ in pure integers as $(q - p - 1)^2 < 4p$. A ceiling that
lands within a hair of an integer is recomputed in arbitrary precision.

## When nothing reduces

Not every Diophantine question gives way to algebra, and it is worth recognising that case rather
than hunting for structure that is not there. Problem 348 asks for palindromes expressible as
$a^2 + b^3$ in exactly four ways. Being a palindrome is a property of base-10 digits, and the number
of representations has no closed form, so the problem really is a search. What is left to decide is
the direction of the search. You can test targets: take each palindrome, try every cube below it, and
check whether the remainder is a perfect square. Or you can generate every pair $(a, b)$ and filter
the sums. Both cost $O(N^{5/6})$. Pair generation wins on constants because it needs no square roots,
and for a fixed $b$ the sums form one contiguous run that NumPy can build and filter as a single
array. The bound on $N$ is unknown, so the search runs one decimal-length band $[10^{d-1}, 10^d)$ at
a time. A finished band yields all its palindromes in order, so the search stops at the first band
that completes the count. Integer width still sets the limit: a 64-bit $a^2 + b^3$ caps the method
at 18 digits, and the solution checks that limit explicitly rather than letting the value wrap.

## How to reason about it

The moment a problem says "integer" and a naive search would overrun the magnitude of the answer,
stop searching and look for structure:

- Is one constraint **linear**? Eliminate a variable and shrink the search (problem 9). If the
  unknowns must be non-negative, it is a coin problem: count the gaps per residue class through the
  Apéry set, never one at a time (problem 718).
- Does the solution family have a known **parametrisation** (Pythagorean triples, sums of two
  squares)? Generate solutions instead of testing candidates. Do coprime factors multiply to a
  square? Then each is a square, and a coprime pair parametrises everything (problems 518, 764).
  When two members of a family must share a part, bucket by that part and pair within the
  buckets (problem 309).
- Can you force a **product equal to a constant**? Solutions are then divisors. Count them from the
  exponents, take the divisor nearest the trivial one for the least solution, and if the constant
  is prime, all factors but one are 1 (problems 108, 291, 955).
- Does the equation reduce to $x^2 - D y^2 = N$? It is **Pell** or Pell-like — find the fundamental
  solution (directly, or via the continued fraction of $\sqrt{D}$) and iterate the recurrence
  (problems 66, 94, 100). A finite family of Pell equations can also prove an unbounded search
  finite (problem 581).
- Is it **quadratic in each variable**? Vieta jumping links the solutions into a tree rooted at a
  fundamental solution; walk it with a pruned DFS (problem 844).
- Is the operation **injective**? Then equality means the expressions match, and the equation is a
  unification problem, not an arithmetic one (problem 674).
- Is there an integer unknown with **no obvious bound** (a ratio, a quotient)? Use the ordering of
  the variables to confine it to a few values, then solve each case (problem 257).
- Is the question **how many**, not which? Parametrise by primitive solutions, usually coprime
  pairs. Count each family with $\lfloor N/L \rfloor$ or a residue-class count, and never list its
  members (problems 251, 257).
- Is the question really about **best rational approximation**? Reach for continued-fraction
  convergents. If it is about powers drifting toward integers, pair each irrational with its
  conjugate so the sum is an integer (problem 318).
- Does the unknown appear as **both exponent and residue**? Treat the equation as a fixed point and
  iterate, and check on small moduli that the limit is the solution you want (problem 455).
- **Nothing reduces?** Then it is a search, so choose its direction by constant factors as well as
  exponent. Generating candidates and filtering them can beat testing targets when it avoids roots
  and vectorises (problem 348).
- **Mind the integer width.** Solutions and intermediates grow quickly. Python's integers are
  unbounded, but a C port is not. The C port of problem 251 silently wrapped a product used only in a
  bound test, and its count came out too high. Compare against a precomputed integer-square-root cap
  instead of forming the product, and keep equality tests exact rather than within a tolerance.
  Floating point has the same failure when two close quantities are subtracted. Square inequalities
  into integer tests, and rearrange near-cancelling differences before taking logarithms (problem
  318).

The recurring mistake is to treat these as search problems by default, looping over candidate $x$ up
to some bound and testing the equation. For a genuine Diophantine problem that bound is
astronomically larger than the number of solutions you need, and the loop never finishes. When the
solutions are few, finding the structure makes the enumeration logarithmic. When they are many, it
turns the count into one division per family. Search is the honest fallback only once you have
checked that no structure exists, and even then the integer view decides how to run it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0257](/solutions/0257/) — Angular Bisectors
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ○ [0279](/solutions/0279/) — Triangles with Integral Sides and an Integral Angle
- ○ [0283](/solutions/0283/) — Integer Sided Triangles with Integral Area/perimeter Ratio
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ○ [0296](/solutions/0296/) — Angular Bisector and Tangent
- ○ [0299](/solutions/0299/) — Three Similar Triangles
- ● [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0404](/solutions/0404/) — Crisscross Ellipses
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ○ [0428](/solutions/0428/) — Necklace of Circles
- ○ [0438](/solutions/0438/) — Integer Part of Polynomial Equation's Solutions
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0482](/solutions/0482/) — The Incenter of a Triangle
- ○ [0496](/solutions/0496/) — Incenter and Circumcenter of Triangle
- ● [0510](/solutions/0510/) — Tangent Circles
- ○ [0513](/solutions/0513/) — Integral Median
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0542](/solutions/0542/) — Geometric Progression with Maximum Sum
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ○ [0566](/solutions/0566/) — Cake Icing Puzzle
- ○ [0576](/solutions/0576/) — Irrational Jumps
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ● [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0583](/solutions/0583/) — Heron Envelopes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0591](/solutions/0591/) — Best Approximations by Quadratic Integers
- ○ [0620](/solutions/0620/) — Planetary Gears
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ○ [0681](/solutions/0681/) — Maximal Area
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0753](/solutions/0753/) — Fermat Equation
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0799](/solutions/0799/) — Pentagonal Puzzle
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0904](/solutions/0904/) — Pythagorean Angle
- ○ [0919](/solutions/0919/) — Fortunate Triangles
- ● [0932](/solutions/0932/) — $2025$
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ● [0955](/solutions/0955/) — Finding Triangles
- ● [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ● [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0991](/solutions/0991/) — Fruit Salad
- ● [0998](/solutions/0998/) — Squaring the Triangle

<!-- /problems -->
