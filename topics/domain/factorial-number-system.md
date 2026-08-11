<!-- tags: [factorial-number-system] -->
<!-- status: final -->
# Factorial number system

The [factorial number system](https://en.wikipedia.org/wiki/Factorial_number_system) — factoradic,
for short — is a positional numeral system whose place values are $1!, 2!, 3!, \dots$ instead of
powers of a fixed base. That sounds like a curiosity until you notice what it counts: there are
exactly $n!$ permutations of $n$ symbols, and a factoradic numeral with $n-1$ digits covers exactly
$0 \dots n!-1$. The system is the natural coordinate grid for permutations. Every problem below is
really the same move — stop enumerating an astronomically long list and start doing arithmetic on
positions in it.

## The idea

Write a non-negative integer as

$$N = d_k \cdot k! + d_{k-1} \cdot (k-1)! + \dots + d_1 \cdot 1!, \qquad 0 \le d_i \le i.$$

The digit cap is the whole point: place $i$ carries at $i+1$, not at some fixed radix, because
$(i+1) \cdot i! = (i+1)!$ is exactly the next place value. That cap makes the representation unique,
and it makes the range come out flush — since $\sum_{i=1}^{k} i \cdot i! = (k+1)! - 1$, the $k$-digit
factoradics are precisely the integers $0$ through $(k+1)!-1$, with nothing left over and nothing
double-counted. Compare a decimal system where the digits ran $0\dots9$ but the place values were
$1, 10, 200, 6000$: you would have gaps and collisions. Factorials are the unique growth rate that
fits a mixed radix of $2, 3, 4, \dots$ snugly.

Converting is the usual repeated-division loop, only with a rising divisor:

```python
def to_factoradic(n: int) -> list[int]:
    """Digits d_1, d_2, ... (least significant first); d_i < i + 1."""
    digits = []
    radix = 2
    while n:
        n, d = divmod(n, radix)
        digits.append(d)
        radix += 1
    return digits
```

Going the other way, never build the factorials. Mixed-radix [Horner
evaluation](https://en.wikipedia.org/wiki/Horner%27s_method) walks from the most significant digit
down, multiplying by the falling radix — `acc = acc * i + d` — so every intermediate stays the size
of the answer rather than the size of $k!$. That single line is what makes the technique survive
under a modulus, and it is the last step of two of the solutions below.

## Permutations: the Lehmer code

Fix the $n$ symbols in sorted order and read a factoradic numeral as instructions: *take the
$d$-th remaining symbol, cross it off, repeat*. That is a bijection between $\{0, \dots, n!-1\}$ and
the permutations, and — because the leading digit selects the whole leading block of $(n-1)!$
consecutive permutations — it is order-preserving. The numeral is the permutation's **lexicographic
rank**, and its digit string is the [Lehmer code](https://en.wikipedia.org/wiki/Lehmer_code): digit
$L_i$ is how many symbols to the right of position $i$ are smaller than the one at position $i$.

The three-symbol case fits in a table, and is worth internalising because everything larger is the
same picture:

| Rank | Factoradic ($2!\,1!$) | Permutation of `0 1 2` |
|-----:|:---------------------:|:----------------------:|
| 0 | `0 0` | `012` |
| 1 | `0 1` | `021` |
| 2 | `1 0` | `102` |
| 3 | `1 1` | `120` |
| 4 | `2 0` | `201` |
| 5 | `2 1` | `210` |

**Unranking** — rank to permutation — is problem 24 in one `divmod`. The lead symbol is the rank
divided by $(n-1)!$; the remainder is the rank of the rest, recursively:

```python
def recursive_solution(digits: str, permutation_number: int) -> str:
    """Return the 1-based permutation_number-th lexicographic permutation of the sorted digits."""
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, math.factorial(len(digits) - 1))
    return digits[current] + recursive_solution(
        digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1
    )
```

Ten digits, a millionth permutation, ten divisions — no list of $3628800$ strings is ever built.

**Ranking** — permutation to rank — is the same bijection run backwards, and it is where the harder
problems live. Problem 720 asks for the position of the lexicographically first permutation of
$\{1, \dots, 2^{25}\}$ with no three-term arithmetic progression among its values, modulo
$10^9+7$. Nothing about that permutation can be found by search, and its rank is a number with
millions of digits. What rescues it is that the permutation has a recursive construction (split the
values by parity, and an AP can never straddle the two classes), and that the *Lehmer code* of the
doubled permutation is a closed-form rewrite of the Lehmer code of the half-sized one. So the
solution never materialises a permutation and never counts an inversion: it doubles the factoradic
digits $\log N$ times, then Horner-folds them under the modulus. Working in Lehmer coordinates
rather than in permutations is what turns an $O(N \log N)$ Fenwick-tree inversion count into a
linear pass.

Problem 868 is the reminder that "factoradic digits ↔ permutation" is not one map but a family. Its
bell-ringing rule is the
[Steinhaus–Johnson–Trotter](https://en.wikipedia.org/wiki/Steinhaus%E2%80%93Johnson%E2%80%93Trotter_algorithm)
algorithm, which lists permutations as a Gray code — each step a single adjacent swap — so the
number of swaps to reach a target *is* its rank in SJT order. SJT recurses exactly like the
factorial system does: the largest element sweeps through all $n$ positions between consecutive
arrangements of the smaller $n-1$. Each level therefore contributes one factoradic digit, and the
rank is the same Horner fold, `rank = rank * level + offset`. The only difference from
lexicographic order is how the digit is read: SJT alternates its sweep direction, so at each level
the offset is measured from the left or the right according to the parity of the rank accumulated so
far. Same numeral system, same fold, one parity test — and a completely different ordering.

## Not just permutations: the shortest sum of factorials

The other half of the tag has nothing to do with orderings. Because each place value divides the
next, $\{1!, 2!, \dots, k!\}$ is a *canonical* coin system: the greedy algorithm — take as many $k!$
as fit, then as many $(k-1)!$, and so on — produces the factoradic representation, and that
representation minimises the number of coins. The proof is the digit cap again. Any other
representation of the same value must use $c_i \ge i+1$ copies of some $i!$, and replacing $i+1$ of
them by a single $(i+1)!$ strictly shortens it. Greedy optimality is not a general property of coin
systems; it is a property of this divisibility chain.

That is the engine of problem 254, which chains "sum of factorials of the digits" with "sum of
digits of the result" and asks for the smallest preimage. Since a digit sum is blind to order and
$0! = 1!$, the question *what is the smallest $n$ with $f(n) = F$?* collapses to *what is the
shortest way to write $F$ as $\sum_{d=1}^{9} c_d \cdot d!$?* — the factoradic expansion of $F$,
directly. Better still, the digits below the top place are capped, so their contribution to the
length is bounded by $1 + 2 + \dots + 8 = 36$ regardless of how large $F$ grows. That bound is
monotone in $F$, which converts an unbounded search into a scan over a window of fixed width. The
target itself has about $1.9 \times 10^{10}$ decimal digits and is never constructed; the solution
carries only its factoradic digit counts.

## How to reason about it

Reach for the factorial number system when a problem talks about *the $k$-th* item of a permutation
listing, or *the position of* a given permutation, over a domain too large to enumerate. The payoff
is random access: rank and unrank in $O(n)$ time (or $O(n \log n)$ with a Fenwick tree, if you must
count inversions from a raw permutation) into a list of length $n!$. Reach for it, separately,
whenever you need a value written as the fewest possible factorials — there, greedy is provably
right.

Things that bite, in rough order of how often they do:

- **Off-by-one on the rank.** Factoradic ranks are 0-based; problem statements usually count from
  1. Problem 24's solution subtracts 1 before the `divmod` and adds it back on the recursive call;
  problem 720's adds 1 at the very end. Pick a convention, write it in the docstring, and check it
  against the worked example the statement gives you.
- **Two digit-indexing conventions.** "Digit at place $i$, weight $i!$, cap $i$" and "digit at
  offset $i$ from the left of an $n$-permutation, weight $(n-1-i)!$" are the same numeral read from
  opposite ends. Mixing them silently reverses your permutation.
- **Materialising factorials.** $2^{25}!$ has no representation you want. If the answer is wanted
  modulo something, fold with Horner and stay small; if it is not, at least avoid recomputing
  $k!$ inside the loop.
- **The trailing digit is always zero.** The last symbol is forced, so $L_n = 0$ always. Some
  formulations write $n$ digits, some $n-1$; both are correct and they differ by nothing.
- **Repeated symbols break the bijection.** Factoradic ranks permutations of *distinct* items. A
  multiset needs multinomial place values, and choosing a subset rather than an ordering needs the
  sibling scheme, the [combinatorial number
  system](https://en.wikipedia.org/wiki/Combinatorial_number_system).

One last property worth keeping in your pocket: the digit sum of a Lehmer code is the permutation's
[inversion](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics)) count, which is also the
minimum number of adjacent transpositions that sort it. So the same numeral answers "where is this
permutation in the list?" through its value and "how disordered is it?" through its digits.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0868](/solutions/0868/) — Belfry Maths

<!-- /problems -->
