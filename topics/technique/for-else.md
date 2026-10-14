<!-- tags: [for-else] -->
<!-- status: final 2026-10-14T17:53Z -->
# for/else

Python lets a loop carry an `else` clause, and the clause runs only when the loop ends *without*
a `break`. That makes it the language's built-in answer to a very common question: "I scanned
for something; did I find it?" Without it you'd keep a `found` flag or a sentinel and test it
after the loop. Two solutions use the clause: the sink search inside the topological sort of
problem 79, which is the textbook case, and the pentagonal pair search of problem 44, which uses
it on a `while` loop as a marker for "this can't happen". This page is part of the
language-idioms series. It covers the idiom, why these solutions use it, and how the same thing
looks in C, which has no `else` on its loops and uses a flag, a sentinel or a `goto` instead.

## The idea

The [Python tutorial](https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops)
states the rule in one line: a loop's `else` runs when the loop finishes normally. For `for`, that
means the iterable ran out. For `while`, it means the condition became false. Anything that
leaves the loop early skips it: `break`, but also `return` and an exception. `continue` has no
effect on it. An empty iterable counts as finishing normally, so the `else` runs straight away.

The name is the stumbling block. `else` doesn't pair with the loop's body the way it pairs with an
`if`'s. The better reading is **"no break"**. In a search loop the `break` means "found", so the
`else` means "not found":

```python
for item in items:
    if matches(item):
        break          # found: skip the else
else:
    handle_missing()   # ran off the end: nothing matched
use(item)              # safe: we only get here after a break
```

The last line matters. A Python loop variable outlives the loop, so after a `break` it still names
the item that matched. If the `else` raises or returns, every path that reaches the code after
the loop has a valid `item`. The loop variable *is* the result, and the `else` guarantees it's
set.

**Passcode ordering (79).** The solution builds a successor set for each digit and then takes the
digits off from the right: on each round it finds a *sink* (a digit with no remaining successors),
prepends it to the passcode, and removes it from the graph. This is
[topological sorting](/topics/technique/topological-sorting) run sink-first. The search for a sink
is exactly the shape above:

```python
for char, after in successor_graph.items():
    if not after:
        passcode = char + passcode
        break
else:
    raise ValueError("No successor found - possible circular dependency in the constraints")
del successor_graph[char]
```

The `else` is the cycle detector. If every remaining digit still has a successor, the constraints
contain a cycle and no passcode exists, so the loop runs off the end and the solution raises.
Otherwise `char` is the sink, and the line after the loop removes it. There's no flag and no
"not found" value to check: the two outcomes are two branches of the same statement.

**Pentagonal pairs (44).** Here the clause sits on a `while` loop, and it does a different job:

```python
i = 0
while i := (i + 1):
    for j in range(i - 1, 0, -1):
        if ...:
            return str(p_i - p_j)
else:
    raise ValueError("No solution found")
```

This `else` can never run. The [walrus](/topics/technique/walrus-operator) condition `i := i + 1`
yields 1, 2, 3, …, which are all truthy, so the condition never becomes false, and the only way
out is the `return`, which skips the `else`. The clause works as a comment the interpreter
enforces: "if this loop ever stops on its own, something is wrong". That's a fair intent, but a
plain `while True:` (or `for i in itertools.count(1):`) followed by a `raise` *after* the loop
says the same thing without making the reader work out when the walrus becomes falsy. Note too
that 44 needs to leave two nested loops at once. `break` would only leave the inner one, and
it's the `return` that gets out of both. Putting a search in its own function and returning from
it is the cleanest way out of nested loops in either language.

## The counterpart in C

C loops have no `else`, so the "did the loop break?" fact has to be stored somewhere or jumped
over. The solutions show the first of three standard forms:

- **A sentinel result (79).** C's sink search starts with `int found = -1;`, sets `found = i`
  before it `break`s, and checks `if (found < 0)` after the loop to report the cycle. One
  variable holds both the flag and the result. This works because −1 can never be a valid index;
  see [sentinel value](/topics/technique/sentinel-value). It's the form most C code uses.
- **The loop index itself.** If the index is declared outside the loop, the loop's own exit test
  doubles as the flag:

  ```c
  int i;
  for (i = 0; i < n; i++)
      if (matches(i)) break;
  if (i == n) { /* the else: nothing matched */ }
  ```

  This is the closest match to `for`/`else`. The "ran off the end" condition is the loop
  condition, and `i` survives the loop just as a Python loop variable does. It only works when
  the loop counts up to a known bound.
- **`goto`.** `for (…) if (matches(i)) goto found;`, then the not-found code, then a `found:`
  label. This mirrors the Python structure exactly, and unlike `break` it also leaves several
  nested loops in one jump. Leaving nested loops is one of the few uses of `goto` that C style
  guides generally accept. The cost is a label that a reader has to look for.

Problem 44's C version shows the other half. `for (long long i = 1; ; i++)` has no condition, so
like the Python `while` it can only exit by `return`. The `return -1` after it is the C version of
the unreachable `else`: dead code kept so the function doesn't fall off its end without a return
value.

Going from C to Python, the trap is copying the flag: `found = False`, set it in the loop, test
it afterwards. That works, but it's three extra lines and one more variable that can get out of
sync. For a pure lookup, `next((c for c, a in graph.items() if not a), None)` collapses the
search to one expression with a `None` sentinel, and `any(...)` answers a yes/no question with no
loop at all. `for`/`else` is the right choice when the found branch has to *do* something with
the item and the not-found branch has to raise or return.

## How to reason about it

- **Read `else` as "no break".** It belongs to the `break`, not to the loop body. If the loop
  has no `break`, the `else` always runs (unless something returns or raises), and it's probably
  not what you meant.
- **Use it when "not found" is an error.** The strongest form is the one in 79: `break` on the
  hit, `raise` in the `else`, and use the loop variable after the loop, knowing it's set.
- **Don't use it to mark unreachable code.** An `else` on a loop that can't finish normally (44)
  only tells the reader something if they first prove that it can't run. `while True:` plus a
  trailing `raise` says it directly.
- **Nested loops need a function.** `break` and `else` only apply to the innermost loop. To stop
  a nested search, put it in a function and `return` (both languages), or use `goto` in C.
- **In C, choose by what you need afterwards.** Need the index → test it against the bound.
  Need a separate result → a sentinel such as −1. Need to leave nested loops → `goto` or an
  early `return`.
- **Prefer `next`/`any` for pure lookups.** When there's nothing to do on a hit but get the
  value, a generator expression is shorter than any loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0079](/solutions/0079/) — Passcode Derivation

<!-- /problems -->
