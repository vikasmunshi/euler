<!-- tags: [generate-and-test] -->
<!-- status: final -->
# Generate and test

[Generate and test](https://en.wikipedia.org/wiki/Generate_and_test) is the most honest algorithm
there is: enumerate candidates, apply the defining property to each, keep the survivors. It recurs
across the problems below because a Project Euler statement is usually a *definition* — "numbers
that are the sum of the fifth powers of their digits", "primes remaining prime when truncated" —
with no constructive characterisation attached. What is worth noticing is that almost none of these
solutions is a plain loop over `range(N)`. The predicate is handed to you; the entire craft is in
the generator.

## The shape

```python
return str(sum(x for x in candidates() if predicate(x)))
```

Cost is $|\text{candidates}| \times \text{cost(test)}$, and the first factor is the one that moves.
Speeding up the test buys a constant; shrinking the stream changes the exponent. So the useful
question is never "how do I test faster" but "what am I generating that could not possibly pass".

## Shrinking the generator

**Bound the search, and prove the bound.** Problem 30 asks for numbers equal to their own digit
fifth-power sum and the statement is silent about how far to look. The solution derives the ceiling
before it loops — a $d$-digit number is at least $10^{d-1}$, while its digit $n$-th power sum is at
most $d \cdot 9^n$, so beyond a certain width the number outruns any sum it could produce:

```python
upper_bound_num_digits = math.ceil(math.log(n * 9**n, 10))
```

Without that line the search does not terminate. With a lazily generous one it terminates and
wastes most of its time. Problem 119 does the same arithmetic in reverse — a $d$-digit number has
digit sum at most $9d$, which caps the base — and problem 200 sidesteps the derivation by growing
its ceiling tenfold until enough survivors appear, which is the honest fallback when no clean bound
exists.

**Generate the shape, not the space.** If the property constrains the *form* of a candidate, build
the form directly. Problem 36 wants numbers palindromic in base 10 and base 2; it emits only decimal
palindromes, by mirroring each left half:

```python
for digits in range(1, 10 ** (max_digits // 2)):
    digits_str = str(digits)
    digits_rev = digits_str[::-1]
    yield int(digits_str + digits_rev)
```

That is $O(\sqrt N)$ candidates instead of $N$, and the decimal half of the test disappears entirely
— every emitted value passes it by construction. Problem 30 plays the same card on a different axis:
a digit-power sum does not depend on digit order, so it enumerates sorted digit *multisets* with
`itertools.combinations_with_replacement` and tests each multiset once rather than once per
permutation.

**Generate answers, not candidates.** The largest single lever, and the least obvious. Problem 119
wants numbers that are a power of their own digit sum; scanning integers and asking "is this a
power?" is far harder than enumerating $b^e$ and asking "is the digit sum $b$?". Problem 346 wants
values that are repunits in more than one base, so it generates repunits per base rather than
testing integers. Problem 87 sums $p^2 + q^3 + r^4$ over sieved primes instead of factoring
candidates. In each case the expensive direction of the property is replaced by the cheap one.

**Constrain the parts jointly.** Problem 32 wants a multiplicand, multiplier and product that
together use 1–9 exactly once. Counting digits shows only the $(1,4)$ and $(2,3)$ operand splits can
work, and the second operand's digits are drawn from what the first leaves unused, so no candidate
is ever built that repeats a digit. Problem 41 prunes by digit sum modulo 3 — of the nine pandigital
lengths only 7 and 4 can contain a prime at all — and never runs a primality test on the other
seven.

**Pre-sieve with a wheel.** When the test is genuinely expensive, filter on cheap arithmetic
structure first. Problem 146 keeps only residues modulo $2 \cdot 3 \cdot 5 \cdot 7 \cdot 11 \cdot 13$
that could possibly yield its six primes, prunes further with boolean residue tables for the primes
up to 37, and only then reaches
[Miller–Rabin](/topics/technique/miller-rabin-primality-test) — a tiny fraction of the range
survives that far. Problem 206 does the arithmetic version: the answer's fixed digit pattern pins
the square between two known bounds, and only two residue classes modulo 10 can produce the required
last digit, so the search steps by 10 across an interval already narrowed by
[integer square roots](/topics/technique/integer-square-root).

## Ordering, which is free

**Cheapest filter first.** Problem 104 needs a Fibonacci number pandigital in both its first and last
nine digits. The tail is cheap — one addition modulo $10^9$, carried along the loop; the head needs
logarithms. So the tail test gates the head test, and the float work runs on a handful of indices
instead of all of them. Problem 35 checks that a prime's digits avoid `024568` before rotating it,
and problem 111 tests digit *shapes* before primality. Ordering a filter chain by ascending cost is
the reliable free win here — see [cheap checks first](/topics/takeaway/cheap-checks-first).

**Order the stream so the first hit is the answer.** Problem 41 wants the *largest* pandigital prime,
so it generates descending and takes `next()`:

```python
pandigital_primes = (
    number
    for length in (7, 4)
    for number in gen_n_digit_pandigital_numbers(length, descending=True)
    if fast_is_prime(number)
)
return str(next(pandigital_primes))
```

Because the [generator](/topics/technique/generator) is lazy, nothing past the first survivor is
ever computed — the search is over at its first success rather than at the end of the range.
Problem 111 uses the same trick one level up, descending the repeated-digit count and stopping at
the first level that yields any prime at all.

**Let the generation order make the test cheap.** Problem 37 is the elegant case. Truncatable primes
are tested against *smaller* primes, and primes are generated in increasing order, so every proper
truncation of a candidate has already been seen:

```python
primes.add(prime)
if not any(
    (pl not in primes or pr not in primes for pl, pr in [(prime[i:], prime[:i]) for i in range(1, len(prime))])
):
```

Each test is a handful of [set](/topics/technique/set) lookups rather than a handful of primality
tests. The generator's *order* is what makes the predicate cheap — a dependency worth looking for
whenever the property refers to smaller members of the same family.

## How to reason about it

- **Reach for it first, and keep it.** It is correct by construction and easy to check by hand, which
  makes it the reference implementation for whatever clever thing replaces it. Problem 85 recomputes
  an exact rectangle count for every grid shape although the closed form is elementary; several
  problems here keep a `brute.py` next to the fast solution for exactly this reason.
- **Know when it stops being a plan.** Problem 59 is the miniature: a repeating-key XOR with a
  $k$-byte lowercase key is $26^k$ candidates, which is hopeless — until you notice the ciphertext
  splits into $k$ independent single-byte ciphers, each solvable by scoring 26 options. That is not a
  faster test, it is a decomposition, and it turns an exponential search into $k$ linear scans. When
  the candidate space grows faster than your bounds shrink it, stop tuning the loop and look for the
  structure that factors it.
- **Deduplicate deliberately.** Enumerating over a parametrisation usually reaches the same value by
  several routes. Problems 32, 87, 141 and 346 all collect into a
  [set](/topics/technique/set) and answer with `sum(set(...))` or `len(set(...))`, which is
  cheap insurance against a double count that is otherwise almost invisible.
- **Prune inside the loop nest, not after it.** Problem 87's nested prime loops break as soon as a
  partial sum exceeds the budget, so the nominally cubic search visits only productive triples.
  Problem 88 prunes its recursive factorisation against a running best. A break in the outer loop is
  worth a thousand tests in the inner one.
- **A bound you cannot justify is a bug you cannot see.** The failure mode of this technique is not
  slowness, it is a search window that quietly excludes the answer — and the program still prints a
  number. Every ceiling in these solutions carries a comment explaining why nothing above it can
  qualify; write that comment, and if you cannot, widen the window and pay for it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0059](/solutions/0059/) — XOR Decryption
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0757](/solutions/0757/) — Stealthy Numbers

<!-- /problems -->
