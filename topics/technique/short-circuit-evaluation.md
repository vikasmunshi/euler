<!-- tags: [short-circuit-evaluation] -->
<!-- status: final -->
# Short-circuit evaluation

[Short-circuit evaluation](https://en.wikipedia.org/wiki/Short-circuit_evaluation) means a
boolean operator evaluates its right operand only when the left one hasn't already decided the
result. `a and b` stops at a false `a`, and `a or b` stops at a true `a`. That makes the *order*
of the conditions a design decision. Put a cheap test in front of an expensive one and the
expensive one runs only for the candidates that survive. Put a test that makes the second one
*meaningful* in front, and the second one can rely on it. The four solutions below are all
search loops that test many candidates and accept very few, and each of them is faster or more
correct because of what its conditions leave out. This page is part of the language-idioms
series. It covers the idiom, why these solutions use it, and how it looks in the other language.

## The idea

Both Python and C guarantee left-to-right evaluation with an early exit. The
[Python reference](https://docs.python.org/3/reference/expressions.html#boolean-operations) says
`x and y` "first evaluates x; if x is false, its value is returned; otherwise, y is evaluated".
C11 §6.5.13 says the same for `&&`, and adds a
[sequence point](https://en.cppreference.com/w/c/language/eval_order) after the left operand, so
every side effect on the left is complete before the right runs. That is a promise, not an
optimisation the compiler may or may not make, so you can build correctness on it.

A condition in front of another one does one of two jobs:

- **A cost filter.** The left test is cheap and rejects most candidates. The right test is
  expensive and now only runs on the few that are left. The total cost becomes
  *(cheap test × all candidates) + (expensive test × survivors)*.
- **A guard.** The right test is only *valid* when the left one holds: `p != NULL && p->x`,
  `i < n and a[i] == k`, `d != 0 && x % d == 0`. Here the order is about correctness, and
  swapping the operands is a bug, not a slowdown.

The same idea applies across a whole sequence of conditions. Python's
[`any`](https://docs.python.org/3/library/functions.html#any) and
[`all`](https://docs.python.org/3/library/functions.html#all) are `or` and `and` over an iterable,
and they stop at the first element that decides the result. They only save work if the iterable
is lazy, so they belong with a [generator](/topics/technique/generator) expression, not a list.

The four problems use these shapes:

| Problem | Left (cheap) | Right (expensive) | What the order buys |
|---|---|---|---|
| [21](/solutions/0021/) | `y != x` | `d(y) == x`, an O(√y) divisor sum | a guard: perfect numbers aren't amicable |
| [47](/solutions/0047/) | the first number in the window to fail | factorising the rest of the window | `any` / `break` stops at the first failure |
| [112](/solutions/0112/) | digit pairs scanned so far | the remaining digits | the verdict is final once both directions are broken |
| [129](/solutions/0129/) | `gcd(n, 10) == 1` | A(n), an O(n) repunit residue walk | a cost filter *and* a guard |

**Amicable numbers (21).** The test reads straight from the definition: x is amicable when
y = d(x) is different from x and d(y) = x.

```python
sum(x for x in range(2, max_num + 1) if (y := sum_factors(x)) != x and sum_factors(y) == x)
```

The [walrus](/topics/technique/walrus-operator) binds `y` in the left operand and the right
operand reads it. That is safe only because evaluation is left to right. In the C version the
sequence point after `&&` gives the same guarantee. To be honest about it, `y != x` saves
almost no time here, because only four perfect numbers lie below 10 000. Its job is to keep the
definition intact. Without it, 6 and 28 satisfy `d(d(x)) == x` and would be counted. This is the
guard form of the idiom, and it happens to be cheap as well.

**Distinct prime factors (47).** The search looks for the first window of *n* consecutive
integers that each have exactly *n* distinct prime factors. Most windows fail on their first
number, so the window test should give up at the first failure:

```python
next(k for k in itertools.count(2) if not any(prime_factor_count(k + i) != n for i in range(n)))
```

`any` over a generator calls `prime_factor_count` until the first mismatch and stops there. The C
version writes the same loop by hand: a `for` with `all_match = 0; break;`. That gives roughly a
factor of *n* in the cost of a rejected window, because each one costs one factorisation instead
of *n*. Wrap the generator in square brackets and the list comprehension computes all *n*
factorisations before `any` sees any of them. It still gives the right answer, but the speedup
is gone.

**Bouncy numbers (112).** A number is bouncy when its digits are neither non-decreasing nor
non-increasing. The C version scans the digits once and keeps two flags. It returns as soon as
both have fallen, because no later digit can make the number monotone again. The Python version
writes the definition literally: two `all(...)` generator expressions, then
`not is_increasing and not is_decreasing`. Each `all` exits at its first violation, so this is
still early-exit, but at a different level. Both `all` calls run before the `and` is reached, so
the `and` itself saves nothing. The C version merges the two checks into one pass and stops when
the *combination* is decided. That is a single-pass version of the same short circuit that
Python's operator can't express across two separate scans.

**Repunit divisibility (129).** A(n) is the length of the shortest repunit divisible by n, and
it exists only when gcd(n, 10) = 1. The search walks upward from the bound and computes A(n) by
stepping the residue of R(k) mod n, which costs up to n steps per candidate. The gcd test runs in
a few modulo operations and rejects every even n and every multiple of 5, which is 60% of
candidates, before the O(n) walk starts. Its second job is easier to miss. When n is not coprime
to 10, the residue walk never reaches 0 and the helper falls back to returning n, which is
*greater* than the bound. Without the guard that sentinel would pass `> min_a_n` and the search
would stop at the first candidate that shares a factor with 10. So the cheap test also keeps the
expensive one from being called outside the inputs it is defined for.

## The counterpart in C

For the binary operators the two languages are equivalent: `&&` and `||` short-circuit exactly
like `and` and `or`, and Problems 21 and 129 have the same condition in both languages. The
differences are around the operators.

- **No `any` or `all`.** C has no lazy sequence for a reduction to consume, so a quantifier over a
  range becomes a loop with a flag and a `break` (Problem 47), or an early `return` from a helper
  (Problem 112). The helper form is usually cleaner. `return 1` inside the loop *is* the short
  circuit, and it needs no flag after the loop.
- **Value versus truth.** Python's `a or b` returns one of its operands, which supports defaults
  such as `x or fallback`. C's `&&` and `||` always return `int` 0 or 1. The solutions here only
  use the truth value, so the difference doesn't matter for them, but it does when you port code
  in the other direction.
- **The operators that don't short-circuit.** C's bitwise `&` and `|` evaluate both sides. On
  0/1 flags they give the same truth value as `&&` and `||`, so swapping one for the other
  compiles and quietly removes the guard. Python has the same trap with `&` on booleans, and with
  a list comprehension in place of a generator inside `any` or `all`.

Most other languages behave the same way. Java, C#, JavaScript, Go and Rust short-circuit `&&`
and `||`. Ada and Visual Basic keep the plain `and`/`And` eager and spell the short-circuit form
`and then` / `AndAlso`, which says outright that the order matters.

## How to reason about it

- **Order filters by cost over rejection rate.** Among independent filters, run the one with the
  best ratio of rejection rate to cost first. Usually that means the O(1) arithmetic test first
  (a gcd, a parity, a residue) and the O(√n) or O(n) test last.
- **Mark guards as guards.** If the right operand is only defined when the left one is true, say
  so in a comment. Problem 129's guard looks like a pure speed filter, and someone tidying the
  code might reorder conditions they assume are independent.
- **Keep the iterable lazy.** `any(f(x) for x in xs)` short-circuits, and `any([f(x) for x in xs])`
  doesn't. The brackets cost one character and the whole benefit.
- **Look for the point where the answer is decided.** Problem 112's C exits when the result can
  no longer change, which is earlier than either separate quantifier would. When you test a
  combination of conditions over a sequence, merge the scans and stop where the combination is
  fixed.
- **Short-circuiting is not pruning.** It skips work inside one candidate's test. Skipping
  *candidates*, for example jumping the window in Problem 47 past the number that failed, is a
  separate and often larger improvement. Use both where you can.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0021](/solutions/0021/) — Amicable Numbers
- ● [0047](/solutions/0047/) — Distinct Primes Factors
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0129](/solutions/0129/) — Repunit Divisibility

<!-- /problems -->
