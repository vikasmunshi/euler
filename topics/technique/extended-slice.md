<!-- tags: [extended-slice] -->
<!-- status: final -->
# extended slice

An [extended slice](https://docs.python.org/3/library/functions.html#slice) is `seq[start:stop:step]`
with a `step` other than 1 — the [slice](https://docs.python.org/3/glossary.html#term-slice) notation
carrying a stride. It looks like a convenience for taking every other element, and it is, but the
problems below use it for something better: as a *reader* it partitions a sequence into residue
classes, with a step of $-1$ it is a reversal that can stand for an operation in the problem itself,
and as a *target* it writes to every $k$-th slot at C speed. In each case the slice is not a tidier
spelling of a loop — it is the observation the algorithm rests on.

## The idea

`a[i::k]` is the elements of `a` at every position congruent to $i$ modulo $k$. That is worth saying
in those words, because the moment a problem has *period $k$*, the slice is the decomposition.

Problem 59 breaks a repeating-key XOR cipher with a known key length. A byte at position $p$ was
XOR-ed with key byte $p \bmod k$, so the ciphertext is not one hard cipher but $k$ independent
single-byte ones — and the slice says exactly that:

```python
slices_range: tuple[int, ...] = tuple(range(key_length))
# Slice i holds ciphertext bytes at positions i, i+k, i+2k, ... - each a single-byte XOR cipher.
encrypted_slices: list[list[int]] = [encrypted[i::key_length] for i in slices_range]
```

Having split it, each of the $k$ subproblems has only 26 candidate key bytes, scored independently by
[letter frequency](/topics/technique/frequency-statistics). A $26^9$ search becomes $9 \times 26$
scans. The line that made that true is one extended slice, and no amount of loop-writing would have
made the structure as visible.

The degenerate case, `a[::-1]`, reverses. Problem 238 uses it structurally rather than cosmetically:
it reverses the digit string before translating each digit into a run of bits, so that the resulting
string, read as `int(runs, 2)`, has its least significant bit at the *start* of the stream. Choosing
the direction at the slice is cheaper than fixing the bit order afterwards.

## Reversal as the operation

Problem 336 goes further: there the reversal *is* the move. Simon's turntable reverses a suffix of
the train, so his sort is a [pancake sort](https://en.wikipedia.org/wiki/Pancake_sorting), and one
turn of the table is one line — `s[:i] + s[i:][::-1]` on a string, or `a[i:] = a[i:][::-1]` in place
on a list (the length always matches, because it is the same slice on both sides). A brute-force
checker that simulates Simon is little more than that line in a loop.

The solution proper runs the process backwards, and the slices carry over from the simulation into
the closed form. Undoing one placement of the first carriage onto an already-built tail $t$ of length
$m$ gives $\operatorname{rev}(t)[0:p] \,\|\, \text{first} \,\|\, t[0:m-p]$ for each offset
$1 \le p < m$, and that formula transcribes into Python almost symbol for symbol: `t[::-1][:p]`,
the letter, `t[:m - p]`. The chained `[::-1][:p]` could be folded into one negative-step slice,
`t[:m - p - 1:-1]`, but the fold trades a visible "reverse, then take $p$" for a stop index that is
easy to get wrong by one — and the bounds of a negative-step slice are the one place this notation
is genuinely hard to read. Here I would keep the chain.

The chain has a cost the formula hides, though. Inside a comprehension over both `t` and `p`,
`t[::-1]` is a fresh copy *per offset*, not per tail — $m-1$ identical reversals of the same string.
At $n = 11$ that is noise next to the sort, so the Python leaves it inline for readability; the C port,
which has no slice and must write the reversal as an explicit loop anyway, naturally builds `rev` once
per tail and then splices each row with two `memcpy` calls around the inserted letter. When the
reversed value is reused, hoist it into a name; the slice reads like a pure expression, but it is an
allocation.

## As an assignment target

An extended slice can be written to, and this is the property that changes running times. Problem
10's [Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes) crosses out multiples without
ever executing the inner loop in Python:

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

Assigning a zero-filled block to `i*i::i` is a single strided store loop inside CPython; only the
$O(\sqrt{n})$ outer iterations are interpreted. At $n = 2 \times 10^6$ this runs in `0.058 s`, while
problem 10's Sieve of Sundaram — the same [`bytearray`](/topics/technique/bytearray), marked one
element at a time from a Python loop — takes `0.361 s`. The container is identical; the slice
assignment is the difference.

Two rules govern the target, and they differ from ordinary slicing:

- **The lengths must match exactly.** `a[0:3] = [1, 2]` is legal and resizes the list;
  `a[0:6:2] = [1, 2]` raises `ValueError`. That rigidity is why `len(range(i * i, max_num + 1, i))`
  is spelled out rather than computed by hand: a wrong count fails loudly on the hottest line in the
  program instead of quietly leaving composites in the sieve.
- **NumPy plays by different rules.** The same syntax on an `ndarray` broadcasts, so problem 196's
  sieve is just `sieve[i * i:: i] = False` and its segmented sieve `seg[start - lo:: p] = False` —
  no length to compute, because a scalar fills whatever the slice selects. NumPy slices are also
  *views* rather than copies, so `seg[a::b]` allocates nothing. Moving code between the two worlds
  is where this bites: the built-in version needs the length and the NumPy version does not.

## How to reason about it

- **Reach for it when the index arithmetic is a residue class.** "Every $k$-th element from $i$" is
  what `a[i::k]` says out loud; a `range(i, n, k)` loop with a manual accumulator says nothing about
  why $k$ was chosen.
- **On built-in sequences it copies.** `encrypted[i::key_length]` allocates a new list per slice —
  fine when the whole ciphertext is a few thousand bytes, wasteful in a hot loop over a large buffer.
  If you only need to iterate, `itertools.islice` is lazy; if you need speed on a big array, use
  NumPy and get a view.
- **`[::-1]` versus `reversed()`.** Both reverse; the slice materialises a copy, `reversed()` is a
  lazy iterator. Use the slice when you need a *value* of the same type (a reversed `str`, a reversed
  `bytes` to feed `int(..., 2)`, a reversed tail to splice into a new string as in problem 336), and
  `reversed()` when you only iterate.
- **It is one of the few Python idioms with no C counterpart.** In C, the sieve line is the
  `for (j = i * i; j <= n; j += i)` loop you would have written anyway — which is precisely the point:
  the extended slice is how you get that loop without leaving Python
  ([parity across languages](/topics/takeaway/parity-across-languages)). The same holds for
  reversal: problem 336's `t[::-1]` becomes a three-line copy loop in C, and writing it out is what
  makes its cost — and the case for doing it once — obvious.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0059](/solutions/0059/) — XOR Decryption
- ● [0336](/solutions/0336/) — Maximix Arrangements

<!-- /problems -->
