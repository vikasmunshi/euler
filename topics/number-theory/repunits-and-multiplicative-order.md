<!-- tags: [repunit, multiplicative-order, carmichael-function, primitive-root] -->
<!-- status: final -->
# Repunits and multiplicative order

A [repunit](https://en.wikipedia.org/wiki/Repunit) is a number written with only ones: `R(k) = 11…1`
(`k` ones). The "which repunits does `n` divide?" questions, the recurring-decimal questions, the
card-shuffle questions and the "what is `aⁿ` mod `m` for an absurd `n`" questions in this list all
ask the same thing: **how many steps until a power comes back to 1?** That count is the
[multiplicative order](https://en.wikipedia.org/wiki/Multiplicative_order). Once you see the order
in a problem, the very large numbers go away. A billion-digit repunit becomes one modular
exponentiation, and an unbounded search gets a hard upper limit.

## The idea

### From repunits to the order of 10

Two forms of the repunit do all the work:

$$ R(k) = 10\,R(k-1) + 1, \qquad R(k) = \frac{10^k - 1}{9}. $$

The recurrence is what you compute with: carry `r = R(k) mod n` and update `r = (10r + 1) mod n`.
The number never gets bigger than `n`. The closed form is what you reason with. Take `n` coprime to
10 (a repunit ends in 1, so 2 and 5 never divide one). Then

$$ n \mid R(k) \iff 9n \mid 10^k - 1 \iff 10^k \equiv 1 \pmod{9n}. $$

So Problem 129's `A(n)`, the length of the shortest repunit that `n` divides, is exactly
`ord₉ₙ(10)`, the multiplicative order of 10 modulo `9n`. When `3 ∤ n` the 9 is a unit and drops out,
leaving `A(n) = ordₙ(10)`. When `3 | n` it does not drop out, and that difference matters. For
example `ord₃(10) = 1`, but `A(3) = 3`: 1 and 11 are not multiples of 3, and 111 is.

The same order measures how long a decimal takes to repeat. For `d` coprime to 10, `1/d` repeats
with period `ord_d(10)`. Long division by `d` multiplies the remainder by 10 at every digit, and the
digits start over when the remainder gets back to 1. Problem 26 (the longest recurring cycle of
`1/d`) is therefore an order problem too. Its solution is public, and its kernel is the plain
definition of the order:

```python
def multiplicative_order(a: int, modulus: int) -> int | None:
    """Smallest k with a**k ≡ 1 (mod modulus), or None if a is not coprime to modulus."""
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None
```

For example, `1/7 = 0.(142857)` has period 6. That is the same fact as `7 | 111111 = 7 · 15873`,
since `7 · 9 = 63` divides `999999`.

### Why A(n) is at most n

The [pigeonhole principle](https://en.wikipedia.org/wiki/Pigeonhole_principle) shows that
`A(n)` exists and is at most `n`. Look at `R(1), …, R(n)` modulo `n`. If none of them is 0, then
`n` values fall into the `n − 1` nonzero residues, so two of them are equal: `R(j) ≡ R(i)` with
`i < j`. Their difference is

$$ R(j) - R(i) = 10^{i}\, R(j - i), $$

and `10ⁱ` is invertible mod `n`, so `n | R(j − i)` with `j − i < n`. Either way some `k ≤ n` works.
The group-theory version of the same argument is that `ord₉ₙ(10)` divides
`φ(9n)`. The bound is also tight: `A(3ᵏ) = 3ᵏ`, so 3, 9, 27, 81, … each reach it exactly.

The bound decides where the search starts. Problem 129 wants the least `n` with `A(n)` above a
threshold `T`. Because `A(n) ≤ n`, no `n ≤ T` can qualify, so the scan can safely begin at `T + 1`.
In practice the answer turns up within a few dozen steps, which turns an apparently `O(T²)` search
into an `O(T)` one.

### Fermat, and composites that imitate primes

[Lagrange's theorem](https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory)) says an
element's order divides the size of its group. For a prime `p > 5` that group has `p − 1` elements,
so `A(p) = ord_p(10)` divides `p − 1`. This is
[Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) in repunit form:
**every prime `p > 5` satisfies `A(p) | p − 1`.**

Problem 130 asks for the composites that satisfy it too. The first one is `91 = 7 · 13`: both
`ord₇(10)` and `ord₁₃(10)` are 6, so `A(91) = lcm(6, 6) = 6`, and 6 divides 90. These numbers are
close relatives of the [Fermat pseudoprimes](https://en.wikipedia.org/wiki/Fermat_pseudoprime) to
base 10, and finding them is a pure order computation. One filter comes from the 3-adjustment above.
If `3 | n`, then 3 divides `A(n)` but not `n − 1`, so the divisibility fails. That means candidates
only need `gcd(n, 30) = 1`, not just `gcd(n, 10) = 1`.

The opposite extreme is a prime whose order is as large as possible, `p − 1`. In that case 10 is a
[primitive root](https://en.wikipedia.org/wiki/Primitive_root_modulo_n) mod `p`, and `1/p` has the
longest possible period (7 is one: `1/7` repeats every 6 digits). Problem 437 asks the same
"is the order maximal?" question in a different setting, for roots of `x² = x + 1` mod `p`.

## Computing the order: three speeds

Problem size decides how you get at the order. The covered problems use three methods.

**1. Walk until you hit 1.** Repeat `r = r·a mod n` and count the steps. This costs `O(ord)`, which
can be close to `n`. It is the right choice when the walk is the whole question, as in Problem 26 or
Problem 129's `A(n)` kernel. You have to pay those steps anyway, and the loop needs no
factorisation.

**2. Start from a known multiple and divide down.** The order divides any `e` with `aᵉ ≡ 1`. The
best general choice of `e` is the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) `λ(n)`, the exponent of
the group of units mod `n`. It is the `lcm` of `λ(pᵉ)` over the prime powers in `n`, with
`λ(pᵉ) = pᵉ⁻¹(p − 1)` for odd `p`. Then remove each prime factor of `e` for as long as the power
still comes out to 1:

```python
order = lam
for q in prime_factors(lam):
    while order % q == 0 and pow(a, order // q, n) == 1:
        order //= q
```

This costs a factorisation plus `O(log² n)` multiplications. Problem 130 uses it with a
smallest-prime-factor sieve, because it needs the order of every candidate in a range. Problems 533
and 952 study `λ` and orders in their own right, and Problem 417 sums `ord_n(10)` over a range far
too large to walk.

**3. Don't compute the order at all.** Often the question is only "does the order divide `k`?",
and that is a single test: `pow(10, k, p) == 1`. Problem 132 looks for prime factors of `R(10⁹)`,
which has a billion digits, by checking `10^(10⁹) ≡ 1 (mod p)` for each sieved prime. Problem 133
goes further. It asks which primes divide *no* `R(10ⁿ)`, which looks like infinitely many tests. A
prime `p` divides some `R(10ⁿ)` exactly when `ord_p(10)` has no prime factors other than 2 and 5.
Since the order divides `p − 1`, that holds exactly when it divides `m`, the part of `p − 1` made of
2s and 5s. So the infinite family comes down to one test per prime, `10^m ≡ 1 (mod p)`.

The same reduction works for any power with a huge exponent. Once `a` is a unit mod `m`, the
sequence `aᵏ mod m` repeats with a period dividing `λ(m)`, so exponents can be reduced mod `λ(m)`.
Problem 250 uses this to cut the `250250` terms of `nⁿ mod 250` down to a short periodic pattern.

## How to reason about it

- **Watch for "until it returns" wording.** Repeating decimals, a shuffle that restores the deck
  (Problem 622 is the order of 2 modulo `n − 1`), a state that cycles, or `xᵏ ≡ 1` for some ring
  element (Problem 752 does this in `ℤ[√7]` mod `n`) are all order problems. The group can change;
  `ord`, `λ` and Lagrange still apply.
- **Repunits come in other bases.** `R_b(k) = (bᵏ − 1)/(b − 1)`. Problem 346 asks which numbers are
  repunits in two or more bases, and these bases show up again in Problem 288 through
  [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula):
  `v_p(N!) = (N − s_p(N))/(p − 1)`.
- **Handle 2, 3 and 5 separately.** 2 and 5 never divide a repunit. 3 divides the `9` in
  `(10ᵏ − 1)/9`, so `A(n) = ordₙ(10)` fails as soon as `3 | n`. Write the general case as
  `ord₉ₙ(10)` or special-case 3 explicitly. Most wrong answers in this area come from that one
  factor.
- **Choose a method by cost.** Walking costs `O(n)` per order. Reducing from `λ` costs a
  factorisation, which is cheap with a sieve. A single "does it divide `k`?" exponentiation costs
  `O(log k)`. Prefer the cheapest method that answers the question actually asked.
- **Watch for overflow in C.** `r · a` with both operands near `10⁹` needs 64-bit arithmetic, and
  squaring near `2⁶³` inside `powmod` needs `__int128`. Python's three-argument `pow` handles this
  for you.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0250](/solutions/0250/) — $250250$
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0346](/solutions/0346/) — Strong Repunits
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ○ [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0847](/solutions/0847/) — Jack's Bean
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0952](/solutions/0952/) — Order Modulo Factorial

<!-- /problems -->
