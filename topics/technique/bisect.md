<!-- tags: [bisect] -->
<!-- status: final 2026-10-29T12:12Z -->
# bisect

Python's [`bisect`](https://docs.python.org/3/library/bisect.html) module does one job. Given a
sorted list and a value, it says where the value *would go*. That "would go" is the useful part. The
insertion point is not a yes/no membership test: it is a **count**, the number of elements below
(or at most) the value. Once you read it as a count, a sorted list together with `bisect` becomes a
counting function, a range cutter and a "which bucket holds item $n$?" locator. The solutions
below use it in exactly those three roles. The general algorithm (invariants, searching over the
answer, bracketing) is covered on the [binary search](/topics/technique/binary-search-algorithm)
page. This page is about the library call and the sorted-table habits that make it pay.

## The idea — an insertion point is a count

For a sorted list `xs`:

| call | returns | read it as |
|---|---|---|
| `bisect_left(xs, x)` | first index `i` with `xs[i] >= x` | how many elements are $< x$ |
| `bisect_right(xs, x)` | first index `i` with `xs[i] > x` | how many elements are $\le x$ |
| `bisect_right(xs, x) - 1` | last index with `xs[i] <= x` | the bucket that contains `x` |

Both calls take optional `lo` and `hi` bounds that restrict the search to `xs[lo:hi]` without
copying the slice. Each call costs $O(\log n)$ comparisons. Because the comparisons run in C, a
`bisect` call on a list of a million `int`s costs about as much as a few lines of Python
arithmetic, which is why reaching for it in a hot loop is not a mistake.

Most errors here come from picking the wrong side. The rule I use: pick the call by which
inequality the *question* uses. "Primes $\le N$" is `bisect_right`. "Primes $\ge 5$" starts at
`bisect_left(primes, 5)`. Half-open ranges `[bisect_left(lo), bisect_right(hi))` compose without
gaps or overlaps.

## Three roles across the problems

**Cutting a range out of a sorted table (problem 134).** The solution sieves primes once into a
sorted list, then needs every consecutive pair $(p_1, p_2)$ with $5 \le p_1 \le N$. Two calls frame
the loop:

```python
start = bisect_left(PRIMES, 5)          # first prime >= 5
end   = bisect_right(PRIMES, max_limit) # one past the last prime <= limit
for i in range(start, end): ...         # PRIMES[i + 1] is p2, so the sieve overshoots the limit
```

`bisect` does almost no work here. What it gives is clarity: the bounds read as the problem
states them, and the half-open `end` already points one past the last $p_1$, which is what makes
`PRIMES[i + 1]` safe as long as the sieve runs a little past the limit.

**A counting function over a prefix-sum table (problem 272).** The solution sums $n \le L$ whose
count of cube roots of unity modulo $n$ is fixed. A DFS chooses all but the last prime factor. The
last factor, which is a large prime $p \equiv 1 \pmod 3$, is batched by $q = \lfloor t/p \rfloor$,
so each batch needs "the sum of good primes in $(lo, hi]$". The solution keeps the good primes
sorted next to their [prefix sums](/topics/technique/prefix-sum), so each batch is two lookups:

```python
good_sums[bisect_right(good_primes, hi)] - good_sums[bisect_right(good_primes, lo)]
```

`bisect_right(good_primes, x)` is the prime-counting function $\pi(x)$ restricted to the good
residue class. It doubles as an index into the prefix-sum array, so a sum over a range of primes
becomes a subtraction. This is the pattern I reach for most: **sorted keys + prefix sums + bisect =
$O(\log n)$ range aggregates over a sparse set.**

**The same pattern, with the bound doing the varying (problem 516).** This problem sums the
$n \le L$ whose totient is 5-smooth. Such an $n$ splits as $m \cdot h$, where $h$ is a
[Hamming number](https://en.wikipedia.org/wiki/Regular_number) and $m$ is a squarefree product of
primes $q > 5$ with $q - 1$ itself 5-smooth. Fix $m$, and its contribution is $m$ times the sum of
every Hamming number $\le L/m$. The Hamming numbers are the sparse key set: there are only a few
thousand below $10^{12}$, far too few to index an array by value, but a sorted list of them and its
prefix sums answer each $m$ with a single call:

```python
total += m * prefix[bisect_right(hamming, limit // m)]
```

Next to 272 two things change. The query is a prefix, not a range, so it takes one lookup instead of
two. And what varies from query to query is the cut-off $L/m$, not a bucket of primes. The general
shape: when a sum over $n \le L$ factors into an outer enumeration over $m$ and an inner sum over a
sorted set up to $\lfloor L/m \rfloor$, the inner sum is one bisect into a prefix-sum array.

**Finding the bucket that holds item $n$ (problem 943).** The solution computes prefix sums of a
self-describing (Kolakoski-like) sequence by walking down a memoised derivation tree. At each level
it must skip every whole child subtree that lies before the $n$-th leaf. When a node has many
same-valued children, their leaf counts are stored as a cumulative array `cum_l`, and the child
that contains the target is `bisect_right(cum_l, need) - 1`, the third row of the table above.
There is an extra wrinkle. The children's masks repeat with period $p$ after a prefix of length
$\mu$ (found by [cycle detection](/topics/technique/cycle-detection)), so the stored array covers
only the first period. Past that, the solution divides off whole periods and bisects inside one
period using the `lo`/`hi` bounds:

```python
q, rem = divmod(need - cum_l[mu], period_len)
k = bisect_right(cum_l, cum_l[mu] + rem, mu, mu + p + 1) - 1 + q * p
```

So the arithmetic jumps across repeated periods, and `bisect` finds the position within one
period. The `lo`/`hi` window keeps the search off the non-periodic prefix.

## The C side — there is no `bisect`

C's standard library has [`bsearch`](https://en.cppreference.com/w/c/algorithm/bsearch), but it
returns a pointer to *a* matching element or `NULL`. It gives no insertion point and no count, and
it makes no promise about which duplicate it returns. None of the uses above fits, so the C
twins handle it in their own ways:

- **Problems 272 and 516** each write a five-line `bisect_right`, the textbook `lo < hi` loop with
  `if (a[mid] <= x) lo = mid + 1; else hi = mid;`, over the prime array and the Hamming array
  respectively. 516's carries the comment "number of elements of a[0..n) that are ≤ x", which is
  the count reading from the table above. It is the same algorithm, so the two languages keep the
  same complexity.
- **Problem 943** writes a `bisect_right(cl, x, lo, hi)` that copies Python's signature, `lo`/`hi`
  included, over `__int128` cumulative counts. Keeping the signature lets the two descent loops
  stay line-for-line comparable.
- **Problem 134** does not bisect at all. It finds `start` and `end` with linear `while` scans.
  That is a real difference in algorithm, but a harmless one: the main loop then walks every prime
  in `[start, end)` anyway, so an $O(\pi(N))$ scan is free next to it. The C version also hard-codes
  its sieve size (`SIEVE_LIMIT`), where the Python version sieves to a module-level bound.

The lesson across them: bisection is worth a hand-written helper in C when the lookup sits inside
the hot loop (272's per-batch prime sums, 516's per-product prefix lookup, 943's per-level descent). When it only frames a loop
that is linear anyway, a scan is just as fast and has no off-by-one risk. When you write the
helper, write `bisect_right` (or `_left`) with half-open `[lo, hi)` semantics and comment which
one it is, as the C files do. Then a reader can check it against the Python call it mirrors.

## How to reason about it

- **Store sorted, query many times.** `bisect` pays off when one sort or sieve serves thousands of
  lookups. If you insert while querying, `insort` is $O(n)$ per insert, because the list shifts. At
  that point you want a balanced tree, a [Fenwick tree](/topics/technique/fenwick-tree) or an
  offline sort of the queries.
- **Pair it with a prefix-sum array** whenever the question is "sum/count of the keys in a range"
  or "below a cut-off". The insertion point is already the right index into the prefix array. A
  sum that splits as $n = m \cdot h$ with $h \le L/m$ is the cut-off case: one bisect per $m$.
- **Use `bisect_right(...) - 1` for "which bucket"** over cumulative sizes, and settle what
  happens when the target lands exactly on a boundary. In 943 that boundary means "this child is
  wholly skipped", which is why the code uses `_right` rather than `_left`.
- **Use `lo`/`hi`, not slices.** `xs[a:b]` copies the slice. The bounds arguments do not.
- **In C, decide whether you need it at all.** A linear scan next to an $O(n)$ loop is fine. A
  bisect inside one needs a helper, and that helper should match Python's semantics exactly.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0943](/solutions/0943/) — Self Describing Sequences

<!-- /problems -->
