<!-- tags: [partition-number-theory] -->
<!-- status: final 2026-10-14T11:44Z -->
# Partition (number theory)

A [partition](https://en.wikipedia.org/wiki/Partition_(number_theory)) of *n* is a way of writing
*n* as a sum of positive integers where order does not matter: 4 = 3 + 1 = 2 + 2 = 2 + 1 + 1 =
1 + 1 + 1 + 1, five ways in all, so p(4) = 5. The idea keeps coming back because "how many ways
can I make this total?" is one of the most natural counting questions there is, and Project Euler
asks it again and again with a different restriction on the parts. Problems 31, 76, 77 and 78 are
the same question four times over — British coins, any summands, prime summands, and "how large
does p(n) get" — and working through them in order shows both the standard algorithm and the
point where it stops being the right one.

## One question, four restrictions

| Problem | Parts allowed | Asked for | Size |
|---|---|---|---|
| [31](/solutions/0031/) | the eight UK coins | ways to make 200p | target fixed and small |
| [76](/solutions/0076/) | 1 … 99 | ways to write 100 as a sum of at least two integers | p(100) − 1 |
| [77](/solutions/0077/) | primes | first *n* with more than 5000 prime partitions | target unknown, small |
| [78](/solutions/0078/) | any positive integer | first *n* with p(n) divisible by one million | target unknown, large |

The "coins" in Problem 78's title are a red herring: piles of coins are just parts, and every part
size is allowed, so it is plain p(n). Likewise Problem 76 is p(100) with the single partition
"100" subtracted, because a sum needs at least two terms.

## The knapsack DP

Fix the set of allowed parts and count by building totals up from zero. Let `ways[i]` be the
number of partitions of *i* using the parts seen so far. Adding a new part *c* means every
partition of *i* either uses no *c* (already counted) or uses at least one *c* — and removing one
*c* leaves a partition of *i* − *c* that may still contain more *c*'s. Hence
`ways[i] += ways[i − c]`, swept upward. This is the counting form of the
[unbounded knapsack](https://en.wikipedia.org/wiki/Knapsack_problem#Unbounded_knapsack_problem),
and Problem 31's public solution is the whole algorithm:

```python
result = [1] + [0] * target_amount
for coin in coins:
    for i in range(coin, target_amount + 1):
        result[i] += result[i - coin]
```

Two details carry all the correctness:

- **Loop order decides what you count.** Parts outer, totals inner counts *combinations* — each
  multiset once, because parts are introduced in a fixed order. Swap the loops and the same
  update counts *compositions* (1 + 2 and 2 + 1 separately), which is a different and much larger
  number. This is the single most common bug in coin-change code.
- **Sweep direction decides reuse.** The upward sweep lets `result[i − coin]` already include
  this coin, so it can be used any number of times. Sweep downward and each part is used at most
  once — partitions into *distinct* parts, the 0/1 knapsack.

The DP is O(|parts| · N) time and O(N) space, and it takes any part set at all. That makes
Problems 76 and 77 the same program as 31 with different coins: parts 1 … 99 for 76, the primes
up to some bound for 77. The repository's solutions to those two happen to use the equivalent
top-down form — a memoised count(remaining, largest part allowed), where passing the chosen part
down as the new ceiling forces non-increasing parts and so counts each multiset once. Same table,
filled lazily; the lazy form is convenient in 77 because it lets the search extend *n* without
fixing a bound in advance. (The enumerating variants that build every partition as a list are kept
only as a baseline: the counts grow far too quickly for materialisation to survive past *n* ≈ 50.)

## When the DP gives way: the pentagonal recurrence

Problem 78 breaks the DP on two counts. The target is unknown — the answer is in the tens of
thousands — and with every part size allowed, |parts| ≈ N, so the knapsack costs O(N²) and must
be rerun (or pre-sized) for a bound you do not know. What is needed is a way to get p(n) from the
smaller values *directly*, so the search can just keep going.

[Euler's pentagonal number theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem)
provides it. The generating function of p(n) is ∏ 1/(1 − xᵏ), and the reciprocal of that product
collapses to an extremely sparse series:

    ∏ (1 − xᵏ) = Σ (−1)ᵏ x^g(k),   k = 0, ±1, ±2, …,   g(k) = k(3k − 1)/2

The exponents g(k) are the generalised pentagonal numbers 1, 2, 5, 7, 12, 15, 22, 26, …
([OEIS A001318](https://oeis.org/A001318)). Multiplying both generating functions gives 1, and
reading off the coefficient of xⁿ gives the
[recurrence](https://en.wikipedia.org/wiki/Partition_function_(number_theory)#Recurrence_relations):

    p(n) = p(n−1) + p(n−2) − p(n−5) − p(n−7) + p(n−12) + p(n−15) − …

with signs in pairs (+ +, − −, …) and p(negative) = 0. Since g(k) grows quadratically, only about
2√(2n/3) terms are non-zero, so each value costs O(√n) and the first N values cost O(N^1.5). The
public solution to Problem 78 builds the table bottom-up:

```python
while True:
    pent_k1 = pentagonal(k)
    pent_k2 = pentagonal(-k)
    if pent_k1 > n:
        break
    partition_value += (-1) ** (k - 1) * partitions[n - pent_k1]
    if 0 < pent_k2 <= n:
        partition_value += (-1) ** (k - 1) * partitions[n - pent_k2]
    k += 1
partition_value %= divisor
```

The last line is the other half of the trick. p(n) grows like
e^(π√(2n/3)) / (4n√3) ([Hardy–Ramanujan](https://en.wikipedia.org/wiki/Partition_function_(number_theory)#Approximation_formulas)),
so near the answer it has hundreds of digits. Because the recurrence uses only addition and
subtraction, it is valid modulo any *m*: store p(n) mod 10⁶ and every value fits in a machine
word, which is what lets the C translation work at all. Problem 76's main solution uses the same
recurrence top-down (memoised recursion), which is overkill at n = 100 but shows the two
approaches agree.

## How to reason about it

- **Restricted parts → knapsack.** If the problem names the parts (coins, primes, at most *k*
  parts, distinct parts), the DP is the default: it is simple, exact, and indifferent to what the
  part set looks like.
- **All parts, large or open-ended *n* → pentagonal recurrence.** The theorem is a statement
  about the full product ∏(1 − xᵏ); it does not survive restricting the parts, so it is not an
  option for Problem 77. (Prime partitions have their own route, via the
  [Euler transform](https://mathworld.wolfram.com/EulerTransform.html) and the sum of distinct
  prime factors — but at Problem 77's size the DP is already instantaneous.)
- **Divisibility or "last digits" questions → work mod *m* from the start.** Both methods are
  pure addition, so reduce every entry; only the final comparison needs care.
- **Sign handling in C.** The pentagonal sum subtracts, so a running value mod *m* can go
  negative; add *m* before taking `%`, or keep the sum in a signed type and normalise once per *n*.
- **Off-by-one on the definition.** Check whether the trivial partition (*n* itself) counts — it
  does not in Problem 76 — and whether p(0) = 1, which both methods need as their base case.

The harder problems on this tag build on the same two pieces rather than replacing them. The
private [Problem 181](/solutions/0181/) partitions *pairs* — two colours of object — which is the
knapsack lifted to a two-dimensional table indexed by (black, white) counts; others, such as
[Problem 772](/solutions/0772/) on bounded partitions or [Problem 374](/solutions/0374/) on the
best product of distinct parts, restrict the parts in ways the generating function still
describes, so the first move on any of them is the same: write down which parts are allowed, and
decide whether a DP over totals or a recurrence on the generating function fits.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0031](/solutions/0031/) — Coin Sums
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ○ [0333](/solutions/0333/) — Special Partitions
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0629](/solutions/0629/) — Scatterstone Nim
- ○ [0688](/solutions/0688/) — Piles of Plates
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0859](/solutions/0859/) — Cookie Game
- ○ [0890](/solutions/0890/) — Binary Partitions
- ○ [0922](/solutions/0922/) — Young's Game A
- ○ [0939](/solutions/0939/) — Partisan Nim
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
