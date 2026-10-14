<!-- tags: [tuple-assignment] -->
<!-- status: final -->
# tuple assignment

Tuple assignment is Python's `a, b = b, a + b`: build a tuple on the right, then unpack it into
names on the left. The solutions below all use it for the same job. Each one carries a *pair* of
numbers forward through a recurrence, and each new pair is computed from both members of the old
one. Done as two ordinary assignments, the first would overwrite a value the second still needs.
Tuple assignment avoids that, because the whole right-hand side is evaluated before any name is
rebound. This page is part of the language-idioms series, so it covers the idiom, why these four
solutions use it, and what the C versions write instead. The neighbouring
[parallel assignment](/topics/technique/parallel-assignment) page is about the general concept of
updating several variables at once, in any language. This page is about the Python mechanism
behind it: packing, unpacking, and the swap.

## The idea

The [language reference](https://docs.python.org/3/reference/simple_stmts.html#assignment-statements)
defines the order exactly. An assignment statement first evaluates the expression list on the
right. With a comma in it, that produces a single tuple. Then it assigns the tuple's items to the
targets on the left, one at a time, from left to right. So in

```python
x, y = (3 * x + 4 * y, 2 * x + 3 * y)
```

both products are computed from the *old* `x` and `y` and stored in a temporary tuple, and only
then are `x` and `y` rebound. The temporary exists, but you never name it. (The parentheses are
house style. The comma makes the tuple, not the brackets.) The swap `a, b = b, a` is the smallest
case: the right side holds the two old values, and the left side writes them back in the other
order.

Each of the four problems uses the idiom with a different recurrence:

| Problem | Pair carried | Update |
|---|---|---|
| [2](/solutions/0002/) | two consecutive *even* [Fibonacci](/topics/domain/fibonacci-sequence) terms | `(a, b) → (b, 4b + a)` |
| [57](/solutions/0057/) | numerator and denominator of the √2 [convergent](/topics/domain/convergent-continued-fraction) | `(p, q) → (p + 2q, p + q)` |
| [100](/solutions/0100/) | a solution of the [Pell equation](/topics/technique/pells-equation) x² − 2y² = −1 | `(x, y) → (3x + 4y, 2x + 3y)` |
| [169](/solutions/0169/) | two neighbouring values of [Stern's diatomic sequence](/topics/domain/sterns-diatomic-sequence), walked one bit of *n* at a time | one member replaced by the sum, the other kept |

Problem 2 is a shift: the old `b` becomes the new `a`, and only the new `b` is real arithmetic.
Problems 57 and 100 are full 2×2 linear maps, so each new value reads *both* old ones. These are
the cases where two plain statements give the wrong answer. Problem 169 is the odd one out, and
the C section explains why it matters.

There is a second reason to write the update this way, besides correctness. Each tuple assignment
*is* one row-pair of a [linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients).
`x, y = 3*x + 4*y, 2*x + 3*y` is the matrix [[3, 4], [2, 3]] applied to the column (x, y), written
out on one line. A reader can check it against the derivation in the notes without tracking which
variable has already been overwritten. Once the update is visibly a matrix, it is also obvious how
to jump *k* steps at once with [matrix exponentiation](/topics/technique/matrix-exponentiation)
when the step count is too large to walk.

### Unpacking is the same mechanism

The left side of the statement is a general *target list*, so the same rule handles more than
swaps. Problem 57 initialises three names in one line (`numerator, denominator, result = (1, 1, 0)`).
Problem 2 starts its [generator](/topics/technique/generator) with `even_fib_a, even_fib_b = (2, 8)`.
The same unpacking appears in `for k, v in d.items()`, in `q, r = divmod(n, d)`, and with a starred
target in `first, *rest = seq` ([PEP 3132](https://peps.python.org/pep-3132/)). In every case the
right side is fully evaluated first and then split. If the number of items doesn't match the
number of targets, Python raises `ValueError` at that point. It never truncates or pads silently.

## The counterpart in C

C has no tuple to pack into, so the temporary has to be written out by hand. Three of the four C
versions do this, and two of them say why in a comment. Problem 100:

```c
/* Use temporaries so the new x does not clobber the old x before y is computed. */
long long nx = 3 * x + 4 * y;
long long ny = 2 * x + 3 * y;
x = nx;
y = ny;
```

This is the tuple assignment with its hidden tuple given names (`nx`, `ny`). Problem 2 needs only
one temporary, because half of its update is a plain shift: compute `next = 4 * b + a`, then
`a = b`, then `b = next`. The order of those last two lines matters, and in Python the tuple form
removes that concern.

Problem 57 shows a cost the Python version hides. Its numbers are big integers, so the C version
keeps them in a fixed-size `BigInt` struct, computes `new_num` and `new_den`, and copies them back
with struct assignment (`num = new_num`). That is valid C, but each copy moves the whole limb
array, on every iteration. In Python the "copy" only rebinds a reference to an `int` object that
already exists, so the rebinding costs nothing. If the copy ever showed up in a profile, the C
version could swap pointers instead and alternate between two buffers. That is the
pointer-level version of `a, b = b, a`.

Problem 169 shows the reverse. Its Python update looks like a full tuple assignment: one branch of
the bit test writes `a, b = a, a + b`, and the other the mirror image. But in each branch, one
target just gets its own old value back. Only *one* variable actually changes, and the value it
needs is still unchanged. So the [GMP](/topics/technique/gmp) version in C needs no temporary at
all. It does a single in-place `mpz_add` into whichever of `a` or `b` the bit selects. The tuple
form is convenient for keeping the two branches symmetric. In C, writing out the dependency shows
it was never a simultaneous update.

The classic C swap is the three-line `tmp` dance. The XOR swap (`a ^= b; b ^= a; a ^= b;`) is a
curiosity, not an optimisation: it is slower on modern hardware, and it zeroes the value if both
operands are the same object. A compiler turns the `tmp` version into register renaming anyway.
CPython does something similar: since 3.11 it compiles two- and three-name swaps to a stack
`SWAP` instruction, without building the tuple at all.

## How to reason about it

- **Use it whenever a new value reads an old value that is also being replaced.** That is the
  test. If every right-hand side only reads variables that keep their value, sequential statements
  are fine, and in C they are cheaper.
- **Read the update as a matrix.** If the pair update is linear, writing it as one tuple assignment
  makes the matrix visible. That makes it easy to check against the derivation and easy to turn
  into a fast power later.
- **Watch the target order when the targets depend on each other.** Targets are assigned left to
  right. `i, a[i] = j, v` writes `a[j]`, not `a[old i]`, because `i` is rebound before `a[i]` is
  evaluated as a target. Keep subscripted targets independent of names that the same statement
  rebinds.
- **In C, name the temporaries after the values.** `nx`/`ny` or `new_num`/`new_den` turn the hidden
  tuple into readable code. A comment saying why (as in 57 and 100) prevents someone from later
  "simplifying" it into a bug.
- **Mind what one assignment copies.** In Python, assignment only rebinds names. In C, assigning a
  struct copies all of it. For large values, swap pointers rather than contents.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0002](/solutions/0002/) — Even Fibonacci Numbers
- ● [0057](/solutions/0057/) — Square Root Convergents
- ● [0100](/solutions/0100/) — Arranged Probability
- ● [0169](/solutions/0169/) — Sums of Powers of Two

<!-- /problems -->
