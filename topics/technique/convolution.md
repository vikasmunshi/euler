<!-- tags: [convolution] -->
<!-- status: final -->
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

**The index set need not be the integers.** Convolution is defined over any group — replace
`i + j` with the group operation. The Quaternion Group I (problem 980) tallies how many blocks map
to each element of the 8-element quaternion group *Q₈*, then pairs them by `Σ_g cnt[g]·cnt[g⁻¹]`.
That is a convolution over *Q₈* evaluated at the identity, and it turns an O(*N*²) pairing over
10¹² ordered pairs into a linear tally over eight buckets. When a problem's parts compose by some
associative rule other than addition, look for the same collapse.

**A comparison is a convolution plus a prefix sum.** "How often does one sum beat another?" is not
a single coefficient but a triangular sum over the product distribution. Precompute the prefix sums
of one side and each query becomes O(1) — problem 205's win count is exactly this, with the
off-by-one (*strictly* greater, so exclude the tie) doing real work.

## How to reason about it

- **Cost.** The direct double loop is O(*mn*) for arrays of length *m* and *n*. That is fine when
  the totals are small — dice sums, digit-square sums, a few hundred slots — and it is what every
  problem here uses. Only when the arrays get long (tens of thousands and up) does it pay to reach
  for an [FFT](https://en.wikipedia.org/wiki/Convolution_theorem)-based multiply at
  O(*n* log *n*), or an [NTT](https://en.wikipedia.org/wiki/Discrete_Fourier_transform_over_a_ring)
  when the answer is wanted modulo a prime.
- **Stay in integers.** Convolving *counts* rather than *probabilities* keeps the arithmetic exact
  through thousands of additions; divide by the size of the outcome space once, at the end. Floats
  accumulate error and can cost you the last of the seven decimal places a problem asks for.
- **Watch the array's length.** Each convolution step grows the support by the new part's span, so
  either allocate a fresh array of length `len(a) + span` or extend in place — and be clear whether
  the old contents should survive (they encode the zero-contribution case) or be cleared first.
  Truncating early to the degree you care about is a legitimate and often large saving.
- **Look for independence first.** The whole technique is unlocked by the observation that two
  quantities do not constrain each other. If they do — if some choice couples the parts — either
  find a variable that decouples them (problem 240 conditions on the value of the tenth-largest
  die, after which the three classes of dice are independent) or accept that convolution is the
  wrong tool.

The tell is a brute force whose cost is a *product* of independent ranges. When you catch yourself
writing nested loops over things that never interact except through their sum, stop: build each
one's distribution separately and convolve.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0205](/solutions/0205/) — Dice Game
- ● [0240](/solutions/0240/) — Top Dice
- ● [0250](/solutions/0250/) — $250250$
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0768](/solutions/0768/) — Chandelier
- ● [0980](/solutions/0980/) — The Quaternion Group I

<!-- /problems -->
