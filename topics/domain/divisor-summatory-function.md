<!-- tags: [divisor-summatory-function] -->
<!-- status: final 2026-10-29T07:14Z -->
# Divisor summatory function

The [divisor summatory function](https://en.wikipedia.org/wiki/Divisor_summatory_function)
$D(x) = \sum_{n \le x} d(n)$ adds up the divisor counts of every integer up to $x$. Its weighted
relatives $\sum_{n \le x} \sigma_k(n)$ do the same for divisor *sums*. The
[divisor function](/topics/domain/divisor-function) page is about one $\sigma_k(n)$ and the
factorisation behind it. This page is about the running total, and that is a different problem:
$x$ is $10^{8}$ to $10^{18}$, far past any sieve, and no individual $\sigma_k(n)$ is ever computed.
The problems below keep landing here because "sum something over the divisors of every $n$ up to
$N$" is what many counting questions reduce to, once their Gaussian integers, cube-full numbers or
dice have been translated away.

## The idea: count from the divisor's side

Every summatory divisor sum is a double sum over pairs $(d, n)$ with $d \mid n \le x$. Summing over
$n$ first is the slow order, because each $n$ has its own irregular divisor list. Summing over $d$
first is regular: a fixed $d$ divides exactly $\lfloor x/d \rfloor$ of the integers up to $x$. So

$$D(x) = \sum_{d \le x} \left\lfloor \frac{x}{d} \right\rfloor, \qquad
\sum_{n \le x} \sigma_k(n) = \sum_{d \le x} d^k \left\lfloor \frac{x}{d} \right\rfloor .$$

The swap does not need $d$ to range over *all* integers. If $s(n)$ counts (or weights) only the
divisors of $n$ that lie in some set $A$, the same argument gives

$$\sum_{n \le x} \sum_{\substack{d \mid n \\ d \in A}} f(d) = \sum_{\substack{d \le x \\ d \in A}} f(d) \left\lfloor \frac{x}{d} \right\rfloor .$$

That one identity is the shared move. What changes from problem to problem is how the right-hand
side gets evaluated, and that depends on what $A$ looks like.

- **$A$ is every integer** (and $\sum f$ has a closed form): the
  [floor function](/topics/domain/floor-function) $\lfloor x/d \rfloor$ takes only $O(\sqrt x)$
  distinct values. [Quotient blocking](/topics/technique/quotient-blocking) walks those runs, or the
  [Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method) reflects the far half
  onto the other axis. Either way it costs $O(\sqrt x)$:

  ```python
  def D(x):                      # sum of d(n) for n <= x
      s = isqrt(x)
      return 2 * sum(x // k for k in range(1, s + 1)) - s * s
  ```

- **$A$ is sparse**: enumerate it. When $|A \cap [1, x]|$ is much smaller than $\sqrt x$, a direct
  loop over the members of $A$ beats any blocking.
- **$D$ is a subroutine**: the summatory function is evaluated at many arguments $\lfloor N/r \rfloor$
  inside a larger sum. Then the fact that matters is $\lfloor \lfloor N/a \rfloor / b \rfloor
  = \lfloor N/(ab) \rfloor$: every argument that ever reaches $D$ is one of the $O(\sqrt N)$
  quotients of $N$, so a memo keyed on the argument stays small and pays off heavily.

## How it plays out across the problems

**Problem 401** is the direct case: $\sum_{n \le 10^{15}} \sigma_2(n)$ modulo $10^9$. After the
swap, $f(d) = d^2$ has the square-pyramidal closed form $x(x+1)(2x+1)/6$, and the hyperbola split
gives about $3 \times 10^7$ terms per strip. The method itself is written up on the
[hyperbola page](/topics/technique/dirichlet-hyperbola-method). Seen from this page, 401 is the
textbook evaluation of $\sum \sigma_k$ for $k = 2$.

**Problem 694** is the sparse case. $s(n)$ counts the *cube-full* divisors of $n$ (every prime
exponent at least 3), and the target is $\sum_{n \le 10^{18}} s(n)$. Swapping gives
$\sum \lfloor x/d \rfloor$ over cube-full $d \le x$. There are only $\Theta(x^{1/3})$ of those,
about a million at $10^{18}$, so the solution enumerates them instead of blocking. A cube-full
number factors uniquely as $m_3^3 m_4^4 m_5^5$ with $m_4, m_5$
[squarefree](/topics/domain/square-free-integer) and coprime: for one prime, each exponent $e \ge 3$
is $3a + 4b + 5c$ in exactly one way once $b = c = 1$ is ruled out. Each $d$ is therefore generated
exactly once, and the innermost loop over $m_3$ is itself a small summatory sum,
$\sum_k \lfloor y/k^3 \rfloor$. The total is $O(x^{1/3})$, cheaper than the $O(\sqrt x)$ the full
divisor set would cost. A restricted divisor set makes the problem easier, not harder.

**Problem 153** is the subroutine case. The sum of the real parts of all
[Gaussian-integer](/topics/technique/gaussian-integer) divisors of $n$, totalled over
$n \le 10^8$, reduces to ordinary integer divisibility: $a + bi$ divides $n$ exactly when
$(a^2 + b^2)/\gcd(a, b)$ does. The real axis contributes $\sum \sigma(n)$ directly. Every coprime
lattice pair $(a, b)$ contributes $a$ times that same summatory function evaluated at
$\lfloor N/(a^2 + b^2) \rfloor$. A [Möbius](/topics/domain/mobius-function) sum removes the
coprimality condition, and the lattice pairs are grouped by quotient, which needs a prefix sum of
$a$ over the quarter-disc (a [lattice-point](/topics/technique/lattice-point) sweep). That leaves
nested blocking loops that call $\sum \sigma$ again and again. The calls are cheap only because
their arguments are all quotients of $N$, so the memo hits. Here the summatory function is not the
answer. It is a building block that the answer needs at many arguments.

**Problem 452** is where the swap stops paying. It counts $n$-tuples of positive integers with
product at most $m$, for $m = n = 10^9$. Grouping the tuples by their product $k$ gives
$\sum_{k \le m} d_n(k)$, the summatory function of the
[$n$-fold divisor function](https://en.wikipedia.org/wiki/Divisor_function#Generalizations)
($d_2 = d$). The swap still holds, since $d_n = d_{n-1} * 1$ gives
$D_n(x) = \sum_{d \le x} D_{n-1}(\lfloor x/d \rfloor)$, but applying it means nesting it
$n - 1$ deep, and $n$ is a billion. So the solution uses a different fact: $d_n$ is
[multiplicative](/topics/domain/multiplicative-function), with
$d_n(p^e) = \binom{n+e-1}{e}$ by [stars and bars](/topics/technique/stars-and-bars-combinatorics).
On primes it is the constant $n$, so the primes up to $x$ contribute $n \cdot \pi(x)$, and the
[Min_25 sieve](/topics/technique/min-25-sieve) builds the rest from
[prime counts](/topics/domain/prime-counting-function) at the $O(\sqrt m)$ quotients of $m$. It
recurses over smallest prime factors and costs about $O(m^{3/4}/\log m)$. The quotient set from
the bullets above is still the skeleton. What sits on it is now $\pi$, not $D$.

Several of the unsolved problems tagged here have the same shape with harder ingredients. Products
or gcds over divisors and summatory sums of other multiplicative functions all start with the same
swap. They differ in what $f$ is and whether its prefix sum has a closed form or, as in 452, needs
its own sub-linear recursion (see
[summing multiplicative functions](/topics/number-theory/summing-multiplicative-functions)).

## How to reason about it

- **Spot it under disguise.** If a total over $n \le N$ contains "for each divisor of $n$", swap
  the order before anything else. The new inner sum $\lfloor N/d \rfloor$ is almost always simpler
  than the old one.
- **Let the size of $A$ pick the method.** All integers means blocking or the hyperbola split at
  $O(\sqrt N)$. A sparse, structured set (squares, cubes, $k$-full numbers) means enumerating it,
  ideally through a unique factorisation so nothing is counted twice. A set that is neither (primes,
  squarefree numbers) needs its own counting function evaluated at every quotient.
- **When the divisor sum nests, go multiplicative.** A $k$-fold convolution like $d_n$ makes the
  swap recurse $k$ levels deep. If the summand is multiplicative with a simple value on primes,
  sum it from its prime values instead (Min_25 or Lucy), and $k$ drops out of the cost.
- **Know the growth.** $D(x) = x \ln x + (2\gamma - 1)x + O(\sqrt x)$ (the error term is the
  [Dirichlet divisor problem](https://en.wikipedia.org/wiki/Dirichlet_divisor_problem)), and
  $\sum_{n \le x} \sigma(n) \approx \tfrac{\pi^2}{12} x^2$. These give an instant sanity check on a
  result, and the second shows that $\sum \sigma$ at $x = 10^{10}$ already exceeds $2^{63}$. Decide
  between 128-bit integers and a modulus before you write the loop.
- **Memoise on the argument, not the call site.** When $D$ is nested inside another quotient sum,
  the same $\lfloor N/m \rfloor$ arrives from many places. A dictionary (or, in C, a small
  open-addressing table) turns a quadratic-looking nest into roughly $O(N^{3/4})$.
- **Check against brute force.** An $O(x \log x)$ divisor sieve up to $10^4$ takes milliseconds and
  catches the usual errors: an off-by-one in a block boundary, a missing overlap term, a set $A$
  that double-counts.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0452](/solutions/0452/) — Long Products
- ○ [0530](/solutions/0530/) — GCD of Divisors
- ○ [0608](/solutions/0608/) — Divisor Sums
- ○ [0625](/solutions/0625/) — Gcd Sum
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0694](/solutions/0694/) — Cube-full Divisors

<!-- /problems -->
