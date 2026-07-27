<!-- tags: [combinatorics] -->
<!-- status: final -->
# Combinatorics

[Combinatorics](https://en.wikipedia.org/wiki/Combinatorics) is the mathematics of finite
arrangements: how many ways are there to choose, order, tile, colour, or partition a finite
collection under some rule. It is the largest domain in this archive — 286 problems carry the tag,
more than any other — and that is not an accident of tagging. Project Euler's favourite question
shape is "how many …?" asked at a size where the answer cannot be reached by listing. The whole
discipline of the domain lives in that gap: **you are asked for a count you can never enumerate**,
so you must find the structure that lets you compute it instead.

## Counting without enumerating

The gap is worth making concrete. Problem 191 asks how many prize strings of length $n$ over a
three-letter alphabet avoid three consecutive absences and contain at most one late mark. At
$n = 4$ there are $3^4 = 81$ candidates and you can filter them by hand. At $n = 30$ there are
over 200 trillion. At $n = 100$ the candidate space has 48 digits, and no amount of hardware
closes that.

What rescues it is an observation that recurs, in some form, in nearly every problem on this
page: **whether a partial configuration can be legally extended depends only on a small, bounded
summary of it, not on its full contents.** For problem 191 the summary is two facts — have I used
my one late mark, and how many absences sit at the tail (0, 1, or 2, since 3 is illegal and any
other letter resets the run). Everything else about the prefix is irrelevant to its future. That
collapses an exponential history into six states, and the count falls out of a linear sweep.

Finding that summary is the intellectual work. Once you have it, the code is short.

## Model before you count

Before any technique, settle the question every combinatorial problem quietly asks: **when are two
configurations the same one?** Does order matter ([permutations](/topics/domain/permutation)) or
not ([combinations](/topics/technique/combination))? Are the objects labelled or interchangeable?
Is the result a set, a multiset, or a sequence? Get this wrong and a perfectly correct algorithm
returns a perfectly wrong number.

Problem 31 (public, `solutions/public/p0031/`) is the cleanest illustration in the archive. Counting
the ways to make £2 from British coins is an unbounded knapsack count, and the entire
order-matters-or-not distinction lives in the *nesting order of two loops*:

```python
result = [1] + [0] * target_amount
for coin in coins:                              # coins outer: each coin folded in once,
    for i in range(coin, target_amount + 1):    # in a fixed order, so {1,2} and {2,1}
        result[i] += result[i - coin]           # have exactly one construction path
```

Swap the loops and you count ordered sequences instead of unordered combinations — a different
question, off by orders of magnitude, with no error message. Problem 181 (grouping two colours of
indistinguishable objects) is the same discipline in two dimensions: each group-type is folded in
completely, in one canonical order, so every multiset is built exactly once.

## The four shapes an answer takes

Across these problems the resolution nearly always falls into one of four moves.

**A closed form.** The best outcome: the count is a formula you evaluate in constant time. Choosing
$k$ of $n$ is a [binomial coefficient](/topics/domain/binomial-coefficient); a sub-rectangle of a
grid is fixed by choosing two of the $m+1$ vertical lines and two of the $n+1$ horizontal ones, so
a grid holds $\binom{m+1}{2}\binom{n+1}{2}$ of them — problem 85's brute-force position count
collapses to that. [Catalan numbers](/topics/domain/catalan-number) count balanced structures;
[necklace counting](/topics/domain/necklace-counting) handles arrangements up to rotation. Problem
24's rank-to-permutation unranking is a closed form in disguise: repeated `divmod` by $(n-1)!$ picks
each digit directly, never touching the million permutations it skips. See
[closed-form expression](/topics/technique/closed-form-expression).

**A recurrence, evaluated as a table.** When no formula exists, decompose by the last decision. It
is the single most common shape here — [dynamic programming](/topics/technique/dynamic-programming)
is the most frequent technique across the solved problems on this list. Problem 116 asks for tilings
of a row with one tile length $L$: the rightmost tile is either a unit square or a length-$L$ block,
the two cases are disjoint and exhaustive, so $dp[i] = dp[i-1] + dp[i-L]$. Problems 114, 115 and 117
vary the same skeleton; problem 215 stacks it, encoding each brick row as a bitmask of its internal
seams so that "no running crack" becomes `mask_a & mask_b == 0`, and the wall count becomes a
layered walk over a compatibility graph. The pattern is always: define the state, enumerate the last
move, sum the disjoint cases. See also [recurrence relations](/topics/domain/recurrence-relation)
and [generating functions](/topics/domain/generating-function), which are the same recurrences
written as algebra.

**Count the complement, or inclusion–exclusion.** "At least one" is usually harder than "none".
Problem 116 subtracts the single all-grey tiling rather than tracking a "used a colour yet?" flag
through the recurrence. When constraints overlap, [inclusion–exclusion](/topics/technique/inclusion-exclusion-principle)
adds back what double-subtraction removed. Reach for it whenever the forbidden set is easier to
describe than the permitted one.

**Quotient by symmetry.** If configurations related by rotation, reflection, or relabelling count as
one, do not enumerate and deduplicate — divide the work by the symmetry group up front, or count
orbits directly. Problem 53 gets a small version free: Pascal's rows are symmetric and unimodal, so
the first $r$ whose entry exceeds the threshold settles the whole middle of the row at once.

```python
for r in range(0, n // 2 + 1):
    if c > threshold:
        count += n - 2 * r + 1      # symmetry: entries r..n-r all qualify
        break
    c = c * (n - r) // (r + 1)      # Pascal's recurrence, no factorials
```

Note the second line as well: that recurrence sidesteps building $n!$ entirely. See
[exploit symmetry](/topics/takeaway/exploit-symmetry).

## The counts themselves are the other hazard

Combinatorial answers grow explosively, and this domain's most common companion tag is
[modular arithmetic](/topics/domain/modular-arithmetic) — 78 of these 286 problems carry it. That
pairing is the point: either the problem hands you a modulus (`1_000_000_007`, so the residue *is*
the deliverable and you work in the ring from line one), or it wants the honest integer and you
need [arbitrary precision](/topics/technique/arbitrary-precision-arithmetic). Python gives you the
latter free; in C the same count silently overflows, which is why
[watch integer width](/topics/takeaway/watch-integer-width) shows up so often alongside these.
Decide which régime you are in *before* writing the accumulator.

Watch the intermediate values too, not just the answer. Computing $\binom{n}{k}$ as
$n! / (k!(n-k)!)$ builds enormous factorials to produce a modest result; the Pascal recurrence above
keeps every intermediate near the size of the answer.

## How to reason about it

The cue is a question that begins "how many" — arrangements, tilings, selections, colourings,
paths, partitions — at a size where listing them is hopeless. When you catch it:

- **Fix the equivalence first.** Ordered or unordered, labelled or identical, set or multiset.
  Write the definition down before writing a loop; most wrong answers here are modelling errors,
  not bugs.
- **Look for the bounded summary.** What is the least you must remember about a prefix to know how
  it may be extended? If that summary is small and finite, you have a DP state and the problem is
  essentially solved.
- **Try to decompose by the last decision.** Cases that are disjoint and exhaustive give a
  recurrence directly; if they overlap, you need inclusion–exclusion instead.
- **Ask whether a formula exists.** A binomial, a Catalan number, a product rule — a closed form
  beats any table. Check [OEIS](https://oeis.org/) with the first few hand-computed terms; a
  matching sequence often comes with the formula attached.
- **Count the complement when "at least one" appears.** Constraints phrased as prohibitions are
  usually cheaper counted the other way round.
- **Decide the arithmetic régime up front.** A stated modulus means reduce after every operation;
  no modulus means big integers, and in C that means thinking about width before the first
  multiply.

Brute force does have a place — it is how you get the small terms that verify a formula or seed a
sequence lookup. Just never expect it to reach the answer. The domain is defined by the distance
between what you can enumerate and what you are asked to count, and every technique here is a way
of crossing it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0011](/solutions/0011/) — Largest Product in a Grid
- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0031](/solutions/0031/) — Coin Sums
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0109](/solutions/0109/) — Darts
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0228](/solutions/0228/) — Minkowski Sums
- ○ [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ○ [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ○ [0240](/solutions/0240/) — Top Dice
- ○ [0242](/solutions/0242/) — Odd Triplets
- ○ [0244](/solutions/0244/) — Sliders
- ○ [0247](/solutions/0247/) — Squares Under a Hyperbola
- ○ [0249](/solutions/0249/) — Prime Subset Sums
- ○ [0253](/solutions/0253/) — Tidying Up A
- ○ [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0259](/solutions/0259/) — Reachable Numbers
- ○ [0265](/solutions/0265/) — Binary Circles
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ○ [0270](/solutions/0270/) — Cutting Squares
- ○ [0275](/solutions/0275/) — Balanced Sculptures
- ○ [0276](/solutions/0276/) — Primitive Triangles
- ○ [0281](/solutions/0281/) — Pizza Toppings
- ○ [0289](/solutions/0289/) — Eulerian Cycles
- ○ [0292](/solutions/0292/) — Pythagorean Polygons
- ○ [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ○ [0307](/solutions/0307/) — Chip Defects
- ○ [0319](/solutions/0319/) — Bounded Sequences
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0331](/solutions/0331/) — Cross Flips
- ○ [0333](/solutions/0333/) — Special Partitions
- ○ [0338](/solutions/0338/) — Cutting Rectangular Grid Paper
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0350](/solutions/0350/) — Constraining the Least Greatest and the Greatest Least
- ○ [0361](/solutions/0361/) — Subsequence of Thue-Morse Sequence
- ○ [0362](/solutions/0362/) — Squarefree Factors
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ○ [0369](/solutions/0369/) — Badugi
- ○ [0371](/solutions/0371/) — Licence Plates
- ○ [0376](/solutions/0376/) — Nontransitive Sets of Dice
- ○ [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ○ [0378](/solutions/0378/) — Triangle Triples
- ○ [0380](/solutions/0380/) — Amazing Mazes!
- ○ [0382](/solutions/0382/) — Generating Polygons
- ○ [0386](/solutions/0386/) — Maximum Length of an Antichain
- ○ [0393](/solutions/0393/) — Migrating Ants
- ○ [0398](/solutions/0398/) — Cutting Rope
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0412](/solutions/0412/) — Gnomon Numbering
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0415](/solutions/0415/) — Titanic Sets
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0426](/solutions/0426/) — Box-Ball System
- ○ [0427](/solutions/0427/) — $n$-sequences
- ○ [0430](/solutions/0430/) — Range Flips
- ○ [0434](/solutions/0434/) — Rigid Graphs
- ○ [0438](/solutions/0438/) — Integer Part of Polynomial Equation's Solutions
- ○ [0452](/solutions/0452/) — Long Products
- ○ [0453](/solutions/0453/) — Lattice Quadrilaterals
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0458](/solutions/0458/) — Permutations of Project
- ○ [0462](/solutions/0462/) — Permutation of 3-smooth Numbers
- ○ [0465](/solutions/0465/) — Polar Polygons
- ○ [0466](/solutions/0466/) — Distinct Terms in a Multiplication Table
- ○ [0469](/solutions/0469/) — Empty Chairs
- ○ [0472](/solutions/0472/) — Comfortable Distance II
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0480](/solutions/0480/) — The Last Question
- ○ [0483](/solutions/0483/) — Repeated Permutation
- ○ [0486](/solutions/0486/) — Palindrome-containing Strings
- ○ [0490](/solutions/0490/) — Jumping Frog
- ○ [0491](/solutions/0491/) — Double Pandigital Number Divisible by $11$
- ○ [0494](/solutions/0494/) — Collatz Prefix Families
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0502](/solutions/0502/) — Counting Castles
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ○ [0519](/solutions/0519/) — Tricoloured Coin Fountains
- ○ [0520](/solutions/0520/) — Simbers
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0523](/solutions/0523/) — First Sort I
- ○ [0524](/solutions/0524/) — First Sort II
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0529](/solutions/0529/) — $10$-substrings
- ○ [0534](/solutions/0534/) — Weak Queens
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0544](/solutions/0544/) — Chromatic Conundrum
- ○ [0553](/solutions/0553/) — Power Sets of Power Sets
- ○ [0557](/solutions/0557/) — Cutting Triangles
- ○ [0559](/solutions/0559/) — Permuted Matrices
- ○ [0564](/solutions/0564/) — Maximal Polygons
- ○ [0572](/solutions/0572/) — Idempotent Matrices
- ○ [0573](/solutions/0573/) — Unfair Race
- ○ [0577](/solutions/0577/) — Counting Hexagons
- ○ [0579](/solutions/0579/) — Lattice Points in Lattice Cubes
- ○ [0584](/solutions/0584/) — Birthday Problem Revisited
- ○ [0590](/solutions/0590/) — Sets with a Given Least Common Multiple
- ○ [0594](/solutions/0594/) — Rhombus Tilings
- ○ [0595](/solutions/0595/) — Incremental Random Sort
- ○ [0597](/solutions/0597/) — Torpids
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0599](/solutions/0599/) — Distinct Colourings of a Rubik's Cube
- ○ [0600](/solutions/0600/) — Integer Sided Equiangular Hexagons
- ○ [0602](/solutions/0602/) — Product of Head Counts
- ○ [0606](/solutions/0606/) — Gozinta Chains II
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0628](/solutions/0628/) — Open Chess Positions
- ○ [0630](/solutions/0630/) — Crossed Lines
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ○ [0635](/solutions/0635/) — Subset Sums
- ○ [0636](/solutions/0636/) — Restricted Factorisations
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ○ [0645](/solutions/0645/) — Every Day Is a Holiday
- ○ [0651](/solutions/0651/) — Patterned Cylinders
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0657](/solutions/0657/) — Incomplete Words
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0662](/solutions/0662/) — Fibonacci Paths
- ○ [0669](/solutions/0669/) — The King's Banquet
- ○ [0670](/solutions/0670/) — Colouring a Strip
- ○ [0671](/solutions/0671/) — Colouring a Loop
- ○ [0677](/solutions/0677/) — Coloured Graphs
- ● [0679](/solutions/0679/) — Freefarea
- ○ [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ○ [0688](/solutions/0688/) — Piles of Plates
- ○ [0690](/solutions/0690/) — Tom and Jerry
- ○ [0696](/solutions/0696/) — Mahjong
- ○ [0698](/solutions/0698/) — 123 Numbers
- ○ [0701](/solutions/0701/) — Random Connected Area
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0709](/solutions/0709/) — Even Stevens
- ● [0710](/solutions/0710/) — One Million Members
- ○ [0713](/solutions/0713/) — Turán's Water Heating System
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0724](/solutions/0724/) — Drone Delivery
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ○ [0726](/solutions/0726/) — Falling Bottles
- ○ [0728](/solutions/0728/) — Circle of Coins
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0736](/solutions/0736/) — Paths to Equality
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ○ [0740](/solutions/0740/) — Secret Santa
- ○ [0741](/solutions/0741/) — Binary Grid Colouring
- ○ [0744](/solutions/0744/) — What? Where? When?
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ○ [0762](/solutions/0762/) — Amoebas in a 2D Grid
- ○ [0763](/solutions/0763/) — Amoebas in a 3D Grid
- ○ [0766](/solutions/0766/) — Sliding Block Puzzle
- ○ [0767](/solutions/0767/) — Window into a Matrix II
- ○ [0768](/solutions/0768/) — Chandelier
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0778](/solutions/0778/) — Freshman's Product
- ○ [0780](/solutions/0780/) — Toriangulations
- ○ [0781](/solutions/0781/) — Feynman Diagrams
- ○ [0782](/solutions/0782/) — Distinct Rows and Columns
- ○ [0783](/solutions/0783/) — Urns
- ○ [0786](/solutions/0786/) — Billiard
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0796](/solutions/0796/) — A Grand Shuffle
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0807](/solutions/0807/) — Loops of Ropes
- ○ [0814](/solutions/0814/) — Mezzo-forte
- ○ [0815](/solutions/0815/) — Group by Value
- ○ [0818](/solutions/0818/) — SET
- ○ [0819](/solutions/0819/) — Iterative Sampling
- ○ [0824](/solutions/0824/) — Chess Sliders
- ○ [0828](/solutions/0828/) — Numbers Challenge
- ○ [0837](/solutions/0837/) — Amidakuji
- ○ [0842](/solutions/0842/) — Irregular Star Polygons
- ○ [0847](/solutions/0847/) — Jack's Bean
- ○ [0848](/solutions/0848/) — Guessing with Sets
- ○ [0849](/solutions/0849/) — The Tournament
- ○ [0851](/solutions/0851/) — SOP and POS
- ○ [0856](/solutions/0856/) — Waiting for a Pair
- ○ [0857](/solutions/0857/) — Beautiful Graphs
- ○ [0858](/solutions/0858/) — LCM
- ○ [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ○ [0866](/solutions/0866/) — Tidying Up B
- ○ [0867](/solutions/0867/) — Tiling Dodecagon
- ○ [0873](/solutions/0873/) — Words with Gaps
- ○ [0878](/solutions/0878/) — XOR-Equation B
- ○ [0879](/solutions/0879/) — Touch-screen Password
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0886](/solutions/0886/) — Coprime Permutations
- ○ [0887](/solutions/0887/) — Bounded Binary Search
- ○ [0888](/solutions/0888/) — 1249 Nim
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0892](/solutions/0892/) — Zebra Circles
- ○ [0895](/solutions/0895/) — Gold & Silver Coin Game II
- ○ [0896](/solutions/0896/) — Divisible Ranges
- ○ [0902](/solutions/0902/) — Permutation Powers
- ○ [0903](/solutions/0903/) — Total Permutation Powers
- ○ [0906](/solutions/0906/) — A Collective Decision
- ○ [0907](/solutions/0907/) — Stacking Cups
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0913](/solutions/0913/) — Row-major vs Column-major
- ○ [0916](/solutions/0916/) — Restricted Permutations
- ○ [0922](/solutions/0922/) — Young's Game A
- ○ [0923](/solutions/0923/) — Young's Game B
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ○ [0928](/solutions/0928/) — Cribbage
- ○ [0930](/solutions/0930/) — The Gathering
- ○ [0936](/solutions/0936/) — Peerless Trees
- ○ [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0948](/solutions/0948/) — Left vs Right
- ○ [0949](/solutions/0949/) — Left vs Right II
- ○ [0950](/solutions/0950/) — Pirate Treasure
- ○ [0951](/solutions/0951/) — A Game of Chance
- ○ [0954](/solutions/0954/) — Heptaphobia
- ○ [0957](/solutions/0957/) — Point Genesis
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0964](/solutions/0964/) — Musical Chairs Revisited
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0973](/solutions/0973/) — Random Dealings
- ○ [0976](/solutions/0976/) — XO Game
- ○ [0977](/solutions/0977/) — Iterated Functions
- ○ [0979](/solutions/0979/) — Heptagon Hopping
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ○ [0984](/solutions/0984/) — Knights and Horses
- ○ [0987](/solutions/0987/) — Straight Eight
- ○ [0988](/solutions/0988/) — Non-attacking Frogs
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ○ [0993](/solutions/0993/) — Banana Beaver
- ○ [0994](/solutions/0994/) — Counting Triangles
- ○ [0996](/solutions/0996/) — Overtakes
- ○ [0997](/solutions/0997/) — Dice Box
- ○ [1001](/solutions/1001/) — Connections I
- ○ [1003](/solutions/1003/) — Lonely Singles
- ○ [1004](/solutions/1004/) — Balanced Integer
- ○ [1005](/solutions/1005/) — Median Prime List
- ○ [1006](/solutions/1006/) — Fibonacci Subwords
- ○ [1007](/solutions/1007/) — Alternating Difference

<!-- /problems -->
