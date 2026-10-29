<!-- tags: [square-free-integer] -->
<!-- status: final -->
# Square-free integer

A [square-free integer](https://en.wikipedia.org/wiki/Square-free_integer) is one that no prime
divides twice: $30 = 2 \cdot 3 \cdot 5$ is, $12 = 2^2 \cdot 3$ is not ([OEIS
A005117](https://oeis.org/A005117)). The definition is trivial, and that is exactly why it
keeps turning up. Square-freeness is the point where "the set of primes dividing $n$" and "$n$"
stop being different things. A square-free number *is* its set of prime factors, so its divisors
are subsets, its [radical](/topics/domain/radical-of-an-integer) is itself, and the
[Möbius function](/topics/domain/mobius-function) on it is a plain $\pm 1$. In the problems below
it does three different jobs. Sometimes it is the thing being **counted**, sometimes it is the
**normal form** that makes a decomposition unique, and sometimes it is a cheap **filter** that
throws out most candidates before the expensive check.

## Three ways to say "no repeated prime"

The same property has three equivalent definitions, and each one is the right handle for a
different kind of problem:

| Form | Statement | What it is good for |
|---|---|---|
| Möbius | $\mu(n)^2 = 1$, i.e. $\mu(n) \ne 0$ | sieving a whole range; prefix counts |
| Divisor | $\mu^2(n) = \sum_{d^2 \mid n} \mu(d)$ | turning a count into a sum over $d \le \sqrt{x}$ |
| Structure | $n = s^2 k$ with $k$ square-free, uniquely | splitting any $n$ into "square part × square-free part" |

The second row is [inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over the
square divisors. Start with everything, remove multiples of $4$, $9$, $25$, …, add back the
multiples of $36$ you removed twice, and so on. The coefficient on $d^2$ is $\mu(d)$. The third
row says that every positive integer factors uniquely into its largest square divisor $s^2$ and a
square-free *core* $k$: give each prime exponent's even part to $s^2$ and its parity bit to $k$.
About $6/\pi^2 \approx 61\%$ of integers are square-free. That is the probability that no prime
"hits twice", $\prod_p (1 - p^{-2}) = 1/\zeta(2)$, and it is worth keeping in mind as a sanity
check on any count you produce.

## Counting them

Summing the divisor form over $n \le x$ and swapping the order gives the identity that problem
193 is built on:

$$Q(x) \;=\; \#\{n \le x : n \text{ square-free}\} \;=\; \sum_{d=1}^{\lfloor\sqrt{x}\rfloor} \mu(d)\,\Big\lfloor \frac{x}{d^2} \Big\rfloor .$$

This is a square-root saving. A count over $2^{50}$ integers turns into a sum over $2^{25}$ values
of $d$, and the only table needed is $\mu$ up to $\sqrt{x}$, built by the signed Eratosthenes sieve
on the [Möbius page](/topics/domain/mobius-function). When you need $Q$ at *every* point of a range
rather than at one large $x$, as problem 464 does for the square-free count of an interval
$[a, b]$, skip the identity and prefix-sum the indicator directly: $Q(b) - Q(a-1)$ with
$Q = \text{cumsum}(\mu \ne 0)$. That comes free from the same $\mu$ table that gives the Mertens
function. Sum the identity at one large $x$; prefix-sum the sieve when you need many $x$.

## The normal form: $n = s^2 k$

Problem 745 sums, over $n \le N$, the largest perfect square dividing $n$. That is $s^2$ in the
decomposition above, so the sum looks like a factorisation job on every $n$. It is not. Group by
$s$ and the count of $n = s^2 k$ with $k$ square-free is $Q(N/s^2)$. Push the Möbius identity
for $Q$ through and collect terms by $m = s\,d$, and the whole sum becomes

$$\sum_{m \le \sqrt{N}} h(m) \Big\lfloor \frac{N}{m^2} \Big\rfloor, \qquad h = \mu * (m \mapsto m^2),$$

a [Dirichlet convolution](/topics/domain/dirichlet-convolution) that is
[multiplicative](/topics/domain/multiplicative-function) with $h(p^a) = p^{2a} - p^{2a-2}$ (it is
[Jordan's totient](https://en.wikipedia.org/wiki/Jordan%27s_totient_function) $J_2$). A
[linear sieve](/topics/technique/linear-sieve) builds $h$ up to $\sqrt N$, and the work is again
$O(\sqrt N)$. The square-free core never gets computed. Its only job is to make "$n = s^2 k$"
a bijection, so that the regrouping counts each $n$ once.

Problem 694 uses square-freeness the same way, as a uniqueness device, one level up. A
[cube-full](https://en.wikipedia.org/wiki/Powerful_number) number (every prime exponent $\ge 3$)
factors uniquely as $a^3 b^4 c^5$ with $b$ and $c$ square-free and coprime. Each exponent
$e \ge 3$ has exactly one form $3i + 4j + 5l$ with $j, l \in \{0, 1\}$ and not both set, chosen by
$e \bmod 3$. Requiring $b$ and $c$ square-free is precisely "$j, l \le 1$"; requiring them coprime
is "not both". Without those two conditions the enumeration would reach $2^{12}$ twice, as
$(2^4)^3$ and as $(2^3)^4$, and double-count it. This is the general recipe for
enumerating [powerful numbers](https://en.wikipedia.org/wiki/Powerful_number) ($a^2 b^3$ with $b$
square-free) and their relatives: **pin the leftover exponents to $\{0,1\}$ by demanding a
square-free factor, and the parametrisation becomes a bijection you can loop over.**

Problem 641 takes the device one step further and makes the square-free factor carry a *sign*.
Die $k$ in a row of $n$ dice ends on 1 when its [divisor count](/topics/domain/divisor-function)
satisfies $d(k) \equiv 1 \pmod 6$. Oddness forces $k = m^2$, and $d(m^2) = \prod (2a_i + 1)$ is
$\equiv 1 \pmod 3$ exactly when no exponent $a_i$ is $\equiv 1 \pmod 3$ and an even number are
$\equiv 2$. Such $m$ factor uniquely as $c^3 q^2$ with $q$ square-free. The primes of $q$ are the
ones whose exponents are $\equiv 2$, and "an even number of them" is just $\mu(q) = +1$. The count
becomes a lattice count of pairs $(c, q)$ under $c^3 q^2 \le \sqrt n$, and the long tail in $q$
needs the number of square-free $q \le x$ *of a given parity*. That is one line once you notice
that $\mu$ is $\pm 1$ on square-free numbers and $0$ elsewhere:

$$\#\{q \le x : \mu(q) = \pm 1\} \;=\; \tfrac12\big(Q(x) \pm M(x)\big),$$

with $M$ the [Mertens function](/topics/technique/mertens-function-application). $Q$ comes from
the identity above, $M$ from its own sub-linear recursion, and the two share one $\mu$ sieve. The
split between "small $q$, loop over them" and "small $c$, count the $q$" is the
[hyperbola method](/topics/technique/dirichlet-hyperbola-method). Whenever a condition reads "an
even (or odd) number of distinct primes", rewrite it as $\mu = \pm 1$ and count it as half of
$Q \pm M$.

## As a filter

Problem 357 asks for $n$ such that $d + n/d$ is prime for every divisor $d$. If $p^2 \mid n$, take
$d = p$. Then $p$ divides both $d$ and $n/d$, so $p + n/p$ is a multiple of $p$ larger than $p$,
which is composite. **Square-free is necessary**, and checking it costs nothing because you are
factoring $n$ anyway: the moment trial division divides out a prime and can divide again, drop
the candidate. The survivors pay back immediately. Their divisors are exactly the $2^{\omega(n)}$
subset products of the distinct primes, built by doubling a list one prime at a time, with no
divisor search. This is the general use: when a property must hold "for every divisor", test
square-freeness first and get the subset structure for free.

Problem 203 asks which entries in the first rows of Pascal's triangle are square-free. The entries
run to fifteen digits, and factoring each one would be wasted work.
[Kummer's theorem](/topics/domain/kummers-theorem) says the exponent of $p$ in
$\binom{n}{k}$ is the number of carries when adding $k$ and $n-k$ in base $p$. So
"$p^2 \mid \binom{n}{k}$" is "at least two carries", decided digit by digit and abandoned at the
second carry. The test is about the *number's prime exponents*, never the number, which is the
[p-adic](/topics/domain/p-adic-valuation) view of square-freeness: $v_p(n) \le 1$ for all $p$.

## C and Python

The algorithms match one for one. The differences come from what each language makes cheap.

- **The $\mu$ table.** Both sides store $\mu$ in a byte (`np.int8` / `signed char`). Python sieves
  it with strided slice assignment (`mu[p::p] *= -1`, then `mu[p*p::p*p] = 0`); C writes the same
  two strided loops by hand. For 193's final sum, Python evaluates
  $\mu(d)\lfloor x/d^2 \rfloor$ as a vectorised dot product in fixed-size chunks of $d$, so the
  `int64` temporaries stay bounded ($d^2 \le 2^{50}$ fits comfortably). C runs a scalar loop and
  skips the $\mu(d) = 0$ terms, about 39% of them, with a branch.
- **The square root.** Python has `math.isqrt`, which is exact. C takes `sqrt`/`sqrtl` and then
  nudges the result up and down with integer checks (193, 745). Near $2^{50}$ a floating-point
  root can be off by one, and an off-by-one at $\sqrt x$ silently drops or double-counts the last
  $\mu(d)$ term. In 641 the input $10^{36}$ does not fit in 64 bits at all, so C parses it into an
  `unsigned __int128` and takes the root there. Everything after $\sqrt n = 10^{18}$ fits in a
  `uint64_t` again.
- **Dedup without a set.** 203 sums *distinct* square-free entries, since $\binom{n}{k}$ repeats
  across rows. Python drops them into a `set[int]`. C has no hash set, so it collects the values
  as GMP `mpz_t`s, sorts them, and sums each run of equal values once. Sort-then-unique is the
  standard C substitute for a set when you only need the result once.
- **Fixed-size divisor buffers.** In 357, Python grows the subset-product list with
  `divisors += [d * p for d in divisors]`. C uses a stack array `divisors[256]`, which is safe
  because $2 \cdot 3 \cdot 5 \cdots 23 > 10^8$, so no square-free $n$ in range has more than eight
  primes and $2^8 = 256$ subsets.
- **Modular overflow.** 745's sum is taken modulo a prime near $10^9$. Python's integers absorb
  the products. C keeps $h$ and each quotient reduced below the modulus so their product fits in
  64 bits, and goes through `__int128` only inside the modular exponentiation.

## How to reason about it

- **Spot the core.** If a problem talks about squares dividing $n$, the largest square factor, or
  a "squarefree part", write $n = s^2 k$ straight away and ask whether the sum regroups by $s$.
  It usually does, and the square-free count $Q$ or a convolution with $\mu$ falls out.
- **Count with the identity, enumerate with the structure.** For *how many*, use
  $\sum_d \mu(d)\lfloor x/d^2\rfloor$ at $O(\sqrt x)$. To *walk* the numbers of a shape
  (powerful, cube-full, $a^2 b^3$), parametrise them with square-free factors and loop. Filtering
  every integer up to $x$ is the wrong order of magnitude either way.
- **Test cheaply.** A full factorisation answers square-freeness as a by-product, but often you
  can stop early: at the first repeated prime in trial division, at the second carry in Kummer, or
  with a sieve flag when a whole range is involved. Testing small squares $p^2$ alone is not a
  test, because a large prime can still appear squared.
- **Mind the edges.** $1$ is square-free ($\mu(1) = 1$), and $0$ is not (every square divides
  it). A sieve that leaves `mu[0] = 1` adds a phantom square-free number to every prefix count.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ○ [0273](/solutions/0273/) — Sum of Squares
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ○ [0362](/solutions/0362/) — Squarefree Factors
- ○ [0399](/solutions/0399/) — Squarefree Fibonacci Numbers
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0556](/solutions/0556/) — Squarefree Gaussian Integers
- ○ [0580](/solutions/0580/) — Squarefree Hilbert Numbers
- ○ [0591](/solutions/0591/) — Best Approximations by Quadratic Integers
- ○ [0632](/solutions/0632/) — Square Prime Factors
- ○ [0633](/solutions/0633/) — Square Prime Factors II
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0745](/solutions/0745/) — Sum of Squares II
- ○ [0864](/solutions/0864/) — Square + 1 = Squarefree

<!-- /problems -->
