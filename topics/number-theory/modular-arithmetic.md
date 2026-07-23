<!-- tags: [modular-arithmetic, modular-multiplicative-inverse, modular-arithmetic-application, modular-exponentiation, modular-multiplicative-inverse-application] -->
<!-- status: final -->
# Modular Arithmetic

[Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) is the arithmetic of
remainders: instead of tracking a number's full value, you track only what is left after dividing
by a fixed **modulus** $m$. It is the single most useful trick in the Euler toolbox, because a
huge fraction of problems ask a question that only depends on a remainder — *the last ten digits
of a number*, *is this divisible by that*, *how many arrangements up to a symmetry* — and the full
value is astronomically large while its residue fits in a machine word. Learn to spot when a
problem is secretly modular, and a computation with millions of digits collapses to one that never
leaves the range $[0, m)$.

## The arithmetic of remainders

Two integers are [**congruent**](https://en.wikipedia.org/wiki/Modular_arithmetic) modulo $m$,
written $a \equiv b \pmod m$, when they leave the same remainder on division by $m$ — equivalently,
when $m$ divides $a - b$. The reason this is *arithmetic* and not just notation is that congruence
is preserved by addition, subtraction, and multiplication:

$$(a + b) \bmod m = ((a \bmod m) + (b \bmod m)) \bmod m,$$

and the same for $a - b$ and $a \times b$. So you may reduce at every step and never let an
intermediate value grow. That single closure property is what powers the classic reframe: "the last
$k$ decimal digits of $N$" is exactly $N \bmod 10^k$. Problem 97 asks for the last ten digits of
$28433 \times 2^{7830457} + 1$ — a number with over two million digits — but working modulo
$10^{10}$ throughout, it never handles anything bigger than $10^{20}$. Problem 19 (public,
`solutions/public/p0019/`) is the same idea wearing a calendar: the day of the week is a residue
modulo 7, so counting how often the first of a month is a Sunday is pure arithmetic mod 7, no date
library required.

The catch is that congruence is preserved by $+$, $-$, and $\times$ **but not by division** — and
not, in general, by exponentiation done naively. Those two operations are what the rest of this page
is about.

## Exponentiation: square-and-multiply

Computing $a^b \bmod m$ by multiplying $a$ into a running product $b$ times is $O(b)$, and $b$ is
often the very thing that is astronomically large ($b = 7830457$ in problem 97; $b = i$ up to $1000$
per term in problem 48). [**Modular exponentiation**](https://en.wikipedia.org/wiki/Modular_exponentiation)
via [exponentiation by squaring](https://en.wikipedia.org/wiki/Exponentiation_by_squaring) reads the
exponent's binary digits instead: repeatedly square the base, and fold it into the result only where
a bit of $b$ is set. That computes the power in $O(\log b)$ multiplications — about 23 instead of 7.8
million for problem 97.

In Python you almost never write the loop yourself; the built-in three-argument `pow` does the
reduction *inside* the squaring loop, so the full power is never materialised. Problem 48 (public,
`solutions/public/p0048/`) — the sum $1^1 + 2^2 + \dots + 1000^{1000}$ modulo $10^{10}$ — is three
lines because of it:

```python
result = 0
for i in range(1, limit + 1):
    result = (result + pow(i, i, modulo)) % modulo   # note: pow(i, i, modulo), not pow(i, i) % modulo
```

The parenthetical matters: `pow(i, i) % modulo` first builds the multi-thousand-digit power and only
then reduces, throwing away the entire benefit. Two further levers keep the *exponent* itself small.
By [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), if $p$ is
prime and $\gcd(a, p) = 1$ then $a^{p-1} \equiv 1 \pmod p$, so exponents may be reduced modulo
$p - 1$; its generalisation, [Euler's theorem](https://en.wikipedia.org/wiki/Euler%27s_theorem),
does the same modulo any $m$ using [Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function)
$\varphi(m)$. That is how "tower of powers" problems (188's hyperexponentiation) stay finite: you
reduce each exponent modulo the totient of the modulus one level up.

## Division: the modular inverse

You cannot divide by $a$ modulo $m$ directly, but you can multiply by its
[**modular multiplicative inverse**](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) —
the number $a^{-1}$ with $a \cdot a^{-1} \equiv 1 \pmod m$. It exists **precisely when $a$ and $m$
are [coprime](https://en.wikipedia.org/wiki/Coprime_integers)** ($\gcd(a, m) = 1$); otherwise $a$ has
no inverse and division is genuinely undefined. There are two standard ways to compute it:

- The [extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm)
  finds $x, y$ with $a x + m y = \gcd(a, m)$; when the gcd is 1, that $x$ is $a^{-1} \bmod m$. This
  works for **any** modulus.
- When the modulus is prime, Fermat's little theorem gives it for free: $a^{-1} \equiv a^{p-2}
  \pmod p$, one modular exponentiation.

In Python both collapse to `pow(a, -1, m)` (a negative exponent asks for the inverse). The inverse is
what turns a [**linear congruence**](https://en.wikipedia.org/wiki/Linear_congruence_theorem) into a
closed form: to solve $a x \equiv c \pmod m$ you write $x \equiv c \cdot a^{-1} \pmod m$ — no search.
Problem 134 does exactly this: "the number ending in the digits of prime $p_1$ and divisible by
$p_2$" becomes $10^d k \equiv -p_1 \pmod{p_2}$, solved in one line as
`k = (-p1 * pow(d, -1, p2)) % p2`; the inverse exists because $p_2 > 5$ shares no factor with
$10^d$. Inverses also appear as the object of study in their own right — problem 451 hunts for
*self-inverse* residues ($m$ with $m^2 \equiv 1 \pmod n$), and modular binomial coefficients (needed
whenever a count is asked "modulo a prime") are computed with inverse factorials.

## Combining moduli: the Chinese Remainder Theorem

When a modulus factors into coprime pieces, the
[**Chinese Remainder Theorem**](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) (CRT) says a
system of congruences with pairwise-coprime moduli has a unique solution modulo the product:

$$x \equiv a_1 \pmod{m_1}, \quad x \equiv a_2 \pmod{m_2} \;\Longrightarrow\; \text{a unique } x
\pmod{m_1 m_2}.$$

This is a workhorse for two reasons. First, it lets you *combine* separately-derived constraints:
problem 531 asks for the smallest $x$ with $x \equiv a \pmod n$ and $x \equiv b \pmod m$ — a direct
CRT solve (returning nothing when the moduli are not coprime and the residues clash). Second, it lets
you *decompose* a hard modulus: to solve a polynomial congruence like $x^3 \equiv 1 \pmod n$
(problem 271) you factor $n$, solve modulo each prime power separately where the structure is simple,
and glue the residue sets back together with CRT. The number of solutions multiplies across the
factors — which is why $S(91) = S(7 \cdot 13)$ in problem 271 has $2 \times 4 = 8$ roots.

## The overflow trap

Modular arithmetic's one sharp edge is a language pitfall, not a mathematical one. Two residues below
$m$ multiply to a product approaching $m^2$; with $m = 10^{10}$ that is $10^{20}$, past the
$\approx 9.2 \times 10^{18}$ ceiling of a signed 64-bit integer. Python's arbitrary-precision
integers make this invisible, but in C the intermediate product overflows and silently corrupts the
answer. The fix used throughout the C solutions here is to widen just the multiply — cast one operand
to `__int128`, form the product at 128-bit precision, and reduce back to 64 bits immediately — so the
oversized value is transient and never stored. Whenever a modulus exceeds about $3 \times 10^9$, that
widening (or a modulus small enough that $m^2$ still fits) is mandatory.

## How to reason about it

The recurring cue is a question that depends only on a remainder — *last digits*, *divisibility*,
*a count modulo a prime*, *a periodic or cyclic structure* — attached to a value too large to form
directly. When you see it:

- Reduce **early and often**. Never build the full number; reduce after every $+$ or $\times$ so
  operands stay in $[0, m)$.
- Need a **power**? Use modular exponentiation ($O(\log b)$), and shrink the exponent itself with
  Fermat/Euler when the base is coprime to the modulus.
- Need to **divide**? Multiply by the modular inverse — extended Euclid for any modulus, $a^{p-2}$
  for a prime one — and remember it exists only when $\gcd(a, m) = 1$.
- Facing **several congruences** or a **composite modulus**? Combine or decompose with the Chinese
  Remainder Theorem, working prime power by prime power.
- Writing **C** (or any fixed-width language)? Guard every modular multiply against overflow.

The classic mistake is to compute the honest quantity first and reduce at the end — materialising the
million-digit power, or the true factorial, before taking the remainder. The whole point is that you
never have to: reduce as you go, and a problem that looks like big-integer arithmetic becomes a
handful of operations on small numbers.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0048](/solutions/0048/) — Self Powers
- ● [0078](/solutions/0078/) — Coin Partitions
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0104](/solutions/0104/) — Pandigital Fibonacci Ends
- ● [0111](/solutions/0111/) — Primes with Runs
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0129](/solutions/0129/) — Repunit Divisibility
- ● [0130](/solutions/0130/) — Composites with Prime Repunit Property
- ● [0131](/solutions/0131/) — Prime Cube Partnership
- ● [0132](/solutions/0132/) — Large Repunit Factors
- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0134](/solutions/0134/) — Prime Pair Connection
- ● [0135](/solutions/0135/) — Same Differences
- ● [0136](/solutions/0136/) — Singleton Difference
- ● [0138](/solutions/0138/) — Special Isosceles Triangles
- ● [0146](/solutions/0146/) — Investigating a Prime Pattern
- ● [0152](/solutions/0152/) — Sums of Square Reciprocals
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0182](/solutions/0182/) — RSA Encryption
- ● [0188](/solutions/0188/) — Hyperexponentiation
- ● [0194](/solutions/0194/) — Coloured Configurations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0200](/solutions/0200/) — Prime-proof Squbes
- ● [0202](/solutions/0202/) — Laserbeam
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0216](/solutions/0216/) — The Primality of $2n^2 - 1$
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0218](/solutions/0218/) — Perfect Right-angled Triangles
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ○ [0237](/solutions/0237/) — Tours on a $4 \times N$ Playing Board
- ○ [0250](/solutions/0250/) — $250250$
- ○ [0258](/solutions/0258/) — A Lagged Fibonacci Sequence
- ○ [0266](/solutions/0266/) — Pseudo Square Root
- ○ [0271](/solutions/0271/) — Modular Cubes, Part 1
- ○ [0272](/solutions/0272/) — Modular Cubes, Part 2
- ○ [0274](/solutions/0274/) — Divisibility Multipliers
- ● [0277](/solutions/0277/) — A Modified Collatz Sequence
- ○ [0282](/solutions/0282/) — The Ackermann Function
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0293](/solutions/0293/) — Pseudo-Fortunate Numbers
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
- ○ [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ○ [0374](/solutions/0374/) — Maximum Integer Partition Product
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ○ [0401](/solutions/0401/) — Sum of Squares of Divisors
- ○ [0402](/solutions/0402/) — Integer-valued Polynomials
- ○ [0405](/solutions/0405/) — A Rectangular Tiling
- ○ [0407](/solutions/0407/) — Idempotents
- ○ [0408](/solutions/0408/) — Admissible Paths Through a Grid
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0411](/solutions/0411/) — Uphill Paths
- ○ [0412](/solutions/0412/) — Gnomon Numbering
- ○ [0413](/solutions/0413/) — One-child Numbers
- ○ [0416](/solutions/0416/) — A Frog's Trip
- ○ [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
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
- ○ [0455](/solutions/0455/) — Powers with Trailing Digits
- ○ [0456](/solutions/0456/) — Triangles Containing the Origin II
- ○ [0457](/solutions/0457/) — A Polynomial Modulo the Square of a Prime
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0467](/solutions/0467/) — Superinteger
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ○ [0475](/solutions/0475/) — Music Festival
- ○ [0477](/solutions/0477/) — Number Sequence Game
- ● [0478](/solutions/0478/) — Mixtures
- ○ [0479](/solutions/0479/) — Roots on the Rise
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ○ [0492](/solutions/0492/) — Exploding Sequence
- ○ [0495](/solutions/0495/) — Writing $n$ as the Product of $k$ Distinct Positive Integers
- ○ [0498](/solutions/0498/) — Remainder of Polynomial Division
- ○ [0500](/solutions/0500/) — Problem 500!!!
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0506](/solutions/0506/) — Clock Sequence
- ○ [0511](/solutions/0511/) — Sequences with Nice Divisibility Properties
- ○ [0512](/solutions/0512/) — Sums of Totients of Powers
- ○ [0515](/solutions/0515/) — Dissonant Numbers
- ○ [0517](/solutions/0517/) — A Real Recursion
- ○ [0522](/solutions/0522/) — Hilbert's Blackout
- ○ [0528](/solutions/0528/) — Constrained Sums
- ○ [0529](/solutions/0529/) — $10$-substrings
- ○ [0531](/solutions/0531/) — Chinese Leftovers
- ○ [0536](/solutions/0536/) — Modulo Power Identity
- ○ [0537](/solutions/0537/) — Counting Tuples
- ● [0545](/solutions/0545/) — Faulhaber's Formulas
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
- ○ [0641](/solutions/0641/) — A Long Row of Dice
- ● [0642](/solutions/0642/) — Sum of Largest Prime Factors
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
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
- ○ [0700](/solutions/0700/) — Eulercoin
- ○ [0706](/solutions/0706/) — $3$-Like Numbers
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0709](/solutions/0709/) — Even Stevens
- ● [0710](/solutions/0710/) — One Million Members
- ○ [0715](/solutions/0715/) — Sextuplet Norms
- ○ [0716](/solutions/0716/) — Grid Graphs
- ○ [0717](/solutions/0717/) — Summation of a Modular Formula
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ○ [0721](/solutions/0721/) — High Powers of Irrational Numbers
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ○ [0728](/solutions/0728/) — Circle of Coins
- ○ [0732](/solutions/0732/) — Standing on the Shoulders of Trolls
- ○ [0733](/solutions/0733/) — Ascending Subsequences
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0739](/solutions/0739/) — Summation of Summations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0745](/solutions/0745/) — Sum of Squares II
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
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0773](/solutions/0773/) — Ruff Numbers
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0778](/solutions/0778/) — Freshman's Product
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
- ○ [0822](/solutions/0822/) — Square the Smallest
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
- ● [0926](/solutions/0926/) — Total Roundness
- ○ [0929](/solutions/0929/) — Odd-Run Compositions
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes
- ● [0940](/solutions/0940/) — Two-Dimensional Recurrence
- ○ [0941](/solutions/0941/) — de Bruijn's Combination Lock
- ○ [0942](/solutions/0942/) — Mersenne's Square Root
- ○ [0943](/solutions/0943/) — Self Describing Sequences
- ● [0944](/solutions/0944/) — Sum of Elevisors
- ○ [0947](/solutions/0947/) — Fibonacci Residues
- ○ [0950](/solutions/0950/) — Pirate Treasure
- ○ [0952](/solutions/0952/) — Order Modulo Factorial
- ○ [0956](/solutions/0956/) — Super Duper Sum
- ○ [0960](/solutions/0960/) — Stone Game Solitaire
- ○ [0967](/solutions/0967/) — $B$-Trivisible Numbers
- ○ [0968](/solutions/0968/) — 5D Summation
- ○ [0971](/solutions/0971/) — Modular Polynomial Composition
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ○ [0977](/solutions/0977/) — Iterated Functions
- ● [0980](/solutions/0980/) — The Quaternion Group I
- ○ [0981](/solutions/0981/) — The Quaternion Group II
- ○ [0984](/solutions/0984/) — Knights and Horses
- ○ [0989](/solutions/0989/) — Fibonacci Sum
- ○ [0990](/solutions/0990/) — Addition Equations
- ○ [0992](/solutions/0992/) — Another Frog Jumping
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials
- ○ [0996](/solutions/0996/) — Overtakes
- ○ [0999](/solutions/0999/) — Alternating Recurrence
- ● [1000](/solutions/1000/) — Problem $1000$
- ○ [1001](/solutions/1001/) — Connections I
- ○ [1004](/solutions/1004/) — Balanced Integer

<!-- /problems -->
