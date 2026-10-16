<!-- tags: [stack-abstract-data-type] -->
<!-- status: final 2026-10-16T15:55Z -->
# Stack (abstract data type)

A [stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)) is the simplest
container worth naming: you can only `push` onto the top, `pop` from the top, and ask
whether it is empty. Last in, first out. Every program already has one, the call stack,
and most of the problems below use a stack because they *would* have been recursive. The
recursion has been taken out of the language runtime and put into a container the code
controls. Two problems use the stack for another reason. In one, its contents are part of
the state being counted. In the other, it holds a resumable frame. This page covers why
you would make the stack explicit, how to size it, the monotonic stack (a different use
of the same structure), and how differently Python and C express a stack.

## The idea — the call stack, made explicit

A recursive call does three things implicitly: it saves the caller's state, runs the
callee with new arguments, and hands a value back. When the caller does no work *after*
the call except adding up results, only the middle step matters. The saved state is just
"which calls are still pending", and a stack of argument tuples records that exactly.

Problem 73 (public) shows the shape. Its second solution counts the fractions strictly
between 1/3 and 1/2 by descending the
[Stern–Brocot tree](https://en.wikipedia.org/wiki/Stern%E2%80%93Brocot_tree). The descent
recurses on the mediant until its denominator passes the limit:

```python
sys.setrecursionlimit(10 ** 6)

def recursion(lower_denominator: int, upper_denominator: int) -> int:
    if (mediant := (lower_denominator + upper_denominator)) > max_d:
        return 0
    return 1 + recursion(lower_denominator, mediant) + recursion(mediant, upper_denominator)
```

The `setrecursionlimit` line is the clue. The leftmost spine of that tree adds only 3 to
the denominator per level, so with a limit of 12 000 the recursion goes about 4 000 frames
deep. CPython's default limit is 1 000
([`sys.getrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.getrecursionlimit)).
Raising the limit is safer than it once was: since 3.11, a Python-to-Python call no longer
uses C stack. But every frame is still a heap object, and the call itself is the most
expensive operation in the loop. The explicit version replaces the limit with a list:

```python
count, stack = 0, [(3, 2)]
while stack:
    lo, hi = stack.pop()
    if (mediant := lo + hi) > max_d:
        continue
    count += 1
    stack.append((lo, mediant))
    stack.append((mediant, hi))
```

The translation always takes the same three steps. The function's arguments become the
pushed tuple. Its base case becomes a `continue`. The `return 1 + …` turns into an
accumulator. The only depth limit left is memory. This is the shape of 139, 218 and 223
(the [ternary tree of Pythagorean triples](/topics/technique/tree-of-primitive-pythagorean-triples),
with three children per node and a perimeter prune), of 226 (dyadic intervals of the
blancmange curve), of 156 (bisecting an interval where the digit-count function crosses
the identity), and of 247 (squares packed under a hyperbola, two children each). In every
case the order of visits does not matter, because the answer is a count or a sum. That is
what makes the stack a free choice over a queue. For the search itself, see
[depth-first search](/topics/technique/depth-first-search).

### When arguments are not enough: frames

Sometimes the caller has work to do after a child returns. In 642, a parent adds the
child's result, multiplies in another power of the prime, and then decides whether to
descend again. Now the stack has to hold what the call stack held: the locals, a *resume
point*, and a slot to receive the return value. The C solution for 642 does exactly this.
Each `Frame` stores the loop variables, a `phase` (start the loop, push a child, or the
child has returned), and a `ret` accumulator. Popping a frame adds its `ret` into the
parent's. This is a hand-written
[continuation](https://en.wikipedia.org/wiki/Continuation), and it is the expensive form of
the technique, both to write and to read. Its Python twin simply stays recursive. The depth
there is the number of distinct primes in one factorisation shape, which is about a dozen
at most, so no limit is ever close. The lesson: rewrite recursion as a stack only when the
depth requires it.

### Following one child in place

An explicit stack also makes a small optimisation natural. In 255, most intervals have
exactly one child. The loop pushes every child except the last, then *rebinds its own
variables to the last child and continues*. That is
[tail-call elimination](https://en.wikipedia.org/wiki/Tail_call) by hand: the common
single-child chain never touches the stack, and the stack holds only the siblings deferred
along one path.

## Sizing it: depth times branching, not tree size

The stack never holds the tree. It holds the current path plus the siblings still waiting
along that path. If each pop pushes at most *b* children and the tree is at most *D*
levels deep, the stack never exceeds (*b* − 1)·*D* + 1 entries. Use that bound to size a
fixed C array:

- **156** bisects [0, 10¹²]. The depth is about 40, so 64 slots are enough.
- **226** halves dyadic intervals but caps the depth at 45, below double precision's
  resolution. With *b* = 2, that needs at most 46 slots, and 128 leaves a comfortable
  margin.
- **218** derives its depth from the tree's slowest-growing spine (≈ √(2w) levels), then
  allocates 3 × (2·depth + margin) `long long`s. That is three coordinates per triple and
  two waiting siblings per level, exactly (*b* − 1)·*D*.

Get the bound wrong and Python just uses more memory. C writes past the end of the array.
That is why 247 and 255 check `top` against the capacity before every push and fail
loudly (`return NULL`) rather than corrupt the heap.

## A stack as state, not as control

In 145, the stack is not a traversal device at all. A reversible number pairs digit *i*
with digit *d* − 1 − *i*, and each pair's sum appears twice in *n* + reverse(*n*), once at
each end. The DP walks the positions in one direction to carry left to right. In the first
half it chooses a pair sum and *pushes* it. In the second half it meets each pair's
partner position in reverse order, so it *pops*. The pairing nests like brackets, and
nesting is exactly what LIFO models. The pending stack therefore belongs in the DP key,
`(carry, pending)`, and two partial numbers merge only when their stacks match. The stack
is short (at most ⌊*d*/2⌋ entries of 0–18), so Python keys on a tuple directly and C packs
it into one `int` in mixed radix 19.

## Monotonic stacks

A [monotonic stack](https://en.wikipedia.org/wiki/All_nearest_smaller_values) keeps its
contents sorted by popping whatever the new element would break the order for. Each pop
is an answer: the element being popped has just met its nearest larger (or smaller)
neighbour.

```python
nearest_greater, stack = [-1] * len(xs), []
for i, x in enumerate(xs):
    while stack and xs[stack[-1]] < x:
        nearest_greater[stack.pop()] = i
    stack.append(i)
```

Every index is pushed once and popped at most once, so the nested loop is O(*n*) amortised
([amortized analysis](https://en.wikipedia.org/wiki/Amortized_analysis)). Reach for it
when a question asks, for every position, where the nearest larger or smaller value is.
Examples include "how far does this value dominate", the largest rectangle under a
histogram, and the sum of subarray minimums. Without the stack, each of these is a
quadratic scan. None of the problems tagged here needs one. Their stacks drive traversals
of implicit *trees*, and a monotonic stack is a tool for *sequences*. The two are worth
telling apart, because seeing `stack.pop()` inside a `while` that compares values means
the second idea, not the first.

## Python's list against C's array and index

| | Python | C |
|---|---|---|
| Container | `list`; push = `append`, pop = `pop()`, both amortised O(1) ([tutorial](https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks)) | an array plus an integer `top` |
| Element | a tuple per entry (one allocation per push) | a `struct` by value, parallel arrays, or flat scalars |
| Empty test | `while stack:` | `while (top)` or `while (sp >= 0)` |
| Capacity | none to manage | fixed and checked, sized to a proven bound, or grown with `realloc` |
| Overflow | `MemoryError`, eventually | silent corruption unless checked |

The idioms in these solutions show what each choice involves:

- **Pick one `top` convention and keep to it.** Most of the C here uses `top` as a *count*:
  `stack[top++] = x` to push, `x = stack[--top]` to pop, and `while (top)` to loop. 642
  uses `sp` as the *index* of the top frame instead, starting at 0 and looping on
  `while (sp >= 0)`. Both are correct. Mixing them inside one function is a classic
  off-by-one.
- **Element layout is a free choice in C.** 223 pushes a `Triple` struct. 156, 226 and 247
  keep parallel arrays (`lo_stack`/`hi_stack`, `stack_x`/`stack_y`). 218 pushes `a, b, c`
  as three bare `long long`s and pops them back as `c, b, a`. That is the cheapest layout,
  but it is LIFO at the scalar level, so the pop order must reverse the push order exactly.
- **Grow before the push that needs it.** 139 doubles its array when fewer than three
  slots remain, because one pop can push three children. 223 and 642 grow on the same
  principle.
- **`realloc` moves the block.** Any pointer into the old stack dangles afterwards. 642
  keeps `Frame *fr = &stk[sp]` live across a push, and so it re-takes `fr` immediately
  after growing. Forgetting that line is a bug that appears only on inputs large enough to
  trigger a resize.
- **In Python, the per-entry cost is the tuple.** Hoisting the bound methods out of the
  loop (`push = stack.append; pop = stack.pop`, as in 223) saves an attribute lookup per
  operation on a hot loop. This is worth doing when the loop runs once per solution
  counted.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors

<!-- /problems -->
