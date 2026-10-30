<!-- tags: [stars-and-bars-combinatorics] -->
<!-- status: final 2026-10-30T06:42Z -->
# Stars and bars (combinatorics)

[Stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)) counts the ways to
put $n$ identical items into $k$ distinguishable bins. Line up the $n$ stars and drop $k - 1$ bars
among them. Each arrangement of stars and bars is one distribution, and the count is a single
binomial coefficient. The [composition](/topics/domain/composition-combinatorics) page uses
the result as one row of its table. This page is about the technique on its own: the two formulas,
the slack-variable trick that turns "at most" into "exactly", and the five ways the problems below
use a stars-and-bars count. They use it as an answer, as the size of a search space, as a
probability, as a generating-function coefficient, and as the prime-power value of a
multiplicative function.

## The idea

Two theorems, one picture:

$$\#\{x_1 + \dots + x_k = n,\ x_i \ge 1\} = \binom{n-1}{k-1}, \qquad
\#\{x_1 + \dots + x_k = n,\ x_i \ge 0\} = \binom{n+k-1}{k-1}.$$

The first chooses $k - 1$ of the $n - 1$ gaps between stars. The second treats the $k - 1$ bars as
symbols too and chooses their positions among $n + k - 1$ slots. Substituting $y_i = x_i - 1$ turns
the first into the second, so the two differ only by a shift. The second is also the number of
**multisets** of size $n$ drawn from $k$ kinds, $\left(\!\binom{k}{n}\!\right)$. Choosing how many
of each kind is exactly choosing how many stars go in each bin.

Two corollaries carry most of the work:

- **Sorted sequences are multisets.** A non-decreasing sequence is fixed by how many times each
  value appears. So there are as many sorted length-$n$ sequences over $k$ values as there are
  multisets.
- **"At most" adds a bin.** $\sum_{x_i \ge 0} [\,\sum x_i \le n\,]$ is the same as
  $x_1 + \dots + x_k + s = n$ with a slack bin $s \ge 0$, so it is $\binom{n+k}{k}$. Summing the
  "exactly $j$" counts for $j \le n$ gives the same answer through the
  [hockey-stick identity](https://en.wikipedia.org/wiki/Hockey-stick_identity). The slack bin is
  that identity with a reason attached.

## Five uses

**As the answer.** Problem 113 counts numbers below $10^{100}$ whose digits never go up or never go
down. An increasing $d$-digit number is a sorted sequence over $\{1, \dots, 9\}$, so a multiset,
and there are $\binom{d+8}{8}$ of them. A decreasing one is a multiset over $\{0, \dots, 9\}$,
$\binom{d+9}{9}$, minus the all-zero string. The nine repdigits per length are in both sets, so
inclusion-exclusion removes them once. Summing over lengths is the slack-bin step again, and the
hockey stick folds the sum into a closed form with two binomials. A googol-sized bound costs the
same as a small one, because the method counts and never visits a number.

**As the size of a search space.** Problem 862 needs, for every multiset of $k$ digits, the
number of its distinct arrangements. That is a [multinomial](/topics/technique/multinomial-theorem),
corrected for leading zeros. The multisets are the weak compositions of $k$ into ten parts, so
stars and bars says in advance how much work enumerating them is: $\binom{k+9}{9}$, about
$2 \times 10^6$ at $k = 16$, against $10^{16}$ numbers. The count is a *budget*. It tells you to
enumerate the multisets and not the numbers. The enumeration is a depth-first recursion that
chooses $c_0$, then $c_1$, and so on, with the last count forced:

```python
def distribute(digit, remaining, ...):
    if digit == 9:
        ...                       # the leaf: c9 = remaining
        return
    for c in range(remaining + 1):
        distribute(digit + 1, remaining - c, ...)
```

Each leaf is one star-and-bar arrangement, and the recursion visits each exactly once.

**As a probability.** Problem 253 lays caterpillar pieces in random order and tracks the segment
count. Its notes show that, given the history, the empty gap widths form a *uniform random
composition* of the $E$ empty cells into $P$ positive parts. The Markov chain needs two facts about
such a composition. Both are ratios of stars-and-bars counts. By symmetry the mean part is $E/P$.
A designated part equals $1$ with probability

$$\frac{\binom{E-2}{P-2}}{\binom{E-1}{P-1}} = \frac{P-1}{E-1},$$

because fixing that part leaves a composition of $E - 1$ into $P - 1$ parts. The binomials never
appear in the code. Only their ratio does, and it is a single division (`lone_gap_chance`). That
holds generally: a marginal of a uniform composition is a ratio of two stars-and-bars counts, and
the ratio is usually a simple rational function.

**As a generating-function coefficient.** $\binom{n+k-1}{k-1}$ is the coefficient of $y^n$ in
$(1 - y)^{-k}$, which is the product of $k$ copies of $1 + y + y^2 + \cdots$, one per bin. Problem
996 ends with a polynomial $N(y)$ divided by $(1 - y^2)^n (1 - y)$ and needs the sum of
coefficients up to $y^k$. The factor $(1 - y^2)^{-n}$ is stars and bars in $y^2$. The extra
$1/(1 - y)$ is the slack bin that turns "exactly" into "at most". Together they give
$\binom{\lfloor t/2 \rfloor + n}{n}$ at $y^t$, so the answer is one short sum of binomials against
the coefficients of $N$. The same problem uses the positive form too: the tuples that break its
half-sum rule are counted as $L \binom{m-1}{L-1}$, a composition of $m$ into $L$ positive parts
for each of the $L$ positions the oversized entry can take.

**As a local factor.** Problem 452 counts the $n$-tuples of positive integers whose product is at
most $m$. Grouping the tuples by their product $k$ gives $\sum_{k \le m} d_n(k)$, where $d_n(k)$
counts the ordered factorisations of $k$ into $n$ factors. Stars and bars is what makes that
function tractable. Write $k = \prod p^{e_p}$. A tuple with product $k$ is chosen one prime at a
time: the $e_p$ copies of $p$ are identical stars, and the $n$ tuple positions are the bins. So
$d_n$ is [multiplicative](/topics/domain/multiplicative-function), and on a prime power

$$d_n(p^e) = \binom{n+e-1}{e}.$$

In the earlier uses the binomial was the count of the whole object. Here it is only the count at
one prime, and the product over primes rebuilds the rest. That changes the job. Once you have a
multiplicative function with a closed form on prime powers, you can sum it with a sublinear
[Min_25 sieve](/topics/technique/min-25-sieve) and never touch the $m$ individual integers. The
shape of the binomial helps as well. At $e = 1$ it is just $n$, constant on primes, so the prime
part of the sum is $n \cdot \pi(m)$. And $e$ never exceeds $\log_2 m$, so only about thirty of
these binomials are ever needed, even with $n = 10^9$ bins.

## Pitfalls

- **Positive or non-negative?** The two formulas differ by $k$ in the top argument. Decide what an
  empty bin means before writing the binomial. A leading digit can't be 0, but the count of zeros
  in a multiset can.
- **Upper bounds are not free.** Stars and bars allows any bin to hold everything. If bins are
  capped, for example digits at most 9 or a part at most half the sum, subtract the violators by
  [inclusion-exclusion](/topics/technique/inclusion-exclusion-principle) or switch to a DP. 996
  manages with one subtraction, because at most one part can exceed half the total.
- **Distinguishable bins, identical stars.** If the bins are also identical, you are counting
  partitions, and no binomial gives the answer.

## C and Python

The combinatorics is the same in both languages. The binomial coefficient is not:

- **Exact, small $k$.** Python calls `math.comb`, which is arbitrary-precision and exact. 113's C
  writes the multiply-then-divide loop `result = result * (n - i) / (i + 1)`. Each division is
  exact because the running value is itself $\binom{n}{i+1}$. With $k \le 10$ the intermediates fit
  a `long long`.
- **Modular, larger $k$.** 996 needs $\binom{\cdot}{n}$ for $n$ up to 1000 modulo a prime. Both
  languages form the product of the $n$ consecutive integers modulo $p$ and multiply by
  $(n!)^{-1}$. Python uses `pow(x, -1, p)` and C uses Fermat, `pow_mod(fact, p - 2)`. With modulus
  0, meaning the unreduced statement examples, Python falls back to `math.comb` and C to the exact
  multiply-then-divide loop in `unsigned __int128`.
- **Modular, huge top and small bottom.** 452 needs $\binom{n+e-1}{e}$ with $n = 10^9$ but
  $e \le 30$. The cheap way to build it is along $e$:
  $\binom{n+e-1}{e} = \binom{n+e-2}{e-1} \cdot (n+e-1) / e$. Each step divides by the small $e$
  through its modular inverse, and there are no factorials of $n$ anywhere. Python again uses
  `pow(e, -1, p)` and C uses Fermat. Products of two reduced residues stay below $2^{62}$, so a
  `long long` is enough.
- **Wide accumulators.** 862's total passes $10^{26}$. Python's integers grow as needed. The C
  keeps $M$ and $V$ in 64 bits, promotes to `__int128` only at the product $V(V - 1)$, and formats
  the 128-bit total by hand, since `printf` cannot print `__int128`.
- **No binomials at all.** 253's chain uses only the ratio $(P-1)/(E-1)$. Both languages run it in
  `double`, so the C is a line-for-line port with no big-integer concerns.

## How to reason about it

- **Identical items into labelled bins: write the binomial.** Look for counts over a fixed
  alphabet: digit multisets, sorted sequences, monomials of a fixed degree, occupancy vectors.
- **"Total at most $n$": add a slack bin** instead of summing over the total.
- **Use the count as a budget.** Before enumerating vectors that sum to $n$, compute
  $\binom{n+k-1}{k-1}$. If it is small, enumerate the vectors instead of the objects they stand for.
- **Marginals of a uniform composition are ratios of binomials.** Simplify the ratio by hand. It is
  usually a short fraction, and the code is better for it.
- **$(1 - y)^{-k}$ is stars and bars.** When a generating function has that denominator, its
  coefficients are binomials, so read them off directly instead of expanding the series.
- **Counting factorisations: split by prime.** Ordered tuples with a given product are stars and
  bars on each exponent. That makes the count multiplicative, so the multiplicative-function
  machinery applies to the sum.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0452](/solutions/0452/) — Long Products
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
