<!-- tags: [lexicographic-order] -->
<!-- status: final -->
# Lexicographic order

Lexicographic order is dictionary order applied to any sequence: compare the first elements, and
only if they tie look at the second, then the third. I keep coming back to it because it does four
separate jobs in these solutions. It is a **comparison key** that ranks things by priority (poker
hands, radicals). It is an **order of generation**, so the first hit of a scan is already the
extremum (pandigital primes). It gives a **canonical form**, so each unordered object is generated
exactly once (digit multisets). And it is an **index**: a permutation or a number has a *position*
in the order, which can be computed without walking up to it.

## The idea

For sequences `a` and `b`, `a < b` lexicographically when, at the first index `i` where they
differ, `a[i] < b[i]`. If there is no such index, the shorter sequence (a proper prefix of the
other) comes first ([Wikipedia](https://en.wikipedia.org/wiki/Lexicographic_order)). Two properties
make it useful:

- **Priority is positional.** Element 0 outranks everything after it. To compare objects on
  criterion A, then B, then C, I build the key `(A, B, C)` and compare keys. Nothing more is needed.
- **It is the numeric order of fixed-width digit strings.** For digit sequences of the *same
  length*, lexicographic order and numeric order agree. That is why "largest number" and "last
  permutation" turn into the same question. Across *different* lengths they disagree (`"9" > "10"`),
  and the fix is [shortlex](https://en.wikipedia.org/wiki/Shortlex_order): compare length first, then
  lexicographically.

## Four ways the problems use it

**1. A tuple as a multi-criterion key.** [Problem 54](/solutions/0054/) turns each poker hand into
`(category, tie-breakers…)`, with the tie-breakers listed most-significant first (the trips value,
then the kickers in descending order). After that, "who wins" is one key comparison, and every rule
about kickers and second pairs is just the order of the tuple's fields.
[Problem 124](/solutions/0124/) has the same shape: sort `1..N` by `(rad(n), n)`, radical first and
`n` breaking ties, then read off the k-th element.

**2. Generate in order, stop at the first hit.** When the candidates come out in descending
lexicographic order, the first one that passes the test is the maximum, with no need to collect and
compare. [Problem 41](/solutions/0041/) walks the 7-digit and then 4-digit pandigitals from
`7654321` downward and returns the first prime. Its C side steps through them with a hand-written
`prev_permutation`: find the rightmost descent, swap it with the largest smaller element to its
right, reverse the suffix. [Problem 68](/solutions/0068/) instead keeps a running maximum over all
valid rings, because its 16-digit strings are not generated in output order.

**3. A canonical representative for unordered objects.** When only the *multiset* of digits
matters, the non-decreasing sequence is the one ordering I keep. [Problem 30](/solutions/0030/)
uses this: a number's digit-power sum ignores digit order, so it enumerates sorted digit tuples and
checks whether each sum reproduces itself. That costs C(10+k−1, k) candidates rather than 10^k.
[Problem 254](/solutions/0254/) uses the same fact the other way round. The smallest number with a
given digit multiset is that multiset written in ascending order. Since fewer digits always means
smaller, the search becomes shortlex: minimise the digit count first, and break ties
lexicographically on the ascending digit string. The minimum-count part is a
[greedy](/topics/technique/greedy-algorithm) walk down the
[factorial number system](/topics/domain/factorial-number-system).

**4. Rank and unrank.** The position of an object in lexicographic order can be computed directly.
To **rank** a permutation, I use its [Lehmer code](https://en.wikipedia.org/wiki/Lehmer_code): digit
`d_i` counts the smaller values to the right of position `i`, and the rank is `1 + Σ d_i·(N−1−i)!`.
[Problem 720](/solutions/0720/) needs the rank of a permutation of 2^25 elements. It builds the
Lehmer code directly with a doubling recurrence, then folds it modulo a prime with Horner's rule
(`acc = acc·(n−i+1) + d_i`), so the huge factorials are never formed. To **unrank**, I fix the
answer one position at a time. At each position I try candidates in increasing order and count how
many completions each one allows. If the remaining rank fits within that count, I take the
candidate. Otherwise I subtract the count and move to the next candidate.
[Problem 845](/solutions/0845/) finds the n-th integer with a prime digit sum this way. A table of digit-sum counts supplies the completion counts, which is the
[digit DP](/topics/technique/digit-dp) pattern. [Problem 336](/solutions/0336/)
shows the other side of the trade-off. Its notes considered unranking, but the reversal-and-splice
structure of its arrangements makes completion counts awkward. With fewer than 4·10^5 candidates,
generating them all, sorting, and indexing is simpler and fast enough. See
[unranking](/topics/technique/unranking) and [permutation](/topics/domain/permutation) for more on
both directions.

## Python and C

Python provides lexicographic comparison for free, while C has to write it out each time:

| Need | Python | C |
|---|---|---|
| Compare composite keys | tuples compare lexicographically: `key=lambda n: (rad[n], n)` | a struct plus a `qsort` comparator that tests field 0, then field 1 (124), or a loop over a tie-breaker array (54) |
| Compare strings / rows | `str` and `list` compare natively; `sorted(strings)` (336) | `strcmp`, or `memcmp` over fixed-width rows (336 packs arrangements into one flat buffer to avoid per-string allocation) |
| Permutations in order | `itertools.permutations` yields them in the lexicographic order of its input, so reversing the input gives descending order (41) | hand-written `next_permutation` / `prev_permutation` (41) |
| Sorted multisets | `itertools.combinations_with_replacement` (30) | advance an index array: bump the rightmost slot below 9 and fill every slot to its right with the new value, which keeps the array non-decreasing (30) |
| Numeric max of digit strings | convert with `int(…)` and compare integers (68) | length first, then `strcmp`: shortlex by hand (68) |

The C comparators share one detail: `qsort` is not stable. A key that compares only `rad` would
leave equal-radical entries in arbitrary order. Putting `n` in the comparator as well makes the
order total, so the k-th element is the same on every run.

## Pitfalls

- **Strings are not numbers.** `"10" < "9"`. Compare digit strings lexicographically only at equal
  width; otherwise use shortlex or convert to integers.
- **The prefix rule decides unequal lengths.** A shorter tuple wins a tie on its common prefix. In
  Problem 54 that would be a bug if two categories had different numbers of tie-breakers, which is
  why the Python key compares tie-breakers only at equal length.
- **Field order is the specification.** A key with the right fields in the wrong order gives a
  plausible but wrong total order. Write the fields most-significant first, and say so in a comment.
- **Ascending vs descending.** The C helpers depend on whether the starting array is sorted up or
  down: `prev_permutation` has to start from the descending arrangement. A descending sort in
  Python is `reverse=True` or a negated numeric field, never a negated string.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0845](/solutions/0845/) — Prime Digit Sum

<!-- /problems -->
