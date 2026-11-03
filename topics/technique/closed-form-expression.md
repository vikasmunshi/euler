<!-- tags: [closed-form-expression] -->
<!-- status: final -->
# Closed-form expression

A [closed-form expression](https://en.wikipedia.org/wiki/Closed-form_expression) computes a
quantity with a bounded formula — a finite chain of arithmetic, powers, roots, binomials and a few
named functions — instead of a loop that walks every case. It is the most common single lever in
this problem set: the ninety-odd problems below each hide a formula behind a process, a grid, a game
or a recurrence. In every one, the obvious program enumerates something astronomically large while
the real program evaluates an expression whose size does not grow with the input. The bounds
Project Euler chooses — $10^{12}$, $10^{16}$, a googol — are often the setter's way of saying
*there is a formula; find it*.

## The idea

The move is always the same in spirit: stop *enumerating* the objects and start *counting*,
*summing* or *solving for* them algebraically. Across these problems the formula comes from six
recognisable places.

### 1. Sums that collapse into polynomials

The seed is the [arithmetic series](https://en.wikipedia.org/wiki/Arithmetic_progression)
$d + 2d + \dots + nd = d\,\frac{n(n+1)}{2}$. Problem 1 sums the multiples of 3 or 5 below a limit
with three such terms under
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle):

```python
def sum_arithmetic_series(common_difference, *, max_limit):
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2
```

Problem 6 takes one line: the square of the triangular number minus the square-pyramidal sum.

```python
return str((n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6)
```

Higher power sums are the [Faulhaber](https://en.wikipedia.org/wiki/Faulhaber%27s_formula)
polynomials. The rest of this family is about *getting a problem into that shape*:

- **Geometry that is secretly a sequence.** The corners of a square number spiral are $(2k+1)^2$
  minus multiples of $2k$. That lets Problem 28 fold an $O(N^2)$ diagonal sum into one cubic in $N$,
  and Problem 58 walks the same corners layer by layer without ever building the grid. Problem 128
  does the hexagonal version: ring $k$ starts at $3k(k-1)+1$, and once every neighbour difference
  is written in closed form, all but two tiles per ring are ruled out.
- **Telescoping.** Problem 487's double sum of power sums telescopes by
  [summation by parts](https://en.wikipedia.org/wiki/Summation_by_parts) into two single power
  sums. Problem 918's trillion-term partial sum of a binary recurrence telescopes to *one* term of
  the sequence. Problem 235's
  [arithmetico-geometric](https://en.wikipedia.org/wiki/Arithmetico-geometric_sequence) partial
  sum becomes one exponentiation inside a root-finder. In Problem 359 each floor of the hotel is
  defined by neighbouring rooms summing to consecutive squares, so two rooms apart the squares
  cancel to $2s - 1$. That difference is linear in the room index, so every occupant is a
  quadratic, and the requested sum is one formula evaluation per divisor of $N$.
- **Separable sums.** When a per-item count factors as $f(m)\,g(n)$, its sum over all sub-grids is
  the product of two one-dimensional sums. This turns Problem 147's axis-aligned rectangles into a
  product of [tetrahedral numbers](https://en.wikipedia.org/wiki/Tetrahedral_number). Problem 234
  uses the triangular-number formula to sum the multiples of $p$ and $q$ between consecutive prime
  squares: one band per prime instead of one step per integer.
- **Sum a scaling family along its ray.** When an equation is homogeneous, its solutions come as
  multiples $t$ of primitive ones, and a quantity linear in the solution sums over a whole ray as
  its primitive value times the triangular number $m(m+1)/2$. Problem 510's tangent circles obey
  $1/\sqrt{r_C} = 1/\sqrt{r_A} + 1/\sqrt{r_B}$, whose integer solutions are $t$ times polynomials
  in a coprime pair $(u, v)$. So the loop visits $O(\sqrt n)$ primitive pairs and never touches
  $t$. Looping over $t$ would undo the parametrisation, because the smallest pair alone has
  $\lfloor n/4 \rfloor$ multiples.
- **Double counting.** Problem 944 swaps the order of summation, tallying each integer's
  contribution across all $2^n$ subsets. It lands on a closed form whose one remaining sum runs
  over the $O(\sqrt n)$ distinct values of $\lfloor n/x \rfloor$.
- **A floor is a staircase.** A prefix sum of $\lfloor j/k \rfloor$ needs no loop, since each value
  repeats $k$ times: with $L = qk + r$, $\sum_{j<L} \lfloor j/k \rfloor = k\binom{q}{2} + rq$.
  Problem 688 reaches that shape by swapping its double sum to put the pile count $k$ outermost.
  The swap pays twice, because $k$ piles of different sizes need a triangular number of plates, so
  only $k \lesssim \sqrt{2N}$ survive. About $10^{16}$ terms become $O(\sqrt N)$ evaluations of one
  formula.
- **Rounding is a periodic correction.** A term like $\operatorname{round}(k^2/12)$ looks
  unsummable, but $k^2 \bmod 12$ takes only four values, so the term is $(k^2 + c(k))/12$ with $c$
  periodic. Its prefix sum is the square-pyramidal polynomial plus whole periods of $c$ plus a
  twelve-entry remainder table — a
  [quasi-polynomial](https://en.wikipedia.org/wiki/Quasi-polynomial). Problem 276 uses exactly this
  for [Alcuin's sequence](https://oeis.org/A005044), the count of integer triangles by perimeter,
  and Problem 950's opening regime sums $C - \lfloor (n-1)/2 \rfloor$ to
  $LC - \lfloor (L-1)^2/4 \rfloor$ the same way.
- **Split by residue class.** A sequence can be irregular overall and still regular along every
  arithmetic progression of its indices. When it is, sum each class on its own. Problem 506 cuts
  its terms from a digit stream of period 6 in which every six-digit window sums to 15. Term
  $n+15$ therefore starts at the same phase as term $n$, and it is term $n$ with one full period
  appended: $v_{n+15} = 10^6 v_n + Q_{n \bmod 15}$. Each of the fifteen classes is then an affine
  recurrence whose unrolled terms are geometric, so the sum to $10^{14}$ costs fifteen modular
  powers. In Problem 605 the game ends at round $m$ with probability $(m-1)/2^m$. A player wins
  when the end round is in their class modulo $n$, so their chance is an arithmetico-geometric
  series over that class, which has a closed form. Problem 718 counts the gaps of the
  [numerical semigroup](https://en.wikipedia.org/wiki/Numerical_semigroup) generated by
  $17^p, 19^p, 23^p$. Within each residue class modulo the smallest generator, the gaps form an
  arithmetic progression that stops just below the class's
  [Apéry set](https://en.wikipedia.org/wiki/Ap%C3%A9ry_set) element. Quadrillions of gaps reduce to
  one triangular-number formula per class.

### 2. Counting without listing

[Combinatorial](https://en.wikipedia.org/wiki/Combinatorics) identities count arrangements without
generating them. Problem 15 is the central binomial $\binom{2n}{n}$. Problem 113 counts monotone
digit strings below a googol with
[stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)), then sums over
lengths with the [hockey-stick identity](https://en.wikipedia.org/wiki/Hockey-stick_identity),
leaving one expression in binomials. Problem 106 counts the subset pairs that need testing as "all
splits minus the dominating ones", and the dominating ones are
[Catalan numbers](https://en.wikipedia.org/wiki/Catalan_number). Problem 158 splits its count into
"which letters" (a binomial) times "how they are ordered", where the second factor is an
[Eulerian number](https://en.wikipedia.org/wiki/Eulerian_number) with its own closed form.
Problem 162 counts hex strings containing 0, 1 and A by inclusion–exclusion over the eight subsets
of forbidden digits, with each term a product of powers.

Problem 862 notices that summing "how many rearrangements are larger" over a whole digit multiset
counts every unordered pair once. Each multiset therefore contributes $\binom{V}{2}$, where $V$ is
a [multinomial](https://en.wikipedia.org/wiki/Multinomial_theorem) count. In Problem 743 the window
constraint forces the column sums to be periodic, so the count becomes a coefficient of a
trinomial power. Problem 194 runs the
[transfer-matrix method](https://en.wikipedia.org/wiki/Transfer-matrix_method) once on a single
unit and finds that the colouring count for the whole chain is a binomial times two powers.
Problem 739's repeated prefix-sum operation is linear, so the final term is a weighted sum of the
starting terms. Each weight counts the monotone paths from one start position to the apex that
never cross a diagonal. That is the [ballot problem](https://en.wikipedia.org/wiki/Bertrand%27s_ballot_theorem),
so each weight is a single binomial times $k/(n-1)$. The statement's tell is its all-ones example,
which ends on a Catalan number.

Problem 561 counts the pairs of divisors $a \mid b$ of $(p_m\#)^i$. Divisibility compares exponent
vectors coordinate by coordinate, so the count is a product of $m$ identical one-coordinate
counts, each $\binom{i+2}{2}$. This is the separable trick from Problem 147, applied to a lattice
of divisors. Problem 628 needs a *characterisation* before it can count anything. A rook that
moves only right or up crosses every anti-diagonal exactly once, so a position is blocked exactly
when some anti-diagonal is completely full. For a permutation, that means a reversed block in a
corner. A permutation has at most one block of each corner kind, so inclusion–exclusion has only
a few exact terms. The identity $m \cdot m! = (m+1)! - m!$ then telescopes the weighted sum into
the [left factorial](https://oeis.org/A003422) $!n = \sum_{m<n} m!$.

Probability is counting with weights, and the same trick applies.
[Linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity) turns Problem
493's expected number of colours into seven copies of one ratio of binomials. Problem 253 shows
that the gap widths of a random fill form a uniform random
[composition](https://en.wikipedia.org/wiki/Composition_(combinatorics)). Its marginals have closed
forms, so the gaps drop out of the state entirely. Problem 605's ring of coin-tossing players
looks like it needs the whole table, but only one bit matters after each round: whether that
round's winner also plays the next round. That makes the game a two-state
[Markov chain](https://en.wikipedia.org/wiki/Markov_chain) with an absorbing state, and its
survival probabilities solve to $t/2^t$. Problem 523's odd sort is insertion sort in
disguise. An element with $s$ smaller elements ahead of it costs $T(s) = 1 + \sum_{i<s} T(i)$
moves, which solves to $2^s$. Its rank is uniform, so the expected total is one short sum of
$(2^k - 1)/(k+1)$.

Smaller counting formulas often sit *inside* a search as its $O(1)$ kernel:

- Problem 86 counts the $(b, c)$ pairs with a given sum in constant time.
- Problem 145's digit DP counts the digit pairs with a given sum directly.
- Problem 173 writes every square lamina as $4t(t+h)$ tiles.
- Problem 207 shows its partitions are indexed by the pronic numbers $n(n-1)$.
- Problem 210's two half-plane regions are exact polynomials in $r$. Only the circle resists a
  closed form, since it is a
  [Gauss circle problem](https://en.wikipedia.org/wiki/Gauss_circle_problem), so it is summed row
  by row.
- Problem 804 shows that a summatory function can be simpler than its summand. Its $g(n)$ counts
  the representations of $n$ by a
  [binary quadratic form](https://en.wikipedia.org/wiki/Binary_quadratic_form), and the class
  number one discriminant even offers a divisor-sum formula for it. Summing over $n$ makes all of
  that unnecessary: every pair $(x, y)$ is counted exactly once, so the total is a count of lattice
  points in an ellipse. After completing the square, each row is one integer square root plus a
  parity correction. $10^{16}$ values of $g$ become $O(\sqrt N)$ rows, and no individual $g(n)$ is
  ever computed.
- Problem 276 needs only the *primitive* triangles. Its $O(1)$ count of all triangles up to a
  perimeter is evaluated at each of the $O(\sqrt N)$ floor quotients $\lfloor N/k \rfloor$, and
  [Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula) peels off the
  non-primitive ones in $O(N^{3/4})$ total. Without the closed form, every quotient would cost a
  sum of its own and the inversion would be no faster than a sieve.
- Problem 401 has the same shape. The
  [Dirichlet hyperbola method](https://en.wikipedia.org/wiki/Dirichlet_hyperbola_method) splits
  $\sum_d d^2 \lfloor n/d \rfloor$ at $\sqrt n$. Each row of the far strip then weighs a
  [square pyramidal number](https://en.wikipedia.org/wiki/Square_pyramidal_number), so
  $10^{15}$ terms become $2\sqrt n$.
- Problem 778 counts how many integers in $[0, M]$ have digit $d$ at place $10^i$ from one
  division, $M + 1 = q \cdot 10u + r$. The histogram therefore costs nothing per integer, and the
  rest is a convolution power over the digit monoid.

### 3. A theorem collapses the statement

Many problems look computational until one classical theorem reduces them to a formula:

| Theorem | What it collapses | Problems |
|---|---|---|
| [Binomial theorem](https://en.wikipedia.org/wiki/Binomial_theorem) mod $a^2$ | $(a\pm1)^n$ to two surviving terms | 120 |
| [Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) | binomials mod $p$ to products over base-$p$ digits | 148, 242 |
| [Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem) / [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) | the prime exponent in $n!$ or $\binom{n}{m}$ to digit sums, so $\sum_{t \le N} v_2(t) = N - s_2(N)$ | 288, 561, 704 |
| [Lifting-the-exponent lemma](https://en.wikipedia.org/wiki/Lifting-the-exponent_lemma) | $v_2(k^m - 1)$ to $v_2(k-1)$, plus a correction in $v_2(m)$ when $m$ is even | 561 |
| [Roots-of-unity filter](https://en.wikipedia.org/wiki/Series_multisection) | the $p$-subsets with sum $\equiv 0 \pmod p$, $p$ prime, to one binomial plus $p-1$ identical terms | 635 |
| [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) | $10^q \bmod p$ with $q \approx 3 \times 10^{17}$ to $10^{q \bmod (p-1)}$ | 684 |
| [Wilson's theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem) | $(p-k)!$ mod $p$ to a fixed modular fraction | 381 |
| [Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function) multiplicativity | $\varphi(pq) = (p-1)(q-1)$, with no factoring | 70 |
| [Digital root](https://en.wikipedia.org/wiki/Digital_root) congruence | $\operatorname{dr}(k) = 1 + (k-1) \bmod 9$ | 159 |
| [Cayley–Hamilton](https://en.wikipedia.org/wiki/Cayley%E2%80%93Hamilton_theorem) | a $2\times2$ square root to two scalars, trace and determinant | 420 |
| [Divisor function](https://en.wikipedia.org/wiki/Divisor_function) | counting the right triangles on a leg to $\tau(M^2)$ | 176 |
| [Conjugate](https://en.wikipedia.org/wiki/Conjugate_(square_roots)) pairs | $x^{2n} + y^{2n}$ to an integer, so $\{x^{2n}\} = 1 - y^{2n}$ | 318 |
| [Fermat's Last Theorem](https://en.wikipedia.org/wiki/Fermat%27s_Last_Theorem) | an exponent search to $\lvert n\rvert \le 2$, once the expression is factored | 180 |
| [Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas) | a symmetric function of a polynomial's roots to its coefficients, so no root is ever found | 479 |

The step before the theorem is usually **algebra on the statement itself**:

- Problem 180's three intimidating functions factor to $(x+y+z)(x^n + y^n - z^n)$.
- Problem 168's rotation condition is a linear equation that, given the digit count, the last
  digit and the ratio, solves for the leading part.
- Problem 141's "divisor, quotient and remainder in geometric progression" becomes the explicit
  parametrisation $n = k^2 p^3 q + k q^2$.
- Problem 772's balanceability is equivalent to a clean divisibility condition.
- Problem 479 sums powers of $(a+b)(b+c)(c+a)$ over the complex roots of a cubic, and its remark
  that the result is always an integer is the tell. Since $a + b = e_1 - c$, the product is the
  cubic evaluated at $e_1$, a polynomial in $k$. The roots vanish from the problem, and what is left
  is a geometric series per $k$.
- In Problem 684, the smallest number with digit sum $n = 9q + r$ is $r$ followed by $q$ nines,
  $(r+1)\,10^q - 1$. The nine values that share a $q$ form a block, and the blocks sum as a
  geometric series.
- Problem 269's integer-root condition becomes a divisibility test that prunes a digit DP down to a
  handful of candidate roots.
- Problem 274's divisibility multiplier turns out to be the
  [inverse of 10](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) modulo $p$, and
  that inverse has a closed form keyed on $p$'s last digit: $m = (kp+1)/10$ with
  $k = 9, 3, 7, 1$ for $p \equiv 1, 3, 7, 9 \pmod{10}$. A formula can replace an *algorithm*, not
  just a loop: no extended Euclid per prime, and branch-free arithmetic that vectorises over every
  prime below the limit in one NumPy expression.

### 4. Recurrences that have a formula

A linear recurrence with constant coefficients has a closed form.
[Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Closed-form_expression) writes
$F_k$ in terms of powers of the golden ratio. Problem 104 uses it to read the *leading* digits of a
60 000-digit Fibonacci number from the fractional part of $k \log_{10}\varphi - \log_{10}\sqrt5$,
and takes the trailing digits from the recurrence mod $10^9$. In Problem 137 the
[generating function](https://en.wikipedia.org/wiki/Generating_function) $x/(1-x-x^2)$ leads to a
[Pell equation](https://en.wikipedia.org/wiki/Pell%27s_equation) whose solutions are products of
Fibonacci numbers. In Problem 321 the minimum move count $n(n+2)$ meets the triangular numbers in
another Pell-like equation.

The recurrence need not be given; it can be *found*. Problem 957 asks how many points a
projective construction has turned blue after 16 days. An exact simulation (in log coordinates,
with FFT sumsets) reaches day 13 before the sets grow too large. On those values the
[Berlekamp–Massey algorithm](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm)
finds an order-five linear recurrence whose characteristic roots are $4, 2, -2, 1, -1$; solving it
gives the count as a polynomial in $4^n$, $2^n$, $(-2)^n$ and $(-1)^n$ over 864. Day 16, or day
1000, is then $O(1)$ big-integer arithmetic.

Non-linear and bitwise recurrences have closed forms more often than one expects:

- Problem 340's "crazy function" generalises the
  [McCarthy 91 function](https://en.wikipedia.org/wiki/McCarthy_91_function). It is a four-deep
  nested recursion with a threshold near $5.6 \times 10^{17}$. Cut $[0, b]$ into blocks of width
  $a$ counted down from $b$, and $F(n)$ is $n$ plus a constant plus a constant per block. Proving
  that takes an induction on the block index. After that the sum over all $b+1$ arguments is two
  triangular numbers and a partial block.
- In Problem 872, the parent of node $k$ is $k$ plus the largest power of two not exceeding the
  gap, so a root path takes one step per set bit.
- Problem 167's Ulam sequences obey an XOR rule, a
  [linear-feedback recurrence](https://en.wikipedia.org/wiki/Linear-feedback_shift_register) over
  $\mathrm{GF}(2)$, which turns $10^{11}$ terms into a period computation.
- Problem 899's game reduces to counting by bit length.
- Problem 711's blackboard game has no recurrence in sight. Instead, its winning starts form two
  families described by bit patterns. Grouping one family by its lowest exponent leaves a weighted
  geometric series $\sum_{m \le L} m x^m$. That series has a closed form of its own,
  $x\bigl(1 - (L+1)x^L + Lx^{L+1}\bigr)/(1-x)^2$, which turns an $O(N)$ loop into
  $O(\log N)$ for $N$ with tens of millions of bits.
- One seed of Problem 1000 decouples across bit positions into an $O(\log n)$ formula.

### 5. Geometry and calculus give the formula directly

Continuous problems often have an exact length, area or optimum:

- Problem 86 unfolds the cuboid, so the spider's path is $\sqrt{a^2 + (b+c)^2}$.
- Problem 126 derives the number of cubes in the $k$-th layer around a cuboid as a quadratic in
  $k$.
- In Problem 222, the axial gap between touching balls in a pipe is $2\sqrt{R(a+b-R)}$.
- Problem 199 grows an Apollonian gasket with
  [Descartes' circle theorem](https://en.wikipedia.org/wiki/Descartes%27_theorem).
- In Problem 246, the points that see the ellipse under more than $45^\circ$ are bounded by its
  [isoptic](https://en.wikipedia.org/wiki/Isoptic) curve.
- In Problem 587, the L-section is the constant $1 - \pi/4$.
- Problem 226 starts from the fact that the blancmange curve passes exactly through the disc's
  centre.
- Problem 177 fixes the diagonal angle and lets the triangle angle sums determine most of the
  eight angles.
- Calculus supplies the optima. Problem 183's best part count sits next to $N/e$, and in Problem
  190 [Lagrange multipliers](https://en.wikipedia.org/wiki/Lagrange_multiplier) give each variable
  its share in closed form.

A discrete optimum has no derivative to set to zero, but an *exchange argument* does the same job:
assume an optimum, and show that a local swap would improve anything not of the claimed shape.
Problem 374 maximises the product of distinct parts. Since $(a+1)(b-1) > ab$ whenever $b - a \ge 2$,
gaps close up until the best partition is a run of consecutive integers with at most one hole. That
shape makes $f(n)$ a factorial divided by one part across almost all of a block of $n$. The blocks
start at triangular offsets, so only about $\sqrt{2N}$ of them reach $N$, and each sums in one
expression.

The [Farey sequence](https://en.wikipedia.org/wiki/Farey_sequence) has a geometry of its own.
Neighbours $a/b < c/d$ satisfy $bc - ad = 1$, so the left neighbour of $3/7$ in Problem 71 is
$n = 3k-1$ over $d = 7k$ with $k = \lfloor N/7 \rfloor$, with no scan at all. Problem 198
characterises ambiguous numbers as midpoints of Farey neighbours. Problem 965 finds that the
minimum fractional part is exactly linear, $bx - a$, on each Farey interval, so the expected value
integrates one interval at a time.

### 6. The inverse: a formula as a test or an oracle

A closed form for a sequence's $k$-th term often inverts into an $O(1)$ **membership test**. The
$k$-th [pentagonal number](https://en.wikipedia.org/wiki/Pentagonal_number) is
$\frac{k(3k-1)}{2}$, so Problem 44 tests whether a number is pentagonal by solving the quadratic
in integers.

A closed form for a *count* also makes a [monotonic](/topics/technique/monotonic-function) oracle
that a binary search can drive:

- Problem 156 counts a digit's appearances up to $n$ in $O(\log n)$, then bisects for the fixed
  points of $f(n,d) = n$.
- Problem 305 counts pattern occurrences in the Champernowne stream up to $N$, then searches for
  the $n$-th.
- Problem 587's area ratio is a decreasing closed form, searched the same way.

Here the formula is no longer the answer. It is the fast inner step that makes an outer search
affordable.

Sometimes the search disappears too, if you invert the *question* as well as the formula. Problem
887 wants the least decision-tree height $Q(N)$ for each of $2.8 \times 10^8$ values of $N$.
Fix the height instead and compute the largest $N$ it can serve, a capacity $F(h)$ given by a
small recurrence. Then the tail-sum identity, which counts each $N$ once for every height
$h < Q(N)$, does the rest:
$\sum_{N \le M} Q(N) = \sum_h \max(0, M - F(h))$. The capacity grows exponentially, so that sum has
only $O(\log M)$ terms.

A closed form can also be solved *symbolically*, so the search never starts. Problem 555 asks for
the [fixed points](https://en.wikipedia.org/wiki/Fixed_point_(mathematics)) of a generalised McCarthy
function with parameters $k$ and $s$. Its value on $[0, m]$ cycles with period $d = k - s$ through a
window of $d$ consecutive integers. Substituting the formula into $M(n) = n$ leaves one condition,
$d \mid s$, that does not mention $n$: either the whole window is fixed or none of it is. The
formula also names the right coordinates. Written in $(d, j)$ with $s = jd$, the answer is a
polynomial in $j$ for each $d$, so each $d$ costs $O(1)$ and the whole sum costs $O(p)$.

## How to reason about it

Reach for a closed form when the naive program is a sum, a count of arrangements, a recurrence or
a simulation, and the input is too large for $O(n)$. The payoff is enormous, but it costs
derivation effort and it brings some standing hazards.

- **Find the formula however you can, then prove it.** Not every closed form here was derived
  first. Problem 313's minimum move count, Problem 321's $n(n+2)$, Problem 256's tatami-free test
  and Problem 167's XOR rule were all *discovered*: an exact brute force (a BFS, a transfer matrix,
  a direct sieve) ran on small cases and the pattern was read off. Problem 957 makes the reading
  off mechanical with Berlekamp–Massey. That is legitimate and often fastest. But the brute force
  stays on as the referee, and the pattern has to be checked well past the cases it was read
  from: Problem 957's recurrence is fixed by ten terms and confirmed by three more. Problem 359's
  occupant formula was read off forty thousand simulated guests and then checked against every
  one of them. Problem 340's block formula was spotted on a memoised brute force, proved by
  induction, and then tested on 400 random small parameter sets. Problem 711's winning families
  were read off an exhaustive game table up to $n = 1100$. Problem 628's blocking criterion was
  checked against exhaustive search for every $n \le 9$ before anything was counted with it.
  Where you sample matters too. Problem 335's $M(x)$ is jagged over all $x$, roughly doubling just
  past each $2^k + 1$, but along the family the statement asks about it is an exact sum of three
  exponentials in $k$. Tabulate on the statement's own index, not the natural one. Not every
  formula here reaches the proof: Problems 335 and 555 rest on their checks alone, and that should
  be said out loud rather than left implied.
- **Keep the slow method behind a flag.** Several solutions keep the obvious $O(N^2)$ version,
  such as Problem 28's spiral walk, behind `--show`. It runs on small inputs purely to confirm the
  formula, because a sign slip is invisible once the loop is gone.
- **An approximate formula still referees.** Problem 804's lattice count has no closed form, but
  the ellipse's area gives its leading term for free. That is a sanity check at the full input
  size, where no brute force can reach.
- **"$O(1)$" can hide real cost.** Problem 15's $\binom{2n}{n}$ takes $O(n)$ big-integer
  multiplications, Problem 162's count is a large integer, and Problem 743's coefficient is an
  $O(k)$ sum. Problem 635's formula is $O(1)$ per prime *given* the factorials, but it needs
  $n! \bmod M$ at points up to $3 \times 10^8$. The running-factorial scan that supplies them is
  the whole cost, and the Python version has to vectorise it in chunks with carries. Count the
  arithmetic on the *values*, not the number of symbols in the formula.
- **Prefer exact integers; distrust roots and logs.** Formulas built from `//` are exact: Problem
  28's `(N * (N * (4*N + 3) + 8) - 9) // 6` always divides evenly. A $\sqrt{\cdot}$ or a $\log$
  invites rounding, so:
  - take square roots with
    [`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) and verify by squaring
    back (Problems 44, 141);
  - compare candidates exactly rather than as floats (Problem 183 decides termination on the
    reduced fraction, not the decimal);
  - a floor of an irrational quotient can still be exact: Problem 950 evaluates
    $\lfloor x/\sqrt m \rfloor$ as $\lfloor \sqrt{\lfloor x^2/m \rfloor} \rfloor$ with `isqrt`;
  - when a float is unavoidable, as with Binet for leading digits in Problem 104, use it only for
    the digits that floating point can actually resolve;
  - rearrange so the float never subtracts near-equal values. Problem 318's per-pair count is a
    ceiling of $d / (-2\log_{10}(\sqrt q - \sqrt p))$. With $\sqrt q - \sqrt p$ close to 1, the
    direct difference loses most of its digits to
    [catastrophic cancellation](https://en.wikipedia.org/wiki/Catastrophic_cancellation).
    Instead, the gap $1 - y$ is written with an exact integer numerator over a positive
    denominator and fed to `log1p`. Any quotient that lands near an integer is recomputed in high
    precision;
  - a formula that yields a rational should be summed as one. Problem 523's expectation is summed
    in `Fraction`s, because a value like $115.725$ sits exactly on a rounding half.
- **Size the intermediates, not just the answer.** A closed form multiplies large factors before
  it divides. Problem 276's answer fits in 64 bits but its $k(k+1)(2k+1)$ does not, so the C port
  works in `__int128`; Problem 957's dominant term grows like $11 \cdot 16^n$, so its C port
  refuses $n > 30$ while Python's unbounded integers take any $n$.
- **Work in the modulus from the start.** When the answer is wanted mod $m$, evaluate the closed
  form with modular inverses and modular powers (Problems 381, 487, 739, 944, 1000). The formula
  only helps if no intermediate is ever formed at full size. Watch for a composite modulus.
  Modulo $10^9$, neither 2 nor 6 has an inverse, so a triangular or pyramidal number cannot be
  "reduced, then divided". Problems 340 and 401 instead divide the even factor (and the multiple
  of 3) exactly *first*, then reduce each factor before multiplying. Check invertibility instead
  of assuming either way. Problem 506's modulus $11111^2$ is composite, yet $10^6 - 1$ shares no
  factor with it, so its geometric sums divide freely. When the divisor really is not invertible,
  as with Problem 605's reducing gcd $g$ (which may contain a 5, while the modulus is $10^8$),
  raise the modulus to $m g^2$, compute the product there, and divide the residue by $g^2$
  exactly.
- **The formula's argument can be too big as well.** Problem 684 evaluates $10^q$ with $q$ near
  $3 \times 10^{17}$, where $q$ comes from a Fibonacci number that will not fit in 64 bits. The
  exponent only matters modulo $p-1$ (Fermat), and the linear term only modulo $p$. So the
  Fibonacci recurrence runs twice, modulo $9p$ and modulo $9(p-1)$. Each residue gives
  $r = f \bmod 9$, and $(f - r)/9$ recovers $q$ in exactly the modulus each part of the formula
  needs.
- **Know when to stop.** Some problems have *no* full closed form. Problem 232's race needs a table
  because optimal play trades off variance state by state, and Problem 210's circle count is a
  Gauss circle sum. There the closed form bounds the search instead (Problem 232 caps the useful
  $T$ at the smallest value with $2^{T-1} \ge b$), or it settles every region except the one that
  genuinely needs a loop. Problem 950's pirate game is closed-form only up to $n = 2C+2$; after
  that, closed forms describe each *run* of failed proposals (constant coins, linearly growing
  walks), so the search jumps run to run, and the runs roughly double, reaching $10^{16}$ in a few
  dozen steps. A derivation can also end on a quantity with no closed form of its own. Problem
  628's ends on the left factorial, so the last step is an $O(n)$ running sum. Problem 718's
  formula sums each class's gaps in $O(1)$, but the Apéry elements still take a pass linear in the
  smallest generator: a prefix minimum along the cycle $iz \bmod x$. Problem 374's block sum ends on
  a [harmonic number](https://en.wikipedia.org/wiki/Harmonic_number) $H_j$, and there the choice of
  what to carry matters. A residue of $H_j$ would cost a modular inverse of every $j$, but the
  scaled $A_j = j!\,H_j$ is an integer with $A_j = j\,A_{j-1} + (j-1)!$, so the same pass runs with
  no division at all. When a leftover quantity has denominators, carry it multiplied through.
- **Evaluate polynomials with [Horner's method](https://en.wikipedia.org/wiki/Horner%27s_method).**
  `N * (N * (a*N + b) + c) + d` keeps intermediates small and uses the fewest multiplications.

The mental checklist is short. *What am I enumerating? Is the per-item quantity a formula in its
index? Does the sum of that formula have a name?* When the answer to the last question is yes, the
loop was never needed.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0232](/solutions/0232/) — The Race
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0510](/solutions/0510/) — Tangent Circles
- ● [0523](/solutions/0523/) — First Sort I
- ● [0555](/solutions/0555/) — McCarthy 91 Function
- ● [0561](/solutions/0561/) — Divisor Pairs
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0628](/solutions/0628/) — Open Chess Positions
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0688](/solutions/0688/) — Piles of Plates
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0950](/solutions/0950/) — Pirate Treasure
- ● [0957](/solutions/0957/) — Point Genesis
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
