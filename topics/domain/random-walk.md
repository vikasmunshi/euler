<!-- tags: [random-walk] -->
<!-- status: final -->
# Random walk

A [random walk](https://en.wikipedia.org/wiki/Random_walk) is the simplest process that goes
somewhere without knowing where: a token sits on a graph, or a number sits on a line, and each step
displaces it by a randomly drawn increment. Formally it is just a
[Markov chain](/topics/domain/markov-chain), and everything on that page applies here. What earns
walks a page of their own is the *extra* structure a general chain does not have: the state is a
**position**, and the step distribution is usually the same wherever you stand — so the position
after $n$ steps is a **sum of increments**. Sums of independent things are the best-understood
objects in probability, and most of what follows is a way of cashing that in.

## The idea

A walk is a graph (or a lattice, or $\mathbb{Z}$) plus a step distribution. Writing $X_n$ for the
position after $n$ steps and $\Delta_i$ for the increments,

$$X_n = X_0 + \sum_{i=1}^{n} \Delta_i, \qquad
  \mathbb{E}[X_n] = n\mu, \qquad \operatorname{Var}(X_n) = n\sigma^2 .$$

Means and variances add, so the walk drifts by $n\mu$ while spreading only like $\sigma\sqrt{n}$.
That one line is the most useful thing to have in your head before writing any code: it tells you
how wide a window the distribution actually occupies, whether a boundary is reachable inside the
horizon at all, and whether "long run" means a hundred steps or a billion. Two consequences are
worth naming.

**Steps convolve.** The distribution of a sum of independent increments is the
[convolution](/topics/technique/convolution) of their distributions, so composite steps can be
collapsed before you start. In problem 227 two dice circulate around a table and the quantity that
matters is the *gap* between them; each die moves $-1$, $0$ or $+1$ with probabilities
$\tfrac16, \tfrac46, \tfrac16$, and the gap's step is the difference of two such — one convolution,
a five-point distribution, and the two-die game has become a single walk. On a cycle the transition
operator is circulant, which means the [discrete Fourier transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform)
diagonalises it, and $n$-step distributions come from pointwise powers rather than repeated
multiplies.

**Logs turn products into walks.** A process that *multiplies* by a random factor each step is a
walk in disguise: take logarithms and the multiplications become a sum of i.i.d. increments.
Problem 697 iterates $X_n = U_n X_{n-1}$ with $U_n$ uniform on $(0,1)$; since $-\log U$ is
[exponential](https://en.wikipedia.org/wiki/Exponential_distribution), $\log X_n$ is a starting
value minus a sum of $n$ exponentials, and a question about $\Pr[X_n < 1]$ at $n = 10^7$ becomes a
quantile of a well-understood sum rather than anything you could propagate step by step.

The caveat is the same structure read backwards: this all requires increments that do **not** depend
on where the walk currently is. Problem 978 jumps by a distance read off its own earlier position,
so the honest state is the *pair* of recent positions and the increments are neither identical nor
independent — no convolution, no generating function, back to a general chain.

## Where the walk lives

The step rule is usually handed to you in one sentence. The state space is what decides the method.

| space | what it changes | the move |
| --- | --- | --- |
| line or interval | boundaries are the whole question | first-passage system, or a DP if it only moves one way |
| cycle | rotational symmetry | collapse to the gap; circulant steps |
| grid | degree varies at the edge; the graph is bipartite | stencil propagation |
| general graph | degrees differ | stationary distribution $\propto$ degree |
| tree or tiling | branching, no cycles to speak of | collapse to distance from the start |

**On a line**, the ask is nearly always a
[first passage](https://en.wikipedia.org/wiki/First-hitting-time_model): when does the walk reach a
level, and with what probability does it reach one level before another — the
[gambler's ruin](https://en.wikipedia.org/wiki/Gambler%27s_ruin) question. Problem 499 is exactly
this with a heavy-tailed step (a doubling pot against a fixed fee per game), and 589 is it in
disguise: two sticks are re-dropped repeatedly, and "one has lapped the other" is a level crossing
by the difference of their crossing counts. Whenever two objects wander independently, look at their
difference before you look at either of them.

**On a cycle**, that difference is the entire state. Problems 227 and 683 seat players around a
table; a chain over ordered pairs of seats has $n^2$ states, but the table has no preferred seat, so
only the gap matters and $n$ states give the identical answer — a $O(n^3)$ solve instead of
$O(n^6)$. The same translation invariance collapses the balls-on-a-circle process of 930. This is
the single highest-value habit in the domain; see [symmetry](/topics/technique/symmetry).

**On a grid**, the walk is a lattice walk with a boundary, and two facts are easy to miss. Degrees
differ — $4$ in the interior, $3$ on an edge, $2$ in a corner — so the outgoing share is $m/d$, not
$m/4$, in problems 213 and 280 alike. And the grid graph is
[bipartite](https://en.wikipedia.org/wiki/Bipartite_graph): colour it like a chessboard and every
step changes colour, so after an even number of steps the walk is certainly on its starting colour
and *half of every landing distribution is exactly zero*. That is a free sanity check, a factor of
two if you want it, and the reason a lattice walk has no stationary distribution in the naive sense
— it is periodic, and only the two-step average settles down.

**On a general undirected graph** with uniform choice among neighbours, the stationary distribution
is not uniform but proportional to degree,

$$\pi_v = \frac{\deg(v)}{2|E|},$$

which is a closed form, not a computation — no eigenvector, no
[power iteration](/topics/technique/power-iteration). Problem 575's robots wandering a grid of rooms
are this: long-run visit frequencies fall straight out of the room degrees. The formula holds only
for the unbiased walk on an undirected graph; bias the steps or direct an edge and you owe a real
stationary solve.

**On a tree or a vertex-transitive tiling**, distance from the start is usually a sufficient
statistic. Problem 979 counts length-$20$ closed walks on a hyperbolic heptagonal tiling — an
infinite graph, but locally tree-like and the same seen from every tile, so the walk collapses onto
distance levels and the count comes from a small transfer matrix. Note also that *counting* walks
and *weighting* them are the same computation with weights $1$ instead of $1/d$.

## Propagate with a stencil, not a matrix

One step of a lattice walk is a matrix multiply that you should never actually write as one. "Each
cell ships an equal share to each neighbour" is a handful of shifted array additions — a
[stencil](/topics/technique/stencil-numerical-analysis):

```python
share = dist / degree                  # degree is 2, 3 or 4 near the boundary
nxt = np.zeros_like(dist)
nxt[1:, :] += share[:-1, :]            # mass arriving from the row above
nxt[:-1, :] += share[1:, :]            # ... and the other three directions likewise
```

This is an exact rewrite of $\pi P$, at $O(\text{cells})$ per step instead of $O(\text{cells}^2)$,
and it ports to C as four guarded loops over a flat buffer with no library in sight. Problem 213
advances $900$ such distributions simultaneously as one three-dimensional array, which is what makes
an apparently astronomical joint-configuration problem a few million floating-point updates.

Which propagation you want follows from the question, and there are only three:

- **a fixed horizon** ("after $50$ rings", "her first $15$ croaks" in 329) — push $\pi_k$ forward
  that many steps and read the answer off the final distribution;
- **the long run** — a stationary distribution, by the degree formula above where it applies and by
  power iteration otherwise;
- **until it stops** — absorption, which is one
  [system of linear equations](/topics/technique/system-of-linear-equations) per the
  [absorbing-chain](/topics/technique/absorbing-markov-chain) recipe, or a plain
  [DP](/topics/technique/dynamic-programming) sweep when the walk can never revisit a state (as in
  648, where the sum only ever increases).

## Recurrence, drift and range

[Pólya's theorem](https://en.wikipedia.org/wiki/Random_walk#Higher_dimensions) is the one piece of
theory worth carrying around: the symmetric simple walk returns to its origin with probability $1$
in one and two dimensions, and with probability strictly less than $1$ in three or more — "a drunk
man will find his way home, but a drunk bird may get lost forever". Any drift at all makes even the
line transient.

That distinction is not decoration; it decides growth rates. Let $q$ be the escape probability, the
chance of never returning to the start. The expected number of **distinct** sites a walk visits in
$n$ steps grows like $qn$, because each visit begins a fresh escape attempt. Problem 959 asks for
precisely that ratio for a frog stepping $-a$ or $+b$, and the statement hands you $f(1,1) = 0$ —
which is Pólya's recurrent case in one line: the symmetric walk always comes back, so $q = 0$, the
range grows like $\sqrt{n}$ rather than linearly, and the ratio vanishes. Asymmetric steps make it
transient and the limit positive.

The continuous cousin is [renewal theory](https://en.wikipedia.org/wiki/Renewal_theory). Problem 970
hops forward by a uniform distance on $(0,1)$; the number of hops to pass $n$ is a renewal count,
and the elementary renewal theorem gives $n/\mathbb{E}[\text{hop}] = 2n$ immediately, with the exact
asymptotic $2n + \tfrac23$ — which is why the statement's examples are full of sixes, and why the
whole problem is the exponentially small correction to a first-order answer you can write down in a
line.

## How to reason about it

- **Do the envelope arithmetic first.** Drift $n\mu$, spread $\sigma\sqrt{n}$. It tells you the
  regime, the array size you actually need, and whether a boundary matters at this horizon.
- **Ask what the walk forgets.** Absolute positions are almost never the state. Differences,
  distances and gaps are, and the collapse is typically worth a polynomial factor.
- **Name which of the three questions you are answering** — fixed horizon, long run, or until it
  stops. They want three different algorithms, and guessing wrong is the expensive mistake here.
- **Respect parity.** Lattice walks are bipartite, so a fixed-time distribution lives on one colour
  class. Reconcile that before concluding a stationary distribution "isn't converging".
- **Take logs when the process multiplies**, and check that increments really are independent of
  position before reaching for convolution, generating functions or the
  [central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem).
- **Assert that the mass sums to $1$** after every step. It is the cheapest bug detector available —
  a boundary cell that ships out $m/4$ when it should ship $m/3$ shows up instantly, rather than as
  an answer wrong in the fourth decimal.
- **Never simulate for the answer.** The harness re-runs `solve()` and demands an identical result,
  and every walk here is exactly computable. Simulate to *check* a small case, never to produce the
  number.

For the machinery these problems share with non-positional processes, see
[Markov chain](/topics/domain/markov-chain); for what you do with the resulting distribution, see
[expected value](/topics/domain/expected-value).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0213](/solutions/0213/) — Flea Circus
- ● [0227](/solutions/0227/) — The Chase
- ● [0253](/solutions/0253/) — Tidying Up A
- ○ [0280](/solutions/0280/) — Ant and Seeds
- ○ [0329](/solutions/0329/) — Prime Frog
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0499](/solutions/0499/) — St. Petersburg Lottery
- ○ [0575](/solutions/0575/) — Wandering Robots
- ○ [0589](/solutions/0589/) — Poohsticks Marathon
- ○ [0648](/solutions/0648/) — Skipping Squares
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0697](/solutions/0697/) — Randomly Decaying Sequence
- ○ [0807](/solutions/0807/) — Loops of Ropes
- ○ [0930](/solutions/0930/) — The Gathering
- ○ [0959](/solutions/0959/) — Asymmetric Random Walk
- ○ [0970](/solutions/0970/) — Kangaroo Hopping over Sixes
- ○ [0978](/solutions/0978/) — Random Walk Skewness
- ○ [0979](/solutions/0979/) — Heptagon Hopping

<!-- /problems -->
