<!-- tags: [greedy-algorithm] -->
<!-- status: final -->
# Greedy algorithm

A [greedy algorithm](https://en.wikipedia.org/wiki/Greedy_algorithm) builds its answer one
irrevocable choice at a time, always taking whatever looks best right now, and never goes
back. Most of the time that is a heuristic, not a method. Fast, but with no promise. It keeps
showing up in Project Euler because many problems are built so that the locally best move
*is* the globally best one: the smallest primes, the largest denomination that fits, the
cheapest leaf to split. Once I can prove that, a search over millions of candidates turns
into a handful of steps. In the problems below the greedy step does one of three jobs. It is
the whole answer, it is the walk a recurrence follows, or it is a bound that makes an exact
search cheap.

## The idea — and the proof it owes you

A greedy step is safe when the problem has two properties:

- **Greedy-choice property.** Some optimal solution starts with the greedy choice. So
  committing to it early never closes off the optimum.
- **Optimal substructure.** Once that choice is made, what is left is a smaller instance of
  the same problem. The same rule then applies again.

The second property is the one [dynamic programming](/topics/technique/dynamic-programming)
also needs. The difference is the first one. DP keeps every sub-answer because it does not
know which choice wins. Greedy knows, so it keeps only one. That knowledge has to be earned,
and the usual way to earn it is an
[exchange argument](https://en.wikipedia.org/wiki/Greedy_algorithm#Correctness_proofs).
Take any optimal solution that does *not* make the greedy choice. Swap the greedy choice in.
Then show the result is no worse. If every such swap holds up, greedy is optimal. If one
fails, it is not.

The standard warning is [change-making](https://en.wikipedia.org/wiki/Change-making_problem).
With coins {1, 3, 4} and a target of 6, "take the largest coin that fits" gives 4 + 1 + 1,
three coins, but 3 + 3 uses two. Greedy is correct only for *canonical* coin systems, and
whether a system is canonical is a property I have to check, not assume. Two of the problems
below rest on canonical systems: Roman numerals and Fibonacci numbers.

## Shape 1 — the greedy choice is the answer

Here an exchange argument proves the greedy rule outright, and the code is just that rule in
a loop.

**Smallest primes first (69).** The ratio $n/\varphi(n)$ is $\prod p/(p-1)$ over the distinct
primes that divide $n$. Every factor is greater than 1, and the factor is largest for the
smallest $p$. So the exchange is easy: replacing any prime with a smaller unused prime makes
$n$ smaller and the ratio larger. The best $n$ under the bound is therefore the
[primorial](/topics/technique/primorial) that fits. The two versions of this one loop show a
point that comes up again and again: you must not commit a step that overshoots. Python
multiplies first and backs out on overflow:

```python
for prime_num in primes_generator():
    if (result := (result * prime_num)) > limit:
        result = result // prime_num
        break
```

C checks before it commits, so there is nothing to undo:

```c
long long next = result * candidate;
if (next > limit) break;
result = next;
```

In Python, commit-then-undo is harmless, because integers never overflow and the division is
exact. In C, check-first is the safer habit. If the bound sits near the limit of the integer
type, the speculative product is exactly the value that overflows.

**Largest denomination first (89).** Roman numerals form a canonical system once the
subtractive pairs (CM, CD, XC, XL, IX, IV) are counted as denominations of their own. Taking
the largest value that fits then produces the unique shortest numeral. The two languages
differ in the data structure, not the algorithm. Python scans an unordered `dict` for
`max(value ≤ number)` on every step. C keeps parallel arrays sorted largest-first and takes
the first match. C also adds up only `strlen` of each piece, because the problem asks how
many characters are saved, not for the numeral itself.

**Split the cheapest leaf (219).** A prefix-free code is the set of leaves of a binary tree.
Splitting a leaf of cost $c$ adds $c + 5$ to the total when a 0 costs 1 and a 1 costs 4. To
reach $n$ leaves at minimum cost, every split should therefore go to a cheapest leaf. This is
[Huffman coding](/topics/technique/huffman-coding) run backwards: it grows a tree instead of
merging weights. The textbook way to implement it is a min-heap with $n - 1$ pops, but that
is hopeless at $n = 10^9$. Leaves with the same cost are interchangeable, though, so the
solution keeps a *count* of leaves at each integer cost and sweeps the costs upwards, the
same order a heap would pop them in. That turns $n$ greedy steps into about 70 batched ones.
Python keys the counts by a `dict`. C uses a fixed `long long` array of 256 levels, with
plenty of headroom.

**Max out the smaller prime (347).** For a fixed power $q^b$, the product $p^a q^b$ increases
with $a$, so the best $a$ is the largest one that fits (`while val * p <= n: val *= p`). The
greedy step solves the inner problem. A short loop over $b$ then takes the maximum. This is a
good pattern to recognise: greedy is often correct for *one coordinate* once the others are
pinned, even when it is not correct for the whole problem.

## Shape 2 — greedy as the walk a recurrence follows

By [Zeckendorf's theorem](/topics/domain/zeckendorfs-theorem), the Fibonacci numbers are a
canonical system. Repeatedly subtracting the largest Fibonacci number that fits gives the
unique representation of $n$ as a sum of non-consecutive Fibonacci numbers. Nothing extra
enforces "non-consecutive". It comes for free: after taking $F_i$, the remainder is below
$F_{i-1}$, so the next term cannot be $F_{i-1}$.

Problems 297 and 692 do more than *use* the decomposition. They sum something over every
$n$ below a limit near $10^{17}$. The trick is that the numbers in the block $[F_i, F_{i+1})$
are exactly $F_i$ plus the numbers below $F_{i-1}$. That gives a block-sum recurrence over
Fibonacci indices. The greedy decomposition of the *limit* then tells the code which blocks
to add up. So the greedy loop runs once, on $N$, about 80 times instead of $10^{17}$ times.
In 297 the summand is the number of terms, and in 692 it is the smallest term, which by the
[Fibonacci nim](/topics/domain/fibonacci-nim) theorem is the winning first move. The skeleton
is the same in both:

```text
for i from top down:
    if F[i] <= rest:  total += block_sum(i) + contribution(i, rest);  rest -= F[i]
```

The two languages differ here only in integer width. Python's arbitrary-precision `int`
absorbs everything. 692's C fits in `long long` arrays of 96 entries. 297's C needs
`unsigned __int128` for its block sums, because the larger benchmark case goes past
$2^{64}$, and it has to print that number by hand since `printf` has no conversion for it.

## Shape 3 — greedy inside an exact search

When greedy is not optimal on its own, it can still do useful work inside a search that is.

**A seed for the bound (110).** The problem asks for the smallest $n$ with
$\tau(n^2) \ge 2T - 1$. An exchange argument fixes the *shape* of the answer. The primes must
be the smallest ones, with exponents that never increase, which is the structure of a
[highly composite number](/topics/domain/highly-composite-number). Swapping a larger exponent
onto a smaller prime keeps $\tau$ the same and shrinks $n$. That argument does not fix the
exponents themselves, so a [branch-and-bound](/topics/technique/branch-and-bound) DFS over
them is still needed. Greedy supplies its first incumbent: take the first $k$ primes, each to
the power 1, with $k$ just large enough that $3^k$ reaches the target. Because the search
starts with a real answer to beat, the "`new_n < best`" cut prunes from the very first leaf
instead of after a long dive. Python shares `best` through `nonlocal`. C keeps it at file
scope and guards every multiplication against overflow.

**Best level first, stop at the first hit (111).** To find the largest number of times a
digit $d$ repeats in a 10-digit prime, the search builds candidates level by level. It
starts at the most repeats and goes down, and it stops at the first level that contains a
prime. Strictly this is not a greedy *construction*. It is a greedy *search order*: levels
are tried best-first, so the first one that is feasible is optimal by definition, and all the
lower levels are never generated.

**A heuristic that only has to be good (152).** Meet-in-the-middle splits the items into two
halves and costs about the larger half's product of option counts. The split is made by
greedy load-balancing: sort the items by option count, largest first, and put each one in
whichever half has the smaller running product. This is the
[LPT rule](https://en.wikipedia.org/wiki/Longest-processing-time-first_scheduling) for
partitioning, and it is *not* optimal. It doesn't need to be. The answer stays exact either
way, and a split that is close to even keeps both tables small. Python and C share this
logic. They differ in the big-integer arithmetic underneath (`math.lcm` against a hand-rolled
384-bit type), not in the greedy step.

## How to reason about it

- **Write down the exchange before writing the loop.** If "swap the greedy choice into an
  optimal solution" does not obviously leave it no worse, try small cases by brute force
  first. 297's recurrence was checked against direct greedy decomposition for every $n$ up
  to 12345 before the solution trusted it.
- **Know when your system is canonical.** "Largest piece that fits" is correct for Roman
  numerals, Fibonacci numbers and powers of a base. It is not correct for arbitrary coin
  sets. If you can't show the system is canonical, use
  [dynamic programming](/topics/technique/dynamic-programming) or a
  [knapsack](/topics/technique/knapsack-problem) formulation.
- **Batch identical choices.** When the greedy choice comes in interchangeable copies, as with
  equal-cost leaves in 219 or whole Fibonacci blocks in 297 and 692, handle a whole class in
  one step. That is how the problems at $10^9$ and $10^{17}$ become a hundred iterations.
- **Use greedy as a bound when it is not the answer.** Even a suboptimal greedy solution is a
  real, feasible incumbent, and in a [branch-and-bound](/topics/technique/branch-and-bound)
  search a good incumbent is worth more than a clever cut.
- **Check before you commit in C.** The step that overshoots is often the one that overflows.
  Test `next > limit` (or `n > best / pe`) before writing the new value back.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ● [0692](/solutions/0692/) — Siegbert and Jo

<!-- /problems -->
