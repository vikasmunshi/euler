<!-- tags: [generator] -->
<!-- status: final -->
# generator expression

A [generator](https://docs.python.org/3/glossary.html#term-generator) is a function that produces
its values one at a time, on demand, keeping its local state alive between yields. A [generator
expression](https://docs.python.org/3/reference/expressions.html#generator-expressions) is the same
thing in comprehension syntax. The reason they recur across the problems below is not brevity: it
is that a search which stops early should not have paid for the elements it never looked at, and a
sequence with no natural end should not have to be given one.

## The idea

Calling a generator function runs none of its body. It returns an object; each `next()` runs until
the following `yield` and then freezes the frame — locals, instruction pointer and all — until
asked again. Three consequences do all the work:

- **Constant space.** A [list comprehension](/topics/technique/list-comprehension) materialises
  every element; a generator holds one. `sum(x*x for x in range(10**8))` runs in a few bytes,
  the list version in gigabytes.
- **Unbounded sequences are expressible.** `while True: … yield` is a legitimate, terminating
  program, because the consumer decides when to stop.
- **Work is demand-driven.** Elements the consumer never requests are never computed — so an early
  exit is a real saving, not just an early `break` after the fact.

The last two are the ones that change algorithms rather than memory footprints.

## Search that stops when it is done

The pattern is `next(genexpr)` — build the candidate stream lazily, in an order that makes the
first hit the answer, and take one element. Problem 9 needs the Pythagorean triplet summing to
`1000`:

```python
next(
    a * b * c
    for a in range(1, sum_sides // 4 + 1)
    for b in range(a, sum_sides // 2)
    for c in (sum_sides - a - b,)
    if a**2 + b**2 == c**2
)
```

Note `for c in (…,)` — a one-element loop used as a `let` binding, which is how a generator
expression names an intermediate. But the real point is `next`: the nested loops describe the whole
`O(S²)` search space, and the machinery abandons it the instant a triplet appears. Problem 41 makes
the ordering carry the argument — pandigital candidates are generated in *descending* order, so the
first prime found is the largest, and no proof of maximality is needed beyond the direction of the
loop:

```python
pandigital_primes = (
    number
    for length in (7, 4)
    for number in gen_n_digit_pandigital_numbers(length, descending=True)
    if fast_is_prime(number)
)
return str(next(pandigital_primes))
```

Generators nest, and that is what makes them worth more than a `break`. Problem 60 searches for a
clique of five primes that pairwise concatenate to primes: a recursive generator yields extended
partial cliques, and `yield from` chains the levels into one lazy stream, so the depth-first search
unwinds naturally on the first complete set. Problem 61 does the same for cyclic figurate chains.
Written with lists, each level would enumerate all of its children before the next level looked at
the first one.

## Streams with no end

The other half of the tag is the infinite generator. Problem 10's second solution yields primes
forever from an incremental sieve — a dict mapping each composite to the prime that will next
strike it — and the caller stops when it likes:

```python
prime_number_gen = primes_generator()
result = 0
while (prime_number := next(prime_number_gen)) < max_num:
    result += prime_number
```

The same generator, unchanged, serves problem 37 (truncatable primes, where the stopping condition
is "eleven found", not a bound) and problem 69 (multiply consecutive primes until the product
exceeds the limit — about ten of them, from a stream that would happily produce millions). One
definition, three different termination conditions, none of them known when the sequence was
written. That is the argument for the shape: a bounded sieve forces you to guess a limit, and the
guess is either wasteful or wrong.

Problem 186 shows the case where the problem statement itself hands you a stream — a lagged
Fibonacci generator producing phone numbers, consumed pair by pair into a union-find structure
until the target component reaches its size. The record count is not known in advance and cannot
be, since it is what the problem asks for; a generator is the only shape that does not require
knowing it. Problem 2 shows the smallest useful version, a generator defined *inside* `solve()`
that closes over the bound:

```python
def _even_fibonacci_numbers() -> typing.Generator[int, None, None]:
    even_fib_a, even_fib_b = (2, 8)
    while even_fib_a < max_limit:
        yield even_fib_a
        even_fib_a, even_fib_b = (even_fib_b, 4 * even_fib_b + even_fib_a)

return str(sum(_even_fibonacci_numbers()))
```

Defining it in the local scope is deliberate here, and matches how this repository benchmarks: with
`--runs=N` the harness times repeated calls to `solve()`, so anything built once at module import
is free on every run after the first and the timing lies. A generator built fresh per call cannot
cheat.

## How to reason about it

- **Laziness pays when you stop early, and costs when you do not.** Consuming a generator to
  exhaustion is *slower* than the array equivalent — per-element interpreter overhead instead of a
  tight loop. Problem 10 measures it exactly: the bounded array sieve sums the primes below two
  million in `0.058 s`, the incremental generator sieve in `0.242 s`. Four times the cost, for
  unboundedness you did not need once the limit was given. Pick the shape from whether the bound is
  known, not from taste.
- **A generator is consumed once.** `next()` past the end raises `StopIteration`; iterating a second
  time yields nothing. If two passes are needed, that is a list. The `next(genexpr)` search idiom
  should be wrapped in `try`/`except StopIteration` (or given a default) whenever "no candidate" is
  a reachable state, as problem 9 does — otherwise the failure surfaces as a confusing exception
  from deep inside the runner.
- **Ordering is the proof.** `next` on a descending stream returns the maximum; on an ascending
  stream, the minimum. Getting the generator's order right replaces an argument about optimality
  with an argument about monotonicity, which is usually much easier — but it is still an argument,
  and it is the thing to state in a comment.
- **They do not translate to C.** Python's frame suspension has no C equivalent, so a C port must
  either fuse the producer into the consumer's loop or hand-roll the state machine explicitly.
  Problem 10's twenty-line Python generator becomes an open-addressing hash table plus explicit
  state in C — the biggest structural divergence between the two languages in this repository, and
  worth anticipating before you write the Python if a C version is coming.
- **Generator expression versus [list comprehension](/topics/technique/list-comprehension).** Inside
  a single-argument call the brackets are optional — `sum(x for x in …)` — and for `sum`, `max`,
  `any` and `all` the generator form is the right default. The exception is when the consumer needs
  a sequence anyway (`sorted`, `len`, two passes, or `math.prod` over something tiny), where
  building the list up front is clearer and no slower.
- **[`itertools`](/topics/technique/itertools) is the standard-library half of this.** `islice`,
  `takewhile`, `count` and `chain` compose with generators without materialising anything, and
  `yield from` splices one generator into another. Reaching for them before writing a manual index
  loop keeps the whole pipeline lazy.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0001](/solutions/0001/) — Multiples of 3 or 5
- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0009](/solutions/0009/) — Special Pythagorean Triplet
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0011](/solutions/0011/) — Largest Product in a Grid
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0033](/solutions/0033/) — Digit Cancelling Fractions
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0041](/solutions/0041/) — Pandigital Prime
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0081](/solutions/0081/) — Path Sum: Two Ways
- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0109](/solutions/0109/) — Darts
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0186](/solutions/0186/) — Connectedness of a Network
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value

<!-- /problems -->
