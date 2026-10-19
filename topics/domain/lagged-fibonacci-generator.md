<!-- tags: [lagged-fibonacci-generator] -->
<!-- status: final 2026-10-19T06:37Z -->
# Lagged Fibonacci generator

A [lagged Fibonacci generator](https://en.wikipedia.org/wiki/Lagged_Fibonacci_generator) (LFG)
produces each term from two terms further back, $s_k = (s_{k-j} \star s_{k-l}) \bmod m$, where $\star$ is usually addition. Project Euler uses one specific
additive LFG, with lags 24 and 55 and modulus $10^6$, as its standard way to generate large inputs. The
problems that use it are not about randomness. They need a million phone calls, a $2000 \times 2000$ grid,
or fifty thousand cuboids, and the generator supplies them reproducibly from a few constants. The
solutions therefore all start the same way: reproduce the stream exactly, cheaply, and in the same
order in both languages. The general family and its uses are on
[pseudorandom number generator](/topics/domain/pseudorandom-number-generator); this page is about
this one generator.

## The idea — a polynomial seed and a two-tap recurrence

The Project Euler generator, as stated in 149, 186 and 212:

$$
s_k = \begin{cases}
(100003 - 200003k + 300007k^3) \bmod 10^6 & 1 \le k \le 55,\\
(s_{k-24} + s_{k-55}) \bmod 10^6 & k \ge 56.
\end{cases}
$$

The cubic fills the 55-term state, and the recurrence then reads two of those
terms to produce each new one. The pair (24, 55) is Knuth's classic choice. The trinomial $x^{55} + x^{24} + 1$ is primitive
modulo 2, so the low bits have the maximum possible period, and the full sequence's period is
enormous compared with any input here. The generator needs only additions and the last 55 terms,
which is why it scales to millions of terms with no cost to speak of.

Three implementation consequences follow, and every solution here handles them:

- **State is 55 numbers.** Nothing older than $s_{k-55}$ is ever read, so an
  unbounded stream needs only a 55-slot ring buffer. When computing $s_k$, slot $(k-1) \bmod 55$
  still holds $s_{k-55}$, and slot $(k-25) \bmod 55$ holds $s_{k-24}$. The new term overwrites
  the slot it just consumed.
- **The seed polynomial is negative for most $k$, and C's `%` keeps the sign.** Python's `%` already
  returns a value in $[0, 10^6)$. C needs `((v % M) + M) % M`. The cubic term is about $5 \times 10^{10}$
  at $k = 55$, so it needs 64-bit arithmetic as well.
- **The smallest lag bounds parallelism.** Terms $s_k, \dots, s_{k+23}$ depend only on terms at
  least 24 back, so a block of 24 can be computed at once. That allows vectorisation.

## How the solutions consume the stream

The generator is the same in each problem. What differs is how many terms are needed, how they are
mapped into the problem's inputs, and therefore how the stream is stored.

**149, maximum-sum subsequence: a materialised grid.** Four million terms, each shifted by
$-500000$ to make signed entries, fill a $2000 \times 2000$ grid. Kadane's algorithm then runs
along every row, column and diagonal ([maximum subarray problem](/topics/technique/maximum-subarray-problem)). The whole grid is needed,
so the stream is stored in full. Python builds it with NumPy. The 55 seed terms are one vectorised
expression over an index array, and the recurrence fills **24 terms per slice assignment**,
`s[i:i+24] = (s[i-24:i] + s[i-55:i-31] + 10**6) % 10**6 - 500000`, using the minimum lag above.
C uses a scalar loop. Both add $10^6$ before the reduction because the stored terms are already
shifted negative.

**186, connectedness of a network: an unbounded stream.** Consecutive pairs
$(s_{2n-1}, s_{2n})$ are caller and called. A
[disjoint-set](/topics/technique/disjoint-set-data-structure) structure merges them until the
Prime Minister's component reaches 99% of users. The number of terms needed is not known in
advance, so neither language precomputes them. Python writes the generator as a `yield`ing
function over a 55-slot ring and draws from it with `next()`. C has `lfg_next(buf, &k)`, which
advances the same ring one term per call. Both use $O(1)$ memory however long the run is. The
solution also parametrises the user count and reduces $s_k \bmod N$ *after* generation. The
generator always runs mod $10^6$, so small test cases exercise exactly the stream from the statement.

**212, combined volume of cuboids: a fixed-length array.** Each of 50000 cuboids takes six
consecutive terms (three corner coordinates mod 10000 and three side lengths). The total,
300000 terms, is known in advance, so both languages fill a plain 1-based array and slice it six at a
time. The union volume is then computed by spatial hashing and a local
[sweep](/topics/technique/sweep-line-algorithm).

**258, a lagged Fibonacci sequence**, still unsolved here, turns the generator into the object of
study. It uses lags 2000 and 1999, and asks for a term far too distant to reach by stepping. That
calls for treating the recurrence as a [linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients)
rather than a stream.

## Python and C

| | Python | C |
|---|---|---|
| seed reduction | `%` is already non-negative | `((v % M) + M) % M` |
| seed width | arbitrary-precision `int` | `long long` (cubic ≈ $5 \times 10^{10}$) |
| bulk terms (149) | NumPy, 24 terms per slice | scalar loop |
| open-ended stream (186) | generator function + `next()` | `lfg_next` over a `long long buf[55]` |
| fixed count (212) | list, 1-based | `int` array, 1-based |

## How to reason about it

- **Match storage to consumption.** Materialise the stream only when the problem needs all of it
  at once (149). A stream consumed once, in order, needs only the 55-term ring (186).
- **Keep the generator canonical and adapt its output.** Any rescaling, shifting or reduction into the
  problem's domain belongs after generation. Then a small test case and the real case draw the
  same stream, and the published example values check the generator by themselves.
- **Check the first few terms against the statement.** 149 quotes $s_{10} = -393027$ and
  $s_{100} = 86613$. An off-by-one in the 1-based indexing or the ring slot is the most common bug,
  and those quoted terms catch it immediately. Problems that quote no terms can be checked against
  the 149 values instead, after removing its $-500000$ shift.
- **Use the minimum lag for vector speed.** Any LFG with smallest lag $j$ can be produced $j$ terms
  at a time, which is what makes the NumPy version fast.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0149](/solutions/0149/) — Maximum-sum Subsequence
- ● [0186](/solutions/0186/) — Connectedness of a Network
- ● [0212](/solutions/0212/) — Combined Volume of Cuboids
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence

<!-- /problems -->
