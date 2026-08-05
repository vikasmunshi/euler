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
echo "eval 42; benchmark 42" | solver           # pipe a single block

solver <<'EOF'                                  # or a heredoc of several lines
new 42 --py
eval 42 && benchmark 42
EOF
```

**3. Command** — pass a command block as an argument; the shell runs it, then
exits with its status (no prompt, no stdin read):

```bash
solver "eval 42; benchmark 42"         # run a block, then exit with its status
solver "eval 42 && benchmark 42"       # && gates each step on the previous one's success
solver -s "eval 42; benchmark 42"      # -s also tees console output to the session log
```

Because the exit status propagates, `solver "<block>"` composes inside an outer
shell script or a `Makefile` target (`solver "eval 42 && benchmark 42" && echo ok`).

### Command-line arguments

| Argument          | Description                                                                      |
|-------------------|----------------------------------------------------------------------------------|
| `-v`, `--version` | Print the version and exit                                                       |
| `-s`, `--save`    | Tee console output to the session log (interactive sessions only)                |
| `-h`, `--help`    | Show the argparse help and exit                                                  |
| `cmdline`         | A command block to run, then exit with its status; omit for interactive or piped |

### The web front end

The same shell — plus a solution viewer and an in-browser editor — is served by
the **deployed web stack**, not by a local process you start: a TLS edge, an SRP
login, and one service per collaborator. Its architecture and deployment are in
[web-server-guide.md](web-server-guide.md) (`make deploy-web`).

Signing in and browsing to `/` gives an `xterm.js` terminal attached to **your own
persistent `solver` shell**: it is forked the first time you connect (as your
signed-in identity, see §6) and **survives disconnect** — closing the tab or
dropping the connection leaves it running, and reconnecting reattaches to it with
its recent output replayed. There is at most one shell per user, so a second
browser tab attaches to the *same* shell (a shared terminal). The shell is torn
down when you type `exit`, log out, or the service stops. `/solutions/` and
`/solutions/NNNN/` are the viewer pages, and they render in the left pane while
the terminal keeps its session in the right one.

`show N` (below) opens a problem's page over the same bridge. From a web shell it
swaps the left pane in place; from a local terminal it opens `$EULER_BASE_URL`
(default `https://euler.vikasmunshi.com`) in a dedicated browser tab named
`solver-doc`, which every later `show` reuses — refreshing it for the same
problem, navigating it for another.

The code editor (and the read-only file viewer) is CodeMirror 6, with a
line-number gutter, syntax highlighting for Python/C/JSON, and word-wrap always
on, so long lines soft-wrap rather than running off-screen. It is progressive
enhancement over a plain `<textarea>`: with JavaScript off, the form still edits
and submits through the same save gate.

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
new 42 --py && eval 42 && benchmark 42   # stop at the first step that fails
eval 42 || echo "needs work"             # react to a failed evaluation
{ new 42 --py; eval 42 } && benchmark 42 # group, then benchmark only if it succeeded
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
| `problem`  | Problem \| None | the current problem as an object (`{problem.number}`)   |
| `rcode`    | int             | exit code of the most recent evaluation                 |
| `loop`     | Any             | the current `loop` element (`None` outside a loop)      |
| `next`     | int             | number of the next unsolved problem                     |
| `random`   | int             | number of a random unsolved problem                     |
| `problems` | list[Problem]   | every known problem                                     |
| `solved`   | list[Problem]   | the solved problems                                     |
| `unsolved` | list[Problem]   | the unsolved problems                                   |
| `stale`    | list[Problem]   | problems whose notes are older than their source        |

`next` / `random` are bare problem **numbers** (handy as arguments: `eval
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
  claude-solve {loop.number} solve || break   # work it; stop the loop on failure
}

loop [1, 2, 3]: echo {loop}       # body runs with loop = 1, then 2, then 3
EOF
```

Each per-iteration step is explicit and gateable. `break` / `continue` (or a
trailing `… || break`) control iteration; loops do not nest.

---

## 3. The command catalogue

Type `?` in the shell for this list, or `? <cmd>` for one command's usage. Each
command name below links to its full entry — usage and description — in the
[Command Index](commands-index.md). **Requires** is the least profile that may run the
command; every rung above it may too, and below it the command is not registered at all,
so it does not appear in your own `?` listing. What four columns cannot show — whether a
command takes a problem number, whether it supports `--silent`, what it asks for — is in
its index entry, one click along its name.

<!-- GEN:command-table -->
| Command | Aliases | Requires | Description |
|---------|---------|----------|-------------|
| [`!`](commands-index.md#command--sh-bash) | `sh`, `bash` | `contributor` | Run a shell command from the shell, returning its exit code. |
| [`?`](commands-index.md#command--help) | `help` | `reader` | List every command, or show detailed help for one command. |
| [`benchmark`](commands-index.md#command-benchmark) | — | `contributor` | Measure and record the execution time of the problem's solutions. |
| [`check-commands`](commands-index.md#command-check-commands) | — | `admin` | Report every command docstring that breaks the documented standard. |
| [`claude-api`](commands-index.md#command-claude-api) | — | `contributor` | Generate one of a problem's solution artifacts through the Claude API. |
| [`claude-batch`](commands-index.md#command-claude-batch) | — | `maintainer` | Bulk-tag a wave of problems in one Message Batches job, at half price. |
| [`claude-blog`](commands-index.md#command-claude-blog) | — | `maintainer` | Write (or flesh out) a topic article via the claude-euler-blogger skill. |
| [`claude-solve`](commands-index.md#command-claude-solve) | — | `contributor` | Run Claude Code over a problem's solution files, via a skill. |
| [`clear`](commands-index.md#command-clear-cls) | `cls` | `reader` | Clear the terminal screen and scrollback, then succeed. |
| [`compile-c`](commands-index.md#command-compile-c-compile) | `compile` | `contributor` | Compile every C solution for the problem into a runnable binary. |
| [`costs`](commands-index.md#command-costs) | — | `contributor` | Print what this session's AI tokens have cost, per model. |
| [`create-topic`](commands-index.md#command-create-topic) | — | `maintainer` | Seed a curated cross-cutting topic page. |
| [`echo`](commands-index.md#command-echo) | — | `reader` | Print the given text to the console, then succeed. |
| [`edit`](commands-index.md#command-edit-ed) | `ed` | `contributor` | Open a solution file in the web code editor. |
| [`evaluate`](commands-index.md#command-evaluate-eval) | `eval` | `contributor` | Evaluate a problem's solutions against its test cases. |
| [`gh-merge`](commands-index.md#command-gh-merge-merge) | `merge` | `maintainer` | List the open pull requests, or rebase-merge one onto master. |
| [`git-audit`](commands-index.md#command-git-audit-audit) | `audit` | `contributor` | Audit what git actually stores, across the whole tracked tree. |
| [`git-commit`](commands-index.md#command-git-commit-commit) | `commit` | `contributor` | Stage and commit the named targets — the one commit verb. |
| [`git-filter`](commands-index.md#command-git-filter-filter) | `filter` | `reader` | Report or wire the transparent encryption filter for `solutions/private`. |
| [`git-hooks`](commands-index.md#command-git-hooks-hooks) | `hooks` | `contributor` | Run the git pre-commit and (simulated) pre-push checks on demand. |
| [`git-identity`](commands-index.md#command-git-identity-identity) | `identity` | `contributor` | Configure your git identity and push credential from your GitHub login. |
| [`git-publish`](commands-index.md#command-git-publish-publish) | `publish` | `maintainer` | Publish changed files for named targets to the remote repository. |
| [`git-push`](commands-index.md#command-git-push-push) | `push` | `contributor` | Push the current branch to origin as yourself, then open its pull request. |
| [`git-reset`](commands-index.md#command-git-reset-reset) | `reset` | `reader` | Soft-reset your branch to origin/master — un-commit, keep every change. |
| [`git-status`](commands-index.md#command-git-status-status) | `status` | `reader` | Display the sync state between the local branch and origin/master. |
| [`git-sync`](commands-index.md#command-git-sync-sync) | `sync` | `reader` | Bring the local repository in sync with origin/master. |
| [`host-authorize`](commands-index.md#command-host-authorize) | — | `admin` | Mail the master key, sealed to one machine's public key — the off-host grant. |
| [`host-unlock`](commands-index.md#command-host-unlock) | — | `admin` | Take the mailed block from `host-authorize` and unlock this machine. |
| [`key-reconstruct`](commands-index.md#command-key-reconstruct) | — | `reader` | Unwrap the half you were sent, complete it from the repository, store the key. |
| [`key-rekey`](commands-index.md#command-key-rekey-rekey) | `rekey` | `admin` | Rotate the master key and re-issue it to every registered public key. |
| [`key-split`](commands-index.md#command-key-split) | — | `maintainer` | Send someone half the master key, sealed to their public key. |
| [`lint`](commands-index.md#command-lint) | — | `contributor` | Lint the problem's solution files, optionally auto-fixing them. |
| [`ls`](commands-index.md#command-ls) | — | `reader` | List the files in a problem's solution directory. |
| [`manage-config`](commands-index.md#command-manage-config) | — | `admin` | Show or update a managed configuration setting. |
| [`mark`](commands-index.md#command-mark-mark-solved) | `mark-solved` | `contributor` | Mark the current problem as solved — once its results confirm it. |
| [`msg`](commands-index.md#command-msg-messages) | `messages` | `reader` | Read and send messages: what is waiting for you, and what it asks you to do. |
| [`new`](commands-index.md#command-new) | — | `contributor` | Generate new solution and/or test-case files for the problem. |
| [`pause`](commands-index.md#command-pause) | — | `reader` | Wait for the user to press Enter before the block carries on. |
| [`pip-upgrade`](commands-index.md#command-pip-upgrade-upgrade) | `upgrade` | `admin` | Upgrade packages in the current venv for the given dependency groups. |
| [`problems`](commands-index.md#command-problems) | — | `reader` | Print a list of problems and their count. |
| [`progress`](commands-index.md#command-progress) | — | `reader` | Print overall progress through the Euler problems. |
| [`results`](commands-index.md#command-results) | — | `reader` | List the recorded results for a problem. |
| [`search`](commands-index.md#command-search-find) | `find` | `reader` | Search the solution stack for a case-insensitive regular expression. |
| [`show`](commands-index.md#command-show-open-view) | `open`, `view` | `reader` | Open a problem's documentation page, in a browser or the web viewer panel. |
| [`summary`](commands-index.md#command-summary) | — | `maintainer` | Refresh the solved/unsolved state from your Project Euler progress page. |
| [`sys-setup`](commands-index.md#command-sys-setup-install) | `install` | `admin` | Install or uninstall a system resource. |
| [`tags`](commands-index.md#command-tags) | — | `reader` | Report over the central tag vocabulary (`topics/tags.json`). |
| [`test-cases`](commands-index.md#command-test-cases) | — | `reader` | List a problem's test cases. |
| [`topic`](commands-index.md#command-topic) | — | `reader` | List a topic article's declared tags and what each one maps to. |
| [`topics`](commands-index.md#command-topics) | — | `reader` | List a problem's tags and the topic articles that cover them. |
| [`update-docs`](commands-index.md#command-update-docs) | — | `admin` | Rebuild the registry-generated blocks in the `docs/` guides and the README. |
| [`update-models`](commands-index.md#command-update-models) | — | `admin` | Refresh the model catalogue and its pricing. |
| [`update-tags`](commands-index.md#command-update-tags) | — | `contributor` | The glue for the double-entry tag graph. |
| [`update-usd-rate`](commands-index.md#command-update-usd-rate) | — | `maintainer` | Refresh the USD→EUR rate used to report API costs. |
| [`user`](commands-index.md#command-user) | — | `reader` | Show the solver user, the current identity, and whether it can decrypt. |
| [`user-authorize`](commands-index.md#command-user-authorize-authorize) | `authorize` | `maintainer` | Record someone's public key and send them half the master key. |
| [`users`](commands-index.md#command-users) | — | `admin` | Administer accounts on the authorization map + the auth service. |
| [`vault`](commands-index.md#command-vault) | — | `reader` | Encrypt this user's `id` + `env` at rest under a password-derived vault key. |
| [`version`](commands-index.md#command-version) | — | `reader` | Print the installed build version, plus live git detail of the clone. |
<!-- /GEN:command-table -->

> The table above is generated from the live command registry by the
> `update-docs` command. The same block stands on its own as
> [`commands-catalogue.md`](commands-catalogue.md) — the page the web front end
> renders beside the shell — and [`commands-index.md`](commands-index.md) carries
> each command's full usage.

---

## 4. Typical sessions

**Solve a problem** (see the [Solver Guide](solver-guide.md) for the full loop):

```bash
solver <<'EOF'
show 42     # open problem 42 in the solver-doc browser tab (and select it as the current problem)
pause       # derive/confirm insights (scratch scripts under the solution dir), then continue
new --tc    # create an empty test-case file for the current problem
new --py    # create a template Python solution file (p0042_s0.py)
pause       # implement solve() in the template, then continue
eval        # evaluate the solution against the test cases
pause       # record the answers in the test-case file, then continue
benchmark   # time the solution
mark        # mark the problem as solved
new --c     # create a template C solution file (p0042_s0.c)
pause       # translate the solution to C, then continue
benchmark   # time the C solution too
pause       # document your learnings in notes.html, then continue
EOF
```

Files are edited in place in the problem's solution directory; `commit` persists
them.

**Sweep a range of unsolved problems:**

```bash
solver <<'EOF'
loop {unsolved}[0:5]: { claude-solve {loop.number} solve }
EOF
```

---

## 5. AI assistance

Two complementary AI paths are wired into the shell (both require the `ai`
dependency group;
API requires `ANTHROPIC_API_KEY` in `~/.euler/env`;
Claude Code requires authentication in the CLI `claude /login`):

- **`claude-api <target>`** — a single templated Claude API call that writes one
  artifact: `py` / `c` (a solution), `notes` (the write-up), or `test-cases`. It
  is fast and cheap, and `costs` tracks its token spend, but the AI neither runs
  nor verifies its output — that happens afterwards in the script.
- **`claude-solve <n> <action>`** — full Claude Code working directly on a
  problem's solution files: it runs `solver` commands, edits files, evaluates,
  benchmarks, and iterates. The actions are `review` and `solve` (e.g.
  `claude-solve 42 solve`). Heavier and slower, it is meant for the harder job.
  `! claude <prompt>` drops into an interactive Claude Code session in the repo.

The goal is to deepen understanding, not skip it: generate alternatives *after*
you have solved a problem, or translate your Python into C for comparison.

---

## 6. Sessions, history, and config

- **Per-user state.** The shell runs as a resolved *identity* and keeps that
  user's state under `.state/<slug>/` (command history, session log, last active
  problem). On a local terminal the identity is your OS login name (granted only
  to the checkout's owner); in the web front end it is your signed-in account,
  vouched by a one-time shell ticket the server redeems with the auth service at
  startup (see docs/web-server-guide.md). Each user gets their own history
  and last problem.
- **History** persists across sessions, per user; auto-suggest offers your past lines.
- **Last problem** is remembered per user: every shell — interactive, a
  `cmdline` block, or piped stdin — restores the problem you last worked on when
  it starts, and records it as you switch.
- **`-s` / `--save`** tees the interactive session (typed input + console output)
  to the session log.
- **`manage-config`** shows or sets the managed settings (the solution timeouts
  and `ecb_usd_rate`); they persist to `solver/config.json`.
- **`! <cmd>`** runs a bash command in the current problem's solution directory
  (`! sh` / `! py` drop into a shell / Python interpreter).

---

## 7. Key Exchange

Solutions under `solutions/private/` are encrypted at rest (in accordance with
[Project Euler's guidelines](https://projecteuler.net/about#publish)) by a
**transparent git clean/smudge filter** — they are ciphertext in git but plaintext
in your working tree. You only need keys if you
want to collaborate on, or study, those files; `solutions/public/` is plaintext and
needs nothing. The mechanics of the filter itself are covered in the
[Git Filter Guide](gitfilter-guide.md); this section covers the key material.

### The two keys

```
~/.euler/id             - your X25519 private key (PKCS8 PEM; machine-local 0600, outside the repo)
~/.euler/enc-key.json   - { "verify": <check ciphertext>, <your-public-key-hex>: <master key wrapped for it> }
```

`~/.euler` is a machine-local secrets dir — a sibling dot-directory named for the repo
(`~/euler` → `~/.euler`) — kept **outside** the checkout so secrets never sit in the work
tree. Both files are yours alone; nothing about key material is committed or pushed. The
private key carries no passphrase (its `0600` permissions, or the per-user vault, are its
protection), and the enc-key file is inert without it.

There is a single 32-byte **master key**, shared by everyone who may read the private
solutions and never stored in the clear: each holder keeps their own copy, wrapped to their
X25519 public key with an ephemeral ECDH exchange (HKDF-SHA256 + ChaCha20-Poly1305). Loading
it reads the private key, unwraps the entry, and proves it against the `verify` ciphertext
before use.

### Gaining access (new user)

```bash
solver "user"        # creates ~/.euler/id, prints your public key, and files a request
```

That request goes to the maintainers over the message spool — you do not have to find anyone.
When one of them issues the key, it arrives as a message:

```bash
msg list                 # the reply is there
msg act <message-id>     # writes ~/.euler/enc-key.json, verified before anything is written
```

`solver "user"` then reports `✓ can encrypt/decrypt`, and the private solutions decrypt in
place. **Rotating your own key needs nobody**: `solver "user --regen"` re-wraps the master key
to your new key itself. Only a machine that cannot load the master key at all files a request.

That grant is a **split**, not a copy of the key. `user-authorize` (or `key-split <you>`
directly) halves the master key: one half already sits on the host your instance runs on
(`/etc/euler/share.json`), and the other is sealed to your public key and sent to you as a
message. `msg act` on it runs `key-reconstruct`, which unwraps your half, puts the two
together, proves the result, and writes `~/.euler/enc-key.json`.

No single piece is enough: the half on the host is a random point that says nothing about the
key, and the half you were sent needs your private key to open it *and* that host to complete
it. On a machine away from the host there is no half to complete, so the grant is
`host-authorize` instead — a sealed key by e-mail, which you install with `host-unlock`. The
mathematics and both flows are in the [Secret Sharing Guide](secret-sharing-guide.md).

### Studying the solutions

Once you have master-key access the private files are plaintext in your working tree —
just open them. Or use `show N` to view any problem's statement, notes, and results in
the browser (the web front end at `$EULER_BASE_URL`); every `show` reuses one dedicated
browser tab (`solver-doc`), so browsing through problems never piles up tabs.

---
