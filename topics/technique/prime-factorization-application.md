<!-- tags: [prime-factorization-application] -->
<!-- status: final -->
# Prime factorization (application)

The [Prime Numbers](/topics/number-theory/prime-numbers) page explains *why* factorisation matters.
The [fundamental theorem of arithmetic](https://en.wikipedia.org/wiki/Fundamental_theorem_of_arithmetic)
makes the exponent vector of $n = \prod p_i^{e_i}$ the true shape of a number. That page also covers
the [algorithms](https://en.wikipedia.org/wiki/Integer_factorization) that recover the vector. This
page is about what a solution *does* once it holds one. The problems below fall into five moves,
and the work in each one is choosing the move, not running the factoriser. Each is a way of
replacing arithmetic on a large or awkward number with arithmetic on a short list of
`(prime, exponent)` pairs.

## Move 1 — a canonical key: compare numbers without building them

Two integers are equal exactly when their factorisations are equal. That makes the factorisation a
perfect hash key for numbers you would rather not build. Problem 29 counts the distinct values of
$a^b$. At the stated bounds ($a, b \le 100$) the big integers are cheap, but past a few hundred
they run to thousands of digits. Factoring $a$ once gives $a^b$ for free, because exponents scale:
$a^b = \prod p_i^{e_i b}$. The public solution `solutions/public/p0029/p0029_s0.py` keys a set on
that signature:

```python
prime_factors = prime_factorization(a)
for b in range(b_min, b_max + 1):
    unique_powers.add(tuple((prime, power * b) for prime, power in prime_factors))
```

The key is correct because trial division returns primes in increasing order, so equal numbers
always produce *identical* tuples. Any factoriser that emits primes in a different order would need
a sort before hashing. This is where the two languages differ most. Python hashes the tuple
directly. C has no tuple type and no built-in set, so `p0029_s0.c` serialises the signature into a
`"p:e,p:e"` string and inserts it into a hand-rolled chained hash table (djb2, power-of-two buckets).
The canonical-order requirement is the same in both, but in C it is also a *string-format* contract:
the separators keep `2:12` and `21:2` apart. The `s1` variants change only the factoriser: they
trial-divide by a `primesieve` list instead of every integer.

## Move 2 — read a multiplicative function off the exponents

Once you have the exponents, a [multiplicative function](/topics/domain/multiplicative-function)
costs one product. Problems 108 and 110 both reduce $\tfrac1x + \tfrac1y = \tfrac1n$ to
$(x-n)(y-n) = n^2$. The solutions are then the divisor pairs of $n^2$, numbering
$\lceil \tau(n^2)/2 \rceil$, and squaring $n$ only doubles the exponents:

$$\tau(n^2) = \prod_i (2e_i + 1).$$

Neither solution ever forms $n^2$ or lists a divisor. Problem 108 scans $n$ upward, factors each by
trial division and multiplies the $(2e+1)$ terms as it peels off primes. A leftover cofactor is a
prime at exponent 1 and contributes a final factor of $3$. The C port is a line-for-line mirror; at
this size nothing overflows and no data structure is needed. See the
[divisor function](/topics/domain/divisor-function) page for the wider family.

## Move 3 — construct the factorisation instead of factoring

When the question asks for the *least* $n$ with some multiplicative property, factoring candidates
is backwards. Search the exponent vectors directly and multiply them out. Problem 110 is problem 108
with a threshold so high that the scan is hopeless. Two exchange arguments shape the search space:
the least $n$ uses the *smallest* primes, and gives them *non-increasing* exponents. Swapping a
larger exponent onto a smaller prime keeps $\tau$ the same and makes $n$ smaller. What is left is a
depth-first search over exponent multisets on $2, 3, 5, \dots, 59$, cut by the incumbent and a
reachability bound. That bounding argument belongs to [branch-and-bound](/topics/technique/branch-and-bound); what
belongs here is that the search object *is* a factorisation. Python's unbounded integers let it
multiply freely. The C port must check every `n * p^e` against `best / pe` *before* multiplying,
because signed overflow is undefined. It also seeds `best` from the product of the first $k$ primes
so that those guards cut branches from the first leaf.

Problem 347 builds numbers from a prescribed *prime support*. It asks for the largest
$p^a q^b \le N$ that has exactly the two primes $p, q$. Nothing gets factored. The solution walks
each prime pair with $pq \le N$ (so $p \le \sqrt N$) and climbs the two power ladders. It
deliberately iterates the shorter ladder of the larger prime on the outside. Both languages take
the primes from `primesieve` up to $N/2$; C asks for `uint64_t` primes so that the ladder products
stay in range.

## Move 4 — enumerate divisors from the factorisation

A divisor is a choice of exponent $0 \le f_i \le e_i$ for each prime. Factor once, take the
Cartesian product, and you have every divisor without trial dividing $n$ by anything.
Problem 221 needs every factorisation $d_1 d_2 = p^2 + 1$, which comes from the parametrisation
$A = p(p+d_1)(p+d_2)$. Its factoriser uses a number-theoretic shortcut worth stealing: an odd prime
$q$ can divide $p^2 + 1$ only if $-1$ is a quadratic residue mod $q$. By
[Fermat's two-squares](https://en.wikipedia.org/wiki/Fermat%27s_theorem_on_sums_of_two_squares)
reasoning, that means only $q \equiv 1 \pmod 4$. So the trial-division list is the primes
$\equiv 1 \pmod 4$ plus $2$, which is about half the primes. *Know which primes can appear* before
you trial-divide. Python grows the divisor list by comprehension and collects the values of $A$ in a
`set`. C computes each $A$ in `__int128` before comparing it with the bound, appends to a growable
array, and gets distinctness from `qsort` plus a dedupe pass instead of a hash set.

Problem 545 combines moves 2 and 4. By the
[von Staudt–Clausen theorem](/topics/domain/von-staudt-clausen-theorem), the denominator of the
[Bernoulli number](/topics/domain/bernoulli-number) $B_k$ is $\prod_{(p-1) \mid k} p$. So "the
denominator equals a given squarefree target" becomes a condition on the divisor set of $k$: the
divisors $d$ with $d+1$ prime must be exactly $\{p - 1 : p \mid \text{target}\}$. Every valid $k$ is
then a multiple of the lcm of that set. The solution scans $k = \text{step}\cdot t$, gets the
factorisation of each $k$ by merging the precomputed factorisation of `step` with that of $t$, and
rejects as soon as some divisor admits an extra prime. Factoring $t$ uses a
[smallest-prime-factor sieve](https://cp-algorithms.com/algebra/prime-sieve-linear.html), which
peels a number in $O(\log t)$ divisions. That is the right tool when *every* integer in a range
needs its factorisation; trial division is right only for the occasional one. The C side differs in
two ways. It walks the divisors with an odometer over the exponent indices instead of building a
list, and its Miller–Rabin test multiplies in `__int128` where Python's `pow(a, d, n)` just works.

## Move 5 — split a coprime product across the prime powers

If $m \mid s(s-1)$, then because $\gcd(s, s-1) = 1$, each prime power $p^e \,\|\, m$ must divide
*all of* $s$ or *all of* $s-1$; it can never split between them. Factoring $m$ into $k$ distinct
prime powers therefore yields exactly $2^k$ residues $r \bmod m$ with $r(r-1) \equiv 0$, one for each
way of assigning the prime powers. The
[Chinese Remainder Theorem](/topics/technique/chinese-remainder-theorem) assembles each one. These are the
idempotents of $\mathbb{Z}/m$. Problem 932 looks for numbers whose digit split $a \| b$ satisfies
$a\|b = (a+b)^2$. Setting $s = a+b$ turns this into $m \mid s(s-1)$ with $m = 10^d - 1$. The
factorisation of $10^d - 1$ turns a scan over $s$ into a stride-$m$ walk from a handful of residues
inside a narrow window. Python's three-argument `pow(m1, -1, m2)` supplies the CRT inverse. C writes
an extended-Euclid `modinv`, and computes the window's discriminant in `__int128` because
$(m+1)^2$ overflows 64 bits once $d$ approaches $10$.

## Which factoriser, and when to skip it

| Need | Tool | Seen in |
|---|---|---|
| A few small numbers | Plain [trial division](/topics/technique/trial-division) to $\sqrt n$ | 29, 108, 932 (and 545's target) |
| Many numbers, a prime list at hand | Trial division by sieved primes only | 29 `s1` |
| Prime factors restricted by theory | Trial division over the admissible residue class | 221 |
| Every integer in a range | Smallest-prime-factor sieve, $O(\log n)$ each | 545 |
| The least $n$ with a given shape | Don't factor — enumerate exponent vectors | 110, 347 |

Two habits run through all of these. First, keep the factorisation as the working representation
and convert back to an integer only at the end. Products, divisors, keys and residues are all
cheaper on the pairs. Second, when the question is an *inverse* one ("find $n$ such that
$f(n) = \dots$"), ask whether the answer's factorisation can be built directly. The
[Prime Numbers](/topics/number-theory/prime-numbers) page carries that inverse idea further, to the
totient and abundancy searches of problems 241, 245 and 248.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0932](/solutions/0932/) — $2025$

<!-- /problems -->
