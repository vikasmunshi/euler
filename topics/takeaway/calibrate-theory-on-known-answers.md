<!-- tags: [calibrate-theory-on-known-answers] -->
<!-- status: final -->
# Calibrate a theory on the known answers

Some problems are mostly argument. The code at the end is short, but it encodes a claim that is
hard to prove and easy to get slightly wrong: a game's values are all numbers, an optimal
configuration has a particular shape, a pursuit game is decided by a particular inequality, a
greedy process can be run backwards one-to-one, a transfer matrix quotiented by a symmetry still
counts exactly. For
those problems the statement's worked examples are the most valuable thing on the page. They are
answers computed by someone who already solved it, so they make a free and independent test
suite. The rule this page describes is simple to state. Before trusting a theory on the unknown
case, **make it reproduce every given value exactly**, and where the givens are thin, make your
own with a brute force. Every problem below was finished that way. In each one, the step
from "plausible" to "correct" was a check against a known answer, not a proof.

## The idea: known answers test the method, not the number

A known value has power only if the theory had no chance to see it. That sets out what counts as
calibration:

- **The givens are tests, never inputs.** If a free parameter is tuned until $S(10)$ comes out
  right, then $S(10)$ has tested nothing. The model has to be derived first and then *run* on the
  given cases. In this repository each given value goes into the problem's `test_cases.json` as a
  `dev` case beside the `main` one, so every `eval` re-runs the check, and a later "optimisation"
  that breaks the theory fails on the spot.
- **Exactly, not approximately.** A theory that is nearly right will usually match a given value
  to two or three digits. Matching it in every printed digit is what separates the right model
  from a close relative. Integers and exact rationals make that comparison clean. For a real
  answer, demand the full stated precision.
- **One code path for every case.** The calibration only counts if the given cases and the
  unknown case go through the *same* routine. A solution that special-cases the examples, or
  hard-codes a closed form derived for one of them, has calibrated a different program. When the
  givens are a different *shape* from the question, change the signature rather than branch: 887's
  examples state single values $Q(N, d)$ while the task is a double sum, so its `solve()` takes
  ranges of $N$ and $d$, and a single value is just a range of width one.
- **Make more answers when the statement gives too few.** One or two small values can be matched
  by coincidence. An exhaustive search, or an exact simulation over a range of small inputs, turns
  a handful of checks into hundreds. Keep that oracle as a scratch script beside the solution, as
  the record of how the theory was earned.

## How the problems use it

**Problem 265** shows the habit at its cheapest. The statement asks for circles of $2^N$ bits
whose $N$-bit windows are all distinct, and gives only $S(3) = 52$. The theory is a reduction:
such a circle is a binary [de Bruijn sequence](https://en.wikipedia.org/wiki/De_Bruijn_sequence),
and starting the encoding at the all-zeros window is a
[canonical form](/topics/technique/canonical-form) that removes rotations, so a backtracking
search only has to build strings with that prefix. Both steps are standard, and both are easy to
get subtly wrong at the seam where the circle closes. One given value is thin, so a brute force
that tests every prefixed integer directly made a second one, $S(4)$, in seconds. The search had
to match both before I ran it on $N = 5$. The literature supplies a third check for free: the
number of sequences the search finds must equal the known count $2^{2^{N-1}-N}$.

**Problem 336** asks for the $k$-th lexicographic "maximix" arrangement: a permutation of
carriages that a fixed greedy suffix-reversal routine takes the most steps to sort. Rather than
filter all $n!$ permutations, I ran the deterministic routine backwards and argued that each
sequence of choices yields a distinct maximix arrangement. That claim predicts there are exactly
$(n-2)!$ of them. The statement gives three independent checks: the two arrangements for four
carriages, the count of $24$ for six, and the tenth of those. The construction matched all
three. They are still only three samples, so a brute force simulated the greedy routine on every
permutation for $n = 3, \dots, 9$, kept those with the worst step count, and compared the
*whole sorted set* with the construction's. They agreed at every size, and the counts
$1, 2, 6, \dots, 5040$ confirmed the $(n-2)!$ formula along the way.

**Problem 455** asks, for each base $n$, for the largest $x < 10^9$ with $n^x \equiv x \pmod{10^9}$.
The theory is that iterating $x \leftarrow n^x$ settles on the answer: the power tower becomes
constant modulo $10^9$ because of the shrinking chain of
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) values, and the limit is a
fixed point. That it is the *largest* fixed point, and indeed the only one, is the claim that needs
evidence, and no brute force can scan $10^9$ exponents for each of $10^6$ bases. What can shrink is the
modulus. On $10^3$, $10^4$ and $10^5$ an exhaustive search over every $x$ is cheap. It found the tower
limit to be the unique solution for every base, and the statement's sum over $n \le 10^3$ agreed as well.

**Problem 670** counts colourings of tiled $2 \times n$ strips with a
[transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method). The step that makes it
small is a symmetry argument: permuting the four colours changes nothing, so the state drops the
colours and keeps only the two tiles' overhangs, and the colour choices become matrix weights such as
"$2$ ways" or "$3 \times 2$ ways". Those weights are exactly where a quotient goes wrong, so a
separate script enumerated every tiling and colouring for $n \le 7$ and had to agree with the matrix
at every length. The statement adds a check from the other end: a value at $n = 100$, given modulo
the problem's prime, which no enumeration reaches but the matrix-power path does. One family of
checks covers the weights, the other the fast exponentiation.

**Problem 761** is a pursuit game in a pool: a swimmer tries to reach the edge before a runner
on the edge can get there. The statement gives the critical runner speed for a circular pool and
a square one to eight decimals, and asks for the hexagon. My analysis produced one general
criterion for when the runner can always contain the swimmer. I did not derive each shape by
hand: the code searches for the containing region directly for any regular polygon. Running that
one routine on the circle and the square reproduced both given speeds to all eight digits. Only
then did I trust its hexagon, and the same routine also handles triangles and octagons as extra
cases. A coarse discretised brute force of the full game backed it up: it reproduced the circle
and put the polygons in the right neighbourhood. A free-form search also found no other shape of
region that does better.

**Problem 860** is a coin-stacking game that turns out to be blue-red
[Hackenbush](https://en.wikipedia.org/wiki/Hackenbush) on stalks of height two. The theory has two
steps: each stack is worth a surreal number ($\pm 2$ or $\pm \tfrac12$), and a position is fair
exactly when the values sum to zero. After that the count is a generating-function coefficient,
which factors into a single binomial sum. Each step is textbook, and an error in either still gives
a tidy formula. So the oracle ignores the theory. It plays the partizan game out by memoised search
over all $4^n$ arrangements for $n \le 7$, and the sequence it produces must equal the closed sum
term by term, as must the given $F(10)$.

**Problem 882** rests on the claim that every single-number game is a
[surreal number](/topics/domain/surreal-number). That is true only if, at every position, Left's
best option sits below Right's. I checked it exhaustively with exact
[`Fraction`](https://docs.python.org/3/library/fractions.html) arithmetic over the small numbers,
and the resulting formula then had to reproduce all three given values of $S(n)$ before I moved
to fixed point.

**Problem 887** asks for the height of the best binary search tree under a per-leaf depth bound,
summed over a huge range. The theory turns the question around: fix the height, compute the
largest $N$ it can serve with a recurrence, and argue that filling the left subtree completely is
always optimal. That greedy step is the claim at risk. The recurrence passes two quick checks
first: it gives closed forms for $d = 0$ and $d = 1$ that reproduce the statement's
$Q(N, 0) = N - 1$ and $Q(7, 1) = 3$. The real test is an interval dynamic program over *every* comparison tree, which never
assumes the greedy split. It matched each $Q(N, d)$ for $N \le 14$, $d \le 3$ and the full sums
for $N \le 30$, $d \le 7$.

**Problem 963** is the related ternary game, and the statement gives a single value, $F(5) = 21$.
That is far too little to calibrate a closed form for infinitesimal-valued games. So I built the
oracle myself: a small [canonical-form](/topics/technique/canonical-form) engine that reproduces
$F(5)$ by brute force and computes exact game values. The closed-form decomposition was fitted on
that engine's output and then checked against it for every number up to $10^6$, well beyond
anything the main case needs.

**Problem 983** gives $R(2) = 1$ and $R(4) = \sqrt5$, and the second example contains the whole
idea: its four circles form a projected
[hypercube](/topics/domain/hypercube-graph). The theory I built on that was that every perfect set
is such a cube. I checked it against an exhaustive search of small radii, where every perfect set
that exists has exactly a cube's size. I then checked the final configuration independently,
directly from the problem's definitions. The search that finds it relies on the cube model, but
the final check does not.

## How to reason about it

Reach for this whenever the solution's correctness depends on a *claim about structure* rather
than on a calculation you could follow by hand: game values, optimal shapes, invariants,
"it can be shown that" statements, patterns read off a table. The cost is small, usually a
brute-force script and a few test cases, and it protects the expensive part of the work.

- **Check the claim, not just the output.** In 882 the assertion "every node has
  $\max L < \min R$" is a direct test of the hypothesis. An end-to-end match only shows that it
  held on the inputs tried. Assert the intermediate claim wherever you can.
- **Build the oracle from the statement, not from the theory.** A brute force that reuses the
  theory's own characterisation will agree with it, mistakes included. In 336 the oracle never
  sees the "carriage strictly inside the suffix" condition the construction rests on. It just
  runs Simon's routine and takes the maximum step count, as the statement defines it. 860's oracle
  plays the coin game rather than adding surreal values, and 887's searches every tree rather than
  the greedy one. 983's final check is independent of the cube model for the same reason.
- **Shrink the axis that makes brute force impossible.** That axis is not always $n$. In 455 it is
  the modulus: $10^9$ is out of reach, but $10^5$ is not, and the claim being tested ("the tower
  limit is the only fixed point") means the same thing at every modulus. Then add a check at full
  scale if the statement offers one, as 670's value at $n = 100$ does for the part of the code
  that small cases never exercise.
- **Compare the whole object when you can.** A count or a single ranked element can match by
  luck. A whole set cannot. 336 compares every arrangement for each $n$, not just the one that
  gets asked about, and a derived count such as $(n-2)!$ or 265's $2^{2^{N-1}-N}$ is a cheap
  extra check that comes with the set.
- **Hold some checks back.** A pattern fitted on a range of brute-force values proves nothing on
  that range. Verify it on inputs the fit never saw, as 963 did up to $10^6$. The sister takeaway,
  [small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence), makes the
  same demand of a fitted recurrence.
- **Treat a near miss as a wrong theory.** If the circle comes out right and the square is off in
  the sixth digit, the criterion is missing a case. Look for the missing case. Don't loosen the
  tolerance. In 761 the easy case to miss is the paths that hug the boundary: without them a tiny
  region looks safe, which ignores the swimmer circling the centre.
- **Prefer exact arithmetic for the comparison.** A float that agrees to $10^{-9}$ cannot tell an
  exact match from a near one. With [exact arithmetic](/topics/takeaway/exact-arithmetic-for-equality)
  the check is a plain equality.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0265](/solutions/0265/) — Binary Circles
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0670](/solutions/0670/) — Colouring a Strip
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
