<!-- tags: [segmented-sieve] -->
<!-- status: final -->
# Segmented sieve

A [segmented sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve) runs the
[Sieve of Eratosthenes](/blogs/technique/sieve-of-eratosthenes) one window at a time instead of
over the whole range at once. Each window `[lo, hi)` gets a fresh array, and you sieve it using
only the primes up to $\sqrt{hi}$. The textbook reason is memory, but in the six problems below
memory is only one of three separate benefits. Segmenting also lets a sieve start far from 1, and
it lets a sieve run when nobody knows where it should stop. Most of these problems also use the
same trick for the one large prime factor a number can have, and that trick is often what makes the
sieve affordable in the first place.

## The idea

Every composite $n < hi$ has a prime factor at most $\sqrt{hi}$. So to sieve a window you need just
two things: the base primes up to $\sqrt{hi}$, found once with a small ordinary sieve, and for each
base prime $p$ the first multiple of $p$ inside the window. That first multiple sits at offset
$(-lo) \bmod p$. From there the work is a strided walk, the same one the classic sieve does,
shifted to start at `lo`:

```python
for p in base_primes:                       # primes <= isqrt(hi - 1)
    start = max(p * p, lo + (-lo) % p)      # first multiple of p in [lo, hi) worth marking
    window[start - lo :: p] = 0             # one strided write per prime per window
```

The base primes take $O(\sqrt{hi})$ memory and the window takes $O(hi - lo)$. The total work is
still $O(N \log\log N)$. The extra cost is one offset computation per prime per window. That
overhead is the only thing you pay, and the choice of window size is a trade against it.

The same walk is not limited to crossing out composites. If you walk the multiples starting at the
first multiple $\ge lo$ (not at $p^2$), you can do anything per-prime on each number in the window:
divide $p$ out, flip a sign, increment a count, multiply in a factor. That turns the segmented sieve
into a **segmented factorizer**, and four of the six problems use it that way.

### The one-large-prime residual

A number below $hi$ has **at most one** prime factor above $\sqrt{hi}$, since two of them would
multiply past $hi$. So after the base primes have been applied, whatever is left of each number is
either 1 or exactly one large prime. You can tell which by keeping one of two side arrays:

- a **residual** array, starting at $n$, with every power of $p$ divided out of it as $p$ is walked.
  Whatever remains above 1 at the end is the large prime itself;
- a **product** array, starting at 1, multiplied by each distinct small prime that divides $n$. If
  $n$ is [square-free](/blogs/domain/square-free-integer) and the product is less than $n$, then $n$
  has a large prime. You learn that it exists but not its value, which is often all you need.

Without this trick you would have to sieve with every prime up to $N$ to factor completely. With it
you sieve only with the primes up to $\sqrt{N}$, plus one final pass over the window.

## What the segmentation buys, problem by problem

| problem | sieved quantity | window | what segmenting buys |
| --- | --- | --- | --- |
| 531 | $\varphi(n)$ | one short interval near $10^6$ | starting far from 1 |
| 619 | prime-exponent parity of $n$ | one interval $[a, b]$ | starting far from 1, and the large prime exposed |
| 632 | square-free flag and $\omega(d)$ | blocks of $2^{22}$ up to $10^8$ | bounded memory |
| 754 | $\mu(d)$ and running products | blocks of $2^{22}$ up to $10^8$ | bounded memory, with state carried across windows |
| 256 | a divisor-style count $T(s)$ | blocks of $2^{24}$, open-ended | an unknown upper bound and an early stop |
| 971 | primes $\equiv 1 \pmod 5$ | blocks of $2^{25}$ up to $10^9$ | streaming into vectorized per-prime work |

**Starting far from 1 (531, 619).** Problem 531 needs [Euler's
totient](/blogs/domain/eulers-totient-function) only on a window of a few thousand integers just
above $10^6$. An ordinary sieve would compute a million totients to read a few thousand of them. A
segmented one walks the base primes up to about $1000$ across just that window, updating
$\varphi \leftarrow \varphi - \varphi/p$ and reducing a residual. Any residual left above 1 is the
large prime, and one more pass applies its factor. Problem 619 does the same over its interval, but
records the *parity* of each small-prime exponent as a bit in a mask. Here the residual matters for
more than the factorization. The large prime is exactly the coordinate that the
[GF(2) elimination](/blogs/technique/gaussian-elimination) handles by pivoting, and that is what
narrows the matrix down to the $\pi(\sqrt{b})$ small-prime columns. In both problems the window
*is* the problem, so the sieve never needs to touch anything outside it.

**Bounded memory (632, 754).** Both problems sieve over $d \le 10^8$. Problem 632 needs a square-free
flag and the distinct-prime count $\omega(d)$, and Problem 754 needs the [Möbius
function](/blogs/domain/mobius-function) $\mu(d)$. Each runs in windows of $2^{22}$, so the working
arrays stay a few tens of megabytes instead of several hundred. Both sieve with only the primes up
to $10^4$ and then use the product test to detect the large prime. That test matters more in
[NumPy](/blogs/technique/numpy) than it looks. Each base prime costs one
[strided slice](/blogs/technique/extended-slice) per window, and each slice has a fixed per-call
overhead. Sieving with the roughly 5.7 million primes below $10^8$ would mean millions of
tiny slices per window. One vectorized comparison replaces all of them.

Problem 754 shows the part of segmentation that is easy to get wrong: **state that crosses window
boundaries**. Its window computes running quantities: factorials, superfactorials, signed products
of square-free $d$, and a Mertens sum. A running product does not reset at `lo`. Each window takes
the previous window's final value as its carry-in, just as a [prefix sum](/blogs/technique/prefix-sum)
would. The solution also saves only the values at the checkpoints $\lfloor N/k \rfloor$, because
those are the only ones the later quotient-block assembly reads. So segmentation bounds the output
as well as the working arrays.

**An unknown upper bound (256).** Problem 256 asks for the *smallest* area $s$ whose count of
tatami-free rooms reaches a target. That count is a divisor-function-style quantity, sieved in
reverse: for each width $a$ and each band of bad lengths $b$, increment $T(ab)$. The answer's size
is not known in advance, so a single array cannot be sized to it. The solution works through
consecutive windows of $2^{24}$ areas. For each width it clips the length range to the window,
skips straight to the first band that can overlap it, and applies one strided update per band.
After each window it scans for the first counter at the target and stops there. This sieve does not
compute primes at all, yet the structure is the same: a strided walk per generator, clipped to the
window at offset $\lceil lo/a \rceil$. The window also sets the counter width. A fresh window of
16-bit counters is enough, because no single window has to hold a total that accumulates across
windows.

**Streaming (971).** Problem 971 needs every prime $p \equiv 1 \pmod 5$ up to $10^9$ and does a
fixed set of modular exponentiations on each. The solution asks
[`primesieve`](/blogs/technique/primesieve) for one window of $2^{25}$ at a time and runs the
per-prime arithmetic on each window's primes as whole
[NumPy arrays](/blogs/technique/vectorized). Here segmentation is a streaming interface. Holding
the roughly fifty million primes below $10^9$, plus 64-bit working arrays for the ones it keeps,
all at once would cost gigabytes. One window's
worth is small, and it is still big enough that the interpreter overhead per window is negligible.

## How to reason about it

- **Segment when one of three things is true:** the range will not fit in memory (632, 754, 971), the
  range you care about does not start at 1 (531, 619), or you do not know where the range ends
  (256). If none of these holds, a plain sieve is simpler and just as fast.
- **The offset is the whole algorithm.** `lo + (-lo) % p` is the first multiple at or above `lo`.
  For crossing out composites, start at `max(p * p, …)`, or the window will mark $p$ itself as
  composite when $p \ge lo$. For factoring, start at the first multiple, because $p$ itself has
  the factor $p$.
- **Sieve with $\sqrt{hi}$ primes, then read the residual.** If you catch yourself sieving with every
  prime up to $N$ in order to factor numbers below $N$, use a residual array or product array
  instead. The large prime is either 1 or the single leftover factor.
- **Pick the window size for the implementation.** In C the right size is about the L2 cache, so
  the window stays resident while every base prime walks it ([locality of
  reference](/blogs/technique/locality-of-reference)). In NumPy the cost that matters is the
  number of slice calls, windows × base primes, so larger windows of $2^{22}$ to $2^{25}$ work
  better: big enough to amortise each call, small enough to keep memory bounded.
- **Decide what crosses the boundary.** Per-element results (a totient, a flag, a count) are local
  to their window. Running quantities (products, cumulative sums, Mertens values) need a carry-in,
  and any off-by-one in passing it along spreads silently into every later window.
- **Size the counters for one window, not for the whole run.** A fresh array per window means a
  per-window maximum is enough to choose an element type, as long as the totals are accumulated
  outside the window.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0256](/solutions/0256/) — Tatami-Free Rooms
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ● [0619](/solutions/0619/) — Square Subsets
- ● [0632](/solutions/0632/) — Square Prime Factors
- ● [0754](/solutions/0754/) — Product of Gauss Factorials
- ● [0971](/solutions/0971/) — Modular Polynomial Composition

<!-- /problems -->
