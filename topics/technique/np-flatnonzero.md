<!-- tags: [np-flatnonzero] -->
<!-- status: final -->
# np.flatnonzero

[`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html)
turns a boolean mask into the sorted array of positions where it is true. That one conversion
recurs because NumPy solutions keep two representations of the same set: a **mask**, indexed
by the number itself, which is what a sieve writes and what membership tests read; and a
**list of members**, dense and short, which is what the next stage wants to loop or vectorize
over. Every problem below crosses from the first to the second at least once, and nearly all of
them cross at the same place: the moment a sieve finishes.

## The idea

For an array `a`, `np.flatnonzero(a)` is `np.nonzero(np.ravel(a))[0]` — the indices of the
non-zero entries of the flattened array, ascending, as a single `intp` array rather than the
tuple `np.nonzero` returns. On a 1-D mask it is the same as one-argument `np.where(mask)[0]`,
without the tuple to unpack. Because a sieve indexes by value, *the index is the value*:

```python
sieve[i * i::i] = False          # mask, written by slice assignment
primes = np.flatnonzero(sieve)   # members: 2, 3, 5, 7, ...
```

That is the canonical shape, and seven of the eight problems here
([133](/solutions/0133/), [134](/solutions/0134/), [214](/solutions/0214/),
[216](/solutions/0216/), [357](/solutions/0357/), [429](/solutions/0429/),
[565](/solutions/0565/)) use it verbatim to read the primes off a
[sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes). The mask is written by
[slice assignment](/topics/technique/numpy-slice-assignment); `flatnonzero` is the read that
follows it. The cost is one linear pass to count and one to fill, so it is the same order as
the sieve itself and never the bottleneck.

The predicate does not have to be stored. [Problem 23](/solutions/0023/) builds it on the fly
from a divisor-sum array, twice:

```python
abundant_numbers = np.flatnonzero(div_sums > np.arange(limit + 1))
...
non_abundant_sums = np.flatnonzero(~is_abundant_sum)
```

The first line compacts "aliquot sum exceeds the number" into the few thousand abundant
numbers, so the pairwise-sum loop that follows ranges over those instead of all 28 123
integers; the second turns the complement mask back into the numbers to sum.

## Doing arithmetic on the indices

Once the indices are an array, they are ordinary integers and can be shifted, filtered and fed
back into the mask:

- **Shift to a derived set.** Problem 357 wants $n$ with $n + 1$ prime, so its candidates are
  `np.flatnonzero(sieve) - 1` — every candidate in one expression, no scan.
- **Gather back.** The same solution then tests `sieve[2 + candidates // 2]`: the index array
  goes back *into* the mask as a [fancy index](/topics/technique/fancy-indexing), reading one
  flag per candidate. Mask → indices → gather is the round trip that keeps a filter pipeline in
  [array form](/topics/technique/array-programming).
- **Find run boundaries.** Problem 429 has a non-increasing array `k = n // primes` that takes
  few distinct values, and wants to process each run of equal `k` in bulk.
  `np.flatnonzero(np.diff(k) != 0) + 1` is the start of every run after the first — the
  classic "where does it change" idiom, and the one use here that is not about a sieve.
- **Intersect predicates first.** Problem 214 combines masks before compacting,
  `np.flatnonzero(is_prime & (chain == length))`, so only the final members are ever
  materialized.

## How to reason about it

**Compact when the next stage is per-member; don't when it must stay aligned.** The list is
the right shape for a loop over members, for gathering, or for reductions over members only.
When a later step needs one entry per *original* position — a prefix sum to be searched by
index, say — compacting destroys the alignment, and the answer is a masked select instead; the
[np.where](/topics/technique/np-where) page shows exactly that choice on problem 565, which
itself compacts its sieve with `flatnonzero` a few lines earlier. Both moves live in the same
solution because they answer different questions.

**Mind the dtype.** The result is `intp`: 64-bit on the Linux machines these run on, but 32-bit
on Windows before NumPy 2.0. Problems 429 and 565 add `.astype(np.int64)` because the indices
go straight into products and modular arithmetic; that cast is cheap insurance whenever indices
become operands rather than subscripts.

**`.tolist()` when Python takes over.** Problems 134, 214 and 357 hand the primes to an
interpreted loop, and convert first. Iterating a NumPy array yields NumPy scalars — slower to
touch than Python `int`s, and fixed-width, so they wrap where a Python `int` would not.
`np.flatnonzero(sieve).tolist()` is the idiomatic handover from the
[vectorized](/topics/technique/vectorized) half of a solution to the scalar half.

**Index 0 is a position too.** `~is_abundant_sum` in problem 23 is true at 0, so 0 lands in
the result; it is harmless under a sum, but a product, a count, or a division over the same
array would see it. Clear the out-of-range slots in the mask (`sieve[:2] = False`) before
compacting, not after.

## C and Python

The C translations never build the list. In C the loop over the mask *is* the fast path, so
the natural form is to walk the flags and act inline —

```c
for (long long i = 2; i <= limit; i++) {
    if (!sieve[i]) continue;
    /* ... use i as a prime ... */
}
```

— and problem 23's C side appends to a preallocated `int` array only because its pairwise loop
needs random access to the abundant numbers. `flatnonzero` exists to move that scan out of the
interpreter, which C has no need of; the price NumPy pays is a fresh allocation the size of the
member set, where C can usually skip the copy. The other half of the family is on the
[NumPy](/topics/technique/numpy) page.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors

<!-- /problems -->
