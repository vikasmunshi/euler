<!-- tags: [list-comprehension] -->
<!-- status: final -->
# list comprehension

A [list comprehension](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
`[expr for x in iterable if cond]` builds a list in a single expression: one output element for
each input element that passes the filter. In Euler code it is the usual way to build a **table**,
whether that is parsed input, a list of candidates, or the initial state of a sieve or DP grid.
The reason is that most of these tables are a function of something that already exists. The six
solutions below all use one. They are also useful for the opposite lesson, because each has a
spot where a generator expression or a plain `for` loop does the job better. All but 181 are
public, so their code can be quoted. This page belongs to the language-idioms series, so it also
covers what each comprehension becomes in the C translation.

## The idea

A comprehension says *what* the list holds, not *how* to append to it. Python can then size and
fill the list without a name, an `.append` lookup, or an index variable. Since
[PEP 709](https://peps.python.org/pep-0709/) (3.12), comprehensions are inlined into the
enclosing function, so you no longer pay for a hidden function call either. In practice, here are
the shapes that keep coming back.

**Parse into a table.** Problem 18 turns the triangle text into rows with a nested comprehension.
The outer one walks the lines and the inner one walks the numbers on each line:

```python
return [[int(num) for num in line.split(" ")] for line in text.splitlines() if line != ""]
```

The `for` clauses read in the same order as the nested loops they replace, outermost first. The
trailing `if` drops the blank line left by the final newline. Problem 59 does the flat version,
`[int(x) for x in text.split(",")]`, and then builds its key slices as one comprehension of
strided slices: `[encrypted[i::key_length] for i in slices_range]`.

**Fold one row from the row below it.** Problem 18's DP replaces each row with a new row computed
from the one beneath:

```python
triangle[-2] = [v + max(triangle[-1][i], triangle[-1][i + 1]) for i, v in enumerate(triangle[-2])]
```

The comprehension fits because the new row depends only on the *old* rows. Nothing in the
expression reads a value that the same comprehension has already written.

**Filter candidates.** Problem 23 collects its abundant numbers with
`[i for i in range(12, limit + 1) if sum_proper_divisors(i) > i]`. This is a filter written as a
list, and the list is needed because the next step indexes into it twice.

**Initialise state.** Problem 73's Möbius sieve starts from `[i * n // d for i in range(len_data)]`,
and problem 181's 2-D knapsack starts from `[[0] * (cols + 1) for _ in range(rows + 1)]`. The
second one matters more than it looks. `[[0] * (cols + 1)] * (rows + 1)` creates `rows + 1`
references to *one* list, so every write lands in every row. The comprehension evaluates
`[0] * (cols + 1)` once per row, which gives each row its own list.

## Where a generator or a loop serves better

The tag is just as much about where these solutions *stop* using comprehensions.

- **The result is consumed once: use a generator.** Problem 23 sums its non-abundant numbers with
  `sum(i for i in range(1, limit + 1) if not is_abundant_sum[i])`, and problem 59 scores and sums
  through `sum(... for ...)` and `"".join(... for ...)`. A
  [generator expression](/topics/technique/generator) gives the same syntax without building the
  list in memory. Problem 59's final line also shows that chained `for` clauses flatten a list of
  strings: `sum(ord(c) for s in decrypted for c in s)`.
- **Except when the consumer materialises it anyway.** Problem 38 writes
  `"".join([str(i * x) for i in range(1, n + 1)])` with brackets. `str.join` needs the full
  sequence before it can size its result, so a generator passed to it gets turned into a list
  internally. Passing the list directly is slightly faster, not slower. This is the one place where
  the brackets are actually the better choice.
- **The loop needs to stop early: write the loop.** Problem 23 marks pairwise sums with a nested
  `for` that `break`s as soon as `abundant[i] + abundant[j]` exceeds the limit. Problem 38 returns
  on its first pandigital hit. A comprehension always consumes its whole input. You can force an
  early exit with `itertools.takewhile`, but that is harder to read than the `break`.
- **Cells depend on cells written in the same pass: write the loop.** Problem 73's sieve does
  `data[j] -= data[i]` over multiples of `i`, and the `data[i]` it reads was itself finished
  earlier in the same sweep. A comprehension builds a new list from a snapshot, so it cannot express
  that dependency.
- **Problem 181 shows the boundary in a single function.** For a group type that adds to a
  *different* row, the update is a vectorised row add,
  `dst[j:] = [d + s for d, s in zip(dst[j:], src[:cols + 1 - j])]`. That is safe because `src` is a
  different list from `dst`. For a group type that stays in the *same* row, the solution falls back
  to an explicit `row[b] += row[b - j]` sweep. The [unbounded knapsack](/topics/technique/knapsack-problem)
  needs to read values that this pass just wrote, so an item can be used again. A comprehension
  there would add from the old row, which quietly turns it into a 0/1 knapsack and gives the wrong
  count.

## The counterpart in C

C has no comprehension. Every table is an allocation followed by a `for` loop that fills it, and
the translations here follow that pattern exactly. Problem 23's C `malloc`s room for `limit + 1`
ints and appends abundant numbers with `abundant[abundant_count++] = i`. That is the comprehension's
filter, written out with a counter and an upper bound on the size. Problem 73's C fills `data[i]` in
a loop and then runs the same in-place sieve. Problem 181's C uses one flat array indexed by
`a * C + b`, which avoids the aliasing trap entirely: there are no row objects to share.

Some differences go the other way and favour C. Problem 18's C folds the triangle **in place**
(`cur[i] += max(prev[i], prev[i + 1])`) with no copy at all, while the Python `deepcopy`s the
input and then builds a fresh row on each step. Problem 181's C uses the same nested `b` loop for
both kinds of group, because in C a loop is the only option and also the fast one. The Python needs
the comprehension in the different-row case only because a C-level zip-and-add beats a
per-element Python loop. Problem 38's C builds its concatenation with `snprintf` and `strcat` into a
buffer, which is what `"".join` does behind the scenes. In short, a comprehension is Python's
syntax for "allocate, then fill in a loop", and C writes out both steps.

## How to reason about it

- **Default to a comprehension when the output is a function of an existing iterable.** It reads
  as a definition, and it cannot leave a half-built list if the loop exits halfway.
- **Ask whether anyone needs the list.** If the only consumer is `sum`, `max`, `any`, or a single
  `for`, drop the brackets and pass a generator. If the consumer indexes into it, iterates it twice,
  or is `str.join`, keep the list.
- **Snapshot vs. in place is the real dividing line.** A comprehension reads the old state and
  produces a new one. That is correct for a DP layer built from the previous layer (problem 18), and
  wrong for any recurrence that reads its own fresh output (problems 73 and 181's same-row case).
  Decide which one your recurrence needs before you choose the syntax.
- **Nest for 2-D tables, never multiply.** `[[0] * w for _ in range(h)]` is the idiom.
  `[[0] * w] * h` is the bug.
- **Keep it to one idea.** If a comprehension needs `break`, side effects, a second filter that
  depends on a running total, or more than about two `for` clauses, write the loop. A plain `for`
  is not a lesser form, and a C reader will recognise it immediately
  ([parity across languages](/topics/takeaway/parity-across-languages)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0059](/solutions/0059/) — XOR Decryption
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects

<!-- /problems -->
