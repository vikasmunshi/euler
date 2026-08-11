<!-- tags: [prefix-sum] -->
<!-- status: final -->
# Prefix sum

A [prefix sum](https://en.wikipedia.org/wiki/Prefix_sum) is the running total of a sequence:
$P_0 = 0$ and $P_k = a_0 + a_1 + \dots + a_{k-1}$. Build it once in $O(n)$ and every contiguous
range sum collapses to one subtraction, $\sum_{i \le t < j} a_t = P_j - P_i$. That identity is the
whole technique. What earns it a tag across problems that share nothing else is that the same array
answers four quite different questions, and knowing which one you are asking is what tells you
whether to build it at all.

## Four jobs

**Range sums in constant time.** The textbook use, and the one to recognise first: a sum over a
contiguous window, asked many times over values that never change. Problem 50 searches for the
prime under a million that is the sum of the longest run of consecutive primes; the run sum is a
range sum, so the whole inner loop is a subtraction and a set lookup:

```python
prime_sums: list[int] = [0] + list(itertools.accumulate(primes_tuple))
...
possible_prime = prime_sums[i] - prime_sums[j]
```

That turns a nominally cubic search into a quadratic one, and the two monotonicity prunes then keep
it near-linear. Problem 150 takes the same idea into two dimensions: row prefix sums make each
horizontal segment of a triangle row one subtraction, and because a downward-pointing sub-triangle
is a stack of such segments, a second cumulative sum along the height yields every sub-triangle
rooted at a given row in one [vectorised](/topics/technique/vectorized) pass.

Problem 82 is the instructive counter-example. A vertical detour's cost there *is* a range sum, but
the code computes it with a plain `sum(...)` inside the comprehension:

```python
sum((matrix[cell][col - 1] for cell in range(min(row, target), max(row, target) + 1)))
```

The grid is $80 \times 80$, so the extra factor never shows in the benchmark and a prefix array
would be more code for no measured gain. Recognising when the technique is not worth its build cost
is part of knowing it.

**The cumulative array as an index.** When the values are non-negative the prefix array is sorted,
and a sorted array is something you can search — so a cumulative sum turns "which block does
position $n$ land in?" into a walk or a [binary search](/topics/technique/bisect). Problem 40 locates
the $n$-th digit of Champernowne's constant by accumulating the lengths of the $d$-digit bands until
it passes $n$, then recovering the number and the digit within it by one floor-division and one
modulo — $O(\log n)$, with the string never built. Problem 565 stores a prefix sum of a weight over
the primes and evaluates its summatory function at arbitrary $x$ by binary-searching the prime
array: a prefix sum plus `bisect` is a piecewise-constant function evaluated in $O(\log n)$.

Problem 205 shows the probabilistic form. Each player's dice total is
[convolved](/topics/technique/convolution) into an exact integer count distribution, and a prefix
sum over one distribution is its cumulative distribution function — so "how often does Peter beat
Colin?" becomes one lookup per outcome instead of enumerating the $4^9 \times 6^6$ joint space.

**When the prefix sum *is* the answer.** For a [multiplicative
function](/topics/domain/multiplicative-function) $f$, the object of interest is almost always the
summatory function $\sum_{k \le n} f(k)$; a sieve gives you $f$ pointwise, and the cumulative sum is
the bridge. The [Mertens function](/topics/technique/mertens-function-application) is literally the
cumulative sum of the [Möbius function](/topics/technique/mobius-function-application) — problems
319, 464 and 478 all reach for `np.cumsum(mu)` — and problem 72's answer is the running sum of
Euler's totient, accumulated as the sieve finalises each cell so the array is never stored twice:

```python
for n in range(2, max_d + 1):
    if euler_totients[n] == n:
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
    result += euler_totients[n]
```

Once that table exists, the standard number-theoretic machinery applies on top of it: problem 233
reads a sieved prefix table at $\lfloor \text{limit}/c \rfloor$ for each core, and problems 319 and
464 group the $O(\sqrt n)$ distinct values of $\lfloor n/d \rfloor$ into *differences* of the
cumulative table — see [quotient blocking](/topics/technique/quotient-blocking).

**A second scan over the prefix array.** The prefix array is itself a sequence, and the deeper uses
scan it again. Maximum subarray is the canonical one:
$\max_j \left( P_{j+1} - \min_{i \le j} P_i \right)$ — a
[running minimum](/topics/technique/prefix-maximum-scan) over the prefixes, which is
[Kadane's algorithm](/topics/technique/maximum-subarray-problem) rewritten so that it vectorises to
a `cumsum` and a `minimum.accumulate` with no Python loop at all. Problem 149 runs exactly that over
every row, column, diagonal and anti-diagonal of a large generated grid.

Problem 103 keeps prefix **and** suffix sums of a sorted candidate set, so the special-sum-set
conditions reduce to comparing a $k$-element prefix against a $k$-element suffix — the cheapest
available necessary condition, checked before any subset enumeration ([cheap checks
first](/topics/takeaway/cheap-checks-first)). Problem 331 accumulates row-width *parities* rather
than values, giving a sliding window over parity counts. And problem 238 is the prettiest inversion
of all: a substring of a periodic digit stream starting after position $t$ sums to $k$ exactly when
$P_t + k$ is itself a prefix sum, so the question becomes membership in the *set* of prefix sums —
held as one machine-word [bitset](/topics/technique/bit-array) and tested by a rotation. The prefix
sums stop being an intermediate and become the data structure.

## How to reason about it

- **Store the leading zero and use half-open ranges.** $P$ has $n+1$ entries and
  $\sum a[i{:}j] = P_j - P_i$, which is why problem 50 writes `[0] + list(itertools.accumulate(...))`
  rather than [`accumulate`](/topics/technique/itertools-accumulate) alone. The $n$-entry variant
  needs a special case for $i = 0$, and that is where the off-by-one lives.
- **It needs an *invertible* operation.** Sum, xor, count, product in a field: all fine, because the
  query is a subtraction. Min and max are not — no prefix bookkeeping recovers $\min a[i{:}j]$. That
  is precisely why maximum subarray is solved by a running minimum *over the prefixes* rather than by
  a range-minimum query, and why real range minima need a sparse table or a monotone deque.
- **Only for a static array.** Any update to the underlying values invalidates every prefix past it.
  When the array changes between queries the right structure is a
  [Fenwick tree](/topics/technique/fenwick-tree) — the same prefix query, $O(\log n)$ for reads *and*
  writes. Problem 464 sweeps points in key order and inserts into one as it goes, so each query
  counts only the points already inserted: a prefix sum you are allowed to write to.
- **Watch the accumulator's width.** A `np.cumsum` in `int64` overflows silently and the result looks
  like data ([watch integer width](/topics/takeaway/watch-integer-width)). Problem 565 bounds its
  chunk width so no chunk's `int64` cumulative sum can overflow and carries the running total as a
  Python `int`; problem 710 reduces every count mod $m$ as it extends the arrays. Under a modulus,
  remember that the query is a subtraction and needs reducing back into range. In floating point,
  differencing two large nearly-equal prefix sums is
  [catastrophic cancellation](/topics/technique/catastrophic-cancellation) — the technique loses
  precision without complaining.
- **Budget the build.** $O(n)$ time and $O(n)$ memory up front to make each query $O(1)$: clearly
  worth it once the query count approaches $n$, clearly not for a handful. Build it inside `solve()`,
  sized to the input, so the cost lands in the benchmark where it belongs
  ([size work to the input](/topics/takeaway/size-work-to-the-input)).
- **Extra dimensions cost inclusion–exclusion.** A 2-D prefix sum answers a rectangle with four
  corner reads. Non-rectangular regions are better handled one dimension at a time — prefix along
  the rows, then cumulate along the second axis, as problem 150 does — because the region's shape
  usually *is* the recurrence.
- **It is one of the few techniques that costs nothing in C.** A prefix sum is an array and a loop,
  so the C sibling is the same algorithm with the same complexity and no scaffolding — the opposite
  of what happens when a Python solution leans on a [set](/topics/technique/set) or a
  [dict](/topics/technique/dict). When you have a choice of how to make a hot loop cheap, prefer the
  one that survives translation.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0022](/solutions/0022/) — Names Scores
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0205](/solutions/0205/) — Dice Game
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0710](/solutions/0710/) — One Million Members

<!-- /problems -->
