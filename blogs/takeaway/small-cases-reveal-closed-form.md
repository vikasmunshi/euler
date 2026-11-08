<!-- tags: [small-cases-reveal-closed-form] -->
<!-- status: final 2026-11-03T07:32Z -->
# Small cases reveal a closed form

Some problems hide a simple rule behind a definition that is expensive to evaluate even once.
Deciding whether one room can be tiled is a search. Settling one pirate vote needs the whole game
below it. Seating one hotel guest needs every guest before them. Valuing one ternary game needs a
canonical-form engine, and deciding one blackboard game needs every smaller budget. Growing one geometric
configuration to day 16 needs about $4^{16}$ cells. Deriving the rule from first principles can
take far longer than the problem is worth. The faster route is to solve the small instances
*exhaustively*, lay the results out so the pattern can show itself, read a closed-form
characterisation off the table, and check it against the brute force well beyond the range it was
read from. The closed form then replaces the expensive definition. Sometimes it is a single
formula in $n$. More often it is a membership test, a piecewise rule, a short vector or a
construction, and it becomes the cheap core of a quite different algorithm at full scale.

## The idea: an oracle, a table, a rule, a check

The method has four parts, and each one matters:

1. **An honest oracle.** The brute force has to be *right*, not fast. In practice that means the
   literal definition, at most with pruning or a reformulation that is provably safe, and exact
   arithmetic. Problem 256's checker is a row-by-row
   [transfer-matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) search over half-mat
   labels that throws away any row creating a four-mat corner. Problem 950 simulates the pirate
   vote move by move. Problem 336 replays the turntable rule on every permutation, and 523 runs its
   odd restart-from-the-front sort on all $n!$ permutations, averaging in exact rationals. Problem
   340 evaluates its McCarthy-style nested recursion literally, with memoisation, and 359 seats
   the first forty thousand guests greedily, one at a time. Problem 335 sows beans round a ring
   of bowls until the start state returns, 555 evaluates its generalised McCarthy function with
   memoisation, 628 tries every pawn placement on boards up to $9 \times 9$, and 711 solves its
   blackboard game by the plain win/lose recursion over (budget, parity) states. Problem 963
   runs a small [canonical-form](/blogs/technique/canonical-form) engine that removes dominated
   options and bypasses reversible ones, so equal games come out identical. Problem 957 shows the
   reformulated kind. A projective map and a logarithm turn its three pencils of lines into three
   families of parallel lines on an integer lattice. The simulation then runs on exact integers
   (point by point, then on grids with [FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform)
   convolution), and because it reproduces the statement's first two days, the model can be
   trusted.
2. **A table with the right axes.** A pattern can only be seen if the data is laid out along the
   parameters that drive it. Problem 256 lists the untileable lengths *for each width*, and in that
   layout the bad lengths fall into bands that shrink step by step and then vanish. Problem 950
   tabulates the senior pirate's outcome against $n$, which separates an early phase where every
   proposal passes from a later one where successes are separated by runs of failures. Problem 963
   writes each game value as a number plus a combination of infinitesimals. Once those
   coefficients are tabulated against the number's ternary digits, each one depends on a simple
   feature of the digit string. In 340, $F(n) - n$ looks erratic against $n$, but indexed by
   blocks of width $a$ counted *down* from the threshold it is constant within each block and
   grows by a fixed step from one block to the next. Sometimes the right axis is a *residual*. In
   957 the raw counts grow like $16^n$ and show nothing. Split into a pencil size and a triple
   count, and with the known leading term subtracted from the triple count, the remainder is small
   and regular. Sometimes it is a *derived* quantity. 359's occupants look irregular, but the sums
   of neighbouring rooms on a floor run through consecutive squares. And when the map is
   [linear](https://en.wikipedia.org/wiki/Linear_map), the right input is a unit vector. 739's
   repeated prefix-sum operation sends the starting sequence to a fixed weighted sum of its terms,
   so feeding it one unit at a time tabulates the weights directly, with the sequence factored out.
   Sometimes it is a *representation*. 711's winning starts mean nothing in decimal, but written
   in binary they fall into two rigid bit patterns, just as 963's coefficients only line up
   against ternary digits. Sometimes it is a *subfamily*. 335's cycle length $M(x)$ is irregular
   over all $x$, but the problem only asks about $x = 2^k + 1$, and tabulated along $k$ alone the
   values grow by a clean factor that tends to $4$. And sometimes the stated instance is
   *degenerate*. The McCarthy 91 function behind 555 is the constant $91$ on its whole lower
   range, which shows nothing. Free its three parameters and the outputs cycle with period
   $k - s$; the famous constant is just the period-one case. When the given instance looks too
   simple to learn from, vary the parameters it fixes.
3. **A rule stated as code.** Write the guess as a function, such as `is_tatami_free(a, b)`, the
   closed form for the early phase, `game_key(x)`, or a constructor that builds every member. A
   pattern only becomes testable once it is a function you can call.
4. **A check on data the guess never saw.** Run the rule against the oracle on a range well beyond
   the one it was read from. 256's band rule was compared with the exhaustive search on every
   width up to $16$ and every length up to $90$. 963's decomposition was checked against the
   engine for every number up to $10^6$. 950's full method was compared with direct simulation on
   300 random small instances and the statement's three values. 336's construction produced
   exactly the same sets as the filter for $n = 3, \dots, 9$. 340's formula was compared with the
   recursion on 400 random small parameter triples, 523's with the permutation brute force for
   every $n \le 8$, exactly as rationals, and 359's with every one of the roughly 40 000 rooms the
   simulation seated. 957's recurrence was fixed by ten simulated terms, and three more confirmed
   it. 711's two families were read from the game table and checked against every start up to
   $1100$, and 335's formula against the simulation up to $4097$ bowls.

## Where the rule comes from

You don't always have to see the pattern yourself. There are four routes, and it pays to try
them roughly in order of cost:

- **Look it up.** Feed the small values to the [OEIS](https://oeis.org/). Problem 276 counts
  primitive integer triangles by perimeter. Before the gcd is imposed, the count for each
  perimeter is [Alcuin's sequence](https://oeis.org/A005044), which already has a closed form,
  $\operatorname{round}(n^2/48)$ for even $n$. That rounding hides a correction with period 12,
  so its prefix sum is a polynomial plus a periodic term, and each one costs $O(1)$. Recognising a
  known sequence is still this takeaway. The literature supplied the formula, and the brute-force
  enumeration (the statement gives no worked values) is what makes it safe to use.
- **Fit it.** When the values are suspected to satisfy a linear recurrence,
  [Berlekamp–Massey](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm) finds the
  shortest one. Solve its characteristic polynomial and you have the closed form. That is how 957
  goes from thirteen simulated days to an $O(1)$ formula: a residual sequence of order five whose
  roots are $\pm 1$, $\pm 2$ and $4$. This is where the
  [recurrence takeaway](/blogs/takeaway/small-cases-reveal-recurrence) shades into this one. The
  recurrence is only the intermediate step, and the closed form is what ships. It is worth
  shipping because $n$ is too large to step through, or, as here, because the oracle itself
  cannot reach $n$. Often the table's growth tells you the *shape* before any algorithm runs.
  335's consecutive ratios creep up towards $4$, which suggests a combination of powers
  $a \cdot 4^k + b \cdot 3^k + c \cdot 2^k + \dots$. A few terms fix the coefficients, and every
  remaining term is a free check. Thirteen tabulated values pinned down a three-term sum of
  exponentials, and the requested total became three geometric series.
- **Recognise it, then explain it.** Some sequences of small values are familiar on sight. 336's
  maximix counts for $n = 3, \dots, 9$ come out as $1, 2, 6, 24, \dots$, which is $(n-2)!$. A
  factorial is a strong hint that a sequence of independent choices lies underneath. Here it is
  the turntable rule run backwards: each placement can be undone in $n-2-i$ distinct ways.
  739's tell is the statement's own example: with every starting term $1$ the process ends at
  $429$, a [Catalan number](https://en.wikipedia.org/wiki/Catalan_number). Catalan totals point to
  [ballot numbers](https://en.wikipedia.org/wiki/Bertrand%27s_ballot_theorem) as the individual
  weights, and the unit-vector table confirms it, because a unit can only reach the apex along a
  lattice path that never crosses a diagonal. In 523 the per-insertion costs come out
  $1, 2, 4, 8, \dots$, and the recurrence behind them, $T(s) = 1 + \sum_{i<s} T(i)$, is the
  explanation of why they double.
- **Derive it, then let the oracle audit it.** Sometimes a short argument gets you there first,
  and the brute force turns from a source into an auditor. 374's exchange arguments say the best
  distinct-part partition is a run of consecutive integers with at most one hole. 628 claims a
  rook path is blocked exactly when some anti-diagonal is full of pawns, which turns counting
  closed positions into a short inclusion–exclusion over reversed corner blocks. 561 factorises
  its divisor-pair count and takes 2-adic valuations through a thicket of parity cases. Each of
  these is plausible on paper, and each could be wrong in one quiet case. So the small instances
  still run: every $n \le 69$ for 374, every board up to $9 \times 9$ for 628, and every divisor
  pair for small primorial powers in 561. The route is different, but the table and the check
  are the same.

## What the closed form buys

The payoff is rarely just "the answer is this formula". Most of the time, an $O(1)$ or $O(\log)$
rule lets you **change algorithms**:

- In **256**, a constant-time test for one room turns the problem into a divisor-style count. I
  run it as a sieve in reverse: walk every width and every band, and add one to the count for each
  area the band produces. That never factorises anything, and it never tiles anything.
- In **276**, the closed-form count of *all* triangles up to a perimeter is the cheap inner
  function of a [Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula)
  over floor quotients. Only the formula makes each of the $O(\sqrt N)$ evaluations cheap.
- In **336**, the bijection that explains $(n-2)!$ also works as a *generator*. Instead of
  filtering $n!$ permutations through a simulation, the solution builds the $(n-2)!$ maximix
  arrangements directly, one splice per level, and sorts them. When the count explains itself,
  the explanation usually gives you an enumeration as well.
- In **711**, the rule is a description of a family rather than a test, and a family can be
  *summed* without being listed. Grouping the sparse winners by their lowest isolated bit turns
  the total into geometric and
  [arithmetico-geometric](https://en.wikipedia.org/wiki/Arithmetico-geometric_sequence) series,
  so a bound of $2^{12\,345\,678}$ (or $2^{10^{18}}$) costs a few modular exponentiations.
- In **555**, the formula becomes something to *reason about*. Solving $M(n) = n$ against the
  per-$n$ closed form shows that fixed points exist exactly when $k - s$ divides $s$, and then
  they fill a whole window. So the problem never looks for fixed points at all: it sums
  arithmetic progressions over (gap, multiple) pairs, with the inner sum over multiples itself in
  closed form.
- In **359**, an $O(1)$ occupant formula (two rooms apart the squares telescope, leaving a
  difference that is linear in the room number, so odd rooms are quadratic) turns a simulation of
  $10^{27}$-sized guests into a loop over the divisors of $N$: a few hundred evaluations.
- In **739**, closed-form weights turn an $n$-round triangle of prefix sums into one sum of $n$
  terms. The closed form also shapes how that sum is computed: rewriting each binomial as a
  running prefix product times a suffix product leaves a single modular inverse at the end.
- In **950**, the early phase is a closed form, and the later phase's runs of failures have a
  length that can be computed. So the backward induction jumps a whole run per step instead of a
  pirate per step, and reaches $n = 10^{16}$ in a few dozen jumps.
- In **963**, a value becomes a short integer vector, and two games are equal exactly when their
  vectors are equal. Equality of games, which is a question about play, becomes equality of
  tuples, which can be grouped and counted.
- In **957** the closed form *is* the solution: a handful of big-integer operations, where the
  simulation it replaces grows fourfold per day. The divisibility of the numerator by the
  formula's denominator is asserted at run time, a cheap check that the formula is still
  consistent. **340** is the same: per-block constants summed over whole blocks plus one partial
  block give an $O(1)$ answer for a threshold near $6 \times 10^{17}$, where the recursion could
  not finish a single call. **523**'s formula is a sum of thirty terms, and **335**, **561** and
  **684** each finish in microseconds.
- "Closed" does not have to mean $O(1)$. **628** reduces to $(n-3)$ times the
  [left factorial](https://en.wikipedia.org/wiki/Left_factorial) plus a constant, and **374**'s
  block sums come down to $j!$ and $j!\,H_j$. Neither sequence has a closed form of its own, so
  the solution is one linear pass of a running product, over $n$ in 628 and over the
  $\sqrt{2N}$ blocks in 374. Reducing to a well-understood sequence with a cheap recurrence is
  still the win. What the pass replaces is a search over $n!$ placements or over partitions.

## How to reason about it

Reach for this when one instance is costly but *structured*: small parameters, a definition that
is clear but slow, and a hint in the statement (a smallest example, a family of named cases, a
couple of worked values) that the behaviour is regular. Compared with the sister takeaway
[small cases reveal the recurrence](/blogs/takeaway/small-cases-reveal-recurrence), the
difference is in what you are looking for. There the structure promises a recurrence and the data
supplies its coefficients. Here nothing promises a formula, so the check carries more weight.

- **Look for a predicate or a construction, not just a count.** A rule that says *which* inputs
  behave one way is far more reusable than a formula for *how many* do. 256's band rule drives the
  sieve directly, and the same rule as a per-room test drives the `--show` listing and the
  cross-check. 336's count of $(n-2)!$ was only the clue. What the solution uses is the
  construction behind it.
- **Strip what you already know.** Divide out or subtract the dominant term before you look for a
  pattern. 957's triple count is asymptotically $\tfrac{7}{12}$ of the squared pencil size, and
  its residual reveals the recurrence where the raw numbers would not. In the same way, 276's
  rounding is easiest to handle as an exact quadratic plus a bounded periodic correction, and
  340's values only line up once the identity $n$ is subtracted. If the process is linear, factor
  the input out entirely, as 739 does, and look for a pattern in the weights alone.
- **Only read the table where the oracle is finished.** A truncated simulation has a frontier
  whose values are not final yet. 359's last room on each floor is still open when the simulation
  stops, so its current occupant may not be the final one. The check skips those rooms. Counting
  them would make a correct formula look wrong, or fit a wrong one.
- **Keep the oracle's arithmetic exact.** A rule checked against floating-point output is only
  checked to within the rounding. 523 compares rationals, and that matters at the end as well:
  $E(10) = 115.725$ lies exactly on a rounding half, so the shipped solution sums exact fractions
  and rounds in integers.
- **Expect regimes and periods.** Closed forms often hold piecewise: below a threshold, inside a
  band, in an early phase, or modulo a small period (276's 12, 957's $(-1)^n$ and $(-2)^n$
  terms). Find the boundary from the data and make the code branch on it explicitly. Don't extend
  the first regime's formula past where it was checked.
- **Check the branches the problem never asks about.** A derivation with case splits can be
  right on the one case the statement exercises and wrong on the others, and then the next
  similar problem inherits the bug. 561's statement fixes an odd $m$, but its brute force covers
  both parities of $m$, and an extra test case drives the even branch through the shipped code.
  555's general $m < p$ branch, where a window straddles zero, is never reached by the main
  input. The lopsided cross-check cases exist to exercise it, because an off-by-one there would
  otherwise go unnoticed.
- **Shape the formula for the arithmetic it will run in.** At full scale a closed form is
  usually evaluated modulo a prime, and its argument may be astronomically large. 684's
  $s(n) = (r+1)\,10^q - 1$ needs $q = \lfloor n/9 \rfloor$ where $n$ runs over Fibonacci numbers of up to nineteen digits, so
  the solution carries the Fibonacci recurrence modulo $9p$ and $9(p-1)$. Both residues give
  $r = n \bmod 9$, and dividing out the 9 gives $q$ modulo $p$ for the linear term and modulo
  $p - 1$ for the exponent, by
  [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem). 374 carries
  $j!\,H_j$, an integer (a
  [Stirling number of the first kind](https://en.wikipedia.org/wiki/Stirling_numbers_of_the_first_kind)),
  in place of the harmonic number itself, so the main loop never needs a modular inverse. 335's
  modulus $7^9$ is not prime, but the geometric series only divide by 2 and 3, which are units
  modulo $7^9$. Before you commit to a form, check which divisions it needs.
- **Make the table bigger than you think you need.** A rule read from twenty cases often has a
  second-order term that only shows up at fifty. A recurrence of order $d$ needs $2d$ terms just to
  be determined, so only the terms after those count as evidence. Keep generating until the
  pattern is boring.
- **Explain it if you can, but test it regardless.** Problem 950's phases and 336's bijection come
  with an argument for why they look the way they do. 340's block formula was spotted first and
  then proved by induction on the block index, and 523's was derived (the sort is insertion sort
  in disguise) and still checked. The same goes for 374's exchange arguments and 628's
  anti-diagonal claim. Problem 256's bands, 711's bit patterns and 555's per-$n$ formula are,
  here, experimental facts that were never proved. All of them are equally safe *only because*
  they were checked against the oracle. That's
  [calibrating theory on known answers](/blogs/takeaway/calibrate-theory-on-known-answers) with
  answers you made yourself.
- **Keep the oracle in the solution directory.** The scratch checker is the evidence for the
  rule. Leave it beside the solution (the `brute_force.py` of 276, 335, 336, 359, 374, 523, 555,
  628 and 711, the `brute.py` of 340, 561 and 739, and 957's `simulate.py` and `pencils.py`), so
  a later reader can re-run it rather than take the pattern on trust.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0335](/solutions/0335/) — Gathering the Beans
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0340](/solutions/0340/) — Crazy Function
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ● [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0523](/solutions/0523/) — First Sort I
- ● [0555](/solutions/0555/) — McCarthy 91 Function
- ● [0561](/solutions/0561/) — Divisor Pairs
- ● [0628](/solutions/0628/) — Open Chess Positions
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ● [0711](/solutions/0711/) — Binary Blackboard
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0767](/solutions/0767/) — Window into a Matrix II
- ● [0782](/solutions/0782/) — Distinct Rows and Columns
- ● [0892](/solutions/0892/) — Zebra Circles
- ● [0950](/solutions/0950/) — Pirate Treasure
- ● [0957](/solutions/0957/) — Point Genesis
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
