<!-- tags: [constraint-propagation] -->
<!-- status: final -->
# Constraint propagation

[Constraint propagation](https://en.wikipedia.org/wiki/Constraint_propagation) means using what the
constraints already imply to shrink each variable's set of possible values, *before and between* guesses.
A search that only checks a candidate once it is complete explores everything. A search that propagates
lets every decision rule out values elsewhere, and often finishes without guessing at all. The three solved
problems below are [constraint satisfaction](/topics/domain/constraint-satisfaction) problems of very
different kinds, a digit string, a Sudoku grid and a set of Diophantine unknowns, and in each one the
speed comes from moving the constraints *into* the domains instead of testing them at the leaves.

## The idea — domains, constraints, a fixpoint

Every variable carries a **domain**, the values still possible for it. Every **constraint** links a
few variables. Propagation repeatedly applies one rule: *if a value in one domain has no support in
the domains it is linked to, delete it.* Each deletion can remove the support of values elsewhere, so the
rule runs until nothing changes, a **fixpoint**. Then exactly one of three things is true:

- some domain is **empty**, so the current branch is a contradiction and can be abandoned now;
- every domain is a **single value**, so the problem is solved;
- otherwise a **guess** is needed: branch on one variable, propagate again, and
  [backtrack](/topics/technique/backtracking) on contradiction.

How hard you propagate is a dial. *Forward checking* only removes a placed value from its immediate
neighbours. Full [arc consistency](https://en.wikipedia.org/wiki/Local_consistency#Arc_consistency)
keeps deleting until every remaining value is supported. The more you propagate, the more work
each node costs, and the fewer nodes there are.

## Three problems, three strengths of propagation

**43, sub-string divisibility: order the variables so constraints bite early.** A 0–9 pandigital
$d_1 \dots d_{10}$ must have $d_2d_3d_4$ divisible by 2, $d_3d_4d_5$ by 3, and so on up to $d_8d_9d_{10}$ by 17.
The windows overlap, so fixing one window fixes two digits of the next. The public solution starts
from the most selective constraint: only 44 three-digit multiples of 17 have distinct digits, and these
seed the search. It then builds *right to left*, so each prepended digit closes exactly one window
and is checked immediately:

```python
for next_digit in (d for d in "0123456789" if d not in current_number):
    next_num: str = next_digit + current_number
    if int(next_num[:3]) % divisor != 0:
        continue
```

This is the lightest form of propagation, a check as soon as a constraint's last variable is bound, but
starting from the most constrained end makes it enough. The whole search tries about 650 digits,
not $10!$ arrangements.

**96, Su Doku: two solutions, two strengths.** The folder holds the progression in one place.

- `s0` is **forward checking** with the minimum-remaining-values (MRV) heuristic. Each empty cell
  keeps a candidate set. Placing a digit removes it from the cell's row, column and box peers. The
  search always branches on the cell with the fewest candidates. It propagates one step and then stops.
- `s2` is **propagation to a fixpoint**, after
  [Norvig](https://norvig.com/sudoku.html). `eliminate` removes a candidate and then applies two rules
  recursively. A *naked single* (a cell down to one candidate) removes that digit from its 20 peers.
  A *hidden single* (a digit with one place left in a unit) is assigned there. An empty domain returns
  `False` at once. Propagating the clues alone solves 40 of the fifty puzzles, and the other ten
  need only a short search.

The domains in `s2` are 9-bit masks, which is why it also carries
[Hamming weight](/topics/technique/hamming-weight) and
[find first set](/topics/technique/find-first-set): `bit_count() == 1` detects a single,
and the position of that bit is the digit. (`s1`, the
[exact cover](/topics/technique/exact-cover) formulation with
[dancing links](/topics/technique/dancing-links), is a third route: there the propagation is
the covering and uncovering of columns.)

**236, luxury hampers: propagate before you enumerate.** The problem asks for ratios $m = p/q$ under
which a table of spoilage counts shows [Simpson's paradox](/topics/domain/simpsons-paradox). Naively it is a
search over five pairs of integer counts for every candidate $m$. The solution never runs that search.
It derives constraints that shrink the domains first. Integrality of every $b_i$ restricts each $a_i$ to the
multiples of a fixed step. The supply caps bound how many such multiples fit. Five products pool to three
by their reduced ratio. The coefficients of the remaining equation must mix signs, which caps $m$. A
bound on the numerator $p$ follows from the same divisibility argument. After that, a candidate is
rejected as soon as any pool's domain is empty. Only about 4,400 ratios survive to the last step, a
bounded [Diophantine equation](/topics/domain/diophantine-equation) in three unknowns solved with the
[extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm). Here propagation is
algebra worked out in advance, not a runtime loop, but the logic is the same: delete the values that
cannot be supported, then search what is left.

## Python and C

- **43**: the same recursion. Python's strings and generator expressions (`d not in current_number`,
  `int(next_num[:3])`) become explicit `char` buffers, a linear scan for used digits, and arithmetic
  on three characters in C. The search is small enough that neither version needs a used-digit bitmask.
- **96 `s0`**: Python builds a *new* list of `(row, col, set)` triples per guess, so undoing a guess is
  free. C does the same with `malloc` + `memcpy` of a `Cell` array, sorts it with `qsort` for MRV, and adds
  an explicit fail-fast scan for a drained cell. Python discovers that one level later instead.
- **96 `s2`**: the propagation is line-for-line identical. Both copy the 81-mask state before a guess,
  `values[:]` in Python and an `int trial[81]` + `memcpy` in C. The bit operations map directly:
  `bit_count()` ↔ `__builtin_popcount`, and `bit_length()` ↔ `__builtin_ctz(x) + 1` for a single set bit.
- **236**: same algorithm. The pooled coefficients reach about $10^{20}$, so C builds them in
  `__int128` and divides out their common gcd before the Euclidean step. It also needs a floored-division
  helper because C's `/` truncates toward zero, and the interval clipping depends on the rounding direction.

## How to reason about it

- **Start where the constraints are tightest.** Seed with the most selective constraint (43's
  multiples of 17) and branch on the variable with the smallest domain (MRV in 96).
- **Check a constraint as soon as its last variable is bound.** That is the minimum. Anything more is
  propagation proper.
- **Make domains cheap to copy.** Backtracking over propagated state needs either an undo log or a copy
  per guess. A small array of bitmasks makes copying trivially cheap.
- **Fail on an empty domain immediately.** Most of the pruning comes from that one check.
- **Some propagation is best done on paper.** In 236 the strongest deletions come from algebra, which
  turns a search over integer tables into a scan over a few thousand ratios.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0096](/solutions/0096/) — Su Doku
- ● [0236](/solutions/0236/) — Luxury Hampers

<!-- /problems -->
