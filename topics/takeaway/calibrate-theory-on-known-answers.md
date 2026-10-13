<!-- tags: [calibrate-theory-on-known-answers] -->
<!-- status: final -->
# Calibrate a theory on the known answers

Some problems are mostly argument. The code at the end is short, but it encodes a claim that is
hard to prove and easy to get slightly wrong: a game's values are all numbers, an optimal
configuration has a particular shape, a pursuit game is decided by a particular inequality. For
those problems the statement's worked examples are the most valuable thing on the page. They are
answers computed by someone who already solved it, so they make a free and independent test
suite. The rule this page describes is simple to state. Before trusting a theory on the unknown
case, **make it reproduce every given value exactly**, and where the givens are thin, make your
own with a brute force. All four problems below were finished that way. In each one, the step
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
  hard-codes a closed form derived for one of them, has calibrated a different program.
- **Make more answers when the statement gives too few.** One or two small values can be matched
  by coincidence. An exhaustive search, or an exact simulation over a range of small inputs, turns
  a handful of checks into hundreds. Keep that oracle as a scratch script beside the solution, as
  the record of how the theory was earned.

## How the problems use it

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

**Problem 882** rests on the claim that every single-number game is a
[surreal number](/topics/domain/surreal-number). That is true only if, at every position, Left's
best option sits below Right's. I checked it exhaustively with exact
[`Fraction`](https://docs.python.org/3/library/fractions.html) arithmetic over the small numbers,
and the resulting formula then had to reproduce all three given values of $S(n)$ before I moved
to fixed point.

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
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
