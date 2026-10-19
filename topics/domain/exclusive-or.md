<!-- tags: [exclusive-or] -->
<!-- status: final 2026-10-19T09:34Z -->
# Exclusive or

[Exclusive or](https://en.wikipedia.org/wiki/Exclusive_or) (XOR, $\oplus$, `^` in both C and Python) is
true when exactly one of its inputs is. Applied bitwise to integers, it is the operation
behind stream ciphers, Nim, parity checks and the "XOR-equation" family of problems. It appears so often
because it has an unusually clean algebra. It is **addition without carries**, which makes each bit
independent of the others, and **every value is its own inverse**. Most XOR problems are solved by
picking whichever of those two views makes the question easy. The three solved problems below use
each of them.

## The idea — two views of the same operation

**As an algebra.** XOR is associative and commutative, $0$ is its identity, and $x \oplus x = 0$. So
$(\{0,1\}^n, \oplus)$ is a group in which every element is its own inverse. It is the vector space
$\mathbb{F}_2^n$, with XOR as vector addition. Consequences:

- **Cancellation**: $a \oplus k \oplus k = a$. Encryption and decryption are the same operation.
- **Order does not matter**: a XOR of many values depends only on which values occur an odd number of times.
- **Linear algebra applies**: systems of XOR equations are solved by Gaussian elimination over
  $\mathbb{F}_2$ (Lights Out, 707, is the textbook case).

**As arithmetic.** For non-negative integers,

$$a + b = (a \oplus b) + 2\,(a \mathbin{\&} b).$$

The XOR is the sum digit by digit, and the AND marks the positions that carry. So $a \oplus b = a + b$
exactly when no position carries, $a \mathbin{\&} b = 0$. Because there are no carries, **each bit of
$a \oplus b$ depends only on the same bit of $a$ and $b$**. A sum of XORs, or a count of values with a
XOR property, can therefore often be split by bit position and solved one bit at a time with
[digit DP](/topics/technique/digit-dp) or a closed count. (Several of the unsolved problems in the list,
XOR-Primes and the XOR-Equations, go one step further and use XOR as the addition of
[carry-less multiplication](https://en.wikipedia.org/wiki/Carry-less_product), the polynomial
arithmetic of $\mathbb{F}_2[x]$.)

## Three uses across the problems

**59, XOR decryption: cancellation.** The ciphertext is ASCII text XORed with a repeating lowercase
key. Since $c \oplus k = p$ for the right key byte, every position $i, i+L, i+2L, \dots$ is a
single-byte XOR cipher, a [Vigenère cipher](/topics/domain/vigenere-cipher) over XOR. Each slice
is broken on its own by trying all 26 key bytes and keeping the one whose decryption contains the most common
English letters ([frequency analysis](/topics/domain/frequency-analysis)). That turns a $26^L$ key
search into $26L$ linear scans:

```python
encrypted_slices: list[list[int]] = [encrypted[i::key_length] for i in slices_range]
...
_decrypted = "".join((chr(_char ^ _key) for _char in encrypted_slices[i]))
```

The test case passes `key_length = 9` for a key of three letters, and this still works. A key that
repeats every 3 also repeats every 9, so each of the nine slices is still a single-byte cipher, just with
less text to score.

**301, Nim: XOR as carry-free addition.** In Nim the position $(n, 2n, 3n)$ is a loss for the player
to move exactly when the [nim-sum](/topics/domain/nimber) $n \oplus 2n \oplus 3n$ is zero. Since
$n + 2n = 3n$ is exact, the identity above gives $n \oplus 2n = 3n$, and so the nim-sum is zero
exactly when $n \mathbin{\&} 2n = 0$. No carries means no two adjacent 1-bits in $n$, which defines the
[fibbinary numbers](/topics/domain/fibbinary-numbers). The game question becomes a count of binary
strings with no `11`, which a digit DP answers in $O(\log n)$. That is $O(30)$ steps for a
bound of $2^{30}$, instead of $10^9$ nim-sums.

**1000, three sub-problems: bit-by-bit decomposition.** Problem 1000 combines three bitwise
sub-problems. Two of them are solved by splitting on bit position. *Max And* partitions $\{1..n\}$ into
two sets to maximise $\sum a \mathbin{\&} b$. Because AND is also carry-free, the objective is a sum
over bits $j$ of $2^j \cdot a_j(c_j - a_j)$, and each bit is maximised independently by a balanced split.
*Unreachable Nim* counts Nim positions that no winning move can reach. A move from pile $a$ wins exactly
when $a \oplus s < a$, where $s$ is the nim-sum, which happens exactly when $a$ has the top bit of $s$ set.
So the condition becomes "all three piles share the top bit of their XOR", a digit DP over bits with
a parity constraint above that bit. The third sub-problem uses $x^2 \oplus y^2$ only as an edge weight,
with no special structure, and is a sort plus DP.

## Python and C

XOR itself is `^` in both languages, but **precedence differs**. In C, `a ^ b == c` parses as
`a ^ (b == c)` because the bitwise operators bind more loosely than `==`. In Python, comparisons bind
more loosely than `^`, so the same text means `(a ^ b) == c`. Parenthesise in both and the code ports
safely. The other differences are in what surrounds XOR:

- **59**: Python slices with `encrypted[i::key_length]` and scores with `str.count` over the
  decrypted string. C makes two passes to size and fill the slices, and scores by XORing each byte and
  scanning the common-letter list, never building a string. The work is the same, at about $26 \times 1.4$k
  byte operations.
- **301**: the same digit DP, written two ways. Python is top-down, `dp(pos, prev, tight)` with a fresh
  `lru_cache` per call so that benchmark runs stay honest. C unrolls it bottom-up into four rolling
  scalars: free numbers ending in 0, free numbers ending in 1, whether the tight prefix is still valid,
  and its last bit. That needs no memo table and no recursion.
- **1000**: the weights $x^2 \oplus y^2 < 2^{20}$ fit an `int` in C, and the edge list (about 500k
  edges) is a `malloc`ed struct array sorted with `qsort`. Python builds and sorts a list of tuples.
  For the modular meta-recurrence, C computes each product of residues in `__int128` before reducing.
  With the test's modulus of $10^9 + 7$ a `long long` would be enough, but the wider type keeps the
  code correct for any modulus that fits 64 bits. Python's integers make the question moot.

## How to reason about it

- **Seeing $\oplus$ next to $+$, think carries.** $a \oplus b \le a + b$, with equality iff
  $a \mathbin{\&} b = 0$. Many "when is this XOR zero / equal to the sum" questions reduce to a
  no-carry condition on bits.
- **Split by bit.** Sums and counts over XOR (or AND, OR) decompose into independent per-bit
  problems. Count how many values have bit $j$ set, solve per bit, and weight by $2^j$.
- **Use cancellation for anything symmetric.** Repeating-key ciphers, "find the element that appears
  an odd number of times", and prefix XORs ($x_l \oplus \dots \oplus x_r = P_r \oplus P_{l-1}$) all rely on
  $x \oplus x = 0$.
- **For systems, think $\mathbb{F}_2$.** A set of XOR constraints is a linear system, and Gaussian
  elimination (or a [linear basis](https://en.wikipedia.org/wiki/Basis_(linear_algebra)) of
  bit-vectors) solves it in polynomial time.
- **In Nim, the top bit of the nim-sum decides.** A winning move exists from a pile exactly when that
  pile has the nim-sum's top bit set. Both 301 and 1000 rest on this.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0059](/solutions/0059/) — XOR Decryption
- ● [0301](/solutions/0301/) — Nim
- ○ [0323](/solutions/0323/) — Bitwise-OR Operations on Random Integers
- ○ [0334](/solutions/0334/) — Spilling the Beans
- ○ [0691](/solutions/0691/) — Long Substring with Many Repetitions
- ○ [0707](/solutions/0707/) — Lights Out
- ○ [0760](/solutions/0760/) — Sum over Bitwise Operators
- ○ [0774](/solutions/0774/) — Conjunctive Sequences
- ○ [0806](/solutions/0806/) — Nim on Towers of Hanoi
- ○ [0810](/solutions/0810/) — XOR-Primes
- ○ [0813](/solutions/0813/) — XOR-Powers
- ○ [0832](/solutions/0832/) — Mex Sequence
- ○ [0877](/solutions/0877/) — XOR-Equation A
- ○ [0878](/solutions/0878/) — XOR-Equation B
- ○ [0945](/solutions/0945/) — XOR-Equation C
- ○ [0973](/solutions/0973/) — Random Dealings
- ● [1000](/solutions/1000/) — Problem $1000$

<!-- /problems -->
