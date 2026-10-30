<!-- tags: [small-cases-reveal-recurrence] -->
<!-- status: final 2026-10-15T11:04Z -->
# Small cases reveal the recurrence

Some counting problems admit no formula worth deriving, yet the object being
counted is assembled by repeating one fixed local step — another column glued to
a board, another digit appended to a number, another rung of a ladder of
solutions. Whenever that is true, the counts obey a
[linear recurrence with constant coefficients](https://en.wikipedia.org/wiki/Linear_recurrence_with_constant_coefficients)
*before you know a single coefficient*: the structure guarantees the shape, and
the small cases hand you the numbers. The move has four steps. Brute-force the
small instances, fit a recurrence to them, confirm it on terms held back from the
fit, then jump to an astronomical index. It is how
[Tours on a $4 \times N$ Playing Board](/solutions/0237/) answers a question about
a board $10^{12}$ columns wide without enumerating anything past a dozen columns,
and how [$10$-substrings](/solutions/0529/) reaches numbers $10^{18}$ digits long
through a recurrence of order $2772$ that nobody could derive by hand.

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
a linear recurrence of order at most the number of boundary states. A running
total $\sum_{k \le n} s_k$ adds at most one to that order.

Problem 237 is the clean case. Counting
[Hamiltonian paths](https://en.wikipedia.org/wiki/Hamiltonian_path) is
[#P-complete](https://en.wikipedia.org/wiki/Sharp-P-complete) in general, but the
board is only four squares tall while $n$ runs to $10^{12}$. Cut it after column
$j$. All the left part can still contribute is which of the four horizontal edges
across the cut are used and how the fragments already laid down pair those
crossings with one another. That is a handful of states, hence a linear
recurrence of small order. You can assert this from the geometry alone, without
ever writing down the transfer matrix or its entries. Deriving those entries by
hand is a fiddly case analysis over path pairings; fitting them from data is an
afternoon's arithmetic. That asymmetry is the whole reason this takeaway is a
takeaway.

Problem 529 shows the same argument at a scale where the transfer matrix exists
but is useless. A number is "friendly" when every digit lies in a run of
consecutive digits summing to $10$. Read left to right, the only memory needed is
the set of suffix sums still $\le 10$ (an $11$-bit mask) and the sum since the
earliest digit not yet covered. That makes it a
[finite automaton](https://en.wikipedia.org/wiki/Deterministic_finite_automaton)
with $5630$ reachable states. Cubing a matrix that size sixty times is out of
the question. But the automaton still bounds the recurrence order, and
[minimising it](https://en.wikipedia.org/wiki/DFA_minimization) tightens the
bound to $2816$ states. So $2 \cdot 2817$ terms of the running total, produced by
an ordinary [digit DP](/topics/technique/digit-dp), are *provably* enough to pin
the recurrence down. The automaton is never exponentiated. Its only job is to
say how many small cases to compute.

## Fit, confirm, jump

**Get the small terms honestly.** The brute force is the oracle, so it has to be
right rather than fast. It does have to finish, though, and search over a
$4 \times 12$ board dies without help. Problem 237's scratch enumerator walks a
[depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) over a
visited [bitmask](https://en.wikipedia.org/wiki/Bit_array) and prunes with two
*necessary* conditions on the remaining graph. A
[flood fill](https://en.wikipedia.org/wiki/Flood_fill) from the walker rejects any
state that has stranded an unvisited square. A degree check rejects any state
where some unvisited square no longer has the two free neighbours it needs to be
entered and left. Both only ever discard positions with no completion, so the
counts stay exact. That distinction is the one to police, because a pruning that
is merely *plausible* corrupts the data the whole fit rests on. When the oracle
is itself a clever DP, as in 529, check it against something dumber first: 529's
DP was compared with a plain scan of every number up to $10^5$ before any term
was fed to the fit.

**Fit.** For order $d$ the ansatz $s_k = \sum_{i=1}^{d} c_i \, s_{k-i}$ is a
linear system: $d$ unknowns, one equation per known term. Solve it in **exact**
arithmetic. Floating-point elimination will hand back `1.9999999999997` where the
truth is $2$, and you will not know whether that is rounding or a wrong order.
"Exact" has two good meanings here. Over the rationals (`fractions.Fraction`, or
integer elimination) you get the true coefficients. Over a prime field you get
them modulo $p$. The second is all you need when the problem asks for an answer
mod a prime, and it is the only practical choice once $d$ runs to thousands and
rational coefficients swell. If the sequence is recognisable at all, try
[OEIS](https://oeis.org/) first: it often names the recurrence, the generating
function and the combinatorial identity in one lookup. Otherwise
[Berlekamp–Massey](/topics/technique/berlekamp-massey-algorithm) finds the
minimal order directly, in $O(d^2)$, instead of sweeping $d$ upwards. It divides
by discrepancies, so it needs a field. Problem 529 runs it modulo $10^9+7$ and
gets order $2772$, just under the $2817$ bound.

**Confirm on data the fit never saw.** A recurrence reproducing the terms used to
derive it has told you nothing, because the system was solved to make that true.
Fitting order $d$ consumes $2d$ terms (the $d$ equations each reach $d$ back), and
every term beyond that is a real test. Problem 237's brute force generates enough
of them to fit its fourth-order recurrence and still have terms in reserve, and
the given $T(10) = 2329$ is one more independent check. Problem 529 checks its
recurrence against the direct DP out to $n = 9000$, far past the fitted prefix.
That is belt-and-braces there, since the automaton bound already makes the fit a
proof. Verification is cheaper to write than the fit:

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

$$M = \begin{pmatrix} c_1 & c_2 & \cdots & c_{d-1} & c_d \\ 1 & 0 & \cdots & 0 & 0 \\ 0 & 1 & \cdots & 0 & 0 \\ \vdots & & \ddots & & \vdots \\ 0 & 0 & \cdots & 1 & 0 \end{pmatrix}, \qquad M v_k = v_{k+1}.$$

The top row *is* the recurrence, and the subdiagonal $1$s shift the history down.
Then $v_n = M^{\,n-d} v_d$, and
[exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring)
advances $2^k$ indices per squaring. That costs $O(d^3 \log n)$ operations: about
forty $4 \times 4$ multiplications for $n = 10^{12}$. Problem 237 wants one
component of the result, so the last step collapses to a single dot product of
the top row of the matrix power with the seed. The same lever, under its
[matrix exponentiation](/topics/technique/matrix-exponentiation) name, drives
[Recursive Sequence Summation](/solutions/0918/) and other problems whose index is
too large to walk to.

The cube in that cost is what breaks at large order: $2772^3$ per squaring is
already about $2 \times 10^{10}$. Treat the recurrence as a polynomial problem
instead. A sequence with a recurrence of order $d$ has a rational
[generating function](https://en.wikipedia.org/wiki/Generating_function)
$P(x)/Q(x)$, where $Q = 1 - c_1x - \dots - c_dx^d$ is exactly what
Berlekamp–Massey returns, and $P$ is the first $d$ terms of $S \cdot Q$. The
Bostan–Mori step extracts one coefficient of $P/Q$. Multiply top and bottom by
$Q(-x)$: the denominator becomes even, so only numerator coefficients of the
target index's parity survive, and the index halves.

```python
while k:                                   # find [x^k] P(x) / Q(x)
    Qm = [-c if i % 2 else c for i, c in enumerate(Q)]          # Q(-x)
    P, Q, k = mul(P, Qm)[k % 2::2], mul(Q, Qm)[::2], k // 2
```

Each round is two polynomial products, so the cost is $O(M(d)\log n)$ rather than
$O(d^3 \log n)$, where $M(d)$ is the cost of one product: $d^2$ schoolbook, or
$d \log d$ by FFT. Problem 529 uses it with both kinds of product. Its Python
runs FFT products, splitting each residue into $10$-bit limbs so that no
convolution coefficient outgrows a double's mantissa. Its C runs schoolbook
products and computes only the parity class each round keeps. Either way the jump
to $10^{18}$ is a small part of the run. Most of the time goes on building the
automaton, running the DP and fitting, and none of that depends on $n$.

The jump can also disappear. When the characteristic polynomial factors over the
integers, the recurrence is a sum of geometric terms and you can write it down.
[Point Genesis](/solutions/0957/) fits an order-five recurrence whose
characteristic polynomial is $(x-4)(x-2)(x+2)(x-1)(x+1)$. Its solution
evaluates the resulting closed form instead of iterating anything. That route
belongs to the sibling takeaway,
[small cases reveal the closed form](/topics/takeaway/small-cases-reveal-closed-form).

The payoff shape shows up without the matrix too, when $d$ is tiny and only a
few terms are wanted. [Almost Equilateral Triangles](/solutions/0094/) is public
and worth reading whole. The integral-area condition collapses to a
[Pell equation](https://en.wikipedia.org/wiki/Pell%27s_equation), whose solutions
look scattered when you tabulate the first few by search but advance by a fixed
linear update. Generating them replaces searching for them:

```python
s, s1, s2, m, p = (0, 1, 1, 1, 0)
while p <= max_perimeter:
    s, s1, s2, m = (s + p, s2, 4 * s2 - s1 + 2 * m, -m)
    p = 3 * s2 - m
```

Sides grow roughly fourfold per step, so fewer than twenty triangles exist below a
billion and the loop is $O(\log N)$. An exhaustive scan has become a walk along
the answers themselves.

## When the small cases reveal the rule

Sometimes the brute force does not hand you numbers to fit at all. It confirms
*what is being counted*, and the left-to-right structure is then simple enough to
write down by hand. In [Overtakes](/solutions/0996/), players on a leader board
swap adjacent ranks and must all end where they started. The question is how many
tuples of per-player overtake counts are possible. A conjectured description of
the possible tuples is checked against a breadth-first search over every board
up to seven players. A player with zero overtakes is a wall nobody crosses. The
positive counts between walls form runs of length at least two, each with an
even sum and no entry above half the sum. The brute-force sets and the
conjectured sets agree exactly.

Once the rule is known, the walls are the cut. Scanning positions left to right,
the boundary state is just "after a wall, in a run of length one, or in a longer
run", plus the parity and half-sum bookkeeping. That is six states, the same
finite-cut argument as 237, with one twist. Each state carries a polynomial in
$y$, where $y$ marks the total overtake count, instead of a single number. So the
second parameter $k \approx 4.6 \times 10^6$ is folded into a
[generating function](https://en.wikipedia.org/wiki/Generating_function) and never
iterated over. Fitting would have been the wrong tool here. The transfer is
small enough to derive, and the open question was the rule, not the
coefficients.

## How to reason about it

Reach for this when the parameter you are pushing to infinity enters as **repeated
identical structure**. Examples are a strip of constant width, a tiling or
colouring scanned column by column, a number scanned digit by digit, walks of
length $n$ on a fixed graph, or an
[integer sequence](https://en.wikipedia.org/wiki/Integer_sequence) generated by a
fixed algebraic ladder. The tell is that you can describe a cut, and the amount
of information crossing it is bounded independently of $n$. The number of states
at that cut then decides the tactic:

| States at the cut | Tactic | Example |
|---|---|---|
| a few, easy to derive | write the transfer by hand | 996 |
| a few, fiddly to derive | fit a small recurrence, jump by companion matrix | 237 |
| thousands, machine-built | bound the order by minimisation, Berlekamp–Massey, Bostan–Mori | 529 |
| no finite-state argument | fit anyway, but only held-back terms vouch for it | 957 |

When the boundary state grows with $n$, as in a strip whose *width* is the
parameter or a rule whose coefficients depend on the index, no
constant-coefficient recurrence exists. The sequence may still be
[holonomic](https://en.wikipedia.org/wiki/Holonomic_function) (polynomial
coefficients), which is a different and heavier tool, and it may be nothing at
all. The step-change here is $O(n) \to O(\log n)$, the same kind of shape change
that [preferring a closed form over iteration](/topics/takeaway/closed-form-over-iteration)
buys, reached by measurement rather than by derivation.

Four cautions earn their keep:

- **Justify the order structurally, fit only the numbers.** Counting the boundary
  states gives an upper bound on $d$ *before* any data. That turns "this pattern
  seems to hold" into "a recurrence of order $\le d$ must exist, and here are its
  coefficients". In 529 the bound is exact enough to say how many terms to
  generate, so the fit is a proof. Without a bound you have a numerical
  coincidence, and overfitting is easy: a high enough order will match any
  prefix. 957 has no such bound. Its sets grow fourfold a day, so only thirteen
  days could be simulated, ten of them fixed an order-five fit, and just three
  were left to confirm it. That is enough to ship, but it is evidence, not proof.
  Earn every held-back term you can. It also helps to subtract the part you
  already understand: 957 fits the residual after removing the dominant
  $\tfrac{7}{12}$-of-the-square growth, and that residual shows a low-order
  recurrence the raw counts did not.
- **Prefer the smallest order that both fits and confirms.** If order $d$ works,
  every larger order works too, with a system that is now singular. Sweep upwards
  and stop at the first fit that survives held-back terms. Berlekamp–Massey does
  this sweep for you.
- **Watch the boundary.** Recurrences often hold only from some index on, because
  the small cases are genuinely special. Seed the jump from an index you have
  verified rather than from the first term you happen to have. Answer any input
  below that seed straight from the table.
- **Reduce late or reduce in a field, and mind the width.** Fit over the integers
  or rationals and reduce only at evaluation time, or do everything modulo a
  *prime*. A composite modulus breaks Berlekamp–Massey's divisions. A negative
  coefficient is fine under a modulus, since the residues form a ring, but in C it
  must be *stored* as its residue so every product stays inside the word. The
  same width concern is why 529 splits residues into limbs before an FFT product
  (see [watch integer width](/topics/takeaway/watch-integer-width)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ● [0957](/solutions/0957/) — Point Genesis
- ● [0996](/solutions/0996/) — Overtakes

<!-- /problems -->
