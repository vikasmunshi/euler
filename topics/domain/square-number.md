<!-- tags: [square-number] -->
<!-- status: final 2026-10-14T07:11Z -->
# Square number

A [square number](https://en.wikipedia.org/wiki/Square_number) is $k^2$ for some integer $k$ — the
first non-trivial shape an integer can have, and the most common one in the archive. Squares turn
up as the thing being counted (problem 173's square laminae), as a filter on something else
(problem 211 wants $\sigma_2(n)$ to be a square, problem 86 wants a shortest path to be an
integer), as a disguise for another sequence (problem 42's triangle numbers), and as the excluded
case of an irrational (problem 64 skips the $n$ whose $\sqrt n$ has no continued fraction at all).
The subjects differ; the engineering does not. Every one of these problems comes down to the same
two operations — **recognising** a square and **generating** squares — and to a handful of
identities that let you avoid doing either.

## Generate, don't test

The single most useful fact about squares is how rare they are: there are only $\lfloor\sqrt N\rfloor$
of them below $N$. If the problem's objects *are* squares, iterate over the root, not the value.
Problem 206 looks for a 19-digit square matching a digit mask; scanning 19-digit numbers is
hopeless, but its roots form a range of about $4 \times 10^8$ ten-digit integers, and the mask
narrows that further. Problem 719 asks about $k^2 \le 10^{12}$, which is a loop over a million
roots. Problem 98 needs every $n$-digit square, and builds the set from roots between
$\lceil\sqrt{10^{n-1}}\rceil$ and $\lfloor\sqrt{10^n - 1}\rfloor$. In every case the root is the
natural coordinate and the square is just its image.

The same instinct applies to sums of squares. Problem 125 wants palindromes that are sums of
consecutive squares; rather than testing each palindrome for that property, the solution walks
starting points $i \le \sqrt N$ and extends a running total $i^2 + (i+1)^2 + \dots$ until it passes
the limit — each step a single multiply-add, and the set of candidates generated directly.

## When you must test, test exactly

Often the square is a *condition* on a computed value — $a^2 + s^2$, $\sigma_2(n)$, $8n+1$ — and
you have to recognise it. The obvious test is the wrong one:

```python
math.sqrt(n).is_integer()          # fine for small n, silently wrong past 2**53
math.isqrt(n) ** 2 == n            # exact for every int
```

A double carries 53 bits of mantissa. Once $n$ passes $2^{53} \approx 9 \times 10^{15}$, the
correctly-rounded $\sqrt{k^2 - 1}$ can round up to exactly $k$: `math.sqrt(94906267**2 - 1)` is
an integer, and `k*k - 1` is never a square. The public solutions to problems 42, 46, 64 and 86
use the float test, and they are right only because their values stay small; problem 206's notes
spell out the failure in C, where a 17-digit bound is beyond a double and the float seed has to be
nudged up or down to the true floor. In Python, reach for
[`math.isqrt`](https://docs.python.org/3/library/math.html#math.isqrt) by default — see
[integer square root](/topics/technique/integer-square-root) and
[floating-point arithmetic](/topics/technique/floating-point-arithmetic). In C, compute the
`sqrtl` seed and correct it with integer multiplications.

Exactness is non-negotiable; speed comes from rejecting most candidates before taking any root.
Squares occupy only a few residues — modulo 16 they are $\{0, 1, 4, 9\}$, modulo 9
$\{0, 1, 4, 7\}$, and their last decimal digit is one of $0, 1, 4, 5, 6, 9$ — so a single mask
discards three quarters of non-squares (see [quadratic residue](/topics/technique/quadratic-residue)).
The residue argument also works on the *root*. In problem 719 a square $k^2$ is split into parts
summing to $k$; since digit sums preserve residues mod 9, that forces $k^2 \equiv k \pmod 9$, so
only $k \equiv 0, 1 \pmod 9$ survive and roughly 78% of roots are dropped before any digit is
examined. Problem 206 does the same with the last digit: the mask fixes the square's final digit,
and only one or two last digits of the root can produce it. When the candidate set is small and
bounded, the cheapest test of all is a precomputed lookup — problem 504 builds the set (in C, a
byte table) of every square up to its maximum interior-point count and replaces the root with an
index.

## The identities that make the problem go away

Squares have more algebra than any other figurate shape, and most of the elegant solutions on this
page come from one of four identities.

- **Inverse tests.** $n$ is [triangular](/topics/domain/triangular-number) exactly when $8n + 1$ is
  a square, and pentagonal when $24n + 1$ is a square with the right root mod 6. Solving the
  quadratic $k(k+1)/2 = n$ turns "is this a member of the sequence?" into "is this a square?" —
  problem 42's whole solution is that one line.
- **Difference of squares.** $a^2 - b^2 = (a - b)(a + b)$, so questions about differences become
  questions about factor pairs ([difference of two squares](/topics/domain/difference-of-two-squares)).
  A square lamina with hole $h$ and thickness $t$ uses $(h + 2t)^2 - h^2 = 4t(t + h)$ tiles — the
  formula problems 173 and 174 rest on, which replaces a search over shapes with a count of
  divisor-like pairs $(t, h)$.
- **Odd-number sums and gaps.** $k^2 = 1 + 3 + \dots + (2k - 1)$, and consecutive squares differ
  by $2k + 1$. That gap is why the corners of problem 28's and problem 58's number spirals are
  quadratics in the ring index: ring $k$ ends at $(2k + 1)^2$, and the other three corners sit
  $2k$, $4k$ and $6k$ below it. It also bounds the search in problem 46: for $n = p + 2k^2$ only
  $k \le \sqrt{n/2}$ are worth trying.
- **Sums of two squares.** $a^2 + b^2 = c^2$ is the [Pythagorean](/topics/domain/pythagorean-triple)
  triple (problems 86 and 218), and which $n$ are $a^2 + b^2$ at all is decided by their prime
  factorisation ([sum of two squares theorem](/topics/domain/sum-of-two-squares-theorem)). Problem 86
  unfolds a cuboid so the shortest path becomes $\sqrt{a^2 + (b + c)^2}$, and then counts the
  $(b, c)$ splits of each square-producing $s = b + c$ in $O(1)$ instead of enumerating them.

## The square as a boundary case

Finally, squares mark where other theories break. $\sqrt n$ is either an integer or irrational —
there is nothing in between — so problems about the decimal or
[continued-fraction](/topics/domain/periodic-continued-fraction) expansion of $\sqrt n$ (64, 80)
and [Pell's equation](/topics/technique/pells-equation) $x^2 - Dy^2 = 1$ begin by excluding
perfect squares: for $n = k^2$ the continued-fraction recurrence's denominator hits zero on its
first step, and a solution that forgets the exclusion crashes or loops forever.
The dual notion, [square-free](/topics/domain/square-free-integer) — divisible by no square
greater than 1 — is the other side of the same coin, and problem 864 sits right on it.

The through-line: treat $k$, not $k^2$, as the variable whenever you can; when you cannot, filter
by residue and confirm with an exact integer root; and before writing either loop, check whether an
identity — inverse test, difference of squares, the odd-number gap — has already done the work.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0028](/solutions/0028/) — Number Spiral Diagonals
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0046](/solutions/0046/) — Goldbach's Other Conjecture
- ● [0058](/solutions/0058/) — Spiral Primes
- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0086](/solutions/0086/) — Cuboid Route
- ● [0090](/solutions/0090/) — Cube Digit Pairs
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0141](/solutions/0141/) — Square Progressive Numbers
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0173](/solutions/0173/) — Hollow Square Laminae I
- ● [0174](/solutions/0174/) — Hollow Square Laminae II
- ● [0201](/solutions/0201/) — Subsets with a Unique Sum
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0211](/solutions/0211/) — Divisor Square Sum
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0234](/solutions/0234/) — Semidivisible Numbers
- ○ [0261](/solutions/0261/) — Pivotal Square Sums
- ○ [0310](/solutions/0310/) — Nim Square
- ○ [0342](/solutions/0342/) — The Totient of a Square Is a Cube
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0359](/solutions/0359/) — Hilbert's New Hotel
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0431](/solutions/0431/) — Square Space Silo
- ○ [0459](/solutions/0459/) — Flipping Game
- ● [0504](/solutions/0504/) — Square on the Inside
- ○ [0558](/solutions/0558/) — Irrational Base
- ○ [0575](/solutions/0575/) — Wandering Robots
- ○ [0585](/solutions/0585/) — Nested Square Roots
- ○ [0611](/solutions/0611/) — Hallway of Square Steps
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0648](/solutions/0648/) — Skipping Squares
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0757](/solutions/0757/) — Stealthy Numbers
- ○ [0769](/solutions/0769/) — Binary Quadratic Form II
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0833](/solutions/0833/) — Square Triangle Products
- ○ [0864](/solutions/0864/) — Square + 1 = Squarefree
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III

<!-- /problems -->
