<!-- tags: [greatest-common-divisor] -->
<!-- status: final -->
# Greatest common divisor

The [greatest common divisor](https://en.wikipedia.org/wiki/Greatest_common_divisor) `gcd(a, b)`
is the largest integer that divides both `a` and `b`. It is cheap to compute, and that matters
because it rarely shows up as the thing a problem asks for. Usually it's a guard on the inside of a
loop: is this triple primitive, is this fraction in lowest terms, do these two steps ever line up.
That's why it carries thirty problems in the archive. Most of them ask about *shapes* (triangles,
fractions, lattice lines, tilings) where two objects that differ only by a common scale factor have
to be counted once. The gcd tells you which one in each scaled family is the reduced
representative. Once you have that, the rest of the problem is usually a count over those
representatives.

## Euclid's algorithm, and why it is fast

The [Euclidean algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm) rests on one identity:
`gcd(a, b) = gcd(b, a mod b)`. Anything that divides `a` and `b` also divides `a − qb`, and the
converse holds too, so the pair shrinks without changing its common divisors. Repeat until the
second number is `0`; the first is the gcd.

```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a
```

The cost is the surprising part. [Lamé's theorem](https://en.wikipedia.org/wiki/Euclidean_algorithm#Worst-case)
says the worst case is two consecutive Fibonacci numbers. Each step there has quotient 1, so the
pair shrinks as slowly as it can. `gcd(89, 55)` takes 9 steps. In general the step count is at
most about five times the number of decimal digits of the smaller input. So a gcd is
`O(log min(a, b))` division steps, which is small enough to call inside a doubly nested loop
without thinking twice. [Problem 433](/solutions/0433/) and [Problem 958](/solutions/0958/) make the
step count itself the subject. Most problems only rely on it being small.

In practice I call `math.gcd` in Python and write the three-line loop above in C. Python's built-in
accepts any number of arguments (`gcd(a, b, c)` is `gcd(gcd(a, b), c)`), and there is a matching
`math.lcm`. When the same small arguments come up millions of times, a precomputed table
`g[i][j]` is faster still. [Problem 504](/solutions/0504/) does this: it evaluates four gcds per
quadrilateral over a grid of `m⁴` shapes, so building the `m × m` table once turns every one of
them into an array lookup.

The [extended algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm) also returns
the coefficients of [Bézout's identity](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity),
`ax + by = gcd(a, b)`. When the gcd is 1, `x` is the inverse of `a` modulo `b`. That's how modular
division works (Python's `pow(a, -1, m)` does it for you), and it is also the reason a linear
equation `ax ≡ c (mod b)` has a solution exactly when `gcd(a, b)` divides `c`.

## Where gcd quietly does the work

### lcm: Problem 5

[Problem 5](/solutions/0005/) asks for the smallest number divisible by every integer from 1 to 20,
which is `lcm(1, …, 20)`. The [least common multiple](https://en.wikipedia.org/wiki/Least_common_multiple)
has no algorithm of its own. It comes from the gcd through
`lcm(a, b) = a·b / gcd(a, b)`, because the product counts the shared prime factors twice and
dividing by the gcd removes one copy. lcm is associative, so the whole range folds:

```python
functools.reduce(lambda x, y: x * y // math.gcd(x, y), range(2, n + 1), 1)
```

Divide before you multiply (`x // gcd(x, y) * y`) when you are working in fixed-width C integers;
the result is the same, and the intermediate value stays smaller. There is an equivalent prime-power
view: `lcm(1..n)` is the product of the largest power of each prime `p ≤ n` that is still `≤ n`.
It's elegant, but it needs a sieve, while the gcd fold needs nothing.

### Primitive triples: Problem 39

[Problem 39](/solutions/0039/) looks for the perimeter `p ≤ 1000` that has the most right
triangles with integer sides. Brute force over `(a, b)` works, but the clean route is
[Euclid's formula](https://en.wikipedia.org/wiki/Pythagorean_triple#Generating_a_triple):
for `m > n > 0`,

    a = m² − n²,   b = 2mn,   c = m² + n²,   perimeter = 2m(m + n)

produces a Pythagorean triple. It produces each **primitive** triple (one with `gcd(a, b, c) = 1`)
**exactly once** when `m` and `n` are coprime and of opposite parity. Drop either condition and you
get duplicates. `(m, n) = (4, 2)` gives `(12, 16, 20)`, a scaled copy of `(3, 4, 5)`, and
`(3, 1)` gives `(8, 6, 10)`, the same triangle again.

So the gcd test is what makes the enumeration a *bijection*. Generate the primitives with
`gcd(m, n) == 1`, then add every multiple `k·p₀` of each primitive perimeter yourself. Each triangle
is reached once, by its primitive and its scale factor, and the count per perimeter is just a
tally. [Problem 139](/solutions/0139/) uses the same scaffold. [Problem 276](/solutions/0276/) runs
it in reverse: every integer triangle is `g` times a primitive one, with `g` its gcd, so the total
count is `S(N) = Σ_g P(⌊N/g⌋)`, and [Möbius inversion](https://en.wikipedia.org/wiki/M%C3%B6bius_inversion_formula)
recovers the primitive count `P` from the easy total `S`.

### Reduced fractions: Problem 73

[Problem 73](/solutions/0073/) counts the reduced fractions `n/d` with `d ≤ 12000` that lie
strictly between `1/3` and `1/2`. "Reduced" means `gcd(n, d) = 1`, and the most direct approach
does exactly that: loop over `d`, loop over `n` in the window, keep the coprime pairs. That's
correct, and about twelve million gcds is fine in C.

The three published solutions show how much more structure the coprimality condition has. The
reduced fractions with denominator `≤ N`, in order, are the
[Farey sequence](https://en.wikipedia.org/wiki/Farey_sequence). Neighbours `a/b < c/d` in it satisfy
`bc − ad = 1`, which is a Bézout identity and so proves both fractions reduced without ever calling
gcd. That gives three routes:

- **Neighbour walk** (`s0`). The identity determines the next denominator from the previous two:
  `d' = N − (N + d_prev) mod d`. Walk from `1/3` to `1/2`, one step per fraction.
- **Stern–Brocot recursion** (`s1`). Between two Farey neighbours, the first fraction to appear is
  their [mediant](https://en.wikipedia.org/wiki/Mediant_(mathematics)), whose denominator is the
  sum of theirs. Recurse into both halves while that sum is `≤ N`. Every fraction produced is
  reduced by construction.
- **Counting by inclusion–exclusion** (`s2`). `⌊i·x⌋` counts *all* fractions `≤ x` with
  denominator `i`, reduced or not. Each one reduces to a fraction with a denominator that divides
  `i`, so subtracting the reduced counts of the divisors leaves the reduced count for `i`. A sieve
  does this in `O(N log N)` and never touches a single numerator.

All three replace "test every pair with gcd" with something that only ever produces coprime pairs.
That shift comes up again and again on this page.

## How to reason about it

- **Spot the scaled family.** When a problem says "primitive", "lowest terms", "distinct lines",
  "visible from the origin" or "up to similarity", it's asking for one representative per
  gcd-class. Either filter with `gcd == 1` or, better, generate only the representatives and
  multiply out.
- **gcd turns geometry into arithmetic.** The segment from `(0, 0)` to `(x, y)` passes through
  exactly `gcd(x, y) + 1` lattice points. Combined with [Pick's theorem](https://en.wikipedia.org/wiki/Pick%27s_theorem),
  that gives the interior-point count in Problem 504. The same fact decides which lattice directions
  are distinct in [Problem 388](/solutions/0388/).
- **Factor out the gcd first.** With `a = g·s`, `b = g·t` and `gcd(s, t) = 1`, the coprime pair
  `(s, t)` often has much more structure than `(a, b)`. For instance, `s + t` and `s·t` are then
  coprime too. [Problem 157](/solutions/0157/) uses this to show that `(s + t)/(s·t)` is already in
  lowest terms, so its denominator is fixed and the divisor count follows.
- **Sums of gcds want divisors, not pairs.** `Σ_{k≤n} gcd(k, n)` groups by the value `d` of the gcd:
  there are `φ(n/d)` values of `k` with `gcd(k, n) = d`, so the sum is `Σ_{d|n} d·φ(n/d)`
  ([Pillai's function](https://en.wikipedia.org/wiki/Pillai%27s_arithmetical_function)). Problems
  such as [625](/solutions/0625/) and [530](/solutions/0530/) work at a scale where only this kind
  of regrouping, plus a [totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function)
  summatory function, will do.
- **Coprimality is common, not rare.** Two random integers are coprime with probability
  `6/π² ≈ 0.61` ([Cesàro](https://en.wikipedia.org/wiki/Coprime_integers#Probability_of_coprimality)).
  A `gcd == 1` filter therefore keeps most of its candidates, so it is a cheap correctness guard
  rather than a pruning tool. If you need speed, it has to come from generating less, not from
  filtering more.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0039](/solutions/0039/) — Integer Right Triangles
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0139](/solutions/0139/) — Pythagorean Tiles
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0276](/solutions/0276/) — Primitive Triangles
- ○ [0338](/solutions/0338/) — Cutting Rectangular Grid Paper
- ○ [0343](/solutions/0343/) — Fractional Sequences
- ○ [0350](/solutions/0350/) — Constraining the Least Greatest and the Greatest Least
- ○ [0388](/solutions/0388/) — Distinct Lines
- ○ [0433](/solutions/0433/) — Steps in Euclid's Algorithm
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0443](/solutions/0443/) — GCD Sequence
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ○ [0489](/solutions/0489/) — Common Factors Between Two Sequences
- ● [0504](/solutions/0504/) — Square on the Inside
- ○ [0530](/solutions/0530/) — GCD of Divisors
- ○ [0570](/solutions/0570/) — Snowflakes
- ○ [0625](/solutions/0625/) — Gcd Sum
- ○ [0643](/solutions/0643/) — $2$-Friendly
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0728](/solutions/0728/) — Circle of Coins
- ○ [0795](/solutions/0795/) — Alternating GCD Sum
- ○ [0876](/solutions/0876/) — Triplet Tricks
- ○ [0913](/solutions/0913/) — Row-major vs Column-major
- ○ [0915](/solutions/0915/) — Giant GCDs
- ○ [0958](/solutions/0958/) — Euclid's Labour
- ○ [0959](/solutions/0959/) — Asymmetric Random Walk

<!-- /problems -->
