<!-- tags: [math-gcd] -->
<!-- status: final 2026-10-30T06:36Z -->
# math.gcd

[`math.gcd`](https://docs.python.org/3/library/math.html#math.gcd) and its partner
[`math.lcm`](https://docs.python.org/3/library/math.html#math.lcm) are the library side of the
[greatest common divisor](/topics/domain/greatest-common-divisor). That page covers the theory:
why Euclid's algorithm is correct, why it's logarithmic, and what the gcd *means* in a problem.
This page is about the call itself. What the Python functions accept and return, what I write in C
where there is no such function, and the one situation where it's worth replacing Euclid with
something cleverer. In most of the problems below, the gcd is never the answer. It's a guard (is
this pair coprime?), a normaliser (put this fraction in lowest terms) or a detector (does this
product share a factor with `n`?), called many times inside a loop. That's why the details of the
call matter. The one exception, Problem 443, puts the gcd in the statement itself, and there the
lesson runs the other way: the fastest gcd is the one an identity lets you skip.

## What the Python functions promise

Both functions have been **variadic** since Python 3.9, and their edge cases are defined so that
folding works without special-casing:

| call | result | why it's useful |
| --- | --- | --- |
| `gcd(a, b, c, …)` | `gcd(gcd(a, b), c)…` | no `functools.reduce` needed |
| `gcd()` | `0` | the identity element: `gcd(0, x) = x` |
| `gcd(-12, 18)` | `6` | always non-negative, whatever the signs |
| `gcd(0, 0)` | `0` | no exception to catch |
| `lcm(a, b, c, …)` | `lcm(lcm(a, b), c)…` | same fold, other operation |
| `lcm()` | `1` | the identity element for lcm |
| `lcm(0, x)` | `0` | zero is a multiple of everything |

The arguments must be integers. `gcd(2.0, 4)` raises `TypeError`, which is the correct behaviour,
because a float gcd would be meaningless after rounding. If you have rationals, use
[`fractions.Fraction`](https://docs.python.org/3/library/fractions.html), which calls the same gcd
internally to keep itself in lowest terms.

[Problem 5](/solutions/0005/) is the textbook lcm fold. The published solution spells it out
because it predates the variadic form:

```python
functools.reduce(lambda x, y: x * y // math.gcd(x, y), range(2, n + 1), 1)
```

Today this is `math.lcm(*range(1, n + 1))`. That reads better, and it's faster, because the loop
runs in C rather than calling a Python lambda for every element. The same goes for
`gcd(*values)` compared with `reduce(gcd, values)`. A variadic gcd also stops early in practice: once
the running value reaches 1, every later step is a single cheap division.

For a single pair, `math.gcd(a, b)` is always the right call in Python. The three-line `while b:`
loop gets interpreted one bytecode at a time, and for large integers CPython switches to
[Lehmer's algorithm](https://en.wikipedia.org/wiki/Lehmer%27s_GCD_algorithm). Lehmer runs most of
the Euclid steps on machine-word approximations of the leading digits, so it does far fewer
big-number divisions. You won't beat that by hand.

## In the problems: guard, normaliser, detector

Every use in the problems below is one of three patterns.

**The coprimality guard.** You generate a parametrised family over pairs `(m, n)` and skip the
pairs that would produce a scaled duplicate:

```python
if math.gcd(m, n) != 1:
    continue
```

[Problem 39](/solutions/0039/) and [Problem 139](/solutions/0139/) use this test on Euclid's
formula for Pythagorean triples. [Problem 141](/solutions/0141/) uses the same test on the ratio
`p/q` of a geometric progression: the progression only counts once if that ratio is in lowest
terms. The gcd here is cheap compared with the work it lets you skip. Still, when there's a cheaper
test, put it first. A parity check like `(m - n) % 2` is one operation. In
[Problem 139](/solutions/0139/), ordering the parity test before the gcd skips the gcd on about half
the pairs.

**The normaliser.** You keep an exact rational as an integer pair and divide both parts by their gcd
after every operation, so that equal values have equal representations. [Problem 155](/solutions/0155/)
counts the distinct capacitances you can build from series and parallel combinations. Every
combination produces a fraction, and those fractions go into a set. The set only deduplicates
correctly if each fraction is reduced to `(n/g, d/g)` before it's inserted. Otherwise `2/4` and
`1/2` would be counted as two values. [Problem 175](/solutions/0175/) and
[Problem 236](/solutions/0236/) start the same way: reduce the target ratio first, because the rest
of the method assumes it's in lowest terms. [Problem 183](/solutions/0183/) uses the
normaliser for a decision rather than for storage. Dividing `k` by `gcd(N, k)` gives the reduced
denominator of `N/k`, and whether that fraction has a terminating decimal depends only on that
denominator's prime factors.

When a pair of small arguments comes up millions of times, use a table: build `g[i][j]` once and
look values up instead of calling gcd. [Problem 504](/solutions/0504/) does this. It needs four gcds
per quadrilateral across `m⁴` shapes, but only `m²` distinct pairs. Following the house rule, the
table is built inside `solve()`, sized to `m`, so its cost is part of the timing.

**The detector.** In [Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm),
the gcd is how a factor is *noticed*. The walk produces differences `x − y`, and a non-trivial
`gcd(x − y, n)` is a factor of `n`. Testing each difference costs one gcd per step, so
[Brent's variant](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm#Variants) multiplies a batch of
them together mod `n` and takes one gcd of the product:

```python
q = q * abs(x - y) % n      # 128 of these…
g = math.gcd(q, n)          # …then one gcd
```

A product shares a factor with `n` as soon as any of its terms does, so the batch loses nothing
except, rarely, overshooting to `g == n`. The algorithm then backtracks and replays that batch one
gcd at a time. This is the factoriser inside [Problem 443](/solutions/0443/). Batching turns
the gcd from the dominant cost of each step into a rounding error.

## Reasoning the call away

[Problem 443](/solutions/0443/) defines a sequence by `g(n) = g(n−1) + gcd(n, g(n−1))` and asks for
a term near `10¹⁵`. Calling the gcd once per term is out of the question, however fast the call.
What saves it is the identity behind Euclid's algorithm, `gcd(a, b) = gcd(a, b − a)`. Write
`g(k) = k + d`. While every gcd is 1, the offset `d` stays put, and the next step's gcd is
`gcd(j, j − 1 + d) = gcd(j, d − 1)`. The second argument no longer moves. So the run of `+1` steps
ends exactly at the first `j` that shares a prime with the fixed number `d − 1`, and that index
can be computed from the factorisation instead of searched for. A quadrillion gcds become a few
hundred factorisations, each one a call to the detector above.

The same move applies whenever a gcd's arguments drift together. Subtract one from the other
(or reduce mod it) and check whether what's left is constant over a stretch. If it is, the gcd
over that stretch is a question about divisibility by fixed primes, and you can jump to the next
place it changes.

## The C counterpart

C has no gcd in its standard library, and neither GCC nor Clang offers a builtin for it. C++17 has
[`std::gcd`](https://en.cppreference.com/w/cpp/numeric/gcd) in `<numeric>`, but C doesn't. So every
C solution here carries its own copy of the same loop. This one is from Problem 39:

```c
static int gcd(int a, int b) {
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}
```

The Python guarantees in the table above don't come with it. Two of them are worth restoring
deliberately:

- **Signs.** In C, `%` truncates toward zero, so `gcd(-12, 18)` from this loop returns `-6`
  (the [modulo](/topics/technique/modulo) page covers why). Every caller in these problems passes
  non-negative values, so the loop is fine as written. If you can't promise that, take absolute
  values first, or better, use `unsigned` or `uint64_t` types so the question can't come up.
  Careful with `abs(INT_MIN)`: it overflows.
- **lcm overflow.** `a * b / gcd(a, b)` overflows long before the lcm itself does. Divide first,
  `a / gcd(a, b) * b`. The division is exact, and the intermediate value never exceeds the
  result. Problem 5's C solution has to go further: the lcm of 1 through n stops fitting in 64 bits
  for quite small n, so it keeps the running value as a hand-rolled big integer. Because each new
  factor `y` is small, `gcd(big, y)` reduces to `gcd(big mod y, y)`, and only the remainder ever
  needs the word-sized gcd.

## When a binary gcd pays off

[Stein's binary gcd](https://en.wikipedia.org/wiki/Binary_GCD_algorithm) replaces the division
with shifts and subtractions. It relies on three facts: `gcd(2a, 2b) = 2·gcd(a, b)`, a factor of 2
that only one argument has can be dropped, and for two odd numbers `gcd(a, b) = gcd(|a − b|, min)`.
Combined with a count-trailing-zeros instruction, which strips all the factors of 2 in one step,
it looks like this:

```c
static uint64_t gcd_binary(uint64_t a, uint64_t b) {
    if (a == 0) return b;
    if (b == 0) return a;
    int k = __builtin_ctzll(a | b);      /* shared power of two */
    a >>= __builtin_ctzll(a);
    do {
        b >>= __builtin_ctzll(b);
        if (a > b) { uint64_t t = a; a = b; b = t; }
        b -= a;
    } while (b);
    return a << k;
}
```

The case for it is that 64-bit integer division is one of the slowest common instructions. Each
Euclid step pays tens of cycles of latency, more on older x86 cores. Each binary step costs a few
single-cycle operations, so even though the binary version needs more steps, it often finishes
first on full-width 64-bit operands. That's why recent versions of libstdc++ (GCC 11 onward)
implement `std::gcd` as a binary gcd.

In practice, it's rarely the change that matters:

- **Only when the gcd is the hot loop.** If a profile doesn't show the gcd dominating, swapping it
  for a binary version saves a fraction of a fraction. In every problem on this page, the gcd is a
  guard next to heavier work. Even Problem 443's Pollard rho, whose gcds take full 64-bit
  operands, batches them so that the modular multiplications dominate.
- **Only in C.** In Python, `math.gcd` is already compiled C, so a hand-written binary gcd in Python
  would be far slower.
- **Mostly for wide operands.** With small arguments, as in Problem 39 where `m, n < 30`, Euclid
  finishes in two or three steps, and nothing is going to beat that by much.
- **A table beats both.** If the arguments are bounded and repeat, as in Problem 504, a lookup
  avoids the computation entirely.
- **Generating less beats all three.** The domain page's closing point applies here too: a
  `gcd == 1` filter keeps about 61% of random pairs, so most of the time goes into the pairs you
  keep, not into the gcds. If speed matters, enumerating only coprime pairs (a Stern–Brocot or
  Farey walk, or a tree of primitive triples) removes the guard altogether.

So: call `math.gcd` and `math.lcm` in Python and use the variadic form. In C, write the plain Euclid
loop with unsigned types and divide before you multiply. Use a binary gcd only after a profile has
pointed at the gcd, and check first whether a table or a smarter enumeration would remove the call
entirely.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0443](/solutions/0443/) — GCD Sequence
- ● [0504](/solutions/0504/) — Square on the Inside

<!-- /problems -->
