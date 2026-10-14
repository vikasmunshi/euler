<!-- tags: [endianness] -->
<!-- status: final -->
# Endianness

[Endianness](https://en.wikipedia.org/wiki/Endianness) is the order in which the parts of a
multi-part number are laid out: most significant part first (**big-endian**) or least significant
first (**little-endian**). It usually comes up as a property of the hardware, the byte order of a
`uint32_t` in memory. In these three C solutions it comes up one level higher. C has no big
integers, so 5 (the LCM of 1..20), 16 (the digits of 2¹⁰⁰⁰) and 20 (the digits of 100!) each
build one out of an array, and each has to decide which end of the array holds the units. All three
choose little-endian and say so in a comment. This page is part of the language-idioms series. It
covers what that choice buys, what it does *not* make them depend on, and how Python handles the
same thing.

## The idea

There are two different byte orders here, and they need to be kept apart:

- **Representation order** is a convention the programmer picks: `digits[0]` is the units digit,
  or `limbs[0]` is the low 32 bits. It is part of the algorithm, and it is the same on every
  machine.
- **Host byte order** is how the CPU stores the bytes *inside* one `unsigned int`. x86-64 and
  almost all ARM systems are little-endian; network protocols, many file formats and some older
  architectures are big-endian. A program only sees it when it reads memory as a type other than
  the one it was written as.

All three solutions use a little-endian representation and none of them depends on the host order.
The table shows what each one stores:

| Problem | Array | Element | Base | Index 0 holds |
|---|---|---|---|---|
| 5 | `unsigned int limbs[64]` | one limb | 2³² | the low 32 bits |
| 16 | `unsigned char *digits` (calloc) | one decimal digit | 10 | the units digit |
| 20 | `unsigned char digits[512]` | one decimal digit | 10 | the units digit |

## Why the solutions choose little-endian

**Carries move toward higher indices.** Schoolbook multiplication by a small number starts at the
units and carries upward. 16 and 20 both do this with one loop:

```c
for (int j = 0; j < len; j++) {
    int val = digits[j] * base + carry;
    digits[j] = val % 10;
    carry = val / 10;
}
while (carry > 0) {
    digits[len++] = carry % 10;
    carry /= 10;
}
```

With the units at index 0, the loop runs forward and a growing number gets new digits at
`digits[len]`, at the end of the array. A big-endian array would have to grow at the front, which
means shifting every digit along by one, or starting the number at the end of a fixed buffer and
keeping track of where it begins. 2¹⁰⁰⁰ grows from 1 digit to 302 one doubling at a time, so growth
happens on every few steps. Little-endian is the order that makes it free.

**Each index has a fixed weight.** `digits[j]` is always worth 10ʲ and `limbs[i]` is always worth
2³²ⁱ, however long the number is. In 5 that is what lets `bi_mul_small` carry up from `limbs[0]` and
`bi_div_small` walk down from `limbs[n - 1]`, carrying the remainder down with
`(rem << 32) | limbs[i]`: both directions work because the index alone gives the place value. It is
the same reason [GMP](https://gmplib.org/manual/Low_002dlevel-Functions) stores its limbs
least significant first.

**The digit sum doesn't care.** 16 and 20 never print the number, they only add its digits up, so
the order the digits are stored in can be whatever suits the multiplication. 5 does print its
result, and its `bi_to_str` shows the cost of the choice: repeated division by 10 produces the
decimal digits units first into `buf`, and a final loop reverses them into a string. Text is
big-endian, because people read the most significant digit first, so a little-endian number has to
be flipped once on the way out.

## Why the host order never comes into it

5 is the solution that could have depended on host byte order, because it splits 64-bit values
into 32-bit limbs. It does it with arithmetic:

```c
a->limbs[0] = (unsigned int)(val & 0xFFFFFFFFULL);
a->limbs[1] = (unsigned int)(val >> 32);
```

Shifts and masks work on the *value* of an integer, not on its bytes, so `val >> 32` is the high
half on every machine. Joining two limbs back into one value, `(rem << 32) | limbs[i]`, is
portable for the same reason. The non-portable versions look like this:

```c
uint64_t v = *(uint64_t *)&limbs[0];        /* also breaks strict aliasing */
union { uint64_t u; uint32_t w[2]; } s;     /* w[0] is the low half only on a little-endian host */
fwrite(limbs, sizeof limbs[0], n, file);    /* the file's byte order is the writer's host order */
```

Each of these reads or writes the bytes of an object instead of computing with its value. On x86 or
ARM they produce the right answer, so the bug is invisible until the code runs on a big-endian
machine or reads a file one wrote. Rob Pike's
[*The byte order fallacy*](https://commandcenter.blogspot.com/2012/04/byte-order-fallacy.html)
gives the rule: you only need to know the order of the *data* you are reading or writing, never
the order of the machine. Assemble values with shifts, as in `b[0] | b[1] << 8 | …` for
little-endian data, and the code is portable without a single `#ifdef`. When code genuinely needs
the host order, C23 provides `__STDC_ENDIAN_NATIVE__` in
[`<stdbit.h>`](https://en.cppreference.com/w/c/numeric/bit_manip).

5 does make one assumption, but it is about width, not order: it uses `unsigned int` for 32-bit limbs
and `unsigned long long` for the 64-bit intermediate. That holds on every mainstream ABI, but
`uint32_t` and `uint64_t` from `<stdint.h>` would make the assumption explicit.

## The Python counterpart

The Python siblings have none of this code. `int` has arbitrary precision, so 5 is a
`functools.reduce` over `x * y // math.gcd(x, y)`, and 16 and 20 are
`sum(int(d) for d in str(n))` over `base**power` and `math.factorial(n)`. The little-endian array
is still there, inside CPython: an `int` is stored as an array of 30-bit "digits", least
significant first, for the same reasons as in 5. It just isn't visible to Python code.

The order shows up again where the number becomes text or bytes:

- **`str(n)` is big-endian.** It gives the most significant digit first, as text always does. That
  is why 5's C solution has to reverse its digits and the Python doesn't. If you want the C order in
  Python, `reversed(str(n))` gives it, or `divmod(n, 10)` in a loop.
- **Byte conversions name the order explicitly.**
  [`int.to_bytes`](https://docs.python.org/3/library/stdtypes.html#int.to_bytes) and
  `int.from_bytes` take `byteorder="big"` or `"little"` (with `"big"` as the default since 3.11),
  and [`struct`](https://docs.python.org/3/library/struct.html) format strings begin with `<`, `>`
  or `!` for little, big and network order. `sys.byteorder` reports the host order, and `struct`'s
  `=` and `@` prefixes use it.

So Python follows Pike's rule by design: you say which order the data is in when you convert it,
and the host order only appears when you ask for it. C leaves it to the programmer. These three
solutions get it right, by storing numbers in an order they chose and combining their parts with
arithmetic, not by reading memory.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0005](/solutions/0005/) — Smallest Multiple
- ● [0016](/solutions/0016/) — Power Digit Sum
- ● [0020](/solutions/0020/) — Factorial Digit Sum

<!-- /problems -->
