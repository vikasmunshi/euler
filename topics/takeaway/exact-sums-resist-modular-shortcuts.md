<!-- tags: [exact-sums-resist-modular-shortcuts] -->
<!-- status: final 2026-10-29T12:04Z -->
# Exact sums resist modular shortcuts

A per-item checksum, hash or score is defined "modulo $10^9+7$" — or the items simply *are*
residues, the solutions of some congruence counted as integers in $[0, n)$ — and the question asks
for the **sum** of them. It reads like a modular problem, and the standard modular move is right
there: carry a $(\text{count},\ \text{running total})$ pair through the search or the dynamic
program, or factor the sum through the structure of the residues, and reduce as you go. That
computation is correct, cheap, and answers a different question. Once each term has been reduced
individually, the total you want lives *outside* the modulus, and no amount of arithmetic inside
it will reach it.

## The idea

Reduction modulo $m$ is a [ring homomorphism](https://en.wikipedia.org/wiki/Ring_homomorphism): it
commutes with $+$ and $\times$, which is the whole licence for reducing early and often in
[modular arithmetic](/topics/domain/modular-arithmetic). What it does not commute with is the
*lift* — taking the canonical representative in $\{0, 1, \dots, m-1\}$ and treating it as an
ordinary integer. A quantity defined as "the checksum, mod $m$" is exactly that lift, and a sum of
such quantities is an ordinary integer sum of lifted values:

$$\sum_i \left(h_i \bmod m\right) \;=\; \sum_i h_i \;-\; m \sum_i \left\lfloor \frac{h_i}{m} \right\rfloor .$$

The floor terms — how many times each *individual* term wrapped — are precisely what the modulus
throws away. If the terms are $c_i \in [0, m)$ and there are $N$ of them, the exact total lies
somewhere in $[0, Nm)$, and knowing $\sum_i c_i \bmod m$ narrows that to $N$ candidates spaced $m$
apart. Choosing between them is the same problem as knowing the wrap counts, and knowing those
means having seen the terms one at a time.

Problem 244 is this trap in its purest form. It is the
[15 puzzle](/topics/domain/15-puzzle) with coloured rather than numbered tiles — seven red, eight
blue — so tiles of a colour are interchangeable and the state space collapses from $16!/2$
permutations to $16\binom{15}{7} = 102\,960$ boards, small enough to walk exhaustively. A
[breadth-first search](/topics/technique/breadth-first-search) layers every board by its distance
from the target, and the [shortest paths](/topics/domain/shortest-path-problem) are the walks that
descend one layer per move. Each path carries a
[polynomial rolling hash](https://en.wikipedia.org/wiki/Rolling_hash) of its move string in base
$243$, reduced modulo $100\,000\,007$ after every move, and the answer is the plain **unreduced**
sum of those already-reduced hashes.

The aggregate [dynamic program](/topics/technique/dynamic-programming) is sitting right there. Give
each state a pair $(n, S)$ — how many prefixes reach it, and the total of their hashes — and one
move by ASCII value $\mu$ extends it to

```python
n_next += n                      # prefixes, merged across all incoming edges
s_next = (s_next + 243 * S + n * mu) % M
```

This is linear in the graph, needs no path enumeration at all, and is *correct* — for the answer
modulo $100\,000\,007$. The exact number the problem wants is not a function of that pair. So the
paths have to be produced individually, which here is affordable: shortest-path counts across this
graph stay in the thousands, so the second phase walks a handful of branches while the first phase
touches all hundred thousand states.

## The same trap, without a hash

Problem 271 arrives at the trap from pure number theory. $S(n)$ is the sum of the $x$ in
$(1, n)$ with $x^3 \equiv 1 \pmod n$, for an $n$ that turns out to be the primorial of the first
fourteen primes. The [Chinese remainder theorem](/topics/technique/chinese-remainder-theorem)
splits the congruence across the prime factors: every solution is $x = \sum_i r_i e_i \bmod n$,
one cube root of unity $r_i$ chosen modulo each prime $q_i$, glued by the CRT idempotents $e_i$
($\equiv 1 \bmod q_i$, $\equiv 0$ modulo the rest). Primes $\equiv 1 \pmod 3$ contribute three
roots, the others only $1$, so six productive primes give $3^6 = 729$ solutions.

Here the shortcut is not a DP but an algebraic identity, and it is even more seductive. Summed over
every combination, $\sum_i r_i e_i$ separates: each $e_i$ is multiplied by the sum of its own
roots times the number of choices at the other primes, and the
[cyclotomic](/topics/domain/cyclotomic-polynomial) fact $1 + \omega + \omega^2 \equiv 0$ kills
the productive terms outright. That is a closed form in $O(t)$ — for $S(n) \bmod n$. But each
$x$ is the *lift* of its CRT combination to $[0, n)$, the reduction happens per solution, and the
true $S(n)$ is hundreds of times larger than $n$. The 729 wrap counts are exactly what the closed
form cannot see, so the solution builds the residues one combination at a time — a list of partial
sums grown prime by prime, each reduced mod $n$ as it branches, then added up as plain integers.

The two problems fail the same way for different reasons. In 244 the per-term reduction is a rule
of the hash; in 271 it is the definition of "the integers $x$ with $1 < x < n$". Either way the
quantity summed is a representative, not a residue class, and representatives do not add like
classes.

## The escapes that do not work

- **A wider modulus, or 128-bit, or Python's unbounded integers.** These help you hold the *sum*
  safely (see [watch integer width](/topics/takeaway/watch-integer-width)) but not compute it. The
  reduction that loses the information happens per term, by definition, before any summing; a
  hash carried modulo some larger $M$ says nothing about the integer value of $h_i \bmod m$.
- **Keeping the hashes exact and reducing at the end.** Legitimate, and here it means a $\sim 250$-bit
  integer per path, one reduction each — but it is still per-term work, only with wider arithmetic.
  It buys nothing over reducing as you go.
- **The [Chinese remainder theorem](/topics/technique/chinese-remainder-theorem).** CRT reconstructs
  a value from residues *of that value*. You have residues of a different quantity, and $c_i$, once
  lifted, is congruent to nothing useful.
- **Counting the wraps in bulk.** You would need $\sum_i \lfloor h_i/m \rfloor$, which is exactly as
  term-by-term as the sum you were trying to avoid.

## The escape that does work

Merge on **equality of the carried value**, not on the aggregate. Two prefixes that reach the same
state with the same residue are interchangeable from there on, because the extension map
$h \mapsto (243h + \mu) \bmod m$ is a deterministic function of the residue and the move. So instead
of one $(n, S)$ pair per state, keep a map from residue to multiplicity, and finish with
$\sum_c c \cdot \text{count}(c)$ — exact, because every $c$ is a real lifted term and its
multiplicity is an ordinary integer. The table per state is bounded by $\min(\#\text{paths}, m)$,
which is the useful middle ground: full enumeration when the paths are few, real compression when
they are many and the residues collide.

Independently, share the prefix work. A [depth-first walk](/topics/technique/depth-first-search) of
the descending layers carries the running hash down the branch and extends it in place, so a prefix
shared by many paths is hashed once rather than once per path, and no move string is ever
materialised. Enumerating the terms does not mean recomputing each from scratch.

## How to reason about it

- **Read where the "mod" sits.** "The sum of the checksums" and "the sum of the checksums, mod $m$"
  differ by one clause and by a complexity class. The second is a gift: it licenses every
  aggregation shortcut. The first is a warning that the terms are real integers you must produce.
- **An aggregation pushes through a map only if the map is a homomorphism *and* the question is
  asked on the far side of it.** Reduction qualifies; the lift back to an integer does not. The
  same trap wears other clothes: sum of digit sums, sum of last-$k$-digits, sum of $\lfloor
  x_i \rfloor$, sum of rounded scores. Any per-term *presentation* step — mod, floor, round,
  truncate, format — breaks the algebra that made the aggregate cheap.
- **If the answer is exact, the term count is part of your complexity.** Before designing anything,
  bound how many terms there are. A few thousand paths, or $3^t$ CRT combinations for small $t$,
  is a loop; $10^{12}$ terms means you need the residue-multiplicity merge, or the problem intends
  something else entirely.
- **Size the accumulator for $N \cdot m$, not $m$.** The whole point is that the total is not
  reduced. In C that is `unsigned long long` or `__int128` — 271's modulus alone needs 54 bits,
  and its C port sums in 128 bits because some test inputs push the total past $2^{64}$; Python hides the issue and a port will not.
- **Keep the modular shortcut as a cross-check** — the DP in 244, the closed form in 271. It is cheap, it is easy to get right, and it gives you
  the exact answer modulo $m$ by an independent route. If your enumerated total disagrees with it
  mod $m$, the enumeration is wrong; if they agree, you have checked everything but the wrap count.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0244](/solutions/0244/) — Sliders
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1

<!-- /problems -->
