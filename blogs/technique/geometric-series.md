<!-- tags: [geometric-series] -->
<!-- status: final 2026-11-11T09:06Z -->
# Geometric series

A [geometric series](https://en.wikipedia.org/wiki/Geometric_series) is a sum whose terms share a
constant ratio: $1 + r + r^2 + \dots + r^{n-1}$. It turns up in a solution whenever something is
*repeated with a fixed multiplier*: a digit's weight in a positional number, a prime power's
divisors, a sequence that appends the same block each time, a count of strings that grows by a
fixed factor per letter, the chance that a failed round sends the game back where it started, a
coefficient sequence that repeats with a fixed period. Each time, the useful move is to replace the
loop with the closed form. Two awkward steps remain: dividing by $r - 1$, and raising $r$ to an $n$
that may be far too large to write down. Many of the problems below differ mainly in how they
handle those two steps. The rest use the closed form as a building block: inside a generating
function, over a run of equal digits, or as one step of eliminating a variable.

## The idea

The finite sum telescopes. Multiply by $r$, subtract, and nearly everything cancels:

$$\sum_{j=0}^{n-1} r^j = \frac{r^n - 1}{r - 1} \qquad (r \ne 1),$$

and for $|r| < 1$ the infinite tail converges to $\frac{1}{1 - r}$. Differentiating with respect to
$r$ (or telescoping once more) gives the
[arithmetico-geometric](https://en.wikipedia.org/wiki/Arithmetico%E2%80%93geometric_sequence)
companion:

$$\sum_{m=1}^{L} m\,x^m = \frac{x\bigl(1 - (L+1)x^L + L\,x^{L+1}\bigr)}{(1 - x)^2}.$$

In this repository the series appears in a handful of guises:

- **As a count.** $\sigma(p^e) = 1 + p + \dots + p^e = \frac{p^{e+1} - 1}{p - 1}$ is the sum of the
  divisors of a prime power. Because $\sigma$ is
  [multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function), the divisor sum of any
  factored number is a product of geometric series (650).
- **As a repunit.** $\frac{p^n - 1}{p - 1}$ is the base-$p$ number written with $n$ ones. Weighting
  a digit by it is what [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula)
  does in its digit-sum form (288). The digit sum also works in reverse: the smallest number with
  digit sum $9q + r$ is $r$ followed by $q$ nines, $(r + 1)\cdot 10^q - 1$ (684).
- **As an unrolled affine recurrence.** If $v \leftarrow x\,v + Q$ is applied $k$ times, then
  $v_k = v_0 x^k + Q\,\frac{x^k - 1}{x - 1}$. Problem 506's digit stream repeats with period 6, so
  every fifteenth term is the term fifteen places earlier with one full period appended:
  multiply by $10^6$, add the period's value. Summing the $v_k$ then adds a *second* geometric
  layer, since $\sum_k \frac{x^k - 1}{x - 1} = \frac{G - K}{x - 1}$, where $G$ is the first sum
  and $K$ the number of terms.
- **As a sum of powers.** A count that comes out as $\sum_k c_k\,k^L$ (eigenvalues of a
  transfer matrix, or roots of an exponential generating function) has one geometric series per
  base $k$ once you sum it over $L$. Problem 520 counts digit strings by
  [EGF](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function), where
  $\cosh x$ and $1 + \sinh x$ expand in $y = e^x$ to a Laurent polynomial. Every coefficient
  $L![x^L]$ is then $\sum_{k=-10}^{10} c_k k^L$, and summing over lengths gives 21 geometric series.
  The bases need not be few or fixed. In 479 [Vieta's formulas](https://en.wikipedia.org/wiki/Vieta%27s_formulas)
  collapse a product of cubic roots to the integer $r_k = 1 - k^2$, and the double sum
  $\sum_k \sum_p r_k^{\,p}$ becomes one closed-form series per $k$: $n$ series at $O(\log n)$ each,
  instead of $n^2$ terms. In 335 the bases come from experiment. Simulating a bean-sowing game for
  small sizes fits $M(2^k + 1) = 4^k - 3^k + 2^{k+1}$ exactly, and once a count has that shape its
  sum up to $K = 10^{18}$ is three geometric series.
- **As a geometric kernel.** In a linear recurrence $G(n+1) = r\,G(n) + b(n)$, a source term
  injected at step $n$ reaches step $m$ multiplied by $r^{m-n}$. Its share of the running total
  $\sum_{m \le L} G(m)$ is therefore the partial sum $\frac{r^{L-n+1} - 1}{r - 1}$. Problem 423
  unrolls such a Pascal-style recurrence with $r = 6$. Every source term picks up the weight
  $6^{L-n+1} - 1$, and the common $\frac{1}{5}$ is pulled out to the very end, so the solution
  needs one inverse rather than $L$ of them. The weights all come from one table of powers of 6,
  built as a running product rather than with one `pow` per term.

The infinite form turns up in probability, where "fail and go round again" with constant odds is a
geometric number of retries (232).

## Dividing by $r - 1$

Over the integers the division is exact, because $r - 1$ always divides $r^n - 1$. Under a modulus
it is not automatically available. The solutions take five routes:

| route | when it works | used in |
| --- | --- | --- |
| divide first, reduce after | the numerator fits before reduction | 288 |
| cancel it symbolically | a coefficient already carries the factor $r - 1$ | 684 |
| work modulo $m \cdot (r - 1)$, then divide | $r - 1$ shares a factor with $m$ | 319 |
| multiply by $(r - 1)^{-1} \bmod m$ | $\gcd(r - 1, m) = 1$ | 335, 423, 479, 506, 650, 711, 968 |
| special-case the ratio | $r = 1$ (or $r = 0$) | 479, 520 |

**Divide first.** Problem 288 needs the exponent of $p$ in $N!$ modulo $p^k$, with $N$ given by its
ten million base-$p$ digits. Legendre's formula makes each digit $T_n$ contribute
$T_n \cdot \frac{p^n - 1}{p - 1}$. Modulo $p^k$ that repunit stops changing once $n \ge k$, because
every higher power of $p$ vanishes. So all the long tail shares one constant
$R = \frac{p^k - 1}{p - 1}$. Both languages compute it as `(modulus - 1) // (p - 1)`, where
`modulus` is $p^k$ itself, so the division is an exact integer division with no inverse involved.
The first $k - 1$ repunits are built by Horner's rule, `acc = acc * p + 1`, which never divides at
all. When you can build the sum digit by digit, that is the simplest way to avoid the division.

**Cancel it.** In 684 the inverse digit sums over one full block of nine add up to
$45 \cdot 10^{q'} - 9$, so summing the blocks gives $45 \cdot \frac{10^q - 1}{9}$. The $9$ goes into
$45$, leaving $5(10^q - 1)$, and the closed form has no division left in it. Do the algebra before
you reach for an inverse: often the $r - 1$ is already there to cancel.

**Widen the modulus.** Problem 319 reduces to $F(m) = \sum_{h \le m} (3^h - 2^h - 1)$, which is
two geometric series and a count:
$F(m) = \frac{3^{m+1} - 3}{2} - (2^{m+1} - 2) - m$. The answer is wanted modulo $10^9$, and $2$ has
no inverse there. The solution therefore evaluates $3^{m+1} - 3$ modulo $2 \cdot 10^9$. The value is
always even, and its residue modulo an even modulus keeps that parity, so halving the residue gives
the right answer modulo $10^9$:

```python
twice = 2 * modulus
geo3 = ((pow(3, m + 1, twice) - 3) % twice) // 2
```

This works for any divisor $d$: compute modulo $d \cdot m$, divide exactly, and the quotient is
correct modulo $m$.

**Invert.** Problem 650 needs $\sigma(B(n))$ for a product of binomial coefficients, modulo the prime
$10^9 + 7$. Every prime $p \le 20000$ has $p - 1$ coprime to that modulus, so each solution
precomputes $(p - 1)^{-1}$ once by Fermat (`pow(p - 1, mod - 2, mod)`) and evaluates each factor as
$(p \cdot p^{e} - 1) \cdot (p - 1)^{-1}$. The tidy detail is that a prime with $e = 0$ gives
$(p - 1)(p - 1)^{-1} = 1$, so inactive primes need no special case in the product. The inverse
precomputation and the vectorised product are on
[modular multiplicative inverse](/blogs/domain/modular-multiplicative-inverse).
A composite modulus does not rule out inversion; it only means you have to check coprimality. In
506 the modulus is $123454321 = 41^2 \cdot 271^2$, and $10^6 - 1 = 3^3 \cdot 7 \cdot 11 \cdot 13
\cdot 37$ shares no factor with it, so the inverse exists. It cannot come from Fermat, though (see
below). The same holds in 335, whose modulus $7^9$ is composite but whose denominators 3 and 2
are coprime to it. In 711 the ratio is itself an inverse: the sums run over both $2^m$ and $2^{-m}$, and
$x = 2^{-1} \bmod p$ goes through the same closed forms as $x = 2$.

**Special-case the ratio.** When the ratios are data rather than constants, some of them are
degenerate. Problem 520's bases run over every $k$ from $-10$ to $10$. $k = 1$ makes the closed
form $0/0$, and the sum is simply the term count. $k = 0$ contributes only its $0^0 = 1$ term.
Negative $k$ need no special treatment, as long as the residue is normalised. A helper that takes
the ratio as an argument must guard these cases itself, or prove they cannot occur. In 479,
$k = 1$ gives $r_1 = 0$ and is simply skipped, while $r_k \equiv 1$ would need $k^2 \equiv 0$
modulo the prime $10^9 + 7$, which no $k \le n$ can satisfy. So the denominator $r_k - 1 = -k^2$
is always invertible, and the guard is an argument rather than a branch.

## When $n$ is too large to write down

The closed form needs $r^n$, and `pow` is $O(\log n)$, but that still assumes you hold $n$, and a
single ratio and coefficient for all $n$ terms. Three problems ask for sums at astronomically
large $n$ where one of those assumptions fails:

- **Reduce the exponent modulo $p - 1$.** In 684 the argument runs over Fibonacci numbers
  $f_i$ up to $i = 90$, so $q = \lfloor f_i / 9 \rfloor$ is the exponent of $10^q$. Since 10 is
  coprime to the prime $p$, [Fermat](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem)
  lets the exponent live modulo $p - 1$, while the linear term $9q$ lives modulo $p$. Both
  residues of $q$ have to come from $f_i$ without dividing a reduced value by 9, so the solution
  carries the Fibonacci recurrence twice, modulo $9p$ and modulo $9(p - 1)$. This is the widened
  modulus from 319, applied this time to the *exponent*.
- **Advance the power, not the exponent.** 520 needs $n = b^u$ for a range of $u$. It never forms
  $n$. Each step replaces $k^n$ by $(k^n)^b$ and $n \bmod p$ by $n b \bmod p$. The power feeds the
  $r^n$ of the closed form, and the residue feeds the $r = 1$ case, whose sum is just the count.
- **Sum by runs, not by terms.** In 889 the number of terms is about $2 \times 10^{18}$, which
  still fits a machine word, so `pow` would be enough for one series. The trouble is that the
  coefficients vary. The blancmange function of a rational $x$ rewrites as
  $\sum_q c_q 2^{-q}$, where $c_q$ counts the earlier binary digits that disagree with digit $q$.
  That count is *constant along any run of equal digits*, because nothing it counts changes
  inside the run. The binary expansion here is mostly long stretches of zeros with a few thousand
  short clusters of ones, so each run is one geometric series with a constant coefficient:
  $c_u\,(2^{N-u+1} - 2^{N-v})$ for the run from $u$ to $v$. With ratio 2 the $r - 1$ is 1 and
  there is nothing to divide. About 4,000 runs replace $2 \times 10^{18}$ terms. A piecewise-constant
  weight is as good as a constant one, provided the pieces are few.

## Swapping the order of summation

A geometric series is sometimes hidden in an index that does not look like a power. Problem 1006
sums the squares of every length-$k$ window of a long digit word. Each window splits into a left
and a right part at the window's position $r$, and the cross term is a double sum over digit
positions $i$ and $j$, nested inside the sum over $r$. Make $r$ the innermost sum instead. Then
$r$ appears only as a power of $10^{-2}$, so the inner sum is geometric with the factor
$\frac{1}{1 - 10^{-2}}$, and its closed form is the difference of two boundary terms. What is
left depends only on $i + j$, and that is the quantity the rest of the solution can walk along
the word with a matrix product. When a weight is a power of the outer index, try summing that index
first.

The same move works on infinite sums. Problem 779 asks for $\sum_{K \ge 1} \overline{f_K}$, where
each $\overline{f_K}$ is itself a series over the primes, weighted by $p^{-K}$. Every term is
positive, so the two sums may be
[interchanged](https://en.wikipedia.org/wiki/Fubini%27s_theorem#Tonelli's_theorem_for_non-negative_measurable_functions)
freely. Summing $K$ first turns $\sum_K p^{-K}$ into $\frac{1}{p - 1}$, and the double series
becomes a single series over the primes, whose terms fall off like $1/p^3$. For positive terms
the interchange needs no further justification; with signed terms you would have to check
absolute convergence first.

## Summing between symbolic bounds

The closed form $\sum_{x=L}^{U} r^x = \frac{r^{U+1} - r^L}{r - 1}$ does not need numeric bounds.
If $L$ and $U$ are linear in other variables, the result is again a combination of exponentials in
those variables, only with different bases. That closure property is what 968 relies on. It
sums the weight $2^{x_1}3^{x_2}5^{x_3}7^{x_4}11^{x_5}$ over the lattice points of a
five-dimensional polytope with about $10^{40}$ points, whose constraints all have the shape
$\pm x_i \pm x_j \le k$. Summing out one variable is a geometric series between the tightest
upper and lower bounds. Each bound has the form $\pm y + k$, so substituting it multiplies the
base of $y$ by $r$ or $r^{-1}$, and the integrand stays a sum of exponential monomials. The cost
is a case split on which bound is tightest, and the new comparisons have the same two-variable
shape. This is
[Fourier–Motzkin elimination](https://en.wikipedia.org/wiki/Fourier%E2%80%93Motzkin_elimination)
with a geometric series as the integration step. After five eliminations every piece is a
constant, and none of the work depends on how large the bounds are. The division is safe for a
structural reason: a variable's own prime appears only in its own base until that variable is
eliminated, so no base can collapse to 1.

## Geometric series inside a generating function

A sequence with periodic coefficients has a rational
[generating function](https://en.wikipedia.org/wiki/Generating_function), because each period is
a polynomial and the repetition is a geometric series in $x^{\text{period}}$. Problem 973 reduces
an expected XOR over a card-dealing chain to counting, for each bit $b$, the compositions of $n$
with an odd number of parts that have bit $b$ set. Give each part a sign: $+1$ on the first
$P = 2^b$ residues of each period $2P$, and $-1$ on the next $P$. The signed part generating
function is a geometric series, and the composition generating function $\frac{1}{1 - C_b(x)}$
simplifies to

$$\frac{(1-x)(1+x^P)}{1 - 2x + 3x^P - 2x^{P+1}}.$$

The denominator has four terms, so the signed counts satisfy a four-term linear recurrence and
each bit costs $O(n)$. The geometric series did its work symbolically: it turned an infinite,
periodic sum into a sparse denominator, and the sparse denominator is the algorithm.

## The infinite form: a self-loop solved in closed form

Problem 232 is a coin race. On their turn, Player 2 picks $T$ and scores $2^{T-1}$ with probability
$q = 2^{-T}$. A miss by both players returns the game to the *same* state, so a state's value
appears on both sides of its own equation. Iterating that equation would sum the series
$\sum_k \bigl(\tfrac{1-q}{2}\bigr)^k$ one term at a time. Instead the solution solves the linear
fixed point once per candidate $T$:

$$x = \tfrac12 h + \tfrac12\bigl(q w + (1 - q)x\bigr) \;\Longrightarrow\; x = \frac{h + q w}{1 + q}.$$

The denominator $1 + q$ is the geometric series' $1 - r$ with $r = \frac{1 - q}{2}$, rescaled by
2. A geometric number of retries is always a closed form, because the retries are
independent and the ratio does not change. The general pattern of collapsing self-loops is on
[probability distribution](/blogs/domain/probability-distribution).

The same series hides in an expectation. In 779, an integer whose smallest prime factor is $p$
picks up each further factor of $p$ with probability $1/p$, so the extra multiplicity follows a
[geometric distribution](https://en.wikipedia.org/wiki/Geometric_distribution), and its mean
$\sum_{j \ge 1} p^{-j} = \frac{1}{p - 1}$ is read off in closed form rather than estimated.

A periodic infinite expansion collapses the same way. In 889 the binary digits of $x$ repeat with
period $N$, and every later period adds the same constant to each coefficient $c_q$. The infinite
tail is therefore a geometric series in $2^{-N}$, and it folds into one finite sum over the first
period plus a constant. That also shows the scaled result is an integer, which is a useful check
before any code is written.

## C and Python

The algorithms match line for line. The differences come from integer width, from how an inverse
is formed, and from how a power of two is formed:

- **Width of the product.** In 288 the head and the tail product $R \cdot \text{tail\_sum}$
  reach about $10^{25}$. Python's integers absorb that. The C accumulates in `unsigned __int128` and
  reduces once at the end. 319 and 650 use `__int128` inside `mulmod` for the same reason.
  Python's `pow(b, e, m)` is already exact at any width.
- **Where the inverse comes from.** Python's `pow(x, -1, m)` inverts modulo any $m$ coprime to
  $x$, prime or not. The C has to choose. Against the prime $10^9 + 7$ (711), Fermat's
  `pow_mod(x, MOD - 2)` is enough. Against the composite moduli of 506 and 335, and 520's modulus,
  which is an input, the C uses the
  [extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm),
  because Fermat's exponent would give a wrong answer without any error.
- **Vectorised products.** 650's and 423's Python keep their tables in NumPy `uint64`/`int64`
  arrays, so every product of two residues must stay below $2^{63}$ or $2^{64}$. 650 multiplies
  the geometric factors pairwise in a tree reduction instead of one big `np.prod`. 423 builds its
  power table with a blocked running product. The C versions just multiply and reduce term by term in a plain loop.
- **Negative residues.** A ratio like 479's $1 - k^2$ is negative before reduction. Python's `%`
  always returns a non-negative result. C's `%` keeps the sign of the dividend, so the C adds the
  modulus before subtracting.
- **Exact powers of two.** 232 forms $2^{-T}$ as `2.0 ** -t` in Python and `ldexp(1.0, -t)` in C.
  Both are exact in binary64, so the two languages print the same digits (see
  [double-precision floating-point format](/blogs/technique/double-precision-floating-point-format)).

## How to reason about it

- **Spot the fixed ratio.** Digit weights, prime-power divisor sums, retry probabilities, a
  sequence that appends the same block, and sums of $a^h$ over a range are all geometric series.
  Write the closed form before writing a loop.
- **An affine step $v \leftarrow xv + Q$ unrolls to a geometric series.** Summing its iterates
  gives a second one (506). A source term fed into a $\times r$ recurrence contributes a partial
  geometric sum to the running total (423).
- **A count that is a sum of powers $\sum c_k k^L$ sums over $L$ as one series per base.** Guard
  the degenerate bases $k = 1$ and $k = 0$ (520), or prove they cannot occur (479). If small cases
  fit such a formula exactly, the sum over a huge range is a few series (335).
- **A factor of $m$ on each term means the arithmetico-geometric form,** $\sum m\,x^m$, with
  $(1 - x)^2$ in the denominator (711).
- **Decide how to divide before you reduce.** First see whether the algebra cancels $r - 1$.
  Otherwise check whether $r - 1$ is invertible modulo $m$, using extended Euclid if $m$ is not
  prime. If it is not invertible, widen the modulus by $r - 1$ and divide exactly. If the
  numerator fits, divide over the integers.
- **A huge exponent lives modulo $p - 1$** when the base is coprime to a prime $p$. Carry $n$ in
  that ring, widened if you must divide it (684). Or advance $r^n$ directly without ever forming
  $n$ (520).
- **Look for a stabilising tail.** Modulo $r^k$, the partial sums stop changing after $k$ terms,
  and a long loop collapses to a short head plus one multiplication (288).
- **Horner avoids the division entirely** when you need every partial sum anyway.
- **Sum the index that appears in an exponent first.** Its geometric closed form leaves only
  boundary terms (1006). With positive terms this works for infinite sums too (779).
- **A piecewise-constant coefficient is one series per piece.** Walk the runs, not the terms (889).
- **Symbolic bounds keep the closed form closed.** Summing $r^x$ between linear bounds leaves
  exponentials in the other variables, so variables can be eliminated one at a time (968).
- **Periodic coefficients mean a rational generating function.** Sum the period geometrically,
  and a sparse denominator gives a short recurrence (973).
- **A self-referencing state is a geometric series in disguise.** Solve the linear equation instead
  of iterating it to convergence.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0232](/solutions/0232/) — The Race
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ● [0479](/solutions/0479/) — Roots on the Rise
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0520](/solutions/0520/) — Simbers
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
- ● [0889](/solutions/0889/) — Rational Blancmange
- ● [0968](/solutions/0968/) — 5D Summation
- ● [0973](/solutions/0973/) — Random Dealings
- ● [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
