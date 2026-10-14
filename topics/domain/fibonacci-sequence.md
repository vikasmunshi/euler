<!-- tags: [fibonacci-sequence] -->
<!-- status: final 2026-10-14 -->
# Fibonacci sequence

The [Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence) is `0, 1, 1, 2, 3, 5,
8, 13, …`, each term the sum of the two before it: `F(n) = F(n−1) + F(n−2)`. It is the smallest
recurrence that is not trivial, and that is why the archive returns to it more than thirty times —
first as a sequence to walk, then as an object with so much algebraic structure that almost every
question about it has a shortcut. The skill this page is about is knowing *which* face of the
sequence a problem is showing you, because each face comes with its own tool: a linear recurrence
you can jump along, an exponential you can take logarithms of, a periodic sequence modulo `m`, and a
number system.

## The idea: one recurrence, four faces

### A linear recurrence you can jump along

Walking the recurrence is fine while the index is small. [Problem 25](/solutions/0025/) only needs
the first term with 1000 digits — about 4800 steps — so a plain loop over big integers is the right
answer. [Problem 2](/solutions/0002/) adds one twist worth remembering: parity repeats with period
3 (odd, odd, even), so every third term is even, and the even terms satisfy their *own* recurrence,
`E(k+1) = 4·E(k) + E(k−1)`. Filtering a linear recurrence by a periodic condition gives another
linear recurrence:

```python
even_fib_a, even_fib_b = (2, 8)
while even_fib_a < max_limit:
    yield even_fib_a
    even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)
```

When the index is astronomical — [Problem 304](/solutions/0304/) wants `F(p) mod M` for primes `p`
near `10¹⁴` — walking is hopeless, but linearity lets you *jump*. In matrix form,
`[[1,1],[1,0]]ⁿ = [[F(n+1), F(n)], [F(n), F(n−1)]]`
([matrix form](https://en.wikipedia.org/wiki/Fibonacci_sequence#Matrix_form)), so
[matrix exponentiation](/topics/technique/matrix-exponentiation) reaches `F(n)` in `O(log n)`
multiplications. Squaring that matrix and reading off the entries gives the leaner
[fast-doubling](/topics/technique/fibonacci-fast-doubling) identities,

$$ F(2k) = F(k)\,\bigl(2F(k+1) - F(k)\bigr), \qquad F(2k+1) = F(k)^2 + F(k+1)^2, $$

which scan the bits of `n` and need only two values per step — about 47 doublings for an index near
`10¹⁴`, with every product reduced modulo `M`.

### An exponential you can take logarithms of

[Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Closed-form_expression),
`F(n) = (φⁿ − ψⁿ)/√5` with `φ = (1+√5)/2` the [golden ratio](/topics/domain/golden-ratio) and
`|ψ| < 1`, says that `F(n)` is `φⁿ/√5` rounded to the nearest integer. Two consequences come up
again and again. First, **growth**: `F(n)` has about `0.209·n` digits, and there are only about
`log_φ N` Fibonacci numbers below `N` — roughly 80 below `10¹⁷`. Any algorithm that touches "every
Fibonacci number up to the limit" is therefore logarithmic in the limit. Second, **leading digits**:
the fractional part of `n·log₁₀φ − log₁₀√5` gives the first digits of `F(n)` without forming it.
[Problem 104](/solutions/0104/) leans on exactly that split — the *last* nine digits come from the
recurrence run modulo `10⁹`, the *first* nine from the logarithm — so a number with tens of
thousands of digits is never built at all.

The closed form also shows up through its algebraic cousins. The
[generating function](/topics/domain/generating-function) `Σ F(k)xᵏ = x/(1 − x − x²)` turns
[Problem 137](/solutions/0137/)'s infinite series into a rational function; asking when it takes an
integer value becomes a [Pell equation](/topics/technique/pells-equation) with `D = 5`, whose
solutions are products of Fibonacci and [Lucas numbers](/topics/technique/lucas-number). When a
problem's algebra keeps producing `√5`, expect Fibonacci numbers to be the answer's skeleton.

### A periodic sequence modulo m

Reduced modulo any `m`, the pair `(F(n), F(n+1))` can take only `m²` values, and the recurrence runs
backwards too (`F(n−1) = F(n+1) − F(n)`), so the sequence is *purely* periodic. That period is the
[Pisano period](/topics/domain/pisano-period) `π(m)`. It is multiplicative in the useful sense
(`π` of a product of coprime factors is the `lcm` of their periods), and it is what
[Problem 853](/solutions/0853/) and [Problem 854](/solutions/0854/) are built on: instead of computing
`π(n)` for a billion `n`, you work out which primes can contribute a period dividing the target and
assemble `n` from them. The related *rank of apparition* — the first index at which `m` divides a
Fibonacci number — is the lens for divisibility questions such as squarefree Fibonacci numbers
([Problem 399](/solutions/0399/)). Periodicity is also why reducing modulo `10⁹` in Problem 104
loses nothing: a linear recurrence commutes with reduction.

### A number system

[Zeckendorf's theorem](/topics/domain/zeckendorfs-theorem) says every positive integer is a unique
sum of *non-consecutive* Fibonacci numbers, found greedily (`100 = 89 + 8 + 3`). That makes the
Fibonacci numbers a base, like powers of two, and it brings a whole family of problems into view.
[Problem 297](/solutions/0297/) sums the number of Zeckendorf terms over all `n` below `10¹⁷`:
because every `n` in `[F(i), F(i+1))` is `F(i)` plus a smaller representation, the totals over
those blocks obey a recurrence of their own, and the greedy decomposition of the limit stitches the
blocks together in `O(log N)` steps. [Problem 692](/solutions/0692/) takes the same shape through
[Fibonacci nim](https://en.wikipedia.org/wiki/Fibonacci_nim), where the winning move is the smallest
Zeckendorf summand; [Problem 755](/solutions/0755/) drops the non-consecutive rule and counts
*all* subsets of Fibonacci numbers with a bounded sum.

The binary shadow of the same rule — no two adjacent `1` bits — defines the
[fibbinary numbers](/topics/domain/fibbinary-numbers), and the number of such `n`-bit strings is a
Fibonacci number. That is the hidden reason [Problem 301](/solutions/0301/), nominally a Nim
problem, has a Fibonacci answer. The *strings* themselves form a recursive object too:
[Problem 230](/solutions/0230/)'s [Fibonacci words](https://en.wikipedia.org/wiki/Fibonacci_word)
concatenate their two predecessors, so their lengths follow the recurrence and any single digit can
be found by descending through the lengths — never materialising a string of `10¹⁷` characters.

## How to reason about it

- **Count the terms before you choose a method.** There are `O(log N)` Fibonacci numbers below
  `N`. A problem bounded at `10¹⁷` that only asks about Fibonacci numbers, or about Zeckendorf
  representations, is a recursion over about 80 levels, not a loop to the limit.
- **Small index → walk; huge index → jump.** Iterate the recurrence while it is cheap; switch to
  fast doubling or matrix powers modulo `M` once the index is beyond reach. Don't use Binet's
  formula in floating point for exact values — it is good for magnitudes and leading digits, not
  for the last digit of `F(500)`.
- **Split the head from the tail.** Trailing digits and residues come from the recurrence modulo
  `m`; leading digits and digit counts come from `log₁₀ φ`. The two never need the full number.
- **Modulo `m`, think period.** Any question about `F(n) mod m` for many `n`, or about which `m`
  divide some `F(n)`, is a question about Pisano periods and ranks of apparition — reason
  prime by prime and combine with `lcm`.
- **Self-similarity is the lever.** Whether it is Zeckendorf blocks, Fibonacci words, or
  fibbinary strings, the object at level `i` is built from the objects at levels `i−1` and `i−2`.
  Write the quantity you want as a recurrence over those levels, then descend greedily from the
  limit.
- **Recognise `√5`, `φ`, and "no two adjacent".** A Pell equation with `D = 5`, a generating
  function with denominator `1 − x − x²`, or a constraint forbidding neighbours are all Fibonacci
  numbers in disguise.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0301](/solutions/0301/) — Nim
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0399](/solutions/0399/) — Squarefree Fibonacci Numbers
- ○ [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0402](/solutions/0402/) — Integer-valued Polynomials
- ○ [0406](/solutions/0406/) — Guessing Game
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0481](/solutions/0481/) — Chef Showdown
- ○ [0543](/solutions/0543/) — Prime-Sum Numbers
- ○ [0554](/solutions/0554/) — Centaurs on a Chess Board
- ○ [0618](/solutions/0618/) — Numbers with a Given Prime Factor Sum
- ○ [0651](/solutions/0651/) — Patterned Cylinders
- ○ [0662](/solutions/0662/) — Fibonacci Paths
- ○ [0669](/solutions/0669/) — The King's Banquet
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ○ [0707](/solutions/0707/) — Lights Out
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ○ [0841](/solutions/0841/) — Regular Star Polygons
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0921](/solutions/0921/) — Golden Recurrence
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0958](/solutions/0958/) — Euclid's Labour
- ○ [0989](/solutions/0989/) — Fibonacci Sum
- ○ [1006](/solutions/1006/) — Fibonacci Subwords
- ○ [1007](/solutions/1007/) — Alternating Difference

<!-- /problems -->
