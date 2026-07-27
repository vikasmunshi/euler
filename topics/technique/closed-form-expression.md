<!-- tags: [closed-form-expression] -->
<!-- status: final -->
# Closed-form expression

A [closed-form expression](https://en.wikipedia.org/wiki/Closed-form_expression) computes an
answer with a bounded formula — a finite chain of arithmetic, powers, roots and a few named
functions — instead of a loop that walks every case. It is the sharpest single lever in this
whole problem set: where the obvious program is a sum over $n$ terms or a simulation of an
$N \times N$ grid, a closed form collapses the work to $O(1)$ evaluation of an expression whose
size does not grow with the input. The problems below recur because each hides such a formula
behind a process, and the whole game is to find it.

## The idea

The move is always the same in spirit: stop *enumerating* the objects and start *counting* or
*summing* them algebraically. Three shapes cover most of it.

**Sums that telescope into polynomials.** The [arithmetic series](https://en.wikipedia.org/wiki/Arithmetic_progression)
$d + 2d + \dots + nd = d\,\frac{n(n+1)}{2}$ is the seed. Problem 1 sums the multiples of 3 or 5
below a limit not by looping but by adding three such closed forms under the
[inclusion–exclusion principle](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
(multiples of 3, plus of 5, minus of 15):

```python
def sum_arithmetic_series(common_difference, *, max_limit):
    n = (max_limit - 1) // common_difference
    return common_difference * (n * (n + 1)) // 2
```

The same family reaches further: the sum of squares $\frac{n(n+1)(2n+1)}{6}$ and the square of
the sum $\left(\frac{n(n+1)}{2}\right)^2$ give Problem 6 in one line, and higher power sums are
the [Faulhaber](https://en.wikipedia.org/wiki/Faulhaber%27s_formula) polynomials. Problem 28 is
the same trick worn as geometry: the four corners of each ring of a number spiral form an
arithmetic pattern, and [summing](https://en.wikipedia.org/wiki/Summation) it over every ring
folds an $O(N^2)$ grid simulation into a single cubic in $N$.

**Counting without listing.** [Combinatorial](https://en.wikipedia.org/wiki/Combinatorics)
identities count arrangements directly. Problem 15 counts monotone lattice paths across an
$n \times n$ grid as the [central binomial coefficient](https://en.wikipedia.org/wiki/Central_binomial_coefficient)
$\binom{2n}{n}$ — no path is ever generated.

**Recurrences that have a formula.** A linear recurrence with constant coefficients has a
closed form. [Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Closed-form_expression)
gives the $n$-th Fibonacci number from powers of the golden ratio; the "golden nuggets" of
Problem 137 and the Pell-equation families sit on this same machinery, turning an unbounded search
into a formula you evaluate.

A fourth, quieter use is the **inverse** direction: a closed form for a sequence's $k$-th term
often inverts into an $O(1)$ *membership test*. Because the $k$-th [pentagonal number](https://en.wikipedia.org/wiki/Pentagonal_number)
is $\frac{k(3k-1)}{2}$, you can test whether a given integer is pentagonal by solving the quadratic
and checking the root is an integer — which is what makes Problem 44's search over pairs feasible.

## How to reason about it

Reach for a closed form when the naive solution is a sum, a count of arrangements, or a linear
recurrence, and the input is large enough that $O(n)$ or $O(n^2)$ will not finish. The payoff is
enormous — constant time — but it is bought with derivation effort, and it comes with three
standing hazards.

- **"$O(1)$" can still hide real cost.** Problem 15's $\binom{2n}{n}$ is a formula, but the
  factorials are big integers, so the evaluation is $O(n)$ big-integer multiplications, not truly
  constant. Count the arithmetic on the *values*, not just the terms.
- **Prefer exact integers; distrust roots.** Formulas built from `//` on integers are exact —
  Problem 28's cubic is always divisible by 6 for odd $N$, so no rounding ever enters. But the
  moment a closed form contains a $\sqrt{\cdot}$ (Binet, the pentagonal test), floating point can
  round $\sqrt{k^2}$ to the wrong side of an integer for large $k$. Do the root in integers
  ([`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt)) and verify by squaring
  back, rather than trusting a float compare.
- **Evaluate polynomials with [Horner's method](https://en.wikipedia.org/wiki/Horner%27s_method).**
  Write $aN^3 + bN^2 + cN + d$ as nested multiplication (`N * (N * (a*N + b) + c) + d`): three
  multiplications, no large intermediate powers. Problem 28's `(N * (N * (4*N + 3) + 8) - 9) // 6`
  is exactly this.

The last discipline worth keeping is a **cross-check**. A closed form is only as good as its
derivation, and a sign slip is invisible once the loop is gone. Several of these solutions keep the
slow, obvious method — the $O(N^2)$ spiral in Problem 28, for instance — behind a `--show` flag,
running it on small inputs purely to confirm the formula agrees. Derive the formula, then prove it
against the brute force you replaced.

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
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0288](/solutions/0288/) — An Enormous Factorial
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
