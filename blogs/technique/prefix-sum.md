<!-- tags: [prefix-sum] -->
<!-- status: final 2026-11-02T18:28Z -->
# Prefix sum

A [prefix sum](https://en.wikipedia.org/wiki/Prefix_sum) is the running total of a sequence:
$P_0 = 0$ and $P_k = a_0 + a_1 + \dots + a_{k-1}$. Build it once in $O(n)$ and every contiguous
range sum collapses to one subtraction, $\sum_{i \le t < j} a_t = P_j - P_i$. That identity is the
whole technique. What earns it a tag across problems that share nothing else is that the same array
answers five quite different questions, and knowing which one you are asking is what tells you
whether to build it at all.

## Five jobs

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
rooted at a given row in one [vectorised](/blogs/technique/vectorized) pass.

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
position $n$ land in?" into a walk or a [binary search](/blogs/technique/bisect). Problem 40 locates
the $n$-th digit of Champernowne's constant by accumulating the lengths of the $d$-digit bands until
it passes $n$, then recovering the number and the digit within it by one floor-division and one
modulo — $O(\log n)$, with the string never built. Problem 565 stores a prefix sum of a weight over
the primes and evaluates its summatory function at arbitrary $x$ by binary-searching the prime
array: a prefix sum plus `bisect` is a piecewise-constant function evaluated in $O(\log n)$.
Problem 516 asks that function many times. Every $n$ with a 5-smooth totient factors as a
[Hamming number](https://en.wikipedia.org/wiki/Regular_number) times a squarefree product $m$ of
"good" primes, so the sum over all such $n \le L$ becomes, for each $m$, $m$ times the sum of the
Hamming numbers up to $\lfloor L/m \rfloor$. One sorted list and one prefix array serve every $m$
with a single `bisect` each. The Hamming numbers themselves are never multiplied out.

Problem 341 applies the index job to a sequence that describes itself.
[Golomb's sequence](https://oeis.org/A001462) is constant on runs, and the value $v$ fills exactly
$G(v)$ positions. So $S(v) = G(1) + \dots + G(v)$ is the last index holding $v$, and a search on
$S$ inverts the sequence. The question asks for $G(n^3)$ with $n^3$ near $10^{18}$, and one inversion
is not enough. The trick is to take a prefix sum of a prefix sum: $T(i) = \sum_{t \le i} t\,G(t)$ is
the last $n$ with $G(G(n)) = i$. Three levels of inversion bring the table down to about
$3 \times 10^4$ entries. Two details matter. First, inside one level-1 block $G$ is constant, so $T$
is a quadratic in $i$ there, and the last step of the search is a square root (with an integer
correction for float rounding) rather than a `bisect`. Second, all the queries go through a single
`np.searchsorted`. When the prefix array has a closed form between its breakpoints, store only the
breakpoints and solve the formula in between.

Problem 205 shows the probabilistic form. Each player's dice total is
[convolved](/blogs/technique/convolution) into an exact integer count distribution, and a prefix
sum over one distribution is its cumulative distribution function — so "how often does Peter beat
Colin?" becomes one lookup per outcome instead of enumerating the $4^9 \times 6^6$ joint space.

Problem 943 asks for the sum of the first $N \approx 2 \times 10^{13}$ terms of a self-describing
([Kolakoski-style](https://en.wikipedia.org/wiki/Kolakoski_sequence)) sequence, and uses the index
job with two twists. First, it keeps *parallel* prefix arrays over a run of sibling subtrees — leaf
counts and leaf sums. It finds the sibling that contains the $N$-th term by a `bisect` on the
counts, then reads the sums at that same index. One array locates, the other answers. Second, the
sibling chain is eventually periodic: after a lead-in of $\mu$ entries it repeats with period $p$.
So the arrays only ever hold one period, and the prefix at any $k$ is the stored remainder plus
whole periods:

$$P(k) = P(\mu + r) + q \bigl(P(\mu + p) - P(\mu)\bigr), \qquad k - \mu = qp + r.$$

That is a prefix sum of an unbounded sequence in $O(1)$ space per chain — the arithmetic version of
the periodic stream in problem 238.

**When the prefix sum *is* the answer.** For a [multiplicative
function](/blogs/domain/multiplicative-function) $f$, the object of interest is almost always the
summatory function $\sum_{k \le n} f(k)$; a sieve gives you $f$ pointwise, and the cumulative sum is
the bridge. The [Mertens function](/blogs/technique/mertens-function-application) is literally the
cumulative sum of the [Möbius function](/blogs/technique/mobius-function-application) — problems
319, 464 and 478 all reach for `np.cumsum(mu)` — and problem 72's answer is the running sum of
Euler's totient, accumulated as the sieve finalises each cell so the array is never stored twice:

```python
for n in range(2, max_d + 1):
    if euler_totients[n] == n:
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
    result += euler_totients[n]
```

Problem 351 needs the same totient sum, but at $n = 10^8$ instead of $10^6$. The geometry
reduces to $3n(n+1) - 6\,\Phi(n)$, so the whole problem comes down to one value of the
[totient summatory function](https://en.wikipedia.org/wiki/Totient_summatory_function). Here the
table no longer has to reach $n$. It sieves $\Phi$ with `np.cumsum` only up to about $n^{2/3}$, and
gets the larger values from the identity $\sum_{d \ge 1} \Phi(\lfloor v/d \rfloor) = v(v+1)/2$,
evaluated at each quotient $v = \lfloor n/k \rfloor$ from smallest to largest. The prefix table
stops being the answer and becomes the base case of a sublinear recursion. That is the move to
reach for once $n$ is too large to sieve.

Problem 463 takes that move all the way: no table at all. Its $f$ is defined by recurrences on
$f(2n)$, $f(4n+1)$ and $f(4n+3)$, and the target is $S(n) = \sum_{i \le n} f(i)$ at an $n$ far too
large to sieve. The insight is that a recurrence on $f$ *lifts* to a recurrence on its prefix sums.
Split the sum by $i \bmod 2$, and the odd part by $i \bmod 4$. The result is a pair of mutually
recursive prefix sums: $S$ and $O(m) = \sum_{k \le m} f(2k+1)$, each defined from both at about half
the argument. Memoised, that is $O(\log n)$ states, and $f$ itself is never evaluated beyond the base
cases. When the pointwise function is defined by halving, look for the halving recurrence its sum
obeys.

Once that table exists, the standard number-theoretic machinery applies on top of it: problem 233
reads a sieved prefix table at $\lfloor \text{limit}/c \rfloor$ for each core, and problems 319, 351
and 464 group the $O(\sqrt n)$ distinct values of $\lfloor n/d \rfloor$ into *differences* of the
cumulative table — see [quotient blocking](/blogs/technique/quotient-blocking). Problem 272, a
sibling of 233, multiplies two prefix tables together. Its last prime factor $p > \sqrt T$ can only
appear to the first power, so it groups those primes by $q = \lfloor T/p \rfloor$. Each group then
contributes (the sum of good primes in $(T/(q+1),\, T/q]$, a difference of a prime prefix sum found
by `bisect`) × (the prefix sum of admissible cofactors up to $q$). Two tables, one subtraction each,
and the primes above $\sqrt T$ are never visited one at a time.

Problem 675 runs the job on a running *product*. It needs $S(i!)$ for every $i \le n$, where $S$
is multiplicative and $S(i!) = \prod_p (2e_p(i!) + 1)$. Two cumulative scans do the work. First,
for each prime $p$, an `np.cumsum` of the valuations $v_p(kp)$ gives
[Legendre's](https://en.wikipedia.org/wiki/Legendre%27s_formula) exponent $e_p((kp)!)$ at every
multiple at once. Second, going from $(i-1)!$ to $i!$ changes only the factors for the primes
dividing $i$. Each one swaps a $(2e'+1)$ for a $(2e+1)$, so $S(i!) = S((i-1)!) \cdot \text{mult}[i]$.
The answer is the sum of that prefix product. The swap is a division, and that only works because
the modulus is prime: each removed factor is undone by multiplying by its
[Fermat inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse).

Problem 423 shows the most common prefix product: the factorial table behind every modular
binomial. It needs $\binom{n-1}{\pi(n)}$ for every $n$ up to $5 \times 10^7$, so three cumulative
arrays do all the work. $\pi(n)$ is an `np.cumsum` of the prime indicator. $n!$ is a running product.
And the inverse factorials come from a *reversed* running product, $top \cdot (top-1) \cdots$, times
one Fermat inverse of $top!$, because $1/i! = (i+1)(i+2)\cdots top \,/\, top!$. That is one modular
exponentiation for the whole table, not one per entry: the suffix product undoes the prefix product
with a single division.

**A second scan over the prefix array.** The prefix array is itself a sequence, and the deeper uses
scan it again. Maximum subarray is the canonical one:
$\max_j \left( P_{j+1} - \min_{i \le j} P_i \right)$ — a
[running minimum](/blogs/technique/prefix-maximum-scan) over the prefixes, which is
[Kadane's algorithm](/blogs/technique/maximum-subarray-problem) rewritten so that it vectorises to
a `cumsum` and a `minimum.accumulate` with no Python loop at all. Problem 149 runs exactly that over
every row, column, diagonal and anti-diagonal of a large generated grid.

Problem 103 keeps prefix **and** suffix sums of a sorted candidate set, so the special-sum-set
conditions reduce to comparing a $k$-element prefix against a $k$-element suffix — the cheapest
available necessary condition, checked before any subset enumeration ([cheap checks
first](/blogs/takeaway/cheap-checks-first)). Problem 331 accumulates row-width *parities* rather
than values, giving a sliding window over parity counts. And problem 238 is the prettiest inversion
of all: a substring of a periodic digit stream starting after position $t$ sums to $k$ exactly when
$P_t + k$ is itself a prefix sum, so the question becomes membership in the *set* of prefix sums —
held as one machine-word [bitset](/blogs/technique/bit-array) and tested by a rotation. The prefix
sums stop being an intermediate and become the data structure.

**Counting pairs through the prefixes.** Problem 238's inversion has a counting form, and it is the
reason prefix sums show up in so many "how many substrings" questions. A window $[i, j)$ has
property $X$ exactly when the pair $(P_i, P_j)$ does. So counting windows means counting pairs of
prefixes, and for an equality condition that is $\sum_r \binom{c_r}{2}$ over the prefix-value
counts $c_r$. Problem 706 rests on this: a digit string's substrings divisible by 3 are the pairs of
prefixes with equal [residue](/blogs/domain/modular-arithmetic) mod 3. To count the $d$-digit
numbers whose number of such substrings is itself divisible by 3, it does not track the substrings
at all. Its automaton state is the three prefix-residue counts, kept mod 3 and relative to the
current residue (81 states), and it is raised to the $d$-th power as a matrix. Problem 705 counts
ordered pairs of a different kind: positions $i < j$ holding digits $x$ and $y$, over a digit string
of several million characters. For each $x$, a cumulative count of $x$-digits gives "how many $x$
come before here" at every position. Summing that at the positions of $y$ is the pair count
$\#(x \text{ before } y)$, so nine cumsums produce the whole $9 \times 9$ table. This is the
textbook way to count [inversions](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics))
over a small alphabet, and it needs neither a Fenwick tree nor a merge sort.

## How to reason about it

- **Store the leading zero and use half-open ranges.** $P$ has $n+1$ entries and
  $\sum a[i{:}j] = P_j - P_i$, which is why problem 50 writes `[0] + list(itertools.accumulate(...))`
  rather than [`accumulate`](/blogs/technique/itertools-accumulate) alone. The $n$-entry variant
  needs a special case for $i = 0$, and that is where the off-by-one lives.
- **It needs an *invertible* operation.** Sum, xor, count, product in a field: all fine, because the
  query is a subtraction. Problem 943 carries a third, xor array of parity bitmasks beside its
  counts and sums. Because xor is its own inverse, $q$ whole periods contribute the period's xor
  once if $q$ is odd and not at all if $q$ is even. Problem 675's prefix product is safe only
  because $1\,000\,000\,087$ is prime; under a composite modulus a factor sharing a divisor with it
  could not be removed. Min and max are not — no prefix bookkeeping recovers $\min a[i{:}j]$. That
  is precisely why maximum subarray is solved by a running minimum *over the prefixes* rather than by
  a range-minimum query, and why real range minima need a sparse table or a monotone deque.
- **Only for a static array.** Any update to the underlying values invalidates every prefix past it.
  When the array changes between queries the right structure is a
  [Fenwick tree](/blogs/technique/fenwick-tree) — the same prefix query, $O(\log n)$ for reads *and*
  writes. Problem 464 sweeps points in key order and inserts into one as it goes, so each query
  counts only the points already inserted: a prefix sum you are allowed to write to.
- **Watch the accumulator's width.** A `np.cumsum` in `int64` overflows silently and the result looks
  like data ([watch integer width](/blogs/takeaway/watch-integer-width)). Problem 565 bounds its
  chunk width so no chunk's `int64` cumulative sum can overflow and carries the running total as a
  Python `int`; problem 351 keeps its totient prefix sums in `int64` and records, next to each
  vectorised sum, why that sum stays under $2^{63}$; problem 710 reduces every count mod $m$ as it extends the arrays. Under a modulus,
  remember that the query is a subtraction and needs reducing back into range. NumPy has no modular
  `cumprod`, and an `int64` one overflows within a few terms. Problem 423 therefore scans in blocks.
  It lays the array out as a $\sqrt n \times \sqrt n$ grid and runs $\sqrt n$ vectorised steps that
  reduce mod $p$ after every multiply. A short Python pass then builds each block's carry-in, and one
  broadcast multiply applies it. The result is a parallel prefix scan with $O(\sqrt n)$ interpreted
  steps instead of $n$. In floating point,
  differencing two large nearly-equal prefix sums is
  [catastrophic cancellation](/blogs/technique/catastrophic-cancellation) — the technique loses
  precision without complaining.
- **Budget the build.** $O(n)$ time and $O(n)$ memory up front to make each query $O(1)$: clearly
  worth it once the query count approaches $n$, clearly not for a handful. Build it inside `solve()`,
  sized to the input, so the cost lands in the benchmark where it belongs
  ([size work to the input](/blogs/takeaway/size-work-to-the-input)).
- **Extra dimensions cost inclusion–exclusion.** A 2-D prefix sum answers a rectangle with four
  corner reads. Non-rectangular regions are better handled one dimension at a time — prefix along
  the rows, then cumulate along the second axis, as problem 150 does — because the region's shape
  usually *is* the recurrence.
- **It is one of the few techniques that costs nothing in C.** A prefix sum is an array and a loop,
  so the C sibling is the same algorithm with the same complexity and no scaffolding — the opposite
  of what happens when a Python solution leans on a [set](/blogs/technique/set) or a
  [dict](/blogs/technique/dict). When you have a choice of how to make a hot loop cheap, prefer the
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
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0309](/solutions/0309/) — Integer Ladders
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ● [0351](/solutions/0351/) — Hexagonal Orchards
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0710](/solutions/0710/) — One Million Members
- ● [0839](/solutions/0839/) — Beans in Bowls
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0949](/solutions/0949/) — Left vs Right II
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0988](/solutions/0988/) — Non-attacking Frogs

<!-- /problems -->
