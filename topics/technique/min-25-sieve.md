<!-- tags: [min-25-sieve] -->
<!-- status: final -->
# Min_25 sieve

The [Min_25 sieve](https://codeforces.com/blog/entry/117635) computes `F(n) = Σ_{k ≤ n} f(k)`
for a [multiplicative function](/topics/domain/multiplicative-function) `f`, in roughly
`O(n^{3/4} / log n)` time and `O(√n)` memory. It never touches all `n` integers. The only
requirements are that `f(p)` is cheap to sum over primes and that `f(pᵉ)` is cheap to evaluate. It
does this in two phases. The first is the Lucy_Hedgehog table from the
[Prime-counting function](/topics/domain/prime-counting-function) page, which sums `f` over the
**primes** at every quotient `⌊n/k⌋`. The second is a walk over smallest prime factors, which adds
the **composites** back. Once phase 1 has been written for `π`, phase 2 is a few more lines, and
it extends the method from counting primes to summing any multiplicative function. The three
problems below use it in three different ways: one sums a divisor function, one sums over a
complement set, and one sums a function that is not multiplicative at all but has the same tree.

## Phase 1: the primes, at every quotient

Lucy's DP runs Eratosthenes on *counts*. `S(v)` starts as the weight of every integer in `[2, v]`.
For each prime `p ≤ √n`, it removes the integers whose smallest prime factor is `p`:

```
S(v) ← S(v) − w(p) · ( S(⌊v/p⌋) − S(p−1) )        for every key v ≥ p², largest v first
```

After the last prime, `S(v) = Σ_{p ≤ v} w(p)` at all of the roughly `2√n` keys. The recurrence
only holds when the weight `w` is **completely multiplicative**, because the struck number `p·m`
has to weigh `w(p)·w(m)` whatever `m` is. That holds for `w = 1` (counting), `w = p` (sums of
primes) and `w = pᵏ`. Min_25 relies on this. You expand `f(p)` as a polynomial in `p`, run one
table for each power, and combine the results. The `π` page explains the storage
(`small[v]` and `large[n/v]`) and why every argument the algorithm reaches is a key, so I won't
repeat it here.

The three problems need very little from phase 1:

- **452** needs `f = d_n`, the `n`-fold divisor function. `d_n(p) = n` is constant on primes, so
  one count table, scaled by `n`, is enough.
- **642** needs the count *and* the sum of primes. That is two tables in the same sweep, kept
  modulo `10⁹`.
- **565** needs `g(p) = p` unless `p ≡ −1 (mod 2017)`, in which case `g(p) = 0`. That weight is
  **not** a polynomial in `p`. A residue-class condition would need a table for every
  [Dirichlet character](https://en.wikipedia.org/wiki/Dirichlet_character) mod 2017, which is 2016
  tables. So the faster solution, `s1`, skips Lucy entirely. It streams every prime up to `10¹¹`
  from [primesieve](/topics/technique/primesieve) in fixed-size chunks and records the running
  `g`-sum each time it passes a key. That costs linear time but only `O(√n)` memory, and primesieve
  is fast enough to make it work. The design lesson is that **phase 2 only needs the key table, not
  any particular way of building it**. The prototype `s0` fills the same table with a full sieve and
  prefix sums, and refuses `n > 10⁹`.

## Phase 2: putting the composites back

Let `S(x, j)` be the sum of `f(k)` over `2 ≤ k ≤ x` whose smallest prime factor is at least `pⱼ`.
Every such `k` is either a prime in `[pⱼ, x]`, which phase 1 gives directly, or has the form
`pᵢᵉ · r`, where `pᵢ` is its smallest prime and every factor of `r` is larger than `pᵢ`.
Multiplicativity splits `f(pᵢᵉ r) = f(pᵢᵉ) f(r)`, and so:

```
S(x, j) = Σ_{pⱼ ≤ p ≤ x} f(p)                                    ← phase-1 table, minus a small prefix
        + Σ_{i ≥ j, pᵢ² ≤ x}  Σ_{e ≥ 1, pᵢ^{e+1} ≤ x}
              ( f(pᵢᵉ) · S(⌊x/pᵢᵉ⌋, i+1)  +  f(pᵢ^{e+1}) )
```

`F(n) = f(1) + S(n, 0)`. The trailing `f(pᵢ^{e+1})` term adds the pure prime powers, which the
recursive call leaves out because `S` starts at 2. Two facts make this cheap. First, every
`⌊x/pᵢᵉ⌋` is again a quotient of `n`, so the prime term is a single table lookup. Second, the
loop over `i` stops at `pᵢ² ≤ x`. A number with no prime factor below `p` and no room for `p²` is
prime, and the table has already counted the primes. The recursion is **not memoised**. Its depth
is at most the number of distinct prime factors, and its node count is about `n^{3/4} / log n` for
the sizes Project Euler uses. The theoretical bound is `n^{1−ε}`, but in practice it runs neck and
neck with phase 1.

The three problems fill in `f` like this:

| Problem | `f` | `f(p)` | `f(pᵉ)` | Phase 1 source |
| --- | --- | --- | --- | --- |
| 452 | `d_n(k)`, ordered `n`-tuples with product `k` | `n` | `C(n+e−1, e)` ([stars and bars](https://en.wikipedia.org/wiki/Stars_and_bars_(combinatorics))) | Lucy count table |
| 565 | `k`·[no prime power `pᵉ ∥ k` has `2017 ∣ σ(pᵉ)`] | `p` or `0` | `pᵉ` or `0` | primesieve stream |
| 642 | largest prime factor of `k` (not multiplicative) | `p` | — | Lucy count + sum tables |

**565 sums over the complement.** The set it asks about, integers whose `σ` is divisible by 2017,
is not multiplicative. Its complement is, because a prime `d` divides `σ(k) = Π σ(pᵉ)` exactly
when it divides one of the factors. So the answer is `n(n+1)/2` minus the Min_25 sum of `g`. When a
condition holds if *any* prime power satisfies something, its negation holds if *every* prime
power fails it, and that negation is multiplicative.

**642 shows that phase 2 is really a tree walk.** The largest prime factor `P(k)` is not
multiplicative, yet 642's DFS has the same shape. It walks the smooth part `m` through increasing
primes, and at each node it adds the sum of the primes in `(P(m), ⌊N/m⌋]`. That is "every `k = m·P`
with `P` larger than anything in `m`". The phase 2 tree enumerates every integer `≤ n` once, as a
chain of prime powers in increasing order with its largest prime left implicit. Any function that
depends only on that chain and its implicit last prime can be summed this way: multiplicative
functions, but also the largest prime factor and similar "last prime" statistics.

A schematic of the walk, with phase 1 abstracted as `prime_part(x, j)`:

```python
def walk(x, j):
    total = prime_part(x, j)                 # Σ f(p), pⱼ ≤ p ≤ x — one table lookup
    for i in range(j, len(primes)):
        p = primes[i]
        if p * p > x: break
        pe, e = p, 1
        while pe * p <= x:
            total += f_pow(p, e) * walk(x // pe, i + 1) + f_pow(p, e + 1)
            pe, e = pe * p, e + 1
    return total
```

## Min_25, Lucy and Meissel–Lehmer side by side

| Method | Answers | Weights on primes | Cost |
| --- | --- | --- | --- |
| [Meissel–Lehmer](/topics/domain/meissel-lehmer-algorithm) / LMO / Deléglise–Rivat | one `π(x)` | count (sums with more work) | `O(x^{2/3} / log² x)` |
| Lucy_Hedgehog table | `Σ_{p ≤ v} w(p)` at **every** `⌊n/k⌋` | completely multiplicative `w` | `O(n^{3/4} / log n)`, `O(√n)` memory |
| Min_25 (Lucy + walk) | `Σ_{k ≤ n} f(k)`, over all integers | `f(p)` a polynomial in `p`; `f(pᵉ)` anything cheap | about the same as Lucy |

Meissel–Lehmer is the right choice when you need one very large `π`, and the Lucy table is the
right choice when you need `π` at many quotients. The [Meissel–Lehmer
page](/topics/domain/meissel-lehmer-algorithm) shows that Lucy is Legendre's `φ` recursion
memoised over quotients. Min_25 is what you get when you then put the composites back. Its walk
is Legendre's recursion run the other way: instead of striking out numbers by smallest prime
factor, it builds them up by smallest prime factor. The
[Summing Multiplicative Functions](/topics/number-theory/summing-multiplicative-functions) page
covers the other route to `Σ f`, which factors `f` as a Dirichlet convolution and walks the
hyperbola. That route wins when `f = g * h` with both summatory functions in closed form, as with
`σ`, `φ` and squarefree indicators. Min_25 wins when no such factorisation is convenient, but `f`
on prime powers is explicit. `d_n` is an example: its `n`-fold convolution of `1` is awkward to
walk for large `n`, but `C(n+e−1, e)` is one line.

## How to reason about it

- **Check the two inputs.** Can you sum `f(p)` over primes at every quotient, and can you evaluate
  `f(pᵉ)`? If both are yes, Min_25 applies. If `f(p)` is a polynomial in `p`, use one Lucy table per
  power. If not, any way of filling the key table will do, including streaming primes (565).
- **Turn "some prime power has property X" into its complement.** "No prime power has X" is
  multiplicative, and the total minus that sum is the answer.
- **The tree is more general than multiplicativity.** If a statistic of `k` is determined by its
  prime-power chain plus its largest prime (642), the same walk sums it.
- **Reduce at every step.** Tables kept mod `M` give differences that can go negative, so add `M`
  back before taking `%` in C. Seeds such as `v(v+1)/2` overflow 64 bits near `10¹¹` unless you
  halve the even factor first.
- **Budget Python honestly.** Phase 1 vectorises with NumPy. Phase 2 is scalar recursion and does
  not. In 452 that leaves C about 30 times faster, which is the gap to expect from this method.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0452](/solutions/0452/) — Long Products
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors

<!-- /problems -->
