<!-- tags: [right-tool-per-cost] -->
<!-- status: final -->
# Match the abstraction to the hot path

Every abstraction has a price. A generator, a dictionary, an arbitrary-precision
integer, a list of lists — each buys you something (laziness, clarity, memory safety,
flexibility) and charges you something every time you use it. The lesson these problems
share is that the charge only matters where the work concentrates: the **hot path**, the
inner loop that runs millions of times. Pick the abstraction that is cheap *there*, and
spend freely everywhere else.

## The idea

Runtime is not spread evenly through a program. It piles up in whatever loop the input
size drives — a scan over `N`, a walk over every reachable state, a sieve pass. An
abstraction's convenience is amortised over how often you pay for it, so a per-element
cost of a few hundred nanoseconds is invisible when you pay it once and decisive when you
pay it a billion times. "Match the abstraction to the hot path" means: identify where the
cycles and allocations actually go, and there — and only there — reach for the leanest
representation that does the job.

The same idea recurs in a few concrete shapes across these problems.

**Iteration overhead.** [Problem 1](/solutions/0001/) sums the multiples of 3 or 5 below
`N`, and I wrote the same `O(N)` arithmetic five ways. Expressed as a hand-driven
[generator](https://en.wikipedia.org/wiki/Generator_(computer_programming)) with an
explicit `while`, it runs 16.5 s in Python; as a generator over `range`, 12.8 s; as a
plain `sum(range(0, N, d))`, 4.8 s. Identical mathematics — the gap is purely the cost of
routing each value through a Python-level generator frame instead of letting `sum` consume
a native `range` in C:

```python
# same O(N) work, three costs — the generator frame is the tax
total = sum(v for v in range(0, N, d))   # per-element Python generator overhead
total = sum(range(0, N, d))              # range consumed in C — much cheaper
```

The generator is not *wrong*; it is the wrong tool for a tight numeric loop, where its one
virtue — streaming without materialising — buys nothing, because the sequence is finite
and cheap to hold. (The real winner here is the `O(1)` closed form, which deletes the loop
altogether — see [closed-form-over-iteration](/topics/takeaway/closed-form-over-iteration/).)

**Representation weight.** [Problem 74](/solutions/0074/) and
[Problem 77](/solutions/0077/) both offer a lean and a rich
[memoisation](https://en.wikipedia.org/wiki/Memoization). In problem 74 the fast solution
caches each chain's *length* — a single integer per node; a variant caches the whole chain
*list* and runs about three times slower, allocating a fresh slice for every cached node.
Problem 77 is the same story: counting prime partitions stores one integer per subproblem,
while the enumeration variant builds and stores every partition as a list, dramatically
slower. In both, the heavier structure exists for debugging or visualisation — but the
*answer* only ever needed a number, so on the hot path a number is what you should store.

**Machine word versus big number.** [Problem 104](/solutions/0104/) hunts for a Fibonacci
index whose value has more than sixty thousand digits. You must never form that number in
the search loop. The tail nine digits come from the recurrence reduced
[modulo](https://en.wikipedia.org/wiki/Modular_arithmetic) `$10^9$` — small enough to live
in a 64-bit word — and the leading digits from the fractional part of a logarithm; both
checks are `O(1)`. Contrast [Problem 20](/solutions/0020/), where the giant factorial is
touched *once*: there Python's built-in
[arbitrary-precision integer](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic)
is exactly the right tool, and the hand-rolled digit array in the C version is simply the
price C pays for lacking one. Same object, opposite verdict — because one sits on the hot
path and the other does not.

**Vectorise the batch; match the container to the language.**
[Problem 501](/solutions/0501/) counts integers with eight divisors up to `$10^{12}$` with
a Lucy_Hedgehog prime-counting sieve whose inner update runs on the order of `$10^6$`
times. In pure Python that loop is hopeless, so the hot update becomes a single
[NumPy](https://numpy.org/doc/stable/) batch operation while the short secondary loop stays
plain Python; the C version just writes nested loops, which the compiler makes fast enough
unaided. [Problem 143](/solutions/0143/) makes the language contrast sharper still: Python
closes graph triangles with a [set](https://en.wikipedia.org/wiki/Set_(mathematics))
intersection — concise and fast on a sparse graph — while C sorts each adjacency list and
uses a [two-pointer merge](https://en.wikipedia.org/wiki/Two-pointer_technique) with a
[bitset](https://en.wikipedia.org/wiki/Bit_array) to dodge hashing overhead entirely. The
right container is not universal; it follows the cost model of the language it runs in.

## How to reason about it

- **Find the hot path before you optimise anything.** Multiply each operation's cost by how
  many times the input makes you run it. The abstraction tax is invisible until you do that
  multiplication — and once you have, it usually points at one loop, not the whole program.
- **Off the hot path, prefer the clearest and safest tool.** Where the cost is negligible,
  readability and correctness win outright: Python's bignum in problem 20, the set
  intersection on problem 143's sparse graph. Do not hand-roll what the language gives you
  for free just to save cycles you never spend.
- **Store what the answer needs, not what produced it.** If you only need a count or a
  length, cache a number; the list, the tree, the full object is weight you pay to allocate
  and never read.
- **Order the loop body cheap-first.** Problem 104 tests the cheap tail condition first and
  only reaches the costlier logarithm on the rare survivor — an ordering that keeps the
  expensive tool off the common path.
- **Laziness pays for memory, not for a tight numeric loop.** Reach for a generator when the
  sequence is unbounded or too large to hold; do not reach for one to shave time off a
  bounded arithmetic loop, where it only adds per-element overhead. That is the whole
  trade-off in one line.
- **The biggest lever is often deleting the hot path.** A closed form (problem 1) or a
  sharper algorithm removes the loop instead of tuning it. Match the abstraction to the hot
  path — but first ask whether the hot path needs to exist at all.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0143](/solutions/0143/) — Torricelli Triangles
- ● [0501](/solutions/0501/) — Eight Divisors

<!-- /problems -->
