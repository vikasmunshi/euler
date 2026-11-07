<!-- tags: [tuple] -->
<!-- status: final 2026-10-14T17:49Z -->
# Tuple

A [tuple](https://en.wikipedia.org/wiki/Tuple) is a fixed-length, ordered group of values. In
Python it is also immutable, hashable when its elements are, and ordered lexicographically. Those
three properties are why it turns up in so many solutions that never mention it by name. A tuple
can be a dictionary key or a memo key, so it can name a *state*. It compares field by field, so
it can be a *record* that sorts itself. And it is what a comma builds, so it is how a function
hands back several values at once. The three solutions below use one role each, and their C
versions show what each role costs once the language doesn't provide it. This page is part of the
language-idioms series. It covers the idiom, why these solutions use it, and how it looks in the
other language.

## The idea

Python's [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) is the immutable
sequence. Three of its guarantees do the work here:

- **Hashable by value.** `hash((1, 2))` is computed from the elements, and two tuples with equal
  elements are equal and hash the same. That makes a tuple a valid `dict` key, `set` member, or
  [`functools.lru_cache`](https://docs.python.org/3/library/functools.html#functools.lru_cache)
  argument, where a `list` raises `TypeError: unhashable type`. Hashability is inherited, so a
  tuple that contains a list is not hashable either.
- **Lexicographic comparison.** `(a1, b1) < (a2, b2)` compares the first fields and only looks at
  the second ones on a tie, as the
  [comparison rules for sequences](https://docs.python.org/3/reference/expressions.html#value-comparisons)
  specify. So `max` over tuples is "best by the first field, ties broken by the second", with no
  key function and no tie-break code.
- **The comma is the constructor.** `return q, r` returns one tuple, and `q, r = f()` unpacks it.
  The [expression list](https://docs.python.org/3/reference/expressions.html#expression-lists)
  syntax makes packing and unpacking so light that a multi-value return reads like a plain one.

The three problems use these roles:

| Problem | Role | The tuple | What it buys |
|---|---|---|---|
| [27](/solutions/0027/) | record | `(run_length, a * b)` | `max` picks the longest run and carries its product along |
| [93](/solutions/0093/) | memo key | the pool of values still to combine | `lru_cache` shares sub-results across the recursion |
| [145](/solutions/0145/) | state key | `(carry, pending_sums)` | a `dict` merges equal DP states and adds their counts |

**Quadratic primes (27).** The search scores every coefficient pair (a, b) by the length of the
prime run of n² + an + b, and the answer is the product a·b of the winner. The solution never
stores the winning a and b. It builds a record for each candidate and lets `max` pick:

```python
max(
    (prime_run(a, b), a * b),
    (prime_run(a, -b), -a * b),
    (prime_run(-a, -b), a * b),
    (prime_run(-a, b), -a * b),
)
```

and the outer `max(...)[1]` reads the product off the winning record. Field order is
meaning here. The run length comes first because it is what we rank by. The product comes second,
so it only breaks ties and otherwise just rides along. Swap the two and the code still runs, but
it returns the largest product. The sieve in the same file returns `tuple(primes)`. That is a
smaller use of the same type: the result is read-only, and the return type says so.

**Arithmetic expressions (93).** For each set of four digits, the solution finds every value
reachable with `+ − × ÷` and brackets. It does that by repeatedly replacing two values in the
pool with their combination, until one value is left. The pool is the memo key:

```python
@functools.lru_cache(maxsize=None)
def eval_all_operations(vals: tuple[int | float, ...]) -> set[int | float]:
    ...
    r = tuple([vals[k] for k in range(len_v) if k not in (i, j)])
    s |= eval_all_operations(r + (a + b,))
```

The pool has to be a tuple. A list can't be hashed, so `lru_cache` would reject it. And because
the tuple is immutable, `r + (a + b,)` builds a *new* pool rather than changing one a caller
still holds. The same function shows the other two roles in small form: `a, b = (vals[i],
vals[j])` unpacks, `k not in (i, j)` uses a tuple literal as a tiny constant set, and the
best-so-far update `max_length, max_digits, max_results = (length, ..., results)` replaces three
variables in one step. Two details matter for the cache. First, `1 == 1.0` and
`hash(1) == hash(1.0)`, so `(1, 2.0)` and `(1, 2)` are the same key, and integer and float pools
share entries. Second, order is part of a tuple's identity, so `(1, 2, 3)` and `(3, 2, 1)` are
different keys for the same multiset. Sorting the pool before the call would turn those into
cache hits. The search is small enough that the solution doesn't bother.

**Reversible numbers (145).** The count runs a digit DP over each length. Column i and column
d−1−i of n + reverse(n) share the pair sum S, so the state is the carry plus a stack of pair sums
whose partner column hasn't been processed yet. The left half pushes onto that stack and the
right half pops from it. In Python the state is the nested tuple `(carry, pending)`, the table is
a `dict` keyed by it, and the push and pop are slicing:

```python
new_pending = pending + (S,)     # push: a new tuple, the old one untouched
new_pending = pending[:-1]       # pop
new_dp[key] = new_dp.get(key, 0) + ways * cnt
```

This is the core of a counting DP: two paths that reach the same (carry, stack) are the same
state, and the `dict` merges them by adding their counts. Because tuples hash by value, that
merge happens automatically. Copying a tuple on each push would be wasteful for a deep stack, but
this one is at most four entries deep, so the copy costs less than the bookkeeping a mutable
stack would need. `for (carry, pending), ways in dp.items()` unpacks key and count in one header.

## The counterpart in C

C has `struct` and arrays, which can hold a group of values. What it lacks is everything a tuple
does *with* that group. Each solution's C version fills the gap in a different way.

- **Records → parallel arrays and a written-out tie-break (27).** The four sign variants become
  `combos_a[4]`, `combos_b[4]` and `products[4]`. A `struct` would also work. The bigger change is
  the comparison: the C loop spells out `run > best_run`, then `run == best_run` and a
  larger-product check, to *replicate* what Python's tuple ordering does with no code. Any
  record compared by more than one field needs a hand-written comparator in C, just as `qsort`
  does.
- **Memo keys → no memo (93).** A cache keyed by a variable-length array of doubles would need a
  hash function, an equality test and a table, written from scratch. The C version drops the
  memo and recurses directly, which the search over four values can afford. Its result set
  `DoubleSet` is a growing array with a linear-scan duplicate check, a `set` built by hand.
- **State keys → an encoded integer (145).** Here the memo can't be dropped, because merging
  states *is* the algorithm. So the C version turns the tuple into a number: the stack becomes
  base-19 digits plus a length prefix, `len * 19⁴ + Σ sᵢ·19ⁱ`, stored next to `carry` in an
  open-addressed hash table with its own hash function and linear probing. The length prefix is
  the detail to notice. Without it, the empty stack and the stack `(0,)` both encode to 0. A
  Python tuple keeps its length as part of its value, and an encoding has to add it back
  explicitly.
- **Return bundles → out-parameters.** Problem 27's sieve returns `tuple(primes)` in Python. In C
  it returns `int *` and reports the length through `int *count`. That is the usual C answer when
  a function has two results. Returning a small `struct` by value is the other option and reads
  closer to the tuple.

Going the other way, the main risk is overusing the tuple. A record with more than two or three
fields, or one passed far from where it is built, is easier to read as a
[`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) or a frozen
[`dataclass`](https://docs.python.org/3/library/dataclasses.html). Both stay hashable and give the
fields names, which a bare `t[1]` doesn't.

## How to reason about it

- **Choose a tuple when the value has to be a key.** Memo keys, DP states, visited-sets of
  positions: if equal values should collapse to one entry, the value must be hashable, and a
  tuple is the cheapest hashable container for it.
- **Put the ranking fields first.** In a record that `max`, `min` or `sorted` will compare, field
  order *is* the priority order. A payload field placed last costs nothing and comes back with
  the winner, which saves tracking an "argmax" separately.
- **Normalise keys that should be equal.** A memo key that can be written several ways (a pool in
  any order, a state with interchangeable parts) misses the cache once per spelling. Sort it, or
  use a `frozenset` when order and multiplicity both don't matter.
- **Keep immutable stacks short.** `t + (x,)` and `t[:-1]` copy the tuple. For a stack a few
  entries deep that is fine, and the persistence makes DP states safe to share. For a deep or
  long-lived stack, use a list and convert it to a tuple only where it becomes a key.
- **Before porting to C, decide whether the hash map is the algorithm.** If the memo is just a
  speedup (93), try dropping it first. If merging equal states is how the method works (145),
  plan for an encoding with an injective packing (lengths included) and a table to hold it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0145](/solutions/0145/) — Reversible Numbers

<!-- /problems -->
