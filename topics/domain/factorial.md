<!-- tags: [factorial] -->
<!-- status: final -->
# Factorial

The [factorial](https://en.wikipedia.org/wiki/Factorial) $n! = 1 \cdot 2 \cdots n$ is the first
function most of us meet that outruns every machine word, and Project Euler leans on it constantly —
usually with an $n$ so large that $n!$ has more digits than the universe has atoms. That sounds like
a cruelty until you notice the compensation: $n!$ is the product of *everything* up to $n$, so
unlike a random integer of its size, its prime factorisation is known in closed form before you
compute anything. Nearly every problem below is the same trade — refuse to build the number, work
with its structure instead.

## Two regimes, decided by size

For small $n$ the factorial is just a big integer and the problem is arithmetic. Problem 20 wants the
decimal digit sum of $100!$, all 158 digits of it; problem 121 needs $(n+1)!$ as the common
denominator of a game's outcome tree so the whole computation can stay in exact integers. Python
hands you both for free, and [Stirling's
approximation](https://en.wikipedia.org/wiki/Stirling%27s_approximation) tells you when "for free"
runs out: $\log_{10} n! \approx n \log_{10}(n/e)$, so the digit count grows like $n \log n$ and the
cost of the naive product like $n^2 \log n$. That is fine to $n$ in the thousands and hopeless
beyond.

The second regime is everything else. $10^{12}!$ has about $10^{13}$ digits; $10^8!$ will not be
written down by any machine ever built. Once a problem names an $n$ like that, computing $n!$ is not
a slow approach, it is a non-approach, and the only question is which *property* of $n!$ the
statement actually asks for.

## Legendre's formula is the whole toolkit

The property is almost always the prime factorisation, and
[Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) gives it outright. The
exponent of a prime $p$ in $n!$ — its [$p$-adic
valuation](/topics/domain/p-adic-valuation) — is

$$v_p(n!) = \sum_{k \ge 1} \left\lfloor \frac{n}{p^k} \right\rfloor = \frac{n - s_p(n)}{p - 1},$$

where $s_p(n)$ is the digit sum of $n$ in base $p$. The sum form is the one you code — it terminates
after $\log_p n$ terms and costs nothing:

```python
def valuation(n: int, p: int) -> int:
    """Exponent of the prime p in n!, by Legendre's formula."""
    total, power = 0, p
    while power <= n:
        total += n // power
        power *= p
    return total
```

The counting argument is worth holding in your head rather than memorising the formula: among
$1 \dots n$ there are $\lfloor n/p \rfloor$ multiples of $p$, each contributing at least one factor
$p$; the $\lfloor n/p^2 \rfloor$ multiples of $p^2$ contribute a second; and so on. Every factor is
counted exactly once, at the level where it appears.

Three consequences do most of the work:

- **Trailing zeros are a valuation.** $n!$ ends in $v_5(n!)$ zeros, because factors of $2$ are
  always more plentiful than factors of $5$. Problems 160 and 592 both ask for the digits *before*
  those zeros — in base $10$ and base $16$ respectively — which is the same question with the roles
  of $2$ and $5$ swapped, and problem 926 generalises "trailing zeros in base $b$" to all bases at
  once.
- **The digit-sum form eliminates $n$ itself.** When $n$ is defined only by its base-$p$ digits, as
  in problem 288, $v_p(n!) = (n - s_p(n))/(p-1)$ can be evaluated digit by digit — each digit
  contributes its value times a base-$p$ repunit — so a number with ten million digits never gets
  assembled.
- **Exponents repeat.** Every prime $p > \sqrt{n}$ has $v_p(n!) = \lfloor n/p \rfloor$ exactly, so
  the exponents across all $\pi(n)$ primes take only about $2\sqrt{n}$ distinct values. At
  $n = 10^7$ that is $2087$ values covering $664\,579$ primes — the difference between a per-prime
  loop and a per-*class* loop, which is what makes several of these problems finish at all.

The same formula run backwards answers "which $m!$ is divisible by this?": since $v_p(m!)$ is a
non-decreasing step function of $m$, the smallest $m$ with $n \mid m!$ is the largest over the
prime powers $p^e \parallel n$ of the smallest $m$ clearing that one constraint (problems 549 and
320). And its floor-superadditivity, $\lfloor a \rfloor + \lfloor b \rfloor \le \lfloor a+b \rfloor$
applied termwise, is the one-line proof that $\binom{n}{k}$ is an integer — a product of $k$
consecutive integers is always divisible by $k!$.

## $n!$ as a multiplicative object

A large fraction of the factorial problems are really problems about a
[multiplicative function](/topics/domain/multiplicative-function) evaluated at $n!$: the sum of
squares of its [unitary divisors](/topics/domain/unitary-divisor) (problem 429), its divisors with a
given last digit (474), pairs of complementary divisors with equal divisor counts (598), a
Liouville-weighted divisor sum in a range (646), divisor-sum sums (608), restricted factorisations
(636), or the divisors of a superfactorial-of-superfactorials filtered by $\Omega$ (956).

The shape is always the same and worth naming, because recognising it converts a hopeless problem
into a routine one:

1. $n!$ has an astronomical number of divisors — $100!$ already has close to $4 \times 10^{16}$ —
   so nothing may ever enumerate them.
2. But a multiplicative $f$ satisfies $f(n!) = \prod_{p \le n} f(p^{v_p(n!)})$, a product over the
   $\pi(n)$ primes of a local factor that depends only on $p$ and one exponent.
3. Legendre supplies every exponent in $O(\log_p n)$, a
   [sieve](/topics/technique/sieve-of-eratosthenes) supplies the primes, and the answer is a single
   pass — with the primes above $\sqrt{n}$ grouped by their shared exponent, as above.

So the data structure for $n!$ is never the number. It is the exponent vector $(v_p(n!))_{p \le n}$,
usually compressed to (exponent, count-of-primes) pairs.

## Factorials under a modulus

When the problem does want $n!$ itself but only modulo $m$, the naive product dies for a second
reason: $n! \equiv 0 \pmod m$ the moment $n$ reaches the largest prime factor of $m$. The
information you want is hiding underneath that zero, and getting at it takes two tools.

[Wilson's theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem) — $(p-1)! \equiv -1 \pmod p$
for prime $p$ — is the anchor. Unwinding it downward with $p - k \equiv -k$ gives
$(p-2)! \equiv 1$, then $(p-3)!$, $(p-4)!$ and so on as small
[modular inverses](/topics/domain/modular-multiplicative-inverse), each a fixed rational independent
of $p$. That is the mechanism behind problem 381: a sum of the first few factorials below $p$
telescopes into one constant residue, so what looked like millions of hundred-million-digit
factorials becomes a lookup per prime.

For a composite modulus the tool is the **$p$-free factorial** — $n!$ with every factor of $p$
divided out — computed modulo $p^k$ by splitting $[1, n]$ into multiples of $p$ (which recurse to
the same problem on $\lfloor n/p \rfloor$, depth $\log_p n$) and non-multiples (which are the units
modulo $p^k$, repeated over whole periods plus a short tail). A generalised Wilson theorem collapses
each whole period to a sign, leaving only the tail to multiply out. Combine the prime-power results
with the [Chinese Remainder Theorem](/topics/technique/chinese-remainder-theorem), restore or remove
powers of $p$ with a modular inverse, and you have the last few digits of a factorial you never
built — the engine of problems 160 and 592. Problem 952, the
[multiplicative order](/topics/domain/multiplicative-order) of a prime modulo $n!$, is the same
decomposition seen from the other side: solve modulo each $p^{v_p(n!)}$, then take a least common
multiple.

## The other factorial: a nine-entry table

A separate family of problems uses factorials not as a growth rate but as a fixed alphabet — the
digit factorials $0!, 1!, \dots, 9!$, of which the largest is $9! = 362880$. Here the growth works
*for* you: $d$ digits can sum to at most $362880d$, which falls behind $10^{d-1}$ almost immediately,
so the search space is bounded by a couple of lines of arithmetic. Problem 34 (numbers equal to the
sum of their digits' factorials) closes at seven digits, and since the sum ignores order, the
candidates are digit *multisets* rather than numbers:

```python
factorial = {"0": 1, "1": 1, "2": 2, "3": 6, "4": 24, "5": 120, "6": 720, "7": 5040,
             "8": 40320, "9": 362880}
for num_digits in range(2, 8):
    for digits in itertools.combinations_with_replacement("0123456789", num_digits):
        ...
```

That is $C(k+9, k)$ combinations instead of $10^k$ numbers — a few thousand checks in total.
Problem 74 iterates the same digit-factorial map and gets a functional graph, where every trajectory
falls into one of three cycles and [memoisation](/topics/technique/memoization) makes the whole
million-element sweep linear. Problem 254 inverts the map, and lands on the fact that
$\{1!, 2!, \dots, 9!\}$ is a canonical coin system — the greedy expansion is the shortest one — which
is the [factorial number system](/topics/domain/factorial-number-system) wearing a different hat.
That page covers the other half of this territory: factorials as place values, and the ranking and
unranking of permutations.

## How to reason about it

The first question on seeing a factorial is always *how big is $n$?* Below a few thousand, compute
it. Above that, the second question is which of four things the statement wants:

| What is asked | What to reach for |
|---|---|
| Digits, size, an exact rational | Big integers; Stirling to sanity-check the cost |
| Divisibility, valuations, trailing zeros | Legendre's formula |
| A divisor-flavoured quantity of $n!$ | Multiplicativity over the exponent vector |
| $n!$ modulo something | Wilson, the $p$-free factorial, CRT |

Things that bite:

- **Reducing too early.** `math.factorial(n) % m` is correct and useless — it builds the number
  first. And reducing *during* the product gives $0$ as soon as you pass a prime factor of $m$, which
  is correct and also useless. Strip the shared primes before reducing, not after.
- **Trailing zeros counted in base $10$.** They are $v_5$, not $v_2$ — and in any other base the
  answer is $\min_p \lfloor v_p(n!) / v_p(b) \rfloor$, which is a different prime for a different
  base.
- **Looping over primes when you could loop over exponents.** Below $\sqrt{n}$, compute valuations
  individually; above it, band the primes by $\lfloor n/p \rfloor$. Skipping this is usually the
  difference between minutes and seconds.
- **Overflow in the "safe" step.** The valuation of $2$ in $n!$ is nearly $n$, so exponents are large
  even when values are reduced; modular exponentiation with a $10^{18}$-ish modulus overflows 64-bit
  products in C long before anything looks suspicious.
- **$0! = 1$.** It is the empty product, not a special case — and in digit-factorial problems it
  makes `0` and `1` interchangeable, which quietly changes what "smallest" means.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0121](/solutions/0121/) — Disc Game Prize Fund
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ○ [0320](/solutions/0320/) — Factorials Divisible by a Huge Integer
- ○ [0330](/solutions/0330/) — Euler's Number
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ○ [0383](/solutions/0383/) — Divisibility Comparison Between Factorials
- ○ [0418](/solutions/0418/) — Factorisation Triples
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0598](/solutions/0598/) — Split Divisibilities
- ○ [0608](/solutions/0608/) — Divisor Sums
- ○ [0636](/solutions/0636/) — Restricted Factorisations
- ○ [0646](/solutions/0646/) — Bounded Divisors
- ○ [0829](/solutions/0829/) — Integral Fusion
- ○ [0851](/solutions/0851/) — SOP and POS
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0937](/solutions/0937/) — Equiproduct Partition
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0956](/solutions/0956/) — Super Duper Sum

<!-- /problems -->
