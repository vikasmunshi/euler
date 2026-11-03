<!-- tags: [aggregate-by-value] -->
<!-- status: final 2026-11-03T12:39Z -->
# Aggregate by value, not by instance

When a problem says "for every tuple", "for every sequence" or "for every string", the
instances are usually astronomically many — $(M+1)^R$ sequences, $3^{38}$ digit strings,
$10^9$-fold products — but the quantity being summed rarely depends on the instance itself.
It depends on some small *value* the instance carries: a digit, a digit-count triple, a digit
sum, a digit set, a gcd, a product, a prime's exponent. Once I can name that value, the move is
always the same: build
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
from a formula, or from a DP over the *structure* of the instances (their digits, their runs),
rather than a pass over the instances themselves.

The problems use a different class map each:

| Problem | Instances | Class $\kappa$ | Size of a class |
|---|---|---|---|
| 452 | $n$-tuples with product $\le m$ | the product $k$ | $d_n(k)$, via [stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics)) per prime |
| 675 | primes $p$ updating $i!$ | the multiple index $k$ (for $p > \sqrt n$) | how many such primes have a $k$-th multiple |
| 698 | digit strings of length $L$ | the digit-count triple $(c_1,c_2,c_3)$ | a [multinomial coefficient](https://en.wikipedia.org/wiki/Multinomial_theorem#Multinomial_coefficients) |
| 778 | integers in $[0, M]$, one decimal place | the digit at that place | a closed-form digit histogram |
| 776 | integers $n \le N$ | the digit sum $s$ | count *and* sum of the class, by [digit DP](/topics/technique/digit-dp) |
| 612 | pairs of integers below $10^{18}$ | each one's digit set (a 10-bit mask) | digit DP, then a [subset-sum transform](/topics/technique/sum-over-subsets-transform) |
| 309 | pairs of Pythagorean triples | the shared leg $w$ | the triples carrying that leg |
| 625 | pairs $(i, j)$ under $\gcd$ | the gcd $d$, then $\lfloor N/k \rfloor$ | $\varphi(j/d)$, then a [totient summatory](/topics/technique/totient-summatory-recursion) difference |
| 754 | factors of a double product | the quotient $\lfloor N/d \rfloor$ | a Mertens difference — as an *exponent* |
| 341 | positions of the Golomb sequence | the value held there | the sequence's own terms |

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

## Beyond the plain count

The later problems stretch the identity above in five directions. Each one changes what a
table entry has to hold, or what is done with it.

**Carry a sum, not just a count (776).** In $\sum_{n \le N} n / d(n)$ the denominator, the
digit sum, has at most 171 values, but the numerator is the instance itself, so knowing
$|\kappa^{-1}(s)|$ is not enough. What the regrouping needs is $T(s) = \sum_{d(n)=s} n$, the
*first moment* of each class. That is cheap because the instance enters linearly: appending a
digit $d$ to $c$ prefixes whose values total $t$ gives a total of $10t + dc$. So each digit-DP
state holds a (count, sum) pair, and the table yields $\sum_s T(s)/s$. The rule generalises.
If the summand is $g(\kappa(x))\cdot h(x)$ with $h$ linear (or polynomial) in the instance,
I keep the moments of $h$ per class, alongside the count.

**Pairs between classes multiply (612, 309).** When the target is a sum over *pairs*, grouping
both sides gives $\sum_{S,T} c_S\,c_T\,[\text{pred}(S,T)]$. In 612, two numbers are "friends"
when their digit sets meet, so $10^{36}$ pairs collapse onto $1024^2$ pairs of masks. Even that
double sum is avoidable. It is easier to
[count the complement](/topics/takeaway/count-the-complement), the disjoint pairs, and
"disjoint from $S$" means "a subset of $\overline S$". A
[zeta transform](/topics/technique/sum-over-subsets-transform) then gives every subset total
in $10 \cdot 1024$ steps. When the predicate between classes has structure of its own, I
aggregate the class table a second time.
In 309 the class does not decide the answer; it decides *who can pair*. Two ladders can cross
only if their [Pythagorean triples](/topics/domain/pythagorean-triple) share the street width as
a leg. So I bucket the two million triples by leg (a
[hash table](/topics/technique/hash-table) in Python, a counting-sort layout in C) and test
pairs only inside a bucket. That costs $\sum_w d_w^2$, where $d_w$ is the bucket size, instead
of the square of the total. This is a database join under another name. Aggregation here
narrows the search rather than replacing it.

**The class can be a divisor (625).** For $\sum_{i \le j \le N} \gcd(i,j)$ the summand *is*
the class. Group the $i$ by the value $d = \gcd(i,j)$: the class has $\varphi(j/d)$ members, so
the inner sum becomes a [Dirichlet convolution](/topics/domain/dirichlet-convolution). Swapping
the order gives $\sum_k \varphi(k)\,T(\lfloor N/k \rfloor)$, which is grouped again by the
quotient, as in 452. Two layers of aggregation by value, one after the other.

**In a product, the multiplicity becomes an exponent (754).** A product of Gauss factorials,
after [Möbius inversion](/topics/technique/mobius-inversion-formula), is
$\prod_d X_{\lfloor N/d \rfloor}^{\mu(d)}$. Grouping the $d$ that share a quotient $M$ gives
$X_M^{\sum \mu(d)}$, so the class weight is a *signed* count, a difference of the
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function), and it lands in the
exponent. Modulo a prime, the exponent is then
[reduced modulo the group order](/topics/takeaway/reduce-exponent-modulo-group-order).
Products are where this takeaway pays the most, because $c$ repeated multiplications become
one $O(\log c)$ power. One practical point: I keep the $\mu = +1$ and $\mu = -1$ running
products apart, so a block needs one modular inverse, not one per element.

**A sequence that is its own histogram (341).** The
[Golomb sequence](/topics/domain/golomb-sequence) holds each value $v$ in exactly $G(v)$
places. So it *is* a multiplicity table, its own
[run-length encoding](/topics/technique/run-length-encoding). Grouping positions by value turns
"where is position $n$?" into a prefix sum over values, $S(v) = \sum_{t \le v} G(t)$. Then I
apply the same grouping to that table: values sharing $G(G(n))$, then blocks sharing $G(i)$.
Each step shrinks the scale like a root, from $10^{18}$ positions to about $10^7$ values to
about $2.6 \times 10^4$ blocks. On a block, the inner sums have closed forms. Aggregation by
value, applied to its own output, is what takes the problem from impossible to milliseconds.

## How to reason about it

**Ask what the summand actually reads.** The tell is a summand that ignores most of its
input: a product that only looks at one digit, a predicate that only looks at counts, an
update that only looks at an exponent. Write down the smallest value that determines the
contribution; that is $\kappa$. Its range is the size of the table, and the size of the table
is the new running time.

**The count is the hard part.** Aggregation pays only if $|\kappa^{-1}(k)|$ can be had
without walking the class. That can be a formula: a binomial, a multinomial, a periodic digit
count, $\pi(x)$, $\varphi$. It can be a DP over the instances' *shape*: 612 and 776 build their
class tables digit by digit, in time polynomial in the number of digits. Or it can be a
self-generating sequence, as in 341. If the only way to count a class is to list its members,
nothing has been saved. This is where the takeaway meets
[closed-form over iteration](/topics/takeaway/closed-form-over-iteration).

**Decide what an entry must hold before building the table.** A count is enough only if the
summand is a function of the class alone. If it also reads the instance linearly, keep a sum
per class (776). If the target is a product, the count goes into the exponent (754). If the
target ranges over pairs, the table is used twice, and the pair predicate may need a transform
of its own (612).

**Classes compose.** Independent coordinates give a product of small tables (778's places,
452's primes), and an associative combining rule lets a table be raised to a power by
squaring rather than combined $R$ times. Associativity is all that is needed — 778's monoid
has zero divisors and no inverses, and squaring still works. Classes also nest. 625 groups
by gcd and then by quotient, and 341 groups the output of one grouping again, three levels deep.

**Watch for classes that are only *almost* uniform.** In 675 the grouping holds only for
primes above $\sqrt n$, where every multiple has valuation exactly 1; an early draft batched
by a threshold that fell below $\sqrt n$ for small inputs and silently mixed in primes with
higher powers. The general lesson, shared with
[split inputs into behaviour classes](/topics/takeaway/split-inputs-into-behaviour-classes):
state the invariant that makes a class a class, and check that the boundary enforces it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0309](/solutions/0309/) — Integer Ladders
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ● [0452](/solutions/0452/) — Long Products
- ● [0612](/solutions/0612/) — Friend Numbers
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0698](/solutions/0698/) — 123 Numbers
- ● [0749](/solutions/0749/) — Near Power Sums
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0778](/solutions/0778/) — Freshman's Product

<!-- /problems -->
