<!-- tags: [catastrophic-cancellation] -->
<!-- status: final 2026-10-28T09:34Z -->
# Catastrophic cancellation

When you subtract two floating-point numbers that agree in their leading digits, those digits
cancel. What is left is made of the trailing digits, and the trailing digits were the ones already
carrying rounding error. That is
[catastrophic cancellation](https://en.wikipedia.org/wiki/Catastrophic_cancellation). The
subtraction itself is exact. The damage was done earlier, and the subtraction just moves it to the
front of the result. The three problems below each hit it in a different place: a quadratic root
(247), the distance of an irrational from 1 (318), and a function evaluated near zero (461). Each
one gets out a different way. This page is about recognising the shape and choosing the exit.

The general theory is on two other pages, and I won't repeat it here.
[Floating-point arithmetic](/topics/technique/floating-point-arithmetic) covers what a `double`
can and cannot represent exactly.
[Rearrange a formula to avoid cancellation](/topics/takeaway/rearrange-to-avoid-cancellation)
covers the condition number of a subtraction and a table of standard rewrites. This page is the
case study: what each solution actually does, and why that choice suits the problem.

## The shape to look for

Cancellation needs two things together: a **small result**, and a formula that builds it from
**large, nearly equal parts**. If the operands agree in $k$ leading digits, about $k$ of the
$16$ digits a `double` carries are gone. So "how many digits do I lose?" has an easy answer:
count how many digits the two sides share.

The way out is never to do the subtraction better. It is to find a formula where the small
quantity is **computed directly** instead of being what is left over. There are three ways to do
that, and the three problems use one each.

## Rearrange: problem 247

Problem 247 packs squares under $y = 1/x$. At every region it needs the side $s$ of the largest
square whose lower-left corner is at $(x, y)$, which is the positive root of $(x+s)(y+s) = 1$.
The quadratic formula gives

$$s = \tfrac12\left(\sqrt{(x-y)^2 + 4} - (x+y)\right),$$

and along the bottom row $x$ grows past $10^3$, so the square root and $x + y$ become nearly
equal. Multiplying top and bottom by their sum puts the small quantity in the numerator, where
it can be computed directly:

$$s = \frac{2(1 - xy)}{(x+y) + \sqrt{(x-y)^2 + 4}}.$$

$1 - xy$ is the slack that really is shrinking, and it comes from inputs that are not themselves
differences of nearly equal values. The denominator adds two positive numbers, which is always
safe. The cost is the same (one square root, one division), and the result is accurate to one
rounding instead of losing digits as $\varepsilon x^2$. The rearrange page measures both forms
against 50-digit decimals. It also shows why this matters for 247 in particular: the problem asks
for a *rank*, so the error has to stay below the gap between neighbouring squares, and with the
naive formula that margin is gone one input size above the main case.

## Conjugate plus an exact numerator: problem 318

Problem 318 depends on the conjugate $y = \sqrt q - \sqrt p$. Why the fractional part of
$(\sqrt p + \sqrt q)^{2n}$ is $1 - y^{2n}$ is explained on the
[Diophantine approximation](/topics/domain/diophantine-approximation) page. The number of nines
is then a ratio of logarithms,

$$N = \left\lceil \frac{d \ln 10}{-2 \ln y} \right\rceil,$$

and the hard pairs are those with $y$ just below 1. There $\ln y$ is tiny, $N$ runs into the
millions, and computing `log(sqrt(q) - sqrt(p))` cancels **twice**. The subtraction loses
digits, and then `log` of a value near 1 loses more, because it effectively computes $\ln(1 - \varepsilon)$
from a $1 - \varepsilon$ that has already been rounded.

The solution handles both with one move. It never forms $y$. It computes the gap
$\varepsilon = 1 - y$ directly. Multiplying $1 + \sqrt p - \sqrt q$ by conjugates twice clears
every root out of the numerator. With $g = q - p - 1$,

$$\varepsilon = \frac{4p - g^2}{\left(2\sqrt p + g\right)\left(1 + \sqrt p + \sqrt q\right)}.$$

The numerator is an **exact integer**. Every factor in the denominator is a sum of positive
numbers. Then `log1p(-ε)` gives $\ln y$ without ever forming the rounded value near 1. What makes
this the right exit is the integer numerator. The small quantity is not just rearranged. It is
*exact*, so the only rounding left is a few well-conditioned operations.

A ceiling is still a ceiling, though. If the float quotient lands within $10^{-4}$ of an integer,
the solution recomputes that one pair in 60-digit
[`decimal`](https://docs.python.org/3/library/decimal.html) (MPFR in the C port). This is the
fourth way out, **switch to exact or high-precision arithmetic**, and it is used the cheap way:
only for the few inputs where the decision is close, not for the whole sweep. Floats propose,
exact arithmetic decides near the boundary.

## The library primitive: problem 461

Problem 461 defines $f_n(k) = e^{k/n} - 1$ and looks for four indices whose values add up as
close to $\pi$ as possible. For small $k/n$, `exp(k/n) - 1` subtracts 1 from a value just above
1, which is the textbook case. [`expm1`](https://docs.python.org/3/library/math.html#math.expm1)
exists for exactly this. It computes $e^x - 1$ without forming the value near 1, so it is accurate
to one rounding *relative to the small result*. The solution builds its whole table with
`np.expm1`.

It is worth asking how much that gains here, because the decision is about the **absolute**
error of a sum near $\pi$. With the naive form, each term's error is at most one ulp of the
numbers involved. At the statement's $n = 200$ I measured at most $4.4 \times 10^{-16}$, one ulp
of $\pi$. Both versions find the same best error there, because the next-best quadruple is about
$7 \times 10^{-9}$ further away. The full-size problem is different. There are over $10^4$ indices
and so on the order of $10^{15}$ candidate quadruples, and near $\pi$ their sums are spaced about
an ulp apart. An error of one
ulp per term is then the same size as the gap between the best and second-best candidates. At
that size `expm1` is not a refinement. It is what lets the search tell the winner from its
neighbour.

That points to a second cancellation, one no rewrite removes. The objective
$\lvert f(a)+f(b)+f(c)+f(d) - \pi \rvert$ is *itself* a small difference of nearly equal values.
The fix for that one is to bound it. Four correctly rounded terms and a few additions give an
error of a handful of ulps, and that bound is what has to be smaller than the gap between the
winner and the runner-up.

## How to reason about it

- **Look for the subtraction behind every small quantity.** A root that shrinks as a parameter
  grows (247), a distance from 1 (318), a function at small argument (461). If the result is small
  and the formula subtracts large numbers to get it, count the shared leading digits. That is the
  number of digits you lose.
- **Pick the exit that fits the problem.**

  | Situation | Exit | Problem |
  | --- | --- | --- |
  | Difference of a root and a sum | conjugate, so the small part goes on top | 247 |
  | Small part has an integer form | rearrange until the numerator is an exact integer | 318 |
  | $e^x - 1$, $\ln(1+x)$ near zero | `expm1`, `log1p` | 461, 318 |
  | Decision lands near a boundary | recompute that case in `decimal` / `Fraction` | 318 |
  | The cancellation is the objective | bound the error against the decision gap | 461 |

- **Compute the small number, don't keep what is left over.** After the rewrite the small
  quantity should come from operands that were never nearly equal: an integer, a slack, a library
  primitive. If your new formula still subtracts nearly equal numbers somewhere, you have moved the
  problem, not solved it.
- **Match the error to the decision.** Rank (247), ceiling (318) and nearest-to-$\pi$ (461) each
  fail at a different error size. Work out the gap the answer depends on, then check that the
  arithmetic stays below it at the *largest* input, not only the example.
- **Use high precision to decide and to diagnose, not as the main path.** Running every case in
  `decimal` hides the structure and costs a lot. Running only the borderline ones (318), or using a
  high-precision rerun to test how many `double` digits were real, keeps the fast path and the
  guarantee.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0318](/solutions/0318/) — 2011 Nines
- ● [0461](/solutions/0461/) — Almost Pi

<!-- /problems -->
