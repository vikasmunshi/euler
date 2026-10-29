<!-- tags: [expected-value] -->
<!-- status: final -->
# Expected value

The [expected value](https://en.wikipedia.org/wiki/Expected_value) of a random quantity is
its long-run average — each outcome weighted by how likely it is. It is the single most
common probabilistic ask in Project Euler: the expected number of empty squares, of distinct
colours, of moves, of rolls, of steps. What makes it a *domain* worth its own page is that
the honest way to compute it is almost never the obvious way. The obvious way enumerates every
joint outcome and its probability; the useful way finds a structure that lets you avoid that
enumeration entirely — or, when the statistic will not split, a state small enough to carry its
whole distribution. Most of the problems below are exercises in spotting which structure applies.

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

The pieces need not be indicators, either. Problem 523 asks for the expected number of moves a
quirky sort makes on a random permutation — a *process*, not a count, and on its face one whose
moves interleave messily. The leverage is to recognise the procedure as
[insertion sort](https://en.wikipedia.org/wiki/Insertion_sort) in disguise: it always keeps a sorted
prefix and never touches the tail until that prefix is clean, so the total cost is a sum of $n-1$
*per-element insertion costs*. Each of those is a deterministic function of one thing — how many
prefix elements are smaller than the newcomer — which a small recurrence pins down in closed form,
and in a uniform permutation that rank is uniform. Linearity then turns the expected total into a
single sum over $k$ of "average cost of inserting the $(k+1)$-th element", with no permutation ever
enumerated. The general move: when a random process runs in stages, ask whether its cost
*decomposes by stage*, and whether each stage's cost depends only on a variable whose distribution
you know. You do not need the stages to be independent — only to be able to average each one alone.

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

## When the quantity is not a sum: carry the distribution

Linearity has a hard edge: it covers sums, and nothing else. A **maximum** is not a sum, and
$\mathbb{E}[\max_k s_k]$ is not $\max_k \mathbb{E}[s_k]$ — the expected peak of a fluctuating walk
sits strictly above the peak of its expected path. Problem 253 asks exactly this: forty pieces are
laid into a row in uniformly random order, the number of separate segments $s_k$ rises and falls, and
the target is the expected *largest* segment count seen along the way. Neither indicators nor a
recurrence on $\mathbb{E}[s]$ can produce that. What works is to stop tracking an expectation and
track a **distribution**: add the running peak to the state, push probability mass forward step by
step through the [Markov chain](/topics/domain/markov-chain), and only at the end read off
$\mathbb{E}[M] = \sum_m m \Pr[M = m]$. Forward probability propagation is first-step analysis run in
the other direction, and it is the move to reach for whenever the statistic is a max, a min, a
"first time above", or anything else non-linear in the path.

The harder half of 253 is making that state small. The next move depends on the widths of the empty
gaps, and carrying the multiset of widths means carrying an integer partition — millions of states.
The reduction is a conditional-symmetry argument: given the segment count and whether each end cell
is still empty, the gap widths form a uniform random
[composition](/topics/domain/composition-combinatorics) of the empty cells, *independently of the
history* that produced them. So the widths are not state at all; they can be averaged away using two
marginals of a uniform composition of $E$ into $P$ parts — mean part $E/P$, and a designated part
equal to $1$ with probability $(P-1)/(E-1)$. This is the same instinct as linearity, applied one
level up: [find the symmetry](/topics/takeaway/exploit-symmetry) that lets a high-dimensional
variable be replaced by its average, and make sure the quantity you replace it in is linear in it.

## When the "random" input is just every input

Sometimes the probability is a veneer. "The average number of iterations over all fourteen-digit
$n$" (problem 255) is an expectation under the uniform distribution on a finite set, which is to say
a *total divided by a count*. There is no clever probability to compute and no indicator to name; the
only obstacle is that the set has $9 \times 10^{13}$ elements. The leverage here is
[splitting inputs into behaviour classes](/topics/takeaway/split-inputs-into-behaviour-classes):
the integer Heron iteration reads $n$ only through $\lceil n/x \rceil$, which is constant on blocks
of consecutive $n$, so a whole interval of inputs that share an estimate splits into a handful of
sub-intervals that share the next one ([quotient blocking](/topics/technique/quotient-blocking),
applied recursively). Each leaf contributes (steps) × (width) to an integer total, and the tree has
roughly $\sqrt{10^{14}}$ nodes rather than $10^{14}$. When an expectation is defined as an average
over an enumerable population, ask what the computation actually *reads* from each input — inputs
that read the same thing contribute the same amount, and can be counted together.

## How to reason about it

- **Try to avoid enumerating.** Before summing over a joint outcome space, ask whether the answer
  is a sum of pieces (linearity), the value of a process (conditioning), or an average over a
  population whose members fall into a few behaviour classes. One of these almost always applies,
  and each replaces an intractable sum with a tractable one.
- **Indicators for counts, first-step for processes.** "Expected number of X" → write X as
  $\sum$ indicators and add probabilities. "Expected value/length of a game or walk" → define
  $E[\text{state}]$ and relate each state to its neighbours.
- **Check that the statistic is linear before using linearity.** Maxima, minima, products and
  "ever reached" questions are not sums. For those, propagate the full distribution with the
  statistic folded into the state (problem 253's running peak), and take the expectation last.
- **Keep it exact when the output demands it.** Many of these ask for an answer to six, nine, or
  thirteen decimal places. An expectation is a sum or ratio of rationals, so the exact answer is a
  fraction; carrying it as integers (Python's arbitrary precision, or `__int128` / a rational type
  in C) and rounding only at the very end avoids the floating-point drift that a `double`
  accumulates over a long sum — problems 121 and 493 both hinge on this. Exactness matters most
  where an expectation lands *on* a rounding boundary: problem 523's own worked example, $E(10)$,
  is a fraction whose decimal expansion ends exactly in a 5 at the third place, so asked for two
  decimals, any `double` drift — or a banker's-rounding `round` — picks the wrong side; summing
  rationals and rounding half-up in integers is the only deterministic answer. Problem 255 keeps an
  integer total and rounds to ten places with an integer formula, using `__int128` in C only for
  the one product that would overflow. But exactness is a judgement, not a rule: a forward pass that
  only adds and multiplies non-negative probabilities summing to $1$ is numerically benign, and
  problem 253 runs it in plain [`double`](/topics/technique/double-precision-floating-point-format)
  after confirming against one exact rational run that the error sits orders of magnitude below the
  places asked for. Reserve a [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method)
  simulation for *cross-checking* the result, not producing it.
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
- ● [0255](/solutions/0255/) — Rounded Square Roots
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
- ● [0523](/solutions/0523/) — First Sort I
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
