<!-- tags: [split-inputs-into-behaviour-classes] -->
<!-- status: final 2026-11-04T13:11Z -->
# Split inputs into behaviour classes

Many problems ask about a deterministic process run on *every* input in a huge range: the
iteration count of a square-root procedure for each of $9 \times 10^{13}$ starting values, the
starting positions of a digit string across a $10^{13}$-digit stream, or a game value for each
of $10^5$ numbers. Simulating each input separately is hopeless. But the process almost never
looks at the whole input. It reads a quotient, a digit length, a prefix, a value. Inputs that agree
on what it reads behave *identically* from then on. So the move is to carry whole **classes** of
inputs at once, usually intervals, arithmetic progressions or groups with a multiplicity, and
split a class only at the point where its members' behaviour actually diverges. The work then
scales with the number of distinct behaviours, not the number of inputs. The same move also goes
further than intervals: classes can merge as well as split, can share a shape instead of a value,
can choose the method instead of the count, and can divide the coordinates of a problem instead of
its inputs.

## The idea: follow what the process reads

The question to ask of any per-input process is: *which function of the input does the next step
actually depend on?* The classes are the
[level sets](https://en.wikipedia.org/wiki/Level_set) of that function, and the cost of the method
is the number of classes you ever create.

- **Problem 255** runs an integer version of Heron's method on every 14-digit $n$. Each step reads
  $n$ only through $\lceil n / x \rceil$. For a fixed estimate $x$ that quotient is constant on
  blocks of $x$ consecutive integers, and adjacent blocks map to the same next estimate. So an
  interval of $n$ sharing an estimate splits into a handful of child intervals, one per next
  estimate. This is [quotient blocking](/blogs/technique/quotient-blocking) applied repeatedly.
  The full tree has about $\sqrt{10^d}$ nodes instead of $10^d$ leaves, and every interval that
  stops adds its step count times its width in one multiplication.
- **Problem 305** needs the $n$-th occurrence of a digit string in the concatenation
  $123456789101112\ldots$. I count the occurrences that start inside $1..N$ and
  [binary-search](/blogs/technique/binary-search-algorithm) on $N$. The count is possible only
  because every occurrence falls into one of **two** classes. Either it lies inside one integer,
  counted per digit length with free leading and trailing digits, or it crosses a boundary between
  consecutive integers, counted by the position of that boundary. That second case is an
  arithmetic progression of integers, so the count is two floor divisions.
- **Problem 257** counts integer triangles by perimeter. Every triangle that qualifies is one
  *primitive shape* scaled by an integer, and the shape fixes everything except the scale. So each
  admissible shape contributes $\lfloor N / L \rfloor$ triangles at once, where $L$ is its smallest
  perimeter. I visit tens of millions of shapes, and none of the scaled copies.
- **Problem 963** evaluates a game value for every number up to $N$, but only a few thousand
  distinct values occur, and fewer still distinct "shapes". Grouping the numbers by value, with a
  multiplicity, and then pairing *groups* rather than numbers turns $O(N^2)$ pair sums into
  $O(D^2)$ for $D$ distinct values.

The arithmetic for "how many members does this class have" is nearly always a floor division.
Counting the members of an arithmetic progression inside an interval is the workhorse:

```python
def count_progression(lo, hi, r, m):        # n in [lo, hi] with n ≡ r (mod m)
    return max(0, (hi - r) // m - (lo - 1 - r) // m)
```

Python's `//` rounds toward $-\infty$, which is what this formula needs. C's `/` truncates toward
zero, so a C port needs its own floor-division helper wherever a bound can go negative. Problem
305's C port carries exactly that helper.

When the classes come from a process that runs for several steps, the skeleton is a worklist of
classes:

```python
stack = [(lo, hi, initial_state)]
while stack:
    lo, hi, state = stack.pop()
    for sub_lo, sub_hi, nxt in split(lo, hi, state):     # pieces on which one step agrees
        if finished(nxt):
            total += weight(nxt) * (sub_hi - sub_lo + 1)
        else:
            stack.append((sub_lo, sub_hi, nxt))
```

## Beyond intervals: four other kinds of class

The problems above all carry a set of inputs and count it. Four later ideas keep the question,
*what does the process actually read?*, and change what a class is.

### Classes that merge: the state of a prefix

Problem 706 counts the $d$-digit numbers, with $d = 10^5$, whose number of substrings divisible by
3 is itself divisible by 3. The inputs are strings, and there is no interval to carry. But read a
number left to right and ask what the future needs. A substring is divisible by 3 when the prefixes
at its two ends have equal digit sums mod 3, so appending a digit adds one new substring for each
earlier prefix with the new residue. Two prefixes that agree on those counts mod 3 and on the tally
so far respond identically to every continuation, whatever their digits were. They are one class
for good, which is the equivalence behind the
[Myhill–Nerode theorem](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem).

So classes here *merge*. In 255 the tree only grows, while in 706 every step pours the classes back
into the same fixed set. A [finite-state machine](/blogs/technique/finite-state-machine) is what a
partition looks like once it stops growing. Three reductions produce this one, and each is a
question about what is read:

- **Close the summary.** The tally mod 3 is all the question reads, but it is not enough to predict
  the next tally. The test is that the same class plus the same next symbol must give the same next
  class. I add what is missing, here the prefix counts, until that holds. This is the
  [full-state rule for memo keys](/blogs/takeaway/memo-key-is-the-full-state) in another guise.
- **Drop the coordinates nothing reads.** Measuring the counts relative to the current residue
  removes the residue from the state, taking 243 states to 81. That is a quotient by a
  [symmetry](/blogs/takeaway/exploit-symmetry).
- **Class the symbols too.** The ten digits drive only three different transitions, so they become
  three edges weighted $(4, 3, 3)$, or $(3, 3, 3)$ for the leading digit, which cannot be zero.

The worklist above then becomes a vector of class sizes, pushed forward one symbol at a time:

```python
sizes = {start: 1}                            # class -> how many inputs are in it
for _ in range(length):
    nxt = Counter()
    for state, size in sizes.items():
        for symbol_class, weight in symbol_classes:
            nxt[step(state, symbol_class)] += size * weight
    sizes = nxt
```

Because the step is the same each time, it is one fixed matrix, and
[matrix exponentiation](/blogs/technique/matrix-exponentiation) turns the length from a loop bound
into a logarithm. This is the [transfer-matrix method](/blogs/domain/transfer-matrix-method). Ten
times the digits costs only a few more squarings.

### Classes that share a shape, not a value

Problem 844 sums the $k$-Markov numbers up to $10^{18}$ for every $k$ up to $10^{18}$. Each $k$ has
its own tree of solutions, grown by [Vieta jumping](/blogs/technique/vieta-jumping) from the
all-ones tuple, and the values differ from one $k$ to the next. Yet the *computation* is the same
for every large $k$: the same branches, with values $k - 1$, then $k^2 - k - 1$, and so on. So I run
the search once with
[$k$ as a polynomial variable](/blogs/takeaway/treat-a-parameter-as-a-polynomial-variable) and get
under a hundred polynomials, each valid from a threshold $T = 10$ up to its own cutoff.
[Power sums](/blogs/technique/faulhabers-formula) then add each polynomial over its whole range of
$k$ at once, and the few $k$ below $T$ are walked numerically.

So the requirement on a class is weaker than it first looks. Its members need not give the same
result, only follow the same path. The result is then a formula in the input, and the class
contributes a sum where 255's contributes a product. The price is that "same path" is a claim about
a vast range of cases, so it has to be earned. The code asserts that every polynomial increases past
$T$, without which pruning at $T$ would be unsound, and that a tuple always has a one left to
replace. Two polynomials could also meet at a particular $k$ and count one number twice, so each
pair is checked with
[Descartes' rule of signs](https://en.wikipedia.org/wiki/Descartes%27_rule_of_signs) and, where that
cannot rule a meeting out, a bounded scan. The threshold makes a useful test too, because the split
point is a free choice: the answer must not change as $T$ moves, and it does not.

### Classes that choose the method

Sometimes the class saves nothing by multiplicity at all. In Problem 752, $g(x)$ is the
[multiplicative order](/blogs/domain/multiplicative-order) of $1 + \sqrt 7$ modulo $x$, and every
prime still gets its own computation. What the class supplies is a *theorem*. The norm of
$1 + \sqrt 7$ is $-6$, so any $x$ sharing a factor with 6 has no order, which disposes of two thirds
of the range with one test. The
[Chinese remainder theorem](/blogs/technique/chinese-remainder-theorem) reduces the rest to prime
powers, and then one [quadratic-residue](/blogs/technique/quadratic-residue) test sorts the primes.
Where 7 has a square root the ring splits into two copies of $\mathbb F_p$, and the order divides
$p - 1$. Where it does not, the ring is $\mathbb F_{p^2}$, and Frobenius moves most of the work back
into $\mathbb F_p$, leaving one factor that divides $p + 1$. The one ramified prime, 7, has its own
small unit group. Each class has a different algebra, so each has a different known multiple to
reduce from. A treatment that ignored the classes would have to work in the much larger group of
order $p^2 - 1$.

Problem 764 is the same kind of split, resolved earlier, on paper. Once $16x^2 + y^4 = z^2$ is
rewritten as a Pythagorean triple, the condition $\gcd(x, y, z) = 1$ behaves differently for odd and
even $y$, and the factoring argument differs with it. Each parity class yields its own two-parameter
family, and the even class's two sub-cases collapse into one. The code has no per-input branch at
all: it is two loops, each [generating only its own class](/blogs/takeaway/reduce-before-coding),
over $O(N^{1/2})$ parameter pairs. A class that can be derived should be generated, not filtered.

### Classes of coordinates, not inputs

Problem 619 counts subsets of an interval whose product is a perfect square. A number matters only
through the parities of its prime exponents, so the count comes from the
[rank of a matrix over GF(2)](/blogs/takeaway/count-solutions-by-rank), with a column for every
prime up to $b$. Here it is the *columns* that split into two behaviours. A number up to $b$ has at
most one prime above $\sqrt b$, to the first power, so such a prime is a coordinate that a few rows
share and nothing else touches. Each large prime contributes exactly 1 to the rank: one carrier
becomes its pivot and the others absorb that pivot's small-prime part. General
[Gaussian elimination](/blogs/technique/gaussian-elimination) is left with only the primes below
$\sqrt b$, just 186 of them for the target range. The large class needs no elimination, because its structure has already decided
the outcome, and the hard algorithm runs only on the class that needs it.

## How to reason about it

Reach for this when the input range is far larger than the number of things that can *happen*.
Signs of it are floors and ceilings of $n / x$, behaviour that depends on digit length or a
prefix, a value function with a small image, or a family generated by scaling. Others are a future
that depends on a small summary of the past, a parameter that changes values without changing the
branching, and a case split that changes which theorem applies. The gain is the ratio of inputs to
classes, often the difference between $10^{14}$ and $10^7$.

- **Find the coarsest function the process depends on.** Split on what the next step *reads*,
  not on the input itself. If you split too finely, the classes are just the inputs again.
- **Split lazily.** Keep a class whole until a step tells its members apart. In 255 most
  intervals have exactly one child at every level after the first, so the tree is mostly long
  chains. Following the last child in place, rather than pushing it, removed most stack traffic.
- **Handle the big first split separately.** The first split is often the widest: 255's root has
  millions of children. Iterating them in a plain loop, and keeping only one subtree on the stack
  at a time, holds memory to a few entries. Pushing them all at once would build millions of
  tuples first.
- **Make the classes provably disjoint and complete.** Every input has to land in exactly one
  class. In 305 that is a classification by the first boundary inside an occurrence, and in 257
  it is the unique reduced fraction behind each triangle. Prove it, and then check it, with a
  per-input brute force on a small range. 255 was checked against direct simulation for one to
  seven digits, 305 against a literal scan of the first $2 \times 10^7$ digits. Disjoint inputs do
  not guarantee disjoint *outputs*, either: 844's polynomials could in principle produce the same
  number, and the question asks for distinct ones.
- **Test every class, not just a range.** A check that never enters a class says nothing about it.
  752's given values matter because they reach split, inert and ramified primes as well as lifts to
  higher prime powers such as $5^4$ and $7^3$.
- **Look for the size where behaviour simplifies.** 619's primes above $\sqrt b$ and 844's $k$ from
  $T$ upward are both regimes where a strong structural fact holds. Past that point a cheap rule
  covers everything, and below it there is little enough left for the general method.
- **Watch the counting at the edges.** Clipping a child interval to its parent and handling an
  empty intersection are where off-by-one errors live. So are the leading-digit and leading-zero
  edge cases of digit-length classes. Write the clipping once, as a helper, and test it alone.

This is the counting cousin of [exploiting symmetry](/blogs/takeaway/exploit-symmetry). There
the classes are orbits of a transformation. Here they are the inputs that a step cannot tell
apart, and 706 shows the two working together.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0255](/solutions/0255/) — Rounded Square Roots
- ● [0257](/solutions/0257/) — Angular Bisectors
- ● [0305](/solutions/0305/) — Reflexive Position
- ● [0564](/solutions/0564/) — Maximal Polygons
- ● [0619](/solutions/0619/) — Square Subsets
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0752](/solutions/0752/) — Powers of $1+\sqrt 7$
- ● [0764](/solutions/0764/) — Asymmetric Diophantine Equation
- ● [0844](/solutions/0844/) — $k$-Markov Numbers
- ● [0963](/solutions/0963/) — Removing Trits

<!-- /problems -->
