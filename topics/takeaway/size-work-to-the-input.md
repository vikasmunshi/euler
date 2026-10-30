<!-- tags: [size-work-to-the-input] -->
<!-- status: final 2026-10-29T12:08Z -->
# Size the work to the input

These solutions all take a size as their one argument — an n, a ceiling N, a
target — and every one of them has to decide how much scaffolding to build: how
far to sieve, how big a table to allocate, how high to let a search run. The trap
that lurks in all of them is the *magic constant*: a bound hard-coded to whatever
made the sample input pass. The habit that runs through the problems below is the
opposite — derive the bound from the argument, build the structure inside
`solve()` sized to that bound, and let the work scale with the input rather than a
guess.

## The idea

A solver is a function of its input, and so is the work it should do. The size of
every sieve, table, cache, and search loop is itself a *function of the argument*;
the job is to write that function down instead of picking a number. Four shapes
recur.

**A bound that is the argument.** The simplest case: the input already names the
range. [Summation of Primes](/solutions/0010/) is asked for the sum of the primes
up to `max_num`, and its
[Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes) runs
to exactly `max_num` — no more, no less. [Circular Primes](/solutions/0035/)
sieves to the given `max_limit`. There is nothing clever here beyond the
discipline of not writing `10_000_000` where `max_num` belongs.

**A bound the input *implies*.** Often the argument does not name the range
directly, and a little mathematics turns it into one. [10001st
Prime](/solutions/0007/) is asked for the $n$-th prime but must sieve over
integers, so it leans on the
[prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem)'s
estimate $p_n < n \ln n$ (for $n$ past a small threshold) and sizes the sieve to
$n \ln n$. The ceiling is still computed from the input — just through a
closed-form bound rather than the raw value. Deriving the right ceiling is a small
[closed-form](/topics/takeaway/closed-form-over-iteration) step in its own right.

A sharper version of the same move divides the limit by the *smallest thing the
rest of the answer could be*. [Modular Cubes, Part 2](/solutions/0272/) sums the
$n \le L$ built from exactly $k$ prime-like factors times a free cofactor. Since
those $k$ factors multiply to at least the product of the $k$ smallest candidates
($7 \cdot 9 \cdot 13 \cdot 19 \cdot 31$ for $k = 5$), the cofactor table only
needs to reach $L$ divided by that product, and the prime list only $L$ divided by
the smallest $(k-1)$-factor product. Both sizes come from the two arguments, and
both come out orders of magnitude below $L$ — the structure of the problem, read
off the input, is what makes the scaffolding small.

Sometimes the input implies a size far below its own magnitude because the answer
depends on only a few *distinct values*. [Square Root Smooth
Numbers](/solutions/0668/) counts up to $N = 10^{10}$, and after counting the
complement it needs only the prime-counting function $\pi$ at the quotients
$\lfloor N/k \rfloor$. There are only about $2\sqrt{N}$ distinct quotients — the
idea behind [quotient blocking](/topics/technique/quotient-blocking) — so the
tables are two arrays of length $\lfloor\sqrt{N}\rfloor + 1$, about $10^5$ entries
each, rather than a sieve of $10^{10}$. Both ports allocate them at run time from
the argument: NumPy arrays in Python, `malloc` in C, with no static array sized to
the main case. The one number they hang on is the
[integer square root](https://en.wikipedia.org/wiki/Integer_square_root), computed
exactly (`math.isqrt`, or a floating estimate corrected by a step), because a
`sqrt` rounded the wrong way would leave the table one entry short.

**A bound that shrinks as the work proceeds.** Sometimes the right size is not
known up front but tightens as you go. [Largest Prime Factor](/solutions/0003/)
trial-divides only up to $\sqrt{r}$, where $r$ is the *remaining* cofactor — and
each time it peels off a factor it recomputes that ceiling from the smaller $r$.
The search limit tracks the live state of the input, so a large prime factor found
early collapses the rest of the search instead of grinding on to a fixed
$\sqrt{n}$.

**A size chosen to balance two costs.** The first three shapes are about
*correctness* — the bound below which the answer lives. The fourth is a size that
correctness does not fix at all, only cost. [Bounded Sequences](/solutions/0319/)
needs the [Mertens function](https://en.wikipedia.org/wiki/Mertens_function) at
every quotient $\lfloor n/d \rfloor$; it sieves the Möbius function directly up to
some $K$ and recurses above it. Any $K$ gives the same answer, but sieving costs
about $K$ while the recursion costs about $n/\sqrt{K}$, and the two meet at
$K = n^{2/3}$ — so that is where the sieve stops, not at $n$.
[Cardano Triplets](/solutions/0251/) has the same shape in a different dress: it
counts with one walk while a parameter $b_1$ is small (where each step yields many
solutions) and a different walk once it is large (where most steps would yield
none), and balancing the two costs puts the switch at $b_1 \approx L^{1/4}$. In
both the split point is a formula in the input, derived from the cost model, not
a number tuned on the main case.

## How to reason about it

Ask, of every table dimension and loop bound: *what input made me write this
number?* If the answer is "the sample", it is a bug waiting for a bigger input.
Two forces push the same way.

- **Correctness.** A bound hard-coded to a fixed maximum is right only for inputs
  below it. Size it to the argument and the one solution answers the whole family
  of inputs the harness can throw at it — the test cases deliberately run several
  sizes per problem for exactly this reason. They catch more than short tables:
  the C port of Cardano Triplets formed a product that wrapped 64 bits only above
  $L \approx 1.9 \times 10^8$, invisible at the main input and exposed by the
  larger benchmark cases. Values grow with the input too, so [integer
  width](/topics/takeaway/watch-integer-width) is part of the size.
- **Honest measurement.** Build the structure *inside* `solve()`, dimensioned from
  the arguments — never at module import with a fixed ceiling. The benchmark runs
  `solve()` repeatedly under `--runs=N` and times the repeats, so a sieve built
  once at import is paid for once and then free, flattering the number you report.
  A fresh, input-sized build on every call is what makes the measured time the
  real time. This is the companion of [precomputing once and
  reusing](/topics/takeaway/precompute-once-reuse): both keep the expensive
  structure local to `solve()`; this takeaway adds that its *size* must come from
  the input.

A couple of cautions earn their keep:

- **An estimated bound needs a margin, or a check.** When the ceiling is an
  approximation — $n \ln n$, a growth-rate guess — make sure it over-estimates
  across the whole input range, or detect the miss and grow. An under-sized sieve
  silently returns the wrong answer rather than failing loudly.
- **Do not over-size out of caution, either.** A bound padded to "surely big
  enough" wastes the very memory and time you were trying to spend precisely.
  Matching the work to the input means matching it — not swapping one arbitrary
  constant for a larger one. Bounded Sequences is the vivid case: sieving all the
  way to $n = 10^{10}$ is "obviously enough" and also infeasible, while the
  balanced $n^{2/3}$ is a few million entries.
- **A cost-balanced split is free to test.** Because any crossover gives the same
  answer, moving it is a built-in cross-check: Cardano Triplets was run with its
  switch anywhere from $1$ to $1601$, and Bounded Sequences with its sieve at
  $n^{1/2}$, $n^{0.55}$ and $n^{0.75}$; the totals never moved, and the timings
  bottomed out where the cost model said they would. If shifting the split changes
  the answer, one side of it is wrong.
- **Clamp the formula at the small end.** An asymptotic size like $n^{2/3}$ can
  round to something degenerate on tiny inputs, so Bounded Sequences takes
  `min(n, max(1000, n ** (2/3)))` — the formula for the real input, and a floor
  below which a plain sieve to $n$ is simply cheaper than any recursion.

The through-line: the input is not merely the data your solution reads, it is the
*specification for how much work to do*. Read the size off the argument — directly,
through a bound, or through a cost model that splits the work between two methods —
build to it, and the solution comes out both correct across the range and honest
on the clock.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0003](/solutions/0003/) — Largest Prime Factor
- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0011](/solutions/0011/) — Largest Product in a Grid
- ● [0013](/solutions/0013/) — Large Sum
- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0026](/solutions/0026/) — Reciprocal Cycles
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0062](/solutions/0062/) — Cubic Permutations
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0122](/solutions/0122/) — Efficient Exponentiation
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0161](/solutions/0161/) — Triominoes
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0166](/solutions/0166/) — Criss Cross
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0230](/solutions/0230/) — Fibonacci Words
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
- ● [0304](/solutions/0304/) — Primonacci
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0668](/solutions/0668/) — Square Root Smooth Numbers
- ● [0692](/solutions/0692/) — Siegbert and Jo
- ● [0710](/solutions/0710/) — One Million Members
- ● [0755](/solutions/0755/) — Not Zeckendorf
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0974](/solutions/0974/) — Very Odd Numbers

<!-- /problems -->
