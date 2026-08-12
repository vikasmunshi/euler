<!-- tags: [binary-search-algorithm] -->
<!-- status: final -->
# Binary search algorithm

[Binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) is the first non-trivial
algorithm most engineers learn, and it is usually taught as *look up a value in a sorted array*.
That is the smaller half of what it does here. In the problems below it does two quite different
jobs: it finds a **value in a sorted array**, and — more often, and more decisively — it finds the
**answer itself**, by halving an interval of candidate answers against a monotone test. The second
use is the one that turns a search over $10^9$ candidates into forty evaluations of a formula, and
it needs no array at all.

## The idea — the invariant, not the loop

The loop is six lines and everybody can write it. What actually needs care is the invariant, and
stating it explicitly is the difference between a search that is obviously right and one that is
off by one in some corner you will find three hours later. There is really only one shape:

> Maintain `lo` and `hi` such that the predicate is **false at `lo`** and **true at `hi`**, and
> shrink the gap until they are adjacent.

Everything else — which boundary you want, whether the endpoints are inclusive, what you return —
follows from writing down that sentence for the predicate at hand. Problem 80's integer square root
is the pattern in its purest form: find $\lfloor\sqrt{S}\rfloor$ for an $S$ far too large for a
hardware `double`, by bisecting on `mid * mid <= scaled_number`.

```python
low = 0
high = scaled_number
while high - low > 1:
    mid = (low + high) // 2
    if mid * mid <= scaled_number:
        low = mid
    else:
        high = mid
return str(low)[:digits]
```

Three things are worth copying from those six lines. The invariant is `low² ≤ S < high²`, and it
holds at entry and is preserved by both branches. The loop condition is `high - low > 1`, not
`low < high` — the interval shrinks by at least one every iteration, so it cannot hang, and the
answer is `low` by the invariant rather than by a post-loop adjustment. And the test uses only
multiplication, never a division or a square root, so it is exact for arbitrarily large integers.
Python's arbitrary-precision `int` makes that free; the C solution at the same index carries its own
big-integer type for exactly this reason.

## Two jobs: searching an array, searching the answer

**Searching an array** is the familiar one, and in Python it is a library call —
[`bisect`](https://docs.python.org/3/library/bisect.html) for lists,
[`np.searchsorted`](https://numpy.org/doc/stable/reference/generated/numpy.searchsorted.html) for
arrays; in C, `bsearch` or a hand-written `upper_bound`. Sorted prime arrays are the recurring
subject. Problem 187 counts semiprimes as $\pi\!\left(\frac{N-1}{p}\right) - \pi(p-1)$ over small
primes $p$, and gets one of those two terms for nothing: in a dense ascending prime array the
*index* of a prime already **is** the count of primes below it, so only the upper end needs a search.
Problem 501 does the same for a three-shape divisor count, problem 231 locates where $b^i \le n$
stops holding, problem 772 finds the $\sqrt{k}$ boundary that splits primes contributing one factor
from those contributing several. The array is sorted because it was *generated* sorted; the search
costs nothing to add.

**Searching the answer** is the interesting one, and the array is imaginary. All you need is a
monotone predicate over the integers (or the reals) and a cheap way to evaluate it:

| problem | the axis you bisect | the monotone quantity |
| --- | --- | --- |
| 80 | the integer $x$ | $x^2$ against the scaled radicand |
| 156 | $n$ over $[0, 10^{12}]$ | $f(n,d)$, the digit-$d$ tally, non-decreasing in $n$ |
| 235 | the real ratio $r$ | the closed-form partial sum $s(5000)$, strictly falling |
| 587 | the count $n$ of circles | the area ratio $\rho(n)$, strictly falling |
| 686 | the index $J$ | $\mathrm{count}(J)$, the hits so far, non-decreasing |
| 800 | the prime index $j$ | $q\ln p + p\ln q$, increasing in its larger argument |

The pattern is always the same two ingredients, and it is worth naming them because finding them is
the actual work: an **$O(\text{cheap})$ evaluator** for a quantity you would otherwise have to
enumerate, and a proof that the quantity is **monotone** along the axis you intend to halve. Problem
686 is the extreme case — it wants the $n$-th power of two whose decimal expansion starts with a
given digit string, and by equidistribution such hits are sparse enough that the index sought runs
into the billions. A Euclidean-style floor-sum evaluates
$\mathrm{count}(J)$ in $O(\log m)$ without touching a single power of two, and because
$\mathrm{count}$ is non-decreasing, binary search finds the smallest $J$ reaching $n$ in another
logarithmic factor. The whole solve is $O(\log^2 n)$ — a few thousand big-integer operations,
regardless of how large the answer is.

Note that the evaluator is usually the hard part and the search is the easy part. Once problem 587
has a closed form for $\rho(n)$, "find the least $n$ with $\rho(n) \le p$" is thirty lines of
bisection over `long long`. Getting the closed form took an integral.

## You rarely know `hi` — bracket first

Textbook binary search is handed both ends. Real ones usually know only that the answer is
*somewhere above here*, which is why several of these solutions bracket before they bisect: start
from a known-safe `lo`, double `hi` until the predicate flips, then halve.
[Exponential search](https://en.wikipedia.org/wiki/Exponential_search) is the standard name; problems
587, 686 and 235 all do it.

Doubling costs another $O(\log)$ — asymptotically free — and it buys something better than speed:
the bound becomes **proved** rather than guessed. A hand-picked ceiling is a silent correctness
risk, because a binary search over an interval that does not contain the answer returns an endpoint
with total confidence. Problem 686 illustrates the discipline: it *estimates* the ceiling from the
density of hits ($\approx 1/L$ per index), then doubles until $\mathrm{count}(hi) \ge n$ before
trusting it. The estimate makes the doubling short; the doubling makes the estimate safe.

Problem 156 is the same instinct applied in reverse, and worth studying as the general form. It
wants *every* fixed point of $f(n,d) = n$, not the single crossing of a threshold, so there is no
boundary to bisect toward. Instead it keeps a stack of intervals $[lo, hi]$ and uses monotonicity to
kill each one wholesale: if $f(lo,d) > hi$ then $f(n,d) > n$ everywhere inside, and if
$f(hi,d) < lo$ then $f(n,d) < n$ everywhere inside. Anything that survives both tests is split at
the midpoint and re-examined. That is binary search with the "one root" assumption removed — the
halving and the monotone pruning survive, the uniqueness does not.

## The awkward parts

**Which boundary, and the off-by-one.** `bisect_left` and `bisect_right` (C++'s `lower_bound` and
`upper_bound`) differ only in where they put an element equal to the key, and picking the wrong one
gives an answer that is right on every test case without duplicates. Decide from the invariant, not
from memory of the names.

**An insertion point is not a match.** Binary search over a discrete array answers "where would this
go", which is not the same as "what is nearest". When the question is *closest to a target* you must
look at the neighbours of the insertion point, because the target generally falls between two
entries. Problem 85 wants the grid whose rectangle count is nearest two million; rectangle count
factors as $T(H) \cdot T(W)$ over triangular numbers, so for each width it bisects the sorted
triangular numbers and then explicitly considers both sides of the landing spot:

```python
j = bisect.bisect_left(a=numbers, x=target_num_rectangles // num_width)
for height in (j + 1, j + 2):
    if 0 <= height - 1 < len_numbers:
        results[(num := (numbers[height - 1] * num_width))] = (height, width, height * width)
```

The same care shows up in problem 461's combine step and in the two-pointer sweeps below: test `j`
*and* `j+1`, always.

**Floating point.** Bisecting on a real parameter is safe in a way that most numerical methods are
not, because it consumes only the **sign** of the residual — the one quantity rounding is least
likely to corrupt. Problem 235 chooses bisection over [Newton's
method](https://en.wikipedia.org/wiki/Newton%27s_method) deliberately for that reason: with values
spanning eleven orders of magnitude, Newton's quadratic convergence buys nothing that sixty halvings
have not already delivered, while bisection cannot diverge and needs no derivative. Two habits go
with it. Stop on a tolerance several guard digits below the precision the answer is reported to, so
the residual interval cannot disturb the final rounding. And where a comparison decides membership
rather than a limit, widen it by a small epsilon — problem 461 admits pairs within `pi + 1e-6`
precisely so that rounding cannot silently discard a pair belonging to the optimal quadruple.

**Monotonicity must be real, on the axis you are halving.** This is the failure that actually bites.
Problem 772 looks like a threshold problem — the least $N$ all of whose $k$-bounded partitions are
balanceable — and it is not: the property is not monotone in $N$, since a larger $N$ can be *worse*.
Binary searching that axis would return a confident wrong number. The solve comes from a divisibility
characterisation instead, and the binary search survives only in its proper role, finding a boundary
in a sorted prime array. Before you bisect, say out loud what is monotone and why.

## When binary search is the wrong tool

**When the queries are sorted too, use two pointers.** $n$ binary searches cost $O(n \log n)$; if
the targets themselves move monotonically, a single merge-style sweep does the same work in $O(n)$
with no branch misprediction and perfect locality. Problem 461's C solution walks `i` up from the
smallest pair-sum while `j` walks down, because `target = pi - pairs[i].sum` decreases as `i`
increases, so `j` never moves back — one sequential pass instead of millions of searches. Problem
252's C merge and problem 184's rotating-arc count are the same trade. Note what the Python versions
of those solutions do instead: they call `searchsorted`, in chunks, because in vectorised code you
cannot `break` out of a loop — a binary search *is* the vectorised form of "where does this monotone
condition stop". Both are right; the language decides. See
[two-pointer technique](/topics/technique/two-pointer-technique).

**When the key space is structured, index it directly.** $O(\log n)$ in an inner loop is still a
factor you can delete. Problem 565's first solution answers "sum of $g(p)$ over primes $p \le x$" by
binary searching a prefix-sum array over every prime up to $n$. Its second solution notices that the
only arguments ever queried are the $O(\sqrt{n})$ distinct values of $\lfloor n/k \rfloor$, stores
them in a two-array sqrt-decomposition, and answers each lookup in $O(1)$ — which, together with not
materialising the primes, is what lifts the solve from $10^9$ to $10^{11}$. The general move:
binary search is what you write when the keys are merely *sorted*; when they are also *predictable*,
compute the index.

**When a hash set would do — unless you are writing C.** This is the one place where binary search
appears not as an optimisation but as a substitute for a missing container. Problem 49 tests
membership among $n$-digit primes and problem 122 tracks a shrinking set of unresolved targets;
both use a Python `set` for $O(1)$ membership, and both use a **sorted array plus `bsearch`** in C,
because the standard library has no hash set. The asymptotics are worse and it does not matter — at
a few hundred elements the contiguous array wins on cache behaviour, deletion is a `memmove`, and
the minimum is `remaining[0]` in $O(1)$ for free, which the C version of problem 122 uses as its
pruning bound. Sorted-array-as-set is a perfectly good data structure when $n$ is small and writes
are rare.

## How to reason about it

Reach for binary search whenever a quantity is monotone along some axis and you can evaluate it far
more cheaply than you can enumerate it. Then, in order:

1. **Name the axis and the predicate.** Write the predicate so it is false below the answer and true
   at and above it. If you cannot write that sentence, you do not have a binary search.
2. **Prove the monotonicity** on that axis — not on the quantity the problem talks about. This is
   where wrong answers come from, and it costs one paragraph of thought.
3. **Make the evaluator cheap.** A closed form, a floor-sum recursion, a prefix-sum lookup. The
   search contributes $\log$; the evaluator sets the constant.
4. **Bracket by doubling** rather than guessing a ceiling, so the interval provably contains the
   answer.
5. **State the invariant in the loop**, halt on `hi - lo > 1`, and return the endpoint the invariant
   names.
6. **Check the neighbours** if the question was "nearest" rather than "equal".
7. **Then ask whether you need it at all** — sorted queries want two pointers, structured keys want
   direct indexing.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0252](/solutions/0252/) — Convex Holes
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0800](/solutions/0800/) — Hybrid Integers

<!-- /problems -->
