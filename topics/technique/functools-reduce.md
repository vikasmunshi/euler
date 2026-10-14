<!-- tags: [functools-reduce] -->
<!-- status: final -->
# functools.reduce

[`functools.reduce`](https://docs.python.org/3/library/functools.html#functools.reduce) collapses
a sequence into one value by applying a two-argument function cumulatively from the left:
`reduce(f, [a, b, c], init)` is `f(f(f(init, a), b), c)`. Functional programmers call this a
[left fold](https://en.wikipedia.org/wiki/Fold_(higher-order_function)). The three solutions below
each fold a short stream with a binary operator: the least common multiple of a range in
Problem 5, the product of four fractions in Problem 33, and the product of seven digits in
Problem 40. Each is a one-line answer to "combine all of these". Two of them are also places where
the standard library has since grown a named function that does the job better. This page is part
of the language-idioms series. It covers the idiom, why these solutions use it, and how it looks
in the other language.

## The idea

A fold needs three things: a binary operation, a sequence, and a starting value. `reduce` keeps an
accumulator, sets it to the initial value, and replaces it with `f(acc, x)` for each element. When
the operation is [associative](https://en.wikipedia.org/wiki/Associative_property) and the initial
value is its [identity element](https://en.wikipedia.org/wiki/Identity_element), the fold is the
mathematical "big operator" (Σ, Π, lcm over a set), and the order of the elements doesn't matter.

| Problem | Operation | Sequence | Identity | Named alternative |
|---|---|---|---|---|
| [5](/solutions/0005/) | lcm(x, y) = x·y / gcd(x, y) | `range(2, n + 1)` | 1 | `math.lcm(*range(1, n + 1))` (3.9+) |
| [33](/solutions/0033/) | `a * b` on `Fraction` | a filtered generator of four fractions | `Fraction(1, 1)` | `math.prod(...)` (3.8+) |
| [40](/solutions/0040/) | `a * b` on `int` | a generator of digit lookups | 1 | `math.prod(...)` |

**Smallest multiple (5).** The smallest number divisible by every integer from 1 to n is
lcm(1, …, n). lcm is associative, so the running result after k steps is lcm(1, …, k), and one
[gcd](/topics/technique/math-gcd) per step extends it:

```python
functools.reduce(lambda x, y: x * y // math.gcd(x, y), range(2, n + 1), 1)
```

This is the only one of the three where the fold carries real meaning. The operation is not
built into the language as an operator, so the lambda spells out the
[lcm identity](/topics/domain/least-common-multiple). Since Python 3.9,
[`math.lcm`](https://docs.python.org/3/library/math.html#math.lcm) accepts any number of arguments,
so `math.lcm(*range(1, n + 1))` says the same thing without the lambda and runs the loop in C.

**Digit cancelling fractions (33).** The search finds the four "curious" fractions such as
49/98, multiplies them, and reports the denominator in lowest terms. The fold runs over a
generator expression with two `if` filters, and its accumulator is a
[`Fraction`](/topics/technique/fractions-fraction):

```python
functools.reduce(lambda a, b: a * b, (Fraction(n, d) for ... if ...), Fraction(1, 1)).denominator
```

Here `reduce` is doing the work of `math.prod`. `Fraction.__mul__` reduces each partial product by
its gcd, so the accumulator always stays in lowest terms and `.denominator` is the answer with no
extra step. `math.prod(gen)` gives the same result, because its default start of `1` multiplied by
a `Fraction` produces a `Fraction`.

**Champernowne's constant (40).** The answer is d₁ × d₁₀ × d₁₀₀ × … × d₁₀₀₀₀₀₀, where each digit
is found by walking the d-digit bands of the concatenated integers. Again the fold is a product:

```python
functools.reduce(lambda x, y: x * y, (digit(10**k) for k in range(0, i + 1)), 1)
```

`math.prod(digit(10**k) for k in range(i + 1))` is the same expression with the ceremony removed.

## Why reach for reduce, and when not to

Guido van Rossum famously
[argued for dropping `reduce`](https://www.artima.com/weblogs/viewpost.jsp?thread=98196) from the
builtins. His view was that apart from `+` and `*`, a `reduce` call usually needs pen and paper to
understand, and that an explicit loop is clearer. Python 3 moved it into `functools`, and the
named reductions have since filled the common cases: `sum`, `math.prod`, `math.lcm`,
`math.gcd`, `any`, `all`, `min`, `max`, `"".join`. The three problems here show the range:

- **`reduce(lambda x, y: x * y, ...)` is `math.prod`.** Problems 33 and 40 use a general tool for
  a job with a specific name. `math.prod` is shorter, needs no lambda, says what it computes, and
  avoids a Python-level function call per element. If you do want a fold with an operator,
  [`operator.mul`](https://docs.python.org/3/library/operator.html#operator.mul) is the idiomatic
  replacement for `lambda a, b: a * b`.
- **The lcm lambda was the right call before 3.9.** Problem 5's operation had no name in the
  standard library until `math.lcm` arrived, so `reduce` with the gcd identity was the cleanest way
  to write it. Now `math.lcm` takes the whole range at once.
- **`reduce` is still the tool for an operation with no built-in name.** Folding with matrix
  multiplication, composing functions, merging dicts, or a modular product
  `reduce(lambda a, b: a * b % m, xs, 1)` are all fine uses. If the operation has a name, use it;
  if it doesn't, `reduce` with a named helper function reads better than a long lambda.

Two details are easy to get wrong:

- **Always pass the initial value.** Without it, `reduce` uses the first element as the start and
  raises `TypeError` on an empty sequence. With it, an empty sequence returns the identity, which
  is the mathematically correct answer: the empty product is 1. All three solutions pass it.
- **The initial value sets the accumulator's type.** In Problem 33, `Fraction(1, 1)` makes the
  type explicit. An `int` 1 also works, because `int * Fraction` returns a `Fraction`, but then the
  result's type depends on whether the generator yielded anything. The explicit start makes the
  type fixed and documents the intent.

To keep the intermediate values instead of only the last one, use
[`itertools.accumulate`](/topics/technique/itertools-accumulate). It is `reduce` that yields every
partial result, and it takes the same function and `initial=` argument.

## The counterpart in C

C has no higher-order fold in its standard library. A fold is a `for` loop with an accumulator
initialised to the identity, and all three C versions are that loop. What changes is what the
accumulator has to hold.

- **Problem 5 needs a big integer.** Python's `int` hides the size of lcm(1, …, 100), about
  7 × 10⁴⁰. In C that number does not fit in 64 bits, so the C version carries a hand-rolled
  [arbitrary-precision](/topics/technique/arbitrary-precision-arithmetic) accumulator of 32-bit
  limbs. Each step computes `result mod y` to get the gcd, then `result = result / g * y`.
  Dividing *before* multiplying keeps the intermediate value no larger than the result, which
  matters in C and is free in Python.
- **Problem 33 replaces the `Fraction` with two integers.** The C version keeps a numerator
  product and a denominator product as `long long`, and reduces the pair with one gcd at the end.
  The Python fold reduces after every step. For four fractions with one-digit parts, nothing can
  overflow, so one reduction at the end is enough. For a longer fold you would reduce each step,
  as `Fraction` does, to keep the numbers small.
- **Problem 40 is a plain product.** Seven digits, each at most 9, fit in a `long long` easily.
  The accumulator starts at 1 and multiplies by each lookup, which is exactly what `math.prod`
  does.

In C the loop *is* the idiom, so there is no question of which one to pick. The design question
moves to the accumulator's type: how large it can grow, and whether to normalise it on every step
or once at the end. Python's `int` and `Fraction` answer that question for you.

## How to reason about it

- **Name the operation first.** If it is sum, product, lcm, gcd, min, max, any, all or join, use
  the built-in for it. Use `reduce` when the operation has no name.
- **Check associativity and the identity.** If both hold, the fold is a big-operator product and
  the empty case is well defined. If the operation isn't associative, such as subtraction or
  function application, the left-to-right order is part of the meaning and should be commented.
- **Pass the initial value.** It handles the empty input and fixes the accumulator's type.
- **Think about how big the accumulator gets.** A product or lcm grows fast. In Python that costs
  time, and in C it costs correctness. Reduce or divide early when you can.
- **Feed it a generator.** All three solutions pass a lazy stream, so nothing is materialised and
  `reduce` consumes one element at a time, as `math.prod` does. `math.lcm(*xs)` is the exception:
  unpacking builds a tuple of every argument first, which is harmless for a range of 100 but worth
  knowing for a long stream.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0040](/solutions/0040/) — Champernowne's Constant

<!-- /problems -->
