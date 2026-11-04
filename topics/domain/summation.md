<!-- tags: [summation] -->
<!-- status: final -->
# Summation

[Summation](https://en.wikipedia.org/wiki/Summation) is the most deceptive domain tag in the
collection. Adding numbers up is the first thing anyone learns to program, and `sum(...)` is one
call — so a statement built around a $\sum$ looks like the easy kind. It almost never is. What the
tag actually marks is a problem whose answer is a
[summatory function](https://en.wikipedia.org/wiki/Summatory_function) $S(N) = \sum_{n=1}^{N} f(n)$
evaluated at an $N$ nobody can iterate to: $10^{12}$, $10^{15}$, $10^{18}$. The loop is written for
you in the statement. The work is finding out what the loop *equals*.

## Two jobs wear the same tag

It is worth separating them before anything else, because they want opposite instincts.

In the first kind, the sum is the **scoring step** at the end of a harder selection. Problem 10
wants the sum of the primes below two million — the summation is a `+=` inside the
[sieve](/topics/technique/sieve-of-eratosthenes); the problem is the sieve. Problem 23 sums the
integers not expressible as two abundant numbers, problem 125 sums the palindromes that are also
runs of consecutive squares. Here the range is small enough to walk, the tag is descriptive rather
than prescriptive, and all the difficulty sits in deciding *which* terms qualify.

In the second kind — the large majority above, and nearly everything from problem 297 on — the range is the
whole difficulty. $f$ is often cheap to evaluate at any single point and completely out of reach to
evaluate $10^{15}$ times. Problem 401 wants $\sum_{n \le 10^{15}} \sigma_2(n)$; problem 918 wants
$\sum_{n \le 10^{12}} a_n$; problem 760 wants a double sum out to $10^{18}$. Nothing about the
terms is hard. The count is.

Check the bound first, always. It tells you which problem you are in, and roughly how much
structure you are going to have to find: at $10^6$ you may loop, at $10^{12}$ you need something
sublinear, at $10^{18}$ you need something logarithmic or closed. And when the bound is $\infty$, it
stops being a cost and becomes a precision target, which has its own section below.

## Five ways to not iterate

These are the moves, in rough order of how much they buy.

### Close the form

The best outcome: the sum has an algebraic identity and the loop disappears entirely. The
[Faulhaber](https://en.wikipedia.org/wiki/Faulhaber%27s_formula) family —
$\sum k = n(n{+}1)/2$, $\sum k^2 = n(n{+}1)(2n{+}1)/6$, and their siblings — covers more statements
than you would guess, because so many objects are indexed by a running integer. Problem 6 is the
whole idea in one line:

```python
return str((n * (n + 1) // 2) ** 2 - (2 * n + 1) * (n + 1) * n // 6)
```

Problem 28 is the same move one step less obviously: the spiral's diagonal entries, taken ring by
ring, are four terms in $s$ for each odd side $s$, and summing those over $s$ collapses an
$O(N^2)$ grid construction into one polynomial evaluated in $O(1)$. Both are the
[prefer a closed form over iteration](/topics/takeaway/closed-form-over-iteration) takeaway in its
purest form, and both are found by
[reducing algebraically before coding](/topics/takeaway/reduce-before-coding) rather than by
optimising a loop that already exists.

The closed form is not always hiding in the statement's algebra. Problem 340 defines a
McCarthy-91-style function by four nested self-calls and asks for its sum over some $10^{17}$
arguments; read literally it is a recursion you cannot even evaluate once. A memoised brute force on
small parameters shows the shape instead: cut the range into blocks of width $a$ counted down from
the threshold, and $F$ is the identity plus a constant plus a fixed step per block. Once that is
proved by induction on the block, the sum is Gauss's triangular number twice over — once for the
identity, once for the block indices — plus a correction for the one partial block. Tabulate
small cases, guess the piecewise-linear shape, prove it, then sum the shape.

Problem 555 is the same function family one level up. It sums the *fixed points* of a generalised
McCarthy function over every parameter pair $(k, s)$ up to $p$. Tabulating again gives the shape:
the outputs cycle through a window of width $d = k - s$, and the window is all fixed points exactly
when $d \mid s$. That leaves a double sum over $d$ and $s = jd$, about $p \ln p$ pairs, each an
arithmetic progression. The last step is the one to remember. **Index the outer sum by the
parameter that makes the inner one a polynomial.** For a fixed gap $d$, the sum over $j$ is a
quadratic in $J = \lfloor p/d \rfloor - 1$, so each $d$ costs $O(1)$ and the total is $O(p)$.
Before you write the inner loop, check whether it has a closed form.

Sometimes the *term* has to close before the sum can. Problem 479 sums powers of a product built
from the three roots of a cubic, real and complex, over an $n \times n$ grid of $(k, p)$. You could
find the roots numerically, but the statement gives the game away when it remarks that the sum is
always an integer: complex ingredients with an integer result usually means they cancel. Here they
do. The product is symmetric in the roots, so
[Vieta's formulas](/topics/technique/vietas-formulas) rewrite it from the cubic's coefficients and
it collapses to a polynomial in $k$. Once the base is a plain integer, the sum over $p$ is a
[geometric series](/topics/technique/geometric-series), and the $n^2$ grid becomes $n$ modular
exponentiations. A term you cannot compute can still have a sum you can, so simplify the summand
before you think about the range.

Periodicity is a closed form in disguise. Problem 506 cuts a period-6 digit stream into terms
$v_n$ whose digit sums are $1, 2, 3, \dots$. Since every six consecutive digits sum to 15, the term
$v_{n+15}$ starts at the same phase as $v_n$ and is $v_n$ with one full period appended:
$v_{n+15} = 10^6 v_n + Q_{n \bmod 15}$. That is an affine recurrence *within each residue class*.
Unroll it and each class is a [geometric series](/topics/technique/geometric-series),
so a sum to $10^{14}$ costs fifteen modular exponentiations. If the terms
[repeat their structure](/topics/domain/periodic-sequence)
with some period, split the sum by residue class and see what each class does on its own.

Watch the integer arithmetic when you do it. `//2` and `//6` in those formulas are exact only
because the numerator is provably divisible; under a modulus they are not divisions at all but
multiplications by a [modular inverse](/topics/technique/modular-multiplicative-inverse-application),
and in C the products overflow 64 bits long before $N$ does.

### Telescope

Sometimes the sum does not have a closed form but *collapses* anyway, because consecutive terms
cancel. [Telescoping](/topics/technique/telescoping-series) is worth actively looking for whenever
$f$ is defined by a [recurrence](/topics/domain/recurrence-relation): split the sum by the cases of
the recurrence, substitute, and see what survives.

Problem 918 is the showcase. Its sequence branches on parity of the index, so splitting
$S(N)$ into even and odd indices and substituting both cases reorganises the trillion-term sum
into a relation among $S$ at roughly $N/2$ — and the cancellation is total: the entire sum equals
a constant minus a *single term* of the sequence. What is left is evaluating $a_m$ at one large
$m$, which the sequence's binary structure does in about forty steps. A trillion additions became
forty multiplications, and no part of that came from writing faster code.

The cancellation will not always be total, and problem 463 shows what to do when it is not. Its
recurrence (it turns out to be binary reversal) relates $f$ at $n$ to $f$ near $n/2$ and $n/4$.
Splitting $S(n)$ by parity works for the even indices, which give back $S(\lfloor n/2 \rfloor)$.
The odd indices give a new sum, $O(m) = \sum_k f(2k+1)$. Split that by residue mod 4 and it
comes back as a linear combination of $S$ and $O$ at half the argument. One sum did not close
under halving, but the *pair* does. With memoisation, the mutual recursion visits about a hundred
states for $n \approx 4.5 \times 10^{17}$. When a substitution leaves a sum you cannot express,
add that sum as a second unknown and substitute again. The state you recur on is a small vector of
sums.

Problem 539 shows that the second unknown need not be a sum. Its survivor $P(n)$ depends only on
$\lfloor n/2 \rfloor$, so $2m$ and $2m{+}1$ contribute the same term and the sum
[folds onto half its range](/topics/takeaway/sum-the-recurrence-over-residue-classes) with
multiplicity two. All that is left over is the one unpaired term at the top edge when $n$ is even,
so the state is the pair (term, sum). Each level has exactly one argument, so this is a chain of
sixty steps rather than a tree, and it needs no memo.

### Swap the order of summation

The single most productive technique in this whole topic, and the one to reach for by reflex when
$f(n)$ is itself defined as a sum — a divisor sum, a digit sum, a count of something. A double sum
can be evaluated in either order, so stop summing over $n$ and start summing over the *inner*
index, asking how many $n$ each inner value serves:

$$\sum_{n \le N} \sum_{d \mid n} g(d) \;=\; \sum_{d \le N} g(d) \left\lfloor \frac{N}{d} \right\rfloor$$

The left side needs the divisors of every $n$; the right side is one pass over $d$. That identity,
or a variant of it, is the spine of the divisor- and totient-summatory problems here — 401, 432,
439, 448, 512 — and of the [Dirichlet convolution](/topics/domain/dirichlet-convolution) machinery
that generalises it. The shape of the loop is unremarkable:

```python
total = sum(g(d) * (n // d) for d in range(1, n + 1))
```

and the second half of the trick is that $\lfloor N/d \rfloor$ takes only $O(\sqrt N)$ distinct
values. Group the $d$ sharing a quotient into a block, sum $g$ over the block in closed form, and
an $O(N)$ pass becomes $O(\sqrt N)$ — which is what turns $10^{15}$ from impossible into a few
seconds. Recursing on the same identity (a summatory function of a
[multiplicative function](/topics/domain/multiplicative-function) expressed in terms of itself at
$N/d$) takes it further still.

Problem 512 shows both halves earning their keep. Its $f(n)$ is an alternating sum of
$\varphi(n^i)$ modulo $n+1$, and it is a sum only in appearance: $\varphi(n^i) = n^{i-1}\varphi(n)$
and $n \equiv -1$, so the terms cancel in pairs and $f(n)$ is $\varphi(n)$ for odd $n$, zero for
even. What remains is the summatory totient restricted to odd arguments. The unrestricted
$\Phi(N)$ falls to the recursion above,
$\Phi(v) = v(v+1)/2 - \sum_{d \ge 2} \Phi(\lfloor v/d \rfloor)$, blocked on quotients and seeded
by a sieve below $N^{2/3}$. The odd restriction then
costs almost nothing: how $\varphi$ treats a factor of two peels the even terms off as
$\sum_k \Phi(\lfloor N/2^k \rfloor)$, and every one of those arguments is a floor quotient the
recursion has already computed. Choose restrictions that land on values you already have.

It matters which slot of the floor is moving. In $\lfloor N/d \rfloor$ the denominator runs, the
steps have uneven widths, and blocking is the best you can do. Problem 688 is the other case. Its
$f(n, k)$ works out to a single [floor](/topics/domain/floor-function) with $n$ in the numerator
and the pile count $k$ in the denominator, so
[swapping the sums](/topics/technique/interchange-of-summation) puts $k$ outside and leaves the
numerator running through a prefix. That is a staircase with equal treads, and it needs no blocks:

$$\sum_{j=0}^{L-1} \left\lfloor \frac{j}{k} \right\rfloor \;=\; k\binom{q}{2} + rq, \qquad L = qk + r,\quad 0 \le r < k$$

The outer range is short as well, because $k$ piles of different sizes need about $k^2/2$ plates,
so only $k \lesssim \sqrt{2N}$ ever contributes. A sum over $10^{16}$ values of $n$ becomes
$O(\sqrt N)$ constant-time terms. With a general slope in place of $1/k$, the same kind of sum
still falls, to the [floor-sum algorithm](/topics/technique/floor-sum-algorithm).

The same reflex has a non-arithmetic form: **count contributions instead of objects**. Problem 760
sums a bitwise expression over a triangular range to $10^{18}$; you do not sum over pairs, you sum
over *bit positions*, counting how many pairs set each bit. Whenever the terms decompose into
independent small pieces, invert the loop so the outer index runs over pieces — there are sixty of
those and $10^{18}$ of the other.

Taken to its limit, the swap removes the summand altogether. Problem 804's $g(n)$ counts the integer
pairs that a [quadratic form](/topics/domain/quadratic-form) sends to $n$. It is tempting to compute
$g$, which has a divisor-sum formula because the form's discriminant has class number one. But
every pair with a value in $[1, N]$ is counted exactly once across the whole sum, so
[a sum of representation counts is a point count](/topics/takeaway/sum-of-representations-is-a-point-count):
$T(N)$ is the number of [lattice points](/topics/technique/lattice-point) in an ellipse, a relative
of the [Gauss circle problem](/topics/domain/gauss-circle-problem). Counted row by row, each row
costs one [integer square root](/topics/technique/integer-square-root), and $10^{16}$ terms become
$O(\sqrt N)$ rows. Whenever $f(n)$ counts the solutions of "something $= n$", the sum counts the
solutions of "something $\le N$", and that is usually a simpler object than $f$.

A related move groups the terms by a statistic that takes **few values**. Problem 776 sums
$n / d(n)$, where $d(n)$ is the digit sum, out to about $10^{18}$. That denominator is at most
171, so the sum is $\sum_s T(s)/s$, where $T(s)$ adds up the $n \le N$ with digit sum $s$. Those
171 totals come from a [digit DP](/topics/technique/digit-dp). A digit DP usually counts. Here it
also has to sum, which works because appending a digit is linear: $c$ prefixes with total $t$
become, after digit $d$, $c$ prefixes with total $10t + dc$. So each state carries a
(count, sum) pair, and a DP that counts can sum at no extra cost. Problem 684 groups the same way
from the other side. The smallest number with digit sum $n = 9q + r$ is $(r{+}1)10^q - 1$, so
each run of nine consecutive $n$ shares a $q$, and the runs form a geometric series in $10^q$.

A statistic with many values can still be grouped if a sieve computes the groups. Problem 521 sums
the smallest prime factor out to $10^{12}$. A prime is its own smallest factor and a composite's is
at most $\sqrt N$, so the sum splits into the sum of the primes plus, for each prime $p \le \sqrt N$,
$p$ times the number of composites whose smallest factor is $p$. That number is exactly what a sieve
strikes out at step $p$. Quotient blocking alone cannot do this, because it needs a closed form for
$g$ over a block and nothing closes a sum over primes. The
[Lucy_Hedgehog sieve](/topics/technique/lucy-hedgehog-sieve) runs the sieve itself, on the
$O(\sqrt N)$ floor quotients only, for about $N^{3/4}$ work. Its tables hold each group's survivor
count at the moment that group is needed, so the answer is read from the sieve's intermediate
states rather than from its result. A second table
[carried alongside the count](/topics/takeaway/carry-sums-alongside-counts) supplies the prime sum
for the price of one more array.

Problem 739 counts contributions through a whole *process*. It applies "drop the first term, take
prefix sums" to a sequence until one term is left. That operation is linear, so the survivor is
a fixed weighted sum of the starting terms, and each weight counts the paths a unit can take from
its starting position to the apex. The paths are monotone lattice paths that may not cross a
diagonal, so the weights are ballot numbers (the all-ones example ending on a Catalan number gives
it away). An $n^2$ triangle of repeated summations becomes a single $O(n)$ sum of binomial-weighted
terms. Under a prime modulus, writing those binomials as running prefix and suffix products means
only one modular inverse is needed, at the very end.

### Prefix sums

For sums over *many contiguous ranges* of one fixed sequence, precompute
$P_i = \sum_{k<i} x_k$ once and every range sum becomes one subtraction, $P_j - P_i$. This is the
cheapest $O(N)$-to-$O(1)$ conversion in programming and it is
[precompute once, reuse](/topics/takeaway/precompute-once-reuse) in miniature. Problem 50 searches
for the longest run of consecutive primes summing to a prime, and the whole search rests on it:

```python
prime_sums: list[int] = [0] + list(itertools.accumulate(primes_tuple))
...
possible_prime = prime_sums[i] - prime_sums[j]
```

The two-dimensional version carries problem 150's sub-triangle search — a row-wise prefix table
makes any sub-triangle's sum a handful of lookups instead of a re-add. And prefix sums have a
second life modulo $m$: a range sum is divisible by $m$ exactly when its two endpoints share a
prefix residue, so counting qualifying ranges becomes tallying residues in a
[hash table](/topics/technique/hash-table) — one pass instead of a quadratic scan over pairs. That
is the hinge of problem 326.

### Descend the structure

When $f$ is defined by a [self-similar](/topics/domain/self-similarity) process rather than a
formula, the sum decomposes the same way the process does. The shape is always the same: tabulate
the sum over each *whole* block the process builds, then compute $S(N)$ by walking down to $N$,
adding every whole block that lies to its left and recursing only into the one block that $N$
splits. The walk is as long as the structure is deep — logarithmic — however large $N$ is.

Problem 297 is the cleanest instance. $z(n)$ counts the terms in the
[Zeckendorf representation](/topics/domain/zeckendorfs-theorem) of $n$, summed below $10^{17}$.
Every $n$ in $[F_i, F_{i+1})$ is $F_i$ plus a remainder below $F_{i-1}$, so $z(n) = 1 + z(n - F_i)$,
and the whole-block sums $T_i = \sum_{n < F_i} z(n)$ obey a recurrence of their own,
$T_{i+1} = T_i + F_{i-1} + T_{i-1}$. A general limit falls out the same way:
$S(N) = T_i + (N - F_i) + S(N - F_i)$ for the largest $F_i \le N$. Unroll that and the descent *is*
the greedy Zeckendorf decomposition of $N$ — about eighty steps. It is digit-by-digit summation, in
a number system whose digits happen to be Fibonacci numbers.

Problem 943 shows what happens when the blocks are not all alike. Its sequence is a two-symbol
[Kolakoski](/topics/domain/kolakoski-sequence)-style sequence that is its own run-length encoding,
and the task is a prefix sum $T(a, b, N)$ at $N \approx 2 \times 10^{13}$ for some fifty thousand
$(a, b)$ pairs. Read backwards, each element is the parent of the run it describes, so the prefix is
the leaf level of a shallow derivation tree, and $T$ is one root-to-leaf descent adding up the
subtrees to the left of leaf $N$. The catch is that a subtree is *not* fixed by its root's value:
which symbol its descendants carry depends on the parity of their positions, which depends on
everything to their left. The memo key has to carry that parity on every level, a bitmask beside
the value and height — the [memo key is the full state](/topics/takeaway/memo-key-is-the-full-state),
and a key without the mask returns plausible, wrong sums. With the right key, $10^{13}$ leaves
collapse to a few million distinct subtree shapes at worst. And when a node has hundreds of
identical children, the sequence of their masks repeats after a short prefix, so
[cycle detection](/topics/technique/cycle-detection) answers "the sum of the first $k$ children" by
counting whole periods instead of walking them.

Problem 341 uses the same self-description to the opposite effect. There, the prefix sum is not
the answer. It is the **inverse** of the answer. In the [Golomb sequence](/topics/domain/golomb-sequence),
$S(v) = \sum_{t \le v} G(t)$ is the last position holding $v$, so finding $G(n)$ means finding the
smallest $v$ with $S(v) \ge n$. Going one level higher, $T(i) = \sum_{t \le i} t\,G(t)$ inverts
$G(G(n))$. Each inversion turns a question about positions near $10^{18}$ into one about values
far smaller. After the third inversion, the tables hold about $2.6 \times 10^4$ entries, and
inside each block $T$ is a quadratic in $i$, so the query solves it with an integer square root.
When a sequence is its own [run-length encoding](/topics/technique/run-length-encoding), its prefix
sums are where the values change. Binary-search the sums instead of generating the terms.

Problems 884 and 672 sum a step-count that is constant on long blocks and recurse on the sub-range
each block leaves behind. Problem 374 has blocks that are not constant but have closed forms. The
maximum-product partition of $n$ into distinct parts is a run $\{2, \dots, k{+}2\}$ with one value
removed, so $n$ falls into blocks of length $k + 2$. Each whole block sums in closed form, and
there are only $\sqrt{2N}$ blocks below $N$. The cost is one pass over the blocks, not one
over $n$. The general instruction is the same one that governs
[recurrence relations](/topics/domain/recurrence-relation): recur on the cheap shadow of the
structure — a block, a bit, a subtree shape — never on the elements themselves.

Two more escape hatches worth naming. When the sum ranges over something random,
**linearity of expectation** lets you sum the expected contribution of each term independently,
without ever describing the joint distribution — that is what makes problem 756's approximation
error tractable. And when the constraint region is an intersection of half-spaces, as in problem
968's five-dimensional sum,
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) turns one impossible sum
into a signed combination of easy ones.

## The modulus is not decoration

A third of the problems here ask for the answer modulo something, and that is a tell, not a
formality: it says the true sum has millions of digits, so the intended method never materialises
it. Take the modulus seriously from the first line of code rather than applying it at the end —
and mind what it changes:

- **Division becomes inversion.** `n * (n + 1) // 2` is invalid under a modulus. Multiply by the
  [modular inverse](/topics/technique/modular-multiplicative-inverse-application) of 2, and note
  that this needs the modulus to be coprime to the divisor — which is why some statements name a
  prime modulus and others (problem 830's $83^3 89^3 97^3$) deliberately do not. A
  "last nine digits" modulus is $10^9$, which is even, so 2 has no inverse at all; problem 340's
  triangular numbers survive by halving whichever factor is even *before* reducing. What has to
  be coprime is the divisor, not the modulus: problem 506's $123454321 = 41^2 \cdot 271^2$ is far
  from prime, but the $10^6 - 1$ its geometric series divides by shares no factor with it.
- **Carry the integer, not the fraction.** Problem 374's block sums involve harmonic numbers
  $H_j$, and keeping $H_j$ as a residue would cost a modular inverse of every $j$. The product
  $A_j = j!\,H_j$ is an integer (a [Stirling number](https://en.wikipedia.org/wiki/Stirling_numbers_of_the_first_kind)
  of the first kind) and satisfies $A_j = j A_{j-1} + (j-1)!$. So the loop carries $j!$ and $A_j$
  and does no division at all. When a recurrence produces fractions, multiply them by whatever
  denominator makes them integers, and carry that product instead.
- **Exponents reduce modulo $p - 1$.** Problem 684 needs $10^q$ where $q$ itself has $10^{17}$
  digits. By [Fermat's little theorem](/topics/technique/fermats-little-theorem-application),
  only $q \bmod (p-1)$ matters in the exponent, while $q \bmod p$ matters in the linear terms. So
  two residues of the same index have to be tracked. Since $q = (f - r)/9$, the Fibonacci values
  $f$ are carried modulo $9p$ and $9(p-1)$. The extra factor of nine leaves room to divide by 9
  exactly, after reduction.
- **Products overflow before sums do.** Two residues below $10^9$ multiply to nearly $10^{18}$,
  which fits `int64` — barely. Add anything, or use a larger modulus, and it does not.
  [Watch the integer width](/topics/takeaway/watch-integer-width): in C this is what
  [`__int128`](/topics/technique/int128) is for, while Python's
  [arbitrary precision](/topics/technique/arbitrary-precision-arithmetic) hides the issue until
  you port the file.
- **The modulus does not protect the intermediates.** Problem 943 reduces its final total mod
  $2233222333$, but its memoised subtree counts and sums are exact quantities that get compared
  against $N$ and multiplied by period counts — they cannot be reduced, and a deep subtree's leaf
  sum outgrows 64 bits. Problem 297 asks for no modulus at all, and its $10^{18}$ variant already
  passes $2^{64}$. Both C ports carry those values in `__int128`.
- **Signs.** A telescoped or alternating sum produces negative intermediates; C's `%` follows the
  sign of the dividend, Python's does not. Normalise once, at a single choke point.

The converse case is worth its own warning. When a problem wants the sum *exactly* — problem 13's
sum of fifty 50-digit numbers, or problem 48's self-powers — the modulus is a red herring you may
be tempted to invent. Problem 48 genuinely only needs the last ten digits, so a modulus is right;
problem 13 needs the leading ones, so it is wrong. Read which end of the number is being asked for.
The leading end has a trap of its own when the terms are fractions. Problem 776 wants thirteen
significant digits of a sum of $10^{18}$ rationals. A floating-point accumulation can round the
wrong way when the fourteenth digit is near a tie. The 171 grouped totals are few enough to add as
an exact rational, which is then rounded once.

## When the sum has no last term

Everything above assumes a finite $N$ and an exact answer. Problem 779 has neither: it wants a sum
over all $K$ of limiting averages over all integers, rounded to twelve decimal places. Each infinity
has to be removed by a different argument.

The limit of an average is a [natural density](/topics/domain/natural-density) question. Divisibility
by distinct primes is independent in the limit, so the integers with a given smallest prime have a
density, and the average becomes a sum over primes of that density times an
[expected value](/topics/technique/expected-value-application). $N$ is gone. The sum over $K$ then
goes the way of every double sum in this topic, with one difference: finite sums always commute,
but [infinite ones need a licence](/topics/technique/interchange-of-summation). Non-negative terms
grant it (that is [Tonelli's theorem](https://en.wikipedia.org/wiki/Fubini%27s_theorem)), while a
conditionally convergent series can change its value when reordered. Check the signs before you
swap. Summing $K$ first gives a geometric series, which leaves one series over the primes.

That series has to be truncated, and now *you* set the bound. Read the precision as the
specification: prove a bound on the tail, then pick the cutoff that puts the tail below the digits
you need. Leave a margin, because rounding to twelve places can need more than twelve correct
digits, and this answer sits very close to a rounding boundary. For the same reason the additions
themselves matter. Hundreds of thousands of tiny terms added to a total near $0.5$ lose low bits at
every step, so the Python adds them with `math.fsum`, in the spirit of
[compensated summation](/topics/technique/kahan-summation-algorithm), and the C carries `long double`.
Problem 776 could add its terms exactly and round once. Here that is out of reach, so
[numeric where necessary](/topics/takeaway/exact-where-possible-numeric-where-necessary) means
knowing how much error each step adds.

## How to reason about it

A practical order of attack when a statement hands you a $\sum$:

1. **Read the bound and the modulus.** They jointly announce the complexity class you have to
   reach. $N = 10^{18}$ with a mod means logarithmic or closed; $N = 10^{15}$ means $O(\sqrt N)$ is
   probably the target; a small $N$ means the sum is not the problem at all. An infinite bound with
   a stated precision means the target is a proved tail bound.
2. **Write the brute force anyway.** Fifteen lines, correct by construction, and useless at scale —
   but it is your oracle. Every identity below is a claim, and a claim you have checked against
   $S(10)$ and $S(1000)$ is worth far more than one you derived carefully and never tested. The
   given sample values in the statement exist for exactly this. Check against more than the given
   samples when the method has state that the samples might never reach: problem 943's descent was
   held against direct generation of the sequence on two thousand random $(a, b, N)$, which is what
   catches an under-specified memo key. At full scale, where no oracle reaches, compare with
   something cruder: problem 804's ellipse area predicts $T(N)$ to leading order, and problem 779's
   series was held against a direct average over the first $3 \times 10^7$ integers.
3. **Look at $f$'s definition, not at the loop.** If $f$ is built from objects you cannot compute,
   simplify the term first. If $f$ is itself a sum, swap the order. If $f$ counts solutions, count
   them all at once. If $f$ obeys a recurrence, try to telescope. If $f$ is defined digit-wise or
   bit-wise, sum over digits.
   If $f$ is piecewise-constant on long blocks, or has a closed form on each block, sum over
   blocks. If the terms are periodic, split by residue class. If part of $f$ takes only a few
   values, group by that part.
4. **Then, and only then, reach for machinery.** Blocking on $\lfloor N/d \rfloor$,
   [matrix exponentiation](/topics/technique/matrix-exponentiation),
   [dynamic programming](/topics/technique/dynamic-programming) over digits — all of these are
   worth more once you know the shape of the sum, and all of them are wasted effort applied to a
   sum you have not reduced first.

The recurring failure mode is optimising step 4 without doing step 3: vectorising, or porting to C,
a loop that was never going to finish. No constant factor closes the gap between $10^{6}$ and
$10^{15}$ — that is what
[the algorithm beats the language](/topics/takeaway/algorithm-beats-language) means, and summation
problems are where the collection makes the point most bluntly.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0013](/solutions/0013/) — Large Sum
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0048](/solutions/0048/) — Self Powers
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ○ [0326](/solutions/0326/) — Modulo Summations
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ○ [0375](/solutions/0375/) — Minimum of Subsequences
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ○ [0427](/solutions/0427/) — $n$-sequences
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0433](/solutions/0433/) — Steps in Euclid's Algorithm
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0444](/solutions/0444/) — The Roundtable Lottery
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0471](/solutions/0471/) — Triangle Inscribed in Ellipse
- ● [0479](/solutions/0479/) — Roots on the Rise
- ○ [0489](/solutions/0489/) — Common Factors Between Two Sequences
- ○ [0490](/solutions/0490/) — Jumping Frog
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0534](/solutions/0534/) — Weak Queens
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ● [0539](/solutions/0539/) — Odd Elimination
- ○ [0542](/solutions/0542/) — Geometric Progression with Maximum Sum
- ○ [0543](/solutions/0543/) — Prime-Sum Numbers
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ● [0555](/solutions/0555/) — McCarthy 91 Function
- ○ [0577](/solutions/0577/) — Counting Hexagons
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0672](/solutions/0672/) — One More One
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ● [0688](/solutions/0688/) — Piles of Plates
- ○ [0689](/solutions/0689/) — Binary Series
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0737](/solutions/0737/) — Coin Loops
- ● [0739](/solutions/0739/) — Summation of Summations
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0775](/solutions/0775/) — Saving Paper
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0792](/solutions/0792/) — Too Many Twos
- ○ [0794](/solutions/0794/) — Seventeen Points
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ● [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ○ [0831](/solutions/0831/) — Triple Product
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0884](/solutions/0884/) — Removing Cubes
- ○ [0893](/solutions/0893/) — Matchsticks
- ○ [0905](/solutions/0905/) — Now I Know
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0915](/solutions/0915/) — Giant GCDs
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ○ [0933](/solutions/0933/) — Paper Cutting
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0986](/solutions/0986/) — Another Infinite Game
- ○ [0991](/solutions/0991/) — Fruit Salad

<!-- /problems -->
