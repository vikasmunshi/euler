# Command Index

The complete reference for every shell command — name, aliases, flags, a one-line
description, the exact usage string, and the command's full description (its
function docstring). This is the long form of the
[User Guide](user-guide.md)'s command catalogue, which links here per command.

The per-command sections below are **generated from the live command registry**
by the `update-docs` command — do not edit them by hand. To change a command's
detailed description, edit its function docstring in the source and run
`update-docs`; also run it after changing any command's name, alias, help text,
or usage.

## Legend

Each command entry opens with an **availability** line — `profiles: …`. *Profiles*
are those whose permissions satisfy the command's `requires=` grants under
`authorizations.json` — reported from the live registry (see the generated
[`authorizations.md`](authorizations.md) audit table). Authorization is by profile
only; the channel (terminal / web) is not an axis. `requires` is mandatory, so
every command declares its floor. See the
[web server guide](web-server-guide.md) for the authorization model.

A command's *flags* line lists the behaviours marked by these glyphs (the same
ones shown after a command's help by `?`):

| glyph | meaning                                                         |
|-------|-----------------------------------------------------------------|
| `§`   | requires the workspace lock to be acquired or inherited         |
| `↻`   | the variable `problem` is read from the workspace on completion |
| `⊘`   | refuses while the workspace is checked out                      |
| `⚑ `  | checkout on start, checkin on completion                        |
| `»`   | supports `--silent` to suppress its incidental output           |

In a usage string: `<required>`, `[optional]`, `a|b|c` is a choice, `key=value`
sets a named parameter, `--flag` / `--no-flag` toggle a boolean, and `...` marks
a parameter that accepts repetition.

---

### Commands

<details>
<summary>command catalogue (click to expand) — each name jumps to its entry below</summary>

<!-- GEN:command-summary -->
| Command | Aliases | Description |
|---------|---------|-------------|
| [`!`](#command--sh-bash) | `sh`, `bash` | Run a bash command. |
| [`?`](#command--help) | `help` | List commands or show help for a specific command. |
| [`benchmark`](#command-benchmark) | — | Benchmark solutions to given/current problem. ❏ » |
| [`claude-api`](#command-claude-api) | — | Generate specified target using Claude API. ❏ |
| [`claude-solve`](#command-claude-solve) | — | Launch the Claude Euler Solver skill. ❏ |
| [`clear`](#command-clear-cls) | `cls` | Clear the screen. |
| [`compile-c`](#command-compile-c-compile) | `compile` | Build all C source files for given/current problem. ❏ » |
| [`costs`](#command-costs) | — | Display total cost of AI API tokens consumed in session. |
| [`echo`](#command-echo) | — | Print text. |
| [`edit`](#command-edit-ed) | `ed` | Open a solution file in the web code editor. ❏ » |
| [`evaluate`](#command-evaluate-eval) | `eval` | Evaluate solutions to given/current problem. ❏ |
| [`gh-pr`](#command-gh-pr-pr) | `pr` | Pull requests: list | merge (walk the queue). » |
| [`git-audit`](#command-git-audit-audit) | `audit` | Audit the whole tracked tree: private encrypted, no compiled binaries. » |
| [`git-commit`](#command-git-commit-commit) | `commit` | Commit a problem's solution directory and progress, optionally resetting to origin/master. ❏ » |
| [`git-commit-amend`](#command-git-commit-amend-amend) | `amend` | Amend the last unpushed commit with a problem's current changes. ❏ » |
| [`git-filter`](#command-git-filter-filter) | `filter` | Wire the git encryption filter: status | install. |
| [`git-hooks`](#command-git-hooks-hooks) | `hooks` | Run pre-commit hook and simulated pre-push hook. » |
| [`git-identity`](#command-git-identity-identity) | `identity` | Sign in to GitHub (gh) and set this clone's git identity from it. |
| [`git-publish`](#command-git-publish-publish) | `publish` | Push targets (keys|scripts|solutions|solver) to remote. » |
| [`git-push`](#command-git-push-push) | `push` | Push the current branch to origin and open a pull request onto master. » |
| [`git-status`](#command-git-status-status) | `status` | Display sync state between local and origin/master. |
| [`git-sync`](#command-git-sync-sync) | `sync` | Bring the local repository in sync with origin/master. |
| [`key-reconstruct`](#command-key-reconstruct) | — | Recover master key from shares. |
| [`key-rekey`](#command-key-rekey-rekey) | `rekey` | Rotate the enc key and re-wrap to users. |
| [`key-split`](#command-key-split) | — | Split master key into shares (n-of-m secret sharing). |
| [`lint`](#command-lint) | — | Lint current problem, auto-fix with --auto-fix. ❏ » |
| [`ls`](#command-ls) | — | List the solutions dir for given/current problem. ❏ » |
| [`manage-config`](#command-manage-config) | — | Manage configuration settings. |
| [`mark`](#command-mark-mark-solved) | `mark-solved` | Mark the current problem as solved, after checking. ❏ » |
| [`new`](#command-new) | — | Generate new solution/test-case file for a problem. ❏ » |
| [`pause`](#command-pause) | — | Pause for user confirmation to continue. |
| [`pip-upgrade`](#command-pip-upgrade-upgrade) | `upgrade` | Upgrade dependency group (all|ai|core|dev|solutions|show). |
| [`problems`](#command-problems) | — | Show list of problems (all|solved|unsolved). |
| [`progress`](#command-progress) | — | Print progress statistics about Euler problems. |
| [`results`](#command-results) | — | list the results for the problem. ❏ |
| [`search`](#command-search-find) | `find` | Find content in the stack. |
| [`show`](#command-show-open-view) | `open`, `view` | Open problem/file in a browser or the web viewer panel. ❏ » |
| [`summary`](#command-summary) | — | Parse .progress.html into problems.json. » |
| [`sys-setup`](#command-sys-setup-install) | `install` | Installs or uninstalls system resources. |
| [`test-cases`](#command-test-cases) | — | list the test cases for the problem. ❏ |
| [`update-docs`](#command-update-docs) | — | Regenerate the generated sections of the docs/ guides. » |
| [`update-models`](#command-update-models) | — | Update Model enum, pricing, and USD→EUR rate. » |
| [`user`](#command-user) | — | Show public key & enc-key access; --regen for new key-pair. |
| [`user-authorize`](#command-user-authorize-authorize) | `authorize` | Authorise another public key (hex) to access the enc key. |
| [`users`](#command-users) | — | Administer accounts + invite requests (re-executes the admin CLI under sudo). |
| [`vault`](#command-vault) | — | Manage the per-user secrets vault: status | init | unlock | change-password. |
| [`version`](#command-version) | — | Show the running solver build version. |

*Legend: ❏ takes an optional problem number (defaults to the current problem) · » supports `--silent`.*
<!-- /GEN:command-summary -->

</details>

---

<!-- GEN:command-index -->
#### Command: `!` (`sh`, `bash`)

Run a bash command.
* profiles: admin, maintainer, contributor

```
! <command> [args]...
! sh → escape to a bash shell.
! py → escape to a python interpreter.
```

```text
Run a shell command from the shell, returning its exit code.

Three forms escape into an *interactive* session that takes over the terminal:

    `! sh` / `! bash`       an interactive bash subshell, in the solution dir
    `! py` / `! python`     an interactive Python interpreter, in the repo root
    `! claude [prompt]`     Claude Code, in the repo root

Any other command (`! ls`, `! git diff`, …) runs non-interactively in the
current problem's solution directory — so paths are relative to that problem's
files — with its output streamed through the shell (so `solver -s` can log it).
After the command finishes, the problem specials are refreshed (↻) in case it
changed the files.

Aliased as `sh` and `bash`, so `sh <command>` is shorthand for `! <command>`.
```

---

#### Command: `?` (`help`)

List commands or show help for a specific command.
* profiles: admin, maintainer, contributor, reader

```
? [command]
```

```text
List every command, or show detailed help for one command.

With no argument, prints a three-column table (command, aliases,
description) of all registered commands; the `»` glyph in a description marks
a command that supports --silent, as noted in the panel subtitle.

With a command name or alias, prints a panel for just that command: its
description (with a trailing `»` glyph expanded to a full sentence about
--silent), its aliases, and its usage. Returns non-zero if the named command
is unknown.

Aliased as `help`.
```

---

#### Command: `benchmark`

Benchmark solutions to given/current problem.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
benchmark
[problem=<n>] (default current)
[all|dev|main|extra ...]
[clean=false|--no-clean]
[timeout=<float>|none] (default None)
[disable_timeout=true|--disable-timeout]
[lang=*|py|c] (default *)
[solution_index=<int>|none] (default None)
[reset=true|--reset]
[verbose=true|--verbose]
[silent=true|--silent]
```

```text
Measure and record the execution time of the problem's solutions.

Like `eval`, runs every solution against the chosen test-case categories, but
always **records** the timings to `results.json` and repeats each case an
adaptive number of times (see "Repeats") instead of running once. Run `eval`
first to confirm correctness, then `benchmark` to measure; categories default
to all three ('dev', 'main', 'extra').

Repeats:
    `benchmark` does not take a `runs` argument — it passes `runs=None` to the
    evaluator, which makes `load_test_cases` (`core/test_cases.py`) choose the
    repeat count **per test-case category** from the previously recorded
    timings::

        runs = clamp(round(21 / slowest_prior_average), 1, 21)

    where `slowest_prior_average` is the largest recorded average (seconds per
    run) among prior *correct* results for that category and the solutions
    being benchmarked. So each case is repeated ~21 times when it runs in well
    under a second and scales down toward a single run as it gets slower —
    keeping the per-category wall time bounded at roughly 21s — clamped to the
    1..21 range. With no prior correct result recorded for a category the
    count is 1: the first benchmark establishes a one-run baseline, and later
    benchmarks use it to repeat the fast cases and average out noise. Passing
    `disable_timeout` overrides this and forces a single run.

Args:
    problem:            The `problem` to benchmark.
    *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                        (which expands to all three). Defaults to all three if omitted.
    clean:              When False, reuse up-to-date build output from previous compilations.
                        Defaults to True.
    timeout:            Per-run timeout in seconds for solution execution. If None, uses the
                        default timeout. Defaults to None.
    disable_timeout:    If True, disables the timeout for solution execution and forces a single
                        run (bypassing the adaptive repeat count above). Defaults to False.
    lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
    solution_index:     Specific solution index to evaluate.
                        If provided, only this solution index will be evaluated.
                        If None, all solutions will be evaluated. Defaults to None.
    reset:              If True, replace any existing persisted results with this run on a
                        clean completion. If the benchmark is interrupted, existing results
                        are preserved untouched. Defaults to False (results are merged with
                        existing records as a running average).
    verbose:            If True, prints error information during evaluation. Defaults to False.
```

---

#### Command: `claude-api`

Generate specified target using Claude API.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)

```
claude-api <c|py|doc|notes|test-cases>
[problem=<n>] (default current)
[force=true|--force]
[major=true|--major]
[model=claude-fable-5|claude-opus-4-8|claude-opus-4-7|claude-opus-4-6|claude-opus-4-5|claude-sonnet-4-6|claude-sonnet-4-5|claude-sonnet-5|claude-haiku-4-5|none] (default None)
```

```text
Generate AI-based content for the specified target.

Args:
    problem: The `problem` to generate for; defaults to the current problem.
    target: The type of content to generate ('c' or 'py' for code, 'doc' to refresh in-source
            docs, 'notes' for documentation, 'test-cases' for test cases).
    major:  Whether this is after a major change (e.g. template or instruction change).
    force:  Whether to force generation even if the target already exists.
    model:  The AI model to use for generation; defaults to Opus for code, docs and notes, Sonnet for test cases.

Prints the USD/EUR cost of the call and returns non-zero if the generator reports failure.
```

---

#### Command: `claude-solve`

Launch the Claude Euler Solver skill.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)

```
claude-solve <solve|review>
[problem=<n>] (default current)
[additional_prompt=<str>] (default '')
```

```text
Run Claude Code over a problem's solution files via the claude-euler-solver skill.

Launches Claude Code headless against the given problem's solution directory,
runs the requested action, and streams a
live-updating Markdown summary back into the shell, ending with a footer of
turns / duration / cost. Heavier and slower than `claude-api` — it actually
runs `solver` commands, edits files, evaluates, and iterates. Needs the
`claude` CLI on PATH and an `ANTHROPIC_API_KEY`.

Args:
    problem:            The `problem` to work on; defaults to the current problem.
    action:             What to do — 'solve' (write and verify a Python
                        solution, translate it to C, then document and
                        summarise), or 'review' (audit an existing solution
                        for C↔Python parity, in-source docs, and notes.html).
    additional_prompt:  Extra free-text instructions appended to the skill
                        invocation. Defaults to empty.
```

---

#### Command: `clear` (`cls`)

Clear the screen.
* profiles: admin, maintainer, contributor, reader

```
clear
```

```text
Clear the terminal screen and scrollback, then succeed.

A convenience wrapper over the console's clear; equivalent to the shell
`clear`. Takes no arguments. Aliased as `cls`.
```

---

#### Command: `compile-c` (`compile`)

Build all C source files for given/current problem.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
compile-c
[problem=<n>] (default current)
[clean=false|--no-clean]
[silent=true|--silent]
```

```text
Compile every C solution for the problem into a runnable binary.

Builds each `.c` file in `problem.solution_dir/` (linking the runner harness)
so it can be evaluated and benchmarked; reports per-file success or the compiler
error. `eval` and `benchmark` invoke this for you, so you rarely call it directly.

Args:
    problem:            The `problem` to compile.
    clean:              When False, reuse up-to-date build output from previous compilations.
                        Defaults to True.
```

---

#### Command: `costs`

Display total cost of AI API tokens consumed in session.
* profiles: admin, maintainer, contributor

```
costs
[ecb_usd_rate=<float>] (default 1.1467)
```

```text
Print the total cost of all AI tokens consumed in the session so far, broken down per model,
or a "No charges so far." notice if nothing has been consumed. Always returns EXIT_OK.

Totals the charges across all models in "consumed_tokens" using each model's published USD
price per million tokens (with cache writes at 1.25x and cache reads at 0.10x the input rate),
then converts to EUR using "ecb_usd_rate".

Args:
    ecb_usd_rate: conversion rate (1 € = N $). Defaults to 'config.ecb_usd_rate'.
```

---

#### Command: `echo`

Print text.
* profiles: admin, maintainer, contributor, reader

```
echo <text>
```

```text
Print the given text to the console, then succeed.

The arguments are joined with single spaces and printed literally (no rich
markup interpretation). Handy in command blocks to annotate progress or to
surface a variable, since `{...}` references are substituted before the
command runs — e.g. `echo solved {len(solved)} problems`.
```

---

#### Command: `edit` (`ed`)

Open a solution file in the web code editor.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
edit <filename>
[problem=<n>] (default current)
[silent=true|--silent]
```

```text
Open *filename* from *problem*'s solution directory in the web code editor.

The counterpart to `show` (which opens the rendered problem): *problem* defaults
to the current problem, and *filename* completes to the files `ls` lists. The
file must already exist — run `new` to create a solution first. Channel-aware,
like `show` (the channel is the resolved subject's):

- **web** — emits an `OSC 5379` `edit` sequence (`edit;<NNNN>;<token>;<relpath>`)
  that the xterm.js page rides over the PTY → WebSocket pipe to point the app
  shell's left pane at the file's editor (`<origin>/edit/solutions/NNNN/<relpath>`).

- **terminal** — opens that editor URL in the named browser tab "solver-edit"
  (via `browser open-in-tab`); errors early if the `browser` command is
  unavailable.

Arguments:
    problem:  The problem owning the file; defaults to the current problem.
    filename: The solution-directory file to edit (as `ls` lists it).
```

---

#### Command: `evaluate` (`eval`)

Evaluate solutions to given/current problem.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)

```
evaluate
[problem=<n>] (default current)
[all|dev|main|extra ...]
[clean=false|--no-clean]
[timeout=<float>|none] (default None)
[disable_timeout=true|--disable-timeout]
[lang=*|py|c] (default *)
[runs=<int>] (default 1)
[show=true|--show]
[solution_index=<int>|none] (default None)
[verbose=true|--verbose]
```

```text
Evaluate solutions against test cases.

Args:
problem:            The `problem` to evaluate.
*categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                    (which expands to all three). Defaults to 'dev', 'main' if omitted.
clean:              When False, reuse up-to-date build output from previous compilations.
                    Defaults to True.
timeout:            Timeout in seconds for solution execution. If None, uses default timeout.
                    Defaults to None.
disable_timeout:    If True, disables timeout for solution execution. Defaults to False.
                    If True, only one run will be performed for each solution.
lang:               Language to evaluate. Accepts '*', 'py' or 'c'. Defaults to '*'.
runs:               Number of times to run each solution per test case (useful for timing).
                    Defaults to 1.
show:               If True, appends '--show' to the arguments passed to each solution;
                    defaults to False.
solution_index:     Specific solution index to evaluate.
                    If provided, only this solution index will be evaluated.
                    If None, all solutions will be evaluated. Defaults to None.
verbose:            If True, prints error information during evaluation. Defaults to False.
```

---

#### Command: `gh-pr` (`pr`)

Pull requests: list | merge (walk the queue).
* profiles: admin, maintainer
* » supports `--silent`

```
gh-pr
[action=list|merge] (default list)
[silent=true|--silent]
```

```text
List the open pull requests, or walk them one at a time to squash-merge.

`list` (the default) shows what is waiting: number, title, branch. `merge` walks
the open pull requests interactively — per request **merge** (squash onto master),
**skip**, or **quit** — the same shape as `users process-requests`. Merging one is
how a collaborator's `user/<slug>` branch lands on master; their next `git-sync`
then rebases the squashed commit away and prunes the merged branch.

A pull request touching anything outside `solutions/` is refused, and that gate
is what makes this a maintainer's command rather than an admin's: merging a
branch that carries solutions is reviewing solutions, but a branch that also
edits the framework, the scripts, or the keys is asking for something else
entirely. Merge those on GitHub, as an admin who has read them.

Args:
    action: 'list' (default) or 'merge' (walk the open queue interactively).

Aliased as `pr`.
```

---

#### Command: `git-audit` (`audit`)

Audit the whole tracked tree: private encrypted, no compiled binaries.
* profiles: admin, maintainer, contributor
* » supports `--silent`

```
git-audit
[details=true|--details]
[silent=true|--silent]
```

```text
Audit what git actually stores, across the whole tracked tree.

Two checks, each reading every tracked blob straight from the object store (so
no smudge filter runs): every file under `solutions/private` is stored as
ciphertext, and no file anywhere is a compiled binary. Both run even when the
first fails; a non-zero exit means one of them found something.

This is the periodic full sweep, and it takes ~25s. The git hooks run the same
two checks scoped to the blobs at hand — `git-hooks` (pre-commit) audits what
you staged, pre-push audits what the push would add — so committing and pushing
stay fast. The cost of that scoping is that neither hook re-examines history
already on origin; this is the command that does.

Args:
    details: When True, lists every file audited. When False (default), reports
             counts only. Offenders are listed by path either way.

Aliased as `audit`.
```

---

#### Command: `git-commit` (`commit`)

Commit a problem's solution directory and progress, optionally resetting to origin/master.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
git-commit
[problem=<n>] (default current)
[message=<str>] (default '')
[reset=true|--reset]
[silent=true|--silent]
```

```text
Stage and commit the problem's solution directory.

Adds everything under `problem.solution_dir`, plus `solutions/problems.json`
    (the progress file `mark` rewrites), and commits just those
    — the routine "save my progress" step.

Args:
    problem:        The problem to commit.
    message:        The commit message. When empty (the default) and `reset` is not
                    set, folds into the last unpushed commit if there is one to amend
                    (see `git-commit-amend`); otherwise commits fresh under the
                    default message "solution for pNNNN".
    reset:          When True, first soft-reset to `origin/master` so the new commit
                    squashes all local commits into a single checkpoint (working
                    tree untouched). Defaults to False. Suppresses the empty-message
                    amend, since squashing to one checkpoint is the opposite intent.
Aliased as `commit`.
```

---

#### Command: `git-commit-amend` (`amend`)

Amend the last unpushed commit with a problem's current changes.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
git-commit-amend
[problem=<n>] (default current)
[silent=true|--silent]
```

```text
Fold this problem's current changes into the last commit, message unchanged.

The "I forgot something" step after `git-commit`: stages everything under
    `problem.solution_dir` plus `solutions/problems.json` and amends HEAD with
    `--no-edit`, so the checkpoint absorbs the fix instead of growing a
    "fix typo" commit behind it.

Refused once HEAD is on origin — amending rewrites the commit, and a rewritten
    commit that is already pushed only lands again through a force-push, so
    `git-commit` is the honest step there. A no-op, not a failure, when nothing
    under those paths has changed.

Args:
    problem:        The problem whose changes are folded into HEAD.

Aliased as `amend`.
```

---

#### Command: `git-filter` (`filter`)

Wire the git encryption filter: status | install.
* profiles: admin, maintainer, contributor, reader

```
git-filter
[action=status|install] (default status)
```

```text
Report or wire the transparent encryption filter for `solutions/private`.

`status` shows the filter wiring and whether this session can unwrap the
master key. `install` verifies master-key access first (refusing cleanly
without it — nothing is wired), registers the clean/smudge filter in this
clone's git config, and re-checks out `solutions/private` so existing
ciphertext decrypts in place. The explicit form of what `git-sync` runs
automatically after a pull that delivers key access — use it when access
arrived some other way, e.g. right after `key-reconstruct` from shares.

Args:
    action: 'status' (default) or 'install'.

Aliased as `filter`.
```

---

#### Command: `git-hooks` (`hooks`)

Run pre-commit hook and simulated pre-push hook.
* profiles: admin, maintainer, contributor
* » supports `--silent`

```
git-hooks
[silent=true|--silent]
```

```text
Run the git pre-commit and (simulated) pre-push checks on demand.

Runs the same checks the git hooks run — the pre-commit hook (whitespace
fixes, flake8, mypy) and a simulation of the pre-push hook — so you can
verify your changes will pass before committing or pushing. Reports the
combined pass/fail in the exit code.

Aliased as `hooks`.
```

---

#### Command: `git-identity` (`identity`)

Sign in to GitHub (gh) and set this clone's git identity from it.
* profiles: admin, maintainer, contributor

```
git-identity
```

```text
Configure your git identity and push credential from your GitHub login.

The one-time setup before `git-push`: runs `gh auth login` when you are not yet
signed in (interactive device flow — works in the web shell), makes gh the git
credential helper (`gh auth setup-git`), and sets this clone's `user.name` /
`user.email` from your GitHub profile, so your commits are authored and pushed
as **you**, never as a service identity.

Aliased as `identity`.
```

---

#### Command: `git-publish` (`publish`)

Push targets (keys|scripts|solutions|solver) to remote.
* profiles: admin
* » supports `--silent`

```
git-publish
[keys|scripts|solutions|solver ...]
[dry_run=true|--dry-run]
[silent=true|--silent]
```

```text
Publish changed files for named targets to the remote repository.

Args:
    targets: Scopes of files to publish — one or more of 'keys', 'scripts', 'solutions', or 'solver'.
             Defaults to 'solutions'.
    dry_run: Print the push and pull-request commands instead of running them.  Defaults to False.

Raises:
    ValueError: If any target is not one of the accepted values.
```

---

#### Command: `git-push` (`push`)

Push the current branch to origin and open a pull request onto master.
* profiles: admin, maintainer, contributor
* » supports `--silent`

```
git-push
[force=true|--force]
[pr=false|--no-pr]
[silent=true|--silent]
```

```text
Push the current branch to origin as yourself, then open its pull request.

In a per-user clone the current branch is `user/<slug>`, pushed with your own
GitHub identity — `git-identity` is the one-time setup. Landing work on master
is a maintainer's `gh-pr merge`, never a direct push: pushing master requires
the `admin` floor, and force-pushing it is always refused.

The PR is the second half of the push: an unreviewed branch on origin is not
work anyone has been asked for. It is skipped on master (nothing to merge into
itself) and on a branch level with origin/master (nothing to review), and a
branch that already has one open keeps it.

Args:
    force: Push with `--force-with-lease` — needed after `git-sync` rebased your
           branch onto a moved origin/master. Refused on master.
    pr:    Open a pull request onto master after a successful push. Defaults to
           True; `--no-pr` pushes and stops there.
```

---

#### Command: `git-status` (`status`)

Display sync state between local and origin/master.
* profiles: admin, maintainer, contributor, reader

```
git-status
[details=true|--details]
```

```text
Display the sync state between the local branch and origin/master.

Args:
    details:    When True, lists every differing file and uncommitted change.
                When False (default), shows file counts only.
```

---

#### Command: `git-sync` (`sync`)

Bring the local repository in sync with origin/master.
* profiles: admin, maintainer, contributor, reader

```
git-sync
[dry_run=true|--dry-run]
```

```text
Bring the local repository in sync with origin/master.

On a per-user clone (branch `user/<slug>`) this is the pull flow: fetch
origin/master and merge/rebase it into your branch — bringing in merged work
and, notably, `keys/enc-key.json`. When that pull first delivers master-key
access for your key, the git filter is wired automatically and the private
solutions decrypt in place.

Stale remote-tracking refs are pruned as part of the fetch, so a branch deleted
when its pull request merged stops shadowing the branch you push next.

Args:
    dry_run: Print the sync commands instead of running them. Defaults to False.
```

---

#### Command: `key-reconstruct`

Recover master key from shares.
* profiles: admin, maintainer, contributor, reader

```
key-reconstruct
[threshold=<int>] (default 2)
```

```text
Prompt for `threshold` shares, reconstruct the master key, and store it wrapped to this user.
```

---

#### Command: `key-rekey` (`rekey`)

Rotate the enc key and re-wrap to users.
* profiles: admin

```
key-rekey
```

```text
Rotate to a new master key (proof-of-possession), re-wrap to all users, and renormalise blobs.

Because the git filter is deterministic, every committed blob depends on the master key, so a
rotation re-encrypts the tracked private files via `git add --renormalize`.
```

---

#### Command: `key-split`

Split master key into shares (n-of-m secret sharing).
* profiles: admin

```
key-split
[num_shares=<int>] (default 3)
[threshold=<int>] (default 2)
```

```text
Print `num_shares` Shamir shares of the current master key (threshold needed to reconstruct).
```

---

#### Command: `lint`

Lint current problem, auto-fix with --auto-fix.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
lint
[problem=<n>] (default current)
[auto_fix=true|--auto-fix]
[silent=true|--silent]
```

```text
Lint the problem's solution files, optionally auto-fixing them.

Checks the current problem's solution files for style and quality issues
(flake8, plus the configured checks). Reports any findings and reflects them
in the exit code.

Args:
    problem:    The `problem` to lint; defaults to the current problem.
    auto_fix:   When True, attempt to fix issues in place with autoflake
                (remove unused imports/variables), autopep8 (style), and
                isort (import order), then re-check. When False (default),
                only report.
```

---

#### Command: `ls`

List the solutions dir for given/current problem.
* profiles: admin, maintainer, contributor, reader
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
ls
[problem=<n>] (default current)
[silent=true|--silent]
```

```text
This function lists all files found recursively in the solution directory of a
given problem while displaying their canonical paths and file sizes. The files
are shown in sorted order for easy navigation.

Args:
    problem (Problem): The problem instance containing the solution directory.
```

---

#### Command: `manage-config`

Manage configuration settings.
* profiles: admin

```
manage-config
[param=all|timeout_multiple|timeout_single|ecb_usd_rate] (default all)
[value=<float>|none] (default None)
```

```text
Show or update a managed configuration setting.

The managed settings persist to `solver/config.json` and override the
defaults in `config.py`: `timeout_single` / `timeout_multiple` (solution
timeouts in seconds for a single run and for repeated runs), and
`ecb_usd_rate` (the rate `costs` uses).

Args:
    param:  Which setting to act on; 'all' (default) prints every setting.
    value:  When given, the new value to assign to `param` (coerced to the
            setting's type and saved). When omitted, the current value of
            `param` is printed instead.
```

---

#### Command: `mark` (`mark-solved`)

Mark the current problem as solved, after checking.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
mark
[problem=<n>] (default current)
[silent=true|--silent]
```

```text
Mark the current problem as solved — once its results confirm it.

Records the current problem as solved (with today's date) in
`problems.json`, the same state `summary` maintains, so `{solved}`,
`progress`, and `solved` reflect it without re-importing the progress page.

It only proceeds after checking the recorded results: there must be a
selected problem, its `test_cases.json` must have a `main` case with an
answer, and `results.json` must contain a `correct` verdict for that `main`
case. Run `benchmark` (which records results) first; a problem already
marked solved is left unchanged.

Aliased as `mark-solved`.

Args:
    problem:    The `problem` to mark solved; defaults to the current problem.
```

---

#### Command: `new`

Generate new solution/test-case file for a problem.
* profiles: admin, maintainer, contributor
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
new
[problem=<n>] (default current)
[py=true|--py]
[c=true|--c]
[tc=true|--tc]
[silent=true|--silent]
```

```text
Generate new solution and/or test-case files for the problem.

Solution files are named from the problem number and the next free solution
index (e.g. "p0001_s0.py", "p0001_s1.py") and are created from the boilerplate
template with the problem information substituted; Python files are made
executable (mode 0o755).

Args:
    problem:    The `problem` to create files for; defaults to the current problem.
    py: Create a Python solution file. Defaults to False.
    c:  Create a C solution file (one per existing Python solution lacking a
        matching ".c"). Defaults to False.
    tc: Create an empty test-cases file instead of solution files, unless one
        already exists. Defaults to False.

With neither `py` nor `c` given (and `tc` False), both a Python and a C file
are created.
```

---

#### Command: `pause`

Pause for user confirmation to continue.
* profiles: admin, maintainer, contributor, reader

```
pause
```

```text
Pause the program execution until the user presses Enter.
```

---

#### Command: `pip-upgrade` (`upgrade`)

Upgrade dependency group (all|ai|core|dev|solutions|show).
* profiles: admin

```
pip-upgrade
[all|ai|core|dev|solutions|show ...]
```

```text
Upgrade packages in the current venv for the given dependency groups.

Groups are defined in pyproject.toml:   'core' for project.dependencies,
                                        'ai', 'dev', 'solutions', 'show' for optional-dependencies,
                                        'all' to upgrade everything.
                                        Defaults to 'all'.

Args:
    groups: One or more group names, or 'all'.
```

---

#### Command: `problems`

Show list of problems (all|solved|unsolved).
* profiles: admin, maintainer, contributor, reader

```
problems
[which=all|solved|unsolved] (default all)
```

```text
Print a list of problems and their count.

Args:
    which:  Which set to list — 'all' (default) every known problem,
            'solved' the problems with a recorded answer, or 'unsolved'
            those without. Mirrors the `{problems}` / `{solved}` /
            `{unsolved}` shell variables.
```

---

#### Command: `progress`

Print progress statistics about Euler problems.
* profiles: admin, maintainer, contributor, reader

```
progress
```

```text
Print overall progress through the Euler problems.

Shows a bar of solved vs. unsolved problems, the solved count and
percentage of the total known problems, and the next problem to solve (the
lowest-numbered unsolved one). Reads the state maintained by `summary`; run
`summary` first if your progress looks out of date.
```

---

#### Command: `results`

list the results for the problem.
* profiles: admin, maintainer, contributor, reader
* ❏ takes an optional problem number (defaults to the current problem)

```
results
[problem=<n>] (default current)
[all|dev|main|extra ...]
```

```text
List the results for a given problem.
Args:
    problem:            The `problem` to list `results` for. This is used to locate the `results` file.
    *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                        (which expands to all three). Defaults to all three if omitted.

Returns:
    int: Exit code indicating the completion status of the operation.
```

---

#### Command: `search` (`find`)

Find content in the stack.
* profiles: admin, maintainer, contributor, reader

```
search <query>
[*|py|c|html|json ...]
[scope=problems|solved] (default solved)
```

```text
Search the solution stack for a case-insensitive regular expression.

For every problem in scope, each matching stack file is read (decrypted as
needed) and scanned line by line; every matching line is printed as
'<stack-dir>/<file>:<line> <text>' with the matched substring highlighted.
A blank line separates the matches of one problem from the next.

Args:
    query:  Regular expression to search for, matched case-insensitively
            against each line ('re.search', so it need not match the whole
            line).
    *files: File extensions to include, given without the leading dot.
            Defaults to 'py html' when omitted; '*' expands to the full
            set 'py c html json'.
    scope:  Which problems to search: 'solved' (default) restricts to
            solved problems; 'problems' covers every known problem.
```

---

#### Command: `show` (`open`, `view`)

Open problem/file in a browser or the web viewer panel.
* profiles: admin, maintainer, contributor, reader
* ❏ takes an optional problem number (defaults to the current problem)
* » supports `--silent`

```
show
[problem=<n>] (default current)
[filename=<str>|none] (default None)
[silent=true|--silent]
```

```text
Open a problem's documentation page, in a browser or the web viewer panel.

When *problem* is omitted, opens the current problem. The path depends on the
shell's channel (from the resolved subject):

- **terminal** — opens the problem's page (`<base_url>/solutions/NNNN/`) in the named
  browser tab "solver-doc" (via
  `browser open-in-tab`). Every `show` reuses that one tab: the same problem is
  focused and refreshed, a different problem navigates the tab in place, and the
  tab is recreated if it has been closed. Prints an error and returns early if
  the "browser" command is not available.

- **web** — the shell has no local browser to drive (it runs on the server while
  the user's browser is elsewhere), so it emits an `OSC 5379` control sequence
  (`open;<NNNN>;<token>`) on stdout. The xterm.js page rides it over the
  PTY → WebSocket pipe and swaps the app shell's left pane to
  `<origin>/solutions/NNNN/`; the monotonic token lets the page ignore the
  sequence when the PTY replay buffer re-sends it on reconnect.

When *filename* is given, `show` opens that solution file in the code editor
instead of the rendered page — it delegates to `edit`, so the same file lookup,
channel handling, and browser tab apply.

Arguments:
    problem:  The `problem` to open; defaults to the current problem.
    filename: A solution file to open in the code editor; when omitted, opens
              the rendered documentation page instead.
```

---

#### Command: `summary`

Parse .progress.html into problems.json.
* profiles: admin, maintainer
* » supports `--silent`

```
summary
[silent=true|--silent]
```

```text
Refresh the solved/unsolved state from your Project Euler progress page.

Parses `solutions/.progress.html` (the saved Page Source of your
authenticated https://projecteuler.net/progress page) and updates
`problems.json` with which problems are solved and their metadata. This is
how the shell learns your real progress, driving `{solved}` / `{unsolved}`,
`progress`, and `solved`.

Returns an error (with instructions) if `.progress.html` is missing: visit
the progress page, copy its Page Source into that file, and retry.
```

---

#### Command: `sys-setup` (`install`)

Installs or uninstalls system resources.
* profiles: admin

```
sys-setup <chrome|dev-env|upgrade-service>
[uninstall=true|--uninstall]
[show_help=true|--show-help]
```

```text
Installs or uninstalls the system resource specified as the target.

Parameters:
    target:     Specifies the target resource to install or uninstall.
                Accepted values are 'chrome', 'dev-env', and 'upgrade-service'
    uninstall:  Indicates whether the operation is an uninstallation.
                Defaults to False, which performs installation.
    show_help:  Displays help information for the specified target.
```

---

#### Command: `test-cases`

list the test cases for the problem.
* profiles: admin, maintainer, contributor, reader
* ❏ takes an optional problem number (defaults to the current problem)

```
test-cases
[problem=<n>] (default current)
[all|dev|main|extra ...]
```

```text
List the test cases for a given problem based on specified categories.

Args:
    problem:            The `problem` to list test cases for. This is used to locate the test cases file.
    *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                        (which expands to all three). Defaults to all three if omitted.

Returns:
    int: Exit code indicating the completion status of the operation.
```

---

#### Command: `update-docs`

Regenerate the generated sections of the docs/ guides.
* profiles: admin
* » supports `--silent`

```
update-docs
[check=true|--check]
[silent=true|--silent]
```

```text
Rebuild the registry-generated blocks in the `docs/` guides and the README.

Rewrites only the marked `<!-- GEN:... -->` sections — the command catalogue,
the in-index summary, the per-command reference, the authorization audit table
in `docs/authorizations.md` (module / command / channels / requires / least
profile), and the README package-layout tree (built from each module's
docstring) — from the live command registry and the source tree, leaving all
hand-written prose untouched. Also regenerates the web start page's summary
(`solver/web/content/home-summary.md`) from the README's HOME slice. Run it
after changing any command's name, alias, help text, signature,
`requires`/`channels`, a module's first docstring line, or the README's HOME
region.

Args:
    ctx:    The command context.
    check:  When True, write nothing and fail (non-zero) if any doc is out
            of date, listing the stale files. When False (default), rewrite
            the docs in place and report which were updated.
```

---

#### Command: `update-models`

Update Model enum, pricing, and USD→EUR rate.
* profiles: admin
* » supports `--silent`

```
update-models
[check=true|--check]
[silent=true|--silent]
```

```text
Refresh the `Model` class in `models.py` and the `usd_to_eur` rate in `config.json`.

Lists the available Claude models from the Anthropic Models API, scrapes each model's base
input/output price (per million tokens) from the public pricing page, and rewrites the
`# GEN:models` block in `models.py` — the enum members, their inline comments, and the
`price` map. Curated per-model comments are kept; a newly discovered model is commented with
its display name. Separately, fetches the USD→EUR rate from the ECB daily reference feed and
writes it to `config.json` (the rate is used only by `costs`). Nothing else is touched.

Args:
    check:  When True, write nothing and fail (non-zero) if either the model block or the
            FX rate is out of date. When False (default), rewrite both in place. The FX rate
            drifts daily, so `--check` will usually report it as stale.
```

---

#### Command: `user`

Show public key & enc-key access; --regen for new key-pair.
* profiles: admin, maintainer, contributor, reader

```
user
[regen=true|--regen]
```

```text
Show the current identity and whether it can decrypt; create a key pair on first run or --regen.

A key pair is created only when the identity file is **truly absent** (first run) or on
an explicitly confirmed ``--regen``. An id file that *exists but cannot be read* — the
vault is locked, the session key is stale, the vault file was lost — is a **vault
failure to fix, never a reason to mint a new identity**: replacing the key would
silently orphan the real one (and with it any enc-key authorization it carries).
```

---

#### Command: `user-authorize` (`authorize`)

Authorise another public key (hex) to access the enc key.
* profiles: admin

```
user-authorize <public_key>
```

```text
Wrap the current master key to `public_key` and add it to enc-key.json (proof-of-possession).
```

---

#### Command: `users`

Administer accounts + invite requests (re-executes the admin CLI under sudo).
* profiles: admin

```
users
[action=list|process-requests|add|change|enable|disable|remove|redeploy] (default list)
[identity=<str>] (default '')
[profile=reader|contributor|maintainer|admin] (default reader)
```

```text
Administer accounts on the authorization map + the auth service.

The whole command is ``admin``-floored and every verb re-executes the admin CLI
under ``sudo`` (the SoR + admin socket are root-only). There is no reader/maintainer
tier here — a web shell cannot get sudo, so nothing runs over the web.

Args:
    action:   list (roster + pending + the invite-request queue), process-requests
              (walk the queue interactively — accept / ignore / dismiss each),
              add (map entry — ``@email`` also provisions + mints an invite; a bare
              os-login is local-only), change (reassign a profile), enable / disable
              (web SRP state), remove (drop the account/entry), redeploy (re-assert
              the per-user host layer and re-lay every collaborator's git hooks —
              takes no identity, and drops live shells).
    identity: a web email (``@``) or a local OS login (required for the account
              verbs; not for list / process-requests / redeploy).
    profile:  the profile to assign (add / change). ``admin`` is valid only for a
              local os-login, never a web account.
```

---

#### Command: `vault`

Manage the per-user secrets vault: status | init | unlock | change-password.
* profiles: admin, maintainer, contributor, reader

```
vault
[action=status|init|unlock|change-password] (default status)
```

```text
Encrypt this user's `id` + `env` at rest under a password-derived vault key.

- `status` (default): show whether the vault exists, which secret files are encrypted, and
  whether this session can decrypt them.
- `init`: create the vault and migrate the existing plaintext `id`/`env` into it in place, then
  unlock the current session. Prompts for a new password.
- `unlock`: unlock a locked session (the shell asks at startup; this is the retry — after a
  typo, or once you have the password to hand).
- `change-password`: re-wrap the vault key under a new password (the secrets are not re-encrypted).

The password is never stored: set `$EULER_VAULT_PASSWORD` for a non-interactive unlock (a script,
CI), otherwise you are asked once per shell.
```

---

#### Command: `version`

Show the running solver build version.
* profiles: admin, maintainer, contributor, reader

```
version
```

```text
Print the installed build version, plus live git detail of the clone.

The first line is the running build: the number recorded in the tracked
`solver/version.py` (`config.version`), written only by the release script and
correct even in the deployed venv where there is no git. The second line is the
live `git describe`
of `config.root_dir` — the developer's checkout in a terminal, or the
collaborator's own `~/euler` clone in the web shell — reporting its exact
commit and dirty state. The two answer different questions (what build is
installed vs. what commit this clone sits on) and can legitimately differ.

Reader-floor and read-only: no writes, no network, no vault access — safe to
run in every collaborator's long-lived web shell.
```
<!-- /GEN:command-index -->
