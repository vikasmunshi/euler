<!-- tags: [markov-chain] -->
<!-- status: final -->
# Markov chain

A [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) is a random process that forgets:
the next state depends only on the current state and a fixed table of transition probabilities,
never on the path that led there. That single property — *memorylessness* — is what turns a
sprawling probabilistic story into a finite object you can compute with. The problems below are
games, walks, shuffles, deals and cutting rules with no obvious common structure; what they share
is that each one can be squeezed into a state space small enough to propagate exactly. Finding
that squeeze is the whole exercise. The arithmetic afterwards is textbook.

## The idea

A chain is a set of states $S$ and a matrix $P$ with $P_{ij} = \Pr[\,i \to j\,]$ in one step, each
row summing to $1$ — a [stochastic matrix](https://en.wikipedia.org/wiki/Stochastic_matrix). If
$\pi_k$ is a row vector holding the probability of being in each state after $k$ steps, then

$$\pi_{k+1} = \pi_k P, \qquad \pi_k = \pi_0 P^k.$$

Everything you can ask about the process is a query against that recurrence, and in practice there
are only four:

| question | object | how you compute it |
| --- | --- | --- |
| where am I after $k$ steps? | $\pi_0 P^k$ | forward propagation, $k$ multiplies |
| where do I end up in the long run? | stationary $\pi = \pi P$ | [power iteration](https://en.wikipedia.org/wiki/Power_iteration), or solve for the eigenvector |
| which absorbing state do I hit? | absorption probabilities | one linear system, or a DP if the states are acyclic |
| how long until I stop? | expected hitting time | one linear system, same shape |

The last two are the [absorbing chain](https://en.wikipedia.org/wiki/Absorbing_Markov_chain)
questions, and both come from the same one-line argument — condition on the first step. Writing
$E_i$ for the answer starting from state $i$,

$$E_i = c_i + \sum_j P_{ij} E_j,$$

with $c_i$ the cost charged for taking a step ($1$ for a hitting time, $0$ for a hitting
probability) and the absorbing states pinned to known values. Move the unknowns to the left and
that is a [system of linear equations](/topics/technique/system-of-linear-equations) in $|S|$
unknowns. Problem 227 is this in its purest form: two dice circulate around a table of $n$ players
and the game ends when they meet, so the state is the gap between them, the step distribution is
the convolution of the two dice, and the answer is one $O(n^3)$ solve away.

The crucial fork is whether the transition graph has **cycles**. If a state can only ever move
"forward" — a card is discarded, a piece is placed, a round elapses — the system is triangular and
you never build a matrix at all: a [dynamic programming](/topics/technique/dynamic-programming)
sweep in dependency order evaluates it in $O(\text{states} \times \text{out-degree})$. If states
can be revisited (any walk that can step back where it came from), the dependency is genuinely
circular and you owe a real solve, or an iteration to a fixed point. Problem 938 sits on the
acyclic side — the deck's `(red, black)` counts only ever shrink, so the whole chain collapses to a
two-term recurrence swept diagonal by diagonal — and 227 sits on the cyclic side.

## Choosing the state is the whole game

The transition rules are handed to you. The state space is not, and that is where these problems
are won or lost. Two moves recur, in opposite directions.

**Augment, when the naive state is not Markov.** A chain is only legitimate if the transition
probabilities depend on nothing but the state. If a rule references history, the state is
incomplete and you must widen it until it does not. Problem 84 (public, so worth reading in full)
walks a Monopoly board: 40 squares looks like the state space, but "three consecutive doubles sends
you to jail" is a fact about the *past*. The fix is to carry the streak along, giving $40 \times 3$
states and a rule that is once again purely local:

```python
for position in range(board_size):
    for doubles in range(3):
        row = matrix[position * 3 + doubles]
        for first in range(1, dice_size + 1):
            for second in range(1, dice_size + 1):
                if first == second and doubles == 2:
                    row[JAIL * 3] += roll_probability      # third double: straight to jail
                    continue
                next_doubles = doubles + 1 if first == second else 0
                ...
```

Tripling the state space is a small price for a rule that is now exactly, rather than
approximately, modelled. The same widening handles a "score so far" in a scoring game, a
"remaining budget", or a phase counter — and problem 610's Roman-numeral generator is the extreme
case, where the state must be the partially-written numeral's grammatical position, because that is
precisely what constrains the next symbol.

**Collapse, when the naive state carries information the dynamics never use.** This is the more
valuable move, and it is always justified by a symmetry or an independence argument. In 227, a
chain over *ordered pairs of seats* has $n^2$ states and an $O(n^6)$ solve; the table is rotationally
symmetric, so only the difference matters, and $n$ states with an $O(n^3)$ solve give the identical
answer. In 253 the honest state is the multiset of gap widths between filled runs — an
[integer partition](https://en.wikipedia.org/wiki/Partition_(number_theory)), millions of them —
but conditioning on the history shows the gap widths remain a uniform random composition
throughout, so they can be *averaged away* and the chain runs on `(pieces placed, segment count,
two boundary flags)`. In 930 the balls on a circle collapse by translation invariance much as the
dice do in 227.

Collapsing is exact when the discarded coordinate genuinely does not influence the future — a
[lumpability](https://en.wikipedia.org/wiki/Markov_chain#Lumpability) argument, not a heuristic. It
is worth spending real effort on, because the payoff is usually a polynomial factor of the state
count, not a constant.

## Sparse propagation beats matrix algebra

Textbook treatments present the chain as a matrix and reach for $P^k$ or
[matrix exponentiation](/topics/technique/matrix-exponentiation). That is the right call only when
the state space is small and dense, or when $k$ is astronomically large and you need
$O(|S|^3 \log k)$. Far more often the reachable set is a tiny sparse corner of the nominal space,
and the winning implementation never materialises $P$ at all:

- **Forward propagation over a dictionary.** Keep `{state: probability}` and, each step, push each
  live state's mass to its successors. Problem 151's envelope has five sheet counts — nominally a
  five-dimensional grid — but only a handful of states are ever reachable across the sixteen
  batches, so a sparse sweep is effectively constant-time, while the dense array would be over a
  million cells. (The C port there earns the same sparsity back by hand, with an explicit list of
  occupied indices.)
- **A stencil instead of a matrix multiply.** When the chain is a
  [random walk](/topics/domain/random-walk) on a grid, one step of $\pi P$ *is* "each cell ships an
  equal share to each neighbour". Writing it as four shifted array additions is an exact rewrite of
  the multiply at $O(|S|)$ instead of $O(|S|^2)$ — problem 213 advances 900 simultaneous walk
  distributions this way, in [NumPy](https://numpy.org/doc/stable/) and again in C.
- **Rolling buffers over an ordered sweep.** If the states admit a level ordering (steps taken,
  cards remaining, anti-diagonal index), only two levels are ever live; the memory drops from
  $O(|S|)$ to $O(\sqrt{|S|})$ or better, which is what makes 938's $1.5 \times 10^8$-cell grid
  tractable.

Reserve the explicit matrix for what it is actually good at: the stationary distribution of a
modest ergodic chain, where power iteration to a $10^{-15}$ fixed point is a dozen lines and
converges in a few hundred passes (problem 84), or a hitting-time system small enough that
[Gaussian elimination](https://en.wikipedia.org/wiki/Gaussian_elimination) with partial pivoting is
free.

## When the chain has choices

A handful of these problems are not chains at all but
[Markov decision processes](https://en.wikipedia.org/wiki/Markov_decision_process): at each state
an agent picks among actions, and the question is the value under *optimal* play. Problem 640's
dice-and-cards game (turn over $x$, $y$, or $x+y$) and 852's coin box (keep tossing, or stop and
guess) are both of this kind. The machinery barely changes — the conditioning equation grows a
$\max$ or $\min$ over actions,

$$V_i = \max_a \Big( c_i^a + \sum_j P^a_{ij} V_j \Big),$$

— but the consequences do. A $\max$ makes the system non-linear, so a direct solve is off the
table; on an acyclic state space you sweep in dependency order as before, and on a cyclic one you
iterate to a fixed point ([value iteration](https://en.wikipedia.org/wiki/Markov_decision_process#Value_iteration)),
which converges because the optimal-value operator is a contraction. Recognising that a problem
says "he must choose" rather than "he moves at random" is the difference between the two.

## How to reason about it

- **Say the state out loud, then test it.** "The next step depends only on …" — finish the
  sentence, and check that nothing in the rules contradicts it. If something does, you have found
  the coordinate you are missing, not a reason to give up on the chain.
- **Then attack the state from the other side.** Ask which coordinates the *dynamics* never
  consult. Symmetry (rotation, relabelling, exchangeability) and conditional independence are the
  two arguments that let you delete one, and each deletion is typically worth a polynomial factor.
- **Classify before you compute.** Acyclic transitions → a DP sweep, no linear algebra. Cyclic with
  absorption → one linear system for absorption probabilities or hitting times. Ergodic and
  long-run → a stationary distribution by power iteration. Fixed finite horizon → forward
  propagation of $\pi_k$. Picking the wrong one of the four is the most expensive mistake available
  here.
- **Never simulate for the answer.** [Monte Carlo](https://en.wikipedia.org/wiki/Monte_Carlo_method)
  is non-deterministic, and the harness re-runs `solve()` and demands an identical result — a
  simulated ranking or a six-decimal expectation will wobble. Every one of these chains is exactly
  computable. Simulate to *check* an exact result on a small case, never to produce one.
- **Watch the precision, not just the complexity.** Propagating a distribution only ever adds and
  multiplies non-negative numbers that sum to $1$, which is numerically benign, so `double` is
  usually plenty even over tens of thousands of steps — and it keeps the C port a line-for-line
  mirror rather than a bignum rewrite. Solving a linear system is a different matter: pivot, and
  sanity-check the residual. When an exact rational is genuinely needed, verify against it once on
  a small case rather than carrying fractions through the whole run.
- **Check the mass.** Every row of $P$, and every state's outgoing weights, must sum to exactly
  $1$. Asserting that is the cheapest bug detector in this entire domain — it catches a
  double-counted move or a dropped case immediately, long before the answer is wrong by a
  suspicious-looking margin. It is also how you know a state collapse was legitimate.

For the closely related question of what you *do* with the resulting distribution, see
[expected value](/topics/domain/expected-value); for the absorbing case specifically, see
[absorbing Markov chain](/topics/technique/absorbing-markov-chain).

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
- ○ [0575](/solutions/0575/) — Wandering Robots
- ○ [0589](/solutions/0589/) — Poohsticks Marathon
- ○ [0595](/solutions/0595/) — Incremental Random Sort
- ○ [0610](/solutions/0610/) — Roman Numerals II
- ○ [0640](/solutions/0640/) — Shut the Box
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0819](/solutions/0819/) — Iterative Sampling
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0852](/solutions/0852/) — Coins in a Box
- ○ [0930](/solutions/0930/) — The Gathering
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ○ [0973](/solutions/0973/) — Random Dealings

<!-- /problems -->
