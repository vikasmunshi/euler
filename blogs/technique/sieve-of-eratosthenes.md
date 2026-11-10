<!-- tags: [sieve-of-eratosthenes] -->
<!-- status: final 2026-11-02T22:26Z -->
# Sieve of Eratosthenes

The [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes) finds
every prime up to a bound `N` by elimination: start with all numbers from 2 to `N`
marked prime, then for each number still marked, strike out its multiples. Whatever
survives is prime. It is the default answer whenever a problem needs *many* primes below
a bound you know in advance — but its real value in Project Euler is often the artefact
it leaves behind, not the enumeration itself, and at the largest bounds it survives as
the small-number tier of an algorithm that never touches most of the range.

## The mechanism

Two observations turn the naive "cross out every multiple of every prime" into something
fast:

- **Start at `p*p`.** When you reach a prime `p`, every multiple of `p` below `p*p` — that
  is `2p, 3p, … (p-1)p` — was already struck out by a smaller prime factor. So the first
  multiple worth touching is `p*p`.
- **Stop at `√N`.** Once `p*p > N` there is nothing left to strike: any composite `≤ N`
  has a prime factor `≤ √N`, so by the time you have sieved with every prime up to `√N`,
  every composite is already marked.

Those two bounds are what give the sieve its `O(N log log N)` running time — near-linear,
and the reason it beats testing each number one at a time. The whole thing is a few lines
of strided assignment over a byte array (`solutions/public/p0010/`):

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

Assigning a zero-filled slice with a stride of `i` marks every multiple in one operation,
which is what makes this far faster than a Python loop that visits each multiple by hand.

## The table is the point

`sieve` is not just a step toward a list of primes — it is a **primality oracle**:
`sieve[k]` answers "is `k` prime?" in `O(1)`, for every `k` up to the bound, for the rest
of the program. A great many prime problems are really "build the oracle once, then query
it a lot": circular primes rotate a candidate's digits and test each rotation
(`solutions/public/p0035/`), truncatable primes chip digits off both ends and test the
survivors (`solutions/public/p0037/`). Both do thousands of membership checks; both want a
table, not a fresh test each time. If your solution calls a primality function in a tight
loop, a sieve that precomputes the answers is usually the speed-up.

The oracle need not be queried one number at a time, either. In problem 333 a dynamic
programme counts, for every `n` below the bound, its valid partitions; the answer wants the
primes whose count is exactly one, and with the sieve held as a boolean array that filter is
a single elementwise AND of two tables. A running sum turns the table into a second
artefact: `cumsum(is_prime) − 1` maps every prime to its rank `π(p) − 1`, so the primes can
be renumbered `0, 1, 2, …` with one lookup. Problem 425 needs exactly that. It treats the
primes below ten million as the vertices of a graph — two primes are joined when changing
one digit, or dropping the leading one, turns one into the other — keeps a union–find array
indexed by prime rank rather than by value, and generates the edges with the oracle too,
testing every one-digit neighbour of every prime as one vectorised query per digit
position.

The same idea generalises past a boolean: sieve a table of each number's **smallest prime
factor**, and you can factor any number up to the bound by repeated lookup, with no trial
division at all — the right tool when a problem needs the *factorisations* of a whole
range, not merely which numbers are prime. Vectorised, it is the strike-out loop with one
guard: write `p` only into cells still empty, so the first — smallest — prime to reach a
cell keeps it. Problem 752 shows the two ways the table earns its keep. Its function `g`,
the multiplicative order of `1+√7` modulo `x`, combines across coprime factors by `lcm`, so
it is fixed by its values at prime powers. Walking `x` upward, `spf[x]` names the smallest
prime `p`, the exact power `p^k` dividing `x` follows from the entry already computed for
`x/p`, and `g(x) = lcm(g(x/p^k), g(p^k))` reads both operands from cells already filled —
one `lcm` per number, no factorisation loop at all. And computing an order at a prime `p`
needs the factorisation of the group order, `p − 1` or `p + 1`, so the same table is
queried at the *neighbours* of primes — which is why it runs to `N + 1`, not `N`.

Sometimes the oracle is queried about numbers the problem never names. Problem 249 counts
the subsets of the primes below 5000 whose sum is prime: the subset sums are tabulated by a
0/1-knapsack pass, and the sieve exists to answer "is this *total* prime?" — so it runs to
the largest possible sum, about 1.5 million, not to 5000. And sometimes only one number
off the table matters: in problem 239 the formula is symmetric in the primes, so the sieve
is consulted once, for the count `π(100)`, and which discs carry primes never enters the
argument.

## Sieve a function, not a flag

The strike-out loop does not care what it writes. Visit each prime's multiples and apply
that prime's contribution, and any [multiplicative
function](https://en.wikipedia.org/wiki/Multiplicative_function) falls out for the whole
range at once. Euler's totient is the classic case — every multiple of `p` loses the factor
`(p-1)/p` (`solutions/public/p0072/`):

```python
euler_totients = list(range(max_d + 1))
for n in range(2, max_d + 1):
    if euler_totients[n] == n:          # untouched, so n is prime
        for j in range(n, max_d + 1, n):
            euler_totients[j] = euler_totients[j] // n * (n - 1)
```

No separate primality array is needed: a cell still equal to its index has never been
touched, so it is prime. The [Möbius function](https://en.wikipedia.org/wiki/M%C3%B6bius_function)
is the same shape with a different rule — start every entry at `+1`, flip the sign on each
prime's multiples, zero the multiples of each prime's square — and it underlies problems
319 and 464, whose answers are built from its running sum, the [Mertens
function](https://en.wikipedia.org/wiki/Mertens_function). Problem 319 adds one economy
worth knowing: sieve with only the primes up to `√K`, keep a parallel array that divides out
every prime power found, and any cofactor left above 1 is a single prime greater than `√K`
(two would exceed `K`), settled by one closing sign flip. That swaps a loop over all `π(K)`
primes for one over `π(√K)`.

Problem 619 carries that cofactor trick to a window `[a, b]` that does not start at 1, and
to a value that is a vector rather than a number. It counts the subsets of `[a, b]` whose
product is a perfect square — linear algebra over GF(2) on each number's vector of exponent
*parities*. So each cell of the sieve holds a bitmask: for every prime `p ≤ √b`, start at
the first multiple inside the window (offset `−a mod p`), divide `p` out of a remainder
array as often as it goes, and flip bit `p` when it went an odd number of times. What is
left in each cell is `1` or a single prime above `√b`, and those large primes never need a
column of their own: the first number carrying one becomes its pivot and is XORed out of
every later carrier, so each adds exactly one to the rank, and the Gaussian elimination
runs over the `π(√b)` small-prime columns alone.

## Variants, and when you need them

- **Bounded array** — the default above. You know `N`, it fits in memory, you want a table.
- **Unbounded / incremental** — when you do *not* know the bound: you need "primes until
  some condition holds", not "primes below `N`". An incremental sieve is a generator that
  keeps a dictionary mapping each known prime's next multiple to the prime, and yields
  primes forever with no ceiling fixed in advance (`solutions/public/p0010/` carries one
  such generator; `solutions/public/p0037/` streams primes from Eppstein's dict-based
  version until the eleven truncatable primes are found). You trade the array's raw speed
  for not having to guess `N`.
- **Doubling** — the middle road, when the bound is unknown but every query has the form
  "the primes up to `x`". Keep an ordinary array sieve; when a query passes its bound,
  rebuild it at twice the size (or at `x`, if that is larger). The rebuilds form a
  geometric series, so the total work stays under twice that of one sieve to the final
  bound, and every query is still answered from a flat array at full speed. Problem 946
  feeds primes, in order, as run lengths into a continued-fraction engine and cannot know
  how many it will consume; problem 829 needs all primes below bounds that its own search
  keeps doubling. Both start small and grow.
- **Segmented** — when `N` is known but the array will not fit: sieve `[1, √N]` once for
  the small primes, then sweep the range in cache-sized windows, marking each window with
  those primes. Same primes, bounded memory. Problem 619's window `[a, b]` is the same
  structure put to work factoring rather than testing.
- **Odd-only** — store only the odd numbers, index `i` standing for `2i+1`. Half the
  memory and half the strikes, at the price of index arithmetic. It matters when the sieve
  *is* the program: in problem 315 the per-prime work collapses to two table lookups, so
  sieving to `2·10⁸` is what remains, and its cost is mostly memory traffic — 100 MB beats
  200 MB.
- **Sieve of Sundaram** — a variant that marks `i + j + 2ij` to knock out the odd
  composites directly (`solutions/public/p0010/` has one for contrast). It is a tidy
  curio, but at `O(N log N)` it is asymptotically slower than Eratosthenes; reach for it to
  understand the family, not for speed.

For contrast, the same `solutions/public/p0010/` also solves the problem by trial-division
primality on each candidate — correct, and `O(N√N / log N)`, which is exactly the blow-up
the sieve exists to avoid when the question is about a whole range.

## When the bound is too big to sieve

Past about `10⁹` a full table stops being an option — problem 245 works up to `2·10¹¹`,
where a totient sieve would need hundreds of gigabytes. The sieve does not disappear; it
shrinks to a *fraction* of the bound and becomes one tier of a larger algorithm. Two
patterns recur.

- **Sieve the small primes, construct the large one.** Every `n ≤ N` has at most one prime
  factor above `√N`, and at most two above `N^(1/3)`. So sieve to the root, and handle the
  part beyond it by algebra plus a primality test rather than by lookup. In problem 245 the
  sieve runs to `√N`, the largest prime of each candidate is *solved for* from the
  divisibility condition, and a deterministic
  [Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) test
  confirms it. Problem 241 sieves only to `N^(1/3)`: any tail of larger primes must have
  the shape `p`, `p²` or `pq`, and each shape pins its primes through a residual fraction —
  the `pq` case as the roots of a quadratic. Problem 251 uses its sieve, to `√((L+1)/6)`,
  only as the prime list for trial division.
- **Sieve to `n^(2/3)`, recurse above it.** Summatory functions — `Φ(n) = Σ φ(k)` in
  problem 351, the Mertens function in problem 319 — satisfy identities such as
  `Σ_{d≤v} Φ(⌊v/d⌋) = v(v+1)/2` that express the value at `v` through values at the
  quotients `⌊v/d⌋`. Only `O(√n)` distinct quotients exist, so a function sieve answers
  every quotient below a cutoff `L` directly and the recursion fills in the few above it.
  The two costs, `O(L)` for the sieve and `O(n/√L)` for the recursion, balance at
  `L = n^(2/3)`, which is the whole algorithm's complexity: problem 319 reaches `n = 10¹⁰`
  from a sieve of under five million entries. The values above the cutoff need no memo
  dictionary either. Each is `F(⌊n/k⌋)` for a small `k`, and `⌊⌊n/k⌋/d⌋ = ⌊n/(kd)⌋`, so
  a plain array indexed by `k`, filled in *decreasing* `k`, already holds every large
  term the recursion for `k` asks for. Problem 512 shows what this two-tier table buys
  once it exists. Its sum of `φ` over the *odd* `n ≤ N` peels off the even part with
  `φ(2m) = φ(m)` or `2φ(m)`, giving `Φ(N) − Σ Φ(⌊N/2ᵏ⌋)`. Every `⌊N/2ᵏ⌋` is already one
  of the quotients the table covers, so restricting to odd `n` costs `log₂ N` lookups and
  no extra sieving.

## Things to get right

- **Size it to the inputs.** When the problem gives you an *index* — "the `n`-th prime" —
  rather than a value ceiling, use the prime number theorem's estimate that the `n`-th
  prime is near `n·ln n` and sieve that far. When it gives a value bound, sieve to the
  bound — or to the largest number you will actually *query*, which is not always the
  input (problem 249's subset sums, problem 752's `p + 1`), and not always all of it (the
  roots and `n^(2/3)` above). When you cannot know it at all, double.
- **Know whether it is the bottleneck.** In problem 365 the sieve covers primes below
  10 000 and is then followed by twenty million Chinese-remainder lifts; a segmented or
  wheel sieve there would be effort spent on nothing. In problem 315 the sieve *is* the
  cost, and halving it pays. Measure before optimising it.
- **Build it inside `solve()`.** Construct the sieve on each call, sized to the inputs —
  not once at module level. With `--runs=N` the harness times repeated `solve()` calls; a
  sieve built once at import is excluded from the first run and free thereafter, which
  flatters the benchmark and hides the cost that is often the bulk of the work.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0023](/solutions/0023/) — Non-Abundant Sums
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0069](/solutions/0069/) — Totient Maximum
- ● [0070](/solutions/0070/) — Totient Permutation
- ● [0072](/solutions/0072/) — Counting Fractions
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0124](/solutions/0124/) — Ordered Radicals
- ● [0127](/solutions/0127/) — abc-hits
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0157](/solutions/0157/) — Base-10 Diophantine Reciprocal
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0187](/solutions/0187/) — Semiprimes
- ● [0193](/solutions/0193/) — Squarefree Numbers
- ● [0196](/solutions/0196/) — Prime Triplets
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0204](/solutions/0204/) — Generalised Hamming Numbers
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0221](/solutions/0221/) — Alexandrian Integers
- ● [0228](/solutions/0228/) — Minkowski Sums
- ● [0231](/solutions/0231/) — Prime Factorisation of Binomial Coefficients
- ● [0233](/solutions/0233/) — Lattice Points on a Circle
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0241](/solutions/0241/) — Perfection Quotients
- ● [0245](/solutions/0245/) — Coresilience
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0251](/solutions/0251/) — Cardano Triplets
- ● [0291](/solutions/0291/) — Panaitopol Primes
- ● [0304](/solutions/0304/) — Primonacci
- ● [0313](/solutions/0313/) — Sliding Game
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ● [0319](/solutions/0319/) — Bounded Sequences
- ● [0333](/solutions/0333/) — Special Partitions
- ● [0347](/solutions/0347/) — Largest Integer Divisible by Two Primes
- ● [0351](/solutions/0351/) — Hexagonal Orchards
- ● [0357](/solutions/0357/) — Prime Generating Integers
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0425](/solutions/0425/) — Prime Connection
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0464](/solutions/0464/) — Möbius Function and Intervals
- ● [0478](/solutions/0478/) — Mixtures
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0619](/solutions/0619/) — Square Subsets
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ● [0771](/solutions/0771/) — Pseudo Geometric Sequences
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0787](/solutions/0787/) — Bézout's Game
- ● [0800](/solutions/0800/) — Hybrid Integers
- ● [0829](/solutions/0829/) — Integral Fusion
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0946](/solutions/0946/) — Continued Fraction Fraction
- ● [0962](/solutions/0962/) — Angular Bisector and Tangent 2
- ● [0975](/solutions/0975/) — A Winding Path
- ● [0995](/solutions/0995/) — A Particular Pair of Polynomials

<!-- /problems -->
