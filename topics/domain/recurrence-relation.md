<!-- tags: [recurrence-relation] -->
<!-- status: final -->
# Recurrence relation

A [recurrence relation](https://en.wikipedia.org/wiki/Recurrence_relation) defines each term of a
sequence from the terms before it: $a_n = F(a_{n-1}, \dots, a_{n-d})$, plus enough seed values to
get started. It is the fourth-largest domain tag in this collection, and that is not an accident of
taste — a recurrence is what you get whenever an object of size $n$ is *assembled* from smaller
objects of the same kind, and most counting, probability and dynamics questions are exactly that.
The recurrence itself is almost never the hard part. Finding it is a paragraph of reasoning;
**evaluating it at the index the problem actually asks about** is the work.

## Where they come from

Four decompositions account for nearly every recurrence below, and it is worth being able to name
them, because recognising the shape is what tells you which one to write down.

- **Condition on the last piece.** Classify every complete object by its final move, then remove
  that move. A row of length $i$ tiled with tiles of length $1..4$ ends in exactly one of four ways,
  so $\text{dp}[i] = \text{dp}[i-1] + \text{dp}[i-2] + \text{dp}[i-3] + \text{dp}[i-4]$ — problem
  117, tetranacci by another name. The classification has to *partition* the objects: every tiling
  falls in exactly one case, which is what makes the counts add without double-counting. This is
  [optimal substructure](/topics/domain/optimal-substructure) stated concretely, and the tiling
  family (114, 115, 116, 117) is the cleanest place to see it.
- **Condition on the first step.** In a probabilistic process, write the unknown at a state in terms
  of the unknowns at the states one step away. Problem 227's expected hitting time gives
  $E_i = 1 + \sum_D P(D)\, E_{(i+D) \bmod n}$, and problem 938's absorption probability gives a
  two-term mixture of its two neighbours. Note the difference in what you then do with it: the
  first is a *cyclic* dependency and becomes a [system of linear
  equations](/topics/technique/system-of-linear-equations); the second is acyclic and becomes a
  [dynamic programming](/topics/technique/dynamic-programming) sweep.
- **Self-similar construction.** When the object is *defined* recursively, the recurrence is handed
  to you and the only question is how to query it. Problem 230's strings satisfy
  $T_k = T_{k-2}T_{k-1}$, so the *lengths* satisfy Fibonacci and a digit position can be chased down
  through the concatenations without ever materialising a string; problem 872's trees are built by
  one reparenting rule per step. The lesson generalises: recur on the **cheap shadow** of the
  structure (lengths, counts, a state index), never on the structure itself.
- **An algebraic ladder.** Solutions to a [Pell equation](/topics/technique/pells-equation), or
  convergents of a [continued fraction](/topics/domain/continued-fraction), advance by a fixed
  linear update. Problems 94, 140 and 65 all turn a search over candidates into a walk along the
  answers.

Sometimes you cannot see the decomposition at all, and the counts still obey a recurrence for
structural reasons. That case has its own page —
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence) — and the move
there is to brute-force the small terms and fit the coefficients rather than derive them.

## Evaluating it without paying $O(n)$

A recurrence read literally is a recipe for $n$ steps. Whether that is acceptable depends entirely
on the index in the statement, and the statements here are usually chosen so it is not.

**Iterate forward, with a window.** The honest baseline: $O(n)$ time, and $O(d)$ — not $O(n)$ —
memory, because only the last $d$ terms are ever read. Prefer this to top-down
[recursion](/topics/technique/recursion-computer-science) whenever the index tree is dense: naive
recursion on a two-term recurrence is exponential, and even with
[memoization](/topics/technique/memoization) you pay call overhead and risk a stack limit. Keep
the table sized to the input and built inside `solve()` — a module-level table is
[precomputation that hides from the benchmark](/topics/takeaway/precompute-once-reuse).

Problem 2 is the miniature that makes the point that *which* sequence you recur on is a choice.
Every third Fibonacci number is even, and the even ones satisfy a recurrence of their own,
$E_{k+1} = 4E_k + E_{k-1}$, so the filter disappears into the generator:

```python
def _even_fibonacci_numbers() -> typing.Generator[int, None, None]:
    """Yield successive even Fibonacci numbers below max_limit."""
    even_fib_a, even_fib_b = (2, 8)
    while even_fib_a < max_limit:
        yield even_fib_a
        even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)
```

That is the whole of `solutions/public/p0002/` — two state variables, no array, no test for
evenness. Re-indexing to the subsequence you actually want is the cheapest optimisation in this
whole topic, and the one most often missed.

**Jump by matrix power.** If the recurrence is
[linear with constant coefficients](/topics/technique/linear-recurrence-with-constant-coefficients),
stacking the last $d$ terms into a vector turns one step into a fixed
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix), and $n$ steps into
$M^n$ — computable by
[exponentiation by squaring](/topics/technique/exponentiation-by-squaring) in $O(d^3 \log n)$.
This is the standard escape when the index is $10^{12}$ or worse, and it composes: problem 940's
two-variable $A(m,n)$ is a product of *two* transfer matrices, one advancing rows and one advancing
columns, which additionally lets a double sum factor into a product of two accumulated sums instead
of an $O(k^2)$ pairing. See [matrix exponentiation](/topics/technique/matrix-exponentiation) for the
mechanics.

**Descend the binary representation.** A recurrence whose arguments are $2n$ and $2n+1$ rather than
$n-1$ and $n-2$ is not slow at all — it is $O(\log n)$, because each step halves the index. The
catch is that the branches usually need *two* neighbouring values, so carry a pair (or a short
vector) and read the bits of $m$ from the top down, applying one linear map per bit:

```python
lo, hi = seed                      # (a(1), a(2)), say
for bit in bin(m)[3:]:             # skip "0b1": the leading bit is the seed
    lo, hi = even_map(lo, hi) if bit == "0" else odd_map(lo, hi)
```

Problems 169 and 918 are both this shape, and problem 872's climb up a tree is its bitwise cousin —
each step clears the top bit of a gap, so the loop runs
[popcount](https://en.wikipedia.org/wiki/Hamming_weight) times.

**Exploit a finite state space.** If the state that advances the recurrence lives in a finite set,
the orbit must eventually repeat, and the sequence is
[eventually periodic](/topics/domain/periodic-sequence). Then a huge index costs only the length of
the tail plus the cycle. Two variants worth distinguishing:

| | shape | how to detect | example |
| --- | --- | --- | --- |
| **eventually** periodic | a tail, then a cycle | compare against an earlier state, or [Floyd/Brent](/topics/technique/cycle-detection) | problem 197 — a float map truncated to nine decimals collapses onto a period-2 attractor |
| **purely** periodic | no tail at all | the recurrence is **invertible** mod $m$, so the map is a permutation and the seed itself must recur | problem 225 — Tribonacci mod $m$, the [Pisano period](/topics/domain/pisano-period)'s cousin |

The invertibility argument is the one to internalise, because it buys $O(1)$ memory: when the map
is a permutation you can detect the period by waiting for the *seed* to come back, instead of
storing every state you have visited.

**Telescope it away.** Occasionally a sum of terms collapses to one term. Splitting $S(N)$ by index
parity and substituting the recurrence can make almost everything cancel
([telescoping](/topics/technique/telescoping-series)), leaving a
[closed form](/topics/takeaway/closed-form-over-iteration) in a single value of the sequence — which
you then evaluate by one of the methods above. Problem 918 does exactly this, turning a
trillion-term sum into one evaluation. The same collapse in the other direction is what makes the
partition function computable: the reciprocal of its
[generating function](/topics/domain/generating-function) is almost all zeros, so $p(n)$ obeys a
recurrence with only $O(\sqrt n)$ terms (problems 76 and 78).

## How to reason about it

- **Check the recurrence before you optimise it.** Every derivation above is a case analysis, and
  case analyses are where the errors are. Write the $O(n)$ version, check it against the values in
  the statement and against brute force on small inputs, and only then replace it with the matrix
  power or the bit descent. Several solutions here keep the brute force in the directory precisely
  so the fast path can be re-validated.
- **Mind where the recurrence starts holding.** Recurrences frequently fail for the first few
  indices, the small cases being genuinely special. Seed from an index you have verified, and
  answer anything below it from a table.
- **Constant coefficients or not.** $a_n = 3a_{n-1} + 2a_{n-2}$ is a different animal from
  $a_n = n\,a_{n-1} + a_{n-2}$. The first has a companion matrix and a $\log n$ jump; the second is
  [holonomic](https://en.wikipedia.org/wiki/Holonomic_function) — still structured, but the matrix
  changes every step, so there is no exponentiation shortcut and you are back to $O(n)$ unless a
  closed form exists.
- **Reduce, but reduce correctly.** If the answer is wanted mod $m$, keep every term reduced —
  otherwise linear recurrences produce numbers with $\Theta(n)$ digits and the arithmetic, not the
  loop, becomes the cost. Signed coefficients need care: in C a negative intermediate must be
  stored as its residue, `((v % m) + m) % m`, or the next multiplication leaves the word
  ([watch integer width](/topics/takeaway/watch-integer-width)). And when the problem does *not*
  offer a modulus, expect big integers — the tetranacci count at $n = 500$ is a 140-digit number,
  which Python handles for free and C does not.
- **Watch the memory, not just the time.** A two-dimensional recurrence rarely needs its whole
  grid. If every cell depends only on cells one step back along some direction, sweep along that
  direction with two rolling buffers: problem 938's grid has both predecessors on the previous
  anti-diagonal, which turns $O(RB)$ memory into $O(R)$ and, as a bonus, makes each sweep one
  vectorised array operation instead of a Python loop.
- **Floating point deserves suspicion.** A recurrence run in `double` accumulates error at every
  step, and subtractive recurrences can amplify it catastrophically. Problem 197 gets away with an
  *exact* equality test only because its map truncates to nine decimals, making the cycle bit-for-bit
  identical; without a quantising step like that, use `fractions.Fraction`, integers, or an explicit
  tolerance you can justify.

The tell for this whole topic is a problem that describes a process — one more tile, one more turn,
one more level — and then asks about it at an index you could never walk to. Write the recurrence
first, in the most literal form you can defend. Then look at its *shape*: constant coefficients,
halving arguments, a finite state, a telescoping sum. The shape picks the method.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0227](/solutions/0227/) — The Chase
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0232](/solutions/0232/) — The Race
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence
- ○ [0282](/solutions/0282/) — The Ackermann Function
- ○ [0287](/solutions/0287/) — Quadtree Encoding (a Simple Compression Algorithm)
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0327](/solutions/0327/) — Rooms of Doom
- ○ [0330](/solutions/0330/) — Euler's Number
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0339](/solutions/0339/) — Peredur Fab Efrawg
- ○ [0340](/solutions/0340/) — Crazy Function
- ○ [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0375](/solutions/0375/) — Minimum of Subsequences
- ○ [0382](/solutions/0382/) — Generating Polygons
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ○ [0422](/solutions/0422/) — Sequence of Points on a Hyperbola
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0443](/solutions/0443/) — GCD Sequence
- ○ [0458](/solutions/0458/) — Permutations of Project
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0469](/solutions/0469/) — Empty Chairs
- ○ [0472](/solutions/0472/) — Comfortable Distance II
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ○ [0490](/solutions/0490/) — Jumping Frog
- ○ [0492](/solutions/0492/) — Exploding Sequence
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ○ [0517](/solutions/0517/) — A Real Recursion
- ○ [0523](/solutions/0523/) — First Sort I
- ○ [0527](/solutions/0527/) — Randomized Binary Search
- ○ [0532](/solutions/0532/) — Nanobots on Geodesics
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ○ [0539](/solutions/0539/) — Odd Elimination
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ○ [0551](/solutions/0551/) — Sum of Digits Sequence
- ○ [0555](/solutions/0555/) — McCarthy 91 Function
- ○ [0558](/solutions/0558/) — Irrational Base
- ○ [0570](/solutions/0570/) — Snowflakes
- ○ [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0609](/solutions/0609/) — $\pi$ Sequences
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0645](/solutions/0645/) — Every Day Is a Holiday
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0664](/solutions/0664/) — An Infinite Game
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0670](/solutions/0670/) — Colouring a Strip
- ○ [0671](/solutions/0671/) — Colouring a Loop
- ○ [0672](/solutions/0672/) — One More One
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0698](/solutions/0698/) — 123 Numbers
- ○ [0700](/solutions/0700/) — Eulercoin
- ○ [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ○ [0729](/solutions/0729/) — Range of Periodic Sequence
- ○ [0736](/solutions/0736/) — Paths to Equality
- ○ [0737](/solutions/0737/) — Coin Loops
- ○ [0739](/solutions/0739/) — Summation of Summations
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ○ [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0770](/solutions/0770/) — Delphi Flip
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0809](/solutions/0809/) — Rational Recurrence Relation
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0822](/solutions/0822/) — Square the Smallest
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0832](/solutions/0832/) — Mex Sequence
- ○ [0839](/solutions/0839/) — Beans in Bowls
- ○ [0843](/solutions/0843/) — Periodic Circles
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0848](/solutions/0848/) — Guessing with Sets
- ● [0872](/solutions/0872/) — Recursive Tree
- ○ [0887](/solutions/0887/) — Bounded Binary Search
- ○ [0909](/solutions/0909/) — L-expressions I
- ○ [0910](/solutions/0910/) — L-expressions II
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0915](/solutions/0915/) — Giant GCDs
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ○ [0921](/solutions/0921/) — Golden Recurrence
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ○ [0935](/solutions/0935/) — Rolling Square
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0943](/solutions/0943/) — Self Describing Sequences
- ○ [0955](/solutions/0955/) — Finding Triangles
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0969](/solutions/0969/) — Kangaroo Hopping
- ○ [0985](/solutions/0985/) — Telescoping Triangles
- ○ [0993](/solutions/0993/) — Banana Beaver
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1003](/solutions/1003/) — Lonely Singles

<!-- /problems -->
