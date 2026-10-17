<!-- tags: [primality-test] -->
<!-- status: final -->
# Primality test

A [primality test](https://en.wikipedia.org/wiki/Primality_test) decides whether a number is
prime. The problems below all ask that question many times, and what separates fast solutions from
slow ones is less the test than the choice of *which* test, applied to *which* candidates. The
mechanics of the workhorse are on the
[Miller–Rabin page](/topics/technique/miller-rabin-primality-test): strong pseudoprimes, the
deterministic witness tables, the overflow in C. This page covers the decision around it. How do the
candidates arrive? What does a single verdict actually cost? And when should you skip testing and
let one old fact settle the question for you?

## One fact under every method

Every method here rests on the same observation: **a composite `n` has a prime factor no larger
than `√n`**. [Trial division](/topics/technique/trial-division) applies it directly: divide by
every prime up to `√n`, and if nothing divides, `n` is prime. The
[Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) turns it around: instead of asking
each number about its factors, each prime up to `√N` crosses off its multiples. Whatever survives
has no small factor, so it is prime. Miller–Rabin is the exception. It never looks for a factor. It
checks a property that every prime has and that almost no composite fakes, which is why its cost
grows with `log n` and not with `√n`.

The unsolved problem 574 shows how far the `√n` fact reaches. Its statement turns that fact into a
*certificate*. Take a prime `q` and coprime `A, B` whose product is divisible by every prime below
`q`. Each such prime then divides exactly one of `A` and `B`, so it cannot divide `A + B` or
`A − B`. Neither number has a prime factor below `q`, so if one of them is greater than 1 and below
`q²`, it must be prime. This is the same idea as trial division, packed into a short certificate.
The general name for this is a
[primality certificate](https://en.wikipedia.org/wiki/Primality_certificate): data that lets a
reader confirm primality faster than the writer could find it.

## Match the method to how the candidates arrive

The useful question is not "how big is `n`?" but "what shape is the set of numbers I must judge?"

| Candidates | Method | Covered problems |
| --- | --- | --- |
| Every integer in `[2, N]`, `N` affordable to allocate | sieve, then `O(1)` lookups | the sieve half of 200 and 293 |
| A few large numbers, scattered or algebraically generated | deterministic Miller–Rabin | 111, 146, 200, 293 |
| Every value `f(n)` of a polynomial, for `n` up to `N` | **sieve in index space** | 216 |
| One number to *certify*, not just decide | a certificate | 574 |

The third row is what this page adds. Problem 216 counts the primes among `t(n) = 2n² − 1` for
`n` up to 5·10⁷. The values reach about 5·10¹⁵, far beyond any integer sieve. Testing them one by
one means fifty million modular exponentiations, each with an exponent of about 50 bits. That is
seconds in C and far too slow in Python. The solution inverts the question. A prime `p` divides
`t(n)` exactly when `n² ≡ 2⁻¹ (mod p)`. That congruence depends only on `n mod p`, so the indices `n`
it marks form at most two arithmetic progressions, and those can be struck from a boolean array
indexed by `n`. Two facts make it cheap:

- [Quadratic reciprocity](/topics/domain/quadratic-reciprocity) says the congruence has roots only
  for `p ≡ ±1 (mod 8)`. Half the primes drop out on a bit test.
- The root itself takes one
  [Tonelli–Shanks](/topics/technique/tonelli-shanks-algorithm) call per prime. When
  `p ≡ 3 (mod 4)`, which covers every `p ≡ 7 (mod 8)`, it is a single
  [modular exponentiation](/topics/technique/modular-exponentiation).

The `√n` fact sets the sieving bound: primes up to `√t(N) ≈ √2·N`, about 7·10⁷. The whole job is
`O(N log log N)`, with no primality test in it at all. There is one boundary case, and it is the
same one an integer sieve meets at `p` itself. When `t(n) = p`, the first index `p` would strike is
a prime value, so the strike has to start one period later. This technique,
[polynomial sieving](https://en.wikipedia.org/wiki/Quadratic_sieve#The_approach), is worth
reaching for whenever the candidates are the values of a fixed polynomial over a dense range of
indices.

## A verdict's cost depends on the answer

Miller–Rabin is asymmetric. A composite is almost always rejected by the **first** witness, after a
single `pow`. A prime has to pass **every** witness in the set. So the work a loop does depends on
how many *primes* it finds, not on how many candidates it tests. The covered problems sit at
different points on that scale:

- **293** walks up from `N + 3` in steps of 2 and stops at the first prime. Each admissible `N`
  pays for a few quick rejections and exactly one full prime verdict. With a few thousand `N`
  values, that is tiny.
- **200** asks whether a number is *prime-proof*: no single-digit change makes it prime. Nearly
  every edited value is composite and is rejected cheaply. The search stops at the first prime
  edit, so a candidate that fails usually fails early. Only the rare true prime-proof number pays
  for every edit.
- **111** wants primes, so many of the generated digit patterns pay for all twelve bases. Here the
  generator, which builds only numbers with the required run of repeated digits, does the work of a
  filter.
- **146** needs six simultaneous primes, `n² + 1, 3, 7, 9, 13, 27`. A survivor pays for six full
  verdicts, which is why the solution filters so hard with residues first. It also needs the
  primes to be *consecutive*, so it must prove the numbers in between composite. Residues rule out
  most of the in-between offsets, and only `n² + 19` and `n² + 21` need an actual test. A residue
  argument settles a composite verdict without any test at all. That is the
  [cheap-checks-first](/topics/takeaway/cheap-checks-first) takeaway at its sharpest.

If profiling shows the test dominating, first check whether the loop is paying for prime verdicts
it did not need. Ordering the checks so the likeliest composite comes first, or stopping at the
first prime, often helps more than a faster `pow`.

## C and Python

The algorithm is the same in both languages. The arithmetic and the array handling differ.

- **Products.** Python's `pow(a, d, n)` and `x * x % n` are exact at any size. Every C port here does
  its modular multiply through `__int128` (see [int128](/topics/technique/int128)), including 293,
  whose candidates stay below 2³², where an unsigned 64-bit product would already be enough. The
  same goes for 216's Tonelli–Shanks step, whose moduli stay below 7·10⁷, so their products fit
  easily in 64 bits. The wider type is cheap insurance, and it keeps one `mulmod` helper correct
  for every port. Where it is truly required is 111, 146 and 200, whose moduli run to 10¹⁰ and
  beyond.
- **Square roots for bounds.** Python takes `math.isqrt` and gets the exact floor. The C port of
  216 computes `sqrt()` in floating point, then nudges the result up and down with integer
  comparisons. A bound that is off by one either misses the largest prime factor it needs or reads
  past the array.
- **Strikes.** 216 marks its progressions with NumPy slice assignment, `is_t_prime[start::p] =
  False`, and turns its integer sieve into a prime list with `np.flatnonzero`. C does the same work
  with a stride loop over a `calloc`'d `char` array.
- **Digit edits.** 200 builds each one-digit variant by slicing a Python string and calling `int()`.
  The C port copies a `snprintf` buffer, overwrites one character, and calls `atoll`. Both have
  the same leading-zero rule: the first digit never becomes `0`.

For the sieve itself, see the [Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes)
page. For the wider landscape, see [prime numbers](/topics/number-theory/prime-numbers) and
[prime-proof numbers](/topics/domain/prime-proof-number).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ○ [0574](/solutions/0574/) — Verifying Primes

<!-- /problems -->
