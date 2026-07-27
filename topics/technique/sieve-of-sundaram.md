<!-- tags: [sieve-of-sundaram] -->
<!-- status: final -->
# Sieve of Sundaram

The [Sieve of Sundaram](https://en.wikipedia.org/wiki/Sieve_of_Sundaram) enumerates the primes
below a bound without ever looking at an even number. Instead of striking out multiples of
primes, it strikes out the *indices* of odd composites, using one small piece of algebra: an
index `k` survives exactly when `2k+1` is prime. It is the sieve this repository reaches for by
default whenever a solution needs a list of primes up to a known bound — problems 7, 10, 27, 35,
49, 50, 51, 60, 77 and 87 all open with the same twenty-line helper.

## Why the marking rule works

Every odd composite factors into two odd factors greater than one. Write them as `2i+1` and
`2j+1` with `i, j ≥ 1`, and multiply out:

```
(2i + 1)(2j + 1) = 4ij + 2i + 2j + 1 = 2(i + j + 2ij) + 1
```

So the odd number `2k+1` is composite **if and only if** `k = i + j + 2ij` for some
`1 ≤ i ≤ j`. That single identity is the whole sieve. Allocate a flag array over
`k ∈ [1, n]` where `n = (N-1)/2`, mark every `i + j + 2ij` that lands inside it, and read the
survivors back as `2k+1`:

```python
def primes_sundaram_sieve(max_num: int) -> tuple[int, ...]:
    if max_num < 2:
        return ()
    n = (max_num - 1) // 2
    marked = bytearray(n + 1)
    for i in range(1, n + 1):
        j = i
        while i + j + 2 * i * j <= n:
            marked[i + j + 2 * i * j] = 1
            j += 1
    primes = [2] if max_num >= 2 else []
    primes.extend((2 * i + 1 for i in range(1, n + 1) if not marked[i]))
    return tuple(primes)
```

Two details in that code are not decoration. `j` starts at `i`, not at 1, because the pair
`(i, j)` and the pair `(j, i)` mark the same index — starting at `i` halves the work at no cost
in coverage. And `2` is prepended by hand: the sieve's universe is the odd numbers, so the one
even prime is structurally invisible to it and must be special-cased. Forgetting that is the
classic Sundaram bug, and it is silent — you get an answer, just the wrong one.

## What it buys, and what it costs

Against the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes) the
trade is clear once you look at both axes:

| | Eratosthenes (odd-only) | Sundaram |
|---|---|---|
| Marks performed | `O(N log log N)` | `O(N log N)` |
| Flag array | `N/2` entries | `N/2` entries |
| Index → number | `2k+1` | `2k+1` |

The memory is identical — both are really sieving the odds — but the marking cost is not.
Eratosthenes touches each composite roughly once per *distinct prime factor*; Sundaram touches
it once per *factorization into two odd factors*, which is the divisor count, and summing that
over the range gives the extra `log N`. In exchange you get a loop with no primality test, no
`p*p` start offset, no `√N` cutoff, and no inner conditional at all: the marking rule is pure
arithmetic on `i` and `j`. For the bounds these problems use — sieves in the millions — the
constant factor of that tight loop makes the asymptotic difference largely academic. Push the
bound to 10⁸ and it stops being academic; that is when to switch.

There is also a subtler cost. Eratosthenes leaves behind a **primality oracle** you can index
directly: `sieve[m]` answers "is `m` prime?" for any `m`. Sundaram's array is indexed by `k`,
not by the number, so answering the same question means mapping `m → (m-1)//2` and handling
`m = 2` and every even `m` separately. When a solution wants membership tests rather than
enumeration, it typically does what problems 35 and 50 do — take the returned tuple and build a
`set` from it — which pays an extra pass and an extra copy. If the problem is dominated by
lookups, an Eratosthenes table read in place is the better shape.

## How to reason about it

Reach for Sundaram when you want **the primes as a list**, ascending, up to a bound you know
before you start — which is most of what these problems need. Prime-power triples build three
lazy generators over one ascending prime tuple (problem 87); consecutive prime sums run
`itertools.accumulate` straight down it (problem 50); prime pair sets treat it as the vertex
list of a graph (problem 60). None of them wants a boolean table; all of them want an ordered
sequence, and Sundaram produces one without a filtering pass over the evens.

Two habits matter more than the choice of sieve:

- **Size the sieve to the input, inside `solve()`.** Problem 7 asks for the 10 001st prime,
  which has no natural bound — so it sieves to `n·ln n`, the prime-number-theorem estimate of
  the n-th prime, and indexes the survivors. Every solution here defines its own
  `primes_sundaram_sieve` as a local helper rather than importing a shared, module-level table:
  the harness times repeated `solve()` calls, so a table built once at import would be free on
  every run after the first and would quietly understate the real cost.
- **Watch the inner-loop bound, not the outer one.** The outer `i` loop nominally runs to `n`,
  but for `i` past roughly `√(n/2)` the inner `while` fails on its first test and does nothing.
  The loop is self-limiting, which is why the naive bound is harmless — but it also means an
  `i`-loop written to stop early buys you nothing measurable. The cost is in the marks.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0007](/solutions/0007/) — 10 001st Prime
- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0027](/solutions/0027/) — Quadratic Primes
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0050](/solutions/0050/) — Consecutive Prime Sum
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0087](/solutions/0087/) — Prime Power Triples

<!-- /problems -->
