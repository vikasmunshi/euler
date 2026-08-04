<!-- tags: [brute-force-search] -->
<!-- status: final -->
# Brute-force search

[Brute-force search](https://en.wikipedia.org/wiki/Brute-force_search) is the method with no
ideas in it: enumerate every candidate, test each one, keep what passes. It is where nearly
every problem below starts, and — the part worth internalising — where a good number of them
correctly end. These are not forty-one failures of imagination. They are a catalogue of what
actually separates an exhaustive search that finishes in a millisecond from one that never
finishes at all, and it is almost never the language or the inner-loop tuning. It is the space
you chose to enumerate.

## Three decisions, only one of them usually conscious

Every exhaustive search answers three questions:

1. **What is the candidate space?** What object are you generating?
2. **In what order do you walk it?** Order decides whether you can ever stop early.
3. **What does one test cost?** And can the test be moved out of the loop?

Most people only think about (3), because that is where the code looks slow. The wins are
overwhelmingly in (1) and (2). Everything below is a way of shrinking or reordering the space
while leaving the "try everything" strategy intact — which is why these all still count as
brute force, and why the label tells you much less about a solution's cost than people assume.

## A constraint removes a loop

The first cut is free and it is the one most often missed: if the candidates satisfy an
equation, do not enumerate the variable the equation determines. Problem 9 wants a Pythagorean
triple with a fixed sum $S$. That is three unknowns, so the reflex is three loops — but the sum
constraint pins the third, and the ordering $a < b < c$ both removes permutations and supplies
bounds. From `solutions/public/p0009/`:

```python
a * b * c
for a in range(1, sum_sides // 4 + 1)
for b in range(a, sum_sides // 2)
for c in (sum_sides - a - b,)
if a**2 + b**2 == c**2
```

The `for c in (…,)` is a one-element loop — a derivation wearing a loop's clothes. Two nested
scans do the work of three, and $O(S^3)$ becomes $O(S^2)$.

The ordering half of that trick generalises past deduplication. Problem 90 pairs two dice, so
the pairs are unordered: iterating `for j in range(i, n)` instead of `range(n)` halves the space
and, more importantly, states the symmetry in the loop header where a reader can check it.
Problem 93's four digits are drawn $a<b<c<d$, which is why its outer search is 126 sets rather
than 10,000 tuples.

## Monotone order buys you a `break`

If you can walk the space so that a failing candidate proves all later candidates fail too, the
scan stops being exhaustive without becoming approximate. Problem 4 searches downward for the
largest palindromic product and keeps the best so far, so the inner loop can quit the moment the
product drops below it:

```python
ab = a * b
if ab <= largest_palindrome:
    break
```

That `break` is only legal because `b` descends and `a` is fixed, making `a * b` monotone.
Problem 23 gets the same leverage from sortedness — its abundant numbers come out in increasing
order, so once a pair sum passes the ceiling every later `j` does as well and the inner loop
ends. The discipline is to be able to name the monotonicity out loud. A `break` justified by
hope rather than by an ordering argument is the most common way an otherwise-correct brute force
silently returns the wrong answer on an input you did not test.

## Count instead of enumerating

The innermost loop of a search is frequently not a search at all — it is a counting question
with a closed form. Problem 86 has three cuboid dimensions and only needs, for each candidate,
*how many* $(b, c)$ pairs sum to a given value under the ordering cap. So it never enumerates
`c` at all:

```python
result += b_plus_c // 2 if b_plus_c <= a + 1 else (2 * a - b_plus_c + 2) // 2
```

An $O(M^3)$ triple loop collapses to $O(M^2)$, with the third dimension surviving only as an
arithmetic expression. Whenever the innermost variable is not inspected individually — only
tallied — that loop is a candidate for deletion.

The same shape appears from the other end in problems 504 and 182, where the outer enumeration
stays genuinely exhaustive but each candidate is settled in $O(1)$: 504 sweeps all four corner
distances and evaluates each quadrilateral's interior lattice count by
[Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem) instead of scanning points,
and 182 scans every valid RSA exponent while counting unconcealed messages with a
[CRT](/topics/technique/chinese-remainder-theorem) fixed-point formula rather than trying
messages. A brute force over parameters with a closed form inside is a perfectly respectable
algorithm, and it is a very different animal from a brute force over outcomes.

## Enumerate the cheap side of the predicate

Most of these problems ask for objects with two properties, one *generative* (you can produce
them in order) and one merely *checkable* (you can test a given object, but not enumerate them
usefully). Always generate the first and test the second. Problem 125 wants numbers that are
both palindromes and sums of consecutive squares; it enumerates the consecutive-square sums —
there are $O(\sqrt{L})$ starting points and a running accumulator makes each next one free — and tests
palindromicity, which is a string comparison. Enumerating palindromes and testing for a square
decomposition would be a far worse program for exactly the same answer.

Choosing the cheap test also means choosing a good *canonical form*. Problem 52 asks whether the
multiples of `x` are digit permutations of one another, and reduces the whole question to one
set of sorted-digit strings:

```python
if len({"".join(sorted(str(i * multiple))) for multiple in multiples_range}) == 1:
```

Sorting the digits maps every member of a permutation class to the same key, so "are these all
permutations of each other" becomes "does this set have one element". Finding the canonical form
is usually the entire work of making a brute force fast enough.

## The slow version is not disposable

The most under-rated use of exhaustive search is as ground truth. Problems 478 and 565 both
carry a deliberately naive index whose docstring calls it the *oracle* for the clever one: a
direct lattice scan and a full sieve, correct by construction, too slow for the real input, and
kept precisely so the fast solution can be checked against it on small `n`. Problems 1, 12 and
23 all keep a plain scan alongside a sharper index for the same reason.

This is why "I only wrote the brute force" is rarely wasted effort. Write it, get a verified
answer on a small case, then optimise against a known-good reference. The alternative — going
straight to the clever method and having nothing to compare it with — is how you end up with a
fast program confidently producing a wrong number.

It also gives an honest measurement of what the cleverness bought. Problem 1's benchmarks, at
limit $10^9$, put the Python scan at 43 seconds and the
[closed form](/topics/technique/closed-form-expression) at 7.7 microseconds. Rewriting the scan
in C gets it to 0.85 seconds — still five orders of magnitude behind the *interpreted* closed
form. That gap is the whole argument of
[algorithm beats language](/topics/takeaway/algorithm-beats-language), and you can only make it
if you kept the slow version.

Note that the refinement need not be a closed form. Problem 12's two indices both scan
triangular numbers and both factor by [trial division](/topics/technique/trial-division); the
faster one merely uses $\gcd(i, i+1) = 1$ to factor two numbers of roughly $\sqrt{T}$ instead of
one of size $T$. Same strategy, same loop, a structural observation applied inside it — that is
the typical distance between a naive brute force and a good one.

## When to stop cutting and change method

The combinatorial wall arrives abruptly, and three signals say you have reached it.

- **The space grows exponentially or factorially in a parameter you do not control.** Pruning
  buys a constant factor; it does not change the exponent. Move to
  [backtracking](/topics/technique/backtracking), which prunes whole subtrees at the moment a
  partial candidate becomes hopeless, or
  [meet-in-the-middle](/topics/technique/meet-in-the-middle-attack), which trades memory to turn
  $2^n$ into $2^{n/2}$.
- **The same subproblem keeps recurring.** Then the search is redundant, not just large, and
  wants [memoization](/topics/technique/memoization) or
  [dynamic programming](/topics/technique/dynamic-programming). Problem 93 does this *inside*
  its brute force: the recursion over pools of values is exhaustive, but an `lru_cache` on the
  pool collapses the repeated parenthesisations, and the whole search then runs in constant time
  over its fixed 126 digit sets.
- **You are optimising a monotone objective.** A bound on the best achievable result lets you
  discard candidates unexamined —
  [branch and bound](/topics/technique/branch-and-bound-search) — and monotonicity in a single
  parameter means [binary search](/topics/technique/binary-search-algorithm) rather than a scan.

## Details that bite

- **An unbounded scan needs a termination argument.** Problems 52, 112 and 225 all count upward
  with no ceiling, relying on a solution existing. That is fine when you can argue it, and an
  infinite loop when you cannot. Say which one it is in the docstring.
- **Test with integers, not floats.** A brute force runs its predicate millions of times, so a
  predicate that is *almost* right fails somewhere. Problem 112 compares
  `bouncy * 100 == target * n` rather than a ratio, keeping the test exact — see
  [exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality).
- **Order the guards by cost.** Put the cheap filter first; a `gcd(n, 10) == 1` test that
  rejects most candidates for nothing should run before anything that allocates. This is
  [cheap checks first](/topics/takeaway/cheap-checks-first), and in an exhaustive search it is
  worth more than anywhere else, because the loop body is executed the maximum possible number
  of times.
- **Build tables inside `solve()`.** Precomputed lists, sieves and caches belong in the
  function, sized to the input. With `--runs=N` the harness times repeated `solve()` calls, so a
  table built once at module import is free from the second run onward and the benchmark flatters
  the solution.
- **Size the space to the actual input.** A bound hard-coded for the headline case makes the
  solution wrong for every other one; derive the ceiling from the argument. See
  [size work to the input](/topics/takeaway/size-work-to-the-input).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0011](/solutions/0011/) — Largest Product in a Grid
- ● [0012](/solutions/0012/) — Highly Divisible Triangular Number
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0102](/solutions/0102/) — Triangle Containment
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0109](/solutions/0109/) — Darts
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0478](/solutions/0478/) — Mixtures
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors

<!-- /problems -->
