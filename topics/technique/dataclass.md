<!-- tags: [dataclass] -->
<!-- status: final -->
# Dataclass

A [dataclass](https://docs.python.org/3/library/dataclasses.html) is a Python class whose
boilerplate is generated from its annotated fields. You write `rank: PokerRank` and
`tie_breakers: tuple[int, ...]`, and `@dataclass` writes `__init__`, `__repr__` and `__eq__` for
you. If you ask, it also writes ordering, hashing, immutability and `__slots__`. It is the
lightest way to give a group of values *names* and *behaviour* together, which is why two
solutions with fairly involved records use it: the poker hands of problem 54 and the anagram
classes of problem 98. Both also show the other side. Some of what they declare is ceremony, and
in one place a plain tuple would have done the same job. This page is part of the
language-idioms series. It covers the idiom, why these solutions use it, and how it looks in the
other language.

## The idea

The decorator reads the class's annotations in order and builds the methods from that field list.
Its keyword arguments choose which methods to build:

| Argument | Generates | Default |
|---|---|---|
| `init`, `repr`, `eq` | constructor, readable `repr`, field-by-field `==` | on |
| `order=True` | `<`, `<=`, `>`, `>=`, comparing the fields *as a tuple* | off |
| `frozen=True` | assignment to a field raises `FrozenInstanceError` | off |
| `slots=True` | a `__slots__` class: no per-instance `__dict__`, smaller and faster | off |
| `kw_only=True` | the constructor accepts only keywords: `Anagram(canonical=key)` | off |

Two field-level tools complete the kit.
[`field(default_factory=set)`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)
gives every instance its own fresh mutable default. A bare `= set()` is rejected, because it would
be shared by all instances. `field(init=False)` declares a field that the constructor doesn't take
and that
[`__post_init__`](https://docs.python.org/3/library/dataclasses.html#post-init-processing) fills
in.

The point to hold on to is that `order=True` and the generated `__eq__` *are* tuple comparison.
The dataclass compares `(self.f1, self.f2, …)` against the other instance's tuple. So a dataclass
that only holds data and only gets compared is a named tuple in effect, with more machinery.

**Poker hands (54).** Two dataclasses split the work. `PokerHand` is the *input* record: it takes
five card strings, and its `__post_init__` validates them and derives two `init=False` fields,
`values` (ranks 0–12) and `suits`. The hand's classification is a
[`functools.cached_property`](https://docs.python.org/3/library/functools.html#functools.cached_property),
so each hand is evaluated once however often it is compared. `HandRank` is the *result* record:
the category plus its tie-breakers, most significant first.

```python
@dataclasses.dataclass
class HandRank:
    rank: PokerRank
    tie_breakers: int | tuple[int, ...]

    def __gt__(self, other):
        if self.rank != other.rank:
            return self.rank > other.rank
        ...  # then compare tie_breakers
```

This is the record from the [tuple](/topics/technique/tuple) page, ranking field first and payload after, and
the hand-written `__gt__` rebuilds what the language already provides. `@dataclass(order=True)`
generates exactly "rank first, then tie-breakers". The mixed `int | tuple` type doesn't break it,
because each category always uses the same shape, so two hands that tie on `rank` always have
comparable tie-breakers. The plain tuple `(rank, tie_breakers)` would also work with no class at
all. What the dataclass adds here is the field names, which help when you read a hand in a
debugger. It also adds a small trap: you write `__gt__` by hand, and `<` then only works because
Python falls back to the reflected `__gt__`.

`PokerHand` has a better reason to be a class. Its validation in `__post_init__`, the derived
fields and the cached classification are behaviour, not just data. Note that `cached_property`
stores its value in the instance `__dict__`, so this class *can't* take `slots=True`. The two
features are mutually exclusive, and Python raises `TypeError` at first access if you combine
them.

**Anagramic squares (98).** `Anagram` holds one anagram class (its sorted-letter key and the
words that share it), and `Anagrams` indexes those classes by length and then by key. Both use
the full set of switches: `frozen=True, slots=True, kw_only=True, order=True`. Two of them
deserve a closer look, because they don't do what they appear to:

- **`frozen` is shallow.** `Anagram` is frozen, yet `add_word` calls
  `anagram.dictionary_words.add(word)` on it. That works because freezing stops you *rebinding*
  a field, not *mutating* the object the field refers to. The solution depends on this: it grows
  each class's word set in place. What `frozen=True` actually gives here is protection against
  accidentally rebinding `canonical`.
- **`frozen` + `eq` generates a `__hash__` that can't run.** A frozen, comparable dataclass
  receives a `__hash__` built from its fields, and hashing a `set` field raises
  `TypeError: unhashable type`. Nothing in 98 hashes an `Anagram`, so this never fires. But the
  class claims to be a valid `dict` key and isn't one. In the same way, `order=True` compares the
  word *sets*, and `<` between sets means "proper subset", which is a partial order. The method
  exists and is never used.

The useful part of 98's dataclasses is `field(default_factory=…)`. Every `Anagram` gets its own
set, and `Anagrams` gets its own `defaultdict(dict)`, with no `__init__` written by hand. Methods
that live next to the data (`add_word`, `prune`, the `anagram_length` property) make the solve
loop read as a sequence of steps. When an argument doesn't change any behaviour the code relies
on, the honest choice is to leave it out.

## The counterpart in C

A C `struct` is the dataclass without the generated methods. You get named fields with a fixed
layout. You don't get a constructor, a `repr`, equality or ordering, and each C solution writes
the part it needs.

- **Ordering → a comparator by hand (54).** C's `HandRank` is
  `{ PokerRank rank; int tie_breakers[5]; int tb_count; }`. That is the `int | tuple` union
  flattened into a fixed array plus a length. `hand_rank_gt` is the lexicographic loop that
  `order=True` would have generated: compare `rank`, then the tie-breakers pairwise up to the
  shorter count. C has no `==` for structs, and `memcmp` isn't a substitute either, because it
  compares padding bytes and the unused tail of `tie_breakers`. So any record compared by value
  needs a function like this.
- **Constructor → zero, then fill (54).** `evaluate_hand` starts from `memset(&hr, 0, sizeof hr)`
  and assigns fields one at a time. That is C's equivalent of `__init__` plus defaults. A C99
  compound literal with designated initializers, `(HandRank){ .rank = FLUSH, .tb_count = 5 }`,
  is the closer analogue of `kw_only=True`: fields are named at the call site, and any field you
  leave out is zero.
- **Container fields → fixed arrays (98).** `Bucket` is
  `{ char canonical[32]; char words[32][32]; int word_count; int word_len; }`. The
  `default_factory=set` becomes a capacity-bounded inline array with a count, and the
  `dict[int, dict[str, Anagram]]` index becomes a flat array of buckets searched linearly by
  `(word_len, canonical)`. Membership uses `strcmp` in a loop. That is the price of not having a
  hashable record, and it is fine for about two thousand words.
- **`frozen` → `const`, and just as shallow.** A `const` struct with a pointer member still lets
  you write through the pointer, exactly as a frozen dataclass lets you mutate its set. Both
  languages protect the binding, not what it points to.

Going the other way, the risk is reaching for a class where a tuple fits. If the only things you
do with a record are build it, compare it and maybe use it as a key, then a tuple (or a
[`NamedTuple`](/topics/technique/namedtuple), if names help)
does the job with no declaration at all.

## How to reason about it

- **Use a plain tuple for a comparison key.** If a record exists to be ranked, sorted or used as
  a `dict` key, a tuple with the ranking field first is the whole solution. If you still want
  names, use `@dataclass(order=True)`, but never write `__gt__` by hand to reproduce what
  `order=True` generates.
- **Use a dataclass when the record has behaviour.** Validation in `__post_init__`, derived
  `init=False` fields, cached or computed properties, and methods that keep invariants (54's
  `PokerHand`, 98's `Anagrams`) are what a tuple can't provide.
- **Turn on only the switches you depend on.** Each one is a claim about the class. `frozen`
  claims immutability but is shallow. `frozen` together with `eq` claims hashability, which
  fails if any field is unhashable. `order` claims a meaningful ordering, which a set field
  doesn't have. A claim that isn't true misleads the next reader.
- **`slots` and `cached_property` exclude each other.** Choose memory and attribute speed
  (`slots=True`, which matters with millions of instances) or lazy caching per instance
  (`cached_property`). For the few thousand records here, either is fine.
- **Mutable defaults always go through `default_factory`.** The decorator rejects `= []` and
  `= set()` at class-definition time for exactly that reason.
- **In C, write the comparator once and next to the struct.** It is the method `order=True`
  would have generated. Compare field by field, never with `memcmp` on the whole struct.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0054](/solutions/0054/) — Poker Hands
- ● [0098](/solutions/0098/) — Anagramic Squares

<!-- /problems -->
