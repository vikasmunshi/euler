<!-- tags: [c-string-handling] -->
<!-- status: final 2026-10-14T17:57Z -->
# C string handling

C has no string type. A "string" is a `char` array that ends at the first zero byte, and every
operation on it is a library call that walks the bytes looking for that zero. The solutions here
deal with text at both ends of a problem. On the way in they parse it: a triangle of numbers
(18), a resource file of comma-separated sets (105), an expression like `28433 × 2^7830457 + 1`
(97). On the way out they produce it, because `runner.h` asks `solve()` for its answer as a string:
a six-digit modal string (84), a 128-bit integer that `printf` cannot format (137), a big number
held in base-10⁹ limbs (138). In between, some solutions compute *with* text: 38 builds its
concatenated products by gluing decimal strings together, and 84 finds Monopoly squares by name
prefix. This page is part of the language-idioms series. It covers the idiom, why these
solutions use it, and how it looks in Python.

## The idea

A [C string](https://en.wikipedia.org/wiki/C_string_handling) is a pointer to its first byte.
The length isn't stored anywhere, so `strlen` costs O(n), and the size of the buffer behind the
pointer isn't stored either, so no function can check that a write fits. The calls these
solutions use fall into five groups:

| Job | Calls | Watch out for |
|---|---|---|
| Compare | `strcmp`, `strncmp(s, prefix, len)` | `strcmp` returns 0 on a match, so `if (strcmp(a, b))` means *different* |
| Search | `strchr`, `strrchr`, `strstr` | they return a pointer into the original, or `NULL` |
| Split | `strtok`, `strtok_r` | they **write** `'\0'` over each delimiter, so the input must be writable |
| Convert | `atoi`, `atoll`, `strtoll`; `snprintf`, `sprintf` | `atoi` reports no errors; `sprintf` checks no bounds |
| Build | `strcpy`, `strcat`, `memcpy`, `strdup` | the destination has to be big enough, and nothing checks it |

[`snprintf`](https://en.cppreference.com/w/c/io/fprintf) is the one call that is safe by design.
It takes the buffer size, always writes the terminating zero, and returns the length it *would
have* written, so you can detect truncation (`n >= size`) and advance a write position
(`pos += n`). `runner.h` uses it this way to build resource paths, and most solutions use it in
the `snprintf(_answer, sizeof _answer, "%lld", …)` line that returns the answer.

## Parsing: tokenising in place

18 shows the full cost of splitting text in C. Python does it in one line,
`[[int(num) for num in line.split(" ")] for line in text.splitlines()]`. C needs a function of
about sixty lines. It counts the newlines to size the row array. It copies the triangle with
`memcpy`, because the text is a string literal, and `strtok` writing zeros into a literal is
undefined behaviour. For each line it then `strdup`s the line and tokenises it to count the
numbers, frees that copy, `strdup`s it again, and tokenises it a second time with `atoi` to fill
the row. The two passes exist because C needs the row length before it can allocate the row.
Python's `list` grows as it goes, so it never has to know.

[`strtok`](https://en.cppreference.com/w/c/string/byte/strtok) keeps its position in hidden static
state, so two tokenisers can't be interleaved: an inner `strtok` on the fields of a line
clobbers the outer one splitting the lines. 105 is the case where this matters. It splits the
file into lines and each line into numbers, and it uses
[`strtok_r`](https://man7.org/linux/man-pages/man3/strtok_r.3.html), which keeps the position in
a `saveptr` the caller owns, one per tokeniser. That is what keeps the two loops apart. The
`strdup` of each line, which a comment credits with protecting the outer state, does no work: the
outer `strtok_r` has already ended the line with a zero, and the inner one writes only inside it.
The two other things to notice in 105 are that `strtok_r` treats `"\n\r"` as one delimiter set,
which handles Windows line endings without special code, and that the fixed `elements[20]` stops
reading at twenty values without saying so. That limit holds for this input, but it is a silent
truncation.

97 parses a mathematical expression. It reassembles its arguments into one buffer with `strcat`
(the runner may receive the expression as several words), then lets `atoll` read the leading
coefficient (it stops at the first non-digit) and finds the exponent with `strchr(expr, '^') + 1`.
That is a neat use of the conversion functions' "parse a prefix" behaviour. The weakness is
`char expr[256]` filled by unchecked `strcat`: a longer argument overflows the stack. Python's
version, `prime.split()` and an index, can't go wrong that way.

## Building: concatenation and its two costs

38's concatenated product, `x·1 ‖ x·2 ‖ … ‖ x·n`, is the textbook case for string building. The
C version formats each product into a scratch buffer with `snprintf`, `strcat`s it onto `buf`, and
parses the result with `atoll`. It works, but it has the two faults of `strcat`:

- **It is quadratic.** Every `strcat` scans the destination from the start to find its end. This
  is [Schlemiel the painter](https://en.wikipedia.org/wiki/Joel_Spolsky#Schlemiel_the_Painter's_algorithm):
  with nine-digit results it costs nothing, but the shape is wrong.
- **It doesn't check the bound.** `buf[64]` is safe only because the problem limits the result
  to nine digits.

The fix for both is to keep a write position and let `snprintf` advance it:

```c
size_t pos = 0;
for (int i = 1; i <= n && pos < sizeof buf; i++)
    pos += (size_t)snprintf(buf + pos, sizeof buf - pos, "%d", i * x);
```

138 already does this when it prints its big number: `pos += sprintf(buf + pos, …)` for each
limb. It uses `sprintf` rather than `snprintf`, and is safe only because it allocates the
worst-case length up front. The format string is the interesting part. Limbs are stored in base
10⁹, so the most significant limb prints with `"%u"` and every other limb with `"%09u"`. Without
the zero padding, a limb of `7` would print as `7` instead of `000000007`, and the number would
silently lose digits from the middle. 137 has the opposite problem: `unsigned __int128` has no
`printf` conversion at all, so it writes the digits itself. It takes `v % 10` into a scratch
array, least significant digit first, then copies them in reverse into the caller's buffer and
adds the terminating zero. That is the standard way to format an integer type the library
doesn't know.

## Strings as keys

84 keeps the Monopoly board as an array of 40 string literals (`"GO"`, `"CC1"`, `"R2"`, …) and
asks questions of it by name. `strcmp(name, "G2J") == 0` tests for an exact square,
`strncmp(name, "CC", 2) == 0` tests for any Community Chest, and `forward_seek` finds the next
railway by comparing each square against the prefix `"R"`. This mirrors the Python solution
closely (`==` and `str.startswith`) and keeps the card rules readable. The price is that
`name_index("C1")` is a linear scan with string compares, repeated for every card in every
transition. That's acceptable for a 40-square board, but the C habit is to resolve names to
indices once, in an `enum` or a few `static int`s, as the solution already does for `JAIL`.

84 and 138 also both return their answer in a buffer from `malloc`. `runner.h` says the returned
string must be a literal or a `static` buffer: the harness `strdup`s it and never frees the
original, so every `--runs` iteration leaks one block. The `static char _answer[32]` pattern used
by 18, 38, 97, 105 and 137 is what the contract asks for. For 138 the static buffer has to be
sized to the worst case, about `9 × BIGINT_MAX_DIGITS` bytes.

## The counterpart in Python

In Python, text is an immutable `str` with its length stored, and parsing and formatting are
methods on it:

| C | Python | Where |
|---|---|---|
| `strtok` / `strtok_r` loop + `atoi` | `line.split(",")`, `map(int, …)` | 18, 105 |
| `strchr(expr, '^')` + `atoll` | `split()`, slicing, `int()` | 97 |
| `snprintf` + `strcat` into a fixed buffer | `"".join(str(i * x) for …)` | 38 |
| `strcmp(…) == 0`, `strncmp(s, p, len) == 0` | `==`, `s.startswith(p)` | 84 |
| `snprintf(buf, 7, "%02d%02d%02d", …)` | `"".join(f"{sq:02d}" for sq in …)` | 84 |
| hand-written `__int128` → decimal | `str(n)` | 137 |
| base-10⁹ limbs, `"%u"` then `"%09u"` | `str(n)`, since `int` is arbitrary precision | 138 |

The last two rows are the biggest difference. In C, an answer wider than 64 bits needs its own
formatting code. In Python it needs `str()`. The C traps (overflowed buffers, a missing terminating
zero, tokeniser state, leaked results) have no Python equivalent. Python has one cost of its own:
`str` is immutable, so `s += piece` in a loop can copy the whole string each time. The fix is the
same as in C: collect the pieces and `"".join` them once, which is what 38 and 84 do.

## How to reason about it

- **Know who owns every buffer and how big it is.** C won't track either for you. Pass the size
  alongside the pointer, and prefer calls that take it (`snprintf`, `strncmp`).
- **Build with `snprintf` and a write position**, never `strcat` in a loop. Check `n >= size`
  where truncation is possible.
- **Tokenise a writable copy, with `strtok_r`.** Never pass a string literal to `strtok`. Nest
  tokenisers only with separate `saveptr`s.
- **Use `strtol`/`strtoll` where input can be wrong.** `atoi` is fine for trusted test data, but it
  can't report garbage or overflow.
- **Zero-pad every limb after the first** when you print a big number in base 10ᵏ, and write the
  digit loop yourself for types `printf` doesn't support.
- **Return the answer in a `static` buffer**, as the runner contract requires, sized for the
  longest answer.
- **In Python, use `split`, `join` and f-strings**, and build strings by joining pieces rather
  than with `+=` in a loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0038](/solutions/0038/) — Pandigital Multiples
- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0097](/solutions/0097/) — Large Non-Mersenne Prime
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0137](/solutions/0137/) — Fibonacci Golden Nuggets
- ● [0138](/solutions/0138/) — Special Isosceles Triangles

<!-- /problems -->
