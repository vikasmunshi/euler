<!-- tags: [number-theory] -->
<!-- status: final 2026-11-01T14:17Z -->
# Number theory

[Number theory](https://en.wikipedia.org/wiki/Number_theory) is the study of the integers on their
own terms — divisibility, primes, remainders, and the arithmetic functions built on top of them.
With 141 problems it is the third-largest domain tag in the archive, behind only
[combinatorics](/topics/domain/combinatorics) and
[modular arithmetic](/topics/domain/modular-arithmetic), and it is the one most often paired with
something sharper: 35 of these problems also carry `modular-arithmetic`, 23
[prime factorization](/topics/domain/prime-factorization), 21
[Diophantine equation](/topics/domain/diophantine-equation), 21
[multiplicative function](/topics/domain/multiplicative-function), 15
[divisor function](/topics/domain/divisor-function). Those pages describe the *objects*. This one
is about what all 141 have in common — the shape the question takes, and the small set of moves
that turn it from impossible into a few seconds of work.

## The question is almost always a summatory function

Strip the story away and a number-theory problem here nearly always reduces to

$$S(N) = \sum_{n \le N} f(n)$$

for some arithmetic function $f$ — a totient, a divisor count, a radical, an indicator that $n$ is
squarefree — with $N$ chosen large enough that evaluating $f$ once per $n$ is out of the question.
That framing is worth internalising, because it says exactly where the difficulty is. Computing
$f$ at a single point is usually easy and usually irrelevant. It is the $N$ of them that kills
you, and every technique below is a way of not doing them one at a time.

Problem 72 (public, `solutions/public/p0072/`) is the domain in miniature. It asks how many reduced
proper fractions have a denominator up to one million — a question about fractions, with no
$\sum$ in sight. But for a fixed denominator $d$ the numerators that survive reduction are exactly
those coprime to $d$, and counting them *is*
[Euler's totient](/topics/domain/eulers-totient-function) $\varphi(d)$. So the answer is
$\sum_{d=2}^{N} \varphi(d)$, and the entire solve is that recognition; what remains is arithmetic.

Learning to perform that translation — from the problem's language into a sum of a named arithmetic
function — is most of the skill this domain teaches. Problem 243 asks for the first denominator
whose "resilience" drops below a given ratio; resilience is $\varphi(d)/(d-1)$. Problem 179 counts
$n$ where $n$ and $n+1$ have equally many divisors; that is the divisor function $\tau$, twice.
Problem 124 sorts integers by their radical; the radical is a multiplicative function. Once the
function has a name, its literature — and its algorithms — come with it.

Sometimes the translation yields a *description* of the qualifying $n$ rather than a sum. Problem
272 counts the nontrivial cube roots of unity modulo $n$ and asks for every $n \le 10^{11}$ that
has exactly 242 of them. The [Chinese remainder theorem](/topics/technique/chinese-remainder-theorem)
splits a root modulo $n$ into independent roots modulo each prime power, so the count (with $x = 1$
included) is multiplicative. Each unit group modulo an odd prime power is
[cyclic](https://en.wikipedia.org/wiki/Cyclic_group), so it holds $\gcd(3, |G|)$ cube roots.
Together these give exactly $3^k$ roots, where $k$ counts the primes $p \equiv 1 \pmod 3$ dividing
$n$, plus one if $9 \mid n$. The statement's $C(91) = 8$ checks it: $91 = 7 \cdot 13$, $3^2 - 1 = 8$.
"242 roots" therefore means $k = 5$, a condition on *which primes* divide $n$ and on nothing else.
Move 5 below is what you do with a condition like that.

The same CRT split works for any polynomial congruence modulo a composite. Its companion, problem
271, fixes a single $n$ — the primorial up to 43 — and asks for the *sum* of the cube roots rather
than their count. A count is multiplicative, but a sum is not, so this time the roots have to be
built. Find each prime power's roots ([Hensel's lemma](/topics/technique/hensels-lemma) lifts a root mod $p$ to mod $p^k$ whenever the derivative is a unit), then recombine every tuple by
CRT. Problem 407 asks the same question of $a^2 \equiv a$. Since $a$ and $a - 1$ are coprime, each
prime power of $n$ divides one of them completely, so the
[idempotents](/topics/domain/idempotent-ring-element) of $\mathbb{Z}/n$ correspond one-to-one with
the coprime splits $n = d \cdot e$. There are $2^{\omega(n)}$ of them, and the search for the
largest becomes a sweep over coprime pairs. In all three problems the question is about $n$ but the
work is done one prime power at a time.

Problem 531 runs the theorem in the other direction. It builds a system rather than taking one
apart: for each pair $n < m$ in a window just above $10^6$, solve $x \equiv \varphi(n) \pmod n$,
$x \equiv \varphi(m) \pmod m$. Neighbouring integers share factors all the time, so the textbook
coprime CRT does not apply. The
[generalised form](https://en.wikipedia.org/wiki/Chinese_remainder_theorem#Generalization_to_non-coprime_moduli)
does. With $d = \gcd(n, m)$, the system is solvable exactly when $d \mid b - a$, and then it has
one solution class modulo $\operatorname{lcm}(n, m)$. Substituting $x = a + nt$ leaves the
[linear congruence](/topics/domain/linear-congruence-theorem) $(n/d)\,t \equiv (b-a)/d \pmod{m/d}$,
whose coefficient is now a unit. So the consistency test and the solution are one gcd and one
[modular inverse](/topics/technique/modular-multiplicative-inverse-application). A cheap detail
makes them cheaper: $\gcd(n, m) = \gcd(n, m - n)$, and $m - n$ is small inside a narrow window.

## Move 1 — build the whole table in one pass

$\varphi(d)$ for a single $d$ costs a factorization. $\varphi(d)$ for *every* $d \le N$ costs one
sieve, and the reason is [multiplicativity](/topics/domain/multiplicative-function): $\varphi$ is
determined by prime powers, via $\varphi(d) = d \prod_{p \mid d} (1 - 1/p)$. That product is over
primes dividing $d$, so instead of pulling each $d$'s primes in, you push each prime out to its
multiples. Problem 72's whole solution is nine lines:

```python
euler_totients: list[int] = list(range(max_d + 1))
result: int = 0
for n in range(2, max_d + 1):
    if euler_totients[n] == n:                       # untouched cell ⇒ n is prime
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
    result += euler_totients[n]                      # φ(n) is final by the time we read it
```

Two details generalise well beyond this problem. The first is that the sieve carries its own
primality test — a cell still equal to its index has been touched by no smaller prime, so its index
is prime — which means no separate boolean array. The second is the ordering argument on the last
line: every prime factor of $n$ is at most $n$, so cell $n$ is finished by the time the outer loop
arrives at it, and the sum can be accumulated in the same pass. Total cost is
$O(N \log \log N)$ against the $O(N \sqrt{N})$ of factoring each $d$ separately.

The pattern recurs with a different payload each time. Problem 124 sieves radicals by multiplying
each cell by each prime once. Problem 179 sieves divisor counts, and pairs divisors $(a, n/a)$ so
the outer loop only runs to $\sqrt{N}$. Problem 834 does the algebra first (below) and then sieves
divisor sums. Problem 675 adds a twist. It needs a multiplicative function of every factorial
$i!$ up to $10^7$, and consecutive factorials differ only in the primes dividing $i$. So the sieve
records, for each $i$, the ratio by which the running product changes. A prime $p$ updates only its
$n/p$ multiples, and one prefix product yields every value; nothing is ever refactored
([update only what changes](/topics/takeaway/update-only-what-changes)). Problem 531 needs
$\varphi$ only on a window of a few thousand integers above $10^6$, so it sieves the window alone
([segmented sieve](/topics/technique/segmented-sieve)). The primes up to $\sqrt{\text{end}}$ are
pushed into the window, and each one is also divided out of a residual copy of every multiple.
Whatever residual is still above 1 afterwards is the single prime factor larger than the square
root, and one last pass applies it. Problems 632 and 754 sieve to $10^8$ with the same economy.
They push only the primes up to $10^4$ and keep a running product of the small primes found in
each cell. A squarefree cell whose product falls short of its index must hold exactly one large
prime, so the millions of primes above $10^4$ never have to be touched. The rule of
thumb is blunt: **if you find yourself factoring inside a loop over a
range, you have the loop inside out.** Invert it — iterate over primes or divisors and push into an
array. See [sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) and
[precompute once, reuse](/topics/takeaway/precompute-once-reuse).

The sieve does not need its cells to be the integers themselves. Problem 659 reduces to the
largest prime factor of $f(k) = 4k^2 + 1$ for every $k \le 10^7$, values up to $4 \times 10^{14}$.
That is far too large to factor one at a time, but the values can still be sieved, because divisibility
by $p$ is periodic in $k$. The prime $p$ divides $f(k)$ exactly when $k$ is a root of $f$ modulo
$p$, and the multiples of $p$ in the integer sieve become the arithmetic progressions through
those roots. Here $(2k)^2 \equiv -1$ forces $p \equiv 1 \pmod 4$. Every such prime has exactly
two roots, found from a square root of $-1$ (a
[quadratic non-residue](/topics/technique/quadratic-residue) raised to $(p-1)/4$). Higher powers of
$p$ come from [lifting each root](/topics/technique/hensels-lemma) to the next progression. A size
bound ends the work at $p \le 2N + 1$: two primes above that would multiply past $f(k)$, so
whatever survives the sieve is $1$ or a single prime. This is the
[polynomial sieve](/topics/technique/polynomial-sieve), and it is the engine of the
[quadratic sieve](https://en.wikipedia.org/wiki/Quadratic_sieve). Wherever the integer sieve walks
over multiples, it walks over roots.

## Move 2 — swap the order of summation

A sieve needs an array of size $N$, so it dies when $N$ is large enough that you cannot hold one.
Problem 193 asks for the count of [squarefree](/topics/domain/square-free-integer) integers below
$2^{50} \approx 1.13 \times 10^{15}$ — six orders of magnitude past any array you will allocate.

The escape is to write the property as a sum over divisors and then exchange the two summations.
An integer is squarefree exactly when no $d^2$ with $d > 1$ divides it, and the
[Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function) packages the
[inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over square divisors into an
indicator, $\sum_{d^2 \mid n} \mu(d)$. Summing that over $n \le M$ and swapping the order gives

$$Q(M) = \sum_{d=1}^{\lfloor \sqrt{M} \rfloor} \mu(d) \left\lfloor \frac{M}{d^2} \right\rfloor,$$

because each $d$ contributes $\mu(d)$ once for every multiple of $d^2$, and there are exactly
$\lfloor M/d^2 \rfloor$ of those. The outer variable is now $d \le \sqrt{M}$, about 33.5 million —
a sieve you *can* build. Work drops from $10^{15}$ to $3.4 \times 10^7$, and the only thing that
changed is which index sits on the outside.

That is the general move, and it is worth stating in the abstract because it applies far past
squarefree counting. Whenever a condition reads "gcd is 1", "squarefree", "has exactly $k$ prime
factors", or "is divisible by no …", express it as a sum over divisors of something simpler, then
exchange the sums so the *small* variable is the outer one. The machinery has a name —
[Möbius inversion](/topics/technique/mobius-inversion-formula), the inverse operation to
[Dirichlet convolution](https://en.wikipedia.org/wiki/Dirichlet_convolution) — and problem 153
(sums over [Gaussian integer](https://en.wikipedia.org/wiki/Gaussian_integer) divisors) is the
archive's fullest workout of it.

"Exactly $k$" needs one more step, because a single divisor sum gives "at least". Problem 632
counts the $n \le 10^{16}$ with exactly $k$ square prime factors. For a squarefree $d$ the count of
$n$ divisible by $d^2$ is $\lfloor N/d^2 \rfloor$. Summing that over the $d$ with $\omega(d) = j$
gives $A_j$, which counts every $n$ once per $j$-subset of its square primes:
$A_j = \sum_k \binom{k}{j} C_k$. That triangular system inverts with alternating signs,
$C_k = \sum_{j \ge k} (-1)^{j-k} \binom{j}{k} A_j$
([binomial inversion](/topics/technique/binomial-inversion), inclusion–exclusion graded by size).
The outer variable is again $d \le \sqrt{N}$, and $j$ stops at 8, since nine primes already
multiply past $10^8$. One sieve classifies each $d$ by $\omega$, and nine sums do the rest.

The swap works for products as well as sums, with the Möbius function moved into the exponent.
Problem 754 multiplies the [Gauss factorials](https://en.wikipedia.org/wiki/Wilson%27s_theorem#Gauss's_generalization)
$g(n)$, the product of the $k \le n$ coprime to $n$, for every $n \le 10^8$. Inversion gives
$g(n) = \prod_{d \mid n} (d^{n/d} (n/d)!)^{\mu(d)}$. Substituting $n = dm$ and exchanging the
products leaves one product over $d$, in which every factor depends only on $\lfloor N/d \rfloor$.
That sets up move 3.

## Move 3 — there are only $O(\sqrt{N})$ distinct quotients

The identity above leaves a floor function in the sum, and floors have an exploitable property:
as $d$ runs from $1$ to $N$, the value $\lfloor N/d \rfloor$ takes at most $2\sqrt{N}$ distinct
values. For $d \le \sqrt{N}$ the quotient is large and changes at every step; past that, the
quotient is below $\sqrt{N}$ and each value persists over a long run of consecutive $d$.

So a sum $\sum_{d \le N} g(\lfloor N/d \rfloor)$ need not be evaluated $N$ times. Group the $d$
that share a quotient — for a given $d$, the last index with the same quotient is
$\lfloor N / \lfloor N/d \rfloor \rfloor$ — evaluate $g$ once per block, and multiply by the block
width. The loop shrinks from $N$ iterations to $O(\sqrt{N})$:

```python
d = 1
while d <= n:                        # blocks of constant q = n // d
    q = n // d
    hi = n // q                      # last index sharing this quotient
    total += g(q) * (hi - d + 1)     # one evaluation for the whole block
    d = hi + 1
```

This is [quotient blocking](/topics/technique/quotient-blocking); paired with a partial sieve for
the small range it becomes the
[Dirichlet hyperbola method](/topics/technique/dirichlet-hyperbola-method), which computes
summatory functions like $\sum \tau(n)$ or $\sum \varphi(n)$ in sublinear time. Problems 153 and
926 both lean on it. It is the standard finishing move once move 2 has produced a floor-laden sum,
and the pair together is the reason $N = 10^{15}$ is not automatically hopeless.

Moves 2 and 3 combine most neatly when the *unrestricted* count is easy and you want only the
coprime part. Problem 276 counts integer triangles with $\gcd(a, b, c) = 1$ and perimeter at most
$N$. Ignoring the gcd, the count $S(N)$ has an $O(1)$ closed form (see "Exactness" below). Every triangle is $g$
times a primitive one of perimeter at most $\lfloor N/g \rfloor$, so
$S(N) = \sum_{g \ge 1} P(\lfloor N/g \rfloor)$, which inverts to

$$P(N) = S(N) - \sum_{g \ge 2} P\!\left(\left\lfloor \frac{N}{g} \right\rfloor\right).$$

No Möbius function appears: the recursion runs only over the $O(\sqrt{N})$ distinct quotients, and
each of those costs a blocked $O(\sqrt{v})$ loop, so the total is $O(N^{3/4})$. That is sublinear,
where sieving $\mu$ up to $N$ would be linear. Fill the values bottom-up, with one array indexed
by small $v$ and one by $k$ for $v = \lfloor N/k \rfloor$, and no dictionary or call stack is
needed. This is the same skeleton as the
[Mertens function](https://en.wikipedia.org/wiki/Mertens_function) recursion, and it applies
whenever "all of them" is a formula and "the primitive ones" is the question. Problem 512 uses it
directly. Counting pairs $a \le b \le v$ by their gcd gives
$\sum_{d} \Phi(\lfloor v/d \rfloor) = v(v+1)/2$ for the summatory totient $\Phi$, which is the same
inversion ([totient summatory recursion](/topics/technique/totient-summatory-recursion)). Sieving
$\varphi$ up to $N^{2/3}$ and recursing above that brings the cost to
$O(N^{2/3})$.

The floor-quotient set is also where prime counting lives. The Lucy–Hedgehog sieve computes $\pi(v)$ for
*every* $v = \lfloor N/i \rfloor$ at once. It stores them in two $\sqrt{N}$-sized arrays, one for
small $v$ and one indexed by $i$, and removes one prime's multiples per pass. Problem 452 builds on
it. Its tuple count is the summatory function of the $n$-fold divisor function $d_n$, which is
multiplicative and *constant on primes* ($d_n(p) = n$). The primes therefore contribute
$n \cdot \pi(m)$, and the composites come from a recursion over smallest prime factors. That pair
is the [Min_25 sieve](/topics/technique/min-25-sieve), and it runs in about $O(N^{3/4} / \log N)$.
Problem 641 lands on a two-variable floor count, the pairs $(c, q)$ with $c^3 q^2 \le X$. It splits
the region the way the [hyperbola method](/topics/technique/dirichlet-hyperbola-method) does: loop
over $q$ when $q$ is small, and over $c$ when $q$ is large. The large side needs
$\#\{q \le x : \mu(q) = +1\}$, which is half the sum of the squarefree count $Q(x)$ and the Mertens
function $M(x)$. Both are the sublinear sums from moves 2 and 3.

Problem 754 shows that blocking survives the switch from sums to products. Over a run of $d$ with
the same quotient $M$, the exponents $\mu(d)$ on the superfactorial
$F(M) = \prod_{m \le M} m!$ add up to a difference of
[Mertens values](/topics/technique/mertens-function-application). The factors $d^{\mu(d)}$ become a
ratio of running products, kept as separate $\mu = +1$ and $\mu = -1$ products so that each block
needs one modular inverse instead of one per element. The running quantities are only *read* at
the $2\sqrt{N}$ checkpoints $\lfloor N/k \rfloor$, so only those values are stored. A linear pass
builds them, and the final product costs $O(\sqrt{N})$ exponentiations.

## Move 4 — reduce the algebra before you write the loop

The three moves above are all mechanical once the sum exists. Getting to the sum is not, and the
most common route is ordinary algebra applied before any code is written — the archive's
[reduce before coding](/topics/takeaway/reduce-before-coding) takeaway is the most frequent one on
this list.

Problem 834 is a clean case. Its sequence is defined by a step rule, and simulating it is hopeless
at the stated scale; but the $m$-th term telescopes to a closed form in $m$ and $n$, and once the
divisibility test is rewritten in terms of $n + m$ it becomes a condition a divisor sieve answers
in bulk. The problem never gets easier — the *representation* does.

Problem 800 shows the same instinct against a different obstacle. It counts integers $p^q q^p$ up
to $800800^{800800}$, a bound with millions of digits, so the comparison itself is the problem.
Take logarithms of both sides and $p^q q^p \le N$ becomes $q \ln p + p \ln q \le \ln N$: ordinary
floating-point arithmetic in machine words. Monotonicity in $q$ then turns the count into a
[binary search](/topics/technique/binary-search-algorithm) per prime.

Problem 243 reduces the *search space* rather than the arithmetic. Since $\varphi(d)/d$ is a
product over the distinct primes dividing $d$, it ignores multiplicity entirely — so the ratio
depends only on which primes appear, and the cheapest way to push it down is to use the smallest
ones. The candidates collapse to multiples of a
[primorial](https://en.wikipedia.org/wiki/Primorial), and an unbounded search becomes a handful of
checks.

Problem 571 reduces a search tree, and the fact it uses is about
[positional notation](/topics/domain/positional-notation) rather than divisibility. It wants the
smallest integers that are [pandigital](/topics/domain/pandigital-number) in every base from 2 up
to $n$. The base-$n$ condition is the strictest, so the search builds base-$n$ permutations digit
by digit, in increasing order. A partial permutation confines every completion to an interval
$[lo, hi]$. Every number in an interval shares its leading digits *in any base* down to the first
place where $lo$ and $hi$ differ. If that shared prefix is missing more digits of base $b$ than
there are free places left below it, no completion can be pandigital in base $b$, and the whole
subtree is dropped. One cheap interval test stands in for hundreds of millions of base
conversions. Four problems, four different things reduced: the formula, the comparison, the
candidate set, the search tree.

Problem 637 is about splitting digits too. $f(n)$ counts how many rounds of inserting plus signs
it takes to reach a single digit. A number has $2^{L-1}$ splits, but $f$ never exceeds 3 below
$10^7$. So the useful question is not "what is the minimum" but "is $f(n) \le t$", and that
question is settled by a single witness split. Splitting at every place gives the digit sum,
which is the cheapest split, and it settles level 1 with no search. Most of level 2 then falls to
a [meet-in-the-middle](/topics/technique/meet-in-the-middle-attack) bit-array AND over the high and
low halves. When a function has a tiny range, asking about thresholds turns a minimisation into a
search for one witness.

Sometimes what shrinks is the *answer's* form. Problem 561 asks for the 2-adic valuation of a
divisor-pair count, summed over $10^{12}$ exponents. Divisors of a primorial power are exponent
vectors, and divisibility compares them one coordinate at a time, so the count factorises into a
closed form. Its [2-adic valuation](/topics/domain/p-adic-valuation) then splits on parity. One
branch needs the [lifting-the-exponent lemma](/topics/technique/lifting-the-exponent-lemma), and
each branch comes down to $\sum_{t \le N} v_2(t) = v_2(N!)$. [Legendre's formula](/topics/domain/legendres-formula)
gives that as $N - s_2(N)$, where $s_2$ is the binary digit sum. The sum of $10^{12}$ terms is a
popcount. A question that asks for a valuation rather than a value is usually asking for this:
LTE turns $v_p(a^n - b^n)$ into valuations of $a - b$ and $n$, and Legendre adds them up.

Problem 615 makes a parameter vanish. It wants the millionth integer with at least $10^6$ prime
factors counted with multiplicity ([almost primes](/topics/domain/almost-prime) of every order
$\ge k$). Nothing that size can be written down. But every early member is mostly made of twos.
Replacing a two by an odd prime costs a factor of at least $3/2$, and $(3/2)^{36}$ already exceeds
$n$. So the first $n$ members all carry $2^{k-36}$, and dividing it out maps them in order onto the
first $n$ members of the $k = 36$ list, which are ordinary 64-bit integers. The
[order statistic](/topics/domain/order-statistic) is then a pruned depth-first search over odd
parts, below a bound found by [doubling](/topics/technique/exponential-search), followed by a sort.
Look for the point where the huge parameter stops changing anything except a scale factor.

Sometimes the reduction is a congruence that makes most of the problem disappear. Problem 512 sums
$\varphi(n^i) \bmod (n+1)$ over $i \le n$. But $\varphi(n^i) = n^{i-1}\varphi(n)$, and
$n \equiv -1 \pmod{n+1}$. The terms alternate and cancel in pairs, leaving $\varphi(n)$ for odd $n$
and $0$ for even $n$, so a double sum becomes a summatory totient restricted to odd arguments.
Problem 641 starts with dice and ends with a divisor count. A die finishes on 1 exactly when
$\tau(k) \equiv 1 \pmod 6$. That forces $k$ to be a square $m^2$ with $\prod (2a_i + 1) \equiv 1
\pmod 3$, and the qualifying $m$ factor uniquely as $c^3 q^2$ with $q$ squarefree and $\mu(q) = +1$.
None of that is code. All of it is what makes the code possible.

## Move 5 — when only the prime set matters, enumerate the shape

A condition that depends only on which primes divide $n$, like problem 272's "exactly five
cube-root factors", should not be tested one $n$ at a time. Enumerate the *shape* instead. Write
each qualifying $n$ uniquely as $A \cdot m$. Here $A$ is the product of the prime powers the
condition cares about, and the cofactor $m$ is built only from primes it does not care about. The
answer then becomes

$$\sum_{A} A \cdot S\!\left(\left\lfloor \frac{L}{A} \right\rfloor\right),$$

where $S(x)$ sums the admissible cofactors up to $x$. $S$ is one sieve (strike out the excluded
primes) followed by a [prefix sum](/topics/technique/prefix-sum), and it is small, because five
mandatory factors already cost at least $7 \cdot 9 \cdot 13 \cdot 19 \cdot 31$. A depth-first
search builds the $A$, choosing primes in increasing order and pruning once the remaining slots
cannot fit even at the current prime.

Most of the work is the last prime, and move 3 removes it. Let $T$ be what $L$ leaves for the last
factor. Every prime above $\sqrt{T}$ appears only to the first power. Its cofactor bound
$\lfloor T/p \rfloor$ also takes fewer than $\sqrt{T}$ values, so the loop runs over the quotient
$q$ instead of the prime. Each $q$ multiplies $S(q)$ by the *sum of the eligible primes* in the
interval that shares it, read from a second prefix-sum array by bisection. The same quotient
blocking applies, but the blocks are over primes rather than consecutive integers. Problem 268
("at least four distinct prime factors below 100") and the other $\omega(n)$-shaped problems have
the same structure.

Problem 516 is the same split arrived at from a multiplicative function. It asks for the $n$ whose
$\varphi(n)$ is [5-smooth](/topics/domain/smooth-number). Since $\varphi(p^e) = p^{e-1}(p-1)$, the
primes 2, 3 and 5 may appear to any power. Any larger prime must appear exactly once, and $p - 1$
must itself be 5-smooth. So $n = h \cdot m$, where $h$ is a Hamming number and $m$ is a squarefree
product of "good" primes. A few thousand Hamming numbers, with a prefix sum over them, take the
place of the cofactor sieve. A depth-first search over the good primes builds the $m$. A search
over $10^{12}$ integers becomes a search over two sets you can list.

## Move 6 — when the question is a process, find its structure

A minority of these problems are not sums at all. They describe a process — a recurrence, a greedy
rule, an orbit — and ask where it stands after $10^{15}$ steps. Simulating it is hopeless, but the
process almost always has much less going on than its step count. The move is to find what
actually changes and [jump to the next event](/topics/takeaway/jump-to-the-next-event).

Problem 443's recurrence $g(n) = g(n-1) + \gcd(n, g(n-1))$ adds 1 at almost every step. Write
$g(k) = k + d$. Then the gcd at step $j$ is $\gcd(j, d - 1)$, so the run of $+1$ steps ends at the
first multiple of a prime factor of $d - 1$. One factorization per jump replaces every step in
between, and there are only a few hundred jumps up to $10^{15}$. Problem 700 looks for the record
lows of $na \bmod m$. Keep two records, the smallest residue and the smallest gap below $m$. The
next candidate is always their difference, which is the subtractive
[Euclidean algorithm](/topics/technique/euclidean-algorithm) under another name, so each record
costs $O(1)$ amortised. Its geometry is the
[three-distance theorem](/topics/domain/three-distance-theorem). Problem 822 repeatedly squares the
smallest of a list of numbers. After a short transient it settles into a fixed rotation, and the
remaining $10^{16}$ rounds reduce to a division
([simulate the transient, then extrapolate](/topics/takeaway/simulate-transient-then-extrapolate)).
Problem 455's self-referential $n^x \equiv x \pmod{10^9}$ is solved by iterating the
[power tower](/topics/domain/tetration) to its [fixed point](/topics/technique/fixed-point-iteration).
The tower stabilises because the exponent only matters modulo $\lambda(m)$, then
$\lambda(\lambda(m))$, down a [Carmichael](/topics/technique/carmichael-function) chain that reaches
1 within a dozen steps.

When no structure is visible, generate it. Problem 359's hotel has no obvious formula. Simulating
the first forty thousand guests shows that the sums of neighbouring rooms run through consecutive
squares, so the occupant of a room telescopes to a quadratic. The sum then runs over the 364
divisors of $N$
([small cases reveal the closed form](/topics/takeaway/small-cases-reveal-closed-form)).

## Exactness is the discipline

Number theory asks questions whose answers are exact integers, and the characteristic bug in this
domain is a correct algorithm ruined by an inexact intermediate.

Comparing ratios is where it bites first. Problem 243 needs $\varphi(d)/(d-1) < 15499/94744$;
computing either side as a float and comparing invites a wrong answer at the boundary, where the
problem's answer lives by construction. Cross-multiply and compare integers instead. The same
applies to $\sqrt{\cdot}$: use `math.isqrt`, not `int(math.sqrt(x))`, which starts losing integers
around $2^{52}$ — problems 179 and 193 both depend on an exact integer square root. Where floats
are genuinely the right tool, as in problem 800's logarithms, treat a near-boundary comparison as
undecided and re-check it exactly. A rounding in a closed form deserves the same treatment.
Problem 276's unrestricted triangle count is built on
[Alcuin's sequence](https://oeis.org/A005044), $\operatorname{round}(k^2/12)$. Since
$k^2 \bmod 12$ only takes the values $0, 1, 4, 9$, the rounding becomes an exact integer
correction with period 12. That makes the sum of the sequence a square-pyramidal number plus a
linear term, with no float involved. See
[use exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
Problem 822 is the opposite case, where floats are safe and exact values are impossible. Its
numbers have $2^{10^{12}}$-sized exponents, so it orders them by $\log_2 \log_2 x^{2^k} =
k + \log_2 \log_2 x$. Distinct values differ in that key by far more than rounding error, and equal
values can be ordered either way without changing the sum.

Modular reduction has its own exactness trap. In problem 271 the roots are combined modulo $n$, but
the question asks for their sum as integers. That sum is hundreds of times larger than $n$, so
reducing it would discard most of the answer
([exact sums resist modular shortcuts](/topics/takeaway/exact-sums-resist-modular-shortcuts)).
Problem 632 multiplies its non-zero counts modulo $10^9 + 7$. Which counts are non-zero is a
question about the exact integers, so the binomial inversion runs without a modulus. A count that
happens to be divisible by the modulus is still a factor. Exponents are where reduction *is*
licensed, if the modulus is right. In problem 754 the base modulus $p$ is prime, so exponents
reduce modulo $p - 1$ by [Fermat](/topics/domain/fermats-little-theorem)
([reduce the exponent modulo the group order](/topics/takeaway/reduce-exponent-modulo-group-order)).
A negative Mertens difference then becomes an ordinary positive exponent. That works only because
$p > N$, so no base is ever $0 \bmod p$.

The second trap is width, and it is language-shaped. Python's integers are arbitrary-precision, so
a solution that works in Python can overflow silently the moment it is ported to C. Problems 241,
251, 271, 272, 276, 359, 531, 615, 632, 641 and 659 all need `__int128` or a reduction that keeps
intermediates small. In 615 it is a pruning product that briefly passes $2^{64}$ before the
comparison rejects it. In 632 it is an alternating sum whose terms are larger than its result.
In 276 the
answer itself still fits in 64 bits, but the intermediate $k(k+1)(2k+1)$ does not. Problem 531 has
the reverse problem: every term fits, but the running total of millions of them passes $2^{63}$ on
the larger test window, so the accumulator has to be wider than the values going into it. Problems 168 and
321 need [GMP](https://gmplib.org/) outright. The Python version gives no warning that the C
version is about to be wrong. See [watch integer width](/topics/takeaway/watch-integer-width).

## Knowing which move to reach for

The tells are reasonably reliable:

| What you see | What it usually means |
| --- | --- |
| "for every $n$ up to $N$", $N \le 10^8$ | sieve the whole table (move 1) |
| $N \ge 10^{12}$, or "below $2^{50}$" | find a summatory identity; sieve only $\sqrt{N}$ (moves 2–3) |
| "coprime", "gcd is 1", "squarefree", "exactly $k$ prime factors" | Möbius / inclusion–exclusion over divisors (move 2) |
| "exactly $k$" of something a divisor sum counts as "at least" | count the $j$-subsets, then binomial inversion (move 2) |
| a *product* over coprime $k$ or over divisors | Möbius in the exponent; block it like a sum (moves 2–3) |
| the factors of $f(k)$ for a polynomial $f$, every $k$ | sieve along the roots of $f$ mod $p$, Hensel for powers (move 1) |
| $\lfloor N/d \rfloor$ anywhere in the derived sum | quotient blocking (move 3) |
| the total is a formula, the question asks for the gcd-1 part | invert over floor quotients, $O(N^{3/4})$ (moves 2–3) |
| the condition only sees which primes divide $n$ | enumerate the prime part, prefix-sum the cofactors (move 5) |
| a congruence modulo a composite $n$ | solve per prime power, recombine by CRT |
| two congruences whose moduli share factors | generalised CRT: solvable iff $\gcd$ divides the difference |
| a condition on the digits of $n$ in several bases | prune whole intervals by their shared leading digits |
| $\pi(v)$, or a function constant on primes, summed to $10^9$+ | Lucy / Min_25 over the floor quotients (move 3) |
| the answer is a $p$-adic valuation | LTE per term, Legendre's formula for the sum (move 4) |
| the $n$-th element for an enormous parameter $k$ | find where $k$ only scales the answer; divide it out (move 4) |
| a minimum whose range is tiny | decide "$\le t$" level by level; one witness settles it (move 4) |
| a recurrence or greedy process run $10^{15}$ times | find the events or the steady state; jump (move 6) |
| $f$ is multiplicative | build $f$ from prime powers; a sieve exists |
| the number is too large to write down | work in logs, or modulo whatever the question actually asks for |
| a ratio, a root, or an equality test | integers only — cross-multiply, `isqrt`, check the width |

What the moves buy is asymptotic, not constant: $N \to N \log \log N$ in move 1, $N \to \sqrt{N}$
in moves 2 and 3. That is why a rewrite in C rarely rescues a number-theory problem and a change of
representation almost always does. The cost is that each move demands the derivation be right
before a line is written — a sieve indexed off by one, or a Möbius identity with the wrong bound,
produces a plausible number rather than an error. Verify on the small case the statement gives you;
it exists for exactly that reason. When there is no small case, as in problem 276, make one: a
brute force for tiny $N$, plus an asymptotic check. Primitive triangles should be about
$1/\zeta(3) \approx 83\%$ of all triangles, and a wrong inversion misses that badly. Problem
632's count with no square prime factors must match the squarefree density $6/\pi^2$; a slip in the binomial signs would
show up there at once. See
[calibrate theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0243](/solutions/0243/) — Resilience
- ● [0251](/solutions/0251/) — Cardano Triplets
- ○ [0268](/solutions/0268/) — At Least Four Distinct Prime Factors Less Than 100
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ○ [0273](/solutions/0273/) — Sum of Squares
- ● [0276](/solutions/0276/) — Primitive Triangles
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ○ [0309](/solutions/0309/) — Integer Ladders
- ● [0321](/solutions/0321/) — Swapping Counters
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ● [0346](/solutions/0346/) — Strong Repunits
- ○ [0350](/solutions/0350/) — Constraining the Least Greatest and the Greatest Least
- ○ [0354](/solutions/0354/) — Distances in a Bee's Honeycomb
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ○ [0360](/solutions/0360/) — Scary Sphere
- ○ [0370](/solutions/0370/) — Geometric Triangles
- ○ [0372](/solutions/0372/) — Pencils of Rays
- ○ [0379](/solutions/0379/) — Least Common Multiple Count
- ○ [0388](/solutions/0388/) — Distinct Lines
- ● [0407](/solutions/0407/) — Idempotents
- ○ [0410](/solutions/0410/) — Circle and Tangent Line
- ○ [0417](/solutions/0417/) — Reciprocal Cycles II
- ○ [0432](/solutions/0432/) — Totient Sum
- ○ [0433](/solutions/0433/) — Steps in Euclid's Algorithm
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ● [0443](/solutions/0443/) — GCD Sequence
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0448](/solutions/0448/) — Average Least Common Multiple
- ○ [0451](/solutions/0451/) — Modular Inverses
- ● [0452](/solutions/0452/) — Long Products
- ○ [0454](/solutions/0454/) — Diophantine Reciprocals III
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0462](/solutions/0462/) — Permutation of 3-smooth Numbers
- ○ [0466](/solutions/0466/) — Distinct Terms in a Multiplication Table
- ○ [0485](/solutions/0485/) — Maximum Number of Divisors
- ○ [0489](/solutions/0489/) — Common Factors Between Two Sequences
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0513](/solutions/0513/) — Integral Median
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0533](/solutions/0533/) — Minimum Values of the Carmichael Function
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0541](/solutions/0541/) — Divisibility of Harmonic Number Denominators
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ○ [0556](/solutions/0556/) — Squarefree Gaussian Integers
- ● [0561](/solutions/0561/) — Divisor Pairs
- ● [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0580](/solutions/0580/) — Squarefree Hilbert Numbers
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0586](/solutions/0586/) — Binary Quadratic Form
- ○ [0596](/solutions/0596/) — Number of Lattice Points in a Hyperball
- ○ [0601](/solutions/0601/) — Divisibility Streaks
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0616](/solutions/0616/) — Creative Numbers
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0632](/solutions/0632/) — Square Prime Factors
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ● [0659](/solutions/0659/) — Largest Prime
- ○ [0672](/solutions/0672/) — One More One
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0699](/solutions/0699/) — Triffle Numbers
- ● [0700](/solutions/0700/) — Eulercoin
- ○ [0708](/solutions/0708/) — Twos Are All You Need
- ○ [0712](/solutions/0712/) — Exponent Difference
- ○ [0714](/solutions/0714/) — Duodigits
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0735](/solutions/0735/) — Divisors of $2n^2$
- ○ [0738](/solutions/0738/) — Counting Ordered Factorisations
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ○ [0749](/solutions/0749/) — Near Power Sums
- ○ [0753](/solutions/0753/) — Fermat Equation
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0789](/solutions/0789/) — Minimal Pairing Modulo $p$
- ○ [0791](/solutions/0791/) — Average and Variance
- ○ [0792](/solutions/0792/) — Too Many Twos
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ● [0800](/solutions/0800/) — Hybrid Integers
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0804](/solutions/0804/) — Counting Binary Quadratic Representations
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0821](/solutions/0821/) — 123-Separable
- ● [0822](/solutions/0822/) — Square the Smallest
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0827](/solutions/0827/) — Pythagorean Triple Occurrence
- ○ [0832](/solutions/0832/) — Mex Sequence
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0858](/solutions/0858/) — LCM
- ○ [0864](/solutions/0864/) — Square + 1 = Squarefree
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0884](/solutions/0884/) — Removing Cubes
- ○ [0908](/solutions/0908/) — Clock Sequence II
- ○ [0915](/solutions/0915/) — Giant GCDs
- ○ [0920](/solutions/0920/) — Tau Numbers
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0931](/solutions/0931/) — Totient Graph
- ○ [0937](/solutions/0937/) — Equiproduct Partition
- ○ [0954](/solutions/0954/) — Heptaphobia
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0986](/solutions/0986/) — Another Infinite Game
- ○ [0999](/solutions/0999/) — Alternating Recurrence

<!-- /problems -->
