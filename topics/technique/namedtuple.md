<!-- tags: [namedtuple] -->
<!-- status: final -->
# NamedTuple

A [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) is a tuple whose
positions have names. That sounds cosmetic, and in most code it is; in these problems it is not,
because the tuple in question is usually a **dynamic-programming state** being used as a
[`dict`](/topics/technique/dict) key. The key has to be hashable, so it has to be a tuple — and once
a state has four or five components, `state[2]` stops meaning anything to the reader while
`state.a3` still does.

## The idea

Two spellings, one result. The class form from `typing` takes annotations and may carry methods and
properties:

```python
class Sheets(NamedTuple):
    a1: int
    a2: int
    a3: int
    a4: int
    a5: int

    @property
    def total(self) -> int:
        return sum(self)
```

The older functional form,
[`collections.namedtuple("Ring", ["outer", "inner"])`](https://docs.python.org/3/library/collections.html#collections.namedtuple),
produces the same kind of object without the annotations — problem 68 uses it for the two record
types it prints in its `--show` diagnostics, which is the lightweight end of the technique: naming
fields so a debug line reads `Ring(outer=..., inner=...)` instead of a wall of anonymous numbers.

Whichever spelling, what you get back is a genuine `tuple` subclass, and *that* is the property worth
understanding. It is immutable and hashable, so it can key a dict or join a set. It compares and
hashes **structurally, and across types**: `Sheets(1, 0, 0, 0, 0) == (1, 0, 0, 0, 0)` is `True`, and
the two hash identically, so a named state and a bare tuple with the same contents are *the same
dict key*. It unpacks (`a, b, c = state`), indexes, iterates, and slices. Anything that accepted a
tuple accepts it unchanged — `sum(self)` in the property above sums the five fields because the
instance *is* the sequence.

## Where it earns its place

Problem 151 is the case the tag was cut for. The state of the envelope is a five-vector of sheet
counts, the batch-by-batch propagation is a
[Markov chain](/topics/domain/markov-chain) over a dict from state to probability, and each of the
five possible draws maps one state to another. Written as a bare 5-tuple, the transition is ten
lines of index arithmetic that nobody can check by eye. Written as a `NamedTuple`, three things fall
out at once:

- the transition becomes a **method on the state** — the state machine's alphabet lives next to the
  state it acts on, and each branch constructs its successor by name;
- `_asdict()` turns the state into `field → count`, so "for each sheet size still present, with
  multiplicity" is a plain iteration over the fields rather than a `zip` against a separate list of
  labels;
- the dict of probabilities is keyed on the state with no conversion, because it is already a tuple.

The `_asdict()` point generalises: a `NamedTuple` is the cheapest way to have a value be *both* a
positional record (fast, hashable, unpackable) and a labelled mapping (readable, iterable by field)
without maintaining a [parallel array](/topics/technique/parallel-array) of names.

## How to reason about it

- **Three fields is the threshold.** A `(numerator, denominator)` pair or an `(x, y)` point is
  self-documenting; nobody needs `Rational.numerator`. By four or five components, positional access
  is a defect waiting to happen — especially in a DP where every branch constructs a successor and a
  transposed pair of fields still runs, just wrongly.
- **It costs nothing to store and almost nothing to read.** Instances are tuples; there is no
  `__dict__` and no per-instance overhead. Field access goes through a descriptor rather than a raw
  index — measurably slower, but by roughly 15% of an already trivial operation. If a hot loop reads
  the same state repeatedly, unpack it once into locals and the question disappears.
- **`_replace` is the update.** Immutability is exactly what makes the value safe as a key, so
  "change one field" means "build a new state": `state._replace(a3=state.a3 - 1)`. The leading
  underscore marks these as *not* colliding with your field names, not as private.
- **Against the alternatives.** A [`dataclass`](/topics/technique/dataclass) is the better choice
  when the object is a bundle of behaviour rather than a value — but even `frozen=True` leaves it
  un-unpackable and unable to stand in for a tuple key. A plain `dict` as state is not hashable at
  all. An [`Enum`](/topics/technique/enum) names a *value*; a `NamedTuple` names *positions*.
  [`frozenset`](/topics/technique/frozenset) is the right key when order genuinely does not matter.
- **Structural equality cuts both ways.** Because a named state equals the bare tuple with the same
  contents, mixing the two in one dict silently merges them. That is usually the behaviour you want
  — it is what lets a `NamedTuple` be introduced into existing tuple-keyed code without touching the
  lookups — but if two different record types share a shape, they will collide too.
- **It does not survive the trip to C.** The C sibling of a `NamedTuple`-keyed DP is a `struct`, or,
  more often and more usefully, a [mixed-radix](/topics/technique/mixed-radix) integer encoding of
  the fields that indexes a flat array. When that encoding exists, it is worth considering for the
  Python too — but only after the readable version is correct, since the encoded one is where the
  transposed-field bug becomes invisible.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0068](/solutions/0068/) — Magic 5-gon Ring
- ● [0151](/solutions/0151/) — A Preference for A5

<!-- /problems -->
