<!-- tags: [concave-function] -->
<!-- status: final -->
# Concave function

A function is [concave](https://en.wikipedia.org/wiki/Concave_function) when the chord between
any two points of its graph lies on or below the graph:
$f(tx + (1-t)y) \ge t f(x) + (1-t) f(y)$. For a twice-differentiable function that means
$f'' \le 0$, and the standard examples are $\ln x$, $\sqrt{x}$ and $-x^2$. Concavity matters in
optimisation because it removes the usual difficulties. A concave function has no false peaks: any local
maximum is global, any stationary point is a maximum, and on the integers the best point is next
to the real optimum. The three solved problems below are optimisations. Each becomes a formula or a
small DP once the concave function is identified, usually after taking a logarithm.

## The idea — what concavity buys

Three consequences carry nearly all the weight:

1. **Stationary means optimal.** If $f$ is concave and $\nabla f(x^*) = 0$ (or, under linear
   constraints, the [Lagrange](/topics/domain/lagrange-multiplier) conditions hold), then $x^*$
   is a *global* maximum. A sum of concave functions is concave, so this holds for objectives like
   $\sum_i w_i \ln x_i$.
2. **Unimodality on the integers.** A concave function of one variable rises and then falls. If its
   real maximiser is $k^*$, the integer maximiser is $\lfloor k^* \rfloor$ or $\lceil k^* \rceil$,
   and two evaluations settle it. No scan is needed.
3. **Spreading lowers a concave sum.** By
   [Jensen's inequality](https://en.wikipedia.org/wiki/Jensen%27s_inequality), and more generally
   [Karamata's](https://en.wikipedia.org/wiki/Karamata%27s_inequality), $\sum f(s_i)$ with a
   fixed $\sum s_i$ is *largest* when the $s_i$ are equal and *smaller* the more spread out they are.
   Minimising a concave sum therefore pushes the arguments apart, and maximising one pulls them together.

The usual way in is the logarithm. Products such as $r^k$ or $\prod x_i^i$ are not concave, but their
logarithms are sums of concave terms, and because $\ln$ is increasing, maximising the log maximises
the product.

## Three uses across the problems

**183, maximum product of parts: unimodality picks two candidates.** Split $N$ into $k$ equal
parts and maximise $P = (N/k)^k$. With $k$ treated as real, $\ln P = k(\ln N - \ln k)$ has second
derivative $-1/k < 0$. It is concave and peaks where its derivative $\ln N - \ln k - 1$ vanishes,
at $k = N/e$ (hence the [e](/topics/domain/e-mathematical-constant) tag). By consequence 2 the
integer optimum is $\lfloor N/e \rfloor$ or $\lceil N/e \rceil$. The solution compares $\ln P$ at
the two and never forms $P$. The rest of the problem is exact arithmetic: $(N/k)^k$ terminates iff
the reduced denominator $k/\gcd(N,k)$ has no prime factors other than 2 and 5
([repeating decimal](/topics/domain/repeating-decimal)).

**190, maximising a weighted product: stationary means optimal.** Maximise
$\prod x_i^{\,i}$ subject to $\sum x_i = m$. The log-objective $\sum i \ln x_i$ is a weighted sum of
concave functions and the constraint is linear, so the single Lagrange stationary point,
$i / x_i = \lambda$, giving $x_i = 2i/(m+1)$, is the global maximum by consequence 1. No search and
no second-order check are needed. Weighted [AM–GM](https://en.wikipedia.org/wiki/Inequality_of_arithmetic_and_geometric_means)
gives the same answer, because AM–GM is itself Jensen's inequality for $\ln$.

**222, sphere packing: spreading shapes the arrangement.** Balls of radii 30 to 50 sit in a pipe
of radius 50, and consecutive balls of radii $a, b$ need an axial gap of $2\sqrt{R(a+b-R)}$, which is
concave in the pair sum $a + b$. The total pair sum is $2\sum r - r_\text{first} - r_\text{last}$,
so the interior ordering cannot change it. Concavity then decides the arrangement. By consequence 3
the gap total is smallest when the pair sums are as unequal as possible, which means neighbours of
similar size. Interleaving small with large is the worst choice, since it makes every pair sum
about 80. Sorted neighbours give pair sums from about 61 to about 98. The best arrangement is a
**valley**: the smallest ball in the middle and radii rising toward both ends. Concavity also
settles the endpoints. A gap's marginal cost, $\sqrt{R/(s - R)}$, is above 1 for pair sums near
the top of the range, so moving radius out of the gaps and into the two exposed ends is a net
saving, even though each end adds its full radius. Rather than trusting the exact interleaving,
the solution runs an $O(n^2)$ DP over all valleys. It inserts balls smallest first onto either end of the
chain, and the brute force over every permutation for up to nine balls confirms it.

## Python and C

All three are line-for-line ports. The differences are idiom only:

- **183**: Python uses `math.e`, `math.log` and `math.gcd`; C uses `M_E`, `log` and a hand-written
  Euclid. Both break a tie toward the floor, so the two languages pick the same $k$.
- **190**: `(2.0 * i / (m + 1)) ** i` in Python and `pow(2.0 * i / (m + 1), i)` in C. The product is
  at most a few thousand for $m \le 15$, so double precision cannot push $\lfloor P_m \rfloor$
  across an integer.
- **222**: the DP layer is a `dict` from "other end" index to cost in Python, which holds only reachable states. C uses two
  `double` arrays initialised to `INFINITY` and swaps them between layers.

## How to reason about it

- **Take the log of a product first.** $r^k$, $\prod x_i^{w_i}$ and likelihoods all become sums of
  concave terms, and the optimisation becomes routine.
- **Check concavity before searching.** If the objective is concave, a stationary point or the two
  integers next to the real optimum is the whole answer. A scan or numerical search there is wasted work.
- **Use Jensen in both directions.** Equalise the arguments to *maximise* a concave sum (190, where the
  ratios $x_i / i$ are equal) and spread them to *minimise* one (222, where neighbour pair sums are spread).
- **Compare in log space.** Choosing between $\lfloor N/e \rfloor$ and $\lceil N/e \rceil$ needs only
  $k(\ln N - \ln k)$, not the huge $P$.
- **Concave is maximise-friendly. For a concave minimisation, verify by brute force.** The minimum of a concave function lies at an
  extreme point, so there is no stationary-point shortcut. 222 uses concavity to restrict the search to valleys and then
  checks small cases exhaustively.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0222](/solutions/0222/) — Sphere Packing

<!-- /problems -->
