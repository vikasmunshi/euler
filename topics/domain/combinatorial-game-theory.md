<!-- tags: [combinatorial-game-theory] -->
<!-- status: final -->
# Combinatorial game theory

[Combinatorial game theory](https://en.wikipedia.org/wiki/Combinatorial_game_theory) studies
two-player games of **perfect information and no chance**: both players see the whole position,
moves alternate, play is finite, and under the usual
[normal play convention](https://en.wikipedia.org/wiki/Normal_play_convention) the player who
cannot move loses. That is narrow enough to be a real theory — every position is a win or a loss
for whoever is to move, decided before a single stone is lifted — and broad enough to cover the
seventy-odd problems below, which arrive dressed as Nim, stone games, coin games, strip games,
card games and board games. The archive's twist is that it almost never asks you to *play*. It
asks you to **count** the positions of a given outcome over a range far too large to enumerate,
so the actual work is turning "the first player wins" into arithmetic.

## The two-line theory: P- and N-positions

Every position is either a $\mathcal{P}$-position (the **P**revious player wins — the player to
move loses) or an $\mathcal{N}$-position (the **N**ext player, the one to move, wins). The
classification is forced by two rules and nothing else:

- a position with no legal move is a $\mathcal{P}$-position (you are to move, you cannot, you lose);
- a position is an $\mathcal{N}$-position if **some** move reaches a $\mathcal{P}$-position, and a
  $\mathcal{P}$-position if **every** move reaches an $\mathcal{N}$-position.

That is [backward induction](/topics/technique/backward-induction) over the game graph, and it is
five lines of code:

```python
def wins(position):                       # True iff the player to move wins
    moves = list(successors(position))
    if not moves:                         # normal play: no move, you lose
        return False
    return any(not wins(m) for m in moves)
```

Written with [memoization](/topics/technique/memoization) over a canonical encoding of the
position, this is the brute force you should write *first* for any of these problems — not because
it will reach the required size (it never does), but because it is the ground truth against which
you check the pattern you are about to conjecture. Two of the solved problems here, 301 and 899,
keep exactly such a brute-force script beside the fast solution for that purpose.

## Sums of games: mex, Grundy values, and Nim

The reason this domain has a theory rather than a pile of case analyses is that most of these games
decompose. A position is often a **disjunctive sum** of independent components — several heaps,
several strips, several coins — and a move touches exactly one of them. For
[impartial games](/topics/domain/impartial-game) (both players have the same moves available), the
[Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem) says each
component is equivalent to a single Nim heap, whose size is the component's **Grundy value**, and
that a sum of components behaves like Nim on those values:

```python
def grundy(component):
    seen = {grundy(c) for c in successors(component)}
    g = 0
    while g in seen:                      # mex: least non-negative integer not in the set
        g += 1
    return g

# the whole position is a loss for the player to move exactly when
#   grundy(c1) ^ grundy(c2) ^ ... ^ grundy(ck) == 0
```

Two ideas are doing all the work. The [mex](/topics/domain/mex-function-set-theory) (minimum
excludant) is what makes a value out of a move set, and the exclusive-or is
[nimber](/topics/domain/nimber) addition — the arithmetic of the theory. Ordinary three-heap Nim is
the degenerate case where `grundy(heap) == heap`, so a position is lost exactly when the heap sizes
XOR to zero; that single fact is the whole of problem 301, which asks how many $n$ make
$(n, 2n, 3n)$ a loss and thereby turns a game into a question about the binary digits of $n$.

Once you hold this, a large family of the problems below is one template: **compute the Grundy
value of a single heap under the variant's move rule, then XOR**. The variants change only the move
rule — remove a square number (310), a proper divisor (509), an amount coprime to the heap (560),
one of a fixed set or a split (888), split into at most $k$ parts (629), delete a digit in some base
(882, 963). The difficulty moves entirely into the *arithmetic of the Grundy sequence*: it is
usually eventually periodic, or determined by a heap's factorisation or its bit pattern, and finding
that structure — then proving it on a brute-force table — is the problem.

The same template covers games that do not look like heaps at all. Gaps between coins on a strip
are heaps (344, the silver dollar game). A token that may move in either of two directions is
itself the sum of two one-dimensional games, so its value is the XOR of a row value and a column
value (649). Coin-turning games — flip a rectangle of disks subject to a shape rule (459) — are
sums of one-coin games, and the two-dimensional ones are governed by nim-*multiplication*. A game
on a recursively built tree (400) decomposes into subtrees. The skill being trained is seeing the
independent parts.

## When the decomposition fails

Plenty of these problems refuse to split, and reaching for XOR anyway is the classic way to get a
confidently wrong answer. Three situations to recognise:

**One indivisible position.** When a move's legality depends on the *other* components — remove a
multiple of the smaller pile (325), take the smallest pile's worth spread across piles (899, 900),
remove $c$ and $d$ with $ad - bc = \pm 1$ (787), the "at most twice the previous move" rule of
Fibonacci nim (366, 692) — there are no independent parts and no Grundy value to compute. What you
look for instead is a direct characterisation of the whole $\mathcal{P}$-position set, and it is
almost always something startlingly clean: a condition on the low bits of one pile relative to the
bit length of the other (899), a [Beatty](https://en.wikipedia.org/wiki/Beatty_sequence)-like pair
of sequences in the style of [Wythoff's game](https://en.wikipedia.org/wiki/Wythoff%27s_game) (665),
a [Zeckendorf representation](/topics/domain/zeckendorfs-theorem) (692), a
[continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) expansion (787). Generate the
losing positions with the brute force, stare at them in binary and in their factorisations, and
conjecture.

**Partisan games.** If the two players have *different* moves — Left removes from the left, Right
from the right (948, 949); one player deletes gold coins, the other silver (860, 895); a player may
only strip their own piles (939); X and O place different symbols (976) — Sprague–Grundy does not
apply at all. These are [partizan games](/topics/domain/partizan-game), whose values live in
[Conway's surreal numbers](https://en.wikipedia.org/wiki/Surreal_number) rather than in the nimbers,
and a position must be classified by *four* outcomes (Left wins whoever starts, Right wins whoever
starts, first player wins, second player wins). The recurring Euler phrasing "whoever plays first
loses" or "the arrangement is fair" is precisely the fourth outcome — a game of value zero.

**Misère play.** When the player taking the last stone *loses*, the normal-play Grundy machinery
breaks; misère Nim has a famous patch, but misère variants in general do not, and you must redo the
induction with the terminal condition flipped rather than adjust the answer at the end.

## Beyond win-or-lose

The tag also gathers problems that are games in the ordinary sense but outside the combinatorial
core, and they need different machinery — worth naming so you do not reach for the wrong tool:

- **Chance.** Dice or coins make a position's value an *expectation*, not a bit: Shut the Box (640)
  is an expectimax over a twelve-card bitmask, and the elimination round of 683 is an absorbing
  [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) feeding an optimal-stopping decision.
- **Scores instead of outcomes.** When both players maximise their own total (477), the value is a
  number and the recursion is [minimax](https://en.wikipedia.org/wiki/Minimax) — for the take-from-
  either-end game, the tidy form is the score *difference*,
  $d(i,j) = \max\big(a_i - d(i+1,j),\ a_j - d(i,j-1)\big)$.
- **Hidden information.** Guessing games with an adversarial answerer (406, 847, 848) are
  worst-case decision trees: an information-theoretic lower bound plus a
  [dynamic programming](/topics/technique/dynamic-programming) search for a strategy that meets it.
- **Pursuit and economics.** Catching a mouse on a graph (690, 825, 761) is a fixed-point
  computation over the set of positions still consistent with the search so far; the pirates of 950
  are pure backward induction from the last surviving proposer.
- **Solitaires and invariants.** Single-player token games (426, 664, 986) are usually settled by a
  **weight function**: assign each square a value so that no move can increase the total, and the
  invariant caps what is reachable; then exhibit a construction that attains the cap.

## The Euler twist: from a game to a count

Almost none of these problems ask for the outcome of one position. They ask for the number of
losing positions with piles below $10^7$, or the sum over all starting integers below $10^{18}$, or
a count modulo $10^9 + 7$. So solving the game is the *setup*; the deliverable is a count, and the
pipeline is nearly always the same three stages:

1. **Brute force small cases** with the five-line induction above, and tabulate the
   $\mathcal{P}$-positions or Grundy values.
2. **Find the structure** — a periodicity in the Grundy sequence, a bit condition, a
   closed form — and verify it against the table and against every value the statement gives you.
3. **Count without enumerating.** A bit condition becomes a digit DP over the binary expansion of
   the bound (as in 301); a per-heap Grundy value becomes a convolution or a
   [generating function](https://en.wikipedia.org/wiki/Generating_function) over $k$ heaps, since
   "the XOR of $k$ independent values is zero" is a counting problem in
   $(\mathbb{Z}/2)^{b}$ that a Walsh–Hadamard style transform or a per-bit argument handles in
   $O(\text{bits})$ rather than $O(n^k)$ — that is the shape of 409, 560 and 888.

Problem 961 is a compact illustration of the whole arc: the game is played on the decimal digits of
an integer, but only the pattern of zero and non-zero slots matters, so a position is a small
bitmask, the induction runs bottom-up over all masks, and the count of winning integers follows by
weighting each winning mask by how many integers wear it.

## How to reason about it

- **Write the honest brute force first, and keep it.** Every pattern you will conjecture is a
  pattern in its output, and it is the only check you have that the fast version is right.
- **Ask whether the position is a sum.** If a move touches exactly one independent component, compute
  Grundy values and XOR. If a move's legality depends on the other components, do not — characterise
  the whole position instead.
- **Check the convention before anything else.** Normal or misère; impartial or partisan. Both
  mistakes are silent, and both invalidate the entire machinery.
- **Look at the losing positions in binary.** Then in their factorisations, then as sums of
  Fibonacci numbers. The characterisations in this domain are overwhelmingly arithmetic, and the
  first place they show up is the bit pattern.
- **Expect periodicity, but prove it.** Grundy sequences of octal-style games tend to become
  periodic — the classic example is the strip game of problem 306, the same game as
  [Dawson's Kayles](https://en.wikipedia.org/wiki/Dawson%27s_Kayles) — and a period lets you answer
  for $10^6$ from a table of a few hundred. Confirm the period over a long stretch, not the first
  repeat you see.
- **Encode the state canonically.** Sort the heaps, pack the board into an integer, quotient by the
  symmetry the rules allow. Most of these state spaces are only tractable once identical positions
  stop being counted twice.
- **Do not stop at "I can decide a position".** The question is a count over a range you cannot walk,
  so budget your effort for the step that converts the winning condition into closed-form or
  digit-DP arithmetic. That step, not the game analysis, is usually where the problem is won.

<!-- problems (generated by update-tags) -->
## Problems

- ○ [0260](/solutions/0260/) — Stone Game
- ● [0301](/solutions/0301/) — Nim
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ○ [0310](/solutions/0310/) — Nim Square
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0367](/solutions/0367/) — Bozo Sort
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0406](/solutions/0406/) — Guessing Game
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0426](/solutions/0426/) — Box-Ball System
- ○ [0444](/solutions/0444/) — The Roundtable Lottery
- ○ [0459](/solutions/0459/) — Flipping Game
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ○ [0481](/solutions/0481/) — Chef Showdown
- ○ [0488](/solutions/0488/) — Unbalanced Nim
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0509](/solutions/0509/) — Divisor Nim
- ○ [0550](/solutions/0550/) — Divisor Game
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0566](/solutions/0566/) — Cake Icing Puzzle
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ○ [0640](/solutions/0640/) — Shut the Box
- ○ [0644](/solutions/0644/) — Squares on the Line
- ○ [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0664](/solutions/0664/) — An Infinite Game
- ○ [0665](/solutions/0665/) — Proportionate Nim
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0690](/solutions/0690/) — Tom and Jerry
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ○ [0711](/solutions/0711/) — Binary Blackboard
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0761](/solutions/0761/) — Runner and Swimmer
- ○ [0770](/solutions/0770/) — Delphi Flip
- ○ [0787](/solutions/0787/) — Bézout's Game
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0847](/solutions/0847/) — Jack's Bean
- ○ [0848](/solutions/0848/) — Guessing with Sets
- ○ [0855](/solutions/0855/) — Delphi Paper
- ○ [0859](/solutions/0859/) — Cookie Game
- ○ [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0870](/solutions/0870/) — Stone Game IV
- ○ [0882](/solutions/0882/) — Removing Bits
- ○ [0888](/solutions/0888/) — 1249 Nim
- ○ [0895](/solutions/0895/) — Gold & Silver Coin Game II
- ● [0899](/solutions/0899/) — DistribuNim I
- ○ [0900](/solutions/0900/) — DistribuNim II
- ○ [0922](/solutions/0922/) — Young's Game A
- ○ [0923](/solutions/0923/) — Young's Game B
- ○ [0933](/solutions/0933/) — Paper Cutting
- ○ [0939](/solutions/0939/) — Partisan Nim
- ○ [0948](/solutions/0948/) — Left vs Right
- ○ [0949](/solutions/0949/) — Left vs Right II
- ○ [0950](/solutions/0950/) — Pirate Treasure
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ● [0961](/solutions/0961/) — Removing Digits
- ○ [0963](/solutions/0963/) — Removing Trits
- ○ [0976](/solutions/0976/) — XO Game
- ○ [0982](/solutions/0982/) — The Third Dice
- ○ [0986](/solutions/0986/) — Another Infinite Game
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
