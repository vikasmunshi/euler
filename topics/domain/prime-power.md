<!-- tags: [prime-power] -->
<!-- status: final 2026-10-19T06:51Z -->
# Prime power

A [prime power](https://en.wikipedia.org/wiki/Prime_power) is a number $p^k$ with $p$ prime
and $k \ge 1$: 2, 3, 4, 5, 7, 8, 9, 11, 13, 16, … ([OEIS A246655](https://oeis.org/A246655)).
[Prime numbers](/topics/number-theory/prime-numbers) covers the wider picture: unique factorisation,
the distribution of primes, and arithmetic modulo a prime. This page covers what is specific to the
*powers*. Unique factorisation says every integer is a product of prime powers, one per prime. That
makes prime powers the **atoms** in three recurring ways. They are the terms you enumerate, with a
bound that tightens quickly as $k$ grows. They are the moduli that the Chinese remainder theorem splits a
composite modulus into. And they are the building blocks of the lcm and of every multiplicative function. The
solved problems below use one each: enumeration (87), CRT components (160), and the lcm (772).

## The idea — one atom per prime

**Bounds shrink with the exponent.** $p^k \le N$ means $p \le N^{1/k}$. There are about $\sqrt N / \ln \sqrt N$ prime squares
below $N$, but far fewer cubes and fourth powers. In any enumeration of sums or products of prime
powers, the high-exponent terms form the short outer loops and the squares the long inner one. The number of prime
powers $\le N$ that are *not* primes is only $O(\sqrt N / \log N)$.

**Moduli split into prime powers.** $m = \prod p_i^{k_i}$ and, by
[CRT](/topics/technique/chinese-remainder-theorem), arithmetic mod $m$ is arithmetic mod each
$p_i^{k_i}$ independently. That matters when the quantity *shares factors with the modulus*. Division
by $p$ is impossible mod $m$, but within the $p^k$ component you can count the factors of $p$
separately ([Legendre's formula](/topics/domain/legendres-formula)) and work in the units group
$(\mathbb{Z}/p^k)^\times$, which is cyclic for odd $p$.

**The lcm picks the highest power of each prime.**
$\operatorname{lcm}(1, \dots, n) = \prod_{p \le n} p^{\lfloor \log_p n \rfloor}$, where each factor is the largest power of $p$ not exceeding $n$.
Equivalently, $\ln \operatorname{lcm}(1..n) = \psi(n) = \sum_{p^k \le n} \ln p$, the Chebyshev function,
which sums the [von Mangoldt function](https://en.wikipedia.org/wiki/Von_Mangoldt_function), and that
function is nonzero exactly on prime powers. Only primes $p \le \sqrt n$ have exponent above 1, so the
product splits into a short loop over small primes and a plain product of the rest.

## Three uses across the problems

**87, prime power triples: bases bounded by roots.** Count the distinct $p^2 + q^3 + r^4 < 5 \times 10^7$.
One sieve to $\sqrt N \approx 7071$ covers all three roles, because the square has the loosest bound. The
fourth powers need only primes up to about 84 and the cubes up to about 368. The loops are nested from
the highest exponent outward and break as soon as a partial sum passes its budget, because each list is ascending.
The public Python:

```python
for quadruple in prime_powers(primes, 4):
    if quadruple > max_quadruple:
        break
    for cube in prime_powers(primes, 3):
        if (quadruple_cube := (quadruple + cube)) > max_quadruple_cube:
            break
        for square in prime_powers(primes, 2):
            if (number := (quadruple_cube + square)) >= max_num:
                break
            numbers.add(number)
```

**160, factorial trailing digits: work modulo each prime power.** The last five non-zero digits of
$10^{12}!$ are the residue mod $10^5 = 2^5 \cdot 5^5$, after dividing out $10^z$. Neither 2 nor 5 can be
divided out modulo $10^5$ directly, so the solution splits into the two prime-power components. Mod
$5^5$, the factors of 5 are stripped from $N!$ structurally. The units mod $5^5$ repeat with period
$5^5$, and a full period multiplies to $-1$ by the
[generalised Wilson theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem#Gauss's_generalization),
so only a tail product and a recursion on $\lfloor N/5 \rfloor$ remain. The leftover $2^{-z}$ is a modular
inverse. Mod $2^5$ the same idea applies with sign $+1$. CRT then glues the two residues back together. The prime-power
split is what makes "divide by $10^z$" possible at all.

**772, balanceable $k$-bounded partitions: the lcm as a prime-power product.** A divisibility argument
reduces the answer to $\operatorname{lcm}(1, \dots, 10^8)$ modulo $10^9 + 7$. The lcm is computed as
$\prod p^{\lfloor \log_p k \rfloor}$. The 1229 primes up to $\sqrt{k} = 10^4$ each get a short loop to
find their top power, and the other 5.76 million primes up to $k$ each contribute a single factor of
$p$, already below the modulus.

The unsolved problems on the list use prime powers as structure in the same way. **578** counts integers
whose prime-power exponents decrease. **634** counts numbers of the form $a^2b^3$. **639** sums a
multiplicative function defined by its values on prime powers.

## Python and C

- **87**: Python deduplicates sums in a `set`, with memory proportional to the roughly one million distinct values.
  C uses a direct-addressed `calloc`'d byte array of $5 \times 10^7$ entries, which is 50 MB but needs no
  hashing. Python generates powers lazily so the `break`s skip unused ones. C casts to `long long`
  before forming $p^4$.
- **160**: Python's `pow(2, -z, M5)` gives the inverse power directly, and `pow(M2, -1, M5)` the
  CRT coefficient. C writes an extended-Euclid `modinv` and a `modpow`. The unit-product table has
  $p^5 + 1$ entries, so it lives on the stack in C (3126 `long long`s) and is rebuilt on each call in both languages.
- **772**: Python takes all primes up to $10^8$ as a NumPy array from `primesieve.numpy`, finds the
  $\sqrt k$ cut with `searchsorted`, and multiplies in two `.tolist()` loops. C sieves into its own
  **bit-packed** array, one bit per number, about 12.5 MB, and multiplies in `unsigned long long`.
  Both operands are below $1.1 \times 10^9$, so each product is below $1.2 \times 10^{18}$ and needs no
  `__int128`.

## How to reason about it

- **Order nested enumerations by exponent.** Highest power outermost, with the tightest bound and
  shortest list, and break on ascending lists.
- **Split a composite modulus into prime powers when the value shares its factors.** Count the
  shared prime with Legendre, work with units mod $p^k$, and recombine with CRT.
- **Compute the lcm of a range as a prime-power product.** The highest power of each prime not above $n$, with only
  primes up to $\sqrt n$ needing a loop.
- **Remember that multiplicative functions are defined on prime powers.** Once you know $f(p^k)$,
  sieves and Dirichlet methods do the rest. See [linear sieve](/topics/technique/linear-sieve).
- **Count prime powers cheaply.** Beyond the primes themselves, there are only $O(\sqrt N)$
  proper prime powers below $N$, few enough to list explicitly.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0087](/solutions/0087/) — Prime Power Triples
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ○ [0578](/solutions/0578/) — Integers with Decreasing Prime Powers
- ○ [0634](/solutions/0634/) — Numbers of the Form $a^2b^3$
- ○ [0639](/solutions/0639/) — Summing a Multiplicative Function
- ● [0772](/solutions/0772/) — Balanceable $k$-bounded Partitions
- ○ [0846](/solutions/0846/) — Magic Bracelets

<!-- /problems -->
