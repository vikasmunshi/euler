<!-- tags: [digit-counting-function] -->
<!-- status: final 2026-10-14T12:00Z -->
# Digit-counting function

The [digit-counting function](https://en.wikipedia.org/wiki/Digit-counting_function) answers "how
long is this number?" — for a positive integer $x$ in base 10,
$$d(x) = \lfloor \log_{10} x \rfloor + 1.$$
The reflex is `len(str(x))`, and for a single small number that is fine. But the problems below ask
the question *thousands of times*, or about numbers too large to build, or *backwards* — "which $x$
has exactly $n$ digits?" — and there the string is either slow, impossible, or simply the wrong
shape of thought. The logarithm turns digit length into ordinary arithmetic you can solve, invert
and sum, and that is what keeps bringing it back.

## The idea

There are two equivalent statements of the same fact, and it pays to keep both at hand:

- **As a logarithm:** $d(x) = \lfloor \log_{10} x \rfloor + 1$. Lengths of products become sums,
  $\log_{10}(ab) = \log_{10} a + \log_{10} b$, so lengths of powers become multiples:
  $d(b^n) = \lfloor n \log_{10} b \rfloor + 1$.
- **As an interval:** $x$ has exactly $n$ digits iff $10^{n-1} \le x < 10^n$. This is the exact,
  integer-only form — a comparison against a power of ten, no rounding anywhere.

The logarithm is for *reasoning* — predicting, bounding, inverting. The interval is for
*deciding* — the one test you trust when the answer must be exact. Most good solutions on this tag
use the first to know where to look and the second to confirm.

### Predicting length from growth — problem 25

Problem 25 asks for the first Fibonacci term with 1000 digits. [Binet's
formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Binet's_formula) says
$F_k \approx \varphi^k/\sqrt 5$, and the error is below $\tfrac12$, so
$$d(F_k) = \Big\lfloor k \log_{10}\varphi - \log_{10}\sqrt5 \Big\rfloor + 1.$$
Setting that to $n$ and solving for $k$ gives the index outright:
$k = \big\lceil (n - 1 + \log_{10}\sqrt5) / \log_{10}\varphi \big\rceil$ — one line, no big
integers. The published solution takes the other route: it iterates the recurrence with exact
big integers and stops at `b >= 10 ** (n - 1)`, the interval form of "has $n$ digits". Both are
right; the point is that even the iterative one never calls `str()`. The logarithm also tells you
*why* the loop is cheap: digits grow linearly in $k$ (about $0.209$ per term), so about
$n/0.209$ terms suffice.

### Counting the digits of a block — problem 40

Champernowne's constant $0.123456789101112\ldots$ is the digit-counting function summed. The
$d$-digit integers $10^{d-1}, \ldots, 10^d - 1$ number $9 \cdot 10^{d-1}$, each $d$ characters
long, so they form a band of exactly $d \cdot 9 \cdot 10^{d-1}$ characters. Prefix-sum the bands
until the target position falls inside one, then floor-division and modulo pick the integer and the
digit within it:

```python
while length_with_num_digits < n:
    num_digits += 1
    length_till_num_digits = length_with_num_digits
    length_with_num_digits += num_digits * 9 * 10 ** (num_digits - 1)
```

The loop runs $d(n)$ times — the digit count of the *position* bounds the work. The same
band arithmetic carries the private problems on this tag that live inside the concatenated string:
problem 305 searches the Champernowne string for occurrences of $n$, and problem 156 counts how many
times a digit has been written by the time you reach $n$. In both, the shape is "sum $d(\cdot)$, or a
per-position digit count, over a block of consecutive integers in closed form" rather than walking
the integers one by one.

### Comparing lengths without computing them — problem 57

Problem 57 counts the $\sqrt2$ convergents $p/q$ (among the first thousand) whose numerator has more
digits than its denominator. The solution here does it the honest way: exact recurrence
$(p, q) \to (p + 2q, p + q)$ and two `len(str(...))` calls per step — and it has to lift Python's
[integer-to-string limit](https://docs.python.org/3/library/stdtypes.html#int-max-str-digits) for
large inputs, a hint that strings were never the natural tool. The logarithm explains what is
really being counted. Since $p \approx q\sqrt2$, the numerator is longer exactly when multiplying by
$\sqrt2$ carries $q$ across a power of ten, i.e. when the fractional part of $\log_{10} q$ is at
least $1 - \log_{10}\sqrt2 \approx 0.849$. And $q$ grows by a factor $1+\sqrt2$ per step, so
$\{\log_{10} q\}$ advances by an irrational constant and
[equidistributes](https://en.wikipedia.org/wiki/Equidistribution_theorem): about 15% of steps
qualify. That predicts roughly 150 of the first 1000 — the exact count is a few more — and the
exact version needs no strings either: compare $p$ and $q$ against the next power of ten.

### Inverting the formula — problem 63

Problem 63 asks how many $n$-digit integers are also $n$-th powers. Write the condition with the
digit-counting function, $\lfloor n \log_{10} b \rfloor + 1 = n$, and the whole search space
collapses:

- $b \ge 10$ gives $n \log_{10} b \ge n$, so at least $n + 1$ digits — only $b \in 1..9$ can work;
- for such $b$, the condition is $n(1 - \log_{10} b) \le 1$, i.e. $n \le 1/(1 - \log_{10} b)$.

So the count is $\sum_{b=1}^{9} \lfloor 1/(1 - \log_{10} b) \rfloor$ — nine terms. The published
solution keeps a scan for safety, but it inverts the interval to pick the candidate bases for each
$n$ (`ceil((10 ** (n - 1)) ** (1 / n))` up to `(10**n - 1) ** (1 / n)`) and then checks the length
exactly — prediction by root, decision by count. This is the general move: once length is a
formula, "which numbers have length $n$" is an inequality you solve rather than a range you scan.

## How to reason about it

**Reach for it when** the problem talks about *how many digits* rather than *which digits*, when
the numbers grow geometrically (powers, linear recurrences, convergents), or when the question is
positional over a concatenation. Problem 255 is a small example of the last kind turned around: the
procedure it studies seeds Heron's method from $d(n)$ alone. Digit-string problems further along — the
[Kempner-like series](https://en.wikipedia.org/wiki/Kempner_series) of problem 368, the
one-child numbers of problem 413, whose rule depends on the length $d$ itself — group numbers by
length first, and do the harder work band by band.

**What it buys.** Constant-time length from a magnitude you already know; a closed-form inverse
("first $k$ with $n$ digits"); and lengths of products and powers as additions you can sum or bound.
It also turns "count those with length $n$" into interval arithmetic over $[10^{n-1}, 10^n)$.

**The pitfall is floating point.** $\lfloor\log_{10} x\rfloor$ is exactly wrong at the boundaries
that matter most: in double precision `math.log10(10**23 - 1)` returns `23.0`, so the formula says
24 digits for a 23-digit number. Near a power of ten, a rounded logarithm can land on either side.
So:

- **predict with logs, decide with integers** — use the logarithm to find the neighbourhood, then
  compare against `10 ** (n - 1)` exactly (or keep a precomputed table of powers of ten);
- for big integers, `x.bit_length()` gives $\lfloor \log_2 x \rfloor + 1$ exactly and cheaply, and
  $d(x)$ is $\lfloor (\text{bits} - 1)\log_{10}2 \rfloor + 1$ or one more — a single comparison
  against a power of ten settles which;
- when a closed form like problem 25's index sits close to an integer, check the neighbours
  rather than trusting the ceiling.

**Don't overdo it.** For a few numbers that fit a machine word, `len(str(x))` is clear and fast
enough; the log only earns its keep when it removes a loop, a big integer, or a search.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0305](/solutions/0305/) — Reflexive Position
- ○ [0368](/solutions/0368/) — A Kempner-like Series
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ○ [0731](/solutions/0731/) — A Stoneham Number
- ○ [0990](/solutions/0990/) — Addition Equations

<!-- /problems -->
