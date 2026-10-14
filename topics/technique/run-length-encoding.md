<!-- tags: [run-length-encoding] -->
<!-- status: final 2026-10-12 -->
# Run-length encoding

[Run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding) describes a sequence by
its maximal blocks of equal symbols: `11110001` becomes four `1`s, three `0`s, one `1`. As a
compression scheme it is old and simple. As a way of *thinking* about a problem it keeps
returning, because many processes treat a run as one unit. A run is cleared in one go, it
behaves independently of its neighbours, or it is itself the quantity being described. The three
problems below use runs in three different roles: as the answer's format, as the definition of
the sequence, and as the unit of independence that turns a probability into a count.

## The idea: work in runs, not elements

In Python the encoding itself is one line:

```python
from itertools import groupby
runs = [(symbol, len(list(group))) for symbol, group in groupby(sequence)]
```

The interesting part is never the encoding. It is noticing that the problem's structure lines up
with the runs, so that you can compute on the $r$ runs instead of the $n$ elements, or on run
lengths instead of positions.

- **Runs as a compressed answer (Problem 175).** The function counts ways to write $n$ as sums of
  powers of two, each used at most twice. It is
  [Stern's diatomic sequence](/topics/domain/sterns-diatomic-sequence) in disguise, and the ratio
  of consecutive values walks the [Calkin–Wilf tree](/topics/domain/calkin-wilf-tree). Finding
  $n$ for a given ratio means walking from that fraction up to the root, recording one binary
  digit per step. A run of identical steps is one subtraction step of the
  [Euclidean algorithm](/topics/technique/euclidean-algorithm) repeated, so a single division
  produces a whole run. The run lengths turn out to be the terms of the fraction's
  [continued fraction](/topics/domain/continued-fraction). The answer is asked for as a run-length
  encoding, and that's not just a convenience: the run list is only as long as the continued
  fraction, while $n$ itself can be far too long to write out. The statement's own example, $13/17 \mapsto 241 = 11110001_2 \mapsto
  4,3,1$, is a good check.
- **Runs as the definition (Problem 943).** A self-describing sequence alternates runs of $a$s
  and $b$s, and its run lengths are the sequence itself. It is a two-symbol
  [Kolakoski sequence](/topics/domain/kolakoski-sequence). Reading the definition backwards makes
  every element the parent of the run it describes, so a prefix of the sequence is the leaf level
  of a derivation tree of logarithmic height. A subtree is fixed by its value, its height, and the
  position parities down its left edge. So [memoization](/topics/technique/memoization) on that
  key, plus [cycle detection](/topics/technique/cycle-detection) on long runs of identical
  children, sums $2 \times 10^{13}$ terms by visiting at most a few million distinct shapes.
- **Runs as independent blocks (Problem 951).** Two players draw from a red and black deck, and a
  turn may take a second card only if it matches the first. So no turn ever crosses from one run
  to the next. The number of turns spent on each run is
  [independent](/topics/domain/independence-probability-theory) of the others, and the signed
  expectation that decides fairness becomes a *product* of per-run factors. Each factor follows a
  short recurrence in the run length. Fairness then depends only on which run lengths appear, and
  counting decks by their run lengths is counting pairs of
  [compositions](/topics/domain/composition-combinatorics) of $n$, one for each colour.

That last correspondence is worth knowing on its own. A binary string of length $n$ with $r$
runs is exactly a choice of first symbol plus a composition of $n$ into $r$ positive parts. So
any count of strings constrained by their run lengths ("no run of length 2", "all runs at most
$k$") becomes a composition count, which is a small
[dynamic program](/topics/technique/dynamic-programming) over (parts, total).

## How to reason about it

- **Ask whether a run is a unit of behaviour.** If a process can't cross a run boundary in one
  step, or treats a block of equal symbols the same way throughout, the runs are independent
  pieces. Products, sums and DPs over runs follow.
- **Batch a run with arithmetic.** When a loop repeats the same step $k$ times, compute $k$
  directly, by a division in 175 or by counting whole periods in 943. One step per element is
  what makes a naive version too slow; 943's first version walked every child and paid for it.
- **Mind the edges of the encoding.** The first and last run are where the off-by-ones live. In
  175 the walk must stop *on* the root rather than overshoot it, so an exact division records
  $k - 1$. The root's leading $1$ then has to be folded into the top run. In 951, equal and
  unequal run counts per colour fix which colour leads, and each case is counted separately.
- **Keep runs as the representation when the expansion is huge.** If the expanded object has
  millions of elements but a few runs, never expand it. Produce, compare and output the runs.
- **Check against direct generation.** Generate the actual sequence or deck for small parameters
  and compare. 943 was checked on 2,000 random small cases, 951 by exact simulation of every deck
  up to $n = 9$, and 175 against the statement's $13/17$ example.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0175](/solutions/0175/) — Fractions and Sum of Powers of Two
- ● [0943](/solutions/0943/) — Self Describing Sequences
- ● [0951](/solutions/0951/) — A Game of Chance

<!-- /problems -->
