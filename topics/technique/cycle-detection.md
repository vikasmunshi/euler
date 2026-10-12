<!-- tags: [cycle-detection] -->
<!-- status: final -->
# Cycle detection

[Cycle detection](https://en.wikipedia.org/wiki/Cycle_detection) is finding where an iterated
process starts repeating. The guarantee behind it is the
[pigeonhole principle](/topics/domain/pigeonhole-principle): a deterministic map on a finite set
of states must revisit some state, and from then on it loops forever. Once the loop is known,
any later term is a modular index into it. That is why the problems below can ask for the
$10^{12}$th term of a sequence, the period of a continued fraction, or the longest chain under a
divisor map. Some problems care about the cycle itself (its length, its members, whether it
contains a zero). Others only use it as a shortcut to an index too far away to reach by stepping.

## The idea: rho, or a pure loop

Iterate $x_{k+1} = f(x_k)$ on a finite set and the orbit has a
[rho shape](https://en.wikipedia.org/wiki/Cycle_detection#Definitions): a tail of $\mu$ distinct
states, then a cycle of length $\lambda$. Two cases are worth telling apart, because they change
what the code has to store.

**$f$ is invertible: no tail.** If every state has exactly one predecessor, $f$ is a
[permutation](/topics/domain/permutation) and every orbit is a pure cycle. So the *seed itself*
recurs, and detecting the period means waiting for the seed, in $O(1)$ memory:

```python
def period(step, seed):                      # step must be invertible, so the seed itself recurs
    state, k = step(seed), 1
    while state != seed:
        state, k = step(state), k + 1
    return k
```

This is how Problem 225 decides whether an odd $m$ divides any Tribonacci number. The triple of
residues mod $m$ evolves invertibly, so it walks one period and asks whether a zero appeared.
Problem 853 uses the Fibonacci version, the [Pisano period](/topics/domain/pisano-period), and
combines prime-power periods with an LCM rather than computing each $n$'s period directly.
Problem 167's Ulam-sequence membership bits follow a recurrence over GF(2) whose window update is
a bijection. So the bit stream is purely periodic, and the $10^{11}$th term costs one period of
work. Problem 238's [Blum Blum Shub](https://en.wikipedia.org/wiki/Blum_Blum_Shub) generator is a
squaring map, which is not a bijection in general. For that seed, though, the orbit turns out to
return exactly to its start, so the infinite digit string is one block repeated. That was
observed for this seed, not guaranteed by the map.

**$f$ is not invertible: a tail, then a loop.** Then you have to remember where you've been. A
dictionary from state to first index finds both $\mu$ and $\lambda$ in one pass, and lets you jump
to any index:

```python
def nth_state(f, x0, n):                     # f^n(x0) for any deterministic f on a finite set
    seen, x = {}, x0
    for i in range(n):
        if x in seen:                         # x = f^i(x0) = f^mu(x0): a cycle of length i - mu
            for _ in range((n - i) % (i - seen[x])):
                x = f(x)
            return x
        seen[x] = i
        x = f(x)
    return x
```

Problem 64 finds each square root's continued-fraction period by tracking the expansion's state
triple until it repeats. Problem 197's floating-point map truncates every value to nine decimals,
so it lives on a finite grid, falls onto a two-cycle after a few hundred steps, and answers for
$n = 10^{12}$ immediately. When memory matters,
[Floyd's or Brent's algorithm](https://en.wikipedia.org/wiki/Cycle_detection#Algorithms) finds
$\mu$ and $\lambda$ with two pointers and $O(1)$ storage. None of the problems here needed that,
because their cycles are short and a dictionary is simpler.

## Many walks over one graph

Several problems run the iteration from *every* starting point. The state space is then a
[functional graph](/topics/domain/functional-graph), where every node has exactly one outgoing
edge. It decomposes into components, each a cycle with trees hanging into it. Walking each start
separately repeats work, so the solutions classify nodes once and reuse the result:

- **Problem 74** counts digit-factorial chains of a given length. Each walk stops when it closes
  a cycle or hits a node whose chain length is already cached. One backward pass then fills in the
  length of every node on the path.
- **Problem 95** looks for the longest amicable chain under the divisor-sum map. A walk stops when
  it leaves the range, reaches a node classified in an earlier walk, or closes a new cycle. Only
  the last case can produce a candidate, and each node is classified once.
- **Problem 92** has just two terminal behaviours, the fixed point $1$ and the cycle through $89$.
  So it classifies digit-square *sums* once and counts starting numbers by sum.
- **Problem 209** works with a permutation of $2^6$ states. The constraint couples each state only
  to its image, so the count factors as a product over cycles, and a cycle of length $n$
  contributes a [Lucas number](/topics/technique/lucas-number).

Cycles also show up *inside* bigger algorithms. In Problem 943 a node's sequence of child masks is
deterministic and repeats after a short prefix. So each chain stores its prefix sums with $\mu$ and
$\lambda$, and "the first $k$ children" is answered by counting whole periods with one division.

## How to reason about it

- **Name the state, and bound it.** The pigeonhole argument only applies once you've said exactly
  what the state is: a residue triple, a sliding bit window, a continued-fraction triple, a
  truncated real. The size of that state space bounds $\mu + \lambda$, and it is often much
  smaller in practice.
- **Check invertibility first.** If the map is a bijection you get a pure cycle, $O(1)$ memory and
  a seed-recurrence test. Linear recurrences mod $m$ whose last coefficient is a unit, and
  permutations, are the common cases.
- **Use exact equality, not a tolerance.** Cycle detection is only sound on an exactly
  represented state. Problem 197 is safe because its floor truncation makes floats repeat bit for
  bit. A float map without that truncation may never repeat exactly.
- **Separate the tail from the cycle when you jump.** An index before $\mu$ must be read directly,
  and an index after it reduces modulo $\lambda$ from $\mu$. Problem 197's smaller test case lands
  before the cycle, and the loop handles both exits.
- **Share work across starts.** Over a functional graph, cache each node's result the first time
  any walk classifies it, so the whole graph costs $O(N)$ rather than $O(N \cdot \text{chain})$.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0064](/solutions/0064/) — Odd Period Square Roots
- ● [0074](/solutions/0074/) — Digit Factorial Chains
- ● [0092](/solutions/0092/) — Square Digit Chains
- ● [0095](/solutions/0095/) — Amicable Chains
- ● [0167](/solutions/0167/) — Investigating Ulam Sequences
- ● [0197](/solutions/0197/) — A Recursively Defined Sequence
- ● [0209](/solutions/0209/) — Circular Logic
- ● [0225](/solutions/0225/) — Tribonacci Non-divisors
- ● [0238](/solutions/0238/) — Infinite String Tour
- ● [0853](/solutions/0853/) — Pisano Periods 1
- ● [0943](/solutions/0943/) — Self Describing Sequences

<!-- /problems -->
