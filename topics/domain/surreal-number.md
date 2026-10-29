<!-- tags: [surreal-number] -->
<!-- status: final -->
# Surreal number

[Surreal numbers](https://en.wikipedia.org/wiki/Surreal_number) are John Conway's numbers built
out of games. A game is written $\{L \mid R\}$: the positions Left can move to, then the positions
Right can move to. Some games turn out to *be* numbers, such as $1$, $\tfrac12$ or $-\tfrac38$, in
a precise sense. A sum of such games is decided by the sign of a rational, so you don't have to
search a game tree at all. That is why the idea keeps coming back in the
[partizan](/topics/domain/partizan-game) problems below. Each one hides a small game in a stack of
coins or in the digits of an integer, then asks about a sum of thousands of copies. Once I could
show the components were numbers, the game question became ordinary arithmetic, and often ordinary
counting.

## The idea: a game whose options are ordered is a number

For [impartial games](/topics/domain/impartial-game) both players have the same moves, and the
[Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem) reduces
every component to a Nim heap. A [partizan game](https://en.wikipedia.org/wiki/Partizan_game)
gives the players different moves, so that reduction fails, and
[combinatorial game theory](/topics/domain/combinatorial-game-theory) has to work with the game
values $\{L \mid R\}$ themselves. Four facts carry almost all the weight:

- **Outcome is a sign.** If $G > 0$ Left wins whoever starts, and if $G < 0$ Right does. If
  $G = 0$ the player to move loses. A fourth case, $G \parallel 0$ ("fuzzy"), means the player to
  move wins, and it never happens when $G$ is a number.
- **Values add.** When a move changes exactly one component, the position is the
  [disjunctive sum](https://en.wikipedia.org/wiki/Disjunctive_sum) of its components, and its
  value is the sum of their values. Swapping the roles of Left and Right negates a game.
- **When a game is a number.** If every option is a number and every Left option is strictly
  less than every Right option, then $\{L \mid R\}$ is a number. It is the **simplest** number
  strictly between $\max L$ and $\min R$. "Simplest" means an integer of least absolute value if
  one fits. Failing that, it is the
  [dyadic rational](https://en.wikipedia.org/wiki/Dyadic_rational) with the smallest power-of-two
  denominator. This is Conway's *simplicity rule*.
- **Finite games give dyadic numbers.** When a game that always ends in finitely many moves is a
  number, that number is a fraction $p / 2^k$. You never need $\tfrac13$, and $k$ is bounded
  by the depth of the game.

Then the definitions of $0$, $1$ and $\tfrac12$ stop looking mysterious:
$\{\,\mid\,\} = 0$ (nobody can move), $\{0 \mid\,\} = 1$ (Left has one free move in hand), and
$\{0 \mid 1\} = \tfrac12$. The last one is the simplest number between $0$ and $1$.
[Blue-Red Hackenbush](https://en.wikipedia.org/wiki/Hackenbush) is the textbook picture. A
pure-blue stalk of length $n$ is worth $n$, and a red edge on top of a blue one is worth
$\tfrac12$.

The simplicity rule is short enough to write once with exact
[`Fraction`](https://docs.python.org/3/library/fractions.html) arithmetic and reuse in every
exploration script:

```python
def simplest(l, r):                       # l < r; None means that side has no option
    if (l is None or l < 0) and (r is None or r > 0):
        return Fraction(0)
    if r is not None and r <= 0:          # mirror the negative case onto the positive one
        return -simplest(-r, None if l is None else -l)
    n = floor(l) + 1                      # the least integer above l
    if r is None or n < r:
        return Fraction(n)
    d = 1
    while True:                           # otherwise the smallest power-of-two denominator wins
        d *= 2
        k = floor(l * d) + 1
        if Fraction(k, d) < r:
            return Fraction(k, d)
```

## How the problems use it

**Problem 860 is Hackenbush with the labels changed.** Gold and silver coins sit in stacks. Each
player takes a coin of their own metal, and everything above it goes too. That is a Blue-Red
[Hackenbush](/topics/domain/hackenbush) stalk, coin for edge. The stacks all have height two, so there are only four
components, and their values can be worked out by hand: a single-colour pair is worth $\pm 2$, and
a mixed pair is worth $\pm\tfrac12$, the textbook $\{0 \mid 1\}$. "Fair" in the statement means
the first player loses whoever it is, which is exactly $G = 0$. So the game theory is over in a
paragraph, and what remains is a counting question: how many ordered sequences of $n$ steps drawn
from $\{\pm 2, \pm\tfrac12\}$ sum to zero? In half-units that is the constant term of
$(x^4 + x + x^{-1} + x^{-4})^n$, a [generating function](/topics/domain/generating-function).
That Laurent polynomial happens to factor into two binomials, so the constant term collapses to a
single sum of products of [binomial coefficients](/topics/domain/binomial-coefficient), linear in
$n$. The surreal value is the bridge: it turns "who wins" into "does this sum vanish", and sums
are what generating functions count.

The other two problems are digit-deletion games. Each player may remove certain digits from a number's
expansion, and a whole position is a multiset of such numbers. That has the right shape for this
theory. Each move touches one number, so the position is a disjunctive sum. Every move also
shortens a number by one digit, so a single number's value is a
[dynamic program](/topics/technique/dynamic-programming) over shorter numbers, filled in bottom
up.

**Problem 882 is the clean case.** One player deletes a binary $1$ and the other deletes a binary
$0$. Every position I checked had $\max L < \min R$, so every component is a number. In the
statement's notation, the small values come out as $G(1) = 1$, $G(2) = \tfrac12$, $G(3) = 2$ and
$G(5) = \tfrac32$. The board is then just a rational. The "skip a turn" allowance is an integer
game for the other player, so the problem's minimum becomes a rounding of that rational. Two
engineering points recur:

- **Fixed point instead of fractions.** The value of a number with $b$ binary digits has a
  denominator of at most $2^{b-1}$. So I scale every value by $2^B$ once, where $B$ bounds
  the length, and the value stays an exact integer. Comparison and addition become machine operations. This is
  [exact arithmetic](/topics/takeaway/exact-arithmetic-for-equality) without the cost of
  `Fraction`.
- **The simplicity rule as a bit trick.** In scaled form, the simplest dyadic in $(\ell, r)$ is
  found by clearing the low bits of $r - 1$ below the highest bit where it differs from $\ell$.
  That's [bit manipulation](/topics/technique/bit-manipulation) in place of a loop over
  denominators. Summed over $10^5$ or $10^6$ weighted components, the scaled total can outgrow
  64 bits, which is why the C ports reach for [`__int128`](/topics/technique/int128).

**Problem 963 is where the hypothesis breaks.** It works in base three. One digit can be removed
by *either* player, and a shared move is exactly what produces games that are not numbers:
[star](https://en.wikipedia.org/wiki/Star_(game_theory)) $* = \{0 \mid 0\}$,
[up](https://en.wikipedia.org/wiki/Up_(game_theory)) $\uparrow = \{0 \mid *\}$, and a tower of ever
smaller [infinitesimals](https://en.wikipedia.org/wiki/Infinitesimal) beneath them. The surreal
part survives, though. With the shared digit struck out, what is left is Problem 882's game with
the colours swapped. Every value split as *a number plus an infinitesimal tail*, and the number
part came straight from 882's table. Fairness then means two sums of values are equal. Because
the infinitesimals are independent, that becomes equality of small integer vectors, and I could
count it with grouped tallies.

## How to reason about it

- **Suspect numbers when moving only costs you.** In a number, nobody wants to move: every move
  makes your own position worse. Games where each player spends a resource that belongs only to
  them tend to be numbers. Examples are deleting your own colour of digit, or cutting your own
  colour of edge. A move both players can make (963's shared digit, a green edge in Hackenbush)
  is the warning sign for $*$ and other infinitesimals.
- **Prove the hypothesis on small cases before you build on it.** Compute exact values with
  `Fraction` and assert $\max L < \min R$ at every node. Then check the resulting outcomes against
  every example in the statement. That's the habit of
  [calibrating theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers). For
  860 a memoised brute force over every arrangement up to $n = 7$ matched the closed sum. For
  882 it was a few lines. For 963 it took a small
  [canonical-form](/topics/technique/canonical-form) engine, one that deletes dominated options
  and bypasses reversible ones, before the structure was visible.
- **Counting fair positions is counting zero sums.** Once every component is a number, "the
  player to move loses" is $\sum G_i = 0$. If the component values come from a small set, the
  count is a constant term of a generating function, as in 860. Look for a factorisation before
  you write a DP over the running total.
- **Keep only the extreme options.** The simplicity rule depends only on Left's best option and
  Right's best option. So the DP stores two values per node, never the option sets.
- **Read the outcome rule carefully.** "Left moves first and wins" means $G > 0$ *or*
  $G \parallel 0$. With numbers, fuzziness can't happen, so it reduces to $G > 0$. Equality, the
  first-player-loses case, means $G = 0$ exactly. This is the off-by-one that decides whether an
  answer is a floor, a ceiling, or a ceiling plus one.

For depth, Conway's *On Numbers and Games* and Berlekamp, Conway and Guy's
[*Winning Ways*](https://en.wikipedia.org/wiki/Winning_Ways_for_Your_Mathematical_Plays) are the
sources. Siegel's *Combinatorial Game Theory* is the modern treatment of canonical forms and
infinitesimals.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
