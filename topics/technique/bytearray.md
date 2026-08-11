<!-- tags: [bytearray] -->
<!-- status: final -->
# bytearray

A [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray) is a mutable sequence of
integers in $0..255$, stored as one contiguous C buffer — `bytes` with the immutability removed. It
recurs across the problems below because the largest data structure in a Project Euler solution is
usually a *flag array*: one slot per integer up to some bound, holding one bit of information. A
`list` will do that job, and will spend eight bytes and a pointer dereference per slot doing it.

## The idea

Three properties do all the work.

**One byte per element, contiguous.** A million-element `bytearray` is 1,000,058 bytes; a
`[0] * 1_000_000` list is 8,000,064 — and that is only the pointer array, before the integer objects
it points at. For a sieve over $10^8$ the difference decides whether the program runs at all.

**Indexing yields `int`, slicing yields `bytearray`.** `sieve[i]` is a plain integer, so a flag test
is `if sieve[i]:` with no unboxing ceremony. Slices stay in the byte world, which is what makes the
next property useful.

**Strided slice assignment runs in C.** This is the property that changes algorithms rather than
memory footprints, and problem 10's [Sieve of Eratosthenes](/topics/technique/sieve-of-eratosthenes)
is the canonical case:

```python
sieve = bytearray(b"\x01") * (max_num + 1)
sieve[0] = sieve[1] = 0
for i in range(2, int(max_num ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i:: i] = bytearray(len(range(i * i, max_num + 1, i)))
```

The inner loop of the sieve — the crossing-out — never executes in Python. `bytearray(k)` is a
zero-filled block of `k` bytes, and assigning it to the [extended
slice](/topics/technique/extended-slice) `i*i::i` is a single strided memset at C speed. Only the
outer loop over $\sqrt{n}$ candidates is interpreted.

Compare problem 10's other sieve, the [Sieve of Sundaram](/topics/technique/sieve-of-sundaram),
which marks the same kind of `bytearray` one element at a time from a Python loop:

```python
marked = bytearray(n + 1)
for i in range(1, n + 1):
    j = i
    while i + j + 2 * i * j <= n:
        marked[i + j + 2 * i * j] = 1
        j += 1
```

Same container, same asymptotics, and at $n = 2 \times 10^6$ it takes `0.361 s` against the
slice-assigned Eratosthenes' `0.058 s`. The `bytearray` is not what made the first one fast; the
slice assignment was. Problem 77 marks a Sundaram sieve the same way, and gets away with it because
its bound is small.

The other C-speed method worth knowing is `.count()`. Problem 926 needs, for each of the
$O(\sqrt{n})$ bands of large primes sharing an exponent in $n!$, how many primes fall in that band —
and gets it with `sieve[lo + 1:hi + 1].count(1)`, one buffer scan per band instead of a Python loop
over the range.

## The other two jobs

**A bit-addressed DP table.** When the state of a dynamic program is a bitmask, the table is indexed
by an integer $0..2^D-1$ and each entry is a single boolean. Problem 961 encodes a game position as
the integer whose binary digits mark which decimal digits are nonzero, and solves the whole impartial
game bottom-up into `win = bytearray(1 << digits)`, reading `win[reduced]` for the position one move
on. The [`bit-array`](/topics/technique/bit-array) proper would be eight times denser again, but you
would pay for the packing in Python-level shifting; a `bytearray` is the point on that curve where
the interpreter stays out of the way.

**A mutable string of digits.** `str` is immutable, so mutating one digit costs a rebuild; a list of
`int` needs a `"".join` to become a number again. A `bytearray` holding ASCII codes is both at once —
mutable in place, and directly parseable, because `int()` accepts a bytes-like object:

```python
digits = bytearray(b"0" * length)
digits[0] = 48 + value          # 48 is ord("0")
number = int(digits)            # int() parses the buffer as a numeral
```

Problem 254 uses exactly this to walk from one number to the next of the same
[digit sum](/topics/domain/digit-sum) without ever building an intermediate string: the successor is
found by editing a suffix in place, and the result is read back as an integer with `int(digits)`.

## How to reason about it

- **Values are $0..255$, and nothing else.** Storing 256 raises `ValueError` — usefully, since it
  fails at the write rather than silently truncating. The moment a slot needs a *count* rather than a
  flag, this is the wrong container: reach for a `list`, [`array`](/topics/technique/array), or
  [NumPy](/topics/technique/numpy).
- **Extended slice assignment must match lengths exactly.** `len(range(i * i, n + 1, i))` looks
  laborious next to a hand-computed count, but it is the correct spelling and a wrong one raises
  rather than corrupting the sieve — a free off-by-one check on the hottest line in the program.
  (Plain contiguous slices *can* resize; only strided ones are rigid.)
- **It is unhashable.** A `bytearray` cannot be a `dict` key or a `set` member. When a mutable buffer
  needs to become a memo key — a board state, a canonical arrangement — freeze it with `bytes(ba)`,
  which copies but hashes.
- **Build it inside `solve()`, sized to the input.** A module-level sieve with a fixed bound is
  computed once at import and is therefore free on every benchmark run after the first, which makes
  the reported time a fiction. Every sieve in this repository is constructed per call
  ([size work to the input](/topics/takeaway/size-work-to-the-input)).
- **Know when to stop.** `bytearray` is the best *pure-Python* array of flags, not the fastest thing
  available. On problem 10 at $2 \times 10^6$, the slice-assigned sieve takes `0.058 s`; the
  [`primesieve`](/topics/technique/primesieve) library, a wheel-factorised C sieve, takes `0.0028 s`.
  Twenty times faster for one import — but also a dependency, and one that only solves the prime
  problem. `bytearray` is what you use when the array is not a sieve of primes.
- **It is the one Python idiom that ports to C unchanged.** A `bytearray` is a `calloc`'d `char *`,
  and the strided slice assignment is the `for (j = i*i; j <= n; j += i) sieve[j] = 0` you would have
  written anyway. That is why the sieve is the one place where the Python and C siblings in this
  repository read alike ([parity across languages](/topics/takeaway/parity-across-languages)) — and
  why the *Python* version of a sieve-shaped problem is usually within a small factor of the C one,
  while a dict-shaped one is not.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0010](/solutions/0010/) — Summation of Primes
- ● [0077](/solutions/0077/) — Prime Summations
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0926](/solutions/0926/) — Total Roundness
- ● [0961](/solutions/0961/) — Removing Digits

<!-- /problems -->
