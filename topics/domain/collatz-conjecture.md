<!-- tags: [collatz-conjecture] -->
<!-- status: final -->
# Collatz conjecture

The [Collatz map](https://en.wikipedia.org/wiki/Collatz_conjecture) halves an even number and
sends an odd `n` to `3n + 1`. The conjecture says every start eventually reaches 1. It has been
checked far beyond anything Project Euler asks about and is still unproven. The problems here don't
need the conjecture settled. They need two engineering habits. Going forward over many starts
(14), I memoise, because chains merge and then share their whole tail. Asked which start produces
a given pattern of steps (277, and 494 in a harder form), I stop simulating and read the pattern
as a residue class. That turns the search into a computation.

## Going forward: chains merge, so memoise

Define `len(n)`, the number of terms from `n` down to 1:

```
len(1) = 1
len(n) = 1 + len(n / 2)      if n is even
len(n) = 1 + len(3n + 1)     if n is odd
```

Computing this independently for every start below a million repeats a lot of work. The chains
from 27 and from 31 both run through 9232, and from there they are the same sequence. The
recurrence has overlapping subproblems, which is the textbook case for
[memoization](../technique/memoization.md). Once I know `len(m)`, every later chain
that reaches `m` stops there. Problem 14's Python solution is the direct transcription:

```python
@functools.lru_cache(maxsize=None)
def collatz_length(number: int) -> int:
    if number == 1:
        return 1
    if number % 2 == 0:
        return 1 + collatz_length(number // 2)
    return 1 + collatz_length(3 * number + 1)
```

With the memo, a start of `n` usually costs a handful of new steps before it lands on a known value.
The total work over all starts below `N` is roughly linear in `N`, not the `N × average chain length`
of the naive loop.

A second observation halves the scan. If `x < N/2`, then `2x < N` as well, and the chain from `2x`
is the chain from `x` with one step added in front, so it is strictly longer. The longest chain
therefore starts above `N/2`. More precisely, it starts above the largest power of two below `N`,
which is the bound 14's solution uses. The lower half still gets visited, just as a tail of
chains that start higher up.

## Sizing the memo table

The awkward part of the memo is the `3n + 1` step: chains climb well above the range I'm
scanning. Below a million, the highest value any chain reaches is about 5.7 × 10¹⁰ (from the start
704 511). That has two consequences:

- **Integer width.** 5.7 × 10¹⁰ doesn't fit in 32 bits. In C the values have to be `long long`.
  Python's unbounded integers make this a non-issue there.
- **What to cache.** I measured both designs on 14's range:

| memo | entries | steps computed | notes |
|---|---|---|---|
| hash map, cache everything (Python `lru_cache`) | ≈ 2.15 M | ≈ 2.15 M | over half of the keys are ≥ 10⁶ and are almost never hit again |
| flat array of size `N`, cache only `n < N` (the C version) | 10⁶ slots | ≈ 2.36 M | ≈ 1.36 M of those steps are excursions above `N`, recomputed each time |

The array does about 10% more raw steps than the hash map, but each step is an array index
instead of a hash lookup, and the memory is one contiguous block with `0` as the "not yet known"
sentinel. That trade almost always wins. Values above `N` are too sparse to be worth storing: few of them
are ever reached a second time. So I size the table to
the range being scanned and let the excursions go uncached. A hash map makes sense only when the
key range isn't bounded in advance.

Two more details. First, the memo is built
**inside** `solve()`, so every benchmarked run pays for it and the timing is honest. Second, the
recursion depth stays at about 500 frames below a million, so Python's recursion is fine here.
For a larger `N` I would switch to an explicit loop that walks forward to the first known value
and then fills the path back in.

## Going backward: a step pattern is a residue class

Problem 277 changes the map. Every rule now divides by 3, and the branch taken depends on
`a mod 3`. The three steps are `D: a/3`, `U: (4a+2)/3` and `d: (2a−1)/3`. The question is the
smallest start above 10¹⁵ whose step string begins with a given 30-letter word. Searching forward
from 10¹⁵ won't work. The key fact is that **each step letter depends only on a residue of the
start**:

- One step is `a ↦ (c·a + e)/3` with `c ∈ {1, 4, 2}`. After `k` steps the value is
  `(C·a₁ + E)/3^k`, where `C` is a product of 2s and 4s and so is coprime to 3.
- The letter at step `k+1` depends on that value mod 3, so it depends only on `a₁ mod 3^(k+1)`.
  Because `C` is invertible mod 3, each of the three possible letters picks out exactly one of the
  three lifts of the current residue.

So a step word of length `L` pins `a₁` to exactly one class mod `3^L`. I can recover that class one
base-3 digit at a time. At each position I try the three digits and keep the one that reproduces
the next letter. There is no backtracking: this is the same "fix one digit, lift" structure as
[Hensel lifting](../technique/hensels-lemma.md). Once I have the residue `r`, the
answer is the first member of `r + 3^L·ℤ` above the threshold, which takes one floor division. The
cost is `O(L²)` for `L = 30`, against a forward search that would never finish. The same reasoning
can run the other way. Each step inverts to an affine map (`D: 3a`, `U: (3a−2)/4`, `d: (3a+1)/2`),
so I can work backward from the end of the word, find the end values that keep every step
integral, and map the smallest of them back to the start. The two directions give the same
residue class.

The ordinary Collatz map has the same structure with 2 in place of 3. The pattern of
odd and even steps in the first `k` steps of a start depends only on `n mod 2^k`, and every pattern
of length `k` appears exactly once in each block of `2^k` starts
([Terras, 1976](https://en.wikipedia.org/wiki/Collatz_conjecture#As_a_parity_sequence)). Problem
494 builds on this. Its prefix families group chains by the relative order of their terms before
the first power of 2, so the counting has to go through parity patterns and the residue classes
they fix, not through individual starts.

## When to reach for which

- **Many starts, one quantity each** (lengths, peaks, stopping times): memoise the forward map.
  Use a flat array sized to the scan range, leave the excursions uncached, use 64-bit values, and
  check whether a dominance argument like "`2x` beats `x`" can shrink the range.
- **One pattern, find its starts**: don't simulate forward. The first `k` steps are periodic in the
  start with period `p^k`, where `p` is the divisor in the map. Lift the residue one digit at a
  time, or invert the steps from the end. Either way it is arithmetic, not search.
- **Counting patterns** (494): the unit of work is the residue class or parity vector, not the
  integer. Enumerate those, with [dynamic programming](../technique/dynamic-programming.md) over the steps where the classes merge.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ○ [0494](/solutions/0494/) — Collatz Prefix Families

<!-- /problems -->
