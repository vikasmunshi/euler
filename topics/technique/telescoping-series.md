<!-- tags: [telescoping-series] -->
<!-- status: final -->
# Telescoping series

A [telescoping series](https://en.wikipedia.org/wiki/Telescoping_series) is a sum whose terms are
built to cancel: write each term as a difference $F(k+1) - F(k)$ and the whole sum collapses to its
two ends, $F(N+1) - F(1)$. Nothing about it is exotic — it is the discrete
[fundamental theorem of calculus](https://en.wikipedia.org/wiki/Fundamental_theorem_of_calculus) —
but it is one of the very few moves that turns $10^{12}$ additions into a handful of arithmetic, so
it is worth actively hunting for whenever a [summation](/topics/domain/summation) bound is too large
to walk.

## The idea

$$\sum_{k=1}^{N} \bigl(F(k+1) - F(k)\bigr) = F(N+1) - F(1)$$

Every interior value appears twice with opposite signs and dies. $F$ is the *antidifference* of the
summand, the discrete counterpart of an antiderivative, and finding one is the entire technique —
the collapse is automatic once you have it.

Sometimes $F$ is obvious. Partial fractions produce it on sight:
$\frac{1}{k(k+1)} = \frac{1}{k} - \frac{1}{k+1}$, so the sum to $N$ is $1 - \frac{1}{N+1}$, no loop
required. Sometimes you go the other way — pick a plausible $F$, difference it, and read off what
you have proved. That is where the standard power-sum identities come from, and it is checkable in
one line:

```python
n = 1000
assert sum((k + 1) ** 3 - k ** 3 for k in range(1, n + 1)) == (n + 1) ** 3 - 1
```

Expand the left summand as $3k^2 + 3k + 1$ and that assertion *is* the derivation of
$\sum k^2 = n(n{+}1)(2n{+}1)/6$ — the [closed form](/topics/technique/closed-form-expression) that
makes problem 6 independent of $n$. The relationship runs both ways: telescoping is the inverse of
[finite differences](/topics/technique/finite-difference), and a
[prefix-sum](/topics/technique/prefix-sum) array is the same identity made concrete — every range
sum $P_j - P_i$ is a telescope you precomputed.

## Shapes it takes

**Cancellation falling out of a recurrence.** This is the form that matters at Project Euler scale,
and it does not announce itself with a difference in the statement. When $f$ obeys a
[recurrence](/topics/domain/recurrence-relation), split $S(N) = \sum f(n)$ along the recurrence's
own cases, substitute each case, and see what survives. Problem 918 is the showcase: its sequence
branches on the parity of the index, so separating even from odd indices and substituting both rules
rewrites $S(N)$ in terms of $S$ at roughly $N/2$ — and the cancellation is total. The trillion-term
sum equals a constant minus a *single term* of the sequence. What is left is evaluating one $a_m$ at
a large $m$, which the sequence's binary structure does in about forty steps by carrying the pair
$(a_m, a_{m+1})$ down the bits of $m$. A trillion additions became forty multiplications, and no
part of that came from writing faster code.

**Summing by levels.** When $g(n)$ is naturally described as *"the first threshold at which
something happens"*, sum over thresholds instead of over $n$. If $t_1 < t_2 < \dots$ are the
possible values and $f_k = \#\{n \le N : g(n) \ge t_k\}$ counts the survivors past level $k$, then

$$\sum_{n=1}^{N} g(n) = \sum_{k} (t_k - t_{k-1})\, f_k$$

— each level contributes its gap to the previous one, weighted by how many $n$ are still alive at
that level. This is the discrete
[layer-cake](https://en.wikipedia.org/wiki/Layer_cake_representation) identity, and equally an
instance of [summation by parts](/topics/domain/summation-by-parts) /
[Abel summation](/topics/technique/abels-summation-formula): the telescope is hiding in
$g(n) = \sum_k (t_k - t_{k-1})[g(n) \ge t_k]$, and swapping the two sums moves the work from $N$
terms to one term per level. Problem 934 is exactly this — its $u(n)$ is the first prime failing an
ordered chain of tests, so the levels are the primes, the gaps are prime gaps, and $f_k$ counts the
integers still satisfying every earlier congruence. Counting those survivors is a
[CRT](/topics/technique/chinese-remainder-theorem) exercise, the modulus outgrows $N$ within about
fifteen primes, and a sum to $10^{17}$ becomes effectively constant work. The generic skeleton is
small enough to write down:

```python
total, prev = 0, 0
for level in levels:            # increasing
    alive = survivors(level)    # count of n <= N not yet resolved
    if alive == 0:
        break
    total += (level - prev) * alive
    prev = level
```

Note what the reformulation bought: `survivors` is a *counting* question over a structured set,
which is usually tractable, whereas $g(n)$ itself was only defined by a search.

## How to reason about it

- **The tell.** A summand that is a difference, a ratio of consecutive terms, a
  [recurrence](/topics/domain/recurrence-relation)-defined sequence, or a "smallest / first index
  such that …" definition. All four are telescopes waiting for the right split. So is any statement
  whose bound ($10^{12}$, $10^{17}$) is far beyond what the terms' cost would allow.
- **What it buys.** Usually $O(1)$ or $O(\log N)$ from $O(N)$ — a category change, not a constant
  factor. That makes it worth a long time at the whiteboard before any code:
  [reduce algebraically before coding](/topics/takeaway/reduce-before-coding).
- **Always verify against brute force.** A telescoped identity is a *claim*, and the cheapest way to
  be wrong is a dropped boundary term. Write the fifteen-line $O(N)$ version, check the collapsed
  form against it for every small $N$ you can afford, and only then run it at scale. The sample
  value in the statement ($S(10)$, $U(1470)$) exists for this.
- **Mind the ends.** Off-by-one is the characteristic failure: whether the sum starts at $0$ or $1$,
  whether the last level's gap is included, whether $\lfloor N/2 \rfloor$ and
  $\lfloor (N-1)/2 \rfloor$ coincide. Split the parity cases explicitly rather than hoping one
  formula covers both.
- **Not everything cancels.** A partial collapse — most terms gone, a residue left over — is still a
  win if the residue is cheap, and often that residue is the *same* sum at a smaller argument, which
  makes the identity a recursion rather than a closed form. Take it either way.
- **For infinite series, the tail must vanish.** $\sum_{k\ge1} (F(k+1) - F(k))$ equals $-F(1)$ only
  if $F(k) \to 0$; otherwise the "collapse" is a divergent sleight of hand.
- **Signs, under a modulus.** Telescoped sums produce negative intermediates by construction. C's
  `%` follows the sign of the dividend and Python's does not, so normalise at one choke point when
  [porting](/topics/takeaway/parity-across-languages).

The failure mode this technique guards against is the reflex to optimise the loop that the statement
handed you. When the bound is astronomical, the loop is not meant to be run — it is meant to be
rewritten until it is not a loop at all.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0918](/solutions/0918/) — Recursive Sequence Summation
- ● [0934](/solutions/0934/) — Unlucky Primes

<!-- /problems -->
