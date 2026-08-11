<!-- tags: [canonical-form] -->
<!-- status: final -->
# Canonical form

A [canonical form](https://en.wikipedia.org/wiki/Canonical_form) is one chosen representative for
everything that ought to count as the same thing. Pick it well and "are these two objects
equivalent?" — a question that can be expensive, or arbitrarily deep, or about numbers too large to
write down — collapses into "are these two keys equal?", which a hash table answers in a probe. The
technique recurs below because the problems keep asking for *distinct* things, or for things
*grouped* by a relation, and the word "distinct" in a Project Euler statement is almost always an
instruction to go find the right key.

## The idea

Start from an [equivalence relation](/topics/domain/equivalence-relation) $\sim$ on some set of
objects: digit permutations of each other, rationals with the same value, board positions that
differ only by relabelling. A canonicalisation is a function $c$ with

$$c(x) = c(y) \iff x \sim y,$$

so the equivalence classes are in bijection with the values $c$ takes. Once you have it, everything
downstream is plumbing: `len({c(x) for x in items})` counts the classes, and a
[dict](/topics/technique/hash-table) keyed on $c(x)$ partitions the items into them.

The two halves of that `iff` are worth naming separately, because a key that satisfies only one is a
different tool. **Soundness** ($x \sim y \Rightarrow$ equal keys) alone gives a *fingerprint*: it
never separates things that belong together, but distinct keys may collide, so a match has to be
confirmed by a real comparison. Adding **completeness** (equal keys $\Rightarrow x \sim y$) is what
makes it a canonical form and lets you skip the confirmation entirely. Every use below is complete;
that is the point of the effort.

Five shapes cover the problems on this page.

**Sort the parts.** When the relation is "same multiset", sorting *is* the canonicalisation.
Problem 52 asks for the smallest $x$ whose first six multiples are digit permutations of one another,
and the whole test is one line:

```python
if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
```

Six numbers are permutations of each other exactly when their sorted-digit strings collapse to a set
of size one. Problem 62 uses the identical key in the other direction — as a `defaultdict` key that
groups cubes into permutation families, so the family of the right size falls out without any pairwise
comparison. The [anagram](/topics/technique/anagram) case is the same key applied to letters.

**Factor into an invariant.** Sometimes the objects are too big to compare and the canonical form is
also a compression. Problem 29 counts distinct $a^b$; at $a = b = 1000$ the values run to three
thousand decimal digits. But by the
[fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic),
$a = \prod p_i^{e_i}$ gives $a^b = \prod p_i^{e_i b}$, and two powers are equal exactly when those
prime-exponent maps agree:

```python
signature = tuple(((prime, power * b) for prime, power in prime_factors))
```

A handful of small integers now decides equality of two thousand-digit numbers. The
[factorisation](/topics/technique/integer-factorization) is not the answer — it is the key.

**Normalise away representational slack.** A representation with more freedom than the value it
denotes needs a rule fixing the freedom. Rationals are the standard case: problem 259 reduces every
fraction it produces to lowest terms with a positive denominator, immediately on construction, so
that equal values are literally the same pair and a `frozenset` of them de-duplicates correctly.
Problem 165 does the same for a point in the plane — an intersection is kept as an integer triple
$(n_x, n_y, d)$ meaning $(n_x/d,\ n_y/d)$, divided through by $\gcd(|n_x|, |n_y|, d)$ with $d > 0$ —
and the answer is the number of distinct triples. Problem 89 is the purest instance: Roman numerals
admit several valid spellings per number, the minimal spelling is the canonical one, and the answer
*is* the total slack, measured by parsing each numeral to an integer and re-encoding it greedily.

**Quotient by a symmetry.** When a relabelling group acts on your objects, the canonical form of an
object is a fixed choice from its orbit — conventionally the minimum. Problem 61 stores each cycle it
finds as `tuple(sorted(path))`, which is identical for all rotations of the same cycle. Problem 177
counts quadrilaterals up to similarity, where relabelling the vertices generates the
[dihedral group](https://en.wikipedia.org/wiki/Dihedral_group) $D_4$ of order 8; it generates all
eight relabellings of each accepted angle tuple and keeps the lexicographically smallest. Problem 68
shows the alternative, and the better one where it is available: rather than generating duplicates
and folding them afterwards, it *pins* the smallest free value at position 0 during generation, so no
two rotations of a ring are ever produced in the first place.

**Encode a state.** In the [state-space searches](/topics/technique/breadth-first-search) the
canonical form is the visited-set key, and it must be exact in both directions — one integer per
position, never two. Problem 244's sliding puzzle has coloured rather than numbered tiles, so tiles
of a colour are interchangeable and $16!/2 \approx 10^{13}$ permutations collapse to about $10^5$
distinct boards; a board is packed as the blank's cell index shifted left over a sixteen-bit mask of
the red cells, with the blank's own bit forced to zero so a single board cannot have two encodings.
That collapse is not an optimisation — it is the reason the problem is searchable at all. Problem 254
is the same move at the level of the answer: numbers with the same digit multiset share the value of
$f$, so the search runs over multisets, and the smallest number realising one is that multiset
written in ascending order.

One variant is worth separating out. Problem 54's `HandRank` — a `(category, tie-breakers)` pair with
tie-breakers ordered most-significant first — is a canonical form for *comparison* rather than
equality: it maps each poker hand to a key whose natural ordering reproduces the rules of the game,
so "which hand wins" becomes `>`. The discipline is identical; the target is a total order instead of
a partition.

## How to reason about it

- **"Distinct", "up to", "non-similar", "the same shape" are the tell.** Any of those phrases in a
  statement means the objects you can generate outnumber the objects you are being asked to count,
  and the gap is an equivalence relation. Name it before you write the loop.
- **Prefer not generating duplicates to removing them.** Canonicalising an orbit costs $|G|$ work per
  object and you paid to generate the duplicates first. If a constraint can be pinned during
  generation — problem 68's smallest node first, problem 254's digits in ascending order — the
  canonical form becomes an invariant of the search rather than a filter on its output.
- **Choose the cheapest key that is still complete.** Sorting $d$ digits into a string is
  $O(d \log d)$; a ten-element digit-frequency count is $O(d)$ and just as exact. When a grouping is
  the bottleneck, look at the key before you look at the table.
- **Floating point has no canonical form.** Two computations of the same point disagree in the last
  bits, and equal things compare unequal — which is exactly the failure that destroys a distinct
  count. Problems 165 and 259 both stay in exact integers or reduced rationals for precisely this
  reason. If the natural key is a real number, find an integer one.
- **Normalise on construction, not at comparison.** A rational reduced when it enters the set is
  reduced for every subsequent lookup; a rational reduced at comparison time has to be reduced again
  at every comparison, and one forgotten path silently admits a duplicate.
- **Handle the degenerate representative explicitly.** $0/1$ and $0/{-3}$, $d < 0$, a leading zero, an
  empty factorisation for $n = 1$: the cases where the normalising rule has nothing to bite on are
  where two encodings of one object survive. They are also the cases the small test input does not
  contain.
- **In Python the key must be hashable, which means immutable** — `tuple`, `frozenset`, `str`.
  In C nothing enforces it and there are no composite keys at all, so the same signature is serialised
  into a string (problem 29 writes `"2:6,5:3"`) or packed into a single integer (problem 244's board).
  Packing is much the better option when the state is small and bounded: it makes the key an array
  index and removes the [hash table](/topics/technique/hash-table) from the problem entirely.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0165](/solutions/0165/) — Intersections
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0244](/solutions/0244/) — Sliders
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0259](/solutions/0259/) — Reachable Numbers

<!-- /problems -->
