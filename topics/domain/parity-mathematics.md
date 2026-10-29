<!-- tags: [parity-mathematics] -->
<!-- status: final -->
# Parity (mathematics)

[Parity](https://en.wikipedia.org/wiki/Parity_(mathematics)) is whether an integer is even or odd —
its remainder mod 2. It is the coarsest thing you can know about a number, and that is its power:
it throws away almost everything, but what it keeps survives addition, multiplication and every
recurrence built from them. Across the problems below, parity does four distinct jobs — it exposes
a **pattern** you can skip along, it **splits** a problem into two cases of which one is trivial,
it is an **invariant** that forbids or forces an outcome, and it is a cheap **state bit** in a
counting DP. Seeing which job it is doing is usually the step that turns brute force into a formula.

## The idea

Reducing mod 2 is a ring [homomorphism](https://en.wikipedia.org/wiki/Ring_homomorphism) from the
integers onto the two-element field [GF(2)](https://en.wikipedia.org/wiki/GF(2)): you can reduce
first and compute afterwards, and the answer agrees.

| `+`  | even | odd  |     | `×`  | even | odd  |
|------|------|------|-----|------|------|------|
| even | even | odd  |     | even | even | even |
| odd  | odd  | even |     | odd  | even | odd  |

Addition is [XOR](https://en.wikipedia.org/wiki/Exclusive_or) and multiplication is AND. Two
corollaries carry most of the weight. First, `(a + b)/2` and `(a − b)/2` are integers **exactly
when `a` and `b` have the same parity** — the condition behind every "halve the sum or difference"
reparametrisation. Second, `(−1)^n` is the parity of `n` written multiplicatively, which turns
"is it odd?" into an expectation or a product you can actually compute.

### A pattern to skip along

Because parity is a homomorphism, the parity sequence of any integer recurrence is itself a
recurrence over two values — so it is eventually periodic, and short. In
[Problem 2](/solutions/0002/) the Fibonacci parities run odd, even, odd, odd, even, … with period
three (odd + odd = even, then even + odd = odd twice). Knowing that every third term is even, the
solution never tests evenness at all; it expands the recurrence three steps to get one that jumps
straight from even term to even term:

```python
even_fib_a, even_fib_b = (2, 8)
while even_fib_a < max_limit:
    yield even_fib_a
    even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)
```

The same reasoning, used defensively, is what makes [Problem 100](/solutions/0100/)'s integer
divisions safe: the Pell-style recurrence maps odd pairs to odd pairs, so the `(x + 1)/2` it later
takes is always exact. A parity argument is often the proof that some division in your code never
truncates.

### A case split where one case collapses

Many expressions behave completely differently for even and odd inputs, and frequently one branch
is trivial. In [Problem 12](/solutions/0012/), exactly one of `n` and `n + 1` is even, so the
triangle number `n(n+1)/2` factors into two **coprime** halves — the `/2` lands on whichever factor
is even — and divisor counts multiply across them. In Problems 120 and 123, expanding
`(a − 1)^n + (a + 1)^n` mod `a²` by the binomial theorem leaves only two terms: for even `n` the
linear terms cancel and the remainder is the constant `2`; for odd `n` the constants cancel and the
remainder is linear in `n`. Every even exponent is discarded on sight, and the exponential-looking
computation becomes a single multiplication.

Problem 512 has the same collapse and then a second use of parity. Its sum of `φ(n^i)` taken mod
`n + 1` reads `n ≡ −1`, so the terms alternate in sign and cancel in pairs. Even `n` contributes
nothing and odd `n` contributes `φ(n)`, which leaves a totient sum over the **odd** `n ≤ N` only.
Filtering a fast summatory function by parity looks like it needs a new algorithm, but the even
half has a recursive form. Since `φ(2m)` is `φ(m)` for odd `m` and `2φ(m)` for even `m`, the
even-index sum `E(N)` equals `Φ(N/2) + E(N/2)`. Unrolling it gives

    odd-only sum = Φ(N) − Φ(⌊N/2⌋) − Φ(⌊N/4⌋) − Φ(⌊N/8⌋) − …

Every `⌊N/2^k⌋` is a floor quotient that the standard summatory-totient recursion evaluates anyway,
so the restriction costs about `log₂ N` table lookups. The same trick applies whenever `f(2m)` is a
simple function of `f(m)` and the parity of `m`: to keep only the odd indices, peel off the factor
of two one level at a time.

Same-parity constraints are the geometric version of this. Problem 174's square laminae need a
border of whole thickness `(outer − hole)/2`, so the outer and hole sides must share parity; Problem
142 recovers `y` and `z` from differences of squares divided by two, so each square-root pair must
share parity. Building the condition into the loop — step by 2, start at the matching parity —
halves the search and removes a filter.

### An invariant that forbids or forces

Where an operation changes some quantity by a fixed parity, that quantity's parity is an
[invariant](https://en.wikipedia.org/wiki/Invariant_(mathematics)), and invariants decide
reachability without search — the classic instance is the [15 puzzle](https://en.wikipedia.org/wiki/15_puzzle),
whose unsolvable half is ruled out by a permutation's sign. Problem 980 is that argument directly:
read each letter as a unit of the [quaternion group](https://en.wikipedia.org/wiki/Quaternion_group),
and each string operation changes the length by a known amount and the letters' product by a known
sign, so the parity of the number of steps used to build a string is fixed by the string alone,
and "can it be built in an even number of steps?" becomes a lookup. Problem 951 asks whether a card
game is fair, which is a question about the parity of the number of turns; rewriting it as
`E[(−1)^T] = 0` turns a probability into a signed sum that factors over the deck's runs. Problems
331 and 430 are flipping games, and flipping twice undoes a flip, so a disk's colour depends only on
the parity of how often it was flipped. In Problem 331 that makes the board a system of linear
equations over GF(2), just like [Lights Out](https://en.wikipedia.org/wiki/Lights_Out_(game)); in
Problem 430 the flips are random, so each disk's expected colour reduces to the probability that it
was flipped an odd number of times — again a job for `(−1)^n`. Problem 868's bell-ringing
order ([Steinhaus–Johnson–Trotter](https://en.wikipedia.org/wiki/Steinhaus%E2%80%93Johnson%E2%80%93Trotter_algorithm))
sweeps left or right according to the parity of the rank built up so far, which is what lets a
rank be computed instead of simulated.

Parity also splits a set into two classes that cannot interact. Problem 720 builds permutations
free of three-term arithmetic progressions by placing all odd values and all even values in separate
blocks: the middle of an AP is the average of its ends, and an odd and an even end have a
non-integer average, so no progression can straddle the seam.

### A state bit in a counting DP

When a condition reads "occurs an odd number of times", you do not need the count — only its
parity, one bit per tracked symbol. Problem 974 carries a bitmask with one bit per odd digit,
flipped by XOR as each digit is placed; the target state is a fixed mask, and the DP over
`(position, mask, residues)` stays tiny where a vector of counts would explode. Problem 520's
simbers impose exactly this kind of per-digit parity condition, over all ten digits. Problem 145 tracks whether
each column sum of `n + reverse(n)` is odd, together with the carry, which is a parity-of-a-sum
question by another name.

Counting **odd coefficients** is the same idea applied to polynomials. Reducing mod 2, the binomial
coefficient `C(a, j)` is odd exactly when the binary digits of `j` are a subset of those of `a`
([Lucas's theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem)); that is why Pascal's
triangle mod 2 is the [Sierpiński triangle](https://en.wikipedia.org/wiki/Sierpi%C5%84ski_triangle).
Problem 242 uses it to decide the parity of a subset count without computing the count; Problem 588
asks the same question of a five-term polynomial's powers, where the mod-2
[Frobenius](https://en.wikipedia.org/wiki/Frobenius_endomorphism) identity `p(x)² ≡ p(x²) (mod 2)`
is the natural lever: it lets the exponent be taken apart one binary digit at a time.

## How to reason about it

- **Reach for parity when the problem says "odd" or "even"** — and also when it says "toggle",
  "flip", "alternate", "swap", or "take turns". Any operation that is its own inverse lives in GF(2).
- **Tabulate parities first.** Writing out the parity of the first dozen terms of a sequence costs
  a minute and usually reveals the period, or the branch that collapses.
- **Parity is necessary, rarely sufficient.** An invariant mismatch proves something impossible; a
  match only proves it is not ruled out. Problem 331 still has to minimise over the boards that pass
  the parity test.
- **Prefer `(−1)^n` over case analysis when you need to sum or average.** A signed sum is linear
  and often factors; "probability of odd" usually does not.
- **Mind the implementation.** In C, `-3 % 2` is `-1`, not `1`, so test oddness with `n & 1` (or
  `n % 2 != 0`). For a multiset of parities, an integer bitmask with XOR beats an array of
  counters.

## Further reading

- [Parity of a permutation](https://en.wikipedia.org/wiki/Parity_of_a_permutation) — the invariant
  behind sliding puzzles and bell-ringing.
- [Invariant (mathematics)](https://en.wikipedia.org/wiki/Invariant_(mathematics)) — parity is the
  simplest of many.
- [OEIS A001316](https://oeis.org/A001316) — Gould's sequence, the number of odd entries in each row
  of Pascal's triangle.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0331](/solutions/0331/) — Cross Flips
- ○ [0430](/solutions/0430/) — Range Flips
- ○ [0502](/solutions/0502/) — Counting Castles
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0520](/solutions/0520/) — Simbers
- ○ [0539](/solutions/0539/) — Odd Elimination
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ○ [0611](/solutions/0611/) — Hallway of Square Steps
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ○ [0859](/solutions/0859/) — Cookie Game
- ● [0868](/solutions/0868/) — Belfry Maths
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ○ [1003](/solutions/1003/) — Lonely Singles

<!-- /problems -->
