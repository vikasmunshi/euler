<!-- tags: [algorithm-beats-language] -->
<!-- status: final -->
# Algorithm beats language

Reach for a faster language and you win a constant factor — a program that runs
five or ten or fifty times quicker, but with the same *shape* to its running
time. Reach for a better algorithm and you change the shape itself: the
[complexity class](https://en.wikipedia.org/wiki/Computational_complexity), the
exponent in the [Big-O](https://en.wikipedia.org/wiki/Big_O_notation) that
governs how the cost grows with the input. Across these problems the same lesson
keeps landing: a better [asymptotic class](https://en.wikipedia.org/wiki/Asymptotic_analysis)
in a slow language beats a worse one in a fast language, and it is rarely close.

## Why the exponent wins

[Asymptotic analysis](https://en.wikipedia.org/wiki/Asymptotic_analysis) separates
two kinds of cost. The **algorithm** sets how the work scales with the input size
$n$ — $O(n)$, $O(n \log n)$, $O(n^2)$, $O(2^n)$. The **language and its
implementation** set the constant factor hidden inside that $O$: how many
nanoseconds one unit of that work takes. C's constant is small; interpreted
Python's is large — commonly one to two orders of magnitude larger for a tight
numeric loop. That gap is real, and it is also *fixed*. It multiplies the running
time by a constant no matter how big the input grows.

The exponent does not multiply — it compounds. Double the input under an $O(n^2)$
algorithm and the work quadruples; under $O(n)$ it merely doubles. So for any two
algorithms in different classes there is a crossover size beyond which the
better-class one wins in *any* language, and past that point the margin only
widens. A constant factor of 50 buys you a little breathing room before the
crossover; it never changes which side of it you end up on.

[Summation of Primes](/solutions/0010/) makes the crossover concrete because it
carries five solutions in both Python and C. Summing the primes below two million,
the [Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes) —
$O(n \log \log n)$, effectively linear — runs in about **0.05 s in Python**.
Plain [trial division](https://en.wikipedia.org/wiki/Trial_division) —
$O(n\sqrt{n} / \ln n)$ — runs in about **0.13 s in C**. The slow language with
the good algorithm beats the fast language with the poor one by more than a factor
of two, and at ten million the Python sieve (~0.28 s) beats the C trial division
(~1.3 s) by nearly five. Line the four cells up:

| | Trial division | Sieve of Eratosthenes |
| --- | --- | --- |
| **Python** | ~4.0 s | ~0.05 s |
| **C** | ~0.13 s | ~0.004 s |

Read it two ways. Down a column (fix the algorithm, change the language) the gap
is the constant factor — here roughly 10–30×. Across a row (fix the language,
change the algorithm) the gap is the complexity class — here **~80×** in Python.
The algorithm swing dwarfs the language swing, and the winning diagonal — Python
sieve over C trial division — is the whole takeaway in one square.

At the far end the choice stops being about speed at all.
[Maximum Path Sum II](/solutions/0067/) has $2^{99}$ top-to-bottom routes through
its triangle; the statement notes that checking them at a trillion per second
would outlast the age of the universe. No compiler, no hand-tuned C, no cluster
rescues an $O(2^n)$ search at $n = 99$. The $O(n^2)$
[dynamic-programming](https://en.wikipedia.org/wiki/Dynamic_programming) fold does
about 5,000 operations and finishes instantly in either language. When the naive
class is exponential, the language is not a variable in the equation — only the
algorithm is.

## How to reason about it

- **Fix the complexity class before you touch the language.** When a solution is
  too slow, the first question is the exponent, not the runtime. A brute force
  that times out wants a better algorithm — a sieve instead of per-number testing,
  a closed form instead of a loop, memoised subproblems instead of a re-exploring
  recursion — long before it wants to be rewritten in C. Most of the problems
  below were "hard" only until the right method turned them $O(n)$ or $O(n \log n)$.
- **Spend the language where the class is already settled.** The constant factor
  is worth chasing once the algorithm is right and you need the last 10× — which
  is exactly why several problems here carry a C sibling of a Python solution that
  already runs. C earns its place *below* the crossover, polishing a good
  algorithm; it cannot lift a bad one over the line.
- **Beware the fast-language trap.** The danger is a poor algorithm that a fast
  language keeps *just* fast enough to look acceptable on the small example, then
  falls off a cliff on the real input. The C trial division above is exactly that:
  respectable at two million, painful at ten. If you find yourself reaching for a
  faster language to save a design, the design is the problem.
- **Watch the honest cost.** Because a better class can make a solution finish in
  milliseconds, benchmark it fairly — build the sieve, table, or cache *inside*
  `solve()`, sized to the input, so a warm cache between `--runs` does not flatter
  the timing and hide which algorithm you are actually paying for.

The through-line is that the exponent is the lever and the language is the trim.
Get the class right and a slow language is fast enough; get it wrong and no
language is fast enough. Each problem below is a place where choosing the
algorithm, not the language, was what made it tractable.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0067](/solutions/0067/) — Maximum Path Sum II
- ● [0073](/solutions/0073/) — Counting Fractions in a Range
- ● [0075](/solutions/0075/) — Singular Integer Right Triangles
- ● [0076](/solutions/0076/) — Counting Summations
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0083](/solutions/0083/) — Path Sum: Four Ways
- ● [0108](/solutions/0108/) — Diophantine Reciprocals I
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0150](/solutions/0150/) — Sub-triangle Sums
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0191](/solutions/0191/) — Prize Strings
- ● [0214](/solutions/0214/) — Totient Chains
- ● [0345](/solutions/0345/) — Matrix Sum
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0461](/solutions/0461/) — Almost Pi
- ● [0686](/solutions/0686/) — Powers of Two
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0834](/solutions/0834/) — Add and Divide
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
