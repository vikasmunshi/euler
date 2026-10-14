<!-- tags: [subset-sum-problem] -->
<!-- status: final 2026-10-14T07:24Z -->
# Subset sum problem

The [subset sum problem](https://en.wikipedia.org/wiki/Subset_sum_problem) asks whether some subset
of a multiset of integers adds up to a target $T$. As a decision problem it is
[NP-complete](https://en.wikipedia.org/wiki/NP-completeness), and that label scares people off more
than it should. Project Euler almost never asks the plain decision question. It asks to *count* the
subsets that hit a target, or a whole range of targets, or a residue class. It asks whether every
sum is *distinct*, or for the subset that comes *closest* to a target. Every one of those variants
has a structural weak point, and the problems below are each built around one. The skill is
recognising the subset sum hiding in the problem (a partition, a sum of reciprocals, a divisor
of a primorial) and then finding the weak point that this instance offers.

## The idea: three ways in

A set of $n$ items has $2^n$ subsets, so brute force stops around $n \approx 25$. Past that, there
are three standard escapes. Each one is cheap in a different quantity, so the first question is
always *what is small here?*

| What is small | Method | Cost |
|---|---|---|
| the range of sums, $M$ | [dynamic programming](/topics/technique/dynamic-programming) over the sum axis ([0/1 knapsack](/topics/technique/knapsack-problem)) | $O(n \cdot M)$ |
| the number of items, $n \lesssim 50$ | [meet in the middle](/topics/technique/meet-in-the-middle-attack) | $O(2^{n/2} \cdot n)$ |
| the number of *distinct* sub-problems | [branch and bound](/topics/technique/branch-and-bound) + [memoization](/topics/technique/memoization) | the number of reachable states |

**The sum axis is short.** Use a table indexed by the sum $s$, and fold the items in one at a
time. When counting, the table holds the coefficients of the
[generating function](/topics/domain/generating-function)

$$F(x) = \prod_{a \in S} \left(1 + x^{a}\right) = \sum_s c_s\, x^s,$$

and $c_s$ counts the subsets that sum to $s$: each factor chooses "leave $a$ out" ($1$) or "put it
in" ($x^a$), and the exponents add. Multiplying in one factor is a single in-place pass:

```python
for a in items:
    for s in range(top, a - 1, -1):   # descending: each item used at most once
        count[s] += count[s - a]
```

The descending loop is the one detail you have to get right. If you sweep upward, `count[s - a]`
has already been updated for this item, so $a$ can be used again. You get the *unbounded* knapsack
(the multisets, as in problem 31's coin sums) instead of the subsets. Problem 249 is this loop
almost exactly: every subset of the primes below $5000$, counted by sum, with only the prime sums
kept. The table has about $1.5$ million cells, which is nothing next to $2^{669}$ subsets. Its
NumPy version gets the descending semantics a different way, from the buffered overlapping-slice
add `count[a:] += count[:-a]`. Problem 201 adds a second axis, the subset *size*, because it
wants $50$-element subsets only. It also caps every count at "two or more", since all it needs to
know is whether a sum is *unique*. With that cap, each row fits in one
[bitset](/topics/technique/bit-array), and an item is folded in with a shift and an OR.

When the question is about sums *modulo* $m$, the sum axis is short by construction. Work in
$\mathbb{Z}[x]/(x^m - 1)$ and the exponents wrap around by themselves. Problem 250 has a quarter
of a million elements but only $250$ residues. Equal residues give equal factors, so
$(1 + x^r)^{c_r}$ can be expanded once with the binomial theorem. The cost no longer depends on
the size of the set at all.

**The item list is short but the sums are huge.** Split the items into two halves and list each
half's $2^{n/2}$ sums. Then match them up: sort and sweep with two pointers to find the pair
nearest the target, or use a hash map to count exact complements. Forty items become two lists of
about a million sums each. Problem 461 uses this on a continuous version: four terms that must
land near $\pi$ become two sorted lists of pair sums, swept toward each other. Problem 266 asks for
the largest divisor of a primorial below its square root. That is a subset sum on the
*logarithms* of $42$ primes, with a target of half the total: too many items to enumerate, but
exactly the right number to split in half. Problem 152 is the hard version. Its sum of
reciprocal squares only becomes an integer subset sum after multiplying by a common denominator.
It only becomes small enough to split after a number-theoretic argument removes most of the large
primes, and turns each remaining prime's multiples into a short list of admissible blocks.

**The sums collide a lot.** If many different subsets reach the same remaining budget, recursing
on (position, remaining budget) and memoising collapses the tree. Problem 755 counts subsets of
Fibonacci numbers with sum at most $n$. The pruning step is simple: whenever the budget covers the
whole remaining suffix, return $2^{\text{rest}}$ at once. With that, $2^{62}$ implicit
subsets come down to a few hundred states.

## Other questions, other weak points

Not every problem on this page asks for a count. The *special sum set* trilogy (103, 105, 106)
asks whether all subset sums are **distinct**, together with an ordering rule. Two ideas run
through all three. First, look at disjoint pairs $(B, C)$ as one assignment of each element to
"in $B$", "in $C$" or "in neither". That gives $3^n$ pairs rather than $4^n$, and the
complement-submask loop `c = (c - 1) & comp` visits them directly. Second, a *sorted* set lets you
discard most pairs without testing them: if one subset dominates the other element by element, its
sum is larger regardless of the values. Problem 106 counts the pairs that survive this filter with
a Catalan-number argument and never looks at a single sum.

Some problems are about whether a target *can* be reached. Problem 772 asks when every
$k$-bounded partition can be split into two equal halves, which is a
[partition problem](https://en.wikipedia.org/wiki/Partition_problem) (subset sum with
$T = \tfrac12 \sum$) over every input at once. The worst cases are the uniform partitions, whose
subset sums are all multiples of a single part size. That turns the problem into a divisibility
condition and a closed form. Problem 382 counts subsets satisfying the polygon inequality (the
largest element is less than the sum of the others), which is again a condition on subset sums,
taken over a sequence too long to fold item by item.

## How to reason about it

- **Find out what is small before choosing a method.** Compare the width of the sum range, the
  number of items, and the number of distinct residues or states. Each method above is cheap in
  exactly one of them. A sum range of $10^6$ means DP, $40$ items with $10^{15}$-sized values means
  meet in the middle, and a modulus means the cyclic generating function.
- **Track only what the question needs.** The full count, a count capped at two, a single
  reachable bit, or a count modulo $10^{16}$ each give a smaller table than the one before. Problem
  201's two-bit cap and problem 249's modular counters are both this move.
- **Make the arithmetic exact first.** Reciprocals, logarithms and $e^{x}$ invite floating-point
  equality tests that silently go wrong. Clear denominators to integers (152), or compare with a
  known tolerance and a cancellation-free routine such as `expm1` (461), before the combinatorics
  starts.
- **Get the 0/1 loop direction right and test against brute force.** A forward-sweeping loop that
  counts multisets gives plausible-looking wrong numbers. For $n \le 20$, enumerating all $2^n$
  subsets is instant and catches it.
- **Group identical items.** Many equal elements (or equal residues) contribute one factor
  $(1 + x^a)^{c}$, which a row of binomial coefficients expands in one step. Don't fold them in one
  at a time.

[Knapsack problem](/topics/technique/knapsack-problem) covers the optimisation version, where items
carry a value as well as a weight (problem 732's escaping trolls are a dressed-up instance).
[Generating function](/topics/domain/generating-function) explains the polynomial view used above
in more depth.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0382](/solutions/0382/) — Generating Polygons
- ● [0461](/solutions/0461/) — Almost Pi
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0732](/solutions/0732/) — Standing on the Shoulders of Trolls
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions

<!-- /problems -->
