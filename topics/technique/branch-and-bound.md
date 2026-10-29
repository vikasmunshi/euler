<!-- tags: [branch-and-bound] -->
<!-- status: final -->
# Branch and bound

[Branch and bound](https://en.wikipedia.org/wiki/Branch_and_bound) splits a search space into
pieces (the *branch*) and attaches to each piece a cheap, provable statement about the best it
could possibly contain (the *bound*). Any piece whose bound cannot beat what is already known gets
discarded unexplored, along with everything inside it. In the eight problems below the branching is
nothing special: factorisations, exponent vectors, digit strings, subsets, a tree of triples. What
makes each one finish in milliseconds, against a search space of $2^{62}$ or $10^{18}$ or a number
with $10^{10}$ digits, is the bound. This page is about how to find bounds and how to use them. How
to order the search so the bound bites early (which branch to try first, depth-first versus
best-first) is covered on the sibling page,
[branch-and-bound search](/topics/technique/branch-and-bound-search).

## The idea

A node of the search tree stands for a *set* of candidates: every completion of the partial choice
made so far. A bound is a number $B(\text{node})$ that is guaranteed to be at least as good as the
best candidate in that set. If the goal is a minimum, $B$ is a lower bound. Once some complete
candidate with value $v^*$ (the *incumbent*) has been found, every node with $B \ge v^*$ can be cut.
The whole technique rests on three properties of $B$:

- **Valid.** It must never claim something worse than the truth. A bound that is sometimes too
  pessimistic silently deletes the answer. The program still runs and still prints a number, so this
  is the bug to fear most.
- **Cheap.** It runs at every node, so it has to cost much less than exploring the node.
- **Tight.** The closer it comes to the true best value, the higher in the tree it cuts. A cut at depth
  3 removes the whole subtree below that node.

These pull against each other. Every solution below makes a different trade between tightness and
cost.

Problem 88 shows the shape with the least machinery. Every factorisation into factors $\ge 2$ with
product $P$ and sum $S$ gives a product-sum set of size $k = m + (P - S)$ once it is padded with
ones. The set $\{2, k, 1, \dots, 1\}$ shows that the minimal $N$ for any $k$ is at most $2k$. That
single inequality is both the initial incumbent and the pruning rule:

```python
min_prod: list[int] = [2 * max_k] * max_k        # incumbent for every k, before any search

def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
    k = prod - total + count
    if k < max_k:
        min_prod[k] = min(min_prod[k], prod)
        for i in range(start, max_k // prod * 2 + 1):   # prod * i <= 2 * max_k, or it can't win
            find_product_sum(prod * i, total + i, count + 1, i)
```

The loop limit is recomputed from the current `prod`, so the bound gets tighter the deeper the
recursion goes. That is why the run time stays close to linear in `max_k` while the number of
factorisations does not.

## Where bounds come from

The eight solutions draw their bounds from five places.

**An optimistic completion.** Finish the partial solution in the most favourable way the
constraints allow, ignoring the rest of the constraints, and evaluate it. Problem 170 looks for the
largest [pandigital](/topics/domain/pandigital-number) concatenated product. It builds the product
string from the most significant digit, so the partial string is always a genuine prefix of a
candidate. Its bound pads that prefix with the unused digits in descending order. If even that
string does not beat the best answer found so far, the branch is dead. Problem 110 gets the same
kind of bound for a minimum. It searches exponent vectors for the smallest $n$ with
$\tau(n^2) \ge$ target, as in a [highly composite number](/topics/domain/highly-composite-number).
Exponents never increase from one prime to the next, so each remaining prime contributes a factor of
at most $(2e+1)$, the current one. If $\tau \cdot (2e+1)^{\text{remaining}}$ still falls short, no
completion reaches the target.

**Monotonicity.** If every step of the branching makes the objective worse, the node's own value is
already a bound on its whole subtree. In problem 139's second solution, every child in the
[Berggren tree](/topics/technique/tree-of-primitive-pythagorean-triples) has strictly larger sides than
its parent. Once a triple's perimeter passes the limit, none of its descendants can come back under
it, and one comparison discards an infinite subtree. Problem 241 builds $n$ prime by prime while
tracking the [abundancy index](/topics/domain/abundancy-index) $\sigma(n)/n$ as an exact fraction.
Every prime power multiplies that index by a factor greater than 1. So the moment the running index
passes the half-integer target, nothing below that node can land on it.

**An algebraic necessary condition.** Sometimes the bound is a divisibility fact rather than a
magnitude. Problem 241 writes the residual target as $a/b$ in lowest terms. The unplaced cofactor
$m$ must then be a multiple of $b$, which gives two cuts: $b$ must fit in the remaining budget
$\lfloor \text{limit}/n \rfloor$, and $b$ must share no prime already passed over. The second test is
one `gcd` against a precomputed primorial. Its notes record that this test alone cut the running time
at $10^{14}$ from twenty-five seconds to a tenth of a second.

**A structural lower bound on the objective.** Problem 254 never builds $g(i)$, which has about
$10^{10}$ digits. It scans candidate digit-factorial sums $F$ instead, and the length of the shortest
number whose digit factorials sum to $F$ is at least $\lfloor F/9! \rfloor$, because the
[factorial-base](/topics/domain/factorial-number-system) digits below the $9!$ place add at most 36.
That bound only grows with $F$, so the scan stops as soon as $\lfloor F/9! \rfloor$ reaches the
incumbent length. In the worst case the window is about $37 \cdot 9!$ wide, and in practice it is much
narrower, because each shorter candidate shrinks it.

**A reachability window on a constraint.** Not every bound is about the objective. When the
problem is a *feasibility* condition, such as a quantity that must end at exactly zero, the bound
asks whether the undecided items can still get it there. Problem 473 looks for integers whose
[phigital](https://en.wikipedia.org/wiki/Golden_ratio_base) representation is a palindrome. Each
mirrored pair of digits, $\varphi^k + \varphi^{-(k+1)}$, is a number $\tfrac12(a + b\sqrt5)$, and a
set of pairs sums to an integer only when the $\sqrt5$ coefficients cancel. The search decides the
pairs from the largest down. Prefix sums of the positive and of the negative coefficients over pairs
$1..k$ give the most the balance can still rise and the most it can still fall. A node whose balance
lies outside that window can never return to zero, so it is cut. Because the coefficients are
Fibonacci numbers and grow geometrically, once a large pair is taken only a thin band of smaller
pairs can cancel it. The window catches this, and the search becomes output-sensitive: it does work
roughly in proportion to the answers, not to the Fibonacci-sized count of digit strings. The same
window works for any search that must hit a target sum exactly, such as subset sum with mixed signs.

## How to reason about it

**Seed the incumbent.** Until a first complete solution exists, an incumbent bound cuts nothing.
Problem 110 does not start `best` at infinity. It seeds it with a concrete legal $n$, the product of
the first $k$ primes with $3^k \ge$ target, so the very first branch is already pruned. Problem 88
seeds every table entry with the provable $2k$. A cheap feasible solution found by a
[greedy](/topics/technique/greedy-algorithm) construction, or a known closed-form upper bound, is
almost always worth computing before the search starts.

**`break`, not `continue`, when the bound is monotone in the loop variable.** In problem 110, a
smaller exponent gives a smaller factor, so once the reachability test fails for some $e$ it fails
for every smaller one too, and the loop can stop there. Problem 241 goes a step further. Its gain
bound falls as the starting prime rises, so it binary-searches for the last prime worth trying and
never tests the others at all.

**Make the bound cheap by precomputing it.** Problem 241's tightest cut asks for the most a tail of
primes $\ge p_j$ fitting in budget $B$ could still add to the index: the product of $q/(q-1)$ over
the smallest such primes. Computing that product at every node would cost more than the node itself.
The solution keeps prefix sums of $\log p$ and $\log\frac{p}{p-1}$, so one binary search and one
subtraction give the bound.

**When the bound is exact, count instead of searching.** Problem 755 counts subsets of the
Fibonacci numbers $\le n$ whose sum fits a budget $b$. With the numbers taken in descending order and
their suffix sums $\sigma_i$ precomputed, a node where $b \ge \sigma_i$ has a bound equal to its true
value: every one of the $2^{m-i}$ tail subsets fits. The node returns a shift instead of recursing.
That is the counting version of pruning. A subtree whose answer is known in closed form never has to
be visited. With [memoization](/topics/technique/memoization) on the colliding $(i, b)$ states, it
leaves 159 states standing in for $2^{62}$ subsets.

**Validity is a proof obligation, so check it independently.** A wrong bound does not crash. It just
deletes answers. Problem 241's endgame accepts a candidate only after checking the exact identity
$2\,\mathrm{num}\,\sigma(m) = \text{target}\cdot\mathrm{den}\cdot m$, so a slip in its algebra could
lose a solution but never invent one. Its result was also confirmed against a divisor-sum sieve and
an independent variant that needs none of the algebra. Problem 254 was checked against two brute
forces. Before trusting a cut on a large input, compare it against an unpruned search on a small one.

**Let approximate arithmetic prune, never decide.** Floating point is cheap enough to run at every
node, but a rounding error in a bound is a validity bug. Problem 473 keeps a running real value of
each partial sum and cuts a branch once it passes $N$. That test carries a small relative slack, so
rounding can only make it keep too much, never too little. Membership is then decided at the leaves
in exact integers: a balance of exactly $0$ and a doubled value at most $2N$. The float bound only
has to be safe. The exact test has to be right.

## C and Python

All eight are direct ports: the C and Python sides apply the same bounds in the same order. The
differences are in the plumbing.

| Concern | Python | C |
|---|---|---|
| Incumbent shared across recursion | closure over `nonlocal best` or an enclosing list (88, 110) | file-scope globals such as `g_min_prod`, `best` (88, 110) |
| Products that may exceed 64 bits | free with unbounded `int` | guard before multiplying: `n > best / pe` (110); `unsigned __int128` with caps proven to fit (241); `__int128` totals and a hand-written decimal printer (473); [GMP](/topics/technique/gmp) with a native `unsigned long long` fast path (254) |
| Memo for the exact-count prune | `functools.lru_cache` (755) | hand-written open-addressing table keyed on $b \cdot 128 + i$, cleared on every call (755) |
| Explicit DFS stack | `list` push/pop (139, 473) | `realloc`-doubled array (139); a fixed-size array (473) |
| Deduplicating results | `sum(set(...))` (88) | a `char` seen-array indexed by value (88) |

The [overflow](/topics/technique/integer-overflow) row matters more than it looks. A bound like
`new_n < best` is only valid if `new_n` was computed correctly. In C, a wrapped product turns an
honest comparison into a cut that removes the answer. So the guards come before the multiplication
they protect, and they are part of what makes the bound valid, not optional decoration. Python gets
the same correctness for free and pays for it in speed: problem 254's notes measure the C port at
about 81 times faster on a loop that is pure integer arithmetic.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0755](/solutions/0755/) — Not Zeckendorf

<!-- /problems -->
