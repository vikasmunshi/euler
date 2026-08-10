<!-- tags: [expected-value] -->
<!-- status: final -->
# Expected value

The [expected value](https://en.wikipedia.org/wiki/Expected_value) of a random quantity is
its long-run average — each outcome weighted by how likely it is. It is the single most
common probabilistic ask in Project Euler: the expected number of empty squares, of distinct
colours, of moves, of rolls, of steps. What makes it a *domain* worth its own page is that
the honest way to compute it is almost never the obvious way. The obvious way enumerates every
joint outcome and its probability; the useful way finds a structure that lets you avoid that
enumeration entirely. Most of the problems below are exercises in spotting which structure applies.

## The idea

For a discrete quantity $X$ taking value $v$ with probability $p_v$, the expected value is
$\mathbb{E}[X] = \sum_v v\,p_v$. For a continuous one — a value sampled from an interval — the
sum becomes an integral, $\mathbb{E}[X] = \int v\,f(v)\,dv$ against the density $f$. That is the
definition, and taken literally it is a recipe for enumerating outcomes. For anything with a
combinatorial state space that recipe explodes: a $30\times30$ grid of fleas each hopping $50$
times (problem 213) has a joint configuration count with hundreds of digits. You cannot sum over
it, and you do not have to.

## Linearity of expectation — the workhorse

The one identity that breaks these problems open is
[linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity):

$$\mathbb{E}[X_1 + X_2 + \dots + X_n] = \mathbb{E}[X_1] + \mathbb{E}[X_2] + \dots + \mathbb{E}[X_n].$$

Its power is a subtle detail: it holds **with no independence requirement whatsoever**. The
$X_i$ may be wildly dependent — the identity is still exact. So the move is to write the quantity
you want as a *sum of simpler pieces*, even pieces that interact, and average each piece on its own.

The pieces are usually
[indicator variables](https://en.wikipedia.org/wiki/Indicator_function): $X_i = 1$ when some event
happens and $0$ otherwise. The expectation of an indicator is just the probability of its event,
$\mathbb{E}[X_i] = \Pr[\text{event}_i]$, so "expected count of things" collapses to "sum of
per-thing probabilities":

$$\mathbb{E}\Big[\#\{\text{things that happen}\}\Big] = \sum_i \Pr[\text{thing } i \text{ happens}].$$

This is the whole trick behind a surprising number of the problems here. *Expected number of
empty squares* (problem 213) becomes a sum, over squares, of the probability that one square ends
empty — which, because the fleas move independently, is a product of per-flea "avoids this square"
probabilities, so a single random walk from each start square is all the machinery you need.
*Expected number of distinct colours drawn from an urn* (problem 493) becomes, by symmetry, the
number of colours times the probability that one fixed colour appears at all — one probability
instead of a full multivariate [hypergeometric](https://en.wikipedia.org/wiki/Hypergeometric_distribution)
enumeration. *Expected number of times the envelope holds a single sheet* (problem 151) is a sum
over batches of the probability that that batch starts with one sheet. In each case the dependent,
high-dimensional problem dissolves into a list of one-dimensional probabilities that you add up.

When you see "expected number of …", reach for indicators first. If you can name the individual
events being counted and find each one's probability, linearity finishes the job — and it does not
care that the events overlap.

## Conditioning and recursion

The other half of these problems are not counts but *processes*: a game or walk that unfolds
until it stops, and you want the expected value at the end (or the expected number of steps to
get there). Here the tool is
[conditional expectation](https://en.wikipedia.org/wiki/Law_of_total_expectation) and its
practical form, **first-step analysis**: define $E[s]$ as the expected value starting from state
$s$, then write one equation per state relating it to the states one move away, weighted by the
transition probabilities. The expected number of fair-die rolls to see a six, for instance, obeys
$E = 1 + \tfrac{5}{6}E$, giving $E = 6$ — the generic shape being

```
E[state] = (cost of one step) + Σ P[state → next] · E[next]
```

with the terminal states pinned to known values. When the states are ordered so each depends only
on later ones, this is a [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)
sweep over the state space; when the dependencies form cycles it becomes a linear system, one
equation per state — a [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) with
[absorbing states](https://en.wikipedia.org/wiki/Absorbing_Markov_chain) whose hitting values or
hitting times you solve for directly. Problem 121 is the small, acyclic end of this: the disc game
has a rigid turn-by-turn structure, so a DP over "number of blue discs so far" accumulates the exact
win probability, and the fair prize fund is set so the game's expected payout does not exceed the
stake. The art in all of these is
[choosing the state](/topics/technique/dynamic-programming) — the minimal description of a
position that makes the recurrence exact.

## How to reason about it

- **Try to avoid enumerating.** Before summing over a joint outcome space, ask whether the answer
  is a sum of pieces (linearity) or the value of a process (conditioning). One of the two almost
  always applies, and either one replaces an intractable sum with a tractable one.
- **Indicators for counts, first-step for processes.** "Expected number of X" → write X as
  $\sum$ indicators and add probabilities. "Expected value/length of a game or walk" → define
  $E[\text{state}]$ and relate each state to its neighbours.
- **Keep it exact when the output demands it.** Many of these ask for an answer to six, nine, or
  thirteen decimal places. An expectation is a sum or ratio of rationals, so the exact answer is a
  fraction; carrying it as integers (Python's arbitrary precision, or `__int128` / a rational type
  in C) and rounding only at the very end avoids the floating-point drift that a `double`
  accumulates over a long sum — problems 121 and 493 both hinge on this. Reserve floating point,
  and a [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method) simulation, for
  *cross-checking* the exact result, not producing it.
- **Continuous expectations are integrals.** When $x$ is drawn uniformly from an interval
  (problem 965's $\{nx\}$, or distance between random points), the expectation is an integral of a
  piecewise-defined function; the work is in cutting the interval into pieces where the integrand
  is simple, then summing exact contributions — the continuous cousin of summing over states.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0253](/solutions/0253/) — Tidying Up A
- ○ [0255](/solutions/0255/) — Rounded Square Roots
- ○ [0267](/solutions/0267/) — Billionaire
- ○ [0280](/solutions/0280/) — Ant and Seeds
- ○ [0285](/solutions/0285/) — Pythagorean Odds
- ○ [0298](/solutions/0298/) — Selective Amnesia
- ○ [0300](/solutions/0300/) — Protein Folding
- ○ [0307](/solutions/0307/) — Chip Defects
- ○ [0316](/solutions/0316/) — Numbers in Decimal Expansions
- ○ [0323](/solutions/0323/) — Bitwise-OR Operations on Random Integers
- ○ [0339](/solutions/0339/) — Peredur Fab Efrawg
- ○ [0352](/solutions/0352/) — Blood Tests
- ○ [0367](/solutions/0367/) — Bozo Sort
- ○ [0371](/solutions/0371/) — Licence Plates
- ○ [0389](/solutions/0389/) — Platonic Dice
- ○ [0394](/solutions/0394/) — Eating Pie
- ○ [0398](/solutions/0398/) — Cutting Rope
- ○ [0430](/solutions/0430/) — Range Flips
- ○ [0436](/solutions/0436/) — Unfair Wager
- ○ [0444](/solutions/0444/) — The Roundtable Lottery
- ○ [0469](/solutions/0469/) — Empty Chairs
- ○ [0470](/solutions/0470/) — Super Ramvok
- ○ [0481](/solutions/0481/) — Chef Showdown
- ● [0493](/solutions/0493/) — Under the Rainbow
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0503](/solutions/0503/) — Compromise or Persist
- ○ [0514](/solutions/0514/) — Geoboard Shapes
- ○ [0523](/solutions/0523/) — First Sort I
- ○ [0527](/solutions/0527/) — Randomized Binary Search
- ○ [0547](/solutions/0547/) — Distance of Random Points Within Hollow Square Laminae
- ○ [0564](/solutions/0564/) — Maximal Polygons
- ○ [0567](/solutions/0567/) — Reciprocal Games I
- ○ [0568](/solutions/0568/) — Reciprocal Games II
- ○ [0573](/solutions/0573/) — Unfair Race
- ○ [0584](/solutions/0584/) — Birthday Problem Revisited
- ○ [0589](/solutions/0589/) — Poohsticks Marathon
- ○ [0595](/solutions/0595/) — Incremental Random Sort
- ○ [0597](/solutions/0597/) — Torpids
- ○ [0602](/solutions/0602/) — Product of Head Counts
- ○ [0610](/solutions/0610/) — Roman Numerals II
- ○ [0613](/solutions/0613/) — Pythagorean Ant
- ○ [0640](/solutions/0640/) — Shut the Box
- ○ [0644](/solutions/0644/) — Squares on the Line
- ○ [0645](/solutions/0645/) — Every Day Is a Holiday
- ○ [0648](/solutions/0648/) — Skipping Squares
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ○ [0695](/solutions/0695/) — Random Rectangles
- ○ [0701](/solutions/0701/) — Random Connected Area
- ○ [0724](/solutions/0724/) — Drone Delivery
- ○ [0727](/solutions/0727/) — Triangle of Circular Arcs
- ○ [0744](/solutions/0744/) — What? Where? When?
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ○ [0765](/solutions/0765/) — Trillionaire
- ○ [0783](/solutions/0783/) — Urns
- ○ [0796](/solutions/0796/) — A Grand Shuffle
- ○ [0815](/solutions/0815/) — Group by Value
- ○ [0819](/solutions/0819/) — Iterative Sampling
- ○ [0826](/solutions/0826/) — Birds on a Wire
- ○ [0852](/solutions/0852/) — Coins in a Box
- ○ [0856](/solutions/0856/) — Waiting for a Pair
- ○ [0863](/solutions/0863/) — Different Dice
- ○ [0866](/solutions/0866/) — Tidying Up B
- ○ [0869](/solutions/0869/) — Prime Guessing
- ○ [0898](/solutions/0898/) — Claire Voyant
- ○ [0901](/solutions/0901/) — Well Drilling
- ○ [0930](/solutions/0930/) — The Gathering
- ○ [0959](/solutions/0959/) — Asymmetric Random Walk
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value
- ○ [0969](/solutions/0969/) — Kangaroo Hopping
- ○ [0970](/solutions/0970/) — Kangaroo Hopping over Sixes
- ○ [0973](/solutions/0973/) — Random Dealings
- ○ [0978](/solutions/0978/) — Random Walk Skewness
- ○ [0982](/solutions/0982/) — The Third Dice

<!-- /problems -->
