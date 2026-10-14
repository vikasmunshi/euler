<!-- tags: [global-variable] -->
<!-- status: final 2026-10-14T17:43Z -->
# Global variable

A [global variable](https://en.wikipedia.org/wiki/Global_variable) is state that lives outside
any one function call: a Python module-level name, or a C file-scope variable. Euler solutions
reach for it for one reason. A recursive helper needs a few values that never change from frame to
frame (the bound it prunes against, the string it scans, the table it fills), and threading them
through every call is noise. The five solutions below all do this, and all five keep it on the C
side. Their Python twins solve the same problem with a closure. This page is part of the
language-idioms series, so it covers the idiom, why it shows up here, and how the other language
gets the same result. It also covers the one rule the house convention places on it: you may
*declare* state outside `solve()`, but you must *initialise* it inside.

## The idea

Take the recursion in [Problem 73](/solutions/0073/). It counts fractions between 1/3 and 1/2 by
splitting each interval at its [mediant](/topics/technique/mediant-mathematics) until the
denominator passes a bound. Every frame compares against the same bound, so the C version moves
it out of the argument list:

```c
static int g_max_d;

static long long recursion(int lower_denominator, int upper_denominator) {
    int mediant = lower_denominator + upper_denominator;
    if (mediant > g_max_d)
        return 0;
    return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator);
}
```

`solve()` assigns `g_max_d = parse_int(argv[1])` and then calls `recursion(3, 2)`. The comment in
the source gives the motive: it keeps the hot recursive frame small. The function makes millions
of calls, and every one now pushes two arguments instead of three.

The `static` keyword matters. At file scope it gives the name
[internal linkage](https://en.cppreference.com/w/c/language/storage_duration), so it is visible
only inside this translation unit. It is a global in lifetime but private in scope. That is as close
as C gets to "a variable shared by `solve` and its helpers, and nothing else". Standard C has no
nested functions, so a helper cannot see its caller's locals. The file is the smallest scope two
functions can share.

The other four solutions use the same shape with more state:

| Problem | What lives at file scope | Why |
|---|---|---|
| [14](/solutions/0014/) | a `calloc`'d chain-length cache and its size | the memoised `collatz_length` recursion reads and writes it from every frame |
| [73](/solutions/0073/) | the denominator bound | a constant every frame tests against |
| [88](/solutions/0088/) | the `min_prod` table and its size | the factorisation search relaxes table entries from deep in the recursion |
| [111](/solutions/0111/) | the digit/position pattern being filled, and a buffer of primes found with its count | the enumeration of digit patterns writes candidates from inside a recursive fill |
| [719](/solutions/0719/) | the digit string and its length | a depth-first split search scans the same string at every level |

There are two kinds here. Some state is **read-only context**: a bound, an input string, a
length. Other state is an **accumulator**: a memo table, a running minimum, a count. Only the
second kind can go wrong.

## Why the convention pushes it inside `solve`

The harness times repeated calls. With `--runs=N` the runner calls `solve()` N times *in the same
process*, averages the wall time, and checks that every run returned the same string. Process
state carries over from one run to the next. Anything built once and kept stays built.

That gives two ways for module-level state to fail.

**Timing distortion.** Suppose the Collatz cache in Problem 14 were filled at import, or kept
warm between calls. Run 1 pays the full cost *T*. Runs 2 through N find every chain length already
cached and finish almost at once. The reported average is about *T*/N, so `--runs=10` claims the
solution is ten times faster than it is. The benchmark is measuring a lookup, not the algorithm.
In Python the trap is easy to fall into: a `@functools.cache` on a module-level function is a
global memo table by another name. The rule in CLAUDE.md therefore says to build sieves, tables and
caches **inside** `solve()`, sized to the inputs, and not at module level with a fixed bound.

**Correctness drift.** An accumulator that is not reset keeps its value from the last run.
A count of found primes that starts the second run where the first one stopped, or a `min_prod`
table still holding last run's minima, gives a different answer (or the same answer for the wrong
reason). The C runner catches the visible case: it compares each run's result with the previous
one and exits non-zero with `Expected consistent result`. It cannot catch state that happens to
produce the same number while doing less work. That case is the timing distortion again.

So the rule splits on the two kinds of state. The *declaration* can sit at file scope.
The *initialisation* has to run on every call. All five C solutions do that:

- **14** allocates the cache in `solve()`, sized `max_number + 1`, and at the end frees it and
  sets the pointer and size back to `NULL`/`0`. The comment says so: "rebuilt per call, so each
  benchmarked run pays the full cost". Resetting the pointer means a stale address can't outlive
  the run.
- **88** `malloc`s the table, fills every slot with the `2·k` upper bound, recurses, sums, and
  frees, all inside one `solve()`.
- **73** and **719** only hold read-only context, and they assign it right before the recursion
  starts. In 719 a small wrapper sets the string and its length and then starts the search, so each
  query begins clean.
- **111** resets its prime count to zero before each digit-and-repetition level it enumerates.
  Its prime buffer is a fixed-size `static` array. Storage set at compile time is harmless across
  runs, because the *count* decides what is live, but it does skip the "sized to the input" half of
  the rule. Here that holds up only because the input is small and the bound is generous.

One global is required by the contract itself: the `static char _answer[32]` inside every C
`solve()`. The runner needs the returned pointer to stay valid until the next call, and returning
a per-call `malloc` would leak across runs. That buffer is overwritten on every call, so it follows
the same rule: global storage, per-call contents.

## The counterpart in Python

Python *does* have nested functions, so its version of these solutions has no globals. The helper
is defined inside `solve()` and closes over its locals, which is a
[closure](/topics/technique/closure-computer-programming). Here is Problem 88 in Python:

```python
max_k += 1
min_prod: list[int] = [2 * max_k] * max_k

def find_product_sum(prod: int, total: int, count: int, start: int) -> None:
    k = prod - total + count
    if k < max_k:
        min_prod[k] = min(min_prod[k], prod)
        for i in range(start, max_k // prod * 2 + 1):
            find_product_sum(prod * i, total + i, count + 1, i)
```

`max_k` and `min_prod` work like C's `g_max_k` and `g_min_prod`: one copy, shared by every
frame, and never passed. But they are created fresh each time `solve()` runs and dropped when it
returns. Resetting them is not a separate step that someone can forget. It happens because the
function is called. Problem 14 does the same thing with the cache: `@functools.lru_cache` decorates
a function *defined inside* `solve()`, so every run gets a new, empty
[lru_cache](/topics/technique/functools-lru-cache) and pays the full memoisation cost. Move that
`def` to module level and you get exactly the warm-cache distortion described above.

There is one Python rule to know. A closure can *read* an outer name and can *mutate* the object
it refers to (`min_prod[k] = …` is fine). To *rebind* the name, as in `count += 1`, it needs a
[`nonlocal`](/topics/technique/nonlocal) declaration. Without one, Python treats `count` as a
new local and raises `UnboundLocalError`. That is why counters in Python closures often appear as a
one-element list or a returned value instead of a bare integer. Problem 73's Python helper avoids
the question by *returning* its count (`1 + left + right`), and the C version does the same.
Accumulating through the return value is the cleanest option in either language when the recursion
allows it.

## How to reason about it

- **Classify the state first.** Read-only context (a bound, an input, a length) is safe at file
  scope once it is assigned on each call. An accumulator (cache, table, counter) has to be
  rebuilt or reset on each call, or the benchmark and possibly the answer are wrong.
- **In C, file-scope `static` is the idiom, not a smell.** It is the only way for a recursive
  helper to share state with its caller without a context struct. A struct pointer passed down is
  the cleaner choice once there are several values or the code has to be reentrant. For
  single-threaded solutions run one call at a time, a handful of `static` variables reads better.
- **In Python, prefer the closure.** Defining the helper inside `solve()` gets per-call
  initialisation for free. If you write `global` or a module-level `@cache`, check whether the
  timing under `--runs=N` still means anything.
- **Free and null what you allocate.** A file-scope pointer outlives the call. Problem 14's
  `cache = NULL` after `free` stops a later run, or a stray helper call, from using a dangling
  pointer.
- **Suspect a speed-up that grows with N.** If the average time per run falls as `--runs`
  increases, something is being kept between calls.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0719](/solutions/0719/) — Number Splitting

<!-- /problems -->
