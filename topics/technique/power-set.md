<!-- tags: [power-set] -->
<!-- status: final -->
# Power set

The [power set](https://en.wikipedia.org/wiki/Power_set) of an $n$-element set is the set of all
its $2^n$ subsets. Brute force runs into it all the time, but the problems below enumerate it on
purpose, because $n$ is small enough after the right reduction: the elements of a candidate set
(103), the nine digits (118), the multiples of one large prime (152), the distinct prime factors of
a squarefree number (357). The interesting part is *how* the subsets get walked. A counter, a
doubling list, a size-ordered generator and a submask loop all visit the same $2^n$ subsets, at
different costs and with different things available at each step.

## The idea

Number the elements $0, \dots, n - 1$. A subset is then an $n$-bit integer whose bit $i$ says
whether element $i$ is in. That bijection gives $|\mathcal{P}(S)| = 2^n$, and it makes a subset
usable as an array index, a dictionary key, or something to combine with `&`, `|` and `~`. The
bit-level vocabulary is on [mask (computing)](/topics/technique/mask-computing). Two other
bijections matter here:

- **Divisors of a squarefree number are subsets of its primes.** If $n = p_1 \cdots p_k$, each
  divisor picks a subset of the $p_i$, so $n$ has exactly $2^k$ divisors. With $k \le 8$ below
  $10^8$, that is at most 256.
- **Subset sums are a function on the power set.** "All subset sums distinct" (103) is a statement
  about all $2^n$ values at once, and checking it means visiting all of them.

## Four ways to walk it

| walk | shape | cost | used in |
| --- | --- | --- | --- |
| **counter** | `for mask in range(1 << n)`, test each bit | $n \cdot 2^n$ | 103 (C), 152 |
| **by size** | `itertools.combinations(a, r)` for $r = 1, \dots, n$ | $n \cdot 2^n$, small subsets first | 103 (Python) |
| **doubling** | for each element, append (each existing subset + element) | $2^n$, one operation per subset | 357 |
| **submasks** | `sub = (sub - 1) & rem` from `rem` down to 0 | $2^{|rem|}$ per call | 118 |

**Counter.** 152 reduces a subset-sum question to a small group of multiples $k = pm$ of each large
prime $p$. It keeps only the subsets whose $\sum m^{-2}$ vanishes modulo $p^2$. With a handful of
multiples per prime, `for mask in range(1 << n)` with an inner bit test is the simplest correct
code, and its cost is negligible. 103's C checks distinct subset sums the same way, flagging each
sum in a `calloc`'d byte array the size of the total, and stops at the first collision.

**By size.** 103's Python uses `itertools.combinations(a, r)` for growing $r$ and a `set` of seen
sums. It visits the same subsets in a different order: all singletons, then all pairs, and so on.
Order matters when you stop at the first failure. In a set that is almost special, the collision
usually involves small subsets, and enumerating by size finds it early.

**Doubling.** 357 needs every divisor of a squarefree $n$, which means every subset product of its
distinct primes. The list doubles once per prime:

```python
divisors = [1]
for p in prime_factors:
    divisors += [d * p for d in divisors]
```

Each subset costs one multiplication, against $n$ bit tests for the counter. In the C version,
the bound $2^8$ sets the stack array size, `long long divisors[256]`. Doubling also builds subset
*sums* (768 on [meet in the middle](/topics/technique/meet-in-the-middle-attack) does exactly that).
The general rule: when a subset's value can be built from a smaller subset's value, carry the value
instead of recomputing it from bits.

**Submasks.** 118 partitions the digits 1–9 into primes. It precomputes, for every one of the 511
non-empty digit masks, the primes those digits can form. The backtracking then needs, at each
node, every non-empty subset of the digits not yet used:

```python
sub = remaining
while sub > 0:
    ...                              # try the primes keyed by `sub`
    sub = (sub - 1) & remaining
```

`(sub - 1) & remaining` steps to the next smaller submask, skipping every integer that is not a
submask, so the loop runs exactly $2^{|remaining|} - 1$ times. Summed over all masks this visits
$3^n$ (subset, submask) pairs, the standard bound for subset DP. The other half of 118's design is
the precomputed table keyed by mask: the power set becomes an index space, and 511 entries are
cheap.

## Don't expand what you can merge

In 152 the reduced items are not a power set any more. Each has several options, and the halves of
the [meet-in-the-middle](/topics/technique/meet-in-the-middle-attack) split would be products of
option counts. `_expand` therefore never lists subsets. It keeps a `dict` from partial sum to the
number of ways to reach it and folds in one item at a time. Distinct subsets with equal sums merge
into one entry. That is the step from enumerating a power set to dynamic programming over it.
Whenever the question is "how many subsets have property $f$" and $f$ depends on one aggregate,
carry the aggregate, not the subsets.

## Pruning comes before enumeration

103 shows the cost order. Its two special-sum conditions are an $O(n^2)$ check (a bigger subset
has a bigger sum, which only needs the $k$ smallest against the $k-1$ largest, via prefix and
suffix sums) and the $O(2^n)$ distinct-sum check. Solution 1 runs the cheap check first and
enumerates the power set only for candidates that pass. That one swap makes the C 3.6 to 7.8 times
faster than solution 0. When a power-set walk is a filter, put every polynomial filter in front of
it. 357 does the same: the $d = 2$ divisor test rejects almost every candidate with one sieve
lookup before any factorisation or divisor doubling.

## C and Python

- **Generators versus loops.** Python has `itertools.combinations` and list doubling. C writes the
  `1LL << n` counter, or the doubling loop over a fixed array. Both enumerate the same set. The
  C counter does $n$ bit tests per subset, which only matters when $n$ is in the twenties.
- **Seen-sets.** 103's Python keeps a `set` of sums. The C allocates a byte array indexed by sum,
  sized to the total of the set. That is denser and faster, and safe because subset sums are
  bounded by that total.
- **Mask-keyed tables.** 118's Python stores `subset_primes` as a `dict` keyed by mask. The C uses
  two parallel arrays of 512 slots (pointer and count), grown with `realloc` and sorted with
  `qsort`. Direct indexing replaces hashing, which is the natural C form whenever the key is a
  small mask.
- **Shift width.** `1 << n` in C is an `int` shift. 103's C writes `1LL << n` so the counter has
  room. Python's integers make this a non-issue.

## How to reason about it

- **Check that $2^n$ is affordable after reduction.** Nine digits, eight primes, a few multiples:
  fine. Thirty elements: split in half first.
- **Pick the walk by what you need at each subset.** Need the subset's members? Use a counter or
  combinations. Need its sum or product? Use doubling. Need all subsets of a varying mask? Use the
  submask step.
- **Order by size when hunting a counterexample.** Small subsets fail first.
- **Merge equal aggregates.** If only a sum or count matters, a `dict` keyed by the aggregate
  replaces the power set with a DP.
- **Run polynomial filters before exponential ones.**

<!-- problems (generated by update-tags) -->
## Problems

- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0357](/solutions/0357/) — Prime Generating Integers

<!-- /problems -->
