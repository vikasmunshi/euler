<!-- tags: [permutation] -->
<!-- status: final 2026-10-29T07:55Z -->
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

Unranking needs the size of every block, though, and when the list is a *filtered* subset of the
permutations those sizes can be awkward to count. [Problem 336](/solutions/0336/) asks for the
N-th "maximix" arrangement: the permutations on which a greedy
[pancake sort](https://en.wikipedia.org/wiki/Pancake_sorting) by suffix reversals takes its
worst-case number of moves. Filtering all `11!` arrangements through a simulation works, but the
greedy rule is deterministic, so it can be run **backwards** from the sorted train: undoing each
placement is one forced reversal followed by a free choice of where the second one starts, and
every distinct choice sequence yields a distinct worst case. The members are in bijection with
those choice sequences, which counts them at `(n − 2)!` — the statement's 24 for six carriages —
and generates exactly them, nothing else. At a few hundred thousand strings, sorting the generated
set and indexing into it is simpler than an unranking scheme, and plenty fast. The lesson
generalises: when the set is "inputs on which a fixed procedure behaves a certain way", invert the
procedure rather than test every input.

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
letters (a binomial) is split from the choice of their order. A forbidden three-term arithmetic
pattern defines the "unpredictable" permutations of [Problem 720](/solutions/0720/).

The sequence view pays off most when it meets the rank view. Record, for each position, how many
earlier elements are larger than the one there: that
[inversion table](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics)#Inversion_related_vectors)
(a [Lehmer code](https://en.wikipedia.org/wiki/Lehmer_code) read the other way round) is a
factorial-base numeral again, and a bijection with the permutations. So a *uniformly random*
permutation is a uniformly random factorial-base number, and its digits are **independent**:
the relative rank of the `(k+1)`-th element among the first `k+1` is uniform on `k+1` values,
whatever came before. That turns averages over `n!` inputs into sums over `n` positions.
[Problem 523](/solutions/0523/) is the clean example. Its sort scans from the front and moves the
first out-of-order element to the start of the list; it looks like a bubble-sort variant, but it
is really [insertion sort](https://en.wikipedia.org/wiki/Insertion_sort) in disguise — the list is
always a sorted prefix plus an untouched tail, and the tail is not inspected until the prefix is
clean again. The total cost therefore splits into one insertion per element, and each insertion's
cost depends only on how many prefix elements are smaller than the newcomer, through a short
recurrence in that one number. That count is exactly one inversion-table digit, so by
[linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Properties) the expected
cost over all `n!` inputs is a single sum over `k`, each term an average of the recurrence over a
uniform digit — `O(n)` work for `n = 30`, where simulation could not reach past ten or so. Two
habits from that solution are worth keeping: the derived formula was checked as exact rationals
against a brute force over every permutation up to `n = 8`, and the sum was kept exact to the end,
because the answer is asked to two decimals and a value can land exactly on a half.
[Problem 524](/solutions/0524/) runs the same sort and asks about individual permutations by their
cost, where the per-insertion decomposition is the natural place to start.

Inversions are also the right lens on a permutation *built up* from adjacent swaps, because an
[adjacent transposition](https://en.wikipedia.org/wiki/Transposition_(mathematics)) flips the
relative order of exactly one pair. In [Problem 996](/solutions/0996/) players on a leader board
swap adjacent ranks day after day and end where they started; the question is which tuples of
per-player overtake counts are possible. Following the permutation step by step is hopeless, but
reading it pair by pair settles it: a pair that ends in its original order has crossed an even
number of times, alternately, so each player's count is a sum of per-pair halves — the degree
sequence of a multigraph, hence an even total with no entry above half of it. The line geometry adds
one more rule: a player who never overtakes never moves, and so walls the board into independent
runs. The permutation then drops out entirely, leaving a count of integer tuples that a
[generating function](https://en.wikipedia.org/wiki/Generating_function) handles in time independent
of the number of days. The conjecture that those conditions are also *sufficient* was the part to
distrust, and it was confirmed against a brute-force search of small boards before it was used. The
tell is a problem that counts permutations
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
- **Run a deterministic process backwards.** If the permutations you want are defined by how a fixed
  procedure treats them (a sort's worst case, a shuffle's end state), undo the procedure from its
  output to generate exactly those permutations, rather than filtering all `n!` of them.
- **Separate "which" from "in what order".** Choosing a set (binomial, multiset) and arranging it
  (factorial, multinomial, Eulerian) are independent factors far more often than not.
- **Average through the inversion table.** An expectation over all `n!` inputs is an expectation
  over `n` independent uniform digits. If a process's cost splits per element and each part sees
  only that element's relative rank so far, linearity of expectation finishes the job.
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
- ● [0336](/solutions/0336/) — Maximix Arrangements
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
- ● [0523](/solutions/0523/) — First Sort I
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
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
