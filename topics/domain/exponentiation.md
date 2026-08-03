<!-- tags: [exponentiation] -->
<!-- status: final -->
# Exponentiation

[Exponentiation](https://en.wikipedia.org/wiki/Exponentiation) is the one elementary operation whose
output outruns its input. Addition and multiplication grow a number by a factor; `a^b` grows it by an
*exponent*, so `1000^1000` — five characters of statement — is a three-thousand-digit integer. Every
problem below inherits that asymmetry, and the recurring move is the same one: refuse to build the
number, and work instead in a representation that answers the actual question.

## The idea

`a^b` is best read as a **description** of a number rather than the number. The description is cheap
(two small integers); the number is not. So the first question on an exponentiation problem is not
"how do I compute this" but *what property of the value am I actually asked about* — because each
property has a compact representation that survives exponentiation, and picking the right one is the
whole solution.

| Question about `a^b` | Representation | Why it survives |
| --- | --- | --- |
| Which is bigger? | `b · log a` | `log` is strictly increasing, and `log(a^b) = b · log a` |
| Are two powers equal? Is it a perfect power? | prime-exponent map | `a = ∏ pᵉ` ⟹ `a^b = ∏ p^(e·b)`; unique factorisation |
| What are the last digits? Is it divisible by `m`? | `a^b mod m` | the modulus distributes over `×` |
| How many digits? | `⌊b · log₁₀ a⌋ + 1` | the same log identity, read as a length |
| What are *all* the digits? | the bignum itself | nothing cheaper preserves the decimal expansion |

The first row collapses a three-million-digit comparison into one multiply: problem 99 ranks a
thousand candidates by [logarithm](/topics/technique/logarithm) in a single linear scan. The second
turns *equality of enormous numbers* into equality of small tuples — problem 29 counts distinct `a^b`
by keying a set on `((p, e·b), …)` rather than on the value, and the same signature is what makes
"is `n` a perfect power" (problems 302, 616) a question about the gcd of exponents. The third is
[modular exponentiation](/topics/technique/modular-exponentiation), and it is the workhorse: problem
48 wants ten trailing digits of `Σ iⁱ`, which is that sum mod `10¹⁰`.

```python
result = 0
for i in range(1, limit + 1):
    result = (result + pow(i, i, 10**10)) % 10**10
```

The three-argument `pow` is
[exponentiation by squaring](/topics/technique/exponentiation-by-squaring) —
`⌊log₂ b⌋ + popcount(b) − 1` multiplications instead of `b − 1`, with every intermediate held below
the modulus. It is why problems that sum `k^k` over hundreds of thousands of terms (problem 250) are
tractable at all.

Only the last row is genuinely expensive, and it is right exactly when the decimal expansion *is* the
question — the digit sums of problems 16 and 56, the digit-power identities of 119 and 749. There,
arbitrary-precision integers are the correct tool and Python hands them over for free; the work moves
to *bounding the search*, and that bound comes from the log row. Problem 63 is the clean case: `b^n`
has `⌊n·log₁₀ b⌋ + 1` digits, so no base `≥ 10` can ever produce an `n`-digit `n`-th power, and each
single-digit base falls out at its own `n` — nine bases, twenty-one exponents, a constant-size search
extracted from an unbounded-looking one.

```python
lo = math.ceil((10 ** (n - 1)) ** (1 / n))        # smallest base with n digits at exponent n
hi = math.ceil((10**n - 1) ** (1 / n)) + 1
```

## Exponents live in their own arithmetic

The second structural fact is that exponents do not combine like bases. `a^m · a^n = a^(m+n)`, so
multiplying powers *adds* exponents — and that shift downward by one operation is where several of
these problems live.

It shows up as a **cost model**: the minimum number of multiplications reaching `n^k` is the length
of a minimal [addition chain](/topics/domain/addition-chain) for `k`, since each multiplication adds
two exponents you already hold. Binary squaring gives a good chain but not always the best — `n^15`
takes six multiplications by squaring and five by the chain `1, 2, 3, 6, 12, 15` — and finding the
minimum is NP-hard in general, which is why problem 122 is a bounded search rather than a formula.

It shows up again as a **modulus**: when reducing `a^e mod n`, the base reduces mod `n` and the
exponent mod [`λ(n)`](/topics/technique/carmichael-function), the two living in different rings. That
is what makes towers and self-powers finite objects — `i ↦ iⁱ mod m` is eventually periodic, and
problems 411, 617, 801 and 830 are built on the period rather than on the values.

## How to reason about it

Ask what the question needs, then take the weakest representation that answers it. Weaker is cheaper,
and cheaper is usually the difference between feasible and not: order needs only logs, equality only
signatures, trailing digits only residues. Reaching for the bignum first is the characteristic
mistake, and it is often not merely slow but impossible.

Three pitfalls are worth naming:

- **Float logs decide order, not equality.** A double carries ~15–16 significant digits. Ranking a
  thousand well-separated candidates is safe; deciding whether `2^a = 3^b` by comparing logs is not.
  When two candidates are close, fall back to the exact prime signature.
- **Exponent reduction needs coprimality.** `a^e ≡ a^(e mod λ(n))` holds when `gcd(a, n) = 1`. When
  `a` shares a factor with `n`, use `a^(e mod λ(n) + λ(n))` for `e ≥ log₂ n`, or split `n` by
  [CRT](/topics/technique/chinese-remainder-theorem) and handle the shared primes separately.
  Skipping this is the standard silent wrong answer.
- **A residue does not answer every question.** It tells you nothing about magnitude, digit sums, or
  order — so a problem asking for an
  [exact sum](/topics/takeaway/exact-sums-resist-modular-shortcuts), or asking *which* term is
  largest, cannot be reduced early however convenient the modulus looks.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0048](/solutions/0048/) — Self Powers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0099](/solutions/0099/) — Largest Exponential
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0250](/solutions/0250/) — $250250$
- ○ [0302](/solutions/0302/) — Strong Achilles Numbers
- ○ [0411](/solutions/0411/) — Uphill Paths
- ○ [0616](/solutions/0616/) — Creative Numbers
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ○ [0678](/solutions/0678/) — Fermat-like Equations
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ○ [0905](/solutions/0905/) — Now I Know

<!-- /problems -->
