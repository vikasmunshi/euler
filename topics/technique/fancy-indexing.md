<!-- tags: [fancy-indexing] -->
<!-- status: final -->
# fancy-indexing

NumPy has two kinds of subscript. A slice `a[lo:hi:step]` selects a regular stride and returns a
view. An **array** subscript, either a list of positions or a boolean mask, selects any set of
elements and returns a **copy**. NumPy calls the second kind
[advanced indexing](https://numpy.org/doc/stable/user/basics.indexing.html), and everyone else calls
it fancy indexing. It is how a vectorised solution handles a lookup whose address is *computed*: a
sieve value read at $k(g - k)$ for a whole range of $k$, a mark written at $a^2 + c$ for a whole
range of $a$. Those are the cases a slice cannot express. This page covers the idiom itself:
gather, scatter, and mask, and the copy semantics behind all three. The rest of the family is on
[numpy](/topics/technique/numpy), [array programming](/topics/technique/array-programming),
[NumPy slice assignment](/topics/technique/numpy-slice-assignment) and
[np.flatnonzero](/topics/technique/np-flatnonzero).

## The idea

Fancy indexing takes one of two kinds of index. Each can be used to read or to write:

| | read (gather) | write (scatter) |
| --- | --- | --- |
| **integer array** `idx` | `out = a[idx]`: `out[i] = a[idx[i]]` | `a[idx] = v`: `a[idx[i]] = v[i]` |
| **boolean mask** `m` | `a[m]`: the `a[i]` with `m[i]` true, in order | `a[m] = v`: write where `m` is true |

A boolean mask is shorthand for `a[np.flatnonzero(m)]`, so the two kinds are the same operation.
The thing to remember is **copy, not view**. `a[idx]` allocates a new array. Writing to that new
array does not change `a`, so `a[idx][0] = 1` silently does nothing. Writing *through* the subscript
(`a[idx] = …`, `a[idx] += …`) does reach `a`. But the compound form is a buffered
read-modify-write. If `idx` repeats a position, `a[idx] += 1` adds once, not once per repeat. When
that matters, the correct tools are `np.add.at` or `np.bincount`; see
[slice assignment](/topics/technique/numpy-slice-assignment).

## Gather: a table read at computed positions

Problem 420 counts $2 \times 2$ matrices with two square roots. Both of its solutions reduce the
count to sums of a divisor-count table $\tau$ (built with a strided slice, `tau[i::i] += 1`) read at
positions that come from a formula. Solution 1 needs $\sum_k \tau\bigl(k(g - k)\bigr)$ over a range
of $k$. Solution 0 needs $\sum_f \tau\bigl((g^2 - f^2)/4\bigr)$ over $f$ of one parity. The vector
form is: build the index array with array arithmetic, gather, and reduce:

```python
ks = np.arange(k_min, k_max + 1, dtype=np.int64)
cnt += int(numdivs[ks * (g - ks)].sum())
```

The positions $k(g - k)$ rise and then fall, so no stride could produce them. Only a gather can. Both
solutions keep a **scalar fallback** for short ranges (fewer than 16 or 20 terms). Each fancy
index allocates two temporary arrays and pays for a few NumPy calls. For a range of three or four
values, a Python loop of plain `tau[w]` reads is faster. A vector call has a fixed overhead, so
use it once the range is long enough to pay that back.

## Scatter: marking computed positions

Problem 229 counts $n$ that are simultaneously $a^2 + b^2$, $a^2 + 2b^2$, $a^2 + 3b^2$ and
$a^2 + 7b^2$ with $a, b \ge 1$. Each form becomes a boolean mask over $[0, N]$, written one $b$ at a
time:

```python
a = np.arange(a_min, a_max + 1, dtype=np.int64)
mark[a * a + c] = True          # c = d * b * b
```

Plain assignment is safe with duplicates, since writing `True` twice is still `True`. That is why a
scatter of marks is simpler than a scatter of counts. Two practical points come from the access
pattern. First, the positions $a^2 + c$ spread further apart as $a$ grows, so the writes jump through
memory. The solution therefore **cache-blocks** the work: it walks output windows of 32 million
entries and, inside each, writes only the $a$ whose squares land there. That also keeps each index
array the size of one window rather than the whole range. Second, `a_min` and `a_max` are computed
with `isqrt` from the window bounds. The index array never holds an out-of-range position, because
a fancy index raises `IndexError` on one, where C would write past the end.

## Mask: selecting by a predicate

A boolean subscript filters. Problem 249 runs a subset-sum knapsack over the primes below 5000,
then needs the total of the coefficients at **prime** positions. The sieve it already has supplies
the selector:

```python
return str(modular_total(counts[prime_flags(total)]))
```

`counts[mask]` gathers the prime-indexed entries into a short array, which is then summed in chunks
small enough not to wrap `uint64`. Problem 421 uses a mask to **partition** rather than to filter:
`primes[(has_cubics == wants_cubics) & (has_quintics == wants_quintics)]` splits the primes into
four groups whose members have the same number of roots of unity, so each group is a rectangular
array. It also keeps a `pending` index array that it gathers from (`exponent[pending]`), scatters
into (`generator[pending] = candidate`), and shrinks by masking itself. Gathering, scattering and
shrinking an index array this way is a worklist, and
[array programming](/topics/technique/array-programming) covers it in detail.

## C and Python

C has no fancy indexing, because it does not need it. Every one of these lines is a loop with a
computed subscript:

| Python | C |
| --- | --- |
| `numdivs[ks * (g - ks)].sum()` | `s += numdivs[idx];` inside the loop over `k` |
| `mark[a * a + c] = True` | `for (a = amin; a <= amax; a++) mark[a * a + c] = 1;` |
| `counts[prime_flags(total)]` | `if (big[s]) answer = (answer + counts[s] % MODULUS) % MODULUS;` |
| `primes[mask]`, `pending[...]` | one loop over primes with a per-prime branch |

So the C side never allocates the index array or the gathered copy. Each element costs one load or
store. That has two consequences. First, the C versions have no scalar fallback to tune, since a
three-element loop and a three-million-element loop are the same code. Second, the Python
versions use memory the C versions do not: an `int64` index array and a gathered copy, each the
length of the range. In C the mask is a branch inside the loop. In NumPy it is a separate array that
is built first and then applied.

## How to reason about it

- **Reach for fancy indexing when the address is a formula** rather than a stride. If it is a
  stride, use a slice: it is a view and costs nothing.
- **Remember the copy.** Read results are new arrays. Assign through the subscript, never through
  the result.
- **Duplicates: `=` is safe, `+=` is not.** Marks can be scattered freely. Counts need `np.add.at`
  or `np.bincount`.
- **Bound the indices before you index.** Compute the valid range with integer arithmetic (`isqrt`,
  floor division) rather than masking out-of-range values afterwards.
- **Short ranges stay scalar.** Index arrays and temporaries have a fixed cost per call. Below a
  dozen or so elements, a Python loop wins.
- **A boolean mask is a gather by predicate.** Use it to filter a result (249) or to partition
  inputs into uniform groups (421).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$

<!-- /problems -->
