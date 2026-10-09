<!-- tags: [positional-notation] -->
<!-- status: final -->
# Positional notation

[Positional notation](https://en.wikipedia.org/wiki/Positional_notation) is the convention that a
string of digits $d_{k-1} \dots d_1 d_0$ means $\sum_i d_i \, b^i$: each symbol is worth its face
value times a power of the base $b$ fixed by where it sits. We use it so constantly that it
disappears — and that is exactly why it keeps turning up in Project Euler. A large family of
problems define their object by how a number is *written* rather than by what it *is*: digit sums,
reversals, rotations, palindromes, digits that must or must not appear, numbers glued together by
concatenation. Each of those is a question about the representation, and the recurring skill is
translating it back into arithmetic on the value, where the real tools live.

## Two views of the same number

Every problem on this page lives in the gap between two views:

- **The string view** — a sequence of digits you can index, sort, reverse, count and compare. It is
  how the problem is stated, and in Python it is one `str()` away.
- **The value view** — a polynomial in $b$ with digit coefficients. It is how carries, divisibility
  and bounds behave, and it is where algebra works.

The basic operations convert between them. `n % b` reads the last digit, `n // b` drops it,
`n * b + d` appends one, $\lfloor \log_b n \rfloor + 1$ counts them. Concatenating $a$ and a
$k$-digit $c$ is $a \cdot b^k + c$; moving the last digit $d$ of a $k$-digit $n = b\,m + d$ to the
front gives $d \cdot b^{k-1} + m$. Once a string operation is written like that, it is an equation
— and equations can be solved instead of searched.

For small inputs the string view is fine and honest. Problem 16 asks for the digit sum of $2^{1000}$,
and Python's arbitrary-precision integers make that literally `sum(int(c) for c in str(2**1000))`.
Problem 36 wants numbers palindromic in base 10 *and* base 2; the solution generates only the decimal
palindromes — by mirroring a left half, so each is built once rather than filtered out of a million
candidates — and tests the binary string with `bin()`. Problem 52's "permuted multiples" become a
string equality on sorted digits, a [canonical form](/topics/technique/canonical-form) for "same
multiset of digits". None of these need more than the representation itself.

## Turn the string into algebra

The problems get interesting once the search space outgrows the string view. Then the move is to
write the digit condition as an equation in the value.

Problem 168 asks for numbers that divide their own right-rotation, below $10^{100}$. Enumerating is
absurd, but writing $n = 10m + a$ and the rotation as $a \cdot 10^{k-1} + m = t\,n$ for a digit
ratio $t$ solves for $m$ outright: $m = a(10^{k-1} - t)/(10t - 1)$. What was a search over a
hundred-digit space becomes a few thousand candidate $(k, a, t)$ triples with one divisibility test
each. Problem 932 has the same shape: a number that splits into $a \Vert c$ with $a \Vert c = (a+c)^2$
is the equation $a \cdot 10^d + c = s^2$ with $s = a + c$, which rearranges to $10^d - 1 \mid s(s-1)$
— and that divisibility, over coprime consecutive integers, is solved by the
[Chinese remainder theorem](/topics/technique/chinese-remainder-theorem) rather than by scanning.
Problem 805 (shifted multiples) and the [cyclic numbers](/topics/domain/cyclic-number) behind
$142857$ belong to the same family: digit shifts are multiplications by $b$ modulo $b^k - 1$.

Partial digit constraints become congruences in the same way. Problem 206's square with alternate
digits pinned reads its last digits first: the low digits of $n^2$ depend only on the low digits of
$n$, because $n^2 \bmod 10^j$ is determined by $n \bmod 10^j$. That one fact cuts the candidates by
two orders of magnitude, and it is the whole engine of problem 284's
[steady squares](/topics/domain/automorphic-number), where $n^2 \equiv n \pmod{b^k}$ is built up one
digit at a time.

## Count by position, not by number

The second big family asks *how many* numbers below some bound have a digit property, or how often a
digit is written. Here the move is to iterate over **places** instead of numbers.

Problem 40's Champernowne digit falls out of the observation that the $d$-digit numbers form a band of
exactly $d \cdot 9 \cdot 10^{d-1}$ characters; walk the bands, then a floor division and a modulus
locate the digit:

```python
while length_with_num_digits < n:
    num_digits += 1
    length_till_num_digits = length_with_num_digits
    length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
```

Problem 156 counts how often a digit $d$ is written from $0$ to $n$; summed column by column, each
place value contributes a closed-form amount, so the count is $O(\log n)$ — a
[digit-counting function](/topics/domain/digit-counting-function). Problem 162 counts hexadecimal
strings containing 0, 1 and A by [inclusion–exclusion](/topics/technique/inclusion-exclusion-principle)
over forbidden symbols, because "avoid these digits" is a product of per-position choices. And when
the property depends on more than one position — problem 145's reversible numbers, where each column
of $n + \text{reverse}(n)$ couples mirror digits through the carry — the general tool is
[digit DP](/topics/technique/digit-dp): build the number one place at a time and carry along only the
state the property needs (a carry, a remainder, a running digit sum, a "still tight to the bound"
flag). The pages for [digit sum](/topics/domain/digit-sum), [palindromic numbers](/topics/domain/palindromic-number)
and [pandigital numbers](/topics/domain/pandigital-number) are this tag's most crowded neighbours.

Problem 885 is a reminder that position carries weight, not just identity: summing "digits sorted
ascending, zeros dropped" over all numbers groups the inputs by digit multiset, and the value of each
group follows from where each digit lands — smaller digits occupy the more significant places.

## The base is a parameter

Base 10 is an accident of anatomy, and several problems make the point by changing it.

- **Integer bases other than 10.** Problem 162 states its count in hexadecimal; problem 36 mixes
  bases 2 and 10; problem 926 sums the trailing zeros of $n!$ in *every* base, which turns into
  counting pairs $(b, k)$ with $b^k \mid n!$ — a question about the prime factorisation, since
  "trailing zeros in base $b$" is just divisibility by powers of $b$.
- **The base as structure.** Problem 288 hands you a number already written as $\sum T_n p^n$ with
  $0 \le T_n < p$ — that is, its base-$p$ digits — and [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula)
  in its digit-sum form, $v_p(N!) = (N - s_p(N))/(p-1)$, lets you answer without ever forming $N$.
  Recognising "this sum is a base-$b$ expansion" is often the whole problem. Problem 396's weak
  Goodstein sequences repeatedly reinterpret base-$b$ digits in base $b+1$.
- **Exotic bases.** Problem 473 uses base $\varphi$ (the golden ratio), problem 558 an irrational
  base, problem 508 the complex base $i - 1$, and mixed-radix systems such as the
  [factorial number system](/topics/domain/factorial-number-system) use place values that are not
  powers of one base at all. What survives
  is the core idea — value equals a weighted sum of digit times place — but uniqueness, carry rules
  and the set of allowed digits must be re-derived for each base, and that is where those problems
  put their difficulty.

## How to reason about it

- **Decide which view you are in.** String operations are clear and quick to write; if the space is
  small (problems 16, 36, 52), use them and stop. If it is not, translate the condition into the value
  view before writing a loop.
- **Read low digits as congruences, high digits as bounds.** The last $k$ digits are $n \bmod b^k$ —
  they compose with multiplication and are where modular arithmetic prunes. The leading digits and
  the digit count fix an interval $[b^{k-1}, b^k)$, which is where length-preservation arguments
  ("$6x$ must not gain a digit") come from.
- **Group by digit length.** Almost every closed form here is per length band: rotations, reversals,
  concatenation and leading-zero rules all depend on $k$, and fixing it first turns them into
  ordinary algebra.
- **Mind the leading zero.** It is the commonest off-by-one in the family: a rotation or reversal that
  produces a leading zero is not a $k$-digit number (problems 145, 168), and inclusion–exclusion over
  digit strings must treat the first position separately (problem 162).
- **Do not trust floating point for digit counts.** `len(str(n))` or an integer-only loop is exact;
  `int(math.log10(n)) + 1` is wrong near powers of ten for large $n$ — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
- **Watch the width.** Digit problems invite huge values ($10^{100}$, $2^{1000}$). Python hides that;
  a C port needs a modulus, a digit array, or a [carry-arithmetic](/topics/technique/carry-arithmetic)
  bignum — see [watch integer width](/topics/takeaway/watch-integer-width).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ○ [0316](/solutions/0316/) — Numbers in Decimal Expansions
- ○ [0361](/solutions/0361/) — Subsequence of Thue-Morse Sequence
- ○ [0368](/solutions/0368/) — A Kempner-like Series
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0414](/solutions/0414/) — Kaprekar Constant
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ○ [0425](/solutions/0425/) — Prime Connection
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0473](/solutions/0473/) — Phigital Number Base
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ○ [0520](/solutions/0520/) — Simbers
- ○ [0524](/solutions/0524/) — First Sort II
- ○ [0558](/solutions/0558/) — Irrational Base
- ○ [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ○ [0698](/solutions/0698/) — 123 Numbers
- ○ [0714](/solutions/0714/) — Duodigits
- ○ [0731](/solutions/0731/) — A Stoneham Number
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0776](/solutions/0776/) — Digit Sum Division
- ○ [0778](/solutions/0778/) — Freshman's Product
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0831](/solutions/0831/) — Triple Product
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0893](/solutions/0893/) — Matchsticks
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ○ [0963](/solutions/0963/) — Removing Trits
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [1003](/solutions/1003/) — Lonely Singles
- ○ [1004](/solutions/1004/) — Balanced Integer
- ○ [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
