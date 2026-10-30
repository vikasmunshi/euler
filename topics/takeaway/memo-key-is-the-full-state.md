<!-- tags: [memo-key-is-the-full-state] -->
<!-- status: final 2026-10-30T12:35Z -->
# Key the memo on the full state

A memo table makes a promise: the same key always gets the same answer. That promise holds only
when the key holds **everything the rest of the computation depends on**, including what the
function reads from its caller's context and not only from its arguments. It should also hold
nothing more, because every extra coordinate multiplies the number of distinct keys and wipes out
the reuse that made caching worthwhile. A key that is too small gives wrong answers, and it does
so silently. A key that is too large gives right answers slowly. The problems below are hard
mainly because the right key isn't the obvious one. Each needs one extra piece of hidden context,
and each needs that context reduced to the smallest summary that still determines the future.

## The idea

The precise notion is the
[Markov property](https://en.wikipedia.org/wiki/Markov_property): a *state* is a summary of the
past such that the future depends on the past only through the summary. Automata theory phrases
the same thing as the
[Myhill–Nerode equivalence](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem): two
histories belong in the same state exactly when no continuation can tell them apart. A memo key is
a state in this sense. That gives two tests, one for each way a key can fail:

- **Sufficiency:** could two calls with the same key ever need different answers? If so, some
  input is missing. It is usually not an argument. It is a closure variable, a global, or a fact
  about *where* in a larger structure the call happens.
- **Minimality:** do two different keys always lead to different futures? If not, the key carries
  detail the future ignores. Replace that coordinate with the function of it the computation
  actually reads, such as a digit sum instead of a number, a residue instead of a count, or a
  parity instead of a position.

The bug that sufficiency guards against looks harmless in code:

```python
@cache
def run(low):          # wrong: the step also adds digit_sum(high), read from outside
    ...
```

Within one call the cache returns correct values. Then a different `high` reuses an entry that was
computed under the old one. Nothing crashes, and the answer is simply wrong.

## Three hidden coordinates

**Problem 551** walks $a_n = a_{n-1} + s(a_{n-1})$ for $10^{15}$ steps by jumping over whole digit
blocks. Write the value as $H \cdot 10^k + L$. While $L$ is filling up toward $10^k$, the high part
$H$ never changes. A jump looks like a function of $(k, L)$, but every step also adds $s(H)$. So
$H$ is a hidden input, and including it in full would make every key unique. The minimal summary is
its digit sum $c$, which gives the key $(k, c, L)$. Because $c$ is bounded by nine times the number
of digits in $H$, the keys repeat constantly. A computation of $10^{15}$ steps touches only tens of
thousands of states.

**Problem 706** asks whether the number of substrings divisible by 3 is itself divisible by 3. The
quantity the problem names, the substring count, is not a state: appending a digit changes it by an
amount that depends on the past. The future depends on the running digit-sum residue, the number of
prefixes in each residue class, and $f$, all taken mod 3. That gives $3^5$ states. Measuring the
prefix counts *relative to the current residue* removes the residue coordinate and leaves 81. This
is minimality applied through [symmetry](/topics/takeaway/exploit-symmetry). Here the "memo" is a
[finite-state machine](/topics/technique/finite-state-machine), counted with a transfer matrix. The
work of finding the state is the same as for a cache. Only the evaluation differs.

**Problem 943** sums a prefix of a Kolakoski-like self-describing sequence by memoising subtrees
of its derivation tree. The natural key is (value, height), and it is insufficient. Which symbol
each level of the subtree uses depends on the parity of that level's position in the whole
sequence, and that parity is set by everything to the left. The sufficient summary is an
$(h+1)$-bit mask with the position parity of the subtree's leftmost descendant on each level. The
memoised result has to return the subtree's own parity mask as well, because the next sibling's
key is computed from it.

## How to reason about it

- **List every input the function reads, not only its parameters.** Enclosing-scope variables,
  the position in the outer loop, and the depth in a tree are all inputs. When a hidden input
  belongs to a whole run, like the pair $(a, b)$ in 943, the alternative to keying on it is a fresh
  memo per run. 943 does that, building its tables from scratch for each pair.
- **Project each input onto what the function uses from it.** Ask what the next step reads, as in
  [splitting inputs into behaviour classes](/topics/takeaway/split-inputs-into-behaviour-classes).
  The answer is usually a much smaller value: $s(H)$ rather than $H$, counts mod 3 rather than
  counts, and parities rather than positions.
- **Count the keys before writing the cache.** Multiply the coordinate ranges and compare the
  result with the number of calls. That ratio is the speed-up, as described under
  [memoization](/topics/technique/memoization). In 943 the bound ($2^{h+1}$ masks against
  $N/\bar{x}^h$ nodes per level) predicts both that the method works and which pairs dominate the
  running time.
- **Return what the next key needs.** When states chain from one call to the next, the cached
  value must include the part of the result that becomes the next key: the carry-out low part in
  551, and the parity mask in 943.
- **Don't cache a result that depended on an input outside the key.** 551's jump also takes a step
  limit. A jump that ended by overflowing its block doesn't depend on the limit, so it is cached. A
  jump cut short by the limit does depend on it, so it is never stored. Leaving such a result out of
  the cache is a valid alternative to widening the key, provided those calls are rare. Here they
  are only the $O(k)$ calls along the final path.

When a memoised solution is fast but disagrees with brute force on small inputs, check the key
before anything else. A missing coordinate is the most common cause, and the hardest to see,
because each individual cached value is correct under the context it was computed in.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0551](/solutions/0551/) — Sum of Digits Sequence
- ● [0706](/solutions/0706/) — $3$-Like Numbers
- ● [0943](/solutions/0943/) — Self Describing Sequences

<!-- /problems -->
