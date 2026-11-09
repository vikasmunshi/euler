<!-- tags: [recurrence-relation] -->
<!-- status: final 2026-11-04T08:10Z -->
# Recurrence relation

A [recurrence relation](https://en.wikipedia.org/wiki/Recurrence_relation) defines each term of a
sequence from the terms before it: $a_n = F(a_{n-1}, \dots, a_{n-d})$, plus enough seed values to
get started. It is the fourth-largest domain tag in this collection, and that is not an accident of
taste — a recurrence is what you get whenever an object of size $n$ is *assembled* from smaller
objects of the same kind, and most counting, probability and dynamics questions are exactly that.
The recurrence itself is almost never the hard part. Finding it is a paragraph of reasoning;
**evaluating it at the index the problem actually asks about** is the work.

## Where they come from

Four decompositions account for nearly every recurrence below, and it is worth being able to name
them, because recognising the shape is what tells you which one to write down.

- **Condition on the last piece.** Classify every complete object by its final move, then remove
  that move. A row of length $i$ tiled with tiles of length $1..4$ ends in exactly one of four ways,
  so $\text{dp}[i] = \text{dp}[i-1] + \text{dp}[i-2] + \text{dp}[i-3] + \text{dp}[i-4]$ — problem
  117, tetranacci by another name. The classification has to *partition* the objects: every tiling
  falls in exactly one case, which is what makes the counts add without double-counting. This is
  [optimal substructure](/blogs/domain/optimal-substructure) stated concretely, and the tiling
  family (114, 115, 116, 117) is the cleanest place to see it.
- **Condition on the first step.** In a probabilistic process, write the unknown at a state in terms
  of the unknowns at the states one step away. Problem 227's expected hitting time gives
  $E_i = 1 + \sum_D P(D)\, E_{(i+D) \bmod n}$, and problem 938's absorption probability gives a
  two-term mixture of its two neighbours. Note the difference in what you then do with it: the
  first is a *cyclic* dependency and becomes a [system of linear
  equations](/blogs/technique/system-of-linear-equations); the second is acyclic and becomes a
  [dynamic programming](/blogs/technique/dynamic-programming) sweep. The state is often far
  smaller than the process suggests. Problem 605's round-robin coin-tossing game seems to need
  every player's history, but a player can only win twice running in the round they share with
  the previous winner. One bit remains: did last round's winner carry over? That makes a two-state
  [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) whose survival probabilities obey a
  first-order recurrence, solved exactly by $a_t = t/2^t$. Before you write the recurrence, ask
  what the next step actually reads.
- **Self-similar construction.** When the object is *defined* recursively, the recurrence is handed
  to you and the only question is how to query it. Problem 230's strings satisfy
  $T_k = T_{k-2}T_{k-1}$, so the *lengths* satisfy Fibonacci and a digit position can be chased down
  through the concatenations without ever materialising a string; problem 872's trees are built by
  one reparenting rule per step. The lesson generalises: recur on the **cheap shadow** of the
  structure (lengths, counts, a state index), never on the structure itself. Problem 943 hides
  the recurrence one level deeper: its sequence is
  [its own run-length encoding](https://en.wikipedia.org/wiki/Kolakoski_sequence), a definition
  with no index arithmetic in it at all. Read it backwards, though, and every element is the
  *parent* of the run it describes. The prefix is then the leaf level of a derivation tree only
  logarithmically tall, and a prefix sum becomes one root-to-leaf descent that banks every whole
  subtree to its left. This is 230's digit chase again, with the tree made explicit. Problem 341's
  [Golomb sequence](https://en.wikipedia.org/wiki/Golomb_sequence) is the same kind of
  self-description, taken a different way. There, $G(n)$ is how many times $n$ occurs. Its prefix
  sum $S(v)$ is the last position that holds the value $v$, so a question about a *position* turns
  into a question about a far smaller *value*. And the inversion can be repeated: one level up,
  $\sum t\,G(t)$ locates where $G(G(n))$ changes. Three inversions take positions near $10^{18}$
  down to a table of a few tens of thousands of block ends. Within a block the sums are
  quadratics, which a single square root solves. Each level shrinks the index by roughly a power
  $\varphi - 1$, so a handful of levels is enough. Problem 698
  is the shallow end of the same pool: a 123-number is one whose digit *counts* are 0 or
  themselves 123-numbers, and since a count never exceeds the length, membership at length $L$
  depends only on the members below $L$. The set grows bottom-up and is tiny, so the
  self-reference costs nothing.
- **An algebraic ladder.** Solutions to a [Pell equation](/blogs/technique/pells-equation), or
  convergents of a [continued fraction](/blogs/domain/continued-fraction), advance by a fixed
  linear update. Problems 94, 140 and 65 all turn a search over candidates into a walk along the
  answers. The same algebra produces a recurrence where none was asked for. If $x$ and $y$ are
  the two roots of an integer quadratic, the power sums $S_n = x^n + y^n$ are integers obeying
  $S_n = (x+y)S_{n-1} - xy\,S_{n-2}$. Problem 721 wants $\lfloor x^n \rfloor$ for a quadratic
  irrational $x$ whose conjugate lies in $[0, 1)$, so the floor is just $S_n - 1$. A real number
  with trillions of digits becomes an integer recurrence that can be reduced mod $p$.

Sometimes you cannot see the decomposition at all, and the counts still obey a recurrence for
structural reasons. That case has its own page —
[small cases reveal the recurrence](/blogs/takeaway/small-cases-reveal-recurrence) — and the move
there is to brute-force the small terms and fit the coefficients rather than derive them.

## Evaluating it without paying $O(n)$

A recurrence read literally is a recipe for $n$ steps. Whether that is acceptable depends entirely
on the index in the statement, and the statements here are usually chosen so it is not.

**Iterate forward, with a window.** The honest baseline: $O(n)$ time, and $O(d)$ — not $O(n)$ —
memory, because only the last $d$ terms are ever read. Prefer this to top-down
[recursion](/blogs/technique/recursion-computer-science) whenever the index tree is dense: naive
recursion on a two-term recurrence is exponential, and even with
[memoization](/blogs/technique/memoization) you pay call overhead and risk a stack limit. Keep
the table sized to the input and built inside `solve()` — a module-level table is
[precomputation that hides from the benchmark](/blogs/takeaway/precompute-once-reuse).

Problem 2 is the miniature that makes the point that *which* sequence you recur on is a choice.
Every third Fibonacci number is even, and the even ones satisfy a recurrence of their own,
$E_{k+1} = 4E_k + E_{k-1}$, so the filter disappears into the generator:

```python
def _even_fibonacci_numbers() -> typing.Generator[int, None, None]:
    """Yield successive even Fibonacci numbers below max_limit."""
    even_fib_a, even_fib_b = (2, 8)
    while even_fib_a < max_limit:
        yield even_fib_a
        even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)
```

That is the whole of `solutions/public/p0002/` — two state variables, no array, no test for
evenness. Re-indexing to the subsequence you actually want is the cheapest optimisation in this
whole topic, and the one most often missed.

**Jump by matrix power.** If the recurrence is
[linear with constant coefficients](/blogs/technique/linear-recurrence-with-constant-coefficients),
stacking the last $d$ terms into a vector turns one step into a fixed
[companion matrix](https://en.wikipedia.org/wiki/Companion_matrix), and $n$ steps into
$M^n$ — computable by
[exponentiation by squaring](/blogs/technique/exponentiation-by-squaring) in $O(d^3 \log n)$.
This is the standard escape when the index is $10^{12}$ or worse, and it composes: problem 940's
two-variable $A(m,n)$ is a product of *two* transfer matrices, one advancing rows and one advancing
columns, which additionally lets a double sum factor into a product of two accumulated sums instead
of an $O(k^2)$ pairing. See [matrix exponentiation](/blogs/technique/matrix-exponentiation) for the
mechanics. The cost is cubic in the state count, so shrink the state before you exponentiate.
Problem 670's coloured $2 \times n$ strip naively needs over a hundred boundary states (a colour
and an overhang per row). Its counts are symmetric under permuting the four colours, though, so
only *how many* colours a new tile may take matters. Fold that number into the matrix weights and
ten states remain, which makes each multiply roughly a thousand times cheaper. Problem 721's quadratic
ring $\mathbb{Z}_p[\sqrt a]$ is the $2 \times 2$ case of the same thing in disguise: squaring
$u + v\sqrt a$ is one step of the companion matrix, written as a pair.

**Descend the binary representation.** A recurrence whose arguments are $2n$ and $2n+1$ rather than
$n-1$ and $n-2$ is not slow at all — it is $O(\log n)$, because each step halves the index. The
catch is that the branches usually need *two* neighbouring values, so carry a pair (or a short
vector) and read the bits of $m$ from the top down, applying one linear map per bit:

```python
lo, hi = seed                      # (a(1), a(2)), say
for bit in bin(m)[3:]:             # skip "0b1": the leading bit is the seed
    lo, hi = even_map(lo, hi) if bit == "0" else odd_map(lo, hi)
```

Problems 169 and 918 are both this shape, and problem 872's climb up a tree is its bitwise cousin —
each step clears the top bit of a gap, so the loop runs
[popcount](https://en.wikipedia.org/wiki/Hamming_weight) times. Halving survives summation,
too. Problem 463's $f$, whose rules send $4n+1$ and $4n+3$ back to $n$ and $2n+1$, turns out to
be binary reversal, but the solution never uses that. It splits the prefix sum
$S(n) = \sum_{i \le n} f(i)$ by parity. That needs a companion sum over the odd indices, and then
each of the two sums is a linear combination of both at $\lfloor n/2 \rfloor$ and its neighbour.
The *sum* of a halving recurrence is itself a halving recurrence, provided you carry enough
companion sums to close the system. The branching is four-way, so memoise: unmemoised it is
exponential, memoised it touches about a hundred states for $n \approx 4.5 \times 10^{17}$.
Problem 539 shows when the memo can go. Its elimination game is self-similar only up to a
reflection: one sweep leaves the even numbers, and the next sweep runs the other way, so the
remainder is the same game on $M = \lfloor n/2 \rfloor$ items read backwards. The recurrence has
to carry that mirror, $P(n) = 2\bigl(M + 1 - P(M)\bigr)$. Since $P(n)$ reads only
$\lfloor n/2 \rfloor$, the indices $2m$ and $2m + 1$ contribute the same term, and
[summing the recurrence](/blogs/technique/recurrence-relation-application) closes the pair
$(P, S)$ on one unbranched chain of halvings.

**Exploit a finite state space.** If the state that advances the recurrence lives in a finite set,
the orbit must eventually repeat, and the sequence is
[eventually periodic](/blogs/domain/periodic-sequence). Then a huge index costs only the length of
the tail plus the cycle. Two variants worth distinguishing:

| | shape | how to detect | example |
| --- | --- | --- | --- |
| **eventually** periodic | a tail, then a cycle | compare against an earlier state, or [Floyd/Brent](/blogs/technique/cycle-detection) | problem 197 — a float map truncated to nine decimals collapses onto a period-2 attractor |
| **purely** periodic | no tail at all | the recurrence is **invertible** mod $m$, so the map is a permutation and the seed itself must recur | problem 225 — Tribonacci mod $m$, the [Pisano period](/blogs/domain/pisano-period)'s cousin |

The invertibility argument is the one to internalise, because it buys $O(1)$ memory: when the map
is a permutation you can detect the period by waiting for the *seed* to come back, instead of
storing every state you have visited.

When the period *is* the question, and over a million moduli, waiting for the seed costs as much
as the period. Compute it as a group order instead. Problem 752 asks when
$(1+\sqrt 7)^n \equiv 1$ in $(\mathbb Z/x)[\sqrt 7]$, which is the period of a two-term linear
recurrence mod $x$. The [Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
splits $x$ into prime powers, and the periods combine by lcm. A prime then either *splits*
(7 is a square mod $p$, and the order divides $p - 1$) or is *inert* (the ring is
$\mathbb F_{p^2}$, the [Frobenius map](https://en.wikipedia.org/wiki/Frobenius_endomorphism) is
conjugation, and the order is bounded through $p + 1$). Lifting from $p^{k-1}$ to $p^k$ multiplies
the order by $p$ or by nothing, and one test decides which. The per-modulus cost drops from the
period to a few dozen modular powers. This is the [Pisano period](/blogs/domain/pisano-period)
theory, done for a general quadratic ring.

**Change variables until it is linear.** A nonlinear recurrence is sometimes a linear one seen
through a bad coordinate. Problem 492's $a_{n+1} = 6a_n^2 + 10a_n + 3$ roughly squares each term,
so $a_n$ has about $2^n$ digits. Completing the square, $b = 6a + 5$ obeys $b_{n+1} = b_n^2 - 2$,
and that is the doubling rule of a [Lucas sequence](https://en.wikipedia.org/wiki/Lucas_sequence),
$V_{2k} = V_k^2 - 2$. Hence $b_n = V_{2^{n-1}}$. The index is astronomical, but mod $p$ it only
matters modulo the order of the characteristic root. That order divides $p - 1$ or $p + 1$,
depending on a [quadratic-residue](https://en.wikipedia.org/wiki/Quadratic_reciprocity) test,
so $2^{n-1}$ is reduced mod $p \mp 1$ and fed to an $O(\log p)$ Lucas ladder. The squaring maps
worth recognising are $x^2 - 2$ (Lucas and
[Chebyshev](https://en.wikipedia.org/wiki/Chebyshev_polynomials) doubling) and $x^2$ itself
(plain powers). The quadratic you are given is often one of them after an affine change of
variable.

The change of variable need not be affine. Problem 921's map
$a \mapsto a(a^4 + 10a^2 + 5)/(5a^4 + 10a^2 + 1)$ looks arbitrary, but its numerator and
denominator are the sum and difference of $(a+1)^5$ and $(a-1)^5$, up to a common factor. So the
[Möbius transformation](https://en.wikipedia.org/wiki/M%C3%B6bius_transformation)
$t = (a+1)/(a-1)$, which is its own inverse, turns the map into plain $t \mapsto t^5$, and $n$
steps become the single power $t_0^{5^n}$. Any rational map whose degree multiplies at each step
deserves this question: is it a power map seen through a Möbius transformation? The solved form
then raises a new problem of its own. Here $n$ runs over Fibonacci numbers, so the exponents are
$5^{F_i}$. Reduced modulo the group order they obey a second recurrence,
$x_i = x_{i-1} x_{i-2}$, which is Fibonacci written multiplicatively. With millions of exponents
on one base, even a logarithmic power per term is wasteful. Splitting each exponent into a high
and a low half, as [baby-step giant-step](/blogs/technique/baby-step-giant-step) does, lets two
tables, each about the square root of the modulus in size, answer every power with one
multiplication.

**Skip the dull stretches.** A nonlinear recurrence often does something trivial on almost every
step. In that case, compute where the next *interesting* step falls and jump straight to it.
Problem 443's $g(n) = g(n-1) + \gcd(n, g(n-1))$ adds 1 on nearly every step, and along such a run
the offset $d = g(k) - k$ is frozen. The gcd then reduces to $\gcd(j, d-1)$, so the run ends at
the first multiple above $k$ of some prime factor of $d - 1$. One factorisation per event (Pollard
rho, at these sizes) replaces up to $10^{15}$ steps with a few hundred. The state is
$(k, d)$, not $g$. The general question to ask is what stays constant between events.
Problem 551 asks it at every scale at once. Its $a_n = a_{n-1} + s(a_{n-1})$ adds the
[digit sum](/blogs/domain/digit-sum) each step, so nothing is ever trivial. But while the low $k$
digits climb towards $10^k$, the high digits are frozen, and they enter each step only through
their digit sum $c$. The run to the next carry therefore depends on $(k, c, \text{low part})$
alone. It splits into at most ten runs one level down, one per leading digit, and those triples
recur so often that a memo of a few tens of thousands of jumps covers $10^{15}$ steps. Where
443 skips one flat stretch at a time, 551 nests its stretches, and the memo key is again the
frozen part rather than the value. Problem 955 finds its next event a different way. Its rule is
second-order, but the differences $d_n = a_n - a_{n-1}$ just count up by one and reset at each
[triangular number](https://en.wikipedia.org/wiki/Triangular_number), so from a triangle $t(x)$
the sequence runs $t(x) + t(j)$ in closed form. Once the stretch has a closed form, "when is the
next event?" is an equation rather than a search: the least $j$ with $t(x) + t(j) = t(y)$. That
rearranges to $x(x+1) = (y-j)(y+j+1)$, so the next triangle comes from the factor pair of $x(x+1)$
that lies closest to the trivial one and has opposite parity. One factorisation per triangle
replaces a walk whose single gaps reach the trillions.

**Read the step count off a potential.** When the question is how many steps a process takes, the
route may not matter at all. Problem 839 moves one bean at a time along a row of bowls, and the
statement's $B(100)$ alone is over three billion moves. Each move lowers exactly one prefix sum by
exactly one, so the prefix sums form a
[potential](https://en.wikipedia.org/wiki/Potential_method), and
[the move count is simply its total drop](/blogs/takeaway/potential-counts-the-moves). Summing by
parts gives $B = \sum_i i\,(f_i - a_i)$, where $f$ is the final arrangement. The process has now
gone, and only its end state is left to find. That state has a direct description: the row
levelled into blocks, which [pool adjacent
violators](/blogs/technique/pool-adjacent-violators) computes in $O(N)$. So look for a quantity
that every step changes by a fixed amount. If there is one, you need the end state, never the
trajectory.

**Telescope it away.** Occasionally a sum of terms collapses to one term. Splitting $S(N)$ by index
parity and substituting the recurrence can make almost everything cancel
([telescoping](/blogs/technique/telescoping-series)), leaving a
[closed form](/blogs/takeaway/closed-form-over-iteration) in a single value of the sequence — which
you then evaluate by one of the methods above. Problem 918 does exactly this, turning a
trillion-term sum into one evaluation. The same collapse in the other direction is what makes the
partition function computable: the reciprocal of its
[generating function](/blogs/domain/generating-function) is almost all zeros, so $p(n)$ obeys a
recurrence with only $O(\sqrt n)$ terms (problems 76 and 78).

**Unroll it into independent terms.** A first-order linear recurrence
$G_{n+1} = c\,G_n + d_n$ is sequential as written, but its solution is not:
$G_n = c^{\,n-1} G_1 + \sum_{j<n} c^{\,n-1-j} d_j$. Summing that over $n \le L$ gives each $d_j$ a
[geometric](https://en.wikipedia.org/wiki/Geometric_series) weight, and the whole sum becomes one
dot product of independent terms. Problem 423 arrives at such a recurrence indirectly. It needs a
truncated binomial sum $\sum_{c \le \pi(n)} \binom{n-1}{c} 5^{n-1-c}$ for every $n$ up to
$5 \times 10^7$, with a cut-off that moves whenever $n$ passes a prime. Pascal's rule links
consecutive sums: $m \to m+1$ multiplies by 6 and subtracts the boundary term, and each new prime
adds one term back. So the $O(\pi(n))$-term sums become a first-order recurrence. Unrolling that
recurrence then turns a fifty-million-step loop, hopeless in Python, into whole-array NumPy
operations over factorial tables. Unrolling buys
[data parallelism](https://en.wikipedia.org/wiki/Data_parallelism), not fewer operations, and in
an interpreted language that is often the larger win.

**Solve it outright.** Some recurrences have a closed form that a few small cases make obvious and
induction then confirms. Problem 523's insertion cost obeys the full-history recurrence
$T(s) = 1 + \sum_{i<s} T(i)$. Subtract consecutive cases and it becomes $T(s) = 2T(s-1)$, so
$T(s) = 2^s$. Problem 340's function nests four calls deep, a generalised
[McCarthy 91](https://en.wikipedia.org/wiki/McCarthy_91_function), and read literally it would
recurse a quintillion times. Brute force on small parameters shows that it is the identity plus
a constant per block of width $a$, and that pattern is easy to prove by induction on the block.
The sum over $b + 1$ arguments then becomes $O(1)$ arithmetic. A closed form can also be *solved*,
not just evaluated. Problem 555 wants the fixed points of the same function family, each member
$M$ climbing by $k$ and descending by $s$. Its small cases show $M$ cycling through a window of
$d = k - s$ values, a formula the solution checks against brute force rather than proves. Setting
$M(n) = n$ in that formula leaves one divisibility test: if $d \mid s$ the whole window is fixed,
and otherwise nothing is. A search over functions and arguments becomes a sum over $d$ and its
multiples. When the recurrence is **linear in its input sequence**, there is a third route. Problem 739 repeatedly replaces a sequence by its
prefix sums, so the final value is $\sum_k w_k a_k$ for fixed weights. Feeding in unit vectors
exposes the weights, and with all-ones input the statement's example ends at 429, a
[Catalan number](https://en.wikipedia.org/wiki/Catalan_number). That points to
[ballot numbers](https://en.wikipedia.org/wiki/Bertrand%27s_ballot_theorem), and the $n$ rows of
iteration collapse to one weighted sum. A recurrence with **constant leaves** has a fourth: its
value is the number of root-to-leaf paths in its own call tree. Problem 517's
$g_a(x) = g_a(x-1) + g_a(x-a)$, with $a = \sqrt n$ irrational, defeats memoisation outright,
because the arguments $x - i - ja$ are all distinct reals. Unrolled, though, $g_a(x)$ counts the
orders in which unit steps and $a$-steps can carry $x$ below $a$. That is a
[lattice path](/blogs/domain/lattice-path) count, and grouping by the number of $a$-steps
telescopes it to a single sum of about $\sqrt n$ binomial coefficients. The real number survives
only inside a floor, which an integer square root computes exactly.

## How to reason about it

- **Check the recurrence before you optimise it.** Every derivation above is a case analysis, and
  case analyses are where the errors are. Write the $O(n)$ version, check it against the values in
  the statement and against brute force on small inputs, and only then replace it with the matrix
  power or the bit descent. Several solutions here keep the brute force in the directory precisely
  so the fast path can be re-validated.
- **Mind where the recurrence starts holding.** Recurrences frequently fail for the first few
  indices, the small cases being genuinely special. Seed from an index you have verified, and
  answer anything below it from a table.
- **Constant coefficients or not.** $a_n = 3a_{n-1} + 2a_{n-2}$ is a different animal from
  $a_n = n\,a_{n-1} + a_{n-2}$. The first has a companion matrix and a $\log n$ jump; the second is
  [holonomic](https://en.wikipedia.org/wiki/Holonomic_function) — still structured, but the matrix
  changes every step, so there is no exponentiation shortcut and you are back to $O(n)$ unless a
  closed form exists.
- **Reduce, but reduce correctly.** If the answer is wanted mod $m$, keep every term reduced —
  otherwise linear recurrences produce numbers with $\Theta(n)$ digits and the arithmetic, not the
  loop, becomes the cost. Signed coefficients need care: in C a negative intermediate must be
  stored as its residue, `((v % m) + m) % m`, or the next multiplication leaves the word
  ([watch integer width](/blogs/takeaway/watch-integer-width)). And when the problem does *not*
  offer a modulus, expect big integers — the tetranacci count at $n = 500$ is a 140-digit number,
  which Python handles for free and C does not.
- **Find the state that actually determines the subproblem.** A recurrence over a tree is cheap
  only if many subtrees coincide, and that depends on what you key them by. In problem 943 a
  subtree is *not* fixed by its root value: what its descendants are depends on the parity of
  their positions, so the value of every node below it depends on everything to its left. The
  key that works is (value, height, a bitmask of those parities down the left edge), and each
  subtree returns the parities its successor needs. Too small a key gives wrong answers; too
  large a key shares nothing. With the right key, $2 \times 10^{13}$ leaves collapse to a few
  million distinct shapes. The siblings' masks then form a deterministic chain over a finite
  set, so a run of 200-odd identical children is a short tail plus a cycle, which is the
  finite-state trick above in miniature.
- **If the quantity has no recurrence, try its inverse.** Problem 887 asks for the least height
  of a search tree that serves $N$ leaves under a per-leaf depth bound. That is an optimisation
  over trees for each of hundreds of millions of values of $N$, and it has no useful recurrence. Fix the height
  instead and ask for the largest $N$ it can serve. That *capacity* splits cleanly at the root:
  fill the left subtree greedily, and each leaf placed there loosens the right subtree's bound.
  The result is a memoised two-argument recurrence over $O(\log N)$ heights. A
  [tail-sum identity](https://en.wikipedia.org/wiki/Expected_value#Properties) turns
  $\sum_N Q(N)$ into a handful of terms, one per height. Monotonicity is what licenses the swap:
  if a height can serve $N$, it can serve every smaller $N$.
- **Watch the memory, not just the time.** A two-dimensional recurrence rarely needs its whole
  grid. If every cell depends only on cells one step back along some direction, sweep along that
  direction with two rolling buffers: problem 938's grid has both predecessors on the previous
  anti-diagonal, which turns $O(RB)$ memory into $O(R)$ and, as a bonus, makes each sweep one
  vectorised array operation instead of a Python loop.
- **Floating point deserves suspicion.** A recurrence run in `double` accumulates error at every
  step, and subtractive recurrences can amplify it catastrophically. Problem 197 gets away with an
  *exact* equality test only because its map truncates to nine decimals, making the cycle bit-for-bit
  identical; without a quantising step like that, use `fractions.Fraction`, integers, or an explicit
  tolerance you can justify.
- **An expanding map needs exact state.** No tolerance helps when each step multiplies the error.
  Problem 558's greedy expansion in base $r \approx 1.4656$, the real root of $x^3 = x^2 + 1$,
  multiplies the remainder by $r$ at every digit, across some 250 digit positions. So keep the
  state in the ring $\mathbb{Z}[r]$ instead: a remainder is an integer triple $(a, b, c)$ meaning
  $a + br + cr^2$, and multiplying by $r$ is the companion step $(a, b, c) \mapsto (c, a, b + c)$.
  The integers stay small because $r$ is a
  [Pisot number](https://en.wikipedia.org/wiki/Pisot%E2%80%93Vijayaraghavan_number): its conjugates
  have modulus below 1, so the two dimensions the real value cannot see contract. The only real
  number left is the sign that decides each digit. A fixed-point estimate settles nearly all of
  them, and the [field norm](https://en.wikipedia.org/wiki/Field_norm), an exact integer with the
  same sign, settles the rest.

The tell for this whole topic is a problem that describes a process — one more tile, one more turn,
one more level — and then asks about it at an index you could never walk to. Write the recurrence
first, in the most literal form you can defend. Then look at its *shape*: constant coefficients,
halving arguments, a finite state, a period that is really a group order, a nonlinear map that is
a linear one or a plain power in disguise, long trivial stretches, a potential that counts the
steps, a telescoping sum, a sequential loop that unrolls into independent terms, a pattern that
induction will confirm. The shape picks the method.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0114](/solutions/0114/) — Counting Block Combinations I
- ● [0115](/solutions/0115/) — Counting Block Combinations II
- ● [0116](/solutions/0116/) — Red, Green or Blue Tiles
- ● [0117](/solutions/0117/) — Red, Green, and Blue Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0227](/solutions/0227/) — The Chase
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0232](/solutions/0232/) — The Race
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence
- ○ [0282](/solutions/0282/) — The Ackermann Function
- ○ [0287](/solutions/0287/) — Quadtree Encoding (a Simple Compression Algorithm)
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0327](/solutions/0327/) — Rooms of Doom
- ○ [0330](/solutions/0330/) — Euler's Number
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0337](/solutions/0337/) — Totient Stairstep Sequences
- ○ [0339](/solutions/0339/) — Peredur Fab Efrawg
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0341](/solutions/0341/) — Golomb's Self-describing Sequence
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ○ [0366](/solutions/0366/) — Stone Game III
- ○ [0375](/solutions/0375/) — Minimum of Subsequences
- ○ [0382](/solutions/0382/) — Generating Polygons
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ○ [0422](/solutions/0422/) — Sequence of Points on a Hyperbola
- ● [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ● [0443](/solutions/0443/) — GCD Sequence
- ○ [0458](/solutions/0458/) — Permutations of Project
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0469](/solutions/0469/) — Empty Chairs
- ○ [0472](/solutions/0472/) — Comfortable Distance II
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ○ [0490](/solutions/0490/) — Jumping Frog
- ● [0492](/solutions/0492/) — Exploding Sequence
- ○ [0497](/solutions/0497/) — Drunken Tower of Hanoi
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0523](/solutions/0523/) — First Sort I
- ○ [0527](/solutions/0527/) — Randomized Binary Search
- ○ [0532](/solutions/0532/) — Nanobots on Geodesics
- ○ [0535](/solutions/0535/) — Fractal Sequence
- ● [0539](/solutions/0539/) — Odd Elimination
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0555](/solutions/0555/) — McCarthy 91 Function
- ● [0558](/solutions/0558/) — Irrational Base
- ○ [0570](/solutions/0570/) — Snowflakes
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0609](/solutions/0609/) — $\pi$ Sequences
- ○ [0617](/solutions/0617/) — Mirror Power Sequence
- ○ [0623](/solutions/0623/) — Lambda Count
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0645](/solutions/0645/) — Every Day Is a Holiday
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0664](/solutions/0664/) — An Infinite Game
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ● [0670](/solutions/0670/) — Colouring a Strip
- ○ [0671](/solutions/0671/) — Colouring a Loop
- ○ [0672](/solutions/0672/) — One More One
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ● [0698](/solutions/0698/) — 123 Numbers
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ○ [0729](/solutions/0729/) — Range of Periodic Sequence
- ○ [0736](/solutions/0736/) — Paths to Equality
- ○ [0737](/solutions/0737/) — Coin Loops
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0751](/solutions/0751/) — Concatenation Coincidence
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0770](/solutions/0770/) — Delphi Flip
- ● [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0809](/solutions/0809/) — Rational Recurrence Relation
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0825](/solutions/0825/) — Chasing Game
- ○ [0832](/solutions/0832/) — Mex Sequence
- ● [0839](/solutions/0839/) — Beans in Bowls
- ○ [0843](/solutions/0843/) — Periodic Circles
- ○ [0848](/solutions/0848/) — Guessing with Sets
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ○ [0909](/solutions/0909/) — L-expressions I
- ○ [0910](/solutions/0910/) — L-expressions II
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0915](/solutions/0915/) — Giant GCDs
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0921](/solutions/0921/) — Golden Recurrence
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0927](/solutions/0927/) — Prime-ary Tree
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0955](/solutions/0955/) — Finding Triangles
- ● [0968](/solutions/0968/) — 5D Summation
- ○ [0969](/solutions/0969/) — Kangaroo Hopping
- ○ [0985](/solutions/0985/) — Telescoping Triangles
- ● [0986](/solutions/0986/) — Another Infinite Game
- ○ [0993](/solutions/0993/) — Banana Beaver
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1003](/solutions/1003/) — Lonely Singles

<!-- /problems -->
