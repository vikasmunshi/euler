<!-- tags: [permutation] -->
<!-- status: final -->
# Permutation

A [permutation](https://en.wikipedia.org/wiki/Permutation) is a rearrangement of a set: an
ordering of its elements, or — the same thing seen from the other side — a bijection of the set
onto itself. It is the most common hidden object in the archive, because almost every problem
that says "rearrange", "shuffle", "sort", "anagram" or "pandigital" is a permutation problem in
disguise. The trouble is always the same: there are `n!` of them, and `n!` outruns every loop by
`n ≈ 13`. So the recurring skill is never "generate them all"; it is knowing which **view** of a
permutation makes the question small. I find there are four such views, and naming the right one
is usually most of the solution.

## Four ways to look at a permutation

### As a position in a list — ranking and unranking

List the `n!` permutations in some fixed order and each one gets an index, its **rank**. For
[lexicographic order](https://en.wikipedia.org/wiki/Permutation#Generation_in_lexicographic_order)
the rank has a clean arithmetic structure: the first element splits the list into `n` blocks of
`(n−1)!`, the second splits each block into `(n−1)` blocks of `(n−2)!`, and so on. That is the
[factorial number system](https://en.wikipedia.org/wiki/Factorial_number_system) — a mixed-radix
numeral whose digits pick "the k-th unused element" at each step. [Problem 24](/solutions/0024/)
asks for the millionth permutation of ten digits, and the solution never enumerates one:

```python
def recursive_solution(digits: str, permutation_number: int) -> str:
    if len(digits) == 1:
        return digits
    current, remaining = divmod(permutation_number - 1, math.factorial(len(digits) - 1))
    return digits[current] + recursive_solution(digits[:current] + digits[current + 1:], remaining + 1)
```

`n` divmods instead of a million steps. The same factorial-base idea works for orders that are
*not* lexicographic, as long as the order is defined recursively. [Problem 868](/solutions/0868/)
describes a bell-ringing rule that turns out to be the
[Steinhaus–Johnson–Trotter](https://en.wikipedia.org/wiki/Steinhaus%E2%80%93Johnson%E2%80%93Trotter_algorithm)
order, where the largest element sweeps back and forth; the rank is still a factorial-base number,
with each digit read from the left or the right end depending on the parity of the rank built so
far. Whenever a problem asks "which one is the N-th" or "how many come before this one", reach for
[numbering permutations](https://en.wikipedia.org/wiki/Permutation#Numbering_permutations), not a
generator.

### As an equivalence class — "is a permutation of"

A second family never cares about the order at all: it asks whether two numbers are *digit
permutations* of each other. The right tool is a **canonical signature** — sort the digits, or
count them into a 10-slot histogram — so that "is a permutation of" becomes plain equality, and a
dictionary keyed by signature groups every class in one pass. [Problem 62](/solutions/0062/) does
exactly that to find five cubes sharing a signature; [Problem 49](/solutions/0049/),
[Problem 52](/solutions/0052/) and [Problem 70](/solutions/0070/) use the same test as a filter.

The class view also brings **invariants**. Every rearrangement of a number's digits keeps its
digit sum, hence its residue modulo 9 (and 3). That is why no 8- or 9-digit pandigital can be
prime in [Problem 41](/solutions/0041/) (digit sums 36 and 45 are divisible by 3), and why `φ(p)
= p − 1` can never be a permutation of a prime `p` in Problem 70. When a problem turns on classes
rather than members, stop iterating over numbers and iterate over the classes themselves: the
digit class *is* a [multiset](https://en.wikipedia.org/wiki/Multiset), and the number of its
arrangements is a [multinomial coefficient](https://en.wikipedia.org/wiki/Permutation#Permutations_of_multisets)
`k! / (c₀!·…·c₉!)`. [Problem 862](/solutions/0862/) sums, over every `k`-digit number, how many
rearrangements are larger; within one class that total is just the number of *pairs* of
arrangements, so the whole sum collapses to a loop over digit-count vectors — hundreds of
thousands of classes in place of `10ᵏ` numbers. Problems 924 and 925 push the same idea further.

### As a function — cycles, order, fixed points

Read `σ` as a map `i → σ(i)` and a different structure appears: every permutation splits uniquely
into disjoint [cycles](https://en.wikipedia.org/wiki/Cyclic_permutation). The cycle type is what
governs repetition. Applying `σ` repeatedly returns to the start after the
[order](https://en.wikipedia.org/wiki/Order_(group_theory)) of `σ`, which is the least common
multiple of its cycle lengths — the engine behind the shuffle problems (a perfect riffle shuffle
in [Problem 622](/solutions/0622/) is multiplication by 2 modulo `n − 1`, so its order is a
[multiplicative order](https://en.wikipedia.org/wiki/Multiplicative_order)) and behind
[Problems 902](/solutions/0902/) and [903](/solutions/0903/) on permutation powers. Cycles also
**decouple constraints**: if a condition only links `x` to `σ(x)`, then each cycle can be counted
on its own and the answers multiplied. [Problem 209](/solutions/0209/) is the showcase — a
64-state shift-register map is an invertible function, hence a permutation; the "no two adjacent
ones" constraint on each cycle of length `n` is counted by a
[Lucas number](https://en.wikipedia.org/wiki/Lucas_number), and `2⁶⁴` truth tables reduce to a
product over a handful of cycles. The cycle type (the [integer
partition](https://en.wikipedia.org/wiki/Integer_partition) of `n` formed by the cycle lengths) is
also the right *state* for random processes that treat every position alike: the randomised bozo
sort of [Problem 367](/solutions/0367/) behaves the same on any two permutations with the same
cycle type, so an `11!`-state Markov chain shrinks to one state per partition of 11. Fixed points
are the special case of 1-cycles: a permutation with none is a
[derangement](https://en.wikipedia.org/wiki/Derangement), the object behind the Secret Santa draw
of [Problem 740](/solutions/0740/).

### As a sequence — ascents, inversions, patterns

Finally, read `σ(1), σ(2), …, σ(n)` as a sequence and count its local features:
[ascents and descents](https://en.wikipedia.org/wiki/Permutation#Ascents,_descents,_runs,_and_excedances),
[inversions](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics)), runs, forbidden
patterns. These **statistics** have their own well-studied counting numbers. Permutations with
exactly one ascent are counted by the [Eulerian number](https://en.wikipedia.org/wiki/Eulerian_number)
`A(n, 1) = 2ⁿ − n − 1`, which is all [Problem 158](/solutions/0158/) needs once the choice of
letters (a binomial) is split from the choice of their order. Out-of-order adjacent pairs are
what the move-to-front sort of [Problems 523](/solutions/0523/) and [524](/solutions/0524/)
reacts to, so its expected cost over all `n!` inputs becomes a question about how such pairs
appear as the sort proceeds, not a simulation; a forbidden three-term arithmetic pattern defines the "unpredictable"
permutations of [Problem 720](/solutions/0720/). The tell is a problem that counts permutations
*by a property of adjacent or ordered pairs*: look the statistic up in
[OEIS](https://oeis.org/) before writing a search.

## How to reason about it

- **Count before you enumerate.** `10! ≈ 3.6·10⁶` is fine; `13! ≈ 6·10⁹` is not. If the input `n`
  is beyond a dozen, the solution cannot touch permutations one at a time.
- **Drop the order the question doesn't ask for.** When a search over permutations is unavoidable,
  the state is usually *which elements are used*, not the sequence they were used in. The
  [assignment problem](https://en.wikipedia.org/wiki/Assignment_problem) of
  [Problem 345](/solutions/0345/) — one entry per row and column — is a maximum over `15!`
  permutations that a bitmask DP settles over `2¹⁵` subsets.
- **Separate "which" from "in what order".** Choosing a set (binomial, multiset) and arranging it
  (factorial, multinomial, Eulerian) are independent factors far more often than not.
- **Mind duplicates.** Digit problems permute a *multiset*: repeated digits collapse arrangements,
  and leading zeros remove some. By symmetry exactly the fraction `(k − c₀)/k` of a class's
  arrangements start with a non-zero digit — a cleaner correction than subtracting a second count.
- **Name the view, then pick the tool.** Rank → factorial base. Class → signature and multinomial.
  Function → cycle decomposition and lcm. Sequence → a known statistic and its generating numbers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ○ [0336](/solutions/0336/) — Maximix Arrangements
- ● [0345](/solutions/0345/) — Matrix Sum
- ○ [0367](/solutions/0367/) — Bozo Sort
- ○ [0393](/solutions/0393/) — Migrating Ants
- ○ [0424](/solutions/0424/) — Kakuro
- ○ [0458](/solutions/0458/) — Permutations of Project
- ○ [0462](/solutions/0462/) — Permutation of 3-smooth Numbers
- ○ [0480](/solutions/0480/) — The Last Question
- ○ [0483](/solutions/0483/) — Repeated Permutation
- ○ [0491](/solutions/0491/) — Double Pandigital Number Divisible by $11$
- ○ [0494](/solutions/0494/) — Collatz Prefix Families
- ○ [0503](/solutions/0503/) — Compromise or Persist
- ○ [0523](/solutions/0523/) — First Sort I
- ○ [0524](/solutions/0524/) — First Sort II
- ○ [0559](/solutions/0559/) — Permuted Matrices
- ○ [0595](/solutions/0595/) — Incremental Random Sort
- ○ [0597](/solutions/0597/) — Torpids
- ○ [0599](/solutions/0599/) — Distinct Colourings of a Rubik's Cube
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0628](/solutions/0628/) — Open Chess Positions
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ○ [0673](/solutions/0673/) — Beds and Desks
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ○ [0687](/solutions/0687/) — Shuffling Cards
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ○ [0740](/solutions/0740/) — Secret Santa
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ○ [0796](/solutions/0796/) — A Grand Shuffle
- ○ [0837](/solutions/0837/) — Amidakuji
- ○ [0842](/solutions/0842/) — Irregular Star Polygons
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ○ [0866](/solutions/0866/) — Tidying Up B
- ● [0868](/solutions/0868/) — Belfry Maths
- ○ [0886](/solutions/0886/) — Coprime Permutations
- ○ [0896](/solutions/0896/) — Divisible Ranges
- ○ [0902](/solutions/0902/) — Permutation Powers
- ○ [0903](/solutions/0903/) — Total Permutation Powers
- ○ [0906](/solutions/0906/) — A Collective Decision
- ○ [0913](/solutions/0913/) — Row-major vs Column-major
- ○ [0916](/solutions/0916/) — Restricted Permutations
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ○ [0928](/solutions/0928/) — Cribbage
- ○ [0964](/solutions/0964/) — Musical Chairs Revisited
- ○ [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
