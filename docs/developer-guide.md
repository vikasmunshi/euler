# Developer Guide — writing command modules

This guide is for someone **extending** the solver: adding a new shell command or
a new command module. It explains the **register contract** — what `@register`
expects of your function and what it gives you in return — and how command
modules are discovered and loaded.

If you only want to *use* the shell, read the [User Guide](user-guide.md). If you
are writing Project Euler *solutions*, read the [Solver Guide](solver-guide.md).

---

## 1. The big picture

Every shell command is a **plain Python function** decorated with `@register`
(from `solver.shell`). The decorator does not change the function — it stays a
normal callable you can import and unit-test — it only *registers an adapter* in
the command registry. The adapter is what the shell invokes: it tokenises the
input line, coerces each token to your parameter's annotated type, calls your
function, and maps the outcome to a Unix exit code.

```
user types:  eval 42 main --clean
                │
                ▼
  lexer → parser → interpreter        (solver/shell/*)
                │  resolves the command, builds a Context, passes raw argv
                ▼
  @register adapter                   (solver/shell/register.py)
                │  shlex split · type coercion · flag parsing · error reporting
                ▼
  your function  eval_evaluate(problem: Problem, *categories: str, clean: bool = False) -> int
```

The contract is therefore: **you write an ordinary typed function that returns an
`int` exit code; `@register` derives the command name, usage, completion, and
argument coercion from its signature.**

---

## 2. A minimal command

```python
from solver.shell import console, register


@register(requires='reader')
def greet(name: str, times: int = 1) -> int:
    """Greet someone by name.

    Args:
        name: Who to greet.
        times: How many times to greet them. Defaults to 1.
    """
    for _ in range(times):
        console.print(f'Hello, {name}!')
    return 0
```

That is a complete command. At the prompt:

```
greet World            # name='World', times=1
greet World times=3    # name='World', times=3 (coerced to int)
greet                  # usage error: missing required <name>
? greet                # shows the synthesised usage
```

Three things were derived automatically from the signature:

- **the command name** `greet` — the function name with underscores turned into
  dashes (`pip_upgrade` → `pip-upgrade`). Override it by renaming the function.
- **the usage string** — `greet <name> [times=<int>] (default 1)`.
- **the description** `?` lists, and `docs/commands-index.md` publishes — the
  docstring's summary line (§3.8).
- **argument coercion** — `times=3` arrives as the `int` `3`, not the string
  `'3'`, because the parameter is annotated `int`.

---

## 3. The register contract in detail

```python
def register(
    *,
    aliases: tuple[str, ...] = (),
    pass_ctx: bool = False,
    quietable: bool = False,
    completers: dict[str, Callable[[Context, str], Iterable[str | Completion]]] | None = None,
    requires: Literal['reader', 'contributor', 'maintainer', 'admin'],
) -> Callable[[Callable[P, int]], Callable[P, int]]
```

`requires` is **mandatory** and keyword-only (§3.7); every other argument is optional.

### 3.1 Your function must return `int`

The return value **is** the exit code, forwarded verbatim (`0` = success, nonzero
= failure). The shell composes commands with `;`, `&&`, `||`, so this code is
what gates a chain (`eval 42 && benchmark`). Use the `ExitCodes` members from
`solver.config` rather than bare integers:

| member                     | value | meaning             |
|----------------------------|-------|---------------------|
| `ExitCodes.EXIT_OK`        | `0`   | success             |
| `ExitCodes.EXIT_ERROR`     | `1`   | generic failure     |
| `ExitCodes.EXIT_USAGE`     | `2`   | parse / usage error |
| `ExitCodes.EXIT_NOTFOUND`  | `127` | unknown command     |

You rarely return `EXIT_USAGE` yourself — the adapter returns it for you when
argument parsing fails.

### 3.2 Parameters become arguments by type

The adapter splits each input line with `shlex`, then routes tokens:

- **positional tokens** fill positional parameters in order;
- **`key=value` tokens** fill the named (keyword-bindable) parameter;
- **`--flag` / `--no-flag` tokens** set boolean parameters (see §3.4).

Each token is coerced (`_coerce`) against the target parameter's annotation:

| annotation                    | coercion                                                            |
|-------------------------------|---------------------------------------------------------------------|
| `str`                         | passed through unchanged                                            |
| `int`, `float`                | constructor (`int(tok)`); a bad value is a reported usage error      |
| `bool`                        | `1/true/yes/y/on` (case-insensitive) → `True`, else `False`         |
| `Literal[...]`                | validated against the members; coerced to the matched member's type |
| `X \| None` / `Optional[X]`   | `none/null/''` → `None`, otherwise coerce to `X`                     |
| `enum.Enum` subclass          | `EnumType(value)`                                                   |
| anything else                 | `ast.literal_eval` (so `[1,2]`, `(1,2)`, `{'a':1}` parse)            |

The parameter **kind** decides how a token may be supplied, matching Python's own
call semantics:

```python
def cmd(required, /, optional='x', *rest, kw_only, flag=False, **extra): ...
#       │              │            │      │         │            └ surplus key=value tokens
#       │              │            │      │         └ boolean → flag or flag=value
#       │              │            │      └ keyword-only → must be `kw_only=...`
#       │              │            └ *args → extra positionals
#       │              └ positional-or-keyword, has a default → optional
#       └ positional-only → first positional token
```

`*args` soaks up surplus positionals (each coerced against the `*args`
annotation — annotate it `*args: int` to get ints). `**kwargs` soaks up unknown
`key=value` tokens (coerced against the `**kwargs` annotation).

### 3.3 The description, and `aliases`

There is **no `help_text`**. A command's one-line description is its docstring's
summary line (§3.8) — read by `summary_of()` at registration, shown by `?`, and
published in `docs/commands-index.md`. One summary, one place to edit it: the
parameter existed for years alongside the docstring and the two drifted apart on most
commands, each telling the reader something slightly different.

`aliases` is a tuple of alternative names (`aliases=('eval',)` makes `eval` resolve to
`evaluate`); registering a name or alias that already exists raises at import time.

### 3.4 Boolean flags

A `bool` parameter can be set either as `name=true` or with a CLI-style flag.
Underscores become dashes (`dry_run` → `--dry-run`). The flag set depends on the
default:

| default      | flags generated                       |
|--------------|---------------------------------------|
| *(required)* | `--name` (True) **and** `--no-name` (False) |
| `False`      | `--name` (True)                       |
| `True`       | `--no-name` (False)                   |

A flag and `name=value` for the *same* parameter on one line conflict and are
reported as a usage error.

### 3.5 `pass_ctx` — reaching shell state

Pass `pass_ctx=True` to receive the live `Context` as the **first positional
parameter** (conventionally `ctx: Context`). The adapter injects it and parses
user tokens against the *remaining* parameters, so `ctx` never consumes a token.

```python
from solver.shell import register
from solver.shell.command import Context


@register(requires='reader', pass_ctx=True)
def cur(ctx: Context) -> int:
    """Print the current problem number.

    Args:
        ctx: [injected] The live shell context; the decorator supplies it.
    """
    ctx.console.print(ctx.variables['problem'])
    return 0
```

`Context` exposes:

| field         | use                                                              |
|---------------|------------------------------------------------------------------|
| `console`     | the shared `rich` console — **always** print through this        |
| `variables`   | the interpreter's variable store (reserved specials + user vars) |
| `argv`        | the parsed token list for this invocation                        |
| `raw_line`    | the original input line                                          |
| `shell`       | the owning `SolverShell` (loosely typed; rarely needed)          |

Most commands do **not** need `ctx` — only reach for it when you must read shell
state or drive the shell itself.

### 3.6 `quietable` — the `--silent` flag

`quietable=True` adds a synthetic `--silent` / `silent=true` flag (it is *not* a
function parameter — the adapter pops it and runs your body with the shared
console quiet). Output your command would print is suppressed, while the final
`cmd(...) → rc` summary and any errors still show. Use it for commands whose
output is incidental to a scripted pipeline. Quietable commands are marked `»` in
the help legend.

### 3.7 `requires` — the authorization floor

`requires` is the **minimum profile** a subject needs to run the command, and it is
**mandatory**: omitting it is a type error, so a command can never be exposed by
forgetting to declare its floor. The rungs are `reader` → `contributor` →
`maintainer` → `admin`, compared by rank (`solver/auth`).

The check happens at **registration**, not at call time: below the floor the command
is never registered at all — invisible to `?` and to completion, "unknown command" if
typed — while the function is returned unchanged, so it stays an ordinary Python
callable. Authorization is by profile only; the channel (terminal vs web) is not an
axis.

Two consequences worth knowing. `registry.all()` is only ever *this* subject's
registry, which is why the commands that generate or audit documentation from it
(`update-docs`, `check-commands`) are admin-floored. And a floor is about blast
radius: read verbs sit at `reader`, verbs that write a collaborator's own branch at
`contributor`, gates onto `master` at `maintainer`, host and key administration at
`admin`.

### 3.8 The docstring standard

A command's docstring is not an internal note — it is the command's
documentation, rendered in two user-facing places: the panel `? <command>`
prints, and the per-command reference in `docs/commands-index.md` (generated
verbatim by `update-docs`). Write it for someone at the prompt deciding what to
type, not for someone reading the call site.

The shape:

```python
"""<Imperative one-line summary, ending with a period.>

<Prose: what the command does, when to reach for it, how it relates to
neighbouring commands, and any non-obvious exit code. One or more paragraphs.
Omit it when the summary genuinely says everything.>

Args:
    ctx: [injected] The live shell `Context`; the decorator supplies it — never
        typed at the prompt.
    problem: [problem] The problem to evaluate. Typed as a bare number
        (`eval 42`) or `problem=42`; omit it to use the current problem, and
        supplying it makes that problem current.
    *categories: Test-case categories: 'dev', 'main', 'extra' or 'all'.
        Defaults to 'dev' and 'main'.
    runs: How many times to run each solution per test case. Defaults to 1.

<Optional free sections — `Repeats:`, `Examples:`, `Notes:` — for anything that
is not per-argument.>
"""
```

The rules, all enforced by the `check-commands` command (§3.9):

1. **The first line is the summary**, one line, ending in a period, and **under 80
   columns**. It is the command's only description: the cell `?` and the generated
   catalogue tables print, so it has to fit one. Write it as an imperative — "Evaluate
   a problem's solutions against its test cases." — not as a noun phrase.
2. **Every parameter is documented, in signature order, and nothing else is.**
   Variadics keep their stars (`*categories:`, `**kwargs:`). A throwaway `*_` is
   exempt. An entry with no description counts as undocumented.
3. **Continuation lines indent four further** than the parameter name. Do *not*
   align descriptions into a column: alignment reflows every entry the moment a
   parameter is renamed, and the renderer ignores it anyway.
4. **State defaults in words** ("Defaults to 1") — the synthesized usage line
   already shows the machine form, so repeating it buys nothing.
5. **No `Returns:` and no `Raises:` sections.** Every command returns an `int`
   exit code and the adapter catches everything it raises, so both sections are
   pure boilerplate. Where the exit code carries a *meaning* worth gating a
   `&&` chain on, say so in one prose sentence instead.
6. **Parameter sections are spelled `Args:`.** Free sections are titled and
   `Capitalised:` on their own line.
7. **Rendered lines stay under 100 columns** (`inspect.getdoc` output, i.e. after
   dedenting), because they land inside a panel and a fenced doc block.
8. **Inline code takes single backticks** — `` `results.json` ``, markdown-style. The
   rST `` ``literal`` `` form renders as stray punctuation in the help panel, and the
   docstrings were swept to one spelling so every reader sees the same thing.

#### Markers — where an argument's value comes from

Two parameters are supplied by the framework rather than typed like the rest, and
a reader has no way to tell from the name alone. Each takes a marker at the
**start** of its description:

| Marker        | Applies to                             | Means                                                                                       |
|---------------|----------------------------------------|---------------------------------------------------------------------------------------------|
| `[injected]`  | `ctx: Context` (`pass_ctx=True`)       | The decorator injects it; it never consumes a token and never appears in usage.               |
| `[problem]`   | `problem: Problem` (the problem special) | Typed as a bare number or `problem=N`, or omitted to inherit — and supplying it sets — the current problem. |

Ordinary arguments take no marker; a marker on one is an error.

`--silent` deliberately gets **no** entry. It is not a function parameter at all
(the adapter synthesizes it for `quietable=True`) and it means the same thing on
every command, so the renderer supplies the standard line — exactly as the `»`
legend glyph already does.

#### What the reader gets

`? <command>` renders, in order: the summary; the **facts** about the command, one
glyph line each — `⚑` the profile floor, `❏` the problem special, `»` `--silent`; the
docstring's prose; the synthesized usage; a row per typeable argument; then each free
section. `update-docs` renders that **same model** (`HelpModel`, built by
`solver/shell/docstring.py`) as markdown into `docs/commands-index.md`, so the
published reference for a command *is* its help rather than a second description of
it. Write the docstring once and both are right.

### 3.9 `check-commands` — enforcing the standard

`check-commands` walks the live registry and reports every docstring that breaks
§3.8, as `command | rule | detail` rows. It is part of
`scripts/linters/check.sh solver`, so it runs with `mypy` and `flake8`.

```bash
check-commands              # the whole registry
check-commands evaluate     # one command, while you rewrite it
```

Like `update-docs`, it is **admin-floored on purpose**: registration is
profile-filtered, so a lesser profile's registry is missing commands entirely and
the check would pass by not looking at them.

---

## 4. Completion

Tab-completion is derived from the signature for free:

- `Literal[...]` members are offered for the relevant positional/keyword slot;
- `bool` parameters offer `true`/`false` and the `--flag` forms;
- `Optional[...]` offers `none`;
- keyword parameters offer `name=` once they are not yet supplied on the line.

One parameter **name** is special-cased: a `problem` parameter (annotated `Problem`,
optionally `| None`) completes to known problem numbers, each shown with its title,
plus the `{next}` / `{random}` aliases. Reusing that name gives you the behaviour
automatically.

That parameter is the **problem special**: the user gives it as a bare problem number
— positionally (`eval 42 …`) or as `problem=42` — which the adapter coerces to a
`Problem`. Supplying it *remembers* the choice as the current problem
(`variables.problem`); omitting it injects the current problem, so a command can
declare `problem: Problem` and never worry about resolving it. Only a leading
positional naming a *known* problem is consumed as `problem`, so a trailing
`*categories` (or other positionals) are unaffected. Document it as `[problem]`
(§3.8) — the marker is how a reader knows the argument is optional at the prompt
despite having no default in the signature.

For values the type system cannot enumerate — a filename, a topic slug — pass
`completers={'param': fn}`, where `fn(ctx, incomplete)` returns candidate strings (or
`Completion` objects, passed through verbatim). It governs the parameter both
positionally and as `param=`.

---

## 5. Registering and loading a module

Commands are collected at **import time** — the `@register` decorator runs as the
module is imported, registering the adapter. A module's commands therefore exist
only if the module is imported on startup.

`solver/utils/loader.py` reads `solver/modules.csv`, a **two-column** manifest:

```
module,registers_commands
solver.core.evaluate,True
solver.core.problems,
```

- **`registers_commands`** — auto-detected: `True` when the module's source
  contains an `@register(` or `@command(` decorator. A module is imported on
  startup iff this is truthy (`true`, `1`, `yes`); blank means off.

It is a **pure loader manifest**: which of an imported module's commands actually
register is decided per-command by the decorator against the current subject's
profile (§ Authorization), not here. The manifest once carried a `load` column
and channel columns; both are gone — every command-registering module imports,
and gating happens at the command.

The manifest is **regenerated by scanning** `solver/` whenever it is missing or
when you run `load_commands(refresh_modules=True)` (e.g. `python -m
solver.utils.loader`; `update-docs` refreshes it too). Regeneration is a pure
scan — rows for deleted modules are dropped and new ones added, so there is
nothing to hand-edit. The workflow for a new command module is:

1. Create `solver/<area>/<module>.py` with one or more `@register` functions.
2. Run `python -m solver.utils.loader` (or `update-docs`) to add it to
   `modules.csv`.
3. Verify with `? <command>` in the shell.

To temporarily disable a module's commands, clear its `registers_commands` cell.
Regeneration re-derives the cell by scanning the source, so the change lasts only
until the next refresh — for anything permanent, remove the decorators.

---

## 6. Error handling — what the adapter does for you

You generally do **not** wrap your body in try/except for argument problems. The
adapter:

- reports a coercion failure with the offending token under a caret, then the
  usage line, and returns `EXIT_USAGE`;
- relabels a Python `TypeError` from wrong arg count/keywords as a usage error;
- catches `KeyboardInterrupt` (prints `interrupted`, returns `EXIT_ERROR`);
- catches any other exception, prints a rich traceback, and returns `EXIT_ERROR`.

So inside the function you can assume arguments are present and well-typed, raise
on genuinely exceptional conditions, and otherwise `return` a meaningful exit
code. Print user-facing output through `ctx.console` (or the shared
`solver.shell.tty.console`) so `--silent` and session logging work.

---

## 7. The lower-level `@command` decorator

`@register` is built on top of `@command` (`solver/shell/command.py`), which
registers a function with the **raw** signature `(ctx: Context, *argv: str)` and
no coercion — you parse `argv` yourself. The framework built-ins that need full
control over their argument line (`?`, `clear`, the `!` bash passthrough) use
`@command` directly. Prefer `@register` for everything else; reach for
`@command` only when token-level coercion is in your way.

---

## 8. Checklist for a new command

- [ ] Plain function, fully type-annotated, returns `int` (`EXIT_*`).
- [ ] Docstring follows the standard in §3.8 — summary line, prose, `Args:` with
      every parameter described and `ctx` / `problem` marked. `check-commands` clean.
- [ ] `aliases=(...)` if it deserves a short form.
- [ ] `pass_ctx=True` only if you need shell state.
- [ ] `quietable=True` if its output is incidental to scripting.
- [ ] `requires=` set to the least profile that should have it (§3.7) — it shows in
      the help panel and in the catalogue's `Requires` column.
- [ ] Module listed in `modules.csv` — run `python -m solver.utils.loader` (or
      `update-docs`) to add the row by scanning.
- [ ] `scripts/linters/check.sh solver` clean (`mypy`, `flake8`, `check-commands`).
- [ ] If you changed any command's name/help/usage, run the `update-docs`
      command to refresh the generated docs.
