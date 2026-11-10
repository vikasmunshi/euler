<!-- tags: [counting] -->
<!-- status: final 2026-11-09T07:08Z -->
# Counting

[Counting](https://en.wikipedia.org/wiki/Counting) is the plainest question in the archive — *how
many?* — and the answer is always a single integer. The problems carrying this tag have almost
nothing else in common: dart checkouts, lattice triangles, squarefree integers, words over a
four-letter alphabet, rolls of twenty dice, grids of digits, opening positions of a two-player game,
cribbage hands, arcs drawn over a row of numbers, points on a hyperbolic plane.
About two thirds of them also carry
[combinatorics](/blogs/domain/combinatorics); the rest count number-theoretic or geometric objects
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
nothing — see [size the work to the input](/blogs/takeaway/size-work-to-the-input). Problem 109 is
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
[reduce algebraically before coding](/blogs/takeaway/reduce-before-coding) in its purest form.

The discipline that makes this safe is **bijection**: the reparametrisation must hit every object
exactly once. In problem 173 the symmetry of a frame forces $s - h$ to be even, which is precisely
what makes $t$ an integer, and $(t, h)$ with $t, h \ge 1$ is exactly the set of laminae — no
duplicates, no omissions. In problem 800, insisting on $p < q$ counts each unordered pair once.
Problem 309 (crossed ladders) gets the same guarantee from a classical generator: once a short
argument shows the two wall heights must be integers, each ladder is a Pythagorean triple, and
[Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple#Generating_a_triple) with a
multiplier $k$ produces every triple exactly once. You generate the two million triples, group them
by the leg they share (the street width), and test pairs only inside each group. You never search
over (ladder, ladder, width) at all.

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
of $P$. See [closed-form expression](/blogs/technique/closed-form-expression) and
[exploit symmetry](/blogs/takeaway/exploit-symmetry).

## Count a different set, at a known exchange rate

Sometimes the set you are asked about is awkward, but a nearby set is easy to count and relates to
it by a **fixed multiplier**. Then you count the nearby set and convert. This is
[double counting](https://en.wikipedia.org/wiki/Double_counting_(proof_technique)), and it shows
up in four forms.

**Label, then divide.** Problem 475 splits $12n$ musicians, $n$ quartets of four, into trios with
no two members from the same quartet. Unordered trios are what make it hard. So you label them:
there are exactly $(4n)!$ labelled arrangements per unlabelled one. A labelled arrangement maps to a
0/1 incidence matrix, with quartets as rows, trios as columns, row sums 4 and column sums 3. Each
matrix comes from exactly $4!$ arrangements per row. So the answer is $24^{3n} M / (4n)!$, where $M$
counts matrices, and $M$ is a short DP. The people are gone; only the incidence pattern is left.

**Count representatives, weighted by their fibre.** Problem 928 scores cribbage hands, and every
score depends on how many cards of each rank you hold, never on the suits. A rank-count vector
$(c_1, \dots, c_{13})$ therefore stands for $\prod_r \binom{4}{c_r}$ real hands. You enumerate
$5^{13}$ vectors instead of $2^{52}$ hands, carrying that product as a weight. The quotient is
still too big, so the solution also cuts it at the 9–10 boundary and meets in the middle (see
problem 166 below). But the first factor of a million comes from asking what the score can
actually see.

**Count from every anchor, divide by the overcount.** Problem 972 counts triples of points on a
common geodesic of the Poincaré disc. After moving to Klein coordinates, geodesics become
straight chords, so the question is just which triples of rational points are collinear. From each anchor point, you group the other points by a canonical
key for the line through the anchor, and each group of size $g$ adds $\binom{g}{2}$. Every triple
is seen once from each of its three points, so the total is exactly three times too big, which you
fix by dividing. The same problem layers a second exchange rate on top: the point set has the
eight symmetries of the square, so you only anchor in one octant and weight each anchor by its
orbit size (1, 4 or 8).

**Count the complement.** Problem 612 counts unordered pairs of numbers below $10^{18}$ that share
a digit. Sharing a digit is an OR over ten digits; being disjoint is one subset condition. So you
count the disjoint ordered pairs $D$, and the answer is $(T^2 - D - T)/2$: subtract $D$ from all
ordered pairs, remove the $T$ self-pairs, and halve. The awkward predicate is never evaluated
directly.

All four have the same risk. The exchange rate has to be **exact**, the same for every object, and
it has to be proved, not assumed. Labelling works because the trios are distinct non-empty sets.
The overcount in 972 is exactly three because three points determine at most one line. Check the
rate on the statement's small case before trusting it: $n = 1$ in problem 475 must give the
statement's 576.

## When there is no parameter, count states

When the objects resist parametrisation, count *partial* objects grouped by a bounded summary —
[dynamic programming](/blogs/technique/dynamic-programming), which is the workhorse here. The
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

When the parts of a partial object are interchangeable, the state can be a **histogram**: you
record how many parts are in each condition, not which ones. In problem 475's incidence matrix,
columns with the same number of ones behave identically. So the state after each row is just how
many columns hold 0, 1, 2 or 3 ones. Two of those four counters are fixed by invariants, so the
table is $O(n^2)$ instead of $2^{4n}$. Each row moves the histogram by one of fifteen splits, each
weighted by a product of binomials.

Problem 1001 shows another shape: **decide what happens to the first element, and the rest falls
apart into independent pieces.** It counts subsets of $n$ intervals with no two crossing (a
[laminar family](https://en.wikipedia.org/wiki/Laminar_set_family)). The crossing graph is far too
dense to split up. But look at the leftmost position $l$ of a range. Either the interval starting
there is left out, which leaves the range $[l+1, r]$, or it is chosen. If it is chosen, nothing can
cross it, so the remaining choices are whatever lies strictly inside it times whatever lies after
it. That gives

$$C_r[l] = C_r[l+1] + g(l)\, C_r[p+1].$$

It uses the [product rule](https://en.wikipedia.org/wiki/Rule_of_product) for independent pieces
and the sum rule for exclusive cases. Interval DP, and most "Catalan-like" counts, come from this
same recurrence shape. The remaining work is engineering. Only one column per right end is ever
read, so the total cost is the sum of the interval lengths, not $N^2$.

Problem 166 shows the last shape: when the state is too wide, cut the object in half. Its $4 \times
4$ grids with equal row, column and diagonal sums have too many degrees of freedom to enumerate, but
the top and bottom halves interact through only a handful of shared partial sums — so tabulate every
top half by its interface, then look up each bottom half's complement. That is
[meet in the middle](/blogs/technique/meet-in-the-middle-attack): $O(|R|^2)$ instead of
$O(|R|^4)$, bought with memory. The skill is choosing the cut where the interface is narrowest.
Problem 928 cuts cribbage ranks between 9 and 10. A fifteen can hold at most one ten-valued card,
and only one run can cross the cut. So the two halves interact through a few small numbers: the
number of low-card subsets that sum to 5, and the length and product of the open run.

## When the predicate is an equality, count collisions

Many counts ask how many tuples satisfy $f(\text{left}) = f(\text{right})$. Then you never need the
tuples: group each side by its value $v$, let $M(v)$ be the size of each group, and the count is
$\sum_v M(v)^2$ — or $\sum_v M_L(v)\,M_R(v)$ when the two sides differ. The whole cost moves from
the number of tuples to the number of **distinct values**, and the hard work becomes finding a key
that makes "equal" checkable by comparing keys.

Problem 963 is the extreme case. It counts the *fair* openings of a two-player game played on four
numbers up to $10^5$ — two on each player's paper — where fair means the player to move loses.
[Combinatorial game theory](/blogs/domain/combinatorial-game-theory) turns that into an equality:
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
[split inputs into behaviour classes](/blogs/takeaway/split-inputs-into-behaviour-classes).

The same tally works when the predicate is **containment** instead of equality. Problem 612 sorts
every number below the bound into one of 1024 classes, keyed by its set of decimal digits. A
[digit DP](https://codeforces.com/blog/entry/53960) gives the class sizes $c_S$ in time that grows
only with the number of digits. Two numbers are disjoint when one's set is a subset of the other's
complement, so the pair count is $\sum_S c_S F(\overline S)$, where $F(M) = \sum_{S' \subseteq M}
c_{S'}$. One [zeta transform](https://en.wikipedia.org/wiki/Incidence_algebra) builds every $F$ in
$10 \cdot 2^{10}$ additions. Where $\sum M(v)^2$ pairs classes on equal keys, the subset-sum
transform pairs them on nested keys.

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
([calibrate theory on known answers](/blogs/takeaway/calibrate-theory-on-known-answers)).
The strongest check uses a method that **does not share your reduction**. Problem 475's
matrix-and-divide formula was checked against a direct count that builds trios one at a time and
never forms a matrix. A shared mistake in the exchange rate cannot pass a check that never uses it.

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
[exact arithmetic for equality](/blogs/takeaway/exact-arithmetic-for-equality). And counts grow
fast: in C they overflow 64 bits sooner than you expect, which is why several of these solutions
reach for wide or arbitrary-precision types
([watch integer width](/blogs/takeaway/watch-integer-width)).

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
- ● [0309](/solutions/0309/) — Integer Ladders
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
- ● [0475](/solutions/0475/) — Music Festival
- ○ [0513](/solutions/0513/) — Integral Median
- ○ [0563](/solutions/0563/) — Robot Welders
- ○ [0572](/solutions/0572/) — Idempotent Matrices
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0579](/solutions/0579/) — Lattice Points in Lattice Cubes
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0586](/solutions/0586/) — Binary Quadratic Form
- ○ [0600](/solutions/0600/) — Integer Sided Equiangular Hexagons
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ● [0612](/solutions/0612/) — Friend Numbers
- ○ [0620](/solutions/0620/) — Planetary Gears
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ○ [0651](/solutions/0651/) — Patterned Cylinders
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0657](/solutions/0657/) — Incomplete Words
- ● [0678](/solutions/0678/) — Fermat-like Equations
- ● [0679](/solutions/0679/) — Freefarea
- ○ [0696](/solutions/0696/) — Mahjong
- ● [0726](/solutions/0726/) — Falling Bottles
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0740](/solutions/0740/) — Secret Santa
- ○ [0741](/solutions/0741/) — Binary Grid Colouring
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0762](/solutions/0762/) — Amoebas in a 2D Grid
- ● [0771](/solutions/0771/) — Pseudo Geometric Sequences
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
- ● [0883](/solutions/0883/) — Remarkable Triangles
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0895](/solutions/0895/) — Gold & Silver Coin Game II
- ○ [0907](/solutions/0907/) — Stacking Cups
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0928](/solutions/0928/) — Cribbage
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0972](/solutions/0972/) — Hyperbolic Plane
- ○ [0997](/solutions/0997/) — Dice Box
- ● [1001](/solutions/1001/) — Connections I

<!-- /problems -->
