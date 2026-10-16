<!-- tags: [counting] -->
<!-- status: final -->
# Counting

[Counting](https://en.wikipedia.org/wiki/Counting) is the plainest question in the archive — *how
many?* — and the answer is always a single integer. The problems carrying this tag have almost
nothing else in common: dart checkouts, lattice triangles, squarefree integers, words over a
four-letter alphabet, rolls of twenty dice, grids of digits, opening positions of a two-player game.
About two thirds of them also carry
[combinatorics](/topics/domain/combinatorics); the rest count number-theoretic or geometric objects
— solutions of a Diophantine equation, integers with a given factorisation shape, triangles with
integral coordinates. What unites them is not the subject but the predicament: **you are asked for
the size of a set you can define in one line and can never walk.**

## A cardinality, not an arrangement

It is worth being precise about how this tag differs from its neighbour. Combinatorics is a
*discipline* — arrangements, choices, orderings, and the machinery that handles them. Counting is a
*question shape*: the answer is $|S|$ for some $S = \{x \in X : P(x)\}$, whatever $X$ happens to be.
A problem earns this tag when the hard part is the cardinality itself, and that is true whether the
elements are permutations or primes.

The framing pays off because the reference implementation is always the same, and always correct:

```python
count = sum(1 for x in space if predicate(x))
```

Every solution on this page is a transformation of that loop that preserves its value and destroys
its cost. Keeping that in view is what tells you when you are done and when you are wrong: however
clever the final algorithm, it must return the number the unaffordable loop would have returned.

## First, size the space

Before reaching for structure, estimate the candidate count. The estimate — not taste — decides
whether you need an idea at all.

Sometimes you do not. Problem 112 asks for the least $N$ at which exactly 99% of the numbers below
it are "bouncy" (digits neither monotonically rising nor falling). There is a clean closed form for
counting monotone numbers, and it is entirely unnecessary: the answer is under 1.6 million, and
classifying one number is a single pass over its at-most-seven digits. A linear scan finds it in
well under a second. Reaching for combinatorics there would have cost an hour of derivation to save
nothing — see [size the work to the input](/topics/takeaway/size-work-to-the-input). Problem 109 is
the same verdict for a different reason: a dartboard offers only 62 distinct non-finishing scores
and 21 finishing doubles, so the entire space is a few tens of thousands of triples. All the
difficulty is in modelling the rules correctly, none of it in the search.

Then there are the problems where the estimate ends the conversation: problem 240's twenty
twelve-sided dice admit $12^{20} \approx 3.8 \times 10^{21}$ rolls; problem 201's fifty-element
subsets number about $10^{29}$; problem 679's words, $4^{30}$; problem 166's digit grids, $10^{16}$.
Those need a different idea, and the rest of this page is about which ideas there are.

## Change what you iterate over

The most productive move in counting is to stop iterating over the objects and iterate instead over
a **parameter that determines them**.

Problem 173 counts square laminae — square frames — buildable from a tile budget. A lamina looks
like a shape, but it is fixed by two integers: the frame thickness $t$ and the hole side $h$, with
tile cost $(h+2t)^2 - h^2 = 4t(t+h)$. The count of laminae within budget $N$ is then the count of
pairs $(t, h)$ with $4t(t+h) \le N$, and since the cheapest lamina of thickness $t$ already costs
$4t(t+1)$, only $O(\sqrt{N})$ thicknesses are viable; for each, rearranging to $h \le N/(4t) - t$
gives the number of holes in one division. A few hundred iterations, and not one shape ever
constructed.

Problem 800 counts "hybrid integers" $p^q q^p \le N$ over primes $p \ne q$, where $N$ has millions of
digits. Taking logarithms turns the predicate into $q \ln p + p \ln q \le \ln N$, ordinary
floating-point arithmetic; and for fixed $p$ the left side is strictly increasing in $q$, so a single
[binary search](https://en.wikipedia.org/wiki/Binary_search) yields the number of qualifying partners
at once. The number being compared against is never formed — only its logarithm. Both problems are
[reduce algebraically before coding](/topics/takeaway/reduce-before-coding) in its purest form.

The discipline that makes this safe is **bijection**: the reparametrisation must hit every object
exactly once. In problem 173 the symmetry of a frame forces $s - h$ to be even, which is precisely
what makes $t$ an integer, and $(t, h)$ with $t, h \ge 1$ is exactly the set of laminae — no
duplicates, no omissions. In problem 800, insisting on $p < q$ counts each unordered pair once.

The public problem 91 shows the same move combined with a case split. It counts right triangles
$OPQ$ with lattice vertices in an $N \times N$ box, partitioned by *where the right angle sits*:

```python
triangles_at_p_or_q = sum(
    min(x * m // y, m * (coordinate_limit - y) // x)
    for x in range(1, coordinate_limit + 1)
    for y in range(1, coordinate_limit)
    for m in [math.gcd(x, y)]
)
triangles_at_p_or_q *= 2
triangles_at_origin = 3 * coordinate_limit**2
```

The right angle is at the origin (an axis-aligned case with a closed form) or at one of the other two
vertices. For the latter, fixing $P = (x, y)$ makes the perpendicular direction a single primitive
step $(-y/m,\ x/m)$ with $m = \gcd(x, y)$, and the number of lattice points reachable along it is a
`min` of two bounds — closed form again. The `* 2` covers the mirrored direction and the right angle
at $Q$. Disjoint cases, each counted by formula: nothing is enumerated except the $O(N^2)$ choices
of $P$. See [closed-form expression](/topics/technique/closed-form-expression) and
[exploit symmetry](/topics/takeaway/exploit-symmetry).

## When there is no parameter, count states

When the objects resist parametrisation, count *partial* objects grouped by a bounded summary —
[dynamic programming](/topics/technique/dynamic-programming), which is the workhorse here. The
question to ask is: **what is the least I must remember about a prefix to know how it may be
extended?**

Problem 679 counts length-30 words over `{A, E, F, R}` containing each of four keywords exactly
once, with overlaps allowed. The word itself is irrelevant; what matters is the current node of an
[Aho–Corasick automaton](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm) — "the longest
suffix so far that is a prefix of some keyword" — plus a small mask recording how often each keyword
has fired. Thirteen nodes and sixteen mask states replace $10^{18}$ words.

Problem 201 adds a second lesson: **resolve your counters only as finely as the question demands.**
It wants the sum of the subset-sums achieved by exactly one 50-element subset of $\{1^2, \dots,
100^2\}$. The DP therefore never counts subsets — it tracks, per sum, whether it has been achieved
zero times, once, or two-or-more. Capping the multiplicity at two collapses an astronomical counter
into two bits, and two bitsets per subset size carry the entire computation.

Problem 240 introduces a variable the statement never mentions. It counts rolls of $n$ dice whose
top $t$ values sum to $T$ — an [order statistic](https://en.wikipedia.org/wiki/Order_statistic),
awkward because "is this die in the top ten?" depends on every other die. Fixing $v$, the value of
the $t$-th largest die, resolves it: every roll has exactly one such $v$, so the classes are
disjoint and exhaustive, and within a class each die is unambiguously above, equal to, or below the
pivot — a multinomial. *Inventing an auxiliary variable whose values partition the space into
disjoint, individually-countable classes* is the single most transferable idea on this page.

Problem 166 shows the last shape: when the state is too wide, cut the object in half. Its $4 \times
4$ grids with equal row, column and diagonal sums have too many degrees of freedom to enumerate, but
the top and bottom halves interact through only a handful of shared partial sums — so tabulate every
top half by its interface, then look up each bottom half's complement. That is
[meet in the middle](/topics/technique/meet-in-the-middle-attack): $O(|R|^2)$ instead of
$O(|R|^4)$, bought with memory.

## When the predicate is an equality, count collisions

Many counts ask how many tuples satisfy $f(\text{left}) = f(\text{right})$. Then you never need the
tuples: group each side by its value $v$, let $M(v)$ be the size of each group, and the count is
$\sum_v M(v)^2$ — or $\sum_v M_L(v)\,M_R(v)$ when the two sides differ. The whole cost moves from
the number of tuples to the number of **distinct values**, and the hard work becomes finding a key
that makes "equal" checkable by comparing keys.

Problem 963 is the extreme case. It counts the *fair* openings of a two-player game played on four
numbers up to $10^5$ — two on each player's paper — where fair means the player to move loses.
[Combinatorial game theory](/topics/domain/combinatorial-game-theory) turns that into an equality:
the position is the sum of four independent single-number games, the opponent's paper enters
negated, and the first player loses exactly when the sum is zero — so fair means
$G(a_1) + G(a_2) = G(b_1) + G(b_2)$. The game values themselves are exotic (numbers plus
infinitesimals such as $*$ and $\uparrow$), but only about three thousand distinct ones occur, and
each can be written as a short integer vector so that game addition becomes vector addition. From
there it is the collision count: tally the unordered pair sums $M(v)$, square, add. Nothing about
$10^{20}$ quadruples is ever touched — the work is quadratic in the three thousand values, and
grouping them first by their infinitesimal part keeps each tally small.

The lesson generalises past games: when the predicate is an equality, look for the **invariant** —
the coarsest key that still decides it — before you look for an algorithm. See
[split inputs into behaviour classes](/topics/takeaway/split-inputs-into-behaviour-classes).

## Getting the number right

Counting fails silently. There is no exception, no crash, no wrong type — just a number that is a
factor of two off, and nothing to tell you. Three habits catch nearly all of it.

**Use the statement's small case as a test.** Every counting problem here ships one: eleven ways to
check out on 6, forty-one laminae from a hundred tiles, 1111 rolls of five dice. Put it in
`test_cases.json` before writing the real input. It is the only cheap oracle you will get, and it
catches double counting and off-by-one immediately. When the fast method rests on a pattern you
fitted rather than proved, keep the slow reference around and widen the check: problem 963's closed
form for its game values came from a small canonical-form engine, which reproduced $F(5) = 21$ by
brute force and then confirmed the formula for every number up to $10^6$ — ten times past the input
— before the formula was trusted
([calibrate theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers)).

**Decide explicitly when two objects are the same.** Is order significant? Problem 240's statement
spells out that two rolls with the same multiset count separately; problem 109's does the opposite
for the two free darts, while keeping the finishing dart ordered — one problem, both conventions.
Problem 963 mixes them the same way: the two numbers on a paper are unordered, the two papers are
not, so a value paired with itself contributes $w(w+1)/2$ pairs, not $w^2$.
Then check the generation itself: a canonical order ($p < q$, $t \ge 1$) is what turns "I think I
counted each once" into a proof.

**Keep the arithmetic exact.** A count is an integer, so its predicates should be too: problem 112
tests "exactly 99%" by cross-multiplying, never by comparing floats, since a rounding error there
would silently pick the wrong $N$ — see
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality). And counts grow
fast: in C they overflow 64 bits sooner than you expect, which is why several of these solutions
reach for wide or arbitrary-precision types
([watch integer width](/topics/takeaway/watch-integer-width)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0109](/solutions/0109/) — Darts
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0240](/solutions/0240/) — Top Dice
- ○ [0275](/solutions/0275/) — Balanced Sculptures
- ○ [0281](/solutions/0281/) — Pizza Toppings
- ○ [0309](/solutions/0309/) — Integer Ladders
- ○ [0311](/solutions/0311/) — Biclinic Integral Quadrilaterals
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ○ [0369](/solutions/0369/) — Badugi
- ○ [0370](/solutions/0370/) — Geometric Triangles
- ○ [0376](/solutions/0376/) — Nontransitive Sets of Dice
- ○ [0378](/solutions/0378/) — Triangle Triples
- ○ [0397](/solutions/0397/) — Triangle on Parabola
- ○ [0412](/solutions/0412/) — Gnomon Numbering
- ○ [0415](/solutions/0415/) — Titanic Sets
- ○ [0428](/solutions/0428/) — Necklace of Circles
- ○ [0465](/solutions/0465/) — Polar Polygons
- ○ [0466](/solutions/0466/) — Distinct Terms in a Multiplication Table
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0513](/solutions/0513/) — Integral Median
- ○ [0563](/solutions/0563/) — Robot Welders
- ○ [0572](/solutions/0572/) — Idempotent Matrices
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0579](/solutions/0579/) — Lattice Points in Lattice Cubes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0586](/solutions/0586/) — Binary Quadratic Form
- ○ [0600](/solutions/0600/) — Integer Sided Equiangular Hexagons
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ○ [0651](/solutions/0651/) — Patterned Cylinders
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0657](/solutions/0657/) — Incomplete Words
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ● [0679](/solutions/0679/) — Freefarea
- ○ [0696](/solutions/0696/) — Mahjong
- ○ [0726](/solutions/0726/) — Falling Bottles
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0740](/solutions/0740/) — Secret Santa
- ○ [0741](/solutions/0741/) — Binary Grid Colouring
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0762](/solutions/0762/) — Amoebas in a 2D Grid
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0780](/solutions/0780/) — Toriangulations
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0814](/solutions/0814/) — Mezzo-forte
- ○ [0815](/solutions/0815/) — Group by Value
- ○ [0818](/solutions/0818/) — SET
- ○ [0824](/solutions/0824/) — Chess Sliders
- ○ [0837](/solutions/0837/) — Amidakuji
- ○ [0849](/solutions/0849/) — The Tournament
- ○ [0864](/solutions/0864/) — Square + 1 = Squarefree
- ○ [0878](/solutions/0878/) — XOR-Equation B
- ○ [0879](/solutions/0879/) — Touch-screen Password
- ○ [0883](/solutions/0883/) — Remarkable Triangles
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0895](/solutions/0895/) — Gold & Silver Coin Game II
- ○ [0907](/solutions/0907/) — Stacking Cups
- ○ [0922](/solutions/0922/) — Young's Game A
- ○ [0928](/solutions/0928/) — Cribbage
- ● [0963](/solutions/0963/) — Removing Trits
- ○ [0972](/solutions/0972/) — Hyperbolic Plane
- ○ [0987](/solutions/0987/) — Straight Eight
- ○ [0997](/solutions/0997/) — Dice Box
- ○ [1001](/solutions/1001/) — Connections I

<!-- /problems -->
