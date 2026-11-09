<!-- tags: [recursion-computer-science] -->
<!-- status: final -->
# Recursion (computer science)

[Recursion](https://en.wikipedia.org/wiki/Recursion_(computer_science)) is a function that solves
its problem by calling itself on a smaller version of the same problem. It is the least exotic
technique on this list and the most quietly load-bearing: across the problems below it shows up as
a way to *state* a definition, a way to *take an object apart*, and a way to *walk a tree of
choices* — three different jobs sharing one piece of syntax. Getting it right is mostly about two
things the syntax does not give you for free: knowing that the descent terminates, and knowing
whether the subproblems repeat.

## The idea — a base case and a smaller call

Every recursive function is the same two clauses:

```
f(x):
    if x is small enough: return the answer directly     # base case
    return combine(f(smaller(x)), ...)                   # recursive case
```

Correctness needs a **well-founded** measure: some quantity that strictly decreases on every call
and cannot decrease forever. In problem 24 it is the number of digits left to place; in problem 65
the remaining depth of the continued fraction; in problem 76 the remaining sum. Name that measure
before writing the function — nearly every non-terminating recursion is a case where the argument
did not actually get smaller on some branch.

The payoff is that the code can be read as the mathematics. Problem 188's tetration is *defined*
recursively ($a \uparrow\uparrow (k+1) = a^{(a \uparrow\uparrow k)}$), and the solution peels the
tower one level at a time under a shrinking modulus — the recursion in the code is the recursion in
the statement, with a number-theoretic identity keeping the numbers finite. Problem 1000's meta-
sequence $M(k) = M(k-1)M(k-2)M(k-3)$ and problem 115's fill-count are the same story. When the
statement hands you a recurrence, the first draft should look like the recurrence.

## Three jobs, one syntax

**Mirror a definition.** The recursion follows the structure of the problem statement, as above.

**Decompose an object.** The recursion splits a thing into a head and a rest. Problem 24 unranks a
permutation by dividing the rank by $(n-1)!$ to fix the leading digit, then recursing on what
remains; problem 17 spells a three-digit number by naming the hundreds and recursing on the
remainder; problem 65 evaluates a continued fraction by recursing to the bottom and unwinding
$a + 1/\text{rest}$ on the way back up. Problems 93 and 259 both decompose an expression: 93
repeatedly replaces two values in a pool by one combination and recurses on the smaller pool, while
259 — whose digits are locked in order — splits a contiguous run into a left part, an operator and
a right part, which is a recursion over intervals.

**Search a tree of choices.** The recursive call *is* the branch. This is
[depth-first search](/blogs/technique/depth-first-search) and
[backtracking](/blogs/technique/backtracking) — problem 96 guessing a Sudoku cell, problem 43
prepending one digit at a time under a divisibility constraint, problems 103, 118, 122, 152, 204,
215 and 248 all growing a partial object choice by choice. Those pages cover the search-specific
concerns (pruning, canonical ordering); what matters here is that the *stack frame* is the
bookkeeping: the path from the root to the current node lives in the call chain, and returning
un-makes a choice for free.

Problem 88 is the compact illustration — the whole search is five lines, and the state that would
otherwise need an explicit stack is just the four parameters:

```python
def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
    k = prod - total + count
    if k < max_k:
        min_prod[k] = min(min_prod[k], prod)
        for i in range(start, max_k // prod * 2 + 1):
            find_product_sum(prod * i, total + i, count + 1, i)
```

Note the `start` parameter: factors are only ever extended with a factor at least as large as the
last, so each factorisation is reached by exactly one path. That trick — pass the current choice
down as the next lower bound — recurs everywhere in these solutions.

## Do the subproblems repeat? The question that decides everything

A recursion whose calls all land on *distinct* subproblems costs one call per node of the tree.
A recursion whose calls collide costs one call per *distinct* subproblem, if you cache — and
exponentially more if you don't. Deciding which case you are in is the single highest-leverage
judgement.

When they collide, add [memoization](/blogs/technique/memoization) and the call tree collapses
into a directed acyclic graph. That is top-down
[dynamic programming](/blogs/technique/dynamic-programming), and it is the most common shape on
this page: problem 14 caching Collatz chain lengths so shared tails are computed once, problem 76's
partition counts keyed on `(number, slots)`, problem 77's prime partitions, problem 301's digit DP
keyed on `(position, previous bit, tight)`. The recursion states the recurrence; the cache supplies
the efficiency. In Python that is one decorator over a function you were going to write anyway,
which is why the top-down form is usually the one to write first — bottom-up tables can come later,
if at all.

When they *don't* collide, a cache is dead weight. Problem 73 counts fractions in $(1/3, 1/2)$ by
walking the [Stern–Brocot tree](https://en.wikipedia.org/wiki/Stern%E2%80%93Brocot_tree), where
every node is a distinct fraction:

```python
def recursion(lower_denominator: int, upper_denominator: int) -> int:
    if (mediant := (lower_denominator + upper_denominator)) > max_d:
        return 0
    return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)
```

Each call produces exactly one fraction, so the running time is the size of the answer and no memo
can help. That is not a defect — it is enumeration, and the right question to ask of it is whether
a counting argument can replace the walk entirely. For this problem one can: index 2 uses
[Möbius](https://en.wikipedia.org/wiki/M%C3%B6bius_function)-based counting and runs in $9.2$ ms
against this recursion's $748$ ms, forty times faster than even the direct index 0.

## Count, don't enumerate

The most expensive mistake with a recursive counter is returning the objects instead of the number
of them. Problems 76 and 77 ship both versions, which makes the cost visible. Counting partitions
memoises an `int` per subproblem; *building* the partitions memoises a list whose length is the
answer itself, so the cache grows with the output and both time and memory go exponential. Problem
76 at $n = 100$:

| index | what it returns | time |
| --- | --- | --- |
| `s0` | count, via Euler's pentagonal recurrence | $21.6\ \mu s$ |
| `s1` | count, via the memoised `(number, slots)` recursion | $334\ \mu s$ |
| `s2` | the partitions themselves | refuses to run past $n = 50$ |

Problem 77 repeats it exactly: the counting index answers the real input in $127\ \mu s$ while the
enumerating index cannot reach it at all. Both enumerating solutions carry an explicit
`safe_limit` guard that raises rather than exhaust memory — a reasonable way to keep an
instructive-but-unscalable variant in the tree honestly labelled.

Enumerate only when you genuinely need the objects (problem 96 wants the grid, problem 43 wants the
numbers to sum). If the question is "how many", make the return type an integer all the way down.

## Collapse the subtree you can summarise

A stronger move than caching a *value* is caching a *whole subtree's effect*. Problem 220 walks a
[Heighway dragon](https://en.wikipedia.org/wiki/Dragon_curve) whose string has around $10^{15}$
characters at the depth required. It never builds it. Each non-terminal's expansion is a rigid
shape, so a level-$k$ expansion is fully summarised by two numbers — a net displacement and a net
rotation, the rotation being multiplication by a Gaussian integer. The descent then compares the
subtree's step count against the remaining budget: if the whole subtree fits, apply the cached
transform in $O(1)$ and skip it; only the subtree containing the target step is actually entered.
One root-to-leaf path instead of $2^n$ nodes.

Problem 199 does the analogous thing with multiplicity: the Apollonian gasket produces $4 \cdot 3^n$
gaps after $n$ iterations, but congruent gaps have identical futures, so the solution keys them on
their sorted curvature triple and carries a count instead of a copy. Same recursion, distinct states
only.

Problem 452 shows the same habit at a whole subtree's *leaves*. It sums the $n$-fold divisor
function $d_n$ up to $10^9$ by walking integers through their prime factorisation in increasing
order of primes. A call $S(x, j)$ covers everything up to $x$ whose smallest prime factor is at
least $p_j$. It branches on $p_i^e$ for $i \ge j$, recurses on $(\lfloor x/p_i^e \rfloor, i+1)$, and
so uses the same pass-the-lower-bound trick as problem 88: each integer is reached along exactly one
path. What it never does is descend into the numbers that are a single prime. Because $d_n(p) = n$
on every prime, that entire fringe is $n\,(\pi(x) - j)$, a single lookup into a prime-count table
precomputed at every $\lfloor m/i \rfloor$. The recursion only visits composites, about
$m^{3/4}/\log m$ work rather than $m$, and it needs no memo. Its depth also needs no guard, which
is the next section's concern from the other side: depth is the number of distinct prime factors, at
most nine below $10^9$, so the bound comes from the problem's structure rather than from
`setrecursionlimit`.

All three are worth making a habit as a habit: before descending, ask whether the subtree's
*contribution* has a closed form or a duplicate elsewhere. Recursion with algebra attached beats recursion alone.

Problem 551 shows what that looks like when the summary has to stop partway through. Its sequence
adds each term's own digit sum, $a_n = a_{n-1} + s(a_{n-1})$, for $10^{15}$ steps. Write the value
as $H \cdot 10^k + L$: until $L$ overflows $10^k$, the high part only contributes its digit sum, so
"how many steps until the low block carries, and what is left behind" depends on $(k, s(H), L)$
alone. A level-$k$ jump is about ten level-$(k-1)$ jumps, and the jumps repeat, so they are cached.
The catch is the step budget: the final block is never finished. The fix is to cache only
*completed* jumps and reuse one only when it fits in what is left. Otherwise the call descends
again, so that it stops on exactly the right step. Only the $O(k)$ calls on the last, truncated path
pay full price. Problem 220's budget check is the same thing, with a rigid transform where 551 has
a memo.

## Halve, and return what the parent needs

A recursion on $\lfloor n/2 \rfloor$ has depth $\log_2 n$, which makes $n = 10^{18}$ cheap. The hard
part is that the quantity asked for usually does not halve cleanly on its own. Problems 463 and 539
both ask for a *prefix sum* of a recursively defined function up to about $10^{18}$, and both solve
it the same way: sum the recurrence itself, and return more than one number from each call.

In problem 539 the elimination game is self-similar. After one sweep the survivors are $2, 4,
\dots$, read backwards, so the last survivor obeys
$P(n) = 2(\lfloor n/2 \rfloor + 1 - P(\lfloor n/2 \rfloor))$. Summing that over $k \le n$ pairs up
$k = 2m$ and $2m+1$. As a result $S(n)$ needs $S(M)$ *and* $P(M)$ at $M = \lfloor n/2 \rfloor$. On its own, neither
quantity can be computed by halving; as a pair they can. The helper returns the tuple
$(P, S)$, and 60 levels of constant work replace $10^{18}$ terms. Problem 463 is the same move for
two mutually recursive sums, $S$ over all indices and $O$ over the odd ones, split by residue
mod 4. Its $O(2n)$ needs four sub-calls, two of them at $n$ and two at $n-1$. Without a memo that
branching is exponential. With one it is about two states per level, 115 of each in total. This is
the general shape: when $f(n)$ needs $g(\lfloor n/2 \rfloor)$, make the recursion return $(f, g)$.
If the calls fan out to neighbouring arguments, memoise, and the state count stays logarithmic.

## Carry richer state down the descent

The parameters of a recursive call need not be scalars. In problem 930 an expected hitting time
becomes a spectral sum over $n^{m-1}$ characters. The summand depends only on how many coordinates
fall in each cosine class, so the recursion walks the classes and chooses how many balls go into
each one. That is a composition of $m$, and there are only thousands of them, not $10^{11}$. A
side condition (the residues must sum to $0 \bmod n$) cannot be checked one class at a time, so the
call carries a length-$n$ *vector* of counts indexed by residue sum. Each level combines it with a
small vector by circular convolution, and the leaf reads entry 0. The recursion enumerates
coarse structures, and the vector carries the fine-grained bookkeeping that would otherwise force
enumeration of the fine ones. Problem 564 is a smaller example of the same coarsening. The area
of a cyclic polygon depends only on the multiset of its sides, so a recursive *generator*
enumerates partitions as `(part, multiplicity)` pairs and weights each one by a multinomial count.
In Python, `yield`-ing from a recursion is the cheap way to stream such structures without
building the list.

## Normalise the state before you branch

When a recursion's argument is a structure rather than a number, two things decide whether it is
tractable. One is whether equal states are *recognised* as equal. The other is whether doomed or
redundant branches are cut before they are explored.

Problem 829 recurses over the *shapes* of factor trees. The numbers of shape $(L, R)$ are built
from the lists for $L$ and $R$, so the recursion follows the tree's structure. The 30 target trees
share many subtrees, so each shape is
[hash-consed](https://en.wikipedia.org/wiki/Hash_consing) to an integer id. The memo is keyed on
that id, which means equal subtrees really are one cache entry. Only 65 distinct shapes are ever
reached. A second refinement is that the cached value is a list *complete up to a bound*. Later
requests for a smaller bound binary-search the prefix, and larger ones double the bound and
rebuild. The cache key is (state, how far we have looked), not just the state.

Problem 968 shows the pruning half. It sums a weighted count over a five-dimensional polytope with
about $10^{40}$ points by eliminating one variable at a time, in the manner of
[Fourier–Motzkin](https://en.wikipedia.org/wiki/Fourier%E2%80%93Motzkin_elimination). Each
elimination is a geometric series, and the recursion branches on which bound is the tightest.
Left alone, that case tree explodes. Before every split the solution closes the region with
Floyd–Warshall on a difference-bound matrix. Empty regions are dropped as negative cycles, and
bounds that can never be the strict minimum are discarded. Most branches never come into being.
A canonical form of the state, computed on entry, is what keeps the call tree small.

## The stack is a finite resource

Python's default recursion limit is $1000$ frames, and a frame is not free. Three responses appear
in these solutions, in increasing order of effort:

1. **Raise the limit** — `sys.setrecursionlimit(10 ** 6)`, as problems 65, 73 and 76 do. Fine when
   the depth is bounded by the input in a way you can see; the interpreter's C stack is the real
   ceiling and it is not the same number.
2. **Invert to bottom-up.** Fill a table in dependency order and the frames vanish. Problem 301's
   Python index memoises a recursion while its C index computes the same DP bottom-up for exactly
   this reason, and problem 76's C solution replaces the pentagonal recursion with a loop over
   `p[0..n]`. Porting a memoised recursion to C is the usual moment to do this — a language without
   `lru_cache` and with a smaller stack pushes you there anyway.
3. **Carry an explicit stack.** Same traversal, no frames, and the depth limit becomes heap memory.
   Worth it when the depth is data-dependent and unbounded.

The related trick when depth is what you are *searching for* is
[iterative deepening](/blogs/technique/iterative-deepening-depth-first-search): problem 122 runs
depth-limited searches at $1, 2, 3, \dots$ so the first chain found is minimal, keeping memory at
$O(\text{depth})$. The re-work is a constant factor, because in a branching tree the deepest level
dominates the total.

## How to reason about it

1. **State the recurrence first**, in maths, including the base cases. If you cannot write it, the
   recursion will not write itself.
2. **Name the decreasing measure.** No measure, no termination.
3. **Ask whether subproblems repeat.** They do → memoise, and count the distinct states to get the
   complexity. They don't → you are enumerating, so ask whether a counting argument replaces the
   walk.
4. **Return a number if a number is wanted.** Never accumulate the objects unless the objects are
   the answer.
5. **Look for a summarisable subtree** — a rigid transform, a multiplicity, a closed form — before
   accepting an exponential descent. If a budget can cut a subtree short, cache only the
   completed ones.
6. **When the argument halves, return a tuple.** If $f(n)$ needs some $g$ at $n/2$, recurse on
   $(f, g)$ together.
7. **Put the whole context in the key, and normalise it first.** Intern structural states,
   carry vectors instead of enumerating what they count, and prune or close a state before
   branching on it.
8. **Check the depth** against the language you are writing in, and know which of the three fixes
   you will reach for.

One repository-specific point, and it bites recursion harder than anything else: build every cache
**inside** `solve()`. The harness times repeated `solve()` calls, so a module-level `lru_cache`
stays warm between runs and every run after the first measures a dictionary lookup. Problems 14, 17
and 301 all say so explicitly in their source — the memo is built or cleared per call, so the
benchmark reflects the real cost.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0096](/solutions/0096/) — Su Doku
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0161](/solutions/0161/) — Triominoes
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0220](/solutions/0220/) — Heighway Dragon
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0259](/solutions/0259/) — Reachable Numbers
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0301](/solutions/0301/) — Nim
- ● [0452](/solutions/0452/) — Long Products
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ● [0539](/solutions/0539/) — Odd Elimination
- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0564](/solutions/0564/) — Maximal Polygons
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0829](/solutions/0829/) — Integral Fusion
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0930](/solutions/0930/) — The Gathering
- ● [0968](/solutions/0968/) — 5D Summation
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
