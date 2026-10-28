<!-- tags: [insertion-sort] -->
<!-- status: final 2026-10-28T16:38Z -->
# Insertion sort

[Insertion sort](https://en.wikipedia.org/wiki/Insertion_sort) is the sort everyone writes
first and then stops thinking about: grow a sorted prefix, take the next element, slide it left
until it fits. In this repository it turns up in two quite different roles. In 61 and 868 it is a
*tool*: the dozen lines of C you write when you need a handful of values in order and `qsort` is
more ceremony than the job deserves. In 523 it is the *subject*: the problem describes a strange
sorting procedure, and the whole solution is recognising it as insertion sort and counting what it
costs. The general sorting picture, and why a sort is usually a means rather than the point, is on
the [sorting algorithm](/topics/technique/sorting-algorithm) page; this page is about the one
algorithm simple enough to analyse exactly.

## The idea

After step `i`, the first `i` elements are sorted among themselves. The next element `key` is
compared against the prefix from the right; each larger element shifts one place to make room,
and `key` drops into the gap. Problem 61's C port has the canonical form, verbatim:

```c
for (int i = 1; i < len; i++) {
    int key = sorted[i];
    int j = i - 1;
    while (j >= 0 && sorted[j] > key) {
        sorted[j+1] = sorted[j];
        j--;
    }
    sorted[j+1] = key;
}
```

Three properties fall straight out of that loop, and they are the ones worth remembering:

- **Stable.** The test is strict `>`, so an element never passes an equal one; ties keep their
  input order.
- **In place, online.** No buffer beyond `key`, and the prefix is a valid answer at every step —
  the algorithm can consume a stream.
- **Adaptive.** The work for each element is exactly how far it has to travel. An already-sorted
  input costs one comparison per element and no shifts.

## Counting the cost

The analysis that makes insertion sort worth studying is that its cost is a sum of independent
per-element pieces. The number of shifts made for element `i` is the number of earlier elements
greater than it, so the total shift count is exactly the number of
[inversions](https://en.wikipedia.org/wiki/Inversion_(discrete_mathematics)) in the input, and
the comparison count is that plus at most one per element. That gives the familiar bounds —
`0` shifts when sorted, `n(n−1)/2` when reversed — but the sharper statement is `O(n + I)` for `I`
inversions, which is why the algorithm is excellent on nearly-sorted data and poor on random data.

For a [uniformly random permutation](https://en.wikipedia.org/wiki/Random_permutation), the
average falls out without any combinatorics. Element `k+1`'s rank among the first `k+1` is uniform
on `k+1` values, so its expected travel is `k/2`; summing over positions by
[linearity of expectation](https://en.wikipedia.org/wiki/Expected_value#Properties) gives
`n(n−1)/4` shifts. Hold on to that pattern — *cost per element depends only on its rank in the
prefix, and that rank is uniform* — because it is the whole engine of 523.

## The first-sort recurrence (523)

Problem 523 defines a procedure that scans from the front, stops at the first element smaller
than its left neighbour, moves that element to the front, and restarts. It reads like a bubble
sort variant, but the scan never gets past the first descent, so at every moment the list is a
sorted prefix followed by untouched elements. When the next untouched element `x` is reached, the
procedure works only inside the prefix until it is sorted again — one insertion per element,
exactly as above.

What differs is the cost of one insertion. Standard insertion sort pays linearly in how far `x`
travels. Here `x` jumps to the very front in a single move, which puts every smaller prefix
element *behind* it and out of order; each of those must then be re-inserted by the same
procedure, and each of those re-insertions displaces the elements smaller than *it*. If `T(s)` is
the cost of inserting an element that has `s` smaller elements ahead of it,

```
T(s) = 1 + T(0) + T(1) + … + T(s−1)
```

— one move for `x`, then one recursive insertion for each displaced element, the smallest first.
That recurrence closes in a line, and the closed form grows geometrically in `s` rather than
linearly. The expected total is then the standard argument again: the rank of each new element in
the prefix is uniform, so each piece is a short average of `T`, and the answer is one sum over
positions. The [expected value (application)](/topics/technique/expected-value-application) page
treats that second half — decomposing a random cost into per-step pieces, and why the answer must
be kept as an exact rational before rounding — as its main example.

The transferable lesson: when a problem describes an unfamiliar sort, ask what is *invariant*
between moves. A sorted prefix means insertion sort, and insertion sort means the cost decomposes
per element.

## Small sorts in C (61, 868)

Python solutions just call `sorted`. The C ports of 61 and 868 instead hand-write the loop above,
and for good reason:

- **The inputs are tiny.** Problem 61 sorts six-element cycles to get a canonical form for
  deduplication; 868 sorts the eighteen-or-fewer symbols of a permutation once, before ranking it
  in [Steinhaus–Johnson–Trotter](https://en.wikipedia.org/wiki/Steinhaus%E2%80%93Johnson%E2%80%93Trotter_algorithm)
  order. At that size the quadratic term is a few dozen comparisons, and an inlined loop with no
  [function-pointer comparator](/topics/technique/qsort) beats `qsort`'s per-comparison indirect
  call. This is the same reason production sorts such as
  [introsort](/topics/technique/introsort) and [Timsort](https://en.wikipedia.org/wiki/Timsort)
  switch to insertion sort below a cutoff of roughly 16–32 elements.
- **Parallel arrays move together.** Problem 61's final step sorts the results by their sums, with
  the sums and the member arrays held in separate tables. `qsort` would demand packing them into a
  struct first; insertion sort just shifts both arrays in the same loop, keyed on one.
- **Stability is free.** Nothing in either problem needs it, but a hand-rolled insertion sort
  cannot accidentally lose it — unlike `qsort`, whose order for equal keys is unspecified.

The pitfall is reaching for it out of habit once `n` is no longer small: insertion sort on random
input is `Θ(n²)`, and the crossover to `qsort` arrives at a few dozen elements, not a few thousand.
Use it when `n` is bounded by the problem, or the input is already nearly sorted; otherwise call
the library.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0061](/solutions/0061/) — Cyclical Figurate Numbers
- ● [0523](/solutions/0523/) — First Sort I
- ● [0868](/solutions/0868/) — Belfry Maths

<!-- /problems -->
