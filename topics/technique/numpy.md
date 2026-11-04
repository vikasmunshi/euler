<!-- tags: [numpy] -->
<!-- status: final 2026-11-03T12:34Z -->
# NumPy

[NumPy](https://numpy.org/doc/stable/) is what I reach for when a problem's work is
*uniform* — the same arithmetic applied to every integer in a dense range, the same
update applied to every cell of a table. Python's per-element cost is an interpreter
dispatch, an object allocation and a reference count; NumPy's is a machine
instruction on a packed buffer. Nothing about the algorithm changes. What changes is
where the innermost loop runs, and that is worth one to two orders of magnitude on
exactly the kind of loop these problems are made of.

## The idea

An [`ndarray`](https://numpy.org/doc/stable/reference/arrays.ndarray.html) is one
contiguous block of memory plus a
[dtype](https://numpy.org/doc/stable/reference/arrays.dtypes.html) and a shape. A
million `np.int64` entries are eight megabytes of packed integers — not a million
`PyObject` pointers to a million heap-allocated boxes. Every operation you write on
that array (`a + b`, `a % m`, `a > k`, `a[::p] = 0`) is a
[universal function](https://numpy.org/doc/stable/reference/ufuncs.html) that loops
over the buffer in compiled C. Your Python code stops describing *each step* and
starts describing *the whole step*.

Across these problems that collapses into a handful of recurring shapes.

**A strided slice is a sieve.** `flags[p*p::p] = False` marks every multiple of $p$
in one C loop. The Python-level loop that remains runs only $\pi(\sqrt{n})$ times, so
the interpreter is touched $O(\sqrt{n}/\log n)$ times to do $O(n \log \log n)$ work.
The same shape carries a divisor-sum sieve, and a
[Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function) sieve where the strided
slices are `mu[p::p] *= -1` followed by `mu[p*p::p] = 0`. A strided slice also works as
a *target*: [407](/solutions/0407/) takes `view = best[s*(s+1)::s]` (every multiple of
the small factor $s$) and folds a whole array of candidates into it with
`np.maximum(view, cand, out=view)`, so one Python iteration per $s \le \sqrt{N}$
updates every modulus that $s$ divides. [668](/solutions/0668/) runs the
Lucy_Hedgehog [prime count](https://en.wikipedia.org/wiki/Prime-counting_function) the same
way — a Python loop over the primes up to $\sqrt{n}$, each step a couple of strided
slice subtractions over the table of $\pi(\lfloor n/k \rfloor)$. [521](/solutions/0521/)
carries a prime-*sum* table alongside the count and shows where the slice stops
working: the entries $\lfloor n/(ip) \rfloor$ that still index the large table are a
strided slice of it, and past a split index they fall into the small table and become a
gather. Because the split is one computed index rather than a per-entry test, each prime's
update is two contiguous pieces, with no mask.

The slice's start is the only thing that has to be computed, and two generalisations
follow from that. A **segmented** sieve over the block $[lo, hi)$ starts each prime at
`-lo % p`, the first multiple inside the block, so [632](/solutions/0632/) can sieve
$d \le \sqrt{n}$ a few million at a time in bounded memory. It also multiplies each
small prime into a per-entry `product` array as it goes: sieving only to $d^{1/2}$,
an entry with `product < d` has exactly one prime factor left over, which is all its
prime-factor count needs, so the large primes never have to be sieved at all. A
**polynomial** sieve walks the values of $f(k)$ instead of $k$: the $k$ with
$p \mid f(k)$ are the roots of $f$ mod $p$, which form residue classes, so each root
is one strided slice. [659](/solutions/0659/) sieves $4k^2 + 1$ this way, and it
*divides* rather than marks (`values[k::q] //= p`), stepping $q$ through
$p, p^2, \dots$ with each root
[Hensel-lifted](https://en.wikipedia.org/wiki/Hensel%27s_lemma) to the next power.
Once every prime up to the bound has been divided out, whatever is left in each entry
is 1 or a single large prime, and one `np.where` picks the largest factor for every
$k$.

**A comparison is a mask, and a mask is an index.** `div_sums > np.arange(limit + 1)`
yields a boolean array;
[`np.flatnonzero`](https://numpy.org/doc/stable/reference/generated/numpy.flatnonzero.html)
turns it into the positions that passed, and the array itself can index another array
to select those entries. [Non-Abundant Sums](/solutions/0023/) — public, so here is
the real code — is that pipeline end to end, with
[broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) doing the
pairwise sums:

```python
div_sums = np.zeros(limit + 1, dtype=int)
for i in range(1, limit // 2 + 1):
    div_sums[2 * i: limit + 1: i] += i          # strided sieve
abundant = np.flatnonzero(div_sums > np.arange(limit + 1))   # mask -> indices
is_sum = np.zeros(limit + 1, dtype=bool)
for i in range(len(abundant)):
    sums = abundant[i] + abundant[i:]           # one scalar + a whole tail
    is_sum[sums[sums <= limit]] = True          # fancy-index assignment
```

**`arange` plus arithmetic is a closed form applied to a range.** Where the maths
gives a formula in $d$, evaluating it over $d = 1 \dots N$ is one expression:
`counts = upper // (d * d)`, then a dot product against a sieved table. That is the
whole inner loop of the squarefree count in [193](/solutions/0193/), and the
divisor-block sums in [944](/solutions/0944/) are the same move over the
$O(\sqrt{n})$ distinct values of $\lfloor n/x \rfloor$. The same holds when the formula
is a recursion: [625](/solutions/0625/) computes the totient summatory function
$\Phi(\lfloor N/k \rfloor)$ by [Du's sieve](https://en.wikipedia.org/wiki/Dirichlet_hyperbola_method),
and each $v = \lfloor N/k \rfloor$'s explicit divisor range is one `arange`. Some terms
$\Phi(\lfloor v/d \rfloor)$ are large values already memoised, others fall in the sieved
small table, and the mask `k * d <= k_max` routes each to its table — two gathers, no
branch. The range need not be the
answer's index: [257](/solutions/0257/) parametrises its triangles by a fraction
$p/q$, and for each $q$ the admissible $p$ are one `arange`, filtered to the coprime
ones by `np.gcd(p, q) == 1`, with every primitive shape's scalings counted by one
floor division — the Python loop runs over $q$ only.

**A table indexed by an array is a vectorised branch.** A case analysis on a residue
is a lookup: [274](/solutions/0274/) needs a multiplier that depends on $p \bmod 10$,
so it stores the four cases in a ten-entry array and writes
`TABLE[primes % 10] * primes` — one gather, no `if`. Two-dimensional tables work the
same way: [315](/solutions/0315/) precomputes a saving for every (last two digits,
digit sum) pair and reads it for every prime at once as `first[big % 100, sums]`.
A binomial coefficient is three gathers from the factorial tables:
[517](/solutions/0517/) evaluates a whole row of
$\binom{m+j}{j}$ terms as `fact[m + j] * inv[j] % M * inv[m] % M`.

**An index map is a transition, and a scatter must not collide.** When a DP keeps a
distribution over states as a dense vector, a deterministic transition is just
an index array: `dst[to] += src[from]`. [400](/solutions/0400/) pushes its weights
over [Grundy values](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
down the tree with `to = (idx ^ mask) - 1`, sizing the vector to a power of two so
that XOR by a constant *permutes* the indices. That permutation is what makes the
one-line scatter correct. Fancy-index `+=` reads once and writes once, so if two
sources land on the same target only one of them sticks, and nothing warns you. An
injective map, like this one, is safe; a many-to-one map needs
[`np.add.at`](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.at.html)
or `np.bincount(to, weights=src)`. Plain assignment is the exception: `a[idx] = True`
lands the same value however often an index repeats, so a scatter of flags may collide
freely.

**Push, don't pull — and `argmin` is a mex.** A [Grundy value](https://en.wikipedia.org/wiki/Mex_(mathematics))
is the smallest value *not* among a position's options, and computing it by pulling —
gather every predecessor, build a set, scan for the gap — is a Python loop per
position. [310](/solutions/0310/) reverses the direction. It keeps a boolean table
`reach[heap, value]`, and the moment a heap's value is known it pushes it forward to
every heap a square-number move leads from, `reach[heap + squares, value] = True` — the
idempotent scatter above. When the loop reaches a heap, its row is complete, and
`np.argmin` of a boolean row is the first `False`: the mex, in one call. The table's
width is bounded because a mex never exceeds the number of options, here about
$\sqrt{N}$. The count of zero-XOR triples then reuses 400's trick: `bincount` the
Grundy values into a histogram sized to a power of two, and for each $x$,
`np.dot(count, count[values ^ x])` is one term of the
[XOR convolution](https://en.wikipedia.org/wiki/Hadamard_transform) — the gather
permutes, so the dot product pairs every $g(a)$ with the $g(b)$ that cancels it.

**A matrix product enumerates linear combinations.** If each candidate is a fixed
linear function of some per-element features, put the features in rows and the
functions in columns, and `@` evaluates every candidate for every element in one
call. [637](/solutions/0637/) inserts plus signs between digits: each placement is a
weight vector (a digit is worth base to the power of its distance from the end of its
block), so `digits @ weights` gives every split sum of every number at once. For set
intersection the same problem packs booleans into words:
`np.packbits(bits, axis=1).view(np.uint64)` turns a 512-wide membership row into
eight integers, and "do these two sets meet?" becomes `(a & b).any(axis=-1)`
broadcast over every (high half, low half) pair. That is a
[meet-in-the-middle](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) split
of each number's digits, with 64 set members tested per machine AND.

**Loop over the digits, not the numbers.** Digit work on a million integers is a
handful of passes, not a million calls: `rem, d = np.divmod(rem, 10); sums += d`
until `rem` is zero computes every digit sum in [315](/solutions/0315/) in at most
ten array operations. [348](/solutions/0348/) tests palindromes the same way, one
digit pair per pass from the outside in, and *keeps only the survivors* each time —
a [cheap check first](/topics/takeaway/cheap-checks-first) that shrinks the array
roughly tenfold per pass, so the whole filter costs barely more than its first
comparison. `np.unique(..., return_counts=True)` then tallies how many ways each sum
was reached.

The digits can also *become* the array. [705](/solutions/0705/) needs the
concatenation of every prime's decimal string, so it writes the digits into a
(primes × width) `uint8` table, one column per place value, and `ravel()` reads it
row-major — the concatenated string, with the leading-position zeros dropped by the
same `flat != 0` filter that drops the real ones. Counting ordered pairs (positions
$i < j$ holding digits $x$ then $y$) is then one pass per $x$: `np.cumsum(digits == x)`
counts the $x$'s up to each position, and summed over the positions of $y$ it counts
the pairs. A stable `argsort` groups positions by digit so each $y$ is one contiguous
slice. That is a vectorised
[inversion count](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics)), and
it is linear only because the alphabet has nine letters — nine prefix sums, not a
merge sort.

**Vectorise across instances, not just across a range.** Nothing requires the
elements to share a modulus. [421](/solutions/0421/) runs square-and-multiply on an
array of primes, each entry reduced by its *own* prime: `np.where(odd, r * f % p, r)`
is the conditional multiply, and the exponent array shifts right until it is zero.
Even a retry loop vectorises — searching for a base whose power is not 1, it keeps a
`pending` index array of the primes still unsatisfied and shrinks it each round, so
the work per round is only the stragglers. The exponent can differ per element too:
[455](/solutions/0455/) iterates $x \leftarrow n^x \bmod 10^9$ for every $n$ up to a
million *at once*, each element raised to its own current $x$, and stops when
`np.array_equal` says the whole array has reached its fixed point — a dozen rounds,
not a million separate iterations. Even the modulus an exponent is reduced by can be
chosen per element: [492](/solutions/0492/) reduces a tower of 2s mod $p - 1$ or
$p + 1$ for each prime, picked by a quadratic-residue mask, and then runs a
[Lucas-sequence](https://en.wikipedia.org/wiki/Lucas_sequence) ladder in which each
prime reads its own exponent bit. The element need not even be a number:
[721](/solutions/0721/) exponentiates $c + \sqrt{a}$ in the ring
$\mathbb{Z}_p[\sqrt{a}]$, holding each ring element as *two* arrays $(u, v)$ — a
struct of arrays — with a ring multiply written once over whole arrays and each $a$'s
own exponent bit applied as a mask. [437](/solutions/0437/) uses the same struct of
arrays in $\mathbb{Z}_p[x]/(x^2 - x - 1)$ and adds what a struct of arrays costs when
lanes *drop out*. Every prime carries five parallel arrays (the prime, its unfactored
$p - 1$, and a remembered "dead root" held as a fraction), and each time a factor rules some
primes out, one `keep` mask compacts all five together. Filter one array and not the others
and the lanes silently stop lining up. The remainder left after trial division up to
$\sqrt{N}$ is the single large factor, and it gets one last vectorised pass, which is the
leftover-factor argument again.

**A scan with no ufunc folds into a grid.** A running product mod $p$ has no
vectorised form: `np.multiply.accumulate` cannot reduce between steps, so it overflows
`uint64` after a couple of terms. [739](/solutions/0739/) needs exactly such prefix and
suffix products over a range of $n$ factors, and gets them by reshaping each
chunk into a $k \times k$ grid: a Python loop over the $k$ *columns* advances all $k$
rows' scans together, then a $k$-step scalar carry stitches the rows into one
sequence. The Python loop count drops from $k^2$ to $2k$. A plain product reduces as a
pairwise tree, `arr = arr[0::2] * arr[1::2] % p`, in $\log_2$ of the length steps, and
even a linear recurrence fills the grid row-wise: an index-shift identity jumps the
recurrence by a whole row, so each row's start is one scalar step and its contents one
broadcast. [754](/solutions/0754/) runs the grid scan inside a segmented
[Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function) sieve and adds two moves.
A product over a *subset* is a full prefix product of `np.where(mu == 1, d, 1)` —
the identity fills the gaps. And each segment's scan starts from the previous segment's
last value, so the scan covers $1 \dots N$ in bounded memory while one fancy index per
segment keeps only the $O(\sqrt{N})$ prefixes the formula reads, at the quotients
$\lfloor N/k \rfloor$. Its sieve also tracks `rad`, the product of each entry's small
primes, so `mu[rad != d] *= -1` accounts for the one prime above $\sqrt{N}$ that the
sieve never visited — the same leftover-factor argument as 632. [423](/solutions/0423/)
uses the grid scan to build the factorial tables, and the inverse factorials need only
*one* modular inverse: the scan of $n, n-1, \dots, 1$, read backwards, gives
$n!/i!$ for every $i$, and one multiply by $(n!)^{-1}$ turns that whole array into
$1/i!$.

Some recurrences do have a ufunc once you change variables.
[718](/solutions/0718/) computes the
[Apéry set](https://en.wikipedia.org/wiki/Numerical_semigroup) of a three-generator
semigroup by walking the residue cycle of $z$ modulo $x$. Each class's least
representable value obeys $w_i = \min(b_i,\; w_{i-1} + z)$, a min-plus recurrence with
no NumPy form as written. Subtracting $iz$ from both sides gives
$w_i - iz = \min(b_i - iz,\; w_{i-1} - (i-1)z)$, which is a running minimum, so the
whole recurrence is `np.minimum.accumulate(base - i*z) + i*z`. Done in chunks, each
chunk's first entry is folded with the previous chunk's last minimum, so the scan
crosses chunk boundaries with a single scalar of carry. The general rule: a recurrence
$s_i = s_{i-1} \oplus a_i$ vectorises exactly when $\oplus$ is a ufunc with an
`accumulate`, and a shift by a known sequence can often make it one.

**Broadcasting builds the pairwise table.** `xs[None, :] - xs[:, None]` is every
difference vector between $n$ points as one $n \times n$ array. [252](/solutions/0252/)
reduces each by `np.gcd` so that exactly collinear directions become *equal integers*
(floats only order them, never decide equality), sorts every row by angle with
`argsort(axis=1)`, turns the sorted order into ranks with `cumsum` and
`put_along_axis`, and decides which triangles are empty with
`np.maximum.accumulate` — a running maximum along each row in place of a scan over
third points. When the objects are points but the tool wants scalars, pack them:
[983](/solutions/0983/) encodes a lattice point as one `int64` key $xB + y$, after
which `np.unique`, `np.isin` and `searchsorted` handle sets of points as sets of
integers. The pairwise table need not be square or symmetric: for each $q$,
[518](/solutions/0518/) takes the multipliers $k$ that already passed one primality
test and the coprime $p < q$, and `np.outer(ks, ps * ps)` lays out every candidate
$(k, p)$ as a grid. Two gathers from the primality table give a boolean grid, and
`np.nonzero` returns the *coordinates* of its `True` cells, `rows` and `cols`, which
index back into `ks` and `ps` to weight each hit. The outer loop runs over $q$ only;
everything inside it is one grid.

**`searchsorted` is a vectorised binary search.** Given a sorted array of primes,
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html)
evaluates $\pi(x)$ for a *whole array* of $x$ at once. [187](/solutions/0187/) counts
semiprimes as a sum of prime-counting differences and never writes a lookup loop at
all — the table is the array's own index, and the queries are one call. The same
call locates the *piece* of a piecewise formula. [341](/solutions/0341/) evaluates
[Golomb's sequence](https://oeis.org/A001462) at a million cubes up to $10^{18}$ by
inverting its run-length structure. Inverted three times, the structure leaves a table
of only a few tens of thousands of block boundaries. Built in exact Python ints, which
are cheap at that size, it is converted to `int64` once. `searchsorted` then finds every
query's block, and inside a block the sequence's partial sum is a quadratic, so one
vectorised quadratic solve finishes the job. The table is small and the queries are
many, so the binary search is what joins the two.

**`cumsum` is the prefix sum, `bincount` the histogram.** The
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function) is literally
`np.cumsum(mu)`; the count of squarefree numbers up to each bound is
`np.cumsum(mu != 0)`. Both fall out of a Möbius sieve for free in
[464](/solutions/0464/), which then needs a
[Fenwick tree](https://en.wikipedia.org/wiki/Fenwick_tree) — and deliberately does
*not* build it in NumPy (see below).

**Shifted slices are stencils and DP layers.** A grid diffusion step is four
boundary-clipped additions of offset slices — `nxt[:, 1:, :] += share[:, :-1, :]` and
its three mirrors — which is how [213](/solutions/0213/) advances every flea's random
walk simultaneously instead of one walk at a time. The subtlest instance is the
[knapsack](https://en.wikipedia.org/wiki/Knapsack_problem) recurrence in
[249](/solutions/0249/): `counts[prime:] += counts[:-prime]` is the whole
"add this item to every reachable subset sum" pass. The two slices *overlap*, and
NumPy buffers the right-hand read before writing — which is exactly the
descending-index update the recurrence requires, and exactly what a hand-written
ascending Python loop would get wrong. The same slice is polynomial arithmetic: hold a
generating function as its coefficient array and multiplying by $y^s$ is
`out[s:] = p[:-s]`. [996](/solutions/0996/) advances a whole transfer recurrence of
polynomials that way — each step a few shifted sums, every coefficient updated
together.

## How to reason about it

**Fixed-width dtypes are the price of the speed** — [watch the integer width](/topics/takeaway/watch-integer-width). Python's `int` is arbitrary
precision; `np.int64` wraps silently at $2^{63}$ and tells you nothing. Every
vectorised modular computation therefore needs an overflow argument before it needs a
correctness argument. [944](/solutions/0944/) does square-and-multiply on arrays with
the invariant that every partial product stays under $m^2 < 2^{63}$;
[249](/solutions/0249/) knows each pass at most doubles a count, so it can run ten
passes before reducing `mod` $10^{16}$, and sums a `uint64` array in chunks small
enough that no partial sum wraps. [421](/solutions/0421/) does both halves of the
job: it *refuses* inputs past $2^{32}$, where a product of two residues would leave
`uint64`, rather than wrap; and since its final sum can pass $2^{64}$ even though no
term does, it sums the high and low 32-bit halves separately and rejoins them as
Python ints. [348](/solutions/0348/) caps its digit bands at the length whose sums
still fit. [401](/solutions/0401/) needs $x(x+1)(2x+1)/6 \bmod m$ for $x$ up to
$10^{15}$, where the raw product is far past $2^{63}$; rather than reach for a modular
inverse of 6, it divides the 2 and the 3 out of whichever factor they divide — chosen
per element by masks on `x & 1` and `x % 3` — and only then reduces and multiplies. If you cannot state the bound, you do not have a correct program — you
have one that happens to work on the test case.

**Floats estimate; integers decide.** `np.sqrt` on an `int64` array goes through
`float64`, which has 53 bits of mantissa, so past $2^{53}$ the truncated root can be
off by one either way. [331](/solutions/0331/) takes the float root as a guess and
corrects it with exact integer comparisons — `root -= root * root > v`, then the
mirror step up — a vectorised [integer square root](/topics/technique/integer-square-root);
[721](/solutions/0721/) uses the identical two lines to decide which $a$ are perfect squares.
[341](/solutions/0341/) rounds its per-element quadratic root the same way.
[252](/solutions/0252/) applies the same division of labour to angles: `arctan2`
sorts directions, but equality is decided on gcd-reduced integers.

[558](/solutions/0558/) pushes the division of labour furthest. It expands every square
greedily in powers of the real root $r$ of $x^3 = x^2 + 1$. Each remainder is held
*exactly*, as integer coefficients $(a, b, c)$ of $a + br + cr^2$ in three `int64`
arrays, and the question "is the remainder at least $r^k$?" is answered by a fixed-point
evaluation $a \cdot 2^P + b\hat{r} + c\widehat{r^2}$. That evaluation is
allowed to *wrap*. Integer multiplication and addition are exact modulo $2^{64}$, so as
long as the true result fits in `int64`, the wrapped intermediate terms do not matter.
The rounding in $\hat r$ gives a known error bound, and the comparison splits the lanes
three ways: clearly yes, clearly no, and a thin ambiguous band. Only the ambiguous lanes
leave NumPy, for an exact sign test (the field
[norm](https://en.wikipedia.org/wiki/Field_norm)) in Python ints, and they are rare
enough that the exact path costs nothing. The lanes that pass then apply their
subtraction in place with `np.copyto(a, a - pa, where=take)`. Vectorise the decision
that is almost always easy, and pay for exactness only where it is actually in doubt.

**The dtype is also the memory budget.** A Möbius array only ever holds $-1, 0, +1$,
so `int8` costs one byte per entry and a sieve to $2^{25}$ fits in 32 MB instead of
256 MB. When the range genuinely does not fit, chunk it: build `arange` a few million
at a time and accumulate, which keeps the vectorisation and bounds the footprint —
[401](/solutions/0401/) walks its $\sqrt{n} \approx 3 \times 10^7$ hyperbola terms in
chunks of $2^{20}$.

**Vectorising means *no Python per element*, not *NumPy somewhere*.**
[`np.vectorize`](https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html)
is a convenience wrapper around a Python loop and buys no speed — the docs say so
themselves. Indexing an array element-by-element in a Python loop is *slower* than a
list, because each read builds a fresh scalar object. This cuts both ways: when the
algorithm genuinely is scalar and branchy, the right move is `.tolist()` once and
loop over plain Python. [464](/solutions/0464/) does exactly that — NumPy for the
sieve, the prefix sums and the sort, then a hand-written Fenwick tree over Python
lists, because a pointer-chasing $O(\log n)$ update has nothing to vectorise.
[425](/solutions/0425/) draws the same line through a graph. Building the edges is
uniform work: for each digit position and each decrement, one masked subtraction and
one `is_prime` gather produce every edge of that kind for all primes at once. The edges
are concatenated, sorted by their larger endpoint with `argsort`, and two
`searchsorted` calls give every prime its slice of that list — a
[CSR](https://en.wikipedia.org/wiki/Sparse_matrix#Compressed_sparse_row_(CSR,_CRS_or_Yale_format))
adjacency, with `np.cumsum(is_prime) - 1` as the value-to-index map. The
[union-find](https://en.wikipedia.org/wiki/Disjoint-set_data_structure) that walks it
is path-chasing, so it runs over `.tolist()` copies in plain Python.
The converse split works too: [983](/solutions/0983/) is a
[depth-first search](/topics/technique/depth-first-search), and the recursion stays
plain Python, but each node carries the table of every signed sum of its chosen
vectors as an array (tripled per level with one `concatenate`), so the pruning test
at each node is a couple of `np.isin` calls rather than a nested loop.

**It is a constant factor, not a complexity class.** A $50\times$ speedup never
rescues the wrong exponent; see [algorithm beats language](/topics/takeaway/algorithm-beats-language).
Fix the asymptotics first, then vectorise the inner loop that survives. Conversely,
once the algorithm is right, NumPy is often the cheapest remaining win — it keeps the
solution in Python, readable and a dozen lines long, at a speed that would otherwise
mean rewriting in C.

**Build the arrays inside `solve()`.** The benchmark harness times repeated calls, so
a table built at module import is free on every run after the first and the reported
cost is a fiction. Size the sieve to the actual input and build it per call.

**When it does not apply:** irregular control flow, data-dependent recursion,
pointer-chasing structures, and heavy exact arithmetic past 64 bits, where Python's
own bignums are the tool. A `dtype=object` array holds Python ints and keeps the
slicing and broadcasting, but its arithmetic runs at interpreter speed — useful as a
switch, not as a speed-up: [996](/solutions/0996/) writes its recurrence once and
picks `int64` when the input supplies a modulus and `object` when it asks for the
exact value, so one body of code serves both the small exact examples and the large
reduced one. NumPy wants the same operation, over a dense
contiguous range, with the branches expressed as masks rather than `if`s. When the
work has that shape, reach for it; when it does not, forcing it produces code that is
both slower and harder to read.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0304](/solutions/0304/) — Primonacci
- ● [0310](/solutions/0310/) — Nim Square
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0407](/solutions/0407/) — Idempotents
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0425](/solutions/0425/) — Prime Connection
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0475](/solutions/0475/) — Music Festival
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0558](/solutions/0558/) — Irrational Base
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0632](/solutions/0632/) — Square Prime Factors
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0688](/solutions/0688/) — Piles of Plates
- ● [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0749](/solutions/0749/) — Near Power Sums
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ● [0921](/solutions/0921/) — Golden Recurrence
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [0983](/solutions/0983/) — Consonant Circle Crossing
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
