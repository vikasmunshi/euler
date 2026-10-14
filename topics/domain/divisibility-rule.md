<!-- tags: [divisibility-rule] -->
<!-- status: final -->
# Divisibility rule

A [divisibility rule](https://en.wikipedia.org/wiki/Divisibility_rule) decides whether `d | n` by
looking at the decimal digits of `n` rather than dividing. Most of us learned them as tricks: the
last digit for 2 and 5, the digit sum for 3 and 9, the alternating sum for 11. In Project Euler
they turn up because many problems define things *in terms of digits*: palindromes, rotations,
pandigitals, substrings. A rule that reads digits is what links those definitions to arithmetic.
I care less about the tricks than about the single fact they all come from. Once you see that
fact, you can derive the rule for any divisor and any digit operation yourself.

## The idea: everything is `10 mod d`

A decimal number is a polynomial in 10:

$$n = \sum_i a_i \cdot 10^i \quad\Longrightarrow\quad n \bmod d = \sum_i a_i \cdot (10^i \bmod d) \pmod d.$$

So the remainder of `n` depends only on its digits and on the sequence of powers `10^i mod d`.
Every classic rule is that sequence happening to be simple:

| `10^i mod d` | Divisors | Rule |
|---|---|---|
| `10 ≡ 0` | 2, 5, 10 | the last digit decides |
| `10^k ≡ 0` | 4, 8, 2^k, 5^k | the last *k* digits decide |
| `10 ≡ 1` | 3, 9 | the digit sum is congruent to `n` |
| `10 ≡ −1` | 11 | the alternating digit sum is congruent to `n` |
| `10^3 ≡ −1` | 7, 11, 13 (all divide 1001) | the alternating sum of 3-digit blocks |
| anything else | every `d` | Horner: `r ← (10·r + a) mod d`, one digit at a time |

The last row is the general case, and the others are just special cases of it. Reading
digits left to right while keeping the remainder `r` is a finite automaton with `d` states. That
automaton is the backbone of every digit-DP that asks "how many numbers with property X are
divisible by `d`". For divisors coprime to 10 there is also a dual form, the subject of
[274](/solutions/0274/): drop the last digit `b` and add `m·b`, where `m` is the inverse of 10
modulo `p`. That is the "multiply the last digit and add" rule for 7 and 13, written generally.
Writing `n = 10a + b` and multiplying by `m` gives `m·n ≡ a + m·b`, and multiplying by a unit
modulo `p` doesn't change whether something is zero.

A rule tells you about divisibility. It does not tell you about primality. Its use for primes is
negative: if a rule *forces* a small factor, then the candidate cannot be prime and you can skip it.

## The rules at work

**Palindromes and 11 ([4](/solutions/0004/)).** In an even-length palindrome, digit `i` and
digit `L−1−i` are equal, and their positions have opposite parity. So each pair contributes
`a − a = 0` to the alternating sum, and **every even-length palindrome is divisible by 11**. The
six-digit target of problem 4 must therefore carry a factor 11, and since 11 is prime, one of the
two factors must supply it. The solution uses this directly: when `a` is not a multiple of 11, the
inner loop steps `b` by 11:

```python
for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
```

That one rule removes ten of every eleven candidates before any palindrome check runs.
[655](/solutions/0655/) applies the same decomposition to a large prime: a palindrome is a sum of
*pairs* `a·(10^i + 10^{L−1−i})`, so you count palindromes divisible by `p` by running a remainder
DP over the paired weights `(10^i + 10^{L−1−i}) mod p`, not over the individual digits.

**Rotations and the last digit ([35](/solutions/0035/)).** A circular prime must stay prime under
every rotation, and every digit spends one rotation as the last digit. If any digit is even or 5,
then that rotation is divisible by 2 or 5. So a multi-digit circular prime uses only `{1, 3, 7, 9}`,
and the solution rejects anything containing `024568` before it builds a single rotation. The rule
is applied to a *set* of numbers at once, because rotation moves every digit through the position
the rule reads.

**Permutations and the digit sum ([41](/solutions/0041/)).** The digit sum doesn't change under
permutation, so the rule for 3 applies to all `n!` arrangements of a pandigital at once. The
digits `1..n` sum to `n(n+1)/2`, which is 45, 36, 21 and 15 for `n = 9, 8, 6, 5`. All of those are
multiples of 3, so every 9-, 8-, 6- and 5-digit pandigital is composite. Only lengths 7 and 4 are
left, and the search drops from `9!` candidates to `7! + 4!`. The same invariance drives
[491](/solutions/0491/): by the rule for 11, a double pandigital is divisible by 11 exactly when the
digits in odd positions and the digits in even positions have sums that differ by a multiple of
11. That turns "count the divisible arrangements" into "count the ways to split a multiset of
digits into two halves with constrained sums", which is a combinatorics problem with no
arithmetic left in it.

**Substrings and windows ([43](/solutions/0043/)).** Here the constraints are on 3-digit windows
`d_{k}d_{k+1}d_{k+2}` with divisors 2, 3, 5, 7, 11, 13, 17. The cheap rules give quick wins:
divisible by 2 means `d4` is even, and divisible by 5 means `d6 ∈ {0, 5}`. But the real point is
that the windows *overlap*, so each one fixes two of the next window's three digits. The solution
starts from the 44 multiples of 17 with distinct digits and prepends one digit at a time,
checking the new leading window against the next divisor in the chain. The overlap is what makes
backtracking prune so hard. [706](/solutions/0706/) and [413](/solutions/0413/) generalise this
to counting *substrings* divisible by `d`. A substring `n[i..j]` is a difference of prefixes
scaled by a power of 10. For `d = 3`, where `10 ≡ 1`, that reduces to "prefix digit sums that are
equal mod 3", so the count depends only on how many prefixes fall in each residue class. That
histogram is small enough to be the state of a DP.

## How to reason about it

- **Ask what the digit operation preserves.** Permutation preserves the digit sum, so think of 3
  and 9. Reversal and palindromes pair positions of opposite parity, so think of 11. Rotation and
  any operation that exposes the last digit point to 2 and 5. Windows and substrings mean prefix
  remainders. The right rule is usually the one whose invariant survives the problem's operation.
- **Use rules to prune, not to prove.** A rule cheaply rules out a whole family (every 8-digit
  pandigital, every rotation set containing a 4). It never certifies a prime. The candidates that
  survive still need a real test.
- **For divisors that aren't 2, 3, 5, 9 or 11, go straight to the remainder automaton.** Problems
  like [303](/solutions/0303/) (the smallest multiple written in small digits, found by a BFS over
  remainders) and [954](/solutions/0954/) (digit swaps and 7) never need a neat rule for 7. They
  need `10^i mod d` and a state that carries the remainder. A swap of digits `a` at `i` and `b` at
  `j` changes the remainder by `(b − a)(10^i − 10^j) mod d`, which is the same polynomial view as
  before.
- **Pitfalls.** Leading zeros change which numbers count (a rotation or substring that starts with
  0 is a shorter number, and some problems forbid it). Alternating sums are signed, so normalise
  them with `% 11` instead of comparing them to zero. Also, `10 ≡ 1` holds only modulo 3 and 9:
  the digit-sum test for 27 does not work. When in doubt, recompute `10^i mod d` instead of
  trusting a remembered trick.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ○ [0333](/solutions/0333/) — Special Partitions
- ○ [0383](/solutions/0383/) — Divisibility Comparison Between Factorials
- ○ [0402](/solutions/0402/) — Integer-valued Polynomials
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0486](/solutions/0486/) — Palindrome-containing Strings
- ○ [0491](/solutions/0491/) — Double Pandigital Number Divisible by $11$
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0635](/solutions/0635/) — Subset Sums
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ○ [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0714](/solutions/0714/) — Duodigits
- ○ [0954](/solutions/0954/) — Heptaphobia
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
