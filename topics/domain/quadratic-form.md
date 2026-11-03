<!-- tags: [quadratic-form] -->
<!-- status: final 2026-11-03T22:45Z -->
# Quadratic form

A [quadratic form](https://en.wikipedia.org/wiki/Quadratic_form) is a polynomial in which every
term has degree exactly two: `a² + b² − c²`, `a² − 7b²`, `a₁² + … + a₄² − b₁² − … − b₄²`. Forms keep
coming back because a sum or difference of squares is the commonest shape an integer constraint
takes once the story is stripped away. The problems below talk about triangles, triangular numbers,
powers of `1 + √7` and a congruence, yet each one turns on a question about a single fixed form:
what are its symmetries, which values does it take and how often, and how many zeros does it have
modulo `n`?

Forms in exactly two variables have a theory of their own, covered on the
[binary quadratic form](/topics/domain/binary-quadratic-form) page (still a draft). That theory
compares forms with each other: the discriminant, reduction to a canonical form, and the class group
that decides which of several forms represents a given prime. Problem 804's `x² + xy + 41y²` and
the four forms intersected in Problem 229 belong there, and Problems 586 and 769 carry both tags.
This page is about what works in any number of variables. Two-variable forms appear here too, but
only as a piece of a larger form or as a norm.

## The idea

### A form is a symmetric matrix

Every form can be written `Q(x) = xᵀAx` with `A` symmetric. For `a² + b² − c²` that matrix is
`diag(1, 1, −1)`. A change of variables `x = Py` replaces `A` with `PᵀAP`, and over the integers
`P` must be [unimodular](https://en.wikipedia.org/wiki/Unimodular_matrix) (determinant ±1) so that
it permutes the lattice instead of thinning it. Two forms related this way are equivalent: they
represent the same integers, the same number of times. So a form's useful properties are the ones
this substitution cannot change. Three matter most:

- **Dimension**, the number of variables. Two squares, three squares and four squares behave very
  differently, as the table further down shows.
- **Signature**, the count of positive and negative squares after diagonalising over the reals
  ([Sylvester's law of inertia](https://en.wikipedia.org/wiki/Sylvester%27s_law_of_inertia)). A
  *definite* form has one sign, so `Q = k` is an ellipsoid with finitely many lattice points. An
  *indefinite* form has both, so `Q = k` is a hyperboloid that can hold infinitely many.
- **Discriminant**, `det A`. It decides how the form behaves modulo each prime.

The signature tells you which kind of algorithm to expect. For a definite form you are counting
something finite, and the question is how to avoid enumerating it. For an indefinite form you cannot
enumerate by size at all, so you need the symmetry.

### Symmetry: isometries move solutions around

An *isometry* is an integer matrix `M` with `MᵀAM = A`, so `Q(Mv) = Q(v)` for **every** vector `v`.
These matrices form the form's [orthogonal group](https://en.wikipedia.org/wiki/Orthogonal_group).
The word "every" is what makes them useful. An isometry does not know which level set it is acting
on, so a matrix discovered on one level works on all of them.

That is the whole content of Problems 223 and 224. The
[Berggren matrices](/topics/technique/tree-of-primitive-pythagorean-triples) are usually introduced
as generators of [Pythagorean triples](/topics/domain/pythagorean-triple), the level `Q = 0` of
`a² + b² − c²`. They are isometries of `Q`, though, so the same matrices carry solutions of `Q = 1`
to solutions of `Q = 1`, and solutions of `Q = −1` to solutions of `Q = −1`. The branch that sends
`(3, 4, 5)` to `(21, 20, 29)` also sends `(2, 2, 3)` to `(12, 12, 17)`, and the form's value is 0
for the first pair and −1 for the second. The test for this property is one line, and it is worth
running on any matrix you suspect:

```python
def is_isometry(M, A):            # integer numpy arrays
    return (M.T @ A @ M == A).all()
```

So a level set falls apart into orbits, and only the starting points depend on the level. The
[tree article](/topics/technique/tree-of-primitive-pythagorean-triples) covers how to find those
roots, how to walk from them, and how to remove the duplicates that mirror symmetry creates.

The size of the group tracks the signature. A definite form has a finite group. For a sum of `n`
squares it is just the signed permutations, `2ⁿ·n!` of them, so symmetry only divides a count by a
constant, like the factor of four between signed and positive representations in Problem 621. An
indefinite form usually has an infinite group, and that is what lets a few seeds reach infinitely
many solutions. In two variables the group is essentially the powers of a single unit, so an orbit
is a chain, which is why [Pell's equation](/topics/technique/pells-equation) has a recurrence. In
three variables there are several independent generators, so an orbit is a tree. Problem 224 shows
both at once: restricted to the diagonal `a = b`, the ternary form becomes the binary `2a² − c²`,
and the tree's central spine is exactly a Pell sequence.

### Representation: how often does the form hit `n`?

Write `r_Q(n)` for the number of integer vectors with `Q(x) = n`. For sums of squares the answer
depends sharply on the dimension:

| squares | which `n` are represented | how to count them |
|---|---|---|
| 2 | no prime `≡ 3 (mod 4)` to an odd power ([theorem](/topics/domain/sum-of-two-squares-theorem)) | `r₂/4` is multiplicative, read from the factorisation |
| 3 | all except `4ᵃ(8b + 7)` ([Legendre](https://en.wikipedia.org/wiki/Legendre%27s_three-square_theorem)) | a [class number](https://en.wikipedia.org/wiki/Ideal_class_group), with no product formula |
| 4 | every `n` ([Lagrange](https://en.wikipedia.org/wiki/Lagrange%27s_four-square_theorem)) | `r₄(n) = 8 Σ d` over `d ∣ n`, `4 ∤ d` ([Jacobi](https://en.wikipedia.org/wiki/Jacobi%27s_four-square_theorem)) |

Three is the odd one out, and the reason is structural. Two and four squares each have a product
identity, the [Brahmagupta–Fibonacci](https://en.wikipedia.org/wiki/Brahmagupta%E2%80%93Fibonacci_identity)
and [Euler four-square](https://en.wikipedia.org/wiki/Euler%27s_four-square_identity) identities, and
three squares has none. `3` and `21` are both sums of three squares, but their product `63` is
`8·7 + 7`, which is not.

Problem 621 runs straight into that gap. Multiplying by 8 and adding 3 turns "three
[triangular numbers](/topics/domain/triangular-number) summing to `n`" into "three odd squares
summing to `8n + 3`", because `8T_a + 1 = (2a + 1)²`. That is a ternary representation count, the
row with no factorisation to read. The way through is to **peel off a variable**. Fix `a`, and what
remains is a two-square count of `8n + 3 − (2a + 1)²`, which the factorisation answers. An
`n`-ary count is a sum of `(n−1)`-ary counts, so you can trade one dimension for a loop and land on
a dimension with a formula. The loop runs over about `√(2n)` values of a single quadratic, and those
can be factored together by a [polynomial sieve](/topics/technique/polynomial-sieve) instead of one
at a time. The class-number identity still earns its place, as an independent estimate to check the
computed count against.

### Norm forms: a form with a multiplication law

Some forms are [norms](/topics/technique/field-norm). `x² + y²` is `N(x + iy)` and `a² − 7b²` is
`N(a + b√7)`, and since `N(uv) = N(u)N(v)`, the values of the form are closed under multiplication.
That moves the reasoning from the integers to the primes. The
[quadratic residue](/topics/technique/quadratic-residue) page covers the mechanics. What matters
here is what the norm itself hands you:

- **Which primes can divide a value.** Problem 659 reduces to the largest prime factor of
  `(2k)² + 1`, a value of `x² + y²`. An odd prime dividing it has `−1` as a square, so it is
  `≡ 1 (mod 4)`, and the search space halves before any factoring starts.
- **Which elements are invertible.** In Problem 752 the power of `u = 1 + √7` can only return to 1
  modulo `x` if `u` is a unit there, and `u` is a unit exactly when its norm is. `N(u) = −6`, so
  `gcd(x, 6) = 1` is the whole test, and it explains the statement's `g(3) = 0` with no computation.
- **A map to something simpler.** When `p` is inert, conjugation is the `p`-th power map, so
  `u^(p+1) = N(u)`. That pushes most of the [order](/topics/domain/multiplicative-order) calculation
  down from `𝔽_{p²}` to `𝔽_p`, where a built-in modular `pow` does the work.

### Zeros modulo `n`: a diagonal form counts itself

Modulo an odd prime, every form can be diagonalised, and a non-degenerate one is determined by its
dimension and by whether its discriminant is a square. So the number of zeros is a formula. In an
odd dimension `d` it is exactly `p^(d−1)`. In an even dimension `2m` it is

$$ p^{2m-1} \pm \left(p^m - p^{m-1}\right), $$

with `+` when the form is **hyperbolic**, meaning it splits into pairs like `a² − b² = (a − b)(a + b)`.
The sign is the [isotropy](https://en.wikipedia.org/wiki/Isotropic_quadratic_form) question in
miniature: `x² + y² ≡ 0 (mod p)` has `2p − 1` solutions when `p ≡ 1 (mod 4)`, where the form factors,
and only the trivial one when `p ≡ 3 (mod 4)`, where it does not.

Problem 875 counts the zeros of an eight-variable form modulo every `n`. Its form pairs each `a²`
with a `−b²`, so it is hyperbolic at every odd prime, and `m = 4` gives `p⁷ + p⁴ − p³`. Composite
moduli need a method that handles prime powers and the prime 2 uniformly. The
[roots-of-unity filter](/topics/technique/roots-of-unity-filter) is that method, and here the
diagonal shape pays off: the filter's sum over a form with no cross terms factors into a product of
one-variable [Gauss sums](/topics/technique/quadratic-gauss-sum), whose absolute values are known.
Eight variables cost no more than one, because the count only needs an eighth power. Grouping by
the reduced denominator then gives a [Dirichlet convolution](/topics/domain/dirichlet-convolution)
of [multiplicative functions](/topics/domain/multiplicative-function), and a sieve finishes it.

The prime 2 is the exception throughout. The odd-prime formula does not extend to it: the Gauss sum
vanishes at modulus 2 and has a different size at higher powers of 2, so the 2-adic part needs its
own correction. The statement's `q(4)` is a valuable test case for exactly this reason. It exercises
the only part of the formula that the odd primes cannot check, which is the
[calibration](/topics/takeaway/calibrate-theory-on-known-answers) habit at work.

The local view also gives cheap negative answers. A form that misses a residue modulo some prime
power misses every integer in that class, which is how `8b + 7` falls out of three squares: squares
are `0, 1, 4 (mod 8)`, and no three of them sum to 7. The
[Hasse–Minkowski theorem](https://en.wikipedia.org/wiki/Hasse%E2%80%93Minkowski_theorem) says that
over the rationals these local checks, plus the real one, are the whole story. Over the integers
they are necessary but not always sufficient, so treat them as a filter, not a proof.

## How to reason about it

When a constraint contains squares, stop and name the form before writing a loop.

- **Bring it to a standard shape.** [Complete the square](/topics/domain/completing-the-square),
  clear denominators, and rescale. `8T + 1` is an odd square, and multiplying a quadratic by `4a`
  completes its square. The form that emerges is usually far simpler than the statement suggests.
- **Check the signature.** A definite form gives a finite count to compute. An indefinite one gives
  an infinite set that must be generated by structure, never bounded by the size of its solutions.
- **Look for isometries, and reuse them across levels.** A matrix known for `Q = 0` works for
  `Q = k`. The seeds and the duplicates do not carry over, though, so verify the walk against a
  brute-force count, as Problems 223 and 224 do.
- **Ask whether it is a norm.** If it is, reason one prime at a time: which primes divide a value,
  which elements are units, and what the split, inert and ramified cases each do.
- **Too many variables for a formula?** Peel one off and sum. Aim for a dimension with a known
  count, then look for a way to do all the resulting factorisations at once.
- **Counting modulo `n`?** Diagonalise, filter with roots of unity, and let the Gauss sums turn
  the dimension into an exponent. Then use multiplicativity to reduce to prime powers.
- **Treat 2 separately.** Diagonalisation and the Gauss-sum sizes both change there. Test any formula
  at a power of 2 before trusting it, and look at residues modulo 8 for obstructions.
- **Exactly two variables, and several forms in play?** That is the
  [binary](/topics/domain/binary-quadratic-form) theory, with its discriminants and classes.

The through-line is the [reduce-before-coding](/topics/takeaway/reduce-before-coding) lesson in a
specific form. Whatever the statement's surface, once you have named the form, its dimension and
its signature, you already know which family of algorithms applies and roughly what it will cost.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ○ [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ○ [0586](/solutions/0586/) — Binary Quadratic Form
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0989](/solutions/0989/) — Fibonacci Sum

<!-- /problems -->
