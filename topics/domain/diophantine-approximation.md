<!-- tags: [diophantine-approximation] -->
<!-- status: final -->
# Diophantine approximation

[Diophantine approximation](https://en.wikipedia.org/wiki/Diophantine_approximation) asks how
well a real number can be approached by rationals, and what that costs: how close $p/q$ can get to
$x$ for a given size of $q$. The same question has a second form. A quantity $q\alpha$ is close to
an integer exactly when $\alpha$ is close to a fraction with denominator $q$. Turn it around and
"how close does $\alpha^n$ get to an integer?" is the same subject. Project Euler asks it both
ways. Problems 192 and 198 ask for the best fraction under a denominator bound, and for when there
are two equally good ones. Problem 318 asks how fast the powers of $\sqrt p + \sqrt q$ approach
integers. In every case the answer is a theorem about integers, and the computation follows the
theorem rather than searching.

This page is about the *measure* of closeness and what follows from it. The mechanics of
expansions, convergents and the Stern–Brocot walk are on the
[continued fraction](/topics/domain/continued-fraction) page. Computing exactly with numbers you
cannot store is on the [irrational number](/topics/domain/irrational-number) page. The numerical
half of problem 318 belongs with its companion page,
[catastrophic cancellation](/topics/technique/catastrophic-cancellation).

## The yardstick: $1/q^2$

Every real $x$ lies within $1/(2q)$ of some fraction with denominator $q$. That is just rounding,
and it is a poor result. [Dirichlet's theorem](https://en.wikipedia.org/wiki/Dirichlet%27s_approximation_theorem)
does far better. For every bound $N$ there is a $q \le N$ with $|qx - p| < 1/N$, so infinitely
many fractions satisfy

$$\left| x - \frac{p}{q} \right| < \frac{1}{q^2}.$$

The proof is a pigeonhole on the fractional parts of $0, x, 2x, \ldots, Nx$. The square in the
denominator is the yardstick. Squaring the exponent is all you can have in general: by
[Hurwitz's theorem](https://en.wikipedia.org/wiki/Hurwitz%27s_theorem_(number_theory)) the
constant can be improved to $1/\sqrt 5$ and no further, and the golden ratio is the number that
stops it. With partial quotients all equal to 1, $\varphi$ is the hardest number to approximate.
Large partial quotients mean unusually good approximations, because a convergent satisfies

$$\left| x - \frac{p_k}{q_k} \right| \approx \frac{1}{a_{k+1}\, q_k^2}.$$

So the continued fraction is not only a way to find good fractions. It is a direct readout of how
good they are.

## Two kinds of "best"

A **best approximation** is a fraction that no fraction with a smaller (or equal) denominator
beats. There are two natural ways to measure "beats", and they do not give the same list:

| Kind   | Minimises       | The best approximations are                                   |
|--------|-----------------|----------------------------------------------------------------|
| second | $\lvert qx - p\rvert$ | exactly the convergents $p_k/q_k$                               |
| first  | $\lvert x - p/q\rvert$ | the convergents, plus some [semiconvergents](https://en.wikipedia.org/wiki/Continued_fraction#Semiconvergents) |

The second kind weights the error by $q$, so it is the right measure when $q$ multiplies the error,
as in "$q\alpha$ is near an integer". The first kind is what a problem means by "the closest
fraction with denominator at most $N$", and that is problem 192's question. There the answer is
one of the two Farey neighbours of $\sqrt n$ in $F_N$: the last convergent that fits, or the
semiconvergent part-way through the next run. The tie-break rule between them is on the continued
fraction page. The point to take from here is why semiconvergents appear at all. Under the
first-kind measure a large denominator is no handicap, so a fraction that is only halfway down a
long run can still win.

## When best is not unique

Problem 198 inverts the question. It asks for which rationals $x$ the best first-kind
approximation is *not* unique for some bound. A tie needs two fractions on opposite sides of $x$ at
the same distance, both admissible, with nothing in between. "Nothing in between, below the bound"
is the definition of Farey neighbours $a/b < c/d$ with $bc - ad = 1$. So the ambiguous numbers are
exactly the midpoints of Farey-neighbour pairs, at distance $1/(2bd)$ from each end. The statement's
example $9/40$ is the midpoint of $1/5$ and $1/4$.

That turns a search over values into a count over pairs, and the determinant does the rest. The
midpoint is $(2ad + 1)/(2bd)$ and is already in lowest terms, so its denominator is exactly $2bd$
and the bound on $q$ becomes a bound on the product $bd$. Fix the smaller denominator, which is at
most $\sqrt{bd}$. Then the neighbour condition makes the other denominator an arithmetic progression
modulo the first, given by a [modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse),
and each count is one floor-division formula. The general lesson: **ties in an approximation
problem are not noise. They are structure.** They happen at rationals, on the Farey lattice, and
can be enumerated, never found by comparing floats.

## Powers near integers

Problem 318 looks like a different subject: the fractional part of $(\sqrt p + \sqrt q)^{2n}$
starts with more and more nines. It is the same subject, seen from the other side. Write
$x = \sqrt p + \sqrt q$ and $y = \sqrt q - \sqrt p$. Then $x^2$ and $y^2$ are the two roots of an
integer quadratic, so $x^{2n} + y^{2n}$ is an integer, and when $0 < y < 1$,

$$x^{2n} = \text{integer} - y^{2n}.$$

So $x^{2n}$ is within $y^{2n}$ of an integer, geometrically close. A real number whose powers do
this is a [Pisot–Vijayaraghavan number](https://en.wikipedia.org/wiki/Pisot%E2%80%93Vijayaraghavan_number):
an algebraic integer greater than 1 whose conjugates all lie inside the unit circle. Almost every
other real number has powers spread evenly mod 1
([Koksma](https://en.wikipedia.org/wiki/Equidistributed_sequence#Metric_theorems)). The problem is
designed around the exceptions. Which pairs qualify, $\sqrt q - \sqrt p < 1$, squares down to the
integer test $(q - p - 1)^2 < 4p$. The degenerate case looks after itself: if $pq$ is a perfect
square then $p = ka^2$, $q = kb^2$ and $y = \sqrt k\,(b - a) \ge 1$, so no rational $x^2$ slips
through. The test also says how many pairs there are. For each $p$ only about $2\sqrt p$ values of
$q$ pass, so the qualifying pairs up to $p + q \le L$ number $\Theta(L^{3/2})$, and each gets a
closed form. How many nines a power has is the exponent at which $y^{2n}$ drops below a power of
ten, so it is a ratio of logarithms, not a big-number expansion:

$$N = \left\lceil \frac{d}{-2\log_{10} y} \right\rceil.$$

The ceiling is never ambiguous in exact arithmetic, because $y^{2n}$ is an irrational algebraic
number and never exactly $10^{-d}$. Whether it is ambiguous in floating point is a separate
question, and the answer is below.

The link with fractions is direct when $x^2$ is a unit. For $\sqrt 2 + \sqrt 3$, $x^2 = 5 + 2\sqrt 6$
has norm $25 - 24 = 1$. Its powers are $a_n + b_n\sqrt 6$ with $a_n^2 - 6b_n^2 = 1$, which is
[Pell's equation](/topics/technique/pells-equation), and

$$\left| a_n - b_n\sqrt 6 \right| = \frac{1}{a_n + b_n\sqrt 6}.$$

That is $|b_n\sqrt 6 - a_n|$ shrinking like $1/b_n$: the fractions $a_n/b_n$ approximate $\sqrt 6$
to the Dirichlet standard, and they are convergents of it. "Powers of a quadratic unit are nearly
integers" and "Pell solutions are best approximations" are the same statement, read in
$\mathbb{Z}[\sqrt 6]$ and in $\mathbb{Q}$. The
[conjugate trick](/topics/takeaway/conjugate-cancels-irrational-part) is what makes both visible.

The difficulty left in problem 318 is numerical. For the pairs where $y$ is just below 1,
$\log y$ is tiny, the counts run into the millions, and $\sqrt q - \sqrt p$ computed in floating
point has lost most of its digits before the logarithm is taken. That is the subject of the
[companion page](/topics/technique/catastrophic-cancellation): rewrite $1 - y$ so its numerator is an
exact integer, take `log1p`, and check any ceiling that lands near an integer with more precision.

## How to reason about it

- **Decide which measure the problem means.** "Closest fraction with denominator $\le N$" is the
  first kind (convergents and semiconvergents). "Multiple of $\alpha$ nearest an integer" is the
  second kind (convergents only). Mixing them up gives an answer that is right for most inputs and
  wrong for a few.
- **Expect $1/q^2$, and read the rest off the partial quotients.** A large $a_{k+1}$ means a very
  good approximation right before it. All-ones means as bad as it gets. That is enough to predict
  whether a float has the precision to separate two candidates.
- **Ties live on the Farey lattice.** An equality between two approximation errors is a rational
  identity; prove it with the determinant $bc - ad = 1$ and count it exactly. Never detect it with
  `==` on floats.
- **Near-integers come from conjugates.** If a power of an irrational is suspiciously close to an
  integer, look for an algebraic conjugate below 1. The integer is a trace you can compute exactly,
  and the distance is the conjugate's power.
- **The closeness is the hazard.** Every quantity on this page is small by design: $|x - p/q|$,
  $y^{2n}$, $1 - y$. Subtracting nearly equal floats to get them is exactly where precision dies.
  Compute the small quantity directly from integers, or use exact arithmetic.

The open problems on the list push the same ideas further. Problem 591 asks for the best
approximations by quadratic integers $a + b\sqrt d$ instead of fractions, and in problem 576 a
point jumps round a circle by an irrational step until it lands in a small gap. How long that takes
depends on how well the step is approximated by fractions, through the
[three-gap theorem](https://en.wikipedia.org/wiki/Three-gap_theorem).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0192](/solutions/0192/) — Best Approximations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0318](/solutions/0318/) — 2011 Nines
- ○ [0542](/solutions/0542/) — Geometric Progression with Maximum Sum
- ○ [0566](/solutions/0566/) — Cake Icing Puzzle
- ○ [0576](/solutions/0576/) — Irrational Jumps
- ○ [0591](/solutions/0591/) — Best Approximations by Quadratic Integers
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0904](/solutions/0904/) — Pythagorean Angle

<!-- /problems -->
