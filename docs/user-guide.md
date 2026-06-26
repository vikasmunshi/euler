# User Guide — the solver shell

This guide is for someone **using** the solver: launching the interactive shell,
driving it non-interactively, composing commands into blocks, and finding the
right command. For exact per-command usage see
[`commands-index.md`](commands-index.md); for writing solutions see the
[Solver Guide](solver-guide.md); for extending the framework see the
[Developer Guide](developer-guide.md).

---

## 1. Invocation

The shell is built on [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/)
and [rich](https://rich.readthedocs.io/): persistent history, auto-suggest,
tab-completion, and typed parameter dispatch.

### Three ways to invoke it

| Command            | Where           | Notes                                                                                                                          |
|--------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------|
| `euler-solver`     | anywhere        | the launcher the installer drops at `~/.local/bin/euler-solver`; it `cd`s into the repo, activates `.venv`, and execs `solver` |
| `solver`           | inside the venv | the installed console-script entry point (`solver.main:main`)                                                                  |
| `python -m solver` | inside the venv | the same entry point via the module's `__main__`                                                                               |

`euler-solver` is the convenient form from outside the project — you do not need
to activate the virtualenv yourself. `solver` and `python -m solver` are
equivalent and assume the `.venv` is already active (`source .venv/bin/activate`).
All three accept the same arguments and modes below; the examples use `solver`.

### Three modes

**1. Interactive** — a bare invocation with a terminal attached starts the prompt
loop:

```bash
solver                                 # launch the interactive shell
```

Inside the shell: `?` lists commands, `? <cmd>` shows usage, `exit` or `Ctrl-D`
quits. Tab completes commands, problem numbers, flags, and `Literal` values.

**2. Piped** — when standard input is not a terminal, the shell reads command
blocks from stdin, runs them in order, and exits with the last block's status.
This is the natural form for scripting against a heredoc or a generated block:

```bash
echo "init 42; eval; reset" | solver           # pipe a single block

solver <<'EOF'                                  # or a heredoc of several lines
init 42
eval && stack
reset
EOF
```

**3. Command** — pass a command block as an argument; the shell runs it, then
exits with its status (no prompt, no stdin read):

```bash
solver "init 42; eval; reset"          # run a block, then exit with its status
solver "init 42 && eval && stack"      # && gates each step on the previous one's success
solver -s "init 42; benchmark"         # -s also tees console output to the session log
```

Because the exit status propagates, `solver "<block>"` composes inside an outer
shell script or a `Makefile` target (`solver "init 42 && eval" && echo ok`).

### Command-line arguments

| Argument          | Description                                                                      |
|-------------------|----------------------------------------------------------------------------------|
| `-v`, `--version` | Print the version and exit                                                       |
| `-s`, `--save`    | Tee console output to the session log (interactive sessions only)                |
| `-h`, `--help`    | Show the argparse help and exit                                                  |
| `cmdline`         | A command block to run, then exit with its status; omit for interactive or piped |

### The web front end

`solver-web` serves the same shell — plus a read-only solution viewer and an
in-browser editor — over a single localhost `aiohttp` server (port `server_port`,
default 8080). It needs the `web` dependency group (`pip install -e ".[web]"`).

```bash
solver-web start        # launch the server (detached) and open the terminal in your browser
solver-web status       # report whether it is running (the default action)
solver-web stop         # stop it
solver-web restart      # stop then start
solver-web start --save # also tee the shell's console output to the session log
```

The server runs **detached**, so it keeps serving after the shell that launched
it exits; an `flock` it holds for its lifetime makes any later `solver-web`
invocation able to query or stop it (and is released automatically if it crashes). Browsing to `/` gives an `xterm.js` terminal running one interactive
`solver` shell — only one terminal session is allowed at a time, because every
session drives the same shared `workspace/`. `/summary` and `/<n>/` are the
read-only viewer pages; `show N` (below) auto-starts this server.

### The workspace lock

Only one shell may own `workspace/` at a time. On launch the shell acquires the
lock; a child process (e.g. `claude` launched via `!`) **inherits** it through
the `solver_workspace_lock` environment variable. The `solver-web` server holds
the lock the same way — acquiring it standalone or inheriting it when launched
from a running shell, and passing it to the PTY shell and any edits it makes.
Commands marked `§` refuse to run without the lock. `lock-status` reports who
holds it.

---

## 2. Command blocks

Commands compose with shell-style operators, both at the prompt and inside a
quoted `cmdline`. Every command returns a Unix exit code (`0` = success) and the
operators gate on it:

- `;` — run the next command unconditionally (sequential; a newline means `;`).
- `&&` — run the next command only if the previous **succeeded** (exit `0`).
- `||` — run the next command only if the previous **failed** (nonzero).
- `{ … }` — group commands; groups nest.

```bash
solver <<'EOF'
init 42 && eval && stack            # stop at the first step that fails
eval || echo "needs work"           # react to a failed evaluation
{ init 42; eval } && stack          # group, then save only if the group succeeded
EOF
```

A statement can also be a `name = expr` **assignment** or a bare **expression**.
An expression sets the exit code from its truthiness (`0` when truthy, `1` when
falsy), so it can gate a chain.

```bash
solver <<'EOF'
limit = 1000                        # assign a user variable
{problem.number} > 100 && echo "a later problem"
EOF
```

The command language — surface syntax, canonical form, and semantics — is
specified end to end in [`docs/syntax.md`](syntax.md).

### Variables

Reference any variable with `{name}` braces; references expand into both command
arguments and expressions. User variables are lowercase (`limit = 1000`). The
**reserved specials** are seeded by the shell:

| name       | type            | meaning                                                 |
|------------|-----------------|---------------------------------------------------------|
| `problem`  | Problem \| None | the workspace problem as an object (`{problem.number}`) |
| `rcode`    | int             | exit code of the most recent evaluation                 |
| `loop`     | Any             | the current `loop` element (`None` outside a loop)      |
| `next`     | int             | number of the next unsolved problem                     |
| `random`   | int             | number of a random unsolved problem                     |
| `problems` | list[Problem]   | every known problem                                     |
| `solved`   | list[Problem]   | the solved problems                                     |
| `unsolved` | list[Problem]   | the unsolved problems                                   |
| `stale`    | list[Problem]   | problems whose notes are older than their source        |

`next` / `random` are bare problem **numbers** (handy as arguments: `init
{next}`); `problems` / `solved` / `unsolved` / `stale` hold `Problem` objects —
reach a field with an attribute path (`{problem.number}`, `{loop.number}`). The
computed specials are re-evaluated on **every** reference, so `{random}` yields a
fresh pick and `{solved}` reflects current progress each time.

### Expressions

Beyond truthiness, expressions support comparisons, arithmetic, list/tuple/set
literals, indexing and slicing (`{solved}[0:5]`), and a fixed set of safe
builtins (`len`, `min`, `max`, `sum`, `sorted`, `range`, …). They are
side-effect free — there is no assignment *inside* an expression, only the
top-level `name = expr` statement.

### Loops

`loop <list>: <block>` is a **language construct** (not a command): it runs the
block once per element of a list, binding the special `loop` to the current
element. The list is any expression evaluating to a sequence — the built-in
number lists (each sliceable) or a literal.

```bash
$ solver <<'EOF'
loop {unsolved}[0:5]: {
  init {loop.number} || break     # set up the problem; stop the loop if init fails
  claude-skill solve              # work it
  stack && reset                  # save and clear before the next iteration
}

loop [1, 2, 3]: echo {loop}       # body runs with loop = 1, then 2, then 3
EOF
```

There is no implicit workspace lifecycle — you spell out `init … stack && reset`
yourself, keeping every per-iteration step explicit and gateable. `break` /
`continue` (or trailing `… || break`) control iteration; loops do not nest.

---

## 3. The command catalogue

Type `?` in the shell for this list, or `? <cmd>` for one command's usage. Each
command name below links to its full entry — usage and description — in the
[Command Index](commands-index.md). The legend glyphs appear in a command's help:

- `§` — requires the workspace lock.
- `↻` — may refresh workspace state (re-reads which problem is loaded).
- `»` — supports `--silent` to suppress its incidental output.

<!-- GEN:command-table -->
| Command | Aliases | Description |
|---------|---------|-------------|
| [`!`](commands-index.md#command--sh-bash) | `sh`, `bash` | Run a bash command. |
| [`?`](commands-index.md#command--help) | `help` | List commands or show help for a specific command. |
| [`claude-api`](commands-index.md#command-claude-api) | — | Generate specified target using Claude API. |
| [`claude-skill`](commands-index.md#command-claude-skill) | — | Launch the Claude Euler Solver skill. |
| [`clear`](commands-index.md#command-clear-cls) | `cls` | Clear the screen. |
| [`costs`](commands-index.md#command-costs) | — | Display total cost of AI API tokens consumed in session. |
| [`echo`](commands-index.md#command-echo) | — | Print text. |
| [`eval-benchmark`](commands-index.md#command-eval-benchmark-benchmark) | `benchmark` | Benchmark the problem currently in the workspace. » |
| [`eval-compile-c`](commands-index.md#command-eval-compile-c-compile) | `compile` | Build all C source files in the solutions_dir. » |
| [`eval-evaluate`](commands-index.md#command-eval-evaluate-eval) | `eval` | Evaluate solutions against test cases. » |
| [`eval-set-problem`](commands-index.md#command-eval-set-problem-problem) | `problem` | Set the active problem » |
| [`git-commit`](commands-index.md#command-git-commit-commit) | `commit` | Commit everything, optionally resetting to origin/master. » |
| [`git-hooks`](commands-index.md#command-git-hooks-hooks) | `hooks` | Run pre-commit hook and simulated pre-push hook. » |
| [`git-publish`](commands-index.md#command-git-publish-publish) | `publish` | Push targets (keys|scripts|solutions|solver) to remote. » |
| [`git-status`](commands-index.md#command-git-status-status) | `status` | Display sync state between local and origin/master. |
| [`git-sync`](commands-index.md#command-git-sync-sync) | `sync` | Bring the local repository in sync with origin/master. |
| [`key-reconstruct`](commands-index.md#command-key-reconstruct) | — | Recover master key from shares. |
| [`key-rekey`](commands-index.md#command-key-rekey-rekey) | `rekey` | Rotate the enc key and re-wrap to users. |
| [`key-split`](commands-index.md#command-key-split) | — | Split master key into shares (n-of-m secret sharing). |
| [`lint`](commands-index.md#command-lint) | — | Lint current problem, auto-fix with --auto-fix. » |
| [`manage-config`](commands-index.md#command-manage-config) | — | Manage configuration settings. |
| [`mark`](commands-index.md#command-mark-mark-solved) | `mark-solved` | Mark the workspace problem as solved, after checking. » |
| [`new`](commands-index.md#command-new) | — | Generate new solution/test-case file in the workspace. » |
| [`pause`](commands-index.md#command-pause) | — | Pause for user confirmation to continue. |
| [`pip-upgrade`](commands-index.md#command-pip-upgrade-upgrade) | `upgrade` | Upgrade dependency group (all|ai|core|dev|solutions|show). |
| [`problems`](commands-index.md#command-problems) | — | Show list of problems (all|solved|unsolved). |
| [`progress`](commands-index.md#command-progress) | — | Print progress statistics about Euler problems. |
| [`search`](commands-index.md#command-search-find) | `find` | Find content in the stack. |
| [`show`](commands-index.md#command-show-open-view) | `open`, `view` | Open problem documentation in a browser. » |
| [`summary`](commands-index.md#command-summary) | — | Parse .progress.html into problems.json. » |
| [`sys-setup`](commands-index.md#command-sys-setup-install) | `install` | Installs or uninstalls system resources. |
| [`update-docs`](commands-index.md#command-update-docs) | — | Regenerate the generated sections of the docs/ guides. » |
| [`update-models`](commands-index.md#command-update-models) | — | Update Model enum, pricing, and USD→EUR rate. » |
| [`user`](commands-index.md#command-user) | — | Show public key & enc-key access; --regen for new key-pair. |
| [`user-authorize`](commands-index.md#command-user-authorize-authorize) | `authorize` | Authorise another public key (hex) to access the enc key. |

*Legend: § requires the workspace lock · ↻ may refresh workspace state · ⊘ refuses while the workspace is checked out · ⚑ checks the workspace out while it runs · » supports `--silent`.*
<!-- /GEN:command-table -->

> The table above is generated from the live command registry by the
> `update-docs` command. See [`commands-index.md`](commands-index.md)
> for each command's full usage.

---

## 4. Typical sessions

**Solve a problem** (see the [Solver Guide](solver-guide.md) for the full loop):

```bash
solver <<'EOF'
init 42     # initialize the workspace for problem 42
checkout    # optionally, check out the workspace to prevent accidental reset
show        # open the problem page in a browser to read and understand the problem
pause       # create scripts (non-executable files) in the workspace directory to derive/confirm mathematical insights
new --tc    # create an empty test-case file in the workspace directory
new --py    # create a template Python solution file in the workspace directory (p0042_s0.py)
pause       # implement solve() in the solution template
eval        # evaluate the solution against the test cases
pause       # record the answers in the test-case file
benchmark   # time the solution, the first time it is run 1 time
mark        # mark the problem as solved
new --c     # create a template C solution file in the workspace directory (p0042_s0.c)
pause       # translate the solution to C,
benchmark   # time the solution, (it is run between 1 to 21 times based on earlier times)
pause       # document your learnings in notes.html
stack       # save the workspace to the stack
checkin     # check in the workspace,
reset       # clear the workspace (reset before checkin is blocked by checkout)
EOF
```

**Sweep a range of unsolved problems:**

```bash
solver <<'EOF'
loop {unsolved}[0:5]: { init {loop.number} && checkout && claude-skill solve && stack && checkin && reset }
EOF
```

---

## 5. AI assistance

Two complementary AI paths are wired into the shell (both require the `ai`
dependency group;
API requires `ANTHROPIC_API_KEY` in `.env`;
Claude Code requires authentication in the CLI `claude /login`):

- **`claude-api <target>`** — a single templated Claude API call that writes one
  artifact: `py` / `c` (a solution), `notes` (the write-up), or `test-cases`. It
  is fast and cheap, and `costs` tracks its token spend, but the AI neither runs
  nor verifies its output — that happens afterwards in the script.
- **`claude-skill <action>`** — full Claude Code working against the *locked*
  workspace: it runs `solver` commands, edits files, evaluates, benchmarks, and
  iterates. The actions are `review` and `solve`. Heavier and slower, it is meant
  for the harder job. `! claude <prompt>` drops into an interactive Claude Code
  session against the same workspace.

The goal is to deepen understanding, not skip it: generate alternatives *after*
you have solved a problem, or translate your Python into C for comparison.

---

## 6. Sessions, history, and config

- **History** persists across sessions; auto-suggest offers your past lines.
- **`-s` / `--save`** tees the interactive session (typed input + console output)
  to the session log.
- **`manage-config`** shows or sets the managed settings (`server_port`,
  timeouts, `usd_to_eur`); **`config`**-style values persist to
  `solver/config.json`.
- **`! <cmd>`** runs a bash command in the workspace (`! sh` / `! py` drop into a
  shell / Python interpreter); it inherits the workspace lock.

---

## 7. Key Exchange

Solutions under `solutions/private/` are encrypted at rest (in accordance with
[Project Euler's guidelines](https://projecteuler.net/about#publish)) by a
**transparent git clean/smudge filter** — they are ciphertext in git but plaintext
in your working tree, with no `init`/`stack`/`reset` step. You only need keys if you
want to collaborate on, or study, those files; `solutions/public/` is plaintext and
needs nothing. The mechanics of the filter itself are covered in the
[Git Filter Guide](gitfilter-guide.md); this section covers the key material.

### The two keys

```
~/.solver/id            - your X25519 private key (PKCS8 PEM, password-protected)
keys/.user-pass         - the private-key password (machine-local; gitignored, never committed)
keys/enc-key.json       - { <public-key-hex>: <master key wrapped for that key>, "verify": <check ciphertext> }
```

There is a single 32-byte **master key**. It is never stored in the clear: each
authorised user holds their own copy, wrapped to their X25519 public key with an
ephemeral ECDH exchange (HKDF-SHA256 + ChaCha20-Poly1305). Keys are identified by
their **public key**, not by email. Loading reads the password from `keys/.user-pass`,
decrypts the private key, unwraps the master key, and proves it correct against the
`verify` ciphertext before use. Authority is **proof-of-possession** — anyone who can
unwrap and verify the master key may rotate it, authorise another key, or split it.

### Gaining access (new user)

```bash
solver "user"        # creates ~/.solver/id (prompts for a password) and prints your public key
```

Send your public key to an existing user, who authorises it:

```bash
solver "authorize <your-public-key-hex>"   # wraps the master key to your public key in enc-key.json
```

Commit and push `keys/enc-key.json`; pull it, and `solver "user"` will now report
`✓ can encrypt/decrypt`. As a fallback you can `key-reconstruct` the master key from
`threshold` out-of-band shares produced by `key-split` (n-of-m secret sharing).

### Studying the solutions

Once you have master-key access the private files are plaintext in your working tree —
just open them. Or use `show N` to view any problem's statement, notes, and results in
a browser via the `solver-web` server.

---
