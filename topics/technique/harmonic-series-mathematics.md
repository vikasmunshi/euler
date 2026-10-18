<!-- tags: [harmonic-series-mathematics] -->
<!-- status: final -->
# Harmonic series (mathematics)

The [harmonic series](https://en.wikipedia.org/wiki/Harmonic_series_(mathematics)) is
$1 + \tfrac12 + \tfrac13 + \cdots$. It diverges, but slowly: the partial sum
$H_n = \sum_{d \le n} 1/d$ is $\ln n + \gamma + O(1/n)$, with $\gamma \approx 0.5772$. In this
repository it is a *cost model*. Any loop of the form "for each $d$, visit every multiple of $d$
up to $N$" does $\sum_d N/d = N H_N \approx N \ln N$ work. That one estimate is why divisor sieves,
Möbius sieves and factor-pair tallies all run in $O(N \log N)$. It also shows how to make them
cheaper: shrink the range of $d$, or the number of multiples each $d$ visits, and the logarithm
shrinks with it.

## The idea

Write the sieve as a double loop:

```python
for d in range(1, N + 1):
    for m in range(d, N + 1, d):     # N // d iterations
        table[m] += weight(d)
```

The inner loop runs $\lfloor N/d \rfloor$ times, so the total is
$\sum_{d=1}^{N} \lfloor N/d \rfloor = N \ln N + O(N)$. At $N = 6.4 \times 10^7$ that is about 18
visits per array entry. Each entry $m$ is visited exactly once per divisor of $m$, so the same sum
is $\sum_{m \le N} \tau(m)$: the average number of divisors is $\ln N$. Read in that direction,
the harmonic bound says that computing a divisor function for *every* $n$ up to $N$ costs only
$\log N$ per value. That is far cheaper than factoring each $n$.

The sum changes with the set $d$ ranges over, and the variations are worth knowing:

| $d$ ranges over | work $\sum N/d$ | example |
| --- | --- | --- |
| all $d \le N$ | $N \ln N$ | divisor sums, Möbius sieve |
| $d \le N/2$, multiples from $2d$ | $N \ln N - O(N)$, half the outer iterations | 211 |
| primes $p \le N$ | $N \ln \ln N$ ([Mertens](https://en.wikipedia.org/wiki/Mertens%27_theorems)) | sieve of Eratosthenes |
| squares $d^2 \le N$ | $\zeta(2) N \approx 1.64 N$ | square-free sieves |
| $d$ in a window $[a, b]$ | $N \ln(b/a)$ | 135, 136 (below) |

## Four sieves, one bound

**A divisor-function sieve: 211.** $\sigma_2(n) = \sum_{d \mid n} d^2$ for every $n < 6.4 \times 10^7$
is the double loop above with weight $d^2$. The solution makes two small savings. It seeds
`sigma2[n] = n * n` (the divisor $n$ itself), so the inner loop starts at $2d$. And since a proper
divisor satisfies $2d \le n$, the outer loop stops at $L/2$. The total stays $\approx L \ln L$.
The number of *outer* iterations halves, and that is what matters in Python, as discussed below.

**Möbius inversion by subtraction: 73.** Solution 2 counts reduced fractions in $(1/3, 1/2)$ by
rank. It sets `data[i] = i * n // d`, which counts all fractions $k/i \le n/d$, reduced or not. It
then subtracts each `data[i]` from `data[2i], data[3i], …`. That leaves only the reduced fractions
of each exact denominator. It is [Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula)
written as repeated subtraction. The pass is a divisor sieve, so it costs $D \ln D$. That is the
reason it beats the two Farey-walk solutions, which do $O(1)$ work per counted fraction and so
$\Theta(D^2)$ in total. At $D = 10^5$ the sieve finishes in milliseconds and the walks take seconds.
This file is public, so here it is in full:

```python
data = [i * n // d for i in range(len_data)]
for i in range(1, len_data):
    for j in range(2 * i, len_data, i):
        data[j] -= data[i]
return sum(data)
```

**Factor-pair tallies: 135 and 136.** Both reduce $x^2 - y^2 - z^2 = n$ over arithmetic
progressions to $n = u \cdot v$ with $v < 3u$ and $u + v \equiv 0 \pmod 4$. Instead of factoring
each $n$, they loop over $u$, step $v$ through its residue class, and increment `count[u * v]`. The
harmonic bound needs adjusting for the two constraints:

- the step of 4 divides every inner loop by 4;
- $v < 3u$ caps the inner loop at $3u$ for small $u$, so the full $N/u$ only applies from
  $u \approx \sqrt{N/3}$ upward.

The tail is a harmonic sum over the window $[\sqrt{N/3}, N/3]$, which gives
$\tfrac N4 \ln \sqrt{N/3}$. The head is a triangular sum of about $N/8$. Together that is roughly
$\tfrac N8 \ln N$, about one eighth of a full divisor sieve. With the bound written out, both
counts are clearly affordable at $N = 5 \times 10^7$ before any code runs.

## Where the time actually goes

The harmonic bound counts inner-loop visits. Language decides what a visit costs.

- **C** runs the double loop as written, so $N \ln N$ simple stores are the cost. 211's C sieve
  over $6.4 \times 10^7$ entries and 135's tally are both well under a second.
- **NumPy** turns each inner loop into one strided slice operation. 211 writes
  `sigma2[2 * d :: d] += d * d`. The $N \ln N$ element updates run in compiled code, so the Python
  cost becomes the **outer** loop, $L/2$ slice calls. Each $d$ above about $L/3$ updates a single
  element, so most of those calls are overhead. 135 builds one `np.arange(v_start, v_max + 1, 4) * u`
  batch per $u$ and tallies all of them with a single `np.bincount`.
- **Pure Python inner loops** pay interpreter cost on every visit. 73's sieve is fine at
  $D = 10^5$, about a million visits. 136 keeps its scattered `count[n] += 1` writes in plain
  Python because the indices are data-dependent. It uses an `int8` array (`signed char` in C), since
  only "0, 1, or more" matters, which cuts memory to 50 MB at $5 \times 10^7$.

So two numbers predict the run time: the harmonic total, which C pays, and the outer-loop length,
which vectorised Python pays.

## How to reason about it

- **"Each $d$ visits its multiples" costs $N \ln N$.** Use it to size a sieve before writing it. At
  $10^8$ that is about $1.8 \times 10^9$ visits: fine in C, too much for scalar Python.
- **Restrict $d$ to shrink the log.** Primes give $\ln \ln N$, squares give a constant, and a
  window $[a, b]$ gives $\ln(b/a)$. Constraints like $v < 3u$ are windows.
- **Invert "factor each $n$" into "visit the multiples of each $d$".** The average $n$ has
  $\ln n$ divisors, so the sieve is much cheaper than factoring.
- **Möbius inversion is a harmonic sieve.** Subtracting `f[i]` from its multiples turns
  "count with common factors" into "count coprime".
- **In NumPy, count the slice calls.** The harmonic total runs at C speed, and the outer loop is
  what the interpreter pays. For large $d$, where slices hold one or two elements, consider a
  scalar tail or a different formulation.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0211](/solutions/0211/) — Divisor Square Sum

<!-- /problems -->
