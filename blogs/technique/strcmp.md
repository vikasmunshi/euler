<!-- tags: [strcmp] -->
<!-- status: final 2026-10-14T18:03Z -->
# strcmp

C has no string type, so it has no string comparison operator either. `a == b` on two `char *`
compares two addresses, and `a < b` compares where they sit in memory. To compare *contents* you
call [`strcmp`](https://en.cppreference.com/w/c/string/byte/strcmp). Two early C solutions use
it, for two different jobs. 22 uses it as an **ordering**: it is the comparator `qsort` needs to
put five thousand names in alphabetical order. 52 uses it as an **equality test**: it checks
whether two numbers have the same sorted-digit key. This page is part of the language-idioms
series. It covers what `strcmp` actually promises, how it plugs into `qsort`, why 52 can compare
numbers by comparing strings, and what the Python versions write instead (mostly `sorted` and
`==`, with no comparator in sight).

## The idea

`strcmp(a, b)` walks both strings together, one byte at a time, and stops at the first position
where they differ or where `a` ends. It returns an `int` whose **sign** is the answer:

- negative if `a` sorts before `b`,
- zero if they are equal,
- positive if `a` sorts after `b`.

Only the sign is specified. glibc may return `-1`, or it may return the difference of the two
bytes, and code that tests `== -1` is relying on one implementation. The bytes are compared as
`unsigned char`, so the order is the order of the byte values. For ASCII text that is the
[lexicographic order](https://en.wikipedia.org/wiki/Lexicographic_order) on character codes:
digits before uppercase before lowercase, and a prefix before any longer string that starts with
it, because the prefix's terminating `'\0'` is smaller than any other byte.

Two properties follow.

- **It is a three-way comparison.** One call tells you less, equal or greater, which is exactly
  the contract a sort comparator has. That is why `strcmp` and `qsort` fit together with almost no
  glue.
- **It is not a boolean.** `strcmp` returns 0 for *equal*, so `if (strcmp(a, b))` reads "if they
  are equal" and means the opposite. Write the comparison out, `strcmp(a, b) == 0` or `!= 0`, as
  52 does. It costs nothing and removes the trap.

`strcmp` also needs both arguments to be NUL-terminated. It has no length to stop at, so a
missing terminator means it reads past the buffer. When you already know the lengths,
[`memcmp`](https://en.cppreference.com/w/c/string/byte/memcmp) compares exactly *n* bytes and is
the better tool. [`strncmp`](https://en.cppreference.com/w/c/string/byte/strncmp) is the bounded
version for strings that may be longer than the part you care about.

## 22: strcmp as a sort comparator

[`qsort`](qsort.md) sorts an array of anything. It knows only the element size, and it calls your
comparator with **pointers to two elements**, typed `const void *`. In 22 the elements are
`char *` pointers into the file buffer (the [strtok](strtok.md) page explains why no name is
copied), so each argument is a pointer to a `char *`. The comparator has to remove one level of
indirection before `strcmp` can see the strings:

```c
static int cmp_str(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

qsort(names, (size_t)n, sizeof(char *), cmp_str);
```

This cast is the most common place to get the idiom wrong, and the mistake compiles silently.
Write `strcmp(a, b)` directly and `strcmp` reads the *bytes of the pointers* as if they were
characters. The result is a valid-looking order that has nothing to do with the names. The cast
depends on the array's shape. Had 22 copied the names into a 2-D array, `char names[N][16]`, the
elements would be the character arrays themselves, and the comparator would be
`strcmp((const char *)a, (const char *)b)` with no dereference. The rule is to ask "what is one
element?" and cast `void *` to a pointer to that.

Sorting pointers rather than strings is also the efficient choice. `qsort` swaps elements by
copying `size` bytes, so swapping two 8-byte pointers is cheap, while swapping two 16-byte name
buffers moves twice as much and grows with the longest name. Each comparison costs only as many
bytes as the two names share before they differ, usually one or two letters.

Byte order is the right order here because the names are uppercase ASCII, where the code order
`A` < `B` < … < `Z` is the alphabet. It would stop being right in three ways that are worth
knowing:

- **Mixed case.** `"Zoe"` sorts before `"adam"`, because every uppercase letter is below every
  lowercase one. Fold the case in the comparator (POSIX
  [`strcasecmp`](https://man7.org/linux/man-pages/man3/strcasecmp.3.html)) if that matters.
- **Locale.** Dictionary order in a real language is not byte order: accents, ligatures and
  language-specific rules all change it. That is what
  [`strcoll`](https://en.cppreference.com/w/c/string/byte/strcoll) is for. Project Euler's data
  is defined in byte order, so `strcmp` is the right choice and `strcoll` would be a bug waiting
  for a non-C locale.
- **Delimiters left in the string.** 22's tokens keep their quotes (`"MARY"`), so `strcmp` compares
  the quotes too. That works only because `'"'` (0x22) is below every letter, so a short name's
  closing quote still sorts before a longer name's next letter. The strtok page covers this in
  detail. The safe habit is to strip the delimiters before sorting, not to rely on ASCII.

`qsort` is not [stable](https://en.wikipedia.org/wiki/Sorting_algorithm#Stability), but with
`strcmp` as the comparator, two elements that compare equal are equal strings, so their order
cannot change the score.

## 52: strcmp as an equality test on canonical keys

52 asks for the smallest *x* such that 2*x*, 3*x*, …, 6*x* all contain the same digits as *x*.
"Same digits in a different order" is hard to test directly and easy to test with a
[canonical form](canonical-form.md): sort the digits of each number, and two numbers are digit
permutations of each other exactly when their sorted digits are equal. 125874 and its double
251748 both reduce to `"124578"`.

The C solution builds the key as a string. It peels off the digits with `% 10`, sorts the
characters with a second, much smaller `qsort`, and adds a terminator. It then compares keys with
`strcmp`:

```c
sorted_digits(i, fingerprint);
for (int m = 2; m <= multiples; m++) {
    sorted_digits(i * (long long)m, candidate);
    if (strcmp(fingerprint, candidate) != 0) { all_match = 0; break; }
}
```

Here only the zero/non-zero part of the result is used, and the order is irrelevant. Storing the
key as a string still helps, for two reasons:

- **Length is handled for free.** If 6*x* has one more digit than *x*, the keys have different
  lengths, and `strcmp` sees one string's `'\0'` meet a digit and reports a difference. There is
  no separate length check to forget.
- **Most candidates fail fast.** The loop starts with 2*x*, and for nearly every *x* the keys
  differ in the first byte or two, so the typical iteration is one short `strcmp` and a `break`.

The `qsort` comparator for the digits is `*(const char *)a - *(const char *)b`. Subtraction is a
common comparator shortcut and is safe here because the values are the digit characters `'0'`
to `'9'`, so the difference is small. For `int` elements it is not safe: `a - b` overflows when
the values have opposite signs and large magnitudes, and the sort comes out wrong. Write
`(x > y) - (x < y)` there instead.

A sort is not the only way to build the key. A ten-element digit count, `int count[10]`, is also
canonical, takes one pass instead of a sort, and compares with `memcmp(c1, c2, sizeof c1)`. With
at most seven digits the difference is negligible, and the sorted string has the advantage of
being readable when you print it.

## The Python counterpart

Python strings compare by content with the ordinary operators, so most of this page disappears.

| C | Python | Where |
|---|---|---|
| `strcmp(a, b) == 0` | `a == b` | 52 |
| `strcmp(a, b) < 0` | `a < b` | |
| `qsort(names, n, sizeof(char *), cmp_str)` | `sorted(names)` | 22 |
| `qsort` with a custom comparator | `sorted(xs, key=f)` | |
| `strcasecmp` | `a.casefold() == b.casefold()`, or `key=str.casefold` | |
| `strcoll` | `key=locale.strxfrm` | |
| sorted-digit string key | `"".join(sorted(str(n)))` | 52 |
| `int count[10]` + `memcmp` | `collections.Counter(str(n))` | |

`str` comparison in Python orders by Unicode code point, which for ASCII is the same byte order
`strcmp` uses, so `sorted(names)` in 22 and `qsort` with `strcmp` give the same list. 22's Python
does the split and the sort in one line: `sorted(text.split(","))`. The quotes are still there
when it sorts, exactly as in C, and they are removed only later by `strip('"')` in the scorer. The
same ASCII accident keeps both versions correct.

Python has no comparator in the C sense. `sorted` takes a **key function**, which maps each
element once to a value whose natural order is the order you want. A comparator is called
O(*n* log *n*) times on pairs; a key is computed *n* times and then compared natively. When you
really do have a three-way comparison function in the `strcmp` style,
[`functools.cmp_to_key`](https://docs.python.org/3/library/functools.html#functools.cmp_to_key)
adapts it. Neither of these solutions needs it.

52's Python shows the other half of the difference. It builds all six keys and puts them in a
set:

```python
len({"".join(sorted(str(i * m))) for m in range(1, multiples + 1)}) == 1
```

The set does the equality tests, through hashing rather than pairwise comparison. It is shorter
than the C loop, but it computes every key for every *x*, while the C loop stops at the first
mismatch. Both are fast here. The trade is the usual one in this series: Python puts the whole
condition in one expression, while C writes the loop out and gets the early exit. A list
comparison would also work: `sorted(str(a)) == sorted(str(b))` compares two lists of characters
element by element, which is `strcmp` without the terminator.

The rules are the same in both languages. Know which order you are sorting in (byte, case-folded
or locale) and choose it on purpose. Compare a canonical key rather than the raw values when
"equal" means "equal up to rearrangement". In C, add two more: never use `==` on strings, and make
the comparator's cast match what one array element actually is.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0022](/solutions/0022/) — Names Scores
- ● [0052](/solutions/0052/) — Permuted Multiples

<!-- /problems -->
