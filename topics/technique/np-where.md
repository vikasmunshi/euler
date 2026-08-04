<!-- tags: [np-where] -->
<!-- status: final -->
# np.where

[`np.where`](https://numpy.org/doc/stable/reference/generated/numpy.where.html) is the
vectorized `if`. Once a computation has been rewritten so its loop runs in compiled code
([vectorized computation](/topics/technique/vectorized)), a per-element `if` is no longer
available — there is no interpreter left to branch in. `np.where(cond, a, b)` is what replaces
it: the arithmetic for *both* outcomes happens, and a boolean mask decides, elementwise, which
one survives. That trade — do all the work, keep some of it — is what lets a conditional
algorithm stay in array form.

## The idea

The three-argument form broadcasts `cond`, `a` and `b` against each other and returns a new
array whose element `i` is `a[i]` where `cond[i]` is true and `b[i]` otherwise. It is a
**select**, not a branch: `a` and `b` are ordinary array expressions, fully evaluated before
`np.where` ever looks at the mask. The hardware analogue is a
[conditional move](https://en.wikipedia.org/wiki/Predication_(computer_architecture)) rather
than a jump, and the cost model follows from that one fact.

Two shapes account for nearly every use.

**Select which lanes act.** When many independent computations share one update rule, make them
an axis of an array and step them in lockstep — but the rule usually has a conditional in it,
and that conditional differs per lane. `np.where` is the join. The clearest case is
[modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation) run over a whole
vector of bases and moduli at once: the
[square-and-multiply](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) schedule is
data-independent, so every lane walks the same bits, and only the multiply is conditional.

```python
result = np.ones_like(modulus)
factor = base % modulus
while remaining.any():
    result = np.where(remaining & 1, result * factor % modulus, result)
    factor = factor * factor % modulus
    remaining >>= 1
```

Every lane executes every iteration; the mask decides who keeps the multiply. That is
roughly 64 array operations in place of one interpreted `pow` per element, and it is how
[problem 421](/solutions/0421/) evaluates $n^{15} \bmod p$ across an array of candidate primes
without ever leaving NumPy. The generalisation is worth naming: **any bounded,
data-independent iteration can be unrolled across the array, with a mask selecting which lanes
participate.**

**Mask to a reduction's identity.** The other shape is filtering that must *not* shrink the
array. [Problem 565](/solutions/0565/) needs a prefix sum over only those primes passing a
divisibility test, and reaches for the neutral element instead of a filter:

```python
g = np.where((primes + 1) % d == 0, np.int64(0), primes)
prefix = np.cumsum(g)
```

Zero is the identity for addition, so the failing primes contribute nothing to the running
total — and, crucially, `prefix` still has one entry per prime, in the original order. That
alignment is the entire reason not to compact: a
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
on `primes` indexes straight into `prefix`, which a filtered array would have made impossible.
The same move works for any reduction with an identity: `1` before a product, `-inf` before a
running maximum.

A third, smaller shape recurs too: carrying a *running best* alongside its bookkeeping. Compute
one `better` mask, then apply it with a separate `np.where` to the value and to every array
that records where the value came from, so value and index can never drift apart — the
vectorized [arg max](/topics/technique/arg-max).

Finally, the **one-argument** form `np.where(cond)` is a different function wearing the same
name: it returns the indices where `cond` is true, and is documented as equivalent to
[`np.nonzero`](https://numpy.org/doc/stable/reference/generated/numpy.nonzero.html). Prefer
`np.nonzero` or `np.flatnonzero` when that is what you mean; the single name for two unrelated
operations is a genuine readability trap.

## How to reason about it

- **Both arms are always evaluated.** `np.where(x != 0, 1 / x, 0)` divides by zero for every
  zero element — the warning fires and the `inf` is produced, and only then discarded. Guard
  the *input*, not the output: clamp the denominator, or use a ufunc's `where=`/`out=` pair
  ([`np.divide`](https://numpy.org/doc/stable/reference/generated/numpy.divide.html)), which
  genuinely skips the masked elements.
- **Overflow hides in the arm you throw away.** The discarded branch still runs in fixed-width
  `int64`, and NumPy overflow wraps **silently**. A product that would only have been safe on
  the selected lanes is computed on all of them, so bound the intermediates for the whole
  array. See [watch integer width](/topics/takeaway/watch-integer-width).
- **Pin the dtype of scalar arms.** `np.where` applies NumPy's promotion rules to all three
  arguments, so a bare Python `0` can quietly decide the result's width. Writing `np.int64(0)`
  — as both problems here do — or an explicit `.astype` afterwards keeps the output dtype a
  decision rather than an accident.
- **It is a select, so it is never cheaper than doing both branches.** It wins only because the
  alternative is an interpreted loop. When one arm is both expensive and rare, do not select —
  compute it on the subset (`arr[mask]`) and scatter the results back.
- **It always allocates.** If you are only writing one arm, boolean assignment `a[mask] = v` (or
  [`np.putmask`](https://numpy.org/doc/stable/reference/generated/numpy.putmask.html)) mutates
  in place and skips the temporary. Inside a loop over bits or chunks that allocation is
  measurable.
- **Do not use it to filter.** `np.where` preserves shape — the point when alignment matters,
  the wrong tool when you want fewer elements. That is boolean indexing or `np.flatnonzero`.
- **Past two branches, use
  [`np.select`](https://numpy.org/doc/stable/reference/generated/numpy.select.html).** Nested
  `np.where` becomes unreadable quickly and still evaluates every arm. And check first whether
  a dedicated ufunc says it better: many a `np.where` is `np.clip`, `np.minimum`, `np.sign` or
  `np.copysign` spelled the long way.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors

<!-- /problems -->
