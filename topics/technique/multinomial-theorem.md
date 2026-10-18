<!-- tags: [multinomial-theorem] -->
<!-- status: final 2026-10-18T10:14Z -->
# Multinomial theorem

The [multinomial theorem](https://en.wikipedia.org/wiki/Multinomial_theorem) expands a power of a
sum:

$$(x_1 + \dots + x_m)^n = \sum_{k_1 + \dots + k_m = n} \binom{n}{k_1, \dots, k_m} x_1^{k_1} \cdots x_m^{k_m},
\qquad \binom{n}{k_1, \dots, k_m} = \frac{n!}{k_1! \cdots k_m!}.$$

The coefficient counts the ways to label $n$ positions with $m$ classes so that class $i$ gets
$k_i$ of them. These problems need that count whenever *order matters but only the class sizes
are known*: dice sorted into above, at and below a pivot, digit strings grouped by their digit
content, factors of a trinomial power picking one of three terms. The four solutions below compute
the coefficient in four different forms: its $p$-adic valuation, its exact value, a ratio between
neighbouring terms, and a product of binomials. Which form to use is the main design decision.

## The idea

Read the theorem from right to left. Expanding $(x_1 + \dots + x_m)^n$ means choosing one term from
each of $n$ factors, and the multinomial coefficient counts the choices that give the same
monomial. That gives two equivalent uses:

- **Counting arrangements.** The number of distinct sequences that are permutations of a multiset
  with multiplicities $k_i$ is $\binom{n}{k_1, \dots, k_m}$. Assigning positions to classes and then
  filling each class independently turns a count of ordered objects into a sum over class sizes.
- **Extracting a coefficient.** To read $[x^j]\,P(x)^n$ for a small polynomial $P$, sum the
  multinomial terms whose exponents give degree $j$. For a trinomial this is a single sum.

Two identities help with the computation:

$$\binom{n}{k_1, \dots, k_m} = \binom{n}{k_1}\binom{n - k_1}{k_2}\cdots\binom{k_m}{k_m}
\quad\text{and}\quad
v_p\binom{n}{k_1, \dots, k_m} = \frac{\sum_i s_p(k_i) - s_p(n)}{p - 1}.$$

The first follows by choosing the classes one at a time. The second follows from
[Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula), with $s_p$ the base-$p$
digit sum. It equals the number of carries when adding the $k_i$ in base $p$, which generalises
[Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem).

## Four forms of the same coefficient

**Its valuation: 154.** Level $n$ of Pascal's pyramid holds the trinomial coefficients
$\binom{n}{i, j, k}$, and the problem asks how many are divisible by $10^{12}$ at $n = 200000$.
These numbers have tens of thousands of digits, and there are $2 \times 10^{10}$ of them. The
valuation formula makes each test a comparison of small integers:
$s_2(i) + s_2(j) + s_2(k) \ge s_2(n) + 12$, and the same with $s_5$ against $s_5(n) + 48$, the 12
scaled by $p - 1 = 4$. The digit sums fill a byte table in $O(n)$ by
$s_p(x) = s_p(\lfloor x/p \rfloor) + x \bmod p$. After that, the $O(n^2)$ scan only adds bytes.
For divisibility questions you need the valuation and never the value.

**Its value: 240.** Twenty 12-sided dice, and the top ten must sum to 70. Fix the pivot $v$, the
value of the tenth-largest die. Then each die is above, equal to, or below $v$, and a roll with
class sizes $(a, b, \ell)$ is counted by

$$\binom{n}{a,\, b,\, \ell} \cdot N_v(a, \Sigma) \cdot (v - 1)^{\ell}.$$

The multinomial places the classes. $N_v$ is a DP over the ordered values above the pivot, and
the last factor fills the dice below it. The multinomial is what makes "ordered rolls" cost
nothing: positions go to classes in closed form, and only the above-pivot class needs its order
counted inside $N_v$. Here the coefficient is needed exactly, from a factorial table, as
`factorial[num_dice] / (factorial[above] * factorial[equal] * factorial[below])`. The
denominator never exceeds $n!$, because a product of factorials of parts is at most the factorial
of their sum, so the C can form it in `long long` too.

**A term ratio: 743.** The count reduces to $[x^k]\,(1 + bx + x^2)^k$. Picking $x^2$ from $p$
factors, $1$ from $p$ others and $bx$ from the rest gives

$$[x^k]\,(1 + bx + x^2)^k = \sum_{p=0}^{\lfloor k/2 \rfloor} \frac{k!}{p!\,p!\,(k - 2p)!}\, b^{k - 2p}.$$

That is the trinomial theorem specialised to the middle coefficient, the
[central trinomial](https://oeis.org/A002426) pattern with a weight. The solution avoids
factorial tables entirely. It starts from $t_0 = b^k$ and steps with the ratio of consecutive terms,
$t_p / t_{p-1} = (k - 2p + 1)(k - 2p + 2) / (p^2 b^2)$, modulo a prime. That is $O(k)$ with
$O(1)$ memory, and $k = 10^8$ is too large for a factorial table anyway. The cost moves into the
inverse of $p^2$ at each step. The solution computes it by Fermat exponentiation inside the loop,
which makes the exponentiation the dominant cost. A linear-time table of inverses (see
[modular multiplicative inverse](/topics/domain/modular-multiplicative-inverse)) would remove that
cost, at the price of $O(k)$ memory.

**A product of binomials: 885.** Sum $f(d)$, the sorted non-zero digits of $d$, over all strings
of $n \le 18$ digits. Strings with the same digit content share $f$, and there are
$\binom{n}{c_0, c_1, \dots, c_9}$ of them. Enumerating the $\binom{n+9}{9}$ count vectors would
work. The DP does better by factoring the multinomial into binomials. It processes digits 9 down
to 1 and multiplies by $\binom{n - t}{k}$ when it places $k$ copies of the next digit into the
$n - t$ free positions. The product telescopes to the full multinomial, so the state needs only
$t$, the number of positions used, and never the whole vector. The zeros take the leftover
positions at no cost. The same factorisation is what lets 862 (on
[stars and bars](/topics/technique/stars-and-bars-combinatorics)) thread a running denominator
down its recursion.

## C and Python

| problem | Python | C |
| --- | --- | --- |
| 154 | forward slice plus reversed slice of the digit-sum table, two masks, `sum()` per row | explicit loop over half the row, using the $j \leftrightarrow k$ symmetry (add 2 off the diagonal, 1 on it) |
| 240 | exact `int` factorials | `long long`, after checking that $20!$ and every partial sum fit below $2^{63}$ |
| 743 | `pow(x, MOD - 2, MOD)` | hand-written `power_mod` with 64-bit reduction |
| 885 | `math.comb` | Pascal's triangle flattened to one block, indexed `a * (n + 1) + k` |

Two of these are worth a closer look. 240's C stays on native integers because of an argument, not
a hope. Every term in the sum is positive, so no partial sum exceeds the answer, and the answer is
81% of `LLONG_MAX`. 154's C halves its inner loop with a symmetry the vectorised Python does not
bother with. A whole-row NumPy expression costs the same either way, while in a scalar loop the
saving is real.

## How to reason about it

- **Order matters, but only class sizes are known? Use a multinomial.** Fix the class sizes, place
  the classes with $\binom{n}{k_1, \dots, k_m}$, and count within each class independently.
- **For divisibility, use the valuation.** Digit sums in base $p$ give $v_p$ of any multinomial
  without forming it.
- **For a power of a short polynomial, sum over the exponent split.** A trinomial coefficient is a
  single sum. Step between terms by their ratio when tables would be too large.
- **Factor into binomials to shrink a DP state.** Choosing one class at a time from the remaining
  positions turns a vector state into a single counter.
- **Prove the width.** Before using a bignum in C, check whether the terms are positive and the
  total is bounded. If so, the final answer bounds every intermediate.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0240](/solutions/0240/) — Top Dice
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0885](/solutions/0885/) — Sorted Digits

<!-- /problems -->
