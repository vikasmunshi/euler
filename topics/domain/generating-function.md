<!-- tags: [generating-function] -->
<!-- status: final -->
# Generating function

A [generating function](https://en.wikipedia.org/wiki/Generating_function) is a whole infinite
sequence written as one power series: given `a₀, a₁, a₂, …`, its ordinary generating function is
`A(x) = Σ aₙ·xⁿ`. Nothing is computed by that move — it is a change of notation. What it buys is
that *structure on the sequence becomes algebra on the function*, and algebra is something you can
do in closed form. The problems below all reach for it because each is a counting question whose
search space is astronomically larger than its answer, and a generating function is the standard
way to compute the answer without visiting the space.

## The idea

Herbert Wilf's line — a generating function is "a clothesline on which we hang up a sequence of
numbers for display" — is exactly right, and the display is not the point; the clothesline is. Two
rules do most of the work:

- **Independent choices multiply.** If part A contributes `A(x)` and part B contributes `B(x)`, and
  the two do not constrain each other, the pair contributes `A(x)·B(x)` — because `xⁱ` from one
  and `xʲ` from the other land together in `x^(i+j)`. Coefficient-wise this is
  [convolution](/topics/technique/convolution).
- **Alternatives add.** Mutually exclusive cases contribute the sum of their series.

From those two, most counting encodings write themselves. "Each prime is in the subset or it isn't,
and its presence adds `p` to the total" is the factor `1 + x^p`, one per prime; the product's
coefficient of `x^s` is the number of subsets summing to `s` (problem 249). "Each slot holds 0, 1
or 2, and holding 1 can be realised `w` ways" is `1 + w·x + x²` (problem 743). "Part size `k` may be
used any number of times" is `1/(1 - x^k)`, and the product over all `k` is the partition
generating function — the object behind problem 78, and behind its variants with restricted parts
(problem 614's distinct summands, problem 890's powers of two).

Then you have to get a number back out, and that is the part with real technique in it.

**Extract by dynamic programming.** Multiplying the running polynomial by `1 + x^p` is the array
update `c[s] += c[s-p]`, which is why 0/1 knapsack and subset-sum counting are the same thing as a
generating function expanded left to right. Problem 249 is this on a table of 1.5 million slots,
reduced mod 10¹⁶ throughout; the series is never written down, only walked.

**Extract by a closed form.** Sometimes you need one coefficient, not the array. Problem 743 needs
`[x^k](1 + b·x + x²)^k` at *k* = 10⁸ — a central trinomial coefficient with a multinomial closed
form, computable as one O(*k*) loop with no array at all. Recognising the polynomial is what buys
the shortcut; the generating function is the *model*, not the *method*.

**Extract by an identity.** The partition generating function `∏ 1/(1 - x^k)` has a reciprocal with
almost all coefficients zero — [Euler's pentagonal number theorem](https://en.wikipedia.org/wiki/Pentagonal_number_theorem) —
and that sparsity turns into a recurrence with only O(√*n*) terms:

```python
partitions = [1]
for n in itertools.count(1):
    partition_value = 0
    k = 1
    while True:
        pent_k1 = pentagonal(k)     # k(3k-1)/2
        pent_k2 = pentagonal(-k)    # k(3k+1)/2
        if pent_k1 > n:
            break
        partition_value += (-1) ** (k - 1) * partitions[n - pent_k1]
        if 0 < pent_k2 <= n:
            partition_value += (-1) ** (k - 1) * partitions[n - pent_k2]
        k += 1
    partition_value %= divisor
    partitions.append(partition_value)
```

That is the whole of `solutions/public/p0078/`. `p(n)` grows like `exp(π√(2n/3))`, so enumeration is
never on the table; the recurrence gets to *n* = 55,374 in milliseconds. Note the reduction on the
last line: the question only asks about divisibility, so nothing ever needs to be a large integer.

## Two flavours

**Ordinary** generating functions (`Σ aₙxⁿ`) count *unlabelled* things — how many subsets, how many
partitions, how many ways to hit a total. **Exponential** generating functions
([EGF](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function_(EGF)),
`Σ aₙxⁿ/n!`) count *labelled* things, where the positions are distinguishable and rearrangements
are distinct. Problem 172 — 18-digit numbers with no digit used more than three times — is the
canonical EGF: one digit usable 0–3 times contributes `1 + x + x²/2! + x³/3!`, ten digits multiply,
and the answer is `n![xⁿ]` of the tenth power. The factorials are doing the arranging. In practice
you can dodge them entirely: fold in one digit at a time with `dp'[t] = Σ_c C(t,c)·dp[t-c]`, where
the binomial *is* the EGF's `t!/(c!(t-c)!)` made concrete — integer arithmetic all the way, no
rationals.

The rule of thumb: if swapping two chosen items gives a different object, you want an EGF.

## Rational generating functions

A sequence satisfying a linear recurrence of order *r* has a generating function that is a ratio of
two polynomials of degree ≤ *r*. Multiply the series by the recurrence's characteristic polynomial
and nearly everything telescopes: `Σ Fₖxᵏ · (1 - x - x²)` collapses to `x`, so the Fibonacci OGF is
`x/(1 - x - x²)`. That one line is the hinge of problems 137 and 140, which ask for which *rational*
`x` the series takes an integer value — meaningless as an infinite sum, immediate once it is a
rational function. Setting it equal to `k` clears to a quadratic, rationality becomes "the
discriminant is a perfect square", and the search collapses into a
[Pell equation](/topics/domain/diophantine-equation) whose solutions are generated by a recurrence.
An infinite search over candidates becomes an O(*n*) walk along an orbit.

This is the direction worth internalising: **a generating function is a bridge to a different
subject**. Rational ⇒ linear recurrence ⇒ Diophantine machinery. The series itself is scaffolding
you take down afterwards.

## Working modulo something

Two different reductions show up, and they are not the same trick.

**Reduce the coefficients.** When the problem asks for the answer mod *m*, every coefficient can be
held mod *m* throughout — sound as long as the extraction uses only `+` and `×`. Watch for
subtraction in a signed recurrence: Euler's pentagonal sum alternates, and in C the running total
can go negative, so `((v % m) + m) % m` rather than a bare `%`. Python's `%` already returns
non-negative, which is exactly the kind of difference that makes a C port disagree with its Python
original.

**Reduce the exponents.** If only the total *mod m* matters, work in `ℤ[x]/(xᵐ - 1)` — the
[group algebra](https://en.wikipedia.org/wiki/Group_ring) of `ℤ/mℤ` — where `xᵐ = 1` makes exponents
wrap by themselves and the array never exceeds *m* slots. Problem 250 counts subsets of
{1¹, …, 250250²⁵⁰²⁵⁰} with sum divisible by 250: the elements collapse to a census over 250
residues, the product `∏ (1 + x^r)^{c_r}` lives in 250 slots regardless of how astronomically large
the true coefficients are, and the answer is read off a single slot. A 2²⁵⁰²⁵⁰-element problem
becomes an array of 250 machine words.

## How to reason about it

- **Convergence is usually not your problem.** Most of this is *formal* power series: `x` is a
  bookkeeping marker, never evaluated, and questions of radius of convergence do not arise. The
  exception is when the problem genuinely evaluates the series at a real `x` — problems 137, 140 and
  722 do — and then convergence and numerical conditioning are back on the table.
- **Truncate early.** You almost never need the whole product. Cap the degree at the largest total
  you care about and drop everything above it on every multiply; that cap is often the difference
  between feasible and not.
- **Cost is degree × factors.** The straightforward expansion is O(*D*) per factor over a
  degree-*D* array. Fine at a few million slots (problem 249 runs ~10⁹ additions this way, which is
  the scale where array-level arithmetic wins and per-element Python loops lose). Only past that
  does an [FFT](https://en.wikipedia.org/wiki/Convolution_theorem)-based multiply, or an NTT modulo
  a prime, start to pay.
- **Look for the structure before the array.** The best outcomes here are not faster expansions but
  escapes from expanding at all: a sparse reciprocal (problem 78), a closed-form coefficient
  (problem 743), a periodicity that makes the input census O(1) (problem 250), a rational form that
  hands the problem to number theory (problems 137, 140). Write the generating function down first;
  then look hard at what it *is* before you start multiplying.

The tell is a counting question whose brute force is a product of independent ranges, or a sequence
defined by a recurrence you cannot see past. Write one factor per independent choice, multiply, and
ask which coefficient you actually need.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ○ [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ○ [0519](/solutions/0519/) — Tricoloured Coin Fountains
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ○ [0648](/solutions/0648/) — Skipping Squares
- ○ [0677](/solutions/0677/) — Coloured Graphs
- ○ [0709](/solutions/0709/) — Even Stevens
- ○ [0722](/solutions/0722/) — Slowly Converging Series
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0768](/solutions/0768/) — Chandelier
- ○ [0851](/solutions/0851/) — SOP and POS
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0890](/solutions/0890/) — Binary Partitions
- ○ [0929](/solutions/0929/) — Odd-Run Compositions

<!-- /problems -->
