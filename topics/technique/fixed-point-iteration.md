<!-- tags: [fixed-point-iteration] -->
<!-- status: final -->
# Fixed-point iteration

Some problems define their answer in terms of itself. A number has to equal its own last nine
digits raised to a power. A real number has to reproduce its own decimal expansion. A table has to
agree with a recurrence that reads the same table. In each case solving for the unknown head-on is
hopeless or impossible, but *checking* a candidate is cheap. [Fixed-point
iteration](https://en.wikipedia.org/wiki/Fixed-point_iteration) turns that check into a solver:
write the condition as $x = f(x)$, start somewhere, and apply $f$ until $x$ stops changing. The
loop is the same three lines every time. What changes from problem to problem is the answer to
the one question that matters: why does it stop?

## The idea

A *fixed point* of a map $f$ is a value $x^\ast$ with $f(x^\ast) = x^\ast$. The iteration is

```python
x = seed
while (nxt := f(x)) != x:
    x = nxt
```

If the sequence $x, f(x), f(f(x)), \dots$ settles, the value it settles on satisfies the equation
by construction. You never solve anything; you replay the definition until it agrees with itself.
That is the attraction. The catch is that nothing in those three lines guarantees they finish, or
that the value they finish on is the one the problem asks for. Every correct use comes with a
reason the sequence converges. The three problems below each lean on a different one.

**A contraction: errors shrink each pass.** The textbook guarantee is the [Banach fixed-point
theorem](https://en.wikipedia.org/wiki/Banach_fixed-point_theorem). If $f$ brings any two points
closer together by at least a constant factor $k < 1$, it has exactly one fixed point, and
iterating from *any* seed reaches it, with the error shrinking by $k$ each pass. Problem 751 has
this shape. A seed $\theta$ drives a floor recurrence whose terms, concatenated, spell out a new
number $\tau$, and the problem wants the $\theta$ with $\tau = \theta$. The map $\theta \mapsto \tau$
is a contraction on the leading digits: changing $\theta$ far out in its expansion only moves
$\tau$ even further out. Each pass therefore locks in more of the front of the number, and from the
crude seed $\theta = 2$ a handful of passes pin down every digit the problem asks for. Nobody
writes $\theta$ in closed form. The iteration *is* the definition of the constant.

**A shrinking modulus: a discrete map that goes constant.** Problem 455 asks for $x$ with
$n^x \equiv x \pmod{10^9}$, where $x$ is both the exponent and the residue. Iterating
$x \leftarrow n^x \bmod 10^9$ from $x = 1$ builds the power tower $n, n^n, n^{n^n}, \dots$ reduced
mod $10^9$. Nothing is shrinking geometrically here, because there is no metric on residues worth
the name. The tower still goes eventually constant, for a number-theoretic reason. Once the exponent
is large, $n^a \bmod m$ depends only on $a$ modulo the [Carmichael function](/topics/technique/carmichael-function)
$\lambda(m)$. So the level below only matters mod $\lambda(m)$, the one below that mod
$\lambda(\lambda(m))$, and that chain of moduli falls to $1$ within a few steps. When the iteration
is run over every base at once, as a vectorised [modular
exponentiation](/topics/technique/modular-exponentiation), it settles in about a dozen rounds. The
alternative is a search over $10^9$ candidates per base.

**A well-founded recurrence: relaxation to the least fixed point.** Problem 214 needs the
totient-chain length $L(n) = 1 + L(\varphi(n))$, with $L(1) = 1$, for every $n$ below
$4 \times 10^7$. Read as an equation over the whole array, that is $L = F(L)$, where
$F(L)[n] = 1 + L[\varphi(n)]$. Start from zeros, apply $F$ to the entire array in one go, and repeat
until nothing changes. This is [relaxation](https://en.wikipedia.org/wiki/Relaxation_(iterative_method)),
the same move Bellman–Ford makes on edge weights. It terminates because $\varphi(n) < n$, so every
chain reaches $1$. Each pass makes one more link of every chain correct, which means the pass count
equals the longest chain length, about 26. A plain [dynamic program](/topics/technique/dynamic-programming)
filling the table in increasing $n$ would do it in one pass. The relaxation does 26 passes instead,
and each one is a single NumPy gather `1 + L[phi]` rather than forty million interpreted steps.
That is a good trade.

Those three cases cover most of what you will meet. Iteration on the reals converges because the
map contracts. Iteration on a finite set, such as residues or bounded integer tables, cannot shrink
an error, but it does not need to: it only has to stop producing *new* values, and a reason the map
reaches a stationary point (a well-founded order, a collapsing modulus chain) is enough. [Newton's
method](/topics/technique/newtons-method) belongs to the first family, as an iteration
$x \leftarrow x - g(x)/g'(x)$ engineered to contract fast. [Power
iteration](/topics/technique/power-iteration) is the same loop aimed at an eigenvector.

## How to reason about it

**Reach for it when the condition is self-referential and the forward direction is cheap.** The
tell is an unknown on both sides of the equation: as exponent and residue, as input and output
digits, as the table and the thing that indexes it. If evaluating $f$ is easy and inverting it is
not, iterate.

**Prove termination before you trust the loop.** "It converged on my test input" is not a reason.
Name the mechanism (contraction, a modulus chain, a strictly decreasing index) and you also learn
the iteration count, which is your complexity bound. Without one, the loop can cycle. The orbit of
a map on a finite set always ends up periodic, and a period-2 oscillation will spin `while nxt != x`
forever. Cap the iterations and fail loudly when the cap is hit.

**Know which fixed point you landed on.** Iteration finds *a* fixed point, the one the seed's
basin leads to. Problem 455 wants the *largest* solution, and the tower limit is only that if it is
the only one. I checked that against exhaustive search on scaled-down moduli ($10^3$ to $10^5$)
before trusting it. Relaxation from zeros, by contrast, reaches the *least* fixed point. That is
the right one for a recurrence that is defined by building up from a base case.

**Pick the stopping test to fit the domain.** On integers and residues, test exact equality with
the previous state; for an array, use `np.array_equal`, never a tolerance. On the reals, stop when
the digits you need have stopped moving. Problem 751 compares the first 40 digits after the point
between passes. A bare `abs(x - nxt) < eps` can quit early on a slowly converging map.

**Budget precision when the map amplifies error.** A contraction shrinks the *iteration's* error,
but evaluating $f$ can still magnify *rounding* error. In problem 751 each step of the floor
recurrence multiplies the fractional part by a growing integer, losing about one decimal digit per
term. A 24-digit answer therefore needs well over 24 digits of working precision. That rules out a
`float` and calls for `decimal` with generous headroom.

**Iterate the whole state at once when you can.** Because the update rule is the same everywhere,
fixed-point loops vectorise well. A million independent power towers, or a forty-million-entry
chain table, advance together in one array operation per pass. A few extra passes cost far less
than a per-element Python loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0214](/solutions/0214/) — Totient Chains
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ● [0751](/solutions/0751/) — Concatenation Coincidence

<!-- /problems -->
