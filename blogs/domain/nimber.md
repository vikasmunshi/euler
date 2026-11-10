<!-- tags: [nimber] -->
<!-- status: final 2026-11-10T23:25Z -->
# Nimber

A [nimber](https://en.wikipedia.org/wiki/Nimber) `*n` is the value of a single Nim heap of size
`n`. The [Sprague–Grundy theorem](../technique/sprague-grundy-theorem.md) says that every position
of an [impartial game](impartial-game.md) is *equal* to one of them. Equal here means that one can
replace the other inside any sum of games without changing who wins. Nimbers also have their own
arithmetic: adding two of them is the bitwise XOR of the indices, and every nimber is its own
negative (`*n + *n = 0`). The six solved problems below never search a game tree. Each one moves
from positions to nimbers once, and the rest of the work is arithmetic on small integers. This
page is about that step: what the nimber is in each problem, and what replacing positions with
nimbers saves. The companion page
[impartial games and nim-values](../game-theory/impartial-games-and-nim-values.md) covers how to
compute Grundy tables in general. Here the nimber is treated as a number to compute with.

## The idea

Two facts carry all of it.

1. **Equivalence.** A position is lost for the player to move exactly when its nimber is `*0`. A
   position worth `*n` can move to every smaller nimber and never to `*n` itself, which is the
   [mex](mex-function-set-theory.md) rule.
2. **Addition is XOR.** In a [disjunctive sum](../technique/disjunctive-game-sum.md), each move
   touches exactly one component. The sum's nimber is the XOR of the components' nimbers.

Together these change the shape of the problem. A position is a large object: a tuple of heaps, a
tree, a board of coins, a set of rectangles. Its nimber is a small integer, and in every problem
here it turns out to be *very* small: 7 bits, 3 bits, 13 bits. "Lose" and "winning move" also
become arithmetic conditions:

| question | condition on nimbers |
|---|---|
| is this sum lost for the mover? | `g₁ ⊕ g₂ ⊕ … ⊕ gₖ = 0` |
| is this move winning? | it changes one component from `gᵢ` to `gᵢ'` with `gᵢ' = gᵢ ⊕ X`, where `X` is the current total |
| how many positions of a family are lost? | count tuples over a *histogram of values*, not over positions |

The last row matters most. Once each component is replaced by its nimber, the count of positions
depends only on how many components carry each value. Counting sums then becomes an
[XOR convolution](../technique/walsh-hadamard-transform.md) of value histograms:

```python
def xor_convolve(p: list[int], q: list[int]) -> list[int]:   # len a power of two
    r = [0] * len(p)
    for x, px in enumerate(p):
        for y, qy in enumerate(q):
            r[x ^ y] += px * qy
    return r
```

Its cost depends on the width of the value alphabet, not on how many positions there are.

## What the reduction buys, problem by problem

**301 (Nim).** This is the theorem in its oldest form, Bouton's rule for Nim, where heap `n` is
worth `*n` and the question asks when `n ⊕ 2n ⊕ 3n = 0`. Nim addition is
ordinary addition without carries, and `n + 2n = 3n`. So the XOR vanishes exactly when adding `n`
and `2n` produces no carry, which means `n & 2n = 0`: `n` has no two adjacent set bits. Those are
the [fibbinary numbers](fibbinary-numbers.md), and a [digit DP](../technique/digit-dp.md) counts
them in `O(log N)`. No game is ever played. The nimber's definition as XOR already answers the
question.

**310 (Nim Square).** Three heaps where a move removes a square number of stones. The one-heap
nimbers need a real mex computation, about `√N` options per heap. Below `10⁵` the values stay
under 128, so they fit in 7 bits. Counting losing triples `g(a) ⊕ g(b) ⊕ g(c) = 0` is then a
single XOR self-convolution of a 128-entry histogram, about 16 000 products in place of `N³`
triples. [Burnside's lemma](../technique/burnside-lemma.md) converts the ordered count into the
sorted triples the problem asks for. Burnside works here because XOR treats the heaps
symmetrically, and `*a + *a = 0` makes the fixed-point terms easy to compute.

**400 (Fibonacci Tree Game).** Removing a subtree is
[Green Hackenbush](hackenbush.md) on a rooted tree. By the colon principle, a node is worth the
XOR over its children of `(child + 1)`, so the whole tree `T(k)` has the nimber
`g(k) = (g(k−1)+1) ⊕ (g(k−2)+1)`. A tree with roughly `F_k` nodes thus has a nimber computed in
`O(k)`. Counting winning first moves needs more than the total. It needs, for each subtree, how
many moves leave it at each value `t`. That works only because the nimbers stay below `2¹³` while
the node count has thousands of digits. The count becomes a DP over `(level, target nimber)`. XOR
with a constant permutes `[0, 2ᵐ)`, so each level is two collision-free gathers.

**649 (Low-Prime Chessboard Nim).** The game splits twice: the coins are independent of each
other, and each coin's row move and column move are independent of each other. So the board is a
sum of `2c` copies of the subtraction game `{2, 3, 5, 7}`. That game's nimbers repeat with period
9 and lie in `{*0, …, *3}`, so a coin is worth one of 8 nimbers. A ten-million-wide board with 100
coins reduces to an 8-entry histogram raised to the 100th XOR-convolution power by
[squaring](../technique/exponentiation-by-squaring.md). The cost does not depend on `n`. One
pitfall: the faster Walsh–Hadamard transform would need to divide by 8 modulo `10⁹`, and 8 has no
inverse there. The direct `8 × 8` product needs no division.

**922 (Young's Game A).** This problem is not impartial, because Right only moves right and Down
only moves down. It is a [partizan game](partizan-game.md), and nimbers still appear inside it.
Computing canonical forms for small staircases shows the pattern
`G(a, b, k) = (b − a) + *(k − 1)`: an integer plus a nimber. A sum of staircases is then
`N + *X`, where the integers add normally and the nimbers add by XOR. Its outcome is fixed by the
sign of `N`, and when `N = 0` by whether `X = 0`. Counting tuples needs an ordinary convolution in
`N` and an XOR convolution in `X`. This time the modulus is prime, so the Walsh–Hadamard
transform can be inverted, and it reduces the XOR axis to 64 independent polynomial powers
([Kronecker substitution](../technique/kronecker-substitution.md) does each product). Here the
nimber is one component of a two-part value, and it is still the component that makes the count
tractable.

**933 (Paper Cutting).** A cut turns one rectangle into four independent rectangles, so an
option's value is the XOR of four nimbers, and a winning cut is one whose XOR is `0`. The table
`g(w, h)` has `h` up to about 1.2 million. The nimber structure makes that height harmless. Each
row is eventually constant, and the reason is a cancellation: once both strips of a cut are
past their thresholds, the four pieces are worth `G_a ⊕ G_{w−a} ⊕ G_a ⊕ G_{w−a} = 0`. Every
nimber is its own negative, so the identical pairs cancel to `*0`, and they do so for every
large `h`. That makes the row constant from some point on, which can be proved by induction. The
tail beyond it is summed in closed form, and the cost does not depend on `H`.

## How to reason about it

- **Look for the sum before the values.** All six reductions start by finding independent
  components: heaps, two axes, subtrees, cut pieces, separate diagrams. The decomposition the game
  really has may be finer than the one the statement draws (649's coin is two games). Without a
  sum, a nimber gives no more than the plain win/lose bit.
- **Measure the value range before choosing a method.** The pay-off in 310, 400, 649 and 922 all
  comes from the nimbers being far fewer than the positions. Print the largest Grundy value for
  small inputs first. If it stays small, plan to count over value histograms. If it grows with the
  input, the reduction buys less, and you need to find structure (periodicity, eventual
  constancy) instead.
- **Winning moves are target hits.** "Count the winning moves" means "count the moves that send
  one component to `gᵢ ⊕ X`". Carry counts indexed by target nimber (400), or count the cuts whose
  XOR is zero (933). Do not test every move against the full position.
- **`*a + *a = 0` is a working tool.** Equal pieces cancel. That is why the fixed points in
  Burnside's count for 310 are easy, and why the stable pieces in 933 cancel. When a structure has
  symmetric pairs, look at what they cancel to before anything else.
- **Pick the XOR-convolution method by modulus and width.** Walsh–Hadamard diagonalises XOR
  convolution, but its inverse divides by the width. Under a prime modulus (922) that division is
  fine. Under `10⁹` with width 8 (649) it is impossible, and the direct `W²` product is both
  correct and fast enough.
- **Partizan does not rule nimbers out.** When a partizan game's canonical forms reduce to
  "number + nimber" (922), the nimber part still adds by XOR. Compute canonical forms for small
  cases and look for that shape before deciding the game is out of reach.
- **Nimbers also multiply.** With XOR as addition and a carefully defined product, the nimbers
  below `2^(2ᵏ)` form a [finite field](https://en.wikipedia.org/wiki/Nimber#Multiplication). None
  of the solved problems here needs nim-multiplication. It is the tool for coin-turning games on
  two-dimensional boards, which are products of games rather than sums
  ([Tartan theorem](https://en.wikipedia.org/wiki/Nimber#Multiplication)), and it is worth knowing
  before reaching unsolved 459 (Flipping Game).

<!-- problems (generated by update-tags) -->
## Problems

- ○ [0260](/solutions/0260/) — Stone Game
- ● [0301](/solutions/0301/) — Nim
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ● [0310](/solutions/0310/) — Nim Square
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0459](/solutions/0459/) — Flipping Game
- ○ [0488](/solutions/0488/) — Unbalanced Nim
- ○ [0509](/solutions/0509/) — Divisor Nim
- ○ [0550](/solutions/0550/) — Divisor Game
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0665](/solutions/0665/) — Proportionate Nim
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0888](/solutions/0888/) — 1249 Nim
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0933](/solutions/0933/) — Paper Cutting
- ○ [0953](/solutions/0953/) — Factorisation Nim

<!-- /problems -->
