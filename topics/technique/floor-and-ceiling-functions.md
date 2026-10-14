<!-- tags: [floor-and-ceiling-functions] -->
<!-- status: final 2026-10-12T14:37Z -->
# Floor and ceiling functions

The [floor and ceiling](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) functions round
a real number down or up to an integer: $\lfloor x \rfloor$ is the largest integer at most $x$, and
$\lceil x \rceil$ the smallest at least $x$. They look like formatting, but in these problems they
do real work. A floor is how you *count* without enumerating, how you get an *exact* integer
bound out of an irrational quantity, how a continuous optimum becomes an integer one, and how a
real-valued process gets squeezed into a finite set of states. Each of the problems below uses
at least one of those jobs, and the code side of all of them is the same discipline: stay in
integers, and know which way your division rounds.

## The idea: five jobs a floor does

**1. Counting.** The number of multiples of $d$ in $[1, N]$ is $\lfloor N/d \rfloor$, and that one
fact turns many sums over divisors into sums over quotients. In Problem 694, counting pairs
$(d, i)$ with $d$ cube-full and $d \mid i \le N$ in the other order gives
$\sum_{d \text{ cube-full}} \lfloor N/d \rfloor$. Problem 745 reorders a sum over largest square
divisors into $\sum_m h(m) \lfloor N/m^2 \rfloor$. Problems 195 and 257 count every scaled copy of a
primitive shape with a single $\lfloor Q / q \rfloor$, rather than generating the copies. Problem
899 counts its losing Nim pairs per bit length with $\lfloor (n+1)/2^k \rfloor$. Counting the
members of a residue class in an interval is two floors, as in Problem 198's helper:

$$\#\{t \in [lo, hi] : t \equiv r \pmod m\} = \left\lfloor \tfrac{hi - r}{m} \right\rfloor - \left\lfloor \tfrac{lo - 1 - r}{m} \right\rfloor.$$

**2. Few distinct quotients.** $\lfloor n/x \rfloor$ takes only about $2\sqrt n$ distinct values as
$x$ runs over $1..n$, and each value holds on a contiguous run of $x$. So a sum
$\sum_x g(x) \lfloor n/x \rfloor$ collapses to $O(\sqrt n)$ blocks when $g$ has a cheap prefix sum.
That is [quotient blocking](/topics/technique/quotient-blocking), the decisive step in Problem
944. Problem 255 uses the same structure the other way round: a ceiling quotient $\lceil n/x \rceil$
is constant on blocks of $n$, so whole intervals of inputs follow one path through Heron's method.
The [nested-floor identity](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions)
$\lfloor \lfloor n/a \rfloor / b \rfloor = \lfloor n/(ab) \rfloor$ lets Problem 694 fold a constant
factor into the floor once, so its inner loop divides by a plain cube.

**3. Exact floors of irrational quantities.** Never compute $\lfloor x\sqrt m \rfloor$ with a float.
For integers $x \ge 0$ and $m > 0$, squaring moves the irrational part inside an
[integer square root](/topics/technique/integer-square-root):

$$\lfloor x\sqrt m \rfloor = \operatorname{isqrt}(x^2 m), \qquad \lfloor x / \sqrt m \rfloor = \operatorname{isqrt}(\lfloor x^2 / m \rfloor).$$

Problem 195 computes its bound $\lfloor 2\sqrt3\,n \rfloor$ as $\operatorname{isqrt}(12 n^2)$.
Problem 257 places a window edge at $\lceil q\sqrt k \rceil$ the same way, so no rounding can shift
a boundary. Problem 950 prices every pirate vote with $\lfloor x / \sqrt m \rfloor$, and because $m$
is never a perfect square the comparison is never ambiguous. In C the squared argument is the
part that overflows. 950 squares values near $10^{18}$, so it needs
[`__int128`](/topics/technique/int128) there, and an isqrt seeded from `sqrtl` and corrected by exact
multiplication.

**4. From a continuous optimum to an integer one.** If $f$ is unimodal over the reals with peak at
$x^*$, the best integer is $\lfloor x^* \rfloor$ or $\lceil x^* \rceil$, so you only have to compare
two values. Problem 183 maximises a product over the number of parts. The real optimum is $N/e$,
and it evaluates both neighbours in log space so it never forms the huge product.

**5. Discretising a process.** A floor that truncates to a fixed precision turns a real-valued map
into one on a finite set, and a deterministic map on a finite set is eventually periodic. Problem
197's map truncates to nine decimals, which is why its orbit lands on an exact two-cycle that can
be detected by equality, with no tolerance. That's
[cycle detection](/topics/technique/cycle-detection) made possible by a floor. Problem 820
extracts one decimal digit as $\lfloor 10 r / k \rfloor$ from a residue $r$, so a digit far down an
expansion needs only modular arithmetic.

## In code: which way does division round?

Python's `//` is a true floor and rounds toward $-\infty$. C's `/` *truncates* toward zero. The two
agree for non-negative operands and differ for negative ones, which is a classic source of
off-by-one errors in a port. Problems 198, 277 and 305 all carry a floor-division helper in C for
exactly this reason:

```c
static long long floor_div(long long a, long long b) {      /* b > 0 */
    return a >= 0 ? a / b : -((-a + b - 1) / b);
}
```

The ceiling follows from the floor: in Python, `-(-a // b)` is $\lceil a/b \rceil$ for any sign of
`a`. Rounding half-up is a floor too. Problem 255 needs a mean exactly to ten decimal places, so it
keeps the total as an integer and rounds with
$\lfloor (2 \cdot \text{total} \cdot 10^{10} + \text{count}) / (2 \cdot \text{count}) \rfloor$, with
no float anywhere. Sums of floors often have closed forms. For example,
$\sum_{n=1}^{L} \lfloor (n-1)/2 \rfloor = \lfloor (L-1)^2/4 \rfloor$, which Problem 950 uses to add
its linear prefix in one step.

## How to reason about it

- **Read a floor as a count.** When $\lfloor N/d \rfloor$ appears, ask what it counts. That usually
  shows an order of summation that is cheaper: sum over the divisor instead of the multiple.
- **Look for the $O(\sqrt n)$ collapse.** Any sum indexed by $x$ that touches $n$ only through
  $\lfloor n/x \rfloor$ can be blocked.
- **Square before you floor.** For a bound that involves a square root, compare squares of
  integers. The float version is right almost everywhere and wrong at exactly the boundary cases
  the problem is testing. Problem 210 needs the floor of values past $2^{53}$, so it takes a
  float64 estimate and then corrects it to the exact integer.
- **Check signs in every C port.** Any division whose numerator can go negative needs the floor
  helper, not `/`. A negative congruence offset, a bound below zero, or a difference of two
  positions are the usual cases.
- **Mind the width of the squared argument.** $x^2 m$ overflows 64 bits long before $x$ does.
  Estimate it, and widen just that expression.

The [domain page on the floor function](/topics/domain/floor-function) collects the problems whose
*statement* is built from floors. This page is about the floor as a tool.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0950](/solutions/0950/) — Pirate Treasure

<!-- /problems -->
