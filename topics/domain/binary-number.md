<!-- tags: [binary-number] -->
<!-- status: final 2026-10-17T06:31Z -->
# Binary number

A [binary number](https://en.wikipedia.org/wiki/Binary_number) writes $n$ as a sum of distinct
powers of two, $n = \sum_i b_i 2^i$ with each $b_i \in \{0, 1\}$. To the machine that is simply
how $n$ is stored. To a problem setter it is a structure, and it keeps coming back because so many
definitions turn out to be secretly about it. A recurrence defined on $2n$ and $2n+1$, a tree whose
parent rule involves a power of two, a game that deletes digits, a count that splits by number
length: each one reads the digits of $n$, whether or not the statement says "binary". This page is
about the *number system*: the digits of $n$ and what they encode. Its companion,
[bit manipulation](/topics/technique/bit-manipulation), covers the other reading, where an
integer is a container of flags and `&`, `|`, `^` act as set operations. The idioms overlap, but
the questions do not.

## The idea — the digits are a path

Every positive integer has exactly one binary expansion with a leading 1. Three facts about that
expansion do almost all the work in the problems below.

- **Appending a digit is $n \mapsto 2n + b$.** Reading the bits from most to least significant,
  $n$ is built by starting at 1 and repeatedly doubling, adding 1 for each 1-bit. So the bits after
  the leading 1 are the root-to-node path to $n$ in the infinite binary tree where node $m$ has
  children $2m$ and $2m+1$. Any sequence defined by rules for $a_{2n}$ and $a_{2n+1}$ is a
  function on that tree. Its value at $n$ can therefore be computed by walking those $\log_2 n$
  edges, instead of filling a table up to $n$.
- **The leading bit is the greedy power of two.** The largest $2^j \le n$ is the top bit of
  $n$, and $n - 2^j$ is $n$ with that bit cleared. Repeatedly taking "the largest power of two that
  fits" visits exactly the 1-bits. That is the binary expansion, read as a
  [greedy algorithm](/topics/technique/greedy-algorithm) for a canonical coin system. A process
  that keeps subtracting the largest fitting power of two runs for
  [popcount](https://en.wikipedia.org/wiki/Hamming_weight) steps, not for $n$ steps.
- **Bit length partitions the integers into blocks.** The numbers with exactly $k$ bits are
  $[2^{k-1}, 2^k - 1]$, a block of size $2^{k-1}$. If a condition depends on $n$ only through
  its length or its low bits, a sum over $1..N$ becomes a sum over about $\log_2 N$ blocks.

[Binary fractions](https://en.wikipedia.org/wiki/Dyadic_rational) carry the same structure past
the binary point. A number whose denominator is a power of two has a finite expansion. So it is
exactly an integer scaled by $2^{-B}$, and the computer can hold it with no rounding.

## Shape 1 — walk the bits, carry a pair

The most useful pattern here evaluates a "divide by two" recurrence at a huge index in
$O(\log n)$. Suppose the rules for $a_{2n}$ and $a_{2n+1}$ need only $a_n$ and $a_{n+1}$. Then
the pair $(a_m, a_{m+1})$ at a node determines the pair at either child, and each transition is
*linear* in the pair. Start at the root pair and apply one of the two transitions per bit:

```python
x, y = root_pair
for bit in bin(m)[3:]:            # the path: every bit after the leading 1
    x, y = step0(x, y) if bit == '0' else step1(x, y)
```

**Problem 169** counts the
[hyperbinary](https://oeis.org/A002487) representations of $n$, meaning sums of powers of two
where each power may appear at most twice. Conditioning on how often the smallest power is used
splits $f(2m)$ and $f(2m+1)$ into sums of $f(m)$ and $f(m-1)$. That is a pair recurrence, and
$n = 10^{25}$ becomes 84 steps of big-integer addition. **Problem 918** is the same machine on a
sequence with linear rules for $a_{2n}$ and $a_{2n+1}$. A
[telescoping](/topics/technique/telescoping-series) identity first reduces a trillion-term sum to
one term, and the bit walk then evaluates that term. Because each step is linear, the walk is a
product of $2\times 2$ matrices chosen by the bits. When the index is a *power*, that is
[matrix exponentiation](/topics/technique/matrix-exponentiation). Here the index is arbitrary, so
the walk follows the bits as they come.

**Problem 175** runs the walk *backwards*. The hyperbinary count is
[Stern's diatomic sequence](/topics/domain/sterns-diatomic-sequence) shifted by one. The ratio of
consecutive terms traces the [Calkin–Wilf tree](/topics/domain/calkin-wilf-tree), which hits
every positive rational exactly once. So a given $p/q$ fixes a unique $n$, and the problem asks
for it as run lengths of its binary digits. Climbing from $p/q$ to the root subtracts the smaller
part from the larger. A maximal run of identical steps is one quotient of the
[Euclidean algorithm](/topics/technique/euclidean-algorithm), and it is also one run of equal
bits of $n$. So $n$'s binary expansion is never built at all: the
[continued fraction](/topics/domain/continued-fraction) of $p/q$ *is* its run-length encoding,
apart from fixing up the top run.

The two languages differ only in how they read the path. Python iterates over the string
`bin(m)`. That is clear and fast enough, because the string has only $\log_2 m$ characters. C has
no such string, so it finds the leading bit and tests downward from it: `mpz_tstbit(n, i)` over
`mpz_sizeinbase(n, 2)` positions in 169, where GMP holds a 1000-digit $n$, and
`(m >> b) & 1` below a scanned `hi` in 918.

## Shape 2 — the top bit, greedily

**Problem 872** builds a tree recursively and asks for a sum along the path from node $K$ to the
root. The analysis shows that in $T_n$ the parent of $k$ is $k$ plus the largest power of two not
exceeding the gap $n - k$. Each step clears the top bit of the gap. So the climb to the root takes
popcount$(n-K)$ steps, at most 57 for $n = 10^{17}$. Most of the work is in the proof. The code
is a three-line loop around one primitive, *the highest set bit*, and that primitive is where
the languages part:

| | Python | C |
|---|---|---|
| bit length of $x$ | `x.bit_length()` | `64 - __builtin_clzll(x)` (undefined at $x = 0$) |
| largest $2^j \le x$ | `1 << (x.bit_length() - 1)` | `1ULL << (63 - __builtin_clzll(x))` |
| bit $i$ of $x$ | `x >> i & 1` | `x >> i & 1` (on a type wide enough for $i$) |
| digits as text | `bin(x)[2:]` | no built-in, so shift and mask |

`__builtin_clzll` compiles to a single instruction (`lzcnt`/`bsr`). Python's `bit_length` is
nearly as cheap, because a big integer already knows how many limbs it has. The C caveat is the
zero case: `clz(0)` is undefined behaviour. Problem 882's `bit_length` helper guards it
explicitly, and 872 avoids it only because its loop condition keeps the gap positive.

## Shape 3 — count by bit length

**Problem 899** is a two-pile take-away game. Its losing positions $(a, b)$, $a \le b$, turn out
to be exactly those where the low $\text{bitlen}(a)$ bits of $b$ are all ones, or equivalently
$2^{\text{bitlen}(a)} \mid b + 1$. For every $a$ in the block $[2^{k-1}, 2^k - 1]$ the number of
partners $b \le n$ is the same, $\lfloor (n+1)/2^k \rfloor$. So the count at $n = 7^{17} \approx 2^{48}$
is a sum over 48 blocks, followed by the usual doubling and diagonal correction to turn
unordered pairs into ordered ones. Spotting the block structure is the whole technique. Once a
predicate depends on $n$ only through its bit length or its trailing bits, never iterate over
$n$.

The diagonal shows a small difference between the languages. It counts the $j$ with
$2^j - 1 \le n$, which Python reads off directly as `(n + 1).bit_length() - 1`. The C port uses a
short loop over $j$. That avoids calling `clz` and keeps every shift below 64 by construction,
which matters more than a few saved cycles.

## Shape 4 — a sequence of bits, read as a number

**Problem 36** (public) is the plain base-conversion question: which numbers are palindromes in
base 10 *and* base 2? Generating the decimal palindromes from their left halves cuts a million
candidates down to about two thousand. The binary test is then the only place where the two
languages really differ. Python reverses the digit string:

```python
number == int(str(bin(number))[2:][::-1], base=2)
```

C extracts the bits low to high into an array and compares it with its mirror:

```c
while (tmp > 0) {
    bits[len++] = (char)(tmp & 1);
    tmp >>= 1;
}
```

Both work because the leading-zero convention rules out trailing zeros in a palindrome. Every
binary palindrome is odd, a free filter that neither version happens to need.

**Problem 265** turns the reading around. A "binary circle" is a cyclic string of $2^N$ bits
whose $N$-bit windows are all distinct, a
[de Bruijn sequence](/topics/domain/de-bruijn-sequence). The answer sums the circles read as
binary numbers. Three integers carry the depth-first search. The current window is updated as
`(window << 1 | bit) & mask`. The windows already used are a bit set, which is
[bit manipulation](/topics/technique/bit-manipulation) proper. The running value is updated as
`value << 1 | bit`. That last integer is a binary number in the most literal sense: the bits as
they were placed. In Python it can grow without limit. In C it has to fit in a word, so the C port
rejects $N > 6$, because $2^N$ windows must fit in a 64-bit set and $2^N$ bits in a 64-bit value.
It also adds up the circles in an `unsigned __int128`, since the sum of up to $2^{26}$ such values
can exceed 64 bits.

## Shape 5 — binary fractions as fixed point

**Problem 882** is a partizan game: the two players delete 1-bits or 0-bits from binary numbers.
Every position's value is a [surreal number](/topics/domain/surreal-number), and here always a
*dyadic* one. Two binary ideas make it tractable. First, deleting bit $i$ of $x$ is an index
computation, `((x >> (i + 1)) << i) | (x & ((1 << i) - 1))`, so every move lands on a smaller
table entry. Second, all values are multiples of $2^{-B}$ for $B = \text{bitlen}(n)$, so they are
stored as integers scaled by $2^B$, with no `Fraction` and no float. The "simplest number"
between the best Left and best Right option, the core rule of
[combinatorial game theory](/topics/domain/combinatorial-game-theory), is then a bit operation.
If no integer fits, the simplest dyadic in the interval is the shared prefix of the endpoints
above their highest differing bit, `(lo ^ top).bit_length()`. Binary expansion, simplicity and
smallest denominator are the same thing for dyadic rationals.

The pitfall is the sign. Values can be negative, and the code rounds with arithmetic right
shifts (`lo >> B` for a floor, `-((-t) >> B)` for a ceiling). Python defines `>>` on negative
integers as floor division by $2^k$. C leaves right-shifting a negative signed value
implementation-defined. GCC and Clang shift arithmetically, which is what the port relies on. A
strictly portable version would divide and correct the rounding by hand. The C port also keeps
the weighted total in `__int128`: at $n = 10^6$ the scaled sum passes $2^{63}$, a limit Python
never shows.

## How to reason about it

- **Spot a recurrence on $2n$ and $2n+1$.** It is a function on the binary tree. Look for a
  small state (often a pair) that the two child rules update, and walk the bits. The cost is
  $O(\log n)$ steps, and that is why a statement can quote $n = 10^{25}$ or $10^{12}$.
- **Spot a "largest power of two" rule.** It walks the 1-bits. Count steps by popcount, and
  use `bit_length` or `clz` rather than a loop that doubles.
- **Spot a predicate on bit length or low bits.** Sum over blocks $[2^{k-1}, 2^k)$, not over
  integers.
- **Spot powers of two in denominators.** They are dyadic, so use integers in fixed point. The
  arithmetic is exact, and comparisons and "simplest" questions become bit tests.
- **In C, mind the edges that Python hides:** `clz(0)`, shifts by 64 or more (undefined, and
  `1 << 40` on a plain `int` is already wrong), right shifts of negative numbers, and values that
  silently outgrow 64 bits. Use `1ULL`, guard zero, and reach for `__int128` or GMP
  ([arbitrary precision](/topics/technique/arbitrary-precision-arithmetic)) as soon as the
  analysis says the numbers can pass $2^{63}$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0265](/solutions/0265/) — Binary Circles
- ○ [0323](/solutions/0323/) — Bitwise-OR Operations on Random Integers
- ○ [0361](/solutions/0361/) — Subsequence of Thue-Morse Sequence
- ○ [0384](/solutions/0384/) — Rudin-Shapiro Sequence
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0409](/solutions/0409/) — Nim Extreme
- ○ [0463](/solutions/0463/) — A Weird Recurrence Relation
- ○ [0486](/solutions/0486/) — Palindrome-containing Strings
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ○ [0538](/solutions/0538/) — Maximum Quadrilaterals
- ○ [0539](/solutions/0539/) — Odd Elimination
- ○ [0626](/solutions/0626/) — Counting Binary Matrices
- ○ [0689](/solutions/0689/) — Binary Series
- ○ [0703](/solutions/0703/) — Circular Logic II
- ○ [0711](/solutions/0711/) — Binary Blackboard
- ○ [0734](/solutions/0734/) — A Bit of Prime
- ○ [0759](/solutions/0759/) — A Squared Recurrence Relation
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0767](/solutions/0767/) — Window into a Matrix II
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0782](/solutions/0782/) — Distinct Rows and Columns
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0810](/solutions/0810/) — XOR-Primes
- ○ [0811](/solutions/0811/) — Bitwise Recursion
- ○ [0813](/solutions/0813/) — XOR-Powers
- ○ [0869](/solutions/0869/) — Prime Guessing
- ● [0872](/solutions/0872/) — Recursive Tree
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0878](/solutions/0878/) — XOR-Equation B
- ● [0882](/solutions/0882/) — Removing Bits
- ○ [0890](/solutions/0890/) — Binary Partitions
- ● [0899](/solutions/0899/) — DistribuNim I
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ○ [0948](/solutions/0948/) — Left vs Right
- ○ [0949](/solutions/0949/) — Left vs Right II
- ○ [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
