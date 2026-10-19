<!-- tags: [frequency-statistics] -->
<!-- status: final 2026-10-19T09:42Z -->
# Frequency (statistics)

A [frequency](https://en.wikipedia.org/wiki/Frequency_(statistics)) is how many times a value occurs
in a collection. A frequency distribution is the table of all of them. It is the most basic summary
in statistics, and in code it is a single array of counters. Its power comes from what it throws
away: **order**. Many questions don't depend on order. Does this number use each digit once? Is this
poker hand a full house? Does this decrypted text look like English? For those, the frequency table
is a smaller, canonical object that answers directly. The three solved problems below each reduce
their input to such a table and then read the answer off its shape.

## The idea — keep the multiset, drop the order

Counting values turns a sequence into a [multiset](https://en.wikipedia.org/wiki/Multiset): the same
elements with the same multiplicities, in no particular order. Two sequences that are rearrangements
of each other have the *same* frequency table, so the table is a canonical form for "equal up to
permutation". Three ways to use it recur:

- **Exact profile check.** Compare the table with a target: every digit exactly once (a
  [pandigital](/topics/domain/pandigital-number) number), every letter as often as in another word (an
  anagram).
- **Shape classification.** Sort the *counts* themselves and ignore which values they belong to. In a
  five-card hand the sorted count profile is one of $(1,1,1,1,1)$, $(2,1,1,1)$, $(2,2,1)$, $(3,1,1)$,
  $(3,2)$ or $(4,1)$, and that profile alone decides the hand's category, apart from straights and flushes.
- **Statistical scoring.** Compare the table with an *expected* distribution and take the closest match.
  This is [frequency analysis](/topics/domain/frequency-analysis), the oldest tool for breaking
  substitution ciphers.

When the values come from a small range (digits, card ranks, bytes), the table is a fixed-size array
indexed by value, the counting phase of [counting sort](/topics/technique/counting-sort). Otherwise a
[`Counter`](/topics/technique/collections-counter) or dictionary does the same job.

## Three problems, three uses

**38, pandigital multiples: an exact profile.** Concatenating $x, 2x, \dots, nx$ must give a
1-to-9 pandigital. The public solution checks this with a ten-slot digit table, rejecting as soon as
a 0 or a repeated digit appears:

```python
digits: list[int] = [0] * 10
while n:
    d = n % 10
    if d == 0 or digits[d] == 1:
        return False
    digits[d] = 1
    n //= 10
```

With the length fixed at nine digits, "no zero and no repeat" already forces each of 1–9 exactly once.
The final `sum(digits[1:]) == 9` is a belt-and-braces check. The search itself is tiny: a static table
of $(n, x_{\max})$ pairs, scanned downward so that the first hit is the largest.

**54, poker hands: shape classification.** To rank a hand, the solution builds the (count, value)
pairs of its card values, sorted by count and then by value, both descending:

```python
value_counts = tuple(sorted([(self.values.count(v), v) for v in set(self.values)], reverse=True))
```

The first count decides four of a kind, full house, three of a kind, two pairs or one pair, and the
same sorted order lists the values that break ties, most significant first. Straights and flushes are
the only categories the profile can't see. They need the values' *spread* and the suits' frequency
(one distinct suit), which are two more small frequency facts.

**59, XOR decryption: statistical scoring.** Each slice of the ciphertext is a single-byte
[XOR](/topics/domain/exclusive-or) cipher, so trying all 26 lowercase keys gives 26 candidate plaintexts.
The right one is the one that looks most like English. The solution scores each candidate by how many
of its characters are among the common letters `e`, `a`, `n` and `t` (both cases), and keeps the
highest score. That is a deliberately crude statistic, the frequency of a handful of letters, but over
about 160 characters per slice the correct key wins by a wide margin.

## Python and C

- **38**: identical, a ten-entry `int` array in both. The Python concatenation
  `"".join(str(i * x) ...)` becomes a `snprintf` of each product plus `strcat` into a buffer in C.
- **54**: Python builds the profile with `set(values)` plus `values.count(v)` and a `sorted` of
  tuples, so tuple comparison does the ranking by count and then value. C builds parallel arrays
  `uvals[]`/`ucounts[]` by linear search, sorts them with a hand-written exchange sort on the same
  two keys, and stores tie-breakers in a fixed array with an explicit `tb_count`. With five cards,
  quadratic loops cost nothing, and they avoid allocation entirely.
- **59**: Python counts with `str.count` over the decrypted string, one pass per common letter. C XORs
  each byte and checks it against the letter list inline, without building a string. The statistic is
  the same, so is the winner.

## How to reason about it

- **If order doesn't matter, count.** A frequency table is the canonical form for "same elements,
  any order", and comparing tables is cheaper and clearer than sorting and comparing sequences.
- **Sort the counts to classify shape.** When only the multiplicity pattern matters (poker, the
  "type" of a factorisation, the cycle type of a permutation), sort the counts and ignore the labels.
- **Use an array for a small value range.** Digits, ranks and bytes index directly. Use a hash map only
  when the range is large or sparse.
- **Fail fast on exact profiles.** Stop at the first repeated or forbidden value (38), as you would in
  any validity check.
- **Strengthen the statistic if the margin is thin.** Counting four letters works on long English
  text. For short or unusual text, score with a full letter-frequency table and a
  [chi-squared](https://en.wikipedia.org/wiki/Chi-squared_test) distance instead.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0059](/solutions/0059/) — XOR Decryption

<!-- /problems -->
