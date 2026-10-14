<!-- tags: [string-slicing] -->
<!-- status: final 2026-10-14T17:35Z -->
# string slicing

[Slicing](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations) is
`s[i:j]` and `s[i:j:k]`: one expression that takes a contiguous run, or a strided one, out of
a sequence. Many Euler puzzles describe a number by what happens to its *decimal digits*: rotate
them, reverse them, chop one off the end, read a window, replace one. Once the number is a string
from `str(n)`, every one of those operations is a single slice. These solutions use it for that
reason. The statement is about how the number is written, so they work on how it is written. This
page is part of the language-idioms series, so it also covers what each slice turns into in C, and
the point where slicing stops being the convenient choice and becomes the better algorithm.

## The idea

Five shapes cover nearly every use here. All of them live in public solutions, so the code can be
quoted:

| Operation | Slice | Problem |
| --- | --- | --- |
| rotate left by $i$ | `s[i:] + s[:i]` | 35 Circular Primes |
| reverse | `s[::-1]` | 36, 55 palindromes |
| truncate from either end | `s[i:]`, `s[:i]` | 37 Truncatable Primes |
| fixed-width window | `s[:w]` | 13 Large Sum |
| choose a digit class | `"0123456789"[:k]`, `str.replace` | 51 Prime Digit Replacements |

**Rotation is two slices joined.** Problem 35 needs every cyclic shift of a prime's digits:

```python
str_num: str = str(num)
return {num} if len(str_num) == 1 else {int(str_num[i:] + str_num[:i]) for i in range(1, len(str_num) + 1)}
```

That line is the definition of a rotation, with nothing to translate. The result is a set, so a
repunit-style prime like 11 gives one rotation, not two. That costs nothing, and it removes a
duplicate membership test.

**Reversal is `[::-1]`, and a palindrome is `s == s[::-1]`.** Problem 55 runs reverse-and-add on
one line:

```python
number += int(str(number)[::-1])
if str(number) == str(number)[::-1]:
    return False
```

Problem 36 uses reversal to *build* palindromes, which is the better direction. It mirrors each
left half (`digits_str + digits_rev`, optionally with a middle digit between them), so only about
$\sqrt{N}$ candidates are generated, instead of filtering all $N$ numbers. It then checks the
base-2 side with the same slice on `bin(number)[2:]`, the binary digits with the `0b` prefix sliced
away. The private problems lean on the same move: 125 and 808 are reversal tests over
sums of squares and over squares of primes; 206 uses the *strided* form, `str(m * m)[::2]`, to read
every other digit of a square against a digit pattern (the [extended
slice](/topics/technique/extended-slice) page covers striding properly).

**Truncation is a prefix and a suffix.** Problem 37 asks for primes that stay prime as digits are
removed from the left or from the right. Slicing gives both families in a single comprehension,
`(prime[i:], prime[:i]) for i in range(1, len(prime))`. The solution then stores the primes it has
already seen *as strings*, so each truncation is a set lookup with no `int()` round-trip. The
generator yields primes in increasing order, so every truncation is already in the set by the time
it is needed.

**A window turns a huge number into a small one.** Problem 13 sums a hundred 50-digit numbers and
wants only the leading ten digits. It slices each number to its first eleven characters, adds those,
and slices the total back to ten. Read numerically, `s[:w]` is $\lfloor n / 10^{\ell - w}\rfloor$.
As text it is free, and it never needs the full-width number.

**Where slicing outgrows arithmetic.** Each of these has an arithmetic twin, and the twin scales
differently. I timed both on this machine:

| Operation | slice | `divmod` loop |
| --- | --- | --- |
| reverse a 6-digit int | 0.13 µs | 0.32 µs |
| reverse a 50-digit int | 0.29 µs | 4.3 µs |
| all rotations of a 6-digit int | 0.89 µs | 0.53 µs |

For reversal, the slice wins, and the gap grows with the length of the number. The arithmetic loop
is $d$ interpreted iterations, and on a big integer each `divmod(n, 10)` is itself $O(d)$. The
`str` → slice → `int` round trip is three passes in C. Problem 55's iterates grow to 29 digits
under the default limits, well into the range where the gap has opened. Rotation goes the other way. One rotation is a single
`divmod(m, 10**(d-1))` and a multiply, while the slice version builds two substrings, a
concatenation and a parse. So the arithmetic version wins, as long as you are willing to carry
the power of ten. Problem 51 is where slicing pulls clearly ahead. "Replace every 3 in this
number with a 7" has no tidy arithmetic form, because you would need the positions of the 3s
first. `str(prime).replace(replaced, replacement)` is just that sentence in code. The private problem 336
goes all the way into string algebra. Its train-car arrangements are built level by level from
reversed prefixes and suffixes (`t[::-1][:p] + first + t[:m - p]`). That slice is the
recurrence, and there is no number underneath it to fall back to.

## The counterpart in C

C has no slice syntax, but a `char` buffer from [`snprintf`](/topics/technique/snprintf) supports
most of the operations directly, and some of them more cheaply than Python.

- **A suffix is free.** `buf + i` *is* `s[i:]`: a pointer into the same storage, with no copy. Only a
  prefix needs work, because the string has to end somewhere. Problem 37's C copies with
  `strncpy(left, buf, i); left[i] = '\0';`. The alternatives are comparing with `strncmp`, or
  printing with `%.*s`. See [C string handling](/topics/technique/c-string-handling).
- **Reversal is an index, not a buffer.** Problem 55's C never builds a reversed copy. Its
  `bignum_add_reverse` adds `digits[i] + digits[n - 1 - i]` directly, and its palindrome test
  compares the same mirrored pairs. Problem 36's C does build `digits_rev`, but only because it
  goes on to `snprintf` the halves together, following the Python.
- **Rotation is two copy loops.** Problem 35's C writes `str_num[i:]` and then `str_num[:i]` into a
  scratch buffer and calls `atoi`. The Python slice comment sits above the loop for that reason: the
  loops *are* that slice, written out.
- **A window over a number that does not fit is the input format.** Problem 13's C cannot
  produce the 50-digit integer, so it never tries. It reads the first $w+1$ characters of each line
  as digit columns, adds column-wise, and propagates carries. The Python slice and the C column sum
  do the same thing. Only C has no other option.

In both directions, the language's natural tool decides how efficient the code is. A Python slice
always allocates a new string, while a C "slice" is a pointer and a length. So the C translation is
often the leaner one, provided the buffers are sized and terminated correctly
([parity across languages](/topics/takeaway/parity-across-languages)).

## How to reason about it

- **Slice when the statement talks about digits; use arithmetic when it talks about values.**
  Rotations, truncations, palindromes and digit replacements are all statements about how a number
  is written. Divisibility, residues and bounds are statements about its value. The two styles mix
  freely, but say which one each line uses.
- **Keep the string form if you will look it up again.** Problem 37 stores primes as strings
  because every truncation it tests is a string. Converting each piece back to `int` just to look
  it up wastes both passes.
- **Watch the edge cases slicing hides.** `int("0113")` quietly drops the leading zero, so a
  rotation of a number that contains a 0 can come out shorter than the original. Problem 35
  excludes 0 anyway: any rotation that ends in 0 is even. Single-digit inputs make
  `s[i:] + s[:i]` degenerate, which is why problem 35 special-cases `len == 1`. A window also drops
  the tail, and the tail carries: 100 discarded tails can add up to almost 100 units in the last
  kept place. One guard digit is therefore a safety margin that happens to hold for problem 13's
  data, not a proof. For a guarantee, keep $\lceil \log_{10} N \rceil$ guard digits and check that
  the kept prefix does not end in a run of 9s.
- **Generate rather than filter.** Reversal is most valuable when you use it to *build* (problem
  36's mirrored halves), not only to test. Building gives you $\sqrt{N}$ candidates instead of
  checking $N$.
- **Measure before you replace a slice with arithmetic.** Arithmetic reversal is slower in
  Python, while arithmetic rotation is a bit faster. Neither difference matters next to the
  algorithmic choice around it.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0013](/solutions/0013/) — Large Sum
- ● [0035](/solutions/0035/) — Circular Primes
- ● [0036](/solutions/0036/) — Double-base Palindromes
- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0051](/solutions/0051/) — Prime Digit Replacements
- ● [0055](/solutions/0055/) — Lychrel Numbers
- ● [0125](/solutions/0125/) — Palindromic Sums
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0336](/solutions/0336/) — Maximix Arrangements
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
