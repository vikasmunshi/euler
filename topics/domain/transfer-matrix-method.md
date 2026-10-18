<!-- tags: [transfer-matrix-method] -->
<!-- status: final 2026-10-18T12:38Z -->
# Transfer matrix method

The [transfer-matrix method](https://en.wikipedia.org/wiki/Transfer-matrix_method) counts
configurations of a long object by cutting it into slices. If the only thing one slice needs to
know about everything before it is a small **boundary state** (the colours along a cut, which
cells a path crosses), then the count is a product of matrices: entry $T_{uv}$ is the number of
ways to fill one slice so that boundary $u$ on the left becomes boundary $v$ on the right, and the
total is $\mathbf{1}^\top T_1 T_2 \cdots T_n \mathbf{1}$. Colourings of grids, tours of strips and
chains of gadgets all fit this shape, which is why the method keeps coming back. What changes from
problem to problem is how much of the matrix you actually build. Of the three solved problems
below, one contracts it a column at a time without ever writing it down, one collapses it to a
single number, and one replaces it with the linear recurrence it guarantees.

## The idea — boundary states and a matrix per slice

The method rests on one modelling decision: **what is the state at a cut?** It must be small
enough to enumerate and complete enough that the left part and the right part interact *only*
through it. Once that holds:

- the count for $n$ slices is a matrix product, so a uniform strip is $\mathbf{1}^\top T^n
  \mathbf{1}$ and [matrix exponentiation](/topics/technique/matrix-exponentiation) gives it in
  $O(s^3 \log n)$ for $s$ states;
- by [Cayley–Hamilton](/topics/domain/cayley-hamilton-theorem), the sequence of counts satisfies a
  linear recurrence of order at most $s$, whether or not you ever write $T$ down;
- symmetries of the problem become symmetries of $T$. A vector fixed by those symmetries, such as
  the all-ones vector under colour permutations, is often an eigenvector.

This is [dynamic programming](/topics/technique/dynamic-programming) over a frontier, written in
linear-algebra notation. The notation earns its keep through the second and third points: it tells
you a recurrence exists and what order to expect, and it lets you reason about eigenvectors
instead of states.

## Three sizes of matrix

**189, tri-colouring a triangular grid: contract, don't build.** The grid has 8 rows of small
triangles, and a row's upward triangles are its only link to the row below, so the boundary state
is the colouring of one row's upward triangles: $3^r$ states for row $r$. The transfer from row $r$
to row $r+1$ is a $3^r \times 3^{r+1}$ matrix, about $1.4 \times 10^7$ entries at the last row.
Building it is wasteful because each entry is a *product* of small local factors: the downward
triangle between new triangles $v_i$ and $v_{i+1}$, under old triangle $u_i$, can take
$W[v_i][v_{i+1}][u_i]$ colours. The solution therefore never forms the matrix. It contracts that
product one column at a time, keeping a single array indexed by a mixed base-3 key in which the
low trits are the new row being built and the high trits are the old row not yet consumed. Each
column step replaces one old trit $u_i$ by one new trit $v_{i+1}$, so the array stays at
$3^{r+1}$ entries and a whole row costs $O(r \cdot 3^{r+1})$. This is the same contraction as
[broken-profile](/topics/domain/broken-profile) DP and a small
[tensor network](/topics/technique/tensor-network): a big transfer matrix that factors into local
pieces is applied one piece at a time.

**194, coloured configurations: the matrix is a scalar.** A configuration is a chain of $a$ units
of type A and $b$ of type B, glued along vertical edges, and the count is of proper $c$-colourings
with $c$ near 2000. The boundary state is the ordered colour pair $(t, b)$ on a shared edge, so
$c(c-1)$ states, about four million, and a $4\text{M} \times 4\text{M}$ matrix per unit type. The
solution instead uses symmetry. Permuting colours maps proper colourings to proper colourings, and
every state $(t, b)$ with $t \ne b$ is one permutation away from every other, so every row of $T_A$
has the same sum $S_A$ (and likewise $S_B$). The all-ones vector is therefore an eigenvector of
both matrices, and since the chain starts from the all-ones vector (any colouring of the first
edge), each unit just multiplies the count by its scalar:

$$N(a, b, c) = \binom{a+b}{a}\, c(c-1)\, S_A^a\, S_B^b .$$

The order of the units drops out, which is why the binomial counts arrangements independently.
$S_A$ and $S_B$ are closed-form polynomials in $c$, found by summing the inner chain's colourings
over the equality classes of the right edge relative to the left (does $r_t$ equal $l_t$, $l_b$,
neither?). That turns a four-million-state matrix into a short calculation.
[Exploiting the symmetry](/topics/takeaway/exploit-symmetry) is the whole solution.

**237, tours on a $4 \times n$ board: use the recurrence the matrix promises.** A Hamiltonian
path from the top-left to the bottom-left corner of a $4 \times n$ board can be cut between columns,
and the state at a cut is how the path's strands cross it and how they are paired up. That is a
finite set of states for height 4, so a transfer matrix exists, and Cayley–Hamilton then says the
tour count obeys a linear recurrence of bounded order. The solution relies on that guarantee
instead of building the matrix. It counts tours by exhaustive search for small $n$, fits the
fourth-order recurrence $T(n) = 2T(n-1) + 2T(n-2) - 2T(n-3) + T(n-4)$, checks it against the search
up to $n = 12$, and then raises the $4 \times 4$
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix) to the power $n - 4$ modulo
$10^8$. The transfer matrix is never seen, but it is why fitting a recurrence was safe. See
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence) and, for doing
the fit mechanically, [Berlekamp–Massey](/topics/technique/berlekamp-massey-algorithm).

## Python and C

The algorithms match; the differences are in arithmetic width and modular reduction.

- **189** is a direct port. Python's lists of `int` become three `calloc`'d `long long` arrays
  that swap roles by pointer exchange, where Python rebinds `msg = nxt`. The base-3 key arithmetic
  (`key // place % 3`, clear a trit by subtracting `ui * place3`) is the same on both sides. The
  counts stay within 64 bits for 8 rows. They would not for much larger grids, which the Python
  side would absorb silently.
- **194** differs in two places. $S_A$ is around $3 \times 10^{16}$ at the problem's $c$, exact in
  Python and just inside `long long` in C, which is reduced $\bmod 10^8$ before `modpow`. The
  binomial is `math.comb` (exact, then reduced) in Python. C cannot divide modulo $10^8$, since
  $10^8 = 2^8 5^8$ has no inverses for the factors that matter, so it builds $\binom{a+b}{a}$ from
  one row of Pascal's triangle using additions only.
- **237** stores the recurrence's $-2$ as $10^8 - 2$ in C, so every matrix entry is a non-negative
  residue and every product stays below $10^{16}$. Python can keep the $-2$, because `%` on a
  negative `int` already returns a non-negative result.

## How to reason about it

- **Choose the cut first.** The method only works if the two sides of a cut interact through the
  state alone. For colourings that is the colours along the cut; for paths it is which positions
  are crossed *and* how the strands pair up. If you leave out part of the interaction, the counts
  come out plausible and wrong.
- **Estimate $s$ before you build anything.** $s^2$ entries to store, $s^3$ to multiply. If that is
  too much, either the matrix factors into local pieces (contract it, as 189 does), or a symmetry
  shrinks it (quotient by it, as 194 does), or you only need the sequence (fit the recurrence, as
  237 does).
- **Look for an invariant vector.** If the problem is symmetric under some group acting on the
  states (colour permutations, reflections), the vector constant on orbits is invariant and the
  matrix acts on the much smaller space of orbits. In the extreme case of 194 there is one orbit,
  and the matrix becomes a number.
- **A fitted recurrence needs a check beyond the fit.** Fit it on some small cases and verify it on
  more, as 237 does up to $n = 12$. The transfer-matrix argument bounds the order, which tells you
  how many terms the check needs.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ○ [0458](/solutions/0458/) — Permutations of Project
- ○ [0544](/solutions/0544/) — Chromatic Conundrum
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0767](/solutions/0767/) — Window into a Matrix II

<!-- /problems -->
