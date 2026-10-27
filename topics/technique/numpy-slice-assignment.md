<!-- tags: [numpy-slice-assignment] -->
<!-- status: final 2026-10-16T15:58Z -->
# NumPy slice assignment

Most sieves in these solutions do one thing over and over: *update every $k$-th entry of
a table, starting at some offset*. That is a C `for` loop with a stride, and NumPy can
write it as one statement, `a[start::step] op= value`, which runs the whole loop in
compiled code. The [NumPy page](/topics/technique/numpy) explains why vectorising pays
and where it doesn't. This page covers the one construct that turns up in every problem
below: what a slice assignment means, which C loop it replaces, and the details that
decide whether the replacement is correct.

## The idea

A [basic slice](https://numpy.org/doc/stable/user/basics.indexing.html#slicing-and-striding)
`a[start:stop:step]` is a *view*: no copy, just a new start pointer and a stride into
the same buffer. Assigning to it, or applying a compound operator to it, writes through
to the original array. So the two lines below do the same work. One runs in the
interpreter's bytecode loop, the other runs entirely in C:

```c
for (long long m = start; m <= n; m += step) a[m] OP= v;
```

```python
a[start::step] OP= v      # stop omitted: "to the end of the array"
```

Read the slice as the loop header. `start` is the initialiser, `step` is the increment,
and the array's length is the `m <= n` guard, because a slice that runs past the end
just stops there and never raises. The C ports of these problems keep this loop
verbatim, so each NumPy line in the Python has a matching line in the C file.

Every problem below uses one of four variations on that loop header.

**Mark: the sieve of Eratosthenes.** `flags[p*p::p] = False` clears the multiples of $p$
from $p^2$ onward. [216](/solutions/0216/), [249](/solutions/0249/),
[319](/solutions/0319/) and [351](/solutions/0351/) all build their prime tables this
way. The [sieve page](/topics/technique/sieve-of-eratosthenes) explains why the start
is $p^2$. On the NumPy side, the Python loop runs only over $p \le \sqrt n$, while each
statement does about $n/p$ writes. [304](/solutions/0304/) uses the stride to skip even
numbers: it clears the evens once with `base[4::2]`, then marks odd multiples with step
$2p$, the same halving the C loop gets from `j += 2 * p`.

**Accumulate: divisor and multiplicative sieves.** Swap `=` for `+=`, `-=`, `*=` or
`//=` and the strided loop gathers arithmetic instead of marking. With `tau[i::i] += 1`
every multiple of $i$ counts $i$ as a divisor, which is how [420](/solutions/0420/)
builds its divisor-count table. In [351](/solutions/0351/),
`phi[p::p] -= phi[p::p] // p` applies the factor $(1 - 1/p)$ of Euler's
[totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function) to every multiple
of $p$ in one statement. The [Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function)
sieves in [319](/solutions/0319/) and [464](/solutions/0464/) take two strides per
prime: they flip the sign at step $p$, then zero the entries at step $p^2$. 319 also
runs `cofactor[q::q] //= p` for each prime power $q$, removing the small primes from
every index so that what is left over shows which numbers still have a large prime
factor. Each of these keeps the same `m += step` header in its C version, and only the
loop body changes.

**Pair: the half-length divisor count.** Looping $i$ up to $n$ costs $n$ Python-level
statements, and each one has a fixed overhead whatever its length. Past $i \approx n/2$
the slices are only one or two entries long, so that overhead becomes most of the cost.
[179](/solutions/0179/) avoids this with the divisor-pair idea. Every divisor
$a \le \sqrt m$ comes with a partner $m/a$, so it runs `div_count[a*a::a] += 2` for
$a \le \sqrt n$ and corrects the square case by one. The work is the same, but there are
$\sqrt n$ statements instead of $n$. The C version doesn't need this trick, because a
loop iteration there costs a few cycles. The trick exists because in Python the cost
per slice dominates.

**Offset: residue classes and windows.** Nothing forces the start to be a multiple of the
step. A slice can describe any arithmetic progression, so a congruence turns into a
slice once you know its least solution:

- [216](/solutions/0216/) sieves the values $2n^2 - 1$ rather than the integers. Each
  prime $p$ divides that polynomial exactly when $n$ is one of the two square roots of
  $1/2 \pmod p$, so each prime contributes two slices, `is_t_prime[r::p]` for each root
  $r$. Finding $r$ is a modular square root. Once $r$ is known, the marking is the same
  one-line stride.
- [304](/solutions/0304/) runs a
  [segmented sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve)
  over a window that starts at `low`. The first multiple of $p$ inside it is at offset
  `(-low) % p`, which is the whole adjustment the segment needs.
- [256](/solutions/0256/) counts, for each area in a window, the rooms of that area that
  can be tiled. For one side length $a$, the valid areas form a band of an arithmetic
  progression, and the step doubles to $2a$ when an odd side forces the other side to
  be even. One `counts[lo:hi:step] += 1` records a whole band, so the window is filled
  with a Python loop over $(a, k)$ and never over the areas themselves.

**Shift: the overlapping slice.** The fourth variation has no stride. The *source* is a
slice of the same array, shifted:

```python
counts[p:] += counts[:-p]        # every subset sum s gains the subsets of s - p
```

```c
for (long long s = total; s >= p; s--) counts[s] += counts[s - p];
```

This is the 0/1 [knapsack](https://en.wikipedia.org/wiki/Knapsack_problem) step in
[249](/solutions/0249/). The C loop runs *downwards* on purpose: going upwards would
read entries that this same prime has already updated, and an item could be used twice.
NumPy gets the downward loop's result without any special care, because it
[detects the overlap](https://numpy.org/doc/stable/release/1.13.0-notes.html#operations-where-ufunc-input-and-output-operands-overlap)
and behaves as if the right-hand side were copied before the write. The
[NumPy page](/topics/technique/numpy) also covers this case. What matters here is the
consequence: the slice gives you *only* the copy semantics. If a recurrence really
needs the upward behaviour, where each entry reads its already-updated neighbour (the
unbounded knapsack, a running total), it is a sequential dependency, and one slice
statement cannot express it. That needs `np.cumsum`, or a Python loop.

The same alignment gives cheap comparisons between neighbours. In
[179](/solutions/0179/), `div_count[2:n] == div_count[3:n+1]` lines up $d(m)$ with
$d(m+1)$ for every $m$ at once. In [464](/solutions/0464/), `key[1:] != key[:-1]` finds
where a sorted key changes value. Both read two views of the same buffer and write
nothing back.

## How to reason about it

**Check the loop header first, then the slice.** Most errors here are off-by-one
mistakes in `start` or `stop`. Write the C loop you mean, including its first index,
step and final index, and then translate it. A missing stop means "through index
`len - 1`", so a table that must include $n$ needs length $n + 1$. That is why every
array in these solutions has size `limit + 1`. An explicit stop is *exclusive*: 256's
band slice ends at `last - lo + 1` to make it inclusive.

**Edge cases do not raise errors.** A start past the end gives an empty slice and a
silent no-op. 216 checks `start > max_n` explicitly because otherwise nothing would
show that a root was skipped. The shift form has a trap at zero: `a[:-0]` is `a[:0]`,
which is *empty*, not the whole array. A zero shift then fails with a shape mismatch
instead of doubling the array. Shift by a value you know is at least 1.

**Compound assignment keeps the left-hand dtype and wraps.** `a[s::k] += x` casts the
result back to `a`'s dtype under the `same_kind` rule. An `int8` Möbius table that
gets `+= 300` wraps without any warning. That is safe for $\mu \in \{-1, 0, 1\}$ and for
256's `uint16` counts, whose values stay tiny. It is a problem for a knapsack count
that doubles every pass, which is why 249 reduces modulo its bound before a
`uint64` could overflow. The table's dtype is part of the correctness argument; see
[watch the integer width](/topics/takeaway/watch-integer-width).

**Basic slices update every entry; fancy indices may not.** A stride touches each
position at most once, so `+=` on it is exact. An *integer-array* index such as
`a[idx] += 1` is buffered, so a repeated index in `idx` is incremented once, not twice.
Use [`np.add.at`](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.at.html)
or `np.bincount` when indices can repeat. 304 mixes the two kinds safely. For small
primes it uses one strided slice per prime. For large primes, which hit the segment at
most once, it uses a single fancy assignment `seg[offsets] = False`. Duplicates in that
array cannot matter because the value assigned is constant.

**The count of statements is the cost model.** A slice statement costs a fixed overhead
plus a C loop over its entries. Total work is the usual sieve bound,
$\sum n/p = O(n \log\log n)$ for primes or $\sum n/i = O(n \log n)$ for divisors.
NumPy wins when the *number of statements* is much smaller than the work, as with
$\pi(\sqrt n)$ marking passes or 179's $\sqrt n$ pair passes. When most slices are a
handful of entries long, the fixed overhead dominates and the Python can fall behind a
plain list loop. In that case either restructure (pair the divisors, sieve only to
$\sqrt n$ as 319's Möbius table does) or accept that the problem belongs in C. When
the work genuinely fits the strided shape, a slice assignment keeps a sieve readable
and close to C speed: one line per loop, matching the C file line for line.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0304](/solutions/0304/) — Primonacci
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0351](/solutions/0351/) — Hexagonal Orchards
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers

<!-- /problems -->
