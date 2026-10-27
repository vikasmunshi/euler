<!-- tags: [digit-sum, palindromic-number, string-slicing, positional-notation] -->
<!-- status: final 2026-10-14T12:24Z -->
# Digit Manipulation

A surprising share of Project Euler is about the *writing* of a number rather than the number:
reverse it, test it for a palindrome, add up its digits, sort them, map each one through a table.
Every one of those operations needs the same first step — get the digits out of the integer — and
there are exactly two ways to take it. Either you hand the integer to the runtime's formatter and work
on the resulting **string**, or you peel digits off with **arithmetic**, `n % 10` and `n // 10`, one
[positional](https://en.wikipedia.org/wiki/Positional_notation) place at a time. The two are
interchangeable in meaning and wildly different in cost, and the cost runs in *opposite directions*
in Python and in C. This page is about choosing between them; the algebra of the digit sum itself
(mod 9, carries, digit DP) lives on [Digit sum](/topics/domain/digit-sum).

## Two ways to read a number

Write $n = \sum_{i=0}^{D-1} d_i\,10^i$ with $D = \lfloor \log_{10} n \rfloor + 1$ digits. The
arithmetic route reads that sum right to left:

```python
def digit_sum(n: int) -> int:
    total = 0
    while n:
        n, d = divmod(n, 10)                     # d is the units digit; n drops one place
        total += d
    return total
```

The string route asks the formatter for all $D$ digits at once, most significant first, and then
treats them as a sequence:

```python
sum(map(int, str(n)))                            # digit sum
int(str(n)[::-1])                                # reversal
"".join(sorted(str(n)))                          # order-blind fingerprint
```

Two differences in *shape* matter before any timing does. The arithmetic loop yields digits
**least-significant first**, which is exactly the order a reversal needs — `r = r * 10 + n % 10`
builds the mirror image while it consumes the original, with no buffer at all. The string yields
them **most-significant first** and *all at once*, which is what you want for anything positional
from the left — prefixes, truncations, the left half of a palindrome, slicing in general (see
[String slicing](/topics/technique/string-slicing)). And the arithmetic loop never sees a leading
zero, while a string can carry one (`"007"`), which is either a bug or exactly the fixed-width view
you wanted.

## Python: the formatter is the fast path

In CPython the decision comes down to one fact: `str(n)` is a single call into C, while the
`divmod` loop is $D$ trips through the interpreter. Timings on the machine this page was written on
(CPython 3.14, nanoseconds per call):

| digits $D$ | `sum(map(int, str(n)))` | `divmod` loop | `int(str(n)[::-1])` | `r*10 + n%10` loop |
| ---------: | ----------------------: | ------------: | ------------------: | -----------------: |
|          1 |                     192 |            68 |                 130 |                 63 |
|          5 |                     267 |           217 |                 145 |                209 |
|          9 |                     352 |           395 |                 154 |                371 |
|         20 |                     608 |           967 |                 197 |              1 273 |
|        302 |                   6 971 |        24 925 |               1 840 |             46 908 |
|      6 021 |                 468 495 |     5 260 430 |           4 469 995 |         12 510 725 |

Below about five digits the string's fixed costs — allocate a `str`, call `int` per character —
lose to a handful of arithmetic steps. Past that the string wins, and once $n$ outgrows a machine
word the gap turns structural: each `n // 10` on a $D$-digit big integer is itself $O(D)$, so the
loop is **quadratic**, and every step of it is interpreted, whereas the formatter converts in C, a
word-sized chunk of digits at a time. Reversal tilts further toward strings than the sum does,
because `[::-1]` is a single C-level copy (an [extended slice](/topics/technique/extended-slice))
with no per-digit Python call at all.

That is why the public big-integer problems are one-liners. Problem 16 sums the digits of
$2^{1000}$, problem 20 those of $100!$, problem 56 those of every $a^b$ for $a, b < 100$ — each is
`sum(int(d) for d in str(...))` over Python's
[arbitrary-precision](/topics/technique/arbitrary-precision-arithmetic) integers, and the
hundreds-of-digits sizes involved sit squarely in the rows where the string is three to four times
faster. Problem 55 runs reverse-and-add on numbers that grow past fifty digits, and its whole inner
step is

```python
number += int(str(number)[::-1])
if str(number) == str(number)[::-1]: ...
```

— the [Lychrel](/topics/domain/lychrel-number) iteration written as directly as the statement.
Problems 4 and 36 test [palindromes](/topics/domain/palindromic-number) the same way, and 36 goes
further: it *generates* its decimal palindromes by string concatenation, `digits + digits[::-1]`
(the odd-length ones with a middle digit spliced in), and checks the binary side with
`bin(n)[2:][::-1]`. Problem 52's test that $x, 2x, \dots, 6x$ are digit permutations of one another
is a set of fingerprints, `"".join(sorted(str(k * x)))` — a canonical form the string gives you for
free. Problem 34 never leaves string-land: it keys its digit-factorial table by the characters
`"0"`…`"9"`, so a digit never has to become an `int`.

Two caveats keep this from being a blanket rule. First, since CPython 3.11 `str()` refuses integers
beyond 4 300 digits by default (a denial-of-service guard against quadratic conversion); the digit
sum of $2^{20000}$ needs `sys.set_int_max_str_digits(0)` first. Second, when the numbers are *small
and hot* — the successor function of an iterated map, called millions of times on values under
$10^7$ — the arithmetic loop is level with or ahead of the string, and it is what problems 74 and 92
use:

```python
while n > 0:
    result += digit_factorials[n % 10]           # problem 74: the digit-factorial successor
    n //= 10
```

The arithmetic form also *composes* with tables in a way the string does not. If the per-digit
function is additive, precompute it for $0 \dots 999$ inside `solve()` and the successor becomes
`T[n % 1000] + T[n // 1000 % 1000] + T[n // 1000000]` — three lookups instead of seven iterations,
which is digit manipulation in base 1000. Better still is not to touch each number's digits at all:
problem 92 counts digit-square-sum *buckets* by convolution and only ever classifies the few hundred
distinct sums, and problem 30 enumerates digit multisets rather than numbers. The fastest digit loop
is the one you replaced with a count.

## C: the formatter is the slow path

C reverses every conclusion. There is no interpreter overhead to amortise; `n % 10` and `n / 10` on
a `long long` compile to a multiply-and-shift by a magic constant, with no division instruction; and
`snprintf` is a general-purpose formatting engine — format-string parsing, a buffer to fill, a
`strlen` to find its end — invoked to do what a few instructions per digit already do. Measured over
twenty million twelve-digit values with `gcc -O2`:

| operation       | `% 10` / `/ 10` loop | `snprintf` + char loop |
| --------------- | -------------------: | ---------------------: |
| digit sum       |              11.9 ns |                36.9 ns |
| palindrome test |              12.8 ns |                38.9 ns |

So in C the arithmetic route is the default, and the solutions mostly take it: problems 30, 34, 74
and 92 compute their digit maps with `% 10` loops, problem 36 extracts bits with `& 1` and `>>= 1`
for its binary palindrome check, and problem 52 pulls its digits out arithmetically before sorting
them. Where a C port still formats, it is usually a literal translation of a Python string idiom,
and usually off the hot path: problem 4 formats each product with `snprintf` and compares from both
ends (problem 34 formats too, for a digit-membership screen), but its descending search breaks out after a few candidates per row, so the 3× is immaterial.
Problem 36 is the instructive counter-case — it builds each palindrome with `snprintf("%s%s", …)`
and parses it back with `atoll`, a round trip through text for what is pure arithmetic:

```c
long long p = half, t = odd ? half / 10 : half;  /* mirror the left half onto itself */
while (t) { p = p * 10 + t % 10; t /= 10; }
```

The same goes for fingerprints. Problem 52's C sorts the digit characters with `qsort`, faithful to
the Python; a ten-slot histogram — or the counts packed four bits apiece into one integer — is the
same canonical form with no sort and no string compare.

The big-integer problems turn the question inside out. C has no built-in big integer, so problems
16, 20, 55 and 56 must choose a representation, and they choose **a little-endian array of decimal
digits**, `digits[0]` the units place. That is the string route, done by hand and kept permanently:
the number is never anything *but* its digits, so the digit sum is a plain loop over the array, and
problem 55's reverse-and-add needs no reversed copy at all — index $i$ of the little-endian number is
index $D-1-i$ of its reversal, so `a[i] + a[n-1-i]` adds the two in one pass. The price is paid in
multiplication, which must carry one digit at a time (see
[Carry arithmetic](/topics/technique/carry-arithmetic)); limbs of $10^9$ would multiply about nine
times faster and then make every digit query a `% 10` loop again. Store what the problem *asks
about*: when the output is a digit property, base-10 storage is the right trade.

## Choosing

- **Python, big integers or one-shot work** — use the string. `str`, slicing, `sorted` and `join`
  run in C; anything you write per digit does not. Mind the 4 300-digit conversion limit.
- **Python, small numbers in a hot loop** — the arithmetic loop is competitive, and it is the one
  that extends to chunked lookup tables. Better: restructure so the per-number digit work
  disappears (multisets, bucket counts, memoised chains).
- **C, anything that fits in 64 bits** — arithmetic, always. Reversal is `r = r*10 + n%10`, a
  palindrome is `n == rev(n)`, a fingerprint is a histogram. Reach for `snprintf` only to print.
- **C, big integers** — store decimal digits when the question is about digits; the representation
  *is* the string, and the manipulation becomes array indexing.
- **Either language** — mind the edges: `0` has one digit but the `while n` loop sees none; leading
  zeros exist in strings and in fixed-width digit arrays but not in integers; and the reversal of a
  number ending in `0` is shorter than the original, so `n == rev(n)` is the palindrome test only
  for the numbers that *are* palindromes — a trailing zero can never mirror a leading one.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0013](/solutions/0013/) — Large Sum
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0022](/solutions/0022/) — Names Scores
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ○ [0290](/solutions/0290/) — Digital Signature
- ○ [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0316](/solutions/0316/) — Numbers in Decimal Expansions
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0358](/solutions/0358/) — Cyclic Numbers
- ○ [0361](/solutions/0361/) — Subsequence of Thue-Morse Sequence
- ○ [0368](/solutions/0368/) — A Kempner-like Series
- ○ [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0414](/solutions/0414/) — Kaprekar Constant
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ○ [0425](/solutions/0425/) — Prime Connection
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0467](/solutions/0467/) — Superinteger
- ● [0473](/solutions/0473/) — Phigital Number Base
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ○ [0520](/solutions/0520/) — Simbers
- ○ [0524](/solutions/0524/) — First Sort II
- ● [0529](/solutions/0529/) — $10$-substrings
- ○ [0538](/solutions/0538/) — Maximum Quadrilaterals
- ○ [0551](/solutions/0551/) — Sum of Digits Sequence
- ○ [0558](/solutions/0558/) — Irrational Base
- ○ [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0698](/solutions/0698/) — 123 Numbers
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0711](/solutions/0711/) — Binary Blackboard
- ○ [0714](/solutions/0714/) — Duodigits
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ○ [0731](/solutions/0731/) — A Stoneham Number
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0776](/solutions/0776/) — Digit Sum Division
- ○ [0778](/solutions/0778/) — Freshman's Product
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0831](/solutions/0831/) — Triple Product
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0893](/solutions/0893/) — Matchsticks
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ○ [0954](/solutions/0954/) — Heptaphobia
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [1003](/solutions/1003/) — Lonely Singles
- ○ [1004](/solutions/1004/) — Balanced Integer
- ○ [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
