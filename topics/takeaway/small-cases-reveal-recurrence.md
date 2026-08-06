<!-- tags: [small-cases-reveal-recurrence] -->
<!-- status: final -->
# Small cases reveal the recurrence

Some counting problems admit no formula worth deriving, yet the object being
counted is assembled by repeating one fixed local step — another column glued to
a board, another rung of a ladder of solutions. Whenever that is true, the counts
obey a
[linear recurrence with constant coefficients](https://en.wikipedia.org/wiki/Linear_recurrence_with_constant_coefficients)
*before you know a single coefficient*: the structure guarantees the shape, and
the small cases hand you the numbers. The move is a four-step one — brute-force
the small instances, fit a recurrence to them, confirm it on terms held back from
the fit, then jump to an astronomical index by
[matrix power](https://en.wikipedia.org/wiki/Matrix_multiplication#Powers_of_a_matrix).
It is how [Tours on a $4 \times N$ Playing Board](/solutions/0237/) answers a
question about a board $10^{12}$ columns wide having never enumerated anything
past a dozen.

## Why a recurrence has to be there

The guarantee is structural, and it is worth internalising separately from any
particular fit. Suppose the objects of size $n$ are built left to right and the
only thing the finished right-hand part needs to know about the left-hand part is
which of a **finite** set of boundary states the cut is in. Then adding one more
unit is a fixed linear map on the vector of per-state counts — a
[transfer matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) $A$ that
does not depend on $n$. The count you want is a fixed linear functional of
$A^{n} v_0$, and by the
[Cayley–Hamilton theorem](https://en.wikipedia.org/wiki/Cayley%E2%80%93Hamilton_theorem)
$A$ satisfies its own characteristic polynomial, so *every* such sequence satisfies
a linear recurrence of order at most the number of boundary states.

Problem 237 is the clean case. Counting
[Hamiltonian paths](https://en.wikipedia.org/wiki/Hamiltonian_path) is
[#P-complete](https://en.wikipedia.org/wiki/Sharp-P-complete) in general, but the
board is only four squares tall while $n$ runs to $10^{12}$. Cut it after column
$j$: all the left part can still contribute is which of the four horizontal edges
across the cut are used and how the fragments already laid down pair those
crossings with one another. A handful of states, hence a linear recurrence of
small order — a fact you can assert from the geometry alone, without ever writing
down the transfer matrix or its entries. Deriving those entries by hand is a
fiddly case analysis over path pairings; fitting them from data is an afternoon's
arithmetic. That asymmetry is the whole reason this takeaway is a takeaway.

## Fit, confirm, jump

**Get the small terms honestly.** The brute force is the oracle, so it has to be
right rather than fast — but it does have to finish, and search over a $4 \times
12$ board dies without help. Problem 237's scratch enumerator walks a
[depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) over a
visited [bitmask](https://en.wikipedia.org/wiki/Bit_array) and prunes with two
*necessary* conditions on the remaining graph: a
[flood fill](https://en.wikipedia.org/wiki/Flood_fill) from the walker rejects any
state that has stranded an unvisited square, and a degree check rejects any state
where some unvisited square no longer has the two free neighbours it needs to be
entered and left. Both only ever discard positions with no completion, so the
counts stay exact — and that distinction is the one to police, because a pruning
that is merely *plausible* corrupts the data the whole fit rests on.

**Fit.** For order $d$ the ansatz $s_k = \sum_{i=1}^{d} c_i \, s_{k-i}$ is a
linear system: $d$ unknowns, one equation per known term. Take $d$ equations to
solve for the coefficients, and solve them in **exact** arithmetic —
`fractions.Fraction` or integer elimination. Floating-point elimination will hand
back `1.9999999999997` where the truth is $2$, and you will not know whether that
is rounding or a wrong order. If the sequence is recognisable at all, try
[OEIS](https://oeis.org/) first: it often names the recurrence, the generating
function and the combinatorial identity in one lookup.
[Berlekamp–Massey](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm)
finds the minimal order directly if you would rather not sweep $d$ upwards.

**Confirm on data the fit never saw.** A recurrence reproducing the terms used to
derive it has told you nothing — the system was solved to make that true. Fitting
order $d$ consumes $2d$ terms (the $d$ equations each reach $d$ back); every term
beyond that is a real test. Problem 237's brute force generates enough of them to
fit its fourth-order recurrence and still have terms in reserve, and the given
$T(10) = 2329$ is one more independent check. Verification is cheaper to write
than the fit:

```python
def holds(seq, coeffs):
    d = len(coeffs)
    return all(seq[k] == sum(c * seq[k - 1 - i] for i, c in enumerate(coeffs))
               for k in range(d, len(seq)))
```

**Jump.** Stepping the recurrence is $O(n)$ and hopeless at $n = 10^{12}$. Stack
the last $d$ terms into $v_k = (s_k, s_{k-1}, \dots, s_{k-d+1})$ and the
recurrence becomes one
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix):

$$M = \begin{pmatrix} c_1 & c_2 & \cdots & c_{d-1} & c_d \\ 1 & 0 & \cdots & 0 & 0 \\ 0 & 1 & \cdots & 0 & 0 \\ \vdots & & \ddots & & \vdots \\ 0 & 0 & \cdots & 1 & 0 \end{pmatrix}, \qquad M v_k = v_{k+1},$$

whose top row *is* the recurrence while the subdiagonal $1$s shift the history
down. Then $v_n = M^{\,n-d} v_d$, and
[exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring)
advances $2^k$ indices per squaring: $O(d^3 \log n)$ operations, about forty
$4 \times 4$ multiplications for $n = 10^{12}$. Problem 237 wants one component of
the result, so the last step collapses to a single dot product of $M$'s power's
top row with the seed. The same lever drives
[Recursive Sequence Summation](/solutions/0918/) and other problems whose index is
too large to walk to.

The payoff shape shows up without the matrix, too, once $d$ is tiny and the number
of terms wanted is small. [Almost Equilateral Triangles](/solutions/0094/) is
public and worth reading whole: the integral-area condition collapses to a
[Pell equation](https://en.wikipedia.org/wiki/Pell%27s_equation), whose solutions —
scattered as they look when you tabulate the first few by search — advance by a
fixed linear update, so generating them replaces searching for them:

```python
s, s1, s2, m, p = (0, 1, 1, 1, 0)
while p <= max_perimeter:
    s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
    p = 3 * s2 - m
```

Sides grow roughly fourfold per step, so fewer than twenty triangles exist below a
billion and the loop is $O(\log N)$ — an exhaustive scan turned into a walk along
the answers themselves.

## How to reason about it

Reach for this when the parameter you are pushing to infinity enters as **repeated
identical structure**: a strip of constant width, a tiling or colouring scanned
column by column, walks of length $n$ on a fixed graph, an
[integer sequence](https://en.wikipedia.org/wiki/Integer_sequence) generated by a
fixed algebraic ladder. The tell is that you can describe a cut, and the amount of
information crossing it is bounded independently of $n$. When the boundary state
grows with $n$ — a strip whose *width* is the parameter, a rule whose coefficients
depend on the index — no constant-coefficient recurrence exists; the sequence may
still be
[holonomic](https://en.wikipedia.org/wiki/Holonomic_function) (polynomial
coefficients), which is a different and heavier tool, and it may be nothing at
all. The step-change here is $O(n) \to O(\log n)$, the same kind of shape change
that [preferring a closed form over iteration](/topics/takeaway/closed-form-over-iteration)
buys, reached by measurement rather than by derivation.

Four cautions earn their keep:

- **Justify the order structurally, fit only the numbers.** Counting the boundary
  states gives an upper bound on $d$ *before* any data, which turns "this pattern
  seems to hold" into "a recurrence of order $\le d$ must exist, and here are its
  coefficients". Without that argument you have a numerical coincidence, and
  overfitting is easy: a high enough order will match any prefix.
- **Prefer the smallest order that both fits and confirms.** If order $d$ works,
  every larger order works too, with a system that is now singular. Sweep upwards
  and stop at the first fit that survives held-back terms.
- **Watch the boundary.** Recurrences frequently only hold from some index on, the
  small cases being genuinely special. Seed the matrix from an index you have
  verified rather than from the first term you happen to have, and answer any
  input below that seed straight from the table.
- **Reduce late, and mind the width.** Fit over the integers or rationals; only at
  evaluation time reduce modulo whatever the problem asks. A negative coefficient
  is fine under a modulus — the residues form a ring — but in C it must be *stored*
  as its residue so every product stays inside the word (see
  [watch integer width](/topics/takeaway/watch-integer-width)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board

<!-- /problems -->
