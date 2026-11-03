<!-- tags: [digit-sum] -->
<!-- status: final 2026-11-02T11:45Z -->
# Digit sum

The [digit sum](https://en.wikipedia.org/wiki/Digit_sum) $s(n)$ — add up the decimal digits and stop
— is the crudest function of an integer anyone bothers to name, and it has almost no arithmetic
structure. It ignores multiplication, only half-respects addition, and swings wildly between $n$ and
$n+1$. That is precisely why it recurs across the problems below: a condition phrased on digits cuts
across every tool a number theorist would reach for, and leaves you computing in the one place where
digit conditions are local — the decimal representation itself. The good news is that the same
crudeness makes $s$ tiny and order-blind, and those two facts are worth more than any algebra it
lacks.

## The one property that is algebra

Since $10 \equiv 1 \pmod 9$, writing $n = \sum_i d_i 10^i$ gives $n \equiv \sum_i d_i = s(n)
\pmod 9$. That single congruence is the whole of
[casting out nines](https://en.wikipedia.org/wiki/Casting_out_nines) and of the
[divisibility rules](/topics/domain/divisibility-rule) for $3$ and $9$, and it collapses the
iterated digit sum into a closed form: the
[digital root](https://en.wikipedia.org/wiki/Digital_root) is

$$\operatorname{dr}(n) = 1 + (n - 1) \bmod 9 \qquad (n \ge 1),$$

which is $n \bmod 9$ with the residue $0$ read as $9$. Problem 159 leans on exactly this — its
per-factor digital roots are never computed by summing digits at all, which turns the inner term of
a divisor-sieve DP into one modulo. In base $b$ the statement generalises to $s_b(n) \equiv n
\pmod{b-1}$, so the trick is about the base, not about ten.

In base $2$ the digit sum is the [Hamming weight](https://en.wikipedia.org/wiki/Hamming_weight), and
its residue mod $2$ is a parity that composes perfectly: adding a number to a *collection* (not to a
sum) flips the total count of ones exactly when that number's own weight is odd. Problem 711 is a game
in which players write numbers under a shrinking budget and the winner is decided by the parity of all
ones on the board, so every position collapses to (remaining budget, current parity) — a two-column
table small enough to compute exhaustively for $n$ up to a thousand. The table then shows the winning
$n$ as two rigid bit patterns, which sum in closed form for $n$ up to $2^{12\,345\,678}$. When the digit
sum enters only through its residue, the residue is the whole state; tabulate small cases and read the
structure off before reaching for theory.

Because the congruence is additive over digits, it survives being cut into pieces: a substring
$n[i..j)$ is divisible by $3$ exactly when the [prefix sums](https://en.wikipedia.org/wiki/Prefix_sum)
of the digits agree mod $3$ at $i$ and at $j$. Problem 706 counts the $d$-digit numbers in which the
number of divisible substrings is itself a multiple of $3$ — a property of all $\binom{d+1}{2}$
substrings, reduced by that one observation to residue counts: with $c_r$ prefixes of residue $r$, the
count is $\sum_r \binom{c_r}{2}$, and appending a digit adds exactly the count of earlier prefixes
sharing the new residue. Everything the future depends on is three counts and a running total, all
mod $3$, so the number is read by an $81$-state automaton whose transitions depend only on each
digit's residue class. That is a [digit DP](/topics/technique/digit-dp) with a constant-size state,
and it sets up the huge-length trick at the end of that section.

The closed form gives you the *destination*, not the route. Problem 315 feeds primes to
[seven-segment](/topics/domain/seven-segment-display) "digital root clocks" that display every
intermediate value of $p \to s(p) \to s(s(p)) \to \dots$, and charges for the segments switched
between consecutive displays — so the whole chain matters and $1 + (p-1) \bmod 9$ is of no use. What
rescues it is the next section's property: only the first step is expensive.

Addition is where the structure stops. Carrying moves $10$ into $1$, losing $9$ each time:

$$s(a + b) = s(a) + s(b) - 9c,$$

with $c$ the number of carries in the addition. That accounting is the bridge between digit sums and
multiplicative number theory — [Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula)
$v_p(n!) = (n - s_p(n))/(p-1)$ and
[Kummer's theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem) are both this identity read
backwards (see [Factorial](/topics/domain/factorial)) — and it is essentially the only bridge.
Nothing similar exists for products: $s(ab)$ is unrelated to $s(a)$ and $s(b)$ beyond mod $9$. When a
problem mixes the two anyway — a [Harshad number](/topics/domain/harshad-number) is divisible by its
own digit sum, the subject of problem 387 — there is no formula to exploit, and the only handle left
is a *hereditary* property: being right-truncatable Harshad is inherited by every prefix, so you grow
candidates a digit at a time and prune the moment a prefix fails. Expect that shape whenever digits
and divisibility are stated together.

## Small, and blind to order

Two properties do most of the real work.

**The digit sum is logarithmic.** A $d$-digit number has $s(n) \le 9d$; the digit-square sum is at
most $81d$, the digit-factorial sum at most $9! \cdot d$. So the value of $s$ is a legitimate piece of
*state*: for the twenty-digit range of problem 171 there are $10^{20}$ numbers but fewer than $1621$
distinct digit-square sums, and for the seventeen-digit range of problem 845 fewer than $154$ digit
sums. A hopeless enumeration becomes a table you can index.

The same bound makes *iterating* $s$ cheap after one application. Below $10^{10}$, $s(n) \le 90$, so
everything downstream of the first digit sum is a function on $\{1, \dots, 90\}$ and can be
[tabulated](/topics/technique/lookup-table) once. Problem 315 goes one better: the two-digit $s(p)$,
right-aligned under $p$, only ever meets $p$'s last two digits, so each prime's contribution is a
function of the pair $(p \bmod 100,\ s(p))$ — a few thousand table entries — and the per-prime work
shrinks to one digit sum and two lookups. The cost of the problem moves entirely into the prime sieve.

Smallness also tames a sequence that *feeds* $s$ back into itself. Problem 551 iterates
$a \mapsto a + s(a)$ for $10^{15}$ steps, with no closed form in sight. Split the current value as
$H \cdot 10^k + L$: until $L$ overflows $10^k$ the high part is frozen, and it influences each step
only through $s(H)$ — a number below $9$ times its length. So "how many steps until the low block
carries, and what is left behind" is a function of $(k, s(H), L)$ alone, not of $H$, and each
level-$k$ jump decomposes into at most ten level-$(k-1)$ jumps, one per leading digit of $L$. The
overshoot after a carry is at most one digit sum, so the same states recur constantly and
[memoization](https://en.wikipedia.org/wiki/Memoization) turns $10^{15}$ steps into a few tens of
thousands of cached blocks. The pattern to remember: when the high digits are only ever *read
through* $s$, the digit sum is the whole of their influence, and you can jump over everything below.

Problem 506 runs the dual construction: rather than feeding digit sums into a sequence, it cuts a
periodic digit stream $1234321234\ldots$ into consecutive pieces whose digit sums are $1, 2, 3, \ldots$.
Measure position in the stream by *cumulative digit sum* instead of by digit index, and the period
becomes a phase: every six-digit window sums to $15$, so two pieces whose starting offsets differ by a
multiple of $15$ start at the same phase. Piece $n+15$ therefore reads piece $n$ and then exactly one
more period, giving an affine recurrence $v_{n+15} = 10^6 v_n + Q_{n \bmod 15}$; within each residue
class that unrolls to a [geometric series](https://en.wikipedia.org/wiki/Geometric_series), and
$10^{14}$ terms cost fifteen modular exponentiations. The lesson generalises: when digits come from a
periodic source, index by the digit-sum offset modulo the period's sum, and periodicity turns into a
linear recurrence.

Smallness also lets the digit sum sit somewhere arithmetically awkward and still be grouped away.
Problem 776 sums $n / s(n)$ for every $n$ up to $1.2 \times 10^{18}$ — the digit sum as a
*denominator*, where no additive trick reaches it. But $s(n) \le 171$, so
$\sum_n n/s(n) = \sum_s T(s)/s$, with $T(s)$ the total of all $n$ having digit sum $s$: one hundred
seventy-one integers, each a digit-DP aggregate (next section). Grouping by the small value converts
a non-linear function of $s$ into a short weighted sum, and because the $T(s)$ are exact integers the
final rational can be rounded to the requested thirteen significant digits with no floating-point
doubt.

The digit sum is also the *floor* of a natural family of operations. Problem 637 lets you insert plus
signs anywhere among a number's base-$B$ digits and add the parts; concatenating parts only increases
a value ($10a + b \ge a + b$), so the finest split — all plus signs — gives the minimum, and that minimum
is $s_B(n)$. One step reaches a single digit exactly when $s_B(n) < B$, with no search at all. The
remaining levels are tiny (at most three up to $10^7$), so the question changes from "find the minimum
over $2^{L-1}$ splits" to "find *one* split sum already known to settle at the level below" — and a
witness can be hunted by a meet-in-the-middle bitset over high and low halves of the digits.

**The digit sum ignores order.** $s$ depends only on the *multiset* of digits, so $123$, $321$ and
$213$ are the same object. Two ways to cash that in. Enumerate the multisets directly — problems 30
and 34 replace a scan of ten million integers with
[combinations with replacement](https://docs.python.org/3/library/itertools.html#itertools.combinations_with_replacement)
over $\{0,\dots,9\}$, under twenty thousand candidates — or count how many numbers land in each
bucket, which is a [convolution](https://en.wikipedia.org/wiki/Convolution) of one-digit
distributions. Problem 92 (public, so here is the code) grows that distribution one digit at a time,
and classifies the few hundred reachable sums rather than the ten million starting values:

```python
a, sq = [1], [x**2 for x in range(1, 10)]
for _ in range(power_of_10):                 # one decimal position per pass
    b, a = a, a + [0] * 81                   # a[s] = how many strings have digit-square-sum s
    for i, v in enumerate(b):
        for s in sq:
            a[i + s] += v
```

Leading zeros are admitted deliberately: $0$ contributes nothing to the sum, so a uniform
$d$-position pass also covers every shorter number, and no per-length special case is needed. Check
that this is really true of your object before relying on it — problem 788 counts numbers *below*
$10^N$, where a leading zero would make the number shorter and change which digit dominates, and
problem 164 counts genuine $20$-digit numbers, so both must seed the top position separately.

Nor does the convolution have to be additive. Problem 778's "freshman's product" multiplies numbers
digit by digit, keeping only the last digit of each product — the carry-free operation the carry
identity above warns you ordinary arithmetic is not. Discarding carries makes the positions
independent, and [linearity](/topics/domain/positional-notation) splits the sum over all $(M+1)^R$
tuples into one sub-problem per decimal place: $\sum_i 10^i \sum_d d \cdot N_i(d)$, where $N_i$ is
the distribution of the $i$-th digit of the product. Each $x_j$ then matters only through its digit
at that place, so $[0, M]$ collapses to a ten-bucket histogram (closed-form: whole periods of $10^{i+1}$
plus one clipped partial run), and $N_i$ is that histogram's $R$-th
[convolution](/topics/technique/convolution) power over the monoid $(\{0,\dots,9\}, \times \bmod 10)$.
Associativity is all [repeated squaring](/topics/technique/exponentiation-by-squaring) needs — not
inverses, which this monoid lacks — so a quarter-million-fold product costs a few dozen $10 \times 10$
convolutions per digit. Here leading zeros are not merely harmless but *correct*: the operation itself
reads a missing digit as $0$.

When the condition is on digit *counts* rather than their sum, order-blindness has a sharper tool.
Problem 520's "simbers" require every odd digit present to occur an odd number of times and every
even digit an even number. Counting *strings* subject to a constraint on each symbol's multiplicity is
the job of [exponential generating functions](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function):
a symbol allowed $j$ times contributes $x^j/j!$, the product of the factorials reproduces the
multinomial count of arrangements, and the answer for length $L$ is $L!\,[x^L]$ of the product. Even
counts give $\cosh x$, odd-or-absent gives $1 + \sinh x$, and both are combinations of $e^{\pm x}$ —
so the whole product expands into $\sum_k c_k e^{kx}$ with $|k| \le 10$, and since
$L!\,[x^L]\,e^{kx} = k^L$, the count is an exact sum of $21$ powers. Summing over all lengths up to
$2^{39}$ is then $21$ geometric series. Whenever the EGF factors are exponentials, the count is a
power sum in the length, and the length can be astronomical.

## Digit DP: count the buckets, not the numbers

Generalise the pass above and you have [digit DP](/topics/technique/digit-dp): walk the number one
position at a time, carrying only a bounded state — typically the running digit sum, plus a "still
equal to the prefix of the bound" flag when the range is not a clean power of ten. The recurrence is
one line, the table is $O(d \cdot 9d)$, and the cost is polynomial in the *digit count* while the
range is exponential in it.

The refinement that makes it answer more than "how many" is to carry an aggregate alongside the
count. Keep per state both $c$, the number of prefixes reaching it, and $v$, the sum of their values;
appending a digit $x$ at the low end maps $(c, v) \mapsto (c,\ 10v + x c)$. Problem 171 uses exactly
that to total every number below $10^{20}$ whose digit-square sum is a perfect square, and problem
725 to total the "DS-numbers", where the awkward clause *contains at least one digit equal to $h$* is
handled by complementary counting: all numbers of digit sum $2h$, minus those avoiding $h$ entirely.
Problem 217 shows the state need not be a single running sum — a balanced number is two half-blocks
keyed by digit sum, and the middle digit of an odd-length number cancels from both sides, so the two
halves are counted independently and convolved. And problem 164, whose constraint is "no three
consecutive digits exceed $9$", keeps the trailing *pair* of digits as its state: what matters is that
the state is bounded, not that it happens to be a sum.

The state can also carry *arithmetic*. Problem 290 counts $n < 10^{18}$ with $s(n) = s(137n)$, which
compares a number's digits with those of its multiple. Long multiplication by a constant is itself a
[transducer](https://en.wikipedia.org/wiki/Finite-state_transducer) read right to left: each column
computes $137d + c$, emits its last digit and passes on a carry that provably stays below $137$. So
the DP state is the pair (carry, running difference $s(\text{input}) - s(\text{output})$) — tracking
the *difference* rather than both sums, because only equality matters, drops a dimension — and the
final carry's own digit sum closes the comparison. The congruence from the first section gives a free
check: $s(n) \equiv s(137n) \pmod 9$ forces $9 \mid 136n$, so every hit is a multiple of $9$.

The constraint need not even look local. Problem 529 asks that *every* digit lie in some contiguous
substring summing to $10$ — a condition on all substrings at once. It still has a bounded state,
because digits are non-negative: a running sum that passes $10$ can never come back. So the state is
the set of suffix sums still $\le 10$ (an $11$-bit mask) plus the sum from the earliest uncovered
digit, which kills the number the moment it exceeds $10$. Non-negativity is what turns a global
substring property into a [finite automaton](/topics/technique/finite-state-machine) read left to
right; look for that monotonicity whenever a digit condition quantifies over substrings.

Once you can count, you can [unrank](/topics/technique/unranking). To find the $n$-th number with a
digit property — problem 845 wants the $n$-th whose digit sum is prime, for $n$ up to $10^{16}$;
problem 974 the $n$-th "very odd" number — never iterate. Fix the length by counting, then choose
digits from the most significant down, at each position subtracting the count of completions that
start with a smaller digit until the remaining rank fits. The work is $O(d^2)$ and completely
independent of $n$, which is the difference between microseconds and never finishing.

"Polynomial in the digit count" stops being good enough when the digit count is itself
astronomical: problem 529 wants the count over all numbers of up to $10^{18}$ digits. A digit DP is
then a fixed automaton run for $L$ steps, and its count of accepted words of length $L$ obeys a
[linear recurrence with constant coefficients](/topics/technique/linear-recurrence-with-constant-coefficients)
of order at most the number of states ([Cayley–Hamilton](/topics/domain/cayley-hamilton-theorem) on
the transition matrix). When the automaton is small, raise its matrix directly: problem 706's $81$
states make an $81 \times 81$ [power by squaring](/topics/technique/exponentiation-by-squaring), so
$10^5$ or $10^6$ digits cost the same handful of products. With a few thousand states, matrix powers
are too slow, but you do not need
the matrix: run the DP for twice the (minimised) state count, let
[Berlekamp–Massey](/topics/technique/berlekamp-massey-algorithm) recover the recurrence, and jump to
index $10^{18}$ with $O(\log L)$ polynomial products. The automaton's size is what makes the fit
*rigorous* rather than a guess from a short prefix.

## When the digit sum is the target

A second family makes $s$ (or a digit-wise variant) the *right-hand* side: find every $n$ with
$n = \sum_i f(d_i)$. These always look unbounded and never are, because the two sides grow at
different rates — the right side is at most $d \cdot \max_d f(d)$, linear in the digit count, while
the left is at least $10^{d-1}$. Solve $d \cdot \max f < 10^{d-1}$ and the search is finite: six
digits for the fifth powers of problem 30, seven for the digit factorials of problem 34. Deriving
that ceiling *is* the problem; the scan afterwards is bookkeeping.

Inversion is the same idea applied harder. Problem 119 asks for numbers equal to a power of their own
digit sum; rather than scan $n$, note that the base must *be* a digit sum, hence at most $9 \cdot 18$
below $10^{18}$, and generate the couple of hundred bases' powers instead. Problem 254 pushes it
furthest: the number it is really about has billions of digits, so nothing can be iterated at all, and
the question "what is the smallest $n$ with a given digit-factorial sum?" is answered structurally —
the digits must be ascending, $0$ is never useful because $0! = 1!$, and the shortest representation
of the target as $\sum_d c_d \cdot d!$ is greedy from $9!$ down.

The plain digit sum inverts the same greedy way, and then the inverse is a closed form. Problem 684
wants the smallest number with digit sum $n$: as few digits as possible, so as many $9$s as fit, with
the remainder in front — writing $n = 9q + r$, that number is $(r+1) \cdot 10^q - 1$. Summing it over
$n \le k$ is a geometric series in $10^q$, and when $k$ is a Fibonacci number near $3 \times 10^{18}$
the power $10^q$ has $10^{17}$ digits and exists only modulo the prime: by
[Fermat](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) the exponent matters only mod
$p - 1$, so $k$ is carried modulo $9p$ and $9(p-1)$ at once, and dividing out the $9$ yields $q$ in
both residues.

Distinguish all of this from the problems where the digit sum is merely the *report*: problem 16
($2^{1000}$), problem 20 ($100!$) and problem 56 want a digit sum only as a way to make you produce
an exact big integer. There the digit sum carries no structure and deserves no thought — the work is
[arbitrary-precision arithmetic](/topics/technique/arbitrary-precision-arithmetic), and $s$ is the
checksum at the end. Recognising which family you are in is the first decision.

## How to reason about it

- **Ask what the property actually depends on.** If it depends only on the digit sum, or only on the
  digit multiset, the search space is $O(d)$ or $O(d^{10})$ states, not $10^d$ numbers. If it depends
  on the digits' *order* too, you usually still win — the state is a bounded suffix.
- **No carries, no coupling.** A digit-wise operation that drops carries splits into one
  independent problem per position; sum over all inputs by weighting each position's digit
  distribution by its place value.
- **Freeze the high digits.** If a process sees the digits above some position only through their
  sum, key the block below on that sum and memoise whole carries instead of single steps.
- **Arithmetic on the number is a carry in the state.** Comparing $s(n)$ with $s(kn)$ is a digit DP
  over (carry, difference); the carry is bounded by the multiplier.
- **Group by the small value.** Any function of $s(n)$ — even a denominator — becomes a short sum over
  the $O(9d)$ possible values, each weighted by a digit-DP total.
- **Multiplicity constraints are EGFs.** Parity-of-count conditions give $\cosh$/$\sinh$ factors,
  hence a power sum in the length; a periodic digit source gives an affine recurrence in the
  digit-sum offset. Either way the length can be astronomical.
- **Count, then unrank.** "The $n$-th number such that…" is never a loop over $n$.
- **When the length is huge, fit the recurrence.** A digit DP over a fixed automaton is a linear
  recurrence in the length; recover it from a prefix sized by the state count, then jump.
- **Mod $9$ is necessary, never sufficient.** $s(n) \equiv n \pmod 9$ prunes candidates and proves
  nothing; a digital-root argument that concludes an equality is wrong.
- **Keep the arithmetic exact.** Digit conditions are equalities on integers. Problem 112's
  "exactly $99\%$ are bouncy" is an integer cross-multiplication, not a float comparison; the digit
  sums a DP accumulates are themselves small, but the values it totals are not, so reduce them mod
  the requested modulus as you go rather than at the end.
- **Watch the base.** Every result here is really about $s_b$ and $b-1$; when a problem's digits are
  binary or $p$-ary, the same machinery applies with the constants moved, and the factorial
  valuation identity becomes available.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0022](/solutions/0022/) — Names Scores
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0290](/solutions/0290/) — Digital Signature
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0358](/solutions/0358/) — Cyclic Numbers
- ○ [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ● [0506](/solutions/0506/) — Clock Sequence
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ● [0520](/solutions/0520/) — Simbers
- ● [0529](/solutions/0529/) — $10$-substrings
- ○ [0538](/solutions/0538/) — Maximum Quadrilaterals
- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0711](/solutions/0711/) — Binary Blackboard
- ○ [0714](/solutions/0714/) — Duodigits
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0749](/solutions/0749/) — Near Power Sums
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ○ [0817](/solutions/0817/) — Digits in Squares
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ○ [0954](/solutions/0954/) — Heptaphobia
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ○ [1004](/solutions/1004/) — Balanced Integer

<!-- /problems -->
