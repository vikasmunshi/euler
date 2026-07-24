<!-- tags: [parity-across-languages] -->
<!-- status: final -->
# Hold complexity fixed across ports

Most of the problems below carry two solutions for one index — a Python `pNNNN_sK.py` and a C
`pNNNN_sK.c` — and the harness times both against the same test cases, recording an `average` per
language. The comparison is only worth anything if the two programs do the *same work*. This page
is about the discipline that makes it worth something: when you port a solution to a second
language, hold the algorithm and its [complexity](https://en.wikipedia.org/wiki/Time_complexity)
fixed, so the benchmark measures the one thing that actually differs — the language's
[constant factor](https://en.wikipedia.org/wiki/Big_O_notation#Multiplication_by_a_constant).

## The idea

A running time is (roughly) an asymptotic term times a constant: `average ≈ c · f(n)`. Port a
solution faithfully and `f(n)` is identical on both sides, so the ratio of the two timings is just
`c_python / c_c` — a clean read on what a compiled, unboxed loop buys you over the
[CPython](https://en.wikipedia.org/wiki/CPython) interpreter's per-operation overhead. Let the
algorithm drift during the port — a better sieve here, an extra prune there — and the ratio now
conflates two effects, and the number teaches you nothing: you can no longer tell whether C was
faster because it is C or because you quietly solved a different problem.

This is why the project's C-translation convention states the bar as *"same algorithm, same
complexity"*, and calls a `.c` correct **precisely when its algorithm matches the Python
sibling's**. Problem 14 (Longest Collatz Sequence) is the clean case. Both
files run the same memoised recursion on [Collatz](https://en.wikipedia.org/wiki/Collatz_conjecture)
chain length, both rebuild the cache per call so every timed run pays full cost, and both scan only
the upper half of the range on the same power-of-two argument — the docstrings are shared verbatim.
Nothing about the *method* differs, so the recorded gap (Python ≈ 0.86 s against C ≈ 0.020 s at a
limit of one million — roughly 44×) is a pure constant-factor result. Problem 52 lands near 16×,
problem 49 near 4×; the spread across problems is itself the interesting data, and it only means
something because the numerator and denominator share a big-O.

## Parity is in the asymptotics, not the syntax

The trap is to read "faithful port" as "line-by-line transliteration". It is not. What must match
is the *shape of the work* — the asymptotic complexity and the hot-path operations — not the
surface code. Idioms should and must diverge:

- Problem 14's Python memoises with `functools.lru_cache`; the C sibling uses a flat `calloc`'d
  `long long` array indexed by `n`. Different data structures, same $O(1)$ lookup, same overall
  $O(N \log N)$ — that is parity.
- Where Python leans on unbounded integers, the faithful C port reaches for a
  [bignum](https://en.wikipedia.org/wiki/Arbitrary-precision_arithmetic) library
  ([GMP](https://gmplib.org/)) rather than silently truncating to 64 bits — matching the range,
  which is part of the algorithm, not changing it.

The sharpest instance runs the *other* way: sometimes the naive C is what breaks parity. Porting
Python's `pow(a, d, n)` with a hand-rolled `unsigned __int128` modular multiply looks faithful, but
for moduli wider than 64 bits it degrades to a bit-by-bit add-and-shift loop — $O(\text{bits})$ per
multiply — and loses to CPython's `pow`, which is itself fast bignum
[modular exponentiation](https://en.wikipedia.org/wiki/Modular_exponentiation). Keeping the
complexity fixed there means routing wide moduli through `mpz_powm` (a native `__int128` fast path
below $2^{64}$), so the C mirrors what CPython already does under the hood. The lesson: parity is
measured against the algorithm *as it actually runs*, hidden fast paths included — not against how
short the code looks.

## How to reason about it

- **Port for comparison, not for a win.** The goal is a like-for-like timing, so freeze the
  approach before you translate. If a better algorithm occurs to you mid-port, apply it to *both*
  languages as a new solution index, and let the benchmark compare the pair — don't smuggle it into
  one side.
- **Match the work, translate the idioms.** Pick each language's natural data structure and library
  for the same asymptotic job. Diverging syntax that preserves the complexity is faithful;
  converging syntax that changes it is not.
- **Watch for hidden fast paths.** A Python builtin is often a tuned C routine — `sorted`, `pow`,
  `set` membership, big-int multiply. Reimplementing it naively in C can be asymptotically or
  constant-factor *worse*, which inverts the comparison. When in doubt, reach for the library
  (`primesieve`, GMP) that mirrors what CPython is really doing.
- **A drifted port is a silent bug.** Because both may still print the right answer, unequal
  complexity won't fail the evaluator — it just quietly poisons the timing. Treat "do these two run
  the same algorithm?" as part of what "correct" means for a port.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0014](/solutions/0014/) — Longest Collatz Sequence
- ● [0018](/solutions/0018/) — Maximum Path Sum I
- ● [0049](/solutions/0049/) — Prime Permutations
- ● [0052](/solutions/0052/) — Permuted Multiples
- ● [0054](/solutions/0054/) — Poker Hands
- ● [0060](/solutions/0060/) — Prime Pair Sets
- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0084](/solutions/0084/) — Monopoly Odds
- ● [0088](/solutions/0088/) — Product-sum Numbers
- ● [0105](/solutions/0105/) — Special Subset Sums: Testing
- ● [0126](/solutions/0126/) — Cuboid Layers
- ● [0135](/solutions/0135/) — Same Differences
- ● [0144](/solutions/0144/) — Laser Beam Reflections
- ● [0153](/solutions/0153/) — Investigating Gaussian Integers
- ● [0169](/solutions/0169/) — Sums of Powers of Two
- ● [0170](/solutions/0170/) — Pandigital Concatenating Products
- ● [0181](/solutions/0181/) — Grouping Two Different Coloured Objects
- ● [0189](/solutions/0189/) — Tri-colouring a Triangular Grid
- ● [0192](/solutions/0192/) — Best Approximations
- ● [0198](/solutions/0198/) — Ambiguous Numbers
- ● [0203](/solutions/0203/) — Squarefree Binomial Coefficients
- ● [0215](/solutions/0215/) — Crack-free Walls
- ● [0223](/solutions/0223/) — Almost Right-angled Triangles I
- ● [0478](/solutions/0478/) — Mixtures
- ● [0487](/solutions/0487/) — Sums of Power Sums
- ● [0501](/solutions/0501/) — Eight Divisors
- ● [0504](/solutions/0504/) — Square on the Inside
- ● [0549](/solutions/0549/) — Divisibility of Factorials
- ● [0650](/solutions/0650/) — Divisors of Binomial Product
- ● [0719](/solutions/0719/) — Number Splitting
- ● [0720](/solutions/0720/) — Unpredictable Permutations
- ● [0743](/solutions/0743/) — Window into a Matrix
- ● [0845](/solutions/0845/) — Prime Digit Sum
- ● [0965](/solutions/0965/) — Expected Minimal Fractional Value

<!-- /problems -->
