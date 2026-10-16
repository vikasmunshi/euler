<!-- tags: [linear-recurrence-with-constant-coefficients] -->
<!-- status: final -->
# Linear recurrence with constant coefficients

A [linear recurrence with constant coefficients](https://en.wikipedia.org/wiki/Linear_recurrence_with_constant_coefficients)
defines each term as a fixed weighted sum of the $d$ terms before it:

$$a_n = c_1 a_{n-1} + c_2 a_{n-2} + \dots + c_d a_{n-d}.$$

The [Fibonacci numbers](/topics/domain/fibonacci-sequence) are the standard example, with $d = 2$
and $c_1 = c_2 = 1$. The problems below arrive dressed as continued fractions, triangles, prefix
codes, board tours, digit strings, two-variable functions, card games and points spreading across
a plane. In every one, the
quantity being asked for is produced by the *same linear step applied over and over* to a small,
fixed state. That is all a constant-coefficient recurrence is. Once I can see it, a question about
the $10^{12}$th or $10^{18}$th term costs a logarithm, not a loop.

## The idea: a fixed linear map on a finite state

Stack the last $d$ terms into a vector. Then one step of the recurrence is multiplication by a
fixed $d \times d$ matrix, the [companion matrix](https://en.wikipedia.org/wiki/Companion_matrix),
and $a_n$ is a component of $M^n$ applied to the seed. Two consequences do most of the work:

- **The roots of the characteristic polynomial set the growth.** That polynomial is
  $x^d - c_1 x^{d-1} - \dots - c_d$. When its roots $r_i$ are distinct,
  $a_n = \sum_i k_i r_i^{\,n}$, and the largest root sets the growth rate. The terms of
  [Problem 57](/solutions/0057/) grow by $1 + \sqrt2$ per step. The almost-equilateral triangles of
  [Problem 94](/solutions/0094/) grow about fourfold. The level counts in Problem 219 grow by the
  real root of $x^4 = x^3 + 1$, about $1.38$. A growth rate above $1$ means only $O(\log N)$ terms
  lie below any bound $N$, so *generating* the terms beats *searching* for them.
- **Any finite linear system produces one.** By the
  [Cayley–Hamilton theorem](https://en.wikipedia.org/wiki/Cayley%E2%80%93Hamilton_theorem), a
  matrix satisfies its own characteristic polynomial. So *any* quantity read off a fixed linear
  map on $m$ states obeys a recurrence of order at most $m$, even when you never write the map
  down. That is why a transfer matrix over the column states of a $4 \times n$ board (Problem 237),
  or a digit [automaton](/topics/technique/finite-state-machine) (Problem 529), must yield a
  recurrence.

There are two ways to get the coefficients. Most of these problems **derive** them: a convergent
update $(p, q) \to (p + 2q, p + q)$, a
[Pell equation](/topics/technique/pells-equation)'s solution ladder, a leaf of cost $c$ splitting
into costs $c + 1$ and $c + 4$, or a card run's win bias conditioned on the first turn. Problems
237, 529 and 957 instead **discover** them from computed terms, which the takeaway
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence) covers in
detail. Problem 529 uses
[Berlekamp–Massey](/topics/technique/berlekamp-massey-algorithm) because its order runs into the
thousands.

Discovery has a price: pinning down a recurrence of order $d$ takes $2d$ terms, and a few more to
confirm it. Problem 957 shows what to do when terms are expensive. Its plane construction can be
simulated exactly only through day 13, because the point sets grow about fourfold a day. The count
it needs, the number of concurrent line triples, grows like $\tfrac{7}{12}a_n^2$ for a pencil size
$a_n$ that already has a closed form. The square of a recurrent sequence is itself recurrent, so
that leading part is no mystery. Subtracting it leaves a residual of order only five, which ten
simulated terms fix and the remaining three confirm. Peeling off the part you already understand
lowers $d$, and with it the number of terms you have to pay for.

In code, a low-order recurrence is just a simultaneous update. Problem 57's whole step is:

```python
numerator, denominator = (numerator + 2 * denominator, numerator + denominator)
```

The tuple assignment matters: both new values must come from the *old* pair.

## Reaching a far term

How I evaluate a recurrence depends on the order $d$ and how far away the target index is:

| Situation | Method | Cost |
|---|---|---|
| Every term up to $n$ is needed, or terms grow past the bound fast | step the recurrence | $O(nd)$, or $O(\log N)$ steps when terms grow geometrically (57, 94, 219) |
| One far term, small $d$ | [matrix power](/topics/technique/matrix-exponentiation) of the companion matrix | $O(d^3 \log n)$ (237, 940) |
| One far term, moderate $d$ | $x^n \bmod$ the characteristic polynomial | $O(d^2 \log n)$ |
| Characteristic roots are small integers | solve once for the closed form $\sum k_i r_i^{\,n}$ | $O(1)$ big-integer operations (957) |
| One far term, $d$ in the thousands | [Bostan–Mori](https://arxiv.org/abs/2008.08822) on the [generating function](/topics/domain/generating-function) $P(x)/Q(x)$, with [FFT](/topics/technique/fast-fourier-transform) products | $O(d \log d \log n)$ (529) |

The polynomial method is worth keeping in a scratch file. It never forms the matrix: it
computes $x^n$ modulo the characteristic polynomial by
[repeated squaring](/topics/technique/exponentiation-by-squaring), then takes a dot product of the
result with the seed:

```python
def nth_term(coeffs, seed, n, mod):          # a_k = sum(c_i * a_(k-1-i)); seed = a_0 .. a_(d-1), d >= 2
    d = len(coeffs)

    def mulmod(p, q):                         # p * q reduced mod the characteristic polynomial
        r = [0] * (2 * d - 1)
        for i, a in enumerate(p):
            for j, b in enumerate(q):
                r[i + j] = (r[i + j] + a * b) % mod
        for k in range(2 * d - 2, d - 1, -1):  # fold x^k into lower powers using the recurrence
            for i, c in enumerate(coeffs):
                r[k - 1 - i] = (r[k - 1 - i] + r[k] * c) % mod
        return r[:d]

    result, base = [1] + [0] * (d - 1), [0, 1] + [0] * (d - 2)
    while n:                                  # x^n mod the polynomial, by repeated squaring
        if n & 1:
            result = mulmod(result, base)
        base = mulmod(base, base)
        n >>= 1
    return sum(r * s for r, s in zip(result, seed)) % mod
```

Problem 529 shows why the last row of the table exists. Its minimised automaton still has
thousands of states, so a matrix power at that size would cost about $d^3 \log n$ operations, on the
order of $10^{12}$, which is far too many. Working on the generating function needs only polynomial products.

## Sums, products, and two indices

The sum $S_n = a_1 + \dots + a_n$ of a recurrent sequence is itself recurrent, of order one
higher. You get it by carrying the running total as one more state component, which is how
Problem 529 turns a count per length into a cumulative count. The termwise product of two
recurrent sequences is recurrent too, with characteristic roots the pairwise products $r_i s_j$.
That is why Problem 957 can treat $a_n^2$ as known and fit a recurrence only to what is left. Other
problems need a little more:

- **Problem 940** has a two-variable function, linear in each direction. It becomes
  $e_1^{\mathsf T} N^{n} M^{m} e_2$ for two $2 \times 2$ matrices. Because that expression is
  bilinear in the two powers, a double sum over Fibonacci-indexed arguments factors into two
  single sums of matrix powers. The $k^2$ pairs never have to be formed.
- **Problem 918** is linear but not constant-coefficient in $n$: the rule branches on the parity
  of the index. The same idea still applies. The pair $(a_n, a_{n+1})$ maps linearly to either
  child pair, so one term is a walk down the bits of the index. A
  [telescoping](https://en.wikipedia.org/wiki/Telescoping_series) rearrangement first collapses
  the partial sum to a single term.
- **Problem 951** uses a recurrence to *prove* something rather than to compute something far
  away. Each run of same-colour cards has a win bias that satisfies a two-term recurrence.
  Scaling by $2^L$ makes it an integer sequence, and reducing that sequence modulo $2$ shows it
  can vanish at only one run length. That single fact turns a probability question into a
  counting one.

## How to reason about it

- **Look for the finite state first.** If the object of size $n + 1$ is built from the object of
  size $n$ through a fixed linear rule on boundedly many quantities, a constant-coefficient
  recurrence exists. If the state grows with $n$, or the coefficients depend on $n$, it doesn't,
  and you need a different tool.
- **Pick the evaluator by $d$ and $n$, not by habit.** For a few terms, step. For one far term
  with small $d$, use a matrix power. Once $d$ reaches the hundreds, switch to polynomial methods.
  The growth rate tells you up front how many steps a bounded search will take.
- **Keep it in integers.** When the roots are irrational, the closed form $\sum k_i r_i^{\,n}$
  (for Fibonacci,
  [Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Binet's_formula)) is for
  reasoning, not for computing: in double precision it stops being exact after about seventy terms.
  When the characteristic polynomial factors into small integer roots, as Problem 957's does
  ($4$, $\pm 2$, $\pm 1$), the closed form *is* integer arithmetic. Clear the denominators of the
  $k_i$, evaluate, and assert that the division comes out exact. Exact big integers are correct,
  but they cost $O(n)$ digits per term, which is why Problem 57 is $O(n^2)$ overall.
- **Reduce under the modulus carefully.** Reducing after every product is valid because the
  answer is wanted modulo $m$. A negative coefficient must be stored as its residue, and the
  products must fit the word: a modulus below $2^{31}$ keeps a product below $2^{62}$ in C (see
  [watch integer width](/topics/takeaway/watch-integer-width)). Berlekamp–Massey divides, so it
  needs a prime modulus.
- **Seed from a verified index.** Some recurrences only hold from some index onward. Start the
  power from terms you have checked, and answer smaller inputs straight from the table.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0957](/solutions/0957/) — Point Genesis

<!-- /problems -->
