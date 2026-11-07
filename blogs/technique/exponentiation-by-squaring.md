<!-- tags: [exponentiation-by-squaring] -->
<!-- status: final 2026-11-03T22:26Z -->
# Exponentiation by squaring

[Exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) computes
$b^e$ in about $\log_2 e$ operations instead of $e$ of them, by reading the exponent in binary. That
much is a one-line summary of a nine-line loop, and if the story stopped there this page would be a
footnote to [modular exponentiation](/blogs/technique/modular-exponentiation), which covers the
residue case in depth. It does not stop there. The reason the tag lands on the problems below is
that **the operation being squared is a parameter**: the same loop advances a linear recurrence
$10^{18}$ steps, raises a polynomial to a power while discarding everything above degree $m$, or
runs a million independent powers in lockstep across a NumPy array. Sometimes the power is not even
the answer, only a question put to a group: does this equal 1? Learning the loop is ten minutes;
learning to recognise what else it will accept is what pays.

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
| A residue mod $m$ | `1` | $b^e \bmod m$ | 48, 97, 217, 335, 752, 820, 926 |
| A $d \times d$ matrix | $I$ | $e$ steps of a linear recurrence | 237, 377, 670, 706, 940 |
| A polynomial truncated at degree $m$ | $1$ | an $e$-fold convolution, low terms only | 768 |
| A table of digit blocks, with its length | the empty block | $e$ digits, summarised | 294 |
| An element $u + v\sqrt{a}$ of $\mathbb{Z}_p[\sqrt{a}]$ | $(1, 0)$ | an irrational power, kept exact | 721, 752 |
| A formal root $ax + b$ of $x^2 - x - 1$ | $0x + 1$ | a power of a root never computed | 437 |
| A distribution over digits under $\times \bmod 10$ | all mass on digit 1 | the digit of an $e$-fold product | 778 |
| A distribution over Grundy values under XOR | all mass on value 0 | the value of $e$ independent games | 649 |
| A whole array of residues | `ones` | many independent powers at once | 407, 421, 429, 437, 455, 721, 944 |

**Matrices — a recurrence in logarithmic time.** Problem 237 counts Hamiltonian tours on a
$4 \times n$ board; the counts obey $T(n) = 2T(n-1) + 2T(n-2) - 2T(n-3) + T(n-4)$, and a fourth-order
[linear recurrence with constant coefficients](/blogs/technique/linear-recurrence-with-constant-coefficients)
is exactly repeated multiplication by its $4 \times 4$
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix). Iterating it $n = 10^{12}$ times
is hopeless; squaring the matrix 40 times is a few thousand integer multiplications, and the extra
test case at $n = 10^{18}$ costs 20 more. Problem 940 is the same move one dimension up: a
two-dimensional recurrence factors into a row matrix and a column matrix, so the answer is a product
of $2 \times 2$ matrix powers whose exponents are Fibonacci numbers — large, but only their bit
lengths are ever paid for. See [matrix exponentiation](/blogs/technique/matrix-exponentiation) and
the [transfer-matrix method](/blogs/domain/transfer-matrix-method); note that matrix multiplication
is not commutative, which the loop never assumed — keep `result` on the same side of every product
and it stays correct.

Problem 670 shows that the accumulator does not even have to live in the monoid. Its
[transfer matrix](/blogs/domain/transfer-matrix-method) has 10 states (each row's tile overhang,
with colours factored out by symmetry), and what it wants is the start vector times $M^{n-1}$, not
$M^{n-1}$ itself. So `result` starts as that row vector and each set bit folds in with a
vector–matrix product, $O(S^2)$, while only the base pays the $O(S^3)$ squaring. Nothing changes in
the bit loop — associativity guarantees $(vA)B = v(AB)$, which is all it needs — and every fold
becomes a factor $S$ cheaper. Problem 706 runs the same shape over an 81-state automaton.

Problem 377 shows that the exponent does not have to exist as a number either. It wants an entry of
$M^{b^i}$ for every $i$ up to 17, with $M$ an $18 \times 18$ matrix. Taking each target from scratch
means walking exponents up to 63 bits long, roughly 800 matrix products over the whole sum. But
$M^{b^i} = (M^{b^{i-1}})^b$, so the solution raises the running matrix to the small fixed power $b$
and keeps it for the next term: seven products a term, 119 in all. The targets had structure that
their binary expansions throw away, and the chain keeps it. Since $b^i$ is never formed, a target
too wide for any integer type would cost nothing extra.

**Truncated polynomials.** Problem 768 raises a generating polynomial to a power, keeping only the
terms up to degree $m$ because nothing above that can influence the answer. Truncated multiplication
is associative and has the identity $1$, so the loop applies unchanged — but here a single "multiply"
is an $O(m^2)$ convolution rather than one machine instruction. That inverts the usual economics:
saving one operation is now worth a line of code, which is why its loop guards the final squaring
(`if exponent:` before squaring the base) instead of computing a square it will never use. Cheap
when a multiply is a `mul` instruction, genuinely worth it when a multiply is a convolution.

**Elements that carry their own context.** Problem 294 counts digit strings of length about
$3 \times 10^{12}$ by residue mod 23 and digit sum, and a block of digits is summarised by a small
table over those two. Concatenation is the operation and it is associative, yet two tables alone
cannot be multiplied: the upper block's residues must first be scaled by $10^L$, where $L$ is the
length of the block beneath it. The way out is to widen the element. The monoid is not tables but
pairs (table, length), with the empty block as identity, a
[semidirect product](https://en.wikipedia.org/wiki/Semidirect_product) in the same way that affine
maps $x \mapsto ax + b$ compose as pairs. An operation that seems to depend on position usually
needs only this: put whatever it depends on into the element.

That solution also runs the loop the other way. Scanning $n$ from its top bit, each step doubles the
block and, on a set bit, appends one digit, so it holds one running table and one fixed one-digit
table, where right-to-left would carry two full tables and two lengths. Associativity makes the two
directions equivalent, and either way it comes to some sixty concatenations for 42 bits.

**Rings you invent for the occasion.** Problem 721 needs $\lfloor (c + \sqrt{a})^{n} \rfloor$ for
exponents in the trillions. Floating point is useless at that size, but the conjugate $c - \sqrt{a}$
lies in $[0, 1)$, so $(c + \sqrt{a})^n + (c - \sqrt{a})^n$ is an integer just above the floor. Write
$(c + \sqrt{a})^n = u + v\sqrt{a}$ and the pair $(u, v)$ multiplies by
$(u_1u_2 + a\,v_1v_2,\; u_1v_2 + v_1u_2)$ — the [quadratic integer](https://en.wikipedia.org/wiki/Quadratic_integer)
ring, reduced mod $p$. That product is associative with identity $(1, 0)$, so the loop
exponentiates an irrational number exactly, and the answer is $2u$ (less one when $a$ is not a
square). Problem 778 goes more abstract still: its "freshman's product" multiplies digit by digit
mod 10, so the count of $R$-tuples whose product has digit $d$ in one position is the $R$-th power
of that position's digit histogram under convolution over the multiplicative monoid
$(\mathbb{Z}/10, \times)$ — a 10-by-10 `out[x*y % 10] += a[x]*b[y]`. Its identity is the
distribution with all its mass on digit **1**; seeding the accumulator with mass on digit 0, the
natural-looking "empty" choice, makes every product zero. That is the identity pitfall from above,
in a setting where it is easy to miss.

Problem 649 repeats the construction over a different index set, and the contrast gives the rule.
Each coin on its board is a game with a [Grundy value](/blogs/technique/sprague-grundy-theorem)
below 8, and independent games combine by XOR, so the histogram for $c$ coins is the $c$-th power of
one coin's histogram under XOR convolution. Here the identity is all mass on **0**, the very seed
that breaks problem 778, because the identity of a convolution is a point mass on the identity of
the operation on its *indices*: 1 for $\times$, 0 for $\oplus$. The problem also shows the loop's
competitor. A [Walsh–Hadamard transform](https://en.wikipedia.org/wiki/Fast_Walsh%E2%80%93Hadamard_transform)
turns XOR convolution into pointwise multiplication, after which the power is eight scalar `pow`
calls. But its inverse divides by 8, which has no inverse modulo $10^9$; you would have to work
modulo $8 \cdot 10^9$ and divide exactly at the end. At width 8 a direct product is only 64
multiplications, so the plain loop wins. Diagonalise when the width is large and the modulus allows
it, and otherwise square.

**A root you never find.** Problem 437 asks about the two roots of $x^2 - x - 1$ modulo each of
about 2.9 million primes, and finding them would take a modular square root of 5 per prime. Instead
the solution exponentiates the *symbol*. In the
[quotient ring](/blogs/technique/quotient-ring-arithmetic) $\mathbb{Z}_p[x]/(x^2 - x - 1)$ every
power reduces to $x^m = ax + b$, with $a$ and $b$ consecutive Fibonacci numbers mod $p$, and that one
result holds for both roots at once, since $r^m = ar + b$ for either. Problem 721's ring keeps an
irrational exact; this one avoids solving an equation at all. One power answers for two unknowns,
and whether $r^m = 1$ is settled by algebra on $(a, b)$, with no square root or inverse anywhere.

It is also a cheaper way to write something familiar. The $x$ here is the $2 \times 2$ Fibonacci
matrix in disguise, and a product costs four multiplications instead of eight. By the
[Cayley–Hamilton theorem](/blogs/domain/cayley-hamilton-theorem) this holds for any companion
matrix: its powers are polynomials in it of degree below $d$, so multiplying them modulo the
characteristic polynomial costs $O(d^2)$ where the matrix product costs $O(d^3)$.

**Arrays.** Python's `pow` is scalar and [NumPy](/blogs/technique/numpy) has no three-argument
`pow`, so a sweep that needs a power for each of a million elements is a million interpreter round
trips. Problems 421, 429 and 944 write the bit loop out by hand for exactly this reason: with the
loop over *bits* on the outside, every step — the squaring, the conditional fold, the shift — is one
whole-array operation, and the number of passes is the bit length of the largest exponent (say 40 or
60), not the length of the array. Problem 421 goes furthest, carrying a *vector* modulus, one prime
per lane, so thousands of different moduli advance together. The payoff shows up in the benchmarks:
the [vectorised](/blogs/technique/vectorized) Python of 421, 429 and 944 runs at 2.2 s, 0.93 s and
9.3 s against C siblings at 0.99 s, 0.70 s and 7.4 s — a factor of 1.3–2.2 — while the scalar
matrix-power solutions of 237 and 940 sit 40–45× behind their C versions. Same algorithm; the
difference is whether the interpreter is entered once per bit or once per element.

The newer array solutions show the two shapes this takes. When every lane shares one exponent, the
loop is the scalar one verbatim: problem 407 builds a table of inverses modulo $s$ for all residues
at once as $r^{\varphi(s)-1}$ ([Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem)),
one exponent for the whole `arange`. When each lane has its own exponent, there is no single
`while exponent:` to test, so the loop runs a fixed number of bits — the width of the largest
exponent — and folds under a mask: `result = np.where(bit_set, result * square % m, result)`.
Problem 455 does this inside a fixed-point iteration, re-evaluating $x \leftarrow n^x \bmod 10^9$
for every $n$ at once until the power tower stops changing, and 721 does it with its ring elements,
one $(u, v)$ pair per lane; 437 gives each lane its own ring element, exponent and modulus. The
masked form pays for every multiply in every lane whether the bit is
set or not, and the price grows with the multiply: 407 and 455 stay within 1.4× and 3.1× of C, but
721's ring product makes a dozen array temporaries per step and lands at 8×.

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
for perhaps 50 ([a better algorithm beats a faster language](/blogs/takeaway/algorithm-beats-language)).
Both answer the question, so the linear loop is not *wrong*; it is merely tied to the size of the
exponent, and one test case at $10^{18}$ would end it. The `__int128` casts are the other half of
the story and belong to [modular exponentiation](/blogs/technique/modular-exponentiation): two
residues near $10^{10}$ multiply to $10^{20}$, which a `long long` cannot hold.

## When the power is a question

Sometimes the value of the power is beside the point, and what matters is whether it equals 1. The
[Miller–Rabin test](/blogs/technique/miller-rabin-primality-test) in problems 200 and 387 computes
$a^d \bmod n$ and then keeps squaring — but it *watches* the intermediate squares, looking for a
nontrivial square root of $1$. The squarings that exponentiation by squaring normally throws away
are the evidence; the fast power is the primitive that makes a probabilistic primality test, and
with it much of public-key cryptography, affordable at all.

Group theory turns the same probe into a measurement. If $d$ is a known multiple of the
[order](/blogs/domain/multiplicative-order) of $u$, then for each prime $q \mid d$ you test whether
$u^{d/q} = 1$ and divide $d$ by $q$ for as long as it holds; what is left is the order exactly.
Problem 752 runs that reduction for every prime up to its limit, and the
[primitive root](/blogs/domain/primitive-root) test in 437 is the yes-or-no version, where $r$ has
order $p - 1$ unless some $r^{(p-1)/q}$ is 1. A search that would naively step through the order
becomes a handful of logarithmic powers. The price is the factorisation of $d$, which is why a
smallest-prime-factor sieve sits next to the loop in 752 and trial division next to it in 437.

Problem 752 also shows that the ring is yours to choose. It wants the order of $1 + \sqrt 7$ in
$(\mathbb{Z}/x)[\sqrt 7]$ and could run its pair loop on every prime, but it does not. Where 7 is a
[quadratic residue](/blogs/technique/quadratic-residue) it pays for one
[Tonelli–Shanks](/blogs/technique/tonelli-shanks-algorithm) root, maps the ring onto two copies of
$\mathbb{F}_p$, and hands the rest to the builtin `pow`. Where it is not, the
[Frobenius endomorphism](/blogs/technique/frobenius-endomorphism) gives $u^{p+1} = N(u) = -6$ for
free, so most of the order is found in $\mathbb{F}_p$, and pair arithmetic is left only with a
norm-one element whose order divides $p + 1$ instead of $p^2 - 1$.

Set that beside 437, which faces nearly the same choice and decides the other way: it refuses the
square root and stays in the ring. Both are right. Problem 437 runs on NumPy lanes, where no builtin
is on offer and one ring power covers both roots. Problem 752 is scalar Python, where `pow` runs in C
and a hand-written pair loop does not. Find the root when it buys a faster multiply, and skip it
when it does not.

## When not to reach for it

- **You need every power, not one.** $b^0, b^1, \dots, b^n$ is a running product: $n$ multiplications
  for the whole table, against $n \log n$ for $n$ independent fast powers. Problems 171 and 788 both
  build a place-value table this way (`pow10[k] = pow10[k-1] * 10 % MOD`) and never call `pow` at all.
  Problem 217 takes the other branch, one `pow(10, k-1-i, mod)` per place — correct, and lost in the
  noise beside its digit DP, but the table is the reflex worth having.
- **Python already does it.** `pow(b, e, m)` and even `b ** e` are binary exponentiation implemented
  in C over [arbitrary-precision integers](/blogs/technique/arbitrary-precision-arithmetic), and
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
  generalisation actually breaks in practice — $(1, 0)$ in a quadratic ring, and in a convolution a
  point mass on the identity of the index operation: digit 1 under $\times$, value 0 under XOR.
- **If the operation depends on position, widen the element.** Carry the length, or whatever else it
  depends on, inside the thing being multiplied, as problem 294 does.
- **The accumulator may be smaller than the base.** If you only need $v \cdot M^e$, start `result`
  at $v$ and fold with vector–matrix products, as problems 670 and 706 do; only the squarings pay
  full matrix cost.
- **Cost is $\log e$ multiplied by the cost of one squaring.** For a $d \times d$ matrix that is
  $O(d^3 \log e)$, so the win comes from shrinking the *state*, not just the exponent: problem 237's
  companion matrix is $4 \times 4$ because the recurrence has order 4, and no larger. A better
  representation helps too, from a matrix to a polynomial in problem 437, or from a pair to a
  residue in problem 752.
- **Look at the exponent's shape before its bits.** If the targets are $b, b^2, b^3, \dots$, chain
  the powers as problem 377 does; a power of a power beats a long binary expansion.
- **Reduce inside the loop.** Under a modulus, reduce after every multiply, or the operands grow and
  the logarithmic operation count buys you nothing. `pow(b, e)` builds an astronomically large
  integer; `pow(b, e, m)` never exceeds $m^2$.
- **When the powers come in bulk, invert the loops** — bits outside, data inside — and mind the
  width: with `int64` lanes every partial product needs $m^2 < 2^{63}$, which is why problem 421 caps
  its primes below $2^{32}$.
- **A matrix product budgets $d \cdot m^2$, not $m^2$,** because a cell sums $d$ products before you
  can reduce. Problem 377's C fits 18 terms in a `uint64_t` with about 2% to spare and reduces once
  per cell; problem 706's 81 terms do not fit, so its Python splits an operand into 15-bit halves and
  its C accumulates in `__int128`.
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
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0407](/solutions/0407/) — Idempotents
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ● [0670](/solutions/0670/) — Colouring a Strip
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ● [0768](/solutions/0768/) — Chandelier
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0944](/solutions/0944/) — Sum of Elevisors

<!-- /problems -->
