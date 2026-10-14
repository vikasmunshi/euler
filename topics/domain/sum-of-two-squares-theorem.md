<!-- tags: [sum-of-two-squares-theorem] -->
<!-- status: final 2026-10-14T07:22Z -->
# Sum of two squares theorem

Which integers are a sum of two squares, `n = a² + b²`, and in how many ways? Fermat stated the
answer and Euler proved it in 1747 — Problem 229 says so in its statement. The [sum of two squares
theorem](https://en.wikipedia.org/wiki/Sum_of_two_squares_theorem) answers both questions from the
prime factorisation alone. It keeps coming back because `a² + b²` turns up whenever a problem
involves distance on the integer grid, Pythagorean geometry, or `n² + 1`. Points on a circle, a
hypotenuse, a Gaussian integer's norm, two square steps that add up to a door number: each one,
looked at closely, is asking about representations as two squares. Once you see that, a search
becomes a factorisation.

## The idea

### Which numbers

Write `n = 2^e · ∏ p^α · ∏ q^β`, where the `p` are primes `≡ 1 (mod 4)` and the `q` are primes
`≡ 3 (mod 4)`. Then

> `n` is a sum of two squares **if and only if every `q ≡ 3 (mod 4)` divides it to an even power.**

The power of 2 doesn't matter (`2 = 1² + 1²`). Every prime `p ≡ 1 (mod 4)` is a sum of two squares
in essentially one way ([Fermat's theorem on sums of two
squares](https://en.wikipedia.org/wiki/Fermat%27s_theorem_on_sums_of_two_squares)), and a prime
`q ≡ 3 (mod 4)` never is: squares are 0 or 1 mod 4, so `a² + b²` can't be 3 mod 4. Products
behave well because of the
[Brahmagupta–Fibonacci identity](https://en.wikipedia.org/wiki/Brahmagupta%E2%80%93Fibonacci_identity):

$$ (a^2 + b^2)(c^2 + d^2) = (ac - bd)^2 + (ad + bc)^2 = (ac + bd)^2 + (ad - bc)^2 $$

So the set of sums of two squares is closed under multiplication, and each new factor can
**multiply the number of representations**, since the identity gives two answers.

### How many ways

The identity is easiest to understand through the
[Gaussian integers](https://en.wikipedia.org/wiki/Gaussian_integer) `ℤ[i]`. There,
`a² + b² = (a + bi)(a − bi)` is the *norm* of `a + bi`. A prime `p ≡ 1 (mod 4)` splits into
`π · π̄`, a prime `q ≡ 3 (mod 4)` stays prime, and `2` ramifies. Representing `n` means choosing,
for each split prime, how many of its `α` copies go to `π` and how many to `π̄`. That gives
`α + 1` choices per prime, and then one of four units. This is
[Jacobi's two-square theorem](https://en.wikipedia.org/wiki/Jacobi%27s_two-square_theorem) in
multiplicative form: for the number of *ordered, signed* pairs `(a, b)`,

$$ r_2(n) = 4 \prod_{p \equiv 1\,(4)} (\alpha_p + 1) \quad\text{if every } \beta_q \text{ is even, else } 0 $$

or, in divisor form, `r₂(n) = 4 (d₁(n) − d₃(n))`: four times the number of divisors `≡ 1 (mod 4)`
minus those `≡ 3 (mod 4)`. Only the primes `≡ 1 (mod 4)` affect the count. The 2s and the
even-power `q`s just scale every representation without adding new ones. That fact does most of
the work in these problems:

```python
def r2(factors: dict[int, int]) -> int:
    """Ordered signed representations of n = ∏ p^e as a² + b², from its factorisation."""
    count = 4
    for p, e in factors.items():
        if p % 4 == 3 and e % 2:
            return 0
        if p % 4 == 1:
            count *= e + 1
    return count
```

### Finding the squares, not just counting them

Sometimes you need the actual `a, b`. For a prime `p ≡ 1 (mod 4)`, find a square root of −1 mod
`p` (raise any quadratic non-residue to the `(p − 1)/4`), then run the Euclidean algorithm on `p`
and that root, stopping at the first remainder below `√p`. That remainder and the next one are
`a` and `b` ([Hermite–Serret](https://en.wikipedia.org/wiki/Fermat%27s_theorem_on_sums_of_two_squares#Algorithm),
a special case of [Cornacchia's algorithm](https://en.wikipedia.org/wiki/Cornacchia%27s_algorithm)).
To get the representations of a composite, multiply the Gaussian primes together with the identity
above. Choosing `π` or `π̄` for each factor walks through every representation exactly once.

## Where it hides

The theorem is rarely named in a problem statement. Usually you recognise it after a substitution:

- **Lattice points on a circle.** A circle centred at a lattice point with radius² `= N` passes
  through exactly `r₂(N)` lattice points. Problem 233 shifts its square's circumcircle so that
  counting points becomes `r₂(2N²)`. Every exponent is then doubled, so the condition on the
  `q`s holds automatically and the count is `4 ∏ (2α + 1)`. "Exactly 420 points" turns into a
  [multiplicative partition](https://en.wikipedia.org/wiki/Multiplicative_partition) of 105 and a
  structured enumeration of prime-exponent patterns. Problem 983 uses the same fact (the vectors
  of norm `N` from a centre are its harmony-point candidates) as the base of a more geometric
  construction, and Problem 723 builds cyclic quadrilaterals from those same lattice points.
- **"In two different ways."** Problem 142 sets `x ± y` and `x ± z` to be squares. Then
  `a² + b² = c² + d² = 2x`, so `2x` needs two same-parity representations. Four of the six
  conditions become one question about sums of two squares, so you enumerate representations and
  group them by value instead of searching triples.
- **Gaussian divisors.** Problem 153 sums the real parts of the Gaussian divisors of every
  `n ≤ 10⁸`. `a + bi` divides `n` exactly when `(a² + b²)/gcd(a, b)` does. That turns the problem
  into a sum over primitive lattice pairs, weighted by an ordinary divisor sum.
- **`n² + 1` and its relatives.** Every divisor of `p² + 1` is built only from 2 and primes
  `≡ 1 (mod 4)`, since −1 must be a square modulo each prime factor. Problem 221's Alexandrian
  integers reduce to factorising `p² + 1 = d₁ d₂`. Problem 846 asks for adjacent bead products of
  the form `x² + 1`, which limits which beads can be neighbours. Problem 659 looks at the primes
  that divide consecutive terms of `n² + k²`, again a question about which primes split.
- **Generating the representations themselves.** Problem 273 restricts `N` to squarefree products
  of primes `≡ 1 (mod 4)` below 150 and sums one coordinate over all representations. That is the
  Gaussian-integer walk above, one `π`/`π̄` choice per prime, with `2^(k−1)` unordered
  representations for `k` primes.
- **The theorem's neighbours.** Problem 229 asks the same question for `a² + d·b²` with
  `d ∈ {2, 3, 7}`. Those forms also have class number one, so similar congruence rules apply. Its
  notes enumerate the lattice points in an ellipse directly anyway, because the requirement that
  both `a` and `b` be positive breaks the clean characterisation. Problem 596 moves up to four
  squares, where [Jacobi's four-square theorem](https://en.wikipedia.org/wiki/Jacobi%27s_four-square_theorem)
  plays the role `r₂` plays here. Problem 611 asks for the parity of the number of ways to write
  a door number as a sum of two *distinct* positive squares.

## How to reason about it

- **Look for `a² + b²` after rearranging.** A circle through lattice points, a hypotenuse, a
  Gaussian norm, `x + y` and `x − y` both squares: all of these turn the condition into a
  representation question, and that question has a closed form.
- **Count from the factorisation, not by enumeration.** `r₂(n)` costs one factorisation. A
  condition like "exactly `k` representations" constrains only the exponents of primes `≡ 1 (mod 4)`,
  so you enumerate exponent patterns and let 2 and the `q`s float freely as a cofactor.
- **Watch which count the problem means.** `r₂` counts ordered pairs with signs, including zeros.
  Problems usually want `0 ≤ a ≤ b`, or positive `a, b`, or *distinct* squares, so divide by the
  symmetry and handle the axis cases (`n` a square, or twice a square) separately. Most
  off-by-small-constant bugs in this family come from here.
- **Use Gaussian integers when you need the actual pairs.** Factor each split prime once with
  Hermite–Serret, then combine. Each `π`/`π̄` choice is one representation, with no duplicates and
  none missed.
- **Know where the clean theory stops.** "Positive integers", "distinct squares" and forms with
  class number above one all add edge cases that the congruence rule doesn't cover. When a
  condition breaks the norm structure, enumerating lattice points inside a circle or ellipse is
  `O(N)` and often the safer choice.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ○ [0273](/solutions/0273/) — Sum of Squares
- ○ [0596](/solutions/0596/) — Number of Lattice Points in a Hyperball
- ○ [0611](/solutions/0611/) — Hallway of Square Steps
- ○ [0659](/solutions/0659/) — Largest Prime
- ○ [0723](/solutions/0723/) — Pythagorean Quadrilaterals
- ○ [0846](/solutions/0846/) — Magic Bracelets
- ● [0983](/solutions/0983/) — Consonant Circle Crossing

<!-- /problems -->
