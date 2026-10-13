<!-- tags: [small-cases-reveal-closed-form] -->
<!-- status: final -->
# Small cases reveal a closed form

Some problems hide a simple rule behind a definition that is expensive to evaluate even once.
Deciding whether one room can be tiled is a search. Settling one pirate vote needs the whole game
below it. Valuing one ternary game needs a canonical-form engine. Deriving the rule from first
principles can take far longer than the problem is worth. The faster route is to solve the small
instances *exhaustively*, lay the results out so the pattern can show itself, read a closed-form
characterisation off the table, and check it against the brute force well beyond the range it was
read from. The closed form then replaces the expensive definition. Usually it is a membership
test, a piecewise formula or a short vector, not a single number, and it becomes the cheap core
of a quite different algorithm at full scale.

## The idea: an oracle, a table, a rule, a check

The method has four parts, and each one matters:

1. **An honest oracle.** The brute force has to be *right*, not fast. In practice that means the
   literal definition, at most with pruning that is provably safe, and exact arithmetic. Problem
   256's checker is a row-by-row
   [transfer-matrix](https://en.wikipedia.org/wiki/Transfer-matrix_method) search over half-mat
   labels that throws away any row creating a four-mat corner. Problem 950 simulates the pirate
   vote move by move. Problem 963 runs a small
   [canonical-form](/topics/technique/canonical-form) engine that removes dominated options and
   bypasses reversible ones, so equal games come out identical.
2. **A table with the right axes.** A pattern can only be seen if the data is laid out along the
   parameters that drive it. Problem 256 lists the untileable lengths *for each width*, and in that
   layout the bad lengths fall into bands that shrink step by step and then vanish. Problem 950
   tabulates the senior pirate's outcome against $n$, which separates an early phase where every
   proposal passes from a later one where successes are separated by runs of failures. Problem 963
   writes each game value as a number plus a combination of infinitesimals. Once those
   coefficients are tabulated against the number's ternary digits, each one depends on a simple
   feature of the digit string.
3. **A rule stated as code.** Write the guess as a function, such as `is_tatami_free(a, b)`, the
   closed form for the early phase, or `game_key(x)`. A pattern only becomes testable once it is a
   function you can call.
4. **A check on data the guess never saw.** Run the rule against the oracle on a range well beyond
   the one it was read from. 256's band rule was compared with the exhaustive search on every
   width up to $16$ and every length up to $90$. 963's decomposition was checked against the
   engine for every number up to $10^6$. 950's full method was compared with direct simulation on
   300 random small instances and the statement's three values.

## What the closed form buys

The payoff is rarely "the answer is this formula". The payoff is that an $O(1)$ or $O(\log)$
predicate lets you **change algorithms**:

- In **256**, a constant-time test for one room turns the problem into a divisor-style count. I
  run it as a sieve in reverse: walk every width and every band, and add one to the count for each
  area the band produces. That never factorises anything, and it never tiles anything.
- In **950**, the early phase is a closed form, and the later phase's runs of failures have a
  length that can be computed. So the backward induction jumps a whole run per step instead of a
  pirate per step, and reaches $n = 10^{16}$ in a few dozen jumps.
- In **963**, a value becomes a short integer vector, and two games are equal exactly when their
  vectors are equal. Equality of games, which is a question about play, becomes equality of
  tuples, which can be grouped and counted.

## How to reason about it

Reach for this when one instance is costly but *structured*: small parameters, a definition that
is clear but slow, and a hint in the statement (a smallest example, a family of named cases) that
the exceptions are rare and regular. Compared with the sister takeaway
[small cases reveal the recurrence](/topics/takeaway/small-cases-reveal-recurrence), the
difference is in what you are looking for. There the structure promises a recurrence and the data
supplies its coefficients. Here nothing promises a formula, so the check carries more weight.

- **Look for a predicate, not just a count.** A rule that says *which* inputs behave one way is
  far more reusable than a formula for *how many* do. 256's band rule drives the sieve directly,
  and the same rule as a per-room test drives the `--show` listing and the cross-check.
- **Expect regimes.** Closed forms often hold piecewise: below a threshold, inside a band, in an
  early phase. Find the boundary from the data and make the code branch on it explicitly. Don't
  extend the first regime's formula past where it was checked.
- **Make the table bigger than you think you need.** A rule read from twenty cases often has a
  second-order term that only shows up at fifty. Keep generating until the pattern is boring.
- **Explain it if you can, but test it regardless.** Problem 950's phases come with an argument
  for why they look the way they do. Problem 256's bands are, here, an experimental fact. Both are
  equally safe *only because* both were checked against the oracle. That's
  [calibrating theory on known answers](/topics/takeaway/calibrate-theory-on-known-answers) with
  answers you made yourself.
- **Keep the oracle in the solution directory.** The scratch checker is the evidence for the
  rule. Leave it beside the solution, so a later reader can re-run it rather than take the
  pattern on trust.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0276](/solutions/0276/) — Primitive Triangles
- ● [0950](/solutions/0950/) — Pirate Treasure
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
