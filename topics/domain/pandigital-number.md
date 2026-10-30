<!-- tags: [pandigital-number] -->
<!-- status: final 2026-10-14T11:55Z -->
# Pandigital number

A [pandigital number](https://en.wikipedia.org/wiki/Pandigital_number) uses every digit of
some alphabet — usually $1$ to $9$ or $0$ to $9$, sometimes $1$ to $n$, sometimes a base other
than ten — exactly once. Project Euler returns to the idea again and again because it is the
purest example of a problem whose *search space is tiny once you look at it the right way*:
there are only $9! = 362\,880$ nine-digit pandigitals and $10! \approx 3.6$ million ten-digit
ones, yet the obvious approach — scan integers and test each — wanders through billions of
numbers to find them. Every problem below is, at heart, a lesson in deciding whether to
**generate** pandigitals or **test** for them, and in using the digit budget to cut the
search down before it starts.

## The idea

A pandigital is a *permutation of a fixed digit multiset* written as a number. Two
operations follow from that, and nearly every solution is a mix of them:

- **Testing** — given a number (or a concatenation of several), decide whether its digits are
  exactly the alphabet. The robust check is *length plus coverage*: the string has as many
  characters as the alphabet, and its set of characters equals the alphabet. Equivalently,
  OR each digit into a bitmask and reject on a repeat; the mask reaches `0b1111111110` exactly
  when $1$–$9$ are each present once. Problem 38 does this with a frequency array over the
  integer, which avoids building strings in the hot loop.
- **Generating** — enumerate the permutations of the alphabet directly
  ([`itertools.permutations`](https://docs.python.org/3/library/itertools.html#itertools.permutations)
  in Python, or Heap's / next-permutation in C). Feed the digits in descending order and the
  permutations come out in descending numeric order, so "the largest pandigital with property
  $P$" becomes "the first one generated that has $P$".

The real leverage is a third thing: **the digit budget is an invariant.** Whatever you build,
the digits are fixed in count and in sum, and both facts prune.

- *Count.* In Problem 32 the identity $a \times b = c$ must use nine digits in total. Since
  $a \cdot b$ has either $\ell(a)+\ell(b)$ or $\ell(a)+\ell(b)-1$ digits, the only length
  splits that can total nine are $1 \times 4 = 4$ and $2 \times 3 = 4$ — every other shape is
  impossible and is never enumerated. Problem 38 uses the same arithmetic: a concatenated
  product of $x$ with $(1, 2, \dots, n)$, $n > 1$, reaches nine digits only if $x$ has at most
  four, which turns an open-ended search into a short static table of $(n, \max x)$.
- *Sum.* Every $1$-to-$n$ pandigital has [digit sum](/topics/domain/digit-sum) $n(n+1)/2$,
  regardless of order — and by the [divisibility rule](/topics/domain/divisibility-rule) for 3,
  a number is divisible by 3 exactly when its digit sum is. For $n = 2, 3, 5, 6, 8, 9$ that sum
  is $3, 6, 15, 21, 36, 45$, all multiples of 3, so *no pandigital of those lengths can be
  prime*. Problem 41 therefore only searches lengths 7 and 4: one line of arithmetic deletes
  the 9- and 8-digit cases, which would otherwise be the bulk of the work.

## How to reason about it

**Prefer generate-and-filter over scan-and-test whenever the property is cheap.** Ten digits
is 3.6 million permutations; ten-digit integers number nine billion. If you can phrase the
answer as "pandigitals with property $P$", generate them. If the pandigital is a by-product
(a concatenation of a product, the end of a Fibonacci number), you cannot generate it directly
— then test, but make the test the cheap first filter.

**Order the constraints so the strongest one goes first.** Problem 43 asks for $0$-to-$9$
pandigitals whose overlapping three-digit windows $d_2d_3d_4, \dots, d_8d_9d_{10}$ are
divisible by $2, 3, 5, 7, 11, 13, 17$. Testing all $10!$ permutations works, but the
idiomatic solution is [backtracking](/topics/technique/backtracking) from the *right*: only 44
three-digit multiples of 17 have distinct digits, so seed with those and prepend one digit at a
time, checking the newly formed window against 13, then 11, and so on. Because consecutive
windows share two digits, each step offers at most a handful of candidates, and the whole tree
is a few hundred nodes. The general lesson: when a pandigital carries positional constraints,
build it digit by digit with a *used* set, and start where the constraint is tightest.

**When the question is "how many", stop enumerating and count.** Problem 178 counts step
numbers (adjacent digits differ by one) below $10^{40}$ that are $0$-to-$9$ pandigital. There
are far too many to list, but pandigitality is just "every digit seen", so it fits in a
10-bit mask carried through a [digit DP](/topics/technique/digit-dp) whose state is
*(position, last digit, mask)*. Problem 491 counts double pandigitals (each digit exactly
twice) divisible by 11; the alternating-sum rule for 11 turns it into choosing *which* copies
of each digit go to odd positions versus even ones, and the arrangements within each half are
counted by multinomials rather than generated. Problem 118 — partition $1$–$9$ into a set of
primes — likewise reduces to recursion over a mask of digits still unused.

**Pandigitality can be tested at a distance.** Problem 104 wants a Fibonacci number whose first
*and* last nine digits are pandigital. Its full value runs to hundreds of thousands of digits,
but the last nine come from iterating modulo $10^9$, and the first nine from the logarithm of
Binet's formula — so the test never touches the full number. Check the cheap end first; most
indices fail there.

**Watch the alphabet.** "Pandigital" shifts between problems: $1$–$9$ (32, 38), $1$–$n$ (41),
$0$–$9$ with no leading zero (43, 170), each digit twice (491), *at least once* in every base
from 2 up to $n$ (571), or in base $n$ (660). Read which one is meant; a `set(s) == digits`
test that ignores length silently accepts repeats, and forgetting the leading-zero rule
silently accepts nine-digit numbers as ten-digit pandigitals.

```python
def is_pandigital(s: str, alphabet: str = "123456789") -> bool:
    return len(s) == len(alphabet) and set(s) == set(alphabet)
```

That one-liner is the test; the craft in this domain lies in arranging the search so you call
it as rarely as possible.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0178](/solutions/0178/) — Step Numbers
- ○ [0491](/solutions/0491/) — Double Pandigital Number Divisible by $11$
- ● [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0660](/solutions/0660/) — Pandigital Triangles

<!-- /problems -->
