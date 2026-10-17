<!-- tags: [mobius-inversion-formula] -->
<!-- status: final -->
# Möbius inversion formula

Many counts are easy to take *with* multiplicity and hard to take without it. Counting all
fractions $k/n$ is trivial, and counting the *reduced* ones is the question. Counting all triangles
of perimeter at most $N$ has a closed form, and counting the *primitive* ones is the question.
Counting every lattice pair is a loop, and counting the *coprime* pairs is the question. The
[Möbius inversion formula](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula) connects
the easy count to the hard one. When the easy total is a sum of the primitive counts over divisors,
or over scalings, inversion undoes that sum and gives back the primitive count. Every problem below
has this shape: there is a total I can write down, and the answer is the primitive part hidden
inside it.

## The idea: three faces of one formula

The classical statement is about divisors. If $g(n) = \sum_{d \mid n} f(d)$ for every $n$, then

$$f(n) = \sum_{d \mid n} \mu(d)\, g(n/d).$$

In [Dirichlet convolution](/topics/domain/dirichlet-convolution) terms, $g = f * \mathbf{1}$ and
$\mu$ is the inverse of $\mathbf{1}$, so $f = g * \mu$. All the formula needs from $\mu$ is the
switch $\sum_{d \mid n} \mu(d) = [n = 1]$, which the
[Möbius function](/topics/domain/mobius-function) page derives. Computing $\mu$ itself is left to
the [Möbius function (application)](/topics/technique/mobius-function-application) page. This page
is about the *sums* that inversion turns around. In these solutions they come in three forms, and
recognising which form you are in is most of the work.

**1. The divisor form, inverted in place.** Problem 73 counts reduced fractions in a range by
taking Farey ranks. For a denominator $i$, $\lfloor i\,n/d \rfloor$ counts every numerator $k$
with $k/i \le n/d$. Each such $k/i$ reduces to a fraction whose denominator divides $i$, so this
is $g(i) = \sum_{b \mid i} f(b)$, where $f(b)$ is the number of *reduced* fractions with
denominator $b$. The solution never builds $\mu$. It inverts the sum directly:

```python
data = [i * n // d for i in range(max_d + 1)]   # g(i): every fraction, reduced or not
for i in range(1, max_d + 1):
    for j in range(2 * i, max_d + 1, i):
        data[j] -= data[i]                       # data[i] is already f(i) by the time we get here
```

The loop is correct because of the order it runs in. When the outer loop reaches $i$, every proper
divisor of $i$ has already subtracted its final value, so `data[i]` has become $f(i)$. That makes
it safe to subtract from $i$'s multiples. This is Dirichlet division by $\mathbf{1}$ done in place,
in $O(n \log n)$, and it is the right tool when you need $f$ at *every* index up to $n$.

**2. The summatory form, over floor quotients.** The second face uses scalings instead of
divisors. If every object of size at most $x$ is a multiple $g \cdot (\text{primitive object})$,
with the primitive object of size at most $\lfloor x/g \rfloor$, then

$$G(x) = \sum_{g \ge 1} F\!\left(\lfloor x/g \rfloor\right) \iff
F(x) = \sum_{d \ge 1} \mu(d)\, G\!\left(\lfloor x/d \rfloor\right).$$

Two solutions use this pair, and they apply it in opposite directions:

- **Problem 276** (primitive triangles) uses the *left-hand* identity as a recursion,
  $F(x) = G(x) - \sum_{g \ge 2} F(\lfloor x/g \rfloor)$. $G$ (all triangles with perimeter at most
  $x$) has a closed form via Alcuin's sequence, and the recursion only ever asks for $F$ at values
  $\lfloor N/k \rfloor$. The solution evaluates those in ascending order, so each one's dependencies
  are already known, and groups the $g$ that share a quotient
  ([quotient blocking](/topics/technique/quotient-blocking)). The total cost is $O(N^{3/4})$ and
  $\mu$ never appears. This is the same move as the
  [totient summatory recursion](/topics/technique/totient-summatory-recursion).
- **Problem 319** (bounded sequences) uses the *right-hand* identity. After a geometric reduction,
  the answer is the number of distinct reals $m^{1/i}$ in a range. $G$ counts all pairs $(m, i)$,
  which is a pair of geometric series, and inversion keeps only the minimal representations. Here
  $\mu$ does appear: the $\lfloor n/d \rfloor$ blocks are weighted by differences of the Mertens
  function, which is evaluated at the quotients by the
  [Mertens recursion](/topics/technique/mertens-function-application).

**3. The coprimality strip.** The third face is the divisor form applied to the gcd:
$[\gcd(a,b) = 1] = \sum_{d \mid \gcd(a,b)} \mu(d)$. Substitute it into a sum over coprime pairs and
swap the order of summation. The result is a sum over $d$ of an *unconstrained* sum with its range
scaled by $d$:

- **Problem 153** (Gaussian integer divisors) needs a sum over coprime lattice pairs $(a, b)$
  weighted by the norm $a^2 + b^2$. Stripping coprimality scales the norm by $d^2$, so the outer
  sum is $\sum_d \mu(d)\, d \cdot I(\lfloor N/d^2 \rfloor)$, and it only needs $\mu$ up to
  $\sqrt N$.
- **Problem 478** (mixtures) counts coprime $(c, k)$ under a linear bound. The result has the form
  $M(s) = \sum_d \mu(d)\, g(\lfloor n/d \rfloor, s)$, again blocked by quotient with Mertens
  weights, and here a *vector* of all $s$ is updated per block.
- **Problem 193** (squarefree numbers) applies the same strip to the largest square divisor
  instead of a gcd. Then $[n \text{ squarefree}] = \sum_{d^2 \mid n} \mu(d)$, and summing gives
  $Q(x) = \sum_{d \le \sqrt x} \mu(d) \lfloor x/d^2 \rfloor$. Problem 153 shows the same effect: an
  inner condition involving squares pulls the $\mu$ range down to $\sqrt x$.

## How to reason about it

**Find the poset first.** Inversion runs over a specific order: divisors of $n$, floor quotients
of $x$, or square divisors. Before writing any code, I write the "all objects = sum of primitive
objects" identity for a small case and check it numerically. Most mistakes here come from
inverting over the wrong order, for example using $\lfloor x/d \rfloor$ where the scaling is
really $d^2$ (as in 153 and 193).

**Choose μ-form or recursion-form by what you already have.** The $\mu$ form costs a sieve, plus
a Mertens evaluation once the quotients go past what you can sieve. It works best when $G$ is
cheap and closed-form at every quotient, as in 319, or when the $\mu$ range is only $\sqrt x$, as in
153 and 193. The recursion form needs no $\mu$ at all and memoises $F$ at the $O(\sqrt x)$
quotients. It works best when $G$ is closed-form and you want the primitive count at a single
point, as in 276. The in-place sieve fits when you need $f$ at every index, as in 73. All three
compute the same inverse.

**Watch the signs.** Inversion always subtracts. The running totals are signed even when every
final count is non-negative, so accumulators must be signed. When the answer is wanted modulo
something (319, 478), each $-1$ term needs a negative-remainder fixup. 319 also has to divide by 2,
which has no inverse modulo $10^9$, so it works modulo $2 \times 10^9$ and divides exactly.

**Get the boundaries right.** "Below $L$" means invert at $L - 1$ (193 does this). The $g = 1$ term
of the recursion is $F(x)$ itself, so it is the term you move across the equals sign. Blocks whose
quotient falls below the smallest meaningful size (153 skips $\lfloor N/d^2 \rfloor < 2$) can be
dropped entirely.

## Python and C

The algorithms match one-for-one across the two languages. The differences come from integer width
and vectorisation:

| Problem | Python | C |
|---|---|---|
| 73 | plain list, unbounded ints | casts `i * n` to `long long` before the product |
| 153 | `dict` memo for the divisor summatory | fixed-size open-addressing hash table, falling back to direct evaluation when full |
| 193 | `math.isqrt`, NumPy over chunks of $2^{22}$ to bound temporaries | `sqrtl` corrected by two loops, scalar loop that skips $\mu = 0$ |
| 276 | unbounded ints, nothing special | `__int128` throughout ($k(k+1)(2k+1)$ overflows 64 bits) and a hand-written decimal printer |
| 319 | NumPy strided slices for the sieve and inner sums | plain loops, `__int128` inside `mulmod` |
| 478 | NumPy `arange` / `cumsum` per block | line-by-line port with explicit negative-remainder fixups |

The Python versions get their speed by pushing the per-block inner sums into NumPy. In C the same
loops are plain code, and the extra care goes into overflow, since inversion's large intermediate
totals cancel down to a much smaller answer.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0478](/solutions/0478/) — Mixtures

<!-- /problems -->
