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

In the second kind — the large majority above, and everything past problem 300 — the range is the
whole difficulty. $f$ is often cheap to evaluate at any single point and completely out of reach to
evaluate $10^{15}$ times. Problem 401 wants $\sum_{n \le 10^{15}} \sigma_2(n)$; problem 918 wants
$\sum_{n \le 10^{12}} a_n$; problem 760 wants a double sum out to $10^{18}$. Nothing about the
terms is hard. The count is.

Check the bound first, always. It tells you which problem you are in, and roughly how much
structure you are going to have to find: at $10^6$ you may loop, at $10^{12}$ you need something
sublinear, at $10^{18}$ you need something logarithmic or closed.

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

The same reflex has a non-arithmetic form: **count contributions instead of objects**. Problem 760
sums a bitwise expression over a triangular range to $10^{18}$; you do not sum over pairs, you sum
over *bit positions*, counting how many pairs set each bit. Problems 684, 685 and 776 do it with
decimal digits. Whenever the terms decompose into independent small pieces, invert the loop so the
outer index runs over pieces — there are sixty of those and $10^{18}$ of the other.

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

When $f$ is defined by a self-similar process rather than a formula, the sum often decomposes the
same way the process does. Problems 884 and 672 both sum a step-count over an enormous range where
the step count is constant on long blocks — so you sum over blocks, recursing on the sub-range each
block leaves behind. Problem 739 iterates partial summation until one term remains; the answer is a
binomial identity hiding in the triangle. The general instruction is the same one that governs
[recurrence relations](/topics/domain/recurrence-relation): recur on the cheap shadow of the
structure — a block, a bit, a count — never on the elements themselves.

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
  prime modulus and others (problem 830's $83^3 89^3 97^3$) deliberately do not.
- **Products overflow before sums do.** Two residues below $10^9$ multiply to nearly $10^{18}$,
  which fits `int64` — barely. Add anything, or use a larger modulus, and it does not.
  [Watch the integer width](/topics/takeaway/watch-integer-width): in C this is what
  [`__int128`](/topics/technique/int128) is for, while Python's
  [arbitrary precision](/topics/technique/arbitrary-precision-arithmetic) hides the issue until
  you port the file.
- **Signs.** A telescoped or alternating sum produces negative intermediates; C's `%` follows the
  sign of the dividend, Python's does not. Normalise once, at a single choke point.

The converse case is worth its own warning. When a problem wants the sum *exactly* — problem 13's
sum of fifty 50-digit numbers, or problem 48's self-powers — the modulus is a red herring you may
be tempted to invent. Problem 48 genuinely only needs the last ten digits, so a modulus is right;
problem 13 needs the leading ones, so it is wrong. Read which end of the number is being asked for.

## How to reason about it

A practical order of attack when a statement hands you a $\sum$:

1. **Read the bound and the modulus.** They jointly announce the complexity class you have to
   reach. $N = 10^{18}$ with a mod means logarithmic or closed; $N = 10^{15}$ means $O(\sqrt N)$ is
   probably the target; a small $N$ means the sum is not the problem at all.
2. **Write the brute force anyway.** Fifteen lines, correct by construction, and useless at scale —
   but it is your oracle. Every identity below is a claim, and a claim you have checked against
   $S(10)$ and $S(1000)$ is worth far more than one you derived carefully and never tested. The
   given sample values in the statement exist for exactly this.
3. **Look at $f$'s definition, not at the loop.** If $f$ is itself a sum, swap the order. If $f$
   obeys a recurrence, try to telescope. If $f$ is defined digit-wise or bit-wise, sum over digits.
   If $f$ is piecewise-constant on long blocks, sum over blocks.
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
- ○ [0297](/solutions/0297/) — Zeckendorf Representation
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0340](/solutions/0340/) — Crazy Function
- ○ [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ○ [0375](/solutions/0375/) — Minimum of Subsequences
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0390](/solutions/0390/) — Triangles with Non Rational Sides and Integral Area
- ○ [0401](/solutions/0401/) — Sum of Squares of Divisors
- ○ [0427](/solutions/0427/) — $n$-sequences
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0433](/solutions/0433/) — Steps in Euclid's Algorithm
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0444](/solutions/0444/) — The Roundtable Lottery
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0471](/solutions/0471/) — Triangle Inscribed in Ellipse
- ○ [0479](/solutions/0479/) — Roots on the Rise
- ○ [0489](/solutions/0489/) — Common Factors Between Two Sequences
- ○ [0490](/solutions/0490/) — Jumping Frog
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0521](/solutions/0521/) — Smallest Prime Factor
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0534](/solutions/0534/) — Weak Queens
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ○ [0539](/solutions/0539/) — Odd Elimination
- ○ [0542](/solutions/0542/) — Geometric Progression with Maximum Sum
- ○ [0543](/solutions/0543/) — Prime-Sum Numbers
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ○ [0555](/solutions/0555/) — McCarthy 91 Function
- ○ [0577](/solutions/0577/) — Counting Hexagons
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0672](/solutions/0672/) — One More One
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0688](/solutions/0688/) — Piles of Plates
- ○ [0689](/solutions/0689/) — Binary Series
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0737](/solutions/0737/) — Coin Loops
- ○ [0739](/solutions/0739/) — Summation of Summations
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0756](/solutions/0756/) — Approximating a Sum
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0775](/solutions/0775/) — Saving Paper
- ○ [0776](/solutions/0776/) — Digit Sum Division
- ○ [0779](/solutions/0779/) — Prime Factor and Exponent
- ○ [0792](/solutions/0792/) — Too Many Twos
- ○ [0794](/solutions/0794/) — Seventeen Points
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ○ [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ○ [0831](/solutions/0831/) — Triple Product
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0875](/solutions/0875/) — Quadruple Congruence
- ○ [0884](/solutions/0884/) — Removing Cubes
- ○ [0893](/solutions/0893/) — Matchsticks
- ○ [0905](/solutions/0905/) — Now I Know
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0915](/solutions/0915/) — Giant GCDs
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ○ [0933](/solutions/0933/) — Paper Cutting
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0943](/solutions/0943/) — Self Describing Sequences
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0986](/solutions/0986/) — Another Infinite Game
- ○ [0991](/solutions/0991/) — Fruit Salad

<!-- /problems -->
