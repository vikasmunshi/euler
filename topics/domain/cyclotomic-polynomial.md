<!-- tags: [cyclotomic-polynomial] -->
<!-- status: final -->
# Cyclotomic polynomial

The $n$-th [cyclotomic polynomial](https://en.wikipedia.org/wiki/Cyclotomic_polynomial)
$\Phi_n(x)$ is the minimal polynomial over $\mathbb{Q}$ of a primitive $n$-th root of unity. It
keeps turning up in problems that never mention polynomials: a robot walking in arcs, a
chandelier that must hang level, a congruence $x^3 \equiv 1$. What they share is a question
about roots of unity — *when does a combination of them vanish?* or *which residues behave like
them?* — and $\Phi_n$ is the exact answer to both. Once I recognise it, a geometric or
modular condition becomes a statement about polynomial divisibility, which I can count.

## The idea

Factor $x^n - 1$ over the rationals and it splits by the *order* of each root:

$$x^n - 1 = \prod_{d \mid n} \Phi_d(x), \qquad \deg \Phi_n = \varphi(n),$$

where $\varphi$ is [Euler's totient](https://en.wikipedia.org/wiki/Euler%27s_totient_function).
So $\Phi_1 = x - 1$, $\Phi_3 = x^2 + x + 1$, $\Phi_5 = 1 + x + x^2 + x^3 + x^4$, and for a prime
$p$, $\Phi_p = 1 + x + \dots + x^{p-1}$. Möbius inversion gives the closed form
$\Phi_n(x) = \prod_{d \mid n} (x^d - 1)^{\mu(n/d)}$, and the coefficients are integers
([OEIS A013595](https://oeis.org/A013595) tabulates them).

Three facts do almost all the work in practice:

1. **Irreducibility.** $\Phi_n$ is irreducible over $\mathbb{Q}$, so an integer polynomial $f$
   satisfies $f(\zeta_n) = 0$ *if and only if* $\Phi_n \mid f$. "These unit vectors sum to zero"
   becomes "this 0/1 polynomial is divisible by $\Phi_n$" — an exact, integer statement with no
   floating-point tolerance anywhere.
2. **A basis.** The powers $1, \zeta_n, \dots, \zeta_n^{\varphi(n)-1}$ are linearly independent
   over $\mathbb{Q}$, so $\mathbb{Z}[\zeta_n]$ is a free module of rank $\varphi(n)$. Every root
   of unity has a small integer coordinate vector, and vanishing sums become vector sums equal
   to zero.
3. **Reduction to the radical.** With $r = \operatorname{rad}(n)$ and $t = n/r$,
   $\Phi_n(x) = \Phi_r(x^t)$. Everything about $\zeta_n$ decomposes into $t$ independent copies
   of the much smaller squarefree case.

Modulo a prime the same polynomial plays a different role: the roots of $\Phi_d$ in
$\mathbb{Z}_p$ are exactly the elements of multiplicative order $d$, and they exist precisely
when $d \mid p - 1$ (the group is [cyclic](https://en.wikipedia.org/wiki/Primitive_root_modulo_n)).

## How it shows up

**Closure of a walk (208).** Every arc of the robot's walk is a unit step along one of five
fixed directions, the fifth roots of unity rotated by $36^\circ$. The only rational relation
among those five is $\Phi_5(\zeta_5) = 0$, i.e. $v_0 + \dots + v_4 = 0$, and irreducibility
says it is the *only* one up to scaling. So a non-negative combination closes exactly when all
five directions are used equally often — the geometry evaporates, and what is left is a
dynamic programme over the heading and the four count differences.

**Vanishing sums of roots of unity (768).** A balanced chandelier is an $m$-subset $S$ of
$\mathbb{Z}_n$ with $\sum_{k \in S} \zeta_n^k = 0$, i.e. $\Phi_n \mid \sum_{k\in S} x^k$. The
tempting shortcut — "balanced sets are unions of regular $p$-gons" — is the
[Lam–Leung theorem](https://arxiv.org/abs/math/9511209) only when $n$ has at most two prime
factors; with three ($30$, $360$) exotic configurations appear, such as the four non-trivial
fifth roots (summing to $-1$) beside the negatives of the two non-trivial cube roots (summing to
$+1$). Pattern-matching polygons misses them; the algebra does not. Fact 3 splits the ring into
$t$ layers over $\mathbb{Z}_r$, so the answer is a coefficient of $G_r(z)^t$, where $G_r$ is the
census of balanced subsets of the squarefree ring. Fact 2 turns that census into exact integer
vector sums in a rank-$\varphi(r)$ lattice — rank $8$ for $r = 30$ — cheap enough for a
[meet-in-the-middle](https://en.wikipedia.org/wiki/Meet-in-the-middle_attack) split.

**Roots of unity modulo $n$ (271).** The non-trivial solutions of $x^3 \equiv 1 \pmod p$ are
the roots of $\Phi_3(x) = x^2 + x + 1$, present exactly when $p \equiv 1 \pmod 3$. The
[Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) multiplies
the per-prime-power root sets together, and to get from $p$ to $p^k$ the roots are lifted by
[Hensel's lemma](/topics/technique/hensels-lemma) — valid because $\Phi_3'$ (equivalently the
derivative $3x^2$ of $x^3 - 1$) is a unit away from $p = 3$. The prime dividing the order is the
exception, and it has to be handled by hand: mod $3$ the root $\omega$ collapses onto $1$, yet
mod $9$ three roots reappear. The two pages are two halves of one method — $\Phi_d$ tells me
*which* roots exist mod $p$, Hensel tells me how they extend.

A sketch of the encoding behind fact 2, for one prime $p$: the residue $a$ maps to the unit
vector $e_a$ for $a < p - 1$, and $\zeta_p^{p-1}$ maps to the all-$(-1)$ vector, because
$\Phi_p(\zeta_p) = 0$ is the single relation. For squarefree $r$, a residue's vector is the
tensor product of its per-prime vectors.

## How to reason about it

- **Reach for it** whenever a condition reads "these rotations / phases / periodic steps
  cancel", or "this residue has order $d$". Rewrite the condition as $f(\zeta_n) = 0$ and ask
  what $\Phi_n \mid f$ forces.
- **Work exactly.** Floating-point sums of $\cos$ and $\sin$ need a tolerance, and a near-miss
  that isn't zero is indistinguishable from one that is. Coordinates in $\mathbb{Z}[\zeta_n]$
  are small integers, can be packed into one machine word, and compare for equality in a single
  instruction.
- **Shrink to the radical first.** The prime powers in $n$ contribute only independent layers;
  the hard combinatorics live in $\operatorname{rad}(n)$, and cost grows with $\varphi(r)$ and
  $r$, not $n$.
- **Count the primes of $n$ before trusting a structure theorem.** Results that hold for one or
  two prime factors (minimal vanishing sums are polygons; minimal relations are the obvious
  ones) break at three. Validate any "it's always a union of…" shortcut with a brute force on a
  small modulus like $30$.
- **Mind the primes dividing the order.** Modulo $p \mid d$, $\Phi_d$ has repeated roots and
  Hensel lifting fails as stated; those primes are always a special case.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0208](/solutions/0208/) — Robot Walks
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0768](/solutions/0768/) — Chandelier
- ○ [0797](/solutions/0797/) — Cyclogenic Polynomials
- ○ [0880](/solutions/0880/) — Nested Radicals
- ○ [0995](/solutions/0995/) — A Particular Pair of Polynomials

<!-- /problems -->
