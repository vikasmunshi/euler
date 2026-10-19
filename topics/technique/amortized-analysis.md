<!-- tags: [amortized-analysis] -->
<!-- status: final -->
# Amortized analysis

[Amortized analysis](https://en.wikipedia.org/wiki/Amortized_analysis) bounds the *total*
cost of a sequence of operations rather than the worst case of each one. Some operations are
expensive, such as a resize, a rebuild or a long pointer chase. If they are rare enough, or each one
makes later operations cheaper, the average per operation is small, and it is *guaranteed* to be
small over any long sequence. This is how you justify an algorithm whose worst single step looks
alarming. The three solved problems below rely on the three classic arguments: a data structure
that repairs itself as it is used (186), a buffer that doubles (710), and a rebuild that is
expensive but improbable (816).

## The idea — charge the expensive steps to the cheap ones

There are three standard ways to make the argument:

- **Aggregate.** Bound the total work of $n$ operations directly and divide by $n$. Doubling a buffer
  from 1 to $n$ copies $1 + 2 + 4 + \dots < 2n$ elements in total, so each append is $O(1)$ amortized.
- **Accounting or potential.** Give each cheap operation a small surcharge, stored as credit or potential,
  that pays for the later expensive one. Path compression in union-find is analysed this way: every
  long walk flattens the tree and lowers the potential that later finds would spend.
- **Expected amortized.** When the expensive step is triggered by chance, multiply its cost by its
  probability. A rebuild costing $O(i)$ that happens with probability $O(1/i)$ contributes $O(1)$ in
  expectation, and summed over $n$ steps that is $O(n)$. The standard proof is *backwards analysis*:
  look at step $i$ in reverse and ask how likely the last element added was the one that changed the answer.

What amortization does **not** promise is a bound on any single operation. That rarely matters in a batch computation,
and it is the reason a benchmark that times only the steady state can mislead.

## Three arguments across the problems

**186, connectedness of a network: union-find, self-repairing.** Calls join users, and the question is
when the Prime Minister's component reaches 99% of a million users. A
[disjoint-set](/topics/technique/disjoint-set-data-structure) forest answers "same component?" and
"merge" with two refinements. *Union by size* attaches the smaller tree under the larger, which keeps
the height at $O(\log n)$. *Path compression* re-points every node on a `find` path directly at the
root. Either alone gives logarithmic amortized cost. Together they give $O(\alpha(n))$ per operation
([inverse Ackermann](https://en.wikipedia.org/wiki/Ackermann_function#Inverse), at most 4 for any
realistic $n$). A single `find` can still walk a long path, but it pays for itself by shortening the
path for everyone after it.

**710, one million members: growing arrays.** The scan over $n$ needs four count arrays indexed up to
$n/2$, and the answer's size is not known in advance. Each array grows on demand, so every index is
computed exactly once and each step of the scan extends the arrays by at most one entry. Python's
`list.append` over-allocates proportionally (CPython adds about 1/8 plus a constant), and C
`realloc`s to *double* the capacity whenever `need >= cap`. Both are the
[dynamic array](/topics/technique/dynamic-array) argument. A resize copies everything, but
resizes are geometrically spaced, so the total copying is linear and the scan is $O(N)$ overall.
The point to get right in C is growing by a *factor*. Growing by a constant, say `cap += 64`, makes the
total copying quadratic.

**816, shortest distance among points: expected rebuilds.** Two million generated points are
inserted one at a time into a grid whose cell side is the current closest distance $\delta$, so each
insertion checks only the 3 × 3 neighbouring cells. When a new point beats $\delta$, the grid is
**rebuilt** at the finer size, which is $O(i)$ work. By backwards analysis, when points arrive in random order the $i$-th point is one of the
closest pair among the first $i$ with probability at most $2/i$. So the expected rebuild cost per step is
$O(i) \cdot 2/i = O(1)$, and the whole run is expected $O(k)$. This is a
[randomized incremental algorithm](/topics/technique/randomized-incremental-algorithm). The
pseudorandom generator provides the random order, but an adversarial order would make it quadratic.

## Python and C

- **186**: the two `find`s are the same two-pass loop: walk to the root, then walk again re-pointing.
  Python's second pass is `parent[x], x = root, parent[x]`. That works because the right side is
  evaluated first and the targets are assigned left to right, so `parent[x]` is written with the
  old `x` before `x` advances. Swap the targets and it breaks. C uses an explicit `next` temporary.
  Neither recurses, so path length never meets a recursion limit.
- **710**: Python lists grow implicitly. C grows four arrays together with `realloc`, doubling `cap` until the needed index fits.
- **816**: the rebuild is where the languages differ most. Python rebuilds by assigning a fresh `dict`
  and re-appending tuples. C sizes a chained hash table once, to the next power of two at or above
  $2k$, so a rebuild is a `memset` of the head array plus a linear refill of a preallocated node
  array. No allocation happens per rebuild, which keeps the constant factor of the "expensive" step low.

## How to reason about it

- **Total cost, not worst step.** If an operation is occasionally $O(n)$, ask how often it can happen,
  and whether each occurrence makes later operations cheaper.
- **Grow by a factor.** Doubling, or any constant ratio above 1, gives $O(1)$ amortized appends.
  Additive growth gives $O(n)$ per append.
- **Use both union-find refinements.** Union by size and path compression together are effectively
  constant time. Leaving out either is a common source of slow solutions.
- **Randomized amortization needs randomness.** The expected-$O(1)$ rebuild argument (816) assumes
  random order. If the input could be sorted or adversarial, shuffle it first.
- **Make the expensive step cheap in absolute terms too.** Preallocate, and reset with `memset`
  rather than freeing and reallocating, so the rare $O(n)$ step has a small constant.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0186](/solutions/0186/) — Connectedness of a Network
- ● [0710](/solutions/0710/) — One Million Members
- ● [0816](/solutions/0816/) — Shortest Distance Among Points

<!-- /problems -->
