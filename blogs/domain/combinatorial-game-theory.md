<!-- tags: [combinatorial-game-theory] -->
<!-- status: final 2026-11-09T12:31Z -->
# Combinatorial game theory

[Combinatorial game theory](https://en.wikipedia.org/wiki/Combinatorial_game_theory) studies
two-player games of **perfect information and no chance**: both players see the whole position,
moves alternate, play is finite, and under the usual
[normal play convention](https://en.wikipedia.org/wiki/Normal_play_convention) the player who
cannot move loses. That is narrow enough to be a real theory — every position is a win or a loss
for whoever is to move, decided before a single stone is lifted — and broad enough to cover the
nearly seventy problems below, which arrive dressed as Nim, stone games, coin games, strip games,
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

That is [backward induction](/blogs/technique/backward-induction) over the game graph, and it is
five lines of code:

```python
def wins(position):                       # True iff the player to move wins
    moves = list(successors(position))
    if not moves:                         # normal play: no move, you lose
        return False
    return any(not wins(m) for m in moves)
```

Written with [memoization](/blogs/technique/memoization) over a canonical encoding of the
position, this is the brute force you should write *first* for any of these problems — not because
it will reach the required size (it never does), but because it is the ground truth against which
you check the pattern you are about to conjecture. Several of the solved problems here keep exactly
such a script beside the fast solution — 301 and 899 an outcome search, 882 an exact-`Fraction`
value table, 963 a canonical-form engine that reproduces the statement's $F(5) = 21$ before any
closed form is trusted (see [calibrate theory on known answers](/blogs/takeaway/calibrate-theory-on-known-answers)).

## Sums of games: mex, Grundy values, and Nim

The reason this domain has a theory rather than a pile of case analyses is that most of these games
decompose. A position is often a **disjunctive sum** of independent components — several heaps,
several strips, several coins — and a move touches exactly one of them. For
[impartial games](/blogs/domain/impartial-game) (both players have the same moves available), the
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

Two ideas are doing all the work. The [mex](/blogs/domain/mex-function-set-theory) (minimum
excludant) is what makes a value out of a move set, and the exclusive-or is
[nimber](/blogs/domain/nimber) addition — the arithmetic of the theory. Ordinary three-heap Nim is
the degenerate case where `grundy(heap) == heap`, so a position is lost exactly when the heap sizes
XOR to zero; that single fact is the whole of problem 301, which asks how many $n$ make
$(n, 2n, 3n)$ a loss and thereby turns a game into a question about the binary digits of $n$.

Once you hold this, a large family of the problems below is one template: **compute the Grundy
value of a single heap under the variant's move rule, then XOR**. The variants change only the move
rule — remove a square number (310), a proper divisor (509), an amount coprime to the heap (560),
one of a fixed set or a split (888), split into at most $k$ parts (629). The difficulty moves
entirely into the *arithmetic of the Grundy sequence*: it is
usually eventually periodic, or determined by a heap's factorisation or its bit pattern, and finding
that structure — then proving it on a brute-force table — is the problem.

The same template covers games that do not look like heaps at all. Gaps between coins on a strip
are heaps (344, the silver dollar game). A token that may move in either of two directions is
itself the sum of two one-dimensional games, so its value is the XOR of a row value and a column
value (649). Coin-turning games — flip a rectangle of disks subject to a shape rule (459) — are
sums of one-coin games, and the two-dimensional ones are governed by nim-*multiplication*. The
skill being trained is seeing the independent parts.

Trees are the case worth singling out. In 400, removing a node and its subtree is cutting an edge in
[Green Hackenbush](https://en.wikipedia.org/wiki/Hackenbush), and the subtrees hanging from one
node are independent games. The *colon principle* says an edge with a subtree of value $v$ on top
is worth $v + 1$, so a node's value is the XOR over its children of (child value $+ 1$). For the
Fibonacci tree that is a one-line recurrence on the level. 400 also asks a different question from
"who wins": it asks *how many winning first moves* there are, in a tree with more than two thousand
digits' worth of nodes. A winning move is one that leaves the whole tree at value $0$, and that
target can be pushed down. If the root must end at $t$, a move in one child must leave that child
at the value that XORs with its sibling's to give $t$. So you count moves by *(level, target value)*
rather than by node. Because the Grundy values stay small, the table is level count × a few thousand
targets, and since XOR with a constant permutes the targets, each level is a gather with no
collisions.

## When the decomposition fails

Plenty of these problems refuse the Grundy template, and reaching for XOR anyway is the classic way
to get a confidently wrong answer. Three situations to recognise:

**One indivisible position.** When a move's legality depends on the *other* components — remove a
multiple of the smaller pile (325), take the smallest pile's worth spread across piles (899, 900),
remove $c$ and $d$ with $ad - bc = \pm 1$ (787), the "at most twice the previous move" rule of
Fibonacci nim (366, 692) — there are no independent parts and no Grundy value to compute. What you
look for instead is a direct characterisation of the whole $\mathcal{P}$-position set, and it is
almost always something startlingly clean: a condition on the low bits of one pile relative to the
bit length of the other (899), a [Beatty](https://en.wikipedia.org/wiki/Beatty_sequence)-like pair
of sequences in the style of [Wythoff's game](https://en.wikipedia.org/wiki/Wythoff%27s_game) (665),
a [Zeckendorf representation](/blogs/domain/zeckendorfs-theorem) (692), a
[continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) expansion (787). Generate the
losing positions with the brute force, stare at them in binary and in their factorisations, and
conjecture.

Before you stare, shrink the state. In 711 (Binary Blackboard) the players write numbers whose sum
is capped by the first one, and a win depends on the parity of the total count of 1 bits. The
history looks unbounded, but only two quantities ever affect the future: the budget left and
whether the parity currently suits the player to move. That pair makes the brute force quadratic
instead of exponential, which is enough to tabulate a thousand starting numbers. The table shows
that the first player's winning starts form two rigid binary families: the all-ones numbers, and
numbers built from isolated 1 bits at even positions with an optional even-length tail of ones.
The bound is $2^{12\,345\,678}$, so the count cannot be a walk over the family either. It becomes a
sum of geometric and arithmetico-geometric series, and the work grows only with the *bit length* of
the bound.

**Partisan games.** If the two players have *different* moves — Left removes from the left, Right
from the right (948, 949); one player deletes gold coins, the other silver (860, 895); a player may
only strip their own piles (939); X and O place different symbols (976); one player slides a counter right, the other down (922); Dr. One deletes a binary
1 while Dr. Zero deletes a 0 (882) — Sprague–Grundy does not apply. These are
[partizan games](/blogs/domain/partizan-game), and a position must be classified by *four*
outcomes (Left wins whoever starts, Right wins whoever starts, first player wins, second player
wins). The recurring Euler phrasing "whoever plays first loses" or "the arrangement is fair" is
precisely the fourth outcome — a game of value zero. Note what fails here is the *nimber*, not the
sum: a partisan position can still be a disjunctive sum, and then it has a theory of its own (next
section).

**Misère play.** When the player taking the last stone *loses*, the normal-play Grundy machinery
breaks; misère Nim has a famous patch, but misère variants in general do not, and you must redo the
induction with the terminal condition flipped rather than adjust the answer at the end.

## Partisan sums: numbers, infinitesimals, and value zero

If each move still touches one component but the players differ, Conway's theory replaces the
nimber with a general game value $G = \{\,\text{Left's options} \mid \text{Right's options}\,\}$, and
the value of a sum is still the sum of the values. What changes is the arithmetic those values live
in, and five problems show the range of it.

The gentlest entry is 860, the gold-and-silver coin game. Taking a coin removes everything stacked
above it, which is exactly cutting an edge of a stalk in
[blue-red Hackenbush](https://en.wikipedia.org/wiki/Hackenbush): every stack is a number, and the
four stacks of height two are worth $\text{GG} = 2$, $\text{SS} = -2$, $\text{GS} = \{0 \mid 1\} =
\tfrac12$ and $\text{SG} = -\tfrac12$. "Fair" is value zero, so counting fair arrangements of $n$
stacks is counting ordered sequences of $n$ steps from $\{\pm 4, \pm 1\}$ (in half-units) that sum
to zero — the constant term of $(x^4 + x + x^{-1} + x^{-4})^n$. The game theory ends there, in one
paragraph; the rest is noticing that $x^8 + x^5 + x^3 + 1 = (1 + x^3)(1 + x^5)$, which turns a
double sum of multinomials into a single sum of products of two binomials. It is the cleanest
example in the archive of a partisan sum reducing, in two moves, to a
[generating function](https://en.wikipedia.org/wiki/Generating_function) coefficient.

In 882 each integer on the board is a component — Left deletes a 1 from its binary string, Right a
0 — and every component turns out to be a [surreal number](/blogs/domain/surreal-number), in fact a
dyadic rational: $\{0 \mid\,\} = 1$, $\{0 \mid 1\} = \tfrac12$, $\{1 \mid\,\} = 2$. Whenever Left's
best option lies below Right's, Conway's *simplicity rule* says the value is the simplest dyadic
strictly between them, so one bottom-up table over the integers values every component from just
its two best options, and the whole board is a single rational $V$. Numbers make the rest of the
problem arithmetic. A skip turn is a free move for Right, i.e. the integer game $-1$, so $k$ skips
add $-k$; Left moves first and Right wins exactly when $V - k \le 0$, which makes the minimal number
of skips $\lceil V \rceil$ — no search over the board at all. Because the denominators are powers of
two bounded by the bit length, the values can be held as integers scaled by $2^B$, and the simplest
number between $\ell$ and $r$ is a bit-clearing trick rather than a loop.

Problem 963 plays the same game in ternary, with one change: a digit 2 may be deleted by *either*
player. That single shared move is enough to break the numbers. The values pick up
[infinitesimals](https://en.wikipedia.org/wiki/Infinitesimal) — star $* = \{0 \mid 0\}$, up
$\uparrow = \{0 \mid *\}$ and a tower of smaller ones — which are neither positive, negative nor zero
in the way a number is, so a value can no longer be stored as a fraction and compared with `<`.
Two structural facts still carry the problem. Exchanging the players' roles is game *negation*, so a
setting $(a_1, a_2 \mid b_1, b_2)$ has value $G(a_1) + G(a_2) - G(b_1) - G(b_2)$, "fair" means that
value is zero, and the count of fair settings is $\sum_v M(v)^2$ over the multiplicities $M(v)$ of
each pair sum. And equality of games is decidable through their
[canonical form](/blogs/technique/canonical-form): delete dominated options, bypass reversible
ones, and equal games become the same object. A small canonical-form engine is the honest brute
force here; its output showed every value is a number plus an infinitesimal, which could then be
written as a vector of coefficients over independent infinitesimals — with the number part read off
882's table for the string with the 2s deleted. Once values are vectors, game equality is vector
equality and game addition is vector addition, and the count is ordinary bucketing.

Problem 922 (Young's Game A) lands between 882 and 963. The same kind of canonical-form engine, run
on every small staircase diagram, showed each one is worth an integer plus a nimber,
$(b - a) + {*}(k - 1)$. The width surplus counts free moves, and the $k$ steps act as a Nim heap,
so impartial values turn up inside a partisan game. A sum of such values is $N + {*}X$, with $N$ added as an integer and $X$ combined by XOR.
Its outcome comes from a short sign rule: positive or negative by the sign of $N$, and when $N = 0$,
zero if $X = 0$ and fuzzy (a first-player win) otherwise. So the value lives on two axes with two
different additions, and the counting step later has to respect both.

Problem 976 (XO Game) shows a different payoff from knowing the values. After an opening phase the
board breaks into gaps between marks. Their values are numbers or numbers plus $*$, and the
opening move on a strip is worth $0$, $*$ or $\pm 2^{1 - n/2}$ depending on the strip's length mod 4.
Odd strips are free tempo moves. Even strips cost whoever opens them a *power of two*. Powers of two
behave like binary digits, so the largest weight left unmatched decides the sign of the total, and
that weight falls on whoever makes the last forced opening. The only escape is when every even
length occurs an even number of times and the weights cancel. A sum of game values thus becomes a
parity rule on the multiset of strip lengths, and the count becomes a
[generating function](/blogs/domain/generating-function) over multisets.

The lesson across the five: in a partisan sum, first find out *what kind of value* the components
take. Numbers give you a total order and plain arithmetic. Number-plus-nimber values give you a
sign rule over two axes. Values that are powers of two let the largest one decide. Anything hotter
or fuzzier needs a canonical representation before you can even test equality, let alone count.
In every case the values were *found* by a small exact engine and only then proved or tested,
never guessed.

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
  [dynamic programming](/blogs/technique/dynamic-programming) search for a strategy that meets it.
- **Pursuit and economics.** Catching a mouse on a graph (690, 825, 761) is a fixed-point
  computation over the set of positions still consistent with the search so far; the pirates of 950
  are pure backward induction from the last surviving proposer.
- **Solitaires and invariants.** Single-player token games (426, 664) are usually settled by a
  **weight function**: assign each square a value so that no move can increase the total, and the
  invariant caps what is reachable; then exhibit a construction that attains the cap. 986 shows
  the other route: stop tracking tokens and count *moves per square*. Conservation then becomes a
  system of linear inequalities on those counts, and in it each count helps exactly one constraint.
  So the cheapest plan is forced square by square, as a floored-average
  [recurrence](https://en.wikipedia.org/wiki/Recurrence_relation). Feasibility is
  [monotone](/blogs/technique/monotonic-function) in the target, which makes the best reachable pile a
  [binary search](/blogs/technique/binary-search-algorithm) over whether that recurrence dies out.

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
   $O(\text{bits})$ rather than $O(n^k)$ — that is the shape of 409, 560 and 888. With partisan
   values the same step is a sum or a multiplicity count over values: a rounded-up total (882),
   the zero coefficient of a power of the per-stack value polynomial (860), or the number of
   equal pair sums (963), which is cheap because only a few thousand distinct
   values occur among $10^5$ components.

Three refinements of stage 3 recur often enough to name:

- **Count over values, not positions.** Grundy values are tiny next to the range: in 310 the
  largest value among $10^5$ heaps is 74. A histogram over a 128-value alphabet turns the triple
  count into an XOR self-convolution of that histogram. When the statement wants *unordered* heaps
  ($a \le b \le c$), count ordered triples and divide out the symmetry exactly with
  [Burnside's lemma](/blogs/technique/burnside-lemma). The losing condition is symmetric, and
  the fixed points of a transposition are triples with two equal heaps, which lose exactly when the
  third has value zero. That avoids a case split on which heaps coincide.
- **Powers of a histogram, and the modulus.** Placing $c$ independent tokens (649) is the $c$-fold
  XOR-convolution power of one token's histogram. Raise it by
  [exponentiation by squaring](/blogs/technique/exponentiation-by-squaring), and the cost no longer
  depends on the board size. The [Walsh–Hadamard transform](/blogs/technique/walsh-hadamard-transform)
  is the usual accelerator, but its inverse divides by the transform length. Modulo $10^9$ the length
  8 has no inverse, so the direct $8 \times 8$ convolution is the correct choice there, not merely
  the simple one.
- **Mixed axes.** When values are integer-plus-nimber (922), a tuple's $(N, X)$ combines by ordinary
  convolution in $N$ and XOR convolution in $X$. Transform only the nimber axis. Each Walsh index
  then carries an ordinary polynomial in $N$, raised to the $m$-th power. You also need only one
  point of the inverse transform, $X = 0$, so you never invert the whole thing.

The closed forms at the end vary as much as the games. 711 ends in geometric and
arithmetico-geometric series. 976 ends in multiset generating functions whose coefficients satisfy an
order-two [holonomic](https://en.wikipedia.org/wiki/Holonomic_function) recurrence, so $10^7$
terms take one division-free linear pass.

Problem 961 is a compact illustration of the whole arc: the game is played on the decimal digits of
an integer, but only the pattern of zero and non-zero slots matters, so a position is a small
bitmask, the induction runs bottom-up over all masks, and the count of winning integers follows by
weighting each winning mask by how many integers wear it.

## How to reason about it

- **Write the honest brute force first, and keep it.** Every pattern you will conjecture is a
  pattern in its output, and it is the only check you have that the fast version is right.
- **Ask whether the position is a sum.** If a move touches exactly one independent component, compute
  Grundy values and XOR — or, for a partisan game, Conway values and add. If a move's legality
  depends on the other components, do neither — characterise the whole position instead.
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
- ● [0310](/solutions/0310/) — Nim Square
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0367](/solutions/0367/) — Bozo Sort
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
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
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0661](/solutions/0661/) — A Long Chess Match
- ○ [0664](/solutions/0664/) — An Infinite Game
- ○ [0665](/solutions/0665/) — Proportionate Nim
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0683](/solutions/0683/) — The Chase II
- ○ [0690](/solutions/0690/) — Tom and Jerry
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0711](/solutions/0711/) — Binary Blackboard
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0770](/solutions/0770/) — Delphi Flip
- ● [0787](/solutions/0787/) — Bézout's Game
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0847](/solutions/0847/) — Jack's Bean
- ○ [0848](/solutions/0848/) — Guessing with Sets
- ○ [0855](/solutions/0855/) — Delphi Paper
- ○ [0859](/solutions/0859/) — Cookie Game
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0870](/solutions/0870/) — Stone Game IV
- ● [0882](/solutions/0882/) — Removing Bits
- ○ [0888](/solutions/0888/) — 1249 Nim
- ○ [0895](/solutions/0895/) — Gold & Silver Coin Game II
- ● [0899](/solutions/0899/) — DistribuNim I
- ○ [0900](/solutions/0900/) — DistribuNim II
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0923](/solutions/0923/) — Young's Game B
- ○ [0933](/solutions/0933/) — Paper Cutting
- ● [0939](/solutions/0939/) — Partisan Nim
- ○ [0948](/solutions/0948/) — Left vs Right
- ● [0949](/solutions/0949/) — Left vs Right II
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ● [0961](/solutions/0961/) — Removing Digits
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0976](/solutions/0976/) — XO Game
- ○ [0982](/solutions/0982/) — The Third Dice
- ● [0986](/solutions/0986/) — Another Infinite Game
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
