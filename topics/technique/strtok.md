<!-- tags: [strtok] -->
<!-- status: final -->
# strtok

Three early problems give you a data file instead of a number. 22 has a file of five thousand
quoted first names on one line, 42 has a similar file of English words, and 54 has a thousand
lines of ten poker cards each. Before any of them can do arithmetic, it has to turn bytes into
tokens. In Python that is `text.split(",")` and you never think about it again. C has no
`split`, so all three C solutions use the standard library's tokeniser,
[`strtok`](https://en.cppreference.com/w/c/string/byte/strtok), or its reentrant form
[`strtok_r`](https://man7.org/linux/man-pages/man3/strtok_r.3.html). This page is part of the
language-idioms series. It covers how the tokeniser works, why these solutions use it, the two
things it gets wrong (quotes and nesting), and what the Python versions write instead.

## The idea

`strtok(s, delims)` is a cursor over a writable string. The first call passes the string, and
every later call passes `NULL` to mean "continue where you stopped". Each call does three things:

1. it skips any run of characters from `delims`;
2. it scans forward to the next delimiter and **overwrites it with `'\0'`**;
3. it returns a pointer to the start of the token, and remembers the position after the zero.

When nothing is left it returns `NULL`, which gives the standard loop:

```c
char *tok = strtok(text, ",");
while (tok) {
    /* use tok */
    tok = strtok(NULL, ",");
}
```

Three properties follow, and each one matters in the solutions below.

- **It allocates nothing.** Each token is a pointer *into the original buffer*, which now holds a
  zero where each delimiter was. Splitting a 46 KB file costs one pass and no `malloc`s. The tokens
  also stay valid exactly as long as the buffer does: free the text and every token is a dangling
  pointer.
- **It writes to its input.** The buffer must be writable. A file read into a `malloc`ed buffer
  is fine. A string literal is not: `strtok("A,B", ",")` is undefined behaviour, and usually
  crashes.
- **It drops empty fields.** A run of delimiters counts as one separator, and a leading or
  trailing delimiter produces no token. `"A,,B"` gives two tokens, not three. For whitespace this
  is what you want. For a CSV column with empty cells it silently shifts every later field.

The delimiter argument is a *set* of characters, not a string to match. `" \r\t"` means "space,
carriage return or tab". That makes it easy to absorb Windows line endings: list `'\r'` among the
delimiters and it never reaches a token.

## Three files, three uses

**22: tokens as pointers into the file.** The C solution reads the whole file with the runner's
`get_text_file`, counts the commas to size an array (`commas + 1` is an upper bound, since
`strtok` can only return fewer tokens), and fills the array with the pointers `strtok` returns.
Then it calls `qsort` with `strcmp` on those pointers. No name is copied. The array of `char *`
is an index into the file buffer, and the buffer is freed only after the scoring loop has used
the names. This is the strongest argument for `strtok`: in-place tokenising and pointer sorting
give C a split-and-sort with no allocation per name.

**42: the same split, with a cleanup copy.** 42's C uses `strtok_r` on `","` and then copies
each token into a local `char word[256]`, dropping quotes, spaces, `'\r'` and `'\n'` as it goes.
The `strtok_r` isn't needed here, because there is only one tokeniser, but it does no harm and
it is the right default. The copy has a guard, `wi < 255`, that silently truncates a longer
word. That can't happen with these words, but it is a limit that would hide a wrong input rather
than report it.

**54: two tokenisers, one inside the other.** 54 splits the file into lines on `"\n"`, and each
line into ten cards on `" \r\t"`. This is where reentrancy matters. `strtok` keeps its "where I
stopped" pointer in hidden static state, and there is only one. If the inner loop called
`strtok(line, " ")`, it would overwrite that state, and the outer `strtok(NULL, "\n")` would
continue from the end of the *line*, not the file. The loop would stop after the first hand,
with no error. `strtok_r` takes the state as a third argument, `char **saveptr`, so each loop
has its own:

```c
char *line = strtok_r(content, "\n", &saveptr);
while (line) {
    char *tok = strtok_r(line, " \r\t", &inner_save);   /* separate cursor */
    ...
    line = strtok_r(NULL, "\n", &saveptr);
}
```

54 also copies each line into `char line_copy[256]` before tokenising it. Like the `strdup` in
105, the copy isn't needed. The outer tokeniser has already put a zero at the end of the line, so
the inner one can only write inside the line, and that part of the buffer is never read again.
Tokenising `line` directly is safe.

The rule is short: **use `strtok_r` everywhere**. Plain `strtok` is safe only if no function
called inside the loop tokenises too, and that includes library code you didn't write. Its
static state also makes it unsafe across threads. `strtok_r` is POSIX, not ISO C. C11's optional
Annex K adds `strtok_s`, which almost no C library ships, and MSVC calls the same function
`strtok_s` with `strtok_r`'s signature.

## The quoting pitfall

`strtok` knows delimiters and nothing else. The names in 22 and the words in 42 are written as
`"MARY","PATRICIA",…`, and the tokeniser returns `"MARY"` *with its quotes*. A CSV parser would
remove them, and would also keep a quoted comma (`"SMITH, JR"`) as part of the field. `strtok`
does neither, and the solutions handle the quotes in three ways:

- **22 leaves them on and relies on the byte order.** The scorer skips `'"'`, so the quotes add
  nothing to a name's value. The sort compares the quoted strings unchanged, and it gives the
  right order only because `'"'` (0x22) sorts below every letter. In `"AB"` against `"ABC"`, the
  closing quote of the shorter name meets `C` and loses, so the prefix still comes first. That is
  correct, but only by an accident of ASCII. With a closing delimiter above `'Z'` the order would
  be wrong.
- **42 strips them in its copy**, along with whitespace, so the scorer sees clean words.
- **54 has no quotes.** Its fields are separated by whitespace, which is the case `strtok` was
  designed for.

The same check applies to the last field. Neither file ends with a newline, so the last token
is `"ALONSO"` and not `"ALONSO"\n`. 22's scorer skips only quotes and spaces, so if the file had a
trailing newline it would add `'\n' - 64` to the last name's score, and the total would be wrong
with no error. 42's copy removes `'\r'` and `'\n'` and doesn't have this problem. Adding `"\r\n"`
to 22's delimiter set would remove the problem at no cost.

If a file really uses CSV quoting, with commas inside fields or doubled `""` quotes, `strtok` is
the wrong tool. Use a small state machine that tracks whether you are inside quotes, or a CSV
library.

## The Python counterpart

Python's `str.split` has two forms, and they behave differently.

| C | Python | Empty fields | Where |
|---|---|---|---|
| `strtok(s, ",")` | `s.split(",")` | C drops them, Python keeps `''` | 22, 42 |
| `strtok_r(s, " \r\t", …)` | `s.split()` | both drop them; runs of whitespace are one separator | 54 |
| `strtok_r(s, "\n", …)` + skip blank | `s.splitlines()` + `if (cards := line.split())` | Python keeps blank lines, the walrus skips them | 54 |
| copy and skip `'"'` | `word.strip('"')` | | 22, 42 |
| hand-written quote state machine | `csv.reader` | handles quoted commas and `""` | none needed |

`s.split()` with no argument is the closest match to `strtok`: it splits on any whitespace,
treats a run as one separator, and ignores leading and trailing whitespace. `s.split(",")` with an
argument is *not* `strtok`. It returns a field for every separator, so `"A,,B"` gives
`['A', '', 'B']`. That is the right behaviour for CSV, and it is why a stray trailing comma shows
up in Python as an empty string where C would skip it.

The Python versions are also missing two of C's problems. There is no hidden cursor, so
reentrancy doesn't come up: `split` returns a list and keeps no state. And there is no buffer
lifetime to manage, because each token is its own `str`. The cost is a new object per token
(five thousand small strings in 22, where C makes none), which doesn't matter at this size.
Python inherits the quoting problem unchanged. 22 and 42 both write `word.strip('"')` because
`split(",")` doesn't understand quotes either. `csv.reader` does: `next(csv.reader([text]))`
returns the names without quotes and would handle a quoted comma.

The practical rules for both languages are the same. Decide what the delimiters are, including
`'\r'` and `'\n'`. Decide whether an empty field means something. Remove quoting in one place, not
in the scorer. In C, add two more: tokenise a writable buffer that outlives the tokens, and use
`strtok_r` with one `saveptr` for each loop.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0022](/solutions/0022/) — Names Scores
- ● [0042](/solutions/0042/) — Coded Triangle Numbers
- ● [0054](/solutions/0054/) — Poker Hands

<!-- /problems -->
