<!-- tags: [vectorize-the-independent-axis] -->
<!-- status: final -->
# Vectorize the independent axis

Almost every heavy computation is a loop nest, and almost every loop nest has two kinds of axis.
Along one, step $i$ needs the result of step $i-1$: a bisection halving its bracket, a walk taking
its next step, a recurrence reading its earlier terms. Along the other, the entries never look at
each other: a thousand partitions, ten million keys, every prime in a window. In Python the
interpreter charges per step, not per arithmetic operation, so the choice of which axis the Python
`for` runs over decides the running time. Keep the dependent axis as the interpreted loop, which
should be short, and turn the independent axis, which is wide, into one
[NumPy](https://numpy.org/doc/stable/user/whatisnumpy.html) array operation per step. All six
problems below are solved that way, and in each one most of the work was spotting the independent
axis and then making its entries uniform enough to run in lockstep.

## The idea

[Array programming](https://en.wikipedia.org/wiki/Array_programming) applies one operation to
every element of an array in a compiled loop. It pays off only when the elements don't depend on
one another *within* the step, so the first question is always **what does step $i$ read?**
Everything that a step neither reads nor writes for its neighbours is a candidate axis to
vectorize. In these problems it shows up in four forms:

| Problem | Sequential axis (the Python loop) | Independent axis (one array op) |
|---|---|---|
| [564](/solutions/0564/) | 64 bisection steps for the circumradius | every side-multiset (partition) of a given $n$ |
| [941](/solutions/0941/) | 12 rotation shifts of a window | all $10^7$ combinations being keyed |
| [971](/solutions/0971/) | ~30 bits of a modular exponent | every prime $p \equiv 1 \pmod 5$ in a sieve window |
| [975](/solutions/0975/) | one step of a walk through a grid of cells | all 2628 prime pairs, each walking its own grid |
| [986](/solutions/0986/) | blocks of a floored-average recurrence | 64 candidate values of $M$ in one search round |
| [1001](/solutions/1001/) | the row $l$ of an interval DP, swept downward | 512 DP columns $r$ at a time |

- **Many instances of the same small problem.** 564 solves one transcendental equation per side
  multiset, 971 runs one fixed recipe per prime, and 975 runs one walk per prime pair. Each instance
  is a lane; the shared recipe is the step.
- **Many inputs to one pure function.** 941 needs a sort key for every pseudo-random combination;
  the key of one never depends on another, so all ten million rotations are formed arithmetically,
  $(w \bmod 10^{n-s})\,10^s + \lfloor w / 10^{n-s} \rfloor$, with a running minimum over the twelve
  shifts.
- **Many candidates in a search.** 986 asks for the largest feasible $M$. Feasibility is monotone,
  which would normally mean a scalar binary search, but each candidate's simulation is independent
  of the others, so the search tests 64 candidates side by side as the columns of one ring buffer:
  a [binary search](https://en.wikipedia.org/wiki/Binary_search) generalised to 64 probes per round.
- **The other axis of a dynamic programme.** 1001's recurrence $C_r[l]$ runs sequentially down $l$,
  but different columns $r$ never read each other except through finished values. Sweeping $l$ once
  for a block of columns turns about $N^2/6$ interpreted updates into $N$ slice updates per block.

941 also does it a second time, on an axis that doesn't look independent at all. The inputs come
from a [linear congruential generator](https://en.wikipedia.org/wiki/Linear_congruential_generator),
the textbook sequential loop. Composing the step map 4096 times gives one affine map
$a \mapsto Aa + C$, and applying it to a row of 4096 values produces the next row. That
jump-ahead turns
the dependency into 4096 independent lanes.

## Making the lanes march in step

Finding an independent axis is half the work. The other half is that every lane must run the same
instruction at the same step, and scalar code is full of branches and early exits that differ from
lane to lane. The six problems use a small set of fixes for that:

- **Fixed trip counts instead of convergence tests.** 564 bisects for exactly 64 steps, which uses
  up double precision for every row, so nothing has to stop early. 971 doesn't detect the cycles
  of its five-node map. It applies the map five times to all five classes, after which the image
  *is* the set of cyclic nodes.
- **Compute both branches, then select.** 564's "centre inside / centre outside" cases become one
  `np.where` over a precomputed boolean mask; 971's binary exponentiation multiplies in only the
  lanes whose current exponent bit is set, because each lane has its own exponent.
- **Shrink the active set.** Lanes that finish leave the arrays. 975 drops completed walks after
  every step; 971 retries only the primes whose primitive-root search hasn't succeeded yet.
- **Check rarely when verdicts are permanent.** 986's "all zero" and "all positive" verdicts can
  never be revoked, so it checks every eighth block. Checking less often delays a verdict but never
  changes it.
- **Peel off the rare case.** 941's "borrowed tail" windows need a different key. They're rare, so
  the vector pass keys everything the common way and a scalar loop re-keys the few exceptions.
- **Turn a condition into a slice.** In 1001 the indicator $[p \le r]$ selects a suffix of the
  sorted block, found with `bisect_left`, so a conditional update becomes `cur[k:] = …`.

The shape they share is easy to sketch. This is the lockstep bisection skeleton, with an arbitrary
per-row residual standing in for the problem:

```python
lo, hi = np.zeros(rows), np.ones(rows)
for _ in range(64):                      # the sequential axis: short, fixed
    mid = (lo + hi) / 2
    above = residual(mid) > 0            # one array op over every row
    lo, hi = np.where(above, lo, mid), np.where(above, mid, hi)
```

## How to reason about it

**What it buys.** The interpreted step count drops from (sequential length × width) to the
sequential length alone. The recorded benchmarks put the vectorised Python within about 2× of the
C port in 941, 2.5× in 971 and 5× in 1001, all of them problems where a per-element Python loop
would have taken minutes. In C, by contrast, the same independence is only a choice of loop order,
and the ports mostly run the scalar loop element by element. 986's C port is the exception: it
keeps the batched layout because a contiguous block update is good for the cache.

**What it costs.**

- *Memory scales with the width.* Vectorize too wide and the working set leaves the cache or
  doesn't fit at all. That's why 971 sieves in windows of $2^{25}$, 1001 takes 512 columns per
  block and keeps snapshots only for open intervals, and 986 keeps a ring of $32n$ rows rather than
  the whole history. Blocking is the normal companion of this technique.
- *Lockstep wastes work.* Every row runs all 64 bisection steps, and 986's probes above the
  threshold simulate until their verdict appears. The trade is worth it while the waste is a
  constant factor and the interpreter overhead it removes is not.
- *Fixed-width lanes overflow quietly.* NumPy has no big integers. 971 relies on $p < 2^{31}$ so
  a product fits in `uint64`, and 941 splits its multiplier into two $10^6$-sized halves because
  $Aa$ can reach $10^{24}$. Check the bound before vectorizing, not after a wrong answer (see [watch integer width](/blogs/takeaway/watch-integer-width)).
- *The bottleneck moves.* Once the arithmetic is vectorized, whatever is still scalar dominates.
  In 564 that is the recursive generator building about a million partition rows, and in 975 it is
  the long half-path, so those two stay well behind C even though their arithmetic is batched.

**When to reach for it.** When a Python solution is too slow and its inner work is simple
arithmetic, look for the axis whose entries don't talk to each other before rewriting in C or
reaching for a cleverer algorithm. If the loop you're running is the dependent one, swap the nest.
If the dependence is real but affine, as in 941's generator, compose it into a jump. And if no
such axis exists, because every step reads its predecessor and there is only one instance, the
win has to come from somewhere else (see [algorithm beats language](/blogs/takeaway/algorithm-beats-language)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0564](/solutions/0564/) — Maximal Polygons
- ● [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ● [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0975](/solutions/0975/) — A Winding Path
- ● [0986](/solutions/0986/) — Another Infinite Game
- ● [1001](/solutions/1001/) — Connections I

<!-- /problems -->
