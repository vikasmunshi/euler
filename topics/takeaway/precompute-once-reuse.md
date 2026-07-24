<!-- tags: [precompute-once-reuse] -->
<!-- status: final -->
# Precompute once, reuse

Many of these problems ask the same small question thousands of times over: *is
this number prime?*, *how long is this chain?*, *what is the cheapest path from
here?* The expensive move is answering it; the cheap move is answering it once,
storing the result, and reading it back. When the queries share structure — they
range over the same integers, walk the same graph, overlap on the same
subproblems — the honest cost of the whole computation is one table built up
front, not a fresh calculation per query. Across the problems below the same
habit recurs: spot the work that repeats, [amortise](https://en.wikipedia.org/wiki/Amortized_analysis)
it into a table computed once, and turn every later use into a lookup.

## The idea

The table takes one of a few recurring shapes, but the accounting is always the
same: pay a setup cost once, then serve each of $Q$ queries in (near) constant
time, so $Q$ expensive computations collapse to one build plus $Q$ cheap reads.
The lever is worth pulling exactly when the build is cheaper than $Q$ separate
computations — which is to say, when the queries overlap.

**A sieve or lookup table, queried across a whole range.** The
[Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes)
(or of Sundaram) computes *every* prime up to $N$ in $O(N \log \log N)$ — far
less than testing each of $N$ numbers individually — and hands back a set in
which membership is $O(1)$. [Circular Primes](/solutions/0035/) sieves once, then
tests every digit rotation of every candidate by set lookup; [Prime Power
Triples](/solutions/0087/) sieves the primes up to $\sqrt{N}$ once and reuses that
one list in all three exponent roles. The same idea generalises past primality:
[Non-Abundant Sums](/solutions/0023/) runs a divisor-sum sieve — for each $i$, add
$i$ to every multiple of $i$ — to label all abundant numbers in one $O(N \log N)$
sweep, rather than factoring each number on its own.

**A memoised map over a functional graph.** When each input maps to exactly one
successor and many inputs feed into shared tails, a
[memoised](https://en.wikipedia.org/wiki/Memoization) walk records each node's
answer once. [Longest Collatz Sequence](/solutions/0014/) caches each chain
length so a start whose tail was already seen stops the moment it lands on a
cached value; [Digit Factorial Chains](/solutions/0074/) walks each chain forward
and *back-propagates* the length into every node it touched, so across all starts
each node is resolved once and the whole scan is $O(N)$ amortised. This is
[dynamic programming](/topics/technique/dynamic-programming/) read as caching:
the overlapping subproblems are the shared graph tails.

**A cumulative table that answers range queries by subtraction.** A
[prefix-sum](https://en.wikipedia.org/wiki/Prefix_sum) array built once turns the
sum of any contiguous run into a single difference. [Consecutive Prime
Sum](/solutions/0050/) accumulates the running total of the sieved primes, so the
sum of primes $j{+}1 \dots i$ is just `prefix[i] - prefix[j]` — one subtraction
instead of re-adding the run. The [path-sum](/solutions/0081/) problems do the
same in two dimensions: fill each cell with the best cost from it to the goal in
one topological sweep, and every cell's answer is then a $O(1)$ read of its two
finalised neighbours.

## How to reason about it

Reach for a precomputed table when the *same* expensive answer is needed more
than once and the set of possible answers is bounded — the candidates share a
range, a graph, or a grid. The tell is a loop whose inner call would recompute
something an earlier iteration already found. The payoff is asymptotic, not a
constant factor: $Q$ queries drop from $Q \cdot C$ to $\text{build} + Q$, and
when $\text{build} \ll Q \cdot C$ that reshapes the running time.

A few cautions earn their keep:

- **Overlap is the whole justification.** A table amortises only when it is read
  many times; precomputing a value queried once is pure overhead, and a sieve to
  $N$ to answer a single membership test is slower than one direct check. Confirm
  the queries actually reuse the work before you build for it.
- **Size the table to the input, not to a fixed bound.** Build the sieve, cache,
  or DP array *inside* `solve()`, dimensioned from the arguments — a bound sized
  to the input is the companion habit of
  [sizing work to the input](/topics/takeaway/size-work-to-the-input/). A table
  hard-coded to some maximum wastes memory on small inputs and silently breaks on
  large ones.
- **Rebuild the table each call — do not hoist it out of the timed loop.** The
  benchmark runs `solve()` repeatedly with `--runs=N` and times the repeats, so a
  table built at module import, or a cache left warm between calls, is paid for
  *once* and then free — which flatters the measurement and hides the real cost.
  Keep the `@lru_cache` or memo dict local to `solve()` so every run pays the full
  build, and the time you report is the time the algorithm actually takes. [Longest
  Collatz Sequence](/solutions/0014/) is written exactly this way: a fresh cache
  per call.
- **You are trading memory for time.** The table has to fit. When the answer set
  is too large to tabulate, fall back to recomputation, a smaller rolling window
  (keep only the DP frontier, not the whole grid), or — when the structure is
  regular enough — skip the table entirely for a
  [closed form](/topics/takeaway/closed-form-over-iteration/), the opposite
  extreme where no storage is needed at all.

The through-line is that repeated work is a table waiting to be built. Find the
computation that recurs, do it once into a structure whose reads are cheap, and
let every later query pay a lookup instead of the full price.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0096](/solutions/0096/) — Su Doku
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0118](/solutions/0118/) — Pandigital Prime Sets
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0199](/solutions/0199/) — Iterative Circle Packing
- ● [0220](/solutions/0220/) — Heighway Dragon
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0710](/solutions/0710/) — One Million Members

<!-- /problems -->
