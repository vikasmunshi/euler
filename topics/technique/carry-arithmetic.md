<!-- tags: [carry-arithmetic] -->
<!-- status: final -->
# Carry (arithmetic)

Python integers have no upper limit, so a Python solution that adds a hundred 50-digit numbers or
computes 100! never has to think about it. C's largest native integer is 64 bits, about 1.8 × 10¹⁹,
so the C sibling of the same solution has to do the arithmetic by hand. Every problem on this page
does it the way we learned at school: split the number into digits, work on one column at a time,
and pass the [carry](https://en.wikipedia.org/wiki/Carry_(arithmetic)) to the next column. The loop
is short and appears in nearly the same form each time. What changes from problem to problem is the
choice of base, the order of the digits, and when the carry is propagated.

## The idea

A non-negative integer is stored as an array of **limbs**, the "digits" of some base `B`:

$$N = \sum_{i} d_i \, B^i, \qquad 0 \le d_i < B.$$

Every operation is one pass over the limbs. A running carry holds whatever overflowed from the
column before. Here is multiplication by a small number, taken from Problem 20 (100!, stored as base-10 digits):

```c
for (int j = 0; j < num_digits; j++) {
    int prod = digits[j] * i + carry;
    digits[j] = prod % 10;
    carry = prod / 10;
}
while (carry > 0) {               /* the number grows at the top */
    digits[num_digits++] = carry % 10;
    carry /= 10;
}
```

The `% B` keeps the low part of the column in place. The `/ B` sends the high part to the next
column. The tail loop is the only place the number gets longer. Addition has the same shape with a
second operand instead of a multiplier, and its carry is never more than 1. Problem 25 runs it on Fibonacci terms in
base 10⁹ and loops `for (i = 0; i < maxlen || carry; i++)`, so the final carry gets its own limb.
Division by a small number is the mirror image. It walks from the most significant limb down and
passes a **remainder** downward instead of a carry upward:
`cur = rem * B + limb; limb = cur / x; rem = cur % x`. Problem 15 alternates the two and computes the
central binomial coefficient as the product of `(n + i) / i` for i = 1..n. Each step multiplies the
big number by `n + i` and then divides it exactly by `i`. The running value is always a binomial
coefficient, so every division is exact and the number never grows to the size of (2n)!.

Three design choices separate the implementations.

**Base.** Base 10 (Problems 13, 20) is the easiest to read. Digit sums and digit counts come
straight off the array, which is all Problem 20 needs. Base 10⁹ (Problems 15, 25) packs nine decimal
digits into each limb, so a loop runs nine times fewer passes. Printing is still easy: print the top
limb with `%llu` and every other limb with `%09llu`. Base 2³² (Problem 5) is what the hardware works
in natively. `% B` and `/ B` become a mask and a shift, but printing in decimal then needs repeated
division by 10. The limit on the base is **headroom**: the largest intermediate value,
`limb × multiplier + carry`, has to fit in the accumulator type. With a 64-bit accumulator, base 10⁹
leaves room to multiply by numbers up to about 1.8 × 10¹⁰. Base 2³² leaves room for any 32-bit
multiplier. Pick B so that `B × (largest multiplier)` fits in 64 bits.

**Order.** Little-endian storage (`limbs[0]` is the least significant) lets the number grow at the
end of the array, which is why Problems 5, 15, 20 and 25 all use it. Problem 13 stores its sum
big-endian because its input is a list of decimal strings with the most significant digit first.

**When to carry.** You don't have to propagate the carry after every operation. Problem 13 adds all
100 numbers into an `int` accumulator array column by column, and each column ends up holding at
most 100 × 9 = 900. Only then does it run one carry pass from right to left. This is the same
deferred-carry trick that real bignum libraries use: let the columns overflow their base as long as
the accumulator type still has room, then normalise once. Problem 13 adds a second trick on top.
It only needs the leading ten digits of the sum, so it adds only the first eleven digits of each
number. The eleventh digit is a **guard digit**: it collects most of the carry coming up from the
digits that were dropped.

## How to reason about it

- **First check whether you need a bignum at all.** This is the small-number case of Problem 5. Its
  main input, lcm(1..20), is a nine-digit number and fits easily in a `uint64_t`. A plain `long long`
  fold of `a / gcd(a, y) * y` would be enough. The extra test cases ask for n = 50 and n = 100, and
  those answers are past 10²¹, which is why the C solution uses limbs. Even then it never needs a
  full bignum by bignum operation. The gcd only needs `result mod y`, and that is the remainder
  from one short-division pass. After that, `lcm` is one exact divide by a small number and one
  multiply by a small number. **Bignum by small number** (Problems 5, 15, 20) is a much smaller job
  than bignum by bignum. Try to reduce a problem to it before you write general long multiplication.
- **Size the array from the mathematics, not by guessing.** 100! has 158 digits. Stirling's formula
  gives the count as about `n log₁₀ n − n log₁₀ e`. A Fibonacci term with n digits has an index of
  about 4.8n. A sum of k numbers with D digits each has at most D + ⌈log₁₀ k⌉ digits. Every
  solution here uses a fixed `MAX_LIMBS`. That is fine only if a comment explains the bound, as
  Problems 13 and 25 do, and if overflow fails loudly, as Problem 15's `bi_mul_ll` does with
  `exit(1)`. Silently dropping the top carry, as Problem 5's `break` does once its limbs run out,
  gives a wrong answer with no error.
- **Most bugs are at the edges.** The final carry needs its own limb. Leading zero limbs have to be
  trimmed after a division (`while (len > 1 && limbs[len-1] == 0) len--`) or the digit count will be
  wrong. Every limb after the first must be zero-padded when printed. Zero is a special case for
  both printing and counting digits.
- **Python is the reference.** The Python sibling of each solution is one line of native
  arithmetic, and it is the test oracle for the C code. That is why the solutions here state that
  they "mirror the Python sibling". The carry loop is extra machinery that the C version needs; it
  does not change the algorithm.

The carry also shows up outside bignum code, as **state**. In Problem 145 (reversible numbers,
where n + reverse(n) must have only odd digits), the solution never adds two whole numbers. Mirror
columns i and d−1−i share the same pair sum `a[i] + a[d-1-i]`, so a digit DP walks the columns and
keeps the incoming carry as part of its state, together with the pair sums still waiting for their
mirror column. That carry is the same one the schoolbook addition would have passed along. The
schoolbook rule does more than describe how to add. It also tells you which local information a
digit-by-digit search has to remember. Problem 181 is the plain bignum case again: its counts pass
64 bits, so its C solution keeps a DP table of base-10⁹ limb arrays, where each `+=` becomes a
carry-propagating add and the arrays grow by doubling.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0013](/solutions/0013/) — Large Sum
- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects

<!-- /problems -->
