<!-- tags: [pascals-triangle] -->
<!-- status: final -->
# Pascal's triangle

[Pascal's triangle](https://en.wikipedia.org/wiki/Pascal%27s_triangle) is the table of
[binomial coefficients](https://en.wikipedia.org/wiki/Binomial_coefficient) `C(n, k)`, row `n`
holding `C(n, 0) … C(n, n)`. In these problems it shows up for a practical reason more than a
pretty one. Counting problems keep producing binomials, and computing a binomial looks trivial
(`n! / (k!·(n−k)!)`) until the language, the integer width or the modulus gets in the way. The
triangle builds the same numbers from **additions alone**. Every problem below reaches for it at
the point where the textbook formula stops working: an overflow, a modulus with no inverses, or a
loop that needs a whole row of coefficients rather than one.

## The idea

Two recurrences generate the triangle, and they solve different problems.

**Pascal's rule**, the additive one, says each entry is the sum of the two above it:

```
C(n, k) = C(n−1, k−1) + C(n−1, k),      C(n, 0) = C(n, n) = 1
```

Combinatorially, a `k`-subset of `{1…n}` either contains `n` (choose the other `k−1` from `n−1`)
or does not (choose all `k` from `n−1`). Filling rows `0…N` this way costs `O(N²)` additions and
yields **every** `C(a, k)` with `a ≤ N` in one table. The only operation is `+`, so:

- **No intermediate exceeds the result.** The factorial formula overflows long before the
  binomial does (`100!` has 158 digits, while `C(100, 25) ≈ 2.4·10²³` merely misses 64 bits). In
  Pascal's rule, no intermediate value is ever larger than the entry being built.
- **It works under any modulus.** Addition is compatible with reduction mod `m` for *every* `m`,
  so `(a + b) mod m` is all you ever need. The factorial formula, done modularly, needs
  `(k!)⁻¹ mod m`, and that [inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
  exists only when `gcd(k!, m) = 1`. Against a prime `p > n` that is fine; against a composite
  modulus such as `10⁸ = 2⁸·5⁸` it fails as soon as `k ≥ 2`.

**The multiplicative recurrence** walks along a single row:

```
C(n, k+1) = C(n, k) · (n − k) / (k + 1)
```

The division is always exact, because `C(n, k)·(n−k) = C(n, k+1)·(k+1)`, as long as you multiply
first and divide second. This gives one row in `O(n)` without a table. The cost is a
multiplication that runs ahead of the result by a factor of `n − k`, and a division, which is the
thing a composite modulus will not let you do.

Two structural facts about each row are worth keeping in mind as well: it is
**symmetric**, `C(n, k) = C(n, n−k)`, and **unimodal**, rising to the centre and falling after.
Together they turn many "how many entries satisfy …" questions into finding one crossing point.

## A worked example

Take `C(6, 3) mod 8`. The true value is `C(6, 3) = 20`, so the answer is `4`.

**The factorial route fails.** `6! = 720 ≡ 0 (mod 8)` and `3!·3! = 36 ≡ 4 (mod 8)`. The formula
now asks for `0 · 4⁻¹ mod 8`, but `4` has no inverse mod 8 because `gcd(4, 8) = 4`. Worse, the zero
in the numerator would make any "inverse" you forced through give `0`, which is wrong. Once you
reduce `6!` early, the factors of 2 that the division was meant to cancel are already gone.

**The triangle does not notice the problem.** Build the rows mod 8, each entry the sum of the two
above it:

```
n = 0:  1
n = 1:  1  1
n = 2:  1  2  1
n = 3:  1  3  3  1
n = 4:  1  4  6  4  1
n = 5:  1  5  2  2  5  1        10 ≡ 2
n = 6:  1  6  7  4  7  6  1     5+2 = 7,  2+2 = 4
```

Row 6 reads `1 6 7 4 7 6 1`, which is `1 6 15 20 15 6 1` reduced mod 8. The `4` in the middle is
the answer. No division happened, so nothing needed an inverse.

In code, a single row updated in place is enough:

```python
def binomial_row(n, m):
    row = [1] + [0] * n
    for a in range(1, n + 1):
        for k in range(a, 0, -1):          # right to left
            row[k] = (row[k] + row[k - 1]) % m
    return row

binomial_row(6, 8)    # [1, 6, 7, 4, 7, 6, 1]
```

The direction of the inner loop matters. Going right to left, `row[k - 1]` still holds row `a−1`'s
value when `row[k]` reads it. Run the same loop left to right and each entry adds in a neighbour
that was already updated this pass. Row 6 then comes out as `1 6 20 48 90 132 132` (before
reduction), which is nothing like a row of binomials.

## Where it does the work

**Walking a row with an early exit.** Problem 0053 counts the `C(n, r)` above a million for
`n ≤ 100`. Since each row is symmetric and unimodal, the first `r` whose coefficient passes the
threshold settles the whole row: entries `r … n−r` all qualify. The public solution walks the row
multiplicatively and stops there:

```python
for n in range(1, max_n + 1):
    c = 1
    for r in range(0, n // 2 + 1):
        if c > threshold:
            count += n - 2 * r + 1
            break
        else:
            c = c * (n - r) // (r + 1)
```

The early exit is what keeps the C port safe in a `long long`: `c` never grows much past the
threshold before the loop breaks. A tabulated alternative would use Pascal's rule with
*saturation*, storing `min(C, threshold + 1)`. Saturation preserves the comparison, because a sum
of two entries is above the threshold whenever either one is, and it keeps every cell small. That
is the version to use once the threshold or `n` would overflow the multiplicative walk.

**A composite modulus.** Problem 0194 counts graph colourings that decompose into a closed form,
with one `C(a+b, a)` choosing the order of the units. The answer is wanted modulo `10⁸`. Python can
take `math.comb` exactly and reduce at the end. C has neither the integer width for the exact value
nor a modular inverse for the factorials, because `10⁸` shares the primes 2 and 5 with them. Filling
the triangle mod `10⁸` avoids both problems at once. The general lesson is to check the modulus
before reaching for factorial tables: only a prime (or coprime) modulus supports the inverse route.

**A whole table, reused.** Problems 0788 and 0885 both turn digit-counting questions into sums of
binomial-weighted terms. In 0788, a "dominating" digit fills `k` of `L` positions, giving terms like
`C(L, k)·9^(L−k)`, with a leading-zero correction that needs `C(L−1, ·)` too. In 0885, a dynamic
program over digit values multiplies in `C(n−t, k)` at every transition; the product of those
binomials telescopes into a multinomial coefficient. Each sum asks for many different `C(a, k)` with
`a ≤ n`. A precomputed triangle answers each one in `O(1)`, the `O(n²)` fill cost equals the cost of
the main loop anyway, and everything stays mod `m` throughout. The 0788 notes record the payoff:
the Python version keeps exact big integers and reduces once at the end, while the C version reduces
each triangle entry and each product as it goes and runs thousands of times faster. That is fine
because reduction mod `m` is a [ring homomorphism](https://en.wikipedia.org/wiki/Ring_homomorphism),
so reducing early gives the same residue as reducing late.

**Wide integers without big-number support.** Problem 0951 reduces fairness of a card game to
counting decks, and finishes with `C(2n, n) − U(n)`, the
[central binomial coefficient](https://en.wikipedia.org/wiki/Central_binomial_coefficient) minus a
count of unfair decks. In C the result needs `__int128`. Even at that width, the multiplicative
formula overflows in its intermediate products before the final value does. One row of Pascal's
triangle, built by additions, stays within the width the result itself needs.

## How to reason about it

Pick by what the computation needs, not by habit:

| Situation | Reach for |
|---|---|
| Exact value, language has big integers | `math.comb` |
| One coefficient or one row, no modulus, values fit | multiplicative recurrence |
| Many `C(a, k)` with `a ≤ N`, `N` up to a few thousand | Pascal's triangle, `O(N²)` |
| Modulus is composite, or shares factors with `k!` | Pascal's triangle mod `m` |
| Prime modulus `p > N`, `N` large (`10⁶` and beyond) | factorials + inverse factorials mod `p`, `O(N)` |
| Prime modulus `p ≤ N` | [Lucas's theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) over the base-`p` digits |
| Only a comparison against a bound matters | Pascal's triangle with saturation |

The pitfalls are few but they recur:

- **Memory is quadratic.** A full table for `N = 10⁴` is `5·10⁷` entries. If the access pattern
  only ever reads row `a` from row `a−1`, keep one row and update it **right to left** in place, so
  that `C(a−1, k−1)` has not been overwritten when it is read. Problem 0885's C port instead keeps a
  full square table in one contiguous block indexed `a·(n+1) + k`. That is the right call when the
  reads jump between rows, and it avoids the per-row allocations of a jagged array.
- **Reduce at every addition**, not just at the end. With `m < 2⁶²`, the sum of two reduced
  entries fits in 64 bits. Only products, like `C(L, k)·9^(L−k)` in 0788, need `m < 2³¹` (or a
  128-bit intermediate) to stay safe.
- **Handle `k > a` as zero.** Recurrences that index `C(n−t, k)` will step off the triangle's edge.
  Either store explicit zeros or guard the index, as 0788 does for `L − 1 − k ≥ 0`.
- **In the multiplicative walk, multiply before dividing.** `c // (r+1) * (n−r)` truncates and
  gives wrong values; `c * (n−r) // (r+1)` is exact.

The triangle is a solved problem in itself. In these problems, its job is to make the binomial in
someone's formula *computable* under the constraints the problem imposes, so the real work can be
spent on deriving that formula.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0951](/solutions/0951/) — A Game of Chance

<!-- /problems -->
