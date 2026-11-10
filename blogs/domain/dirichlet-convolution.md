<!-- tags: [dirichlet-convolution] -->
<!-- status: final 2026-11-09T16:59Z -->
# Dirichlet convolution

[Dirichlet convolution](https://en.wikipedia.org/wiki/Dirichlet_convolution) is the
multiplication that arithmetic functions use when they talk about divisors. Whenever a quantity
is "a sum over the divisors of $n$", it is a convolution $f * g$. Once you recognise one, you can
factor it, invert it, and, most usefully, sum it. All six problems below ask for
$\sum_{n \le N} F(n)$ at an $N$ (up to $10^{18}$) far past anything you can loop over, and in
every one the way in is the same. Write $F$ as a convolution in which one factor is *easy to sum*
and the other is *sparse*, then swap the order of summation.

## The idea

For arithmetic functions $f, g$,

$$(f * g)(n) = \sum_{d \mid n} f(d)\, g\!\left(\frac{n}{d}\right).$$

The operation is commutative and associative. Its identity is $\varepsilon$ ($1$ at $n=1$, $0$
elsewhere), and it has a small cast of named functions: the constant $\mathbf{1}$, the powers
$\mathrm{Id}^k(n) = n^k$, [Möbius](/blogs/domain/mobius-function) $\mu$ (the inverse of
$\mathbf{1}$), and [Euler's totient](/blogs/domain/eulers-totient-function) $\varphi$. The
identities worth knowing by heart are $\mu * \mathbf{1} = \varepsilon$, $\varphi * \mathbf{1} =
\mathrm{Id}$, and $\varphi = \mu * \mathrm{Id}$. The convolution of two
[multiplicative](/blogs/domain/multiplicative-function) functions is multiplicative, so every
function in this page is pinned down by its values on prime powers, and that is where you do the
algebra.

The identity that turns all of this into an algorithm comes from swapping the order of
summation. Write $n = dm$ and sum over $m$ first:

$$\sum_{n \le N} (f * g)(n) = \sum_{d \le N} f(d)\, G\!\left(\left\lfloor \frac{N}{d} \right\rfloor\right), \qquad G(x) = \sum_{m \le x} g(m).$$

That is the whole trick. One sum of length $N$ over a hard function becomes a sum over $d$
weighted by $f(d)$, with an inner sum $G$ of the easy function. Choose $g$ so that $G$ has a
closed form ($\lfloor x \rfloor$ for $g = \mathbf{1}$, a
[Faulhaber](/blogs/technique/faulhabers-formula) polynomial for $g = \mathrm{Id}^k$, a prefix-sum
table for a periodic $g$). Then you only need to make the outer sum cheap. There are two ways to
do that, and the six problems split between them.

## Two ways to make the outer sum cheap

**Make $f$ sparse.** Suppose $F$ is multiplicative and $F(p) = 1$ for every prime. Then
$F = \mathbf{1} * h$ with $h = F * \mu$, and on a prime $h(p) = F(p) - F(1) = 0$. A multiplicative
function that vanishes on primes is supported only on
[powerful numbers](https://en.wikipedia.org/wiki/Powerful_number), the $n$ in which every prime
appears squared or higher. There are only $\Theta(\sqrt N)$ of those up to $N$. So
$\sum_{n \le N} F(n) = \sum_{d \text{ powerful}} h(d) \lfloor N/d \rfloor$, and you enumerate the
$d$ by a [depth-first search](/blogs/technique/depth-first-search) over primes up to $\sqrt N$
(the [powerful-number sieve](/blogs/technique/powerful-number-sieve)). On a prime power,
$h(p^a) = F(p^a) - F(p^{a-1})$, so the search carries $h$ along with one multiplication per step:

```python
def walk(d, h, i):                       # d powerful, h = h(d); primes[i:] may still be attached
    total = h * (N // d)
    for j in range(i, len(primes)):
        p = primes[j]
        if d * p * p > N: break
        pa, a, prev = p * p, 2, F_pp(p, 1)    # F_pp(p, a) = F(p^a)
        while d * pa <= N:
            cur = F_pp(p, a)
            if cur != prev:                     # h(p^a) = 0 prunes the whole subtree
                total += walk(d * pa, h * (cur - prev), j + 1)
            pa, a, prev = pa * p, a + 1, cur
    return total
```

Three problems take this route.

- **484** sums $\gcd(k, k')$ for the
  [arithmetic derivative](https://en.wikipedia.org/wiki/Arithmetic_derivative) up to
  $5 \times 10^{15}$. A $p$-adic argument shows the gcd is multiplicative, with $p^{a-1}$ or $p^a$
  on each prime power depending on whether $p \mid a$, and it is $1$ on every prime. So it is
  $\mathbf{1} * h$ with $h$ on powerful numbers. There are about $10^8$ of them, and whole subtrees
  drop out where $h(p^a) = 0$.
- **850** reduces a sum of fractional parts $\{i^k/n\}$ to $\sum_n z_k(n)$, where $z_k(n)$ counts
  residues with $n \mid i^k$. Again $z_k(p) = 1$, so $z_k = \mathbf{1} * g_k$ with $g_k$ on powerful
  numbers. The twist is that the problem sums over many exponents $k$, and a *sum* of
  multiplicative functions is not multiplicative. The search therefore carries a short vector of
  $g_k(d)$, one entry per distinct class of $k$, and multiplies each component separately as
  primes are attached.
- **967** asks for the $n \le 10^{18}$ whose distinct small prime factors sum to $0 \bmod 3$. The
  weight $\chi(n) = x^{S(n)}$ lives in the
  [group ring](/blogs/technique/group-ring-arithmetic) $\mathbb{Z}[C_3]$, and the same algebra
  holds there. $\chi$ takes the same value on every power of $p$, so $\chi = \mathbf{1} * h$ with
  $h$ supported on *squarefree* $d$ built from the 29 relevant primes, and $h(p) = x^p - 1$. That
  is still about $7 \times 10^7$ terms. The fix is to convolve only over the large primes, and to
  let $g$ be the small primes' periodic part. Its partial sums come from a prefix table over one
  period, $Q = 3\,233\,230$. This is the general lesson: **you choose which factor is "easy".**
  Anything periodic, or anything with a closed-form prefix sum, can sit in $g$.

**745** is the same move in a different shape. The largest square dividing $n$ is $s^2$ where
$n = s^2 k$ with $k$ squarefree. Writing $\mathrm{Id}^2 = \mathbf{1} * h$, that is
$h = \mu * \mathrm{Id}^2$ with $h(p^a) = p^{2a} - p^{2a-2}$, turns the sum into
$\sum_{m \le \sqrt N} h(m) \lfloor N/m^2 \rfloor$. The support is squares instead of powerful
numbers, so a [linear sieve](/blogs/technique/linear-sieve) of $h$ up to $\sqrt N$ is the whole
cost.

**Make $G$ cheap at few points.** Sometimes neither factor is sparse, but
$\lfloor N/d \rfloor$ takes only about $2\sqrt N$ distinct values. You can
[block by quotient](/blogs/technique/quotient-blocking): group the $d$ that share a quotient and
pay once per block, using a prefix sum of $f$.

- **625** sums $\gcd(i, j)$ over pairs up to $10^{11}$. The inner sum over $i$ is Pillai's
  function $\mathrm{Id} * \varphi$, so the total is $\sum_k \varphi(k)\, T(\lfloor N/k \rfloor)$
  with $T$ triangular. After blocking, what you need is the totient summatory $\Phi$ at every
  quotient, and the convolution gives you that as well. Summing $\varphi * \mathbf{1} = \mathrm{Id}$
  up to $x$ gives $\sum_d \Phi(\lfloor x/d \rfloor) = T(x)$, a recursion for $\Phi$ that stays
  inside the quotient set. Sieve $\varphi$ up to $N^{2/3}$ and apply the
  [recursion](/blogs/technique/totient-summatory-recursion) above that, and the whole thing is
  $O(N^{2/3})$. This is the technique usually called Du's sieve, and it is just the
  [hyperbola method](/blogs/technique/dirichlet-hyperbola-method) applied to a known convolution.
- **875** counts the zeros of an eight-variable quadratic form mod $n$. A
  [roots-of-unity filter](/blogs/technique/roots-of-unity-filter) and the moduli of
  [quadratic Gauss sums](/blogs/technique/quadratic-gauss-sum) give $q = \mathrm{Id}^7 * w$, where
  $w$ is nearly $\varphi(m)\, m^3$ apart from a $2$-adic correction. The summed form
  $\sum_m w(m)\, S_7(\lfloor N/m \rfloor)$ needs a totient sieve to $N$ anyway. Blocking does not
  change the complexity here, but it means the degree-8 Faulhaber polynomial is evaluated a few
  thousand times instead of $10^7$.

## How to reason about it

The recipe has three steps, and the work is in the first one.

1. **Find the convolution.** It shows up as "$\gcd$" (625: count the pairs by their gcd), as a
   multiplicative function that is $1$ on primes (484, 850, 967), as "largest $k$-th power
   dividing" (745), or as the result of an exponential-sum computation that groups terms by a
   divisor (875). If $F$ is multiplicative, compute $h = F * \mu$ on prime powers by hand for
   $p^1, p^2, p^3$ and look at what you get. $h(p) = 0$ means powerful support. $h(p^a) = 0$ for
   $a \ge 2$ means squarefree support. Neither means you should reach for blocking.
2. **Assign the roles.** Put whatever has a cheap prefix sum in $g$. Put whatever is sparse, or
   sieveable to a small bound, in $f$. The roles are yours to choose: in 967 the split falls
   between small and large primes, not between named functions.
3. **Pick the evaluator.** That means a DFS over powerful or squarefree $d$, a sieve to
   $\sqrt N$, quotient blocking with a prefix table, or a recursion over the quotients for the
   summatory function. Costs run from $O(\sqrt N)$ to $O(N^{2/3})$, against $O(N)$ for the direct
   sum.

The pitfalls are mostly arithmetic. The sparse factor $h$ is a *difference*, so it is often
negative or zero, and the zero cases are worth pruning (484). A sum of multiplicative functions
needs one component per summand (850). Products like $h(d) \lfloor N/d \rfloor$ sit close to the
64-bit limit at $N = 10^{16}$ to $10^{18}$, so bound them before multiplying, or use `__int128` in
C. Coefficients in a group ring grow like $2^{\#\text{primes}}$ even when the final count fits
(967). Before trusting a derived $h$, check $(\mathbf{1} * h)(n) = F(n)$ by brute force for every
$n$ up to a few thousand. That check catches the off-by-one in the exponent case analysis, which
is where every one of these derivations is most likely to slip.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0484](/solutions/0484/) — Arithmetic Derivative
- ● [0625](/solutions/0625/) — Gcd Sum
- ● [0745](/solutions/0745/) — Sum of Squares II
- ● [0787](/solutions/0787/) — Bézout's Game
- ● [0850](/solutions/0850/) — Fractions of Powers
- ● [0875](/solutions/0875/) — Quadruple Congruence
- ● [0967](/solutions/0967/) — $B$-Trivisible Numbers

<!-- /problems -->
