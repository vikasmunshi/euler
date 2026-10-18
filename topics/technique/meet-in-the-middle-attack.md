<!-- tags: [meet-in-the-middle-attack] -->
<!-- status: final -->
# Meet-in-the-middle attack

The [meet-in-the-middle attack](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) comes from
cryptanalysis. To break double encryption you do not try all $2^{2k}$ key pairs. You encrypt forward
from one end and decrypt backward from the other, then look for a value the two lists share. The
same trade works for any search whose candidates are combinations of two independent halves. Here
it shows up as subset sums, magic-square halves, four-term sums and balanced subsets. A search of
size $N = A \cdot B$ becomes two enumerations of size about $\sqrt N$ and a join. It costs
$O(\sqrt N)$ memory instead of $O(1)$, and in all four problems below that was the only way to
finish.

## The idea

Write a candidate as a pair $(x, y)$ with $x$ from half $X$ and $y$ from half $Y$. Suppose the
condition on the pair can be written as $\kappa(x) = \lambda(y)$ for some *key* functions, or
as "$\kappa(x) + \lambda(y)$ is as close as possible to $t$". Then:

1. Enumerate $X$ and tabulate $\kappa(x)$. If you are counting, keep a count per key, so equal keys
   merge.
2. Enumerate $Y$ and compute $\lambda(y)$ for each element.
3. Join the two tables on the key.

That is $|X| + |Y|$ enumeration work plus the join, where brute force would cost $|X| \cdot |Y|$.
The [subset-sum](https://en.wikipedia.org/wiki/Subset_sum_problem) version, splitting $n$ items into
two halves of $n/2$ and matching sums, is the
[Horowitz–Sahni](https://en.wikipedia.org/wiki/Subset_sum_problem#Horowitz_and_Sahni) algorithm,
and it turns $2^n$ into $2^{n/2}$.

The hard part is not the join. It is finding a **cut across which the halves interact through a
small key**. If the key carries most of a half's state, the tables do not merge and nothing is
saved.

## Choosing the cut and the key

| problem | halves | key | join |
| --- | --- | --- | --- |
| 152 | the reduced items, balanced by product of option counts | exact integer numerator of $\sum 1/k^2$ | hash, lookup `target - v` |
| 166 | top two rows / bottom two rows, per common sum $s$ | three column partial sums + two diagonal parts | hash (Py) / dense table (C) |
| 461 | pairs $(a, b)$ / pairs $(c, d)$ | the real pair sum $f(a) + f(b)$ | sort, then nearest to $\pi - v$ |
| 768 | the sockets of $\mathbb{Z}_{30}$, split 15 / 15 | packed coordinate vector in $\mathbb{Z}[\zeta_{30}]$ | hash on $-v$ (Py) / sort-merge (C) |

**Problem 166** shows the clearest cut. A $4 \times 4$ magic square of digits, cut horizontally,
leaves two $2 \times 4$ halves. All the bottom half needs to know about the top half is what each
column and diagonal still needs. That is four column sums and two diagonal parts, and the fourth
column is forced because each half sums to $2s$, so the key has five components. Ten-digit
cells give $10^{16}$ grids. Through the key, the work is $\sum_s |R_s|^2$ row pairs, a few
million. The constraint that couples the halves is linear, so the key is a vector of partial sums
and the complement is $s$ minus each one.

**Problem 152** first reduces the problem: number theory removes the large primes and leaves a few
dozen multiple-choice items. Only then does the split run. The halves are not split by item count,
since items have different numbers of options. The solution sorts items by option count and greedily
puts each into the half with the smaller running product. The cost is set by the larger half, so
that half should be as small as possible. The key is a large exact integer, the numerator over a
common denominator, because a float sum of $1/k^2$ cannot decide equality.

**Problem 768** counts balanced subsets of the 30th roots of unity. Writing each root in an integer
basis of $\mathbb{Z}[\zeta_{30}]$ makes "sums to zero" an exact test on vectors, and packing each
vector into one integer at a base wider than any coordinate makes vector addition a single integer
add. A subset is balanced when its two halves have *opposite* packed sums. The join also records
cardinalities, and convolving the two histograms gives the balanced counts for every subset size
at once.

**Problem 461** asks for four indices whose $e^{k/n} - 1$ values sum closest to $\pi$. Here there is
no exact key to look up. "Nearest" needs an *ordered* table, so hashing cannot do the join. The
solution enumerates pairs with $a \le b$, sorts them by sum, and for each pair finds the partner
nearest $\pi - v$. When the target is an inequality or a nearest value rather than an equality,
sort the table instead of hashing it.

## Three joins

- **Hash join.** Build a `dict` from key to count over one half, then look up each complement from
  the other. This is linear and the natural Python choice (152, 166, 768). The counts multiply,
  `left[target - v] * right[v]`, so a counting problem never expands individual matches.
- **Dense table.** If the key components have small ranges, a mixed-radix index
  $((((c_1 w + c_2) w + c_3) w + d_1) w + d_2)$ with $w = 2M + 1$ replaces the hash. 166's C does
  this, keeps a list of touched indices so the combine step skips empty cells, and bounds-checks
  each complement index, since $s - c_j$ can fall outside the table.
- **Sort and sweep.** Sort both tables (or one, if the target is fixed) and walk them. In 461's C,
  `i` climbs from the smallest pair sum while `j` falls from the largest. Because $\pi - v_i$
  decreases as `i` grows, `j` never moves back, and the whole join is one $O(P)$ pass that tests `j`
  and `j + 1` at each step. 768's C negates one half's keys, sorts both with `qsort`, and merges.
  That avoids writing a hash table for 128-bit keys.

## C and Python

The split is identical in both languages. They differ in how the table is stored:

- **Big keys.** Python's integers make 152's numerators and 768's packed vectors free. 152's C
  writes a fixed-width 384-bit integer type with only the operations the algorithm uses (add,
  subtract, small multiply and divide, compare, hash) and an open-addressing table keyed on it.
  768's C fits its packed vectors in `__int128` and reports overflow rather than wrapping when the
  radical grows past what 128 bits can hold.
- **Vectorised join.** 461's Python cannot afford a scalar two-pointer loop over tens of millions of
  pairs. It sorts with `np.argsort` and runs `np.searchsorted` over chunks of $2^{20}$ targets,
  checking the insertion point and the one below it. That is the same nearest-neighbour join,
  written as a batch of binary searches instead of a sweep.
- **Hash or not.** C has no built-in hash map, so the C side usually prefers a dense table (166) or
  sort-merge (461, 768) where Python reaches for a `dict`. Only 152, whose big-integer keys are
  sparse and unordered, hand-rolls a hash table.

## How to reason about it

- **Look for a cut with a narrow interface.** Count how many numbers one side must know about the
  other. If that is small (five partial sums, one numerator, one vector), meet in the middle
  applies.
- **Balance by search-space size, not by item count.** The larger half sets both time and memory.
- **Exact keys hash; "nearest" keys sort.** Pick the join from the shape of the target condition.
- **Store counts, not members, when counting.** Equal keys merge, the table shrinks, and the join
  multiplies counts. Keep a separate reconstruction path, like 152's `--show`, for when you need the
  actual sets.
- **Halve the remaining symmetry too.** 461 enumerates only $a \le b$, which halves the table before
  the sort.
- **Memory is the price.** $2^{n/2}$ entries is fine at $n = 30$ and not at $n = 80$. That is why
  152 reduces its 79 candidates to a few dozen items before splitting. The exponential wall is
  still there, as 768's jump from radical 30 to radical 42 shows. Meet in the middle halves the
  exponent but does not remove it.

The bitmask enumeration that builds each half's table is on
[power set](/topics/technique/power-set).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0768](/solutions/0768/) — Chandelier

<!-- /problems -->
