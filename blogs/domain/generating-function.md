<!-- tags: [generating-function] -->
<!-- status: final 2026-11-09T17:05Z -->
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
  [convolution](/blogs/technique/convolution).
- **Alternatives add.** Mutually exclusive cases contribute the sum of their series.

From those two, most counting encodings write themselves. "Each prime is in the subset or it isn't,
and its presence adds `p` to the total" is the factor `1 + x^p`, one per prime; the product's
coefficient of `x^s` is the number of subsets summing to `s` (problem 249). "Each slot holds 0, 1
or 2, and holding 1 can be realised `w` ways" is `1 + w·x + x²` (problem 743). "Part size `k` may be
used any number of times" is `1/(1 - x^k)`, and the product over all `k` is the partition
generating function — the object behind problem 78, and behind its variants with restricted parts
(problem 614's distinct summands, problem 890's powers of two).

Two more constructions round out the toolkit:

- **Ordered sequences invert.** If one part is drawn from a class with series `C(x)`, then a
  *sequence* of any number of parts is `1 + C + C² + … = 1/(1 - C(x))`. That is how
  [compositions](/blogs/domain/composition-combinatorics) work. The zero-free numbers with digit sum
  *n* in problem 377 are compositions of *n* into parts 1–9, so their series is
  `1/(1 - x - x² - … - x⁹)`.
- **A second statistic gets a second variable.** Problem 682 pairs 5-smooth numbers `2ᵃ3ᵇ5ᶜ` on two
  statistics at once: `y` marks the sum of prime factors, and `x` marks how many there are. Each
  prime contributes `1/(1 - x·yᵖ)`. To require two numbers with *equal* factor counts, mark one with
  `x` and the other with `x⁻¹`, then keep the **constant term in `x`**. This is the same move as
  problem 860's returning walk, now used as a filter on a bivariate series. The general rule: a
  constraint "these two statistics agree" becomes "the exponent of the marker variable is zero"., and that is the part with real technique in it.

**Extract by dynamic programming.** Multiplying the running polynomial by `1 + x^p` is the array
update `c[s] += c[s-p]`, which is why 0/1 knapsack and subset-sum counting are the same thing as a
generating function expanded left to right. Problem 249 is this on a table of 1.5 million slots,
reduced mod 10¹⁶ throughout; the series is never written down, only walked.

**Extract by a closed form.** Sometimes you need one coefficient, not the array. Problem 743 needs
`[x^k](1 + b·x + x²)^k` at *k* = 10⁸ — a central trinomial coefficient with a multinomial closed
form, computable as one O(*k*) loop with no array at all. Recognising the polynomial is what buys
the shortcut; the generating function is the *model*, not the *method*.

Problem 860 shows how far that recognition can go. It is a partizan coin game, and combinatorial
game theory gives each height-two stack a value of ±2 or ±½. "Fair" means the values sum to zero.
Measured in half-units, *F*(*n*) counts ordered sequences of *n* steps from {±4, ±1} that sum to
zero. That is a walk that comes back to the origin, so the count is the **constant term** of the
Laurent polynomial `(x⁴ + x + x⁻¹ + x⁻⁴)ⁿ`. Negative exponents are fine; multiply through by `x⁴ⁿ`
and you are reading `[x⁴ⁿ]` of an ordinary polynomial. The useful part is that the step polynomial
factors: `x⁴ + x + x⁻¹ + x⁻⁴ = x⁻⁴(1 + x³)(1 + x⁵)`. The *n*-th power of a four-term polynomial
becomes the product of two binomial powers. So the coefficient is a single sum `Σ C(n,i)·C(n,j)` over
`3i + 5j = 4n`, about *n*/5 terms, where the direct count would sum multinomials over four stack
multiplicities. Before you expand a power, try factoring its base.

**Extract by powering.** When the independent parts are also *identical*, the product is a power,
and a power takes [exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring):
log *t* multiplies, each truncated at the degree you will read. Problem 768 counts balanced
chandeliers, meaning *m* candles in a ring of *n* sockets whose unit vectors sum to zero. Here the
generating function shows up twice. First the subset itself is a polynomial `f_S(x) = Σ_{k∈S} xᵏ`,
and "balanced" means `f_S(ζₙ) = 0`, so the [cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial)
`Φₙ` divides it. That algebra splits the ring into `t = n/rad(n)` interleaved copies of the
squarefree ring, and each copy must balance on its own. Second, if `G(z)` counts the balanced
*k*-subsets of one copy, the answer is `[z^m] G(z)^t`. The real work is the census of one 30-socket
copy. After that, combining the copies is a dozen lines of truncated powering, and its cost depends
on *n* only through `log t`.

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

Problem 520 shows an EGF that collapses completely. A "simber" puts a parity condition on how often
each digit occurs: even digits an even number of times, and odd digits an odd number of times or not
at all. Those series are named functions: `Σ x²ʲ/(2j)! = cosh x` and `1 + sinh x`, so the count of
length-*L* strings is `L![xᴸ] cosh⁵x·(1 + sinh x)⁵`. The useful step is to substitute `y = eˣ`.
Then `cosh` and `sinh` become `(y ± y⁻¹)/2`, the whole product becomes a Laurent polynomial
`Σ c_k y^k` with *k* in −10…10, and `L![xᴸ] e^{kx} = kᴸ`. The count is therefore an exact
**power sum** `Σ c_k kᴸ`, and summing it over every length up to *n* gives 21
[geometric series](/blogs/technique/geometric-series). So an EGF that is a polynomial in `eˣ` leads
to a closed form that costs O(log *n*), even for *n* = 2³⁹.

## Rational generating functions

A sequence satisfying a linear recurrence of order *r* has a generating function that is a ratio of
two polynomials of degree ≤ *r*. Multiply the series by the recurrence's characteristic polynomial
and nearly everything telescopes: `Σ Fₖxᵏ · (1 - x - x²)` collapses to `x`, so the Fibonacci OGF is
`x/(1 - x - x²)`. That one line is the hinge of problems 137 and 140, which ask for which *rational*
`x` the series takes an integer value — meaningless as an infinite sum, immediate once it is a
rational function. Setting it equal to `k` clears to a quadratic, rationality becomes "the
discriminant is a perfect square", and the search collapses into a
[Pell equation](/blogs/domain/diophantine-equation) whose solutions are generated by a recurrence.
An infinite search over candidates becomes an O(*n*) walk along an orbit.

This is the direction worth internalising: **a generating function is a bridge to a different
subject**. Rational ⇒ linear recurrence ⇒ Diophantine machinery. The series itself is scaffolding
you take down afterwards.

Rationality also pays off when you never solve anything: keep the numerator, and read the
denominator from a formula. Problem 996 counts the tuples of overtake counts that tennis players
can accumulate in at most *k* ≈ 4.6 million days. Each board position gets a rational weight in `y`:

- a positive count is `y/(1 - y)`;
- the even-total condition keeps the even part `½(f(y) + f(-y))`, the two-term case of a
  [series multisection](https://en.wikipedia.org/wiki/Series_multisection);
- tuples that break the half-sum bound are subtracted as `y²/(1 - y²)` terms.

Every denominator divides `1 - y²`. Clear it from each factor and the product becomes a numerator
polynomial `N(y)` of degree 2*n*, built by a left-to-right DP whose states are polynomials. What is
left is `(1 - y²)ⁿ(1 - y)`, and its coefficients come in closed form (stars and bars, then the
hockey-stick identity). So the answer is a sum of 2*n* + 1 products `Nᵢ·C(⌊(k-i)/2⌋ + n, n)`.
Never expand the series to degree *k*: here *k* is only a binomial argument.

When the target index is astronomical and no closed form shows up, a rational generating function
still gives you **one far coefficient in O(log *n*)**. There are two standard ways to get it.

- **Matrix power.** A recurrence of order *r* is a fixed *r* × *r*
  [transition matrix](/blogs/technique/matrix-exponentiation), and `[xⁿ]` is one entry of `Mⁿ`.
  Problem 377 needs the *sum* of the numbers counted above, not only how many there are. The sum
  alone is not closed, because appending digit *d* maps *v* to `10v + d` and so needs the count.
  Carrying the sum and the count together makes an 18-dimensional state that *is* closed. Its
  targets are 13ⁱ, so it chains the powers as `M^{13ⁱ} = (M^{13ⁱ⁻¹})¹³`, and the exponent is never
  written down as a number.
- **[Bostan–Mori](/blogs/technique/bostan-mori-algorithm).** To compute `[yⁿ] N(y)/D(y)`, multiply
  the top and the bottom by `D(-y)`. The denominator becomes even, and only the half of the
  numerator with the parity of *n* can reach `yⁿ`, so *n* halves while the degrees stay at *d*. That
  is O(*d*² log *n*), compared with O(*d*³ log *n*) for the matrix. Problem 682 uses it after a
  residue argument shows that its constant-term series is rational with a known degree-40
  denominator. The code then **checks that claim**: it computes 81 terms, multiplies them by `D`,
  and asserts that every coefficient from 40 to 80 vanishes. A missed pole would make the assertion
  fail instead of producing a quietly wrong answer.

Rational functions also handle **parity**. Problem 973 sums the XOR of the parts over all
compositions of *n*, which is 2ⁿ⁻¹ of them for *n* = 10⁴. Split the XOR by bit. Bit *b* is set when an
odd number of parts have it, so give each part the sign `−1` if it has bit *b* and `+1` if not.
The signed count, the [sequence construction](/blogs/domain/composition-combinatorics) applied to
these signed parts, is the gap between the even and odd cases. The sign has period `2·2ᵇ`, so
`C_b(x)` sums to a rational function, and `1/(1 - C_b)` has a four-term denominator, which is a
four-term recurrence. The `±1` weight is the same filter as `½(f(y) + f(-y))` in problem 996:
assign `−1` to whatever you want to count mod 2, and the signed sum gives the difference between
the even and odd cases.

## Algebraic and holonomic generating functions

Past rational come *algebraic* functions (series involving square roots) and, more generally,
[holonomic](https://en.wikipedia.org/wiki/Holonomic_function) ones: series that satisfy a linear
differential equation with polynomial coefficients. Their coefficients satisfy a linear recurrence
whose coefficients are polynomial in *n*. That is not enough for O(log *n*), but it gives an O(*n*)
loop in O(1) memory with no array.

Problem 1007 shows this in full. It sums a signed Fibonacci expression over all
[Catalan](/blogs/domain/catalan-number)-many bracketings, which is too many to enumerate at
*n* = 10⁷. It needs three steps:

1. [Binet](/blogs/technique/binets-formula) turns the Fibonacci leaf weights into two
   *geometric* weights `tⁱ`. With `t = φ` and `t = ψ`, both live in `𝔽_p`, because 5 is a quadratic
   residue modulo the prime.
2. Splitting a binary tree at its root gives a functional equation. The right subtree's leaves are
   shifted (a factor `t^k`) and negated. Solving it gives a series built from `√(1−4w)` and
   `√(1−4tw)`.
3. Rationalising twice leaves one linear denominator and a numerator made of the radicals and their
   product. Each radical `g = √P` satisfies `2P·g′ = P′·g`, and that differential equation is the
   recurrence for its coefficients.

Problem 976 reaches the same point from another direction. After a combinatorial-game argument has
reduced the game to a parity rule, what remains is reading `[x^K]` of
`(1−x)^{−α}(1+x)^{−β}` at *K* = 10⁷. The series satisfies `(1−x²)f′ = (α(1+x) − β(1−x))f`, which
gives an order-two recurrence for its coefficients. An extra factor `(1−x)⁻¹` turns each coefficient
into a prefix sum over `k ≤ K` at no cost.

Both problems hit the same practical obstacle: a holonomic recurrence divides by *n* + 1 at every
step. Ten million modular inverses are slow, and a table of them is large. In both, the fix is to
track `n!·cₙ`. The division disappears, every sequence carries the same factorial, and **one**
inverse at the end removes it. The general version of this idea is on
[its own page](/blogs/takeaway/scale-fraction-sums-to-integer-recurrences).

## Working modulo something

Two different reductions show up, and they are not the same trick.

**Reduce the coefficients.** When the problem asks for the answer mod *m*, every coefficient can be
held mod *m* throughout — sound as long as the extraction uses only `+` and `×`. Watch for
subtraction in a signed recurrence: Euler's pentagonal sum alternates, and in C the running total
can go negative, so `((v % m) + m) % m` rather than a bare `%`. Python's `%` already returns
non-negative, which is exactly the kind of difference that makes a C port disagree with its Python
original. Division is the other hazard. Problem 996's `½(f(y) + f(-y))` would need an inverse of 2.
It avoids one by carrying the half-sum and half-difference as separate states, so every update
stays a shift and an addition.

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
  a prime, start to pay. A *t*-fold power of one factor costs O(*D*² log *t*) by squaring, not *t*
  passes (problem 768).
- **Look for the structure before the array.** The best outcomes here are not faster expansions but
  escapes from expanding at all: a sparse reciprocal (problem 78), a closed-form coefficient
  (problem 743), a base that factors into binomials (problem 860), a periodicity that makes the input census O(1) (problem 250), a rational form that
  hands the problem to number theory (problems 137, 140), a known denominator that takes the target
  degree out of the cost (problem 996), an EGF that is secretly a polynomial in `eˣ` (problem 520).
  Write the generating function down first; then look hard at what it *is* before you start
  multiplying.
- **Classify it, and the classification gives the cost.** Polynomial: closed-form coefficients.
  Rational: O(log *n*) for any single coefficient, by Bostan–Mori or a matrix power
  (problems 377, 682). Algebraic or holonomic: an O(*n*) recurrence in O(1) memory
  (problems 976, 1007). Anything else: expand it and truncate.
- **Verify the class on small terms.** A claimed denominator is easy to check: multiply it by enough
  computed terms and confirm the tail vanishes (problem 682). Problem 973's composition formula was
  found the same way, by solving its Markov chain exactly for small *n*, noticing that every
  expected visit count was an integer, and then confirming the pattern before relying on it.

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
- ● [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ○ [0519](/solutions/0519/) — Tricoloured Coin Fountains
- ● [0520](/solutions/0520/) — Simbers
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ○ [0648](/solutions/0648/) — Skipping Squares
- ○ [0677](/solutions/0677/) — Coloured Graphs
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0709](/solutions/0709/) — Even Stevens
- ○ [0722](/solutions/0722/) — Slowly Converging Series
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0768](/solutions/0768/) — Chandelier
- ○ [0851](/solutions/0851/) — SOP and POS
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ○ [0881](/solutions/0881/) — Divisor Graph Width
- ○ [0890](/solutions/0890/) — Binary Partitions
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0973](/solutions/0973/) — Random Dealings
- ● [0976](/solutions/0976/) — XO Game
- ● [0996](/solutions/0996/) — Overtakes
- ● [1007](/solutions/1007/) — Alternating Difference

<!-- /problems -->
