<!-- tags: [snprintf] -->
<!-- status: final -->
# snprintf

[`snprintf`](https://en.cppreference.com/w/c/io/fprintf) is how a C solution turns a number into
text, and in this repository it does two entirely different jobs. Every C solution uses it once at
the end, because the runner's `solve()` returns a `const char *` and something has to render the
answer — 336 of the 366 C files here contain the call for that reason alone. The problems below are
the ones where it does *algorithmic* work: where the Python sibling wrote `str(n)` and indexed,
sliced or reversed the result, and the port needs the same digit string. That second job is the one
worth understanding, because C gives you no `str()` and `snprintf` is the closest thing.

## The idea

```c
int snprintf(char *s, size_t n, const char *fmt, ...);
```

It makes two promises, and the second is the one people forget. It writes **at most `n` bytes
including the terminating NUL** — so it never overruns the buffer, and when `n > 0` the result is
always NUL-terminated. And it returns **the length it *would* have written**, excluding the NUL —
not the length it actually wrote. Both halves are useful:

- Truncation is detectable, and only via the return. The idiom is `if (ret < 0 || (size_t)ret >=
  size)`, with the cast because `ret` is a signed `int` and `sizeof` is unsigned. The runner header
  itself does exactly this when it builds a resource path:

  ```c
  int pn = snprintf(path, sizeof(path), "%s/resources/%.*s", dirname(prog), (int)name_len, name_start);
  if (pn < 0 || (size_t)pn >= sizeof(path)) return NULL;
  ```

- The return value is a free digit count. Problem 32 needs to know whether `a`, `b` and `c`
  concatenate to exactly nine digits, and gets the length from the same call that produces the
  string:

  ```c
  char buf[20];
  int len = snprintf(buf, sizeof(buf), "%d%d%d", a, b, c);
  if (len != 9) return 0;
  ```

  No `strlen`, no separate digit-counting loop. Problems 125, 238 and 845 use the return the same
  way — to size or bound something before touching the characters.

The older [`sprintf`](https://en.cppreference.com/w/c/io/fprintf) has neither promise: no bound, and
its return tells you the damage only after it has been done. It survives here in exactly one place —
the hand-rolled [bignum](/topics/technique/arbitrary-precision-arithmetic) printers, which emit the
top limb bare and every following one zero-padded (`"%09llu"`) so the concatenation *is* the decimal
expansion — and only because those buffers are sized from the limb count first, so overflow is
arithmetically impossible.

## `str(n)` has no C equivalent

This is the whole reason the tag exists. In Python, `str(n)` gives you a random-access sequence of
digits and the rest is slicing. In C you format into a `char` array and index it, converting back
with `- '0'`. The ports below are that translation, four ways:

| Python | C | seen in |
| --- | --- | --- |
| `str(n)[i]` | format, then `buf[i] - '0'` | 40 |
| `str(n)[::-1]` | format, then accumulate `r = r*10 + (buf[i]-'0')` backwards | 808 |
| `str(n)` split at every position | format once, recurse over split points on the buffer | 719 |
| `f"{a}{b}{c}"` | one call, `"%d%d%d"` | 32, 93 |

Problem 40 is the cleanest: it computes which number of Champernowne's constant contains the
requested digit, then formats it and indexes — three lines that replace an entire digit-extraction
loop.

```c
char buf[32];
snprintf(buf, sizeof(buf), "%lld", number);
return buf[digit_in_number] - '0';
```

Problem 719 shows the shape at scale: each candidate square is formatted **once**, and the
backtracking search over its split points then works on that buffer, never re-formatting. Problem
808 formats a square only to walk it backwards. Problem 34 formats a digit-factorial sum so a
membership test can ask which digits it contains. Problem 17 is the outlier — it formats *words*,
not digits, composing `"%s hundred and %s"` from lookup tables into a per-number cache.

The concatenate-and-test pattern deserves one warning. Problem 93 writes four values into
`char best_digits[5]` with `"%d%d%d%d"`, which fits exactly: four digits plus the NUL. That is
correct because the four values are provably single digits — the bound comes from an invariant of
the data, not from anything the format string enforces. Feed the same call a two-digit value and it
truncates silently, and you will not notice unless you check the return.

## Formatting the answer

The runner's contract is explicit about lifetime:

> The returned pointer is owned by `solve()` and must stay valid until the next call — return a
> string literal or write into a `static` buffer; do not return a per-call malloc'd buffer (it would
> leak across `--runs`).

Hence the one-line tail that ends nearly every C solution here:

```c
static char answer[32];
...
snprintf(answer, sizeof answer, "%lld", total);
return answer;
```

`static` because a plain local array dies when `solve()` returns and the pointer dangles;
32 bytes because the widest `long long` is 19 digits plus a sign and a NUL. Two solutions in the set
below — 151 and 93 — `malloc` their buffer instead and never free it, which is harmless at 32 bytes
a run but is exactly what the header asks you not to do.

Match the specifier to the type, and check it yourself: the build line is `gcc -O2 -Werror` with no
`-Wall`, and gcc's format checking rides on
[`-Wformat`](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html), which `-Wall` enables. A
`%d` handed a `long long` is undefined behaviour that this toolchain will compile without a word.

| result type | specifier |
| --- | --- |
| `long long` / `unsigned long long` | `%lld` / `%llu` |
| `size_t` | `%zu` |
| GMP `mpz_t` | `gmp_snprintf` with `%Zd` |
| fixed decimal places | `%.6f`, `%.8f` |
| significant digits | `%.10g` |

Problems 151 and 226 are the fixed-decimal cases: their answers are decimal fractions, `%.6f` and
`%.8f` against the Python siblings' `f"{result:.6f}"` and `f"{total:.8f}"`. Both glibc and CPython
round the exact binary value of the `double` correctly, so the two strings agree — the risk is not
the formatter but the value. If the C and Python arithmetic differ by one
[ULP](https://en.wikipedia.org/wiki/Unit_in_the_last_place) and the true result sits near a rounding
boundary, the last printed digit flips and the C port fails a test case the Python one passes.
When the answer *can* be kept exact, keep it exact and place the decimal point yourself: problem 239
formats a scaled integer as `"%lu.%0*lu"` and problem 252 as `"%lld.%d"`, neither of which can round
at all. (The `*` there takes the field width as an argument — the way to parameterise precision
without building the format string.)

## How to reason about it

**It is a runtime interpreter, so keep it out of hot loops.** Every call parses the format string
and runs the full stdio conversion machinery — hundreds of nanoseconds, against a couple of
nanoseconds for a `% 10` and a `/= 10`. Problem 206 says so in its own comment: it tests whether a
square matches the pattern `1_2_3_4_5_6_7_8_9` by reading digits with `% 10` and skipping the free
ones with `/= 100`, "no string work", across a few hundred thousand candidates. Problem 719 goes the
other way and formats every candidate — but only after a mod-9 filter has discarded about 78% of
them first. That pairing is the one to imitate: cheap arithmetic filter, then the expensive format
on what survives (see [order checks by cost](/topics/takeaway/cheap-checks-first)).

**Reach for it when the question is genuinely about the digit string.** Splitting at arbitrary
positions, reversing, indexing the *k*-th digit from the left, testing a permutation with `strcmp` —
these are natural over characters and awkward over arithmetic, because they need the digit count up
front and left-to-right access, and division gives you neither. Counting digits, summing them,
testing divisibility, matching a fixed positional pattern — these are natural over arithmetic. The
tagged problems split cleanly along that line.

**`sizeof` only works on arrays.** `snprintf(buf, sizeof buf, ...)` is right where `buf` is a local
array and silently wrong where it is a `char *` parameter, which measures the pointer instead. A
function that writes into a caller's buffer must take the size as an argument — problem 17's word
formatter does exactly that.

**Appending is where the bound gets lost.** The accumulate idiom, `pos += snprintf(out + pos,
sizeof out - pos, ...)`, is correct only while nothing truncates: one truncated call pushes `pos`
past the end, and `sizeof out - pos` then underflows to an enormous `size_t` that defeats the bound
entirely. It appears here in problems 103 and 175, safe in both because the buffers are sized from
the data first. If you cannot prove the size, check each call's return before adding it.

**Never format into the buffer you are reading from.** `snprintf(buf, n, "%s!", buf)` is undefined
behaviour, not a clever in-place append.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0032](/solutions/0032/) — Pandigital Products
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0040](/solutions/0040/) — Champernowne's Constant
- ● [0044](/solutions/0044/) — Pentagon Numbers
- ● [0063](/solutions/0063/) — Powerful Digit Counts
- ● [0093](/solutions/0093/) — Arithmetic Expressions
- ● [0128](/solutions/0128/) — Hexagonal Tile Differences
- ● [0151](/solutions/0151/) — A Preference for A5
- ● [0184](/solutions/0184/) — Triangles Containing the Origin
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0206](/solutions/0206/) — Concealed Square
- ● [0226](/solutions/0226/) — A Scoop of Blancmange
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0808](/solutions/0808/) — Reversible Prime Squares

<!-- /problems -->
