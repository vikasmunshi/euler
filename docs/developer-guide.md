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
user types:  init 42 --force-refresh
                │
                ▼
  lexer → parser → interpreter        (solver/shell/*)
                │  resolves the command, builds a Context, passes raw argv
                ▼
  @register adapter                   (solver/shell/register.py)
                │  shlex split · type coercion · flag parsing · error reporting
                ▼
  your function  init(problem_number: int, *, force_refresh: bool = False) -> int
```

The contract is therefore: **you write an ordinary typed function that returns an
`int` exit code; `@register` derives the command name, usage, completion, and
argument coercion from its signature.**

---

## 2. A minimal command

```python
from solver.shell import console, register


@register(help_text='Greet someone.')
def greet(name: str, times: int = 1) -> int:
    """Print a greeting `times` times."""
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
- **argument coercion** — `times=3` arrives as the `int` `3`, not the string
  `'3'`, because the parameter is annotated `int`.

---

## 3. The register contract in detail

```python
def register(
    *,
    help_text: str = '',
    aliases: tuple[str, ...] = (),
    pass_ctx: bool = False,
    quietable: bool = False,
    changes_workspace: bool = False,
) -> Callable[[Callable[P, int]], Callable[P, int]]
```

### 3.1 Your function must return `int`

The return value **is** the exit code, forwarded verbatim (`0` = success, nonzero
= failure). The shell composes commands with `;`, `&&`, `||`, so this code is
what gates a chain (`init 42 && eval && stack`). Use the named constants from
`solver.shell.command` rather than bare integers:

| constant       | value | meaning                |
|----------------|-------|------------------------|
| `EXIT_OK`      | `0`   | success                |
| `EXIT_ERROR`   | `1`   | generic failure        |
| `EXIT_USAGE`   | `2`   | parse / usage error    |
| `EXIT_NOTFOUND`| `127` | unknown command        |

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

### 3.3 `help_text` and `aliases`

`help_text` is the one-line description shown by `?`. If omitted, the adapter
falls back to the first line of the function's docstring. `aliases` is a tuple of
alternative names (`aliases=('eval',)` makes `eval` resolve to `evaluate`);
registering a name or alias that already exists raises at import time.

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


@register(help_text='Show the current problem number.', pass_ctx=True)
def cur(ctx: Context) -> int:
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

### 3.7 `changes_workspace` — refreshing workspace state

`changes_workspace=True` wraps the function so that, after it runs, the shell
re-derives the `problem` special from the workspace and prints a one-line status
(`Workspace has #42 …` / `Workspace is empty`). Use it on commands that mutate
which problem is loaded (`init`, `reset`). These are marked `↻`.

### 3.8 The workspace lock decorator

Independent of `@register`, commands that touch `workspace/` stack the
`check_workspace_lock_command` decorator (from `solver.core.lock`) **beneath**
`@register`:

```python
from solver.core.lock import check_workspace_lock_command


@register(help_text='…', changes_workspace=True)
@check_workspace_lock_command
def init(problem_number: int, /, *, force_refresh: bool = False) -> int:
    ...
```

It refuses to run (returning a failure code) unless this process holds — or
inherited — the workspace lock, preventing two shells from corrupting the
workspace. Such commands are marked `§` in the help legend. `check_workspace_lock_command`
is for `-> int` commands; `check_workspace_lock_generic` is the variant for
helper functions returning other types.

---

## 4. Completion

Tab-completion is derived from the signature for free:

- `Literal[...]` members are offered for the relevant positional/keyword slot;
- `bool` parameters offer `true`/`false` and the `--flag` forms;
- `Optional[...]` offers `none`;
- keyword parameters offer `name=` once they are not yet supplied on the line.

Two parameter **names** are special-cased: `problem_number` completes to known
problem numbers (with titles) plus `{next}`/`{random}`, and `solution` completes
to executable files in the workspace. Reusing those names gives you that
behaviour automatically.

---

## 5. Registering and loading a module

Commands are collected at **import time** — the `@register` decorator runs as the
module is imported, registering the adapter. A module's commands therefore exist
only if the module is imported on startup.

`solver/shell/loader.py` reads `solver/modules.csv`, a three-column manifest:

```
module,registers_commands,load
solver.core.workspace,True,True
solver.core.problems,,
```

- **`registers_commands`** — auto-detected: `True` when the module's source
  contains an `@register(` or `@command(` decorator.
- **`load`** — the manual on/off switch. A module is imported on startup iff
  *both* columns are truthy. Blank, `false`, `0`, `no`, `off` mean off.

The manifest is **regenerated** by scanning `solver/` whenever it is missing or
when you run `load_commands(refresh_modules=True)` (e.g. `python -m
solver.shell.loader`). Regeneration **preserves** your manual `load` edits for
known modules and defaults a newly discovered module's `load` to whether it
registers commands. So the workflow for a new command module is:

1. Create `solver/<area>/<module>.py` with one or more `@register` functions.
2. Run `python -m solver.shell.loader` (or just start the shell after a
   `refresh_modules`) to add it to `modules.csv` with `load=True`.
3. Verify with `? <command>` in the shell.

To temporarily disable a module's commands, set its `load` cell to `False` —
the row survives regeneration.

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
- [ ] One-line `help_text` (or a docstring whose first line serves as one).
- [ ] `aliases=(...)` if it deserves a short form.
- [ ] `pass_ctx=True` only if you need shell state.
- [ ] `quietable=True` if its output is incidental to scripting.
- [ ] `changes_workspace=True` if it changes which problem is loaded.
- [ ] `@check_workspace_lock_command` beneath `@register` if it touches `workspace/`.
- [ ] Module added to `modules.csv` with `load=True` (via the loader).
- [ ] `mypy solver` and `flake8 solver` clean.
- [ ] If you changed any command's name/help/usage, run the `update-docs`
      command to refresh the generated docs.
