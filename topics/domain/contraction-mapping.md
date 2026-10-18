<!-- tags: [contraction-mapping] -->
<!-- status: final -->
# Contraction mapping

A [contraction mapping](https://en.wikipedia.org/wiki/Contraction_mapping) is a map $T$ that
brings every pair of points closer by at least a fixed factor $r < 1$:
$d(T x, T y) \le r\, d(x, y)$. The
[Banach fixed-point theorem](https://en.wikipedia.org/wiki/Banach_fixed-point_theorem) then gives
three things at once. $T$ has exactly one fixed point. Iterating $T$ from *any* start converges
to it. And the error after $n$ steps is bounded in advance:

$$d(x_n, x^*) \le \frac{r^n}{1 - r}\, d(x_1, x_0).$$

Problems that look unrelated, a sequence defined by an ugly recurrence, a number defined by its own
digits, a fractal tree, all become easy once you see the contraction in them, because that bound
tells you both that the iteration converges and how far it must run. The three solved problems
below find a contraction in three different metrics: ordinary distance on the real line, "number
of agreeing leading digits", and distance between sets in the plane.

## The idea — find the metric in which the map shrinks

The theorem needs two ingredients: a complete metric space and a map that shrinks distances in it.
The second is where the work is. A map that is not a contraction in the obvious metric is often a
contraction in a better one, or after composing it with itself, or on a smaller region. Once a
contraction is found, the practical consequences are:

- **Start anywhere.** Convergence does not depend on a clever seed, so a crude one is fine.
- **Know when to stop.** The a priori bound turns a tolerance $\varepsilon$ into a step count,
  $n \ge \log(\varepsilon(1-r)/d_0) / \log r$, and the a posteriori bound
  $d(x_n, x^*) \le \frac{r}{1-r} d(x_n, x_{n-1})$ lets you stop when two successive iterates agree
  closely enough.
- **Uniqueness is free.** There is nothing else to find, so a converged iterate *is* the answer.

[Fixed-point iteration](/topics/technique/fixed-point-iteration) is the algorithm and contraction
is the reason it works.

## Three metrics across the problems

**197, a recursively defined sequence: the real line, after two steps.** The sequence is
$u_{k+1} = f(u_k)$ with $f(x) = \lfloor 2^{30.403243784 - x^2} \rfloor \cdot 10^{-9}$, and the
question is $u_n + u_{n+1}$ for $n = 10^{12}$. $f$ is not a contraction where the orbit lives, and
the orbit does not settle on a fixed point. It alternates between two values. But $f \circ f$
contracts near that pair, so the even and odd subsequences each converge to a fixed point of
$f \circ f$, an attracting [period-2 point](/topics/domain/periodic-point). In floating point the
convergence is not just asymptotic. A double has finitely many values, and the floor makes $f$
coarser still, so the orbit lands *exactly* on the 2-cycle after about 520 steps. The solution
iterates until $u_k = u_{k-2}$ bit for bit and stops. The exact equality test is correct here, not
a hazard. The state of the iteration is the single value $u_k$, so once a value recurs, everything
after it repeats exactly. That is [cycle detection](/topics/technique/cycle-detection) with the
cycle length known in advance to be 2.

**751, concatenation coincidence: the agreeing-digits metric.** A real $\theta \ge 2$ generates a
sequence $b_1 = \theta$, $b_n = \lfloor b_{n-1} \rfloor (b_{n-1} - \lfloor b_{n-1} \rfloor + 1)$,
and the integer parts $a_n = \lfloor b_n \rfloor$ concatenated after the decimal point give a new
number $\tau = a_1.a_2a_3\ldots$. The problem asks for the $\theta$ with $\tau = \theta$. On the
real line the map $\theta \mapsto \tau$ is not even continuous (it jumps whenever some $b_n$
crosses an integer). But measure distance as $10^{-k}$, where $k$ is the number of leading digits
two numbers share, and near the fixed point it behaves as a contraction: a change far out in
$\theta$ moves $\tau$ only further out. The leading digits of $\theta$ settle the first terms
$a_n$, and since each term is written out in full, those terms fill the leading digits of $\tau$
with something to spare. So iterating from the crude seed $\theta = 2$ gains digits on every pass, and the
solution stops when the leading 40 digits of two successive iterates agree. That is the a
posteriori stopping rule in this metric. The cost is precision. Each step of the $b_n$ recurrence
multiplies the fractional part by $\lfloor b_{n-1} \rfloor$, losing about a digit per term, so the
solution works at 160 significant digits with Python's [`decimal`](/topics/technique/decimal) to
deliver 24.

**395, Pythagorean tree: the Hausdorff metric on sets.** The tree is the unit square together with
its images under two similarities, $z \mapsto i + wz$ and $z \mapsto i + w + (1-w)z$, which scale
by $|w|$ and $|1-w|$, both below 1. Hutchinson's theorem applies Banach's to the map
$S \mapsto \text{square} \cup f_1(S) \cup f_2(S)$ on compact sets with the
[Hausdorff distance](https://en.wikipedia.org/wiki/Hausdorff_distance): it contracts by
$r = \max(|w|, |1-w|)$, so the tree exists, is unique, and is the limit of the finite trees. The
solution needs the tree's bounding box, and it uses the contraction twice. First, to find a disk
that holds the whole tree, it takes a centre $c$ and the smallest radius $R$ that covers the unit
square and satisfies $|f_k(c) - c| + |w_k| R \le R$ for both maps, which is $R \ge |f_k(c) - c| / (1 - |w_k|)$. That is
Banach's a priori bound with $c$ as the starting point. Second, below depth $n$ every subtree lies in
a copy of that disk scaled by $r^n$, so the depth is chosen to make $2Rr^n$ smaller than the
tolerance, and the [support function](/topics/technique/support-function) DP is run with the deep
tree replaced by the bare square (a lower bound) and by the disk (an upper bound). See
[fractal](/topics/domain/fractal) for how that bracket is used.

## Python and C

- **197** is a line-for-line port. Python's `2.0 ** x` and C's `pow(2.0, x)` both reach the
  platform `pow`, and `floor` and the multiply by `1e-9` are IEEE operations, so both languages walk
  the same orbit and reach the same 2-cycle at the same step. Neither side needs a tolerance,
  because the exact-equality cycle check is equally valid in both.
- **395** maps Python's `complex` onto C99 `<complex.h>`. The bounding-disk computation (the
  Banach bound) and the two truncated DPs are the same in both.
- **751** has no C twin. The solution depends on arbitrary-precision *decimal* arithmetic, which
  Python provides in `decimal`. A C version would need MPFR or GMP's `mpf_t` with explicit precision
  management, plus binary-to-decimal conversion on every pass to read off the digits $a_n$.

## How to reason about it

- **When a problem defines something by a self-referential rule, ask whether the rule
  contracts.** A self-describing number, the limit of a recurrence and the attractor of a set of
  maps are all fixed points. If the map contracts, iteration from any start finds the fixed point.
- **Try other metrics before giving up on contraction.** Digit agreement (751) and the Hausdorff
  metric (395) make maps contract that are discontinuous or set-valued in the usual sense.
- **Try iterating twice.** A map whose orbit oscillates may have $f \circ f$ contracting (197). The
  answer is then a cycle, not a point.
- **Derive the stopping point.** With the ratio $r$ known, the a priori bound gives the step count
  and the a posteriori bound gives a test on successive iterates. Either is better than "iterate
  until it looks stable" with no reason behind the threshold.
- **In floating point, expect exact convergence.** A contraction on a finite set of doubles ends in
  an exact cycle, so testing for exact repetition is valid, and it avoids choosing a tolerance at
  all.
- **Budget precision for amplification.** If each step magnifies errors (751's digit erosion),
  the working precision must cover the target digits plus the loss over the whole iteration.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0751](/solutions/0751/) — Concatenation Coincidence

<!-- /problems -->
