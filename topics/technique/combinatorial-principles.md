<!-- tags: [combinatorial-principles] -->
<!-- status: final -->
# Combinatorial principles

The [combinatorial principles](https://en.wikipedia.org/wiki/Combinatorial_principles) are the
handful of rules that every counting argument is built from. The **rule of sum** says disjoint cases add. The
**rule of product** says independent choices multiply. The **rule of subtraction**, or
[complementary counting](https://en.wikipedia.org/wiki/Combinatorial_principles#Complementary_counting),
says count everything and remove what is forbidden. **Bijection** says count something easier that is in
one-to-one correspondence. They are too basic to be "the idea" of a hard problem, and that is why they
deserve a page. In the three solved problems below the real work is choosing the case split that
makes the rules apply *cleanly*: no overlap between cases, true independence inside each case, and
an easy complement. Once the split is right, the count is a short formula over a few parameters
instead of an enumeration of $10^{21}$ or $10^{2022}$ objects.

## The idea — partition, multiply, correct

Most counting solutions have the same three steps:

1. **Partition** the objects by a parameter that each object determines *uniquely*. Then summing
   over the parameter counts every object once (rule of sum), with no inclusion–exclusion needed.
   Choosing the parameter is the creative step. Good ones are "the dominant digit", "the value of the
   $t$-th largest die", or "the digit lengths of the factors".
2. **Within a case, factor** the count into independent choices: which positions, which values, how
   the rest is filled (rule of product). A binomial or multinomial coefficient
   chooses positions, and a power such as $9^{L-k}$ fills free slots.
3. **Correct** with the rule of subtraction for whatever the factorisation over-counts. A typical example is
   strings with a leading zero, which are not numbers of that length.

If step 1's parameter is *not* determined by the object, for example "some digit appears $k$ times" when two
digits could each appear $k$ times, the cases overlap. You then need
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle), which is the general and heavier
form of step 3.

## Three countings across the problems

**32, pandigital products: count digits to prune the search.** Find all $a \times b = c$ whose digits,
together, use 1 to 9 once. Counting digits is the principle at work: the three lengths sum to 9,
and a product of an $m$-digit and an $n$-digit number has $m + n - 1$ or $m + n$ digits. Only the
splits $(1, 4, 4)$ and $(2, 3, 4)$ satisfy both. Each split's candidates are then a *product* of choices:
an ordered selection for $a$ from 9 digits, then one for $b$ from the remaining ones. That is
$9 \times 1680 + 72 \times 210$, about 30,000 candidates. The public Python is the enumeration
written exactly as that product:

```python
for a_len, b_len in ((1, 4), (2, 3))
for a in itertools.permutations(nine_digits, a_len)
for b in itertools.permutations((d for d in nine_digits if d not in a), b_len)
```

**240, top dice: partition by the pivot.** Count ordered rolls of twenty 12-sided dice whose top ten
sum to 70, out of $12^{20} \approx 3.8 \times 10^{21}$ rolls. The partition parameter is the value $v$ of
the tenth-largest die, together with how many dice are above it ($a$) and equal to it ($b$). Every roll
determines $(v, a, b)$ exactly, so the cases are disjoint. Within a case the count factors into three
independent parts. A multinomial chooses which positions are above, equal and below. An ordered-sum
[DP](/topics/technique/dynamic-programming) counts the above-pivot values that bring the total to 70.
And $(v - 1)^{\text{below}}$ fills the rest. The sum over cases is about $10^5$ operations.

**788, dominating numbers: sum, product, subtract.** Count numbers below $10^{2022}$ with more than half
their digits equal. The case parameter is the length $L$, the dominant digit $v$, and its multiplicity
$k > L/2$. At most one digit can exceed half, so the cases are disjoint, and no inclusion–exclusion is needed.
Within a case the count is $\binom{L}{k} 9^{L-k}$: choose positions, then fill the others. The rule of
subtraction removes strings that start with 0. Those are counted separately for $v = 0$, where a dominant slot is
first, and for $v \ne 0$, where a filler 0 is first. The result is an $O(N^2)$ double sum.

## Python and C

- **32**: Python is one set comprehension over two `itertools.permutations` calls. C has no
  permutation generator, so it unrolls the ordered selections into nested loops with collision guards
  (`if (q1 == q0) continue`), and it deduplicates products with a linear scan of a small array.
- **240**: the same three-layer computation. Python's integers are exact. C checks that `long long` is
  enough: every term is positive and at most the final total, and the largest factorial used, $20!$,
  fits. So no bignum is needed, and C is about 30 times faster.
- **788**: here the languages differ sharply. Python keeps $9^{L}$ and `math.comb` values as **exact**
  integers with thousands of digits and reduces mod $p$ once at the end. C reduces every operation mod $p$
  and builds a Pascal-triangle table of binomials mod $p$. Both are correct, because reduction commutes
  with $+$, $-$ and $\times$. But Python takes 67.8 s and C 0.027 s, a gap that has nothing to do with
  the interpreter and everything to do with carrying 2000-digit numbers. A Python version reducing
  as it goes would close most of it.

## How to reason about it

- **Find a parameter every object determines.** Then the cases are disjoint and the rule of sum is
  exact. If no such parameter exists, plan for inclusion–exclusion.
- **Inside a case, look for independent choices.** Positions times values times free fills: a
  binomial or multinomial times powers.
- **Count the complement when it is simpler.** Leading zeros, "at least one", and "not all distinct" are
  often easier to subtract than to count directly.
- **Use counting to prune enumeration.** Digit-length or size arguments (32) cut a search before any
  candidate is built.
- **Check against brute force on small inputs.** 240's notes compare thousands of small parameter sets
  with a full enumeration. That catches exactly the off-by-one in a case boundary that counting
  arguments are prone to.
- **Under a modulus, reduce as you go.** In every language, not just C.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0240](/solutions/0240/) — Top Dice
- ● [0788](/solutions/0788/) — Dominating Numbers

<!-- /problems -->
