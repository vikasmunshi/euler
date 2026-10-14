<!-- tags: [matrix-exponentiation] -->
<!-- status: final 2026-10-12T14:45Z -->
# Matrix exponentiation

Matrix exponentiation here means computing an integer power $M^n$ of a square matrix by
[repeated squaring](/topics/technique/exponentiation-by-squaring). (The tag's reference, the
[matrix exponential](https://en.wikipedia.org/wiki/Matrix_exponential) $e^M$, is a related but
different object.) The reason it matters: any process that advances a fixed-size state by the
same linear rule each step is one matrix multiplication per step, so $n$ steps are $M^n$. Squaring
reaches $M^n$ in about $2\log_2 n$ multiplications instead of $n$. So a question about the
$10^{12}$th board column, or an index of $1.2 \times 10^{10}$, costs a few dozen small matrix
products. Each problem below hides a linear step behind something else: Hamiltonian tours of a
narrow board, a two-variable function defined by mixed rules, a sequence that branches on the
parity of its index.

## The idea: one step is one multiply

Pick a state vector $v_k$ that holds everything the next step needs. If $v_{k+1} = M v_k$ for a
fixed matrix $M$, then $v_n = M^n v_0$. Squaring computes $M^n$ from the binary digits of $n$, by
the same loop as integer exponentiation but with matrix products:

```python
def mat_mul(A, B, mod):
    return [[sum(a * b for a, b in zip(row, col)) % mod for col in zip(*B)] for row in A]

def mat_pow(M, e, mod):
    R = [[int(i == j) for j in range(len(M))] for i in range(len(M))]
    while e:
        if e & 1:
            R = mat_mul(R, M, mod)
        M = mat_mul(M, M, mod)
        e >>= 1
    return R
```

For a $d \times d$ matrix that is $O(d^3 \log n)$ operations, with
`mat_pow([[1, 1], [1, 0]], n, mod)[0][1]` as the Fibonacci check. Three ways the problems arrive
at $M$:

- **A recurrence's companion matrix (Problem 237).** Counting tours of a $4 \times n$ board is a
  [transfer-matrix](/topics/domain/transfer-matrix-method) problem, and the counts satisfy a
  fourth-order recurrence. Stack the last four terms into $v_k$. The
  [companion matrix](https://en.wikipedia.org/wiki/Companion_matrix) carries the recurrence in its
  top row and shifts the history down with $1$s below the diagonal. About forty $4 \times 4$
  products reach $n = 10^{12}$. Finding the recurrence is covered under
  [small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence).
- **Two directions, two matrices (Problem 940).** The function $A(m, n)$ is linear in each index
  separately. So one $2 \times 2$ matrix advances $m$, another advances $n$, and every value is
  $e_1^{\mathsf T} N^{n} M^{m} e_2$. Because that expression is bilinear in the two powers, a double
  sum over pairs factors into $(\sum N^{f_j})(\sum M^{f_i})$, so the $k^2$ pairs are never formed.
- **A product chosen by the bits of the index (Problem 918).** The rule branches on the parity of
  the index, so the pair $(a_n, a_{n+1})$ maps to either child pair by one of *two* matrices.
  Reaching $a_m$ multiplies them in the order spelled by $m$'s binary digits. That is a
  product of different matrices rather than the power of one, and since matrix multiplication is
  not commutative, the order of the bits matters.

## Useful tricks around the power

- **Want one entry? Multiply a vector.** If only $v_n$ is needed, keep squaring $M$ but
  apply each needed $M^{2^k}$ to the vector, which is $O(d^2)$ per bit instead of a full product.
  Or take a single row of $M^n$ times the seed at the end. Problem 237 reads one
  component as a dot product of the power's top row with its seed.
- **Sums of powers with a block matrix.** $\begin{pmatrix} M & I \\ 0 & I \end{pmatrix}^{n}$ has
  $I + M + \dots + M^{n-1}$ in its top-right block. One power of a matrix twice the size gives a
  geometric sum of matrices, which is useful for running totals of a recurrence.
- **Exponents that follow a recurrence.** Powers of one matrix commute, so
  $M^{a+b} = M^a M^b$. When the exponents themselves form a sequence like the Fibonacci numbers in
  940, $M^{f_{i+1}} = M^{f_i} M^{f_{i-1}}$ produces each power from the previous two with a single
  product, which removes the $\log$ factor of computing each one from scratch.
- **Know when to stop using matrices.** For order $d$ in the hundreds or thousands, $d^3 \log n$
  is too much. Polynomial methods ($x^n$ modulo the characteristic polynomial, or Bostan–Mori)
  do the same job in $O(d^2 \log n)$ or better. See
  [linear recurrence with constant coefficients](/topics/technique/linear-recurrence-with-constant-coefficients).

## How to reason about it

- **Find the smallest state that makes the step linear.** Add a constant $1$ to the state to
  handle an affine term, a running total to get prefix sums, or two consecutive terms when the
  rule looks back two steps. The matrix size is the cost driver, so keep it minimal.
- **Reduce after every product, and mind the dot product's width.** A modulus below $2^{31}$ keeps
  each product below $2^{62}$, but a row of $d$ such products summed before reduction can reach
  $d \cdot 2^{62}$. Just two terms reach $2^{63}$, past the signed 64-bit limit. In C, reduce inside the
  dot product or accumulate in [`__int128`](/topics/technique/int128). Store negative coefficients
  as residues.
- **Seed and index carefully.** $v_n = M^{n-k} v_k$ for a seed at index $k$. Off-by-one errors in
  the exponent are the usual bug, so check the first few values against direct iteration.
- **Verify the closed matrix form on given values.** Problem 940's two-matrix form was checked
  against the statement's four values of $A(m, n)$ before the factorisation was trusted.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence

<!-- /problems -->
