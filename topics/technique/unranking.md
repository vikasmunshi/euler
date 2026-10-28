<!-- tags: [unranking] -->
<!-- status: final 2026-10-19T09:39Z -->
# Unranking

[Unranking](https://en.wikipedia.org/wiki/Unranking) is the inverse of ranking: given an index $k$
into an ordered family of objects, construct the $k$-th object **directly**, without generating the
$k - 1$ before it. Project Euler asks for this often. "The millionth permutation", "the
$10^{16}$-th number with property $X$": $k$ is far too large to count up to, but the objects are
built one symbol at a time, and you can *count* how many objects begin with a given prefix. The
three solved problems below use the same construction loop. They differ in the counting function
behind it, from a closed form ($n!$) to a [digit DP](/topics/technique/digit-dp) table.

## The idea — count the subtree, skip it or enter it

Arrange the objects in [lexicographic order](/topics/technique/lexicographic-order) as the leaves of a
tree: the root's children are the possible first symbols, their children the second symbols, and so on.
To find leaf $k$ (1-based):

```
for each position, left to right:
    for each candidate symbol c, in order:
        w = number of valid completions of prefix + c
        if k <= w: append c; break      # the target is in this subtree
        k -= w                          # skip the whole subtree
```

The loop does $O(\text{length} \times \text{alphabet})$ calls to the count function. Everything
interesting is in **how $w$ is computed**:

- If every prefix of the same length has the same number of completions, $w$ is a closed form and
  the loop becomes `divmod`. For permutations, that is the
  [factorial number system](/topics/domain/factorial-number-system).
- If the count depends on a *summary* of the prefix (a digit sum, a residue, a parity mask), precompute
  a table `count[remaining length][summary]` by DP, then look $w$ up in it.

The same table answers "how long is the $k$-th object?". Subtract whole lengths' counts first, then
unrank within the right length.

## Three problems, three counting functions

**24, lexicographic permutations: a closed form.** All $(n-1)!$ completions of a one-digit prefix are
valid, so the leading digit is the quotient of $k - 1$ by $(n-1)!$, and the remainder is the rank
within that block. The public solution writes it recursively:

```python
current, remaining = divmod(permutation_number - 1, math.factorial(len(digits) - 1))
result: str = digits[current] + recursive_solution(
    digits=digits[:current] + digits[current + 1:], permutation_number=remaining + 1
)
```

Ten steps, against the $10^6$ that `itertools.permutations` would have to step through.

**845, prime digit sum: a DP over digit sums.** We need the $n$-th positive integer whose digit sum is
prime, with $n$ up to $10^{16}$. Whether a completion is valid depends only on the prefix's digit sum, so
the solution builds `counts[length][s]`, the number of length-$\ell$ digit strings (leading zeros
allowed) with digit sum $s$. The number of completions of a prefix with sum $p$ is then
$\sum_s \text{counts}[\ell][s] \cdot [\,p + s \text{ prime}\,]$. The table grows until it covers $n$ valid
numbers. Then the loop fixes digits from most significant to least significant. Leading zeros
come out naturally: a number with fewer digits is a string with leading zeros, and the all-zero
string has sum 0, which is never prime, so it is never counted.

**974, very odd numbers: a DP over a richer state.** Here the valid objects have only odd digits, are
divisible by 105, and use each odd digit an odd number of times. The state after a prefix is
(value mod 7, digit sum mod 3, a 5-bit mask of digit-count parities), and the last digit is forced to be
5 for divisibility by 5. The solution tabulates completions over $7 \times 3 \times 32$ states for each
remaining length, skips whole lengths (only odd lengths $\ge 5$ are possible) until the rank falls inside
one, and then runs the same skip-or-enter loop. The richer state changes only the DP, not the
construction.

## Python and C

- **24**: identical recursion. Python's string slicing `digits[:current] + digits[current + 1:]`
  becomes a `malloc`ed copy with one character skipped, and each level allocates a new result
  string. C's `long long` factorial is ample for ten digits. It would overflow past $20!$, where
  Python keeps going.
- **845**: Python grows `counts` as a list of lists only as long as needed. C allocates a static
  `long long counts[MAX_LEN + 1][MAX_SUM + 1]` with fixed generous bounds and `memset`s it for each
  call. For $n = 10^{16}$ the table stops at about 18 digits, so every count and every prefix total is
  below $10^{18}$ and fits a signed 64-bit integer.
- **974**: the DP counts grow like $5^{\ell}$ and pass $2^{64}$ for long enough numbers, so C stores
  them as `unsigned __int128` in a flat array with a hand-written index function (`cget`), and
  formats the 128-bit result itself. Python's `dict` keyed by 4-tuples and its unbounded `int` need
  neither. The Python also re-runs `build_counts` from scratch each time it grows `max_len`, a
  simplicity-over-speed choice that the tiny state space makes affordable.

## How to reason about it

- **Is there an order and a way to count by prefix?** Then the $k$-th object can be built in
  $O(\text{length} \times \text{alphabet})$ count queries, however large $k$ is.
- **Find the smallest prefix summary that determines validity.** That summary is the DP state: nothing
  for permutations, the digit sum for 845, (mod 7, mod 3, parity mask) for 974.
- **Use 0-based ranks inside the loop.** `divmod(k - 1, …)` avoids the off-by-one that 1-based ranks
  invite. Convert back only at the boundary.
- **Settle the length first.** Subtract the counts of whole shorter lengths, or let leading zeros
  stand in for shorter numbers as 845 does. Do not mix the two.
- **Mind the width of the counts, not just of the answer.** The intermediate counts can exceed the
  answer by orders of magnitude (974).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0698](/solutions/0698/) — 123 Numbers
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
