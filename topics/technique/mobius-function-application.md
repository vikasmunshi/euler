<!-- tags: [mobius-function-application] -->
<!-- status: final -->
# Möbius function (application)

The [Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function) $\mu(n)$ is $0$ when
$n$ has a repeated prime factor, and $(-1)^k$ when $n$ is a product of $k$ distinct primes. In
these solutions it does three jobs. It is a squarefree indicator ($\mu(n) \ne 0$). It supplies the
sign pattern of inclusion–exclusion over prime factors. And its prefix sums form the Mertens
function. The theory of why $\mu$ undoes divisor sums belongs to the
[Möbius inversion formula](/topics/technique/mobius-inversion-formula) page. This page covers the
practical part: getting a table of $\mu$ quickly, sized correctly, and in a form the rest of the
solution can use.

## The idea: two sieves, and one shortcut

$\mu$ is [multiplicative](/topics/domain/multiplicative-function), and its value at a prime power
is simple ($-1$ at $p$, $0$ at $p^2$ and above), so a sieve can fill a whole table in one pass. The
solutions use two sieves.

**The Eratosthenes-style sieve.** Start every entry at $+1$. For each prime $p$, flip the sign of
every multiple of $p$, then zero every multiple of $p^2$:

```python
mu = np.ones(n + 1, dtype=np.int8); mu[0] = 0
for p in primes_up_to(n):          # every prime up to n, not just up to sqrt(n)
    mu[p::p] *= -1                 # one sign flip per distinct prime factor
    mu[p * p::p * p] = 0           # a square factor kills the entry for good
```

After the loop, a squarefree $n$ has been flipped once per prime factor, which gives $(-1)^k$, and
every other $n$ has been zeroed. Later flips of a zero entry leave it at zero. The cost is
$O(n \log\log n)$, the same as the [sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes).
Problems 193 and 464 take their primes from [primesieve](/topics/technique/primesieve), and 478
sieves them itself and fills Euler's $\varphi$ in the same loop. The prime loop must run all the way
to $n$: a prime above $\sqrt n$ never zeroes anything, but it still flips signs.

**The linear sieve.** The [linear sieve](/topics/technique/linear-sieve) reaches each composite
exactly once, as $i \cdot p$ with $p$ its smallest prime factor. That gives the recurrence
directly: $\mu(i p) = 0$ if $p \mid i$ (and the inner loop stops there), otherwise
$\mu(ip) = -\mu(i)$. Problem 153 uses it, and so does the small-$n$ oracle of 478. It runs in
$O(n)$ and produces the primes as a by-product.

**The shortcut: no table at all.** When only one $n$ matters, its squarefree divisors and their
$\mu$ values come straight from its distinct prime factors. Each subset of the $k$ primes is a
divisor $d$ with $\mu(d) = (-1)^{|\text{subset}|}$. Problem 202 reduces a reflection path to
counting the $P$ in $[1, S)$ that are coprime to a single $S$ and lie in one residue class
mod 3. It factors $S$ by trial division, walks the
$2^k$ bitmasks, and lets the popcount parity be the sign. This is
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) with $\mu$ written out by
hand. It costs $O(\sqrt S)$ for the factorisation and $2^k$ terms after that, which is tiny.

## The direct uses

Once the table exists, the solutions read it in four ways.

- **As a coprimality filter.** $[\gcd(a, b) = 1] = \sum_{d \mid \gcd(a,b)} \mu(d)$ turns "count
  the $k$ in $[lo, hi]$ coprime to $g$" into $\sum_{d \mid g} \mu(d)\,
  (\lfloor hi/d \rfloor - \lfloor (lo-1)/d \rfloor)$. That is exactly the inner loop of 478's
  brute-force oracle, which skips the $d$ with $\mu(d) = 0$. Problems 153 and 478's fast solution
  use the same identity at scale, as described on the inversion page.
- **As a squarefree indicator.** In 193, $\mu(d)\lfloor x/d^2 \rfloor$ counts squarefree numbers,
  so $\mu$ is needed only up to $\sqrt x$. In 464, $Q(n) = \#\{k \le n : \mu(k) \ne 0\}$ is a
  prefix count of the same table (see [square-free integers](/topics/domain/square-free-integer)).
- **As a running sum.** The Mertens function $M(n) = \sum_{k \le n} \mu(k)$ is a single cumulative
  sum of the table. Problem 464 is about $\mu$ itself. It counts intervals $[a, b]$ where the
  $+1$ and $-1$ values of $\mu$ are nearly balanced, and both counts are differences of prefix sums,
  $P - N = M(b) - M(a-1)$ and $P + N = Q(b) - Q(a-1)$. The inequality then becomes a 2-D dominance
  count, swept with a [Fenwick tree](/topics/technique/fenwick-tree). The tree is indexed by $M$,
  whose range is only a few thousand across the whole sieve, and not by $n$. In 478, Mertens
  differences $M(d_{hi}) - M(d-1)$ weight whole blocks of equal $\lfloor n/d \rfloor$ at once. Past
  what you can sieve, the [Mertens recursion](/topics/technique/mertens-function-application) takes
  over.
- **As a sign selector.** $Q$ counts where $\mu = \pm 1$ and $M$ is the difference between the two
  signs, so $(Q + M)/2$ counts the squarefree numbers with an *even* number of prime factors
  ($\mu = +1$), and $(Q - M)/2$ the odd ones. Problem 641 needs exactly that class. A die ends on 1
  when its divisor count is $\equiv 1 \pmod 6$, which forces a square $m^2$ whose exponents
  avoid $1 \bmod 3$ and include an even number of $2 \bmod 3$. Those $m$ factor uniquely as
  $c^3 q^2$ with $\mu(q) = +1$, so the answer is a count of pairs $(c, q)$. For small $q$ the
  solution reads $\mu(q) = 1$ off the table and adds $\lfloor \sqrt[3]{X/q^2} \rfloor$. For large
  $q$, only a few $c$ remain, and each needs a count of $\mu = +1$ values up to a bound far past
  the table. There it evaluates $Q$ by the 193 formula and $M$ by the Mertens recursion, both fed
  by the same small table. Neither of these functions alone gives the sign class, but their
  average does.

Problem 745 adds one more variation: sieve the convolution, not $\mu$. The sum of the largest
square divisor rearranges into $\sum_m h(m) \lfloor N/m^2 \rfloor$, where
$h = \mu * \mathrm{id}^2$ is a [Dirichlet convolution](/topics/domain/dirichlet-convolution). It
is multiplicative, with $h(p^a) = p^{2a} - p^{2a-2}$. The linear sieve fills $h$ directly from those
prime-power values, reduced modulo the problem's modulus, and $\mu$ never needs its own array. When
$\mu$ appears only inside a fixed convolution, sieving the product saves both a pass and a table.

## How to reason about it

**Size the sieve to the scaling.** The range of $\mu$ you need follows from how $d$ enters the sum.
With $\lfloor x/d \rfloor$ you need it up to $x$ (464, 478). With $\lfloor x/d^2 \rfloor$ you need
it only up to $\sqrt x$ (153, 193, and 745's $h$). Sieving to $x$ when $\sqrt x$ would do is the
most common waste, and for 193 it is the difference between $2^{25}$ entries and $2^{50}$. When
the sum splits into a sieved part and a recursive part, the bound becomes a tuning knob instead:
641 sieves to about $4\sqrt[3]{X}$, which is large enough that only a handful of $c$ fall into the
large-$q$ part and the Mertens recursion bottoms out in the table quickly.

**Pick the sieve for the language.** In C the two sieves are equally easy to write. In Python the
choice matters more. The linear sieve is $O(n)$, but every step runs in the interpreter. The
Eratosthenes-style sieve does more work in total, but each prime's pass is a single NumPy
[slice assignment](/topics/technique/numpy-slice-assignment) executed in C. So 193, 464 and 478's
fast solution use the NumPy form for tables of $10^7$ entries or more, and the pure-Python linear
sieve is kept for 153's table of about $10^4$ and for 478's small oracle.

**Mind the widths.** $\mu$ fits in a byte, and that is how 193, 464, 478 and 641 store it: NumPy
`int8` in Python and `signed char` in C, an eighth of the memory of `int64`. The prefix sums do not
fit in a byte. Python's 464 casts with `mu.astype(np.int64)` before `np.cumsum`, because otherwise
the cumulative sum accumulates in the narrow type. C's 464 accumulates $M$ and $Q$ into
`long long` in the same loop that reads the `signed char` table, then frees the table. 153 keeps
$\mu$ as `int` in C because the table has only $\sqrt N$ entries.

**Skip the zeros.** About $1 - 6/\pi^2 \approx 39\%$ of the integers have $\mu = 0$. Every
$\mu$-weighted loop here (153, 193, 478's oracle) tests `if mu[d]` first, and in 153 that skips an
entire nested quotient-blocked evaluation each time.

## Python and C

| Problem | Python | C |
|---|---|---|
| 153 | linear sieve over plain lists | the same linear sieve, `int` table, `calloc`'d composite flags |
| 193 | NumPy `int8` sieve, then the weighted sum vectorised in chunks of $2^{22}$ | `signed char` sieve over `primesieve_generate_primes`, scalar sum that skips $\mu = 0$ |
| 202 | bitmask subsets of the distinct primes, sign by flipping; `pow(d, -1, 3)` for the residue | same subsets over a fixed `primes[16]`; an explicit guard where C's truncating division would miscount the residue class |
| 464 | NumPy sieve, `cumsum` for $M$ and $Q$ | `signed char` sieve, one loop builds both prefix arrays, then frees $\mu$ |
| 478 | NumPy sieve fills $\mu$ and $\varphi$ together | the same combined sieve over a `char` primality table |
| 641 | NumPy sieve that finds its own primes; `cumsum` of `mu == 1` and of $\mu$ for $S$ and $M$ | `signed char` $\mu$, `long long` $M$, a fixed-size memo for the recursion, 128-bit input |
| 745 | linear sieve of $h = \mu * \mathrm{id}^2$ mod $m$ | same, `long long` tables |

The algorithms match one-for-one. Python's speed comes from NumPy's strided slices and
`cumsum`. C's care goes into storage: byte-wide $\mu$, 64-bit prefix sums, and freeing the large
table as soon as its prefix sums are built.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0745](/solutions/0745/) — Sum of Squares II

<!-- /problems -->
