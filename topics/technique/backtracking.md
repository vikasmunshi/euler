<!-- tags: [backtracking] -->
<!-- status: final 2026-10-14T12:11Z -->
# Backtracking

[Backtracking](https://en.wikipedia.org/wiki/Backtracking) builds a solution one decision at a time
and drops a partial solution the moment it can no longer be completed. It is
[depth-first search](/topics/technique/depth-first-search) over a tree whose nodes are *partial*
answers, and it keeps coming back because so many Project Euler puzzles have the same shape: a
handful of slots to fill (digits, primes, ring positions, grid cells), and constraints that can be
checked before every slot is filled. Brute force enumerates the leaves of that tree. Backtracking
only looks at the part of the tree that survives pruning, and every technique on this page exists to
make that part smaller.

## The idea

Every backtracking search has the same skeleton: **choose, check, recurse, un-choose.** Problem 61's
cycle finder shows it with nothing extra:

```python
for next_num in number_mapping.get(current, []):
    if next_num not in visited:
        path.append(next_num)          # choose
        visited.add(next_num)
        result.extend(find_cyclic_paths(start, next_num, path, visited, number_mapping, target_length))
        path.pop()                     # un-choose: restore the state exactly
        visited.remove(next_num)
```

The search costs roughly *(nodes visited) × (cost per node)*. Brute force over the same problem costs
*(leaves) × (cost of checking one leaf)*. Pruning wins because a constraint that fails at depth 3
rules out every leaf below that node at once. Problem 43 spells this out. There are $10! \approx 3.6$
million digit orderings, but its search builds the number right to left, three-digit window by window,
and each new digit has to make the leading window divisible by the next prime in
17 → 13 → 11 → 7 → 5 → 3 → 2. Only 44 three-digit strings are multiples of 17 with distinct digits, and
each later step keeps about one digit in ten, so the search finishes in microseconds.

The skeleton never changes. What separates a search that finishes from one that runs all night is how
it uses five levers.

**1. Decide the most constrained thing first.** Problem 43 runs right to left *because* 17 is the
largest divisor: starting there gives the smallest seed set and lets every later window overlap one
that is already fixed. Problem 96's first solution applies the same rule dynamically. Before each
guess it sorts the empty cells by how many candidates they have left and branches on the cell with
the fewest (the *minimum-remaining-values* heuristic). A cell with one candidate costs no branching
at all, and a cell with zero exposes a contradiction straight away instead of nine levels later.

**2. Check incrementally, on the partial state.** Problem 60 builds its prime set like a
[clique](/topics/domain/clique-problem). A new prime joins only if it pairs with *every* current
member (both concatenations prime), so each node does one prime-pair check per member, never a
re-check of the whole set. The pair check is the expensive edge test, and it is memoised because the
same pairs come up across many branches. Problem 265 keeps a bitmask of the N-bit windows a
[de Bruijn](/topics/domain/de-bruijn-sequence) circle has already used, so "is this extension legal?"
is a single AND.

**3. Derive what you can; choose only what you must.** In problem 68's magic 5-gon ring, ten numbers
fill ten positions, but once the five inner values and the line total are known, every outer value is
*forced*: `outer[i] = S - inner[i] - inner[i+1]`. The search permutes only the inner ring and computes
the rest. If a forced value has already been used or is out of range, the branch dies. Choosing 5 of
10 values instead of all 10 shrinks the tree by orders of magnitude. Sudoku pushes the same lever all
the way: [constraint propagation](/topics/technique/constraint-propagation) (problem 96's third
solution, after Norvig) eliminates candidates and fills naked and hidden singles until nothing more
follows, and only then guesses.

**4. Break symmetry so each answer is reached once.** A ring has no natural starting point, so
problem 68 pins the smallest outer value to position 0. That fixes the rotation the problem's
"clockwise from the numerically lowest external node" rule asks for and cuts the search fivefold.
Problem 60 adds primes in ascending order, so each set appears as one path rather than $5!$. Problem
118 partitions digits into prime sets the same way, choosing primes in strictly increasing order so
an unordered set has exactly one canonical path. Problem 61 does *not* break its rotational symmetry
(every cycle is found once per starting number and deduplicated afterwards by sorting). That works,
but starting every cycle from the octagonal numbers, the sparsest family, would make the
deduplication unnecessary. See [exploit symmetry](/topics/takeaway/exploit-symmetry).

**5. Order the branches, and bound them, when you want the best answer.** If the goal is *the largest*
or *the smallest*, branch order and an optimistic bound turn the search into
[branch and bound](/topics/technique/branch-and-bound). Problem 170 builds its pandigital product
most-significant digit first, so better candidates are tried first and branches that can't beat the
best result so far get cut. Problem 122 runs
[iterative deepening](/topics/technique/iterative-deepening-depth-first-search) over addition chains.
It allows depth $d$, then $d+1$, so the first chain that reaches a target is a shortest one, and it
prunes any branch whose current value, doubled at every remaining step (`current << remaining`),
still falls short.

## How to reason about it

**Reach for it when the constraints are local.** Backtracking pays off exactly when a partial
assignment can be *refuted* before it is complete: a three-digit window that isn't divisible, a prime
that doesn't pair, a window that repeats, a cell left with no candidates. If the constraint can only
be checked on a finished object, there is nothing to prune and you are back to brute force with
extra recursion. When the same *subproblem* recurs along different paths, the right tool is
[memoization](/topics/technique/memoization) or dynamic programming instead. A backtracking node
carries its whole path (which digits are used, which primes are in the set), so two nodes rarely
share a state, and that is why these problems don't memoise their searches.

**Pruning versus per-node work is the central trade-off.** Problem 96 shows the whole range on one
puzzle. Solution 0 is plain DFS with MRV and *forward checking* (removing the placed digit from its
peers' candidates). Solution 2 does full propagation at every node: each node is expensive, but very
few nodes get visited. Solution 1 rewrites Sudoku as [exact cover](/topics/technique/exact-cover) and
runs Knuth's Algorithm X with [Dancing Links](/topics/technique/dancing-links), which makes "choose
the most constrained column" and "undo a choice" both cost almost nothing. All three solve the 50
grids comfortably. The lesson is that propagation and backtracking are two dials on the same machine,
not rival methods. Turn up propagation when nodes are cheap to check but the tree is bushy.

**Undo exactly, or copy deliberately.** The un-choose step has to restore the state *exactly*. Problem
61 pops and removes, and problem 96's first solution writes the cell back to 0. The alternative is to
pass each child a fresh copy, which is what the same solution does with its candidate list
(`update_possibilities` returns a new list). Copying is simpler to get right and costs memory and
time per node. Mutate-and-undo is faster and is where the subtle bugs live: a missed `remove`, or an
early `return` that skips the undo. Choose one approach per data structure and stick to it.

**A first-hit stop needs an ordering argument.** Stopping at the first solution found is correct only
if the search order matches the objective. Iterative deepening guarantees that for "shortest"
(problem 122), and most-significant-digit-first does for "largest number" (problem 170). Ascending
*lexicographic* order (problem 60) is not the same as ascending *sum*, though: a set found later can
still have a smaller total. Either prove that no later set can win, or keep searching under a bound,
as in [branch and bound](/topics/technique/branch-and-bound). Calibrate on the problem's worked
example ([calibrate theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers)).

**Recursion depth is not the worry; branching factor is.** These trees are shallow (ten digits, five
primes, six figurate numbers, 81 cells), so Python's recursion limit never comes into play. What
explodes is the width, and every lever above is a way to cut the branching factor at the top of the
tree, where each pruned branch takes the most leaves with it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0096](/solutions/0096/) — Su Doku
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0265](/solutions/0265/) — Binary Circles
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
