<!-- tags: [chinese-remainder-theorem] -->
<!-- status: final -->
# Chinese remainder theorem

The [Chinese remainder theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem) (CRT) says
that arithmetic modulo a composite `m` is nothing more than arithmetic modulo each of its coprime
factors, done side by side. That sounds like a statement about congruences, and it gets taught as a
recipe for solving them, but in practice it is a *structural* tool: it is the licence to take a
problem stated modulo one awkward number and replace it with several independent problems modulo
friendlier ones. Every problem below reaches for it at a different point in the pipeline — to split
a modulus, to count a solution set, or to grow one — and the theorem is the same each time.

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
accumulate one at a time.

**All moduli at once (Gauss).** With `M_i = m / m_i`,

```
x = Σ aᵢ · Mᵢ · (Mᵢ⁻¹ mod mᵢ)   (mod m)
```

Each term is `aᵢ` in its own component and `0` in every other, so the sum lands on the right residue
everywhere. The inverses depend only on the moduli, not on the residues, so this form pays off when
you lift *many* different residue vectors through the *same* moduli — the inverse table is built
once and amortised. Problem 0365 pushes that further: it lifts twenty million triples `(p, q, r)`
drawn from a pool of 501 primes, and since `(qr)⁻¹ mod p` factors as `q⁻¹·r⁻¹ mod p`, every inverse
it will ever need is one of `O(P²)` *pairwise* ones. The `O(P³)` triple loop then contains no
inverse at all, just a few multiplications.

## Three things it is actually used for

**Split a hard modulus into tractable ones.** The textbook use. Problem 0160 wants five digits of a
factorial modulo `10⁵`, and the difficulty is that the value shares its factors `2` and `5` with the
modulus, so reducing directly destroys the information you need. Splitting `10⁵ = 2⁵ · 5⁵` isolates
one prime per component, and *within* a component you can strip that prime's powers explicitly and
divide them back out with an inverse — a manoeuvre that is meaningless modulo the composite. The
split does not just make the arithmetic smaller; it makes an otherwise-blocked step legal.

**Construct and count a solution set.** Because the isomorphism is a bijection, solutions modulo `m`
correspond exactly to *tuples* of solutions in the components — so the count is
[multiplicative](https://en.wikipedia.org/wiki/Multiplicative_function), and CRT is the constructor
that turns a choice per component into an actual residue. Problem 0932 needs the `s` with
`s(s−1) ≡ 0 (mod m)`. Consecutive integers are coprime, so each prime power of `m` must divide `s`
or `s−1` *entirely*, never split across both: `k` distinct prime factors give exactly `2ᵏ` residues,
one per binary choice, each assembled by CRT. That converts a scan over a huge interval into a walk
along a handful of arithmetic progressions. Read this direction of the theorem carefully — it is the
one people miss. CRT is not only how you *solve* a congruence system, it is how you *enumerate* the
solutions of a condition that is local to each prime.

**Grow a modulus incrementally.** When the constraints arrive as a sequence, maintain a running
modulus `M` and the set `R` of residues modulo `M` that satisfy everything so far; each new prime
`p` with its own allowed residues lifts every pair `(r ∈ R, s allowed mod p)` to a residue modulo
`M·p`. This is a CRT-driven [sieve](/topics/technique/sieve-of-eratosthenes) with no array: you
never touch the integers themselves, only their residue classes. Problem 0934 uses exactly this
shape, and it shows why the technique is worth the trouble — `M` grows *multiplicatively* while `R`
grows by a much smaller factor per prime, so within about fifteen steps `M` overshoots a bound of
`10¹⁷` and the survivor set collapses to nothing. Counting the integers in `[1, N]` covered by a
residue class is then a division, and a sum over `10¹⁷` values becomes a loop over fifteen primes.

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
- **Normalise the sign in C.** `(a₂ − a₁)` is routinely negative and C's `%` follows the dividend's
  sign, so the merge needs `((x % m) + m) % m`. Python's `%` already returns a non-negative result
  for a positive modulus.
- **Watch what the components cost.** CRT is only a win if the per-component work is cheaper than
  the original. It usually is — a smaller modulus means smaller tables and, for a *prime* component,
  the whole toolbox that needs a field:
  [Lucas's theorem](/topics/domain/lucass-theorem),
  [Fermat's little theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem), free division.
  But the glue costs an inverse per component, so for a one-off lift with two small moduli the split
  can be pure overhead.
- **Recognise the trigger.** Any of these three should make you reach for it: the modulus is
  composite and its factorisation is known; a condition is stated independently at each prime; or
  constraints modulo several coprime numbers must hold simultaneously. In all three the theorem
  turns a global problem into local ones, and local problems are the ones you can solve.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0932](/solutions/0932/) — $2025$
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
