<!-- tags: [zeckendorfs-theorem] -->
<!-- status: final 2026-10-28T08:07Z -->
# Zeckendorf's theorem

[Zeckendorf's theorem](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem) says that every
positive integer is, in exactly one way, a sum of distinct, **non-consecutive**
[Fibonacci numbers](/topics/domain/fibonacci-sequence). Read as digits, that is a positional
number system with Fibonacci place values, digits 0 and 1, and the rule "no two adjacent 1s".
It keeps coming back because it turns a problem about *all integers up to $N$* into a problem
about $O(\log N)$ Fibonacci blocks. The three problems below use it three ways: 297 sums the
*length* of every representation below a limit, 692 sums the *smallest term* of every
representation, and 473 swaps the Fibonacci place values for powers of the
[golden ratio](/topics/domain/golden-ratio). Once the representation is in view, each problem is a
short walk down the Fibonacci list rather than a scan over $10^{16}$ numbers.

## The idea — a number system with Fibonacci place values

Index the Fibonacci numbers without the repeated 1, as $1, 2, 3, 5, 8, 13, \dots$. Two facts
carry everything.

- **Greedy finds it.** Take the largest $F_k \le n$ and recurse on $n - F_k$. Since
  $n < F_{k+1} = F_k + F_{k-1}$, the remainder is below $F_{k-1}$, so the next term is never
  $F_{k-1}$. Non-adjacency is not something the [greedy algorithm](/topics/technique/greedy-algorithm)
  has to enforce; it falls out of the recurrence.
- **It is unique.** A sum of non-consecutive Fibonacci numbers whose largest term is $F_k$ is at
  most $F_k + F_{k-2} + F_{k-4} + \dots = F_{k+1} - 1$. So the leading term of any valid
  representation of $n$ is forced to be the largest $F_k \le n$, and induction does the rest.

The identity $F_k + F_{k+1} = F_{k+2}$ is the carry rule: a `011` in the digit string rewrites to
`100`. Any set of Fibonacci summands can be normalised to the Zeckendorf form this way, exactly as
base 10 normalises a digit 12 into a carry. The same rule with place values $\varphi^k$ gives the
[golden ratio base](https://en.wikipedia.org/wiki/Golden_ratio_base), because
$\varphi^k + \varphi^{k+1} = \varphi^{k+2}$ is the same identity one level up. That is the bridge
to the golden-ratio page, and the [positional notation](/topics/domain/positional-notation) page
covers the general frame.

Written greedily, the decomposition is three lines:

```python
def zeckendorf(n, fibs):            # fibs ascending: 1, 2, 3, 5, 8, ...
    terms = []
    for f in reversed(fibs):
        if f <= n:
            terms.append(f)
            n -= f
    return terms
```

## The block recurrence — summing over every $n < N$

Problems rarely want one representation. They want a statistic summed over every integer below a
huge $N$. The structural fact that makes this cheap is
[self-similarity](/topics/domain/self-similarity): the integers in $[F_k, F_{k+1})$ are exactly
$F_k + m$ for $m \in [0, F_{k-1})$, and their representations are $m$'s representation with $F_k$
prepended. So the block $[0, F_{k+1})$ is the block $[0, F_k)$ followed by a shifted copy of the
block $[0, F_{k-1})$. Write $T_k$ for the sum of some statistic $s$ over $[0, F_k)$; then

$$T_{k+1} = T_k + \bigl(\text{what prepending } F_k \text{ adds, summed over } F_{k-1} \text{ numbers}\bigr) + T_{k-1}.$$

For an arbitrary limit $N$, the same split applies to the greedy decomposition of $N$ itself:
peel the largest $F_k \le N$, add the full block $T_k$ plus the contribution of the partial block
above $F_k$, and continue with $N - F_k$. With about $\log_\varphi N$ terms, that is roughly 80
steps for $N = 10^{17}$. This is the Fibonacci analogue of the
[digit DP](/topics/technique/digit-dp) used for decimal digit sums, with the no-adjacent-1s
constraint baked into the block sizes.

The two counting problems differ only in the middle term.

- **Problem 297** sums $z(n)$, the number of terms. Prepending $F_k$ adds one term to each of the
  $F_{k-1}$ numbers in the upper block, so the middle term is just $F_{k-1}$.
- **Problem 692** sums $H(n)$, the smallest term, which is what the game reduces to (below).
  Prepending $F_k$ leaves the smallest term unchanged, except for $m = 0$, where $F_k$ is the only
  term. So the middle term is $F_k$ itself, contributed once.

Both are $O(\log N)$ with the tables built inside `solve()`, sized to the limit. The pitfall is
width, not time: the block sums outrun 64 bits well before the Fibonacci numbers do, which is why
the C ports keep their totals in [`__int128`](/topics/technique/int128).

## Where the representation hides

Problem 692 never mentions Fibonacci numbers. It describes a pebble game in which each move may
take at most twice the previous one. That is [Fibonacci nim](/topics/domain/fibonacci-nim), and
its theory ([combinatorial game theory](/topics/domain/combinatorial-game-theory)) says the
winning move is to take the smallest Zeckendorf term of the heap. The doubling cap is the
connection: the next-smallest term is more than twice the smallest (non-adjacency again), so the
opponent can never reach it in one move. The lesson is to look for the representation behind an
"at most $c$ times the last move" rule, the same way one looks for binary behind ordinary Nim.

Problem 473 is the irrational side. It sums the integers whose base-$\varphi$ expansion is a
palindrome. The same non-adjacency rule makes the expansion unique, but the place values are
now irrational, so the work is in exact arithmetic over $\mathbb{Z}[\varphi]$ and a pruned search
over mirrored digit pairs. The [golden ratio](/topics/domain/golden-ratio)
page covers it in full; here the point is only that the uniqueness argument carries over unchanged.

## How to reason about it

- **Non-adjacent 1s mean Fibonacci.** A count of binary strings with no two adjacent 1s, a game
  with a "twice the last move" cap, a sum over Fibonacci-indexed blocks: each is Zeckendorf.
- **Sum over blocks, never over integers.** Any statistic that changes predictably when a leading
  term is prepended gives a three-term recurrence on $T_k$, and the greedy decomposition of $N$
  stitches the partial block together in $O(\log N)$.
- **Derive the middle term carefully.** It is the only part that differs between problems, and
  the off-by-one sits at $m = 0$ (the lone-term number $F_k$) and at the inclusive/exclusive end
  of the limit. A brute force over small $N$ catches both, which is how 297's recurrence was
  checked before it was trusted.
- **Watch the indexing.** Zeckendorf's theorem uses $1, 2, 3, 5, \dots$; the standard Fibonacci
  sequence has $F_1 = F_2 = 1$. Mixing the two silently shifts every block by one.
- **Same rule, other radices.** Swap $F_k$ for $\varphi^k$ and the uniqueness proof survives;
  what changes is that sums stop being integers by default, so integrality becomes the question.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0692](/solutions/0692/) — Siegbert and Jo

<!-- /problems -->
