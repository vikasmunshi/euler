<!-- tags: [decompose-overlap] -->
<!-- status: final -->
# Decompose overlapping conditions

Some conditions are tangled: "a number containing all of the digits $0$, $1$ and A",
"a triple of points whose triangle holds the origin", "the messages a cipher leaves
fixed". Tested head-on, each forces an enumeration you cannot afford — the objects
number in the billions, or the constraints entangle every variable with every other.
The move that recurs across the problems below is to stop testing the tangled thing
and instead *rewrite* it as a combination of counts over pieces that are each easy:
add them with alternating signs when the pieces overlap, or multiply them when the
pieces are independent. The signed-sum version has a name —
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle) —
and it is the single most common way these problems get unstuck.

## The idea

The [inclusion–exclusion principle](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
counts a union of overlapping sets by correcting for the double-counting:

$$|A_1 \cup \dots \cup A_k| = \sum_i |A_i| - \sum_{i<j} |A_i \cap A_j| + \dots + (-1)^{k+1} |A_1 \cap \dots \cap A_k|,$$

or, run the other way, it counts the elements in *all* of several sets by signing the
counts of elements allowed to *miss* some of them. The reason it earns its keep is
almost always the same: the intersections are easy even when the union is not. The
tangled requirement "must contain $x$" is awkward, but its negation "must avoid $x$"
shrinks the alphabet and turns the count into a closed-form product.

**The archetype** is problem 1, "Multiples of 3 or 5". The multiples of $3$ and the
multiples of $5$ overlap on the multiples of $15$, so summing the two progressions
independently double-counts that overlap — and one subtraction undoes it. Each of the
three parts is a closed-form arithmetic series, so the whole answer is a few
multiplications with no loop at all:

```python
def sum_arithmetic_series(d, *, max_limit):
    n = (max_limit - 1) // d
    return d * (n * (n + 1)) // 2

# 3 + 5 − 15: add the two progressions, subtract the overlap
return sum_arithmetic_series(3, max_limit=N) \
     + sum_arithmetic_series(5, max_limit=N) \
     - sum_arithmetic_series(15, max_limit=N)
```

That is the two-set case. The same identity scales to more overlapping conditions
without changing shape. Problem 162 counts hexadecimal strings that contain *all* of
$0$, $1$ and A: it sums over the eight subsets $S \subseteq \{0, 1, \mathrm{A}\}$,
counting strings drawn from the alphabet with $S$ *removed* (so those digits are
guaranteed absent) and signing each term by $(-1)^{|S|}$. Eight closed-form products
replace an enumeration of $15 \times 16^{15}$ strings. Problem 269 pushes the order
higher still: "a polynomial with at least one integer root" becomes a signed sum over
the $2^{10}-1$ non-empty subsets of the eleven possible roots, each intersection
count supplied by a [digit DP](https://en.wikipedia.org/wiki/Dynamic_programming).
The sign is just the parity of the subset in every case.

**Complementary counting** is inclusion–exclusion's smallest instance — two terms,
"everything minus the bad" — and it is the workhorse for any "at least one"
requirement. Problem 725 wants numbers containing a digit equal to half their digit
sum; it counts *all* numbers of the right digit sum and subtracts those that avoid
that digit, each side a clean [DP](https://en.wikipedia.org/wiki/Dynamic_programming)
([the complement rule](https://en.wikipedia.org/wiki/Complementary_event) handling
"at least one" regardless of multiplicity). Problem 710 counts palindromic
compositions containing a part equal to $2$ as *all* palindromes minus those avoiding
$2$; problem 184 counts triangles containing the origin as $\binom{N}{3}$ minus the
triangles that fit in a half-plane. In each, the awkward positive condition is easy to
state in the negative.

**The [Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function) is
inclusion–exclusion over divisors.** When the tangled condition is "coprime to $n$" or
"exactly divisible by a square", the signed sum runs over the squarefree divisors with
$\mu(d) = (-1)^{\omega(d)}$ as its sign. Problem 202 counts totatives of $S$ in one
residue class this way — a sum over the squarefree divisors of $S$ rather than a walk
to $6 \times 10^9$; problem 745 uses $\mu$ to isolate the *exact* maximal square divisor
of each integer. The mechanism is identical to counting over subsets; the "sets" are
just the divisibility conditions.

**When the pieces are independent, the decomposition multiplies instead of signing.**
This is the same instinct — break one tangled quantity into separable parts — but the
parts don't overlap, so no correction is needed. Problem 182 counts fixed points of an
RSA map by the [Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem):
a message is unconcealed mod $pq$ exactly when it is unconcealed mod $p$ *and* mod $q$,
and the two prime-modulus counts simply multiply. Problem 213 turns an intractable
joint distribution of $900$ fleas into $\mathbb{E}[E] = \sum_t \prod_f (1 - p_f(t))$ —
[linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Linearity)
splits the sum over target squares, and the fleas' independence factors the product.
Problem 178 collapses "has visited all ten digits" into two independent booleans,
*reached $0$* and *reached $9$*, shrinking a $2^{10}$ state set to $4$.

## How to reason about it

The trigger is linguistic. "At least one", "contains all of", "the union of",
"coprime to", "or" — each names an overlap, and each is a cue to stop enumerating the
combined thing and decompose it. The discipline that makes the decomposition pay off:

- **Choose pieces that are individually easy.** The whole method is worthless if the
  intersection counts are as hard as the union. Forbidding beats requiring: "avoid this
  digit" gives a smaller alphabet and a closed-form product (problem 162), where
  "contain it" gives nothing. Pick the split whose parts have a closed form or a small
  DP state.
- **Overlap adds with signs; independence multiplies — and you must know which.**
  Inclusion–exclusion is only correct when you have genuinely accounted for the overlaps,
  and a product is only correct when the parts are genuinely independent. Verify it:
  the RSA counts multiply *because* $p$ and $q$ are coprime and CRT makes the residues
  independent; the fleas' contributions multiply *because* they move independently. An
  assumed independence that isn't there corrupts the answer silently.
- **Get the sign right.** The inclusion–exclusion sign is the parity of the subset,
  $(-1)^{|S|}$ (or $\mu(d)$ over divisors). It is the one place a typo produces a
  plausible-looking wrong number rather than a crash — derive it, don't guess it.
- **Watch the seams the decomposition opens.** The corrections all live where the clean
  count over-includes: leading-zero strings that are really shorter numbers (problems 162
  and 725 subtract them off explicitly), boundary and collinear cases a half-plane sweep
  misses (problem 184 adds a second inclusion–exclusion term for triples through the
  origin). And in C specifically, the subtractions bite twice — truncating integer
  division and a `%` that can go negative both need explicit repair
  (`((total % mod) + mod) % mod`) that Python's flooring arithmetic gives for free.

The payoff is a change of kind, not degree: an enumeration that is exponential or
outright infinite becomes a polynomial number of closed-form or DP evaluations — $2^k$
signed terms, each cheap. When a single test refuses to be computed directly, the
question to ask is not "how do I test this faster" but "what independent or
overlapping pieces does this test decompose into".

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0205](/solutions/0205/) — Dice Game
- ● [0213](/solutions/0213/) — Flea Circus
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0679](/solutions/0679/) — Freefarea
- ● [0710](/solutions/0710/) — One Million Members
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence

<!-- /problems -->
