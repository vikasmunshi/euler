<!-- tags: [reduce-before-coding] -->
<!-- status: final 2026-11-03T22:36Z -->
# Reduce algebraically before coding

Before you write a loop, ask what the loop is really computing — and whether the
mathematics will hand you the answer with less work, or none. Reducing
algebraically before coding is the habit of spending five minutes with pen and
paper on a problem's structure so the program that follows is smaller, tighter,
or gone entirely. The payoff runs from the modest (one nested loop removed) to
the total (an O(n) scan collapsed to a formula), but it is the same move every
time: simplify the math first, because the cheapest loop is the one you never
have to run. Past the first hundred problems it stops being optional — the
search spaces run to $2^{669}$ subsets or $10^{24}$ index pairs, and the only
program that finishes is the one written after the reduction.

## The reduction, in degrees

A reduction is any algebraic step that shrinks the work *before* it becomes code.
The problems below reach for it at four escalating strengths.

**Eliminate a variable.** A constraint that ties two unknowns together lets you
solve for one and delete a whole dimension of search. In
[Special Pythagorean Triplet](/solutions/0009/) the sum condition $a + b + c = S$
means $c$ is never searched — it is computed, $c = S - a - b$ — so a naive
three-nested-loop hunt over $(a, b, c)$ becomes a two-loop scan over $(a, b)$,
$O(S^3)$ down to $O(S^2)$. Nothing clever happened; one line of algebra removed
an entire loop.

**Prune the domain.** The same ordering $a < b < c$ that eliminates $c$ also
*bounds* what is left: $a$ cannot exceed $S/4$ and $b$ cannot exceed $S/2$, or no
valid larger values fit. Deriving the tightest bounds before the loop is written
keeps the search inside the region that can actually contain an answer. The
[cheap-checks-first](/blogs/takeaway/cheap-checks-first) and
[exploit-symmetry](/blogs/takeaway/exploit-symmetry) takeaways are this same
instinct pointed at the loop body and the coordinate system. A domain can also
be pruned by *type*. [Integer Ladders](/solutions/0309/) promises integers for
the two ladders, the crossing height $h$ and the street width, but says nothing
about the heights $a$ and $b$ the ladders reach. A short irrationality argument
settles it: $1/a + 1/b = 1/h$ cannot hold with an integer $h$ unless both heights
are integers too. That unstated fact makes each ladder a Pythagorean triple, and
a problem about real geometry becomes pairs of triples that share a leg.

**Exploit structure to skip work.** Sometimes the sequence itself has a pattern
that lets you step over most of it. [Even Fibonacci Numbers](/solutions/0002/)
never tests a single term for evenness: the parities of the
[Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence) run
odd, even, odd with period three forever, so every third term is even, and
expanding the recurrence three times gives a direct rule
$E(k+1) = 4E(k) + E(k-1)$ that walks the even terms alone. The divisibility test
is not optimised — it is *derived away*. The same move carries
[GCD Sequence](/solutions/0443/) to $10^{15}$: writing $g(k) = k + d$ turns
each step's $\gcd(j, g(j-1))$ into $\gcd(j, d-1)$ with $d$ fixed, so the long
runs of $+1$ steps end exactly at the next multiple of a prime factor of $d-1$.
The program jumps from event to event — a few hundred factorisations in place of
a quadrillion gcds.

**Close the form.** At the far end, the structure is regular enough that the loop
disappears into a single expression. [Counting Rectangles](/solutions/0085/)
sees that a sub-rectangle is fixed by choosing two of $H+1$ horizontal and two of
$W+1$ vertical grid lines, so the count *factors* into
$T(H)\cdot T(W)$ with $T(n) = \tfrac{n(n+1)}{2}$ — two independent
[triangular numbers](https://en.wikipedia.org/wiki/Triangular_number) instead of
a two-dimensional enumeration. [Number Spiral Diagonals](/solutions/0028/) sums
each ring's four corners in closed form to
$\tfrac{N(N(4N+3)+8)-9}{6}$, an $O(N^2)$ grid replaced by one arithmetic line.
[Sums of Totients of Powers](/solutions/0512/) defines $f(n)$ as a sum of $n$
totients of powers modulo $n+1$; with $\varphi(n^i) = n^{i-1}\varphi(n)$ and
$n \equiv -1$, the terms alternate in sign and cancel, leaving $\varphi(n)$ for
odd $n$ and $0$ for even — the defining sum is never evaluated at all.
The same move scales a long way: [Odd Triplets](/solutions/0242/) asks about
roughly $10^{24}$ pairs $(n, k)$, but only about the *parity* of a subset count,
and two applications of
[Lucas' theorem](https://en.wikipedia.org/wiki/Lucas%27s_theorem) reduce that
parity to $\binom{n-1}{k-1} \bmod 2$ — so each admissible $n = 4t + 1$
contributes $2^{\mathrm{popcount}(t)}$ pairs, and nothing is ever counted one
at a time. This is the endpoint the [closed-form-over-iteration](/blogs/takeaway/closed-form-over-iteration)
takeaway is about; reducing before coding is the wider discipline that *reaches*
it — and that is content to stop one step short when the algebra will not close
all the way.

## Reductions that change the question

The four degrees above simplify a computation that is already the right one.
The harder problems on the list mostly need something earlier: a reduction that
changes *what* is computed before any of it is simplified. Seven such moves
recur.

**Restate the condition.** The question as posed is often the awkward form of
an easier one. [Twenty-two Foolish Primes](/solutions/0239/) asks for 22 of
the 25 primes to be *away* from home; "3 are at home" is the same event, and
fixed points are what
[inclusion–exclusion](https://en.wikipedia.org/wiki/Inclusion%E2%80%93exclusion_principle)
counts well. [Coresilience](/solutions/0245/) asks for a unit fraction, which
is a divisibility, which forces $n$ to be squarefree and turns the search into a
construction. [A Game of Chance](/solutions/0951/) asks whether a deck is fair;
that is a statement about the parity of the turn count, the parity factors over
the deck's single-colour runs, and the run bias obeys a small recurrence that
is zero at exactly one length — so "fair" becomes a pattern-avoidance count with
no probability left in it. [A Long Row of Dice](/solutions/0641/) asks which
dice end on face 1; that is $d(k) \equiv 1 \pmod 6$, which forces $k = m^2$,
and the residue of $\prod(2a_i + 1)$ modulo 3 forces $m = c^3 q^2$ with
$\mu(q) = +1$ — a dice simulation becomes a lattice count under a hyperbola.
[Idempotents](/solutions/0407/) asks for the largest $a$ with
$a^2 \equiv a \pmod n$; since $a$ and $a-1$ are coprime, every prime power of
$n$ divides one or the other, so the idempotents are exactly the coprime splits
$n = d \cdot e$, and a per-$n$ search becomes a sweep over pairs.
[Largest Prime](/solutions/0659/) asks for the largest prime dividing two
*successive* terms of $n^2 + k^2$; a common divisor divides their difference
$2n + 1$, which pins $n \equiv -\tfrac12 \pmod p$, and substituting back leaves
the condition $p \mid 4k^2 + 1$ — a search over $n$ for every $k$ becomes the
largest prime factor of one polynomial value.
[A Polynomial Modulo the Square of a Prime](/solutions/0457/) asks for the least
root of $n^2 - 3n - 1$ modulo $p^2$; completing the square makes that a square
root of 13, found modulo $p$ and lifted to $p^2$ by one
[Hensel](https://en.wikipedia.org/wiki/Hensel%27s_lemma) step, and
[quadratic reciprocity](https://en.wikipedia.org/wiki/Quadratic_reciprocity)
turns "does 13 have a root modulo $p$?" into a lookup on $p \bmod 13$ — a scan
of $p^2$ candidates becomes a few modular powers per prime. A restatement can
also change the *kind* of collection being summed. [Fibonacci
Subwords](/solutions/1006/) sums over the $k+1$ distinct length-$k$ factors of
the Fibonacci word, a set that would need deduplicating if listed; reading the
factors off the arcs of a rotation of the circle makes them the $k+1$
consecutive windows of one explicit, almost-palindromic word, and a sum over
sliding windows is a running total, linear in a small state vector and so
walkable block by block along the Zeckendorf decomposition of $k$. Each
restatement is a line of algebra, and each one is where the problem actually
gets solved.

**Translate into a known object.** Sometimes the restated problem is one that
mathematics has already solved under another name. The Diophantine-reciprocal
problems [108](/solutions/0108/) and [110](/solutions/0110/) become
[divisor counting](https://en.wikipedia.org/wiki/Divisor_function).
[Cross Flips](/solutions/0331/) is
[Lights Out](https://en.wikipedia.org/wiki/Lights_Out_(game)), and so linear
algebra over $\mathbb{F}_2$. [Chandelier](/solutions/0768/) is divisibility by
a [cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial).
[March of the Penguins](/solutions/1010/) is a walk through Young diagrams,
whose complete marches are
[standard Young tableaux](https://en.wikipedia.org/wiki/Young_tableau) counted
by the [hook length formula](https://en.wikipedia.org/wiki/Hook_length_formula) —
so about $10^{16}$ partitions collapse to $n$ hook-length exponents.
[Removing Bits](/solutions/0882/) is a partisan game whose positions are
[surreal numbers](https://en.wikipedia.org/wiki/Surreal_number) that simply
add — and [Gold and Silver Coin Game](/solutions/0860/) is the same theory in
disguise, blue-red Hackenbush on stalks, where "fair" means total value zero
and the generating function $x^4 + x + x^{-1} + x^{-4}$ factors as
$x^{-4}(1+x^3)(1+x^5)$, leaving a single binomial sum.
[Long Products](/solutions/0452/) counts $n$-tuples by product, which is the
summatory function of the multiplicative $d_n$ — constant on primes, and so
exactly what a Min_25 sieve sums in sublinear time.
[Eulercoin](/solutions/0700/)'s record lows of $na \bmod m$ are the subtractive
[Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm) run on
two records, so the coins arrive in logarithmically many steps.
[Summation of Summations](/solutions/0739/) applies a linear operator, so the
answer is a weighted sum of the inputs; the statement's 429 is a
[Catalan number](https://en.wikipedia.org/wiki/Catalan_number), the tell that
the weights are ballot numbers. Sometimes the object only shows its name after a
change of variables. [Exploding Sequence](/solutions/0492/) iterates the quadratic
map $a \mapsto 6a^2 + 10a + 3$, whose terms double in length every step;
completing the square with $b = 6a + 5$ turns it into $b \mapsto b^2 - 2$, the
doubling rule of a [Lucas sequence](https://en.wikipedia.org/wiki/Lucas_sequence),
so the $n$-th term is $V_{2^{n-1}}$. Modulo a prime $p$ that index only matters
modulo the order of the underlying root, which divides $p - 1$ or $p + 1$, so
$10^{15}$ iterations become two short exponentiations.
The theory that comes with a name can include a *bound*. [$47$-smooth Triangular
Numbers](/solutions/0581/) looks like an open-ended search, since nothing in the
statement says where smooth pairs $n, n+1$ stop; rewriting $n(n+1)$ as a Pell
equation $x^2 - 2q\,y^2 = 1$, with $q$ ranging over the $2^{15}$ products of
primes up to 47, brings in
[Størmer's theorem](https://en.wikipedia.org/wiki/St%C3%B8rmer%27s_theorem) and
Lehmer's refinement, which say only the first two dozen powers of each
fundamental solution can qualify — the search is finite because a theorem says
so, not because a loop happened to stop finding things. And the known object can
lie outside arithmetic altogether. [Solving
$\mathcal{I}$-equations](/solutions/0674/) asks for the least common value of two
nested polynomial expressions, but the operator is injective on pairs of
non-negative integers, so two expressions are equal exactly when their trees
match after substitution: the equation is first-order
[unification](https://en.wikipedia.org/wiki/Unification_(computer_science)),
solved with union-find and an occurs check, and monotonicity makes the least
value the most general unifier with every free variable set to zero. No number is
ever searched. Once the object has a name, its theory comes with it, and the code
implements a theorem rather than a search.

**Turn it into squares, then read the sign.** A quadratic condition often
becomes a statement about squares, and the sign between them decides which
theory applies. Triangular numbers are the easiest case, since
$8T_a + 1 = (2a+1)^2$. [Expressing an Integer as the Sum of Triangular
Numbers](/solutions/0621/) and [Finding Triangles](/solutions/0955/) both open
with that line, then part ways. Problem 621 fixes one of its three terms and
lands on a *sum*, $(2b+1)^2 + (2c+1)^2 = 8m + 2$. The number of ways to write a
number as a sum of two squares is a
[multiplicative function](https://en.wikipedia.org/wiki/Multiplicative_function)
read off the prime factorisation, so the inner search is never run: it is
*counted*, and more than $10^{13}$ pairs become a few million factorisations.
In problem 955 the steps between triangles run $1, 2, 3, \dots$, so the next
triangle is the least $j$ with $t(x) + t(j) = t(y)$. Here the squares land on
opposite sides, and a *difference* factors: the equation becomes
$x(x+1) = pq$ with $p = y - j$ and $q = y + j + 1$. The least $j$ is the factor
pair nearest the trivial one, so the walk
[jumps from triangle to triangle](/blogs/takeaway/jump-to-the-next-event) at
the cost of one divisor scan each, and the terms between are never generated.
Problem 621 still has to factor every value of a quadratic, and that is cheaper
than it sounds, because values of a polynomial factor better together than
apart. A prime divides such a value only on at most two residue classes of the
index, so one [sieve over the primes](/blogs/technique/polynomial-sieve)
replaces all the separate factorisations.

**Keep only what the answer reads.** Most inputs carry far more information
than the question uses, and finding the part it uses shrinks the state.
[$250250$](/solutions/0250/) needs each $k^k$ only modulo 250, so a quarter of
a million elements collapse to a census of 250 residues.
[A Huge Binomial Coefficient](/solutions/0365/) never forms a number with nine
billion digits: the squarefree modulus splits by the
[Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
into prime fields, where Lucas' theorem answers digit by digit.
[Digital Root Clocks](/solutions/0315/) shows the per-prime saving depends only
on the last two digits and the digit sum, so two small tables replace any
simulation. [Rounded Square Roots](/solutions/0255/) reads $n$ only through
$\lceil n/x \rceil$, so whole intervals of $n$ share a path and are processed
as one. [Freshman's Product](/solutions/0778/) has more sequences than a
number with a million digits, but its carry-free product reads each decimal
place independently and each input only through its digit there — a ten-entry
histogram per place, raised to the $R$-th power under multiplication modulo 10.
[Fibonacci Tree Game](/solutions/0400/) plays on a tree with a 2000-digit node
count, but once the game is recognised as Green Hackenbush, a move matters only
through the [Grundy value](https://en.wikipedia.org/wiki/Sprague%E2%80%93Grundy_theorem)
it leaves at the root, and those values stay small. So the moves are counted per
(level, target value), a few thousand values per level, and no node is ever visited.
A huge *parameter* can be state the answer does not read, too.
[The Millionth Number with at Least One Million Prime Factors](/solutions/0615/)
looks impossible because $k = 10^6$, but the early members of the list are
overwhelmingly powers of two: each odd prime that replaces a two multiplies the
value by at least $3/2$, so beyond about 36 prime factors every early member
shares a common power of two. Dividing it out maps the head of the list for $k$
onto the head of the list for 36 in order, and $k$ is gone — the answer is an
ordinary 64-bit enumeration times one modular power.
Sometimes the state shrinks to a single bit. In [Pairwise Coin-Tossing
Game](/solutions/0605/) consecutive rounds share exactly one player, so the
only thing that matters after a round is whether its winner plays the next one;
the game is a two-state Markov chain, the ending round has a simple geometric
law, and each player's chance is an arithmetico-geometric series summed in
closed form.
The question to ask is: *what is this result actually a function of?*
The answer is the real state space.

**Search the answer's structure, not the input range.** When the inputs are too
many to visit, walk the thing that generates the answers instead.
[Prime Factors of $n^{15}+1$](/solutions/0421/) exchanges the order of
summation — instead of factorising $10^{11}$ huge numbers, it asks each of
the primes below $10^8$ how many $n$ it divides, which group theory answers
in $O(1)$. [Euler's Totient Function Equals 13!](/solutions/0248/) inverts
$\varphi$ by enumerating factorisations of the target into
$p^{a-1}(p-1)$ pieces — a few hundred candidate primes rather than tens of
billions of candidate $n$. [Modular Cubes, Part 2](/solutions/0272/) and
[Perfection Quotients](/solutions/0241/) likewise build $n$ from the prime
factors the condition demands, and
[Sums of Digit Factorials](/solutions/0254/) inverts a chain of digit functions
through the
[factorial number system](https://en.wikipedia.org/wiki/Factorial_number_system)
rather than iterating it. [$5$-smooth Totients](/solutions/0516/) reads the
totient's product formula backwards: $\varphi(n)$ is 5-smooth only when $n$ is a
Hamming number times distinct primes $q$ with $q - 1$ Hamming, so $10^{12}$
candidates become a few thousand Hamming numbers and the square-free products of
a few hundred primes. For a Diophantine equation the generator is a
parametrisation. [Asymmetric Diophantine Equation](/solutions/0764/) reads
$16x^2 + y^4 = z^2$ as a Pythagorean triple with one leg a multiple of 4 and the
other a square; Euclid's formula, plus the fact that coprime factors of a square
are squares, yields two two-parameter families in which $z$ grows like a fourth
power — so $z \le 10^{16}$ means about $3 \times 10^7$ coprime parameter pairs,
each one a solution, and no search over $(x, y)$ or square test anywhere. Construction beats filtering whenever the answers are
sparse and the space is not.

**Divide out the scale.** When a condition survives multiplying every variable
by a constant, the solutions lie on rays, and there is a standard way to find
them: [write the ratio in lowest terms](/blogs/takeaway/parametrise-by-reduced-ratio)
and let coprimality push every denominator into the scale factor. What comes out
is a complete family in which each solution appears exactly once.
[Tangent Circles](/solutions/0510/) reduces tangency to
$1/\sqrt{r_C} = 1/\sqrt{r_A} + 1/\sqrt{r_B}$, which forces $r_A/r_B$ to be the
square of a reduced fraction $u/v$; since $u + v$ is coprime to $uv$, $(u+v)^2$
must divide the scale, and the three radii become $t$ times fixed polynomials in
$u$ and $v$. [Prime Triples and Geometric Sequences](/solutions/0518/) does the
same to a common ratio $q/p$, giving $(kp^2, kpq, kq^2)$.
[Panaitopol Primes](/solutions/0291/) takes out $g = \gcd(x, y)$ from
$(x^4 - y^4)/(x^3 + y^3)$; after cancelling, the denominator is coprime to what
is left of the numerator, so it too must divide $g$. The step is the same each
time. What differs is what the problem does with the scale, and that decides the
program. In problem 510 the radii scale freely, so a family's multiples sum as a
triangular number, and looping over them would bring back the linear cost the
parametrisation removed. In problem 518 the members must be one below a prime,
which breaks the scaling, so $k$ stays a live variable and the program filters
it, testing $kq^2 - 1$ first because every $p$ shares that result. In problem 291
the scale disappears altogether. The value has become a product of three positive
integers, $k(a-b)(a^2+b^2)$, and it must be prime, so $k = 1$ and $a - b = 1$. A
primality condition is weak until a factorisation appears, and then it is an
equation: two variables with no stated bound collapse to one, and the answers are
the primes among $n^2 + (n+1)^2$.

**Trade the condition for a sum that collapses.** A congruence condition, "the
total is $0 \bmod n$", is awkward to count directly but easy to *filter*: the
average of $\omega^{js}$ over the $n$-th roots of unity is $1$ when $n \mid s$
and $0$ otherwise. The
[roots-of-unity filter](https://en.wikipedia.org/wiki/Root_of_unity#Orthogonality)
turns the count into $n$ sums with no condition at all, and the reduction pays
when those sums turn out to be nearly all alike. In
[Subset Sums](/solutions/0635/) the modulus is prime, so every non-trivial root
is primitive and the $p-1$ non-trivial terms are *identical*, each worth $q$;
the count becomes $\bigl(\binom{qp}{p} + q(p-1)\bigr)/p$, a single binomial
coefficient per prime. [Quadruple Congruence](/solutions/0875/) filters the zeros
of an eight-variable quadratic form the same way; each term becomes a power of a
[quadratic Gauss sum](https://en.wikipedia.org/wiki/Quadratic_Gauss_sum), whose
*modulus* is classical even though its value is not, and $n^8$ tuples collapse
into a Dirichlet convolution summed with a totient sieve. For a small modulus
the filter needs no complex numbers at all. [$B$-Trivisible
Numbers](/solutions/0967/) counts the $n$ whose prime factors up to a bound sum
to $0 \bmod 3$, and it carries all three remainders at once in the
[group ring](/blogs/technique/group-ring-arithmetic) $\mathbb{Z}[C_3]$: a formal
$x$ with $x^3 = 1$, whose elements are just triples of integers. The condition
becomes the multiplicative function $x^{S(n)}$, which a Dirichlet convolution
turns into a sum over square-free divisors. One more reduction finishes it. The
small primes' share of that function is periodic in $n$, so a prefix table
answers it in $O(1)$, and only the large primes go through the divisor sum, which
cuts it from about $7 \times 10^7$ terms to $1.4 \times 10^6$. The transform
costs a sum over $n$ roots and buys a structure that counting never exposes.

## How to reason about it

Reach for a reduction whenever the quantities you are about to iterate over are
*related by a rule* rather than being arbitrary data — a linear constraint, an
ordering, a recurrence, a symmetry, a counting structure. The tell is that you
can write down an equation the answer must satisfy. Spend the algebra there: each
equation you solve is a loop you delete, a dimension you drop, or a bound you
tighten. A second tell is a search space that dwarfs the answer — $2^{669}$
subsets when only the totals matter, as in
[Prime Subset Sums](/solutions/0249/), or $40!$ fill orders when the state that matters is a
step count, a segment count and two boundary flags, as in [Tidying Up A](/solutions/0253/). That gap means
the problem has a smaller state hiding in it, and finding that state is the
reduction.

Three cautions keep the habit honest:

- **Know when to stop.** Not every problem closes into a formula, and forcing one
  produces fragile, wrong code. [Counting Rectangles](/solutions/0085/) reduces
  the *count* to $T(H)\cdot T(W)$ but still searches grid shapes for the one
  nearest a target, because that outer question has no closed form — the honest
  reduction is partial, and that is fine. A reduction that removes one loop of
  three is already a win. Most of the later reductions end the same way — in a
  smaller computation, not a formula: a generating-function DP over board
  positions in [Overtakes](/solutions/0996/), a four-wide table over depth in
  [Pythagorean Tree](/solutions/0395/).
- **Derive, then verify.** An algebraic reduction is only as good as its
  derivation, and an off-by-one in a bound or a dropped term fails silently. Keep
  the brute-force version as an oracle and check the two against each other on
  small inputs — [Number Spiral Diagonals](/solutions/0028/) ships exactly that,
  running an $O(N^2)$ spiral simulation under `--show` purely to confirm its
  formula. The check matters most when the reduction is a guess.
  [Chandelier](/solutions/0768/) is the warning: "every balanced set is a union
  of regular polygons" is a theorem when $n$ has at most two prime factors and
  false for 360, which has three — already in $\mathbb{Z}_{30}$ there are 525
  balanced 6-subsets against 495 polygon unions. [Overtakes](/solutions/0996/)
  shows the honest version: its characterisation was conjectured, then checked
  against a breadth-first brute force for every $n \le 7$ before any fast code
  was trusted. [Summation of Summations](/solutions/0739/) found its ballot-number
weights by simulating unit vectors, and
[Gold and Silver Coin Game](/solutions/0860/) checked its surreal values by
playing every arrangement out for $n \le 7$. A reduction often predicts something
checkable on its own: [problem 615](/solutions/0615/)'s says that past the threshold,
raising $k$ by one exactly doubles the unreduced answer, and a brute force confirms
it does. Beyond brute-force range, a reduction can still be tested at full size.
[Problem 621](/solutions/0621/) has a second route it never computes through:
Gauss's theorem ties its count to a class number, and the class number formula
predicts the sieve's result to about two parts per million.
[Problem 967](/solutions/0967/) has a free parameter, the point where small primes
end and large ones begin, and moving it rearranges the whole calculation without
changing the answer. And small edge cases hide in correct derivations too: in
  [Euler's Totient Function Equals 13!](/solutions/0248/) the factor contributed
  by the prime 2 at exponent 1 is $1$, so a search that stops when the residual
  target reaches 1 silently drops half the solutions.
- **Mind the arithmetic you introduce.** Reductions multiply before they divide
  and can form intermediates far larger than the answer — an overflow risk in C,
  and a reason to keep the algebra in exact integers (compute $c = S - a - b$, not
  $\sqrt{a^2+b^2}$) so equality checks stay reliable. See
  [exact-arithmetic-for-equality](/blogs/takeaway/exact-arithmetic-for-equality).
  An alternating inclusion–exclusion sum, as in
  [Twenty-two Foolish Primes](/solutions/0239/), cancels catastrophically, so it
  stays in exact integers until the final division. Reducing modulo the
  requested digits is safe only when the reduced formula uses addition and
  multiplication alone — true of the subset-sum table in
  [Prime Subset Sums](/solutions/0249/), and something to check rather than
  assume once a division appears. [Pairwise Coin-Tossing
  Game](/solutions/0605/) shows the fix when it does: its closed form must be
  reduced to lowest terms, the common factor $g$ need not be invertible modulo
  $10^8$, so the product is computed modulo $10^8 g^2$ and divided *exactly* by
  $g^2$ — and $g$ itself comes from $\gcd(n, 2^n \bmod n - 1)$, never from the
  thirty-million-digit $2^n - 1$.

The discipline underneath all of it is order of operations, in the human sense:
do the mathematics *first*. A loop written before the algebra is a loop you will
optimise later; a loop written after it is often a loop you never write at all.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0029](/solutions/0029/) — Distinct Powers
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0045](/solutions/0045/) — Triangular, Pentagonal, and Hexagonal
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0071](/solutions/0071/) — Ordered Fractions
- ● [0079](/solutions/0079/) — Passcode Derivation
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0082](/solutions/0082/) — Path Sum: Three Ways
- ● [0085](/solutions/0085/) — Counting Rectangles
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0091](/solutions/0091/) — Right Triangles with Integer Coordinates
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0106](/solutions/0106/) — Special Subset Sums: Meta-testing
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0109](/solutions/0109/) — Darts
- ● [0110](/solutions/0110/) — Diophantine Reciprocals II
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0113](/solutions/0113/) — Non-bouncy Numbers
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0127](/solutions/0127/) — abc-hits
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0140](/solutions/0140/) — Modified Fibonacci Golden Nuggets
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0144](/solutions/0144/) — Laser Beam Reflections
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0147](/solutions/0147/) — Rectangles in Cross-hatched Grids
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0154](/solutions/0154/) — Exploring Pascal's Pyramid
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0158](/solutions/0158/) — Lexicographical Neighbours
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0163](/solutions/0163/) — Cross-hatched Triangles
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0190](/solutions/0190/) — Maximising a Weighted Product
- ● [0195](/solutions/0195/) — $60$-degree Triangle Inscribed Circles
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0207](/solutions/0207/) — Integer Partition Equations
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0210](/solutions/0210/) — Obtuse Angled Triangles
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0222](/solutions/0222/) — Sphere Packing
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0227](/solutions/0227/) — The Chase
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0232](/solutions/0232/) — The Race
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0235](/solutions/0235/) — An Arithmetic Geometric Sequence
- ● [0236](/solutions/0236/) — Luxury Hampers
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0240](/solutions/0240/) — Top Dice
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0243](/solutions/0243/) — Resilience
- ● [0245](/solutions/0245/) — Coresilience
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0248](/solutions/0248/) — Euler's Totient Function Equals 13!
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0250](/solutions/0250/) — $250250$
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0253](/solutions/0253/) — Tidying Up A
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0297](/solutions/0297/) — Zeckendorf Representation
- ● [0301](/solutions/0301/) — Nim
- ● [0309](/solutions/0309/) — Integer Ladders
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0331](/solutions/0331/) — Cross Flips
- ● [0346](/solutions/0346/) — Strong Repunits
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0395](/solutions/0395/) — Pythagorean Tree
- ● [0400](/solutions/0400/) — Fibonacci Tree Game
- ● [0407](/solutions/0407/) — Idempotents
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0443](/solutions/0443/) — GCD Sequence
- ● [0452](/solutions/0452/) — Long Products
- ● [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0492](/solutions/0492/) — Exploding Sequence
- ● [0493](/solutions/0493/) — Under the Rainbow
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0510](/solutions/0510/) — Tangent Circles
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0516](/solutions/0516/) — $5$-smooth Totients
- ● [0518](/solutions/0518/) — Prime Triples and Geometric Sequences
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ● [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ● [0621](/solutions/0621/) — Expressing an Integer as the Sum of Triangular Numbers
- ● [0635](/solutions/0635/) — Subset Sums
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0659](/solutions/0659/) — Largest Prime
- ● [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ● [0694](/solutions/0694/) — Cube-full Divisors
- ● [0700](/solutions/0700/) — Eulercoin
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0768](/solutions/0768/) — Chandelier
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0779](/solutions/0779/) — Prime Factor and Exponent
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0862](/solutions/0862/) — Larger Digit Permutation
- ● [0872](/solutions/0872/) — Recursive Tree
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0882](/solutions/0882/) — Removing Bits
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0938](/solutions/0938/) — Exhausting a Colour
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0951](/solutions/0951/) — A Game of Chance
- ● [0955](/solutions/0955/) — Finding Triangles
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [0996](/solutions/0996/) — Overtakes
- ● [1000](/solutions/1000/) — Problem $1000$
- ● [1006](/solutions/1006/) — Fibonacci Subwords
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
