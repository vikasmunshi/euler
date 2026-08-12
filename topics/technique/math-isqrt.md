<!-- tags: [math-isqrt] -->
<!-- status: final -->
# math.isqrt

[`math.isqrt(n)`](https://docs.python.org/3/library/math.html#math.isqrt) returns the largest integer
$r$ with $r^2 \le n$, computed entirely in integers. It is one line in the docs and it turns up in
every problem below, almost none of which want a square root as such: they want a loop bound, a
range endpoint, or a yes/no answer about squareness. This page is about the *function* — what it
guarantees, what it costs, and the small algebra of bounds built on it. For the underlying
algorithm and its non-Python cousins, see
[integer square root](/topics/technique/integer-square-root).

## The contract

Four guarantees, and every one of them is load-bearing somewhere below.

**Exact, at any size.** No `double` is involved at any point, so there is no precision cliff and no
[`OverflowError`](https://docs.python.org/3/library/exceptions.html#OverflowError). `math.sqrt(10 **
400)` raises — the value has no `float` representation — while `math.isqrt(10 ** 400)` returns its
201-digit root. That matters for the discriminant of a quadratic in a big-integer problem, where the
operand is routinely wider than a `double` can hold.

**Floor, never round.** `isqrt(3) == 1`, `isqrt(4) == 2`. The result is the *floor*, which is the
right convention for a bound: `range(2, isqrt(n) + 1)` covers exactly the candidates with
$d^2 \le n$.

**`ValueError` on a negative argument**, rather than a `NaN` that propagates silently. A
discriminant that can go negative needs its own branch — the exception tells you where.

**`TypeError` on a `float`**, and `__index__` on anything else. `math.isqrt(2.0)` is refused, which
prevents an inexact value sneaking in through the front door; a NumPy `int64` scalar is accepted and
converts to a Python `int`, which is also why calling it per element over an array is a Python-level
loop rather than a vectorised one.

## The algebra of bounds

Most uses are not `isqrt(n)` on its own — they are one of four spellings, chosen by which inequality
the surrounding loop actually needs:

| what you want | spelling | example |
| --- | --- | --- |
| largest $a$ with $a^2 \le n$ | `isqrt(n)` | sieve and trial-division bounds |
| largest $a$ with $a^2 < n$ | `isqrt(n - 1)` | problem 187's "primes $p$ with $p^2 <$ limit" |
| smallest $a$ with $a^2 \ge n$, i.e. $\lceil \sqrt n \rceil$ | `isqrt(n - 1) + 1` | problem 229's lower end of a band |
| is $n$ a perfect square | `isqrt(n) ** 2 == n` | problems 141, 142 |

The middle two hold for $n \ge 1$ and are worth memorising, because the alternative — computing
`isqrt(n)` and then correcting with an `if` — is where off-by-ones live. Problem 229 sweeps a
window $[lo, hi)$ of a lattice and needs both ends at once: `amax = isqrt(hi - 1 - c)` for the strict
upper bound and `amin = isqrt(amin_sq - 1) + 1` for the inclusive lower one, after which `range(amin,
amax + 1)` is exactly the row. Nothing in that loop tests whether a point is in range; the arithmetic
already guarantees it.

The perfect-square predicate is the second big family. Problem 141 generates candidates from a
parametric form and keeps the ones that are square:

```python
s = isqrt(n)
if s * s == n:
    result_set.add(n)
```

Problem 142 applies the same two lines twice per candidate, to $y+z$ and $y-z$, as the last filter in
a chain. Written this way the test is total: no size guard, no tolerance, no comment explaining when
it stops working.

## The trap it replaces

`int(math.sqrt(n))` and `int(n ** 0.5)` agree with `isqrt` right up until they do not, and the
threshold is far lower than the usual "beyond $2^{53}$" rule of thumb suggests. It is
$2^{52} \approx 4.5 \times 10^{15}$ — because the failure that bites is not a wrong root but a wrong
*floor*, and that needs only the input to round up:

```python
>>> n = 4503599761588224          # (2**26 + 1)**2 - 1, just past 2**52
>>> math.isqrt(n)
67108864
>>> int(math.sqrt(n))
67108865                          # claims 67108865**2 <= n; it is n + 1
```

Every $n$ of the form $m^2 - 1$ with $m > 2^{26}$ fails this way. A loop bounded by that value runs
one iteration too far — usually harmless, occasionally a spurious hit — and a `while a * a <= n`
written around it silently changes its termination point. The predicate form fails in the other
direction: above $2^{53}$ a genuine square gets rejected, because the root itself is no longer
representable.

The public solutions show both sides of the judgement. Problem 44 tests pentagonality by inverting
the quadratic in floating point:

```python
return ((1 + math.sqrt(1 + 24 * n)) / 6).is_integer()
```

which is correct here and only here: its arguments stay in the millions. Problem 64 mixes the two
deliberately — `math.isqrt(n)` for the value $a_0 = \lfloor \sqrt n \rfloor$ that seeds the continued
fraction, and a float test to skip perfect squares, safe because its limit is in the low thousands.
Both are fine. What makes them fine is a bound on the input, and a bound on the input is a fact about
today's test case.

## What it costs

Not $O(1)$: CPython uses an adaptive-precision integer Newton iteration, so the cost tracks the width
of $n$. But at the sizes most solutions use, "expensive" is a myth — measured on this repository's
Python 3.14, 200,000 calls each:

| expression | ns/call |
| --- | --- |
| `math.isqrt(n)` | 31 |
| `int(math.sqrt(n))` | 49 |
| `int(n ** 0.5)` | 71 |
| `math.isqrt(n)`, $n \approx 10^{200}$ | 766 |

For a machine-word argument `isqrt` is the *fastest* of the three, because the float routes pay for a
`float` → `int` conversion that `isqrt` never performs. The exact answer is not the slow option; it
is the default, and the float spelling has to earn its place rather than the other way round.

Where the cost does show is repetition. A bound recomputed inside a hot loop is waste — hoist it,
as problem 193 does with `d_max = isqrt(upper)` before the Möbius sweep and problem 719 with
`limit = isqrt(n)` before enumerating roots. The exception is a bound whose argument *shrinks*: in
trial division the remaining cofactor collapses each time a factor is stripped, and recomputing the
ceiling pays for itself many times over.

## How to reason about it

- **Reach for it by default, and make the float version argue its case.** It is faster at word size,
  exact at every size, and one import. The only reasons in this collection to use anything else are
  vectorisation and C.
- **Derive the range, do not discover it.** When an inner loop's limit is the root of a quadratic,
  `isqrt` of the discriminant gives it exactly: `max_k = (-b + isqrt(disc)) // (2 * a)`. That turns a
  `while` with a break test into a `range`, which is both faster and easier to reason about — see
  [quadratic formula](/topics/technique/quadratic-formula). Problem 246 nests the idiom, taking an
  `isqrt` of an expression that itself contains one.
- **It is the natural bound for anything that pairs around $\sqrt n$.** Divisors, the small factor of
  a semiprime, the smaller denominator of a fraction pair: problems 179, 187 and 198 all bound a
  search this way, and the [Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) stops at
  `isqrt(limit) + 1` for the same reason.
- **There is no vectorised `isqrt`.** NumPy has no exact integer square root, and `math.isqrt`
  applied per element is a Python loop that undoes the point of the array. Where the root is the
  *summand* rather than a bound and runs millions of times — counting lattice points row by row, as
  problem 210 does — the answer is a float square root over the whole array plus an integer fix-up.
  That is a deliberate trade in vectorised code, not a licence to use floats in scalar code.
- **The C sibling has to hand-roll it.** C has no integer square root either, so every C counterpart
  here opens with a five-line seed-and-correct helper. The correction loop's own
  `(r + 1) * (r + 1)` overflows near $2^{63}$, which is a bug the Python side simply cannot have —
  one of the clearer cases where the two languages are not the same program with different syntax.
- **Ask whether the root is needed at all.** Before an `isqrt` in a hot squareness test, a residue
  filter is nearly free: a square is $0$ or $1 \bmod 4$, and only 12 of the 64 residues $\bmod 64$ are
  possible, which rejects over 80% of candidates with a mask. Cheap checks first, expensive checks
  after.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0142](/solutions/0142/) — Perfect Square Collection
- ● [0179](/solutions/0179/) — Consecutive Positive Divisors
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0229](/solutions/0229/) — Four Representations Using Squares
- ● [0246](/solutions/0246/) — Tangents to an Ellipse
- ● [0420](/solutions/0420/) — $2 \times 2$ Positive Integer Matrix
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0719](/solutions/0719/) — Number Splitting

<!-- /problems -->
