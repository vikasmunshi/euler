<!-- tags: [digit-sum] -->
<!-- status: final -->
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
the state is bounded and the constraint is local, not that it happens to be a sum.

Once you can count, you can [unrank](/topics/technique/unranking). To find the $n$-th number with a
digit property — problem 845 wants the $n$-th whose digit sum is prime, for $n$ up to $10^{16}$;
problem 974 the $n$-th "very odd" number — never iterate. Fix the length by counting, then choose
digits from the most significant down, at each position subtracting the count of completions that
start with a smaller digit until the remaining rank fits. The work is $O(d^2)$ and completely
independent of $n$, which is the difference between microseconds and never finishing.

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

Distinguish all of this from the problems where the digit sum is merely the *report*: problem 16
($2^{1000}$), problem 20 ($100!$) and problem 56 want a digit sum only as a way to make you produce
an exact big integer. There the digit sum carries no structure and deserves no thought — the work is
[arbitrary-precision arithmetic](/topics/technique/arbitrary-precision-arithmetic), and $s$ is the
checksum at the end. Recognising which family you are in is the first decision.

## How to reason about it

- **Ask what the property actually depends on.** If it depends only on the digit sum, or only on the
  digit multiset, the search space is $O(d)$ or $O(d^{10})$ states, not $10^d$ numbers. If it depends
  on the digits' *order* too, you usually still win — the state is a bounded suffix.
- **Count, then unrank.** "The $n$-th number such that…" is never a loop over $n$.
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
- ○ [0290](/solutions/0290/) — Digital Signature
- ○ [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ○ [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0358](/solutions/0358/) — Cyclic Numbers
- ○ [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ○ [0520](/solutions/0520/) — Simbers
- ○ [0529](/solutions/0529/) — $10$-substrings
- ○ [0538](/solutions/0538/) — Maximum Quadrilaterals
- ○ [0551](/solutions/0551/) — Sum of Digits Sequence
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0698](/solutions/0698/) — 123 Numbers
- ○ [0705](/solutions/0705/) — Total Inversion Count of Divided Sequences
- ○ [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0711](/solutions/0711/) — Binary Blackboard
- ○ [0714](/solutions/0714/) — Duodigits
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0776](/solutions/0776/) — Digit Sum Division
- ○ [0778](/solutions/0778/) — Freshman's Product
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
