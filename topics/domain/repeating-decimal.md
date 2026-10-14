<!-- tags: [repeating-decimal] -->
<!-- status: final -->
# Repeating decimal

Every fraction has a decimal expansion that either stops or settles into a loop. That is the
whole of the [repeating decimal](https://en.wikipedia.org/wiki/Repeating_decimal) story at school
level. Project Euler keeps returning to it because the loop is a number-theoretic object in
disguise. The length of the repeating block of `1/d` is the
[multiplicative order](multiplicative-order.md) of 10 modulo `d`, and once I see it that way,
"find the longest cycle" (26), "sum every cycle length to 10⁸" (417), "read the ten-millionth digit"
(820), "terminating or not?" (183) and "which cyclic number starts like this?" (358) all become
questions about powers of 10 in modular arithmetic. None of them is about digits.

## Long division is exponentiation mod d

Divide 1 by `d` by hand. At every step I hold a remainder `r`, write down the digit `⌊10r/d⌋` and
carry `10r mod d` forward. Starting from `r₀ = 1`, the remainder after `k` steps is

```
r_k = 10^k mod d,        digit_k = ⌊10 · r_{k−1} / d⌋
```

So the digits are a by-product of the sequence `10^k mod d`, and that sequence is a walk in a
[functional graph](functional-graph.md) on the residues mod `d`: finite, deterministic, and
therefore a tail followed by a cycle. The shape of that ρ is the shape of the decimal:

- Write `d = 2^a · 5^b · m` with `gcd(m, 10) = 1`.
- If `m = 1`, the walk reaches remainder 0 and stops. The decimal **terminates** after `max(a, b)`
  digits. This is the test 183 needs: a reduced fraction terminates exactly when its denominator
  has no prime factor besides 2 and 5. The 183 notes show you never build the huge value; you
  only factor its small denominator.
- Otherwise the decimal has a **pre-period** of `max(a, b)` digits (the factors of the base being
  "used up"), then a **period** of length `ord_m(10)`, the smallest `k ≥ 1` with
  `10^k ≡ 1 (mod m)`. That is `1/6 = 0.1(6)`: one pre-period digit for the 2, period
  `ord_3(10) = 1`.

The factors of 2 and 5 only change the tail. The period depends on `m` alone. Problem 417's
`L(n)` therefore satisfies `L(2^a 5^b m) = L(m)`, which I'll come back to.

## What the order can be

Because `10` is a unit mod `m`, its powers form a cyclic subgroup of the unit group, and
[Lagrange's theorem](https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory)) bounds the
period:

- `ord_m(10)` divides [`φ(m)`](eulers-totient-function.md), and more sharply divides the
  [Carmichael function](../technique/carmichael-function.md) `λ(m)`.
- For a prime `p ∤ 10`, [Fermat's little theorem](fermats-little-theorem.md) gives
  `ord_p(10) | p − 1`, so the period of `1/p` is at most `p − 1`.
- For a composite, the order is the `lcm` of the orders of its prime-power parts
  (by the [Chinese remainder theorem](../technique/chinese-remainder-theorem.md)), so it is always
  well short of `m − 1`.

The maximum `p − 1` is reached exactly when 10 is a [primitive root](primitive-root.md) mod `p`.
Those are the **[full reptend primes](https://en.wikipedia.org/wiki/Full_reptend_prime)**:
7, 17, 19, 23, 29, 47, 59, 61, 97, … ([OEIS A001913](https://oeis.org/A001913)).
[Artin's conjecture](https://en.wikipedia.org/wiki/Artin%27s_conjecture_on_primitive_roots)
predicts they make up about 37.4% of primes, so they are common, and one is never far below any
bound.

That settles Problem 26 by reasoning before any computation. A composite can't win, and a prime
`p` scores at most `p − 1`. So scan the primes downward from the limit and stop at the first full
reptend prime, because every smaller `d` has period at most `d − 1 < p − 1`. `p0026_s0.py` gets the same
result more bluntly. It simulates the remainder walk for the top tenth of the range:

```python
r = 1
for k in range(1, modulus):
    r = r * a % modulus
    if r == 1:
        return k
```

## Computing the order without walking it

Simulating costs `O(ord)` steps, which is fine for 26 (`d < 1000`). It is hopeless for 417, which
needs the order of 10 for every `n ≤ 10⁸`. The standard fast method starts from a known multiple
of the order and strips factors:

```python
k = p - 1                                  # or λ(m) for a composite modulus
for q in prime_factors(k):
    while k % q == 0 and pow(10, k // q, p) == 1:
        k //= q                            # 10 still returns to 1 at k/q, so the order divides it
```

Each test is one [modular exponentiation](../technique/modular-exponentiation.md), so a prime
costs `O(ω(p−1) · log² p)`, given the factorisation of `p − 1`. A
[smallest-prime-factor sieve](../technique/linear-sieve.md) supplies that factorisation for every
`p` up to the limit at once. Composites are then assembled rather than recomputed:

- **Prime powers lift.** Usually `ord_{p^k}(10) = ord_p(10) · p^{k−1}`. The exceptions are the
  primes where `10^ord_p(10) ≡ 1` holds mod `p²` as well as mod `p`: the base-10
  [Wieferich primes](https://en.wikipedia.org/wiki/Wieferich_prime#Generalizations). The ones
  whose squares fall in 417's range are 3 (since `10 ≡ 1 (mod 9)`, `ord_9 = ord_3 = 1`) and 487
  (`ord_{487²} = ord_{487} = 486`). A lifting rule that assumes the generic case is silently wrong
  at exactly those two primes, so I'd compute `ord_{p²}` directly instead of trusting the formula.
- **Coprime parts combine by lcm.** `ord_{ab}(10) = lcm(ord_a(10), ord_b(10))` for coprime `a, b`.
  The [repunits and multiplicative order](../number-theory/repunits-and-multiplicative-order.md)
  page covers the same `lcm` structure for `R(k) ≡ 0 (mod n)`, which is this problem read the other
  way.
- **Factors of 2 and 5 are free.** `L(n) = L(m)`, so the work is over `n` coprime to 10 and the
  rest is multiplicity.

## Jumping to a digit

The remainder recurrence also says where any digit comes from, without the ones before it. The
`n`-th digit of `1/k` is

```
d_n(1/k) = ⌊10 · (10^(n−1) mod k) / k⌋
```

which is one `pow(10, n − 1, k)` plus a floor. That is the entirety of Problem 820's idea. It
asks for a deep digit of every `1/k` up to `10⁷`, and the identity replaces `O(n)` long division
per denominator with `O(log n)`. Periodicity offers a second route (reduce `n` mod the period
first), but finding the period costs more than the exponentiation it would save.

## Cyclic numbers

Take a full reptend prime `p` and let `C` be the repeating block of `1/p`, leading zeros kept:

```
C = (10^(p−1) − 1) / p          1/7 → 142857,   1/17 → 0588235294117647
```

Since 10 generates all units mod `p`, every `j ∈ {1, …, p−1}` is `10^s mod p` for some shift `s`.
So `j/p` is `1/p` with the decimal point moved `s` places, and its repeating block (which is
`j·C`) is `C` rotated by `s` digits. That is the
[cyclic number](https://en.wikipedia.org/wiki/Cyclic_number) property: multiplying by
`1, …, p−1` permutes `C` cyclically. Conversely every base-10 cyclic number arises this way, so
cyclic numbers and full reptend primes are the same list.

Problem 358 gives a cyclic number's first eleven and last five digits and asks for its digit
sum. The identity `C · p = 10^(p−1) − 1` splits it into two independent constraints on `p`:

- The **leading digits** of `C` are the leading digits of `1/p`, so they pin `p` to a narrow
  interval.
- The **trailing digits** satisfy `C · p ≡ −1 (mod 10⁵)`, which fixes `p` modulo `10⁵` via a
  [modular inverse](modular-multiplicative-inverse.md).

The candidates surviving both are few, and the full reptend test is the order computation above.
The digit sum doesn't need `C` written out either.
[Midy's theorem](https://en.wikipedia.org/wiki/Midy%27s_theorem) says that when the period is
even, the two halves add to `99…9` (`142 + 857 = 999`), so the digit sum of a cyclic number is a
function of its length alone.

## Pitfalls

- **gcd(d, 10) ≠ 1 hangs the simulation.** The remainder walk then never returns to 1; it either
  hits 0 or enters a cycle that misses 1. Strip the 2s and 5s first, or guard with `gcd`, as
  `p0026_s0.py` does.
- **The cycle does not always start at the first digit.** The pre-period is `max(a, b)` digits.
  Counting distinct remainders until a repeat measures the pre-period plus the period.
- **Lifting to prime powers is not uniform.** Check 3 and 487 explicitly (see above).
- **Leading zeros are digits.** `1/17`'s cyclic number is `0588…`, and 358 states that the zeros
  count.
- **Bounds by `p − 1` are tight only for primes.** For composites, a `λ(m)`-based bound is far
  smaller, which is why 26 and the search in 358 can ignore composites outright.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ○ [0358](/solutions/0358/) — Cyclic Numbers
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals

<!-- /problems -->
