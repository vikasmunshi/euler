<!-- tags: [markov-chain, expected-value-application, stationary-distribution, random-walk] -->
<!-- status: final 2026-10-14T07:42Z -->
# Markov chains and expected value

A large share of the archive's probability problems ask for an *expected* something — turns until
a game ends, empty squares after fifty hops, distinct colours in a handful of balls — about a
process that is random step by step. Two tools answer nearly all of them. A
[Markov chain](https://en.wikipedia.org/wiki/Markov_chain) models the process itself: name the
state, write down the transitions, and solve. [Linearity of
expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity) skips the process: break the
quantity into small pieces, find each piece's expectation, and add. They overlap more than they
first appear to, and most of the work in these problems is choosing which one fits — and, for a
chain, finding a state small enough to solve.

## The idea

### The chain: state, transitions, and three questions

A Markov chain is a random process whose next state depends only on its current state, not on how
it got there. Once the state is fixed, one step is a
[stochastic matrix](https://en.wikipedia.org/wiki/Stochastic_matrix) `P`, where `P[i][j]` is the
probability of moving from `i` to `j`. The problems ask one of three things about it.

**Where is it after `n` steps?** Push a probability distribution forward `n` times. Problem 151
(sheets of paper in an envelope) does this over a sparse dictionary of reachable states. Problem
213 (fleas on a grid) does it for 900 independent walkers at once, with each step written as a
neighbour stencil rather than a dense matrix multiply.

**Where does it spend its time in the long run?** If the chain is ergodic, the
[stationary distribution](https://en.wikipedia.org/wiki/Stationary_distribution) `π = πP` is the
answer, and it does not depend on where the chain started. Problem 84 (Monopoly) finds it by power
iteration. That code is public, and short enough to quote:

```python
def stationary_distribution(matrix: list[list[float]]) -> list[float]:
    """Power-iterate the chain to its stationary distribution over the augmented states."""
    states = len(matrix)
    distribution = [1 / states] * states
    for _ in range(100_000):
        nxt = [0.0] * states
        for i, weight in enumerate(distribution):
            if weight:
                row = matrix[i]
                for j, probability in enumerate(row):
                    if probability:
                        nxt[j] += weight * probability
        if max(abs(a - b) for a, b in zip(nxt, distribution)) < 1e-15:
            return nxt
        distribution = nxt
    return distribution
```

**How long until it stops, and where does it stop?** This is the
[absorbing chain](https://en.wikipedia.org/wiki/Absorbing_Markov_chain), and it is the most common
of the three. Condition on the first step (*first-step analysis*). With `E_i` the expected number of
steps left from transient state `i`, and `E = 0` on absorbing states:

$$ E_i = 1 + \sum_j P_{ij}\, E_j . $$

That is one linear equation per transient state. In matrix form, with `Q` the transient-to-transient
block, it is `(I − Q)E = 1`. The *fundamental matrix* `N = (I − Q)⁻¹` holds the expected number of
visits to each state, and absorption probabilities come from the same system with the `1` replaced
by the one-step probabilities of being absorbed. Problem 227 (two dice passed around a table) is
the textbook case: a dense `(n−1) × (n−1)` system solved by Gaussian elimination. Problem 938
(drawing cards until a colour runs out) has the same shape, but its transitions only ever go
"downhill" in the counts, so the system is triangular. It becomes a dynamic-programming recurrence
instead of a matrix solve. Bozo sort (367), the ant carrying seeds (280) and the chases (683, 825)
are all hitting-time questions too.

### Linearity: decompose, then add

For *any* random variables, dependent or not,

$$ \mathbb{E}\Big[\sum_i X_i\Big] = \sum_i \mathbb{E}[X_i] . $$

The standard move is to write the quantity as a sum of
[indicator variables](https://en.wikipedia.org/wiki/Indicator_function), one per "thing that might
happen". The expectation of an indicator is just a probability. Problem 493 counts distinct colours
among balls drawn from an urn. The honest model is a multivariate hypergeometric distribution over
every split of the draw. Linearity replaces it with "seven times the probability that one given
colour shows up", which is two binomial coefficients and a subtraction.

The thing to notice is what linearity does *not* need: independence. The colours in 493 are
negatively correlated (a draw that uses one colour can't use another), and that changes nothing.
Independence only comes in when you compute one indicator's probability. In Problem 213,
`P(square t is empty)` is a product over fleas, and that product is valid only because the fleas
hop independently. Adding those probabilities over all squares needs no independence at all.

### They are the same idea, seen from two sides

The two tools are not really rivals. The fundamental matrix of an absorbing chain is a linearity
argument: the expected number of visits to `j` is the sum over `t` of the probability of being at
`j` at time `t`, so `N = I + Q + Q² + … = (I − Q)⁻¹`. The tail-sum formula
`E[T] = Σ_t P(T > t)` writes a hitting time as a sum of indicators "not finished yet at time `t`".
Problem 151 asks for the expected *number of batches* at which the envelope holds a single sheet.
It runs a chain forward to get each batch's distribution, then uses linearity to add the
single-sheet probability batch by batch. The chain supplies the per-step probabilities, and
linearity adds them up.

## How to reason about it

### Which model fits

| The quantity is…                                            | Reach for                                   |
|-------------------------------------------------------------|---------------------------------------------|
| a count or sum of local events (empty cells, colours seen)  | linearity over indicators                   |
| a time until something happens                              | absorbing chain, first-step analysis        |
| a probability of ending in one outcome rather than another  | absorbing chain, absorption probabilities   |
| a long-run frequency                                        | stationary distribution                     |
| a count over a fixed horizon of a path-dependent process    | forward propagation, then linearity per step |
| a maximum, a record, or anything non-additive along a path  | a chain whose state carries that statistic  |

The last row is the trap. Linearity works only for sums. The maximum number of segments in Problem
253's caterpillar is not a sum of anything local, so the running peak has to become part of the
state. Once it is, the chain only needs `O(n³)` work. Going the other way, if you set up a chain
for something linearity already solves (493 as a walk over draw counts), the answer still comes
out, but you have done far more work than the problem needed.

### The real work is the state

A Markov chain is only as good as its state, and you usually have to pick that state. Three moves
recur:

- **Collapse by symmetry.** The two dice in 227 sit on a ring, and only the *gap* between them
  matters. That takes `n²` states down to `n`, and an `O(n⁶)` solve down to `O(n³)`, with no
  approximation.
- **Augment to restore memorylessness.** Monopoly's "three doubles in a row goes to jail" depends
  on history, so the 40 squares alone are not Markov. Adding the current doubles streak (0, 1 or 2)
  gives 120 states, and the chain is Markov again.
- **Factor out what never matters.** In 938, the "both black" draw changes nothing. Conditioning on
  a productive move removes that self-loop and cancels a common factor from the recurrence. In 253,
  a counting argument shows the empty gaps' widths stay uniformly distributed whatever happened
  before. So they can be averaged out of the state instead of carried as an integer partition.

If the state space is still in the millions, the model is usually wrong, not the hardware too slow.

### Pitfalls

- **Simulation is not an answer.** A [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method)
  run is a good cross-check. As a solution it gives a different number on every run, and in 84 the
  top squares are close enough that the ranking itself can flip. Solve the chain exactly.
- **Mind the precision the answer needs.** A double is fine for 227's ten significant figures, but
  rounding an exact rational like 493's to nine places is safest done in integer arithmetic.
- **Dense solves cost `O(s³)`.** That is fine for a few hundred states. Beyond that, use the
  structure: triangular systems become recurrences (938), local transitions become stencils (213),
  and a chain whose state only grows can be swept in topological order.
- **Check that the chain is ergodic before trusting `π`.** A periodic chain (a bipartite random
  walk, for instance) has a stationary distribution that power iteration never converges to.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0227](/solutions/0227/) — The Chase
- ● [0253](/solutions/0253/) — Tidying Up A
- ○ [0280](/solutions/0280/) — Ant and Seeds
- ○ [0298](/solutions/0298/) — Selective Amnesia
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0339](/solutions/0339/) — Peredur Fab Efrawg
- ○ [0367](/solutions/0367/) — Bozo Sort
- ○ [0470](/solutions/0470/) — Super Ramvok
- ● [0493](/solutions/0493/) — Under the Rainbow
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0499](/solutions/0499/) — St. Petersburg Lottery
- ● [0523](/solutions/0523/) — First Sort I
- ○ [0575](/solutions/0575/) — Wandering Robots
- ○ [0589](/solutions/0589/) — Poohsticks Marathon
- ○ [0595](/solutions/0595/) — Incremental Random Sort
- ○ [0610](/solutions/0610/) — Roman Numerals II
- ○ [0640](/solutions/0640/) — Shut the Box
- ○ [0648](/solutions/0648/) — Skipping Squares
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0697](/solutions/0697/) — Randomly Decaying Sequence
- ○ [0807](/solutions/0807/) — Loops of Ropes
- ○ [0819](/solutions/0819/) — Iterative Sampling
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0852](/solutions/0852/) — Coins in a Box
- ○ [0930](/solutions/0930/) — The Gathering
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ○ [0959](/solutions/0959/) — Asymmetric Random Walk
- ○ [0970](/solutions/0970/) — Kangaroo Hopping over Sixes
- ○ [0973](/solutions/0973/) — Random Dealings
- ○ [0978](/solutions/0978/) — Random Walk Skewness
- ○ [0979](/solutions/0979/) — Heptagon Hopping

<!-- /problems -->
