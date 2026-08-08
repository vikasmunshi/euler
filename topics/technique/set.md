<!-- tags: [set] -->
<!-- status: final -->
# set

Python's [`set`](https://docs.python.org/3/library/stdtypes.html#set) is a
[hash table](/topics/technique/hash-table) with the values thrown away: keys only, average $O(1)$
for `in`, `add` and `discard`, and the [algebra of collections](https://en.wikipedia.org/wiki/Set_(abstract_data_type))
on top. Across the problems below it does four jobs that have almost nothing to do with each other,
and the reason it earns a tag of its own is that recognising *which* job you are asking of it is
what tells you whether a `set` is the right container at all.

## The four jobs

**Membership.** The same "have I seen this?" question, asked many times against a collection that
barely changes. Problem 37's truncatable primes is the clean case — primes arrive in increasing
order, so every proper truncation of a candidate has already been added, and the whole predicate is
a handful of lookups. Problem 35 sieves primes into a set so that testing all rotations of a
candidate is $O(\text{digits})$ rather than $O(\text{digits} \cdot \sqrt N)$. Problem 95 walks the
$n \mapsto s(n)$ functional graph and uses a set of the current path to notice when it closes:

```python
ch, c, path = ({i}, divisor_sum[i], [i])
while i <= c <= max_num and c not in ch:
    ch.add(c)
    path.append(c)
    c = divisor_sum[c]
```

The tell is a lookup inside a loop. A `list` here would turn each $O(1)$ probe into an $O(n)$ scan,
and the loop is where you would never notice.

**Deduplication.** The word "distinct" in the statement. Problems 32, 87, 141, 203, 346 and 757 all
enumerate over a parametrisation that reaches the same value by several routes, and the answer is
`sum(set(...))` or `len(set(...))`. This is the cheapest correctness insurance in
[generate and test](/topics/technique/generate-and-test): a double count produces a plausible wrong
number rather than a crash.

**A canonical key.** Here the element stored is not the object but a fingerprint that collapses an
equivalence class, so that "equal under this relation" becomes "equal as a key" — the set is doing
the work of a [canonical form](/topics/technique/canonical-form). Problem 52 wants an $x$ whose
multiples $x, 2x, \dots, Mx$ are all digit permutations of one another, and the whole test is that
the set of sorted-digit fingerprints has size one:

```python
if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
```

A set of size one says *all the same*, with no pairwise comparison written anywhere. Problem 49
groups $n$-digit primes into permutation families the same way; problem 32 tests pandigitality with
`set(str(n)) == set_nine_digits`, letting set equality stand in for a digit histogram.

**The algebra.** Union, intersection and difference as the actual computation rather than a
convenience. Problem 155 counts distinct capacitances reachable with $n$ identical capacitors: for
each $k$ it takes every unordered split $(i, k-i)$, forms the parallel and series combinations of the
values already known, and the answer is the size of the union over all $k$. Problem 143 stores
adjacency as sets and finds triangles by intersecting neighbourhoods. Problem 122 keeps a `remaining`
set of exponents not yet reached and shrinks it as an iterative-deepening search first attains each
one — the set *is* the loop's termination condition.

## How to reason about it

- **Hashable means you must choose a representation, and that is the point.** Elements must be
  immutable, so tuples and `frozenset`s qualify and lists do not. Problem 155 stores reduced
  $(\text{num}, \text{den})$ integer pairs rather than floats precisely so that equal capacitances
  collide exactly; a set of floats would silently keep two entries for one value, or merge two
  values, depending on the last rounding — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality). When the natural
  element is itself a collection, `frozenset` is the hashable form and can be a set element or a dict
  key.
- **`in` on a list is $O(n)$.** This is the single performance bug the tag most often fixes, and it
  is invisible in a profile-free reading because the code looks identical. Note the legitimate
  exception: problem 64 detects the period of a continued fraction with `(m, d, a) in p` against a
  *list*, because it needs the order for the length and the periods are short. When both are true,
  keep the list; when the collection grows, keep a set beside it.
- **Set, dict, or bit array.** If you need a value alongside the key it was always a
  [dict](/topics/technique/hash-table). If the keys are small dense integers, a
  [bit array](/topics/technique/bit-array) or `bytearray` wins by an order of magnitude:
  `set(range(10**7))` is about 270 MB of hash table plus the integer objects themselves, against
  10 MB for `bytearray(10**7)`. Membership sets over a sieve range are the common place to get this
  wrong — see [size work to the input](/topics/takeaway/size-work-to-the-input).
- **A set has no order, and you will want one at the end.** Sets iterate in an unspecified order that
  is not insertion order, so any problem asking for the smallest, the largest or a listing pays a
  sort on the way out. That is usually the right trade — deduplicating on the way in is cheaper than
  sorting a much longer list on the way out — but budget for it.
- **Build it in one pass.** A set comprehension and `set(<generator>)` are the same thing and both
  beat `s = set()` plus a loop of `add`. Sizing it inside `solve()` rather than at module level keeps
  the construction cost inside the benchmark, which is where it belongs.
- **It is the biggest single cost of translating to C.** C has no associative container, so every
  one of these jobs must be rebuilt. Problem 142's C sibling collects all its candidate triples,
  sorts them, and scans runs of equal keys to recover the grouping a Python set gave for free;
  problem 141's C hand-rolls a power-of-two hash table just to deduplicate. When a Python solution
  is three lines and its C counterpart is eighty, a set is usually the reason — see
  [parity across languages](/topics/takeaway/parity-across-languages).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0757](/solutions/0757/) — Stealthy Numbers

<!-- /problems -->
