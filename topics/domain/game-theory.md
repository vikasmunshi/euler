<!-- tags: [game-theory] -->
<!-- status: final 2026-10-12 -->
# Game theory

[Game theory](https://en.wikipedia.org/wiki/Game_theory) studies decisions made by rational agents
whose outcomes depend on each other's choices. The problems below are a different family from the
[combinatorial games](/topics/domain/combinatorial-game-theory) of Nim and digit deletion. There is
chance in them, payoffs other than win or lose, and continuous motion. One is a coin race in which
one player chooses how much risk to take each turn. One is the pirate puzzle, where a crew votes
on a share of treasure. One is a pursuit around a pool. The question is always the same: what
happens when *every* player plays optimally? And the method is always the same too. Define the
**value of a state** under optimal play, find the order in which values depend on each other, and
make the state small enough to fill in.

## The idea: a value per state, solved from the end

A sequential game is a tree of decisions. Its value comes from
[backward induction](/topics/technique/backward-induction): settle the positions nearest the end,
then work back, letting each player at each node pick the option that is best *for them* given
the values already known. What varies across the problems is what the state is, and what makes
the backward pass awkward.

- **Problem 232: chance, and a state that repeats.** Two players race to $100$ points. Player 1
  tosses a coin once per turn. Player 2 chooses how many tosses $T$ to risk for a payoff of
  $2^{T-1}$. The whole history collapses into two deficits $(a, b)$, so a
  [dynamic programming](/topics/technique/dynamic-programming) table over pairs holds the
  probabilities. The interesting choice is $T$. Every $T$ has the same *expected* yield, so the
  choice is purely about variance and about finishing the deficit in one stroke, and that can
  only be decided state by state. The awkward part is that a round where both players miss
  returns the game to the *same* state, so a state's value appears on both sides of its own
  equation. The equation is linear in that value, so I solve it in closed form per candidate $T$
  rather than iterating it to convergence.
- **Problem 950: rational voters.** The most senior pirate proposes a split, everyone votes, and
  a failed proposal sends the proposer off the plank. A voter accepts exactly when the offer
  beats the happiness they would have if the proposer walked and the game went on with one fewer
  pirate, so this is backward induction over the number of pirates. Two observations make it tractable at $n = 10^{16}$. First, the
  state is only the *histogram* of coin holdings plus the number who have walked, because who
  holds which coins doesn't matter. Second, the problem's bloodthirstiness parameter is
  irrational, so no voter is ever exactly indifferent. That removes the tie-breaking question
  that plagues every version of this puzzle. Small cases then show long runs of failed proposals
  that can be jumped over in one step.
- **Problem 761: continuous play.** A swimmer in a pool tries to reach the edge before a runner on
  the edge can get there. This is a [differential game](/topics/domain/differential-game): both
  players steer continuously and react instantly, so there is no tree to walk. The value is a
  yes or no per runner speed, and the work is finding the critical speed. The analysis shows that
  optimal play moves in straight lines, that a single threat never wins, and that the swimmer
  needs a *two-way* threat. The answer then depends on whether a central region exists from which
  the swimmer cannot launch one.

## How to reason about it

- **Write the state as the least the future depends on.** That's two deficits in 232, and a
  histogram plus a walk count in 950, not a list of who holds what. In 761 it is a geometric
  configuration reduced by symmetry. Collapsing the state is almost always the step that makes
  the problem finite.
- **Find the dependency order before you write a loop.** In 232 the successful branch reads a
  strictly smaller $b$ and the heads branch a strictly smaller $a$ in the same row. So two
  ascending loops fill the table with no recursion. When the order has a cycle, as with a
  repeating miss, solve the cycle algebraically, or fall back to
  [fixed-point iteration](/topics/technique/fixed-point-iteration) as a check.
- **Settle tie-breaking explicitly.** Rational-agent puzzles are fragile wherever a player is
  indifferent. Either show that ties can't happen, as 950's irrational parameter guarantees, or
  fix the rule and check that the answer doesn't depend on it. 950 did both.
- **Separate the expected value from the choice.** When every option has the same expectation,
  as in 232, the optimal choice is driven by variance and by thresholds. That is why the answer
  needs a table and not a formula.
- **Check the strategy by playing it.** A value table is only as good as its recurrence.
  Problem 232 has no worked example, so I checked it three ways: a race to one point by hand,
  plain value iteration without the closed-form step, and a
  [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method) simulation of the game played
  with the computed strategy. In 761, one general criterion had to reproduce both of the
  statement's given speeds to all eight digits before I trusted it on the hexagon. That's the
  habit of [calibrating theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0232](/solutions/0232/) — The Race
- ● [0761](/solutions/0761/) — Runner and Swimmer
- ● [0950](/solutions/0950/) — Pirate Treasure

<!-- /problems -->
