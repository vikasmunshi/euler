<!-- tags: [lucas-number] -->
<!-- status: final 2026-10-30T06:35Z -->
# Lucas number

The [Lucas numbers](https://en.wikipedia.org/wiki/Lucas_number) $2, 1, 3, 4, 7, 11, 18, \dots$
obey the Fibonacci recurrence $L_n = L_{n-1} + L_{n-2}$ but start from $L_0 = 2$, $L_1 = 1$.
On their own they look like a curiosity, a Fibonacci sequence with the wrong seeds. They are
really the other half of the [Fibonacci sequence](/topics/domain/fibonacci-sequence): where
$F_n$ is the *difference* of the powers of the [golden ratio](/topics/domain/golden-ratio) and
its conjugate, $L_n$ is their *sum*, and most useful Fibonacci identities need both. That is why
they keep turning up. The problems below never set out to use Lucas numbers. One counts
constrained bit patterns on cycles (209), one does exact arithmetic in base $\varphi$ (473),
and one is handed a Lucas sequence as data (739). In each, recognising $L_n$ turns the problem
into arithmetic I already know how to do fast.

## The idea — the sum to Binet's difference

Let $\varphi = (1+\sqrt5)/2$ and $\psi = (1-\sqrt5)/2 = -1/\varphi$ be the two roots of
$x^2 = x + 1$. Any sequence $a\varphi^n + b\psi^n$ satisfies the Fibonacci recurrence, and the
two natural choices of $(a, b)$ give the two sequences:

$$F_n = \frac{\varphi^n - \psi^n}{\sqrt5}, \qquad L_n = \varphi^n + \psi^n.$$

The first is [Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Closed-form_expression).
The second is simpler, since it has no $\sqrt5$ to divide out, and it explains the most basic facts at
once. $L_n$ is an integer, because it is the sum of a conjugate pair. And since $|\psi^n| < 1/2$
for $n \ge 2$, $L_n$ is just $\varphi^n$ rounded to the nearest integer. Solving the two
equations for $\varphi^n$ gives the identity that does the most work:

$$\varphi^n = \frac{L_n + F_n\sqrt5}{2}, \qquad \psi^n = \frac{L_n - F_n\sqrt5}{2}.$$

So the pair $(L_n, F_n)$ *is* $\varphi^n$, written in the basis $\{1, \sqrt5\}$ with a factor of
one half. The same thing in matrix form: $Q = \begin{pmatrix}1&1\\1&0\end{pmatrix}$ has
eigenvalues $\varphi, \psi$, so $\operatorname{tr} Q^n = \varphi^n + \psi^n = L_n$. Fibonacci
numbers are the off-diagonal entries of $Q^n$, and Lucas numbers are its trace.

### The identities the solutions lean on

All of these follow by expanding the closed forms and using $\varphi\psi = -1$:

| identity | what it is for |
|---|---|
| $L_n = F_{n-1} + F_{n+1} = 2F_{n+1} - F_n$ | get $L_n$ from a Fibonacci pair |
| $L_n^2 - 5F_n^2 = 4(-1)^n$ | the norm of $\varphi^n$: a [Pell-type](/topics/technique/pells-equation) invariant |
| $F_{2n} = F_n L_n$, $\; L_{2n} = L_n^2 - 2(-1)^n$ | index doubling |
| $L_{m+n} = F_{n-1} L_m + F_n L_{m+1}$ | jump any distance from a known pair |
| $L_{-n} = (-1)^n L_n$, $\; F_{-n} = (-1)^{n+1} F_n$ | run the recurrence backwards |
| $\varphi^{-n} = (-1)^n (L_n - F_n\sqrt5)/2$ | negative powers, from $1/\varphi = -\psi$ |

The shift identity works for *every* sequence with the Fibonacci recurrence, not only for $L$:
any such sequence is determined by two consecutive terms, and $F$ supplies the coefficients.

### Why cycles count to Lucas numbers

The combinatorial reading is the one 209 needs. Colour the vertices of a
[cycle graph](/topics/domain/cycle-graph) $C_n$ with 0/1 and forbid two adjacent 1s. Each
valid colouring is an [independent set](/topics/domain/independent-set-graph-theory). The
allowed transitions between neighbouring colours form exactly the matrix $Q$ (0 may follow
anything, 1 may only follow 0). A valid colouring of the cycle is a closed walk of length $n$,
and the number of closed walks of length $n$ is $\operatorname{tr} Q^n = L_n$. On a *path*
the walk need not close, and the count is $F_{n+2}$. That is the general rule: Fibonacci counts
strings and Lucas counts necklaces. The trace form also gets the small cases right without
special handling. $L_1 = 1$ is a fixed point whose self-loop forces a 0, and $L_2 = 3$ is a
2-cycle that allows 00, 01 and 10. In 209 the truth-table constraint is defined along the edges
of a [non-linear feedback shift register](/topics/domain/nonlinear-feedback-shift-register).
That register is a permutation of the states, so the count factors over its cycles into a
product of Lucas numbers, one per cycle length.

## Fast computation

Three regimes come up, and each has its own tool.

- **All of $L_1, \dots, L_n$.** Just run the recurrence: $O(n)$ additions, exact in Python,
  or modulo $p$ in C. For 209 the cycle lengths are at most $2^k$, so a table is all it takes.
- **One $L_n$ for huge $n$, usually modulo $p$.** Use
  [fast doubling](/topics/technique/fibonacci-fast-doubling) to get $(F_n, F_{n+1})$ in
  $O(\log n)$ steps, then $L_n = 2F_{n+1} - F_n$. You can also double on $L$ directly
  with $L_{2n} = L_n^2 - 2(-1)^n$. This is the same algorithm as
  [matrix exponentiation](/topics/technique/matrix-exponentiation) of $Q$ with the redundant
  entries dropped:

  ```python
  def fib_pair(n):                      # (F_n, F_{n+1})
      if n == 0:
          return 0, 1
      a, b = fib_pair(n >> 1)
      c, d = a * (2 * b - a), a * a + b * b
      return (d, c + d) if n & 1 else (c, d)
  ```

- **A long run of terms starting deep in the sequence.** Combine the two: compute one start
  pair by doubling, then step. In 739 the repeated prefix-summing is linear, so the final term
  is a fixed [ballot-number](/topics/domain/catalan-number)-weighted sum of the starting terms,
  and the Lucas numbers are just the data being weighted. The sum is evaluated in chunks over
  $10^8$ indices, and its pairing of weights to terms wants the Lucas terms in *descending*
  order. So each chunk doubles to a start pair at its top, using
  $a_x = L_{x+1} = 2F_x + F_{x+1}$ for the problem's shifted indexing, and walks down with
  $L_{k-1} = L_{k+1} - L_k$. Running the recurrence backwards costs nothing extra, because
  subtraction undoes the addition exactly, modulo $p$ included. The vectorised Python version
  cannot step one term at a time. It uses the shift identity at negative offsets,
  $a_{x-t} = (-1)^t F_{t+1}\,a_x + (-1)^{t+1} F_t\,a_{x+1}$, to fill a whole row of a NumPy
  grid from one start pair and two precomputed coefficient vectors. That turns a sequential
  recurrence into an elementwise multiply-add.

## How to reason about it

- **Spot it from the seeds.** A sequence that satisfies $x_n = x_{n-1} + x_{n-2}$ is some
  combination $\alpha F_n + \beta L_n$. If the problem hands you $1, 3, 4, 7, \dots$ (739),
  that is $L_{n+1}$ with a shifted index. Write down the shift explicitly before using any
  identity. Off-by-one indexing ($L_0 = 2$ versus "the first term is 1") is the commonest bug.
- **Spot it from a trace.** When a count is "closed walks", "cyclic strings" or "states on a
  cycle" with a two-state transfer matrix equal to $Q$, the answer is $L_n$, not $F_n$.
- **Use $(L, F)$ as exact coordinates for $\mathbb{Z}[\varphi]$.** Any element can be written as
  $(a + b\sqrt5)/2$ with $a \equiv b \pmod 2$. Powers of $\varphi$ are $(L_n, F_n)$, and
  negative powers come from the conjugate with a sign. 473 sums mirrored pairs
  $\varphi^k + \varphi^{-(k+1)}$ in exactly these coordinates and tests "is this an integer?"
  as "is the $\sqrt5$ coefficient exactly zero?". That is an
  [exact-arithmetic](/topics/takeaway/exact-arithmetic-for-equality) test, and floating point
  could not make it reliably.
- **Do not evaluate the closed form numerically past small $n$.** $\varphi^n$ in a double
  has about 53 bits of precision, so rounding gives the wrong $L_n$ beyond roughly $n = 70$. The
  closed form is for *deriving* identities. Compute with integer recurrences, doubling, or
  the $(a, b)$ pair.
- **Mind the sizes.** $L_n \approx \varphi^n$ grows by about 0.21 decimal digits per step.
  Products of Lucas numbers (209) and sums of them (473) overflow 64 bits quickly, which is why
  the C ports of both reach for [`__int128`](/topics/technique/int128). Under a prime modulus
  (739) every identity above holds unchanged, with $(-1)^n$ and the halving taken modulo $p$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0209](/solutions/0209/) — Circular Logic
- ● [0473](/solutions/0473/) — Phigital Number Base
- ● [0739](/solutions/0739/) — Summation of Summations

<!-- /problems -->
