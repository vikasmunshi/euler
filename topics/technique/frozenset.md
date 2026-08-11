<!-- tags: [frozenset] -->
<!-- status: final -->
# frozenset

A [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset) is a
[`set`](/topics/technique/set) with the mutators removed: the same hash table, the same $O(1)$
average `in`, the same `&` / `|` / `-`, but no `add`, no `discard`, no `update`. The textbook reason
to want one is that it hashes, so it can be a `dict` key or an element of another set. None of the
problems below use it for that. They use it for the other half of the bargain — the guarantee that
the contents will not change — and that turns out to be the more common reason to reach for it.

## The idea

Three jobs, one per problem, in increasing order of how much the immutability matters.

**A membership constant.** Problem 104 asks whether a number's leading and trailing nine digits are
each a permutation of $1..9$. The whole test is a set comparison against a module-level constant:

```python
_PANDIGITAL = frozenset("123456789")

def _is_pandigital_9(n: int) -> bool:
    s = str(n)
    return len(s) == 9 and frozenset(s) == _PANDIGITAL
```

Set equality is doing real work here: with the length already pinned at nine, "the set of digits is
exactly $\{1..9\}$" implies all nine are distinct and none is zero, so one comparison replaces a
sort or a digit tally. The `frozenset` is not required for that — a plain `set` compares equal to a
`frozenset` with the same elements — but it declares at the definition site that this table is
fixed, which is what a module-level constant should say.

**A precomputed rejection table.** Problem 146 hunts for $n$ where $n^2 + \{1,3,7,9,13,27\}$ are all
prime. Before any [primality test](/topics/technique/miller-rabin-primality-test) runs, it kills
candidates with [modular arithmetic](/topics/technique/modular-arithmetic-application): for a small
prime $p$, if $n^2 \equiv -\text{off} \pmod p$ for some offset then $n^2 + \text{off}$ is divisible
by $p$ and cannot be prime. So build, once, the forbidden residues per prime and test with a lookup:

```python
fb17 = frozenset((-o) % 17 for o in offsets)
...
if n2 % 17 in fb17:
    continue
```

The gain is structural, not micro: a six-iteration inner loop over the offsets becomes one hash
lookup, in a loop that runs for every candidate. `frozenset` is right because these tables are built
before the hot loop and never touched again.

Its C sibling is worth putting alongside it, because it shows what the set *is*:

```c
int fb17[17] = {0}, fb19[19] = {0}, fb23[23] = {0};
...
if (fb17[n2 % 17]) continue;
```

A flat array indexed by the residue. Same table, same semantics, no hashing at all — because the key
space here is tiny and dense. A set is a hash table because keys are usually sparse; when they are
not, the array *is* the set, and it is faster ([right tool per cost](/topics/takeaway/right-tool-per-cost)).

**A value handed out by a cache.** Problem 259 is an interval
[DP](/topics/technique/dynamic-programming) over exact rationals: `reachable(i, j)` returns every
value obtainable from the digit run `digits[i:j+1]`, memoised with
[`@lru_cache`](/topics/technique/functools-lru-cache), and the recurrence consumes its own results
in a cross product over every split point. Its signature is

```python
@lru_cache(maxsize=None)
def reachable(i, j) -> frozenset[Rational]: ...
```

and here the `frozenset` is not a preference. A memoised return value is *shared*: every caller of
`reachable(0, 4)` receives the same object. If that object were a mutable `set`, one caller calling
`.add()` on it — or building its result by mutating what it got back — would silently rewrite the
cache for every later caller, and the failure would surface as a wrong total with nothing to point
at. Returning a `frozenset` converts that into an `AttributeError` at the offending line. The body
still uses a mutable `set` while it accumulates, and freezes on the way out:

```python
values: set[Rational] = {...}
for k in range(i, j):
    ...
    values.add(norm(...))
return frozenset(values)
```

That "mutate locally, freeze at the boundary" shape is the pattern; the `lru_cache` just makes
skipping it expensive.

## How to reason about it

- **Freeze at the boundary, not throughout.** Accumulate in a `set`, return a `frozenset`.
  `frozenset` has no efficient incremental build — `fs | {x}` copies the whole table — so building
  one element at a time is quadratic.
- **It is not a faster `set`.** Both are the same C implementation; `frozenset` saves you nothing per
  lookup. Choose it for the contract it publishes, or because you need the hash — never for speed.
- **The hash is lazy but cached.** `hash(fs)` is computed on first use and stored, so the first
  insertion into a `dict` pays $O(n)$ in the set's size and later ones do not. Freezing a set you
  never hash costs a copy for no return.
- **Immutable is not deeply immutable.** `frozenset` of tuples of ints is genuinely fixed; a
  `frozenset` of lists cannot be built at all, since the elements must themselves hash. If elements
  need a [canonical form](/topics/technique/canonical-form) — problem 259 reduces every rational to
  lowest terms with a positive denominator before it goes in — normalise *before* inserting, or
  equal values will occupy separate slots.
- **Build it once, outside the loop.** `frozenset(...)` allocates and hashes every element. Problem
  146's six tables are built before the scan, not inside it; had they been rebuilt per candidate they
  would have cost more than the loop they replaced.
- **When the keys are small and dense, use an array.** The C sibling above is the reminder: a set
  over residues mod 17 is seventeen bytes of direct-addressed table, and no hash function can beat an
  index.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0259](/solutions/0259/) — Reachable Numbers

<!-- /problems -->
