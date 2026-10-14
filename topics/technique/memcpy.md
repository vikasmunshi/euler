<!-- tags: [memcpy] -->
<!-- status: final 2026-10-14T17:59Z -->
# memcpy

C arrays aren't values. You can't assign one array to another, you can't return one from a
function, and when you pass one to a function it decays to a pointer to its first element. So
whenever a C solution needs a second, independent copy of some state, it asks for the bytes to be
copied explicitly with [`memcpy`](https://en.cppreference.com/w/c/string/byte/memcpy). The
solutions here need that copy for five different jobs: to roll a pair of bignums forward (25),
to prepend a part to a partition (77), to build the next pool of operands (93), to give a
backtracking search a state it can throw away (96), and to swap a DP table for the next one (164).
This page is part of the language-idioms series. It covers the idiom, why these solutions use it,
and what it turns into in Python, where most of these copies don't happen at all.

## The idea

`memcpy(dst, src, n)` copies `n` **bytes** from `src` to `dst` and returns `dst`. It knows nothing
about types, so the caller supplies the byte count, almost always as `count * sizeof(element)` or
`sizeof array`. Two rules come with it:

- **The regions must not overlap.** If they might, use
  [`memmove`](https://en.cppreference.com/w/c/string/byte/memmove), which copies as if through a
  temporary. None of the solutions here need it: every copy goes into a separate buffer.
- **Both pointers must be valid, even when `n` is 0.** In C23 and earlier,
  `memcpy(NULL, NULL, 0)` is undefined behaviour. 96 guards its copy with `if (remaining_count > 0)` for exactly this reason,
  because a `malloc(0)` may return `NULL`.

In exchange, `memcpy` is the fastest copy the platform has. Compilers treat it as a builtin: a
small fixed-size copy becomes a few register moves, and a large one becomes a vectorised loop.
Writing the element loop by hand gains nothing.

The byte count is where the bugs are. These solutions use three forms, and each is right only in
its context:

| Form | Example | Right when |
|---|---|---|
| `sizeof array` | `memcpy(state, nxt, sizeof state)` (164) | the array is declared in this scope, not a parameter |
| `sizeof(Type)` | `memcpy(&a, &b, sizeof(BigInt))` (25) | copying one whole object |
| `count * sizeof(T)` | `memcpy(combined, rest, (size_t)rlen * sizeof(double))` (93) | copying a prefix of a buffer |

The trap in the first form is that `sizeof` applied to an array *parameter* gives the size of a
pointer, eight bytes, and the copy silently moves one or two elements. 96's `search(int values[81])`
avoids it by taking the size from its local `trial[81]` in both directions:
`memcpy(values, trial, sizeof(trial))`.

## Three shapes of copy

**Rolling state forward (25, 164).** 25 advances Fibonacci numbers held as `BigInt` structs of
200 base-10⁹ limbs: `tmp = a + b`, then `memcpy(&a, &b, …)` and `memcpy(&b, &tmp, …)`. 164 runs a
digit DP over a `long long state[10][10]` table, fills a fresh `nxt` for each new digit, and copies
it back with `memcpy(state, nxt, sizeof state)`. Both are the same pattern: the update needs the
old value while it writes the new one, so it writes into a second buffer and copies it over.

Two refinements apply. For 25 the `memcpy` isn't necessary, because **structs** are values in C
even though arrays aren't: `a = b;` copies the whole 1.6 KB, and the compiler checks the types,
which `memcpy` doesn't. Wrapping an array in a struct is the standard way to make it assignable.
And neither copy needs to happen at all: keep pointers to the buffers and rotate them
(`BigInt *t = a; a = b; b = c; c = t;`), so each step costs three pointer moves instead of a
copy. At these sizes the difference is not measurable, but rotating pointers is the habit to have
when the buffer is a megabyte.

**Building a longer array from a shorter one (77, 93).** 77's prime partitions are built
recursively: each partition of `n - p` becomes a partition of `n` with `p` in front. The C version
`malloc`s `len + 1` ints, writes `p` at index 0, and copies the sub-partition into
`new_parts + 1`. The pointer arithmetic places the block one slot along. 93 reduces a pool of
operands: it takes two values out, combines them with an operator, and recurses on the rest plus
the result. It copies `rest` into `combined` and sets the last slot. In both cases the copy builds
a new array that the recursion owns, while the source stays unchanged for the next iteration.

**Copy-before-mutate for backtracking (96).** A Sudoku search guesses a digit, propagates its
consequences, and has to undo all of it if the guess fails. Undoing a guess is hard; throwing a
copy away is easy. 96's first C solution copies its array of `Cell` records, removes the guessed
digit from the copy's peers, and recurses on the copy. The second copies the whole 81-cell
candidate-mask grid into a stack-local `trial[81]`, assigns into it, and on success copies the
solved `trial` back into the caller's grid with one more `memcpy`. A 324-byte copy per guess is
far cheaper than an undo log, and it can't get the undo wrong.

## The Python counterpart

Python variables are references to objects, so most of these copies disappear. The question in
Python is whether you are *sharing* an object or need a *copy* of it.

- **Immutable values don't need copying.** 25's Python is `a, b = (b, a + b)`. Integers are
  immutable and arbitrary-precision, so rebinding the names is all the roll-forward needs: there
  are no limbs to copy and no buffer to reuse. 164 is the same: `state = nxt` rebinds the name to
  the dict just built, and the next step builds a new one.
- **Concatenation makes a new sequence.** 77 writes `[n] + partition` and 93 writes
  `r + (a + b,)`. Both are 77's `malloc` + `memcpy` + write in one expression: CPython allocates
  the new list or tuple and copies the element references in, which is a `memcpy` of pointers
  internally.
- **Slicing is a shallow copy.** 96's second Python solution uses `trial = values[:]` where the C
  uses `memcpy(trial, values, sizeof(trial))`. It is safe because the elements are ints. For a list
  of lists, `grid[:]` copies only the outer list, and the rows are still shared. 96's first
  solution uses `copy.deepcopy(grid)` to keep the unsolved grid for `--show`, and
  `[row[:] for row in grid]` would do the same job for a 9×9 grid of ints at a fraction of the
  cost.
- **Sharing can replace copying.** 96's Python `update_possibilities` builds a new list of
  `(row, col, candidates)` tuples, but it reuses each unchanged candidate set rather than copying
  it, and replaces a changed one with `possibilities - {number}` rather than modifying it. This
  works because nothing modifies the sets: they are treated as immutable. The C version
  `memcpy`s every `Cell`, including each one's `possibilities[9]`, because its update edits the
  copies in place.

The trade-off is the reverse in each language. In C, a copy has to be asked for, and a missing one
shows up as two names writing the same memory. In Python, sharing is the default, and the bug is a
copy you thought you had made: `grid[:]` that should have been a deep copy, or a mutable default
that every call shares. The rule that works in both is the one 96 follows: decide which data a
step may modify, and make that data either a private copy or immutable.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0025](/solutions/0025/) — $1000$-digit Fibonacci Number
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0096](/solutions/0096/) — Su Doku
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit

<!-- /problems -->
