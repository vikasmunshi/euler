<!-- tags: [bit-length] -->
<!-- status: final 2026-10-18T10:17Z -->
# Bit-length

The [bit-length](https://en.wikipedia.org/wiki/Bit-length) of a positive integer $n$ is the number
of binary digits needed to write it, $\lfloor \log_2 n \rfloor + 1$. It is 0 for $n = 0$. Python
has it as `int.bit_length()`. The general bit vocabulary (masks, XOR prefixes, Kummer and Lucas)
is on [bit manipulation](/topics/technique/bit-manipulation), and this page covers one function
from it. In the four problems below, bit-length is an exact integer $\lfloor \log_2 \rfloor$.
It names the largest power of two below a value, it labels the dyadic block a value belongs to,
and it sizes a fixed-point scale. Each of those turns a loop or a float logarithm into a single
exact operation.

## The idea

For $n \ge 1$, `b = n.bit_length()` is the unique $b$ with $2^{b-1} \le n < 2^b$. Every use below
reads one side of that inequality:

| want | expression | why |
| --- | --- | --- |
| $\lfloor \log_2 n \rfloor$ | `n.bit_length() - 1` | the index of the top set bit |
| largest power of two $\le n$ | `1 << (n.bit_length() - 1)` | the top bit alone |
| number of $j \ge 1$ with $2^j - 1 \le n$ | `(n + 1).bit_length() - 1` | $2^j \le n + 1$ |
| the block $[2^{k-1}, 2^k)$ containing $n$ | $k$ = `n.bit_length()` | blocks are indexed by bit-length |
| a scale big enough for $n$ | `1 << n.bit_length()` | strictly exceeds $n$ |

The reason to prefer it over `math.log2` is exactness. `int(math.log2(n))` converts $n$ to a
`double` first. For $n = 2^{53} + 1$, or for $2^k - 1$ once $k$ is large, rounding can land on the
wrong side of a power of two. `bit_length` reads the integer's representation and is exact at any
size. In C the equivalent is `64 - __builtin_clzll(x)`, where `clz` counts leading zeros. That
compiles to one instruction (`lzcnt` or `bsr`) but is **undefined for $x = 0$**, which is why the
helpers that wrap it test for zero.

## Three uses

**The largest power of two: 14 and 872.** Problem 14 looks for the longest Collatz chain up to a
limit $N$. Any $x \le N/2$ has $2x$ in range with a chain one step longer, so the winner lies in
$(N/2, N]$. The Python sets its scan's lower bound to `2 ** (max_number.bit_length() - 1)`, the
largest power of two $P \le N$. That is a cautionary use. $P$ is always above $N/2$, so the scan
also skips $(N/2, P]$, which the doubling argument does not cover. For $N = 10^6$ that is
$(500000, 524288]$. Both recorded answers lie above $P$, so the results are right, but the sound
bound is `N // 2`. When you replace an arithmetic bound with a bit-length one, check that it
rounds in the safe direction.

Problem 872 climbs a recursively built tree, where the parent of node $k$ in $T_n$ is $k$ plus the
largest power of two not exceeding $n - k$. In Python that is
`1 << ((n - k).bit_length() - 1)`, and in C `1LL << (63 - __builtin_clzll(gap))`. Each step adds
the gap's top bit and so removes it from the gap. The climb therefore takes one step per set bit
of $n - K$, which is $O(\text{popcount})$, and needs no recursion over the tree's construction.
The bit-length is what turns "the greedy largest-child path" into one instruction per level.

**Blocks of equal bit-length: 899.** In this two-pile Nim variant, a sorted position $(a, b)$ is
losing exactly when $2^{\text{bitlen}(a)}$ divides $b + 1$, so it depends on $a$ only through its
bit-length. That suggests grouping the $a$ by block $[2^{k-1}, 2^k - 1]$. Within one block every
$a$ has the same losing partners, $b = m \cdot 2^k - 1$, and there are $\lfloor (n+1)/2^k \rfloor$
of them up to $n$. The count becomes a sum of $O(\log n)$ block terms (block size, clipped at
$n$, times partners per $a$) instead of a loop over $a$. The diagonal correction, positions with
$a = b = 2^j - 1$, is counted by `(n + 1).bit_length() - 1`. Whenever a quantity depends on $x$
only through $\lfloor \log_2 x \rfloor$, sum over bit-length blocks. The
[power of two](/topics/domain/power-of-two) page uses the same banding for 207 and 704.

**A fixed-point scale and a prefix: 882.** Each number's game value in this bit-deletion game is a
[dyadic rational](https://en.wikipedia.org/wiki/Dyadic_rational), and the solution stores it as an
integer scaled by $2^B$ with `B = n.bit_length()`. The scale is chosen so that every value that
occurs has a denominator dividing $2^B$. The arithmetic is then exact and the final ceiling is one shift,
`-((-total) >> scale_bits)`. Inside the game, `x.bit_length()` bounds the loop over deletable bit
positions. `(lo ^ top).bit_length() - 1` finds the highest bit where two bounds disagree, and that
is what the simplicity rule needs. Bit manipulation covers that prefix trick. The bit-length is
what makes it a single call.

## C and Python

| Python | C | note |
| --- | --- | --- |
| `n.bit_length()` | `x ? 64 - __builtin_clzll(x) : 0` | 882 wraps it in a helper with the zero guard |
| `1 << (g.bit_length() - 1)` | `1LL << (63 - __builtin_clzll(g))` | 872, where `g > 0` inside the loop |
| `(n + 1).bit_length() - 1` | `for (j = 1; (1ULL << j) <= n + 1; j++) diagonal++;` | 899 counts with a shift loop |
| `2 ** (N.bit_length() - 1)` | `while (p * 2 < N) p *= 2;` | 14 doubles in a loop |

The loops in 14's and 899's C run at most 64 times, so they cost nothing. They do show the main
risk of hand-rolled bit-lengths, which is an off-by-one at exact powers of two. 14's two spellings
differ there. The Python takes the largest power $\le N$, the C the largest power $< N$. When $N$ is
itself $2^k$, the Python's scan range $(2^k, N]$ is empty, while the C scans $(2^{k-1}, 2^k]$,
which is exactly the sound top half. The problem's limits are not powers of two, so the two agree
on their inputs, but the bounds are not interchangeable. The builtin has a different trap: `__builtin_clzll(0)` is
undefined, and `1 << 40` in C is an `int` shift that overflows, so C needs `1LL` or `1ULL`, as all
four ports use.

## How to reason about it

- **Use `bit_length` for $\lfloor \log_2 \rfloor$, never `int(math.log2(n))`.** It is exact for
  every integer.
- **Write down which inequality you mean.** $2^{b-1} \le n < 2^b$. "Largest power $\le n$" and
  "largest power $< n$" differ exactly at powers of two. Neither is $n/2$, so a bit-length bound
  used for pruning must be checked against the argument that justifies the pruning. Test powers of
  two and the values just above them.
- **Group by bit-length when the formula depends on it.** $O(\log n)$ blocks replace $O(n)$
  terms, and each block's size is a difference of powers of two.
- **Size scales and buffers from it.** $2^{\text{bitlen}(n)} > n$ is a safe fixed-point
  denominator or table size.
- **In C, guard zero and widen the shift.** `x ? 64 - __builtin_clzll(x) : 0`, and `1ULL << k`.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0899](/solutions/0899/) — DistribuNim I

<!-- /problems -->
