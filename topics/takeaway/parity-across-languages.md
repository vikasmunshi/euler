<!-- tags: [parity-across-languages] -->
# Hold complexity fixed across ports

_Keep the C and Python algorithms identical so benchmarks compare constant factors._

Every problem in this repository is solved twice: once in Python, once in C, under one shared
harness. That only tells me something if the two files run the *same algorithm*. When they do, the
ratio between them is a clean measurement of what the language costs me. When they don't, the ratio
measures nothing at all — and, usefully, says so loudly.

## The idea

A benchmark comparing two programs measures the difference between them. If the Python and the C
differ in *both* algorithm and language, the timing is a sum of two effects I cannot separate. So I
fix one variable: the C port is a faithful translation, not a redesign — same recurrence, same data
structures, same memoization, same
[asymptotic class](https://en.wikipedia.org/wiki/Big_O_notation). This is the rule in
[the C translation conventions](/docs/convention_c_translation), and it is why a `.c` here
counts as *correct* only when its algorithm matches its Python sibling's.

With complexity held fixed, the remaining difference is the **constant factor**: what one step of
the algorithm costs in each language. The runner makes that comparison honest — the same test-case
inputs, the same timed `solve()` loop, the same `<runs> <avg_seconds> <result>` line out of both.

The measurement, across the 42 public Python/C index pairs carrying this tag on their production
test case:

| Ratio (Python ÷ C) | What is happening |
| --- | --- |
| **~1–3×** | Almost no interpreted work — a closed form, or a loop that lives inside a C-implemented builtin or library |
| **~10–30×** (median **20×**) | The typical band: an ordinary Python loop over ints, lists and dicts |
| **~50–185×** | A tight numeric inner loop, millions of iterations, one [CPython](https://en.wikipedia.org/wiki/CPython) bytecode dispatch per operation |

The geometric mean is **21.5×**. That number is the useful one to carry around: a faithful port
buys roughly one and a half orders of magnitude, and *only* that. It does not buy a better
complexity class — which is why a slow language with the right algorithm still beats a fast one
with the wrong algorithm (see
[algorithm beats language](/topics/takeaway/algorithm-beats-language)).

## How to reason about it

**Read the ratio as a diagnostic, not a score.** Once I expect ~20×, every departure is a question
worth answering:

- **Far *below* the band** — the Python was never really doing the work. Problem 10's `primesieve`
  index lands at 6.7× because both languages call the same C library; its dict-keyed incremental
  sieve lands at 2.6× because CPython's `dict` *is* a tuned C hash table, and the port's
  hand-rolled one is no faster. In both cases I am timing C against C.
- **Far *above* the band** — either the inner loop is unusually arithmetic-heavy, or the two files
  have quietly diverged. A ratio in the hundreds is the first place I look for a broken port.
- **A ratio near 1× on an O(1) solution** is expected and uninteresting: there is nothing to
  amortise, so I am measuring process startup, not the algorithm.

**Parity includes the parts that are easy to skip.** Python hands me `functools.lru_cache`,
unbounded integers, and `dict` for free; a faithful port has to *build* the equivalents rather than
drop them. Problem 60's C file carries an explicit hash table commented as an "lru_cache stand-in"
precisely for this reason — omitting it would have changed the complexity, not just the constant.
The same applies in the other direction: when Python's arbitrary-precision integers are load-bearing,
the port reaches for [GMP](https://gmplib.org/) instead of silently truncating to `long long`.

**The pitfall is optimising one side.** It is tempting to let the C use a better trick "because C
can". That single change makes every subsequent timing comparison meaningless, and it usually hides
the insight: if the trick is genuinely better, it belongs in *both* files, as a new solution index.
Indices are cheap; a contaminated benchmark is not.

## In the wild

- **[Problem 1](/solutions/0001/)** — five indices of the same problem give the whole spread at
  once. The closed-form index runs at **1.4×**, the term-by-term scan at **23.8×**. The algorithms
  are matched pairwise, so the gap between those two ratios is purely how much work each index
  leaves inside the interpreter. The port is line-for-line:

  ```python
  def sum_arithmetic_series(common_difference: int, *, max_limit: int) -> int:
      """Closed-form sum of 0, d, 2d, ... below max_limit: d*n(n+1)/2."""
      n = (max_limit - 1) // common_difference
      return common_difference * (n * (n + 1)) // 2
  ```

  ```c
  /* Closed-form sum of 0, d, 2d, ... below max_limit: d*n(n+1)/2. */
  static long long sum_arithmetic_series(int common_difference, long long max_limit) {
      long long n = (max_limit - 1) / common_difference;
      return (long long)common_difference * (n * (n + 1)) / 2;
  }
  ```

- **[Problem 7](/solutions/0007/)** — a [sieve of Sundaram](https://en.wikipedia.org/wiki/Sieve_of_Sundaram)
  marking a Python `list` element by element: **105×**, near the top of the band. Nothing is wrong
  with the port; the algorithm is simply one cheap arithmetic operation per iteration, which is
  exactly where a bytecode dispatch per operation hurts most.

- **[Problem 78](/solutions/0078/)** — the [pentagonal number theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem)
  recurrence — `O(N·sqrt(N))` of pure integer arithmetic — at **185×**, the widest gap in the set.
  Same recurrence, same modular reduction, same table; only the per-operation cost differs.

- **[Problem 60](/solutions/0060/)** — the clique search whose C port reimplements
  [memoization](https://en.wikipedia.org/wiki/Memoization) by hand to stay faithful. It settles at
  **3.1×**, because most of the runtime is memoized primality tests that both languages end up
  performing the same number of times.

## Problems

<!-- BEGIN problems (generated by update-tags) -->
p0001
p0003
p0004
p0005
p0007
p0014
p0027
p0030
p0032
p0034
p0037
p0042
p0043
p0044
p0045
p0048
p0049
p0050
p0051
p0052
p0053
p0057
p0060
p0061
p0064
p0066
p0072
p0073
p0075
p0078
p0081
p0083
p0086
p0092
p0095
p0098
p0104
p0105
p0109
p0112
p0115
p0116
p0122
p0126
p0127
p0129
p0131
p0133
p0135
p0138
p0139
p0142
p0144
p0145
p0146
p0149
p0150
p0151
p0153
p0156
p0161
p0166
p0168
p0171
p0172
p0176
p0179
p0181
p0184
p0185
p0191
p0200
p0201
p0204
p0211
p0212
p0215
p0216
p0221
p0223
p0224
p0345
p0347
p0387
p0429
p0478
p0501
p0504
p0545
p0642
p0650
p0679
p0704
p0719
p0745
p0751
p0757
p0800
p0808
p0816
p0820
p0834
p0845
p0932
p0934
p0938
p0944
p0965
p1000
<!-- END problems -->
