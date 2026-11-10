<!-- tags: [impartial-game] -->
<!-- status: final 2026-11-02T18:31Z -->
# Impartial game

An [impartial game](https://en.wikipedia.org/wiki/Impartial_game) is a two-player game of perfect
information and no chance in which **the moves available depend only on the position, never on
whose turn it is**. Project Euler keeps returning to them because the statements arrive in costume —
digits on a blackboard, a tree you prune, coins on a chessboard, stones you redistribute — and the
real work is taking the costume off. The mathematics that comes after (P-positions, Grundy values,
the XOR rule) is collected in the curated topic
[Impartial games and nim-values](/blogs/game-theory/impartial-games-and-nim-values), and the wider
setting in [combinatorial game theory](/blogs/domain/combinatorial-game-theory). This page is about
the step before either of those: **reading a statement as an impartial game**, so that the theory
has something exact to work on.

## The idea

Every one of these problems hands you three things, all in disguise. Before computing anything I
want to have written each of them down explicitly.

1. **The position.** This is the smallest state that settles every future move. It is almost never
   the object the statement describes.
2. **The components.** These are the independent parts of the position, if it has any. A move
   touches exactly one of them.
3. **The question.** This is what is actually being counted: losing positions, winning starts,
   winning *moves*, or arrangements.

Only once all three are explicit do I pick a method. The method then usually follows directly: a
win/lose sweep for a single indivisible position, Grundy values plus XOR for a sum, and a hunt for a
closed form when the range is astronomical.

### Is it impartial at all?

The test is the definition, taken literally: swap the players' names and check whether any legal
move changes. "Each player removes a digit" passes. "Left takes from the left end, Right from the
right" fails, and so does "each player may only touch their own piles". Those are
[partisan games](/blogs/domain/partizan-game), and the Sprague–Grundy machinery simply does not
apply to them. The second check is the **ending**. The theory assumes
[normal play](https://en.wikipedia.org/wiki/Normal_play_convention), where the player who cannot move
loses. Many statements dress that up: in [Problem 961](/solutions/0961/), whoever removes the last
non-zero digit wins, which is normal play once you notice that an all-zero number is the terminal
position. Some endings are genuinely different. In [Problem 711](/solutions/0711/) the winner is
decided by the *parity* of a running total when the game stops, not by who moved last. That is still
a finite impartial game, but the parity has to become part of the state before the win/lose
recursion means anything.

### Finding the position

The single most useful habit is asking *what does the future actually depend on?* and throwing
everything else away. The six solved problems here each make a different cut.

| Problem | The statement's state | The position after modelling | What was thrown away |
| --- | --- | --- | --- |
| [961](/solutions/0961/) — Removing Digits | an integer below a power of ten | a bitmask of zero/non-zero digit slots | the digit values themselves |
| [711](/solutions/0711/) — Binary Blackboard | every number written so far | (remaining budget, parity flag) | the history, beyond one bit |
| [899](/solutions/0899/) — DistribuNim I | two piles and a redistribution rule | sorted pair `(a, b)`; a move re-splits `b` with one part at most `a` | the literal "take from both piles" mechanics |
| [400](/solutions/0400/) — Fibonacci Tree Game | a tree whose nodes you delete with their subtrees | [Green Hackenbush](https://en.wikipedia.org/wiki/Hackenbush) on a rooted tree | the "must take the root" phrasing |
| [649](/solutions/0649/) — Low-Prime Chessboard Nim | `c` coins on an `n × n` board | `2c` independent one-dimensional subtraction games | the board |
| [310](/solutions/0310/) — Nim Square | three heaps | three independent heaps | nothing — this one comes undisguised |

Two kinds of cut recur. The first is **forgetting labels that do not affect play**: in 961 a digit's
value never matters, only whether it is zero. Each bitmask then stands for `9^a` real integers, and
that multiplicity has to come back at the counting stage. The second is **rewriting the move rule
until it is obviously simple**: 899's "remove the smaller pile's worth from both piles" turns out to
mean "split the larger pile freely, as long as one part fits under the smaller one". Every later
step depends on that rewrite.

### Finding the components

A position is a *sum* when it falls apart into pieces and every move lands in exactly one of them.
This is the property that unlocks the [Sprague–Grundy theorem](/blogs/technique/sprague-grundy-theorem).
Spotting it is a modelling skill, not a computation. Heaps are the obvious case (310). Less
obviously, a coin that may move along its row *or* its column is the sum of a row game and a column
game (649), so one coin is already two components. Subtrees hanging from one node of a tree are
independent games, and the
[colon principle](https://en.wikipedia.org/wiki/Hackenbush#Green_Hackenbush) turns "a stalk on top of
a subtree" into "the subtree's value plus one" (400).

When the move rule couples the parts, nothing decomposes and you should not pretend it does. In 899
a move's size is set by the *other* pile, so the pair is one indivisible position. In 711 and 961
there is only ever one shared object. For these games there is no XOR to take. You classify P- and
N-positions directly, and then look for the pattern.

### Pinning the question

The same game supports very different counts, and confusing them is a classic way to get a
plausible wrong answer.

- **Losing positions over a range** (899, 310). Count the P-positions, then mind the bookkeeping:
  sorted against ordered tuples, and the diagonal where entries coincide. 310 converts ordered heap
  triples into sorted ones with [Burnside's lemma](https://en.wikipedia.org/wiki/Burnside%27s_lemma).
  899 doubles its sorted count and subtracts the diagonal once.
- **Winning starts, weighted** (961). Classify each modelled position, then add up the real inputs
  it stands for.
- **Arrangements by outcome** (649). Only the *distribution* of component values matters, so the
  count becomes a histogram raised to a power under XOR-convolution, and the board size drops out
  entirely.
- **Winning moves** (400). This counts edges, not positions: the number of first moves that leave
  a total value of zero. It needs its own recurrence, one that tracks how many moves reach each
  target value, level by level.

## How to reason about it

**Model first, then brute-force the model.** Before looking for a formula, write the naive
win/lose search over your *modelled* position and check it against the statement's sample values.
If it disagrees, the model is wrong, and no amount of pattern-spotting downstream will fix that.
The solved problems here were all checked this way; in 961 the search over the modelled
position *is* the solution.

**Make the state small enough to sweep, and ordered.** A good encoding often gives you a free
topological order. In 961 removing a digit always produces a numerically smaller bitmask, so a
single forward pass over `[1, 2^D)` decides every position with no recursion. Where the encoding has
that property, prefer an array sweep over a memoized recursion.

**Expect the decisive structure to be arithmetic.** Once modelled, the P-positions of these games
have tended to depend on binary digits: the low bits of one pile against the bit length of the other
(899), isolated set bits at even positions (711), a Grundy sequence that is eventually periodic (the
`{2, 3, 5, 7}` subtraction game in 649). The game theory gets you to a clean table. Turning that
table into an `O(log n)` count is a separate, ordinary counting problem.

**Watch for multiplicity on the way back out.** Every simplification that merges inputs (forgetting
digit values, sorting piles, replacing coordinates with Grundy values) has to be undone exactly when
you count. The arithmetic for that is weights, symmetry factors and diagonals, and it is where most
off-by-a-factor errors in this domain come from.

<!-- problems (generated by update-tags) -->
## Problems

- ○ [0260](/solutions/0260/) — Stone Game
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ● [0310](/solutions/0310/) — Nim Square
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0391](/solutions/0391/) — Hopping Game
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0459](/solutions/0459/) — Flipping Game
- ○ [0488](/solutions/0488/) — Unbalanced Nim
- ○ [0550](/solutions/0550/) — Divisor Game
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ○ [0644](/solutions/0644/) — Squares on the Line
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0665](/solutions/0665/) — Proportionate Nim
- ● [0711](/solutions/0711/) — Binary Blackboard
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0859](/solutions/0859/) — Cookie Game
- ○ [0870](/solutions/0870/) — Stone Game IV
- ○ [0888](/solutions/0888/) — 1249 Nim
- ● [0899](/solutions/0899/) — DistribuNim I
- ○ [0900](/solutions/0900/) — DistribuNim II
- ○ [0933](/solutions/0933/) — Paper Cutting
- ○ [0939](/solutions/0939/) — Partisan Nim
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ● [0961](/solutions/0961/) — Removing Digits

<!-- /problems -->
