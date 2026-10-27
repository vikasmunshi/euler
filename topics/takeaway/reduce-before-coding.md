<!-- tags: [reduce-before-coding] -->
<!-- status: final 2026-10-15T10:15Z -->
# Reduce algebraically before coding

Before you write a loop, ask what the loop is really computing — and whether the
mathematics will hand you the answer with less work, or none. Reducing
algebraically before coding is the habit of spending five minutes with pen and
paper on a problem's structure so the program that follows is smaller, tighter,
or gone entirely. The payoff runs from the modest (one nested loop removed) to
the total (an O(n) scan collapsed to a formula), but it is the same move every
time: simplify the math first, because the cheapest loop is the one you never
have to run. Past the first hundred problems it stops being optional — the
search spaces run to $2^{669}$ subsets or $10^{24}$ index pairs, and the only
program that finishes is the one written after the reduction.

## The reduction, in degrees

A reduction is any algebraic step that shrinks the work *before* it becomes code.
The problems below reach for it at four escalating strengths.

**Eliminate a variable.** A constraint that ties two unknowns together lets you
solve for one and delete a whole dimension of search. In
[Special Pythagorean Triplet](/solutions/0009/) the sum condition $a + b + c = S$
means $c$ is never searched — it is computed, $c = S - a - b$ — so a naive
three-nested-loop hunt over $(a, b, c)$ becomes a two-loop scan over $(a, b)$,
$O(S^3)$ down to $O(S^2)$. Nothing clever happened; one line of algebra removed
an entire loop.

**Prune the domain.** The same ordering $a < b < c$ that eliminates $c$ also
*bounds* what is left: $a$ cannot exceed $S/4$ and $b$ cannot exceed $S/2$, or no
valid larger values fit. Deriving the tightest bounds before the loop is written
keeps the search inside the region that can actually contain an answer. The
[cheap-checks-first](/topics/takeaway/cheap-checks-first) and
[exploit-symmetry](/topics/takeaway/exploit-symmetry) takeaways are this same
instinct pointed at the loop body and the coordinate system.

**Exploit structure to skip work.** Sometimes the sequence itself has a pattern
that lets you step over most of it. [Even Fibonacci Numbers](/solutions/0002/)
never tests a single term for evenness: the parities of the
[Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence) run
odd, even, odd with period three forever, so every third term is even, and
expanding the recurrence three times gives a direct rule
$E(k+1) = 4E(k) + E(k-1)$ that walks the even terms alone. The divisibility test
is not optimised — it is *derived away*.

**Close the form.** At the far end, the structure is regular enough that the loop
disappears into a single expression. [Counting Rectangles](/solutions/0085/)
sees that a sub-rectangle is fixed by choosing two of $H+1$ horizontal and two of
$W+1$ vertical grid lines, so the count *factors* into
$T(H)\cdot T(W)$ with $T(n) = \tfrac{n(n+1)}{2}$ — two independent
[triangular numbers](https://en.wikipedia.org/wiki/Triangular_number) instead of
a two-dimensional enumeration. [Number Spiral Diagonals](/solutions/0028/) sums
each ring's four corners in closed form to
$\tfrac{N(N(4N+3)+8)-9}{6}$, an $O(N^2)$ grid replaced by one arithmetic line.
The same move scales a long way: [Odd Triplets](/solutions/0242/) asks about
roughly $10^{24}$ pairs $(n, k)$, but only about the *parity* of a subset count,
and two applications of
[Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) reduce that
parity to $\binom{n-1}{k-1} \bmod 2$ — so each admissible $n = 4t + 1$
contributes $2^{\mathrm{popcount}(t)}$ pairs, and nothing is ever counted one
at a time. This is the endpoint the [closed-form-over-iteration](/topics/takeaway/closed-form-over-iteration)
takeaway is about; reducing before coding is the wider discipline that *reaches*
it — and that is content to stop one step short when the algebra will not close
all the way.

## Reductions that change the question

The four degrees above simplify a computation that is already the right one.
The harder problems on the list mostly need something earlier: a reduction that
changes *what* is computed before any of it is simplified. Four such moves
recur.

**Restate the condition.** The question as posed is often the awkward form of
an easier one. [Twenty-two Foolish Primes](/solutions/0239/) asks for 22 of
the 25 primes to be *away* from home; "3 are at home" is the same event, and
fixed points are what
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
counts well. [Coresilience](/solutions/0245/) asks for a unit fraction, which
is a divisibility, which forces $n$ to be squarefree and turns the search into a
construction. [A Game of Chance](/solutions/0951/) asks whether a deck is fair;
that is a statement about the parity of the turn count, the parity factors over
the deck's single-colour runs, and the run bias obeys a small recurrence that
is zero at exactly one length — so "fair" becomes a pattern-avoidance count with
no probability left in it. Each restatement is a line of algebra, and each one
is where the problem actually gets solved.

**Translate into a known object.** Sometimes the restated problem is one that
mathematics has already solved under another name. The Diophantine-reciprocal
problems [108](/solutions/0108/) and [110](/solutions/0110/) become
[divisor counting](https://en.wikipedia.org/wiki/Divisor_function).
[Cross Flips](/solutions/0331/) is
[Lights Out](https://en.wikipedia.org/wiki/Lights_Out_(game)), and so linear
algebra over $\mathbb{F}_2$. [Chandelier](/solutions/0768/) is divisibility by
a [cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial).
[March of the Penguins](/solutions/1010/) is a walk through Young diagrams,
whose complete marches are
[standard Young tableaux](https://en.wikipedia.org/wiki/Young_tableau) counted
by the [hook length formula](https://en.wikipedia.org/wiki/Hook_length_formula) —
so about $10^{16}$ partitions collapse to $n$ hook-length exponents.
[Removing Bits](/solutions/0882/) is a partisan game whose positions are
[surreal numbers](https://en.wikipedia.org/wiki/Surreal_number) that simply
add. Once the object has a name, its theory comes with it, and the code
implements a theorem rather than a search.

**Keep only what the answer reads.** Most inputs carry far more information
than the question uses, and finding the part it uses shrinks the state.
[$250250$](/solutions/0250/) needs each $k^k$ only modulo 250, so a quarter of
a million elements collapse to a census of 250 residues.
[A Huge Binomial Coefficient](/solutions/0365/) never forms a number with nine
billion digits: the squarefree modulus splits by the
[Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
into prime fields, where Lucas' theorem answers digit by digit.
[Digital Root Clocks](/solutions/0315/) shows the per-prime saving depends only
on the last two digits and the digit sum, so two small tables replace any
simulation. [Rounded Square Roots](/solutions/0255/) reads $n$ only through
$\lceil n/x \rceil$, so whole intervals of $n$ share a path and are processed
as one. The question to ask is: *what is this result actually a function of?*
The answer is the real state space.

**Search the answer's structure, not the input range.** When the inputs are too
many to visit, walk the thing that generates the answers instead.
[Prime Factors of $n^{15}+1$](/solutions/0421/) exchanges the order of
summation — instead of factorising $10^{11}$ huge numbers, it asks each of
the primes below $10^8$ how many $n$ it divides, which group theory answers
in $O(1)$. [Euler's Totient Function Equals 13!](/solutions/0248/) inverts
$\varphi$ by enumerating factorisations of the target into
$p^{a-1}(p-1)$ pieces — a few hundred candidate primes rather than tens of
billions of candidate $n$. [Modular Cubes, Part 2](/solutions/0272/) and
[Perfection Quotients](/solutions/0241/) likewise build $n$ from the prime
factors the condition demands, and
[Sums of Digit Factorials](/solutions/0254/) inverts a chain of digit functions
through the
[factorial number system](https://en.wikipedia.org/wiki/Factorial_number_system)
rather than iterating it. Construction beats filtering whenever the answers are
sparse and the space is not.

## How to reason about it

Reach for a reduction whenever the quantities you are about to iterate over are
*related by a rule* rather than being arbitrary data — a linear constraint, an
ordering, a recurrence, a symmetry, a counting structure. The tell is that you
can write down an equation the answer must satisfy. Spend the algebra there: each
equation you solve is a loop you delete, a dimension you drop, or a bound you
tighten. A second tell is a search space that dwarfs the answer — $2^{669}$
subsets when only the totals matter, as in
[Prime Subset Sums](/solutions/0249/), or $40!$ fill orders when the state that matters is a
step count, a segment count and two boundary flags, as in [Tidying Up A](/solutions/0253/). That gap means
the problem has a smaller state hiding in it, and finding that state is the
reduction.

Three cautions keep the habit honest:

- **Know when to stop.** Not every problem closes into a formula, and forcing one
  produces fragile, wrong code. [Counting Rectangles](/solutions/0085/) reduces
  the *count* to $T(H)\cdot T(W)$ but still searches grid shapes for the one
  nearest a target, because that outer question has no closed form — the honest
  reduction is partial, and that is fine. A reduction that removes one loop of
  three is already a win. Most of the later reductions end the same way — in a
  smaller computation, not a formula: a generating-function DP over board
  positions in [Overtakes](/solutions/0996/), a four-wide table over depth in
  [Pythagorean Tree](/solutions/0395/).
- **Derive, then verify.** An algebraic reduction is only as good as its
  derivation, and an off-by-one in a bound or a dropped term fails silently. Keep
  the brute-force version as an oracle and check the two against each other on
  small inputs — [Number Spiral Diagonals](/solutions/0028/) ships exactly that,
  running an $O(N^2)$ spiral simulation under `--show` purely to confirm its
  formula. The check matters most when the reduction is a guess.
  [Chandelier](/solutions/0768/) is the warning: "every balanced set is a union
  of regular polygons" is a theorem when $n$ has at most two prime factors and
  false for 360, which has three — already in $\mathbb{Z}_{30}$ there are 525
  balanced 6-subsets against 495 polygon unions. [Overtakes](/solutions/0996/)
  shows the honest version: its characterisation was conjectured, then checked
  against a breadth-first brute force for every $n \le 7$ before any fast code
  was trusted. And small edge cases hide in correct derivations too: in
  [Euler's Totient Function Equals 13!](/solutions/0248/) the factor contributed
  by the prime 2 at exponent 1 is $1$, so a search that stops when the residual
  target reaches 1 silently drops half the solutions.
- **Mind the arithmetic you introduce.** Reductions multiply before they divide
  and can form intermediates far larger than the answer — an overflow risk in C,
  and a reason to keep the algebra in exact integers (compute $c = S - a - b$, not
  $\sqrt{a^2+b^2}$) so equality checks stay reliable. See
  [exact-arithmetic-for-equality](/topics/takeaway/exact-arithmetic-for-equality).
  An alternating inclusion–exclusion sum, as in
  [Twenty-two Foolish Primes](/solutions/0239/), cancels catastrophically, so it
  stays in exact integers until the final division. Reducing modulo the
  requested digits is safe only when the reduced formula uses addition and
  multiplication alone — true of the subset-sum table in
  [Prime Subset Sums](/solutions/0249/), and something to check rather than
  assume once a division appears.

The discipline underneath all of it is order of operations, in the human sense:
do the mathematics *first*. A loop written before the algebra is a loop you will
optimise later; a loop written after it is often a loop you never write at all.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0109](/solutions/0109/) — Darts
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0127](/solutions/0127/) — abc-hits
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0144](/solutions/0144/) — Laser Beam Reflections
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0227](/solutions/0227/) — The Chase
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0232](/solutions/0232/) — The Race
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0240](/solutions/0240/) — Top Dice
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0243](/solutions/0243/) — Resilience
- ● [0245](/solutions/0245/) — Coresilience
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0301](/solutions/0301/) — Nim
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0768](/solutions/0768/) — Chandelier
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [0996](/solutions/0996/) — Overtakes
- ● [1000](/solutions/1000/) — Problem $1000$
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
