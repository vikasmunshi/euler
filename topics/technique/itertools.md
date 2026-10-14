<!-- tags: [itertools] -->
<!-- status: final 2026-10-14T17:33Z -->
# itertools

A good half of Project Euler is "try every arrangement, keep the ones that pass" —
[generate-and-test](/topics/technique/generate-and-test) — and in Python the *generate* half is
almost always one call into [`itertools`](https://docs.python.org/3/library/itertools.html). The
problems below each pick the combinatoric iterator whose shape matches the search space: ordered
or unordered, with or without repetition, one pool or several. Picking the right one is half the
algorithm, because the shape decides how many candidates exist; the other half is not undoing the
laziness that makes these iterators cheap.

## The idea

`itertools` gives four combinatoric generators, and each is a different counting formula:

| Call | Yields | Count from $n$ items | Used by |
| --- | --- | --- | --- |
| [`permutations(p, r)`](https://docs.python.org/3/library/itertools.html#itertools.permutations) | ordered, no repeats | $n!/(n-r)!$ | 32, 49, 68, 118 |
| [`combinations(p, r)`](https://docs.python.org/3/library/itertools.html#itertools.combinations) | unordered, no repeats | $\binom{n}{r}$ | 49, 163 |
| [`combinations_with_replacement(p, r)`](https://docs.python.org/3/library/itertools.html#itertools.combinations_with_replacement) | unordered, repeats allowed | $\binom{n+r-1}{r}$ | 30, 34 |
| [`product(p, q, …)`](https://docs.python.org/3/library/itertools.html#itertools.product) | one from each pool | $\lvert p\rvert \cdot \lvert q\rvert \cdots$ | 98 |

plus the unbounded [`count()`](https://docs.python.org/3/library/itertools.html#itertools.count)
(problem 76 walks Euler's pentagonal recurrence with `for n in itertools.count(1)` and breaks
when both terms vanish) and [`accumulate()`](https://docs.python.org/3/library/itertools.html#itertools.accumulate),
the streaming [prefix sum](/topics/technique/prefix-sum).

**Match the iterator to what the predicate can see.** Problems 30 and 34 test whether a number
equals the sum of a function of its digits. That sum does not depend on digit *order*, so the
search space is digit [multisets](/topics/technique/stars-and-bars-combinatorics), not numbers:

```python
for digits in itertools.combinations_with_replacement(range(10), upper_bound_num_digits)
    if (num := sum((x**n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))
```

For problem 30's six-digit bound that is $\binom{15}{6} = 5005$ candidates instead of $10^6$ —
each multiset yields its one possible sum, and the round trip through `str(num)` checks that the
sum is spelled by those digits. Leading zeros make a fixed length cover every shorter number too;
problem 34 loops the lengths instead, because $0! = 1$ means a zero is not free.

Where order *does* matter, `permutations` is the tool. Problem 68 enumerates only the inner ring
of the 5-gon — `permutations(range(1, 10), 5)`, 15 120 tuples — and forces every outer node from
the line-sum constraint. Problem 49 takes `permutations(prime)` over a four-digit string to find
its prime siblings, then `combinations(siblings, 2)` to bucket pairwise differences.
Problem 118 tabulates, for each 9-bit subset of the digits 1–9, every prime its permutations form,
and problem 163 picks three of the six line directions with `combinations(families, 3)` before
intersecting their members.

**Nesting is where a generator beats `product`.** Problem 32 needs two operands with disjoint
digits. `product` cannot express that, so it nests, drawing the inner pool from what the outer
choice left:

```python
for a in itertools.permutations(nine_digits, a_len)
for b in itertools.permutations((d for d in nine_digits if d not in a), b_len)
```

## Materialising versus streaming

These iterators are lazy: each yields one tuple, recycling its internal index array, and holds
$O(r)$ state however large the count. A generator expression over them is a pipeline with no
intermediate list, and `return` or `break` stops it mid-stream. Problem 98 relies on that —
`product(candidate.dictionary_words, square_numbers)` never builds the $|\text{words}| \times
|\text{squares}|$ pairs; the loop returns at the first anagramic square, longest length first.

Three things materialise anyway, and each needs a reason:

- **The inputs.** `permutations` and `combinations` call `tuple()` on their argument; `product`
  converts *every* argument up front. Passing a huge generator to `product` costs its full memory
  before the first output. That is fine here — pools of ten digits or a few thousand squares —
  but it is why `product` cannot replace problem 32's nested loop, where the inner pool depends on
  the outer value.
- **Deduplication.** `permutations` treats *positions* as distinct, not values: the permutations of
  `"1487"` are 24 strings, but those of `"1117"` are also 24, with heavy repetition. Problem 49
  wraps its stream in `set(...)` for that reason, and problem 32 collects products in a set
  because the same product arises from several factor pairs. Materialise to dedup, and only the
  survivors — not the raw stream.
- **Random access.** Problem 50 (outside this tag) builds `[0] + list(itertools.accumulate(primes))`
  because it then indexes `prime_sums[j] - prime_sums[i]` for many pairs; a prefix sum you only
  walk once should stay a stream.

`list(permutations(...))` "to be safe" is the anti-pattern: $10!$ tuples is 3.6 million objects,
a few hundred megabytes, for a loop that wanted one at a time.

## The C counterpart

C has no `itertools`, so each solution writes its enumerator by hand — and the two ends of the
trade-off show up plainly.

The **streaming** end is a successor function on an index array, which is exactly what CPython
does internally (the docs give the equivalent Python). Problem 30's C advances a non-decreasing
array in place — the multiset odometer behind `combinations_with_replacement`:

```c
int pos = k - 1;
while (pos >= 0 && indices[pos] == 9) pos--;
if (pos < 0) break;
int val = indices[pos] + 1;
for (int i = pos; i < k; i++) indices[i] = val;
```

$O(k)$ memory, no allocation per candidate. `combinations(families, 3)` in problem 163 becomes
three nested loops with $i < j < k$, which is the same thing unrolled.

The **materialising** end is problem 49's C, which runs
[Heap's algorithm](/topics/technique/heaps-algorithm) to write all $n!$ permutations into a buffer
and then filters. At $n = 4$ that is 24 rows and irrelevant; it would not survive $n = 10$.

The third shape is **recursion with a `used[]` array** — problem 68's and 118's C. It yields the
same tuples as `permutations`, but it has a point between depths where a partial arrangement can
be rejected. A flat itertools stream only lets you test complete tuples. When the constraint can
fail early, [backtracking](/topics/technique/backtracking) prunes whole subtrees that `permutations`
must enumerate leaf by leaf — the one place the hand-written C is *structurally* better, not just
faster.

## How to reason about it

- **Count before you loop.** Write down $n!/(n-r)!$ or $\binom{n+r-1}{r}$ first. Pure-Python
  iteration costs on the order of a microsecond per tuple once the body does any work, so a few
  million is the practical ceiling; past that, change the shape, not the language.
- **Drop the order the predicate ignores.** If the test is symmetric in the elements, `combinations`
  or `combinations_with_replacement` cuts the space by up to $r!$ — the
  [canonical form](/topics/technique/canonical-form) of each candidate is the sorted one, and the
  iterator emits only those.
- **Output order is lexicographic in input positions.** Sort the input and the stream is
  [lexicographically](/topics/technique/lexicographic-order) sorted, which supports early exit
  ("first hit is the smallest") at no cost.
- **Stream by default; materialise to dedup or index.** And when you must, materialise the
  filtered result, not the raw combinatoric stream.
- **Need pruning? Recurse instead.** `itertools` is the right tool when every candidate must be
  scored anyway; when prefixes can be rejected, a hand-written recursion in either language beats it.
- **Build inside `solve()`.** The enumeration *is* the cost being timed — never hoist it to module
  level ([size work to the input](/topics/takeaway/size-work-to-the-input)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0163](/solutions/0163/) — Cross-hatched Triangles

<!-- /problems -->
