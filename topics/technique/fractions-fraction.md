<!-- tags: [fractions-fraction] -->
<!-- status: final -->
# fractions.Fraction

[`fractions.Fraction`](https://docs.python.org/3/library/fractions.html) is Python's exact
rational number: a numerator and a denominator, both arbitrary-precision `int`s, always kept in
lowest terms with the sign on the numerator. Arithmetic is closed (`+ - * /` of two Fractions give
a Fraction), comparison is exact, and `==` means equal as numbers. Problems keep reaching for it
for one reason: many Euler statements are about *ratios*, such as a fraction that cancels, a
convergent, or a Farey neighbour, and their answers are read off the reduced numerator or
denominator. In floating point, `1/3 + 1/3 + 1/3` only happens to round back to `1.0`. A
`Fraction` has no rounding to get lucky with. This page is part of the language-idioms series, so
it also covers what a Fraction turns into in C, and when the convenience costs more than it buys.

## The idea

A Fraction does four jobs, and each covered problem leans on a different one.

**It reduces for you.** Problem 33 multiplies the four digit-cancelling fractions together and wants
the denominator of the product in lowest terms. The solution folds them as Fractions, so the
reduction is the type's invariant rather than a step:

```python
return str(functools.reduce(
    lambda a, b: a * b,
    (
        fractions.Fraction(numerator, denominator)
        for denominator in range(2, 10)
        for numerator in range(1, denominator)
        for x in range(1, 10)
        if denominator != x != numerator
        if (10 * numerator + x) * denominator == (10 * x + denominator) * numerator
    ),
    fractions.Fraction(1, 1),
).denominator)
```

Note what the *test* uses: the cross-multiplied integer identity, not
`Fraction(10*n + x, 10*x + d) == Fraction(n, d)`. That is the right split. Fractions hold the
values that get carried forward, and the comparison stays a single integer multiply. Problem 71 is
the same idea in one line: `Fraction(3, 7) - Fraction(1, 7 * k)` comes back reduced, and the
answer is its `.numerator`.

**It evaluates a continued fraction as written.** A
[convergent](/topics/domain/convergent-continued-fraction) is
$a_0 + 1/(a_1 + 1/(a_2 + \cdots))$ cut off at some depth. With Fractions, that is the code.
Problem 65 recurses `e_denominator(k) + Fraction(1, rest)` to depth $n$. Problem 66 runs the same
thing as a backward loop over the [periodic](/topics/domain/periodic-continued-fraction)
expansion of $\sqrt{D}$ to find the [Pell](/topics/technique/pells-equation) solution,
`convergent = term + Fraction(1, convergent)`, and finishes with `.as_integer_ratio()` to unpack
$(x, y)$.

**It is an exact key for sets, sorts and equality.** A Fraction hashes by value, so
`Fraction(2, 4)` and `Fraction(1, 2)` are one set element. Problem 180 builds its admissible
fractions as `sorted({Fraction(a, b) for b in range(2, k + 1) for a in range(1, b)})`, which is
"reduced fractions with denominator $\le k$", deduplicated by construction. It then collects sums
in a `set[Fraction]`. Equality is the whole problem there: whether $x^n + y^n$ equals $z^n$ for
some admissible $z$, and a float would answer that wrongly (see
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality)). Problem 101
evaluates [Lagrange](/topics/technique/lagrange-polynomial) interpolants whose basis terms are
ratios $(x - x_j)/(x_i - x_j)$. Problem 236 uses `Fraction(p, q)` only as a `key=` to order ratios
exactly. Problem 198 parses its bound with `Fraction("1/100")`, because the constructor accepts the
string form.

**It keeps the value exact until the last decimal.** Some answers are rationals that must be
reported "rounded to two digits after the decimal point". Problem 523 is one. It asks for the
expected number of moves of an odd restart-from-the-front sort over all permutations of $n$
items. Once you see that the sort is insertion sort in disguise, the expectation is a short sum of
rational terms. The given example $E(10) = 115.725$ is exactly $4629/40$, which sits *on* a half. The
rounding is then the delicate step, and neither of Python's obvious tools gives the half-up answer:

```python
>>> x = Fraction(4629, 40)
>>> round(x, 2), f"{x:.2f}"       # Fraction rounds half to even
(Fraction(2893, 25), '115.72')
>>> round(115.725, 2)             # the float is 115.72499999999999…
115.72
```

So the solution keeps the sum as a Fraction and rounds once, in integers:
$\lfloor 100x + \tfrac12 \rfloor$ via `(x * 100 + Fraction(1, 2)).__floor__()`, then `divmod` by
100 to format the whole and decimal parts itself. The float version fails differently from the
Fraction version. The float has already moved off the half before `round` sees it, while the
Fraction is exactly on the half and `round` applies the banker's rule. Exact arithmetic fixes the
first problem. Choosing the rounding rule yourself fixes the second.

## When the overhead stops paying

Every Fraction operation runs a `gcd` to restore lowest terms, and the class is implemented in pure
Python. For a handful of values, as in problems 33 and 71, that cost is invisible. In a loop it is
not. I timed problem 65's convergent three ways on this machine: the Fraction form, the same backward
loop on a bare `(p, q)` pair (`p, q = a*p + q, p`), and the forward recurrence
$h_k = a_k h_{k-1} + h_{k-2}$:

| depth $n$ | Fraction | `(p, q)` pair | forward recurrence |
| --- | --- | --- | --- |
| 100 | 181 µs | 7.4 µs | 7.1 µs |
| 1 000 | 2.8 ms | 156 µs | 145 µs |
| 10 000 | 144 ms | 9.6 ms | 8.6 ms |

The factor of about 20 is entirely the reduction, and here the reduction is wasted. Consecutive
convergents satisfy $p_k q_{k-1} - p_{k-1} q_k = \pm 1$, so every $p_k / q_k$ is *already* in lowest
terms, and the `gcd` always returns 1. That is the general rule. Hand-roll the pair when the
mathematics guarantees coprimality (convergents, [Farey](/topics/domain/farey-sequence) and
[Stern–Brocot](/topics/domain/stern-brocot-tree) neighbours, where $bc - ad = 1$) or when you only
need one side of the ratio. Keep the Fraction when values come from arbitrary arithmetic and
might share factors, or when you need them hashed and compared.

Problem 198 is the example. It is about Farey neighbours $a/b < c/d$ and their midpoints
$(2ad+1)/(2bd)$. The fast solution never builds those midpoints as Fractions, because
$bc - ad = 1$ already makes the midpoint irreducible, so its denominator is just $2bd$. The
solution counts over integers $a, b, d$ and uses Fraction only to read the input. The brute-force
check beside it is the reverse: Fractions everywhere, because there it is the definition being
tested, not the speed.

## The counterpart in C

C has no rational type, so every C sibling decides the representation for itself. That forces the
question the Python could skip: does this value need to be reduced, and how big can it get?

- **Defer the reduction.** Problem 33's C keeps `num_product` and `den_product` as two
  `long long`s and calls `gcd` once at the end. The products of four one-digit numbers cannot
  overflow, so one reduction is enough.
- **Skip it when the maths guarantees it.** Problems 65 and 66 represent a convergent as a
  numerator–denominator pair of hand-rolled base-$10^9$ `BigInt`s, using only multiply-by-small and
  add. There is no `gcd` anywhere, by the coprimality argument above. Problem 65's C goes further
  and carries only the numerator recurrence, since that is all the answer reads.
- **Reduce eagerly when the operands are arbitrary.** Problem 101's C defines
  `typedef struct { long long num; long long den; } Frac;`. It cross-reduces before multiplying
  ($\gcd(a, q)$ and $\gcd(p, b)$ for $\frac{a}{b}\cdot\frac{p}{q}$) and adds over a gcd-merged
  denominator in [`__int128`](/topics/technique/int128), so the intermediate products fit. That is
  what `Fraction` does for you, plus the overflow analysis that Python's unbounded `int` lets you
  skip.
- **Compare by cross-multiplying.** Where problem 236's Python picks the smallest ratio with
  `key=lambda pool: Fraction(pool[0], pool[1])`, its C compares $a/b < c/d$ as $ad < bc$ on the
  integers directly. That needs the same check that the products fit.
- **Use a real rational type when nothing stays small.** In problem 523, the common denominator
  grows like $\operatorname{lcm}(2, \dots, n)$ and the numerators grow exponentially, so no
  `long long` pair survives and no invariant lets you skip the reduction. Its C uses GMP's
  [`mpq_t`](https://gmplib.org/manual/Rational-Number-Functions), which is the closest thing C has
  to `Fraction`: arbitrary-precision, and kept in lowest terms by `mpq_add` once each term has been
  `mpq_canonicalize`d. The half-up rounding is ported the same way, with `mpz_fdiv_q` on
  $100x + \tfrac12$.

Going in the other direction, a C `num`/`den` pair translates into Python as two `int`s, not as a
Fraction, unless the C was reducing anyway. Translating it to a Fraction adds a gcd per step that
the C never paid ([parity across languages](/topics/takeaway/parity-across-languages)).

## How to reason about it

- **Use a Fraction for values, and integers for tests.** Carry results that need reducing as
  Fractions. Do one-off comparisons by cross-multiplying, as problem 33 does, which avoids building
  two objects to throw away.
- **Ask whether the gcd can ever be nontrivial.** If an invariant like $bc - ad = 1$ says no, the
  Fraction is paying about 20× for a guarantee you already have. Use a `(p, q)` pair.
- **Read the parts with `.numerator` and `.denominator`.** They are always reduced and the
  denominator is always positive, so the "answer is the denominator in lowest terms" problems need
  no extra step. `.as_integer_ratio()` gives both at once.
- **Know the neighbouring tools.**
  [`limit_denominator(N)`](https://docs.python.org/3/library/fractions.html#fractions.Fraction.limit_denominator)
  returns the closest fraction with denominator $\le N$, the best-approximation question behind
  Farey and Stern–Brocot problems. `math.gcd` is the hand-rolled path. Building a Fraction *from* a
  float gives you the float's exact binary value (`Fraction(0.1)` is not $1/10$), so construct from
  integers or strings.
- **Round once, at the end, using a rule you chose.** When the answer is a decimal rendering of a
  rational, keep everything exact and convert only in the formatter. `round()` and `:.2f` on a
  Fraction round half to even. If the problem's numbers land on halves, as problem 523's do, write
  the floor-of-plus-a-half yourself.
- **Exact is not the same as correct.** A Fraction makes the arithmetic right. It cannot make the
  formula right. Problem 71 asks for the left neighbour of $3/7$ among fractions with denominator
  $\le N$. That neighbour is $p/q$ with $3q - 7p = 1$ and $q$ as large as possible. It is not
  $3/7 - 1/(7\lfloor N/7\rfloor)$ in general: for $N = 8$ the neighbour is $2/5$, while the
  shortcut gives $2/7$. The reduced numerator from the shortcut can still match the true one, so
  the result looks fine. Check closed forms against a brute force over small $N$, using Fractions
  in the brute force so that it can be trusted.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0523](/solutions/0523/) — First Sort I

<!-- /problems -->
