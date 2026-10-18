<!-- tags: [hash-function] -->
<!-- status: final -->
# Hash function

A [hash function](https://en.wikipedia.org/wiki/Hash_function) maps a key of any shape to a
fixed-width number, under one rule: equal keys give equal hashes. Unequal keys only *usually* give
unequal hashes. The [hash table](/topics/technique/hash-table) page covers what happens once you
have that number: buckets, collision policy, load factor, deletion. This page is about the function
itself. The five problems below use it in three ways: to place a key in a table, to rule a pair of
candidates out cheaply, and to give a whole path a single number. In Python you almost never see
the function, because `hash()` is built into every immutable type. In C you write it yourself, and
the C files here contain four different ones, each picked to suit its keys.

## The idea

A hash has two jobs, and the uses below lean on different ones.

**Agreement.** If $a = b$ then $h(a) = h(b)$. Turned around: if $h(a) \ne h(b)$, then $a \ne b$, and
you know it without comparing $a$ and $b$. Every hash relies on this, and it is the only property a
*filter* needs.

**Spread.** Distinct keys should land on distinct values as often as chance allows, and that has to
hold in the bits you actually keep. A table of $2^{k}$ slots keeps only the low $k$ bits
(`h & mask`). A function can be perfectly injective and still useless as a bucket index if all its
variation sits in the bits the mask throws away.

Agreement is free: any deterministic function has it. Spread is where the work goes, and how much
work depends on how patterned the keys are.

## Four C hashes, one per kind of key

**The identity hash, when the keys already spread.** Problem 37's incremental sieve (a C port of the
Python dict shown below) indexes its open-addressed composites table with no mixing at all:

```c
unsigned int h = (unsigned int)key & HASH_MASK;
```

This looks like a mistake, but it isn't. The live keys are of two kinds. Each active sieving prime
has its next pending multiple, and those sit in a short contiguous run just above the current $n$,
where low bits are as distinct as the numbers themselves. Each other prime has its square waiting
further ahead, and those scatter. Only primes whose square stays below $2^{30}$ are ever inserted,
so a few thousand odd, distinct keys share $2^{20}$ slots. At that load even an unmixed index almost
never probes past its first slot. Python makes the same choice: `hash(n) == n` for small ints.
CPython's dict copes with identity hashes in general by mixing the higher bits into its probe
sequence (the "perturbation" in `dictobject.c`). The C port gets away without that because its keys
are sparse and close to random in their low bits.

**A string hash: djb2.** The same file's prime-string set hashes the decimal text with
[djb2](http://www.cse.yorku.ca/~oz/hash.html), in Bernstein's later XOR form:

```c
unsigned int h = 5381;
while (*s) h = ((h << 5) + h) ^ (unsigned char)*s++;
```

`(h << 5) + h` is `h * 33`, so each character shifts the earlier ones up by roughly five bits before
the next one is folded in. The hash-table page shows the `+` form used by problems 29 and 62. The two
behave much the same; the XOR form is generally reported to spread slightly better on short ASCII
keys. Either is plenty for a few hundred thousand short strings. On the Python side, `str` hashes
with SipHash, seeded at random per process (`PYTHONHASHSEED`), so the same `set[str]` iterates in a
different order from one run to the next. Nothing in these solutions depends on that order, and
nothing should.

**Packed fields: a finaliser is mandatory.** Problem 208's robot-walk DP keys its states on
(heading, four arc-count deltas). Python keys a `defaultdict` on the nested tuple directly. The C
port packs the state into one 64-bit word: the heading at bit 32 and each delta, offset by 128, in
its own byte. Then it runs the
[SplitMix64](https://en.wikipedia.org/wiki/MurmurHash) finaliser over that word before masking:

```c
x += 0x9E3779B97F4A7C15ULL;
x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9ULL;
x = (x ^ (x >> 27)) * 0x94D049BB133111EBULL;
return x ^ (x >> 31);
```

Without it, `key & TMASK` on a $2^{22}$ table would keep the lowest two delta bytes and six bits of
a third. The heading and the top delta would never reach the index, so every state that differed
only in those fields would share a bucket. Packing is an injective encoding, but it does no mixing.
Each xor-shift pulls high bits down into the low ones, and each odd multiply pushes every bit
upward. Two rounds of that leave every output bit depending on every input bit, which is exactly the
spread the mask needs.

Problem 155 hashes a reduced fraction $(p, q)$ the same way. It multiplies each half by a different
64-bit odd constant (one of them $2^{64}/\varphi$, the Fibonacci-hashing multiplier), XORs the
products, and runs a short xor-shift/multiply tail. Using two multipliers matters. With
`hash(p) ^ hash(q)` the hash would be symmetric, so $(p, q)$ and $(q, p)$ would always collide. That
matters here: swapping series and parallel throughout a unit-capacitor circuit turns $C$ into $1/C$,
so every $p/q$ in the set arrives together with $q/p$. With `p + q`, every point on an
anti-diagonal would collide. Python's tuple hash (an xxHash-style combine since 3.8) is
order-sensitive for the same reason, which is why `set[tuple[int, int]]` needs no thought on that
side.

## A hash as a filter, not an index

Problem 98's "shape hash" never goes into a table. For a word and a candidate square it computes the
multiset of symbol-repeat counts, sorted descending and written out as a string. "CARE" gives
`1111`; "DOOR" and the square 4225 both give `211`. A letter-to-digit bijection keeps every repeat count, so if
the shapes differ, no bijection exists, and the pair is dropped before the solver builds any
mapping. That is agreement used on its own. Equal shapes prove nothing, because many words share
`1111`, so the full consistency check still runs on the pairs that survive. It costs one string
comparison per pair and removes most of them. This hash is also *structural*: it is designed to
collide on purpose, exactly on the keys that might match. That makes it a
[canonical form](/topics/technique/canonical-form) used as a necessary condition. The anagram key in
the same file (letters sorted) is the stronger version, a canonical form that is equal *exactly*
when the words are related.

## A hash of a sequence: the rolling checksum

Problem 244 defines its own hash in the statement. A move sequence $m_1 \dots m_n$ is reduced by
$c \leftarrow (243\,c + m_i) \bmod 100\,000\,007$, which makes it a
[polynomial rolling hash](https://en.wikipedia.org/wiki/Rolling_hash) in base 243. The property the
solutions use is that it extends one step at a time: the checksum of a path plus one move depends
only on the path's checksum and that move. So the depth-first walk over shortest paths carries the
running checksum as a third field on its stack entry, `(state, left, checksum)` in Python and a
parallel `stack_sum[]` array in C, and never stores a path. The C and Python sides are the same
code; only the stack layout differs.

The same problem also shows the case where no hash function is needed. A board state packs
*injectively into a dense range*, as (blank cell, colour bitmask), so the BFS distance table is a
plain `bytearray` / byte array indexed by that integer. A packing that is both injective and dense
is a [perfect hash](https://en.wikipedia.org/wiki/Perfect_hash_function): no collisions, no keys
stored, no probing. Whenever the state can be packed this way, the table becomes an array.

## How to reason about it

- **Look at where the key's variation lives, then decide how much mixing it needs.** Keys that are
  consecutive or close together, like problem 37's composites, already spread in their low bits, and
  identity is the fastest correct hash. Keys built from packed fields, like problem 208's, keep
  their variation in bit ranges the mask may drop, and need a finaliser. Text is in between: a
  cheap multiplicative string hash like djb2 is enough.
- **Keep the components ordered.** Combine fields with different multipliers or by sequential
  folding (`h = h * K + x`), never with a symmetric operation. `^` and `+` collide on
  swaps and on sums, and mathematical inputs tend to produce exactly those swaps and sums.
- **Pack before you hash, and check whether packing alone is enough.** Packing turns a tuple into a
  word that a fast 64-bit mixer can take. If that word also lands in a dense range, as in problem
  244, skip the table altogether.
- **A hash can screen pairs without being a table index.** If an invariant must be equal for two
  objects to match, compare the cheap invariant first and only check the survivors in full.
  [Canonical forms](/topics/technique/canonical-form) are the case where the invariant is also
  sufficient.
- **None of these are cryptographic.** djb2, SplitMix64 and Fibonacci hashing are fast and spread
  well, but they are trivially invertible or easy to collide on purpose. That is fine for solver
  inputs. Python's SipHash is seeded at random precisely so that a hostile input cannot force every
  `dict` key into one bucket. For integrity or tamper-resistance, use
  [`hashlib`](https://docs.python.org/3/library/hashlib.html), not any of the functions above.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0037](/solutions/0037/) — Truncatable Primes
- ● [0098](/solutions/0098/) — Anagramic Squares
- ● [0155](/solutions/0155/) — Counting Capacitor Circuits
- ● [0208](/solutions/0208/) — Robot Walks
- ● [0244](/solutions/0244/) — Sliders

<!-- /problems -->
