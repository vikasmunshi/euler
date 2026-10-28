<!-- tags: [aggregate-by-value] -->
<!-- status: final 2026-10-28T16:32Z -->
# Aggregate by value, not by instance

When a problem says "for every tuple", "for every sequence" or "for every string", the
instances are usually astronomically many — $(M+1)^R$ sequences, $3^{38}$ digit strings,
$10^9$-fold products — but the quantity being summed rarely depends on the instance itself.
It depends on some small *value* the instance carries: a digit, a digit-count triple, a
product, a prime's exponent. Once I can name that value, the move is always the same: build
a **multiplicity table** — how many instances map to each value — and do the arithmetic once
per value, weighted by its count. The enumeration disappears, and what is left costs as much
as the number of distinct values, which is usually tiny.

## The idea

Write the target as $\sum_{x \in X} f(x)$ over a huge set $X$. If $f(x) = g(\kappa(x))$ for a
map $\kappa$ onto a small set of classes $K$, then

$$\sum_{x \in X} f(x) = \sum_{k \in K} g(k)\,\bigl|\kappa^{-1}(k)\bigr|.$$

That is the whole trick — the same regrouping as a
[histogram](https://en.wikipedia.org/wiki/Histogram), or the "law of the unconscious
statistician" that lets an [expected value](https://en.wikipedia.org/wiki/Expected_value)
be taken over a distribution instead of over sample points. The work splits into two
independent questions: *what is the class?* (find $\kappa$) and *how big is each class?*
(count $|\kappa^{-1}(k)|$ without listing it). The second is where the mathematics lives —
usually a closed-form count from [combinatorics](https://en.wikipedia.org/wiki/Combinatorics).

The shape in code is a counter followed by a weighted sum:

```python
counts = Counter(map(kappa, xs))        # how many instances per class
total = sum(g(k) * c for k, c in counts.items())
```

— except that in the problems below even the first line is too slow, so the counts come
from a formula rather than a pass.

The four problems use four different class maps:

| Problem | Instances | Class $\kappa$ | Size of a class |
|---|---|---|---|
| 452 | $n$-tuples with product $\le m$ | the product $k$ | $d_n(k)$, via [stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)) per prime |
| 675 | primes $p$ updating $i!$ | the multiple index $k$ (for $p > \sqrt n$) | how many such primes have a $k$-th multiple |
| 698 | digit strings of length $L$ | the digit-count triple $(c_1,c_2,c_3)$ | a [multinomial coefficient](https://en.wikipedia.org/wiki/Multinomial_theorem#Multinomial_coefficients) |
| 778 | integers in $[0, M]$, one decimal place | the digit at that place | a closed-form digit histogram |

**452 (Long Products)** counts $n$-tuples whose product is at most $m$. Grouping tuples by
product turns the count into $\sum_{k \le m} d_n(k)$, and $d_n$ is multiplicative, with
$d_n(p^e) = \binom{n+e-1}{e}$ depending only on the exponent. The aggregation then happens a
second and third time inside the [Min_25 sieve](/topics/technique/min-25-sieve) that sums it:
every prime contributes the same value $n$, so all primes up to $x$ collapse into the single
term $n\,\pi(x)$; and $\lfloor m/i \rfloor$ takes only $O(\sqrt m)$ distinct values
([quotient blocking](/topics/technique/quotient-blocking)), so the prime counts are tabulated
once per floor value rather than once per integer. Min_25 is, in effect, aggregation by value
applied recursively — group by smallest prime factor, then by exponent, then by quotient.

**698 (123 Numbers)** asks for the $n$-th string over $\{1,2,3\}$ whose digit counts are
themselves such numbers. Membership depends only on the multiset of digits, never their
order, so a length-$L$ block is a sum over at most $13^2$ admissible count triples of
$\binom{L}{c_1,c_2,c_3}$. The same table, conditioned on a prefix's used counts, drives the
[unranking](/topics/technique/unranking): one count per class instead of $3^L$ strings.

**778 (Freshman's Product)** sums a carry-free digitwise product over $(M+1)^R$ sequences.
Each decimal place is independent, and at one place an integer is nothing but its digit — so
$M+1$ integers become a ten-entry histogram, and the distribution of the $R$-fold product is
that histogram's $R$-th [convolution](/topics/technique/convolution) power over the monoid
$(\mathbb{Z}/10, \times)$, taken by squaring. The instance count is a number with a million
digits; the class count is ten.

**675 ($2^{\omega(n)}$)** is the subtler case, because the aggregation is over the *work*
rather than over the answer. Building each step multiplier $S(i!)/S((i-1)!)$ prime by prime
means one pass per prime — $664\,579$ of them. But for a prime $p > \sqrt n$ the update at its
$k$-th multiple is $(2k+1)/(2k-1)$, a function of $k$ alone. So the large primes are grouped
by $k$: one vectorised update per value of $k$ covers every prime at once, and only a few
thousand small primes keep individual passes. It sits next to
[update only what changes](/topics/takeaway/update-only-what-changes), which supplies the
incremental product the multipliers feed.

## How to reason about it

**Ask what the summand actually reads.** The tell is a summand that ignores most of its
input: a product that only looks at one digit, a predicate that only looks at counts, an
update that only looks at an exponent. Write down the smallest value that determines the
contribution; that is $\kappa$. Its range is the size of the table, and the size of the table
is the new running time.

**The count is the hard part.** Aggregation is free only if $|\kappa^{-1}(k)|$ has a formula —
a binomial, a multinomial, a periodic digit count, $\pi(x)$. If the only way to count a class
is to walk it, nothing has been saved. This is where the takeaway meets
[closed-form over iteration](/topics/takeaway/closed-form-over-iteration).

**Classes compose.** Independent coordinates give a product of small tables (778's places,
452's primes), and an associative combining rule lets a table be raised to a power by
squaring rather than combined $R$ times. Associativity is all that is needed — 778's monoid
has zero divisors and no inverses, and squaring still works.

**Watch for classes that are only *almost* uniform.** In 675 the grouping holds only for
primes above $\sqrt n$, where every multiple has valuation exactly 1; an early draft batched
by a threshold that fell below $\sqrt n$ for small inputs and silently mixed in primes with
higher powers. The general lesson, shared with
[split inputs into behaviour classes](/topics/takeaway/split-inputs-into-behaviour-classes):
state the invariant that makes a class a class, and check that the boundary enforces it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0452](/solutions/0452/) — Long Products
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0698](/solutions/0698/) — 123 Numbers
- ● [0778](/solutions/0778/) — Freshman's Product

<!-- /problems -->
