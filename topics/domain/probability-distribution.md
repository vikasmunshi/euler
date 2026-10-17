<!-- tags: [probability-distribution] -->
<!-- status: final 2026-10-17T07:37Z -->
# Probability distribution

A [probability distribution](https://en.wikipedia.org/wiki/Probability_distribution) is a table:
every outcome a random experiment can produce, each with a weight, the weights summing to one.
Project Euler keeps returning to it because almost every probability problem has the same shape.
The statement gives you a few small distributions you can write down at once (a fair die, a coin
toss, a card drawn from a sixteen-card deck, a uniformly random permutation) and asks about a
distribution *derived* from them: the total of nine dice, the square a Monopoly token lands on in
the long run, whether a player wins a race. The work is building the derived table without listing
the joint outcome space it comes from. That space is usually astronomically large, and the derived
table is usually small.

## The idea

For a discrete random variable the distribution is its
[probability mass function](https://en.wikipedia.org/wiki/Probability_mass_function): $p(x) =
\Pr[X = x]$, with $p(x) \ge 0$ and $\sum_x p(x) = 1$. In code that is an array indexed by outcome,
or a dictionary when the outcomes are sparse. Every solve below holds a table like this and
transforms it. Across the solved problems I count four transformations, and spotting which one a
problem needs is most of the analysis.

**1. Sum of independent variables: convolve.** If $X$ and $Y$ are independent, the distribution of
$X + Y$ is the [convolution](/topics/technique/convolution) of theirs:
$\Pr[X+Y=s] = \sum_k \Pr[X=k]\Pr[Y=s-k]$. Problem 205 pits nine four-sided dice against six
six-sided ones. The joint space has $4^9 \cdot 6^6 \approx 1.2\times10^{10}$ outcomes, but each
player's total has only a few dozen values. So I build each player's table one die at a time, with
each die spreading every existing count across its faces:

```python
d = [1]                                   # zero dice: total 0, one way
for _ in range(n_dice):
    new_d = [0] * (len(d) + n_sides)
    for i, c in enumerate(d):
        for face in range(1, n_sides + 1):
            new_d[i + face] += c
    d = new_d
```

Because the two players are independent, "Peter beats Colin" reduces to
$\sum_s \Pr[P = s]\Pr[C < s]$. A [prefix sum](/topics/technique/prefix-sum) over Colin's table gives
$\Pr[C < s]$ for every $s$ in one pass. One convolution and one prefix sum replace ten billion
enumerated outcomes.

**2. One step of a random process: push the table through a transition.** If the next state
depends only on the current one, the distribution one step later is the current table multiplied
by the transition matrix of a [Markov chain](/topics/domain/markov-chain). If you keep stepping
until nothing changes, you reach the [stationary distribution](/topics/domain/stationary-distribution)
$\pi = \pi P$. Problem 84 (Monopoly) does exactly this with
[power iteration](/topics/technique/power-iteration). The design lesson is in how the matrix is
built. A square's row is not "move by the dice total"; it is a mixture. Roll two dice, land on a
square, then *resolve* that landing through the board's rules into a distribution over finishing
squares. Chance sends you to one of nine places at $1/16$ each and leaves you where you are at
$6/16$. One of its cards, "go back three", can land on Community Chest, so `resolve` calls itself
and adds the second table into the first, weighted by $1/16$. Composing distributions like this,
an outcome that is itself a distribution, is the general move. The other half of the lesson is
the state. "Three doubles in a row sends you to jail" means the square alone is not Markov, so the
state becomes (square, doubles so far), $40 \times 3$ entries. At the end it is marginalised back
to per-square probabilities by summing the three streak entries.

**3. A distribution over outcomes with a decision in it: induct backwards.** Problem 232's race
has a player choose how many coin tosses $T$ to risk. That choice gives probability $2^{-T}$ of
scoring $2^{T-1}$ points and otherwise scores nothing. The relevant distribution is the
two-outcome one for each $T$, and the problem is to choose the best $T$ in every state. With states
indexed by points still needed, a [backward induction](/topics/technique/backward-induction) over
the (needed, needed) grid fills in each player's win probability from states closer to the end.
The trap is the failure outcome. Tails on every toss returns the game to *the same state*, so the
recurrence refers to itself. Solving the one-variable linear equation
$x = \tfrac12 h + \tfrac12\big(q\,w + (1-q)\,x\big)$ for $x$ gives
$x = (h + q\,w)/(1+q)$. That replaces an infinite tail of repeated failures, a
[geometric series](/topics/technique/geometric-series), with a closed-form
[fixed point](/topics/technique/fixed-point-iteration) per choice of $T$. Then the solve takes the
maximum over $T$. It also bounds $T$ before searching: once $2^{T-1}$ already reaches the target,
a larger $T$ only lowers the success probability, so the search stops at $\lceil\log_2 b\rceil + 1$.

**4. Uniform over a finite set: count, then divide.** When every outcome is equally likely,
$\Pr[E] = |E| / |\Omega|$, and the distribution reduces to counting.
Problem 239 shuffles the discs $1..100$ uniformly and asks for the probability that exactly 22
of the prime-numbered discs end up off their own positions. The favourable count picks which
primes stay home, then counts arrangements of the rest in which none of the chosen primes is
fixed. That is a [derangement](/topics/domain/derangement)-style
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle),
$\sum_k (-1)^k \binom{d}{k}(m-k)!$, with the non-prime discs left unconstrained. Divide by $100!$
to get the probability. Problem 100 sits at the edge of this family. Drawing two discs without
replacement is the two-draw case of the
[hypergeometric distribution](/topics/domain/hypergeometric-distribution), and asking for
$\Pr[\text{blue, blue}] = \tfrac{b}{n}\cdot\tfrac{b-1}{n-1} = \tfrac12$ turns the probability into
a Diophantine condition. It rearranges to $(2n-1)^2 - 2(2b-1)^2 = -1$, a
[Pell equation](/topics/technique/pells-equation)
([in disguise](/topics/number-theory/pells-equation-in-disguise)). After that, the solution
contains no probability at all.

## Carry counts, not probabilities

One habit runs through the exact solves: the table holds **integer counts**, and the only division
happens once, at the end. Problem 205 convolves counts of ways, sums the wins as an integer, and
divides by $4^9 \cdot 6^6$ just before formatting. Problem 239 keeps the numerator and $100!$
as exact integers and rounds half-up with integer arithmetic,
`(2·num·10^12 + den) // (2·den)`, so all twelve requested decimals are right without a float
anywhere. The reason is cancellation. Inclusion–exclusion alternates signs over terms near
$100!$, and a [`double`](/topics/technique/double-precision-floating-point-format) would lose the
answer in the subtraction.

The processes in families 2 and 3 run in floating point, and that is fine there. Power iteration
and backward induction only multiply and add non-negative weights, so there is no catastrophic
cancellation for error to grow through. Problem 84 needs only the *ranking* of three squares, and
problem 232's eight decimals sit well above `double` round-off.

## C and Python

The algorithms match one for one. They differ in how each language holds a table.

| Problem | Python | C |
|---|---|---|
| 84 | `resolve` returns a sparse `dict` of finishing squares, merged with `.get(k, 0) + p` | `resolve` fills a dense `double[40]`; the caller skips zero entries |
| 84 | top three by `sorted(key=(-p, square))` | three masked linear scans, strict `>` keeping the lowest index on ties, so the order matches Python's |
| 205 | lists of unbounded ints | `long long` counts (the largest is far below $2^{63}$); the $1.2\times10^{10}$ total is exact in a `double` |
| 232 | `2.0 ** -t` | `ldexp(1.0, -t)`, exact and with no `pow` call; the 2-D tables are flattened row-major |
| 239 | native big integers and `//` | [GMP](/topics/technique/gmp) `mpz_t`, with `mpz_divexact_ui` for the running factorial and binomial, which are known to divide exactly |
| 100 | plain ints | `long long`: the Pell iterates stay within 64 bits for totals up to $10^{12}$ |

The pattern is the usual one. Python's [arbitrary-precision](/topics/technique/arbitrary-precision-arithmetic)
integers make the exact "count, then divide" style free. C needs a size argument for each table:
`long long` when the counts provably fit, GMP when they do not, and `double` only where the
analysis above says rounding is harmless.

## How to reason about it

- **Name the derived distribution first.** Ask what single random quantity the question is about
  (a total, a final square, a winner, a count of displaced items) and how many values it can take.
  If that number is small, build its table directly and never enumerate the joint space.
- **Match the transformation to the structure.** For independent pieces that add, convolve. For a
  process that steps from state to state, apply the transition, or iterate it to stationarity.
  When a player chooses, induct backwards and take the maximum. When outcomes are equally likely,
  count favourable cases and divide.
- **Make the state Markov before building a matrix.** Any rule that remembers history (three
  doubles, a running maximum) belongs in the state. Marginalise it away at the end.
- **Settle self-loops algebraically.** "On failure, try again" makes a state depend on itself.
  Solve the linear equation once instead of iterating it.
- **Divide last.** Keep exact counts as long as the arithmetic allows, and treat a `double` as a
  deliberate decision based on the operations involved (no subtraction of near-equal terms) and
  the precision the answer needs.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0205](/solutions/0205/) — Dice Game
- ● [0232](/solutions/0232/) — The Race
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ○ [0267](/solutions/0267/) — Billionaire
- ○ [0286](/solutions/0286/) — Scoring Probabilities
- ○ [0307](/solutions/0307/) — Chip Defects
- ○ [0323](/solutions/0323/) — Bitwise-OR Operations on Random Integers
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0352](/solutions/0352/) — Blood Tests
- ○ [0371](/solutions/0371/) — Licence Plates
- ○ [0376](/solutions/0376/) — Nontransitive Sets of Dice
- ○ [0389](/solutions/0389/) — Platonic Dice
- ○ [0394](/solutions/0394/) — Eating Pie
- ○ [0436](/solutions/0436/) — Unfair Wager
- ○ [0444](/solutions/0444/) — The Roundtable Lottery
- ○ [0481](/solutions/0481/) — Chef Showdown
- ○ [0499](/solutions/0499/) — St. Petersburg Lottery
- ○ [0567](/solutions/0567/) — Reciprocal Games I
- ○ [0568](/solutions/0568/) — Reciprocal Games II
- ○ [0573](/solutions/0573/) — Unfair Race
- ○ [0584](/solutions/0584/) — Birthday Problem Revisited
- ○ [0597](/solutions/0597/) — Torpids
- ○ [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0689](/solutions/0689/) — Binary Series
- ○ [0697](/solutions/0697/) — Randomly Decaying Sequence
- ○ [0744](/solutions/0744/) — What? Where? When?
- ○ [0765](/solutions/0765/) — Trillionaire
- ○ [0807](/solutions/0807/) — Loops of Ropes
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0826](/solutions/0826/) — Birds on a Wire
- ○ [0852](/solutions/0852/) — Coins in a Box
- ○ [0856](/solutions/0856/) — Waiting for a Pair
- ○ [0863](/solutions/0863/) — Different Dice
- ○ [0898](/solutions/0898/) — Claire Voyant
- ○ [0978](/solutions/0978/) — Random Walk Skewness

<!-- /problems -->
