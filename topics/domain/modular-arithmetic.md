<!-- tags: [modular-arithmetic] -->
<!-- status: final 2026-10-28T21:01Z -->
# Modular arithmetic

[Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) is the arithmetic of
remainders: you fix a **modulus** $m$ and track only what a number leaves behind on division by
$m$, working inside the finite ring $\mathbb{Z}/m\mathbb{Z} = \{0, 1, \dots, m-1\}$ instead of on
the full integers. As a *domain* it is less a topic than a lens — an enormous share of the archive
poses a question that, read carefully, depends only on a residue, even when the word "modulo"
never appears. The skill this page is about is **recognising** that a problem lives here: once you
see that the quantity asked for is a remainder, an astronomically large computation collapses to
one that never leaves $[0, m)$. The mechanics that follow from that — fast exponentiation, the
modular inverse, the Chinese Remainder Theorem, the overflow trap — are the subject of the deeper
[Modular Arithmetic](/topics/number-theory/modular-arithmetic) note; here I want to catalogue the
disguises the domain wears, so you learn to spot it, and the few facts about the modulus that
decide what you are allowed to do once you have.

## The one property, in one line

The reason any of this works is that congruence — $a \equiv b \pmod m$, meaning $m$ divides
$a - b$ — is preserved by addition, subtraction, and multiplication. So

$$(a + b) \bmod m = ((a \bmod m) + (b \bmod m)) \bmod m,$$

and likewise for $a - b$ and $a \times b$. You may therefore reduce after every step and never let
an intermediate value grow. Every disguise below is ultimately a chance to apply that one closure
property early instead of late. Note what is *missing* from the list: division. Whether you may
divide depends on the modulus, and that is the subject of the section after the disguises.

## The disguises

**"The last $k$ digits of …"** is the tell that gives the game away most directly: the last $k$
decimal digits of $N$ are exactly $N \bmod 10^k$. Problem 97 wants the final ten digits of
$28433 \times 2^{7830457} + 1$, a number with over two million digits; working modulo $10^{10}$
throughout, nothing bigger than $10^{20}$ is ever formed. Problem 48 (public,
`solutions/public/p0048/`) sums $1^1 + 2^2 + \dots + 1000^{1000}$ and asks the same "last ten
digits", and the private problem 104 (Fibonacci terminal digits) is the same instinct dressed
differently. Problem 778 takes the idea to the limit. Its carry-free "freshman's product"
multiplies numbers digit by digit, keeping each column's product mod $10$. With no carries,
every decimal place is its own copy of $\mathbb{Z}/10\mathbb{Z}$. One column is a ten-entry
histogram of digits, and combining $R$ factors is a convolution of histograms under
multiplication mod $10$. That convolution can be raised to the $R$th power by squaring.

**"Is this divisible by …?"** is a residue-is-zero question. Problem 78 (public,
`solutions/public/p0078/`) asks for the first $n$ whose partition count $p(n)$ is divisible by one
million — and because only divisibility matters, the whole [dynamic
programming](/topics/technique/dynamic-programming) table can be carried mod $10^6$, so the
values that in truth run to hundreds of digits stay in a machine word:

```python
partition_value += (-1) ** (k - 1) * partitions[n - pent_k1]
# ... accumulate the pentagonal recurrence ...
partition_value %= divisor          # only the residue matters, so reduce and store that
partitions.append(partition_value)
```

The private problems 129 and 132 (when does a [repunit](https://en.wikipedia.org/wiki/Repunit)
become divisible by $n$?) and columns of "$B$-trivisible" or "unlucky prime" divisibility tests
across the later archive are the same shape. Problem 274 runs the idea backwards: it asks for the
multiplier $m$ that makes the schoolbook divisibility rule "drop the last digit $b$, add $b \cdot m$"
exact for a prime $p$. Writing $n = 10a + b$ gives $10 f(n) = n + b(10m - 1)$, so the rule works
precisely when $10m \equiv 1 \pmod p$ — every such divisibility trick is a
[modular inverse](/topics/domain/modular-multiplicative-inverse) of $10$ in disguise, and this one
even has a closed form that depends only on the last digit of $p$.

**"Give the answer modulo $1\,000\,000\,007$."** Counting problems whose true answer overflows any
integer type hand you the modulus explicitly — the residue *is* the deliverable. Here the domain is
not a shortcut you discover but a contract you are handed: every count, product, and
[binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) is computed in the ring
from the start. This is the register a large fraction of the combinatorial problems past 300 are
written in — and, as the section after the disguises shows, the *kind* of modulus you are handed
matters. The contract can even be attached to a question that looks real-valued. Problem 721 wants
$\lfloor(\lceil\sqrt a\rceil + \sqrt a)^{a^2}\rfloor$. Its conjugate $\lceil\sqrt a\rceil - \sqrt a$
lies in $[0, 1)$, so the floor is the integer $x^n + y^n$ minus one. That integer is computed
in the ring $\mathbb{Z}_p[\sqrt a]$, whose elements are pairs of residues, and no real number ever
appears.

**"… modulo $n + 1$" written into the definition.** A modulus that is part of the *object*,
rather than of the deliverable, is often there to simplify it. Problem 512 defines
$f(n) = \sum_{i=1}^{n} \varphi(n^i) \bmod (n + 1)$. Modulo $n + 1$ we have $n \equiv -1$, and
$\varphi(n^i) = n^{i-1}\varphi(n)$, so the terms alternate in sign and cancel in pairs. That leaves
$\varphi(n)$ for odd $n$ and $0$ for even $n$. Substitute the residue of the base before you compute
anything.

**"How many of these sum to a multiple of $m$?"** When the question counts objects by the residue
of a total, put the residue in the exponent. Problem 250 counts the subsets of
$\{1^1, 2^2, \dots, 250250^{250250}\}$ whose sum is divisible by $250$ — out of $2^{250250}$
subsets. Each element matters only through $k^k \bmod 250$, so a quarter-million elements become a
census over $250$ residues, and the subset-sum
[generating function](/topics/domain/generating-function) $\prod_k (1 + x^{k^k})$ is computed not in
$\mathbb{Z}[x]$ but in $\mathbb{Z}[x]/(x^{250} - 1)$, where $x^{250} = 1$ makes exponents add
modulo $250$ by themselves: the state is $250$ counters, never a polynomial of growing degree. The
smallest instance of the same trick is parity — problem 996 keeps only the even-total terms of a
generating function as $\tfrac12\big(f(y) + f(-y)\big)$, the [root-of-unity
filter](/topics/domain/root-of-unity) for modulus $2$.

**Periodicity and cyclic structure.** Residues wrap around, so any process defined by "$+$" or
"$\times$ a constant" is eventually periodic modulo $m$, and the period is often the real question.
Problem 19 (public, `solutions/public/p0019/`) is a calendar: the day of the week is a residue mod
7, so counting how often the first of a month is a Sunday is arithmetic mod 7, no date library
needed. [Pisano periods](https://en.wikipedia.org/wiki/Pisano_period) (the cycle length of Fibonacci
numbers mod $m$, problem 854), the [multiplicative order](https://en.wikipedia.org/wiki/Multiplicative_order)
of an element, and "clock"-flavoured problems (506, 790, 891) all turn on the same idea: find the
cycle, then jump across billions of steps by reducing the step count modulo its length. The period
is often *provable* rather than merely observed: in problem 250 the map $k \mapsto k^k \bmod 250$
repeats every $500$ values of $k$ (for $k \ge 3$), because $250 = 2 \cdot 5^3$ and the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) gives
$\lambda(125) = 100$, so a shift by $500$ leaves base and exponent alike unchanged modulo each
factor — a quarter-million exponentiations become one block of five hundred. Where no theorem hands
you the period, detect it: problem 943 walks deterministic sequences of parity masks only until
one repeats, then answers "the first $k$ terms" by counting whole periods.

The cycle can also hide in a physical process. In problem 641 each die face cycles with period $6$,
so a die ends showing 1 exactly when its turn count, $d(k) - 1$, is a multiple of 6. That is
$d(k) \equiv 1 \pmod 6$. It splits into "$d(k)$ odd", which forces $k$ to be a square, and a
condition mod $3$ on the prime exponents. A row of $10^{36}$ dice becomes a count of integers
with a particular factorisation shape. Iteration can also *stop* moving. In problem 455, iterating
$x \mapsto n^x \bmod 10^9$ builds the power tower $n, n^n, n^{n^n}, \dots$, and because the chain $m, \lambda(m), \lambda(\lambda(m)),
\dots$ of Carmichael values shrinks to $1$ quickly, the tower goes constant within a dozen rounds. That
constant is the fixed point the problem asks for, and the search never touches the $10^9$
candidates. Problem 700 turns the cycle into a different algorithm. Its sequence $na \bmod m$
sets successive record lows, and the records come from repeatedly subtracting the smaller of
"current minimum" and "gap below $m$" from the larger. That is Euclid's algorithm on $(a, m)$,
and it ends at $1$ when $n = a^{-1} \bmod m$. A walk over quadrillions of terms costs one step
per record.

**Congruences as the object of study.** Sometimes the residues are not a tool but the thing being
counted. Problems 271 and 272 (Modular Cubes) ask for the solutions of $x^3 \equiv 1 \pmod n$;
problem 451 hunts *self-inverse* residues with $m^2 \equiv 1 \pmod n$; problem 801 studies pairs
with $x^y \equiv y^x$. These are number theory proper — you factor the modulus, understand the
structure prime power by prime power, and glue the answer back with the Chinese Remainder Theorem —
and they are where the domain stops being a convenience and becomes the subject. In 272 that glue
is the whole solution: the [unit group](https://en.wikipedia.org/wiki/Multiplicative_group_of_integers_modulo_n)
modulo an odd prime power is cyclic, a cyclic group of order $k$ holds exactly $\gcd(3, k)$ cube
roots of unity, and so the count of solutions is a power of $3$ read straight off the
factorisation of $n$ — the search becomes one over factorisations, not over residues. Problem 421
reaches the same structure from the other side. It asks for the prime factors below $10^8$ of
$n^{15} + 1$ for $10^{11}$ values of $n$, which is hopeless; swap the order of summation and ask
each prime $p$ instead "for which residues $n$ does $p \mid n^{15} + 1$?" The answer is the
negatives of the $15$th roots of unity mod $p$ — exactly $\gcd(15, p - 1)$ of them — and each
residue class contributes its count of $n \le N$ by a single division. Factorisation turned into
counting residues. Problem 407 makes the decomposition itself the answer. An idempotent,
$a^2 \equiv a \pmod n$, must be $0$ or $1$ modulo each prime power of $n$, because $a$ and $a - 1$
are coprime. So the idempotents correspond to the ways of splitting $n$ into a coprime pair
$d \cdot e$, and there are $2^{\omega(n)}$ of them. Finding the largest one for every $n \le 10^7$
means enumerating coprime factor pairs and solving two congruences by CRT, rather than testing
residues.

## What the modulus allows

Addition and multiplication survive reduction modulo *any* $m$. Everything else depends on the
modulus, so read it before you write the first line:

- **A prime modulus is a field**, and every nonzero residue has an inverse. That is why setters
  choose $10^9 + 7$ or $1234567891$, and the primality is often load-bearing rather than cosmetic.
  Problem 529 finds a linear recurrence of order $2772$ with the
  [Berlekamp–Massey algorithm](https://en.wikipedia.org/wiki/Berlekamp%E2%80%93Massey_algorithm),
  which divides by discrepancies and so needs a field; problems 996 and 1010 divide by $n!$ and by
  products of hook lengths, legal only because the prime exceeds every factor involved — check that
  inequality too, since a prime *smaller* than your factorials makes them vanish. A field also
  shrinks exponents. By Fermat, $a^{p-1} \equiv 1$, so problem 822 reduces the exponent $2^k$ of a
  number squared $k \approx 10^{12}$ times modulo $p - 1$, which is one modular exponentiation inside
  another. Division is legal but not free: each inverse is an exponentiation. Problem 739 needs
  about $10^8$ binomials, so it multiplies the whole sum through by a factorial until every term is a
  prefix product times a suffix product, and takes a single inverse at the end.
- **A composite modulus is a product of smaller problems.** By the [Chinese Remainder
  Theorem](/topics/technique/chinese-remainder-theorem) a squarefree $m = pqr$ splits into three
  prime fields, so you solve in each and glue. Problem 365 wants $\binom{10^{18}}{10^9}$ — over nine
  billion digits — modulo some twenty million products of three primes; per prime it is one
  application of [Lucas's theorem](/topics/domain/lucass-theorem), and the recombination factors so
  that only pairwise inverses are ever needed.
- **A composite modulus also takes division away.** In problem 250 the answer is wanted mod
  $10^{16}$, and the binomial recurrence $\binom{c}{i+1} = \binom{c}{i}(c-i)/(i+1)$ divides by
  numbers that share factors with $10$ — no inverse exists. The two escapes are the two
  implementations: carry the coefficient as an exact big integer and reduce only when storing it
  (Python), or strip the powers of $2$ and $5$ into exponents and invert only the unit that remains
  (C). Reach for the second shape whenever a recurrence divides and the modulus is not prime. The
  commonest case is easy to miss: "the last nine digits" means mod $10^9$, and $10^9$ is even.
  Problem 401's closed form $x(x+1)(2x+1)/6$, with $x$ up to $10^{15}$, has no inverse of $2$ or $3$
  to lean on. The cure is to **divide before reducing**: one of $x, x+1$ is even and one of the three
  factors is a multiple of 3, so divide those exactly, then reduce and multiply.
- **A residue forgets size.** Once a value is reduced you can no longer compare it with another
  or count how often a sum wrapped. Problem 822 must repeatedly pick the *smallest* of numbers
  squared a trillion times. It decides the order with the real-valued key
  $\log_2\log_2 x^{2^k} = k + \log_2\log_2 x$ and uses residues only for the final sum. Problem 271
  sums the cube roots of unity mod a primorial *as integers*, and that total is many times the
  modulus. Adding the CRT combinations mod $n$ would return a plausible wrong number. Reduce exactly
  what the statement reduces.
- **Mind the width.** A modulus near $10^{16}$ means the product of two residues no longer fits in
  64 bits, and a sum that is *not* reduced — problem 421's lands just under $2^{63}$ — leaves no
  headroom at all; estimate the magnitude before choosing the type. The fixes (`__int128`, a split
  multiply, reducing the operands first) are in the
  [Modular Arithmetic](/topics/number-theory/modular-arithmetic) note.

## How to reason about it

The recurring cue is a question about a **remainder** — last digits, divisibility, a count returned
mod a prime, a count of totals hitting a residue, a periodic or cyclic structure — hung on a value
far too large to form directly. When you catch it:

- **Name the modulus first, then classify it.** "Last $k$ digits" means mod $10^k$; "divisible by
  $d$" means residue $0$ mod $d$; a stated `1_000_000_007` means work in that ring from line one.
  Prime means you may divide; composite means factor it, then split by CRT or keep division out of
  the ring.
- **Reduce early and often.** Never build the honest quantity and take its remainder at the end —
  reduce after each $+$ and $\times$ so operands stay in $[0, m)$. The classic mistake is to
  materialise the million-digit power or the true factorial first; the whole point is that you
  never have to.
- **Substitute the modulus into the definition.** When the modulus is $n + 1$ and the base is
  $n$, the base is $-1$. When the modulus is prime, exponents live mod $p - 1$. Simplify the object
  before you compute it.
- **Keep size outside the ring.** Orderings, comparisons and unreduced totals need the real
  magnitude, through logarithms or plain integers. Residues are only for the quantity the
  statement reduces.
- **Collapse inputs to their residues.** If only the residue of a total matters, a quarter-million
  elements are a census over $m$ buckets, and their generating function can live in
  $\mathbb{Z}[x]/(x^m - 1)$.
- **Look for the cycle.** If a sequence is defined by adding or multiplying a constant, it is
  periodic mod $m$; prove the period from the factorisation of $m$, or detect it, and leap over an
  astronomical number of steps.
- **Turn the sum around.** When a sum over $n$ asks which primes divide something, summing over
  the primes and asking which residue classes of $n$ each one divides is often the tractable
  direction.
- **Then reach for the machinery.** Powers, division, and composite moduli each have a standard
  device — [modular exponentiation](/topics/technique/modular-exponentiation), the
  [modular inverse](/topics/domain/modular-multiplicative-inverse), and the Chinese Remainder
  Theorem — all collected, with the fixed-width overflow trap, in the
  [Modular Arithmetic](/topics/number-theory/modular-arithmetic) note.

Learn to hear the question underneath the wording, and a problem that looks like big-integer
arithmetic turns out to be a handful of operations on small numbers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0048](/solutions/0048/) — Self Powers
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0250](/solutions/0250/) — $250250$
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ○ [0282](/solutions/0282/) — The Ackermann Function
- ○ [0284](/solutions/0284/) — Steady Squares
- ○ [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ○ [0303](/solutions/0303/) — Multiples with Small Digits
- ● [0304](/solutions/0304/) — Primonacci
- ○ [0312](/solutions/0312/) — Cyclic Paths on Sierpiński Graphs
- ○ [0322](/solutions/0322/) — Binomial Coefficients Divisible by 10
- ○ [0324](/solutions/0324/) — Building a Tower
- ○ [0325](/solutions/0325/) — Stone Game II
- ○ [0326](/solutions/0326/) — Modulo Summations
- ○ [0330](/solutions/0330/) — Euler's Number
- ○ [0335](/solutions/0335/) — Gathering the Beans
- ○ [0344](/solutions/0344/) — Silver Dollar Game
- ○ [0356](/solutions/0356/) — Largest Roots of Cubic Polynomials
- ○ [0364](/solutions/0364/) — Comfortable Distance
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0401](/solutions/0401/) — Sum of Squares of Divisors
- ○ [0402](/solutions/0402/) — Integer-valued Polynomials
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ● [0407](/solutions/0407/) — Idempotents
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0411](/solutions/0411/) — Uphill Paths
- ○ [0412](/solutions/0412/) — Gnomon Numbering
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ○ [0422](/solutions/0422/) — Sequence of Points on a Hyperbola
- ○ [0423](/solutions/0423/) — Consecutive Die Throws
- ○ [0427](/solutions/0427/) — $n$-sequences
- ● [0429](/solutions/0429/) — Sum of Squares of Unitary Divisors
- ○ [0435](/solutions/0435/) — Polynomials of Fibonacci Numbers
- ○ [0437](/solutions/0437/) — Fibonacci Primitive Roots
- ○ [0439](/solutions/0439/) — Sum of Sum of Divisors
- ○ [0440](/solutions/0440/) — GCD and Tiling
- ○ [0445](/solutions/0445/) — Retractions A
- ○ [0446](/solutions/0446/) — Retractions B
- ○ [0447](/solutions/0447/) — Retractions C
- ○ [0451](/solutions/0451/) — Modular Inverses
- ● [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ○ [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ○ [0492](/solutions/0492/) — Exploding Sequence
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0498](/solutions/0498/) — Remainder of Polynomial Division
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ● [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ● [0517](/solutions/0517/) — A Real Recursion
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0528](/solutions/0528/) — Constrained Sums
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0537](/solutions/0537/) — Counting Tuples
- ○ [0546](/solutions/0546/) — The Floor's Revenge
- ○ [0552](/solutions/0552/) — Chinese Leftovers II
- ○ [0554](/solutions/0554/) — Centaurs on a Chess Board
- ○ [0559](/solutions/0559/) — Permuted Matrices
- ● [0565](/solutions/0565/) — Divisibility of Sum of Divisors
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0593](/solutions/0593/) — Fleeting Medians
- ○ [0602](/solutions/0602/) — Product of Head Counts
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ○ [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ○ [0612](/solutions/0612/) — Friend Numbers
- ○ [0614](/solutions/0614/) — Special Partitions 2
- ○ [0615](/solutions/0615/) — The Millionth Number with at Least One Million Prime Factors
- ○ [0619](/solutions/0619/) — Square Subsets
- ○ [0622](/solutions/0622/) — Riffle Shuffles
- ○ [0624](/solutions/0624/) — Two Heads Are Better Than One
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0627](/solutions/0627/) — Counting Products
- ○ [0628](/solutions/0628/) — Open Chess Positions
- ○ [0631](/solutions/0631/) — Constrained Permutations
- ○ [0635](/solutions/0635/) — Subset Sums
- ○ [0638](/solutions/0638/) — Weighted Lattice Paths
- ● [0641](/solutions/0641/) — A Long Row of Dice
- ○ [0653](/solutions/0653/) — Frictionless Tube
- ○ [0654](/solutions/0654/) — Neighbourly Constraints
- ○ [0658](/solutions/0658/) — Incomplete Words II
- ○ [0663](/solutions/0663/) — Sums of Subarrays
- ○ [0666](/solutions/0666/) — Polymorphic Bacteria
- ○ [0672](/solutions/0672/) — One More One
- ○ [0673](/solutions/0673/) — Beds and Desks
- ○ [0680](/solutions/0680/) — Yarra Gnisrever
- ○ [0682](/solutions/0682/) — $5$-Smooth Pairs
- ○ [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ○ [0693](/solutions/0693/) — Finite Sequence Generator
- ○ [0696](/solutions/0696/) — Mahjong
- ● [0700](/solutions/0700/) — Eulercoin
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0709](/solutions/0709/) — Even Stevens
- ● [0710](/solutions/0710/) — One Million Members
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ○ [0728](/solutions/0728/) — Circle of Coins
- ○ [0732](/solutions/0732/) — Standing on the Shoulders of Trolls
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ● [0739](/solutions/0739/) — Summation of Summations
- ○ [0746](/solutions/0746/) — A Messy Dinner
- ○ [0747](/solutions/0747/) — Triangular Pizza
- ○ [0750](/solutions/0750/) — Optimal Card Stacking
- ○ [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ○ [0753](/solutions/0753/) — Fermat Equation
- ○ [0754](/solutions/0754/) — Product of Gauss Factorials
- ○ [0758](/solutions/0758/) — Buckets of Water
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0767](/solutions/0767/) — Window into a Matrix II
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ● [0778](/solutions/0778/) — Freshman's Product
- ○ [0784](/solutions/0784/) — Reciprocal Pairs
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0789](/solutions/0789/) — Minimal Pairing Modulo $p$
- ○ [0790](/solutions/0790/) — Clock Grid
- ○ [0797](/solutions/0797/) — Cyclogenic Polynomials
- ○ [0801](/solutions/0801/) — $x^y \equiv y^x$
- ○ [0803](/solutions/0803/) — Pseudorandom Sequence
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ○ [0809](/solutions/0809/) — Rational Recurrence Relation
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ○ [0812](/solutions/0812/) — Dynamical Polynomials
- ○ [0813](/solutions/0813/) — XOR-Powers
- ○ [0814](/solutions/0814/) — Mezzo-forte
- ● [0816](/solutions/0816/) — Shortest Distance Among Points
- ● [0820](/solutions/0820/) — $N$thDigit of Reciprocals
- ● [0822](/solutions/0822/) — Square the Smallest
- ○ [0823](/solutions/0823/) — Factor Shuffle
- ○ [0824](/solutions/0824/) — Chess Sliders
- ○ [0830](/solutions/0830/) — Binomials and Powers
- ● [0834](/solutions/0834/) — Add and Divide
- ○ [0835](/solutions/0835/) — Supernatural Triangles
- ○ [0837](/solutions/0837/) — Amidakuji
- ○ [0839](/solutions/0839/) — Beans in Bowls
- ○ [0840](/solutions/0840/) — Sum of Products
- ○ [0844](/solutions/0844/) — $k$-Markov Numbers
- ○ [0849](/solutions/0849/) — The Tournament
- ○ [0850](/solutions/0850/) — Fractions of Powers
- ○ [0851](/solutions/0851/) — SOP and POS
- ○ [0854](/solutions/0854/) — Pisano Periods 2
- ○ [0858](/solutions/0858/) — LCM
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ○ [0866](/solutions/0866/) — Tidying Up B
- ○ [0871](/solutions/0871/) — Drifting Subsets
- ○ [0873](/solutions/0873/) — Words with Gaps
- ○ [0874](/solutions/0874/) — Maximal Prime Score
- ○ [0875](/solutions/0875/) — Quadruple Congruence
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0889](/solutions/0889/) — Rational Blancmange
- ○ [0891](/solutions/0891/) — Ambiguous Clock
- ○ [0892](/solutions/0892/) — Zebra Circles
- ○ [0902](/solutions/0902/) — Permutation Powers
- ○ [0903](/solutions/0903/) — Total Permutation Powers
- ○ [0909](/solutions/0909/) — L-expressions I
- ○ [0910](/solutions/0910/) — L-expressions II
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0916](/solutions/0916/) — Restricted Permutations
- ○ [0917](/solutions/0917/) — Minimal Path Using Additive Cost
- ○ [0921](/solutions/0921/) — Golden Recurrence
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ○ [0977](/solutions/0977/) — Iterated Functions
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ○ [0984](/solutions/0984/) — Knights and Horses
- ○ [0989](/solutions/0989/) — Fibonacci Sum
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ● [0996](/solutions/0996/) — Overtakes
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1001](/solutions/1001/) — Connections I
- ○ [1004](/solutions/1004/) — Balanced Integer
- ● [1010](/solutions/1010/) — March of the Penguins

<!-- /problems -->
