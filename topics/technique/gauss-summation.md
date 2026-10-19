<!-- tags: [gauss-summation] -->
<!-- status: final -->
# Gauss summation trick

The story goes that the young Gauss, told to add the numbers from 1 to 100, paired the first with the last,
the second with the second-to-last, and so on: fifty pairs, each summing to 101, so 5050. In general,
$1 + 2 + \dots + n = n(n+1)/2$, the [triangular number](https://en.wikipedia.org/wiki/Triangular_number)
$T_n$ ([Wikipedia](https://en.wikipedia.org/wiki/1_%2B_2_%2B_3_%2B_4_%2B_%E2%8B%AF) collects the history).
It is the smallest closed form in mathematics, and it keeps coming back because so many sums in Project
Euler are, at the bottom, *a run of consecutive integers or of evenly spaced multiples*. Each time
you spot one, a loop of $n$ additions becomes three multiplications. In the three solved problems below
it is never the whole solution, but it is always the step that turns a linear inner loop into $O(1)$.

## The idea — pair the ends of an arithmetic series

Write the series forwards and backwards and add them term by term. Every column has the same sum, so

$$\sum_{k=a}^{b} k = \frac{(a + b)(b - a + 1)}{2},$$

"first plus last, times the count, halved". Two consequences carry most of the weight:

- **Multiples of $s$ in a range.** The multiples of $s$ in $(L, H]$ are $s \cdot k$ for
  $k = \lfloor L/s \rfloor + 1, \dots, \lfloor H/s \rfloor$. Their sum is $s$ times a Gauss sum, or with
  $f = \lfloor L/s \rfloor$ and $\ell = \lfloor H/s \rfloor$, $s\,(T_\ell - T_f)$.
- **Higher powers.** The same "telescope and solve" trick that derives $T_n$ gives
  [Faulhaber's formulas](https://en.wikipedia.org/wiki/Faulhaber%27s_formula), the next one being
  $\sum k^2 = n(n+1)(2n+1)/6$. The pattern stops being a two-line derivation, but it stays a closed
  form in $n$.

The division is always exact — one of $n$ and $n+1$ is even, and $n(n+1)(2n+1)$ is a multiple of 6 — so the
formulas work in integer arithmetic with no rounding, *if* you divide last.

## Three uses across the problems

**6, sum square difference: the formula is the answer.** The difference between $(\sum k)^2$ and
$\sum k^2$ for $k \le n$ is $T_n^2$ minus the square-pyramidal number, both closed forms. The public
Python is a single expression:

```python
return str((n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6)
```

The loop it replaces is trivial at $n = 100$; the point is the habit. Once the problem is a formula,
$n = 10^{9}$ costs the same as $n = 100$.

**153, Gaussian integer divisors: Gauss sums inside a divisor-sum block.** The problem reduces to
sums of the form $D(x) = \sum_{k \le x} k \lfloor x/k \rfloor$, the summatory divisor function. The
quotient $\lfloor x/k \rfloor$ takes only $O(\sqrt{x})$ distinct values, and on each run of $k$ where it is
constant the remaining factor is $\sum k$ over a contiguous range. That run is one Gauss sum,
`q * (k + kmax) * (kmax - k + 1) // 2`, so the whole of $D(x)$ is $O(\sqrt{x})$ instead of $O(x)$. Without the
closed form, [quotient blocking](/topics/technique/quotient-blocking) would save nothing: you
would still add every $k$ in the block.

**234, semidivisible numbers: sum of multiples in a band.** Between consecutive primes $p < q$, every $n$
in $(p^2, q^2)$ has the same lower and upper prime square roots. The numbers in the band divisible by exactly
one of $p$, $q$ are the multiples of $p$, plus the multiples of $q$, minus twice the multiples of $pq$
([inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) on a sum rather than a count). Each
of those three is "multiples of $s$ in $(L, H]$", a Gauss sum. So the work is one $O(1)$ step per prime up
to $\sqrt{\text{limit}}$; the bands themselves, about $10^{12}$ numbers in all, are never walked.

## Python and C

- **6**: identical arithmetic. Python's integers are exact at any $n$. C's `long long` holds the
  intermediate $T_n^2$ only while $n \lesssim 7.7 \times 10^4$ — $T_n^2 \approx n^4/4$ must stay under
  $2^{63}$ — which is ample for the problem's input but not for an arbitrary one.
- **153**: the Gauss step is the same line in both. The difference is around it: Python memoises $D$
  in a `dict`, C in a hand-written open-addressing hash table, and C needs an exact `isqrtll`
  (a `sqrtl` seed corrected by $\pm 1$) where Python has `math.isqrt`.
- **234**: here the languages split on width. The products inside `sum_multiples` and the running total
  outgrow 64 bits, so C computes them in `__int128` and needs its own decimal formatter, since `printf`
  has no conversion for it. Python just uses `int`. C also guards the band's upper end with
  `upper > limit / upper` before squaring, so that $q^2$ itself cannot overflow.

## How to reason about it

- **Look for a contiguous range inside a sum.** Arithmetic progressions hide behind "multiples of",
  "for every $k$ between", and any block where one factor is constant and the other is the index.
- **Multiply before you divide, but divide before you overflow.** The division by 2 or 6 is exact only on
  the full product. In fixed width, either widen (`__int128`) or divide the even factor first:
  `(n / 2) * (n + 1)` when $n$ is even, `n * ((n + 1) / 2)` otherwise.
- **Express a range as a difference of prefixes.** $T_\ell - T_f$ is easier to get right than
  first-plus-last formulas with their off-by-one bounds, and it extends unchanged to $\sum k^2$.
- **It composes.** Gauss sums are the leaf of bigger machinery: inclusion–exclusion over the multiples
  (234), quotient blocking (153), or modular arithmetic, where the $/2$ becomes multiplication by the
  modular inverse of 2.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0234](/solutions/0234/) — Semidivisible Numbers

<!-- /problems -->
