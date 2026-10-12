<!-- tags: [inclusion-exclusion-principle] -->
<!-- status: final -->
# Inclusion–exclusion principle

The [inclusion–exclusion principle](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
counts a union by adding and subtracting intersections:
$|A \cup B| = |A| + |B| - |A \cap B|$, and in general

$$\Big|\bigcup_{i} A_i\Big| = \sum_{\emptyset \ne S} (-1)^{|S|+1} \Big|\bigcap_{i \in S} A_i\Big|.$$

It keeps coming back for one reason. Conditions like "contains each of these digits", "has at
least one integer root" and "is coprime to $S$" are awkward to impose directly. Their
*intersections*, though, are often trivial to count: forbid a set of symbols, pin a set of
positions, demand divisibility by a product. Inclusion–exclusion is the bookkeeping that turns the
easy intersections into the hard union, and the problems below range from the three-term version
in Problem 1 to Möbius-weighted sums over divisors.

## The idea: count the easy thing with signs

Phrase the target as "objects having **none** of the bad properties $B_1, \dots, B_k$". Let
$N(S)$ count the objects that have *every* bad property in $S$. Then the count you want is

$$\sum_{S \subseteq \{1..k\}} (-1)^{|S|}\, N(S).$$

An object with exactly $j$ bad properties is counted $\sum_i (-1)^i \binom{j}{i}$ times, which is
$1$ if $j = 0$ and $0$ otherwise. That's the whole proof, and it is also the check to run when you
adapt the formula to a new weighting. The skeleton is short:

```python
total = 0
for k in range(len(bad) + 1):
    for S in combinations(bad, k):
        total += (-1) ** k * count_with_all(S)    # objects having every bad property in S
```

[Problem 1](/solutions/0001/) is the smallest case. Multiples of 3 or 5 are multiples of 3, plus
multiples of 5, minus multiples of 15, each one an arithmetic series in closed form:

```python
return str(
    sum_arithmetic_series(3, max_limit=max_limit)
    + sum_arithmetic_series(5, max_limit=max_limit)
    - sum_arithmetic_series(15, max_limit=max_limit)
)
```

## Four shapes in the problems

**A handful of explicit conditions.** Use this when $k$ is small enough to enumerate all $2^k$
subsets. Problem 162 counts hexadecimal strings containing each of `0`, `1` and `A`. Strings that
*avoid* a chosen subset of those digits are just a power of the reduced alphabet size, so eight
signed terms do the job, with the leading-zero rule folded into each one. Problem 269 counts
digit polynomials with at least one integer root. Only a few candidate roots are possible, so it
sums over non-empty subsets of them, and a digit DP counts the polynomials that vanish at every
root in the subset. Problem 234 wants numbers divisible by *exactly one* of two primes. Changing
the weighting gives $\Sigma_p + \Sigma_q - 2\Sigma_{pq}$: the overlap is subtracted twice, because it
must contribute nothing at all.

**Symmetric conditions, so $N(S)$ depends only on $|S|$.** Then the $2^k$ terms collapse into
$k + 1$ binomially weighted ones. Problem 239 counts permutations in which a prescribed number of
prime-labelled discs sit at home. Pinning any $j$ of the remaining primes leaves a number of
free arrangements that depends only on $j$, so the alternating sum has one binomially weighted term
per $j$. That's the [derangement](/topics/domain/derangement) formula, generalised to a partial
derangement in which only some positions are constrained.

**Divisibility conditions, so the signs are the Möbius function.** When the bad properties are
"divisible by $p$" for the primes $p$ dividing something, an intersection is divisibility by a
product. The sign of a squarefree $d$ is then exactly the
[Möbius function](/topics/domain/mobius-function) $\mu(d)$, which is zero for every $d$ with a
square factor. Problem 193 counts [squarefree](/topics/domain/square-free-integer) numbers this
way, weighting each square divisor count by $\mu$. Problem 202 counts the residues coprime to $S$
over the squarefree divisors of $S$. Problem 319 runs the same inclusion–exclusion over the
primes dividing an exponent, and evaluates it with a
[Mertens-function](/topics/technique/mertens-function-application) recursion. Terms with
$\mu(d) = 0$ cost nothing, so the sum runs over far fewer than $2^k$ subsets.

**One condition: count the complement.** With a single bad property the formula is just
"everything minus the bad ones". Problem 710 counts palindromic compositions with at least one
part equal to $2$ as all palindromic compositions minus those avoiding $2$. Problem 725 sums
numbers with a given digit sum that contain at least one digit $h$ in the same way. Problem 184
counts triangles containing the origin as all triangles minus the bad ones. That first
subtraction overcounts collinear triples, so it needs a second-order inclusion–exclusion
correction. Problem 113 counts non-bouncy numbers as increasing plus decreasing numbers. That
counts the repdigits twice, so it subtracts them once.

## How to reason about it

- **Turn "at least one" and "all of" into "none of".** Both are unions or intersections of
  simple events. Rephrase the condition until each $N(S)$ is a product, a power or a floor.
- **Look for structure before enumerating $2^k$ subsets.** Symmetry makes $N(S)$ depend on $|S|$
  alone. Multiplicativity turns the signs into $\mu$, which vanishes on most subsets. Without one
  of these, inclusion–exclusion is only practical for small $k$.
- **Write the weights, then check them.** For "exactly one", "exactly $j$" or "at least two", work
  out the coefficient each object receives and confirm it is $1$ for the objects you want and $0$
  otherwise. Problem 234's factor of $2$ comes straight out of that check.
- **Look for a second overlap.** A correction can itself overcount, as with 184's collinear
  triples. Brute-force a small case and compare. A missing second-order term shows up immediately.
- **Signs under a modulus.** Alternating sums produce negative intermediates. Python's `%` with a positive
  modulus is never negative, but C's `%` can return a negative value. Problem 725 normalises with
  `((x % m) + m) % m`, and 710 applies a sign correction after every subtraction.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0710](/solutions/0710/) — One Million Members
- ● [0725](/solutions/0725/) — Digit Sum Numbers

<!-- /problems -->
