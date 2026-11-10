<!-- tags: [convolution] -->
<!-- status: final 2026-11-04T18:06Z -->
# Convolution

[Convolution](https://en.wikipedia.org/wiki/Convolution) is the operation that combines two
sequences into a third by summing every way their indices add to the same total:
`(a * b)[k] = Σᵢ a[i]·b[k-i]`. That one line is three familiar things at once — multiplying
polynomials, distributing a sum of two independent random variables, and the inner loop of a
counting DP. It recurs across the problems below because they all ask the same question in
different costumes: *in how many ways can independent parts add up to this total?*

## The idea

Encode a count array as a polynomial: if `a[i]` is the number of ways to reach total `i`, the
[generating function](https://en.wikipedia.org/wiki/Generating_function) is `A(x) = Σ a[i]·xⁱ`.
Combining two independent parts multiplies their polynomials, because a term `xⁱ` from one and
`xʲ` from the other land together in `x^(i+j)` — which is exactly the convolution formula, read
coefficient-wise. So *independent parts add; their generating functions multiply*.

The immediate consequence is that repeating a part means **raising one polynomial to a power**.
A fair *n*-sided die is `x + x² + … + xⁿ`; rolling *d* of them and asking for the distribution of
the total is that polynomial to the *d*-th, and the coefficient of `x^T` is the number of rolls
summing to *T*. Dice Game (problem 205) is this twice over — nine 4-sided dice and six 6-sided
dice, each side's distribution convolved with itself once per die — which collapses a
4⁹ × 6⁶ ≈ 1.2 × 10¹⁰ joint enumeration into a few array passes. Top Dice (problem 240) uses the
same power, restricted to a sub-range of faces, as the inner table of a larger decomposition.

The parts need not be dice. Square Digit Chains (`solutions/public/p0092/`) counts *d*-digit
strings by digit-square-sum: each digit position contributes the same fixed distribution
(digit 0 adds 0, digit 1 adds 1, …, digit 9 adds 81), so the answer is that little distribution
convolved with itself *d* times. The whole algorithm is the scatter loop:

```python
a, sq = ([1], [x**2 for x in range(1, 10)])
for _ in range(power_of_10):
    b, a = (a, a + [0] * 81)
    for i, v in enumerate(b):
        for s in sq:
            a[i + s] += v
```

`a[s]` is the number of digit strings with square-sum `s`. Each pass zero-extends by 81 — the most
one digit can add — and scatters every existing count across the nine non-zero squares. (Digit 0
adds nothing, and is handled for free by *not* clearing `a` before the pass.) The domain shrinks
from 10⁷ numbers to at most 81·*d* + 1 distinct sums, and 10⁷ chain simulations become a few
thousand additions.

## Shapes it takes

**You often need one coefficient, not the whole product.** Window into a Matrix (problem 743)
reduces to the coefficient of `x^k` in `(1 + b·x + x²)^k` — a central trinomial coefficient. At
*k* = 10⁸ nobody expands that polynomial; the coefficient has a closed form as a sum of
multinomials, and consecutive terms differ by a fixed ratio, so the whole thing is one O(*k*)
loop with no array at all. Recognising the polynomial is what buys the closed form; convolution
is the *model*, not necessarily the *method*.

Even without a closed form, one coefficient is cheaper than a product. The coefficient of `x^k`
in `A·B` is a single dot product, `Σᵢ a[i]·b[k-i]` — O(*k*), not the O(*k*²) of the full
convolution. March of the Penguins (problem 1010) leans on this hard: it counts, over every
partition of *n*, the cells of each hook length, and each cell position splits a partition into
three independent regions, each counted by a partition generating function — two of them
[Gaussian binomials](https://en.wikipedia.org/wiki/Gaussian_binomial_coefficient), partitions
fitting in a box. The count it wants is one coefficient of their triple product, so it convolves two of the
factors once (`np.convolve`) and then reads off the coefficients it needs, for every arm length at
once, as a vectorised dot product against the third.

**A constraint between the parts is a constant term.** Problem 682 counts pairs of Hamming numbers
whose prime-factor sums add to *n* and whose prime-factor counts are *equal*. The sums add, which is
ordinary convolution; the counts must match, which looks like a coupling that rules convolution
out. Give it a variable instead. Tag each prime factor of the first number with `x` and each of the
second with `x⁻¹`, and multiply the two generating functions: a term lands on `x⁰` exactly when the
counts cancel, so equality has become a constant term, while a second variable `y` carries the sums
as usual.

Nor must the factors be finite. Each prime there contributes `1/(1 − x·y^p)`, any number of copies,
yet the constant term in `x` is a [rational function](https://en.wikipedia.org/wiki/Rational_function)
`N(y)/D(y)` with a denominator of degree 40, so the sequence obeys a
[linear recurrence](https://en.wikipedia.org/wiki/Linear_recurrence_with_constant_coefficients) and
the target is one coefficient of an infinite series. The
[Bostan–Mori algorithm](https://arxiv.org/abs/2008.08822) reads it in O(*d*² log *n*): multiply top
and bottom by `D(−y)`, which makes the denominator even, keep only the numerator terms whose parity
matches *n*, and *n* halves while the degrees stay put. One safeguard is worth stealing. `D` came
from a pen-and-paper residue argument, so the code computes 81 terms directly, multiplies them by
`D`, and asserts that every coefficient from degree 40 to 80 vanishes: a missed pole fails loudly
instead of producing a plausible wrong number.

**Many identical parts: power by squaring, truncated.** When the same part repeats *t* times and
*t* is large, raise its polynomial to the *t*-th by
[repeated squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) — O(log *t*)
multiplications instead of *t*. If only degrees up to *m* matter, drop every term above *m* after
each multiply, and the cost is O(*m*² log *t*) however large the true product would be. Chandelier
(problem 768) ends exactly this way: the structure of the roots of unity splits a balanced
arrangement into *t* independent layers, each with the same distribution of candle counts, and the
answer is the coefficient of `x^m` in that distribution's *t*-th power. The hard part of the
problem is finding the independence; once found, the combination is a three-line function.

Repeated parts also collapse the other way. Problem 250 multiplies one factor `(1 + x^r)` per
element, but its elements fall into only 250 residue classes, so each class of *c* equal factors
is `(1 + x^r)^c` — written down directly from a row of binomial coefficients rather than built by
*c* multiplications. Group equal factors before multiplying anything.

**The index set need not be the integers.** Convolution is defined over any group — indeed any monoid —
replace `i + j` with its operation. The everyday case is the cyclic group ℤ/*m*: "how many subsets
have a sum divisible by *m*?" is a product of `(1 + x^e)` factors in the ring
`ℤ[x]/(x^m − 1)`, where exponents add modulo *m* and the array has a fixed length *m* forever —
an index past the end wraps to the front instead of growing the array. Problem 250 asks this for
the 250250 numbers `k^k` with *m* = 250, and the subset count is the coefficient of `x⁰` in a
product of at most 250 cyclic multiplies, never wider than 250 slots. Elements in residue class
0 do not even need a multiply: each one doubles every count, so the whole class is a scalar
`2^c`.

The exotic case works the same way. The Quaternion Group I (problem 980) tallies how many blocks
map to each element of the 8-element quaternion group *Q₈*, then pairs them by
`Σ_g cnt[g]·cnt[g⁻¹]`. That is a convolution over *Q₈* evaluated at the identity, and it turns an
O(*N*²) pairing over 10¹² ordered pairs into a linear tally over eight buckets. Chandelier's
[meet-in-the-middle](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) step is the same
move in two variables at once: each half's subsets are tallied by (vector sum, size); the halves
are joined only where their sums cancel — the sum variable evaluated at the identity — while the
sizes convolve in full. When a problem's parts compose by some associative rule other than
addition, look for the same collapse.

The rule need not even be invertible. Freshman's Product (problem 778) multiplies numbers digit by
digit with no carries, so each decimal place is its own sub-problem — the same independence across
positions that problem 92 exploits. Within one place, each of the *R* factors contributes a
ten-entry histogram of digits, and two independent digits combine by
`(a * b)[z] = Σ_{xy ≡ z (mod 10)} a[x]·b[y]`: a convolution over the digits under multiplication
mod 10. That is a [monoid](https://en.wikipedia.org/wiki/Monoid), not a group — 0 absorbs
everything, 5 times any even digit is 0, and most digits have no inverse — yet the *R*-fold power
still falls to repeated squaring from the identity distribution (all mass on the digit 1), because
associativity is the only property square-and-multiply uses. The array is ten slots forever, so
*R* in the hundreds of thousands costs a few dozen 10 × 10 multiplies per place.

Problem 294 takes that claim further: the rule need not commute, and the parts need not be identical.
It counts digit strings of length 11¹² with a fixed digit sum and a fixed residue mod 23. Digits are
not identical parts here, because digit *d* at position *i* adds `d·10ⁱ` to the residue, so no single
polynomial is being raised to a power. The way out is to change what is multiplied. Describe a
*block* of digits by a table `T[r][s]`, with the residue *r* measured from the block's own lowest
digit and the digit sum *s*, and carry the block's length beside it. Placing one block above another
of length *L* first relabels its residues by `r → r·10ᴸ` and then convolves, cyclically in *r* and
truncated at 23 in *s*. That twisted product of (table, length) pairs cares about order, as `12` and
`21` do, but it is associative, so doubling still works: about 80 products of a 23 × 24 table for a
length in the trillions. When parts differ only by a position-dependent relabelling, fold the
position into the element and square that.

**A transform turns convolution into pointwise multiplication, if you can divide.** The
[convolution theorem](https://en.wikipedia.org/wiki/Convolution_theorem) holds over any finite
abelian group: transform, multiply entry by entry, invert, and a *c*-fold power is just the *c*-th
power of each transformed entry. For XOR the transform is
[Walsh–Hadamard](https://en.wikipedia.org/wiki/Hadamard_transform), and problem 649 has exactly that
shape: the [Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
reduces each coin to a Grundy value and makes the sum of games an XOR, so the arrangements of *c*
coins are a *c*-fold XOR-convolution power of an 8-slot histogram. Yet the solution deliberately
skips the transform. The inverse divides by the group's size, 8, and the answer is wanted modulo
10⁹, where 8 has no inverse. (The escape is to work modulo 8·10⁹ and divide exactly at the end, at
the price of wider products.) Square-and-multiply on the direct 8 × 8 product needs only ring
operations and is free at this size. Before reaching for a transform, check that the ring can invert
it, and that the array is long enough to need it.

**Interleaved parts convolve binomially.** Everything above combines parts that occupy fixed places.
When parts are shuffled together, as letters in a string or events in an order, splitting *n* slots
into *k* and *n − k* must also choose *which* slots, so the rule becomes
`(a ⋆ b)[n] = Σₖ C(n,k)·a[k]·b[n−k]`. Divide each `a[n]` by `n!` and the binomial disappears: that
is the [exponential generating function](https://en.wikipedia.org/wiki/Exponential_generating_function),
and independent parts multiply again. Problem 520 constrains only how often each digit occurs, so
each digit is one such part: an even digit, occurring an even number of times, is `cosh x`, an odd
digit is `1 + sinh x`, and the strings of length *L* are `L!·[x^L]` of the ten-fold product.

That product has a further move in it. `cosh` and `sinh` are built from `e^{±x}`, so setting
`y = e^x` makes it a [Laurent polynomial](https://en.wikipedia.org/wiki/Laurent_polynomial) in `y`
with exponents −10 to 10, an ordinary 21-slot convolution, and `L!·[x^L] e^{kx} = k^L` reads the
count back as a fixed combination of 21 powers `k^L`. Summing over lengths is then 21
[geometric series](https://en.wikipedia.org/wiki/Geometric_series). The length, which reaches 2³⁹,
never enters the convolution at all: a change of basis moved the multiplication onto a small index
set and left *L* as an exponent.

**A sequence can be convolved with itself to define itself.** Sometimes the independent parts are
smaller copies of the whole. Tidying Up B (problem 866) lays *N* pieces in a random order and
multiplies in a hexagonal number `H(k)` for each segment a placement forms. Condition on the last
piece placed: it separates two stretches that never touched, each one's sub-order is still uniform,
so the expectation factorises and `E(N) = (H(N)/N)·Σⱼ E(j−1)·E(N−j)`, the
[Catalan](https://en.wikipedia.org/wiki/Catalan_number) recurrence with a weight. This is no product
of two known arrays. `E(N)` needs every earlier term, so the table fills in order at O(*N*²), and
speeding it up would take an online scheme rather than one FFT. The sum is symmetric, so half the
loop suffices. It is also the binomial rule in disguise: counted over orders, the two sides interleave
in `C(N−1, j−1)` ways, and dividing by *N*! to get an expectation is precisely the exponential
normalisation, which is why no binomial survives in the recurrence.

**A comparison is a convolution plus a prefix sum.** "How often does one sum beat another?" is not
a single coefficient but a triangular sum over the product distribution. Precompute the prefix sums
of one side and each query becomes O(1) — problem 205's win count is exactly this, with the
off-by-one (*strictly* greater, so exclude the tie) doing real work.

## How to reason about it

- **Cost.** The direct double loop is O(*mn*) for arrays of length *m* and *n*. That is fine when
  the totals are small — dice sums, digit-square sums, 250 residues, a few hundred slots — and it is
  what every problem here uses, `np.convolve` included. Only when the arrays get long (tens of thousands and up) does it pay to reach
  for an [FFT](https://en.wikipedia.org/wiki/Convolution_theorem)-based multiply at
  O(*n* log *n*), or an [NTT](https://en.wikipedia.org/wiki/Discrete_Fourier_transform_over_a_ring)
  when the answer is wanted modulo a prime.
- **Stay in integers.** Convolving *counts* rather than *probabilities* keeps the arithmetic exact
  through thousands of additions; divide by the size of the outcome space once, at the end. Floats
  accumulate error and can cost you the last of the seven decimal places a problem asks for.
  When the counts outgrow a machine word, either reduce them modulo the answer's modulus after
  every multiply (problem 250 keeps only 16 digits — and in C the product of two 16-digit
  residues still needs 128 bits) or prove they cannot overflow: NumPy's `int64` wraps silently,
  and problem 1010 is safe only because every coefficient it convolves counts partitions of at
  most 300, which stay below 10¹⁶. The sum can overflow where each product does not: problem 866's
  products fit 64 bits, but thousands of them added up do not, so its C accumulates in 128 bits and
  reduces once per `E(N)`.
- **Watch the array's length.** Each convolution step grows the support by the new part's span, so
  either allocate a fresh array of length `len(a) + span` or extend in place — and be clear whether
  the old contents should survive (they encode the zero-contribution case) or be cleared first.
  Truncating early to the degree you care about is a legitimate and often large saving
  (problem 768 never holds more than *m* + 1 terms); working modulo `x^m − 1` stops the growth
  altogether.
- **Look for independence first.** The whole technique is unlocked by the observation that two
  quantities do not constrain each other. If they do — if some choice couples the parts — either
  find a variable that decouples them (problem 240 conditions on the value of the tenth-largest
  die, after which the three classes of dice are independent; problem 1010 fixes one cell and
  its arm and leg, after which the three regions around it are; problem 866 fixes the last piece
  placed), give the coupling a variable of its own (problem 682), or accept that convolution is
  the wrong tool.

The tell is a brute force whose cost is a *product* of independent ranges. When you catch yourself
writing nested loops over things that never interact except through their sum, stop: build each
one's distribution separately and convolve.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0205](/solutions/0205/) — Dice Game
- ● [0240](/solutions/0240/) — Top Dice
- ● [0250](/solutions/0250/) — $250250$
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0520](/solutions/0520/) — Simbers
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0767](/solutions/0767/) — Window into a Matrix II
- ● [0768](/solutions/0768/) — Chandelier
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0866](/solutions/0866/) — Tidying Up B
- ● [0922](/solutions/0922/) — Young's Game A
- ● [0923](/solutions/0923/) — Young's Game B
- ● [0930](/solutions/0930/) — The Gathering
- ● [0949](/solutions/0949/) — Left vs Right II
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
