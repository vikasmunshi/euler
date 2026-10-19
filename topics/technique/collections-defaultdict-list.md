<!-- tags: [collections-defaultdict-list] -->
<!-- status: final -->
# collections.defaultdict(list)

[`collections.defaultdict(list)`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
is a dictionary that creates an empty list the first time a missing key is looked up. It gives the
*group-by* idiom in one line:

```python
groups = defaultdict(list)
for item in items:
    groups[key(item)].append(item)
```

No `if key not in groups` check and no `setdefault`. Its usual job in these solutions is
**bucketing**: put many items into groups by a computed key, then examine only the groups that
matter. The three solved problems below bucket by a canonical form (62), by a shared value (142),
and by a spatial cell (212). C has no such container, so each C port has to choose a replacement,
and those choices are the most instructive part of the comparison.

## The idea — group first, then look inside each group

Bucketing replaces a pairwise search with a single pass. "Find items that agree on some property"
naively compares all $\binom{n}{2}$ pairs. With a key function that maps items to the same key exactly when they agree,
one $O(n)$ pass puts every candidate pair into the same group, and the pairwise work happens only
*within* groups, which are usually tiny. Three ways to choose the key:

| key | example | what it captures |
|---|---|---|
| a canonical form | sorted digits of a number | "is a permutation of" |
| a computed value | $a^2 + b^2$ | "represents the same number" |
| a coarse cell | `(x // 400, y // 400, z // 400)` | "close enough to possibly interact" |

The value type matters too. `list` keeps every member, in insertion order, with duplicates. Use
`defaultdict(int)` or [`Counter`](/topics/technique/collections-counter) when only the group sizes
matter, and `defaultdict(set)` when duplicates must collapse.

## Three groupings across the problems

**62, cubic permutations: key by canonical form.** Two cubes are digit permutations of each other
exactly when their sorted digit strings are equal, so `"".join(sorted(str(c)))` is a
[canonical form](/topics/technique/canonical-form). The public solution groups each digit-length
band of cubes and looks for a group of exactly five:

```python
permuted_cubes: dict[str, list[int]] = collections.defaultdict(list)
for cube_number in cube_numbers:
    permuted_cubes["".join(sorted(str(cube_number)))].append(cube_number)
solutions = set(min(v) for k, v in permuted_cubes.items() if len(v) == num_permutations)
```

Grouping a whole band before testing matters. "Exactly five" can only be decided once no more
members can arrive, and permutations always share a digit count, so the end of a band is that point.

**142, perfect square collection: key by a shared value.** The substitution $a^2 = x+y$,
$b^2 = x-y$, $c^2 = x+z$, $d^2 = x-z$ turns four of the six conditions into "$2x$ is a sum of two
squares in two ways", with each pair of the same parity. The solution enumerates same-parity pairs
$(a, b)$ once, appends each to `reps[a*a + b*b]`, and then visits only the keys with at least two
pairs, testing the remaining two conditions there. The group-by turns a triple loop over $x, y, z$
into a near-linear sweep. It is the same move as [meet in the middle](/topics/technique/meet-in-the-middle-attack):
compute one side, index it by the value, and join.

**212, combined volume of cuboids: key by a spatial cell.** To find which earlier cuboids can
overlap a new one, space is cut into cells of side 400, just over the largest cuboid side of 399. Each cuboid is appended to
`buckets[(bx, by, bz)]` for every cell it touches, at most eight. Overlap candidates are then
the union of a few buckets, collected into a `set` because one cuboid can share several cells with
the new one. That is a [grid spatial index](/topics/technique/grid-spatial-index), built from a
`defaultdict(list)` keyed by tuples.

One caution from 212. Reading `buckets[cell]` for a cell nobody has used **inserts** an empty list.
The candidate loop probes cells before the new cuboid is added, so the dictionary fills with
empty entries for every cell probed. Here that costs nothing, since at most about $26^3$ cells exist, but in a
sparse, unbounded key space it is a memory leak. Read with `buckets.get(cell, ())` when you do not
mean to create.

## Python and C — three replacements for one container

| problem | key space | C replacement |
|---|---|---|
| 62 | sparse strings | chained hash table: 65536 buckets, djb2 hash, each entry a `realloc`-doubled `long long` array |
| 142 | sparse integers, all known up front | **no map at all**: push `(s, a, b)` triples into one array, `qsort` by `s`, scan runs of equal `s` |
| 212 | dense, small ($32^3$ cells) | flat `calloc`'d array of growable `int` lists indexed by `(bx*32 + by)*32 + bz`, and a `seen[]` array stamped with the current index instead of a set |

Each is the right C answer for its key space. A real hash table is needed when keys are arbitrary
strings that arrive online (62). Sort-and-scan is simpler and cache-friendly when all keys are
known before any group is read (142), at $O(n \log n)$ instead of $O(n)$. Direct indexing wins when the
keys are small integers or tuples with a known bound (212), because then there is no hashing at all. In Python, one
`defaultdict(list)` covers all three cases.

## How to reason about it

- **Turn "find items that agree" into "group by a key".** If you can write a function that maps
  equivalent items to the same key, one pass replaces a pairwise search.
- **Choose the key carefully.** Canonical forms for permutations and rotations, computed values for
  "same sum" joins, and coarse cells for spatial proximity.
- **Decide group membership only when the group is complete.** Count-based conditions such as
  "exactly five" need every member present (62's digit-length bands).
- **Do not read a defaultdict without meaning to create.** Use `.get()` for probes.
- **In C, choose by key space.** Use direct indexing if bounded, sort-and-scan if offline, and a hash table only when
  keys are sparse and arrive online.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids

<!-- /problems -->
