<!-- tags: [coprime-integers] -->
<!-- status: final 2026-11-04T03:46Z -->
# Coprime integers

Two integers are [coprime](https://en.wikipedia.org/wiki/Coprime_integers) when
$\gcd(a, b) = 1$ — they share no prime factor. That is the whole definition, and on its own it
looks like a triviality worth one line of a library call. It earns a *domain* page because of what
it does to the problems below: coprimality is the condition under which arithmetic **stops
interfering with itself**. Two coprime numbers can be reasoned about independently, so a
multiplicative quantity splits across them, a fraction has exactly one reduced form, a lattice
direction has exactly one primitive vector, a residue becomes invertible, and a step reaches every
residue before it repeats. Almost every problem
on this page is a case of noticing that some pair in the statement is forced to be coprime, and
then cashing that in.

## The idea

The gcd itself is cheap: the [Euclidean algorithm](/blogs/technique/euclidean-algorithm) costs
$O(\log \min(a,b))$, and Python spells it `math.gcd`. The content is in the equivalences that
$\gcd(a,b) = 1$ unlocks.

**[Bézout](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity):** $\gcd(a,b) = 1$ iff
$ax + by = 1$ has an integer solution, which the
[extended Euclidean algorithm](/blogs/technique/extended-euclidean-algorithm) produces. Reduce
that mod $b$ and it says $a$ is a *unit* modulo $b$ — coprimality is exactly the condition for a
[modular inverse](/blogs/domain/modular-multiplicative-inverse) to exist, which is why the units
group $(\mathbb{Z}/n\mathbb{Z})^\times$ has order
[$\varphi(n)$](/blogs/domain/eulers-totient-function) and why every "solve $ax \equiv c$" step in
these problems begins by checking a gcd. Problem 274 is the cleanest instance: its "divisibility
multiplier" $m$ for a prime $p$ turns out to be $10^{-1} \bmod p$, and the statement's
hypothesis "$p$ coprime to $10$" is precisely the condition for that inverse to exist. The
coprimality also hands over a closed form — $m = (kp+1)/10$ with $k$ fixed by $p$'s last digit —
so no extended Euclid runs at all.

Problem 605 is what happens when that gcd check is neither cheap nor passing. It needs a fraction
in lowest terms whose denominator is built from $2^n - 1$, a number some thirty million digits
long, so the gcd cannot be run on the operands. It does not have to be: the numerator's factor
$T$ satisfies $T \equiv n \pmod{2^n - 1}$, so one Euclid step taken on paper shows any prime they
share also divides $n$, and $\gcd(n, 2^n - 1)$ needs only $2^n \bmod n$. That names the candidate
primes; each one's exponent is then read from residues modulo a high power of it. The common
factor can still fail to be a unit modulo the required output modulus, so there is no inverse to
divide by. The way out is to
[lift the modulus](/blogs/takeaway/divide-by-lifting-the-modulus): if $d \mid v$, then
$(v \bmod md)/d \equiv v/d \pmod m$, so compute modulo $md$ and divide exactly. Coprimality decides
whether a division is an inverse; it does not decide whether the division is possible.

**Splitting:** a [multiplicative function](/blogs/domain/multiplicative-function) satisfies
$f(ab) = f(a)f(b)$ *only* under $\gcd(a,b) = 1$, and the
[Chinese remainder theorem](/blogs/technique/chinese-remainder-theorem) says
$\mathbb{Z}/ab\mathbb{Z} \cong \mathbb{Z}/a\mathbb{Z} \times \mathbb{Z}/b\mathbb{Z}$ under the
same condition. The underlying fact is local at each prime: a prime power dividing a product of
coprime factors lies wholly inside one factor — it can never straddle both. Problem 932 is that
sentence made into an algorithm: it needs $m \mid s(s-1)$, and because consecutive integers are
coprime, each prime power of $m$ independently chooses which of $s$ and $s-1$ absorbs it, giving
$2^k$ residue classes reassembled by CRT instead of a search over $s$. Problem 407 is the same
condition in its general form: $a^2 \equiv a \pmod n$ reads $n \mid a(a-1)$, so the
[idempotents](https://en.wikipedia.org/wiki/Idempotent_(ring_theory)) of $\mathbb{Z}/n\mathbb{Z}$
correspond one-to-one with the coprime splits $n = de$ — the
[unitary divisors](https://en.wikipedia.org/wiki/Unitary_divisor) — and there are
$2^{\omega(n)}$ of them. Wanting the largest idempotent for *every* $n \le N$, it turns the loop
inside out: rather than factor each $n$, it enumerates the coprime pairs $(d,e)$ with $de \le N$
and solves each by CRT. One factor of every pair is below $\sqrt N$, so inverting modulo the small
one lets a single inverse table serve all its partners — and storing $0$ as the "inverse" of a
non-unit makes a non-coprime pair collapse to the trivial idempotents $0$ and $1$, so the
coprimality test is never written at all. Problem 834 factors $n$ and
$n-1$ separately for the same reason; problem 127 uses it on the radical
($\operatorname{rad}(abc) = \operatorname{rad}(a)\operatorname{rad}(b)\operatorname{rad}(c)$ once
the triple is pairwise coprime), and problem 694 uses it to give every cube-full number the unique
form $m_3^3 m_4^4 m_5^5$ with $m_4, m_5$ squarefree and coprime.

The same locality settles exponents. If coprime $a$ and $b$ have $ab = c^k$, each prime of $c$ lies
wholly in one factor and brings its full exponent, a multiple of $k$, so $a$ and $b$ are perfect
$k$-th powers themselves. This is the move behind Fermat's
[infinite descent](https://en.wikipedia.org/wiki/Proof_by_infinite_descent), and problem 764 uses
it to solve an equation outright. Read $16x^2 + y^4 = z^2$ as a
[Pythagorean triple](/blogs/domain/pythagorean-triple) $(4x, y^2, z)$ and
[Euclid's formula](/blogs/technique/euclids-formula) applies; for odd $y$ the square leg factors
as $y^2 = (m-n)(m+n)$ with coprime factors, so each factor is a square. Substituting those squares
turns the solutions into quartic forms in a new coprime pair, and $z \le N$ now holds both
parameters to $O(N^{1/4})$ and the whole enumeration to $O(N^{1/2})$ pairs. For even $y$ the
factorisation carries a stray $2$, which must be assigned to one side: the even factor is twice a
square and the odd one a square.

**Canonical form:** every pair $(a,b)$ is $d \cdot (s,t)$ with $d = \gcd(a,b)$ and
$\gcd(s,t) = 1$, uniquely. So a family parametrised by an unreduced pair is really a family of
*primitive* representatives times a scale, and enumerating primitives once each removes the
duplication for free. This is the single most common move on this page. Problem 141 writes the
geometric ratio as $p/q$ in lowest terms and a scale $k$, so each geometric family is generated by
exactly one $(p,q)$; problem 157 sets $a = ds$, $b = dt$ and finds that $\gcd(s,t)=1$ forces
$\gcd(s+t, st) = 1$, which is what collapses the divisibility into "$st$ divides $10^n$"; problem
251 splits $b$ against $n$ the same way and turns the surviving constraint linear in $d$.
Problem 257 shows the payoff in full. Writing the side ratio $(a+b)/b$ as a reduced $p/q$
parametrises every triangle as one coprime pair times a scale $s$, and the scale is never
enumerated: each admissible pair contributes $\lfloor N/L \rfloor$ triangles, $L$ being the
perimeter of its smallest member. Coprimality also caps the gcd that sets $L$ —
$\gcd(p, kq - p) = \gcd(p, k)$ once $\gcd(p,q) = 1$ — and that cap is what bounds the search to
$q = O(\sqrt N)$. The
[tree of primitive Pythagorean triples](/blogs/technique/tree-of-primitive-pythagorean-triples)
and the [Stern–Brocot tree](/blogs/domain/stern-brocot-tree) are this idea made into generators:
they emit coprime pairs directly, so no candidate is ever tested and rejected.

The canonical form also proves itself complete, through
[Euclid's lemma](https://en.wikipedia.org/wiki/Euclid%27s_lemma): if $b \mid ac$ and
$\gcd(b,c) = 1$ then $b \mid a$, and coprimality survives taking powers. So a
[reduced ratio](/blogs/takeaway/parametrise-by-reduced-ratio) leaves its denominator nowhere to go
but the scale. In problem 518 a geometric triple with ratio $q/p$ has $z = xq^2/p^2$; since $p^2$
cannot cancel against $q^2$, it must divide $x$, and every triple is $k(p^2, pq, q^2)$ with no
exceptions. Problem 510 runs the argument twice. Tangency forces $r_A/r_B = u^2/v^2$, so
$r_A = ku^2$ and $r_B = kv^2$, and the third radius comes out as $ku^2v^2/(u+v)^2$. Because $u+v$
is coprime to $uv$, all of $(u+v)^2$ has to be absorbed by $k$. Integrality is therefore a step in
a derivation rather than a filter on candidates, and it yields the exact shape of every solution.
What the leftover scale costs depends on the quantity. Problem 510's radii are homogeneous in it,
so its multiples sum to a triangular number as in problem 257; problem 518 asks whether each term
is prime, which is not homogeneous, so there the scale has to be walked.

**Visibility:** in the [integer lattice](/blogs/domain/integer-lattice), $(p,q)$ is visible from
the origin — no lattice point strictly between — iff $\gcd(p,q) = 1$. Reduced fraction, primitive
vector and unobstructed line of sight are three names for one object. Problem 202 unfolds a
laser bouncing in a triangle into a straight lattice segment, and "the beam must not leak out
through an intermediate vertex" becomes $\gcd(p,q)=1$ exactly. Problem 351's hexagonal orchard is
the same test on a different lattice: in the basis of two lattice vectors $60^\circ$ apart, a point
$(a,b)$ is hidden iff $\gcd(a,b) > 1$, and since $\gcd(a,b) = \gcd(a, a+b)$ the visible points on
the ring $a + b = s$ of one sector number exactly $\varphi(s)$. Six-fold symmetry then gives
$H(n) = 3n(n+1) - 6\sum_{s \le n}\varphi(s)$ — the visibility question becomes a totient sum. The
same condition is what problems 388, 777 and 841 are counting when they talk about distinct lines,
Lissajous curves and star polygons.

**Reach:** a step $s$ coprime to $n$ generates $\mathbb{Z}/n\mathbb{Z}$ additively: the walk
$0, s, 2s, \dots$ visits all $n$ residues in one cycle, where $\gcd(s,n) = g > 1$ would trap it in
a subgroup of size $n/g$. Replace the cycle with non-negative combinations and the statement
becomes the [Frobenius](/blogs/domain/frobenius-number) setting: the
[numerical semigroup](https://en.wikipedia.org/wiki/Numerical_semigroup) generated by
$a_1, \dots, a_k$ misses only finitely many integers iff their overall gcd is $1$, and for two
coprime generators the largest miss is $ab - a - b$. Problem 718 needs both forms. It totals the
gaps of a three-generator semigroup through its Apéry set, the least reachable member of each
residue class modulo the smallest generator $x$, which in general is a shortest-path computation
over the residues. Coprimality removes the graph. An inverse of the second generator modulo $x$
gives its least multiple in each class directly. Then walking the classes in the order
$iz \bmod x$, one cycle because $\gcd(z,x) = 1$, makes "add one more $z$" a step between neighbours,
so the third generator costs a single
[running minimum](/blogs/takeaway/shift-min-plus-recurrence-to-running-minimum) instead of
Dijkstra.

## Counting coprime pairs

Once the condition is coprimality, the question is usually *how many*, and there are three tools
in ascending order of reach.

$\varphi(n)$ counts $m \le n$ with $\gcd(m,n)=1$, so any "reduced fractions with denominator $n$"
count is a totient. Problem 72 is nothing but $\sum_{d \le N} \varphi(d)$, sieved.

[Möbius](/blogs/domain/mobius-function) handles the cases where $\varphi$ does not fit, because
$\sum_{d \mid \gcd(a,b)} \mu(d) = [\gcd(a,b) = 1]$ — an
[inclusion–exclusion](/blogs/technique/inclusion-exclusion-principle) indicator for coprimality
that you can push through a summation and swap the order of. Problem 202 uses it to count
totatives of $S \approx 6 \times 10^9$ restricted to one residue class mod $3$, by summing over
the squarefree divisors of $S$ rather than over $S$ itself.

The trick worth internalising is that this often needs no $\mu$ table at all. From the public
problem 73, counting reduced fractions up to a bound:

```python
data = [i * n // d for i in range(max_d + 1)]   # all fractions, coprime or not
for i in range(1, max_d + 1):
    for j in range(2 * i, max_d + 1, i):        # subtract each count from its multiples
        data[j] -= data[i]
return sum(data)                                # what remains is the coprime count
```

Seed each cell with the *unfiltered* count, then sieve out every scaled copy in increasing order.
Because index $i$ is finalised before it is subtracted from $j > i$, the sieve performs Möbius
inversion implicitly, in $O(N \log N)$ with no gcd call anywhere. The same seed-then-subtract
shape works whenever the unfiltered count is easy and the coprime one is not.

For sums that run past sieve range, pair the indicator with
[quotient blocking](/blogs/technique/quotient-blocking): only $O(\sqrt N)$ distinct values of
$\lfloor N/d \rfloor$ exist, so a coprimality-weighted sum over $d \le N$ collapses to
$O(\sqrt N)$ blocks. Problem 351 needs $\Phi(n) = \sum_{s \le n} \varphi(s)$ at $n = 10^8$ and
beyond, and gets it from the canonical-form fact read as a counting identity: every pair
$1 \le a \le b \le v$ has exactly one reduced form, scaled by some $d$, so
$\sum_{d \le v} \Phi(\lfloor v/d \rfloor) = v(v+1)/2$. Solved for $\Phi(v)$, that recursion
touches only the $O(\sqrt n)$ quotient values, and with a sieved table below $n^{2/3}$ it runs in
$O(n^{2/3})$ — the 73-style seed-then-subtract idea, lifted past the reach of any array. Mind the
width when you do this: $\Phi(n) \approx 3n^2/\pi^2$ outgrows 64 bits once $n$ passes about
$5.5 \times 10^9$, so a coprime *count* can overflow long before its argument looks large.

Nothing ties the indicator to a sum. Problem 754 wants a *product* over the integers coprime to
$n$, and in a product the indicator rises into the exponent:

$$\prod_{\substack{k \le n \\ \gcd(k,n) = 1}} k = \prod_{d \mid n} \Bigl(\prod_{\substack{k \le n \\ d \mid k}} k\Bigr)^{\mu(d)} = \prod_{d \mid n} \bigl(d^{\,n/d}\,(n/d)!\bigr)^{\mu(d)}.$$

Swap the order of the products and quotient blocking carries over, with exponents in place of
terms: across one block of constant $\lfloor N/d \rfloor$ the $\mu(d)$ add up to a difference of the
[Mertens function](/blogs/technique/mertens-function-application). Two things change in the
multiplicative setting. Exponents
[reduce modulo $p - 1$](/blogs/takeaway/reduce-exponent-modulo-group-order) rather than $p$, which
[Fermat](/blogs/domain/fermats-little-theorem) allows only for bases coprime to $p$, a condition
met here because $p > N$. And a negative exponent is an inverse, so keeping the $\mu = +1$ and
$\mu = -1$ running products apart costs one inversion per block instead of one per element.

## How to reason about it

**Look for coprimality you are given for free.** Consecutive integers, $n$ and $n \pm 1$; a
fraction already stated in lowest terms; $a$ and $b$ in $a + b = c$ with any two of the three
coprime — in problem 127 a common factor of $a$ and $b$ would divide $c$, so a single
$\gcd(a,b) = 1$ test delivers all three pairwise conditions. Free structure of this kind is the
cheapest speed-up in the problem.

**Prefer generating primitives to testing candidates.** The density of coprime pairs is
$1/\zeta(2) = 6/\pi^2 \approx 0.608$, so filtering by gcd throws away only about $39\%$ of the
work — a constant factor, and often the honest choice at small $N$. But a `gcd` in the innermost
loop of an $O(N^2)$ scan is a signal that the enumeration is wrong: rewriting it as primitive
$\times$ scale, or Möbius-inverting it, changes the exponent rather than the constant.

**Watch the edges.** $\gcd(0, n) = n$, so $0$ is coprime only to $\pm 1$; $\gcd(1, n) = 1$ always,
and the pair $(1,1)$ is a favourite off-by-one. *Pairwise* coprime is strictly stronger than
*setwise* — $\{6, 10, 15\}$ has overall gcd $1$ with no two members coprime — and problems that
build a graph or a matching out of "shares a prime factor" (355, 838, 886) live precisely in that
gap. Check which one a theorem needs: $\langle 6, 10, 15 \rangle$ still has finitely many gaps,
because that needs only the setwise gcd, but the single-cycle walk of problem 718 needs a coprime
*pair* and has none here. Primitivity also does not survive a substitution unexamined. Problem
764's $\gcd(x,y,z) = 1$ is a condition on $(x, y, z)$, not on the triple $(4x, y^2, z)$: its
solution $(3, 4, 20)$ becomes $(12, 16, 20)$, which is not primitive, so the factor of $4$ must be
divided out before Euclid's formula applies. Finally, coprime is not prime: $\gcd(8, 9) = 1$ says
nothing about either number's factorisation beyond its disjointness from the other's.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0127](/solutions/0127/) — abc-hits
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ○ [0278](/solutions/0278/) — Linear Combinations of Semiprimes
- ● [0351](/solutions/0351/) — Hexagonal Orchards
- ○ [0355](/solutions/0355/) — Maximal Coprime Subset
- ○ [0388](/solutions/0388/) — Distinct Lines
- ● [0407](/solutions/0407/) — Idempotents
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ○ [0441](/solutions/0441/) — The Inverse Summation of Coprime Couples
- ○ [0451](/solutions/0451/) — Modular Inverses
- ● [0510](/solutions/0510/) — Tangent Circles
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ○ [0540](/solutions/0540/) — Counting Primitive Pythagorean Triples
- ○ [0560](/solutions/0560/) — Coprime Nim
- ○ [0574](/solutions/0574/) — Verifying Primes
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ○ [0652](/solutions/0652/) — Distinct Values of a Proto-logarithmic Function
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0718](/solutions/0718/) — Unreachable Numbers
- ○ [0727](/solutions/0727/) — Triangle of Circular Arcs
- ○ [0730](/solutions/0730/) — Shifted Pythagorean Triples
- ○ [0748](/solutions/0748/) — Upside Down Diophantine Equation
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0758](/solutions/0758/) — Buckets of Water
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0777](/solutions/0777/) — Lissajous Curves
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ○ [0785](/solutions/0785/) — Symmetric Diophantine Equation
- ○ [0787](/solutions/0787/) — Bézout's Game
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0838](/solutions/0838/) — Not Coprime
- ○ [0841](/solutions/0841/) — Regular Star Polygons
- ○ [0886](/solutions/0886/) — Coprime Permutations
- ● [0932](/solutions/0932/) — $2025$
- ○ [0958](/solutions/0958/) — Euclid's Labour
- ○ [0975](/solutions/0975/) — A Winding Path
- ● [0988](/solutions/0988/) — Non-attacking Frogs

<!-- /problems -->
