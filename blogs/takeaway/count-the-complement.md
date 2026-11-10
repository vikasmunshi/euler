<!-- tags: [count-the-complement] -->
<!-- status: final 2026-11-10T18:40Z -->
# Count the complement

Some sets are hard to count directly. Their members share no structure, or the defining
condition mixes "and" with "or" in a way that makes direct counting messy. Often the
*complement* of the set, the things that fail, is easy to describe. Then I count the failures
and subtract them from a total I already know: $|A| = |U| - |U \setminus A|$. The six problems
below all have this shape. Each time, the move works for the same reason: negating the
condition turns a hard "there exists" into a "for all", or turns a scattered set into a
structured one.

## The idea

The identity is the simplest case of
[inclusion–exclusion](/blogs/technique/inclusion-exclusion-principle), and in set theory it is
just the [complement](https://en.wikipedia.org/wiki/Complement_(set_theory)). For it to pay,
two things must be true:

1. **The universe $U$ is easy to count.** Usually it has a closed form: $n!$ permutations,
   $N$ integers, $T^2$ ordered pairs, a polynomial in the grid size.
2. **The complement is structured.** It has a
   [bijection](https://en.wikipedia.org/wiki/Bijection) to something countable, it is small,
   or it factors where the target does not.

When the target is a sum and not a count, the identity becomes
$\sum_{A} w = \sum_{U} w - \sum_{U \setminus A} w$. 833 uses that form.

Negation explains why the complement is so often the easier side, by
[De Morgan's laws](https://en.wikipedia.org/wiki/De_Morgan%27s_laws). "Some digit is shared"
is a union over ten digits. "No digit is shared" is one condition: one digit set lies inside
the other's complement. "Some path is open" is about all paths at once. "Every path is
blocked" turned out to have a single local cause. An existential condition is hard to count,
because each member can satisfy it in many ways and must not be counted twice. A universal
condition can usually be checked one piece at a time, so its count factors.

## Six complements

| Problem | Target | Universe | Complement counted |
|---|---|---|---|
| 612 | pairs whose digit sets meet | all $T^2$ ordered pairs | disjoint pairs, by a subset-sum transform |
| 628 | open chess positions | all $n!$ permutations | closed positions: a full anti-diagonal |
| 668 | square-root-smooth $n \le N$ | all $N$ integers | $n = p\,m$ with $m \le p$, $p$ the largest prime |
| 994 | triangles of segments | non-dominating cell triples | triples meeting at one point |
| 833 | $c$ over fundamental Pell solutions | the sum over *every* $f$ | the sparse non-fundamental $f = T_m(y)$ |
| 520 | simbers (no leading zero) | all digit strings | strings starting with $0$ |

**612 (Friend Numbers).** Two numbers are friends when their
[digit sets](/blogs/technique/digit-dp) meet. "Meet" is a union over ten digits, so direct
counting means adding $c_S c_T$ over every intersecting pair of 10-bit masks. The disjoint
pairs are simpler: $T$ is disjoint from $S$ exactly when $T \subseteq \overline S$. So the
count of disjoint partners is one lookup in the
[sum-over-subsets transform](/blogs/technique/sum-over-subsets-transform) of the class counts.
The friendly count is then $(T^2 - D - T)/2$: the universe, minus the disjoint pairs, minus the
self-pairs, halved for order. The complement turns a $1024^2$ double loop into a $10 \cdot 1024$
transform.

**628 (Open Chess Positions).** A position is a [permutation](/blogs/domain/permutation). It is
"open" if some monotone [lattice path](/blogs/domain/lattice-path) avoids every pawn, and
"some path exists" is hard to count. The closed positions have a single local cause. Every path
crosses each anti-diagonal exactly once, so a fully occupied anti-diagonal blocks every path.
The converse also holds, which I checked by exhaustive search. For a permutation, a full
anti-diagonal means a reversed corner block, and a permutation has at most one block in each
corner. That makes the inclusion–exclusion over the closed positions three terms long. A
[telescoping](/blogs/technique/telescoping-series) step then collapses $n!$ minus that count
into a closed form in the left factorial.

**668 (Square Root Smooth Numbers).** The [smooth numbers](/blogs/domain/smooth-number) have
no structure that makes them easy to list. The failures do. Write $n = p\,m$ with $p$ the
largest prime factor. Then $n$ fails exactly when $m \le p$, and every such pair $(p, m)$ is a
distinct failure. The complement is in [bijection](https://en.wikipedia.org/wiki/Bijection)
with pairs (prime, small cofactor), and counting it needs only $\sum p$ over small primes and
$\sum \lfloor N/p \rfloor$ over large ones. The second sum regroups into
[prime counts](/blogs/domain/prime-counting-function) at the floor quotients, which the
[Lucy_Hedgehog sieve](/blogs/technique/lucy-hedgehog-sieve) supplies.

**994 (Counting Triangles).** Here the complement is applied twice. First, a triangle is three
segments that meet pairwise. Segments $(i,j)$ and $(i',j')$ fail to meet exactly when one
dominates the other in both coordinates. Counting triples with no dominating pair is a small
polynomial in binomials. I fitted its coefficients from tiny grids, since a valid triple uses
at most three distinct values per coordinate. Second, some of those triples meet at a single
point and are not triangles. By projective duality, concurrent segments become collinear cells
on a line of negative slope. Collinear triples are counted by their outer pair, with weight
$\gcd(a,b) - 1$ ([lattice points](/blogs/domain/integer-lattice) strictly between). The heavy
part is that gcd-weighted sum, computed with
[totient prefix sums](/blogs/technique/totient-summatory-recursion). The count is "everything
non-dominating, minus the degenerate ones". The degenerate ones are the only part needing real
number theory.

**833 (Square Triangle Products).** This is the weighted version. The terms to sum come from
[Pell](/blogs/technique/pells-equation) families indexed by their *fundamental* solution $f$,
and "$f$ is fundamental" cannot be tested cheaply for each of $\sim 10^{11}$ candidates. If I
drop that condition, the sum over *every* $f$ in a progression is a polynomial in the number of
terms, which [Lagrange interpolation](/blogs/technique/lagrange-polynomial) evaluates in
constant time. The non-fundamental values are exactly the later family members
$f = T_m(y)$ ([Chebyshev](/blogs/domain/chebyshev-polynomials) values). They grow at least
quadratically, so only about $\sqrt F$ of them exist, and they can be generated directly and
subtracted. Summing everything is cheap, and the error is sparse and enumerable.

**520 (Simbers).** The complement here is a small correction. The
[EGF](/blogs/technique/exponential-generating-function) $\cosh^5 x\,(1+\sinh x)^5$ counts every
digit string with the simber property, leading zeros included, because the EGF treats all ten
symbols alike. A first-digit restriction would break that symmetry. So I count all strings and
subtract those that start with $0$. Pinning a $0$ in front only flips that digit's parity
requirement, so the subtracted set is another EGF of the same shape. The two power sums share
all their machinery.

## How to reason about it

**Look for the existential.** "At least one", "some", "there is a path", "they share a digit":
a union is hard to count without double counting. Negate it, and check whether the
"for all" / "none" version factors, has a local cause, or has a bijection.

**Know the universe exactly.** The method moves all difficulty into $|U|$ and the complement,
so $U$ needs a closed form or a cheap count. Choosing it is part of the design. In 994 the
universe is not "all triples" but "all non-dominating triples", a set that is itself a
complement and still has a polynomial count. In 520 the universe includes the leading-zero
strings deliberately, because the symmetric set is the one that has a clean generating function.

**Prefer a sparse error.** 833 shows the generalisation: when a filter is expensive, sum
without it and subtract what it would have removed, provided that set is small and can be
listed. This is the same reasoning as a sieve, which removes composites instead of finding
primes.

**Check the boundary of the bijection.** A complement argument depends on the claimed
characterisation being *exact*. In 628, "closed iff a full anti-diagonal" needed both
directions. In 668, the edge case $n = 1$ is smooth and never appears among the pairs. In 612,
the self-pairs have to be removed separately. Off-by-one terms hide there, so I compare against
a brute force on small inputs. Every one of these six solutions keeps one for that reason.

**Mind the arithmetic.** A subtraction under a modulus can go negative, and $T^2$ can overflow
before the difference becomes small. 612 computes $T^2 - D$ exactly in 128-bit arithmetic and
reduces once at the end, which also avoids needing a modular inverse of $2$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0520](/solutions/0520/) — Simbers
- ● [0612](/solutions/0612/) — Friend Numbers
- ● [0628](/solutions/0628/) — Open Chess Positions
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0833](/solutions/0833/) — Square Triangle Products
- ● [0994](/solutions/0994/) — Counting Triangles

<!-- /problems -->
