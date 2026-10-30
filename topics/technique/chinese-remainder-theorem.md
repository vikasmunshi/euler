<!-- tags: [chinese-remainder-theorem] -->
<!-- status: final 2026-10-29T02:14Z -->
# Chinese remainder theorem

The [Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) (CRT) says
that arithmetic modulo a composite `m` is nothing more than arithmetic modulo each of its coprime
factors, done side by side. That sounds like a statement about congruences, and it gets taught as a
recipe for solving them, but in practice it is a *structural* tool: it is the licence to take a
problem stated modulo one awkward number and replace it with several independent problems modulo
friendlier ones. Every problem below reaches for it at a different point in the pipeline — to split
a modulus, to count a solution set, to build one, or to grow a modulus — and the theorem is the same
each time.

## The theorem

Let `m = m₁ · m₂ · … · m_k` with the `m_i` [pairwise coprime](https://en.wikipedia.org/wiki/Coprime_integers).
Then for any target residues `a₁, …, a_k` the system

```
x ≡ a₁ (mod m₁),  x ≡ a₂ (mod m₂),  …,  x ≡ a_k (mod m_k)
```

has exactly one solution `x` in `[0, m)`. Existence and uniqueness both matter, and it is worth
separating them: uniqueness is the easy half (two solutions differ by a multiple of every `m_i`,
hence of `m`), while existence is what makes the theorem useful — *any* combination of residues is
achievable.

The compact statement is that the map `x ↦ (x mod m₁, …, x mod m_k)` is a
[ring isomorphism](https://en.wikipedia.org/wiki/Ring_isomorphism)

```
ℤ/m  ≅  ℤ/m₁ × ℤ/m₂ × … × ℤ/m_k
```

That is the version to hold in your head, because it is stronger than the congruence-solving
version. Being a ring isomorphism means it respects addition *and* multiplication, so it does not
merely transport a number — it transports a whole computation. Anything you can compute modulo `m`
you may compute component-wise instead, in whatever way is convenient in each component, and glue
the answers at the end. A hard modulus becomes several easy ones, and the moduli are smaller, so
the components are frequently faster as well as simpler.

The canonical factorisation is into
[prime powers](https://en.wikipedia.org/wiki/Prime_power): `m = ∏ pᵉ` are automatically pairwise
coprime, and no finer split is available. When `m` is [squarefree](https://en.wikipedia.org/wiki/Square-free_integer)
the components are prime *fields*, where every non-zero element is invertible — the friendliest case
there is, and the reason problem 0365's modulus `p·q·r` of three distinct primes collapses so
cleanly into three independent per-prime computations.

## Doing the glue

Two constructions, and the choice between them is about how the moduli arrive.

**Two moduli at a time (Garner).** Solve `x ≡ a₁ (mod m₁)` and `x ≡ a₂ (mod m₂)` by writing
`x = a₁ + m₁·t` — which satisfies the first congruence by construction — and forcing the second:

```python
def crt2(a1, m1, a2, m2):
    t = (a2 - a1) * pow(m1, -1, m2) % m2
    return a1 + m1 * t, m1 * m2        # x, combined modulus
```

One [modular inverse](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) per merge,
supplied by the [extended Euclidean algorithm](/topics/technique/extended-euclidean-algorithm) (or
by Python's `pow(a, -1, m)`). Fold it over a list to handle any number of moduli. Its virtue is that
the intermediate values stay bounded by the product *so far*, which is what you want when the moduli
accumulate one at a time. It also merges whole *sets* cheaply: when the first modulus carries a list
of residues `R` and the second a list `S`, the inverse `m₁⁻¹ mod m₂` is shared by all `|R|·|S|`
pairs, so a merge is one inverse and a product of lists — the form problems 0245 and 0934 both use.

**All moduli at once (Gauss).** With `M_i = m / m_i`,

```
x = Σ aᵢ · Mᵢ · (Mᵢ⁻¹ mod mᵢ)   (mod m)
```

Each term is `aᵢ` in its own component and `0` in every other, so the sum lands on the right residue
everywhere. The coefficients `eᵢ = Mᵢ · (Mᵢ⁻¹ mod mᵢ)` deserve a name: each is `1` in component `i`
and `0` elsewhere, so `eᵢ² = eᵢ` — they are the
[idempotents](https://en.wikipedia.org/wiki/Idempotent_(ring_theory)) of `ℤ/m`, the basis vectors of
the product ring, and lifting a residue vector is just taking a linear combination of them. They
depend only on the moduli, not on the residues, so this form pays off when you lift *many* different
residue vectors through the *same* moduli — the basis is built once and amortised. Problem 0271
precomputes one `eᵢ` per prime power of its modulus and then assembles every root as `Σ rᵢ·eᵢ`,
growing a list of partial sums that branches once per root choice at each prime. Problem 0365 pushes that further: it lifts twenty million triples `(p, q, r)`
drawn from a pool of 501 primes, and since `(qr)⁻¹ mod p` factors as `q⁻¹·r⁻¹ mod p`, every inverse
it will ever need is one of `O(P²)` *pairwise* ones. The `O(P³)` triple loop then contains no
inverse at all, just a few multiplications.

## Four things it is actually used for

**Split a hard modulus into tractable ones.** The textbook use. Problem 0160 wants five digits of a
factorial modulo `10⁵`, and the difficulty is that the value shares its factors `2` and `5` with the
modulus, so reducing directly destroys the information you need. Splitting `10⁵ = 2⁵ · 5⁵` isolates
one prime per component, and *within* a component you can strip that prime's powers explicitly and
divide them back out with an inverse — a manoeuvre that is meaningless modulo the composite. The
split does not just make the arithmetic smaller; it makes an otherwise-blocked step legal.

**Count a solution set without finding it.** Because the isomorphism is a bijection, solutions
modulo `m` correspond exactly to *tuples* of solutions in the components — so their number is a
[multiplicative function](https://en.wikipedia.org/wiki/Multiplicative_function) of `m`, and you can
know it without constructing a single one. Problem 0272 counts the `x` with `x³ ≡ 1 (mod n)`. The
isomorphism restricts to the unit groups, `(ℤ/n)ˣ ≅ ∏ (ℤ/pᵉ)ˣ`, and for an odd prime each factor is
[cyclic](https://en.wikipedia.org/wiki/Multiplicative_group_of_integers_modulo_n), where `x³ = 1` has
exactly `gcd(3, order)` solutions. So each prime power contributes a factor `3` or `1`, decided by
`p mod 3` alone, and the count is `3ᵏ`. The question "which `n` have exactly 242 non-trivial cube
roots of unity" has stopped being about congruences at all: it is "which `n` have exactly five
contributing factors", a factor-shape enumeration that never computes a root. That is the payoff of
the counting direction — the theorem translates an arithmetic condition into a statement about the
shape of the factorisation, and the search runs over factorisations instead of over residues.
Problem 0271 is the same equation asked the other way — not *how many* cube roots of unity modulo
one fixed primorial, but their *sum* — so there the count `3ᵏ` is no longer the answer but the size
of the enumeration, and a small one: the theorem says in advance that only a few hundred residues
exist, and the remaining work is to factor the modulus and build them.

**Construct a solution set, one prime at a time.** When you do need the solutions, CRT is the
constructor that turns a choice per component into an actual residue. Problem 0932 needs the `s`
with `s(s−1) ≡ 0 (mod m)`. Consecutive integers are coprime, so each prime power of `m` must divide
`s` or `s−1` *entirely*, never split across both: `k` distinct prime factors give exactly `2ᵏ`
residues, one per binary choice, each assembled by CRT. That converts a scan over a huge interval
into a walk along a handful of arithmetic progressions. Read this direction of the theorem
carefully — it is the one people miss. CRT is not only how you *solve* a congruence system, it is
how you *enumerate* the solutions of a condition that is local to each prime.

Those `2ᵏ` residues are exactly the idempotents from the Gauss construction above, and problem 0407
asks for the largest one modulo *every* `n` up to `10⁷`. Factoring each `n` and trying its `2ᵏ`
splits would work; the better move is to turn the theorem inside out and enumerate the splits
directly. Every idempotent of `n` comes from a coprime pair `n = d·e` with `a ≡ 0 (mod d)` and
`a ≡ 1 (mod e)`, so sweeping all coprime pairs with `d·e ≤ N` visits every idempotent of every `n`
once — `Θ(N log N)` pairs, no factorisation anywhere. The merge for each pair needs an inverse, and
here the Garner form's asymmetry becomes a lever: one factor of every pair is at most `√N`, so always
invert modulo the *small* factor `s`. The inverse of the partner `L` depends only on `L mod s`, so a
single table of inverses mod `s` serves every partner, and the per-pair work drops to a lookup and a
multiply. Two more structural facts trim it further: the two idempotents of a split are `a` and
`n + 1 − a`, so one merge yields both, and a non-coprime pair can be left in the sweep with a `0`
"inverse", which collapses it to the trivial idempotents that never win.

The general recipe for a polynomial congruence `f(x) ≡ 0 (mod m)` has three stages: find the roots
modulo each prime `p`, lift them to `pᵉ` with [Hensel's lemma](https://en.wikipedia.org/wiki/Hensel%27s_lemma),
and glue across primes with CRT. Problem 0245 runs it on `x² − x + 1`. Its roots modulo a prime are
`−ω` for `ω` a primitive cube root of unity — so they exist only for `p ≡ 1 (mod 3)`, plus a single
root at `3` itself, the same primes that carried the factor `3` in problem 0272 — and a modulus with
`j` such prime factors carries `2ʲ` roots. The per-prime step is where the number theory lives; CRT
is the mechanical part, which is exactly the point.

**Grow a modulus incrementally.** When the constraints arrive as a sequence, maintain a running
modulus `M` and the set `R` of residues modulo `M` that satisfy everything so far; each new prime
`p` with its own allowed residues lifts every pair `(r ∈ R, s allowed mod p)` to a residue modulo
`M·p`. This is a CRT-driven [sieve](/topics/technique/sieve-of-eratosthenes) with no array: you
never touch the integers themselves, only their residue classes. Problem 0934 uses exactly this
shape, and it shows why the technique is worth the trouble — `M` grows *multiplicatively* while `R`
grows by a much smaller factor per prime, so within about fifteen steps `M` overshoots a bound of
`10¹⁷` and the survivor set collapses to nothing. Counting the integers in `[1, N]` covered by a
residue class is then a division, and a sum over `10¹⁷` values becomes a loop over fifteen primes.

The same growth can branch instead of running in a line. Problem 0245 needs the roots of
`x² − x + 1` modulo *every* solvable modulus up to a bound, not modulo one big one, so it grows them
as a depth-first tree: each node is a modulus with its root list, and each child appends one more
prime power and merges the parent's list with that prime power's roots. Every node is itself an
answer, and every root list is computed once and inherited by all its children — the tree is the
memo.

## Getting it right

- **Coprimality is a precondition, not a formality.** If `gcd(m_i, m_j) = g > 1`, the inverse in the
  merge does not exist and the system is solvable only when `a_i ≡ a_j (mod g)` — in which case you
  can still merge, with combined modulus `lcm(m_i, m_j)` rather than the product. Check the gcd or
  guarantee it structurally; the usual guarantee is that your moduli are distinct primes or the
  prime powers of a single factorisation.
- **Reduce before you multiply.** The Gauss form multiplies `aᵢ` by `Mᵢ`, which is nearly `m` — so
  intermediates reach `m²` even though the answer is below `m`. That is the standard place a 64-bit
  accumulator silently wraps, and why several C ports here compute the lift in
  [`__int128`](/topics/technique/int128) where Python's
  [arbitrary-precision integers](/topics/technique/arbitrary-precision-arithmetic) absorb it
  unremarked. Arranging the lift as a sum of terms each below `m` — so the total is below `k·m` and
  the reduction is a couple of conditional subtractions rather than a division — is both faster and
  narrower.
- **The lift gives residues; the question may want integers.** CRT returns each solution reduced
  into `[0, m)`, which is the right object — but if the problem sums or compares the solutions,
  keep them as integers and do that arithmetic outside the modulus. Problem 0271 sums its roots of
  unity: adding them modulo `n` would yield only the sum mod `n`, while the true total is hundreds of
  times larger than `n` and needs a wider accumulator (`__int128` in the C port).
- **Normalise the sign in C.** `(a₂ − a₁)` is routinely negative and C's `%` follows the dividend's
  sign, so the merge needs `((x % m) + m) % m`. Python's `%` already returns a non-negative result
  for a positive modulus.
- **Expect a few primes to break the pattern.** The per-component answer is usually a rule in `p`,
  but the small primes that divide the problem's own constants are exceptions, and each needs its
  own case. In problem 0272 the prime `3` contributes a cube root only from `9` upward, and `2` never
  does; in problem 0245 `3` divides `x² − x + 1` but `9` never does, so Hensel lifting must stop
  there. Check every prime power below a small bound by brute force before trusting the general
  rule.
- **Watch what the components cost.** CRT is only a win if the per-component work is cheaper than
  the original. It usually is — a smaller modulus means smaller tables and, for a *prime* component,
  the whole toolbox that needs a field:
  [Lucas's theorem](/topics/domain/lucass-theorem),
  [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), free division.
  But the glue costs an inverse per component, so for a one-off lift with two small moduli the split
  can be pure overhead.
- **Recognise the trigger.** Any of these should make you reach for it: the modulus is composite
  and its factorisation is known; a condition is stated independently at each prime; you are asked
  to count or list the roots of a polynomial modulo many different `n`; or constraints modulo
  several coprime numbers must hold simultaneously. In every case the theorem
  turns a global problem into local ones, and local problems are the ones you can solve.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0245](/solutions/0245/) — Coresilience
- ● [0271](/solutions/0271/) — Modular Cubes, Part 1
- ● [0272](/solutions/0272/) — Modular Cubes, Part 2
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0407](/solutions/0407/) — Idempotents
- ● [0531](/solutions/0531/) — Chinese Leftovers
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
