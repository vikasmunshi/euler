<!-- tags: [continued-fraction] -->
<!-- status: final 2026-10-14T07:30Z -->
# Continued fraction

A [continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) writes a number as
$x = a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cdots}} = [a_0; a_1, a_2, \ldots]$, and the terms $a_k$
are simply the quotients of the Euclidean algorithm run on $x$. That sounds like a curiosity of
notation. It isn't, because the expansion answers the question every problem below asks in some
form: *which fractions are close to $x$, and in what order do they arrive?* The truncations, called
convergents, are the best rational approximations there are. Read a little differently, they are
neighbours in a [Farey sequence](/topics/domain/farey-sequence), and they are the corners of a path
through the [Stern–Brocot tree](/topics/domain/stern-brocot-tree). I find it pays to hold all three
pictures at once. A problem that looks like approximation, or counting, or a game, or "how many
steps does Euclid take", often turns out to be one of the other two.

## The expansion and its convergents

Expanding $x$ means taking the integer part and inverting what is left:
$a_k = \lfloor x_k \rfloor$, $x_{k+1} = 1/(x_k - a_k)$. For a rational $p/q$ this is exactly
`a, (p, q) = p // q, (q, p % q)`. That is the [Euclidean algorithm](/topics/technique/euclidean-algorithm),
so the expansion is finite and short. For $\sqrt{n}$ the state $x_k = (m_k + \sqrt n)/d_k$ stays
inside a small integer triple, and the expansion is periodic. Problem 64 counts periods by detecting
when that triple repeats, and problem 66 reads the fundamental solution of
[Pell's equation](/topics/technique/pells-equation) off the convergent at the end of one period.
Some numbers have patterned expansions: $e = [2; 1, 2, 1, 1, 4, 1, 1, 6, \ldots]$ (problem 65) and
$\sqrt 2 = [1; 2, 2, 2, \ldots]$ (problem 57). Those problems only ask you to generate the terms.

The convergents $p_k/q_k = [a_0; a_1, \ldots, a_k]$ do not need to be evaluated from the inside
out. A forward recurrence builds them in one pass, with exact integers:

```python
p0, q0, p1, q1 = 0, 1, 1, 0          # the seeds p_{-2}/q_{-2} = 0/1, p_{-1}/q_{-1} = 1/0
for a in terms:
    p0, q0, p1, q1 = p1, q1, a * p1 + p0, a * q1 + q0
```

Problem 57 is this loop with every $a = 2$. Its one-line update $(p, q) \to (p + 2q,\, p + q)$
just folds the two-step recurrence into a single step. Two facts about the recurrence carry the
rest of this page:

- **The determinant is $\pm 1$.** $p_k q_{k-1} - p_{k-1} q_k = (-1)^{k-1}$. So every convergent is
  in lowest terms, consecutive convergents fall on opposite sides of $x$, and the gap between them
  is exactly $1/(q_k q_{k-1})$.
- **Denominators grow at least like Fibonacci numbers.** The slowest case is all $a_k = 1$, the
  golden ratio. So there are only $O(\log N)$ convergents with $q \le N$; for $N = 10^{12}$ that is
  fewer than 60. Every algorithm here takes about $\log N$ steps for this reason.

## Farey neighbours

The [Farey sequence](https://en.wikipedia.org/wiki/Farey_sequence) $F_N$ lists the reduced
fractions in $[0, 1]$ with denominator at most $N$, in order. Its defining property is the same
determinant: $a/b < c/d$ are adjacent in some $F_N$ exactly when $bc - ad = 1$. Comparing that with
the identity above, **consecutive convergents are Farey neighbours.** And when two neighbours first
get split, as $N$ grows, the fraction that lands between them is their
[mediant](https://en.wikipedia.org/wiki/Mediant_(mathematics)) $(a + c)/(b + d)$.

That gives a concrete way to think about "the closest fraction to $x$ with denominator at most
$N$". In $F_N$, the number $x$ sits between two neighbours, one on each side. The best
approximation is whichever of the two is closer, so the job is to find the pair, not to search
$N$ denominators. Problem 71 is the simplest instance: it asks for the left Farey neighbour of
$3/7$. The continued fraction finds both neighbours in $O(\log N)$ steps, as the next section shows.

## The Stern–Brocot path

The [Stern–Brocot tree](https://en.wikipedia.org/wiki/Stern%E2%80%93Brocot_tree) starts from the
two "fractions" $0/1$ and $1/0$ and puts the mediant of every adjacent pair between them, level by
level. Each positive rational appears exactly once, in lowest terms. Pruning the tree to
denominators $\le N$ gives $F_N$ (restricted to $[0, 1]$). To locate $x$ in the tree, walk down
from $1/1$, going right while the current node is below $x$ and left while it is above. The
directions of that walk come in runs:

$$x = [a_0; a_1, a_2, \ldots] \quad\longleftrightarrow\quad R^{a_0}\, L^{a_1}\, R^{a_2}\, L^{a_3} \cdots$$

(for a finite expansion the last run is one shorter). **The run lengths are the partial
quotients.** Each node where the walk changes direction is a convergent. The nodes inside a run are
the [semiconvergents](https://en.wikipedia.org/wiki/Continued_fraction#Semiconvergents)
$(p_{k-1} + t\,p_k)/(q_{k-1} + t\,q_k)$, one mediant step at a time. So all three pictures
describe one object:

| Continued fraction      | Stern–Brocot tree           | Farey sequence                     |
|-------------------------|-----------------------------|------------------------------------|
| partial quotient $a_k$  | length of a run of R or L   | number of mediant splits on one side |
| convergent $p_k/q_k$    | node where the path turns   | neighbour of $x$ for a range of $N$ |
| semiconvergent          | node in the middle of a run | intermediate neighbour             |
| $\sum a_k$              | depth of the node           | —                                  |
| Euclid, one division    | a whole run, in one step    | skipping straight to the next turn |

Seen this way, several problems become easier to recognise:

- **Best approximations (problem 192).** The two Farey neighbours of $\sqrt n$ in $F_N$ are the last
  nodes on each side of $\sqrt n$ on its Stern–Brocot path whose denominator is still $\le N$. One
  of them is a convergent. The other is a semiconvergent, partway through the run that would
  overshoot $N$, and the bound tells you how far in: $t = \lfloor (N - q_{k-1}) / q_k \rfloor$. The
  only subtlety is the tie-break between the two. A semiconvergent with $t > a_{k+1}/2$ always beats
  the previous convergent, one with $t < a_{k+1}/2$ never does, and $t = a_{k+1}/2$ needs an exact
  comparison. Problem 591 asks the same "closest point under a bound" question about quadratic
  integers $a + b\sqrt d$ instead of fractions.
- **Counting Euclid's steps (problem 958).** The subtractive Euclidean algorithm on $(n, m)$ takes
  $\sum a_k - 1$ subtractions, and that number is the depth of $m/n$ in the Stern–Brocot tree.
  Minimising it means looking for the shallowest node with a given denominator, so the question
  becomes about partial quotients rather than about search.
- **The Calkin–Wilf tree (problem 175).** This tree holds the same rationals as Stern–Brocot, in
  bit-reversed order (see [Calkin–Wilf tree](/topics/domain/calkin-wilf-tree) and
  [Stern's diatomic sequence](/topics/domain/sterns-diatomic-sequence)). Walking a target fraction
  up to the root, each run of identical moves is again one division step. The binary expansion of
  the answer comes out run-length encoded, as a sequence of partial quotients, even when written in
  full it would run to millions of bits.

## Beyond approximation

The same structure turns up in problems that never mention fractions:

- **Lattice points under an irrational line.** A sequence like $\lfloor \alpha n \rfloor - \lfloor \alpha (n-1) \rfloor$
  is a [Sturmian word](https://en.wikipedia.org/wiki/Sturmian_word). Its self-similar structure is
  given by the expansion of $\alpha$: in problem 656 the palindromic prefix lengths are built from
  the convergent and semiconvergent denominators of $\sqrt\beta$. Summing over the lattice points
  below $y = \varphi x$, the boundary of the losing positions in problem 325, is a
  [floor sum](https://en.wikipedia.org/wiki/Floor_and_ceiling_functions) that reduces recursively,
  and the recursion follows Euclid's steps on the slope.
- **Arithmetic on expansions.** Problem 946 applies a Möbius map $(2\alpha + 3)/(3\alpha + 2)$ to a
  number known only by its terms. [Gosper's algorithm](https://perl.plover.com/classes/cftalk/INFO/gosper.txt)
  does this by streaming: it keeps a $2 \times 2$ integer matrix and emits an output term whenever
  the matrix's range of possible values has a settled integer part. It never forms $\alpha$ as a
  float.
- **Statistics of the terms.** For almost every $x$, the geometric mean of the $a_k$ tends to
  [Khinchin's constant](https://en.wikipedia.org/wiki/Khinchin%27s_constant). Problem 911 is about
  numbers that break that rule because their expansions are lacunary and highly structured.

## How to reason about it

Use the continued fraction when the problem involves **a rational approximation under a size
bound**, **a real number known only through its expansion**, or **a process that repeatedly
subtracts the smaller of two quantities from the larger**. The last one is Euclid in disguise, and
it is the easiest to miss.

It gives you logarithmic depth. A search over $N$ denominators becomes a walk of $O(\log N)$
convergents, and each run of identical tree moves becomes one division. All of it is exact integer
arithmetic: the determinant identity keeps every fraction reduced, and for $\sqrt n$ the expansion
never needs floating point.

The pitfalls are always the same few:

- **Floating point.** Expanding $\sqrt n$ or $\pi$ from a `double` gives correct terms for a while,
  then wrong ones with no warning. Use the integer recurrence for quadratic irrationals, and
  rational interval bounds for anything else.
- **The last convergent is not always the answer.** Under a bound, the best approximation can be
  a semiconvergent. Check the tie-break at $t = a/2$ exactly, never by comparing floats.
- **Off-by-one in the indexing.** Both the seeds $p_{-1}/q_{-1} = 1/0$ and the "last run is one
  shorter" rule are easy to get wrong by one. Check against a small case by hand, such as
  $7/2 = [3; 2]$ with path $RRRL$.
- **Subtracting one step at a time.** If a loop subtracts the same thing repeatedly, replace it
  with a division. A run of length $10^{12}$ is a single quotient.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0066](/solutions/0066/) — Diophantine Equation
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0192](/solutions/0192/) — Best Approximations
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0591](/solutions/0591/) — Best Approximations by Quadratic Integers
- ○ [0656](/solutions/0656/) — Palindromic Sequences
- ○ [0911](/solutions/0911/) — Khinchin Exceptions
- ● [0946](/solutions/0946/) — Continued Fraction Fraction
- ○ [0958](/solutions/0958/) — Euclid's Labour

<!-- /problems -->
