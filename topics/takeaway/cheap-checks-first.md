<!-- tags: [cheap-checks-first] -->
<!-- status: final -->
# Order checks by cost

A program that filters candidates spends its time inside the tests it runs. When
several conditions must all hold, the order you write them in is a performance
decision: a cheap, highly selective test placed first rejects most candidates
before the expensive test ever runs, and — thanks to
[short-circuit evaluation](https://en.wikipedia.org/wiki/Short-circuit_evaluation) —
the expensive one is simply never reached on them. Across the problems below the
same move recurs: find the cheapest necessary condition, run it first, and let it
guard everything costlier.

## The idea

Most of these problems reduce to the same skeleton — enumerate candidates, keep
the ones that satisfy several conditions. Written as a conjunction `A and B and C`,
the language evaluates left to right and stops at the first false: that is what
[short-circuit evaluation](https://en.wikipedia.org/wiki/Short-circuit_evaluation)
means, Python's `and` and C's `&&`. So the cost of the whole test is dominated by
whichever conditions run on the most candidates — and that is decided entirely by
ordering.

Two properties of a test govern a good order:

- **Cost** — how long it takes on one candidate. An array lookup or a `% 9` is a
  few nanoseconds; a [factorization](https://en.wikipedia.org/wiki/Integer_factorization),
  a [primality test](https://en.wikipedia.org/wiki/Primality_test), or a $2^n$
  subset enumeration is orders of magnitude more.
- **Selectivity** — the fraction of candidates it rejects. A test that kills 90%
  of the input shrinks the work every later test sees tenfold.

You want the tests that are cheap *and* selective at the front. A cheap test that
rejects almost nothing is nearly free but buys nothing; an expensive test that
rejects almost everything is worth running only when nothing cheaper does the same
job. The ideal first filter is a cheap [*necessary condition*](https://en.wikipedia.org/wiki/Necessity_and_sufficiency) —
something every true answer must satisfy, read off the structure of the problem —
so it never discards a real solution, only narrows the field before the costly
*sufficient* check confirms what survives.

```python
# a cheap, selective necessary condition guards the expensive confirmation
if k % 9 in (0, 1) and passes_expensive_check(k):
    accept(k)
```

That is the shape of nearly every solution below: a sieve or generator produces a
constrained candidate stream, one or two $O(1)$ filters strip the bulk of it, and
only the residue pays for the heavy test.

## How to reason about it

The purest demonstration is [Special Subset Sums: Optimum](/solutions/0103/), which
ships two solutions that are *identical except for the order of two checks*.
Validating a candidate set means testing a cheap $O(n^2)$ cardinality condition and
an expensive $O(2^n)$ distinct-subset-sum condition. Solution 0 runs the expensive
one first; solution 1 runs the cheap one first — and because almost every candidate
fails the cardinality test, the reorder skips the subset enumeration on nearly every
leaf of the search. The measured effect is large and grows with the search: in C,
$n = 7$ drops from about $0.068$ s to $0.009$ s (~7.8×), and $n = 8$ from $1.52$ s
to $0.32$ s (~4.8×). Same algorithm, same answer, one line moved.

The rest are filter chains where a structural insight yields the cheap front test:

- [Prime Generating Integers](/solutions/0357/) needs $d + n/d$ prime for every
  divisor $d$ of $n$. A single $d = 2$ test — one array lookup asking whether
  $2 + n/2$ is prime — discards almost every candidate before any factorization
  runs; it is the strongest cheap filter in the solution.
- [Number Splitting](/solutions/0719/) tests whether $k^2$ can be split into
  digit-groups summing to $k$, an exponential [backtracking](https://en.wikipedia.org/wiki/Backtracking)
  search. But [casting out nines](https://en.wikipedia.org/wiki/Casting_out_nines)
  forces $k \equiv 0$ or $1 \pmod 9$, so a `k % 9` comparison removes about 78% of
  roots before the search is entered.
- [The Primality of $2n^2 - 1$](/solutions/0216/) only needs to sieve with primes
  $p \equiv \pm 1 \pmod 8$; a `p & 7` test discards half of all primes before the
  expensive [Tonelli–Shanks](https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm)
  square-root step.
- [Reversible Prime Squares](/solutions/0808/) runs its cheapest test — is the
  square a [palindrome](https://en.wikipedia.org/wiki/Palindromic_number)? — first,
  ahead of the perfect-square check and the primality probe behind it.
- [Prime-proof Squbes](/solutions/0200/) generates sparse squbes, then applies a
  substring test before the costly prime-proof mutation check, so only the few
  candidates that could possibly qualify pay for it.

A few cautions earn their keep:

- **The cheap check must be a necessary condition.** Reordering is free only when
  the filter never rejects a true answer — a parity, a residue modulo a small
  number, a digit-tail constraint, a substring. Derive it from the problem's
  structure and satisfy yourself it admits *every* solution; a filter with a false
  negative silently corrupts the answer, and it will still pass the small example
  that happens to have none.
- **Order by cost *and* selectivity, not cost alone.** The front test should be the
  one with the best ratio of candidates-killed to time-spent. A cheap test nobody
  fails just adds a branch.
- **Selectivity compounds down the chain.** Each filter runs only on what the
  previous ones let through, so the biggest wins come from putting the most
  discriminating cheap test first — every later test then sees a fraction of the
  input. [Largest Integer Divisible by Two Primes](/solutions/0347/) applies the
  same instinct to loop bounds: it `break`s each prime-pair loop the instant the
  product exceeds $N$, so the expensive inner work never runs on pairs that cannot
  contribute.

The through-line is that for a conjunction of pure tests correctness is
order-independent but cost is not. Spend a moment deciding which check is cheapest
and kills the most, put it first, and let short-circuit evaluation keep the
expensive checks off the candidates that were never going to survive.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
