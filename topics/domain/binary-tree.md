<!-- tags: [binary-tree] -->
<!-- status: final -->
# Binary tree

A [binary tree](https://en.wikipedia.org/wiki/Binary_tree) is a rooted structure in which every
node has at most two children, conventionally *left* and *right*. In a textbook it is a data
structure you build out of pointers. In these problems it almost never is: the tree is a **model**
— the shape that appears whenever a process keeps making a two-way choice, or keeps cutting a
thing into two pieces of the same kind. Prefix codes, greedy packings and comparison strategies all
turn out to be binary trees in disguise, and once you have seen the tree, the question usually
becomes "count something about its nodes" — which you can do without ever building it.

## The idea

The recurring move is a **bijection**: some object the problem talks about is, node for node, a
binary tree, and a quantity the problem asks for is a quantity on that tree.

- **Bit strings ↔ root-to-node paths.** Read a string of bits as directions from the root, $0$ for
  left and $1$ for right. A set of strings in which none is a prefix of another — a
  [prefix code](https://en.wikipedia.org/wiki/Prefix_code) — is exactly the leaf set of a tree, since
  "no chosen string is a prefix of another" means "no chosen node lies on the path to another".
  Problem 219 ("Skew-cost Coding") asks for the cheapest such code of size $n$ when a $0$ costs
  $1$ and a $1$ costs $4$: the code is a tree with $n$ leaves, and the cost is the sum of
  leaf-depths, measured with unequal edge weights.
- **Recursive decomposition ↔ children.** If removing one piece of a region leaves *two* regions of
  the same shape as the original, the process is a binary tree whose nodes are regions. Problem 247
  ("Squares Under a Hyperbola") packs the area under $y = 1/x$ with greedy squares; each square
  leaves one region to its right and one above it, both described by a corner point alone. The
  problem's index $(\ell, b)$ — squares to the left, squares below — is then nothing more than the
  number of right steps and up steps on the root path, so the squares carrying a given index are the
  $\binom{\ell+b}{\ell}$ interleavings of those steps.
- **Questions ↔ internal nodes.** Any strategy that asks yes/no questions is a
  [decision tree](https://en.wikipedia.org/wiki/Decision_tree): each internal node is a question,
  each leaf a possible answer, and the number of questions spent on an answer is its leaf's depth.
  Problem 887 ("Bounded Binary Search") wants the shortest such strategy for finding $x \in
  \{1,\dots,N\}$ when the answer $x$ may cost at most $x + d$ questions — a minimum-height tree whose
  leaves, read left to right, are $1,\dots,N$, each under its own depth limit.

The three problems ask three different questions — minimum weighted leaf-depth, a rank among nodes,
a minimum height — but each one starts the same way: name the tree, then name the node quantity.

## How to reason about it

**Never materialise the tree.** The trees here have $10^9$ leaves, hundreds of thousands of nodes,
or are chosen from an astronomically large family. What saves you is that nodes are
interchangeable once you know the right *summary* of a node:

- In 219 every leaf of the same cost behaves identically, so the state is a histogram
  "how many leaves sit at cost $c$", not a list of leaves. The obvious algorithm — keep leaf costs in
  a [min-heap](https://en.wikipedia.org/wiki/Binary_heap) and split the cheapest $n-1$ times — becomes
  a sweep over cost levels in increasing order, splitting a whole level's worth of leaves at once.
  The counts per level grow geometrically (a linear recurrence with ratio about $1.38$), so the sweep
  is $O(\log n)$ levels, not $O(n \log n)$ heap operations.
- In 247 a node is a corner $(x, y)$, and its square's side follows from $(x+s)(y+s) = 1$. Nothing
  else about the history matters, so a subtree is a pure function of one point.
- In 887 a subtree is summarised by two integers: its remaining height and its *slack* — how much
  deeper than its position its leaves are allowed to sit. That is what makes the problem's
  constraint self-similar, so a memoised recurrence over (height, slack) replaces a search over
  trees.

**Look for monotonicity down the branches — it buys greed and pruning.** Each of these trees has
a quantity that only gets worse as you descend, and that is what turns an optimisation into a
greedy rule or a cut-off:

- In 219, splitting a leaf of cost $c$ adds $c + 5$ to the total; a cheaper leaf always adds less,
  so splitting the cheapest leaf first is optimal — the
  [Huffman](https://en.wikipedia.org/wiki/Huffman_coding) intuition, run as a growing process
  instead of a merging one.
- In 247 squares shrink down every branch, so "how many squares are at least as large as this one"
  is a depth-first walk that abandons a subtree the moment its root falls below the threshold —
  $O(\text{answer})$ work, with no sort of the squares at all.
- In 887 capacity never decreases with slack, and leaves pushed to the left give the right subtree
  more slack, so the best tree fills its left side completely before spending anything on the right.

**Turn the question around when you are minimising height.** "What is the shortest tree for $N$?"
is an optimisation per $N$; "how many leaves can a tree of height $h$ serve?" is one number per $h$.
When the property is downward-closed (deleting a leaf keeps a valid tree), the first answer is just
the least $h$ whose capacity reaches $N$, and a sum of minimum heights over all $N$ collapses by the
tail-sum identity $\sum_N Q(N) = \sum_h \#\{N : Q(N) > h\}$ into a handful of terms. This is the
same inversion that turns the
[egg-drop puzzle](https://en.wikipedia.org/wiki/Dynamic_programming#Egg_dropping_puzzle) from a
search into a capacity table.

**Mind the shape of the walk.** A tree that is deep along one spine — 247's bottom row is a chain
of right steps hundreds of thousands long — will overflow a recursive DFS. Use an explicit stack,
and choose the push order so the short branches are finished first; then the stack stays as small
as the *number* of short detours, not the length of the spine. The generic skeleton is three lines:

```python
stack = [root]
while stack:
    node = stack.pop()
    if key(node) < threshold: continue            # monotone: whole subtree is out
    count += 1; stack += [right(node), up(node)]  # long branch first, short branch on top
```

And when node values are floats computed down a long chain, check the formula, not just the
algorithm: in 247 the textbook quadratic root subtracts two nearly equal numbers, and the
rearranged form $s = 2(1-xy) / \bigl((x+y) + \sqrt{(x-y)^2+4}\bigr)$ is what lets plain `double`
rank millions of nearly equal squares correctly.

The through-line is that the binary tree is the *language* of these problems, not a container you
have to build: once you have identified what a node is, what its two children are and which
quantity is monotone along a branch, the tree hands you a greedy rule, a pruning bound or a
capacity recurrence — and the tree itself never needs to exist in memory.

<!-- problems (generated by update-tags) -->
## Problems

- ● [0219](/solutions/0219/) — Skew-cost Coding
- ● [0247](/solutions/0247/) — Squares Under a Hyperbola
- ○ [0400](/solutions/0400/) — Fibonacci Tree Game
- ○ [0406](/solutions/0406/) — Guessing Game
- ○ [0505](/solutions/0505/) — Bidirectional Recurrence
- ○ [0674](/solutions/0674/) — Solving $\mathcal{I}$-equations
- ○ [0829](/solutions/0829/) — Integral Fusion
- ● [0887](/solutions/0887/) — Bounded Binary Search
- ○ [1007](/solutions/1007/) — Alternating Difference

<!-- /problems -->
