<!-- tags: [modular-arithmetic-application] -->
<!-- status: final -->
# Modular arithmetic (application)

[Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) as a *technique* is not the
mathematics of remainders — that is the subject of the [domain
page](/topics/domain/modular-arithmetic), and the machinery (exponentiation, inverses, the Chinese
Remainder Theorem, the overflow trap) is catalogued in the deeper [Modular
Arithmetic](/topics/number-theory/modular-arithmetic) note. This page is about the *engineering
move*: deciding to replace the object you were asked about with its residue, and knowing where in
the program that decision lands. It is rarely a `%` sprinkled into an existing loop. In almost every
solution below, applying modular arithmetic changed the algorithm — often before a line was written.

## The one property, and the four places it lands

Everything rests on congruence surviving $+$, $-$ and $\times$: you may reduce after every step and
never let an intermediate grow. What varies is *what* you reduce, and that choice is the technique.
Four shapes cover nearly the whole archive.

**1 — Collapse the algebra before you code.** The strongest application of a modulus is the one that
deletes the computation. Problems 120 and 123 both ask for $(a-1)^n + (a+1)^n \bmod a^2$, which
reads like a job for [modular
exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation). Expand with the [binomial
theorem](https://en.wikipedia.org/wiki/Binomial_theorem) *inside* the modulus instead: every term
carrying $a^k$ with $k \ge 2$ is divisible by $a^2$ and vanishes, so an $(n+1)$-term expansion
collapses to two, and the whole expression reduces to a constant for even $n$ and to $2na \bmod a^2$
for odd $n$. What was an exponentiation per candidate becomes one multiply, and the search over $n$
becomes a one-line maximisation. Problem 168 does the same to a $10^{100}$-wide search: "n divides
its own right-rotation" is a linear equation whose solutions are counted directly, with the modulus
appearing only at the end, where the question asks for the last five digits. Problem 512 hides the
same collapse inside a sum of totients: it wants $\sum_{i=1}^{n} \varphi(n^i) \bmod (n+1)$ for every
$n$ up to $5 \times 10^8$, and the modulus is chosen so that $n \equiv -1$. With
$\varphi(n^i) = n^{i-1}\varphi(n)$ the inner sum becomes $\varphi(n)$ times an alternating sum of
$\pm 1$ — $\varphi(n)$ for odd $n$, zero for even — and since $\varphi(n) \le n$ the final reduction
does nothing at all. A double sum of huge powers turns into "sum $\varphi$ over the odd integers",
and the real work moves to a [summatory totient](/topics/domain/eulers-totient-function) that never
mentions a modulus again. This is
[reduce-before-coding](/topics/takeaway/reduce-before-coding) in its purest form — the modulus is a
tool of *algebra* first and of arithmetic second.

**2 — Turn a residue condition into a stride.** A congruence that a solution must satisfy is a
filter, and a filter you can apply by construction beats one you apply by test. Problem 4 (public,
`solutions/public/p0004/`) wants the largest palindromic product of two three-digit numbers; every
even-length palindrome is divisible by 11, so one factor must supply that 11, and the inner loop
walks multiples of 11 rather than testing them:

```python
a_is_multiple_11 = a % 11 == 0
for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
```

Ten of every eleven candidates are never generated. The same instinct scales: problem 206's target square ends in 0, so its
root is $10m$, and the remaining pattern ends in 9, which forces $m \equiv 3$ or $7 \pmod{10}$ —
two arithmetic progressions instead of a scan, a hundredfold cut; problem 146 stacks residue conditions across
the first several primes until roughly 499 of every 500 candidates fall away before any expensive
[primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) runs. Note the
shape in all three — the residue argument is *cheap* (an integer division, or nothing at all,
because the stride encodes it) and the work it avoids is expensive.

Once a condition is a stride, the last step is to stop walking it. Problem 305 needs to count where
a digit string $s$ occurs in the [Champernowne](https://en.wikipedia.org/wiki/Champernowne_constant)
stream $123456789101112\ldots$ up to integers near $10^{12}$, and the hard case is an occurrence that
straddles two integers: its head $s[{:}i]$ must end $p-1$ and its tail must begin $p$. "Ends in" a
digit string, with the carry from $p-1$ to $p$ thrown in, sounds like casework; written as a
congruence it is one line, $p \equiv s[{:}i] + 1 \pmod{10^i}$, and the carry takes care of itself.
The candidates for $p$ are then an arithmetic progression inside an interval, and those are never
enumerated — they are *counted*:

```python
(hi - r) // m - (lo - 1 - r) // m      # members of {p ≡ r (mod m)} in [lo, hi]
```

A count that would have been a scan over $10^{12}$ integers becomes two floor divisions, cheap
enough to sit inside a [binary search](/topics/technique/binary-search-algorithm) on the count.

**3 — Carry the residue as the state.** When the quantity itself is unbounded but the question
depends only on its remainder, the residue becomes the loop's state variable, and an infinite or
astronomically large state space becomes a finite one. Problem 225 asks whether a Tribonacci
sequence ever hits a multiple of $m$ — an infinite check, until you observe that divisibility
depends only on the triple of consecutive residues mod $m$, which lives in a set of size $m^3$, and
that the recurrence is invertible mod $m$ (recovering the earlier term needs a subtraction, no
division), hence [purely periodic](/topics/domain/periodic-sequence). One period is a complete
answer. Problem 277 pushes the idea further: because each step of its Collatz-style map is chosen by
the current value mod 3, a step string of length $L$ is a base-3 fingerprint pinning the seed to a
single residue class mod $3^L$, recovered one digit at a time — a search becomes an inversion. The
[digit DPs](/topics/technique/dynamic-programming) (725, 885, 217) are the same trick with a small
modulus: the state is a digit sum or a count, not the number.

Two refinements make a residue state much smaller. The first turns a question about *substrings*
into one about *prefixes*: a digit string is divisible by 3 exactly when its digit sum is, so the
substring between positions $i$ and $j$ is divisible precisely when the prefix sums $P_i$ and $P_j$
agree mod 3 — the same move as finding zero-sum subarrays by matching prefix sums. Problem 706 counts
$d$-digit numbers whose number of divisible substrings is itself a multiple of 3. Appending a digit
adds one new divisible substring for each earlier prefix with the new running residue, so the state
is the running residue, three prefix counts and the running total. The question wants the total
only mod 3, so the counts can be kept mod 3 too — the modulus applies to the bookkeeping as well as
to the number. The second refinement is to measure the counts *relative to the current residue*.
That removes the residue from the state and leaves $3^4 = 81$ states. One digit then acts as an
$81 \times 81$ transfer matrix, and $d = 10^5$ is a matrix power.

Sometimes the right state is not one residue but two. Problem 700 walks the sequence $an \bmod m$
for a 16-digit $a$ and $m$ and asks for the sum of its record lows. The terms look random and the
records thin out fast, so a scan stalls after a handful. But the orbit of a multiplication mod $m$ is
not random: carry just the current record low $L$ and the current record gap below the modulus $D$
(the term closest to $m$ from beneath), and the next term to beat either one sits at the sum of their
indices, with value $L - D$ or $D - L$. The state is a pair of residues, the update is a subtraction,
and the whole walk is the [Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm)
on $(a, m)$ in disguise — the [three-gap
theorem](https://en.wikipedia.org/wiki/Three-gap_theorem) explaining why. The indices, which run to
around $10^{16}$, never need to be tracked at all.

The residue need not be of a value at all. Problem 342 sums the $n < 10^{10}$ for which
$\varphi(n^2)$ is a perfect cube, and "is a cube" is a statement about a factorisation: every prime
exponent $\equiv 0 \pmod 3$. Since $\varphi(n^2) = \prod_{p \mid n} p^{2e_p-1}(p-1)$, each prime of
$n$ adds $2e_p - 1$ to its own exponent, and the factorisation of $p - 1$ adds to strictly smaller
primes. The state is then a sparse map from prime to exponent mod 3 — the primes still *owed* — and a
depth-first search places primes from the largest down. Nothing placed later can reach a prime above
it, so the largest owed prime must be settled before the search passes it, and its exponent in $n$
is forced by $2e - 1 + r \equiv 0 \pmod 3$. The largest prime of $n$ is owed nothing, which forces
$e \equiv 2$ and caps every prime at $\sqrt{N}$. The modulus acts on a vector of exponents, and a
search over $10^{10}$ integers becomes an output-sensitive walk over residue maps.

**4 — The modulus you are handed.** Late problems often *state* the modulus — "give $S(k)$ modulo
$1123581313$" — and then the residue is the deliverable, not a shortcut. The discipline is
mechanical but unforgiving: reduce at **every** combine, inside the recurrence, not at the end.
Problem 940's $2 \times 2$ transfer matrices are multiplied mod the given prime throughout, so a
value defined over Fibonacci-sized arguments costs $O(\log m + \log n)$ per entry; problem 885's
[multinomial](https://en.wikipedia.org/wiki/Multinomial_theorem) DP accumulates mod $1123455689$ cell
by cell. A prime modulus does more than bound the numbers: it makes the residues a field, so whole
algebraic objects can be carried exactly. Problem 682 counts pairs of 5-smooth numbers through a
*rational* generating function with a degree-40 denominator. With every coefficient a residue, the
$n$-th coefficient comes from [Bostan–Mori](https://arxiv.org/abs/2008.08822)
halving in $O(d^2 \log n)$ — the same cost at $10^7$ as at $10^{18}$. A single unreduced accumulator anywhere in the loop reintroduces the growth the modulus was
there to prevent.

The converse discipline matters as much: reduce what enters the answer *linearly*, and keep exact
whatever steers the program. Problem 539's survivor of an alternating elimination game obeys a
halving recurrence on a pair — the survivor's position $P$ and the running sum $S$ of positions.
$S(n)$ is an integer-coefficient combination of $S(\lfloor n/2 \rfloor)$ and terms in $P$, so it is
reduced at every level. $P$ is an *index*, used to locate the next survivor, so it stays exact, which
it can afford because $P(n) \le n$. Problem 521's [Lucy\_Hedgehog
sieve](/topics/technique/lucy-hedgehog-sieve) carries two tables side by side for the same reason.
The prime *sums* are reduced mod $10^9$ from the first entry, since every sieve step is linear in
them. The prime *counts* stay exact, because the loop recognises a prime by the count rising at it.
(Problem 463 is the clean case: its paired prefix sums obey linear identities with integer
coefficients, so the whole state reduces.) Problem 674 takes the split furthest. Its
$\mathcal{I}$-expressions grow doubly exponentially, and it wants the *least* common value of two of
them mod $10^9$. "Least" is an ordering, which no residue keeps, so the decision is made where order
survives. $\mathcal{I}$ is injective and increasing in each argument, so equality is structural
[unification](/topics/technique/unification-computer-science) of the expression trees, and the
minimum is the unifier with every free variable set to zero. Only then is the term evaluated, under
the modulus. Compare and decide exactly; reduce only the number you report.

The handed modulus is often *composite* — "the last nine digits" means mod $10^9$ — and that
quietly removes division. Closed forms are full of it: problem 340 reduces its nested "crazy
function" to a sum with a $b(b+1)/2$ in it, and problem 401's
[hyperbola-method](/topics/technique/dirichlet-hyperbola-method) sum of $\sigma_2$ evaluates
$x(x+1)(2x+1)/6$ at $x$ up to $10^{15}$, and problem 688's floor-sum closed form needs $q(q-1)/2$
with $q$ near $10^{16}$. Neither $2$ nor $6$ has an inverse mod $10^9$, so you cannot
reduce the factors and then divide. The fix is to divide *first*, while the factors are still exact:
$2$ divides $x$ or $x+1$, $3$ divides one of $x$, $x+1$, $2x+1$ (which one is decided by $x \bmod 3$),
so strike the factors out of the right term, then reduce and multiply the cofactors.

```python
a, b = (x // 2, x + 1) if x % 2 == 0 else (x, (x + 1) // 2)   # x(x+1)/2, exact
half = (a % m) * (b % m) % m                                     # x(x+1)/2 mod m
```

It costs nothing, needs no inverse, and works for any modulus — prime or not. When it is not
obvious which factor absorbs the divisor, a residue argument can prove the division exact. In problem
764, odd $a$ and $b$ give $a^4 \equiv b^4 \equiv 1 \pmod{16}$, so $5a^4 + 3b^4 \equiv 8 \pmod{16}$ and
division by 8 is exact before anything is reduced. Better still, the division can cancel on paper.
Problem 866's expected product of hexagonal numbers carries a $1/N$ from averaging over the last
piece placed, but $H(N)/N = 2N - 1$ exactly. The recurrence is integral term by term, and the
modulus never meets a fraction.

A prime modulus does have inverses, but each one costs a modular exponentiation, and a loop that
needs one per step pays a logarithmic factor for it. Problem 374 sums, over about $1.4 \times 10^7$
blocks, terms built from $(k+2)!\,H_{k+2}$, where $H_j$ is the [harmonic
number](https://en.wikipedia.org/wiki/Harmonic_number). Carrying $H_j$ as a residue would invert
every $j$. Carrying $A_j = j!\,H_j$ instead — an integer, the [Stirling number of the first
kind](https://en.wikipedia.org/wiki/Stirling_numbers_of_the_first_kind) $\left[{j+1 \atop 2}\right]$
— gives the inverse-free recurrence $A_j = j\,A_{j-1} + (j-1)!$, and the loop spends one inverse at
the very end, for the truncated last block. When a run of fractions shares a natural denominator,
carry the numerator.

A missing inverse can also veto an *algorithm*, not just a formula. Problem 649 is an [impartial
game](/topics/domain/impartial-game) whose positions combine by XOR, so the count of winning
arrangements is a $c$-fold XOR-convolution power of an 8-entry histogram of Grundy values. The
textbook tool is the [Walsh–Hadamard transform](https://en.wikipedia.org/wiki/Hadamard_transform),
but its inverse divides by 8, which has no inverse mod $10^9$. The direct $8 \times 8$ convolution,
raised by squaring, uses only $+$ and $\times$ and costs nothing at that size. Before choosing a fast
transform under a handed modulus, check that its inverse exists there.

Sometimes even the exact factor cannot be formed. Problem 684 needs $10^q$ where $q = \lfloor f/9
\rfloor$ and $f$ is a Fibonacci number near $3 \times 10^{18}$, carried only as a residue. This needs
two moves. First, the exponent and the coefficient live in different moduli: by [Fermat's little
theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), $10^q \bmod p$ depends only on
$q \bmod (p-1)$, while a linear term in $q$ needs $q \bmod p$. So one unknown integer is wanted
modulo two different numbers. Second, the quotient by 9 does not survive reduction mod $p$, so
*lift the modulus*. Run the Fibonacci recurrence mod $9p$ and mod $9(p-1)$. Each residue then
still shows $f \bmod 9$; subtracting that leaves a multiple of 9, and dividing by 9 gives $q \bmod p$
and $q \bmod (p-1)$ exactly. To divide by $k$ under a modulus where $k$ has no inverse, carry the
value mod $km$.

## How to reason about it

The cue is a question whose answer depends only on a remainder attached to a value too large to
form. When you see it, ask in this order: can the modulus be applied *on paper* to collapse the
expression (shape 1)? Can it be applied *to the enumeration* as a stride — or, better, as a count
of the stride (shape 2)? Can it be the
*state* (shape 3)? Only then reach for the arithmetic itself.

Two failure modes are worth naming, because both survive testing on small inputs.

**Reducing something that is not congruence-friendly.** Congruence is preserved by $+$, $-$ and
$\times$ — and by nothing else you are likely to want. Ordering, `max`, `min`, exact equality of
magnitudes and plain integer division all break: $a \equiv b \pmod m$ says nothing about which of
$a$ and $b$ is larger. The trap has a name here, [exact sums resist modular
shortcuts](/topics/takeaway/exact-sums-resist-modular-shortcuts), and problem 244 is the case study:
its checksums are rolling hashes each reduced mod $10^8 + 7$, but the answer is the **plain,
unreduced** sum of those already-reduced values. Carrying a `(count, sum-of-hashes)` pair through
the search — the obvious dynamic program — yields the total only mod $10^8 + 7$, because no residue
records how many individual hashes wrapped around. Each contributing path has to be produced
explicitly. Before you fold a reduction into an aggregate, check that the aggregate is one of $+$,
$-$, $\times$ *in the same modulus as the final answer*.

**Language semantics on the C side.** Python's `%` returns a non-negative result for a positive
modulus; C's truncates toward zero, so any expression that can go negative — a difference of two
residues, an inverse-scaled term — needs normalising, which is why `((x % m) + m) % m` appears in C
solution after C solution here. Division has the same split: the progression count above relies on
Python's `//` flooring, and with `lo - 1 - r` negative C's `/` would round the wrong way, so the C
port of problem 305 carries a small `floor_div` helper. The companion hazard is that two residues below $m$ multiply to
nearly $m^2$, past the 64-bit ceiling once $m$ exceeds about $3 \times 10^9$; see
[`__int128`](/topics/technique/int128) for the standard widening. A *sum* of products overflows
sooner than a single product. Problem 866's convolution has each term below $2^{60}$, but thousands
of them together pass 64 bits, so the C port accumulates in `__int128` and reduces once per entry.
NumPy has no 128-bit type at all: problem 706's 81-term matrix products of 30-bit residues would
overflow `int64`, so the Python splits one operand into 15-bit halves to keep every partial sum
below $2^{52}$. The reverse case is a budget you can rely on. Problem 400 only adds, so with modulus
$10^{18}$ the sum of two residues stays below $2 \times 10^{18}$, which still fits a signed 64-bit
integer. Both the sign bug and the overflow bug produce a plausible wrong number rather than a
crash, and neither shows up on small test inputs.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0244](/solutions/0244/) — Sliders
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0463](/solutions/0463/) — A Weird Recurrence Relation
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0521](/solutions/0521/) — Smallest Prime Factor
- ● [0539](/solutions/0539/) — Odd Elimination
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0628](/solutions/0628/) — Open Chess Positions
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0649](/solutions/0649/) — Low-Prime Chessboard Nim
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ● [0682](/solutions/0682/) — $5$-Smooth Pairs
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0688](/solutions/0688/) — Piles of Plates
- ● [0700](/solutions/0700/) — Eulercoin
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0710](/solutions/0710/) — One Million Members
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0866](/solutions/0866/) — Tidying Up B
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
