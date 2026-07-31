<!-- tags: [gmp] -->
<!-- status: final -->
# GMP

[GMP](https://gmplib.org/) — the GNU Multiple Precision Arithmetic Library — is the bignum library
you link when the C port of a Python solution runs out of bits. Python's `int` is unbounded, so a
solution that sums 100-digit values, counts 18-digit arrangements or keeps an exact rational never
announces that it needs big integers; the translation to C does, loudly, at the first silent
overflow. `__int128` buys about 38 digits and stops there. Past that line the honest options are to
[hand-roll a bignum](/topics/technique/arbitrary-precision-arithmetic/) or to link GMP, and every
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
run without a scratch variable.

**The `_ui` / `_si` suffixes are the whole performance story at small scale.** Where one operand is a
machine word, the suffixed variant takes it directly (`mpz_mul_ui`, `mpz_add_ui`, `mpz_sub_ui`,
`mpz_cmp_ui`) and skips converting it into a temporary `mpz_t` first. In an inner loop that
difference is most of the cost. The same instinct explains `mpz_divexact_ui`, which divides when you
already know the division is exact and therefore skips computing a remainder, and `mpz_mul_2exp` /
`mpz_fdiv_q_2exp`, which are shifts rather than general multiply and divide.

Beyond arithmetic, the library ships the number-theoretic operations that would otherwise be the
hard part of the port, and these are exactly the ones the problems below reach for:

| Function | What it does | Where it earns its place |
| --- | --- | --- |
| `mpz_powm`, `mpz_powm_ui` | modular exponentiation $a^b \bmod m$ | [Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test) primality once the modulus passes $2^{64}$ (Problem 387) |
| `mpz_bin_uiui` | an exact [binomial coefficient](https://en.wikipedia.org/wiki/Binomial_coefficient) $\binom{n}{k}$ | Pascal-triangle entries far past 64 bits (Problem 203) |
| `mpz_set_str`, `mpz_get_str` | decimal string ↔ value, any base | writing a bound like $10^{100}$ or $10^{25}$ as a literal, and printing the result (Problems 168, 169) |
| `mpz_sizeinbase` | digit or bit count without materialising the string | a length test that would otherwise cost a full conversion |
| `mpz_ui_pow_ui`, `mpz_pow_ui` | exact powers | scaling a probability to an integer before dividing (Problem 239) |
| `mpq_*` with `mpq_canonicalize` | exact rationals, kept in lowest terms | a sum of fractions that must be compared for exact equality (Problem 180) |

That last row is worth separating out. `mpq_t` is a numerator/denominator pair of `mpz_t`s with
accessors `mpq_numref` / `mpq_denref`; arithmetic reduces through a
[GCD](https://en.wikipedia.org/wiki/Greatest_common_divisor) on every operation, exactly as Python's
[`Fraction`](https://docs.python.org/3/library/fractions.html) does. It is the direct translation
when the Python used `Fraction`, and it is the right tool when the *problem* is about exactness —
[exact arithmetic for equality](/topics/takeaway/exact-arithmetic-for-equality/). But when you only
need to compare two ratios, cross-multiplying with plain `mpz_t` ($ad$ versus $bc$) avoids the
normalisation entirely; that is why the continued-fraction work in Problem 192 stays in `mpz_t` and
compares products, rather than building rationals.

In this repository the build glue is already done: `scripts/c/compile.sh` greps the source for
`#include <gmp.h>` and appends `-lgmp` to the `gcc` line (and `-lmpfr -lgmp`, in that order, for
`#include <mpfr.h>`). The header comes from `libgmp-dev`, installed by `make install-all`. Add the
include and the linking follows.

## How to reason about it

**Reach for it at the third rung of the ladder, not the first.** 64-bit native → `__int128` → a
hand-rolled base-$10^9$ bignum → GMP. Each rung costs something, and GMP's cost is that every value
is heap-allocated and every operation is a function call. Stop at the lowest rung that provably
holds; a bound like "the count of 18-digit strings is under $10^{18}$" is a proof that you do not
need this page at all.

**Hybridise when most of the work is small.** The most effective shape here is a native fast path
with a GMP fallback: run the loop in `unsigned __int128` while the operands stay under $2^{64}$ and
promote to `mpz_t` only above it. Problem 387 carries a small `mpz_set_u128` bridge for exactly
this — 128-bit modular arithmetic is a few instructions, `mpz_powm` is a call into a library, and
you want the second only where the first would wrap.

**Expect a 5–20× win over CPython for the same algorithm — and much less on small values.** On this
project's benchmarks, on the same test case with the same approach, the GMP port beats the Python
original by 12× on Problem 192 ($4.2$ s → $332$ ms), 20× on Problem 180 ($1.6$ s → $81$ ms), 12× on
Problem 387 ($2.0$ s → $166$ ms) and 5× on Problem 239 ($857$ ms → $179$ ms). But Problem 321, whose
values are big yet whose loop is trivially short, gains only about 1.3× — per-operation overhead is
the same in both, and there is not enough arithmetic for the asymptotics to matter. CPython's `int`
is itself a competent bignum (30-bit digits, Karatsuba above a threshold); GMP wins on tuning and on
not paying for object allocation per result, not by magic. Where a Python solution is slow because
of its *algorithm*, porting it to GMP will faithfully reproduce the slowness —
[algorithm beats language](/topics/takeaway/algorithm-beats-language/).

**The pitfalls are all about lifetime.** `mpz_init` inside a loop body without a matching
`mpz_clear` is the classic leak, and it is invisible until the benchmark's `--runs=N` amplifies it;
initialise once outside the loop and reuse, since a re-`set` value costs nothing extra. Conversely,
`mpz_clear` on an uninitialised value, or a second `mpz_init` on a live one, corrupts the heap
quietly. Two smaller traps: the `NULL` terminator on `mpz_inits`/`mpz_clears`, and `mpz_get_str`,
which allocates with GMP's own allocator when passed a `NULL` buffer — either free it through
`mp_get_memory_functions` or, more simply, size a stack buffer with `mpz_sizeinbase(x, 10) + 2` and
pass that.

**Keep the numbers small before you make them big.** GMP's cost grows with the operand size, so the
reductions that matter most are the ones that stop growth: work modulo something and the values
never leave a machine word ([modular arithmetic](/topics/domain/modular-arithmetic/)); track a digit
count instead of the digits; carry the last $k$ digits when the question only asks for them. A
`mpz_t` that exists because nobody
[reduced the problem before coding](/topics/takeaway/reduce-before-coding/) is a self-inflicted
constant factor.

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
- ● [0321](/solutions/0321/) — Swapping Counters
- ● [0387](/solutions/0387/) — Harshad Numbers

<!-- /problems -->
