<!-- tags: [binomial-coefficient] -->
<!-- status: final 2026-10-14T07:09Z -->
# Binomial coefficient

The [binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient)
$\binom{n}{k} = \frac{n!}{k!\,(n-k)!}$ counts the ways to choose $k$ things from $n$. It turns up in
the problems below for two quite different reasons. Sometimes it is the *answer*: a counting
question, once its objects are seen as choices, collapses to a closed form in a handful of
binomials. And sometimes it is the *obstacle*: the problem names a coefficient like
$\binom{10^{18}}{10^9}$, which has billions of digits, and asks for something about it — a residue, a
prime exponent, a parity — that must be found without ever building the number. The first case is a
modelling skill; the second is a small, sharp toolkit of number theory. I treat them in turn.

## Seeing the choice

The skill is recognising that the objects being counted are subsets in disguise. A few disguises
recur often enough to learn by sight:

- **Lattice paths.** A monotone path across an $n \times n$ grid is $2n$ steps of which $n$ go
  right; choose which ones, and problem 15 is $\binom{2n}{n}$
  (see [Lattice path](/topics/domain/lattice-path)).
- **Rectangles in a grid.** A rectangle is two of the $m+1$ vertical lines and two of the $n+1$
  horizontal ones, so problem 85 counts $\binom{m+1}{2}\binom{n+1}{2}$ — and because that count
  *factors*, problem 147 can sum it over every sub-grid as a product of two one-dimensional sums.
- **Multisets and sorted sequences.** A non-decreasing digit string is fixed by how many of each
  digit it uses, so [stars and bars](/topics/technique/stars-and-bars-combinatorics) counts them as
  $\binom{n+d-1}{d}$. Problem 113 counts every non-bouncy number below a googol this way, in a
  constant number of binomials; problems 885 and 862 lean on the same "only the digit content
  matters" observation, with the [multinomial](/topics/technique/multinomial-theorem)
  $\frac{n!}{c_0!\cdots c_9!}$ as the next step up.
- **Choose, then arrange.** When a count splits into *which* items and *how they are ordered*, the
  first factor is a binomial. Problem 158 is $\binom{26}{n}$ letter sets times the Eulerian count of
  orderings with one ascent.
- **Ratios as probabilities.** $\binom{N-K}{n}/\binom{N}{n}$ is the probability that a draw of $n$
  from $N$ misses a given $K$. With linearity of expectation that is the whole of problem 493 — one
  ratio of binomials instead of an enumeration of every colour split.

The pattern is to stop counting objects and start counting *decisions*. Once each object
corresponds to exactly one set of choices, the binomial is the count, and the remaining work is
bookkeeping — usually an [inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
correction for the degenerate cases (problem 113 subtracts the repdigits it counted twice).

## Computing one without overflow

When the coefficient is merely large, not astronomical, the practical question is how to evaluate
it. The factorial formula is correct and wasteful: $\frac{(2n)!}{(n!)^2}$ builds two numbers far
bigger than the answer. Two better routes:

- **The multiplicative recurrence** $\binom{n}{r+1} = \binom{n}{r}\cdot\frac{n-r}{r+1}$ walks a row of
  [Pascal's triangle](/topics/technique/pascals-triangle) with every intermediate value an exact
  integer — divide *after* multiplying and the division is always exact. Problem 53 uses it with an
  early exit, because a row is symmetric and unimodal: the first $r$ past the threshold settles
  the whole middle of the row at once.

  ```python
  c = 1
  for r in range(0, n // 2 + 1):
      if c > threshold:
          count += n - 2 * r + 1
          break
      c = c * (n - r) // (r + 1)
  ```

- **The additive recurrence** $\binom{n}{k} = \binom{n-1}{k-1} + \binom{n-1}{k}$ builds a whole table
  with additions only, which is the right shape when you need many coefficients at once, or need
  them modulo something where division is awkward.

In Python the standard library already has [`math.comb`](https://docs.python.org/3/library/math.html#math.comb),
which is exact and fast; in C, the recurrences above with 64-bit (or 128-bit) integers are the
safe default — $\binom{68}{34}$ is already past $2^{64}$, so know your bound.

## Knowing it without building it

The harder half of the tag is the problems that name a coefficient too large to write down. Three
theorems carry almost all of them, and they share a single picture: **the arithmetic of
$\binom{n}{k}$ modulo a prime $p$ lives in the base-$p$ digits of $n$ and $k$.**

| Question about $\binom{n}{k}$ | Tool | What it reduces to |
|---|---|---|
| exponent of $p$ in it | [Legendre's formula](/topics/domain/legendres-formula) | $v_p(n!) - v_p(k!) - v_p((n-k)!)$, each $\sum_i \lfloor n/p^i \rfloor$ |
| the same, structurally | [Kummer's theorem](/topics/domain/kummers-theorem) | the number of carries adding $k$ and $n-k$ in base $p$ |
| its residue mod $p$ | [Lucas's theorem](/topics/domain/lucass-theorem) | $\prod_i \binom{n_i}{k_i} \bmod p$ over base-$p$ digits |
| its residue mod $m$ squarefree | Lucas per prime + [CRT](/topics/technique/chinese-remainder-theorem) | one small residue per prime factor of $m$ |

**Exponents.** Problem 231 asks for the prime factorisation of a coefficient with around a million
digits; Legendre's formula gives each prime's exponent with a few integer divisions, so the work is
one pass over the primes up to $n$. Problem 650 needs the factorisation of a *product* of a whole
row and gets it the same way, then updates the exponent vector incrementally as $n$ grows rather
than recomputing it. Kummer's form of the same fact is what makes conditions on exponents cheap to
*test*: problem 203 decides whether a 29-digit coefficient is squarefree by checking that no prime
produces two carries — a few digit additions on small numbers instead of a factorisation. For
$p = 2$ the carry count becomes popcounts, $s_2(k) + s_2(n-k) - s_2(n)$, and problem 704 turns into a
question about bit patterns; problem 792 asks the same $2$-adic kind of question of a whole sum of
central binomials.

**Residues.** Lucas's theorem says $\binom{n}{k} \not\equiv 0 \pmod p$ exactly when every base-$p$
digit of $k$ is at most the matching digit of $n$. Counting the entries of a row not divisible by
$p$ is then a product $\prod_i (n_i + 1)$ over $n$'s digits, and that product is self-similar: over
a full block of $p^m$ rows it sums to $\left(\binom{p+1}{2}\right)^m$. Problem 148 counts the entries
of a billion rows of [Pascal's triangle](https://en.wikipedia.org/wiki/Pascal%27s_triangle) not
divisible by $7$ by recursing on the leading base-$7$ digit — the
[Sierpiński-like fractal](https://en.wikipedia.org/wiki/Sierpi%C5%84ski_triangle) you see when you
colour the triangle mod $p$, turned into an algorithm. Problem 365 takes the residue of
$\binom{10^{18}}{10^9}$ modulo a product of three primes by applying Lucas to each prime and
gluing with the Chinese remainder theorem; problem 242 uses the mod-$2$ case to make a parity
question over $10^{24}$ pairs collapse into a statement about binary digits.

## How to reason about it

- **Translate before you compute.** If a count has a "choose" in it, find the bijection to subsets
  or multisets first; enumeration is almost never the intended route, and the binomial form often
  exposes a factorisation (problem 147) or a symmetry (problem 53) the enumeration hides.
- **Prefer the exact integer path.** Floats lose $\binom{n}{k}$ around $n \approx 60$; a
  probability that is a ratio of binomials (problem 493) should be carried as an exact rational and
  rounded once at the end.
- **If the coefficient is huge, the question is about primes.** Ask which prime-local fact is being
  requested — an exponent (Legendre / Kummer), a residue (Lucas), a residue mod a composite (Lucas
  plus CRT) — and work on the digits of $n$ and $k$, never on the number.
- **Know the edges of the toolkit.** Lucas's theorem is for prime moduli; prime *powers* need
  Granville's generalisation or a $p$-free factorial computation, and a modulus with a repeated
  prime factor cannot simply be split by CRT into prime fields. Check the factorisation of the
  modulus before reaching for the clean version.

The [primes in Pascal's triangle](/topics/number-theory/primes-in-pascals-triangle) page follows the
divisibility half of this story further; [Factorial](/topics/domain/factorial) covers the
factorials that every formula above is built from.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0242](/solutions/0242/) — Odd Triplets
- ○ [0267](/solutions/0267/) — Billionaire
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0468](/solutions/0468/) — Smooth Divisors of Binomial Coefficients
- ● [0493](/solutions/0493/) — Under the Rainbow
- ○ [0498](/solutions/0498/) — Remainder of Polynomial Division
- ○ [0567](/solutions/0567/) — Reciprocal Games I
- ○ [0568](/solutions/0568/) — Reciprocal Games II
- ○ [0588](/solutions/0588/) — Quintinomial Coefficients
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0792](/solutions/0792/) — Too Many Twos
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ○ [0831](/solutions/0831/) — Triple Product
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0885](/solutions/0885/) — Sorted Digits

<!-- /problems -->
