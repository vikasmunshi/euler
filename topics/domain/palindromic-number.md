<!-- tags: [palindromic-number] -->
<!-- status: final -->
# Palindromic number

A [palindromic number](https://en.wikipedia.org/wiki/Palindromic_number) reads the same forwards
and backwards in some base: `9009`, `585`, or `1001001001` in binary. The property belongs to the
*representation*, not to the number, so it has almost no arithmetic structure. You can't factor
your way to a palindrome, and no formula counts the ones with some other property. That is why
palindromes keep appearing in the archive. Each problem adds a second condition with real structure
(a product, a sum of squares, a divisor, a second base), and the work is choosing which condition
drives the search. The theme across these problems is simple: palindromes are rare, and you can
**build** them directly. Testing every integer to see whether it happens to be one is usually the
slow way.

## A palindrome is half a number

A `d`-digit palindrome is fixed by its first `⌈d/2⌉` digits, because the rest is the mirror image.
That one fact sets the whole cost model:

- **Counting.** There are `9·10^(⌈d/2⌉−1)` palindromes with `d` digits, so about `2√N` lie below
  `N`. Below a million that is under two thousand candidates instead of a million.
- **Generating.** Loop over the left halves, mirror each one, and for odd lengths insert a middle
  digit. Every palindrome comes out exactly once, and the half's nonzero leading digit takes care of
  the "no leading zeros" rule for free.
- **Ordering.** For a fixed length, mirroring is monotone in the half: a larger half gives a larger
  palindrome. So you can produce palindromes in ascending or descending order without sorting.

[Problem 36](/solutions/0036/) is the textbook case. It sums the numbers below a million that are
palindromes in both base 10 and base 2. Instead of scanning a million integers, the generator makes
only the decimal palindromes, and the binary test filters them:

```python
def generate_decimal_palindromes(max_digits: int) -> typing.Generator[int, None, None]:
    """Yield every decimal palindrome up to max_digits by mirroring each left half exactly once."""
    for digit in range(1, 10):
        yield digit
    for digits in range(1, 10 ** (max_digits // 2)):
        digits_str = str(digits)
        digits_rev = digits_str[::-1]
        num_digits = len(digits_str)
        yield int(digits_str + digits_rev)
        if 2 * num_digits < max_digits:
            for mid_digit in "0123456789":
                yield int(digits_str + mid_digit + digits_rev)
```

This drops the work from `O(N)` to `O(√N log N)`. The other base adds a free filter of its own: a
binary palindrome starts with a `1` bit, so it must also end with one. Every even number fails
before you reverse anything.

## The structure a palindrome does have

The property is mostly arbitrary, but two consequences of the mirror are worth knowing well.

**Even-length palindromes are multiples of 11.** In base 10, `10 ≡ −1 (mod 11)`, so a number is
congruent mod 11 to the [alternating sum of its digits](https://en.wikipedia.org/wiki/Divisibility_rule#Divisibility_by_11).
In an even-length palindrome, each digit and its mirror sit at positions of opposite parity, so the
pairs cancel and the sum is `0`. [Problem 4](/solutions/0004/) uses this. The largest palindrome
made from two `n`-digit factors has `2n` digits, so it is divisible by 11, and one of the factors
must supply that 11. When the outer factor `a` is not a multiple of 11, the inner loop steps `b` by
11. That discards ten of every eleven products before the palindrome test runs. Together with a
descending search and an early exit once `a·b` falls below the best palindrome found so far, this
makes the product search fast.

Problem 4 also has a mirror-image solution that follows this page's theme directly. Generate the
`2n`-digit palindromes in **descending** order, which is just counting the left half down. For each
one, look for an `n`-digit divisor in the narrow range `[⌈P/(10ⁿ−1)⌉, √P]`. The first palindrome
that has such a divisor is the answer. There are only `9·10^(n−1)` such palindromes but about
`10^(2n)/2` factor pairs. The product search stays competitive only because its early exit prunes
almost all of those pairs, and the answer sits near the top. Building the palindromes doesn't
depend on that luck.

**A palindrome is a linear form in its half.** Writing digit `dᵢ` into position `i` and its mirror
adds `dᵢ·(10ⁱ + 10^(L−1−i))`. Each half-digit therefore contributes independently, with a fixed
weight, to the value modulo any `m`. [Problem 655](/solutions/0655/) asks how many palindromes below
`10³²` are divisible by a seven-digit prime. Mirroring alone cannot help here, because there are
about `10¹⁶` halves. But the linear form turns the count into a
[digit DP](https://en.wikipedia.org/wiki/Dynamic_programming) over residues: process the half one
digit at a time, carry the residue of the partial weighted sum, and read off the count for residue
`0`. The two halves can also be split in a meet-in-the-middle. The sequence is the same as before,
just one level higher: first construct the palindromes, then aggregate over the construction instead
of listing it.

The same linear form survives a change of base, even an irrational one. In
[Problem 473](/solutions/0473/) numbers are written in base φ, with digits `0` and `1` and no two
adjacent `1`s (the rule that makes [Zeckendorf](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem)
representations unique). An integer's φ-expansion usually has a fractional part, and the radix point
counts as a character of the string. So a palindrome has the point exactly in the middle, and the
mirror pairs exponent `k` with exponent `−(k+1)`. The "half" is therefore a set of exponents
`k ≥ 1`, no two consecutive, and the value is a sum of fixed pair weights `φᵏ + φ^−(k+1)`. Each
weight is `(a + b√5)/2` with [Lucas](https://en.wikipedia.org/wiki/Lucas_number) and Fibonacci
coefficients. The second condition is that the sum be an integer, which means its `√5` coefficients
cancel. That is a constraint on a weighted sum of the half, exactly like 655's residue, except that
the quantity carried is a signed balance instead of a residue mod `p`. The search decides pairs from
the largest down and prunes any branch whose balance can no longer be brought back to zero by the
pairs that remain. Because the coefficients grow geometrically, very few branches survive, and the
cost tracks the number of answers rather than the number of strings. Two lessons carry over. Find
out precisely what the mirror pairs up before you build anything (here the point shifts the pairing
by one). And accept candidates in exact arithmetic: a floating-point "is this an integer?" test is
useful for pruning but not for deciding membership.

## When to build, and when to filter

Building palindromes is cheap, but it is not always the right enumeration. The rule is to **drive
the search with whichever set is smaller and cheaper to produce, and use the other condition as the
filter.**

- [Problem 125](/solutions/0125/) wants palindromes below `10⁸` that are sums of consecutive
  squares. There are about `2·10⁴` palindromes, but testing whether one is a run of squares is
  awkward. The runs themselves are easy to produce with a running sum and few in number, so the
  natural direction is to generate the sums and test each one for being a palindrome. Deduplicate,
  because one palindrome can come from more than one run.
- [Problem 348](/solutions/0348/) wants palindromes with exactly four representations as `a² + b³`.
  Both directions cost `O(N^(5/6))`, so constant factors decide. Generating pairs needs no square
  roots, and for a fixed `b` the sums form one contiguous, vectorisable run. The size problem goes
  away by working in **digit-length bands** `[10^(d−1), 10^d)`. All palindromes in a band are known
  once the band has been scanned, so the answers come out in ascending order without guessing a
  bound. Inside a band every value has `d` digits, so the palindrome test becomes a sequence of
  outer-pair comparisons, and each comparison discards about nine values in ten.
- [Problem 473](/solutions/0473/) is the opposite case. It wants the integers up to `10¹⁰` whose
  representation in the [golden-ratio base](https://en.wikipedia.org/wiki/Golden_ratio_base) is a
  palindrome. Converting ten billion integers to base φ is hopeless, and the palindromic strings are
  far rarer than the integers, so the palindrome drives and integrality becomes the filter, applied
  as a running balance that prunes the construction (see above).

## Palindromes as a process: reversal

Digit **reversal** is the operation behind the palindrome test, and some problems use it as a
transformation in its own right.

[Problem 55](/solutions/0055/) iterates *reverse and add* (`n → n + rev(n)`) and asks which starting
values never reach a palindrome. These are [Lychrel numbers](https://en.wikipedia.org/wiki/Lychrel_number).
No number has been *proven* to be Lychrel in base 10, so the problem sets a bound: no palindrome
within 50 steps counts as Lychrel. Nothing here can be built ahead of time, because the trajectory
is the whole problem. Two practical details matter. First, test the result of each step, not the
seed: `4994` is already a palindrome and is still a Lychrel candidate. Second, the values grow by
roughly one digit every step or two, so after a few dozen steps they no longer fit in 64 bits. You
need [arbitrary-precision](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) integers,
or, in C, a decimal digit array that can add a number to its own reversal in a single pass.

[Problem 808](/solutions/0808/) uses reversal as a pairing. It wants prime squares whose digit
reversals are also prime squares, and it **excludes** palindromes because a palindrome reverses to
itself. Here the palindrome test is a rejection filter, and the candidate set comes from somewhere
else entirely: a streaming prime iterator, squared, reversed, and checked with an integer square
root.

## How to reason about it

- **Count before you loop.** About `2√N` palindromes lie below `N`. If your loop touches all `N`
  integers to find them, you are doing roughly `√N` times too much work.
- **Generate from the half.** Mirror a left half, insert a middle digit for odd lengths, and let the
  half's leading digit enforce "no leading zeros". For a fixed length, the half also orders the
  output.
- **Pick the sparser side to enumerate.** The palindrome is only a filter when the other condition
  is cheaper to enumerate (125, 348). It drives the search when it is the rarer set (36, 473).
- **Use the structure the mirror gives you.** Even length means a multiple of 11 in base 10 (4). The
  value is a linear form in the half-digits, which leads to a digit DP over residues (655) or a
  balance-pruned search over the half (473). In base 2, a palindrome must be odd (36).
- **When the palindrome comes from a process, keep the process honest.** Test the result of each
  step rather than the seed, bound the iteration explicitly, and budget for big integers (55).
- **Mind the representation.** "Palindromic" always means palindromic *in some base*. Fix the base,
  the leading-zero convention, and whether a radix point counts as a character before you write
  the test (473).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ● [0473](/solutions/0473/) — Phigital Number Base
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
