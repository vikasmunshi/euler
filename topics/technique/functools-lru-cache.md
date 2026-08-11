<!-- tags: [functools-lru-cache] -->
<!-- status: final -->
# functools.lru_cache

[`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache) is
[memoization](/topics/technique/memoization) as a one-line decorator: it wraps a function in a dict
keyed on the call arguments, and returns the stored result on a repeat. It appears on more solutions
below than almost any other library device, because the shortest correct statement of a
counting problem is usually a recurrence, and a recurrence written literally re-computes the same
subproblem an exponential number of times. The decorator is what makes the literal statement
affordable — which is the whole appeal, and also the trap: it makes a *bad* recurrence affordable
too, and then you stop looking for the good one.

## The idea

```python
@functools.lru_cache(maxsize=None)
def collatz_length(number: int) -> int:
    if number == 1:
        return 1
    if number % 2 == 0:
        return 1 + collatz_length(number // 2)
    return 1 + collatz_length(3 * number + 1)
```

That is problem 14 entire. Without the decorator it is an $O(n \cdot L)$ walk that re-descends every
[Collatz](/topics/domain/collatz-conjecture) tail once per start; with it, every chain length in the
[functional graph](/topics/domain/functional-graph) is computed once and shared by everything
downstream of it.

`maxsize=None` means never evict, which is what a dynamic program wants — the point is that the
table survives to be hit, and eviction can only turn a hit into recomputation.
[`functools.cache`](https://docs.python.org/3/library/functools.html#functools.cache) is the
identical thing under a shorter name, with the LRU bookkeeping compiled out. A finite `maxsize` is
for a genuinely hot subset of an unbounded key space, which is a service's problem, not a solver's.

Arguments must be **hashable**, and the key is the whole argument pattern. Two consequences that
bite: `f(3)` and `f(x=3)` are *different* cache entries, so a memoised recursion should call itself
one way consistently (problems 76 and 77 use keyword-only parameters throughout, which settles it);
and a list argument is a `TypeError`, which is why memoised states in these solutions are tuples,
`frozenset`s, or plain integers.

## The three shapes it takes

**Top-down dynamic programming.** The dominant use, and the reason the tag is dense. Write the
recurrence honestly, decorate it, and the memo table builds itself in whatever order the recursion
happens to need — no thinking about a topological order, no bottom-up loop bounds. The state is
whatever the arguments are: `(position, previous bit, tight)` for the
[digit DP](/topics/technique/digit-dp) that counts fibbinary numbers in problem 301 and the
three-coordinate variant in problem 1000; `(index, budget)` for the branch-and-prune subset count in
problem 755; `(cell, frontier mask)` for the [broken-profile](/topics/domain/broken-profile) tiling
count in problem 161; `(i, j)` for the interval DP over exact rationals in problem 259; and
`(number, largest allowed part)` for the partition counts in problems 76 and 77. Different problems,
one skeleton — the recurrence is the design work, and the decorator is the implementation.

**A pure function called with repeats.** Here the cache is not the algorithm, only deduplication:
problem 42's word-to-value scorer, problem 60's `concatenate_is_prime(a, b)` edge predicate memoised
across a [clique](/topics/domain/clique-problem) search that revisits the same pairs constantly, or
the generalised-pentagonal helper in problems 76 and 78. Cheap to add, occasionally the difference
between a search finishing and not.

**A cache built inside `solve()`.** Problems 14, 21, 161, 259, 301, 755 and 1000 decorate a
*closure*, defined within `solve()`, capturing the parsed input:

```python
max_num = runner.parse_int(args[0])

@functools.lru_cache(maxsize=None)
def sum_factors(n: int) -> int:
    ...
```

This is correctness first and benchmark honesty second. Correctness, because a closure's results
depend on what it captured — a module-level table would answer a later call with a value computed
under a different bound. Honesty, because of how this repository measures: `--runs=N` times repeated
calls to `solve()`, so a module-level cache is *warm* from the second run onwards and the reported
average is the cost of dict lookups rather than of the algorithm. Problem 17 keeps its speller at
module level and handles this explicitly with `number_triplet_in_words.cache_clear()` as the first
statement of `solve()`; problem 77 does neither, so its recorded average is a warm-cache figure and
understates the real work. Problem 1000 shows the third reason to scope a cache: its inner
recursion is re-created (and `cache_clear()`ed) per outer parameter, because the captured parameter
is part of the state and keeping the entries would be simply wrong.

## What memoization does not fix

Problem 76 computes one number — the partition count $p(n)$ — two ways, both memoised with this same
decorator. The naive `(number, largest part)` recursion takes `0.798 s` at $n = 1000$. Euler's
[pentagonal-number recurrence](/topics/domain/pentagonal-number-theorem), which sums only
$O(\sqrt{n})$ terms per value, takes `0.0008 s`. A thousandfold, with the caching held constant.

The cache removes *repetition*; it cannot shrink the state space, and the state space is the
complexity. If `cache_info()` reports a healthy hit rate and the program is still slow, the
recurrence is the problem ([reduce before coding](/topics/takeaway/reduce-before-coding)). Problem
76's third solution makes the neighbouring mistake — it memoises a function that returns the actual
*list* of partitions rather than their count, and overflows on inputs the counting version handles
instantly. Cache the number you need, not the objects it came from.

## How to reason about it

- **Choosing the arguments is choosing the state.** Every parameter joins the key, so a redundant one
  multiplies the table and a missing one is a correctness bug. Arguments that are logically identical
  but differently spelled miss the cache: problem 93 memoises on a tuple of remaining values that is
  never canonicalised, so the same pool in a different order is a fresh entry — sorting the tuple
  first would collapse whole families of them ([canonical form](/topics/technique/canonical-form)).
- **Never mutate what the cache handed you.** The stored object is shared with every future hit.
  Problem 93 returns a `set` and builds its result with `s |= …` into a *new* set, which is safe; an
  `.add()` on a returned value would silently corrupt the table for every later caller. Returning an
  immutable value removes the hazard entirely — problem 259 returns a `frozenset` for exactly that
  reason.
- **Be careful with float keys.** Problem 93's pools hold floats, where `1` and `1.0` hash equal and
  share an entry — harmless there, but in general two values that ought to be equal can round to two
  different keys and split the table
  ([exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality)).
- **Top-down memoization is recursion.** It inherits Python's ~1000-frame limit. Problem 14 recurses
  once per Collatz step and the longest chain below $10^7$ is 685 steps — inside the limit, but not
  by a comfortable margin. Where every state will be visited anyway, the bottom-up form (a list
  filled in order, as in problem 78) uses no stack, needs no hashing, and is usually faster; the
  top-down form wins when the reachable state space is far smaller than the nominal one.
- **`cache_info()` is the diagnostic.** Hits, misses and current size, for free. A low hit rate means
  the key is too fine — you are caching things you never ask for twice. A `currsize` climbing into
  the millions means the table, not the computation, is your memory profile.
- **It does not cross into C, and that matters both ways.** Problem 14's C sibling replaces the
  decorator with a flat array indexed by $n$ — [direct addressing](/topics/technique/direct-addressing),
  the right answer whenever keys are small integers — and runs 44 times faster than the Python.
  Problem 93's C sibling instead drops memoization altogether, and is four times *slower* than the
  memoised Python it mirrors, `0.023 s` against `0.005 s`. One decorator outweighs the entire
  language gap ([a better algorithm beats a faster language](/topics/takeaway/algorithm-beats-language)),
  which is worth knowing before you assume the port will be an improvement
  ([parity across languages](/topics/takeaway/parity-across-languages)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0161](/solutions/0161/) — Triominoes
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0301](/solutions/0301/) — Nim
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
