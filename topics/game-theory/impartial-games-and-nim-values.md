<!-- tags: [impartial-game, nimber, mex-function-set-theory, fibonacci-nim] -->
<!-- status: final 2026-10-14T07:42Z -->
# Impartial games and nim-values

An [impartial game](https://en.wikipedia.org/wiki/Impartial_game) is a two-player game where both
players have the same moves from every position, there is no chance, and (under the
[normal play convention](https://en.wikipedia.org/wiki/Normal_play_convention)) the player who
cannot move loses. Project Euler returns to these games again and again — stone piles, paper
strips, coins on a line, digits on a blackboard — because one theorem turns every one of them into
arithmetic. The [Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
says each position is equivalent to a single Nim heap of some size, its **nim-value** (or
[nimber](https://en.wikipedia.org/wiki/Nimber)), and that a sum of independent games is worth the
XOR of their values. The problems below then split into two families: those where you *compute*
the Grundy table, and those where the table hides a closed form that you have to *find*.

## The idea

### Win/lose first: P- and N-positions

Every position of a finite impartial game is either a **P-position** (the *Previous* player wins —
the player to move loses) or an **N-position** (the *Next* player wins). The classification is a
two-line induction: a terminal position is P; a position is N if *some* move reaches a P-position,
and P if *every* move reaches an N-position. When the question is only "who wins from here?", this
boolean is all you need. [Problem 961](/solutions/0961/) (remove a digit; whoever takes the last
non-zero digit wins) is solved exactly this way: the state compresses to a bitmask of
zero/non-zero digit slots, every move produces a strictly smaller mask, so a single forward sweep
over the masks fills the win/lose array with no recursion at all.

### Nim-values: mex over the options

The boolean stops being enough as soon as the game is a **sum** — several independent heaps or
regions, where a move touches exactly one of them. Win/lose does not compose (two losing
components do not make a losing sum in any simple way), but nim-values do. The Grundy value of a
position is the [mex](https://en.wikipedia.org/wiki/Mex_(mathematics)) — *minimum excludant*, the
smallest non-negative integer not in a set — of the values of its options:

$$ g(p) = \operatorname{mex}\{\, g(q) : p \to q \,\} $$

A position is P exactly when `g(p) = 0`. Value `k` means "behaves like a Nim heap of `k`": from it
you can reach every smaller value, but not `k` itself. For a one-parameter game (a heap of `n`
stones under some move rule) the table is a direct loop:

```python
def grundy_table(n_max: int, moves) -> list[int]:
    g = [0] * (n_max + 1)
    for n in range(1, n_max + 1):
        seen = {g[m] for m in moves(n)}
        g[n] = next(k for k in range(len(seen) + 1) if k not in seen)
    return g
```

`mex` of a set of size `s` is at most `s`, so the `range(len(seen) + 1)` bound is always enough.
Positions that **split** into independent parts — painting two adjacent squares in a strip
([Problem 306](/solutions/0306/)), cutting a rectangle into four ([Problem 933](/solutions/0933/))
— fit the same mould: an option's value is the XOR of its parts' values, and the mex runs over
those XORs.

### The nim-sum

The payoff is the [nim-sum](https://en.wikipedia.org/wiki/Nim#Mathematical_theory): for a sum of
games, `g(A + B) = g(A) ⊕ g(B)`, bitwise XOR. In plain [Nim](https://en.wikipedia.org/wiki/Nim)
each heap's value is its size, so `(a, b, c)` is lost for the mover iff `a ⊕ b ⊕ c = 0`.
[Problem 301](/solutions/0301/) is Nim with heaps `(n, 2n, 3n)` and turns entirely on the XOR: since
`n + 2n = 3n` and `a + b = (a ⊕ b) + 2(a & b)`, the triple is a P-position exactly when `n & 2n = 0`
— no two adjacent set bits — so the game question becomes a binary-string count.

Variants change the move rule but keep the structure. [Problem 310](/solutions/0310/) (take only a
square number of stones) and [Problem 509](/solutions/0509/) (take only a proper divisor of the
pile) are three-heap sums: compute each heap's Grundy value under the new rule, then count the
triples whose values XOR to zero.

## How to reason about it

**Count by value, not by position.** Grundy values are usually tiny compared with the positions
they label — a few dozen or a few hundred distinct values over a range of `10⁵` or more. Once you
have `g`, build a histogram `cnt[v]` of how many heaps take value `v`, and count P-positions of a
multi-heap sum as `Σ cnt[x]·cnt[y]·cnt[x ⊕ y]` over value pairs (with care over ordering if the
heaps are sorted). That is the step that turns an `O(N³)` triple loop into something linear in `N`
plus a small square in the number of values.

**Print the table before you trust it — then look for the closed form.** The Grundy table is the
honest algorithm, but most of these problems ask about bounds like `10¹⁶` where no table fits. The
recurring move is: brute-force `g(n)` (or the P/N pattern) for small inputs, stare at it, and spot
the structure. The shapes that keep turning up:

| Pattern in the table | Where it comes from | Example |
| --- | --- | --- |
| Depends on the **binary** digits of `n` | a move rule tied to doubling or halving | divisor-style piles (509), [Problem 899](/solutions/0899/): P exactly when the low bits of the larger pile are all ones, at a width set by the smaller pile's bit length |
| Depends on the **Zeckendorf** digits | a move bound tied to the previous move | [Fibonacci nim](https://en.wikipedia.org/wiki/Fibonacci_nim) in [Problem 692](/solutions/0692/): the minimal winning take is the smallest term of `n`'s [Zeckendorf representation](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem) |
| **Eventually periodic** | finite move sets on a line ([octal games](https://en.wikipedia.org/wiki/Octal_game)) | the strip-painting game in 306 is [Dawson's Kayles](https://en.wikipedia.org/wiki/Dawson%27s_Kayles), whose values settle into a period after a short irregular prefix |
| A **mex recurrence** with arithmetic structure | the "write the smallest unused number" constructions | [Problem 832](/solutions/0832/): the mex-and-XOR sequence groups into blocks by powers of four |

Once the pattern has a name, the answer usually falls to a [digit DP](https://en.wikipedia.org/wiki/Dynamic_programming)
or a sum over bit lengths in `O(log n)` — the game theory was only the doorway.

**Prove the pattern, or at least cross-check it.** A pattern read off a table is a conjecture. The
cheap insurance is to keep the brute-force Grundy solver and compare it with the closed form over
every input it can reach — the solution to 899 does exactly this up to `n = 200` before trusting
the bit-length formula at the real bound.

**Know when Sprague–Grundy does *not* apply.** It needs an impartial game under normal play with
independent components. [Misère play](https://en.wikipedia.org/wiki/Mis%C3%A8re#Mis%C3%A8re_game)
(last mover loses) breaks the XOR rule outside a few special cases. *Partisan* games, where the
players' moves differ — [Problem 939](/solutions/0939/) "Partisan Nim", [Problem 949](/solutions/0949/)
"Left vs Right II" — need [combinatorial game theory](https://en.wikipedia.org/wiki/Combinatorial_game_theory)
proper (surreal values, temperature) rather than nimbers. And a move whose legality depends on
history (Fibonacci nim's "at most twice the last take") makes the *state* bigger than the heap: fold
the history into the state before you look for a value.

<!-- problems (generated by update-tags) -->
## Problems

- ○ [0260](/solutions/0260/) — Stone Game
- ● [0301](/solutions/0301/) — Nim
- ○ [0306](/solutions/0306/) — Paper-strip Game
- ○ [0310](/solutions/0310/) — Nim Square
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0459](/solutions/0459/) — Flipping Game
- ○ [0488](/solutions/0488/) — Unbalanced Nim
- ○ [0509](/solutions/0509/) — Divisor Nim
- ○ [0550](/solutions/0550/) — Divisor Game
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ○ [0644](/solutions/0644/) — Squares on the Line
- ○ [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ○ [0665](/solutions/0665/) — Proportionate Nim
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ○ [0711](/solutions/0711/) — Binary Blackboard
- ○ [0798](/solutions/0798/) — Card Stacking Game
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0832](/solutions/0832/) — Mex Sequence
- ○ [0859](/solutions/0859/) — Cookie Game
- ○ [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0870](/solutions/0870/) — Stone Game IV
- ○ [0888](/solutions/0888/) — 1249 Nim
- ● [0899](/solutions/0899/) — DistribuNim I
- ○ [0900](/solutions/0900/) — DistribuNim II
- ○ [0933](/solutions/0933/) — Paper Cutting
- ○ [0939](/solutions/0939/) — Partisan Nim
- ○ [0949](/solutions/0949/) — Left vs Right II
- ○ [0953](/solutions/0953/) — Factorisation Nim
- ● [0961](/solutions/0961/) — Removing Digits
- ○ [0976](/solutions/0976/) — XO Game

<!-- /problems -->
