<!-- tags: [closed-form-over-iteration] -->
<!-- status: final 2026-11-11T09:00Z -->
# Prefer closed form over iteration

A loop that adds up a structured sequence is doing arithmetic the sequence has
already promised. When the terms follow a rule — an [arithmetic](https://en.wikipedia.org/wiki/Arithmetic_progression)
or [geometric progression](https://en.wikipedia.org/wiki/Geometric_progression),
a count of lattice paths, the corners of a spiral — that rule usually collapses
into a [closed-form expression](https://en.wikipedia.org/wiki/Closed-form_expression):
a fixed formula whose cost does not grow with the number of things it counts.
Often that means a constant number of operations; sometimes it means a short sum
— a few dozen terms standing in for $10^{12}$ cases. Across the problems below
the same move recurs — spot the structure, write the formula, delete the loop —
and it is the single highest-leverage habit these puzzles teach.

## What a closed form buys

The classic case is the sum $1 + 2 + \dots + n$. The obvious program is an
$O(n)$ accumulation; the [Gauss summation](https://en.wikipedia.org/wiki/1_%2B_2_%2B_3_%2B_4_%2B_%E2%8B%AF)
pairs the ends — $1 + n$, $2 + (n-1)$, … — to give $\tfrac{n(n+1)}{2}$ in a
handful of operations that never grow with $n$. That $n$-th
[triangular number](https://en.wikipedia.org/wiki/Triangular_number) is the seed
of a whole family. [Multiples of 3 or 5](/solutions/0001/) sums three arithmetic
runs with it and combines them by
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
($3 + 5 - 15$), turning a scan of the whole range into one line:

```python
def sum_arithmetic_series(d, *, max_limit):
    n = (max_limit - 1) // d
    return d * (n * (n + 1)) // 2
```

[Sum Square Difference](/solutions/0006/) folds the same triangular number
together with the [square-pyramidal](https://en.wikipedia.org/wiki/Square_pyramidal_number)
sum $\tfrac{n(n+1)(2n+1)}{6}$, so $\left(\sum k\right)^2 - \sum k^2$ becomes a
single expression evaluated in $O(1)$. [Lattice Paths](/solutions/0015/) reads
the grid as a counting problem — every route is a sequence of moves, so the
number of them through an $n \times n$ grid is the
[central binomial coefficient](https://en.wikipedia.org/wiki/Central_binomial_coefficient)
$\binom{2n}{n}$ — and [Number Spiral Diagonals](/solutions/0028/) sums each
ring's four corners into $\tfrac{N(N(4N+3)+8)-9}{6}$ instead of laying out the
$N \times N$ grid.

The payoff is not a constant factor. Dropping from $O(n)$ (or an $O(n^2)$
enumeration) to $O(1)$ changes the shape of the running time — it is the same
lever the [algorithm-beats-language](/blogs/takeaway/algorithm-beats-language)
takeaway pulls, taken to its limit, where the work stops growing with the input
at all. Larger problems reach for heavier closed forms — a matrix recurrence
solved by [fast exponentiation](https://en.wikipedia.org/wiki/Exponentiation_by_squaring),
a [generating function](https://en.wikipedia.org/wiki/Generating_function), a
combinatorial identity — but the principle is one and the same: let the
structure do the counting.

## Closed forms as building blocks

In the harder problems the formula rarely *is* the answer. It is a component —
the part of the computation that would otherwise be the inner loop — and the
surrounding algorithm is designed around having it. Eleven shapes recur.

**A formula per item, in place of a search per item.**
[Divisibility Multipliers](/solutions/0274/) asks, for every prime $p$ coprime
to 10, for the smallest multiplier $m$ that preserves divisibility under a
digit-shuffling map. The obvious program tries $m = 1, 2, \dots$ for each prime.
A line of algebra shows the condition is $10m \equiv 1 \pmod p$ — $m$ is the
[modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse)
of 10 — and that inverse has a closed form, $(kp+1)/10$, with $k$ read off a
four-entry table by $p$'s last digit. The outer sum over primes remains; the
per-prime search is gone, and what is left vectorises into one array expression.

**A formula for the full blocks, iteration only along the boundary.** Counting
up to an arbitrary bound $N$ rarely closes in one formula, but the count over a
*complete* block — all $b$-bit numbers, all $D$-digit numbers — usually does.
[Odd Triplets](/solutions/0242/) reduces, through
[Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem), to summing
$2^{\operatorname{popcount}(t)}$ over $t \le T$; over a free block of $b$ bits
that sum is exactly $3^b$ (each bit contributes a factor $1 + 2$). Walking the
bits of $T$ from the top, every 1-bit closes off one full block, so a sum over
a quarter of a trillion values takes under forty steps. [Reflexive Position](/solutions/0305/)
uses the same split on decimal digits: occurrences of a string inside a
$D$-digit integer at a fixed offset leave the other digits free, a power of 10
apiece, and only the top length needs a comparison against $N$. This is the
skeleton of a [digit DP](https://en.wikipedia.org/wiki/Dynamic_programming),
with the closed form doing the work the memo table would.

**A formula for the tail, iteration only for the transient.** Some sequences are
irregular at first and then settle down. [Paper Cutting](/solutions/0933/) is a
cutting game whose positions are sums of independent sheets, so the
[Sprague–Grundy theorem](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
gives each $w \times h$ sheet a nimber. Counting the winning moves needs those
nimbers for heights up to $1.2 \times 10^6$, and each one is a mex over $O(wh)$
cuts, so the full table is out of reach. But every row $g(w, \cdot)$ is
eventually constant, and induction on the width proves it: once both strips of
a cut are past their thresholds, the four pieces cancel in pairs under XOR. So
each row has to be computed only up to twice the largest threshold among its
splits. Past that point the count of winning cuts at height $h$ follows a fixed
linear rule, and the remaining million heights are one arithmetic series. The
cost no longer depends on $H$. The same split works for any sequence that
settles into a constant, linear or periodic pattern: compute the transient
honestly, and prove where it ends.

**A cheap count you can invert.** Once "how many up to $N$" costs
$O(\log N)$, "where is the $n$-th one" is a
[binary search](https://en.wikipedia.org/wiki/Binary_search_algorithm) over a
monotone function — which is how Reflexive Position locates the $n$-th
occurrence of $n$ in the Champernowne string without ever writing the string
out. The closed form did not answer the question; it made the question
searchable.

**A formula at the leaves of a quotient recursion.**
[Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula)
over the floor quotients $\lfloor n/d \rfloor$ — the engine behind
[Primitive Triangles](/solutions/0276/) and [Bounded Sequences](/solutions/0319/)
— evaluates some summatory function at only $O(\sqrt n)$ distinct arguments,
which is sublinear *only if* each evaluation is cheap. Primitive Triangles needs
the count of all integer triangles with perimeter $\le v$: that is a prefix sum
of [Alcuin's sequence](https://oeis.org/A005044), $\operatorname{round}(k^2/12)$,
and the rounding, being periodic in $k \bmod 12$, folds into the
square-pyramidal sum as a correction term — $O(1)$ per quotient, $O(n^{3/4})$
overall. Bounded Sequences reduces its count to $F(m) = \sum_{h \le m} (3^h - 2^h - 1)$,
two geometric series evaluated with modular exponentiation at each large
quotient. Without these leaf formulas each method would be a linear scan in
disguise.

**A formula for a process, read off a small run of it.** Some problems do not
hand you a sequence at all. They hand you a *procedure*, a recursion or a greedy
rule, and the closed form is something you discover. [Crazy Function](/solutions/0340/)
generalises the [McCarthy 91 function](https://en.wikipedia.org/wiki/McCarthy_91_function):
above a threshold $b \approx 5.6 \times 10^{17}$ it subtracts a constant, and
below it the call nests four deep. Taken literally that is unbounded recursion
summed over $b+1$ arguments. A memoised brute force on small parameters shows
the pattern. Cut $[0, b]$ into blocks of width $a$ counted down from $b$. Then
$F(n)$ is $n$ plus a fixed offset plus one constant increment per block, and
induction on the block index proves it. Summing an affine function block by
block brings back the Gauss sum, and the whole problem becomes $O(1)$.
[Hilbert's New Hotel](/solutions/0359/) is the greedy version. Guests take the
first floor where they sum to a perfect square with the previous occupant, and
the question needs occupants of order $10^{27}$. Simulating forty thousand
guests shows the rigid structure. Neighbouring rooms sum to *consecutive*
squares, so two rooms apart the squares telescope,
$P(f, r+2) - P(f, r) = (s+1)^2 - s^2 = 2s + 1$, which is linear in $r$. That
makes each floor a quadratic in the room number, and the requested sum shrinks
to a few hundred formula evaluations over the divisors of $N$. [Binary Blackboard](/solutions/0711/)
is the game version. An exhaustive search of a two-player game up to $n = 1100$
shows that the first player wins on exactly two families of binary patterns:
all-ones numbers, and isolated ones at even bit positions followed by an
optional even-length block of ones. Summing those families up to $2^N$ is pure
algebra, with $N$ in the tens of millions. In all three problems the brute force
is a microscope rather than the solution. It shows you the pattern, a proof
makes the pattern safe to use, and the formula replaces the process.

Sometimes the process yields to derivation instead of observation.
[A Real Recursion](/solutions/0517/) defines $g_a$ by a recursion with two step
sizes, $1$ and an irrational $a = \sqrt n$, so no two arguments ever coincide
and memoisation finds nothing to reuse. Unrolled, though, the recursion is a
*count*: each path of unit steps and $a$-steps that stops in the final window
contributes 1. Splitting the paths by their last step and applying the
[hockey-stick identity](https://en.wikipedia.org/wiki/Hockey-stick_identity)
makes the two cases [telescope](https://en.wikipedia.org/wiki/Telescoping_series),
leaving a single sum of about $\sqrt n$ binomial coefficients. [Pairwise Coin-Tossing Game](/solutions/0605/)
is a random process. Once you see that only one bit of state survives each
round, it becomes a two-state [Markov chain](https://en.wikipedia.org/wiki/Markov_chain),
and its recurrence solves exactly: the game ends at round $m$ with probability
$(m-1)/2^m$. The process is gone, and what remains is a series to sum (see
below).

The deepest derivation changes coordinates. [Golden Recurrence](/solutions/0921/)
iterates a degree-five rational map and wants its terms at Fibonacci indices,
far past anything a loop could step through. But the map's numerator and
denominator are the odd and even halves of a binomial expansion, and the
[Möbius transformation](https://en.wikipedia.org/wiki/M%C3%B6bius_transformation)
$t = (a+1)/(a-1)$ [conjugates](https://en.wikipedia.org/wiki/Topological_conjugacy) it
into the plain power map $t \mapsto t^5$. Conjugation is what makes this pay: if
$f = \phi^{-1} \circ g \circ \phi$, the steps in between cancel and
$f^n = \phi^{-1} \circ g^n \circ \phi$, so $n$ steps of $f$ cost only what $n$
steps of $g$ cost, and $n$ steps of a power map are one power. Diagonalising a
matrix does the same for a linear recurrence, which is why
[Binet's formula](https://en.wikipedia.org/wiki/Fibonacci_sequence#Binet's_formula)
exists. Here the trick reaches a nonlinear one, and the article on
[recurrence relations](/blogs/domain/recurrence-relation) takes up how to spot it.

**A bijection to a family that is already counted.** Sometimes the objects being
summed are a well-known combinatorial family in disguise. Once you see which
family it is, a classical count does the work. [Zebra Circles](/solutions/0892/)
sums over non-crossing chord diagrams. Put a vertex in each piece and join pieces
that share a chord, and each diagram becomes exactly one plane tree. The colour
difference then compares the tree's vertices at odd and even depth. Plane trees
counted by their odd-depth vertices are the
[Narayana numbers](https://en.wikipedia.org/wiki/Narayana_number), so $D(n)$
becomes a weighted sum of $n$ of them. Even that short sum closes. On small $n$
its partial sums turned out to be products of two binomials, and a guess of that
kind proves itself: check that consecutive products differ by the summand, the
same test [Gosper's algorithm](https://en.wikipedia.org/wiki/Gosper%27s_algorithm)
automates. Each $D(n)$ is then one binomial product, and ten million of them come
from a single recurrence for the central binomial coefficients.
[Stone Game Solitaire](/solutions/0960/) reaches a family from a process. Counting
stones shows that every successful game has $n-1$ turns, that the pairs of piles
the turns touch form a spanning tree, and that the tree alone fixes how many
stones each turn takes, and so its score, in any order of play. The sum over
games becomes $(n-1)!$ times a sum over labelled trees and their edges, which is
a double sum to turn on its side (see below). Count the (tree, edge) pairs by the
sizes of the two parts the edge separates, using
[Cayley's formula](https://en.wikipedia.org/wiki/Cayley%27s_formula) for the trees
on each side, and $n$ terms are left.

**A formula you solve, not just evaluate.** An expression can do something a
process cannot: it can stand in an equation. [McCarthy 91 Function](/solutions/0555/)
starts as Crazy Function did, with memoised runs on small parameters showing
that below the threshold the generalised function is a sawtooth in $n$ of period
$d = k - s$. But this problem wants the *fixed points*, summed over every
parameter pair. With the formula on paper, $M(n) = n$ can simply be solved, and
the result is all-or-nothing: fixed points exist exactly when $d \mid s$, and
then a whole window of $d$ consecutive integers is fixed. That condition also
tells you how to index the sum. Almost every pair $(k, s)$ contributes nothing,
so stop looping over them and loop over $d$ and the multiples $s = jd$ instead.
Each window is a Gauss sum and the sum over $j$ is a polynomial, which leaves one
closed form per $d$.

**A summand rewritten until it matches a known sum.** [Divisor Pairs](/solutions/0561/)
asks for a [2-adic valuation](https://en.wikipedia.org/wiki/P-adic_valuation)
summed over $10^{12}$ values of $i$. Counting divisor pairs coordinate by
coordinate gives a closed form for each term. A parity case split (with the
[lifting-the-exponent lemma](https://en.wikipedia.org/wiki/Lifting-the-exponent_lemma)
for one branch) then shows that each term's valuation is just $v_2$ of a
half-index, scaled by a constant. And $\sum_{t \le N} v_2(t) = v_2(N!)$, which
[Legendre's formula](https://en.wikipedia.org/wiki/Legendre%27s_formula) gives as
$N - s_2(N)$, where $s_2$ is the count of 1 bits. The summand never gets a
formula of its own here. You keep rewriting it until it matches a sum someone
has already closed.

**A double sum turned on its side.** A term with a formula does not make the sum
of those terms easy, and which index you sum first can decide it.
[Piles of Plates](/solutions/0688/) sums a floor over a plate count $n$ up to
$N = 10^{16}$ and a pile count $k$. Taken in that order, the outer loop alone is
hopeless. [Swap the order](https://en.wikipedia.org/wiki/Summation) and $k$ is
fixed while $n$ runs, so the floors form a staircase in which each value repeats
$k$ times, and a prefix of a staircase closes as a triangular number plus one
partial step. Only $k$ up to about $\sqrt{2N}$ contribute, so what remains is
$O(\sqrt N)$ closed-form terms. When a double sum resists, ask which index the
summand is simplest in, and put that index innermost.

**A formula for the solution set.** A search can close as well as a sum.
[Tangent Circles](/solutions/0510/) sums over the integer triples of radii that
satisfy a tangency equation. Instead of testing pairs of radii, you
[parametrise by the reduced ratio](/blogs/takeaway/parametrise-by-reduced-ratio):
every solution is a scale $t$ times a fixed polynomial triple in a coprime pair
$(u, v)$, and it appears exactly once. That shrinks $O(n^2)$ pairs of radii to
$O(\sqrt n)$ pairs $(u, v)$, but only with a second closed form behind it.
The radii are linear in $t$, so a pair's multiples sum as one triangular number.
A loop over $t$ would bring back the linear cost, since the smallest pair alone
has $\lfloor n/4 \rfloor$ multiples.

Both halves of that move generalise. [Nested Radicals](/solutions/0880/) gets its
parametrisation from algebra in a cubic field. The radical denests exactly when a
certain element is a square, and that condition comes out as two quartic forms in
a coprime pair $(\alpha, \gamma)$, times a scale $s^2$. Because the scale enters
squared, a primitive pair's multiples sum as a square-pyramidal number instead of
a triangular one. [Angular Bisector and Tangent 2](/solutions/0962/) gets its
family from geometry. Asking for an integer $CE$ turns into a conic
$g^2 - w^2 = Dm^2$ with an obvious rational point, and the
[lines through that point](https://en.wikipedia.org/wiki/Rational_point)
meet every other rational point exactly once. It then closes a third count as
well. The numerators of those slopes run over integers coprime to a known number,
up to a bound one integer square root gives, so the solution counts them by
[inclusion–exclusion](/blogs/technique/inclusion-exclusion-principle) over that number's
primes, split by parity, instead of visiting them. Neither the scales nor the
numerators are ever enumerated one by one.

The plainest variant is a sum that is short rather than constant.
[Twenty-two Foolish Primes](/solutions/0239/) asks a probability over all $100!$
permutations; [inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
over which displaced discs are nevertheless fixed gives an alternating sum of
binomial-times-factorial terms — the
[derangement](https://en.wikipedia.org/wiki/Derangement) formula, generalised —
with as many terms as there are displaced discs. Twenty-three exact
big-integer terms replace an enumeration no computer could finish.

## Many roads end in a geometric series

Among the later problems, the formula that finally does the work is very often
the oldest one, the [geometric series](https://en.wikipedia.org/wiki/Geometric_series)
$\sum_{k<K} x^k = (x^K - 1)/(x - 1)$. Under any modulus coprime to $x - 1$ that
is one [modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation)
and one [modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse),
so $K$ can be $10^{18}$. The hard part is turning the problem into geometric
series in the first place, and six different routes lead there.

**Periodicity, split into residue classes.** [Clock Sequence](/solutions/0506/)
reads terms off a digit stream with period 6. Because a full period always sums
to 15, every fifteenth term starts at the same phase. So within each residue
class $r \bmod 15$ the terms obey an affine recurrence,
$v_{n+15} = 10^6 v_n + Q_r$, and unrolling an affine recurrence always gives a
geometric series. Summing $10^{14}$ terms takes fifteen modular powers. When a
sequence is periodic, split it by the period and look for a fixed linear map
from each term to the next term in its class.

**A change of basis to exponentials.** [Simbers](/solutions/0520/) constrains
how often each digit appears, which is a job for
[exponential generating functions](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function):
"an even number of times" is $\cosh x$ and "zero or an odd number of times" is
$1 + \sinh x$. Their product is still awkward to read coefficients from. But
$\cosh$ and $\sinh$ are combinations of $e^{\pm x}$, and
$L!\,[x^L]\,e^{kx} = k^L$. Rewritten in powers of $e^x$, the product becomes a
Laurent polynomial with 21 terms, so the count of strings of length $L$ is
exactly $\sum_k c_k k^L$. Summing over all lengths up to $2^{39}$ is then 21
geometric series. The general move: if the basis you were given makes
coefficients hard to read, find a basis where each piece is a pure power.

**One derivative up: arithmetico-geometric sums.** When the terms are $m x^m$
rather than $x^m$, as in the $(m-1)/2^m$ ending probabilities of Pairwise
Coin-Tossing Game, the [arithmetico-geometric](https://en.wikipedia.org/wiki/Arithmetico-geometric_sequence)
sum still closes. That is
$\sum_{m=1}^{L} m x^m = x\bigl(1 - (L+1)x^L + Lx^{L+1}\bigr)/(1-x)^2$, the
derivative of the geometric series. Pairwise Coin-Tossing sums it over every
$n$-th round to get each player's winning probability. Binary Blackboard uses it
to remove its last loop: grouping the second family by its lowest exponent $m$
leaves a weighted sum in $m$ with ratio $\tfrac12$, which closes the same way. Without that
step the sum would be $O(N)$, and with it $N = 10^{18}$ takes microseconds.

**Symmetry, past roots you never compute.** [Roots on the Rise](/solutions/0479/)
defines each term through the three complex roots of a cubic with parameter $k$,
and sums the $p$-th power of a product built from those roots over both $k$ and
$p$. No root is ever found. The product is symmetric in the roots, so
[Vieta's formulas](/blogs/technique/vietas-formulas) rewrite it in the cubic's
coefficients. The complex parts cancel and leave a polynomial in $k$. Each inner
sum over $p$ is then a geometric series with that polynomial as its ratio, and
$10^{12}$ terms become $10^6$ closed forms. When a definition passes through
objects you cannot write down, check whether the final quantity is symmetric in
them.

**A table that fits a sum of powers.** [Gathering the Beans](/solutions/0335/) is
a sowing game on a ring of bowls, asked at $2^k + 1$ bowls with $k$ up to
$10^{18}$. Simulation is practical to about $k = 12$, and the solution never needs the
general $M(x)$, only that one family, so that is the sequence to tabulate. Its
consecutive ratios settle on a small integer, which is what a sum of pure powers
does as the largest base takes over, and the table fits three such powers
exactly. Each power is then its own geometric series. If a sequence grows at a
steady ratio, try that form before anything cleverer.

**Runs in a sparse digit string.** [Rational Blancmange](/solutions/0889/)
evaluates the [blancmange function](https://en.wikipedia.org/wiki/Blancmange_curve)
at a rational number whose binary period is about $2 \times 10^{18}$ digits long.
Regrouping the defining series by digit position gives
$T(x) = \sum_q 2^{-q} c_q$, where $c_q$ counts the earlier digits that disagree
with digit $q$. Every later period adds the same amount to each $c_q$, so the
infinite tail is one geometric series and only a single period is left to sum.
That period is almost all zeros, because the
[binomial theorem](https://en.wikipedia.org/wiki/Binomial_theorem) spreads the
numerator into about sixty short clusters of bits. And $c_q$ stays constant along
any run of equal digits, so a run from $u$ to $v$ contributes one geometric
segment, $c_u\,(2^{N-u+1} - 2^{N-v})$. Two quintillion digits become about four
thousand runs. When a summand changes at only a few places, sum it in closed form
between them.

Two edge cases come with the formula. Watch for the degenerate ratios: $x = 1$
sums to the number of terms and $x = 0$ to its $x^0$ term alone, and Simbers
hits both among its 21 series. And keep $x - 1$ invertible. Clock Sequence
checks that $10^6 - 1$ shares no factor with its modulus before dividing by it.
A prime modulus is convenient but not required: Gathering the Beans works modulo
$7^9$, and all it needs is that its denominators are coprime to 7.

## How to reason about it

Reach for a closed form when the quantity you are accumulating is *structured* —
the terms obey a recurrence or an algebraic rule, not arbitrary data. The tells
are concrete: an arithmetic or geometric run, a triangular / pyramidal / binomial
count, a sum over a regular grid, a linear recurrence with constant coefficients,
a count over all numbers with a fixed number of digits or bits, a term that
is a polynomial up to a periodic wobble (floors and rounds of $k^2/c$), a
periodic sequence, a recursion whose unrolling is a path count, a random
process with only a few states, a quantity symmetric in roots you cannot write
down, a rational map that may be a power map in disguise, a double sum that
is simple in one of its indices, a sequence that settles after a transient, a
summand that changes at only a few places, a conic with one rational point on it,
or a set of objects (or of successful runs of a process) that is a known
combinatorial family, such as trees, in disguise.
When the summand is genuinely irregular — the rectangle counts scanned in
[Counting Rectangles](/solutions/0085/), where the search stops at the shape
nearest a target — no formula collapses the whole thing, and iteration is the
honest answer. The skill is telling the two apart: derive on paper first, and if
the algebra does not close, do not force it.

Five cautions earn their keep:

- **Derive, then verify.** A closed form is only as good as its derivation; an
  off-by-one in the bounds or a dropped term is silent. Keep a brute-force
  version as an oracle and check them against each other on small inputs —
  [Number Spiral Diagonals](/solutions/0028/) ships exactly that, running an
  $O(N^2)$ spiral simulation under `--show` purely to confirm the formula.
  When the formula came *from* the brute force, as in Crazy Function and
  Hilbert's New Hotel, checking it on the same few cases proves nothing. Test
  it on fresh ones: Crazy Function was checked on 400 random parameter
  triples, and Hilbert's New Hotel on every room the simulation filled.
  Sometimes no proof arrives, and then the formula is only as good as the
  evidence, so aim that evidence where a wrong formula would show.
  Gathering the Beans rests on simulation alone, but thirteen table entries
  against the handful of constants in its fit leave the fit little freedom.
  McCarthy 91 Function was never proved either, so its checks use lopsided
  parameters that force the window-clipping branch, where an off-by-one would
  hide. Say which of the two you have: a proved formula and a well-tested one
  are not the same claim.
- **Mind the arithmetic.** Formulas multiply before they divide, so intermediate
  values can be far larger than the answer — a real overflow risk in C, and a
  reason to prefer exact integer arithmetic (Python's big integers, or careful
  ordering so the division is exact) over anything that rounds. Division is the
  sharp edge. Under a modulus the halving in $(3^{m+1} - 3)/2$ is not a plain
  division; Bounded Sequences works modulo $2M$, where the residue stays even,
  and halves that. Crazy Function, working modulo $10^9$ where 2 has no
  inverse, halves whichever factor of $n(n+1)$ is even *before* it reduces. A `round` inside the summand, as in Alcuin's sequence, is
  not something to evaluate in floating point term by term; Primitive Triangles
  folds it into a periodic integer correction. Twenty-two Foolish Primes keeps
  its probability as an exact ratio of two big integers and rounds to twelve
  decimals in integer arithmetic.
- **The argument may be too big to write down.** A closed form cheap enough to
  handle $10^{18}$ will be given inputs where even $10^q$ has $10^{17}$ digits.
  Then you evaluate the formula without ever forming its argument.
  [Inverse Digit Sum](/solutions/0684/) has the simple closed form
  $s(9q + r) = (r+1)\,10^q - 1$ for the smallest number with digit sum $9q + r$,
  but its $q$ comes from Fibonacci numbers near $3 \times 10^{18}$. By
  [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem)
  the exponent only matters modulo $p - 1$, while the linear term only matters
  modulo $p$. So the solution runs the Fibonacci recurrence modulo $9p$ and
  modulo $9(p-1)$, and reads off $r$, $q \bmod p$ and $q \bmod (p-1)$ from the
  two residues. Simbers never forms $n = \text{base}^u$. It moves from one $u$
  to the next by raising each $k^n$ to the power of the base, which keeps the C
  port inside 64 bits. Pairwise Coin-Tossing needs a reduced fraction whose
  numerator has thirty million digits. The structure of the formula confines
  any common factor to $\gcd(n, 2^n - 1)$, which needs only $2^n \bmod n$. That
  factor may not be invertible modulo $10^8$, so the solution divides it out
  exactly under a raised modulus $10^8 g^2$. The trap also hides in
  bookkeeping. Rational Blancmange first checked that its binomial blocks
  could not overlap with `max(coefficients) < (1 << t)`, and that tried to
  allocate a number with $10^{14}$ bits. Comparing bit lengths asks the same
  question for free.
- **A formula is worth deriving once and reusing.** The triangular and
  pyramidal-number identities recur across many of the problems below; naming
  them as small helpers, as these solutions do, keeps each new use a one-liner
  rather than a fresh derivation.
- **Closed form is not always cheaper per call.** When you need a formula at
  every small argument in order, a running total costs $O(1)$ per step, while
  re-evaluating the formula can cost more (a modular power each time). Bounded
  Sequences accumulates $F$ incrementally below $\sqrt n$ and switches to the
  closed form only for the scattered large quotients. Use the formula where it
  lets you skip arguments, and plain iteration where you visit every one
  anyway. A formula evaluated millions of times can also be paid for in bulk.
  Golden Recurrence needs one fixed base raised to over a million scattered
  exponents, so it tabulates the powers for an exponent's low and high bits, and
  one multiplication of two table entries replaces about 29 squarings.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0006](/solutions/0006/) — Sum Square Difference
- ● [0015](/solutions/0015/) — Lattice Paths
- ● [0024](/solutions/0024/) — Lexicographic Permutations
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0053](/solutions/0053/) — Combinatoric Selections
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0099](/solutions/0099/) — Largest Exponential
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0148](/solutions/0148/) — Exploring Pascal's Triangle
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0183](/solutions/0183/) — Maximum Product of Parts
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0232](/solutions/0232/) — The Race
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0479](/solutions/0479/) — Roots on the Rise
- ● [0506](/solutions/0506/) — Clock Sequence
- ● [0510](/solutions/0510/) — Tangent Circles
- ● [0517](/solutions/0517/) — A Real Recursion
- ● [0520](/solutions/0520/) — Simbers
- ● [0555](/solutions/0555/) — McCarthy 91 Function
- ● [0561](/solutions/0561/) — Divisor Pairs
- ● [0587](/solutions/0587/) — Concave Triangle
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0688](/solutions/0688/) — Piles of Plates
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0704](/solutions/0704/) — Factors of Two in Binomial Coefficients
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0868](/solutions/0868/) — Belfry Maths
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0880](/solutions/0880/) — Nested Radicals
- ● [0889](/solutions/0889/) — Rational Blancmange
- ● [0892](/solutions/0892/) — Zebra Circles
- ● [0899](/solutions/0899/) — DistribuNim I
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0921](/solutions/0921/) — Golden Recurrence
- ● [0932](/solutions/0932/) — $2025$
- ● [0933](/solutions/0933/) — Paper Cutting
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ● [0960](/solutions/0960/) — Stone Game Solitaire
- ● [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
