<!-- tags: [finite-state-machine] -->
<!-- status: final -->
# Finite-state machine

A [finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) reads a string one
symbol at a time and remembers only which of finitely many states it is in. That model fits a
whole family of counting problems: "how many strings of length $n$ satisfy some local rule?" If
the rule can be checked by a machine that never needs more than a bounded memory, the count stops
depending on the $k^n$ strings and depends only on the number of states. The three problems below
count attendance records, digit strings covered by sums of ten, and digit strings whose substring
counts behave mod 3. All three have the same structure. The hard part is designing the machine.
Counting with it is routine.

## The idea: count paths, not strings

A deterministic automaton is a set of states $S$, a start state, a set of accepting states, and a
transition $\delta(s, c)$ for every state and symbol. Every string traces one path. Counting the
accepted strings of length $n$ is the same as counting length-$n$ paths from the start into an
accepting state, and paths compose:

$$
v_{k+1}[t] \;=\; \sum_{s}\;\#\{c : \delta(s,c)=t\}\cdot v_k[s].
$$

That forward sweep is [dynamic programming](/topics/technique/dynamic-programming) with $|S|$
cells per position. Written as a matrix, it is the
[transfer-matrix method](/topics/domain/transfer-matrix-method): $T_{st}$ counts the symbols that
take $s$ to $t$, and the answer is $e_{\text{start}}^\top T^n \mathbf{1}_{\text{accept}}$. When the
alphabet is the ten digits, the same construction is called a [digit DP](/topics/technique/digit-dp).

All the design work goes into choosing the state. It is the smallest summary of the prefix that
still decides every legal continuation, which is the
[Myhill–Nerode](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem) view of a state and the
subject of [key the memo on the full state](/topics/takeaway/memo-key-is-the-full-state). In
practice I ask two questions about every piece of history: *can a future symbol still be affected
by it?* and *if so, what is the coarsest function of it that the future reads?*

## Three machines

**191, prize strings.** Strings over {O, A, L} with no three consecutive A's and at most one L. The
future reads the length of the trailing run of A's, capped at 2 because 3 is illegal, and whether
an L has been used, capped at 1 because a second L is illegal. That gives six states and three
transitions each. A plain forward sweep is enough here because $n$ is small. The bounds that keep
the machine finite come from the rules: once a quantity reaches its illegal value, the string is
dead, so the state never has to store anything larger.

**529, 10-substrings.** Every digit must lie inside some contiguous run that sums to exactly 10.
The machine's memory is the set of suffix sums that are still at most 10, stored as an 11-bit mask,
plus the sum from the earliest uncovered digit to the end. The key step is proving that the
*earliest* uncovered digit is enough to track. Digits are non-negative, so any run that covers the
earliest uncovered digit also covers every uncovered digit after it. Breadth-first search from the
start finds a few thousand reachable states, and
[DFA minimization](/topics/technique/dfa-minimization) roughly halves that. At length $10^{18}$
even matrix powering is too slow at that size. The machine is still useful, though: by
[Cayley–Hamilton](/topics/domain/cayley-hamilton-theorem), its count sequence obeys a
[linear recurrence](/topics/technique/linear-recurrence-with-constant-coefficients) whose order is
at most the minimal state count. [Berlekamp–Massey](/topics/technique/berlekamp-massey-algorithm)
recovers that recurrence from twice that many terms of the forward DP. In this problem the
automaton's main job is to *certify the order* of the recurrence, and the counting happens
elsewhere.

**706, 3-like numbers.** The problem asks whether the number of substrings divisible by 3 is itself
$\equiv 0 \pmod 3$. The quantity named in the statement is not a state, because the count it adds
on each step depends on history. The real state is the running digit-sum residue, the number of
prefixes with each residue (mod 3), and the running answer (mod 3). Measuring residues relative to
the current one removes a coordinate by
[symmetry](/topics/takeaway/exploit-symmetry) and leaves 81 states. The digits also fall into three
classes by residue, so the alphabet shrinks to three weighted symbols. The result is an
$81 \times 81$ matrix raised to the power $d-1$ by
[matrix exponentiation](/topics/technique/matrix-exponentiation), with a separate first step that
forbids a leading zero.

## How to reason about it

- **Reach for it** when the constraint is *local* or *aggregate mod something*, such as runs,
  windows, caps, or residues, and the question is a count over all strings of a given length. If
  the constraint needs unbounded memory, like balanced brackets or "equal numbers of each digit",
  no finite machine exists, and you need a counter in the state or a different method.
- **Cap everything.** A run length, a usage count, or a sum matters only up to the point where the
  string dies or the value stops mattering. Store `min(x, cap)` or `x mod m`, never the raw value.
- **Reduce the alphabet.** Symbols that act identically on every state collapse into one weighted
  edge. In 706 that turns ten digits into three classes.
- **Build the machine, then pick the evaluator by size and length.** Small $n$ calls for a forward
  sweep in $O(n\,|S|\,|\Sigma|)$. Huge $n$ with a small $|S|$ calls for $T^n$ in
  $O(|S|^3 \log n)$. Huge $n$ with a large $|S|$ calls for the recurrence the machine guarantees,
  recovered from about $2|S|$ terms.
- **Generate states by search, don't hand-enumerate them.** In 529 a breadth-first search over
  `step(state, digit)` lists the reachable states, and that list was far smaller than the product
  of the coordinate ranges. Minimizing the machine afterwards gives a tight bound wherever the
  state count feeds into the cost.
- **Check against brute force on short lengths.** A machine that is one transition wrong still
  produces plausible numbers. All three solutions were validated against direct enumeration for
  small $n$ before being trusted at scale.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0191](/solutions/0191/) — Prize Strings
- ● [0529](/solutions/0529/) — $10$-substrings
- ● [0706](/solutions/0706/) — $3$-Like Numbers

<!-- /problems -->
