<!-- tags: [small-cases-reveal-closed-form] -->
<!-- status: final 2026-10-15T11:02Z -->
# Small cases reveal a closed form

Some problems hide a simple rule behind a definition that is expensive to evaluate even once.
Deciding whether one room can be tiled is a search. Settling one pirate vote needs the whole game
below it. Valuing one ternary game needs a canonical-form engine. Growing one geometric
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
   vote move by move. Problem 336 replays the turntable rule on every permutation. Problem 963
   runs a small [canonical-form](/topics/technique/canonical-form) engine that removes dominated
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
   feature of the digit string. Sometimes the right axis is a *residual*. In 957 the raw counts
   grow like $16^n$ and show nothing. Split into a pencil size and a triple count, and with the
   known leading term subtracted from the triple count, the remainder is small and regular.
3. **A rule stated as code.** Write the guess as a function, such as `is_tatami_free(a, b)`, the
   closed form for the early phase, `game_key(x)`, or a constructor that builds every member. A
   pattern only becomes testable once it is a function you can call.
4. **A check on data the guess never saw.** Run the rule against the oracle on a range well beyond
   the one it was read from. 256's band rule was compared with the exhaustive search on every
   width up to $16$ and every length up to $90$. 963's decomposition was checked against the
   engine for every number up to $10^6$. 950's full method was compared with direct simulation on
   300 random small instances and the statement's three values. 336's construction produced
   exactly the same sets as the filter for $n = 3, \dots, 9$. 957's recurrence was fixed by ten
   simulated terms, and three more confirmed it.

## Where the rule comes from

You don't always have to see the pattern yourself. There are three routes, and it pays to try
them in order of cost:

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
  [recurrence takeaway](/topics/takeaway/small-cases-reveal-recurrence) shades into this one. The
  recurrence is only the intermediate step, and the closed form is what ships. It is worth
  shipping because $n$ is too large to step through, or, as here, because the oracle itself
  cannot reach $n$.
- **Recognise it, then explain it.** Some sequences of small values are familiar on sight. 336's
  maximix counts for $n = 3, \dots, 9$ come out as $1, 2, 6, 24, \dots$, which is $(n-2)!$. A
  factorial is a strong hint that a sequence of independent choices lies underneath. Here it is
  the turntable rule run backwards: each placement can be undone in $n-2-i$ distinct ways.

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
- In **950**, the early phase is a closed form, and the later phase's runs of failures have a
  length that can be computed. So the backward induction jumps a whole run per step instead of a
  pirate per step, and reaches $n = 10^{16}$ in a few dozen jumps.
- In **963**, a value becomes a short integer vector, and two games are equal exactly when their
  vectors are equal. Equality of games, which is a question about play, becomes equality of
  tuples, which can be grouped and counted.
- In **957** the closed form *is* the solution: a handful of big-integer operations, where the
  simulation it replaces grows fourfold per day. The divisibility of the numerator by the
  formula's denominator is asserted at run time, a cheap check that the formula is still
  consistent.

## How to reason about it

Reach for this when one instance is costly but *structured*: small parameters, a definition that
is clear but slow, and a hint in the statement (a smallest example, a family of named cases, a
couple of worked values) that the behaviour is regular. Compared with the sister takeaway
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence), the
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
  rounding is easiest to handle as an exact quadratic plus a bounded periodic correction.
- **Expect regimes and periods.** Closed forms often hold piecewise: below a threshold, inside a
  band, in an early phase, or modulo a small period (276's 12, 957's $(-1)^n$ and $(-2)^n$
  terms). Find the boundary from the data and make the code branch on it explicitly. Don't extend
  the first regime's formula past where it was checked.
- **Make the table bigger than you think you need.** A rule read from twenty cases often has a
  second-order term that only shows up at fifty. A recurrence of order $d$ needs $2d$ terms just to
  be determined, so only the terms after those count as evidence. Keep generating until the
  pattern is boring.
- **Explain it if you can, but test it regardless.** Problem 950's phases and 336's bijection come
  with an argument for why they look the way they do. Problem 256's bands are, here, an
  experimental fact. All of them are equally safe *only because* they were checked against the
  oracle. That's
  [calibrating theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers) with
  answers you made yourself.
- **Keep the oracle in the solution directory.** The scratch checker is the evidence for the
  rule. Leave it beside the solution (276's and 336's `brute_force.py`, 957's `simulate.py` and
  `pencils.py`), so a later reader can re-run it rather than take the pattern on trust.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0359](/solutions/0359/) — Hilbert's New Hotel
- ● [0950](/solutions/0950/) — Pirate Treasure
- ● [0957](/solutions/0957/) — Point Genesis
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
