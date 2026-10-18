<!-- tags: [knapsack-problem] -->
<!-- status: final 2026-10-18T12:41Z -->
# Knapsack problem

The [knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem) is usually stated as an
optimisation: items with weights and values, a capacity, maximise the value that fits. The
*technique* behind it is more general, and it is what this page is about: a table indexed by
**capacity used**, with the items folded in one at a time, each fold a single sweep over the
table. The three solved problems below all count rather than optimise, and the most common case,
counting subsets by sum, is covered in depth on the
[subset sum problem](/topics/domain/subset-sum-problem) page. This page covers what that one leaves
out: the knapsack *variants* (0/1 versus unbounded, one capacity versus several), the loop-order
rule that separates them, and how the same sweep turns into code in Python and C.

## The idea — one sweep per item, and the direction decides the variant

Write $f[c]$ for "the answer using capacity exactly $c$" over the items folded in so far. Folding
in an item of weight $w$ is

$$f[c] \mathrel{\oplus}= f[c - w] \otimes \text{(item)} \qquad \text{for every } c \ge w,$$

where $(\oplus, \otimes)$ depends on the question:

| question | $f[c]$ holds | $\oplus$ | $\otimes$ item | problems |
|---|---|---|---|---|
| how many ways? | a count | $+$ | $\times 1$ | 181, 249 |
| is it reachable (once, twice)? | a bit or a capped count | OR | shift | 201 |
| best value? | a value | $\max$ | $+\,v$ | (the textbook case) |

The recurrence is the same in all three; only the
[semiring](https://en.wikipedia.org/wiki/Semiring) changes. That is worth knowing because it means
a counting solution and an optimising one share their bugs, and the most common bug is loop
direction:

- **0/1 knapsack (each item at most once):** sweep $c$ **downward**. Then $f[c - w]$ still holds
  the value from *before* this item, so the item can be used once at most.
- **Unbounded knapsack (any number of copies):** sweep $c$ **upward**. Then $f[c - w]$ already
  includes this item, and reading it lets the item be used again. This counts multisets.
- **Bounded (at most $k$ copies):** either fold the item in $k$ times as a 0/1 item, or, for
  counting, multiply by $1 + x^w + \dots + x^{kw}$ with a sliding-window sum.

With several capacities (a vector $\mathbf{c}$), the rule generalises: the sweep must visit
$\mathbf{c} - \mathbf{w}$ before $\mathbf{c}$ for unbounded and after it for 0/1, and lexicographic
order in either direction does that.

## The three problems

**181, grouping black and white objects: a two-dimensional unbounded knapsack.** $B$ black and $W$
white objects (identical within a colour) are split into unordered groups. A group is a pair
$(i, j)$ of black and white counts, and a grouping is a multiset of such pairs adding up to
$(B, W)$. That is the [partition](https://en.wikipedia.org/wiki/Partition_(number_theory)) of a
two-coloured number, and the knapsack form is direct: every $(i, j) \ne (0, 0)$ is an item that may
be used repeatedly, the capacity is the vector $(B, W)$, and $f[a][b]$ counts multisets that use
exactly $a$ black and $b$ white objects. Each item is folded in completely before the next, which
is what makes each multiset be counted once, in the fixed order of its item types. The sweep runs
upward in $a$, and for items with $i = 0$ (white-only groups) upward in $b$ within the row. There
are $(B+1)(W+1) - 1$ item types and each sweeps the whole table, so the cost is $O(B^2 W^2)$.

**201, subsets with a unique sum: a second capacity for the size.** The question is which sums are
reached by exactly one 50-element subset of $\{1^2, \dots, 100^2\}$. Subset *size* is a second
capacity axis, and since each element is used at most once, the size axis is swept downward (the
0/1 rule applied to $j$). The value semiring is "reached once / reached twice or more", so each
row is two [bitsets](/topics/technique/bit-array) and an item is folded in by a shift and two ORs.
The subset sum page explains the capped counter.

**249, prime subset sums: the plain 0/1 counting knapsack.** Every subset of the primes below 5000,
counted by sum modulo $10^{16}$, and the prime-indexed counts added up. One capacity, 0/1 items,
counts: the downward sweep exactly. The only addition is how the modulus is applied (below).

## Python and C — the direction rule, implemented

How each language enforces the loop direction is the most instructive difference across the three.

- **NumPy's overlapping slice add is a 0/1 sweep.** In 249 the Python fold is
  `counts[p:] += counts[:-p]`. The two slices overlap, but NumPy reads the source into a buffer
  before writing, so every read sees the pre-item counts. That is the downward-sweep semantics with
  no explicit loop. The C side writes the loop itself, `for (s = total; s >= p; s--)`, and the
  direction is visible in the code.
- **An unbounded in-row sweep cannot be vectorised that way.** In 181 the white-only items $(0, j)$
  read and write the same row, and the unbounded rule needs each read to see values updated
  *during this pass*, which is a running recurrence, not a slice add. Python keeps that case as a
  plain loop (`row[b] += row[b - j]`, ascending). For $i > 0$ the source is a different row,
  $f[a - i]$, already finished for this item because $a$ ascends, so the whole row can be added in
  one slice-aligned list comprehension at C-level speed. C needs neither distinction: both cases are
  the same doubly nested ascending loop.
- **Counts that outgrow 64 bits.** 181's counts are exact and very large. Python's `int` handles
  them. The C side carries a small bignum (base-$10^9$ limbs, add with carry) in every cell of one
  contiguous table, since addition is the only operation the DP needs.
- **Lazy modular reduction.** 249 counts modulo $10^{16}$. A 0/1 fold at most doubles a count, so
  after a reduction there is room for ten folds: $10^{16} \cdot 2^{10} \approx 1.0 \times 10^{19}$
  is still below $2^{64} \approx 1.8 \times 10^{19}$.
  Both sides reduce the table once every ten primes, not after every addition, which removes about
  90% of the `%` operations. The final sum is reduced in chunks for the same reason.
- **Bitsets.** 201 uses Python's unbounded `int` as a bitset, so `reach[j - 1] << v` is one
  operation. C has no arbitrary-width shift, so it writes `bs_shl` across an array of `uint64_t`
  words, carrying the bits that cross each word boundary, and then sums set-bit positions with
  `__builtin_ctzll`.

## How to reason about it

- **Name the capacities.** Each independent constraint (a sum, a size, a second colour) is an axis
  of the table, and the table's size is the product of the axes. 181 is cheap because both
  capacities are below 100; a third axis would multiply the cost again.
- **Decide 0/1 or unbounded first, then pick the loop direction from it.** A wrong direction still
  gives plausible numbers. Check one tiny case by hand (one item of weight 1, capacity 2: 0/1 gives
  $f[2] = 0$, unbounded gives $1$).
- **Fold each item completely before the next** when counting multisets. Interleaving item types
  counts orderings instead of multisets.
- **Choose the semiring for the question, not the textbook.** If only "unique or not" matters, cap
  the counter (201). If only a residue matters, reduce, and reduce lazily when you know how fast
  the values grow (249).
- **Watch the width.** Unbounded counts grow like partition numbers, exponential in
  $\sqrt{\text{capacity}}$. Know whether you need big integers (181) or a modulus (249) before
  writing the C side.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0249](/solutions/0249/) — Prime Subset Sums

<!-- /problems -->
