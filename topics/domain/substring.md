<!-- tags: [substring] -->
<!-- status: final 2026-10-12T14:33Z -->
# Substring

A [substring](https://en.wikipedia.org/wiki/Substring) is a contiguous run of characters inside a
longer string. Here the string is nearly always the decimal digits of a number: one integer, or
an endless concatenation of them like the
[Champernowne](/topics/domain/champernowne-constant) stream $123456789101112\ldots$. A string of
length $n$ has $n(n+1)/2$ substrings, and in these problems $n$ is $10^{13}$ or $10^{18}$, so
listing the substrings is never an option. Each problem asks for something *aggregate* about
them: where the $n$-th copy of a pattern sits, how many numbers have every digit inside some
substring with a given property, or the sum of all substrings. The work is choosing a way to
count substrings without visiting them.

## The idea: three ways to count without listing

**By contribution.** When the question is a sum over all substrings, swap the order of
summation and ask what each *digit* contributes. Take a digit $d_i$ at position $i$, counting from
$0$ on the left, of an $n$-digit string. It lies in every substring that starts at or before $i$,
which gives $i + 1$ choices of start. It lies in every substring that ends at or after $i$, and
there its place value is $10^{0}, 10^{1}, \dots, 10^{n-1-i}$ depending on the end. So

$$\sum_{\text{substrings}} \text{value} = \sum_i d_i\,(i + 1)\,\frac{10^{\,n-i} - 1}{9}.$$

That's one [geometric series](/topics/technique/geometric-series) per digit, and it reproduces
Problem 603's worked example, $S(2024) = 2304$. Problem 603 then asks for the same sum over a
string far too long to walk digit by digit: a trillion copies of the concatenated first million
primes. It is not solved here yet. The contribution identity is the natural first step, and the
remaining work is summing it in closed form over the repeated blocks under a modulus.

**By the state a left-to-right scan needs.** When the question is about a *property* of
substrings, read the digits left to right and ask what must be remembered about the part already
read. Problem 529 counts the numbers in which every digit lies inside some substring whose digits
sum to $10$. Any future such substring must start inside a recent suffix whose digit sum is still
at most $10$. So it is enough to remember the *set* of suffix sums at most $10$ (an 11-bit mask),
plus the sum from the earliest uncovered digit. That is a
[finite automaton](/topics/technique/finite-state-machine). A
[digit DP](/topics/technique/digit-dp) over it counts the qualifying numbers of each length, and
because those counts come from a finite automaton they satisfy a
[linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients), which reaches
length $10^{18}$. The general lesson: a substring condition on a digit stream usually depends on
a bounded window of suffix information, and that window is the state.

**By classifying where a substring sits.** When the string is a concatenation of integers, an
occurrence of a pattern either lies *inside* one integer or *crosses* a boundary between
consecutive integers. Problem 305 counts the occurrences of a digit string that start within
$1..N$, and then binary-searches $N$ for the $n$-th. Inside one integer, the pattern sits at some
offset with free digits around it, counted per digit length. Across a boundary, the pattern's
tail is a prefix of $p$ and its head is a suffix of $p - 1$. The second condition is a
congruence on $p$ modulo a power of ten, and that congruence handles the carry from $p - 1$ to
$p$ automatically. Both classes are counted with a few floor divisions. The rare case where the
occurrence swallows a short integer whole is left to a direct check.

## How to reason about it

- **Decide what is being aggregated.** A sum over substrings wants contribution counting. A
  "some substring satisfies…" property wants an automaton over the digits. A position or rank
  wants a monotone count and a binary search. Mixing these up leads to an enumeration that can't
  finish.
- **Bound the state by the property, not the length.** In 529 suffix sums above $10$ can never
  matter again, because digits are non-negative. That fact is what makes the state finite.
  Look for the equivalent cut-off in any substring condition.
- **Concatenation boundaries are where the difficulty is.** Inside one integer, digits are
  independent and counting is clean. At a boundary, consecutive integers are related by $+1$, so
  carries and digit-length changes ($99 \to 100$) appear. Treat the boundary as its own case, and
  turn "the previous integer ends in…" into a congruence.
- **Leading zeros are a separate rule.** A substring such as `02` or `024` has a leading zero.
  It counts as written in 603's sum, but a number can't *start* with zero. Both 305 and 529 carry
  that distinction explicitly.
- **Verify against a literal scan.** Build the actual string for small parameters and count
  directly. 305 was checked against the first $2 \times 10^7$ digits of the stream, and 529's
  digit DP against a brute-force scan of every number up to $10^5$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0529](/solutions/0529/) — $10$-substrings
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations

<!-- /problems -->
