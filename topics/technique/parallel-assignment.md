<!-- tags: [parallel-assignment] -->
<!-- status: final 2026-10-14T17:46Z -->
# Parallel assignment

[Parallel assignment](https://en.wikipedia.org/wiki/Parallel_assignment) updates several
variables in one statement. Every right-hand side reads the *old* values, and only after that are
the new values written. The four solutions below use it for one job: stepping a linear recurrence
forward one term at a time. In each one the state is a handful of numbers, the next state is a
fixed linear function of the current one, and every new value depends on at least one value that
is being replaced in the same step. This page is part of the language-idioms series. It covers
what the idiom buys when you step a recurrence, why these solutions use it, and what the C
versions write instead. The Python mechanism itself (packing a tuple, unpacking it into targets,
the swap) is covered on the neighbouring [tuple assignment](/topics/technique/tuple-assignment)
page.

## The idea

A [linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients) has a
*state*: the last *k* terms of a scalar sequence, or a small vector of coupled quantities. It also
has a *step*: a matrix that maps one state to the next. To walk the sequence you apply the step
repeatedly. The step is a function of the whole state, so the natural code is one statement that
replaces the whole state:

```python
a, b = (b, a + b)            # Problem 25: Fibonacci, the state is a sliding window of two terms
```

Problem 25 keeps the window (F(i−1), F(i)) and steps it until F(i) reaches *n* digits. The
`(b, a + b)` on the right is the step matrix [[0, 1], [1, 1]] applied to (a, b), written out
directly. Write it as two statements and you get a bug that is easy to miss: `a = b; b = a + b`
sets `b` to twice the old `b`, because `a` was already overwritten. Fibonacci turns into
doubling, and the loop still finishes, just at the wrong index.

The other problems use the same idiom with two different state shapes:

| Problem | State | Step |
|---|---|---|
| [25](/solutions/0025/) | window of two [Fibonacci](/topics/domain/fibonacci-sequence) terms | `(a, b) → (b, a + b)` |
| [94](/solutions/0094/) | window of two side-length terms, a sign, and a running sum | `(s, s1, s2, m) → (s + p, s2, 4·s2 − s1 + 2m, −m)` |
| [138](/solutions/0138/) | a solution of the [Pell equation](/topics/technique/pells-equation) x² − 5y² = −1 | `(x, y) → (9x + 20y, 4x + 9y)` |
| [139](/solutions/0139/) | a solution of x² − 2y² = ±1 | `(x, y) → (x + 2y, x + y)` |

**Sliding windows (25, 94).** A scalar recurrence of order *k* keeps its last *k* terms. Each step
shifts the window by one place and computes one new term. Only one value is new arithmetic and the
rest are moves, but the moves are why sequential assignment fails: the new term reads the value
that the shift is about to overwrite. Problem 94 puts four things in one statement. Its
almost-equilateral triangles come from a Pell equation, and the two triangle families (the third
side one longer or one shorter) are merged into a single increasing sequence. To do that, the
window `s1, s2` carries a second-order recurrence, `m` flips sign each step to switch family, and
`s` adds up the perimeter computed in the previous iteration. Every item on the right reads the
old state, and the solution's comment says so.

**Coupled pairs (138, 139).** Here the state is a point (x, y) on a Pell conic, and each step
multiplies x + y√D by a fixed unit. For √2 the unit is 1 + √2, which gives (x + 2y, x + y). In
Problem 139 this produces the near-isosceles primitive triples whose "hole" in the tiling has side
1. For √5, Problem 138 multiplies by the *square* of the fundamental unit, 9 + 4√5. This skips the
solutions of the wrong sign and lands on x² − 5y² = −1 every time, which gives the isosceles
triangles whose height is one more or one less than the base. Both new coordinates read both old
ones, so neither can be written first. This is the case the idiom is built for.

In both shapes, one statement per step keeps the code next to the maths. Each assignment is one
row of the step matrix, so you can check it against the derivation line by line. The same
statement is also what you would square repeatedly to jump many steps with
[matrix exponentiation](/topics/technique/matrix-exponentiation) (or, for Fibonacci,
[fast doubling](/topics/technique/fibonacci-fast-doubling)). These four problems don't need that.
Pell solutions grow geometrically, so the number of steps is logarithmic in the bound, and walking
them one by one is already O(log N).

## The counterpart in C

C has no parallel assignment, so the hidden state tuple has to become named temporaries, and the
write-back order becomes the programmer's job. The four C versions show the three ways this
usually looks.

- **Coupled pair: one temporary per coordinate.** Problem 139 computes `nx = x + 2*y` and
  `ny = x + y`, then writes `x = nx; y = ny;`. Its comment gives the reason: *"Explicit temporaries
  because C lacks parallel assignment."* Problem 138 does the same with big integers, and there the
  cost shows. Each row of the step needs two scalar multiplies and an add into scratch `BigInt`s,
  plus a `bi_copy` back into `x` and `y` at the end, so every step moves whole limb arrays.
- **Sliding window: temporaries only for the new values, then shift in order.** Problem 94 puts
  only `new_s2` and `new_m` in temporaries. It updates `s` in place (it reads nothing else that
  changes), then writes `s1 = s2` *before* `s2 = new_s2`. The order of those two lines carries the
  correctness, and Python's single statement makes the order irrelevant.
- **Big-number window: rotate, or better, swap pointers.** Problem 25's C version hand-rolls a
  base-10⁹ `BigInt` and does `tmp = a + b`, then two `memcpy`s to shift. That is a three-way
  rotation, with each copy as large as the number. Python's `a, b = b, a + b` costs nothing
  beyond the addition because it only rebinds references. The C version could match that by
  keeping three buffers and rotating pointers to them instead of copying contents. That is the
  pointer form of parallel assignment.

Two ways *around* the temporary turn up in old C code, and neither is worth using. The first is
the arithmetic shift `b = a + b; a = b - a;`, which steps Fibonacci with no temporary but does an
extra subtraction and breaks on overflow. The second is the XOR swap. Both trade readability for
nothing, because an optimising compiler already turns `nx`/`ny` into register renaming.

Other languages sit between the two. Go (`a, b = b, a+b`), Ruby, Lua and Rust (since 1.59)
support parallel assignment directly. JavaScript gets it through
[array destructuring](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment)
(`[a, b] = [b, a + b]`), which allocates an array unless the engine optimises it away.

## How to reason about it

- **Write the state, then the step.** Before writing the loop, list exactly what the recurrence
  needs from one iteration to the next. That list goes on the left side of the parallel
  assignment, and the step goes on the right. If something the step reads isn't on the list, the
  state is incomplete.
- **Check each row for reads of things being replaced.** If a new value reads an old value that the
  same step also replaces, sequential code needs a temporary or a careful order. A shift
  (`s1 = s2`) is safe only if it comes *after* every read of the old `s1`.
- **Keep work that doesn't depend on the step outside the statement.** Problem 94 computes `p`
  from the *new* state on its own line after the update. Putting it inside the tuple would read the
  old state, which is a different and wrong quantity. The parallel statement is for the step and
  nothing else.
- **In C, say why the temporaries exist.** A `nx`/`ny` pair looks like something to clean up. A
  one-line comment, as in Problems 94 and 139, stops someone from "simplifying" it into the
  doubling bug.
- **For big values, think about what one assignment copies.** In Python, assignment only rebinds
  a name. In C, assigning a struct copies all of it. When the state is made of big integers, rotate
  pointers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0094](/solutions/0094/) — Almost Equilateral Triangles
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0139](/solutions/0139/) — Pythagorean Tiles

<!-- /problems -->
