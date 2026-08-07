<!-- tags: [modular-arithmetic-application] -->
<!-- status: final -->
# Modular arithmetic (application)

[Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) as a *technique* is not the
mathematics of remainders — that is the subject of the [domain
page](/topics/domain/modular-arithmetic), and the machinery (exponentiation, inverses, the Chinese
Remainder Theorem, the overflow trap) is catalogued in the deeper [Modular
Arithmetic](/topics/number-theory/modular-arithmetic) note. This page is about the *engineering
move*: deciding to replace the object you were asked about with its residue, and knowing where in
the program that decision lands. It is rarely a `%` sprinkled into an existing loop. In almost every
solution below, applying modular arithmetic changed the algorithm — often before a line was written.

## The one property, and the four places it lands

Everything rests on congruence surviving $+$, $-$ and $\times$: you may reduce after every step and
never let an intermediate grow. What varies is *what* you reduce, and that choice is the technique.
Four shapes cover nearly the whole archive.

**1 — Collapse the algebra before you code.** The strongest application of a modulus is the one that
deletes the computation. Problems 120 and 123 both ask for $(a-1)^n + (a+1)^n \bmod a^2$, which
reads like a job for [modular
exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation). Expand with the [binomial
theorem](https://en.wikipedia.org/wiki/Binomial_theorem) *inside* the modulus instead: every term
carrying $a^k$ with $k \ge 2$ is divisible by $a^2$ and vanishes, so an $(n+1)$-term expansion
collapses to two, and the whole expression reduces to a constant for even $n$ and to $2na \bmod a^2$
for odd $n$. What was an exponentiation per candidate becomes one multiply, and the search over $n$
becomes a one-line maximisation. Problem 168 does the same to a $10^{100}$-wide search: "n divides
its own right-rotation" is a linear equation whose solutions are counted directly, with the modulus
appearing only at the end, where the question asks for the last five digits. This is
[reduce-before-coding](/topics/takeaway/reduce-before-coding) in its purest form — the modulus is a
tool of *algebra* first and of arithmetic second.

**2 — Turn a residue condition into a stride.** A congruence that a solution must satisfy is a
filter, and a filter you can apply by construction beats one you apply by test. Problem 4 (public,
`solutions/public/p0004/`) wants the largest palindromic product of two three-digit numbers; every
even-length palindrome is divisible by 11, so one factor must supply that 11, and the inner loop
walks multiples of 11 rather than testing them:

```python
a_is_multiple_11 = a % 11 == 0
for b in range(max_number if a_is_multiple_11 else max_multiple_11, a - 1, -1 if a_is_multiple_11 else -11):
```

Ten of every eleven candidates are never generated. The same instinct scales: problem 206's target square ends in 0, so its
root is $10m$, and the remaining pattern ends in 9, which forces $m \equiv 3$ or $7 \pmod{10}$ —
two arithmetic progressions instead of a scan, a hundredfold cut; problem 146 stacks residue conditions across
the first several primes until roughly 499 of every 500 candidates fall away before any expensive
[primality test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) runs. Note the
shape in all three — the residue argument is *cheap* (an integer division, or nothing at all,
because the stride encodes it) and the work it avoids is expensive.

**3 — Carry the residue as the state.** When the quantity itself is unbounded but the question
depends only on its remainder, the residue becomes the loop's state variable, and an infinite or
astronomically large state space becomes a finite one. Problem 225 asks whether a Tribonacci
sequence ever hits a multiple of $m$ — an infinite check, until you observe that divisibility
depends only on the triple of consecutive residues mod $m$, which lives in a set of size $m^3$, and
that the recurrence is invertible mod $m$ (recovering the earlier term needs a subtraction, no
division), hence [purely periodic](/topics/domain/periodic-sequence). One period is a complete
answer. Problem 277 pushes the idea further: because each step of its Collatz-style map is chosen by
the current value mod 3, a step string of length $L$ is a base-3 fingerprint pinning the seed to a
single residue class mod $3^L$, recovered one digit at a time — a search becomes an inversion. The
[digit DPs](/topics/technique/dynamic-programming) (725, 885, 217) are the same trick with a small
modulus: the state is a digit sum or a count, not the number.

**4 — The modulus you are handed.** Late problems often *state* the modulus — "give $S(k)$ modulo
$1123581313$" — and then the residue is the deliverable, not a shortcut. The discipline is
mechanical but unforgiving: reduce at **every** combine, inside the recurrence, not at the end.
Problem 940's $2 \times 2$ transfer matrices are multiplied mod the given prime throughout, so a
value defined over Fibonacci-sized arguments costs $O(\log m + \log n)$ per entry; problem 885's
[multinomial](https://en.wikipedia.org/wiki/Multinomial_theorem) DP accumulates mod $1123455689$ cell
by cell. A single unreduced accumulator anywhere in the loop reintroduces the growth the modulus was
there to prevent.

## How to reason about it

The cue is a question whose answer depends only on a remainder attached to a value too large to
form. When you see it, ask in this order: can the modulus be applied *on paper* to collapse the
expression (shape 1)? Can it be applied *to the enumeration* as a stride (shape 2)? Can it be the
*state* (shape 3)? Only then reach for the arithmetic itself.

Two failure modes are worth naming, because both survive testing on small inputs.

**Reducing something that is not congruence-friendly.** Congruence is preserved by $+$, $-$ and
$\times$ — and by nothing else you are likely to want. Ordering, `max`, `min`, exact equality of
magnitudes and plain integer division all break: $a \equiv b \pmod m$ says nothing about which of
$a$ and $b$ is larger. The trap has a name here, [exact sums resist modular
shortcuts](/topics/takeaway/exact-sums-resist-modular-shortcuts), and problem 244 is the case study:
its checksums are rolling hashes each reduced mod $10^8 + 7$, but the answer is the **plain,
unreduced** sum of those already-reduced values. Carrying a `(count, sum-of-hashes)` pair through
the search — the obvious dynamic program — yields the total only mod $10^8 + 7$, because no residue
records how many individual hashes wrapped around. Each contributing path has to be produced
explicitly. Before you fold a reduction into an aggregate, check that the aggregate is one of $+$,
$-$, $\times$ *in the same modulus as the final answer*.

**Language semantics on the C side.** Python's `%` returns a non-negative result for a positive
modulus; C's truncates toward zero, so any expression that can go negative — a difference of two
residues, an inverse-scaled term — needs normalising, which is why `((x % m) + m) % m` appears in C
solution after C solution here. The companion hazard is that two residues below $m$ multiply to
nearly $m^2$, past the 64-bit ceiling once $m$ exceeds about $3 \times 10^9$; see
[`__int128`](/topics/technique/int128) for the standard widening. Both bugs are invisible in the
Python original and both produce a plausible wrong number rather than a crash.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ● [0244](/solutions/0244/) — Sliders
- ● [0249](/solutions/0249/) — Prime Subset Sums
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0710](/solutions/0710/) — One Million Members
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ● [0788](/solutions/0788/) — Dominating Numbers
- ● [0885](/solutions/0885/) — Sorted Digits
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
