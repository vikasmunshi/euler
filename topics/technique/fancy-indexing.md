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
gather, scatter, and mask, the shape of the index, and the copy semantics behind them all. The rest
of the family is on
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

Repeats are a hazard on that one path only. A gather may read a position as often as it likes:
problem 521 indexes with `np.arange(p_squared, root + 1) // p`, which reads each source about $p$
times, and that is exactly what it means. A plain `=` of a constant may collide freely, as the
scatter below shows. And a boolean mask cannot name a position twice, so a compound update through
one is always exact: problem 333's `acc[fits] += …` needs no `np.add.at`.

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

An index array can also be a pure relabelling. Problem 310 needs the XOR self-convolution of a
histogram, and `count[values ^ x]` reorders the histogram so that one `np.dot` pairs each value with
its partner; [numpy](/topics/technique/numpy) has the details. This gather needs no bounds check, for
a reason worth copying: the histogram is padded to a power of two, and XOR maps that range onto
itself, so no index can leave the table.

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

A mask is also the vector spelling of `if`. Problem 291 raises a whole array of bases to a whole
array of exponents by square-and-multiply, and each element multiplies only where its own exponent
has the current bit set. So it reads, computes and writes back through one mask:
`result[odd] = result[odd] * b[odd] % mod[odd]`.

## The result takes the shape of the index

Everything so far used a one-dimensional index on a one-dimensional table. The general rule is that
the result has the shape of the *index*, whatever the shape of the table. Problem 518 reads a flat
primality table through a two-dimensional index:

```python
ok = is_prime[np.outer(ks, ps * ps) - 1] & is_prime[np.outer(ks, ps * q) - 1]
```

So `ok[i, j]` is the verdict on the pair `ks[i]`, `ps[j]`. A position in the result carries the
parameters that produced it, and `np.nonzero(ok)` hands them back as coordinates, ready to gather
from `ks` and `ps`. [numpy](/topics/technique/numpy) walks through that grid.

On a table with several axes, each axis takes its own subscript, and how they combine depends on
what those subscripts are:

| subscript | selects | example |
| --- | --- | --- |
| `t[:, cols]` | whole columns, every row | 333: `table[:, evens] = table[:, evens // 2]` |
| `t[rows, c]` | one column of many rows: the scalar broadcasts | 310: `reach[heap + squares[:span], value] = True` |
| `t[rows, cols]` | `t[rows[i], cols[i]]`: the arrays pair up, element by element | `ok[rows, cols]` |

The last row is the surprise. Two index arrays do not form a grid. For that, use
[`np.ix_`](https://numpy.org/doc/stable/reference/generated/numpy.ix_.html) or a broadcast index.
One caution on the first row: 333's index arrays are regular, since `evens` steps by 2 and
`evens // 2` by 1, so slices would express the same move without the copies. The arrays are a
convenience there, not a necessity. What makes the statement legal is the
[doubling block](/topics/technique/dynamic-programming) around it.

## The copy as a snapshot

So far the copy has been a trap. In a table that updates itself it is a tool. The
[Lucy_Hedgehog sieve](/topics/technique/lucy-hedgehog-sieve) in problem 521 rewrites each entry from
the entry at $\lfloor v/p \rfloor$, and every read must see the value from *before* this prime's
step. The C port arranges that with loop direction: it walks the small table downwards, so the entry
it reads has not been written yet. The NumPy version has no direction to choose:

```python
index = np.arange(p_squared, root + 1) // p
snapshot = count_small[index]                 # complete before anything is written
count_small[p_squared:] -= snapshot - primes_below
```

The name matters. A slice held in a variable is a view and tracks later writes. A gather held in a
variable keeps the old values. ([Slice assignment](/topics/technique/numpy-slice-assignment) meets
the same line in problem 452.) The snapshot protects one table within one step, though, not the
order of the steps. 521 still updates its large table first, because that update reads the small
table and needs it unchanged.

## Slice or scatter is a choice per range

"A stride gets a slice, a formula gets an index array" is the right first rule, but the choice also
depends on length, and one logical step can use both.

Problem 291 runs a [polynomial sieve](/topics/technique/polynomial-sieve): for each of about two
million primes it strikes two residue classes. Every class is a stride, so a slice can express each
one. But a slice is a statement, and for primes above $N/64$ each statement would strike fewer than
64 entries, so the interpreter would dominate. An index array can hold positions from *many* strides
at once, which no slice can do. The primes are grouped into doubling bands, and the loop runs over
the hit number instead of the prime:

```python
for k in range(hits):             # the k-th hit of every prime in the band
    idx = start + k * q_band
    mark[idx[idx <= limit]] = False
```

Primes up to $N/64$ keep their slices, and the rest cost a few hundred statements in all rather than
millions. [Slice assignment](/topics/technique/numpy-slice-assignment) gives this transposition in
general. What belongs here is the mask on `idx`, which seems to break the advice below to bound
indices first. It does not: each prime runs out at a different $k$, so no single bound exists. The
limit is ragged, and masking is the way to apply it. Banding keeps the waste small, since hit counts
within a band differ by at most a factor of two or so.

Problem 521 splits by position rather than by length. For one prime, the quotient
$\lfloor n/(ip) \rfloor$ falls in the large table at index $ip$ for small $i$, which is a stride, and
in the small table beyond that, where its position is a formula. One buffer is filled from both:

```python
new[:split] = large[p:split * p + 1:p]        # a stride: slice
new[split:] = small[n // (i * p)]             # a formula: gather
```

## C and Python

C has no fancy indexing, because it does not need it. Every one of these lines is a loop with a
computed subscript:

| Python | C |
| --- | --- |
| `numdivs[ks * (g - ks)].sum()` | `s += numdivs[idx];` inside the loop over `k` |
| `mark[a * a + c] = True` | `for (a = amin; a <= amax; a++) mark[a * a + c] = 1;` |
| `counts[prime_flags(total)]` | `if (big[s]) answer = (answer + counts[s] % MODULUS) % MODULUS;` |
| `primes[mask]`, `pending[...]` | one loop over primes with a per-prime branch |
| `is_prime[x] & is_prime[y]` | `if (is_prime[x] && is_prime[y])` |
| `snapshot = small[index]` | a loop that runs downwards |

So the C side never allocates the index array or the gathered copy. Each element costs one load or
store. That has two consequences. First, the C versions have no scalar fallback to tune, since a
three-element loop and a three-million-element loop are the same code. Second, the Python
versions use memory the C versions do not: an `int64` index array and a gathered copy, each the
length of the range. In C the mask is a branch inside the loop. In NumPy it is a separate array that
is built first and then applied.

Whole-array evaluation has two more effects. `&` cannot short-circuit, so 518's Python gathers from
both tables for every pair, where C's `&&` skips the second load once the first fails. And the
recorded timings show what vector length is worth. With long vectors, 291, 518 and 521 all run about
twice as slow as their C ports. 310 issues its calls once per heap, on vectors of at most
$\sqrt{N} \approx 316$ entries, and runs about nine times as slow.

## How to reason about it

- **Reach for fancy indexing when the address is a formula** rather than a stride. If it is a
  stride, use a slice: it is a view and costs nothing. The exception is many short strides, where
  one index array across all of them beats one slice each (291).
- **Remember the copy.** Read results are new arrays. Assign through the subscript, never through
  the result. In a self-updating table, use it: a gather is a snapshot of the old values (521).
- **Duplicates only matter on a compound write through an integer array.** Gathers may repeat, marks
  may collide, and masks cannot repeat. Counts through an integer array need `np.add.at` or
  `np.bincount`.
- **Bound the indices before you index.** Compute the valid range with integer arithmetic (`isqrt`,
  floor division) rather than masking out-of-range values afterwards. If the limit differs per
  element, mask the index array (291). Better still, size the table so the index cannot leave it
  (310).
- **The result has the shape of the index.** A 2-D index on a flat table gives a grid whose
  coordinates are the parameters (518). Two index arrays pair up; they do not form a grid.
- **Short ranges stay scalar.** Index arrays and temporaries have a fixed cost per call. Below a
  dozen or so elements, a Python loop wins.
- **A boolean mask is a gather by predicate.** Use it to filter a result (249), to partition
  inputs into uniform groups (421), or to apply an update only where a condition holds (291).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0310](/solutions/0310/) — Nim Square
- ● [0333](/solutions/0333/) — Special Partitions
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0521](/solutions/0521/) — Smallest Prime Factor

<!-- /problems -->
