<!-- tags: [mixed-radix] -->
<!-- status: final -->
# Mixed radix

Positional notation normally fixes one base and repeats it: decimal weights every place by ten,
binary by two. A [mixed radix](https://en.wikipedia.org/wiki/Mixed_radix) numeral gives each place
its own base — which is exactly what a clock does (60 seconds to a minute, 60 minutes to an hour,
24 hours to a day) and what a date does. In the problems below it is never about writing a number
down for a human to read. It is about the bijection underneath: a tuple of small, bounded fields
becomes a single integer, and once it is a single integer it can be a hash key, an array index, or
a rank you compare with `<`.

## The idea

Fix bases $b_0, b_1, \dots, b_{k-1}$, all at least 2, and digits $d_i$ with $0 \le d_i < b_i$. The
place values are the running products of the bases below:

$$N = \sum_{i=0}^{k-1} d_i w_i, \qquad w_0 = 1, \quad w_{i+1} = w_i b_i.$$

Two properties do all the work. First, the map from digit tuples to integers is a **bijection** onto
$0 \dots \prod b_i - 1$ — every code is reachable and no two tuples collide — and the reason is the
strict digit bound. A digit that could reach its own base would weigh $b_i w_i = w_{i+1}$, which is
precisely the next place's value, so it would alias a carry. Fixed radix is the special case where
all $b_i$ are equal; the [factorial number system](/topics/domain/factorial-number-system) is the
case $b_i = i + 2$.

Second, the conversions are one line each. Encoding is [Horner
evaluation](https://en.wikipedia.org/wiki/Horner%27s_method) from the most significant end, so no
place value is ever materialised; decoding is a `divmod` chain from the least significant end.

```python
def encode(digits: list[int], bases: list[int]) -> int:
    """Least significant first; requires 0 <= digits[i] < bases[i]."""
    code = 0
    for digit, base in zip(reversed(digits), reversed(bases)):
        code = code * base + digit
    return code


def decode(code: int, bases: list[int]) -> list[int]:
    digits = []
    for base in bases:
        code, digit = divmod(code, base)
        digits.append(digit)
    return digits
```

Write them as a pair, next to each other, and round-trip them in a test. Everything below is one of
these two functions wearing a costume.

## Three jobs it does

**A numeral system the structure hands you.** Sometimes the bases are not a choice — the object
being counted dictates them. Permutations are the standard case: there are $n!$ of them, a factoradic
numeral with bases $2, 3, \dots, n$ covers exactly $0 \dots n!-1$, and rank and
[unrank](/topics/technique/unranking) are the two functions above. Problem 868's bell-ringing rule
turns out to be the Steinhaus–Johnson–Trotter enumeration, and the number of swaps to reach a target
arrangement is its rank in that order — computed by the same `code = code * base + digit` fold, one
digit per recursion level. Problem 254 uses the same system for something with no ordering in it at
all: because each place value divides the next, greedily writing a number as a sum of factorials
*is* its factoradic expansion, and that expansion provably uses the fewest terms. Both are worked
through on the [factorial number system](/topics/domain/factorial-number-system) page; the point
here is that they are one encoding with two readings.

**A tuple key in a language that has no tuples.** Problem 145 counts the integers below $10^9$ whose
sum with their own reversal has only odd digits, by [digit DP](/topics/technique/digit-dp) over the
columns of that addition. Because column $i$ and column $d-1-i$ share a digit-pair sum but are
resolved at different times, the DP state is a carry plus a stack of at most four pending pair sums,
each in $0 \dots 18$. In Python that is a dictionary keyed by `(carry, tuple_of_sums)` and there is
nothing to think about. In C there is no such key, so the stack is packed into one `int` as four
base-19 digits with the stack length as a fifth, higher place — the four sums contribute
$s_0 + 19 s_1 + 361 s_2 + 6859 s_3$, and the length is added on at weight $19^4 = 130321$.
Hashing and comparison are now integer operations on a value below about $6.5 \times 10^5$. The
length field is not decoration: the stack is *variable length*, and without it the empty stack,
`(0)` and `(0, 0)` would all encode to zero. Leading zeros are invisible in any positional system, so
a variable-length code needs either a length place, a per-length offset, or a base of $b+1$ with $0$
reserved for "absent".

**A key whose order is the order you want.** Problem 254 breaks ties between equal-length candidates
lexicographically on the digit counts $(c_1, \dots, c_8)$, preferring a larger $c_1$, then a larger
$c_2$, and so on. Rather than compare eight-element tuples in the hot loop, it precomputes a single
integer per candidate — the same Horner fold, with $e_d = d - c_d$ as the digit and $e_1$ most
significant — `rank = rank * (d + 1) + (d - c_d)`, accumulated over $d = 1 \dots 8$, with bases
$2, 3, \dots, 9$. Now a single `<` between two `int`s reproduces the tie-break exactly. Order preservation is not automatic; it
needs three things, all present here: **fixed width** (every code has the same places), **most
significant field first**, and each field encoded **monotonically** in what you are comparing.
Complementing a field, as `d - c_d` does, is how you flip one field's direction without disturbing
the others — the mixed-radix answer to a `sort(key=...)` with mixed ascending and descending keys.
The same solution collects the second dividend of packing: since the code is a small dense integer,
its two lookup tables are plain lists indexed by it, and the [hash
table](/topics/technique/hash-table) disappears entirely.

**And the odometer.** The bijection also runs a loop. When the number of nested dimensions is a
runtime value, `for code in range(math.prod(bases))` plus a `decode` sweeps the whole product space
with one counter, or you increment the digits in place and let the carry propagate:

```python
def advance(digits: list[int], bases: list[int]) -> bool:
    """Step to the next tuple; False when the space wraps to all zeros."""
    for i, base in enumerate(bases):
        digits[i] += 1
        if digits[i] < base:
            return True
        digits[i] = 0
    return False
```

## How to reason about it

- **Compute $\prod b_i$ before you write anything else.** That single number decides the design. If
  it fits in a comfortable array, the code is an index and you need no hash table at all. If it fits
  in a machine word, you can hash and compare it cheaply. If it does not fit, do not pack — you are
  about to build a silent overflow.
- **Bound every digit strictly, and assert it while developing.** An out-of-range digit does not
  raise; it quietly becomes some *other* valid state, and the DP that results is wrong in a way no
  crash will tell you about. The bound is the entire correctness argument for the encoding.
- **Pad the bases to powers of two when the loop is hot.** Then the multiplies and `divmod`s become
  shifts and masks — ordinary [bit packing](/topics/technique/bit-manipulation) is just mixed radix
  with power-of-two bases. You trade range for speed, so check the product again after rounding up.
- **Don't pack when the language already has the key.** A Python `dict` keyed on a tuple is clearer,
  is checked by the interpreter, and is usually fast enough; problem 145 packs only on the C side.
  Reach for the encoding when the container demands a scalar, when the code can be an array index,
  or when comparison is the inner loop.
- **Decide LSB-first or MSB-first once, and write it in the docstring.** The two conventions are the
  same numeral read from opposite ends, and mixing them reverses your tuple without any other
  symptom. This is the most common bug in code that has an encoder and a decoder in different files.
- **Variable-length states need a length field.** See above; it is the same bug as a leading zero,
  and it shows up only once the state actually shrinks.
- **Ordering is a stronger requirement than uniqueness.** A packing that merely distinguishes states
  is free-form; a packing you intend to compare must be fixed-width and most-significant-first, or
  the comparison silently means something other than you think.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0145](/solutions/0145/) — Reversible Numbers
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0868](/solutions/0868/) — Belfry Maths

<!-- /problems -->
