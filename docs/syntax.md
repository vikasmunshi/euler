# Solver shell — language & syntax reference

This is the authoritative reference for the solver shell command language. It
defines what the user types (the **surface syntax**), how that is normalised (the
**canonical form**), and how the canonical form executes (**semantics**), driving
the `lexer → parser → interpreter` pipeline that runs every command block.

---

## 1. Overview

The shell reads one **command block** at a time and executes it, producing a
single integer exit code (`rcode`). A command block is a tree of **statements**
composed with the sequencing operators `;` `&&` `||`, optionally grouped with
`{ }`, and optionally wrapped in a `loop` header that runs the whole block once
per value of a list.

Every statement has the same shape once normalised:

```
<guard>: <target> = <evaluation>;
```

* **guard** — `True`, or a boolean expression that decides whether the statement
  runs. The `&&` / `||` operators lower to guards over `rcode`.
* **target** — `_` (discard) or a variable name to which the evaluation's value
  is assigned.
* **evaluation** — a command invocation or a value expression; it yields a value
  and sets `rcode`.

The whole language is sugar over a list of these guarded statements.

---

## 2. Lexical elements

* **sequence separator** — `;` or newline
* **and-operator** — `&&`
* **or-operator** — `||`
* **group** — `{` … `}`
* **loop header** — `loop` … `:`
* **assignment** — `=`
* **discard target** — `_`
* **variable reference** — `{name}` (also `{name.attr}` and `{name:spec}`;
  `{{` / `}}` for a literal brace)
* **word / command** — bare token, `shlex`-quoted (`'…'`, `"…"`)
* **comment** — `#` to end of line (outside quotes)

* A **newline** inside an unclosed `{ }` continues the block (the reader counts
  brace depth); otherwise a newline ends the block. A newline is otherwise
  equivalent to `;`.
* **Whitespace** is insignificant except inside quotes and as a token separator.
* **Quoting** follows `shlex`: single quotes are literal, double quotes group,
  backslash escapes. Tokenisation of a command's arguments uses `shlex.split`.

### Variable references

A `{name}` (or `{name.attr}`, `{name:spec}`) reference is expanded by the
**interpreter** as it evaluates a statement. It reads the value from the
store and, when the name is a *callable*, **invokes** it first
(without any arguments), so the substituted value is recomputed on every
reference; an attribute path is then resolved on that value with
`getattr`, segment by segment (`{problem.difficulty}` → the `difficulty` field
of the workspace `Problem`). How the resulting value is rendered depends on
context:

* **command argument** — rendered with `shlex.quote(str(value))` (or
  `format(value, spec)` when a spec is given), i.e. as one shell-safe token, so a
  value containing spaces stays a single argument.
* **expression** — handed to the safe evaluator (§4): a literal-safe value
  (number, string, list of those, …) is inlined as its `repr` so it parses as a
  literal, while any other object (e.g. `{problem}`, a `Problem`) is bound by
  reference and resolved during evaluation rather than stringified.

Also:

* A non-group `{…}` is **always a variable reference** — never a set/dict
  literal — so it must be a complete `{name}` / `{name.attr}` / `{name:spec}`
  with a §3-valid name (`[a-z][a-z0-9_]*`). Anything else (`{0problem}`,
  `{problem[0:1]}`, `{1,2,3}`) is a **lex-time syntax error**. To index or slice
  a list, the brackets go *outside* the braces — `{problems}[10:12]`,
  `{solved}[0]`, not `{problems[0]}` (see §4).
* `{name.attr}` is **attribute access** on the variable's value; the path may
  chain (`{name.attr.attr}`). Each segment follows the same `[a-z][a-z0-9_]*`
  convention as a name — so private/dunder attributes are not reachable — and
  anything else (`{problem.0}`, `{problem._fields}`) is a lex-time syntax
  error. A missing attribute raises at substitution time and aborts the
  statement (reported, not fatal), like an undefined `{name}`.
* `{name:spec}` applies Python's format mini-language: `echo {problem.number:04d}`.
  A spec may follow an attribute path — `{problem.title:>30}` — and formats the
  final value.
* A literal brace must be doubled: `{{` → `{`, `}}` → `}`.
* Substitution is **not** quote-aware: a `{name}` inside quotes is still expanded.
* An undefined `{name}` raises and aborts the statement (reported, not fatal).

---

## 3. Names and variables

Variable storage, the reserved names, and the two write channels are defined by
`variables.py`; this section only states the syntactic rules.

* **User variable name:** `[a-z][a-z0-9_]*` (lowercase, leading letter, no dash —
  so a name never collides with a command name like `claude-api` or with
  subtraction `a-b`). It may not be a reserved name or a registered command name.
* **Special (reserved) variables** — seeded by `variables.py`:

  | name       | type              | meaning                                              | writable by user |
  |------------|-------------------|------------------------------------------------------|------------------|
  | `loop`     | Any               | current loop value (set only by `loop`; `None` outside a loop) | no    |
  | `problem`  | Problem \| None   | the workspace problem, as an object                  | no (shell-set)   |
  | `rcode`    | int               | exit code of the most recently run evaluation        | no (shell-set)   |
  | `reserved` | list[str]         | sorted list of every reserved name                   | no               |
  | `problems` | list[Problem]     | every known problem                                  | no               |
  | `next`     | int               | number of the next unsolved problem                  | no (computed)    |
  | `random`   | int               | number of a random unsolved problem                  | no (computed)    |
  | `solved`   | list[Problem]     | the solved problems                                  | no (computed)    |
  | `unsolved` | list[Problem]     | the unsolved problems                                | no (computed)    |
  | `stale`    | list[Problem]     | the stale problems                                   | no (computed)    |

  The *computed* specials are dynamic — re-evaluated on **each** `{…}` reference
  (so `{random}` yields a fresh pick and `{next}` / `{solved}` reflect current
  progress), whereas the others hold a fixed (shell-updated) value.

  `next` / `random` are bare problem **numbers** (handy as command arguments:
  `init {next}`), while `problems` / `solved` / `unsolved` / `stale` hold
  `Problem` objects — use an attribute path to reach a field, e.g.
  `{problem.number}`, `{loop.title}`.

* **assign vs set** (see `variables.py`): a user `name = expr` statement assigns
  through the *assign* channel, which rejects every reserved name. The shell
  updates the settable specials (`problem`, `rcode`, and `loop` via the `loop`
  construct) through the separate *set* channel.

---

## 4. Statements

A statement is one of:

1. **Command** — a registered command name followed by arguments:
   `init {next}`, `eval`, `stack && reset`. Returns the command's `int` exit code.
2. **Assignment** — `name = evaluation`: evaluates the right-hand side and stores
   its **value** under `name`. The right-hand side may be either kind of
   evaluation — an expression (`x = {problem.number} + 1`) or a command, in which
   case the stored value is the command's integer exit code (`x = init 42`).
3. **Bare expression** — a value expression with no command and no `=`:
   `{problem.number} > 100`, `[1, 2, 3]`. Its value sets `rcode` by truthiness
   (see §6).

### Evaluations: command vs expression

Within an evaluation the interpreter dispatches on the first token (after `{}`
substitution): if it names a registered command, the evaluation is a **command**
invocation; otherwise it is a **value expression** evaluated by the safe
evaluator. A safe expression supports only literals, names already substituted to
literals, comparisons, boolean/unary/binary operators, list and tuple literals
(`{…}` is a variable reference, not a set/dict literal — §2), indexing/slicing
(`{problems}[6:10:2]`, `{solved}[0]`), and calls to a fixed set of pure builtins
(`len`, `min`, `max`, `sum`, `sorted`, `abs`, `round`, `any`, `all`, `range`,
`int`/`str`/`bool`/`list`/`tuple`/`set`/`dict`/`frozenset`, …) where the callee is
a bare name — no attribute access, lambdas, calls to substituted values, or
surviving names. (Attribute access exists only *inside* a `{…}` reference —
`{problem.title}` — resolved at substitution time, §2; `{problem}.title` in an
expression is still an error.)

---

## 5. Composition and precedence

Binding from tightest to loosest:

1. `{ }` grouping
2. `&&` (and)
3. `||` (or)
4. `;` / newline (sequence)

So `a && b || c ; d` parses as `(((a && b) || c) ; d)`. Use `{ }` to override:
`a && { b ; c }` guards the whole `{ b ; c }` group on `a` succeeding.

### Lowering operators to guards

`&&` and `||` are sugar; the lexer/parser lower them to guarded statements. The
guard of each operand after the first is built from the **preceding** operand's
`rcode`:

```
a ;  b   →   True: a        then   True: b
a && b   →   True: a        then   {rcode} == 0: b
a || b   →   True: a        then   {rcode} != 0: b
```

The exit code is referenced as the variable `{rcode}` (not a bare `rcode`), so
the parser resolves it through the same `{}` substitution as any other variable.

A statement whose guard is false is **skipped** and **does not change `rcode`**,
so a skipped operand's predecessor code flows on to the next guard (e.g.
`false && a || b` runs `b`).

---

## 6. Exit code (`rcode`) semantics

Every executed evaluation sets `rcode`:

* **Command:** `rcode` = the command's returned `int`.
* **Expression:** `rcode` = `0` if the value is truthy, else `1`. (The value
  itself is what an assignment stores; `rcode` is only the truthiness.)
* **Skipped statement** (guard false): `rcode` unchanged.
* **Block / group:** `rcode` is that of its last executed statement.

`solver "<block>"` exits the process with the block's final `rcode`, so blocks
can gate shell-level pipelines: `solver "init 42 && eval && stack"`.

---

## 7. Loops

A command block may be prefixed with a loop header:

```
loop <list>: <block>
```

* `<list>` is an expression (subject to `{}` substitution) that evaluates to an
  iterable of values — a variable holding a list, e.g. `loop {problems}:`, a
  literal, e.g. `loop [1, 2, 3]:`, or a slice of either, e.g.
  `loop {problems}[6:10:2]:`. The elements may be any objects (ints, `Problem`s,
  …). Only a plain sequence (`list`, `tuple`, `set`, `range`) spreads into
  per-iteration values; any other value — an int, a str, a single `Problem`
  (`loop {problems}[503]:`) — is looped over **once**, as itself.
* The block runs once per element, with the special `loop` bound to the current
  element for the duration of that iteration (`{loop}` in the body resolves to
  it; an element's fields are reached with an attribute path, e.g.
  `{loop.number}`). The variable shares its spelling with the keyword: bare
  `loop …:` at the start of a block is the header, `{loop}` is the value.
* With no header (or an empty list) the block runs **once** with `loop` =
  `None`.
* The header `:` may be **omitted** when the body boundary is unambiguous —
  the body is a `{ … }` group (`loop {problems} { init {loop.number} }`) or
  starts on a new line — the lexer inserts the missing `:` (auto-fix). An
  inline body on the same line still requires the `:` (`loop [1, 2] echo hi`
  is an error: without it the list expression cannot be told apart from the
  body).
* After the loop, `loop` is reset to `None` and `rcode` is that of the last
  executed statement.
* **Loops do not nest.** A `loop` header may only prefix a top-level block;
  there is a single loop variable `loop`, so a `loop` appearing inside another
  block is a syntax error. (The grammar enforces this — a `loop-header` is
  reachable only from `block`, never from within a `group` or `statement`.)

### Flow-control words

These keywords (classified as `Flow`, not commands) raise control-flow signals
handled by the run loop:

* `break` — stop the loop; resume after it.
* `continue` — skip to the next loop element.
* `exit` — end the shell session (or the `solver "<block>"` invocation).

### On-error shortcuts

A trailing `|| continue` or `|| break` is **not** lowered to an ordinary
guarded statement; it folds into the preceding statement's *on-error* action:

* `cmd || continue` — if `cmd` fails (`rcode != 0`), continue the loop.
* `cmd || break` — if `cmd` fails, break out of the loop.

The default on-error action is *ignore*. The shortcut applies to the whole
left-hand operand, so `cmd1 && cmd2 || break` breaks when the `cmd1 && cmd2`
group fails. `exit` is not an on-error action — `cmd || exit` is an ordinary
`||` chain whose right operand is the `exit` flow-control statement.

---

## 8. Canonical form

The lexer normalises any block to this shape — a loop header (`None` when
absent) over a brace group of guarded statements, with nested groups where a
guard applies to more than one statement:

```
<None | list>:
{
    <guard>: <target> = <evaluation> [|| continue | break];
    <guard>: { <nested canonical group> } [|| continue | break];
    ...
}
```

where `guard ∈ { True, {rcode} == 0, {rcode} != 0, <user expression> }`,
`target ∈ { _, <name> }`, and the optional `|| continue` / `|| break` clause
carries the on-error action (absent ⇒ *ignore*).

### Parser output

The parser turns the canonical form into

```
(loop, [Statement(guard, target, evaluation, on_error), …])
```

* `loop` — the loop list, classified (a `Variable`/`Literal`) or `None`.
* `guard`, `evaluation` — each **classified** into `Variable` (a lone `{name}`),
  `Command` (first token is a known command), `Flow` (`continue`/`break`/`exit`),
  `Literal` (any other value expression), or `Block` (a nested group — the
  `evaluation` recurses into another statement list).
* `on_error` — `IGNORE` / `CONTINUE` / `BREAK`.

Variable substitution of `{…}` is performed by the **interpreter**, not the
parser; the parser only records where variables and commands occur.

### Worked examples

```
cmd1
─────────────────────────────
None:
{
    True: _ = cmd1;
}
```

```
cmd1; cmd2
─────────────────────────────
None:
{
    True: _ = cmd1;
    True: _ = cmd2;
}
```

```
cmd1 && cmd2
─────────────────────────────
None:
{
    True:          _ = cmd1;
    {rcode} == 0:  _ = cmd2;
}
```

```
cmd1 || cmd2
─────────────────────────────
None:
{
    True:          _ = cmd1;
    {rcode} != 0:  _ = cmd2;
}
```

```
x = {problem.number} + 1
─────────────────────────────
None:
{
    True: x = {problem.number} + 1;
}
```

```
loop {problems}: init {loop.number} && eval
─────────────────────────────
{problems}:
{
    True:          _ = init {loop.number};
    {rcode} == 0:  _ = eval;
}
```

---

## 9. Grammar (EBNF, surface syntax)

```ebnf
block        = [ loop-header ] sequence ;
loop-header  = "loop" [ expression ] ":" ;
                                         (* a missing ":" is auto-fixed before
                                            a "{…}" body group or newline, §7 *)
sequence     = or-expr { ( ";" | NEWLINE ) or-expr } [ ";" | NEWLINE ] ;
or-expr      = and-expr { "||" and-expr } ;
and-expr     = primary { "&&" primary } ;
primary      = group | statement ;
group        = "{" sequence "}" ;
statement    = assignment | command | expression ;
assignment   = name "=" evaluation ;
command      = command-name { argument } ;
evaluation   = command | expression ;
expression   = (* safe-eval subset: literals, comparisons, bool/unary/binary
                  operators, list/tuple literals, indexing/slicing,
                  calls to safe builtins, substituted names *) ;
name         = lowercase-letter { lowercase-letter | digit | "_" } ;
var-ref      = "{" name { "." name } [ ":" format-spec ] "}" ;
                                         (* expanded by the interpreter, §2 *)
argument     = word ;                    (* shlex-tokenised, {}-substituted *)
```