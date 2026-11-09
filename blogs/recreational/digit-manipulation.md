<!-- tags: [digit-sum, palindromic-number, string-slicing, positional-notation] -->
<!-- status: final 2026-11-03T07:27Z -->
# Digit Manipulation

A surprising share of Project Euler is about the *writing* of a number rather than the number:
reverse it, test it for a palindrome, add up its digits, sort them, map each one through a table.
Every one of those operations needs the same first step — get the digits out of the integer — and
there are exactly two ways to take it. Either you hand the integer to the runtime's formatter and work
on the resulting **string**, or you peel digits off with **arithmetic**, `n % 10` and `n // 10`, one
[positional](https://en.wikipedia.org/wiki/Positional_notation) place at a time. The two are
interchangeable in meaning and wildly different in cost, and the cost runs in *opposite directions*
in Python and in C. This page is about choosing between them; the algebra of the digit sum itself
(mod 9, carries, digit DP) lives on [Digit sum](/blogs/domain/digit-sum).

## Two ways to read a number

Write $n = \sum_{i=0}^{D-1} d_i\,10^i$ with $D = \lfloor \log_{10} n \rfloor + 1$ digits. The
arithmetic route reads that sum right to left:

```python
def digit_sum(n: int) -> int:
    total = 0
    while n:
        n, d = divmod(n, 10)                     # d is the units digit; n drops one place
        total += d
    return total
```

The string route asks the formatter for all $D$ digits at once, most significant first, and then
treats them as a sequence:

```python
sum(map(int, str(n)))                            # digit sum
int(str(n)[::-1])                                # reversal
"".join(sorted(str(n)))                          # order-blind fingerprint
```

Two differences in *shape* matter before any timing does. The arithmetic loop yields digits
**least-significant first**, which is exactly the order a reversal needs — `r = r * 10 + n % 10`
builds the mirror image while it consumes the original, with no buffer at all. The string yields
them **most-significant first** and *all at once*, which is what you want for anything positional
from the left — prefixes, truncations, the left half of a palindrome, slicing in general (see
[String slicing](/blogs/technique/string-slicing)). And the arithmetic loop never sees a leading
zero, while a string can carry one (`"007"`), which is either a bug or exactly the fixed-width view
you wanted.

## Python: the formatter is the fast path

In CPython the decision comes down to one fact: `str(n)` is a single call into C, while the
`divmod` loop is $D$ trips through the interpreter. Timings on the machine this page was written on
(CPython 3.14, nanoseconds per call):

| digits $D$ | `sum(map(int, str(n)))` | `divmod` loop | `int(str(n)[::-1])` | `r*10 + n%10` loop |
| ---------: | ----------------------: | ------------: | ------------------: | -----------------: |
|          1 |                     192 |            68 |                 130 |                 63 |
|          5 |                     267 |           217 |                 145 |                209 |
|          9 |                     352 |           395 |                 154 |                371 |
|         20 |                     608 |           967 |                 197 |              1 273 |
|        302 |                   6 971 |        24 925 |               1 840 |             46 908 |
|      6 021 |                 468 495 |     5 260 430 |           4 469 995 |         12 510 725 |

Below about five digits the string's fixed costs — allocate a `str`, call `int` per character —
lose to a handful of arithmetic steps. Past that the string wins, and once $n$ outgrows a machine
word the gap turns structural: each `n // 10` on a $D$-digit big integer is itself $O(D)$, so the
loop is **quadratic**, and every step of it is interpreted, whereas the formatter converts in C, a
word-sized chunk of digits at a time. Reversal tilts further toward strings than the sum does,
because `[::-1]` is a single C-level copy (an [extended slice](/blogs/technique/extended-slice))
with no per-digit Python call at all.

That is why the public big-integer problems are one-liners. Problem 16 sums the digits of
$2^{1000}$, problem 20 those of $100!$, problem 56 those of every $a^b$ for $a, b < 100$ — each is
`sum(int(d) for d in str(...))` over Python's
[arbitrary-precision](/blogs/technique/arbitrary-precision-arithmetic) integers, and the
hundreds-of-digits sizes involved sit squarely in the rows where the string is three to four times
faster. Problem 55 runs reverse-and-add on numbers that grow past fifty digits, and its whole inner
step is

```python
number += int(str(number)[::-1])
if str(number) == str(number)[::-1]: ...
```

— the [Lychrel](/blogs/domain/lychrel-number) iteration written as directly as the statement.
Problems 4 and 36 test [palindromes](/blogs/domain/palindromic-number) the same way, and 36 goes
further: it *generates* its decimal palindromes by string concatenation, `digits + digits[::-1]`
(the odd-length ones with a middle digit spliced in), and checks the binary side with
`bin(n)[2:][::-1]`. Problem 52's test that $x, 2x, \dots, 6x$ are digit permutations of one another
is a set of fingerprints, `"".join(sorted(str(k * x)))` — a canonical form the string gives you for
free. Problem 34 never leaves string-land: it keys its digit-factorial table by the characters
`"0"`…`"9"`, so a digit never has to become an `int`.

Two caveats keep this from being a blanket rule. First, since CPython 3.11 `str()` refuses integers
beyond 4 300 digits by default (a denial-of-service guard against quadratic conversion); the digit
sum of $2^{20000}$ needs `sys.set_int_max_str_digits(0)` first. Second, when the numbers are *small
and hot* — the successor function of an iterated map, called millions of times on values under
$10^7$ — the arithmetic loop is level with or ahead of the string, and it is what problems 74 and 92
use:

```python
while n > 0:
    result += digit_factorials[n % 10]           # problem 74: the digit-factorial successor
    n //= 10
```

The arithmetic form also *composes* with tables in a way the string does not. If the per-digit
function is additive, precompute it for $0 \dots 999$ inside `solve()` and the successor becomes
`T[n % 1000] + T[n // 1000 % 1000] + T[n // 1000000]` — three lookups instead of seven iterations,
which is digit manipulation in base 1000. Better still is not to touch each number's digits at all:
problem 92 counts digit-square-sum *buckets* by convolution and only ever classifies the few hundred
distinct sums, and problem 30 enumerates digit multisets rather than numbers. The fastest digit loop
is the one you replaced with a count.

The rule flips once more when the *same* digit edit applies to a whole array of numbers. Problem 425
links two primes if they differ in one digit, or if one is the other with a digit prepended. It needs
every such link among the 660 000 primes below $10^7$. The string route would build, slice and parse
millions of strings. The arithmetic route writes each edit as a change of place value: lowering the
digit at place $10^k$ by $\delta$ is `v - delta * 10**k`, valid when `v // 10**k % 10 >= delta`, and
dropping the leading digit is `v % 10**(d-1)`. Both are whole-array expressions in NumPy, one per
(place, $\delta$) pair, run over every prime at once and filtered through the sieve mask. The
per-digit work leaves the interpreter just as `str()` does, and nothing is ever formatted. The edge
cases are positional rules, not string rules. A leading digit may not drop to 0, because that
shortens the number and is a different kind of link. And dropping the lead of 203 gives 3, which is
not a link: prepending 2 to 3 makes 23, so the remainder must still have $d-1$ digits. Generating
only the *downward* edits, toward smaller neighbours, halves the work, because each edge is made
when its larger end arrives.

## C: the formatter is the slow path

C reverses every conclusion. There is no interpreter overhead to amortise; `n % 10` and `n / 10` on
a `long long` compile to a multiply-and-shift by a magic constant, with no division instruction; and
`snprintf` is a general-purpose formatting engine — format-string parsing, a buffer to fill, a
`strlen` to find its end — invoked to do what a few instructions per digit already do. Measured over
twenty million twelve-digit values with `gcc -O2`:

| operation       | `% 10` / `/ 10` loop | `snprintf` + char loop |
| --------------- | -------------------: | ---------------------: |
| digit sum       |              11.9 ns |                36.9 ns |
| palindrome test |              12.8 ns |                38.9 ns |

So in C the arithmetic route is the default, and the solutions mostly take it: problems 30, 34, 74
and 92 compute their digit maps with `% 10` loops, problem 36 extracts bits with `& 1` and `>>= 1`
for its binary palindrome check, and problem 52 pulls its digits out arithmetically before sorting
them. Where a C port still formats, it is usually a literal translation of a Python string idiom,
and usually off the hot path: problem 4 formats each product with `snprintf` and compares from both
ends (problem 34 formats too, for a digit-membership screen), but its descending search breaks out after a few candidates per row, so the 3× is immaterial.
Problem 36 is the instructive counter-case — it builds each palindrome with `snprintf("%s%s", …)`
and parses it back with `atoll`, a round trip through text for what is pure arithmetic:

```c
long long p = half, t = odd ? half / 10 : half;  /* mirror the left half onto itself */
while (t) { p = p * 10 + t % 10; t /= 10; }
```

The same goes for fingerprints. Problem 52's C sorts the digit characters with `qsort`, faithful to
the Python; a ten-slot histogram — or the counts packed four bits apiece into one integer — is the
same canonical form with no sort and no string compare.

The big-integer problems turn the question inside out. C has no built-in big integer, so problems
16, 20, 55 and 56 must choose a representation, and they choose **a little-endian array of decimal
digits**, `digits[0]` the units place. That is the string route, done by hand and kept permanently:
the number is never anything *but* its digits, so the digit sum is a plain loop over the array, and
problem 55's reverse-and-add needs no reversed copy at all — index $i$ of the little-endian number is
index $D-1-i$ of its reversal, so `a[i] + a[n-1-i]` adds the two in one pass. The price is paid in
multiplication, which must carry one digit at a time (see
[Carry arithmetic](/blogs/technique/carry-arithmetic)); limbs of $10^9$ would multiply about nine
times faster and then make every digit query a `% 10` loop again. Store what the problem *asks
about*: when the output is a digit property, base-10 storage is the right trade.

## When neither route applies

Both routes assume there is a number in hand to take apart, and that taking it apart once is cheap
enough to do as often as needed. Past a certain scale neither holds, and the digit operations above
turn up as *bookkeeping* instead. Recent problems show the ways this happens (their mathematics is on
[Positional notation](/blogs/domain/positional-notation) and [Digit sum](/blogs/domain/digit-sum);
what matters here is what replaces the extraction loop).

- **The number is too long to hold.** Problem 698 asks for a 123-number of rank about $10^{17}$, but
  only modulo $123\,123\,123$. Unranking picks its digits most-significant first, and each one is
  folded straight into the residue with `ans = (ans * 10 + d) % m`. That is the reversal loop's
  `r * 10 + d` step, run in the other direction. The full number is never formed, so it never needs to
  be converted or divided. Its only other digit question is "how many of each digit". That is the
  order-blind fingerprint from problem 52, and here it is the whole definition.
- **The constraint is on the multiset, so count arrangements with an EGF.** Problem 520 counts
  numbers up to $10^{2^{39}}$ digits long in which every even digit appears an even number of times
  and every odd digit an odd number of times or not at all. That is a condition on problem 52's
  fingerprint, and it says nothing about order. An
  [exponential generating function](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function)
  counts exactly that: a digit allowed $j$ times contributes $x^j/j!$, and the product of the
  $1/j!$ factors is the multinomial that counts arrangements. So the even digits are $\cosh x$
  each and the odd ones $1 + \sinh x$. Both are made of $e^{\pm x}$, and $L!\,[x^L]\,e^{kx} = k^L$,
  so the count for length $L$ is a sum of 21 powers $k^L$, and summing over lengths is 21 geometric
  series. Leading zeros cost one more such product, with the zero digit's parity flipped. No
  digit string is ever enumerated, not even as a state.
- **The number is a digit pattern, so it has a formula.** Problem 684 needs the smallest number
  with digit sum $n$, for $n$ up to a Fibonacci number near $3 \times 10^{18}$. The greedy answer
  is a short leading digit followed by as many 9s as possible. Writing $n = 9q + r$, a run of $q$
  nines is $10^q - 1$, so the number is $(r+1)\,10^q - 1$. The digit string is now a formula, so
  sums of it are geometric series. Its $3 \times 10^{17}$ digits never exist: $10^q$ is taken
  modulo a prime, with the exponent reduced by Fermat. A `str()` of it would fill hundreds of
  petabytes. The
  general move is to name a digit string by the arithmetic that spells it: repunits are
  $(10^k - 1)/9$, and a block $w$ repeated is $w \cdot (10^{kL} - 1)/(10^L - 1)$. The same move
  sums a whole *family* given by a digit pattern. In problem 711 a brute-force game search shows
  the winning numbers are all-ones binary strings, plus isolated ones at even bit positions
  followed by an optional even-length run of ones. Each family is a set of binary patterns, so its
  sum over all lengths up to $2^{12\,345\,678}$ is a geometric series, or an arithmetico-geometric
  one when the pattern's position also counts how many tails it allows.
- **The fold has a small state, so count all inputs at once.** Problem 706 asks how many $d$-digit
  numbers, for $d = 10^5$, have a number of 3-divisible substrings that is itself a multiple of 3.
  Reading the digits left to right is the same fold as above, but the state it carries is richer than
  one residue: the running digit sum mod 3, how many earlier prefixes share each residue (mod 3), and
  the substring count so far (mod 3). Measured relative to the current residue, that is 81 states, and
  every digit of a residue class moves them the same way. So the "loop over digits" becomes an
  $81 \times 81$ transfer matrix raised to the power $d - 1$. The digit string is never written down;
  only how many strings sit in each state.
- **The length itself is astronomical, so concatenate blocks.** Writing a digit after a number is
  $v \mapsto 10v + d$. Writing a whole block $w$ of $L$ digits after it is
  $v \mapsto 10^L v + w$. So a block's effect is fixed once you know its length, and blocks
  compose. Problem 294 counts the $n$-digit strings, for $n = 11^{12}$, whose value is divisible by 23
  and whose digit sum is 23. Even a matrix step per digit is too many steps. Instead it keeps a table
  per *block*: how many strings of length $L$ have each residue and each digit sum up to 23. Each
  block's residue is measured from its own lowest place, so the table does not depend on where the
  block ends up. Putting block $M$ above block $L$ multiplies $M$'s residues by $10^L \bmod 23$ and
  convolves the two tables. That join is associative, so the length-$n$ table comes from
  exponentiation by squaring on *length*: about 80 joins. Problem 506 is the same algebra with a
  periodic digit stream: one term is the term fifteen places back with one period appended,
  $v_{n+15} = 10^6 v_n + Q$. That affine step unrolls into a geometric series in each of the
  fifteen residue classes. Problem 1006 goes furthest. Its strings are factors of the
  [Fibonacci word](https://en.wikipedia.org/wiki/Fibonacci_word), and it needs sums of their squared
  decimal values for lengths near $10^{18}$. A state vector such as $(1, Q, Q^2, \Sigma)$ makes
  "append a digit" a fixed $4 \times 4$ matrix. The word is built by concatenation,
  $S_n = S_{n-1}S_{n-2}$, so each standard block's matrix is the product of the previous two. Any
  prefix is then a product of a few blocks, read off its
  [Zeckendorf representation](https://en.wikipedia.org/wiki/Zeckendorf%27s_theorem). In all three
  the digit string is defined by how it is put together, and the arithmetic follows that structure,
  not the digits one at a time.
- **The question is about a second number made from the first.** Problem 290 counts $n < 10^{18}$
  whose digit sum equals that of $137n$. Here the fold has to run *right to left*, the order the
  `% 10` loop already gives. Long multiplication by a constant reads one digit $d$ of $n$, together
  with a carry $c$, and writes one digit of $137n$: `c, out = divmod(137 * d + c, 10)`. So the
  multiplication is a finite automaton (the carry stays below 137), and the second number's digits
  come out in step with the first's. Track only the carry and the running difference of the two digit
  sums. Then every $n$ is counted together in at most $137 \times 325$ states, and no product is
  ever formed. At the end the leftover carry is the top of $137n$; its digit sum settles the last
  comparison. Adding a constant has the same shape. Whenever the second number's digit at each place
  depends only on the first number's digit there and a bounded carry, read both numbers in lockstep.
- **The count is not enough; the values are needed too.** Problem 776 sums $n / d(n)$ for every $n$
  up to about $1.2 \times 10^{18}$. Grouping by the digit sum leaves at most 171 denominators, each
  multiplying $T(s)$, the *sum* of the $n$ with that digit sum, rather than their count. A digit DP
  ordinarily stores only counts. Here positional notation is linear, which lets it carry values too.
  Appending digit $d$ to a prefix $p$ gives $10p + d$. So if a state holds $c$ prefixes totalling
  $t$, appending $d$ to all of them gives $(c,\ 10t + d\,c)$. This is the reversal loop's
  `r * 10 + d` step again, applied to a whole class of numbers at once. The same pair works for any
  quantity linear in $n$, and adding squared totals extends it to sums of $n^2$. The limit $N$ is
  handled by one *tight* prefix, which equals $N$'s own prefix. At each position it spills off
  its smaller digits as new free states, so no state needs a "tight" flag.
- **There are too many steps to take.** Problem 551 iterates $a \mapsto a + s(a)$, the same shape as
  problem 74's digit-factorial successor, but $10^{15}$ times. The numbers fit in a machine word (or
  two), so extraction is not the problem; doing it $10^{15}$ times is. The fix splits the number the way
  the base-1000 table does, into a high block $H$ and a low block $L$ of $k$ digits. Until $L$ carries
  out of $10^k$, $H$ is frozen and enters every step only through its digit sum. So "how many steps to
  overflow the low block, and what is left behind" depends on $(k, s(H), L)$ alone. That is a small,
  heavily repeated key, so the jumps memoise, and each level splits into at most ten jumps one level
  down, one per leading digit of $L$. The digit loop survives, but it walks the digits of the
  *position*, not of each of the $10^{15}$ values.
- **The digits you need are in other bases, of numbers not built yet.** Problem 571 wants the
  smallest numbers that are pandigital in every base from $2$ to $n$. The search builds base-$n$
  permutations most-significant first. Converting each of some $10^8$ candidates into ten bases is the
  arithmetic route at its most brute. Instead, a fixed prefix confines every completion to an interval
  $[lo, hi]$, and in any base $b$, all numbers in it share the leading digits on which $lo$ and $hi$
  agree, found by the same division as always, $\lfloor lo / b^{j} \rfloor = \lfloor hi / b^{j} \rfloor$.
  If that shared prefix is missing more digits than there are free places below it, the whole subtree
  dies. Digit extraction is still the tool, but applied to the *bounds* of a set of numbers rather than
  to its members. The leaf test, for what survives, is problem 52's fingerprint again in its C form: a
  bitmask of digits seen, compared with a full mask.
- **There are too many ways to read the digits.** Problem 637 lets a step insert plus signs
  anywhere in a number's base-$B$ digits. It asks how few steps reach a single digit, in base 10
  and in base 3, for every $n$ up to $10^7$. A 15-digit base-3 number has $2^{14}$ splits. Each
  split is a fixed *weight vector*: a digit's weight is $B$ raised to its distance from the end of
  its block. A split sum is then the dot product of that vector with the digit vector. Laying all $n$
  out as a digit matrix makes a split one matrix-vector product, which is vectorised re-reading.
  Before that, the high/low block split from problem 551 does most of the work. Write
  $n = h \cdot B^k + \ell$ and cut only at the boundary. Then a split sum is a split sum of $h$
  plus one of $\ell$, and each half has only a few thousand values. Store each half's set of
  reachable sums as a bitset, and one AND settles nearly every number. Exhaustive search is left for
  the few the filter cannot decide.
- **There are too many numbers to visit.** Problem 778 sums a carry-free digitwise product over
  $(M+1)^R$ sequences. Each place is independent, so all it ever needs is how often digit $d$ appears
  at place $10^i$ across $[0, M]$. That count has a closed form from the digit's period-$10^{i+1}$
  cycle: with $u = 10^i$ and $M + 1 = 10u\,q + r$, it is $q\,u + \min(\max(r - d\,u, 0), u)$. No number in the range is ever split
  into digits. This is the "replace the digit loop with a count" advice from the Python section, taken
  as far as it goes.
- **There is no `% 10` and no `str()`.** Problem 473 asks which integers have palindromic
  expansions in base $\varphi$. Neither tool exists for an irrational radix, so testing each $n$
  means a greedy expansion in exact $\mathbb{Z}[\varphi]$ arithmetic. The solution does what problem
  36 does with `digits + digits[::-1]`: it *generates* palindromes from their halves. Each chosen
  exponent $k$ brings its mirror $-(k+1)$, and the search keeps only the combinations that land on an
  integer. Generating from halves was a speed-up in base 10. Here it is the only practical route.
  Problem 558 works in a base where testing is the only route, the real root $r \approx 1.4656$ of
  $x^3 = x^2 + 1$, and asks for the number of digits of five million squares. In this base,
  greedy extraction is the digit loop: subtract the largest power of $r$ that fits, and repeat. The
  algebra guarantees that greedy gives the required gap of three between exponents. The catch is
  numerical. Each step multiplies the remainder by $r$, so floating-point error grows by $r$ every
  step, and a large square has some 250 places. So the remainder is held exactly as
  $a + br + cr^2$ with integers. Multiplying by $r$ is then a rotation of three coefficients, the
  arithmetic analogue of `n // 10`. And because $r$ is a
  [Pisot number](https://en.wikipedia.org/wiki/Pisot%E2%80%93Vijayaraghavan_number), the
  coefficients stay small enough for 64-bit integers. Only the comparison "does $r^k$ fit?" needs
  the real value of $r$, and fixed-point arithmetic, with an exact fallback for close calls,
  supplies it.
- **There is no integer at all.** Problem 731 asks for ten digits of a real number, the
  [Stoneham number](https://en.wikipedia.org/wiki/Stoneham_number)
  $A = \sum_i 3^{-i} 10^{-3^i}$, starting at position $10^{16}$. The digit extraction loop still
  applies, scaled up. `n % 10` takes the units digit after shifting; for a real $x$, the ten digits
  from position $n$ on are $\lfloor 10^{n+9} x \rfloor \bmod 10^{10}$. The floor splits term by
  term. Each term's integer part is a quotient by $3^i$, so it is a modular exponentiation times a
  modular inverse modulo $10^{10}$. Its fractional part, $10^e \bmod 3^i$ over $3^i$, adds a small
  carry. The terms too small to reach the window provably cannot change the floor. About 33 terms do
  the work, and none of the $10^{16}$ earlier digits is ever written. This is the
  [BBP](https://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula) idea:
  shift the window to the units place by multiplying modulo the denominator, then read it off.

## Choosing

- **Python, big integers or one-shot work** — use the string. `str`, slicing, `sorted` and `join`
  run in C; anything you write per digit does not. Mind the 4 300-digit conversion limit.
- **Python, small numbers in a hot loop** — the arithmetic loop is competitive, and it is the one
  that extends to chunked lookup tables. Better: restructure so the per-number digit work
  disappears (multisets, bucket counts, memoised chains).
- **Python, one digit edit over many numbers** — write the edit as place-value arithmetic
  (`v - delta * 10**k`, `v % 10**(d-1)`) and apply it to a NumPy array; the same goes for
  re-reading digits under a new grouping, which is a weight vector against a digit matrix.
- **C, anything that fits in 64 bits** — arithmetic, always. Reversal is `r = r*10 + n%10`, a
  palindrome is `n == rev(n)`, a fingerprint is a histogram. Reach for `snprintf` only to print.
- **C, big integers** — store decimal digits when the question is about digits; the representation
  *is* the string, and the manipulation becomes array indexing.
- **Beyond any representation** — build the number digit by digit into a residue (or a small
  automaton, then count strings with a matrix power), count digits per place in closed form, or
  generate the digit strings you want rather than testing values. Name a patterned digit string
  by its formula ($10^q - 1$ for $q$ nines), and get digits deep inside a real number from
  $\lfloor 10^{k} x \rfloor \bmod 10^{m}$ by modular arithmetic.
- **A length too long to step through** — make "append a block" the unit of work: $10^L v + w$,
  a table convolution with residues shifted by $10^L$, or a matrix. Then compose blocks by squaring
  on length, or by the recurrence that builds the string.
- **A condition on how often digits occur, not where** — count arrangements with an exponential
  generating function. When it is made of $e^{kx}$ terms, the counts are power sums $k^L$.
- **A non-integer base** — greedy extraction in exact ring arithmetic (coefficients over
  $1, r, r^2$), with floating point used only to compare.
- **A digit DP that needs more than a count** — carry a bounded carry in the state to follow a
  derived number such as $kn$ (read right to left), and carry (count, total) pairs, updated as
  $(c, 10t + dc)$, when the answer sums values rather than counting them.
- **Too many steps or candidates** — split the number into digit blocks and memoise what the low
  block does given only a summary of the high one, or extract digits from the bounds of a whole
  interval of candidates and prune on them.
- **Either language** — mind the edges: `0` has one digit but the `while n` loop sees none; leading
  zeros exist in strings and in fixed-width digit arrays but not in integers; and the reversal of a
  number ending in `0` is shorter than the original, so `n == rev(n)` is the palindrome test only
  for the numbers that *are* palindromes — a trailing zero can never mirror a leading one.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0004](/solutions/0004/) — Largest Palindrome Product
- ● [0008](/solutions/0008/) — Largest Product in a Series
- ● [0013](/solutions/0013/) — Large Sum
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0020](/solutions/0020/) — Factorial Digit Sum
- ● [0022](/solutions/0022/) — Names Scores
- ● [0030](/solutions/0030/) — Digit Fifth Powers
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0056](/solutions/0056/) — Powerful Digit Sum
- ● [0065](/solutions/0065/) — Convergents of $e$
- ● [0080](/solutions/0080/) — Square Root Digital Expansion
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0112](/solutions/0112/) — Bouncy Numbers
- ● [0119](/solutions/0119/) — Digit Power Sum
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0156](/solutions/0156/) — Counting Digits
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0162](/solutions/0162/) — Hexadecimal Numbers
- ● [0164](/solutions/0164/) — Three Consecutive Digital Sum Limit
- ● [0168](/solutions/0168/) — Number Rotations
- ● [0171](/solutions/0171/) — Square Sum of the Digital Squares
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0217](/solutions/0217/) — Balanced Numbers
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0269](/solutions/0269/) — Polynomials with at Least One Integer Root
- ○ [0284](/solutions/0284/) — Steady Squares
- ● [0288](/solutions/0288/) — An Enormous Factorial
- ● [0290](/solutions/0290/) — Digital Signature
- ● [0294](/solutions/0294/) — Sum of Digits - Experience #23
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0315](/solutions/0315/) — Digital Root Clocks
- ○ [0316](/solutions/0316/) — Numbers in Decimal Expansions
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0348](/solutions/0348/) — Sum of a Square and a Cube
- ○ [0358](/solutions/0358/) — Cyclic Numbers
- ○ [0361](/solutions/0361/) — Subsequence of Thue-Morse Sequence
- ○ [0368](/solutions/0368/) — A Kempner-like Series
- ● [0377](/solutions/0377/) — Sum of Digits - Experience #13
- ● [0387](/solutions/0387/) — Harshad Numbers
- ○ [0391](/solutions/0391/) — Hopping Game
- ○ [0396](/solutions/0396/) — Weak Goodstein Sequence
- ○ [0414](/solutions/0414/) — Kaprekar Constant
- ○ [0419](/solutions/0419/) — Look and Say Sequence
- ● [0425](/solutions/0425/) — Prime Connection
- ○ [0442](/solutions/0442/) — Eleven-free Integers
- ○ [0467](/solutions/0467/) — Superinteger
- ● [0473](/solutions/0473/) — Phigital Number Base
- ○ [0474](/solutions/0474/) — Last Digits of Divisors
- ● [0506](/solutions/0506/) — Clock Sequence
- ○ [0508](/solutions/0508/) — Integers in Base $i-1$
- ● [0520](/solutions/0520/) — Simbers
- ○ [0524](/solutions/0524/) — First Sort II
- ● [0529](/solutions/0529/) — $10$-substrings
- ○ [0538](/solutions/0538/) — Maximum Quadrilaterals
- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0558](/solutions/0558/) — Irrational Base
- ● [0571](/solutions/0571/) — Super Pandigital Numbers
- ○ [0592](/solutions/0592/) — Factorial Trailing Digits 2
- ○ [0603](/solutions/0603/) — Substring Sums of Prime Concatenations
- ● [0637](/solutions/0637/) — Flexible Digit Sum
- ○ [0655](/solutions/0655/) — Divisible Palindromes
- ○ [0660](/solutions/0660/) — Pandigital Triangles
- ○ [0676](/solutions/0676/) — Matching Digit Sums
- ● [0684](/solutions/0684/) — Inverse Digit Sum
- ○ [0685](/solutions/0685/) — Inverse Digit Sum II
- ● [0698](/solutions/0698/) — 123 Numbers
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0711](/solutions/0711/) — Binary Blackboard
- ○ [0714](/solutions/0714/) — Duodigits
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0725](/solutions/0725/) — Digit Sum Numbers
- ● [0731](/solutions/0731/) — A Stoneham Number
- ● [0749](/solutions/0749/) — Near Power Sums
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0778](/solutions/0778/) — Freshman's Product
- ● [0788](/solutions/0788/) — Dominating Numbers
- ○ [0805](/solutions/0805/) — Shifted Multiples
- ● [0808](/solutions/0808/) — Reversible Prime Squares
- ○ [0817](/solutions/0817/) — Digits in Squares
- ○ [0831](/solutions/0831/) — Triple Product
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ○ [0865](/solutions/0865/) — Triplicate Numbers
- ● [0885](/solutions/0885/) — Sorted Digits
- ○ [0893](/solutions/0893/) — Matchsticks
- ○ [0912](/solutions/0912/) — Where are the Odds?
- ○ [0924](/solutions/0924/) — Larger Digit Permutation II
- ○ [0925](/solutions/0925/) — Larger Digit Permutation III
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0932](/solutions/0932/) — $2025$
- ○ [0954](/solutions/0954/) — Heptaphobia
- ● [0963](/solutions/0963/) — Removing Trits
- ● [0974](/solutions/0974/) — Very Odd Numbers
- ● [0990](/solutions/0990/) — Addition Equations
- ○ [1003](/solutions/1003/) — Lonely Singles
- ○ [1004](/solutions/1004/) — Balanced Integer
- ● [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
