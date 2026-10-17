<!-- tags: [array-programming] -->
<!-- status: final 2026-10-17T07:21Z -->
# Array programming

[Array programming](https://en.wikipedia.org/wiki/Array_programming) means writing a program
whose operands are whole collections, not single values: `a + b` adds every pair, `a > k` tests
every entry, `a.sum()` folds them all, and the loop over the elements is never written down. The
idea comes from Iverson's [APL](https://en.wikipedia.org/wiki/APL_(programming_language)), and
NumPy is how it reaches Python. The other pages in this family are about the instruments: the
[NumPy page](/topics/technique/numpy) on the library as a whole,
[slice assignment](/topics/technique/numpy-slice-assignment) for strided updates,
[`np.flatnonzero`](/topics/technique/np-flatnonzero) for turning a mask into members,
[fancy indexing](/topics/technique/fancy-indexing) for gather and scatter, and
[vectorized](/topics/technique/vectorized) for the performance argument. This page is about the
step that comes before any of those: taking an algorithm written one element at a time and
restating it so that *a whole array is the unit of work*. The five problems below each do that
restatement differently, and each one meets a different obstacle on the way.

## The idea

A scalar program has three things that stop it from being an array program: **branches** (an `if`
on the current element), **loops whose trip count depends on the element** (a `while` that runs
until this element is done), and **writes whose target depends on the element** (`counts[n] += 1`).
To turn it into an array program you trade each one for an array equivalent:

| scalar construct | array form | what it costs |
|---|---|---|
| `if cond: x = f(x)` | `x = np.where(cond, f(x), x)` | `f` is evaluated for every element, taken or not |
| `while e: ...` per element | `while e.any(): ...` over all | every element runs as many rounds as the slowest |
| boundary checks on a neighbour | zero padding plus shifted copies | a few extra cells per row |
| `counts[n] += 1` scattered | build every `n`, then `np.bincount` | the whole list of `n` is in memory at once |
| loop over independent instances | one more array axis | memory multiplied by the instance count |

None of these changes the algorithm. Each one changes *who runs the loop*. Each row also has a
cost column, and that column is why array programming is a design decision and not a mechanical
rewrite.

## Five restatements

**Generate, then tally — [135](/solutions/0135/).** The problem reduces to counting factor pairs
$(u, v)$ of $n$ under a congruence and an inequality, which suggests a sieve: walk the pairs and
increment `counts[u * v]`. That increment is a scatter with repeated targets, which is exactly the
write an array program cannot do directly. `counts[ns] += 1` on a fancy index with duplicates
adds **once** per distinct index, not once per occurrence, because the read, the add and the
write each happen as a whole-array operation. So the Python side splits the sieve in two. For each
$u$, the valid $v$ form a single arithmetic progression, so one `np.arange(v_start, v_max + 1, 4)`
times `u` generates that $u$'s batch of products. After the loop, the batches are concatenated
and one [`np.bincount`](/topics/technique/np-bincount) does the tally. The Python loop runs over
$u$ only, while every $v$ is handled in C. The price is that the full multiset of products exists
in memory at the moment `bincount` reads it. The C side never builds that list: its inner loop
just runs `counts[u * v]++` in place.

**Neighbourhoods by shifting — [196](/solutions/0196/).** Here the question is which primes in a
row of a triangular number array have at least two prime neighbours among their eight
king-move neighbours, and which primes border such a "centre". Asked one cell at a time, that is
a stencil full of edge cases: the first column, the last column, and rows of different lengths.
Asked of a whole row, it is eight shifted copies of three indicator rows, added together:

```python
nb = shift_up(p_here) + shift_dn(p_here) + shift_up(p_up) + p_up + shift_dn(p_up) + ...
centre = (p_here == 1) & (nb >= 2)
```

Zero padding removes the edge cases. Each row is stored with spare zero columns on both sides, so
a shift past the edge reads a zero, and a neighbour that does not exist counts the same as a
composite. The second question, whether a cell borders a centre, has the same shape with `|` in
place of `+`. The primality underneath comes from a [segmented sieve](/topics/technique/segmented-sieve)
over the five rows' contiguous value range, which is itself an array program of strided slices.

**One more axis — [213](/solutions/0213/).** Each of 900 fleas does a random walk on a grid, and
the expected number of empty squares needs every flea's landing distribution. The scalar program
loops over fleas and, for each one, evolves a $30 \times 30$ probability grid. The array program
gives the flea index its own axis: `dist` has shape `(fleas, n, n)` and starts as the identity
matrix, reshaped. One step of the walk is a [stencil](/topics/technique/stencil-numerical-analysis)
of four boundary-clipped slice additions, `nxt[:, 1:, :] += share[:, :-1, :]` and its three
mirrors, and it advances all 900 walks at once. The answer is then a reduction along the flea
axis, `np.prod(1.0 - landing, axis=0)`, summed. Raising the rank works because the instances are
independent and all the same size. When they are, "for each instance" and "for each cell" collapse
into a single loop, and NumPy runs it.

**A scalar algorithm on many moduli — [421](/solutions/0421/).** The counting needs roots of
unity modulo each of millions of primes, which means one
[modular exponentiation](/topics/technique/modular-exponentiation) per prime, with each prime as
its own modulus. Square-and-multiply has both obstacles at once. The multiply is conditional on
the current exponent bit, and the loop length depends on the exponent. The array version turns the
`if` into `np.where(odd, result * factor % modulus, result)`, and turns the `while` into
`while remaining.any()`. An element whose exponent has already reached zero keeps going round, but
its multiplications are masked out, so it gets no wrong answers, only spent cycles. Then comes the
retry loop: find a base whose power is not 1. That has a data-dependent trip count per prime. It
is handled with a shrinking **pending index array**. Each round computes only the primes still
unsatisfied, writes their results back through that index, and keeps the ones that failed. Most
primes succeed at the first base, so after round one the array is small. There is also a ragged
part: a prime has 1, 3, 5 or 15 roots depending on its residues mod 3 and mod 5. That is handled
by **grouping**. The primes are split into four masks by residue class, so within each group every
prime has the same root count and the inner loops are rectangular again.

**A recurrence whose step is an array — [720](/solutions/0720/).** The permutation that is wanted
doubles in a structured way, and so does its [Lehmer code](https://en.wikipedia.org/wiki/Lehmer_code):
the code for $2n$ is the code for $n$ cut into a head and a tail, adjusted element-wise, with a
two-entry seam between them. Each doubling step is therefore a few slice expressions and one
`np.concatenate`, and reaching $2^{25}$ takes 23 such steps instead of $2^{25}$ scalar updates.
The second half shows where array programming *stops*. Reading the code as a
[factorial-base](/topics/domain/factorial-number-system) rank modulo $m$ is a
[Horner](/topics/technique/horners-method) fold, $acc \leftarrow d_i + k \cdot acc$, in which
each step depends on the one before. No ufunc expresses a modular fold like that. So the solution
switches to scalar: it converts with `.tolist()` in chunks of $2^{20}$, which bounds the size of
the temporary Python list, and runs a plain loop over Python ints.

## How to reason about it

**Ask what the axes are before you ask what the loop is.** The useful question is not "how do I
vectorise this loop" but "which arrays does this computation live on". In 213 the answer is
fleas × rows × columns. In 196 it is one row at five offsets. In 421 it is one entry per prime. Once
the axes are named, the operations usually follow.

**Masks compute both branches.** `np.where` costs the price of the expensive branch on every
element. That is fine when the branches are cheap, as with the multiply in 421, and wasteful when
one branch is rare and expensive. In that case, compact first and work only on the members, which
is what 421's pending array does, and what
[`flatnonzero`](/topics/technique/np-flatnonzero) is for.

**Ragged work wants grouping or padding.** Array operations need rectangular shapes. When the
instances differ in size, either pad them to a common size (196's spare zero columns) or sort them
into groups that are each rectangular (421's four residue classes). Padding wastes a little work
everywhere. Grouping costs one loop iteration per group.

**Materialisation is the hidden cost.** Every intermediate expression in an array program is a
full-size temporary. 135 holds every product at once, and 213 allocates `share` and `nxt` on every
ring. The C translations need neither. When memory becomes the limit, process the range in
chunks: the vectorisation survives, and only the peak memory goes down.

**Sequential dependencies stay scalar unless a scan ufunc fits.** `cumsum`, `cumprod` and
`np.maximum.accumulate` vectorise the prefix scans they implement. A fold with a modulus or a
data-dependent update, such as 720's Horner step, does not vectorise. Leave it as a scalar loop,
and convert to Python ints first, because iterating an array element by element is slower than
iterating a list.

**Width is fixed.** Every array here is `int64`, `uint64` or `float64`, and none of them warn on
overflow ([watch the integer width](/topics/takeaway/watch-integer-width)). 421 has to bound its
moduli below $2^{32}$ so that a product of two residues fits in `uint64`.

## C and Python

In every one of these problems the C side is the scalar program that the Python side was derived
from, and comparing the two shows each restatement undone:

- **135**: C runs `counts[u * v]++` inside the double loop. There is no list of products and no
  `bincount`, and memory stays at the size of the count array.
- **196**: C keeps the zero padding but replaces the shifted copies with direct indexing
  `ph[c - 1] + ph[c + 1] + ...`. It also skips non-prime cells with an early `continue`, which a
  mask-based version cannot do. The `||` in its triplet test short-circuits, while the Python `|`
  evaluates all nine terms.
- **213**: C flattens `(flea, cell)` to `f * cells + t` and writes the four neighbour additions
  with `if (r > 0)` style guards per cell, instead of clipped slices. These are the same boundaries,
  enforced by branches instead of by slice bounds.
- **421**: C is one loop over primes with a scalar `powmod` and a `for` loop that tries bases until
  the generator exceeds 1. It needs no grouping and no pending array, because each prime simply
  takes as many iterations as it needs. It accumulates the total in `unsigned __int128`, while
  Python sums the high and low 32-bit halves of a `uint64` array separately and recombines them as
  Python ints.
- **720**: The doubling is the same head, seam and tail loops, written with explicit indices into
  freshly allocated buffers. The Horner fold is the same loop in both languages, because it was
  never vectorised in the first place.

The pattern is consistent. Each place where Python pays to remove a branch, a variable trip count
or a scatter is a place where C simply keeps it. Array programming is the right model when the
interpreter is the bottleneck. In C, the scalar loop is already the fast path.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0135](/solutions/0135/) — Same Differences
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0720](/solutions/0720/) — Unpredictable Permutations

<!-- /problems -->
