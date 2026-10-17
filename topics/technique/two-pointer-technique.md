<!-- tags: [two-pointer-technique] -->
<!-- status: final 2026-10-17T06:37Z -->
# Two-pointer technique

The [two-pointer technique](https://en.wikipedia.org/wiki/Two-pointer_technique) keeps two
indices into an ordered sequence and moves each of them in one direction only. If neither pointer
ever goes back, the pair of loops that looked like $O(n^2)$ costs at most $2n$ steps in total. It
is rarely the idea a problem is built around. Its usual job is the last step: something else has
put the data in order (a sort, an angular ranking, a monotone formula), and the two pointers turn
that order into a linear scan. In the problems below it does that job in three settings: a
nearest-sum search after a [meet in the middle](/topics/technique/meet-in-the-middle-attack), a
merge of sorted lists, and a rotating window over points sorted by angle.

## The idea

Both pointers walk one ordered sequence. The technique stands on one claim: **when a pointer
moves past a position, no answer that still needs that position is left**. Monotonicity is what
makes the claim true. Three shapes keep coming up.

**Converging pointers.** One index starts at each end and they walk toward each other. The
textbook case is pairs with a given sum in a sorted array: if `a[i] + a[j]` is too large, then
`a[j]` paired with any later `i` is larger still, so `j` can step down for good. The simplest
case is the palindrome test in the C side of [Problem 4](/solutions/0004/), which compares
characters from both ends of the digit string:

```c
for (int i = 0, j = len - 1; i < j; i++, j--) {
    if (buf[i] != buf[j]) return 0;
}
```

The Python twin gets the same check from `str_number == "".join(reversed(str_number))`. It
builds a reversed copy, does a full comparison, and leaves the walk to the runtime. For a
six-digit number that is the right call. It shows the pattern that runs through this whole
page: the pointer walk is the C idiom, and Python usually reaches for a built-in or a vectorised
call that does the same job some other way.

**Same-direction merge.** Two pointers walk two sorted lists, and on each step the smaller head
moves forward. This is the merge step of
[merge sort](https://en.wikipedia.org/wiki/Merge_sort), and with a different action on equal
heads it intersects the lists or takes their union. It runs in $O(|A| + |B|)$ and needs no hash
table.

**Chasing pointers (a sliding window).** Both indices move forward. `i` is a left anchor and
`j` is the first position that breaks some condition relative to `i`. When `i` advances, the
condition gets looser or stays the same, so `j` never has to step back. Every `i` gets its window
`[i, j)` for a total of $O(n)$ work. This shape needs the monotonicity to be argued, not just
assumed. It is also where the edge cases are.

## How the solutions use it

**Nearest sum to a target ([461](/solutions/0461/)).** A four-index search over
$f(a) + f(b) + f(c) + f(d) \approx \pi$ becomes a two-index one through
[meet in the middle](/topics/technique/meet-in-the-middle-attack): every pair sum is enumerated
and the pairs are sorted by sum. What's left is to find the two pair sums whose total is closest
to $\pi$. That is the converging shape. As `i` walks up the sorted sums, the target
$\pi - s_i$ goes down, so the matching `j` walks down and never comes back. Two details matter.
The pointer stops at the last sum that does not overshoot, so the nearest candidate is either
`j` or `j+1`, and the C code checks both. The search also stops as soon as the target goes
negative. The Python side does not walk at all. It processes the sorted array in chunks and calls
`np.searchsorted` on each chunk, then checks the insertion point and the entry just below it.
That is $O(n \log n)$ binary search where C does an $O(n)$ walk, but it runs in compiled code
and not one interpreter step per pair. In NumPy, the asymptotically worse method is the faster
one.

**Intersecting adjacency lists ([143](/solutions/0143/)).** The solution builds a graph whose
edges are pairs $(p, q)$ with $p^2 + pq + q^2$ a perfect square, and then looks for triangles.
For each edge $(p, q)$ it needs the common neighbours $r > q$. The C side sorts and dedups each
adjacency list once, then closes triangles with a merge of the two lists: skip both to values
above $q$, then advance whichever head is smaller and record a hit when they are equal. Python
writes `neighbors_p & adjacency[q]`, a [set](https://docs.python.org/3/library/stdtypes.html#set)
intersection. That is shorter and probably as fast as anything Python could do by hand. The C
merge avoids hashing entirely, and that accounts for a good part of the recorded speed gap.

**Counting points in a half-plane ([184](/solutions/0184/), [478](/solutions/0478/)).** Both
problems ask whether a set of points around the origin fits in an open half-plane. Both sort the
points by [polar angle](/topics/domain/polar-coordinate-system) and then need, for each point
$i$, how many points lie in the half-turn just counter-clockwise of it. That is the chasing
shape on a *circular* sequence. As the anchor rotates counter-clockwise, the far edge of its
half-turn rotates too, so `j` only moves forward. The total work is linear after the
$O(n \log n)$ sort. In 184 the count $w_i$ gives $\binom{w_i}{2}$ triangles that miss the
origin. In 478's reference solution (`s0`) the count $A_d$ sets an exponent $2^{A_d}$. The
circle needs one of two treatments. Either let `j` run past `n` and index modulo `n`, with the
bound `j < i + n` so a window never covers the whole circle, or (478) lay a
[prefix sum](/topics/technique/prefix-sum) of multiplicities over a *doubled* copy of the order
so every window is one subtraction. Both solutions test window membership with the exact integer
[cross product](/topics/technique/cross-product), never a float angle. On a lattice there are
many collinear points, and the half-open convention (include a point on the same ray as the
anchor, exclude the antipodal one) has to be applied exactly. Otherwise a triangle gets counted
twice or not at all. The Python and C sides of 184 both keep the walk itself, since the loop is
linear and runs only once. 478's walk is in its Python reference solution only: the fast
solution (`s1`, in Python and C) replaces it with a closed form based on symmetry.

**Merging two angular orders ([252](/solutions/0252/)).** The largest empty convex polygon is a
fan dynamic program. For a fixed apex and spoke, the possible predecessors and successors of a
vertex are two lists sorted by angle, and the convexity test between them reduces to one key
comparison. A merge of the two lists, carrying a running maximum of the predecessor values
(see [prefix-maximum scan](/topics/technique/prefix-maximum-scan)), fills a whole row of the
table in linear time. The C side is an explicit two-pointer walk with an integer turn test.
Python replaces the merge with `searchsorted` against the prefix maximum, which is the same
NumPy substitution as in 461.

**Sliding intervals with no array ([331](/solutions/0331/)).** Here the two pointers are not
indices into a stored list. They are the endpoints $L_b$ and $R_b$ of a row's black interval on
an annulus, and both move monotonically as the row index goes down. The solution needs, for each
row, how many odd-width positions fall inside its interval. Since the interval only slides one
way, each position enters once and leaves once. C keeps the window in a
[circular buffer](/topics/technique/circular-buffer) with a running count: drop what left, then
add what entered. Python cannot afford a step per row at $N \approx 2^{31}$, so it computes a
block of positions at a time as a prefix-sum array and answers each row with two lookups. The
pointers are still there, but they mark block boundaries, not single steps.

## How to reason about it

- **Earn the monotonicity first.** Before writing the loop, state what moves each pointer and
  why the other one can never need to go back. In 461 it is "the target decreases as `i`
  increases". In 184 it is "the half-turn's far edge rotates with its anchor". If you can't say
  it in one sentence, the walk is probably wrong in some cases.
- **Know where the answer lies when the pointer stops.** For "nearest to target" the pointer
  stops next to the answer, not on it, so check both neighbours. For "count in window" decide
  whether `j` points to the last member or the first non-member, and keep that choice the same
  through the whole loop.
- **Handle circular orders explicitly.** Double the array or index modulo `n`, cap the window
  below a full turn, and restart `j` from `i + 1` if it falls behind the anchor.
- **Make ties exact.** A pointer advanced by a floating comparison can stop one step early on a
  tie. Integer cross products (184, 252, 478) or an explicit epsilon (461) are how these
  solutions avoid that.
- **In Python, prefer the vectorised equivalent.** The walk is $O(n)$ interpreted steps, while
  `np.searchsorted`, set intersection or a prefix-sum block is $O(n \log n)$ or $O(n)$ in
  compiled code. For a single pass over a few thousand points the plain loop is fine. Over tens
  of millions of pair sums, the vectorised form wins even with the extra log factor. C has no
  such tension: the walk is the fastest and simplest form, and it is cache-friendly because both
  pointers read memory sequentially.

Related pages: [binary search](/topics/technique/binary-search-algorithm) (the per-element
alternative the walk replaces), [sorting](/topics/technique/sorting-algorithm) (which nearly
always comes first), and the [sweep line](/topics/technique/sweep-line-algorithm), a
two-dimensional cousin of the chasing window.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0478](/solutions/0478/) — Mixtures

<!-- /problems -->
