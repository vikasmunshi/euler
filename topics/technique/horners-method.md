<!-- tags: [horners-method] -->
<!-- status: final -->
# Horner's method

[Horner's method](https://en.wikipedia.org/wiki/Horner%27s_method) evaluates a polynomial by
nesting the multiplications:

$$a_n x^n + a_{n-1}x^{n-1} + \dots + a_1 x + a_0 = (\cdots((a_n x + a_{n-1})x + a_{n-2})x + \cdots)x + a_0.$$

It needs $n$ multiplications and $n$ additions, forms no power of $x$, and keeps one running value.
The same loop, `acc = acc * base + digit`, is how you read a number written in a positional system,
so Horner's method is not limited to polynomials. It reads digits in any
[mixed radix](/topics/technique/mixed-radix), including the factorial number system that ranks
permutations. In the three solved problems below it evaluates a closed-form cubic (28), folds a
33-million-digit factorial-base number under a modulus (720), and folds a factorial-base number
whose digits depend on the value read so far (868).

## The idea — one accumulator, highest digit first

The general form takes digits $d_0, d_1, \dots$ (most significant first) and radices $b_1, b_2, \dots$:

```python
acc = 0
for d, b in zip(digits, radices):
    acc = acc * b + d
```

With a constant radix $x$ this is polynomial evaluation. With radices $n, n-1, \dots, 1$ it turns a
[Lehmer code](https://en.wikipedia.org/wiki/Lehmer_code) into a permutation's rank,
$\sum_i d_i (n-1-i)!$, without computing a factorial. What it buys:

- **No large powers or factorials.** Every intermediate value is the number read so far, so it stays
  as small as the answer.
- **Reduction at every step.** `acc = (acc * b + d) % m` is valid because each step uses only
  ring operations, so a result mod $10^9 + 7$ never needs the full integer.
- **Fewer operations.** For a degree-$n$ polynomial, $n$ multiplies against roughly $2n$ for the
  naive sum of powers, and floating-point error is usually better too.
- **The prefix value is visible at each step.** At every step `acc` is the value of the leading
  digits. When the *next* digit depends on that prefix, Horner order is what makes the dependency
  available, as in 868.

## Three uses across the problems

**28, number spiral diagonals: nest the cubic.** Summing the four corners of each ring of the
spiral gives a closed form, a cubic in the side length $N$. The public solution writes it in Horner
form, so the whole answer is three multiplications and one exact division:

```python
return str((size * (size * (4 * size + 3) + 8) - 9) // 6)
```

This is $\frac{4N^3 + 3N^2 + 8N - 9}{6}$, evaluated with no `size ** 3`. In C the same expression
runs in `long long`, and the largest intermediate value is about $4N^3$, so the nested form is
enough to avoid overflow for any realistic $N$.

**720, unpredictable permutations: a factorial-base number mod $p$.** The answer is the rank of a
specific permutation of $2^{25}$ elements. The solution builds its Lehmer code by a doubling
recurrence and then reads the code as a factorial-base number,
$\text{rank} = 1 + \sum_i d_i (N-1-i)!$, with Horner's rule and a decreasing radix:
`acc = (d + mult * acc) % m`, with `mult` going $N, N-1, \dots$. A factorial like $(2^{25})!$ is never
formed. Each step is one multiply and one reduction, and the 33 million digits fold in linear time.

**868, belfry maths: a fold whose digits depend on the prefix.** The bell-ringers' rule is the
[Steinhaus–Johnson–Trotter](/topics/domain/steinhaus-johnson-trotter-algorithm) order, and the
swap count to reach a target is its rank. SJT sweeps the largest element across all positions once
per arrangement of the smaller ones, alternating direction. So the rank is again a factorial-base
number, read from the innermost level (size 2) outward with radix equal to the level. The
digit at each level is the largest element's offset, *measured from the left or right end
depending on whether the rank so far is odd or even*. Horner order supplies exactly that: the
running `rank` before the step is the parity source, then `rank = rank * level + offset`. Any other
evaluation order would need the prefix value recomputed.

## Python and C

- **28**: the same expression in both. Python divides with `//` and C with `/`, which is exact here
  because the numerator is divisible by 6 for odd $N$.
- **720**: Python builds the Lehmer code with NumPy slices and `concatenate`, but folds with Python
  integers, streaming the `int32` array in $2^{20}$-element chunks through `.tolist()` so that
  `acc * mult` never goes through a fixed-width dtype. C folds in a `long long` with `% m` on both
  factors. C is about 6 times faster, almost entirely in that fold, where Python handles each digit as an object.
- **868**: 18 symbols, so both are instant. Python uses `sorted`, `list.index` and `list.pop`; C uses
  fixed 64-slot arrays, an insertion sort, and shifts the array down by hand. $18! < 2^{63}$, so the
  accumulator fits in `long long`.

## How to reason about it

- **Use Horner for any polynomial evaluation.** Nested form avoids powers, halves the
  multiplications, and keeps intermediates at the size of the result.
- **Recognise positional numbers in disguise.** Ranks of permutations, mixed-radix counters, digit
  strings and base conversions are all Horner folds with the right radices.
- **Fold under the modulus.** Reduce `acc` at every step, and never build the factorial or power the
  formula mentions.
- **Use the prefix.** If a digit's meaning depends on the digits before it, as with SJT's
  direction, process most-significant first so `acc` holds that context.
- **Keep the accumulator exact in Python.** A NumPy fixed-width accumulator overflows silently; fold
  with Python `int` and reduce, or keep the operands below $\sqrt{2^{63}}$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0868](/solutions/0868/) — Belfry Maths

<!-- /problems -->
