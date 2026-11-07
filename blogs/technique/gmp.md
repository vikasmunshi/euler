<!-- tags: [gmp] -->
<!-- status: final 2026-11-04T03:33Z -->
# GMP

[GMP](https://gmplib.org/) — the GNU Multiple Precision Arithmetic Library — is the bignum library
you link when the C port of a Python solution runs out of bits. Python's `int` is unbounded, so a
solution that sums 100-digit values, counts 18-digit arrangements or keeps an exact rational never
announces that it needs big integers; the translation to C does, loudly, at the first silent
overflow. `__int128` buys about 38 digits and stops there. Past that line the honest options are to
[hand-roll a bignum](/blogs/technique/arbitrary-precision-arithmetic) or to link GMP, and every
problem below took the second one — because each needs not just addition but division, exact
comparison, modular exponentiation, binomials or rationals, and a library that has been tuned since
1991 beats what you will write in an afternoon.

## The idea

GMP gives C a set of opaque number types with a strict calling convention. The integer type is
[`mpz_t`](https://gmplib.org/manual/Integer-Functions); there is also `mpq_t` for exact rationals
and `mpf_t` for arbitrary-precision floats (though for serious float work you want
[MPFR](https://www.mpfr.org/), which layers correct rounding on top of GMP). A value is declared as
a one-element array, which is why an `mpz_t` passed to a function decays to a pointer and mutation
is visible to the caller — the whole API is built on that.

Three conventions carry most of the learning curve:

**Every value is initialised and cleared.** `mpz_init(x)` allocates, `mpz_clear(x)` frees, and the
variadic `mpz_inits(a, b, c, NULL)` / `mpz_clears(a, b, c, NULL)` do batches — the `NULL` sentinel is
mandatory and omitting it is undefined behaviour, not a compile error.

**Operations are three-operand and out-parameter first.** There is no operator overloading in C, so
`d = a * b + c` becomes a sequence of calls whose first argument is the destination:

```c
mpz_mul(t, a, b);      /* t = a * b   */
mpz_add(d, t, c);      /* d = t + c   */
mpz_addmul_ui(d, a, 7);  /* d += a * 7 — fused, no temporary */
```

Aliasing is explicitly allowed — `mpz_add(x, x, y)` is fine — which is what lets an accumulator loop
run without a scratch variable. It does not help with a simultaneous update. The Pell step in
Problem 582, $(X, Y) \mapsto (2X + 3Y,\ X + 2Y)$, reads both old values to make both new ones, so it
writes into two scratch variables and then calls `mpz_swap`, which exchanges the internals of the two
values and copies no limbs. The [digit DP](/blogs/technique/digit-dp) in Problem 776 turns over its
layers the same way, one `mpz_swap` per cell.

**The `_ui` / `_si` suffixes are the whole performance story at small scale.** Where one operand is a
machine word, the suffixed variant takes it directly (`mpz_mul_ui`, `mpz_add_ui`, `mpz_sub_ui`,
`mpz_cmp_ui`) and skips converting it into a temporary `mpz_t` first. In an inner loop that
difference is most of the cost. The division variants go one better and *return* the remainder as an
`unsigned long`: `r = mpz_fdiv_q_ui(q, n, d)` is Python's `q, r = divmod(n, d)` in one call, with
the small half landing straight in a machine word, ready to index a table (Problem 254 splits every
candidate by $9!$ this way). The same instinct explains `mpz_divexact_ui`, which divides when you
already know the division is exact and therefore skips computing a remainder, and `mpz_mul_2exp` /
`mpz_fdiv_q_2exp`, which are shifts rather than general multiply and divide.

Beyond arithmetic, the library ships the number-theoretic operations that would otherwise be the
hard part of the port, and these are exactly the ones the problems below reach for:

| Function | What it does | Where it earns its place |
| --- | --- | --- |
| `mpz_powm`, `mpz_powm_ui` | modular exponentiation $a^b \bmod m$ | [Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) primality once the modulus passes $2^{64}$ (Problem 387); a power of ten whose exponent has a thousand digits, under a one-word modulus (Problem 1006) |
| `mpz_bin_uiui` | an exact [binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) $\binom{n}{k}$ | Pascal-triangle entries far past 64 bits (Problem 203) |
| `mpz_set_str`, `mpz_get_str` | decimal string ↔ value, any base | writing a bound like $10^{100}$ or $10^{25}$ as a literal, and printing the result (Problems 168, 169) |
| `mpz_sqrt`, `mpz_perfect_square_p` | exact $\lfloor\sqrt{x}\rfloor$, and a perfect-square test | the first term of a continued fraction, and rejecting a square $d$ before a Pell search (Problem 581) |
| `mpz_sizeinbase` | digit or bit count without materialising the string: exact in a power-of-two base, possibly one too many otherwise | checking that the answer fits its output buffer before `mpz_get_str` writes it (Problem 254). It is a bound, not a count, so Problem 776, whose decimal exponent must be right, counts the digits `mpz_get_str` actually wrote |
| `mpz_import` | a value from an array of raw words | moving an `unsigned __int128` total into an `mpz_t` in one call, as its two 64-bit halves (Problem 844) |
| `mpz_ui_pow_ui`, `mpz_pow_ui` | exact powers | scaling a probability to an integer before dividing (Problem 239) |
| `mpq_*` with `mpq_canonicalize` | exact rationals, kept in lowest terms | a sum of fractions that must be compared for exact equality (Problem 180), or rounded only once, at the end (Problem 523) |
| `gmp_printf`, `gmp_snprintf` | `printf` with `%Zd` / `%Qd` conversions for `mpz_t` / `mpq_t` | printing a fixed-point decimal straight into the answer buffer, and a `--show` trace of the exact rational (Problem 523) |

The `mpq_*` row is worth separating out. `mpq_t` is a numerator/denominator pair of `mpz_t`s with
accessors `mpq_numref` / `mpq_denref`; arithmetic reduces through a
[GCD](https://en.wikipedia.org/wiki/Greatest_common_divisor) on every operation, exactly as Python's
[`Fraction`](https://docs.python.org/3/library/fractions.html) does. It is the direct translation
when the Python used `Fraction`, and it is the right tool when the *problem* is about exactness —
[exact arithmetic for equality](/blogs/takeaway/exact-arithmetic-for-equality). But when you only
need to compare two ratios, cross-multiplying with plain `mpz_t` ($ad$ versus $bc$) avoids the
normalisation entirely; that is why the continued-fraction work in Problem 192 stays in `mpz_t` and
compares products, rather than building rationals.

Problem 523 shows the other common use of `mpq_t`: an expected value that is a sum of fractions
with different denominators, which the problem wants rounded to two decimals. The Python sums
`Fraction`s and rounds once at the end. The C port does the same, with an `mpq_add` accumulator, and
then rounds using only integer operations, so no `double` is ever involved:

```c
mpq_mul(shifted, shifted, value);              /* value · 10^d                     */
mpq_add(shifted, shifted, half);               /* + 1/2: round half up             */
mpz_fdiv_q(scaled, mpq_numref(shifted), mpq_denref(shifted));   /* floor          */
mpz_fdiv_qr(whole, frac, scaled, scale);       /* split at the decimal point       */
gmp_snprintf(out, size, "%Zd.%0*Zd", whole, d, frac);
```

That is a translation of Python's `floor(x·10^d + ½)` followed by `divmod`, and the `%0*Zd` keeps
the leading zeros of the fractional part. One more rule is worth knowing. Every `mpq_*` arithmetic
function assumes its operands are already in lowest terms. If you assign a numerator and a
denominator directly, through `mpq_set_num` or `mpq_denref` as Problem 523 does for each
$(2^k-1)/(k+1)$ term, you must call `mpq_canonicalize` before you use the value. Forgetting it does
not raise an error. The arithmetic simply gives wrong answers.

Problem 776 adds a rule about where the rational belongs. It sums $n/d(n)$ over about $10^{18}$
values of $n$, and a digit DP groups the terms by digit sum, so every DP state is a plain integer. The
DP therefore runs on arrays of `mpz_t` and pays for no GCD. `mpq_t` appears only after it, for the
171 or so terms $T(s)/s$, whose common denominator can reach 74 digits. Rationals inside the DP
would reduce on every update for no benefit, and a `double` at the end could misround the 13th
significant digit. Keep integers for as long as the state is integral, and convert to `mpq_t` at the
one point where the division happens.

In this repository the build glue is already done: `scripts/c/compile.sh` greps the source for
`#include <gmp.h>` and appends `-lgmp` to the `gcc` line (and `-lmpfr -lgmp`, in that order, for
`#include <mpfr.h>`). The header comes from `libgmp-dev`, installed by `make install-all`. Add the
include and the linking follows.

## How to reason about it

**Reach for it at the top of the ladder, not the bottom.** 64-bit native → `__int128` → a
hand-rolled base-$10^9$ bignum → GMP. Each rung costs something, and GMP's cost is that every value
is heap-allocated and every operation is a function call. Stop at the lowest rung that provably
holds; a bound like "the count of 18-digit strings is under $10^{18}$" is a proof that you do not
need this page at all.

**Hybridise when most of the work is small.** The most effective shape here is a native fast path
with a GMP fallback: run the loop in `unsigned __int128` while the operands stay under $2^{64}$ and
promote to `mpz_t` only above it. Problem 387 carries a small `mpz_set_u128` bridge for exactly
this — 128-bit modular arithmetic is a few instructions, `mpz_powm` is a call into a library, and
you want the second only where the first would wrap. The guard need not be a value comparison.
Problem 254 builds each candidate as a string of decimal digits, so it branches on the *length*:
nineteen digits or fewer always fit an `unsigned long long`, and only a longer candidate goes
through `mpz_set_str`. The fast path covers the dense part of the scan, and GMP handles the few
large candidates where one or two settle the answer.

**The guard can test doubt instead of size.** Problem 558 makes about $10^9$ digit decisions in a
non-integer base. Each one is the sign of $a + br + cr^2$, with $r$ irrational and $a, b, c$ integers
that fit `int64_t`. The operands are never large, so a size guard has nothing to test. What can go
wrong is the sign, because a fixed-point estimate using rounded $r$ and $r^2$ can land inside its own
error bound. The port uses the shape of an
[adaptive exact predicate](https://www.cs.cmu.edu/~quake/robust.html): compute cheaply, keep an error
bound, and pay for exactness only when the estimate cannot decide.

```c
x = fixed_eval(a, b, c);        /* native words, wrong by at most err */
if (x >  err) return 1;
if (x < -err) return 0;
return exact_sign(a, b, c);     /* GMP, and only here */
```

The exact branch takes the sign of a [field norm](https://en.wikipedia.org/wiki/Field_norm), a cubic
in coefficients near $2^{47}$, which is past `__int128`. On the main input it fires about three times
in a million decisions, so the function can afford its own `mpz_inits` and `mpz_clears` on every call.
The advice to hoist allocation applies to the hot path, and this is not the hot path. The estimate has
a trick of its own. It lets the products wrap in `uint64_t`, because the true sum fits in 63 bits and
arithmetic modulo $2^{64}$ recovers it exactly. The wrapping must be unsigned, since signed overflow
is undefined in C.

**Know which inputs actually need the bignum.** Python reaches a width boundary without noticing,
so check where the port actually crosses it. In Problem 254, every value for the problem's own
bound fits in 64 bits. GMP is in the C port so that the same code also handles the stress input
($i \le 500$), where the count of nines reaches about $10^{51}$. That is a good reason to link it,
but say so in the source. A reader who sees `mpz_t` will otherwise assume the stated problem
overflows, and anyone who later tries to remove GMP needs to know which input breaks without it.
Problem 523 sits on the same boundary from the other direction. At the problem's own size, the
reduced numerator of the sum is only a couple of bits past $2^{64}$, so an `__int128` fraction would
technically hold it. `mpq_t` is still the better choice there. It is the line-for-line translation
of `Fraction`, its GCD reduction comes for free, and it keeps working when $n$ grows and $2^n$ takes
over.

**The bignum may be the index, not the data.** Problem 1006 reverses the usual shape. It walks
[matrix products](/blogs/takeaway/running-totals-as-matrix-products) along the
[Fibonacci word](/blogs/domain/fibonacci-word), and every entry stays below a nine-digit modulus, so
a ten-term dot product fits `uint64_t` and the hot loop never touches GMP. But the extra case sets
$k = 10^{1000}$, so `mpz_t` holds $k$, the block lengths and the exponents. Only that bookkeeping,
which says how far to walk, needs a bignum, and that is why the port stays fast at that size. Ask of
each variable which of the two it is, because often only the control path has to be wide.

Inputs like that fail before any arithmetic starts. The runner's `parse_int` returns a `long long`, so
Problems 582, 776 and 1006 each parse their own argument into an `mpz_t`, `10**100` notation included.
When the input does not fit a word, the first GMP call in the port is in the parser.

**An irrational rarely needs `mpf_t`.** None of these problems uses it. If what you want is the floor
of something irrational, an integer square root is exact:
$\lfloor n\sqrt{5} \rfloor = \lfloor \sqrt{5n^2} \rfloor$ is an `mpz_mul`, an `mpz_mul_ui` and an
`mpz_sqrt`. That is how Problem 1006 reads one letter of the Fibonacci word at a position near
$10^{1000}$, with no precision to choose and no rounding to bound. For a root with no closed form,
scale it. Problem 558 finds $\lfloor r \cdot 2^{200} \rfloor$ by integer bisection, testing each
midpoint against the cubic with the powers of two cleared, so every comparison is an exact integer
sign. It then rounds that value to word-sized constants, and GMP is done until the fallback above.
This is the useful shape for a constant: build it wide once, then run the loop narrow.

**Expect a 5–20× win over CPython when GMP does the work, and more when it mostly stays out of
it.** On this project's benchmarks, on the same test case with the same approach, the GMP port beats
the Python original by 12× on Problem 192 ($4.2$ s → $332$ ms), 20× on Problem 180 ($1.6$ s →
$81$ ms), 12× on Problem 387 ($2.0$ s → $166$ ms) and 5× on Problem 239 ($857$ ms → $179$ ms). But
Problem 321, whose values are big yet whose loop is trivially short, gains only about 1.3× —
per-operation overhead is the same in both, and there is not enough arithmetic for the asymptotics
to matter. Problem 605 goes further and comes out slightly slower in C ($4.3\,\mu$s → $5.1\,\mu$s):
it is a handful of modular powers, and at that scale the timing measures call overhead, not
arithmetic. At the other end, Problem 254 gains 81× ($1.43$ s → $18$ ms). That is not because GMP is
fast. The hot loop runs over a million candidates on native words and table lookups, and the
interpreter's cost per candidate is what the port removes. Problem 1006 gains 38× ($5.4$ ms →
$0.14$ ms) the same way, since nearly all of its time goes into matrix products on native words. In
short, the speedup comes from the work the bignum does not do. CPython's `int` is itself a competent bignum (30-bit digits, Karatsuba
above a threshold); GMP wins on tuning and on not paying for object allocation per result, not by
magic. Where a Python solution is slow because
of its *algorithm*, porting it to GMP will faithfully reproduce the slowness —
[algorithm beats language](/blogs/takeaway/algorithm-beats-language).

**The pitfalls are all about lifetime.** `mpz_init` inside a loop body without a matching
`mpz_clear` is the classic leak, and it is invisible until the benchmark's `--runs=N` amplifies it;
initialise once outside the loop and reuse, since a re-`set` value costs nothing extra. Conversely,
`mpz_clear` on an uninitialised value, or a second `mpz_init` on a live one, corrupts the heap
quietly. Two smaller traps: the `NULL` terminator on `mpz_inits`/`mpz_clears`, and `mpz_get_str`,
which allocates with GMP's own allocator when passed a `NULL` buffer — either free it through
`mp_get_memory_functions` or, more simply, size a stack buffer with `mpz_sizeinbase(x, 10) + 2` and
pass that.

**Leaving `mpz_t` is the one unchecked step.** `mpz_get_ui` keeps only the low bits of a value that
does not fit, and it says nothing. Every exit to a machine word therefore needs a reason, written
down or tested with `mpz_fits_ulong_p`. Problem 581 is a clean example: at $p = 59$ its $d$ is past
$2^{64}$, yet it calls `mpz_get_ui` on the Pell $y$, because the search has already stopped any $y$
above $10^{10}$. The cap is what makes the conversion safe, so the two belong together.

**Keep the numbers small before you make them big.** GMP's cost grows with the operand size, so the
reductions that matter most are the ones that stop growth: work modulo something and the values
never leave a machine word ([modular arithmetic](/blogs/domain/modular-arithmetic)); track a digit
count instead of the digits; carry the last $k$ digits when the question only asks for them.
Problem 254 is the extreme case. The number it reasons about has about $10^{10}$ digits, far too
many to build even with GMP. So the solution stores it as a pair: how many nines it starts with,
plus a residue below $9!$ that encodes the remaining digits. The only bignum is that count of nines,
and the answer, a digit sum, follows from the pair directly. A
`mpz_t` that exists because nobody
[reduced the problem before coding](/blogs/takeaway/reduce-before-coding) is a self-inflicted
constant factor.

**When the value is not worth building, GMP can hold the modulus instead.** Problem 605 wants the numerator and
denominator of a fraction in lowest terms, taken modulo $10^8$, and the denominator comes from
$2^n - 1$ with $n = 10^8 + 7$, a number of thirty million digits. The solution never forms it and
works only in residues. The difficulty is the reduction, because the common factor $g$ need not be
invertible modulo $10^8$, so no modular inverse is available. The fix is to raise the modulus rather
than invert:

$$g^2 \mid x \implies \frac{x \bmod m g^2}{g^2} \equiv \frac{x}{g^2} \pmod{m}.$$

`mpz_powm_ui` works modulo $10^8 g^2$, `mpz_divexact` removes $g^2$, and `mpz_mod_ui` comes back down
to $10^8$. The same port reads $p$-adic valuations from residues modulo $p^{64}$. In both places GMP
is present because the *modulus* outgrows a word, while the values it stands for are never built. On
the main input $g = 1$ and the lift does nothing. It exists for inputs such as the $n = 6$ example,
where $g = 3$.

**Reduce to save work, not out of habit.** Problem 844 makes the opposite choice on purpose. Its answer
is modular too, but the port carries polynomial coefficients and power sums exactly, up to about
$10^{340}$, and reduces once at the end with `mpz_fdiv_r_ui`. There are only a few dozen closed-form
sums, so 340-digit operands cost almost nothing. The power-sum recurrence divides by $j + 1$, which
`mpz_divexact_ui` does directly and a residue would need an inverse for, and the example cases with
no modulus run through the same code. The thing to weigh is operand size times operation count.
Thirty million digits is a poor trade in Problem 605, where residues finish in microseconds, and a
few dozen sums make exact arithmetic the simpler choice here.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0168](/solutions/0168/) — Number Rotations
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0176](/solutions/0176/) — Common Cathetus Right-angled Triangles
- ● [0178](/solutions/0178/) — Step Numbers
- ● [0180](/solutions/0180/) — Golden Triplets
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0239](/solutions/0239/) — Twenty-two Foolish Primes
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0387](/solutions/0387/) — Harshad Numbers
- ● [0523](/solutions/0523/) — First Sort I
- ● [0558](/solutions/0558/) — Irrational Base
- ● [0581](/solutions/0581/) — $47$-smooth Triangular Numbers
- ● [0582](/solutions/0582/) — Nearly Isosceles $120$ Degree Triangles
- ● [0605](/solutions/0605/) — Pairwise Coin-Tossing Game
- ● [0776](/solutions/0776/) — Digit Sum Division
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ● [1006](/solutions/1006/) — Fibonacci Subwords

<!-- /problems -->
