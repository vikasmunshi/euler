<!-- tags: [partizan-game] -->
<!-- status: final -->
# Partizan game

A [partizan game](https://en.wikipedia.org/wiki/Partizan_game) is a two-player game of perfect
information in which the players have *different* moves from the same position. One player may
delete a $1$ and the other a $0$, or one cuts blue edges and the other red. That one difference
removes the main shortcut of the
[impartial](/topics/domain/impartial-game) theory, the Nim heap. In its place comes a richer
algebra of game values, where one component can be worth $\tfrac12$, $-3$, $*$ or $\uparrow$. The
problems below are all sums of many small games: stacks of coins, or numbers whose digits are
deleted one at a time. Each asks a question that no search could answer at full size: how many
starting arrangements are exactly balanced, or how many free passes one player needs. The work is
to translate the question into a statement about game values, and then make those values cheap.

## The idea: Left, Right, and four outcomes

The convention of [combinatorial game theory](/topics/domain/combinatorial-game-theory) names the
players **Left** and **Right**. It writes a position as $G = \{G^L \mid G^R\}$, the positions each
can move to. Under [normal play](https://en.wikipedia.org/wiki/Normal_play_convention) (no move,
you lose) an impartial position is either a first-player or a second-player win. A partizan
position falls into one of **four** outcome classes, because who moves first now matters
separately for each player:

| Class | Left moving first | Left moving second | Value |
|---|---|---|---|
| $\mathcal{L}$ | wins | wins | $G > 0$ |
| $\mathcal{R}$ | loses | loses | $G < 0$ |
| $\mathcal{P}$ | loses | wins | $G = 0$ |
| $\mathcal{N}$ | wins | loses | $G \parallel 0$ (fuzzy) |

So the brute force for a partizan game has to carry the mover as part of the state. It is still
[backward induction](/topics/technique/backward-induction), with an `any` for the player who chooses
and an `all` for the one who must survive every reply:

```python
@cache
def left_wins(pos, left_to_move):         # normal play: the player who cannot move loses
    if left_to_move:
        return any(left_wins(p, False) for p in left_options(pos))
    return all(left_wins(p, True) for p in right_options(pos))
```

Two rules let the algebra do the work that search cannot:

- **Sums.** When a move changes exactly one component, the position is the
  [disjunctive sum](https://en.wikipedia.org/wiki/Disjunctive_sum) of its components. Its value is
  the sum of the component values, and the outcome class of the sum follows from that value.
- **Negation and comparison.** Swapping the roles of Left and Right turns $G$ into $-G$. Then
  $G = H$ exactly when $G - H$ is a second-player win, and $G \ge H$ exactly when Left wins
  $G - H$ moving second. Equality of games is defined *by playing*. That is also how you test it.

Why the impartial shortcut fails: the
[Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem) relies on
every position being its own negative ($G + G = 0$), which is what makes Nim-sums an XOR. In a
partizan game $G + G$ is usually not zero, since two copies of a Left advantage are a bigger Left
advantage. So values have to live in a partially ordered group, not in the nim-numbers.

## How the problems use it

All three problems reach the values by the same route. The position is a sum over independent
pieces, so the board's value is a sum of piece values. Each piece value comes from its own small
recursion, because every move shrinks one piece. What differs is *what kind* of value turns up, and
so what question the sum can answer.

- **Problem 860** is the cleanest case. Two players remove gold or silver coins from stacks of two,
  taking everything above the chosen coin. That is
  [blue-red Hackenbush](/topics/domain/hackenbush) on stalks, and every stalk is a
  surreal number. There are only four stacks, so their values can be worked by hand. Two of a
  colour are worth $\pm 2$. A gold coin under a silver one gives Gary one move, which empties the
  stack, and gives Sally one move, which leaves a lone gold coin worth $1$: the value is
  $\{0 \mid 1\} = \tfrac12$, and the reverse stack is $-\tfrac12$. "Fair" means whoever moves
  first loses, which is value $0$. So the game disappears, and what is left is a count of ordered
  sequences of $\pm 2, \pm\tfrac12$ that sum to zero. That count is the constant term of a power
  of a four-term [generating function](/topics/domain/generating-function), and that Laurent
  polynomial happens to factor, which collapses the count to a single sum of binomial products.
  The game theory does one paragraph of work, and the rest is combinatorics, a clear case of
  [reducing before coding](/topics/takeaway/reduce-before-coding).
- **Problem 882** asks how many passes Right needs to win. A pass is a free move for Right, so
  $k$ passes add the integer game $-k$. The question becomes the smallest $k$ that makes the total
  a Right win with Left to move. That is a sign condition on $V - k$. It is tractable only because
  every component turns out to be a [surreal number](/topics/domain/surreal-number), so $V$ is an
  ordinary dyadic rational.
- **Problem 963** asks how many starting settings are *fair*: the player to move loses, so the
  value is $0$. Each player holds two numbers, and a number on the opponent's paper is the same
  game with the roles swapped, so the setting's value is $G(a_1) + G(a_2) - G(b_1) - G(b_2)$.
  Fairness is then an *equality of pair sums*, and the count becomes a collision count over a
  table of values. It is 860's question again, but over a far larger table of values. The catch is that one digit can be
  removed by either player. That shared move produces infinitesimals such as
  [star](https://en.wikipedia.org/wiki/Star_(game_theory)) and
  [up](https://en.wikipedia.org/wiki/Up_(game_theory)), so values are no longer plain numbers.
  Before equality could be tested cheaply, every value had to be put in a
  [canonical form](/topics/technique/canonical-form) and then written as a short integer vector.

## How to reason about it

- **Label Left and Right before anything else, and record who moves first.** Most mistakes here
  are an off-by-one between "Left moving first wins" ($G > 0$ or $G \parallel 0$) and "the player
  to move loses" ($G = 0$). Write the problem's question as a condition on the value, and check
  it against the statement's examples.
- **Look for the sum.** If each move touches exactly one part of the position, you never need the
  joint state. Compute one component's value, then add. A board of thousands of numbers turns
  into one table plus one sum.
- **"Fair" means zero, and zero turns a game into a count.** Once each piece has a value, "the
  first player loses whoever it is" is a sum equal to $0$. Counting such positions is counting
  zero-sum sequences (860) or colliding pair sums (963). Both are combinatorics problems with no
  game left in them.
- **Use negation for mirrored roles.** A component that belongs to the other player, or where the
  colours are swapped, is the same game negated. In 963 that is why the opponent's numbers enter
  with a minus sign. It also reuses 882's table with the colours swapped.
- **Expect numbers when moves are private, and trouble when they are shared.** If each move uses
  up something only the mover owns, values tend to be numbers and nobody wants to move. That is
  why 860 and 882 stay inside the surreals. A move
  either player can make is where $*$, $\uparrow$ and hot games come from.
- **Build a small engine before you build on a pattern.** Exact values with a few lines of
  [`Fraction`](https://docs.python.org/3/library/fractions.html) code, or a canonical-form engine
  that deletes dominated options and bypasses reversible ones, are the ground truth. Check every
  closed form against them, and against the statement's examples, before you scale it. That's the
  habit of [calibrating theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers).

For the theory in full, Berlekamp, Conway and Guy's
[*Winning Ways*](https://en.wikipedia.org/wiki/Winning_Ways_for_Your_Mathematical_Plays) is the
classic. Siegel's *Combinatorial Game Theory* covers canonical forms, infinitesimals and
temperature rigorously.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
