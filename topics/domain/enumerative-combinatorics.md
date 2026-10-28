<!-- tags: [enumerative-combinatorics] -->
<!-- status: final 2026-10-18T12:42Z -->
# Enumerative combinatorics

[Enumerative combinatorics](https://en.wikipedia.org/wiki/Enumerative_combinatorics) is the part of
combinatorics that treats a count as a **function of a size parameter**: not "how many tilings of
this row?" but $a(n)$, the number of tilings of a row of length $n$, as a sequence to be computed,
inverted or summed. The broader [combinatorics](/topics/domain/combinatorics) page covers the
general toolkit (modelling equivalence, recurrences, complements, symmetry, integer width), and the
three solved problems here use parts of it. This page adds the sequence view, which asks three
questions those problems turn on: how to get $a(n)$ for one $n$, how to get $a(n)$ for *every*
$n$ up to a bound at once, and how to find the $n$ at which $a(n)$ takes a given value.

## The idea — a count is a sequence

Stanley's framing in [*Enumerative Combinatorics*](https://math.mit.edu/~rstan/ec/) is that the
goal is a *good description* of $a(n)$, and a good description can be any of:

| description | what it gives | problem here |
|---|---|---|
| a recurrence in $n$ | every $a(n)$ in order, by a table | 114 |
| a tabulation by enumerating structures and recording their size | $a(n)$ for all $n \le N$ at once | 126 |
| an explicit sum (often alternating, from inclusion–exclusion) | one $a(n)$ directly | 239 |
| a generating function $\sum a(n) x^n$ | all of the above, as algebra | (background) |

Which description is "good" depends on what the problem asks of the sequence. A single large $n$
favours an explicit sum or a fast recurrence. A question like "the least $n$ with $a(n) = 1000$"
favours tabulating every $n$ at once, because $a(n)$ is not monotone and no single evaluation tells
you where to look.

## Three descriptions in practice

**114, block combinations: a recurrence from the first decision.** A row of length $n$ is filled
with grey unit squares and red blocks of length at least $m$, with two red blocks never adjacent.
The solution decides what occupies position $i$. Either it is grey, leaving positions $i+1$ onward,
or a red block of length $k \ge m$ starts there. A block that ends before the row's end must be
followed by a grey square, so the next free position is $\text{end} + 1$, and the "not adjacent"
rule becomes a $+1$ offset rather than extra state. With $f[n] = 1$ as the empty filling:

$$f[i] = f[i+1] + [\,n - i \ge m\,] + \sum_{k=m}^{n-i-1} f[i + k + 1],$$

where the bracket counts the one block that runs exactly to the end of the row.

As written this is $O(n^2)$. The inner sum is a suffix sum of $f$, so a running total would make it
$O(n)$. At $n = 50$ that does not matter, but it is the usual first optimisation for this family of
tiling recurrences (problems 115–117 are its siblings).

**126, cuboid layers: tabulate by enumerating structures.** Wrapping an $a \times b \times c$
cuboid in successive layers of unit cubes uses
$$\text{layer}_m = 2(ab + bc + ca) + 4m(a + b + c + m - 1)$$
cubes in layer $m+1$. Let $C(n)$ be the number of (cuboid, layer) pairs that need exactly $n$
cubes. The problem asks for the least $n$ with $C(n) = 1000$. There is no formula for $C(n)$, and
evaluating it for one $n$ means counting the solutions of a Diophantine equation in four unknowns. The solution turns the
question round: it enumerates every structure (sorted $a \le b \le c$, each layer $m$) whose layer
size is at most a bound $N$, and increments a histogram at that size. Each structure is counted
once, in its canonical order, and $C(n)$ for every $n \le N$ falls out of one pass. The loops break
as soon as the smallest possible value overshoots $N$, so the total work is close to the number of
structures counted, effectively $O(N)$. If no $n \le N$ reaches the target, the bound doubles and
the tabulation runs again. Doubling bounds the total work to about twice the final pass.

This is the general move for "least $n$ with $a(n) = t$" and for "$\sum_{n \le N} a(n)$". **Generate
the objects and bin them by size, instead of evaluating the counting function point by point.**
It works whenever the objects can be listed in order of a parameter that bounds their size.

**239, twenty-two foolish primes: an explicit sum by inclusion–exclusion.** The discs $1..100$ are
permuted at random. The question is the probability that exactly 22 of the 25 prime-numbered discs
are not in their home position. This generalises the
[rencontres numbers](https://en.wikipedia.org/wiki/Rencontres_numbers), which count permutations
with a given number of fixed points, to the case where only a subset of positions is watched.
Choose which $f = 25 - 22$ primes stay home ($\binom{25}{f}$ ways) and pin them. Then count the
arrangements of the other $n - f$ discs in which none of the 22 chosen primes is at home.
[Inclusion–exclusion](/topics/technique/inclusion-exclusion-principle) over the set of those primes
that are nevertheless fixed gives

$$\binom{25}{f} \sum_{k=0}^{22} (-1)^k \binom{22}{k} (n - f - k)! ,$$

while the 75 non-prime discs stay unconstrained throughout. The terms are carried across $k$
incrementally: $(n-f-k)!$ is divided by $n - f - k$ and $\binom{22}{k}$ is updated by the
multiplicative step, both as exact integer divisions, so no factorial is recomputed. The
probability is that count over $100!$, a ratio of two integers of several hundred bits, and the
twelve decimals asked for come from exact rounding, $\lfloor (2 p\,10^{12} + q) / 2q \rfloor$,
not from floating point. A double can hold the magnitude of $100!$ but only 53 bits of it, so an
alternating sum of such terms would carry rounding error of unknown size into the result. Exact
integers make the twelfth decimal certain.

## Python and C

- **114** is identical on both sides. The only change is the accumulator: `long long` in C, because
  the count at $n = 50$ already exceeds 32 bits.
- **126** is identical too: a `calloc`'d `int` histogram in C against a Python list, with the
  same canonical-order loops and the same doubling of the bound. The histogram values are small, so
  `int` is enough; the *bound* is what grows, and a doubled `int` limit stays far from overflow at
  the target count.
- **239** is where the languages differ. Python's `int` carries the 525-bit $100!$ without
  comment. C uses GMP (`mpz_t`), and every Python operation maps to one GMP call: the incremental
  updates use `mpz_divexact_ui`, which is faster than general division because it is told the
  division is exact. The half-up rounding is `mpz_mul_2exp` and `mpz_fdiv_q`. The scaled result
  fits in an `unsigned long`, so it leaves GMP only for printing.

## How to reason about it

- **Ask what the problem wants from the sequence.** One term, all terms up to $N$, the first term
  meeting a condition, or a sum of terms each call for a different description. Pick the
  description to match before writing code.
- **For "least $n$ such that …", tabulate.** Enumerate the structures by a size-bounding parameter,
  bin them, and scan. Grow the bound geometrically if you cannot predict it.
- **Make the order canonical.** Both 114 (first decision) and 126 ($a \le b \le c$) count each object
  once because there is exactly one way to generate it. Check this against brute force for small
  sizes. A missing or doubled symmetry is the usual bug.
- **Use exact arithmetic for alternating sums.** Inclusion–exclusion sums large terms of
  alternating sign to get a small result. Big integers (or a modulus, if the problem allows one)
  are required, and incremental updates keep the cost to one multiply or divide per term.
- **Look the sequence up.** The first few terms of a combinatorial sequence, computed by brute force
  and entered into [OEIS](https://oeis.org/), often return a formula, a recurrence or a generating
  function. Verify it, and then use it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ○ [0480](/solutions/0480/) — The Last Question
- ○ [0502](/solutions/0502/) — Counting Castles
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ○ [0657](/solutions/0657/) — Incomplete Words
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0696](/solutions/0696/) — Mahjong
- ● [0698](/solutions/0698/) — 123 Numbers
- ○ [0709](/solutions/0709/) — Even Stevens
- ○ [0762](/solutions/0762/) — Amoebas in a 2D Grid
- ○ [0763](/solutions/0763/) — Amoebas in a 3D Grid
- ○ [0781](/solutions/0781/) — Feynman Diagrams
- ○ [0818](/solutions/0818/) — SET
- ○ [0849](/solutions/0849/) — The Tournament
- ○ [0873](/solutions/0873/) — Words with Gaps
- ○ [0907](/solutions/0907/) — Stacking Cups
- ○ [0936](/solutions/0936/) — Peerless Trees
- ○ [0987](/solutions/0987/) — Straight Eight

<!-- /problems -->
