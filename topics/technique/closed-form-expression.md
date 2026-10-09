<!-- tags: [closed-form-expression] -->
<!-- status: final -->
# Closed-form expression

A [closed-form expression](https://en.wikipedia.org/wiki/Closed-form_expression) computes a
quantity with a bounded formula — a finite chain of arithmetic, powers, roots, binomials and a few
named functions — instead of a loop that walks every case. It is the most common single lever in
this problem set: the sixty-six problems below each hide a formula behind a process, a grid, a game
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
  sum becomes one exponentiation inside a root-finder.
- **Separable sums.** When a per-item count factors as $f(m)\,g(n)$, its sum over all sub-grids is
  the product of two one-dimensional sums. This turns Problem 147's axis-aligned rectangles into a
  product of [tetrahedral numbers](https://en.wikipedia.org/wiki/Tetrahedral_number). Problem 234
  uses the triangular-number formula to sum the multiples of $p$ and $q$ between consecutive prime
  squares: one band per prime instead of one step per integer.
- **Double counting.** Problem 944 swaps the order of summation, tallying each integer's
  contribution across all $2^n$ subsets. It lands on a closed form whose one remaining sum runs
  over the $O(\sqrt n)$ distinct values of $\lfloor n/x \rfloor$.

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

Probability is counting with weights, and the same trick applies.
[Linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity) turns Problem
493's expected number of colours into seven copies of one ratio of binomials. Problem 253 shows
that the gap widths of a random fill form a uniform random
[composition](https://en.wikipedia.org/wiki/Composition_(combinatorics)). Its marginals have closed
forms, so the gaps drop out of the state entirely.

Smaller counting formulas often sit *inside* a search as its $O(1)$ kernel:

- Problem 86 counts the $(b, c)$ pairs with a given sum in constant time.
- Problem 145's digit DP counts the digit pairs with a given sum directly.
- Problem 173 writes every square lamina as $4t(t+h)$ tiles.
- Problem 207 shows its partitions are indexed by the pronic numbers $n(n-1)$.
- Problem 210's two half-plane regions are exact polynomials in $r$. Only the circle resists a
  closed form, since it is a
  [Gauss circle problem](https://en.wikipedia.org/wiki/Gauss_circle_problem), so it is summed row
  by row.

### 3. A theorem collapses the statement

Many problems look computational until one classical theorem reduces them to a formula:

| Theorem | What it collapses | Problems |
|---|---|---|
| [Binomial theorem](https://en.wikipedia.org/wiki/Binomial_theorem) mod $a^2$ | $(a\pm1)^n$ to two surviving terms | 120 |
| [Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) | binomials mod $p$ to products over base-$p$ digits | 148, 242 |
| [Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem) / [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) | the prime exponent in $n!$ or $\binom{n}{m}$ to digit sums | 288, 704 |
| [Wilson's theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem) | $(p-k)!$ mod $p$ to a fixed modular fraction | 381 |
| [Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function) multiplicativity | $\varphi(pq) = (p-1)(q-1)$, with no factoring | 70 |
| [Digital root](https://en.wikipedia.org/wiki/Digital_root) congruence | $\operatorname{dr}(k) = 1 + (k-1) \bmod 9$ | 159 |
| [Cayley–Hamilton](https://en.wikipedia.org/wiki/Cayley%E2%80%93Hamilton_theorem) | a $2\times2$ square root to two scalars, trace and determinant | 420 |
| [Divisor function](https://en.wikipedia.org/wiki/Divisor_function) | counting the right triangles on a leg to $\tau(M^2)$ | 176 |
| [Fermat's Last Theorem](https://en.wikipedia.org/wiki/Fermat%27s_Last_Theorem) | an exponent search to $\lvert n\rvert \le 2$, once the expression is factored | 180 |

The step before the theorem is usually **algebra on the statement itself**:

- Problem 180's three intimidating functions factor to $(x+y+z)(x^n + y^n - z^n)$.
- Problem 168's rotation condition is a linear equation that, given the digit count, the last
  digit and the ratio, solves for the leading part.
- Problem 141's "divisor, quotient and remainder in geometric progression" becomes the explicit
  parametrisation $n = k^2 p^3 q + k q^2$.
- Problem 772's balanceability is equivalent to a clean divisibility condition.
- Problem 269's integer-root condition becomes a divisibility test that prunes a digit DP down to a
  handful of candidate roots.

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

Non-linear and bitwise recurrences have closed forms more often than one expects:

- In Problem 872, the parent of node $k$ is $k$ plus the largest power of two not exceeding the
  gap, so a root path takes one step per set bit.
- Problem 167's Ulam sequences obey an XOR rule, a
  [linear-feedback recurrence](https://en.wikipedia.org/wiki/Linear-feedback_shift_register) over
  $\mathrm{GF}(2)$, which turns $10^{11}$ terms into a period computation.
- Problem 899's game reduces to counting by bit length.
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

## How to reason about it

Reach for a closed form when the naive program is a sum, a count of arrangements, a recurrence or
a simulation, and the input is too large for $O(n)$. The payoff is enormous, but it costs
derivation effort and it brings some standing hazards.

- **Find the formula however you can, then prove it.** Not every closed form here was derived
  first. Problem 313's minimum move count, Problem 321's $n(n+2)$, Problem 256's tatami-free test
  and Problem 167's XOR rule were all *discovered*: an exact brute force (a BFS, a transfer matrix,
  a direct sieve) ran on small cases and the pattern was read off. That is legitimate and often
  fastest. But the brute force stays on as the referee, and the pattern has to be checked well
  past the cases it was read from.
- **Keep the slow method behind a flag.** Several solutions keep the obvious $O(N^2)$ version,
  such as Problem 28's spiral walk, behind `--show`. It runs on small inputs purely to confirm the
  formula, because a sign slip is invisible once the loop is gone.
- **"$O(1)$" can hide real cost.** Problem 15's $\binom{2n}{n}$ takes $O(n)$ big-integer
  multiplications, Problem 162's count is a large integer, and Problem 743's coefficient is an
  $O(k)$ sum. Count the arithmetic on the *values*, not the number of symbols in the formula.
- **Prefer exact integers; distrust roots and logs.** Formulas built from `//` are exact: Problem
  28's `(N * (N * (4*N + 3) + 8) - 9) // 6` always divides evenly. A $\sqrt{\cdot}$ or a $\log$
  invites rounding, so:
  - take square roots with
    [`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) and verify by squaring
    back (Problems 44, 141);
  - compare candidates exactly rather than as floats (Problem 183 decides termination on the
    reduced fraction, not the decimal);
  - when a float is unavoidable, as with Binet for leading digits in Problem 104, use it only for
    the digits that floating point can actually resolve.
- **Work in the modulus from the start.** When the answer is wanted mod $m$, evaluate the closed
  form with modular inverses and modular powers (Problems 381, 487, 944, 1000). The formula only
  helps if no intermediate is ever formed at full size.
- **Know when to stop.** Some problems have *no* full closed form. Problem 232's race needs a table
  because optimal play trades off variance state by state, and Problem 210's circle count is a
  Gauss circle sum. There the closed form bounds the search instead (Problem 232 caps the useful
  $T$ at the smallest value with $2^{T-1} \ge b$), or it settles every region except the one that
  genuinely needs a loop.
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
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
