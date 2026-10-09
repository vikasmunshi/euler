<!-- tags: [monotonic-function] -->
<!-- status: final -->
# Monotonic function

A [monotonic function](https://en.wikipedia.org/wiki/Monotonic_function) is one that never changes
direction: as $x$ grows, $f(x)$ only ever goes up (non-decreasing) or only ever goes down
(non-increasing). Stated like that it sounds like a property you would *check*, not one you would
*use*. In practice it is the opposite. Monotonicity is a licence to stop looking: it says that what
is true at one point is true for everything beyond it, so a single evaluation can rule out an
entire range. Every problem below is too big to enumerate, and every one becomes tractable at the
moment its author notices that some quantity only moves one way.

## The idea

If $f$ is non-decreasing and $a \le b$, then $f(a) \le f(b)$. Everything on this page is a
consequence of that one inequality, used in one of three ways.

**1 — Compare through it.** A strictly increasing $g$ preserves order: $x < y \iff g(x) < g(y)$. So
when two quantities are awkward to compare directly, compare their images instead. Problem 99 asks
which of a thousand pairs $b^e$ is largest, where each number has millions of digits. The
[logarithm](/topics/technique/logarithm) is strictly increasing, so ranking $e \ln b$ ranks $b^e$ —
one multiplication per line instead of a bignum power:

```python
# log(base^exponent) = exponent * log(base): order-preserving and computable in O(1).
log_val = exponent * math.log(base)
```

Problem 800 uses the same surrogate the other way round: the condition $p^q q^p \le N$ becomes
$q \ln p + p \ln q \le \ln N$, a comparison of small floats instead of astronomically large
integers. The surrogate only has to be monotone; it does not have to be exact.

**2 — Search through it.** A monotone function turns "find where $f$ crosses a target" into a
predicate $f(n) \ge t$ that is false, false, …, false, true, true, … — exactly the shape
[binary search](/topics/technique/binary-search-algorithm) needs. This is the commonest use here:

- Problem 305 defines $C(N)$, the number of occurrences of a string that start inside one of the
  integers $1 \dots N$ of the concatenated sequence. Writing more integers never removes an
  occurrence, so the integer holding the $n$-th occurrence is the least $N$ with $C(N) \ge n$, and
  binary search finds it in $O(\log N)$ evaluations of a closed-form $C$.
- Problem 587 needs the least $n$ at which an area ratio $\rho(n)$ drops below a threshold. The
  ratio is decreasing in $n$, but no upper bound on $n$ is given, so the search first *brackets*
  the crossing by doubling — [exponential search](/topics/technique/exponential-search) — and then
  bisects inside the bracket.
- Problem 235 solves for the real ratio $r$ of a partial sum $s(r)$ that equals a target. On the
  relevant side of $r = 1$ the sum is monotone in $r$, so the [bisection method](/topics/domain/bisection-method)
  converges from the *sign* of $s(r) - \text{target}$ alone — no derivative, no divergence, and the
  sign is the one quantity floating-point noise cannot plausibly flip.
- Problem 800, again: fix the smaller prime $p$ and $q \ln p + p \ln q$ is increasing in $q$, so
  each $p$ has a single cut-off partner, found by a binary search over the primes. (Because the
  cut-off itself moves monotonically as $p$ grows, a [two-pointer](/topics/technique/two-pointer-technique)
  sweep would do it in one pass too.)

**3 — Prune through it.** The strongest form. If $f$ is non-decreasing on $[lo, hi]$, then two
evaluations at the endpoints bound $f$ on the whole interval:

$$f(lo) \le f(n) \le f(hi) \quad \text{for every } n \in [lo, hi].$$

Problem 156 wants every *fixed point* $f(n, d) = n$ of the [digit-counting function](/topics/domain/digit-counting-function)
below $10^{12}$ — not one crossing but all of them. Writing one more number never lowers a digit
tally, so $f(\cdot, d)$ is non-decreasing, and the endpoint bound kills whole intervals at once:

- if $f(lo, d) > hi$, then $f(n, d) \ge f(lo, d) > hi \ge n$ throughout — no fixed point;
- if $f(hi, d) < lo$, then $f(n, d) \le f(hi, d) < lo \le n$ throughout — none either.

Surviving intervals are halved and re-tested. Because $f(n, d) - n$ is near zero only in a few
narrow bands, almost all of the tree dies at shallow depth: a [branch-and-bound](/topics/technique/branch-and-bound)
search whose bound is nothing more than monotonicity. Problem 247 prunes the same way in geometry —
squares packed under a hyperbola shrink as you descend the region tree, so once a square is below
the size threshold everything beneath it is too, and the depth-first walk cuts the subtree.

Problem 168 is the loop-sized version: a candidate $m(t)$ is strictly decreasing in a digit $t$, so
the first $t$ that drops $m$ below its digit-length floor ends the loop with a `break`.

## How to reason about it

**Look for the quantity that only accumulates.** Counts over a prefix ("how many … among
$1 \dots N$"), cumulative sums of non-negative terms, areas swept out, sizes that shrink as you
recurse — these are monotone by construction, and the proof is usually one sentence ("adding an
element never removes a match"). If you can say that sentence, you can probably binary-search or
prune.

**Monotone in which variable?** Problem 800's expression is monotone in $q$ *with $p$ fixed*; the
search must be organised around that. Look for a variable to freeze that makes the remainder
one-directional.

**The break-versus-continue trap.** Monotonicity justifies stopping only in the direction it
points. Problem 168 makes this concrete: as $t$ grows, the candidate $m$ and the derived $n$
*both* shrink. "$m$ is too small" therefore stays true for every larger $t$ — `break`. But "$n$ is
too large" can become false for a larger $t$ — that test must `continue`. Swap them and the loop
silently undercounts. Before writing a `break`, say aloud which way the function moves and which
side of the threshold you are on.

**Non-decreasing is not strictly increasing.** A step function such as $C(N)$ or $f(n, d)$ has
flat runs, so "the $n$ with $f(n) = t$" may not exist or may not be unique. Phrase the search as
"least $n$ with $f(n) \ge t$" and binary search returns a well-defined answer; phrase it as
equality and it can miss.

**Know your bracket.** Bisection needs an interval whose ends lie on opposite sides of the target.
When the problem does not hand you one, bracket by doubling (587, 235), or derive a crude growth
bound — 156 argues that $f(n, d) \approx Dn/10$ for $D$-digit $n$, which outruns $n$ past twelve
digits, so $10^{12}$ is a safe ceiling.

**Floats and surrogates.** A log surrogate is monotone in exact arithmetic but rounded in
[floating point](/topics/technique/floating-point-arithmetic). Ties and near-ties — two pairs
whose logs agree to the last ulp — are where a surrogate comparison can lie. For problem 99 the
margins are comfortable; when they are not, confirm the boundary cases in exact integer arithmetic.

The unifying instinct: **when a search space is too large to walk, ask what only moves one way.**
That quantity is the axis along which you can stop early, halve, or discard whole ranges unseen.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0099](/solutions/0099/) — Largest Exponential
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0800](/solutions/0800/) — Hybrid Integers

<!-- /problems -->
