<!-- tags: [divisor-sum-sieve] -->
<!-- status: final 2026-10-17T07:08Z -->
# Divisor-sum sieve

A divisor-sum sieve fills a whole table $f[1..N]$ at once, where each $f(n)$ is a sum over the
divisors of $n$. The trick is to stop asking "what divides $n$?" and instead let every $d$ push a
contribution onto each of its multiples. The [divisor function](/topics/domain/divisor-function)
page explains the arithmetic ($d(n)$, $\sigma(n)$, $\sigma_k(n)$, and what to do when you only need
their sum) and shows the basic loop. This page is about the loop itself: what you can put in it,
where to start and stop it, how big its table can get, and why the same loop costs very different
amounts in C and in Python. Six solved problems use it, and each one bends it a different way.

## The idea: one loop, many weights

Every pair $(d, m)$ with $d \cdot m \le N$ is one divisor relation, "$d$ divides $dm$". A
divisor-sum sieve visits each such pair once and adds a weight to the product:

```python
for d in range(1, N + 1):
    for n in range(d, N + 1, d):     # n = d·m, m = 1, 2, …
        f[n] += w(d, n // d)
```

The number of pairs is $\sum_{d \le N} N/d \approx N \ln N$, a
[harmonic sum](/topics/domain/harmonic-series), so the sieve costs $O(N \log N)$ additions with
no division and no factorisation. The weight decides what comes out:

| weight $w(d, m)$ | table holds | problem |
|---|---|---|
| $d$, skipping $m = 1$ | $s(n) = \sigma(n) - n$, proper-divisor sum | 95 |
| $1$ | $d(n)$, divisor count | 179, 420 |
| $d^2$ | $\sigma_2(n)$ | 211 |
| $[\,(d, m)\text{ satisfies a condition}\,]$ | the number of "good" factorisations of $n$ | 256 |

The last row is the general form, and it is worth noticing. Problem 256 counts rooms
$a \times b$ of area $s$ that cannot be tiled with tatami mats. A room is a factor pair of $s$, so
$T(s)$ is a divisor count restricted to the pairs that pass a test. The notes show the test only
holds when $b$ falls in a band $k(a+1)+2 \le b \le (k+1)(a-1)-2$. So for each width $a$ the sieve
skips the multiples that cannot pass, and adds 1 only along the stretch of $a \cdot b$ inside each
band. Any sieve over factor pairs can filter this way. The faster you can enumerate the pairs that
pass, without testing all of them, the less work the sieve does.

## The loop bounds are where it goes wrong

The inner loop is easy to get right. Most bugs are in where the two loops start and stop.

- **Proper divisors start at $2d$.** Problem 95 needs $s(n)$, so $d$ must not count itself. The
  inner loop starts at $2d$, and the outer loop stops at $N/2$ because a larger $d$ has no proper
  multiple in range. Problem 211 needs the full $\sigma_2$, but it uses the same bounds: it seeds
  each entry with $n^2$ (the "$d = n$" term) in one vectorised pass, then runs the sieve only over
  proper divisors. The result is the same, and the outer loop is half as long.
- **Pairing starts at $d^2$.** Problem 179 counts each divisor pair $\{a, n/a\}$ from its
  smaller member. For each $a \le \sqrt N$ the stride begins at $a^2$ and adds 2 at every
  multiple. Then it takes 1 back at $a^2$ itself, where the two members are the same number. The
  total work is about the same, but the outer loop now runs $\sqrt N$ times, not $N$ times. As the
  next section shows, that matters a great deal in Python. The C side computes `a * a` as
  `long long` and gets $\lfloor\sqrt N\rfloor$ by exact integer stepping, not with `sqrt()`.
- **Size the table to its largest lookup, not to $N$.** In problem 420 the sieve is a helper, not
  the main step. Each candidate matrix family contributes $d(W \cdot V)$ for some product, and the
  parametrisation bounds every such product by $g^2/4 \le N/20$. So both solutions sieve $d$ only up
  to $N/10$ plus some padding, one tenth of the table the obvious bound would give. Work out the
  largest index the later code will look up. It is often well below the problem's $N$.

## When the table does not fit: sieve in windows

Problem 256 has a different difficulty: the search bound is not known in advance. It asks for
the smallest $s$ with a given $T(s)$, so no $N$ is given. Its solutions borrow the
[segmented sieve](/topics/technique/segmented-sieve) idea. They sieve $[lo, lo + 2^{24})$, scan
that window for the target, and move on to the next window only if there is no hit. Inside a
window, each width $a$ starts at the first multiple of $a$ that is $\ge lo$, so no pair is counted
twice across windows. The counts are small, so the table is `uint16`: 32 MiB per window in both
languages, however far the search goes. The cost is a little bookkeeping for the start offsets. In
return, the search no longer needs an upper bound.

Problem 211 shows why this matters. Sieving $\sigma_2$ below $6.4 \times 10^7$ in one go takes a
512 MB `int64` table. The NumPy version also holds an index array and a root array next to it.
That is about as large as a single unwindowed table should get.

## When you need the divisors, not their sum

The additive sieve gives you a number for each $n$, not the divisors themselves. Problem 834
needs the actual divisors $q > n$ of $n(n-1)/2$, and it needs them for every $n$. So it uses a
different sieve, the multiplicative kind. A smallest-prime-factor table (built Eratosthenes-style,
starting each prime's stride at $p^2$) factors any $n \le N$ in $O(\log n)$. Since $n$ and $n-1$
are coprime, their factorisations combine by simple concatenation. And $n$'s factorisation is
carried forward to serve as the next iteration's "$n-1$", so each number is factored only once.
The divisors are then generated from the exponent vector. This is the sieve to use whenever the
per-$n$ question depends on *which* divisors $n$ has, not just how many there are or what they add
up to. It is the same structure the [linear sieve](/topics/technique/linear-sieve) exploits to
compute multiplicative functions in $O(N)$.

## C and Python

In C the textbook double loop is already fast. The two languages differ in how the Python side
avoids paying the interpreter for each of the $N \ln N$ additions.

- **Pure Python is fine at $10^6$.** Problem 95's Python solution is the literal double loop
  over a list. At a million entries the $\sim 1.4 \times 10^7$ interpreted additions are tolerable,
  and the cycle walk that follows needs Python-level logic anyway.
- **NumPy turns the inner loop into one statement.** In problems 179, 211, 256 and 420 the inner
  loop becomes a strided [slice assignment](/topics/technique/numpy-slice-assignment),
  `f[start::d] += w`, which runs in compiled code. A basic slice never repeats an index, so the
  compound `+=` is correct here. With repeated indices that would not be true, and it is why
  [fancy indexing](/topics/technique/fancy-indexing) needs `np.add.at`. What is left in the
  interpreter is the *outer* loop, one Python iteration per slice. So the outer loop's length is
  the cost to cut. The $\sqrt N$ pairing of 179 matters far more in Python than in C. In 211 the
  outer loop still runs $N/2$ times, but late slices are short, so it is the early, long slices
  that do most of the work.
- **The post-pass vectorises too.** After sieving, 179 compares `d[2:N] == d[3:N+1]` as two
  offset views and counts the matches. 256 finds its hit with
  [`np.flatnonzero`](/topics/technique/np-flatnonzero) on the window. 211 tests which $\sigma_2(n)$
  are perfect squares: it takes a float square root of the whole array and checks `root - 1`,
  `root` and `root + 1`. A double has 53 bits, so near $10^{16}$ the root can be off by one, and
  this fix-up catches it (see [integer square root](/topics/technique/integer-square-root)). The C
  side does the same check per element with `sqrtl`.
- **Types are explicit on both sides.** $\sigma_2(n) < \zeta(2)\,n^2$ reaches about $7 \times 10^{15}$
  in 211, so the C table is `long long` and the NumPy one is `np.int64`. In C, `d * d` is
  computed in `long long` before it is added. Divisor counts fit easily in `int`/`int32`, or in
  `uint16` for 256's tatami counts. Python's `int` never overflows, but a NumPy array does, silently,
  so the dtype is a decision you have to make, not a default you inherit.
- **Lookups after the sieve.** Problem 420 reads its $d$ table at scattered indices. C does it in
  a scalar loop. Python reads the table one element at a time when the range is short, and with a
  single fancy-indexed `tau[idx].sum()` once the range is long enough to repay building the index
  array.

## How to reason about it

- **Reach for it when you need a value for every $n \le N$** and the value is a sum of a weight
  over the divisors, or over factor pairs that pass a test. If you only need one $n$, use trial
  division. If you only need $\sum_{n\le N} f(n)$, swap the order of summation (see the divisor
  function page). That avoids building the table at all.
- **Prefer the linear sieve for multiplicative functions at large $N$.** It runs in $O(N)$ and
  works prime power by prime power. The additive sieve's advantage is that the weight can be
  anything, multiplicative or not, including a predicate on the pair.
- **Write down the four numbers before coding:** where the outer loop stops, where the inner
  loop starts, the largest index the table must hold, and the largest value an entry can reach.
  Each of the problems here fixes at least one of them on purpose.
- **Keep the sieve inside `solve()`**, sized to the input, so the benchmark measures it on every
  run (the house rule for every precomputed table in these solutions).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0834](/solutions/0834/) — Add and Divide

<!-- /problems -->
