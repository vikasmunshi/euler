<!-- tags: [quotient-blocking, mobius-inversion-formula, mobius-function-application, dirichlet-convolution, divisor-summatory-function, totient-summatory-recursion] -->
<!-- status: final 2026-11-04T13:23Z -->
# Summing multiplicative functions fast

A whole family of Project Euler problems asks for $\sum_{n \le N} f(n)$, where $f$ is a
[multiplicative function](/blogs/domain/multiplicative-function) and $N$ is $10^{11}$, $10^{15}$ or
$10^{18}$. Examples are the sum of divisors, the totient, the largest square divisor, $\gcd(k, k')$,
and the squarefree indicator. At that size you cannot touch every $n$, and you cannot even sieve
$f$ up to $N$. Four techniques keep turning up in the solutions below:
[quotient blocking](/blogs/technique/quotient-blocking),
[Möbius inversion](/blogs/technique/mobius-inversion-formula), the
[Dirichlet hyperbola method](/blogs/technique/dirichlet-hyperbola-method) and the
[totient summatory recursion](/blogs/technique/totient-summatory-recursion). They look like four
separate tricks, but they are one idea. You factor $f$ as a
[Dirichlet convolution](/blogs/domain/dirichlet-convolution) of two pieces that are each easy to
sum, then you choose how to walk the hyperbola $ab \le N$. This page explains that idea once, shows
where each of the four techniques fits, and then covers the problems that use the same machinery
without a sublinear payoff or without a convolution at all.

## The one identity

Write $F(x) = \sum_{n \le x} f(n)$ for the summatory function. Suppose $f = g * h$, meaning
$f(n) = \sum_{ab = n} g(a)\,h(b)$. Then summing $f$ up to $x$ is the same as summing $g(a)h(b)$ over
the lattice points under the hyperbola $ab \le x$. Fix $a$ and sum over $b$ to get

$$F(x) = \sum_{a \le x} g(a)\, H\!\left(\left\lfloor \tfrac{x}{a} \right\rfloor\right).$$

Everything on this page comes from that one line. The simplest case is $h = \mathbf 1$, the
constant function, whose summatory is $H(y) = y$. This gives the "swap the order of summation" move
behind the [divisor summatory function](/blogs/domain/divisor-summatory-function):
$\sum_{n \le x} \sigma(n) = \sum_{d \le x} d \lfloor x/d \rfloor$. Problem 694 uses the same move
with $g$ equal to the indicator of cube-full numbers: the number of cube-full divisors, summed to
$x$, is $\sum_{d \text{ cube-full}} \lfloor x/d \rfloor$. Convolutions also stack. Problem 452
counts ordered $n$-tuples with product at most $m$, which is the summatory function of the $n$-fold
divisor function $d_n = \mathbf 1 * \cdots * \mathbf 1$. Grouping the tuples by their product is
the same swap, applied $n - 1$ times.

The identity turns the problem into two questions:

1. **Which factorisation?** Pick $g$ and $h$ so that one of them is sparse or simple and the other
   has a summatory function you can evaluate quickly.
2. **Which walk?** Decide how to evaluate the sum over the hyperbola. Each of the four techniques is
   an answer to this second question, chosen according to what is cheap.

## Four ways to walk the hyperbola

**Quotient blocking: when $H$ has a closed form.** As $a$ runs over $1..x$, the quotient
$\lfloor x/a \rfloor$ takes only about $2\sqrt x$ distinct values, and each value occurs on a
contiguous run of $a$. So group the terms by run, and each run costs one evaluation of $H$ and one
difference of $G$ (the summatory function of $g$). This takes $O(\sqrt x)$ time, provided both
summatory functions are $O(1)$, as triangular numbers and power sums are. The divisor summatory
$\sum_k k \lfloor x/k \rfloor$ is the standard example. The sum of squares of divisors (Problem 401)
is the same with $k^2$ as the weight, although its solution walks the hyperbola differently (see
below). The
[technique page](/blogs/technique/quotient-blocking) covers the loop itself.

**Möbius inversion: when you know $f * \mathbf 1$ and want $f$.** Many problems hand you a count
that is easy *without* a coprimality or primitivity condition and hard *with* it. If $S$ counts all
objects and $P$ counts the primitive ones, scaling by the common factor gives
$S(x) = \sum_{g \ge 1} P(\lfloor x/g \rfloor)$. That is the identity above with $h = \mathbf 1$,
read backwards. The [Möbius function](/blogs/domain/mobius-function) inverts it:
$P(x) = \sum_d \mu(d)\, S(\lfloor x/d \rfloor)$. This is how Problem 276 gets primitive integer
triangles out of Alcuin's closed-form count of all triangles. It is how 0153 removes the
condition $\gcd(a, b) = 1$ from its sum over Gaussian divisors. And it is how 0319 and 0478 end up
with a sum $\sum_d \mu(d)\, g(\lfloor n/d \rfloor)$, which is quotient-blocked against the
[Mertens function](/blogs/technique/mertens-function-application). Problem 73 is public, so its
code can be shown. It does the same inversion *eagerly*, as a sieve. `data[i]` starts as the count
of all fractions $\le n/d$ with denominator $i$, and subtracting each entry from its multiples
leaves the reduced ones:

```python
data = [i * n // d for i in range(max_d + 1)]   # all fractions <= n/d, by denominator
for i in range(1, max_d + 1):
    for j in range(2 * i, max_d + 1, i):
        data[j] -= data[i]                       # remove the non-reduced ones
```

That is $O(N \log N)$. The rest of this page is about reaching the same answer in less than
linear time.

**Dirichlet hyperbola: when neither side is free, or one side is sparse.** You need not sum all of
$a$ first. Split the hyperbola at a point $(y, x/y)$ and count each half along its own short axis,
then subtract the rectangle that was counted twice:

$$F(x) = \sum_{a \le y} g(a)\, H\!\left(\tfrac{x}{a}\right) + \sum_{b \le x/y} h(b)\, G\!\left(\tfrac{x}{b}\right) - G(y)\, H\!\left(\tfrac{x}{y}\right).$$

With $y = \sqrt x$ and $g = h = \mathbf 1$ this gives the divisor-count sum
$2\sum_{k \le \sqrt x} \lfloor x/k \rfloor - \lfloor \sqrt x \rfloor^2$. That is the textbook
case. Problem 401 is the weighted version, with $g = \mathrm{id}^2$ and $h = \mathbf 1$. One pass over
$k \le \sqrt n$ adds both $k^2 \lfloor n/k \rfloor$ and the square-pyramidal closed form at
$\lfloor n/k \rfloor$, because both terms need the same quotient. Then the $s \times s$ square is
subtracted once. With no blocking bookkeeping, the loop is a plain range that vectorises cleanly in
NumPy. The more useful form for Project Euler is the *lopsided* split, where $g$ is supported on a
sparse set, so the sum over $a$ is short even though it runs all the way to $x$:

- **Square-supported $g$.** Squarefreeness is $\sum_{d^2 \mid n} \mu(d)$, so the count of squarefree
  numbers is $\sum_{d \le \sqrt M} \mu(d) \lfloor M/d^2 \rfloor$. That is Problem 193, done in
  $O(\sqrt M)$. Problem 745 has the same shape. To sum the largest square divisor, write it as
  $\sum_{m \le \sqrt N} (\mu * \mathrm{id}^2)(m)\, \lfloor N/m^2 \rfloor$, sieving the convolution
  with a [linear sieve](/blogs/technique/linear-sieve) up to $\sqrt N$. Problem 641 goes a step
  further. Its numbers factor uniquely as $c^3 q^2$, with $q$ squarefree and $\mu(q) = +1$, so the
  count is a lattice count under the curve $c^3 q^2 \le X$, split at a bound $L$. Small $q$ are
  summed one at a time. Above $L$ only a few dozen $c$ survive, and each needs the number of
  squarefree $q$ with an even number of prime factors. Because $\mu = \pm 1$ on squarefree numbers,
  that count is $\tfrac12\bigl(Q(x) + M(x)\bigr)$: the squarefree count plus the Mertens function,
  which are two of this page's summatory functions used together.
- **Powerful-supported $g$.** If $f$ agrees with a function you can sum easily on every prime,
  then $f = \mathbf 1 * h$, where $h(p) = 0$. A multiplicative function that vanishes on primes
  is nonzero only on [powerful numbers](https://en.wikipedia.org/wiki/Powerful_number), and there
  are only $O(\sqrt x)$ of those. Problem 484 does exactly this with $g(k) = \gcd(k, k')$, which is
  $1$ on squarefree $k$. Problem 694's cube-full divisors are sparser still, at $O(x^{1/3})$. This
  is the "powerful number trick", and it is the natural approach for 639.
- **Smooth-supported $g$, periodic $h$.** The split need not be by size. It can be by primes.
  Problem 967 sums a ring-valued multiplicative function that depends only on which primes up to
  $B$ divide $n$. Let $h$ be the part that sees the few smallest primes. It depends only on
  $n \bmod Q$, where $Q$ is their product, so it is
  [periodic](/blogs/domain/periodic-sequence) and
  $H(y) = \lfloor y/Q \rfloor H(Q) + H(y \bmod Q)$ is one lookup in a prefix table. That is a third
  kind of cheap summatory function, after closed forms and sieved tables. Then $g$ takes the
  remaining primes and lives on their squarefree products, which thin out fast: about
  $1.4 \times 10^6$ of them below $10^{18}$, against $7 \times 10^7$ if every prime stayed in $g$.
  The cost is $O(Q)$ plus the size of the support of $g$, and the choice of $Q$ trades one against
  the other. The [multiplicative function](/blogs/domain/multiplicative-function) page explains
  why the values may be ring elements.

**Totient summatory recursion: when you know $f * g$ but $f$ is the unknown.** Now invert the
identity *at the level of summatory functions* rather than term by term. Consider the totient.
We have $\varphi * \mathbf 1 = \mathrm{id}$, so

$$\sum_{d \le x} \Phi\!\left(\left\lfloor \tfrac{x}{d} \right\rfloor\right) = \frac{x(x+1)}{2}
\quad\Longrightarrow\quad
\Phi(x) = \frac{x(x+1)}{2} - \sum_{d=2}^{x} \Phi\!\left(\left\lfloor \tfrac{x}{d} \right\rfloor\right).$$

The Mertens function satisfies the same recursion, with $\mu * \mathbf 1 = \varepsilon$ and right-hand
side $1$. So does Problem 276's primitive count, with right-hand side $S(x)$. In general, if
$f * g$ has a summatory function you can evaluate and $G$ is cheap, then
$F(x) = \bigl[\,\Sigma_{f*g}(x) - \sum_{d \ge 2} g(d) F(\lfloor x/d \rfloor)\bigr] / g(1)$.
Competitive programmers know this as the *Du Jiao sieve*. Two facts make it sublinear. First,
the inner sum is quotient-blocked. Second, the recursion only ever asks for $F$ at values
$\lfloor x/k \rfloor$, because $\lfloor\lfloor x/a\rfloor/b\rfloor = \lfloor x/(ab)\rfloor$.
There are about $2\sqrt x$ such values, so a memo of that size holds everything:

```python
def summatory(n, S, small):          # S(v): summatory of f*1; small[v] = F(v) from a sieve
    memo = {}
    def F(v):
        if v < len(small):
            return small[v]
        if v not in memo:
            total, d = S(v), 2
            while d <= v:
                q = v // d
                d_end = v // q
                total -= (d_end - d + 1) * F(q)
                d = d_end + 1
            memo[v] = total
        return memo[v]
    return F(n)
```

Without a sieve this costs $O(x^{3/4})$. If you sieve $f$ directly up to about $x^{2/3}$ and use the
recursion only above that, the cost falls to $O(x^{2/3})$. Problem 351 counts visible hexagonal
lattice points, and after a symmetry argument it reduces to a single $\Phi(10^8)$ evaluated this way.

Problem 512 shows why the closed key set matters. It needs $\varphi$ summed over *odd* $n$ only.
Since $\varphi(2m)$ is $\varphi(m)$ or $2\varphi(m)$ depending on the parity of $m$, the even part
unrolls to $\Phi(N) - \sum_{k \ge 1} \Phi(\lfloor N/2^k \rfloor)$. Every $\lfloor N/2^k \rfloor$ is
already a key, so the restriction costs only $\log_2 N$ extra lookups. The same closure removes the
memo dictionary. Store $\Phi(\lfloor N/k \rfloor)$ in an array indexed by $k$ and fill it for
decreasing $k$. Every large value the recursion at $k$ reads lives at index $kd > k$, so it has
already been computed.

Problem 625 stacks two walks. Its gcd sum is Pillai's function $\mathrm{id} * \varphi$, so the
identity gives $\sum_{k \le N} \varphi(k)\, T(\lfloor N/k \rfloor)$ with $T$ triangular. One side has
a closed form, which calls for quotient blocking. But blocking takes differences of the other side's
summatory function, $\Phi$, at every key, and $\Phi$ has no closed form. That costs nothing extra.
The recursion for $\Phi(N)$ fills in the large keys anyway, and the sieve below it supplies the small
ones, so the outer sum is one last pass over a table that already exists. The total stays
$O(N^{2/3})$. Whenever a walk needs a summatory function at the keys and that function has a
recursion, the two compose for free.

The same problem removes the weakness of the blocking loop above, which is serial: each `d_end`
depends on the one before it, so the loop cannot become an array expression. Any cut $c$ divides the
range exactly, because $d \le \lfloor v/(c+1) \rfloor$ says the same thing as
$\lfloor v/d \rfloor > c$:

$$\sum_{d \le v} g(d)\, H\!\left(\left\lfloor \tfrac{v}{d} \right\rfloor\right)
= \sum_{d \le \lfloor v/(c+1) \rfloor} g(d)\, H\!\left(\left\lfloor \tfrac{v}{d} \right\rfloor\right)
+ \sum_{q \le c} H(q) \left( G\!\left(\left\lfloor \tfrac{v}{q} \right\rfloor\right) - G\!\left(\left\lfloor \tfrac{v}{q+1} \right\rfloor\right) \right).$$

The first sum goes through $d$ one at a time, and the second goes through the quotient values. With
$c$ near $\sqrt v$ both are about $\sqrt v$ long, and both are plain ranges, so each is a single NumPy
expression. There is no rectangle to subtract, as there is in the hyperbola formula, because the cut
partitions the terms and nothing is counted twice.

## Outside the four walks

Some problems on this list use the blocks without the sublinear payoff, or without a convolution.

**Blocks over a sieve: when $N$ is within reach.** Problem 875 has $N$ near $10^7$. Its count
factors as $q = \mathrm{id}^7 * w$, where $w(m)$ is $\varphi(m)\, m^3$ with a separate rule at the
powers of 2. The [multiplicative function](/blogs/domain/multiplicative-function) page derives that
from Gauss sums. The identity leaves $\sum_m w(m)\, S_7(\lfloor N/m \rfloor)$, with $S_7$ a
[Faulhaber](/blogs/technique/faulhabers-formula) closed form, which looks like a job for blocking.
But blocking needs the summatory function of $w$, and here that is a prefix sum over a totient sieve
up to $N$. The sieve sets the cost, and the blocks only cut the evaluations of $S_7$ from $N$ to a few
thousand. A recursion is available for the main term, since
$(\varphi\,\mathrm{id}^3) * \mathrm{id}^3 = \mathrm{id}^4$, but at this size it is more code for no
real gain. Sublinear methods answer a size problem, so
[size the work to the input](/blogs/takeaway/size-work-to-the-input) before reaching for one.

**Stream and checkpoint: when a summatory function has no shortcut.** Problem 754 is a product, and
its summand is not even multiplicative, yet Möbius inversion still yields a product over $d$ with
exponent $\mu(d)$, blocked by $\lfloor N/d \rfloor$. The same page shows that algebra. One base
changes with $d$ inside a block, so each block needs the running product of $d^{\mu(d)}$ at its two
ends. The solution has no identity to recurse on for that product, so it makes one linear pass. The
point is that the pass need not keep what it computes. A
[segmented sieve](/blogs/technique/segmented-sieve) produces $\mu$ one window at a time, the running
quantities advance through the window, and their values are stored only at the keys
$\lfloor N/k \rfloor$. Memory is one window plus $O(\sqrt N)$ checkpoints. The assembly is then the
usual walk, with one modular power per block rather than one per $d$. Keeping the $\mu = +1$ and
$\mu = -1$ products apart also means one modular inverse per block, not one per element.

**Read the sieve mid-flight: when $f$ is not multiplicative at all.** Problem 521 sums the smallest
prime factor of each $n$ up to $10^{12}$. No convolution reaches that function, but the
[Lucy sieve](/blogs/technique/lucy-hedgehog-sieve) processes numbers in exactly that order: step $p$
removes the composites whose smallest prime factor is $p$. So the table is useful during the run, not
only at the end. Let $C_p(v)$ count the survivors in $[2, v]$ just before step $p$. The composites
$pm \le n$ with smallest factor $p$ match the survivors $m \in [p, \lfloor n/p \rfloor]$, so there are
$C_p(\lfloor n/p \rfloor) - \pi(p - 1)$ of them. Every composite up to $n$ has its smallest factor
at most $\sqrt n$, so reading that one entry before each step covers them all. The primes are their own
smallest factors, and a [sum table carried alongside the count](/blogs/takeaway/carry-sums-alongside-counts)
supplies them when the sieve ends. The extra work is one read per prime, on top of the sieve's
$O(n^{3/4}/\log n)$. Any weight that depends only on the smallest prime factor works the same way.
[Min_25](/blogs/technique/min-25-sieve)'s second stage has to build numbers up by smallest prime
factor. Here the first stage's strike order already provides them, so no second stage is needed.

## How to reason about it

- **Look for the convolution first.** Write $f$ on prime powers, then look for a simple function
  that matches it on primes: $\mathbf 1$, $\mathrm{id}$, $\mathrm{id}^k$, or
  $\mu$. The quotient $h = f * g^{-1}$ is then concentrated on squares, cubes or powerful numbers,
  and that sparseness is what you exploit. If $f$ is defined by a coprimality condition, $\mu$ is
  already one of the factors. If $f$ counts solutions mod $n$, a
  [roots-of-unity filter](/blogs/technique/roots-of-unity-filter) can hand you the factorisation:
  grouping the filter's $t$ by $\gcd(t, n)$ is what produces Problem 875's $\mathrm{id}^7 * w$.
- **Choose the walk by what is cheap.** If $N$ is small enough to sieve, sieve, and block only to save
  evaluations. If both summatory functions have closed forms, block the
  sum for $O(\sqrt x)$. If one factor is sparse, use a lopsided hyperbola, with cost equal to the
  size of its support. If the unknown summatory function sits on both sides, use the recursion,
  $O(x^{2/3})$ with a sieve. If you need sums over primes at every $\lfloor x/k \rfloor$ (Problems
  501, 565, 642), use the Lucy/[Min_25](/blogs/technique/min-25-sieve) DP over the same set
  of key values. That DP is also the general fallback when $f$ has no sparse quotient but takes
  a simple value on primes. Problem 452's $d_n$ is the constant $n$ on primes, so Lucy's
  $\pi(v)$ table plus a recursion over smallest prime factors sums it in about
  $O(m^{3/4}/\log m)$. Problem 668 uses only the first half. After a complement argument its
  count is $\sum_{p > \sqrt N} \lfloor N/p \rfloor$, which regroups by quotient into differences
  $\pi(\lfloor N/k \rfloor) - \pi(\sqrt N)$, all read from the same table.
- **The key set is the shared data structure.** $V(x) = \{\lfloor x/k \rfloor\}$ is closed under
  further division. Every technique here reads and writes the same $2\sqrt x$ values, so store
  them in a small/large pair of arrays indexed by $v$ below $\sqrt x$ and by $x/v$ above it,
  rather than in a dictionary when speed matters. Nested sums (0153) and Mertens values needed at
  every key (0319) then cost nothing extra to look up.
- **Precompute small, recurse large.** The crossover around $x^{2/3}$ is the only tuning parameter.
  Below it a [linear sieve](/blogs/technique/linear-sieve) is faster than any recursion.
- **Watch the arithmetic.** Under a modulus, closed forms like $x(x+1)/2$ need a
  [modular inverse](/blogs/technique/modular-multiplicative-inverse-application) or a reduction
  done before dividing. When the modulus shares a factor with the divisor, there is no inverse.
  Problem 401 asks for $x(x+1)(2x+1)/6 \bmod 10^9$, so it divides the even factor by 2 and the
  multiple of 3 by 3 exactly, and only then reduces. A long polynomial has no such tidy factors, but
  if $c \mid X$ then $(X \bmod cm)/c \equiv X/c \pmod m$. So reduce modulo $cm$ and divide the
  residue, which is how Problem 875's C port evaluates $S_7$ with $c = 24$. Products such as
  $\lfloor x/k \rfloor \cdot G(\cdot)$ overflow 64 bits long
  before $x$ does, and intermediates can outgrow the answer: Problem 967's ring coefficients need
  128 bits even though its final count does not. Use `math.isqrt` for the split, never a float square
  root. Check "below $N$"
  against "at most $N$" too: Problem 193 needs $Q(2^{50} - 1)$, not $Q(2^{50})$.
- **Sanity-check against brute force.** For small $x$, sieve $f$ directly and compare the summatory
  values at every key. Inversion and recursion are quick to code, and a wrong $g(1)$ or a missing
  rectangle correction makes them quietly wrong. A free parameter gives a second check at full size,
  where brute force cannot go. Problem 967 gets the same answer with very different periods $Q$, and
  the sieve limit in a recursion can be moved in the same way.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0351](/solutions/0351/) — Hexagonal Orchards
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0452](/solutions/0452/) — Long Products
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0530](/solutions/0530/) — GCD of Divisors
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0608](/solutions/0608/) — Divisor Sums
- ● [0625](/solutions/0625/) — Gcd Sum
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0850](/solutions/0850/) — Fractions of Powers
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0883](/solutions/0883/) — Remarkable Triangles
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0935](/solutions/0935/) — Rolling Square
- ● [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0994](/solutions/0994/) — Counting Triangles

<!-- /problems -->
