<!-- tags: [triangular-number] -->
<!-- status: final 2026-10-14T11:43Z -->
# Triangular number

A [triangular number](https://en.wikipedia.org/wiki/Triangular_number) counts the dots in a
triangle with *n* on a side: T(n) = 1 + 2 + … + n. It keeps coming back because it is the shape of
the most common sum in programming — "add up the first *n* integers" — and also of the most common
count — "choose 2 things out of *n* + 1". Whenever a loop adds a growing step, or a problem pairs
things up, a triangular number is hiding in it, and recognising it turns a loop into a formula.

## The closed form

Write the sum forwards and backwards and add the two rows column by column: every column is
*n* + 1, and there are *n* of them, so twice the sum is n(n+1):

    T(n) = n(n+1)/2 = C(n+1, 2)

The binomial form is the one worth remembering, because it explains where triangular numbers turn
up without any summing at all. In [Problem 85](/solutions/0085/) a rectangle inside an H × W grid
is fixed by choosing two of the H + 1 horizontal lines and two of the W + 1 vertical lines, so the
count is T(H)·T(W) and the search becomes "which pair of triangular numbers multiplies to nearest
two million". The sum form does the work elsewhere: [Problem 1](/solutions/0001/) sums the
multiples of *k* below a limit as k·T(m), and [Problem 6](/solutions/0006/)'s "square of the sum"
is just T(n)². In each case an O(n) loop collapses to O(1) arithmetic.

Two structural facts about the formula do almost all the heavy lifting:

- **The factors are coprime.** *n* and *n* + 1 share no divisor, and exactly one of them is even,
  so T(n) is the product of two coprime numbers — one of them carrying the `/2`.
- **It is a quadratic in *n*.** So it can be inverted: given a value, the quadratic formula tells
  you which *n* (if any) produced it.

## Counting divisors: split, don't factor

[Problem 12](/solutions/0012/) asks for the first triangular number with more than 500 divisors.
The divisor-count function d(m) = ∏(aᵢ + 1) over the prime factorisation needs a factorisation,
and factoring T(n) directly by trial division costs O(√T(n)) ≈ O(n). But
[d is multiplicative](https://en.wikipedia.org/wiki/Divisor_function): d(ab) = d(a)·d(b) whenever
gcd(a, b) = 1 — and the coprime split above hands us exactly such a pair. The faster of the two
public solutions does no more than this:

```python
if i % 2 == 0:
    divisor_count = num_factors(i // 2) * num_factors(i + 1)
else:
    divisor_count = num_factors(i) * num_factors((i + 1) // 2)
```

Each factorisation now runs on a number about √(2·T(n)), not T(n), so trial division costs
O(√n) per step instead of O(n). It also composes: d(n + 1) computed for this step is next step's
d(n), so a careful implementation factors each integer only once. The general lesson — *when a
number arrives as a product of coprime pieces, never multiply them out before you analyse them* —
reaches well past this tag; the private [Problem 581](/solutions/0581/) asks for *smooth*
triangular numbers, and the same split reduces it to finding consecutive integers that are both
smooth.

## Membership: invert the quadratic

"Is *x* triangular?" needs neither a table nor a bound. Set n(n+1)/2 = x and solve
n² + n − 2x = 0:

    n = (−1 + √(8x + 1)) / 2

That *n* is a whole number exactly when **8x + 1 is a perfect square** (the square is then
automatically odd, so the division by 2 is exact). [Problem 42](/solutions/0042/) uses precisely
this to classify word values in O(1) each, with no precomputed list and no guess at how large a
word value might get.

[Problem 45](/solutions/0045/) shows the test generalising. Every polygonal family is a quadratic,
so each has its own inverse: x is pentagonal when 24x + 1 is a square whose root is ≡ 5 (mod 6).
And the hexagonal case needs no test at all, because H(n) = n(2n − 1) = T(2n − 1) — the hexagonal
numbers *are* the odd-indexed triangular numbers. A three-way intersection becomes a scan over one
sequence with one membership test. The congruence on the root is the part people forget: a
perfect-square discriminant only says the quadratic has a rational root; the residue condition is
what makes that root a positive integer of the right parity.

## Pitfalls

- **Floating-point square roots.** `(8 * x + 1) ** 0.5` is exact for the small values in Problems
  42 and 45, but a double carries only 53 bits; past about 10¹⁵ a non-square can round to an
  integer root and pass. For large inputs use [`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt)
  and check `r * r == 8 * x + 1`.
- **Overflow in C.** Compute n(n+1)/2 as `(n / 2) * (n + 1)` or `n * ((n + 1) / 2)` depending on
  parity — the same split as in Problem 12 — so the intermediate product does not exceed the type
  before the halving.
- **Off-by-one in the index.** T(n) = C(n+1, 2), not C(n, 2). In counting problems, decide first
  whether you are choosing among *n* items or *n* + 1 boundaries; Problem 85 hinges on that.
- **Know the deeper results exist.** Gauss's
  [Eureka theorem](https://en.wikipedia.org/wiki/Fermat_polygonal_number_theorem) — every natural
  number is a sum of three triangular numbers — sits behind the private
  [Problem 621](/solutions/0621/); and "triangular *and* square" style questions
  ([OEIS A001110](https://oeis.org/A001110)) lead to Pell equations rather than to brute search.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0321](/solutions/0321/) — Swapping Counters
- ○ [0378](/solutions/0378/) — Triangle Triples
- ○ [0459](/solutions/0459/) — Flipping Game
- ○ [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ○ [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ○ [0647](/solutions/0647/) — Linear Transformations of Polygonal Numbers
- ○ [0726](/solutions/0726/) — Falling Bottles
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0955](/solutions/0955/) — Finding Triangles
- ○ [0985](/solutions/0985/) — Telescoping Triangles

<!-- /problems -->
