<!-- tags: [lookup-table] -->
<!-- status: final -->
# Lookup table

A [lookup table](https://en.wikipedia.org/wiki/Lookup_table) is the oldest optimisation in
computing — [trigonometric tables](https://en.wikipedia.org/wiki/Trigonometric_tables) predate the
computer by two millennia — and it is still the one with the best ratio of payoff to cleverness. The tag lands on the problems below for
two quite different reasons, and separating them is most of the value of this page. Sometimes the
table is a **speed** decision: a read replaces a computation you would otherwise repeat. Sometimes
the table *is* the **specification**: it holds a relation that has no formula behind it, and the
code around it exists only to index it. Both are the same move — **turn a question into an
address** — and the second one is the reason the technique never goes out of date.

## The idea

A lookup table answers a question by indexing a stored array of answers. The precondition is not
"the answer is expensive" but "the input can be reduced to a small dense key", usually an integer
in a known range, so that retrieval is address arithmetic — `base + k × width`, one instruction, no
comparison, no hash, no search.

That clause is what distinguishes it from its neighbours, which the problem lists overlap with
heavily. [Memoization](/topics/technique/memoization) stores the same kind of answers but *lazily*
and keyed by call arguments, paying a hash per query for the freedom of not knowing the key space in
advance. [Precompute once, reuse](/topics/takeaway/precompute-once-reuse) is the accounting
principle — build cost against query count. A lookup table is the data structure you reach for when
the key is already an index, or can be made one cheaply, and you intend to fill every slot.

What ends up in the slots falls into four recurring shapes:

| What the table holds | Indexed by | Seen in |
| --- | --- | --- |
| A relation with no formula | a symbol or small integer | 17 (number → English word), 89 (Roman symbol ↔ value), 103 (the small cases given in the statement) |
| Values of an expensive function | its argument | 34, 862 (factorials), 365 ($i! \bmod p$), 160 (running products of units mod $p^5$), 504 ($\gcd(i,j)$), 177 ($\sin(k\pi/n)$), 254 (factorial-base digit sums) |
| The outcome of a case analysis | the discriminant | 381 ($p \bmod 8$), 159 (digital root), 244 (legal moves per blank cell) |
| An entire state space's answers | a packed state | 244 (distance to target per board state) |

## When the table is the specification

Problem 89 converts Roman numerals to integers and back, and it carries two tables pointing in
opposite directions — symbols to values for parsing, values to numerals for encoding:

```python
values: dict[str, int] = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

numerals: dict[int, str] = {
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", ...
    40: "XL", 50: "L", ... 90: "XC", 100: "C", ... 900: "CM", 1000: "M",
}
```

The second table is the interesting one. It lists the *subtractive compounds* — `IV`, `IX`, `XL`,
`XC`, `CD`, `CM` — as first-class entries beside the plain denominations, and because they are in
the table, the encoder that greedily takes the largest fitting entry produces the minimal form with
no special case anywhere in the code. **Put the irregularity in the data and the code has no
irregularity.** That is the whole design, and it is why the [Roman
numeral](/topics/domain/roman-numerals) conversion is twenty lines rather than a thicket of `if`s.

Problem 17 spells numbers in English on the same principle: the table carries $0$–$20$ and the
tens, which is exactly the part of English that is irregular, and everything above is composed by
rule from comma-separated triplets. Problem 103 uses a table for a third reason again — the optimum
sets for the small sizes named in the statement seed a recursive search, so the table is a **base
case** rather than an optimisation. In none of these three is the table making anything faster. It
is the input.

## When the table is a speed decision, the index is the design

Once the goal is speed, the question stops being "what do I store" and becomes "what is the key,
and how dense is it".

**Dense integer key → an array.** Problem 244 walks the state graph of a $4 \times 4$ sliding
puzzle whose states pack into 20 bits (blank position plus a colour mask), and stores the BFS
distance for every one of them in a flat `bytearray` of $2^{20}$ entries — one megabyte, one byte
per state, indexed directly by the packed integer. A dictionary keyed by the same integers would
hold the same information at roughly ten times the memory and a hash per probe, in the inner loop
of a search that touches every state. See [`bytearray`](/topics/technique/bytearray) — the point is
that the state *encoding* and the table's *addressing* were designed together.

**Sparse key → a hash.** The same problem 504 that builds a full $(m+1) \times (m+1)$ table of
$\gcd(i,j)$ — dense, every entry read many times — keeps its perfect squares in a `set`, because
the squares are sparse in the range they cover and no array indexed by "is this value a square"
would be worth its size. Density decides the container, not taste; see
[hash table](/topics/technique/hash-table).

**Pad the don't-cares.** Problem 381 reduces a sum of five factorials modulo a prime, via
[Wilson's theorem](https://en.wikipedia.org/wiki/Wilson%27s_theorem), to a value that depends on
nothing but $p \bmod 8$. The table has eight slots even though only four residues can occur — the
even entries hold zeros that are never read. Sizing it to the reachable residues would save four
machine words and cost a division-and-remap on every access. Problem 159 does the same with a
digital-root array whose entry for $0$ is defined as $0$ purely so indices $0$ and $1$ stay inert.
A table with dead slots is usually the right table: **arithmetic-free indexing is worth more than
the memory the padding costs.**

## The payoff memoization cannot give you

A branch cannot be vectorised. A table can — and this is the sharpest practical argument for
preferring one over the other when both would work.

Problem 381's case analysis on $p \bmod 8$ could have been written as a four-way `if`. Written as an
8-entry table it becomes `t_for_residue[primes % 8]`, one [fancy-index](/topics/technique/fancy-indexing)
over a [NumPy](/topics/technique/numpy) array holding every prime below $10^8$, and the entire
case analysis is resolved for all of them in a single pass with no interpreter involvement. The
benchmark shows what that is worth: Python 0.085 s against C 0.039 s, a factor of 2.2 for an
interpreted language against a compiled one. Compare its neighbours on this same page, where the
table is read one scalar at a time from a Python loop — problem 254 at 1.43 s against 0.018 s in C,
problem 504 at 7.06 s against 0.097 s, both around 75×. Same technique, same tables; the difference
is whether the index is a scalar or a whole array (see [vectorised](/topics/technique/vectorized)).

The other end of the range is worth seeing too. Problem 177 precomputes $\sin(k\pi/n)$ once and
indexes it throughout — the textbook trigonometric table — in both languages, and the two land at
2.149 s and 2.135 s. When the table does enough of the work, the language stops mattering.

## Paying for the table

The trade is [space against time](https://en.wikipedia.org/wiki/Space%E2%80%93time_tradeoff), and
the ratio that decides it is **entries built against reads served**. Problem 504 builds $m^2$ gcd
entries and reads them $O(m^4)$ times — no argument to have. Problem 254 builds a table over all
$9! = 362{,}880$ residues once and consults it throughout a scan that would otherwise recompute
factorial-base digit sums constantly.

But the ratio can go the other way, and one of these problems shows it honestly. Problem 365
applies [Lucas's theorem](/topics/domain/lucass-theorem) to a binomial coefficient modulo each prime
$p$ in a range, and for each prime it builds a full table of $i! \bmod p$ for $i < p$ — several
thousand entries — in order to read about fifteen of them, one per base-$p$ digit of $n$ and $k$.
In isolation that is a losing trade by two orders of magnitude. It survives because the whole phase
sits beside an $O(P^3)$ CRT combination that dwarfs it, and because the table makes the Lucas loop
obviously correct. Worth knowing that it is a deliberate loss rather than assuming a table is free:
**count the reads before you build.**

One rule is specific to this repository and easy to get wrong. Build tables **inside** `solve()`.
The harness times repeated calls, so a table hoisted to module level is built once at import and is
free from the second run onward — the benchmark then reports a program nobody runs. Problem 160
rebuilds its few-thousand-entry product table on every call and says so in the docstring; 17 calls
`cache_clear()` on its memo at the top of `solve()` for exactly the same reason. The corollary is
also the healthier habit: a table built inside the function can be
[sized to the input](/topics/takeaway/size-work-to-the-input), which a module-level constant with a
guessed bound never is.

## How to reason about it

- **Ask what the key is first.** If the input is already a small integer, or one cheap operation
  away from being one (`p % 8`, a packed state, a digit), the table is an array and the lookup is
  free. If it is not, you are choosing between a hash and a redesign of the encoding — problem 244
  chose the redesign.
- **Dense fills an array; sparse wants a hash.** Estimate what fraction of slots you would actually
  use before allocating.
- **Pad rather than remap.** Unreachable slots that keep the index arithmetic-free are cheaper than
  the arithmetic that would avoid them.
- **Count entries built against reads served.** A table read fewer times than it has entries is a
  loss, and only survives when something larger hides it.
- **Put the exceptions in the data.** Every irregularity you can move from control flow into a table
  is a branch you cannot get wrong.
- **If the index can be an array, the whole case analysis vectorises** — which is the one advantage
  a table has over a memo, and it is frequently the difference between a 2× gap to C and a 75× one.
- **Build it inside the timed function**, sized to the actual input.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0017](/solutions/0017/) — Number Letter Counts
- ● [0019](/solutions/0019/) — Counting Sundays
- ● [0034](/solutions/0034/) — Digit Factorials
- ● [0043](/solutions/0043/) — Sub-string Divisibility
- ● [0089](/solutions/0089/) — Roman Numerals
- ● [0103](/solutions/0103/) — Special Subset Sums: Optimum
- ● [0159](/solutions/0159/) — Digital Root Sums of Factorisations
- ● [0160](/solutions/0160/) — Factorial Trailing Digits
- ● [0177](/solutions/0177/) — Integer Angled Quadrilaterals
- ● [0244](/solutions/0244/) — Sliders
- ● [0254](/solutions/0254/) — Sums of Digit Factorials
- ● [0365](/solutions/0365/) — A Huge Binomial Coefficient
- ● [0381](/solutions/0381/) — $(\text{prime}-k)$ Factorial
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0862](/solutions/0862/) — Larger Digit Permutation

<!-- /problems -->
