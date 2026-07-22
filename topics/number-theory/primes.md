<!-- tags: [sieve-of-eratosthenes, trial-division, wheel-factorization, miller-rabin-primality-test, prime-number] -->
<!-- status: final -->
# Generating and testing primes

A [prime number](https://en.wikipedia.org/wiki/Prime_number) is a whole number
greater than 1 with no divisors but 1 and itself — the multiplicative atoms every
other integer factors into. They are the single most recurrent object in Project
Euler, and the problems that touch them almost always reduce to one of three
questions: *give me every prime up to some bound*, *is this one number prime*, or
*what are the prime factors of this number*. Each question has its own right tool,
and choosing the wrong one is the usual reason a prime-heavy solution is slow.

## The three questions, and their tools

The tools sort cleanly by which question you are asking.

**Enumerate every prime up to N — the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes).**
Write down every number from 2 to `N`; walk the list, and each time you meet a
number still standing, cross out all of its multiples. What survives is exactly the
primes. The trick that makes it fast is that you start crossing out from `p*p`
(every smaller multiple of `p` already carries a smaller factor) and stop sieving
once `p*p > N`. The whole thing runs in `O(N log log N)` time — very nearly linear —
which is why, whenever a problem needs *all* the primes below a known ceiling, the
sieve is almost always the answer. In `solutions/public/p0010/` the core is three
lines of `bytearray` strided assignment:

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

The one subtlety a sieve carries into Euler work is the *bound*. You often want "the
first `n` primes" rather than "primes below `N`", and you must size the sieve before
you know where the `n`-th prime lands. The [prime number theorem](https://en.wikipedia.org/wiki/Prime_number_theorem)
gives the estimate: the `n`-th prime is near `n·ln n`, so sieving `[1, n·ln n]` is
enough — that is exactly the ceiling `solutions/public/p0007/` uses to find the
10 001st prime. When even that range will not fit in memory, a *segmented* sieve
processes the interval in cache-sized windows, and an *incremental* sieve (a
generator keyed on each prime's next multiple, as in `p0010_s2`) yields primes
endlessly with no upper bound fixed in advance.

**Test or factor a single number — [trial division](https://en.wikipedia.org/wiki/Trial_division).**
When you have one number, not a range, sieving the whole space below it is wasteful.
To factor `n`, just divide by 2, 3, 4, … and peel off each divisor you find; to test
primality, divide by candidates up to `√n` and declare it prime if none divide it.
The `√n` cutoff is the key: a composite `n` must have a factor no larger than its
square root, so nothing above `√n` can be the *smallest* factor. A second saving is
to divide each found factor out completely as you go — then every divisor you
encounter is automatically prime and needs no separate primality check. Problem 3's
solution in `solutions/public/p0003/` does exactly this, recomputing the `√`-ceiling
against the shrinking remainder so the loop ends early once a large prime cofactor is
all that's left.

**Skip the numbers that can't be prime — [wheel factorization](https://en.wikipedia.org/wiki/Wheel_factorization).**
Trial division spends most of its time dividing by numbers that are themselves
composite. Every prime past 2 is odd, so step by 2 and you halve the work; every
prime past 3 is `≡ 1` or `5 (mod 6)`, so stepping through the pattern `6k ± 1` skips
two-thirds. A *wheel* generalises this: fix a few small primes (2, 3, 5, …), and only
visit the residues coprime to their product. It does not change the asymptotics — it
shaves a constant factor off both trial division and the sieve — but on the hot loop
of a factoriser that constant is worth having.

**Test a *large* single number — the [Miller–Rabin primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test).**
Trial division to `√n` is fine up to maybe `10^12`; past that its cost explodes.
Miller–Rabin instead asks a witness question: it writes `n − 1 = 2^s · d` and checks,
for a chosen base `a`, whether the sequence of repeated squarings of `a^d` betrays `n`
as composite. A single base can be fooled, but each independent base that passes
multiplies your confidence, and for `n` below fixed thresholds a *specific small set
of bases* makes the test **deterministic** — exactly correct, with no probability
left. Its cost is `O(k log^3 n)` for `k` bases: effectively instant even for numbers
with dozens of digits, which is why the higher-numbered primality problems in this
repo reach for it rather than a sieve.

## How to reason about which one

The decision is almost mechanical:

- Do I need **many** primes below a **known** bound? → sieve. Size it to the inputs
  (`n·ln n` for "the `n`-th prime"); build it *inside* `solve()`, not at module
  level, so the benchmark counts it honestly.
- Do I need to **factor** one number, or the numbers in a modest range? → trial
  division with the `√n` cutoff and full division-out, sped up by a `6k ± 1` wheel.
- Do I need a **yes/no** on one **large** number? → Miller–Rabin, with a
  deterministic base set if the number fits the known thresholds.

The classic mistake is to answer a range question one number at a time (calling a
primality test in a loop when a single sieve would produce the whole set in one
`O(N log log N)` pass), or to answer a single-number question with a sieve (building
a table of millions of primes to check just one). Match the tool to the shape of the
question and most prime problems become straightforward.

## In the wild

- [Problem 10](/solutions/0010/) — sum every prime below two million: the archetypal
  sieve problem, with five solution indices contrasting bounded, incremental, and
  wheel-assisted sieves.
- [Problem 7](/solutions/0007/) — the 10 001st prime: a sieve sized to the
  prime-number-theorem bound `n·ln n` because the target index, not a value ceiling,
  is what's given.
- [Problem 3](/solutions/0003/) — the largest prime factor of a big number: trial
  division that divides each factor out completely, so no primality test is needed.
- [Problem 50](/solutions/0050/) — the longest run of consecutive primes summing to a
  prime: a sieve to generate the primes, then prefix sums and monotonicity pruning
  over that list.

<!-- problems (generated by update-tags)
p0003
p0004
p0007
p0010
p0012
p0023
p0027
p0029
p0035
p0037
p0041
p0046
p0047
p0049
p0050
p0051
p0058
p0060
p0069
p0070
p0072
p0073
p0075
p0077
p0087
p0095
p0108
p0111
p0118
p0123
p0124
p0127
p0128
p0130
p0131
p0132
p0133
p0134
p0135
p0136
p0146
p0152
p0153
p0157
p0171
p0176
p0179
p0187
p0193
p0196
p0200
p0202
p0203
p0204
p0211
p0214
p0216
p0221
p0228
p0229
p0231
p0293
p0304
p0313
p0347
p0357
p0381
p0387
p0420
p0429
p0478
p0487
p0501
p0545
p0549
p0565
p0642
p0650
p0694
p0745
p0772
p0800
p0808
p0834
p0845
p0926
p0934
-->
