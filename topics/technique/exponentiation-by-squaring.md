<!-- tags: [exponentiation-by-squaring] -->
<!-- status: final -->
# Exponentiation by squaring

[Exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) computes
$b^e$ in about $\log_2 e$ operations instead of $e$ of them, by reading the exponent in binary. That
much is a one-line summary of a nine-line loop, and if the story stopped there this page would be a
footnote to [modular exponentiation](/topics/technique/modular-exponentiation), which covers the
residue case in depth. It does not stop there. The reason the tag lands on the problems below is
that **the operation being squared is a parameter**: the same loop advances a linear recurrence
$10^{18}$ steps, raises a polynomial to a power while discarding everything above degree $m$, or
runs a million independent powers in lockstep across a NumPy array. Learning the loop is ten
minutes; learning to recognise what else it will accept is what pays.

## The idea

Write the exponent in binary: $13 = 1101_2$, so $b^{13} = b^8 \cdot b^4 \cdot b^1$. The powers
$b, b^2, b^4, b^8, \dots$ come from squaring the previous one, and you fold each into a running
result exactly where the corresponding bit is set. Right to left, that is the entire algorithm:

```python
def power(base, exponent, mul, one):
    """base ** exponent, for any associative `mul` with identity `one`."""
    result = one
    while exponent:
        if exponent & 1:
            result = mul(result, base)
        exponent >>= 1
        if exponent:
            base = mul(base, base)
    return result
```

The cost is $\lfloor \log_2 e \rfloor$ squarings plus $\mathrm{popcount}(e) - 1$ multiplications —
between $\log_2 e$ and $2\log_2 e$ operations, never more. Two lines of that skeleton carry the
whole generalisation. `one` is the identity: `1` for numbers, the identity matrix for matrices,
the constant polynomial $1$ for polynomials — and an accumulator initialised to a zero-like value
instead is the classic way to get a silent zero out of a correct-looking loop. `mul` need only be
**associative**; it does not need to be commutative, and nothing here ever divides, so no inverses
are required either. In algebraic terms the requirement is a [monoid](https://en.wikipedia.org/wiki/Monoid),
and that is a much weaker demand than "numbers" — which is why the same nine lines keep showing up
in unrelated solutions.

## What "multiply" can be

| What you square | Identity | What the power means | Seen in |
| --- | --- | --- | --- |
| A residue mod $m$ | `1` | $b^e \bmod m$ | 48, 97, 217, 820, 926 |
| A $d \times d$ matrix | $I$ | $e$ steps of a linear recurrence | 237, 940 |
| A polynomial truncated at degree $m$ | $1$ | an $e$-fold convolution, low terms only | 768 |
| A whole array of residues | `ones` | many independent powers at once | 421, 429, 944 |

**Matrices — a recurrence in logarithmic time.** Problem 237 counts Hamiltonian tours on a
$4 \times n$ board; the counts obey $T(n) = 2T(n-1) + 2T(n-2) - 2T(n-3) + T(n-4)$, and a fourth-order
[linear recurrence with constant coefficients](/topics/technique/linear-recurrence-with-constant-coefficients)
is exactly repeated multiplication by its $4 \times 4$
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix). Iterating it $n = 10^{12}$ times
is hopeless; squaring the matrix 40 times is a few thousand integer multiplications, and the extra
test case at $n = 10^{18}$ costs 20 more. Problem 940 is the same move one dimension up: a
two-dimensional recurrence factors into a row matrix and a column matrix, so the answer is a product
of $2 \times 2$ matrix powers whose exponents are Fibonacci numbers — large, but only their bit
lengths are ever paid for. See [matrix exponentiation](/topics/technique/matrix-exponentiation) and
the [transfer-matrix method](/topics/domain/transfer-matrix-method); note that matrix multiplication
is not commutative, which the loop never assumed — keep `result` on the same side of every product
and it stays correct.

**Truncated polynomials.** Problem 768 raises a generating polynomial to a power, keeping only the
terms up to degree $m$ because nothing above that can influence the answer. Truncated multiplication
is associative and has the identity $1$, so the loop applies unchanged — but here a single "multiply"
is an $O(m^2)$ convolution rather than one machine instruction. That inverts the usual economics:
saving one operation is now worth a line of code, which is why its loop guards the final squaring
(`if exponent:` before squaring the base) instead of computing a square it will never use. Cheap
when a multiply is a `mul` instruction, genuinely worth it when a multiply is a convolution.

**Arrays.** Python's `pow` is scalar and [NumPy](/topics/technique/numpy) has no three-argument
`pow`, so a sweep that needs a power for each of a million elements is a million interpreter round
trips. Problems 421, 429 and 944 write the bit loop out by hand for exactly this reason: with the
loop over *bits* on the outside, every step — the squaring, the conditional fold, the shift — is one
whole-array operation, and the number of passes is the bit length of the largest exponent (say 40 or
60), not the length of the array. Problem 421 goes furthest, carrying a *vector* modulus, one prime
per lane, so thousands of different moduli advance together. The payoff shows up in the benchmarks:
the [vectorised](/topics/technique/vectorized) Python of 421, 429 and 944 runs at 2.2 s, 0.93 s and
9.3 s against C siblings at 0.99 s, 0.70 s and 7.4 s — a factor of 1.3–2.2 — while the scalar
matrix-power solutions of 237 and 940 sit 40–45× behind their C versions. Same algorithm; the
difference is whether the interpreter is entered once per bit or once per element.

## Twenty-three steps instead of eight million

Problem 97 asks for the last ten digits of $28433 \times 2^{7830457} + 1$, and its two public
solutions are the clearest measurement of the idea in the repository. The Python doubles under the
modulus in a plain loop, $7{,}830{,}457$ iterations of it; the C squares:

```c
static long long mod_pow(long long base, long long exp, long long mod) {
    long long result = 1LL;
    base %= mod;
    while (exp > 0) {
        if (exp & 1LL) result = (long long)((__int128)result * base % mod);
        base = (long long)((__int128)base * base % mod);
        exp >>= 1;
    }
    return result;
}
```

Twenty-three squarings instead of eight million doublings, and the recorded averages are
$0.79\ \mu\text{s}$ against $0.56$ s — a factor of about 700,000, where the language alone accounts
for perhaps 50 ([a better algorithm beats a faster language](/topics/takeaway/algorithm-beats-language)).
Both answer the question, so the linear loop is not *wrong*; it is merely tied to the size of the
exponent, and one test case at $10^{18}$ would end it. The `__int128` casts are the other half of
the story and belong to [modular exponentiation](/topics/technique/modular-exponentiation): two
residues near $10^{10}$ multiply to $10^{20}$, which a `long long` cannot hold.

A quieter use of the same loop is worth noticing. The
[Miller–Rabin test](/topics/technique/miller-rabin-primality-test) in problems 200 and 387 computes
$a^d \bmod n$ and then keeps squaring — but it *watches* the intermediate squares, looking for a
nontrivial square root of $1$. The squarings that exponentiation by squaring normally throws away
are the evidence; the fast power is the primitive that makes a probabilistic primality test, and
with it much of public-key cryptography, affordable at all.

## When not to reach for it

- **You need every power, not one.** $b^0, b^1, \dots, b^n$ is a running product: $n$ multiplications
  for the whole table, against $n \log n$ for $n$ independent fast powers. Problems 171 and 788 both
  build a place-value table this way (`pow10[k] = pow10[k-1] * 10 % MOD`) and never call `pow` at all.
  Problem 217 takes the other branch, one `pow(10, k-1-i, mod)` per place — correct, and lost in the
  noise beside its digit DP, but the table is the reflex worth having.
- **Python already does it.** `pow(b, e, m)` and even `b ** e` are binary exponentiation implemented
  in C over [arbitrary-precision integers](/topics/technique/arbitrary-precision-arithmetic), and
  CPython switches to a windowed variant (precomputing small powers, consuming several exponent bits
  at a time) once the exponent is large. A hand-rolled scalar loop in Python is strictly slower.
  Write the loop only when the operation is not integer multiplication, or the operands are not
  scalars.
- **The exponent is small and fixed.** `x*x*x` beats any loop, and for a fixed exponent the minimal
  number of multiplications comes from an [addition chain](https://en.wikipedia.org/wiki/Addition_chain),
  not from binary: $x^{15}$ takes 6 multiplications by squaring and 5 by chain. Finding optimal
  chains is hard and almost never worth it — unless, as in problem 768, a single multiplication is
  expensive enough to notice.
- **The exponent is a secret.** The branch on each bit is a timing side channel; production
  cryptography uses a [Montgomery ladder](https://en.wikipedia.org/wiki/Exponentiation_by_squaring#Montgomery's_ladder_technique)
  to do the same work in constant time. Irrelevant to Project Euler, decisive elsewhere.

## How to reason about it

- **Ask whether the operation is associative.** That is the entire precondition. If it is, the
  logarithmic power exists — for matrices, permutations, polynomials, function composition, min-plus
  products, whatever you are iterating.
- **Then ask what the identity is,** and seed the accumulator with it. This is where the
  generalisation actually breaks in practice.
- **Cost is $\log e$ multiplied by the cost of one squaring.** For a $d \times d$ matrix that is
  $O(d^3 \log e)$, so the win comes from shrinking the *state*, not just the exponent: problem 237's
  companion matrix is $4 \times 4$ because the recurrence has order 4, and no larger.
- **Reduce inside the loop.** Under a modulus, reduce after every multiply, or the operands grow and
  the logarithmic operation count buys you nothing. `pow(b, e)` builds an astronomically large
  integer; `pow(b, e, m)` never exceeds $m^2$.
- **When the powers come in bulk, invert the loops** — bits outside, data inside — and mind the
  width: with `int64` lanes every partial product needs $m^2 < 2^{63}$, which is why problem 421 caps
  its primes below $2^{32}$.
- **Skip the last squaring** when a multiply is expensive. One line, one saved convolution.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0048](/solutions/0048/) — Self Powers
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0768](/solutions/0768/) — Chandelier
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0944](/solutions/0944/) — Sum of Elevisors

<!-- /problems -->
