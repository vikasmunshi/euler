<!-- tags: [kummers-theorem] -->
<!-- status: final 2026-10-19T06:44Z -->
# Kummer's theorem

[Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem) says that the exponent
of a prime $p$ in $\binom{n}{m}$ equals **the number of carries when $m$ and $n - m$ are added in
base $p$**. It turns a question about a huge number, how divisible $\binom{n}{m}$ is, into
an addition of two small numbers. The formula and its derivation from Legendre are on
[Legendre's formula](/topics/domain/legendres-formula), and
[primes in Pascal's triangle](/topics/number-theory/primes-in-pascals-triangle) puts it beside
Lucas's theorem. This page is about the *carry* reading itself: why it holds, and how each solved
problem uses it differently. 154 counts carries, 203 stops at the second one, and 704 maximises them.

## The idea — a carry is a factor of $p$

By [Legendre](/topics/domain/legendres-formula), $v_p(n!) = (n - s_p(n))/(p-1)$, where $s_p$ is the
base-$p$ digit sum. Subtract for $m!$ and $(n-m)!$:

$$v_p\binom{n}{m} = \frac{s_p(m) + s_p(n-m) - s_p(n)}{p-1}.$$

The carry reading follows from what a carry does to digit sums. When two digits plus an incoming
carry reach $p$ or more, the column keeps the excess and passes 1 to the next column. That loses
$p$ from the digit total and adds back 1, a net drop of $p - 1$. So
$s_p(m) + s_p(n-m) - s_p(n) = (p-1) \cdot \#\text{carries}$, and the division is exact. Three
consequences make it practical:

- **Only small numbers are involved.** $m$ and $n-m$ have $O(\log_p n)$ digits, while $\binom{n}{m}$
  can have thousands. The valuation is computed without ever forming the binomial.
- **The carries arrive one at a time.** A digit-by-digit addition increases the exponent as it goes, so a
  threshold test ("at least $e$ factors of $p$?") can stop at the $e$-th carry.
- **It extends to multinomials.** For $\frac{n!}{i!\,j!\,k!}$ the exponent is the total carry count of
  the three-way addition $i + j + k$, which equals $(s_p(i)+s_p(j)+s_p(k)-s_p(n))/(p-1)$.

For $p = 2$ the digit sum is the popcount, so
$v_2\binom{n}{m} = \mathrm{popcount}(m) + \mathrm{popcount}(n-m) - \mathrm{popcount}(n)$. That is
three [Hamming weights](/topics/technique/hamming-weight).

## Three uses across the problems

**154, Pascal's pyramid: compare digit-sum tables.** The question is how many trinomial coefficients of
$(x+y+z)^{200000}$ are divisible by $10^{12}$. That holds when $v_2 \ge 12$ and $v_5 \ge 12$, and in
digit-sum form, with $p - 1$ multiplied through to avoid division, it becomes

$$s_2(i)+s_2(j)+s_2(k) \ge s_2(n) + 12, \qquad s_5(i)+s_5(j)+s_5(k) \ge s_5(n) + 4 \cdot 12.$$

So the whole problem is two byte tables, $s_2[x]$ and $s_5[x]$ for $x \le n$, each filled by
$s_p[x] = s_p[\lfloor x/p \rfloor] + x \bmod p$, followed by $2 \times 10^{10}$ table comparisons. No
coefficient is computed.

**203, squarefree binomial coefficients: stop at the second carry.** $\binom{n}{k}$ is
[square-free](/topics/domain/square-free-integer) iff every prime $p \le n$ produces *at most one*
carry in $k + (n-k)$. The test walks the base-$p$ digits of $k$ and $n-k$ together with a running
carry and rejects on the second one. Values reach $10^{14}$ for 51 rows and $10^{28}$ for the larger
test, but no value is factored. Only coefficients that pass are formed, so they can be summed as
distinct values. This is the incremental threshold test from above.

**704, factors of two: maximise the carries.** $F(n) = \max_m v_2\binom{n}{m}$ asks for the
addition $m + (n-m) = n$ that carries most often in binary. The carry rules give the answer. A
carry *out* of a column with no carry in needs $1 + 1$, which leaves a 0 in $n$, so a chain must
start at a 0-bit of $n$. Once started, a chain can be sustained through every column below the top
bit, by choosing the right bits of $m$. So $F(n)$ depends only on $n$'s binary shape, not its
size, and $S(N) = \sum F(n)$ groups by bit length into closed forms over complete binary ranges plus one
partial top range. That is $O(\log N)$ work for $N = 10^{16}$. Kummer here does more than compute a
valuation: it turns an optimisation over $m$ into a statement about carry chains.

## Python and C

- **154** is where the languages differ most. Both build the digit-sum tables (Python vectorises the
  build with repeated `% base` and `//= base` over an `arange`; C uses the one-line recurrence into
  `unsigned char` arrays). For each row, Python adds the forward slice to a *reversed copy*, so
  `s[:m+1] + rs[i:]` is the vector of $s[j] + s[m-j]$, and counts the elements where both masks are true.
  C cannot vectorise, so it halves the work instead with the $j \leftrightarrow k$ symmetry: it tests
  $j \le m/2$ and adds 2, or 1 on the diagonal.
- **203**: the carry walk is the same in both. Python keeps the distinct squarefree values in a
  `set[int]` built with `math.comb`. C builds each value with GMP's `mpz_bin_uiui` into a growable
  `mpz_t` array, sorts it with an `mpz_cmp` comparator, and sums one value from each run of equal values.
- **704**: Python uses `int.bit_length()` and `int.bit_count()`. C writes both as shift loops
  (`__builtin_popcountll` would also work), and the closed forms fit in `long long`.

## How to reason about it

- **When a question asks how many times $p$ divides a binomial or multinomial, count carries.** Never
  form the coefficient to factor it.
- **Precompute digit sums when the same numbers recur.** If the indices range over $0..n$, a
  $O(n)$ table of $s_p$ makes each valuation a few lookups (154).
- **Stop early on thresholds.** Divisible by $p^e$ means $e$ carries, so stop at the $e$-th (203,
  where $e = 2$).
- **Optimise over carry patterns, not over $m$.** A carry chain starts only at a 0-digit of $n$
  and can then run upward, so extremes of $v_p\binom{n}{m}$ are properties of $n$'s digits (704).
- **Use popcount for $p = 2$.** $v_2\binom{n}{m}$ is a difference of popcounts, and $\binom{n}{m}$ is odd iff
  $m$'s bits are a subset of $n$'s, the Lucas corollary.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients

<!-- /problems -->
