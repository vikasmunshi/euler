<!-- tags: [in-place-algorithm] -->
<!-- status: final -->
# In-place algorithm

An [in-place algorithm](https://en.wikipedia.org/wiki/In-place_algorithm) transforms its data
using only a constant (or small) amount of extra memory, overwriting the input as it goes. In
Project Euler the idea shows up mostly in [dynamic programming](/topics/technique/dynamic-programming):
a DP *table* is often only ever read along a moving front, so a full table is wasted memory, and one
array updated in place does the same job. The difficulty is that overwriting is only safe when
nothing later still needs the old value. **Update order is the whole correctness argument.** The three
solved problems below each overwrite in place, and each relies on a different ordering rule to do it safely.

## The idea — overwrite only what is dead

A DP recurrence reads some cells and writes one. Storing it in place is correct iff, at the moment
you overwrite cell $x$, every future read of $x$ wants the **new** value. Equivalently, no future
computation needs the **old** value. Two classic forms:

- **Overwrite the input with the answer.** If the recurrence for a cell reads only its own input
  value and cells already finalised, the input grid itself can become the DP table (81).
- **Collapse a dimension.** If row $i$ of the table reads only row $i - 1$, keep one row. The update
  direction then decides which version (old or new) each read sees. That single choice is the
  difference between 0/1 and unbounded knapsack (249).

When the order cannot be made to work, the fallback is **two rolling buffers** (old and new) with a
pointer swap per step: $O(2n)$ instead of $O(n)$, but still far from the full table (938).

## Three problems, three orderings

**81, path sum (two ways): the matrix becomes the DP.** The minimal path from a cell to the
bottom-right corner, moving right or down, is the cell's own cost plus the cheaper of its right and
lower neighbours' minimal paths. Visit cells so that both neighbours are finished first. The public
solution walks reverse anti-diagonals from the corner and adds into the input matrix directly:

```python
for row, col in move_diagonally((size := len(matrix))):
    ...
    matrix[row][col] += min(neighbors, default=0)
return matrix[0][0]
```

Each cell's original cost is read exactly once, in its own update, so overwriting it costs nothing.
Any order with both successors done first would also work, reverse row-major for example. The
anti-diagonal sweep is one valid
[topological order](https://en.wikipedia.org/wiki/Topological_sorting) of the grid.

**249, prime subset sums: the descending knapsack.** The number of subsets of the primes below 5000
with each sum $s$ is the coefficient table of $\prod_p (1 + x^p)$. Multiplying in one factor
$(1 + x^p)$ is the [0/1 knapsack](/topics/technique/knapsack-problem) step
$\text{count}[s] \mathrel{+}= \text{count}[s - p]$. Done in a single array, the direction matters:

- **descending $s$**: `count[s - p]` has not been updated yet in this pass, so it is still the old
  value. Each prime is used *at most once*, which is what the problem asks for.
- **ascending $s$**: `count[s - p]` may already include $p$, so a prime can be used many times. That is
  the *unbounded* knapsack, and here a wrong answer.

The C writes the descending loop. The Python writes it as one NumPy statement,
`counts[prime:] += counts[:-prime]`, where source and destination overlap. NumPy detects the overlap
and reads the whole source before writing, which is exactly the "old values" semantics of the
descending loop (see [NumPy slice assignment](/topics/technique/numpy-slice-assignment)). In pure
Python, the slice-free equivalent `for s in range(p, S + 1)` would be the unbounded version and
silently wrong.

**938, exhausting a colour: wavefront with two buffers.** The probability $P(r, b)$ of an
[absorbing Markov chain](/topics/technique/absorbing-markov-chain) satisfies
$P(r, b) = \alpha\,P(r - 2, b) + (1 - \alpha)\,P(r, b - 1)$. Indexing even $r$ by $j = r/2$, both
predecessors lie on the previous anti-diagonal $d - 1$ of the $(j, b)$ grid. So the solution keeps
two arrays of length $R/2 + 1$, `prev` and `cur`, fills `cur` from `prev`, and swaps them. Memory is
$O(R)$ instead of the $O(RB)$ table. Note that a *single* array would also work. Storing the diagonal by
$j$, the new value at $j$ reads old values at $j - 1$ and $j$, so a sweep in **descending** $j$ never
reads a slot it has already overwritten. That is the 249 trick again. The solutions choose the two-buffer
form for clarity, which costs one more array.

## Python and C

- **81**: identical algorithms. Python generates the coordinates lazily from a generator. C fills
  two coordinate arrays first, then sweeps. Both mutate the parsed matrix, so the input is consumed.
  If you needed the grid again you would copy it first.
- **249**: the clearest contrast on this page. C's explicit `for (s = total; s >= prime; s--)` is
  correct *by visible direction*. Python's vectorised slice is correct *by NumPy's overlap rule*. That is
  an implicit contract, so the solution states it in a comment. Both keep counts in `uint64` and reduce
  mod $10^{16}$ only every ten primes, because each pass at most doubles a value and
  $10^{16} \cdot 2^{10} < 2^{64}$.
- **938**: both swap two buffers per diagonal. NumPy evaluates each diagonal as one vectorised
  convex combination, while C uses a scalar loop. There is a small trap in the Python: at $j = 0$ it
  reads `prev[j - 1]`, which is `prev[-1]` and wraps around to the *last* element. The boundary
  override `cur[0] = 1.0` then hides it. The C guards it explicitly with `(j >= 1) ? prev[j - 1] : 0.0`.
  The in-place version would have to keep that boundary handling correct.

## How to reason about it

- **List the reads of each update.** For each one, ask whether it should see the old or the new value,
  then choose the sweep direction that delivers it.
- **Descending for "use once", ascending for "use any number of times".** This rule covers every
  one-array knapsack.
- **Vectorised updates read before writing.** A NumPy expression with overlapping slices behaves like a
  copy of the source. That is right for 0/1-style updates, but cannot express a recurrence that should
  see the new values within the same pass.
- **Mutating the input is a contract.** Overwriting the matrix (81) is fine in a single-use solver, but
  copy it if the caller needs the data again.
- **Two buffers are the safe default.** When the order is subtle, two rolling arrays with a swap give
  most of the memory saving with no ordering risk.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0938](/solutions/0938/) — Exhausting a Colour

<!-- /problems -->
