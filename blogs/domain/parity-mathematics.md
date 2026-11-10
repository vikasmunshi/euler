<!-- tags: [parity-mathematics] -->
<!-- status: final -->
# Parity (mathematics)

[Parity](https://en.wikipedia.org/wiki/Parity_(mathematics)) is whether an integer is even or odd —
its remainder mod 2. It is the coarsest thing you can know about a number, and that is its power:
it throws away almost everything, but what it keeps survives addition, multiplication and every
recurrence built from them. Across the problems below, parity does five distinct jobs. It exposes
a **pattern** you can skip along. It **splits** a problem into two cases of which one is trivial.
It is the **lowest binary digit**, which you can peel off before recursing on half the problem. It
is an **invariant** that forbids or forces an outcome. And it is a **filter** on a count — a state
bit in a DP, or a sign flip in a generating function. Seeing which job it is doing is usually the
step that turns brute force into a formula.

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

The split can also choose between two different parametrisations. Problem 764 solves
`16x² + y⁴ = z²` as a Pythagorean triple `(4x, y², z)` and branches on the parity of `y`. For odd `y`
the triple is primitive and `y²` is its odd leg `m² − n²`. For even `y` the condition
`gcd(x, y, z) = 1` forces `x` to be odd, which moves the square onto the even leg `2mn`. The two
branches give two unrelated two-parameter families. Parity also proves that the code's division is
exact, and here it says more than one bit. An odd number is `1 (mod 2)`, but its square is
`1 (mod 8)` and its fourth power `1 (mod 16)`. So for odd `a` and `b`, `(5a⁴ + 3b⁴)/8` is always an
integer. Knowing that a number is odd often fixes several of its low bits, not just the last one.

### The lowest binary digit: peel it off and halve

Parity is the last bit of `n`, and `n = 2⌊n/2⌋ + (n mod 2)`. When a problem's even part is a scaled
copy of the whole problem, you can recurse on `⌊n/2⌋` and finish in `log₂ n` steps.

Problem 333 counts partitions of `n` into terms `2^i 3^j` where no term divides another. The odd
terms are the pure powers of three, and any two of those divide one another, so a valid partition
holds **at most one** odd term. The parity of `n` says how many it holds. If `n` is even it holds
none, every term is even, and halving every term is a bijection onto the partitions of `n/2`. If `n`
is odd it holds exactly one, some `3^b`. The remaining terms are even, and halving them leaves a
partition of `(n − 3^b)/2` restricted to exponents `j < b`. Every right-hand index is below `n/2`,
so the table fills in doubling blocks `[2^k, 2^{k+1})`, each depending only on earlier blocks. That
dependence pattern is what lets a whole block be computed in one vectorised step.

Problem 539's elimination game halves itself literally. The first left-to-right pass deletes every
odd number, which leaves `2, 4, …, 2M` with `M = ⌊n/2⌋`, a mirrored copy of the game on `M` items.
So the survivor satisfies `P(n) = 2(M + 1 − P(M))`. The problem then asks for the **sum** of `P(k)`
up to `10^18`, and parity handles that too. The indices `2m` and `2m + 1` share the half `m`, so they
contribute the same term. The sum over `k ≤ n` therefore folds into a sum over `m ≤ n/2`, with a
one-term correction when `n` is even, and the pair `(P, S)` follows a single halving recurrence.
Pairing indices by parity is how you sum a halving recurrence without visiting its terms.

Problem 1003 does the same peeling in a base other than two. Its stone move turns two stones at
position `i` into one at `i + 1` and one at `i + 3`. That move conserves `Σ cᵢ xⁱ` whenever
`x² + x + 2 = 0`, and one root of that quadratic is, 2-adically, a [uniformizer](https://en.wikipedia.org/wiki/Uniformizer).
So every integer has a unique expansion in base `x` with digits 0 and 1, and at each step the
parity of the pile at position `i` is forced to be the next digit. This is the binary-expansion
loop — take `n mod 2`, subtract it, divide — with `x` in place of 2. Once you see that, you stop
simulating the process and enumerate digit patterns instead.

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

In two-player games the invariant is often **tempo**: who moves last. Problem 976's partizan strip
game reduces, once its canonical values are computed, to free moves, moves that cost a power of
two, and copies of `*`. Since `* + * = 0`, the star is its own inverse, so it lives in GF(2) too. A
sum of stars is `*` or `0` depending on the parity of how many there are. The winner then depends
only on the parity of the number of opening moves and the parity of the number of strips of length
`3 (mod 4)`.

Parity also splits a set into two classes that cannot interact. Problem 720 builds permutations
free of three-term arithmetic progressions by placing all odd values and all even values in separate
blocks: the middle of an AP is the average of its ends, and an odd and an even end have a
non-integer average, so no progression can straddle the seam.

### A filter on a count: a state bit, or `x → −x`

When a condition reads "occurs an odd number of times", you do not need the count — only its
parity, one bit per tracked symbol. Problem 974 carries a bitmask with one bit per odd digit,
flipped by XOR as each digit is placed; the target state is a fixed mask, and the DP over
`(position, mask, residues)` stays tiny where a vector of counts would explode. Problem 145 tracks
whether each column sum of `n + reverse(n)` is odd, together with the carry, which is a
parity-of-a-sum question by another name.

A generating function can filter by parity with no state at all. Substituting `x → −x` flips the
sign of exactly the odd-index terms, so `(f(x) + f(−x))/2` keeps the even terms and
`(f(x) − f(−x))/2` keeps the odd ones. This is the order-2 case of
[series multisection](https://en.wikipedia.org/wiki/Series_multisection). Apply it to `eˣ`, the
[exponential generating function](https://en.wikipedia.org/wiki/Exponential_generating_function)
of a symbol that may appear any number of times, and you get `cosh x` for "an even number of times"
and `sinh x` for "an odd number of times". Problem 520's simbers require each even digit to appear
an even number of times and each odd digit an odd number of times or not at all, so the strings
are counted by `cosh⁵x · (1 + sinh x)⁵`. The DP would carry ten parity bits; this product carries
none. It pays off a second time. Since `cosh` and `sinh` are combinations of `e^{±x}`, the product
is a short polynomial in `eˣ` and `e^{−x}`. Each `e^{kx}` contributes `kᴸ` strings of length `L`,
so a total over every length up to `2^39` becomes a handful of geometric series. Problem 976 uses
the same filter on an ordinary generating function. Once the game theory has reduced winning to
"the number of strips of length `3 (mod 4)` is even", the multisets that satisfy it are counted by
`½[(1 − x)^{−c} + (1 + x)^{−c}]`.

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
  and often factors; "probability of odd" usually does not. In a generating function the same
  move is `x → −x`. Try it before adding a parity bit to a DP's state.
- **Check whether the even case is a smaller copy.** If removing or halving the even part gives
  back the original problem, recurse on `⌊n/2⌋`. Sums over `n` then fold the same way, because
  `2m` and `2m + 1` share the half `m`.
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
- ● [0333](/solutions/0333/) — Special Partitions
- ○ [0430](/solutions/0430/) — Range Flips
- ○ [0502](/solutions/0502/) — Counting Castles
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0520](/solutions/0520/) — Simbers
- ● [0539](/solutions/0539/) — Odd Elimination
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ○ [0611](/solutions/0611/) — Hallway of Square Steps
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0859](/solutions/0859/) — Cookie Game
- ● [0868](/solutions/0868/) — Belfry Maths
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0976](/solutions/0976/) — XO Game
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ● [1003](/solutions/1003/) — Lonely Singles

<!-- /problems -->
