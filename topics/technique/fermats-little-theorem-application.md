<!-- tags: [fermats-little-theorem-application] -->
<!-- status: final -->
# Fermat's little theorem (application)

[Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem) is one line of
number theory that pays for itself over and over in code. The theorem itself is the *domain* page
[Fermat's little theorem](/topics/domain/fermats-little-theorem); this page is about the **use** —
the four distinct jobs a working solution asks it to do, all of which turn an expensive or
outright infinite computation into a single
[modular exponentiation](/topics/technique/modular-exponentiation). Once you have the habit, you
stop seeing a theorem and start seeing a tool with four settings.

## The one line

For a prime $p$ and any integer $a$ not divisible by $p$,

$$a^{\,p-1} \equiv 1 \pmod p.$$

Everything below is a consequence of reading that identity in a different direction. Multiply both
sides by $a^{-1}$ and it gives you **division**. Read it as a statement about the exponent and it
**bounds the order** of $a$. Split the exponent and it **manufactures roots of unity**. Reduce the
exponent and it **shrinks an astronomically large power** to one of ordinary size. The
hypothesis that does all the work is *$p$ prime* — the identity is exactly the statement that the
nonzero residues mod $p$ form a [group](https://en.wikipedia.org/wiki/Multiplicative_group_of_integers_modulo_n)
of order $p-1$ under multiplication, so $a^{p-1}$ is the identity by
[Lagrange's theorem](https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory)).

## Setting 1 — division in a prime modulus

The most common use by a wide margin. Since $a \cdot a^{p-2} = a^{p-1} \equiv 1$, the
[modular inverse](/topics/domain/modular-multiplicative-inverse) is just another power:

$$a^{-1} \equiv a^{\,p-2} \pmod p.$$

In Python that is the whole implementation — `pow(a, p - 2, p)` — and in C it is one call to the
same binary [exponentiation by squaring](/topics/technique/exponentiation-by-squaring) routine you
already wrote for everything else. This is why the counting problems that hand you the modulus
$1\,000\,000\,007$ hand you a *prime* one: it makes the ring a field, so every formula that divides
— a geometric series $\frac{p^{e+1}-1}{p-1}$, a binomial coefficient, a ratio between consecutive
terms of a recurrence — survives being carried mod $M$ intact. Problems 650, 743 and 926 all lean
on it for exactly that: 650 evaluates the divisor-sum $\sigma$ as a product of geometric series and
needs $(p-1)^{-1}$ for each prime; 743 builds a trinomial-coefficient sum from the ratio
$t_j / t_{j-1}$, which carries a division by $j$; 926 multiplies a running product into a sweep and
must divide the same factor back out later. Problem 675 is the same move at scale: it walks a
multiplicative function along $1!, 2!, 3!, \dots$, and each step replaces one prime's factor
$2e' + 1$ by $2e + 1$ — a running product that has to divide out what the previous step put in.
Its modulus, $1\,000\,000\,087$, is chosen prime for no other reason. Nor need a modulus look
like $10^9+7$ to qualify: 860 counts fair games mod $989\,898\,989$, which is also prime, and
that is the one fact that licenses its binomial coefficients.

The trade-off is that $a^{p-2}$ costs about $\log_2 M \approx 30$ modular multiplications, so an
inverse is roughly thirty times a multiply — cheap once, ruinous in a hot loop. Four habits
follow, in increasing order of payoff:

- **Hoist the constant ones.** An inverse of a value that does not change between iterations
  belongs outside the loop. In 743 the inner loop runs $5 \times 10^7$ times and computes one fresh
  inverse per iteration; that single choice dominates the whole runtime, and it is visible in the
  profile long before it is visible in the code.
- **Precompute a table** when you need $1^{-1} \dots n^{-1}$: the recurrence
  $\mathrm{inv}[i] = -\lfloor M/i \rfloor \cdot \mathrm{inv}[M \bmod i] \bmod M$ fills all $n$ in
  $O(n)$ multiplications, not $O(n \log M)$. If you do exponentiate per entry, as 675 does for its
  table of $(2e+1)^{-1}$, do it *vectorised* — one square-and-multiply over the whole array, so the
  thirty steps are thirty array operations rather than thirty times $n$ interpreter steps.
- **Batch with [Montgomery's trick](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Multiple_inverses)**
  when the values are arbitrary: multiply $n$ residues into one running product, take *one*
  inverse, then unwind. That is $3n$ multiplications and a single exponentiation for $n$ inverses.
  The factorial table is the special case everyone meets first, and 860 uses it as written: build
  $k!$ upward, invert only $n!$, then walk down with $(k-1)!^{-1} = k!^{-1} \cdot k$, after which
  every $\binom{n}{k}$ is three multiplications.

  ```python
  inverse_factorial[n] = pow(factorial[n], M - 2, M)
  for k in range(n, 0, -1):
      inverse_factorial[k - 1] = inverse_factorial[k] * k % M
  ```
- **Defer the division to the very end.** The strongest habit is to need no inverse in the loop
  at all. 739 sums a ballot-number weight $k\binom{2n-3-k}{n-2}/(n-1)$ against every term; rather
  than invert anything per term, it multiplies each term through by the common denominator
  $(n-1)\,(n-2)!$, so what remains is a prefix product times a suffix product — pure
  multiplication, vectorisable — and a single inverse of that denominator finishes the job. The
  prime modulus is what guarantees the denominator is invertible at all.

## Setting 2 — bounding the multiplicative order

The [multiplicative order](/topics/domain/multiplicative-order) of $a$ mod $p$ is the smallest
$d > 0$ with $a^d \equiv 1$. Fermat says $a^{p-1} \equiv 1$, and the set of exponents killing $a$ is
closed under subtraction, so

$$d \mid p - 1.$$

That single divisibility is what makes order-flavoured questions finite. The naive way to find $d$
is to multiply until you come back to $1$ — as the public problem 26
(`solutions/public/p0026/`) does, since there the modulus is small enough that $O(m)$ is fine:

```python
def multiplicative_order(a: int, modulus: int) -> int | None:
    """Smallest k with a**k ≡ 1 (mod modulus), or None if a is not coprime to modulus."""
    r = 1
    for k in range(1, modulus):
        r = r * a % modulus
        if r == 1:
            return k
    else:
        return None
```

For a large prime that loop is hopeless, and Fermat replaces it: factor $p-1$, and the order is
the divisor of $p-1$ you land on by peeling prime factors off the exponent while the power stays
$1$. Better still, most questions never need $d$ itself — they need to know whether $d$ divides
some target $t$, and *that* is one exponentiation:

$$d \mid t \iff a^{\,t} \equiv 1 \pmod p.$$

Problem 133 is the clean example. It asks which primes can never divide a
[repunit](https://en.wikipedia.org/wiki/Repunit) $R(10^n)$ — an infinite quantifier over $n$. Since
$R(k) \equiv 0$ means $10^k \equiv 1$, the question is whether the order of $10$ divides some power
of ten, i.e. whether that order is [5-smooth](https://en.wikipedia.org/wiki/Smooth_number). Fermat
bounds the order by $p-1$, so writing $p - 1 = 2^{a} 5^{b} r$ with $\gcd(r,10)=1$, the order is
$2$-$5$ smooth exactly when it divides $m = 2^a 5^b$ — and one `pow(10, m, p)` settles a prime
forever, with no factoring and no order computation. An infinite search became a `== 1` test.

## Setting 3 — manufacturing roots of unity

If $r \mid p - 1$, then for any base $a$,

$$g = a^{(p-1)/r} \bmod p \quad\Longrightarrow\quad g^{\,r} = a^{\,p-1} \equiv 1 \pmod p,$$

so $g$ is an $r$th [root of unity](/topics/domain/root-of-unity) by construction — and it is a
*primitive* one unless $a$ happened to be an $r$th power, a case you detect for free because then
$g = 1$. A fraction $(r-1)/r$ of bases work, so trying $a = 2, 3, 5, \dots$ terminates almost
immediately. Once you hold a primitive $g$, the rest of the subgroup is $g^2, \dots, g^{r-1}$ by
plain multiplication — no further exponentiation.

This is how problem 421 counts solutions of $n^{15} \equiv -1 \pmod p$ for every prime below
$10^8$. The [cyclic group](/topics/domain/cyclic-group) mod $p$ has a unique subgroup of order
$\gcd(15, p-1)$, whose size is decided by the two cheap tests $p \equiv 1 \pmod 3$ and
$p \equiv 1 \pmod 5$; the members are then built by the construction above for $r = 3$ and $r = 5$
and combined, since a cyclic group of order 15 is the direct product of its subgroups of orders 3
and 5. The whole per-prime cost is one modular exponentiation, and the algorithm scales with the
*number of primes* rather than with the size of the range being counted.

The same construction underlies [primitive roots](/topics/domain/primitive-root) (take $r = p-1$),
[Tonelli–Shanks](https://en.wikipedia.org/wiki/Tonelli%E2%80%93Shanks_algorithm) square roots mod
$p$ (the case $r = 2$, extended), and the choice of an NTT-friendly modulus, where you want a
$2^k$th root of unity to exist and so pick $p = c \cdot 2^k + 1$.

## Setting 4 — shrinking the exponent

Exponents mod $p$ live modulo $p - 1$: write $e = q(p-1) + r$ and the $q$ full cycles vanish, so

$$a^{\,e} \equiv a^{\,e \bmod (p-1)} \pmod p \qquad (p \nmid a).$$

This matters when the exponent itself is too large to hold. Problem 822 starts with the list
$2, 3, \dots, n$ and repeatedly squares its smallest member, for a number of rounds far beyond
anything you could simulate. After a short warm-up the squarings settle into a round-robin, so
each $x$ ends up as $x^{2^{k}}$ with a $k$ you can compute — but $2^k$ is a number with an
astronomical count of digits, and $x^{2^k}$ is beyond any storage. Reducing the exponent first
makes it two ordinary exponentiations:

```python
pow(x, pow(2, k, p - 1), p)
```

The inner `pow` works modulo $p - 1$, which is *not* prime — that is fine, because it only
multiplies, never divides. Two pitfalls. First, the hypothesis $p \nmid a$ is now load-bearing: if
$a \equiv 0$, reducing $e$ to $0$ turns the correct answer $0$ into $1$ (822 is safe because every
base is below the modulus). Second, a deeper tower $a^{b^{c}}$ needs the exponent's exponent
reduced modulo the order of $b$ mod $p - 1$ — Euler's theorem with $\varphi(p-1)$, or better the
[Carmichael function](https://en.wikipedia.org/wiki/Carmichael_function) — and since $p - 1$ is
even, $b$ need not be coprime to it, which is where the clean rule ends and care begins.

## The converse does not hold

Reading Fermat backwards gives the [Fermat primality test](https://en.wikipedia.org/wiki/Fermat_primality_test):
if $a^{n-1} \not\equiv 1 \pmod n$ then $n$ is certainly composite. The failure to conclude the
opposite is not a technicality — [Carmichael numbers](https://en.wikipedia.org/wiki/Carmichael_number)
such as $561 = 3 \cdot 11 \cdot 17$ pass for *every* base coprime to them, and there are infinitely
many. Use the test as a fast composite filter and follow it with
[Miller–Rabin](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test), which is the same
exponentiation plus a check on the square roots of 1 encountered along the way.

## How to reason about it

The cue is a **prime modulus** in a computation that wants to divide, an **order** question
phrased over an unbounded range, or an **exponent too large to write down**. When you catch it:

- **Check the hypothesis before the identity.** $p$ must be prime and $a \not\equiv 0$. For a
  composite modulus the analogue is [Euler's theorem](/topics/domain/eulers-totient-function),
  $a^{\varphi(m)} \equiv 1$ for $\gcd(a,m)=1$, which needs $\varphi(m)$ — usually you are better off
  with the [extended Euclidean algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm),
  which inverts in $O(\log m)$ without factoring anything and is the right default when the modulus
  is not known-prime.
- **Prefer "does it divide?" to "what is it?"** Testing $a^t \equiv 1$ is one exponentiation;
  computing the order needs $p-1$ factored. Most problems only ever ask the first question.
- **Count your exponentiations.** They are the unit of cost in this whole family. One per prime
  scales beautifully; one per inner-loop iteration usually does not.
- **Mind the width.** A modular multiply forms a product of two residues below $M$, so $M^2$ must
  fit the machine word — with $M$ near $10^9$ that is fine in 64 bits, but a 63-bit modulus needs
  `__int128` in C. Python has no such trap, and `pow(a, b, m)` is already the fast path.

The theorem is one line; the leverage comes from knowing which of its four readings the problem in
front of you is asking for.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0133](/solutions/0133/) — Repunit Nonfactors
- ● [0421](/solutions/0421/) — Prime Factors of $n^{15}+1$
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0675](/solutions/0675/) — $2^{\omega(n)}$
- ● [0739](/solutions/0739/) — Summation of Summations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0822](/solutions/0822/) — Square the Smallest
- ● [0860](/solutions/0860/) — Gold and Silver Coin Game
- ● [0926](/solutions/0926/) — Total Roundness

<!-- /problems -->
