<!-- tags: [concatenation] -->
<!-- status: final -->
# Concatenation

[Concatenation](https://en.wikipedia.org/wiki/Concatenation) is joining strings end to end:
`"12" + "34" == "1234"`. In Project Euler the strings are nearly always decimal digits, so the
operation sits awkwardly between two worlds. Read as text it is trivial; read as a number it is
$a \cdot 10^{\ell(b)} + b$, where $\ell(b)$ is the digit count of $b$, and that formula has properties
ordinary arithmetic does not. Pandigital puzzles, prime pairs and Fibonacci words all hinge on three
of those properties: lengths add, residues combine predictably, and a concatenated object can be
indexed without being built.

## The idea

**Concatenation is arithmetic, and you can do it without leaving the integers.** The identity is

```python
def cat(a: int, b: int) -> int:
    return a * 10 ** len(str(b)) + b      # a || b; len(str(b)) is the digit count, 1 for b == 0
```

A solution that writes `int(str(a) + str(b))` is computing the same thing with two allocations and
a parse. Problem 60 tests both orders of every prime pair, a || b and b || a, millions of times, and
that predicate is the hot loop. In C there is no string shortcut anyway: you keep each operand's
power of ten next to it and multiply. In both languages, the length is a property of the operand
that you compute once, not on every join.

**Lengths add, and that is the strongest bound you have.** $\ell(a \Vert b) = \ell(a) + \ell(b)$,
while a product $ab$ has $\ell(a)+\ell(b)$ or $\ell(a)+\ell(b)-1$ digits. Put those two facts
together and most pandigital searches shrink to a handful of cases before any enumeration starts:

- Problem 32 needs multiplicand ‖ multiplier ‖ product to be exactly nine digits. Only the operand
  splits (1, 4) and (2, 3) can add up, so the search covers two shapes instead of all pairs.
- Problem 38 concatenates $x, 2x, \dots, nx$ into nine digits. With $n \ge 2$ the base $x$ is at
  most four digits, so one static table of `(n, max_x)` lists every case:

  ```python
  for n, x in ((2, 9876), (3, 987), (4, 98), (5, 9), ...):
      number = int("".join(str(i * x) for i in range(1, n + 1)))
  ```

- Problem 170 is the same argument, done in general: the inputs and the products each span ten
  digits, and summing the minimum product lengths forces $(k-1)\,\ell(a) \le k$. So the shared
  multiplier has at most two digits, and two digits allow only $k = 2$.
- Problem 68 asks for a *16-digit* string. That length alone says the 10 must sit on the outer
  ring, since it is counted once there and twice inside. The bound is a digit count.

Problem 17 uses the same additivity on words. You never assemble "three hundred and forty-two". You
add the lengths of its fragments from a table, because the letter count of a concatenation is the
sum of the letter counts.

**Residues combine, so divisibility can be read off the parts.** Since $10 \equiv 1 \pmod 9$, a
concatenation is congruent to the *sum* of its parts mod 3 and mod 9: $a \Vert b \equiv a + b$.
In problem 60, two primes $p \equiv 1$ and $q \equiv 2 \pmod 3$ concatenate to a multiple of 3, so,
apart from 3 itself, a prime-pair set lives entirely in one residue class. That halves the graph before any primality test
runs. Problem 170 uses a sharper version: if every block is a multiple of $a$, then so is their
concatenation, because each block is just shifted by a power of ten. The whole candidate, and each
block of it, must therefore divide by the multiplier. In general,
$a \Vert b \equiv a \cdot 10^{\ell(b)} + b \pmod m$ for any modulus. That is how you test a
concatenated number's divisibility without materialising it.

**A concatenation you cannot store can still be indexed.** When the pieces nest recursively, the
structure of the join tells you where a position lands. Problem 230's Fibonacci words obey
$T_k = T_{k-2} T_{k-1}$, so the lengths obey $L_k = L_{k-2} + L_{k-1}$. To find the $n$-th character
of $T_k$, compare $n$ with $L_{k-2}$ and step into the left or right part. You only ever compute the
~80 lengths, never the $10^{17}$-character string. Problem 305 has the same shape over the
[Champernowne](https://en.wikipedia.org/wiki/Champernowne_constant) stream $123456789101112\ldots$:
every occurrence of a pattern either lies inside one integer or crosses a boundary between
consecutive integers. Both classes can be counted in closed form, and a
[binary search](/topics/technique/binary-search-algorithm) on that count locates the $n$-th
occurrence. The boundary-crossing class is where the difficulty concentrates, and it is the case a
naive "search inside each number" misses.

**Enumerating concatenations means enumerating partitions of the digits.** Problem 118 reads
concatenation the other way round. The digits 1–9 are cut into groups, and each group is joined into
a number that must be prime. The clean model is a bitmask per digit subset, mapped to the primes its
permutations form. Joining parts becomes a disjoint union of masks, and an increasing-order rule on
the chosen primes makes every set partition appear exactly once.

## How to reason about it

- **String order equals numeric order only at equal length.** `"9" > "10"` as text. Problem 68
  compares its candidates as numbers *because* it fixes the length first. Problem 170 builds its
  answer most-significant digit first and prunes with an optimistic bound, which works for the same
  reason: at a fixed width, the lexicographic prefix order is the numeric order.
- **Mind leading zeros.** `int("07")` silently becomes a one-digit 7, so a 0–9 pandigital check that
  goes through `int` can lose a digit. Check the string, or reject a leading `0` explicitly.
- **Prefer the closed form in a hot loop.** `a * pow10[len_b] + b` with precomputed powers beats
  `int(str(a) + str(b))` by a large constant. In C, use `unsigned long long` and check that
  $\ell(a) + \ell(b)$ fits ([watch integer width](/topics/takeaway/watch-integer-width)), because two
  ten-digit primes already overflow 64 bits.
- **Bound by length before you enumerate.** Do the digit-count arithmetic on paper first. It usually
  removes an order of magnitude, and on the pandigital problems it removes nearly everything.
- **If the string is too big to build, recurse on lengths.** Any concatenation defined by a rule —
  a recurrence, a stream of integers, a repeated block — can be indexed by walking the rule with the
  lengths alone.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0305](/solutions/0305/) — Reflexive Position

<!-- /problems -->
