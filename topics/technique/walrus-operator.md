<!-- tags: [walrus-operator] -->
<!-- status: final 2026-10-14T17:40Z -->
# walrus operator

The [assignment expression](https://docs.python.org/3/reference/expressions.html#assignment-expressions)
`name := expr` evaluates `expr`, binds it to `name`, and *is* the value. Python added it in
[3.8](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions) for one narrow job:
computing a value once, testing it, and keeping it for later use, in places where a statement is
not allowed. Those places are a comprehension's `if` clause and a `while` header. Euler code ends
up in both all the time. A filter computes something expensive, checks it, then yields that same
thing. A loop runs until a computed value goes empty or stops changing. All six solutions below are
public, so the code can be quoted. This page is part of the language-idioms series, so it also
covers the C side, where assignment has always been an expression and these translations still
choose not to use it.

## The idea

Three shapes cover every use here.

**Filter on a value, then yield it.** A generator expression has nowhere to put a temporary.
Without `:=` you either compute the candidate twice, once to test and once to yield, or use the
`for x in [expr]` trick that wraps one value in a list. Problem 30 builds each candidate from a
digit multiset, then keeps it only if it reproduces itself:

```python
num
for digits in itertools.combinations_with_replacement(range(10), upper_bound_num_digits)
if (num := sum((x**n for x in digits))) > 9 and num == sum((int(x) ** n for x in str(num)))
```

`num` is bound in the first conjunct, read twice more in the condition, and yielded. Problem 63
does the same with `r := i**n`, kept when `len(str(r)) == n`. Problem 32 goes further and binds
three names inside one function argument:

```python
if is_nine_pandigital(
    (a_str := "".join(a)) + (b_str := "".join(b)) + str((c := (int(a_str) * int(b_str))))
)
```

Here `c` is the product the comprehension yields, and `a_str` is reused to build it. `b_str` is
never read again, so that one binding only names a piece.

**Compute, test, and use in a loop header.** This is the case the PEP was written for. Problem 63's
driver keeps going while the current exponent still has solutions:

```python
while solutions := n_digit_nth_powers(n):
    result += len(solutions)
    n += 1
```

The alternative is the "loop-and-a-half": `while True:`, compute, `if not solutions: break`, use.
That is four lines, and the exit is buried in the body. The walrus puts the stop condition back in
the header, where a reader looks for it.

**Compare the old value with the new one.** Problem 80 finds $\lfloor\sqrt{N\cdot 10^{200}}\rfloor$
by [Newton's method](/topics/technique/newtons-method) on integers:

```python
sqrt = number
while sqrt != (sqrt := ((sqrt + number // sqrt) // 2)):
    pass
```

This works only because Python evaluates the operands of `!=` left to right. The left `sqrt` is
read *before* the right side rebinds it, so the test compares the previous iterate with the next.
The loop is a [fixed-point iteration](/topics/technique/fixed-point-iteration) in one line with an
empty body.

The remaining two stretch the idea. Problem 70 binds `number` and `totient` inside a
`sorted(str(...)) == sorted(str(...))` permutation test, then binds `ratio` in the next `if`. That
is three assignments across two conditions, where a pair of plain statements above the `if` would
have done the same job. Problem 44 writes `while i := (i + 1):`. The value is never falsy (i
starts at 1), so the walrus is just a counter dressed up as a condition. `for i in
itertools.count(1):` says the same thing and doesn't look like a test.

## The counterpart in C

In C, assignment has always been an expression: `while ((c = getchar()) != EOF)` is the idiom
PEP 572 brought to Python. Python spelled it `:=` instead of `=` to rule out C's oldest bug, where
`if (x = 0)` is legal, compiles, and is always false. Even so, none of these six translations use
an assignment in a condition, and the reasons are useful:

- **No comprehensions, so nothing to work around.** The walrus exists mainly because a generator
  expression cannot hold a statement. A C loop body can, so problem 30's C computes `num` on one
  line and tests `num > 9 && digit_power_sum(num, n) == num` on the next. Problem 70's C declares
  `number` and `totient` as locals before calling `is_digit_permutation`. The temporary becomes
  an ordinary variable, which is the plainer form anyway.
- **The loop-and-a-half is the idiom.** Problem 63's C is `while (1) { … if (solutions_this_n == 0)
  break; … }`, the exact shape the Python walrus removes. Problem 44's C is
  `for (long long i = 1; ; i++)`, the honest form of an endless counter.
- **The fixed-point test needs care.** Problem 80's C runs Heron's iteration with a separate
  `xnew` and stops on `bi_cmp(&xnew, &x) >= 0`, meaning "stop when the next value is no smaller",
  not "stop when it is equal". That difference matters, as the next section explains. The C needs
  the temporary anyway, because a `BigInt` assignment is a function call, not an expression.

## How to reason about it

- **Use it when the name is read again.** If the bound value is tested *and* yielded, or tested
  and then used in the body, the walrus removes a duplicate computation or a loop-and-a-half. If
  it is never read again (problem 32's `b_str`), it is just a label, and an inline comment would
  do the same job.
- **One walrus per condition is a good budget.** Problems 30 and 63 read cleanly. Problem 70's
  two-line condition, with a binding inside `str()` inside `sorted()` on each side, makes you
  parse three layers of parentheses to find out what is being compared. When the condition is
  doing that much, hoist the values into statements. A plain `for` loop is not a step down from a
  comprehension.
- **Its scope is the enclosing function, not the comprehension.**
  [PEP 572](https://peps.python.org/pep-0572/#scope-of-the-target) binds the target in the
  containing scope on purpose, so `num` in problem 30 still exists after the `sum(...)` finishes.
  Usually that doesn't matter. It does matter if you reuse the name below and expect it to be
  untouched.
- **"Until unchanged" assumes there is a fixed point.** Integer Newton started above the root
  falls monotonically to $\lfloor\sqrt n\rfloor$. But when $n+1$ is a perfect square, the next
  step goes back *up* by one, and the iteration flips between two values forever. Problem 80's
  `!=` loop never stops on $n = 8, 15, 24, 99$. Its real inputs happen to avoid that case. The C
  version's `>=` test, or [`math.isqrt`](/topics/technique/math-isqrt), has no such gap. In
  general, a terse loop header can hide a weak termination condition, so check what it actually
  tests ([integer square root](/topics/technique/integer-square-root)).
- **Evaluation order is part of the contract.** `old != (old := new)` relies on left-to-right
  evaluation, which Python guarantees. The C spelling `x != (x = f(x))` is undefined behaviour,
  because the read and the write of `x` are unsequenced. Translating line for line would carry
  the bug over, so the C has to make the temporary explicit
  ([parity across languages](/topics/takeaway/parity-across-languages)).

<!-- problems (generated by update-tags) -->
## Problems

- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0080](/solutions/0080/) — Square Root Digital Expansion

<!-- /problems -->
