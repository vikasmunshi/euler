<!-- tags: [depth-first-search] -->
<!-- status: final 2026-11-03T07:36Z -->
# Depth-first search

[Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) (DFS) explores a
tree of possibilities by going as deep as it can before backing up. In a graph-algorithms
course it is one of two ways to visit the vertices of a given graph; in Project Euler it
is almost always something slightly different and more useful — a way to *enumerate
constructed objects*. There is no graph on disk. The tree is implicit: a node is a partly
built object, an edge is one more choice, and a leaf is a finished candidate. Sets of
primes, factorisations, addition chains, digit strings, binary circles, tilings,
Pythagorean triples, squares packed under a curve, palindromes in base $\varphi$, numbers
pandigital in every base at once — the problems below all build their answers that way.
(The exception, problem 674's unifier, is a real graph walk, and it shows what the
classical version still offers.)

## The idea — a tree you never store

The whole search is a recursive function with the partial object as its argument:

```
search(partial):
    if partial is complete: record it
    for each legal extension e of partial:
        search(partial + e)
```

What makes this cheap is what it *doesn't* keep. Breadth-first search must hold an entire
frontier in memory, which is the widest level of the tree — exponential. DFS holds only
the current root-to-node path, which is the tree's *depth*. When the branching factor is
large and the depth is small (ten digits, twenty-five primes, fourteen chain terms), that
is the difference between a table you cannot allocate and a recursion a dozen frames deep.

The price is that DFS finds *a* solution, not the nearest one. It commits to a branch and
follows it to the bottom, so the order in which leaves arrive is the order you chose to
list the children — nothing more. Everything below is about exploiting that freedom or
working around it.

## Canonical extension: visiting each object exactly once

The first thing a good DFS enumeration does is fix an order on the choices so that every
object has exactly **one** path to it. Problem 204 counts $100$-smooth numbers by
recursing over the ordered list of primes and only ever extending with a prime at the
current index *or later*; problem 484 walks powerful numbers the same way, and problem 241
grows a number by choosing primes in strictly increasing order. Because the primes come
out sorted, each factorisation is reachable by precisely one sequence of decisions.

That convention pays twice. It removes duplicates without a `visited` set — no hash table,
no dedup pass, no memory proportional to the output. And it makes the subtree bound honest:
once the running product exceeds the limit, no descendant can come back under it, so the
branch is dead. In problem 60's clique of pairwise-concatenable primes the same rule appears
as `if prime <= current_list[-1]: continue` — members are added in ascending order, so a
five-element set is built once rather than $5!$ times, and the first clique found is
automatically the minimal one.

The order can also enforce a rule between neighbouring choices. Problem 473's digit pairs must
never sit next to each other, and that is built into the moves themselves. Skipping pair $k$
moves on to $k-1$; taking it jumps to $k-2$. No illegal set can be built at all, so there is
nothing to check and nothing to throw away.

The node need not carry what has been built; it can carry **what is left to build**.
Problem 248 inverts Euler's totient — every $n$ with $\varphi(n) = 13!$ — and its node is
a *residual*: the part of $13!$ not yet accounted for. Taking prime $p$ to the power $a$
peels $p^{a-1}(p-1)$ off the residual, so the only primes worth listing are those with
$(p-1) \mid 13!$, a child exists only if $(p-1)$ divides what remains, and a leaf is a
residual of $1$. The ascending-prime rule does the deduplication exactly as in 204, and
the divisibility test is the prune — a much sharper one than a size bound, because almost
every candidate prime fails it.

The *direction* of the order matters as much as the fact of having one. You can pick it so
that each choice's side effects land only on choices **not yet made**. Problem 342 sums the
$n$ for which $\varphi(n^2)$ is a perfect cube. Taking a prime $p$ into $n$ contributes
$p^{2e-1}$ to $\varphi(n^2)$, and also contributes $p-1$, whose prime factors are all smaller
than $p$. So the search takes primes in *decreasing* order. Then a choice can only create
debts — exponents not yet $\equiv 0 \pmod 3$ — on primes that still lie ahead. The node
carries those debts as a small map from prime to exponent mod 3. The ordering also gives a
prune for free: the largest prime still owed can only be paid by taking that prime itself,
since any later prime is smaller. If even its cheapest admissible power overflows the limit,
the branch is dead. A search whose consequences flowed in both directions would have to wait
until every prime had been decided before it could judge anything.

An order on the choices also orders the leaves, and sometimes that is what the question asks
for. Problem 571 wants the *smallest* few numbers that are pandigital in every base below
$n$. The candidates are base-$n$ digit permutations. Trying the unused digits in ascending
order makes the leaves arrive in increasing numeric order, so the search can return the
moment it has found as many as it needs. "The first $k$" becomes an early exit. Nothing has
to be sorted, and the rest of the tree is never visited.

Cyclic objects need one more decision before the order can do its work: *where the cycle
starts*. Problem 265 counts binary circles — $2^N$ bits whose $N$-bit windows, read around
the circle, are all different ([de Bruijn sequences](https://en.wikipedia.org/wiki/De_Bruijn_sequence)).
Every circle has $2^N$ rotations, but exactly one begins with its all-zeros window, so
the search fixes those $N$ zeros as the root and grows only the rest. One anchoring
choice divides the tree by $2^N$ and makes each circle's numeric reading unique — the
same symmetry-breaking move as the strict inequality, applied to rotation instead of
permutation. The seam is the one place the anchor is not free: the $N-1$ windows that
wrap around the end must be checked once the circle is complete.

When the tree really is a walk over a graph, you pay the other way: the same vertex is
reachable by many paths and you need explicit bookkeeping. Problem 61 chains four-digit
figurate numbers by their overlapping digits and hunts for cycles, so it carries a
`visited` set — and, being a search rather than an enumeration, it must undo every mark
on the way back up:

```python
for next_num in number_mapping.get(current, []):
    if next_num not in visited:
        path.append(next_num)
        visited.add(next_num)
        result.extend(find_cyclic_paths(start, next_num, path, visited, ...))
        path.pop()
        visited.remove(next_num)
```

That four-line sandwich — mutate, recurse, un-mutate — is *backtracking*, and it is the
single most common source of wrong answers in a DFS. Anything you change on the way down
has to be restored on the way up, exactly. Passing a fresh copy of the state to each child
avoids the bug at the cost of copying, so mutate-and-restore is the default for a `set`
or a list. But when the state fits in a machine word the trade-off flips: problem 265's
"windows already seen" is a $2^N$-bit integer mask, and the child receives
`used | 1 << window` — a new value, built in one instruction, with nothing to undo. Make
the state an immutable value whenever it is small enough, and the backtracking bug
cannot be written.

Graph DFS has one more classical job that enumerations never need: **post-order with cycle
detection**. Problem 674 reduces equations between nested $I(x, y)$ expressions to
[syntactic unification](https://en.wikipedia.org/wiki/Unification_(computer_science)), which
is possible because $I$ is injective. The terms are
[hash-consed](https://en.wikipedia.org/wiki/Hash_consing) into one shared DAG, and union-find
merges the classes that unification forces together. After that the least solution is a
bottom-up evaluation over the class graph: a node's value needs its children's values first,
which is post-order. Shared subterms are evaluated once, because each finished class keeps its
value. The [occurs check](https://en.wikipedia.org/wiki/Occurs_check) — whether a variable
ended up equal to a term containing itself — is the textbook three-colour test. A class is
*grey* while its children are still open and *done* once it has a value. Reaching a grey class
again is a back edge, which means a cycle, which means no solution. The expressions nest far
too deeply for recursion, so the walk runs on an explicit stack, with the grey set doing the
work that the call stack would otherwise do.

## Pruning is the algorithm

A bare DFS over these trees is exponential and useless. What makes it finish is the test
that kills a subtree before entering it, and that test is where the real thinking goes.
Five flavours recur:

- **Monotone feasibility.** The partial object only ever gets bigger, so the moment it
  breaks the bound, stop. Multiplying primes into a smooth number (204) or a powerful
  number (484) is monotone in exactly this sense — the loop over exponents halts the
  instant the product passes $L$, and no branch that cannot yield a valid number is ever
  entered. The monotone quantity need not be the size: in problem 245 (composites whose
  "coresilience" $(n-\varphi(n))/(n-1)$ is a unit fraction) it is the ratio
  $\varphi(m)/m$, which only falls as primes are multiplied in, and the condition can only
  hold while it stays above $\tfrac12$ — so a prefix that drops below is dead however
  small it still is.
- **Branch and bound.** For an *optimisation*, complete the current prefix as optimistically
  as the rules allow and compare that bound with the best answer so far. Problem 170 builds
  a pandigital product one digit at a time from the most significant end and pads the prefix
  with the largest unused digits to get an upper bound; problem 103 adds, to the partial sum
  of a special set, the smallest total the remaining elements could possibly contribute, and
  breaks when even that meets the best sum already found.
- **Reachability window.** Some searches need a running quantity to land on an exact
  target, and it can move in both directions. Problem 473 sums palindromes in the golden-ratio
  base: each palindrome is a set of mirrored digit pairs $\varphi^k + \varphi^{-(k+1)}$, every pair
  adds a $\pm F\sqrt5$ term, and the total is an integer only when those $\sqrt5$ terms add to
  exactly zero. The search decides pairs from the largest $k$ down. Prefix sums record the most
  the remaining pairs could still push the balance up, and the most they could pull it down. Any
  node whose balance lies outside that window is dead. The Fibonacci coefficients grow
  geometrically, so once a large pair is taken the window closes around a narrow band of small
  pairs, and the search costs about as much as its output rather than the full Fibonacci-sized
  count of subsets. Its other prune, a floating-point value bound, shows what *admissible*
  means in practice. The float is only allowed to cut a branch, never to accept a leaf, and it
  carries a little slack so rounding cannot discard a real hit. Acceptance happens in exact
  integers.
- **Interval of completions.** A prefix fixes more than a partial object. It fixes the
  *range* $[\text{lo}, \text{hi}]$ that every completion falls in, and a property that holds
  across that whole range can be read off the range's endpoints. Problem 571's prefix is a run
  of leading base-$n$ digits. Filling the rest with the remaining digits ascending gives
  $\text{lo}$, and descending gives $\text{hi}$. In every other base $b$, all completions share
  the leading base-$b$ digits that $\text{lo}$ and $\text{hi}$ share. If the free low places
  are fewer than the base-$b$ digits that shared prefix is still missing, no completion can be
  pandigital in base $b$, and the branch is cut — long before any completion has been written
  out in base $b$. The shared prefix only gets longer with depth, so each base's free-place
  count and digit mask are passed down the path and updated incrementally. They are never
  recomputed. Bases are checked largest first, because those fail soonest.
- **Algebraic.** The cheapest prune is one the mathematics hands you. Problem 484 notices
  that a certain multiplicative factor is zero for particular exponents and drops the whole
  subtree, since every deeper term carries the zero. Problem 241's search over abundancy
  indices tests a single `gcd` against a precomputed primorial — a prune that, by the notes,
  took one instance from twenty-five seconds to a tenth of a second.

Two second-order effects are worth internalising, because they cost nothing to apply:

**Child order decides how fast the bound tightens.** Branch and bound is only as strong as
the incumbent it compares against, so arrange to find a good one immediately. Problem 170
tries digits in descending order and lands a near-maximal answer almost at once, after
which the bound discards nearly the whole tree. Problem 122 tries the largest sums first
for the same reason.

**Order the tests at the leaf by cost.** Problem 103 ships two solution indices that differ
in exactly one line — which of two validity conditions is checked first — and that single
line dominates the running time, because the expensive $O(2^n)$ test runs on every candidate
the cheap $O(n^2)$ test would have rejected for free. Cheap and discriminating first, always.

## Stop one level early

In a branching tree most of the nodes are leaves, so most of the cost of a DFS is its
last level. The strongest optimisation is often not a better prune but **not descending
into that level at all** — replacing it by arithmetic over the whole fan-out at once.

- **Solve for the last choice.** In problem 245 the unknown largest prime $q$ appears
  linearly once the prefix $m$ of smaller primes is fixed: for each small integer $K$
  the condition rearranges to $q = (K\varphi(m)+1)/\bigl(m - K(m-\varphi(m))\bigr)$. The
  search walks prefixes only; at each one it tries the handful of $K$ that keep $q$ in
  range, checks divisibility, and runs one primality test. A leaf level that would have
  been "every prime up to $L/m$" becomes a few lines of algebra.
- **Count the last choice in bulk.** Problem 272 sums the $n \le L$ with a prescribed
  number of cube roots of unity, which fixes how many primes $\equiv 1 \pmod 3$ divide
  $n$. The DFS chooses all but the last of those primes; the last prime $p$ and the
  free cofactor below $T/p$ are then summed together, with the large $p$ grouped by the
  value of $\lfloor T/p \rfloor$ and priced by prefix sums over primes and over
  admissible cofactors. The deepest level — by far the widest — is never enumerated.
- **Sum a free factor from a table.** Problem 516 sums the $n \le L$ whose totient is
  5-smooth. The totient product formula splits every such $n$ uniquely as $h \cdot m$: $h$ is a
  Hamming number $2^a3^b5^c$, and $m$ is a square-free product of primes $q > 5$ with $q-1$
  Hamming. Only $m$ has structure worth searching. A 204-style DFS over the ascending admissible
  primes lists every $m$. The $h$ side is a complete, independent level: every Hamming number up to
  $L/m$. A sorted Hamming list with prefix sums prices that level with one binary search, so it
  contributes $m \cdot \sum_{h \le L/m} h$ with no further descent. The DFS visits a few million
  products, and none of the far more numerous $n$.

- **Count a chain by its length.** In problem 615 each node is an odd part $o$, and its
  members are $o$ times an unbounded run of powers of two. The number of members under a
  bound $L$ is a single `bit_length` of $L / V(o)$, where $V(o)$ is the smallest member. So the
  powers of two never become a level of the tree.

The pattern is the same in all four: let the DFS do the combinatorial part, where the
choices genuinely interact, and hand the final, independent choice to a formula or a
table. See [closed form over iteration](/blogs/takeaway/closed-form-over-iteration).

You can take the same split further back, and decide **which choices the tree contains at
all**. Problem 967 counts $n \le 10^{18}$ by the sum, mod 3, of their distinct prime factors
up to $B$. It does this with a divisor-sum identity that has one term per square-free product
of the relevant primes, about $7 \times 10^7$ of them. Searching over every prime is too slow.
But the contribution of the seven smallest primes depends only on $n$ modulo their product, so
a period table absorbs them. The DFS then enumerates square-free products of the 22 large
primes only, which is about $1.4 \times 10^6$ nodes. And because each leaf's weight depends
only on how many of its primes are $1$ and $2 \bmod 3$, the leaves are summed per class rather
than one at a time. A small prime is a choice that branches a lot and adds little structure,
so it belongs in a table; a large prime is rare enough to search. The Python solution also
shows that a tree pruned only by a monotone bound need not be walked recursively at all.
Taking the primes in order, it appends $d \cdot p$ for every surviving $d$ to a NumPy array.
That builds exactly the same node set level by level, vectorised, while the C port walks it
as an ordinary DFS.

## A node can be a set of inputs

So far each node has been one partial object. A more powerful reading makes a node a
*block of inputs that share the same history*. Problem 255 asks for the average number of
steps a rounded Heron's-method square root takes over every 14-digit $n$ — $9 \times 10^{13}$
separate runs. But each step maps the current estimate $x$ to
$\lfloor (x + \lceil n/x \rceil)/2 \rfloor$, and $\lceil n/x \rceil$ is constant on runs of
$x$ consecutive $n$. So the search starts from the interval of all inputs, splits it into
one child interval per possible next estimate, and closes a branch the moment the estimate
repeats, adding *step count × interval length* to the total. The tree has about
$10^7$ nodes rather than $10^{14}$ leaves; the DFS is over the computation's decision
tree, not over its inputs. Whenever a per-input procedure branches on a quantity that is
piecewise constant in the input, this is how to run it on all inputs at once.

## Depth, recursion, and the explicit stack

Depth is DFS's one resource, and it is not always as small as it looks. Problems 139, 218
and 223 all enumerate Pythagorean-like triples by walking a ternary tree of matrix
transformations (Barning–Hall / Berggren), where each child is strictly larger than its
parent — so a DFS that prunes any node past the bound visits exactly the in-range triples,
with the tree's structure supplying primitivity for free and no `gcd` filtering at all.
But those trees have a "thin" spine that grows only quadratically, descending thousands of
levels before it exceeds the limit. Python's default recursion limit and C's stack both
object. The fix in all three is an **explicit stack**: `push` the children, `pop` the next
node, loop. Same traversal, same order up to the child ordering, no frames.

Reach for the explicit form when the depth is data-dependent and unbounded, when you are
writing C, or when you want to swap traversal order later — a stack becomes a queue with a
one-line change, which is exactly the experiment you want to be able to run.

The explicit stack also lets you shape *what* it holds. Problem 255's root interval has an
enormous fan-out but each subtree beneath it is shallow, so pushing every child of the root
would fill the stack with millions of deferred siblings. Its solution walks the root's
children with an ordinary loop and runs a fresh stack per subtree; inside, the last child
of each node is followed in place rather than pushed, since most nodes have only one.
Memory then tracks one subtree's open branches, which is the DFS promise kept in practice.

## When DFS is the wrong tool — and how it comes back

DFS gives no guarantee about *distance*. If the question is a shortest path, DFS answers
the wrong question: it will happily return a path of length 400 when one of length 52
exists. Problem 244 slides tiles on a 15-puzzle where every move costs the same, so the
right tool is breadth-first search, which visits states in non-decreasing distance and
therefore labels each with its true minimum.

Note the shape of what happens next, though, because it generalises: once BFS has labelled
every state with its distance, a **DFS restricted to strictly descending labels** enumerates
*all* shortest paths — every step drops the label by one, so every root-to-target walk is
optimal by construction. BFS establishes the metric; DFS enumerates within it. That pairing
is worth remembering whenever a problem asks not for the shortest path but for something
summed over all of them. See also [shortest path problem](/blogs/domain/shortest-path-problem).

The same caution applies to *ranking*. Problem 247 packs squares under $y = 1/x$: each
region yields one square and two smaller sub-regions, and the question is the position of
a given square when all of them are sorted by size. That reads like a job for best-first
search — a priority queue popping the largest square each time. But the tree is
**heap-ordered**: a child's square is always smaller than its parent's. So once the target
square's side $s$ is known, the squares at least as large as it form a connected subtree at
the root, and a plain DFS that refuses to enter any region whose square is smaller than $s$
visits exactly them. Their count is the rank, found with a stack and no heap. When values
fall monotonically down every branch, "the top $k$" is a pruned DFS, and the order of the
visit stops mattering.

The other repair is [iterative deepening](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
(IDDFS): run a depth-limited DFS at limit $1$, then $2$, then $3$, until an answer appears.
The first solution found is then shortest, as with BFS, but memory stays $O(\text{depth})$,
as with DFS. The re-work looks wasteful and is not: in a branching tree the last level
dominates the total, so re-expanding all the shallow ones costs a constant factor. Problem
122 uses exactly this to find minimal addition chains — chain lengths are small (about
$\log_2 k$ plus a bit) but not known in advance, which is precisely IDDFS's case.

The same trick works on **value** instead of depth. Many enumerations here are pruned by
"stop once the product passes $L$", and the question then is what $L$ should be when the
answer is not known in advance. Start with a bound that is too small and double it. Problem
615 wants the $n$-th smallest member of a set. The DFS above can *count* the members under a
bound cheaply, so the solution doubles the bound until the count reaches $n$. Then it runs
the walk once more to collect those members, and sorts them. Selection becomes counting
plus a final sort of at most about $2n$ values. Problem 829 needs the smallest number whose
factor tree has a given shape. It generates every number of that shape below a bound, starting
from the product of its two subtrees' minima and doubling until the list is non-empty. The first
non-empty list contains the true minimum, because everything below the bound was enumerated.
Each shape's list is cached with its bound, so a later request for a smaller bound is
answered by slicing the cached list. As with IDDFS, the geometric growth is what makes the
repetition affordable. The last round costs about as much as all the earlier rounds put
together, so overshooting by up to a factor of two is the whole price.

829 also shows the smallest DFS on this page, an *existence* query. A number's factor
tree depends on whether it has a divisor in a given interval $(a, \sqrt n\,]$. The divisors
are walked from the known factorisation, exponent by exponent, with a bound cut whenever the
partial divisor passes $\sqrt n$, and the search returns at the first hit. A search that only
needs a yes or no should short-circuit all the way up the call stack, not count.

## How to reason about it

Reach for DFS when the answer is *built* rather than looked up, when the number of
candidates is astronomically larger than the number of *plausible* candidates, and when a
partial candidate can be judged before it is finished. Then, in order:

1. **Define the node** — what a partial object is (or what is still left to build, or
   which block of inputs shares this history), and what "complete" means.
2. **Fix a canonical extension order**, so each object is reachable one way. This is
   usually a strict inequality on the choices, plus an anchor for anything cyclic, and it
   is free. Point it so each choice's consequences fall on choices not yet made.
3. **Find the prune.** Without it you have brute force with extra steps; the prune *is*
   the solution. Make sure it is admissible — a bound that can be wrong silently discards
   real answers, which is much worse than being slow.
4. **Order the children** so a strong incumbent arrives early, and **order the leaf tests**
   cheapest-first.
5. **Look at the last level.** If the final choice is independent of the rest, solve for
   it or count it in bulk instead of descending.
6. **If the bound is unknown, double it** — the value-space twin of iterative deepening.
7. **Check the depth** before trusting recursion.

And, as everywhere in this repository, build the sieves and tables the search needs
*inside* `solve()`, sized to the inputs — the harness times repeated calls, and anything
kept warm between them flatters the measurement.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0244](/solutions/0244/) — Sliders
- ● [0245](/solutions/0245/) — Coresilience
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0265](/solutions/0265/) — Binary Circles
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0571](/solutions/0571/) — Super Pandigital Numbers
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ● [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ● [0829](/solutions/0829/) — Integral Fusion
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ● [0850](/solutions/0850/) — Fractions of Powers
- ● [0928](/solutions/0928/) — Cribbage
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers

<!-- /problems -->
