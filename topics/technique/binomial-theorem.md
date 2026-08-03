<!-- tags: [binomial-theorem] -->
<!-- status: final -->
# Binomial theorem

The [binomial theorem](https://en.wikipedia.org/wiki/Binomial_theorem) is the one-line statement
that

$$(x + y)^n = \sum_{k=0}^{n} \binom{n}{k} x^{k} y^{\,n-k}.$$

Read as arithmetic it is a way to expand a power. Read as engineering it is something much more
useful: a *dictionary* between a product of simple factors and a list of counts. Every problem on
this page uses it in one direction or the other — either to make an enormous power collapse into
two or three surviving terms, or to make a counting question turn into a polynomial you can
actually multiply out.

## Three ways it earns its keep

The identity never changes. What changes is which part of it you exploit.

**1 — Truncate.** Expand $(a \pm 1)^n$ and every term from $k = 2$ upward carries a factor $a^2$.
Work [modulo](/topics/domain/modular-arithmetic) $a^2$ and those terms are all zero, so an
expansion of $n+1$ terms leaves exactly two:

$$(a + 1)^n \equiv 1 + na \pmod{a^2}.$$

That is the whole content of problems 120 and 123, which ask about the remainder of
$(a-1)^n + (a+1)^n$ modulo $a^2$. Add the two truncated expansions and the answer splits on the
parity of $n$: for even $n$ the linear terms cancel and only a constant survives; for odd $n$ the
constants cancel and the linear terms reinforce. An expression that looks like it needs
[modular exponentiation](/topics/technique/modular-exponentiation) — or worse, a literal
thousand-digit power — turns into one multiplication. Note the shape of the win: the modulus is a
*perfect power* of the thing being added, and that is what makes the tail vanish. Any time you see
$(\text{something} \pm \text{small})^n \bmod \text{something}^2$, expand before you compute.

**2 — Substitute.** The theorem holds for any $x$, so plugging in a specific value turns a sum of
binomial coefficients into a closed form. $x = 1$ gives $\sum_k \binom{n}{k} = 2^n$; $x = -1$ gives
$0$; and the one that keeps showing up in disguise is

$$\sum_{i} \binom{b}{i} 2^{i} = 3^{b}.$$

Problem 242 reduces, after a long parity argument, to summing $2^{s(t)}$ (with $s$ the
[popcount](https://en.wikipedia.org/wiki/Hamming_weight)) over a range of $t$. Across a full block
of $b$ free bits there are $\binom{b}{i}$ values with $i$ bits set, so the block sums to exactly
$3^b$ — and a $2.5 \times 10^{11}$-term sum becomes one term per set bit of the limit, a
[digit DP](/topics/technique/digit-dp) over forty bits. Whenever a sum weights each subset of a
$b$-element set by $c^{|S|}$, the answer is $(1+c)^b$; recognising that is often the difference
between $O(2^b)$ and $O(1)$.

**3 — Bookkeep.** This is the direction that generalises furthest. Treat $x$ as a formal marker
rather than a number: in $(1 + x^r)^{c}$, the coefficient of $x^{j}$ counts the ways to reach total
$j$. That is a [generating function](/topics/domain/generating-function), and the binomial theorem
is what lets you write down a whole family of choices in one factor instead of multiplying $c$
factors one at a time.

Problem 250 is the clean case. It counts subsets of a $250250$-element set whose sum is divisible
by $250$, so each element contributes a factor $1 + x^{r}$ for its residue $r$, and the answer is
one coefficient of the product — a [subset-sum count](/topics/domain/subset-sum-problem) in
$\mathbb{Z}[x]/(x^{250}-1)$, where exponents add modulo $250$ for free. The elements sharing a
residue share a factor, and the binomial theorem expands their combined contribution
$(1 + x^{r})^{c_r}$ as a single row $\sum_i \binom{c_r}{i} x^{ri}$. Two hundred and fifty thousand
polynomial multiplications become at most two hundred and fifty.

Problems 172 and 788 use the same bookkeeping without any polynomial appearing in the code. Both
count digit strings under a repetition constraint, and both turn on the same question — *which
positions carry this digit?* — whose answer is a binomial coefficient times a free choice for the
rest. In 788 that is a direct sum over the dominant digit's multiplicity; in 172 it becomes a
[dynamic programme](/topics/technique/dynamic-programming) that folds in one digit type at a time,
$\binom{t}{c}$ choosing where the $c$ new copies land among $t$ positions. That factor is exactly
the [exponential generating function](https://en.wikipedia.org/wiki/Generating_function#Exponential_generating_function_(EGF))
identity $\frac{t!}{c!\,(t-c)!}$ made concrete: EGF multiplication *is* interleaving labelled
positions, and the binomial coefficient is the interleaving count.

## Binomial coefficients as a basis

There is a fourth use, less obviously "the binomial theorem" but the same algebra. The
[Newton forward-difference formula](https://en.wikipedia.org/wiki/Finite_difference#Newton's_series)
writes a polynomial's value at a new integer node as

$$u_{k+1} = \sum_{j=0}^{k} \binom{k}{j}\, \Delta^{j} u_1,$$

which is the binomial theorem for the operator identity $E = 1 + \Delta$ — shifting by one is
"do nothing or difference", raised to the $k$th power. Problem 101 asks for the first incorrect
term of each low-degree interpolant of a degree-10 polynomial, and this identity replaces solving a
[Vandermonde](https://en.wikipedia.org/wiki/Vandermonde_matrix) system with reading entries off a
[finite-difference](/topics/technique/finite-difference) table — exact integers throughout, no
rationals. The same expansion explains why the interpolation error at the next node is precisely
$\Delta^{k} u_1$. When your nodes are equally spaced integers, binomials are the natural basis and
[Lagrange](/topics/domain/polynomial-interpolation) is doing unnecessary work.

## Modulo 2, the theorem gets simpler

Over $\mathbb{F}_2$ the cross terms of $(1+x)^2 = 1 + 2x + x^2$ die, leaving the
[freshman's dream](https://en.wikipedia.org/wiki/Freshman%27s_dream) $(1+x)^2 \equiv 1 + x^2$, and
by induction $(1+x)^{2^m} \equiv 1 + x^{2^m}$. Squaring becomes a shift. That single fact is the
engine behind [Lucas's theorem](/topics/domain/lucass-theorem) and behind the self-similarity of
[Pascal's triangle](/topics/technique/pascals-triangle) mod $2$; problem 242 leans on it to collapse
a two-factor generating function down to one shifted $(1+x)^{n-1}$. If a problem asks only for the
*parity* of a count, expand mod $2$ before you expand anything else — the expression usually gets
shorter, not longer.

## How to reason about it

The tell for use **1** is a modulus that is a power of a term inside the parentheses. The tell for
**2** is a sum of binomial coefficients against a geometric weight. The tell for **3** is any
counting problem where the objects are built from independent choices and only a total matters.

Three practical cautions, all of which cost real time in the archive:

- **Decide early whether you need the coefficient or the count.** $\binom{2n}{n}$ has a closed form
  and Python computes it exactly with one call — problem 15 is the whole solution below. But that
  luxury disappears the moment the answer is wanted modulo something.

  ```python
  return str(math.factorial(2 * lattice_size) // math.factorial(lattice_size) ** 2)
  ```

- **The recurrence $\binom{c}{i+1} = \binom{c}{i}\frac{c-i}{i+1}$ is exact over the integers, not
  modulo an arbitrary $m$.** The division is only valid when $i+1$ is invertible, so it is fine mod
  a prime and *wrong* mod $10^{16}$ or $2^{64}$. Problem 250 hits this squarely: Python carries the
  coefficient as an exact bignum and reduces on store, while the C port has to strip the powers of
  $2$ and $5$ out and carry them as exponents so the remaining unit is coprime to the modulus. If
  your modulus is not prime, plan the representation before you write the loop.
- **Bignums are correct and slow.** Both problem 788 and problem 172 build intermediates of
  thousands of digits if you defer the reduction to the end; reducing at every step — legitimate,
  because reduction is a ring homomorphism — moved 788 from over a minute to a few hundredths of a
  second. Where the modulus forbids that, expect the arbitrary-precision cost and see
  [watch integer width](/topics/takeaway/watch-integer-width) for the other half of the trap.

The unifying instinct is this: **a power of a sum is a list of counts, and a list of counts is a
power of a sum.** Whichever side of that equation your problem hands you, try writing down the
other.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0101](/solutions/0101/) — Optimum Polynomial
- ● [0120](/solutions/0120/) — Square Remainders
- ● [0123](/solutions/0123/) — Prime Square Remainders
- ● [0172](/solutions/0172/) — Few Repeated Digits
- ● [0242](/solutions/0242/) — Odd Triplets
- ● [0250](/solutions/0250/) — $250250$
- ● [0788](/solutions/0788/) — Dominating Numbers

<!-- /problems -->
