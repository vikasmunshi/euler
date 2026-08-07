<!-- tags: [dynamic-array] -->
<!-- status: final -->
# Dynamic array

A [dynamic array](https://en.wikipedia.org/wiki/Dynamic_array) is an array that does not need its
final length up front: contiguous storage, a count, a capacity, and an append that grows the block
when the count catches up with it. Python hands you one and calls it `list`; C hands you `malloc`
and expects you to assemble it. The problems below are the ones where the length genuinely could not
be known in advance — usually because the length *is* the thing being computed.

## The idea

Three numbers describe the structure: the block, how many slots hold data, and how many slots exist.
Reading or writing an occupied slot is an ordinary array access — $O(1)$, with the cache behaviour of
a flat run of memory. Appending is $O(1)$ as well, right up to the moment the count reaches the
capacity, at which point a larger block is allocated, the contents are copied across, and the old
one is freed.

That single expensive step is the whole design question, and the answer is not obvious until you do
the sum. Grow by a **constant** — `capacity += 1024` — and appending $n$ elements copies $O(n^2)$
elements in total, because every growth recopies everything already there and the growths keep
coming. Grow by a **factor** — `capacity *= 2` — and the copies form a geometric series bounded by
$2n$, so the per-append cost is $O(1)$
[amortized](https://en.wikipedia.org/wiki/Dynamic_array#Geometric_expansion_and_amortized_cost).
Every growable buffer in this repository doubles. Problem 78 states the reason in its own comment:

```c
if (n >= capacity) {
    /* Doubling growth keeps reallocs at O(log N) for unknown answer size */
    capacity *= 2;
    long long *tmp = realloc(partitions, (size_t)capacity * sizeof(long long));
    ...
    partitions = tmp;
}
```

The `tmp` is not decoration — `realloc` returns `NULL` on failure and assigning it straight back over
`partitions` would lose the only pointer to the data. That hazard, and the rest of the C mechanics,
belong to [dynamic memory allocation](/topics/technique/dynamic-memory-allocation); what matters here
is the shape above it. Python's `list` runs the same policy behind `append`, over-allocating on
growth so that a loop of appends is linear rather than quadratic — which is why building a list by
appending is idiomatic Python rather than a performance mistake.

## Where the unknown length comes from

Three situations recur across these problems, and they are worth recognising because each has a
different escape hatch.

**The loop runs until a condition, not to a bound.** Problem 78 builds the partition table $p(0),
p(1), \dots$ by Euler's pentagonal recurrence and stops at the first value divisible by the given
divisor — but the recurrence for $p(n)$ reads back into the table at $n - g(k)$, so every earlier
value has to still be there. The array has to hold everything computed so far and cannot be sized
in advance, because knowing its final size would be knowing the answer. Problem 64's period detection
is the same idea in miniature: iterate the continued-fraction state $(m, d, a)$ until a state repeats,
keeping every state seen, with the period — the length of the list — as the result.

**The count comes from the data.** Problem 46 sieves primes below a bound and needs them as a list
afterwards, but the count of primes below $N$ is not something the sieve loop knows before it runs;
it starts at 1024 entries and doubles. Problem 56 does it for the digits of a big integer, where each
multiplication may or may not carry into a new digit. Both could be bounded analytically — $\pi(N)$
has good estimates, and the digit count of $a^b$ is $\lfloor b\log_{10} a\rfloor + 1$ — and that is
exactly the trade: an estimate plus a doubling fallback is often less work than a proof.

**Each group's size depends on which group it is.** Problem 62 groups cubes by their sorted-digit
string, and the interesting property is precisely how many cubes share a key. The outer table has a
fixed bucket count; each *bucket* carries its own growable list, starting at four entries:

```c
if (e->count >= e->capacity) {
    /* Amortised doubling keeps append O(1) amortised. */
    e->capacity = e->capacity ? e->capacity * 2 : 4;
    e->values = realloc(e->values, (size_t)e->capacity * sizeof(long long));
}
e->values[e->count++] = value;
```

Problem 98 groups anagram words the same way, and problem 77 accumulates the prime partitions of each
$n$ as lists whose length is the count being sought. In Python all three are `defaultdict(list)` and
the growth is invisible; the C ports make it explicit, which is the usual relationship between the
two languages in this stack.

## The append is cheap; the search is not

The failure mode worth internalising is that a dynamic array gives you $O(1)$ append and $O(1)$
indexing and nothing else. Problem 64's Python detects the repeat by scanning:

```python
if (m, d, a) in p:
    break
p.append((m, d, a))
```

`in` on a list is a linear scan, so the loop is $O(\text{period}^2)$ where a
[hash table](/topics/technique/hash-table) would make it $O(\text{period})$. Here it is defensible —
periods for $n \le 10^4$ are small, tuples compare fast, and the list is also the answer's length —
but the reasoning has to be *done*, not assumed. The moment the container is queried more often than
it is appended to, the choice of a sequence over a set is the bug.

## How to reason about it

- **Exact beats growable when a bound exists.** A single allocation of the right size costs no copies,
  no slack, and no growth branch in the loop. Take the bound whenever the problem hands you one; the
  dynamic array is for when it does not.
- **A count pass is often cheaper than the copies.** When the length is expensive to bound but cheap
  to compute, run the loop twice — once counting, once filling — and allocate exactly once in between.
  Two passes of arithmetic against $\log n$ reallocations and up to $2n$ element copies is usually the
  better trade on large inputs.
- **Seed the capacity from what you know.** Problem 78 starts at 100000 slots and problem 46 at 1024,
  not at 1. A good initial guess removes most of the doublings; the doubling then only has to catch
  the case where the guess was low. This is the standard way to use an estimate you do not trust
  enough to rely on.
- **Doubling wastes up to half the block.** Right after a growth the array is half empty, so peak
  memory is up to twice the data. For a few million entries that is invisible; for a table sized in
  gigabytes it is the difference between fitting and not, and a growth factor of 1.5 — or an exact
  second allocation and a trim — starts to earn its complexity.
- **Any pointer into the block dies at the growth point.** `realloc` may move the data, so a cached
  pointer to an element, or a saved "end" pointer, is dangling immediately afterwards. Keep integer
  indices across an append. It is the same hazard as an iterator invalidated by `push_back`, and it
  fails the same way: usually not at all, until it does.
- **Parallel arrays grow together or not at all.** Problem 710 keeps four arrays indexed by the same
  variable and grows all four in one branch; problem 155 keeps two. The discipline is to compute the
  new capacity once and apply it to every array in the group — a per-array growth test is four chances
  to leave the arrays out of step, and the resulting read is silently out of bounds rather than a
  crash.
- **Build it inside `solve()`.** With `--runs=N` the harness times repeated calls, so a list grown once
  at import is free from the second run onward and the benchmark understates the real cost. A buffer
  allocated and grown per call cannot cheat, and the growth is part of what is being measured — which
  is the honest thing to measure, since it is part of what the program does.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0059](/solutions/0059/) — XOR Decryption
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0224](/solutions/0224/) — Almost Right-angled Triangles II
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0710](/solutions/0710/) — One Million Members
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
