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
| [`claude-api`](#command-claude-api) | — | Generate specified target using Claude API. |
| [`claude-skill`](#command-claude-skill) | — | Launch the Claude Euler Solver skill. |
| [`clear`](#command-clear-cls) | `cls` | Clear the screen. |
| [`costs`](#command-costs) | — | Display total cost of AI API tokens consumed in session. |
| [`echo`](#command-echo) | — | Print text. |
| [`eval-benchmark`](#command-eval-benchmark-benchmark) | `benchmark` | Benchmark the problem currently in the workspace. » |
| [`eval-compile-c`](#command-eval-compile-c-compile) | `compile` | Build all C source files in the solutions_dir. » |
| [`eval-evaluate`](#command-eval-evaluate-eval) | `eval` | Evaluate solutions against test cases. » |
| [`eval-set-problem`](#command-eval-set-problem-problem) | `problem` | Set the active problem |
| [`git-commit`](#command-git-commit-commit) | `commit` | Commit everything, optionally resetting to origin/master. » |
| [`git-hooks`](#command-git-hooks-hooks) | `hooks` | Run pre-commit hook and simulated pre-push hook. » |
| [`git-publish`](#command-git-publish-publish) | `publish` | Publish named targets (keys|scripts|solutions|solver) to remote. » |
| [`git-status`](#command-git-status-status) | `status` | Display sync state between local and origin/master. |
| [`git-sync`](#command-git-sync-sync) | `sync` | Bring the local repository in sync with origin/master. |
| [`key-reconstruct`](#command-key-reconstruct) | — | Recover master key from shares and wrap it to the current user. |
| [`key-rekey`](#command-key-rekey-rekey) | `rekey` | Rotate the enc key and re-wrap to users. |
| [`key-split`](#command-key-split) | — | Split master key into shares; recovery by threshold num of shares. |
| [`lint`](#command-lint) | — | Lint the workspace, fix with autoflake + autopep8 + isort. » |
| [`manage-config`](#command-manage-config) | — | Manage configuration settings. |
| [`mark`](#command-mark-mark-solved) | `mark-solved` | Mark the workspace problem as solved, after checking. » |
| [`new`](#command-new) | — | Generate new solution/test-case file in the workspace. » |
| [`pause`](#command-pause) | — | Pause for user confirmation to continue. |
| [`pip-upgrade`](#command-pip-upgrade-upgrade) | `upgrade` | Upgrade dependency group (all|ai|core|dev|solutions|show). |
| [`problems`](#command-problems) | — | Show list of problems (all|solved|unsolved|stale). |
| [`progress`](#command-progress) | — | Print progress statistics about Euler problems. |
| [`search`](#command-search-find) | `find` | Find content in the stack. |
| [`show`](#command-show-open-view) | `open`, `view` | Open problem documentation in a browser. » |
| [`summary`](#command-summary) | — | Parse .progress.html into problems.json. » |
| [`sys-setup`](#command-sys-setup-install) | `install` | Installs or uninstalls system resources. |
| [`update-docs`](#command-update-docs) | — | Regenerate the generated sections of the docs/ guides. » |
| [`update-models`](#command-update-models) | — | Update Model enum, pricing, and USD→EUR rate. » |
| [`user`](#command-user) | — | Show user public key & enc-key access; --regen makes new key-pair. |
| [`user-authorize`](#command-user-authorize-authorize) | `authorize` | Authorise another public key (hex) to access the enc key. |

*Legend: § requires the workspace lock · ↻ may refresh workspace state · ⊘ refuses while the workspace is checked out · ⚑ checks the workspace out while it runs · » supports `--silent`.*
<!-- /GEN:command-summary -->

</details>

---

<!-- GEN:command-index -->
#### Command: `!` (`sh`, `bash`)

Run a bash command.

```
! <command> [args]...
! sh → escape to a bash shell.
! py → escape to a python interpreter.
```

```text
Run a shell command from the shell, returning its exit code.

Any child process inherits this shell's workspace lock (via the
`solver_workspace_lock` environment variable), so tools launched here operate
on the locked workspace safely. Three forms escape into an *interactive*
session that takes over the terminal:

    `! sh` / `! bash`       an interactive bash subshell, in `workspace/`
    `! py` / `! python`     an interactive Python interpreter, in the repo root
    `! claude [prompt]`     Claude Code, in the repo root

Any other command (`! ls`, `! git diff`, …) runs non-interactively in
`workspace/` — so paths are relative to the current problem's files — with
its output streamed through the shell (so `solver -s` can log it). After the
command finishes, the workspace specials are refreshed (↻) in case it changed
the workspace.

Aliased as `sh` and `bash`, so `sh <command>` is shorthand for `! <command>`.
```

---

#### Command: `?` (`help`)

List commands or show help for a specific command.

```
? [command]
```

```text
List every command, or show detailed help for one command.

With no argument, prints a table of all registered commands with their
aliases and one-line descriptions, plus the legend (§ requires the workspace
lock, ↻ may refresh workspace state, ⊘ refuses while checked out, ⚑ checks
out while it runs, » supports --silent).

With a command name or alias, prints a panel for just that command: its
description (with the legend glyphs expanded to full sentences), its aliases,
and its usage. Returns non-zero if the named command is unknown.

Aliased as `help`.
```

---

#### Command: `claude-api`

Generate specified target using Claude API.

```
claude-api <c|py|doc|notes|test-cases>
[force=true|--force]
[major=true|--major]
[model=claude-fable-5|claude-opus-4-8|claude-opus-4-7|claude-opus-4-6|claude-opus-4-5|claude-sonnet-4-6|claude-sonnet-4-5|claude-haiku-4-5|none] (default None)
```

```text
Generate AI-based content for the specified target.

Args:
    target: The type of content to generate ('c' or 'py' for code, 'doc' to refresh in-source
            docs, 'notes' for documentation, 'test-cases' for test cases).
    major:  Whether this is after a major change (e.g. template or instruction change).
    force:  Whether to force generation even if the target already exists.
    model:  The AI model to use for generation; defaults to Opus for code and docs and Sonnet for test cases.
```

---

#### Command: `claude-skill`

Launch the Claude Euler Solver skill.

```
claude-skill <solve|review>
[additional_prompt=<str>] (default '')
```

```text
Run Claude Code over the locked workspace via the claude-euler-solver skill.

Launches Claude Code headless against the current `workspace/` (which this
shell holds the lock for), runs the requested action, and streams a
live-updating Markdown summary back into the shell, ending with a footer of
turns / duration / cost. Heavier and slower than `claude-api` — it actually
runs `solver` commands, edits files, evaluates, and iterates. Needs the
`claude` CLI on PATH and an `ANTHROPIC_API_KEY`.

Args:
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

```
clear
```

```text
Clear the terminal screen and scrollback, then succeed.

A convenience wrapper over the console's clear; equivalent to the shell
`clear`. Takes no arguments. Aliased as `cls`.
```

---

#### Command: `costs`

Display total cost of AI API tokens consumed in session.

```
costs
[ecb_usd_rate=<float>] (default 1.1342)
```

```text
Return a formatted cost string for all AI tokens consumed in the session so far, or "nil"
if nothing has been consumed.

Totals the charges across all models in "consumed_tokens" using each model's published USD
price per million tokens (with cache writes at 1.25x and cache reads at 0.10x the input rate),
then converts to EUR using "ecb_usd_rate".

Args:
    ecb_usd_rate: conversion rate (1 € = N $). Defaults to 'config.ecb_usd_rate'.
```

---

#### Command: `echo`

Print text.

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

#### Command: `eval-benchmark` (`benchmark`)

Benchmark the problem currently in the workspace.
* » supports `--silent`

```
eval-benchmark
[all|dev|main|extra ...]
[clean=true|--clean]
[timeout=<float>|none] (default None)
[disable_timeout=true|--disable-timeout]
[lang=*|py|c] (default *)
[solution_index=<int>|none] (default None)
[reset=true|--reset]
[verbose=true|--verbose]
[silent=true|--silent]
```

```text
Measure and record the execution time of the workspace solutions.

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
    *categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                        (which expands to all three). Defaults to all three if omitted.
    clean:              If True, force compiles C solutions. Defaults to False.
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

#### Command: `eval-compile-c` (`compile`)

Build all C source files in the solutions_dir.
* » supports `--silent`

```
eval-compile-c
[clean=true|--clean]
[silent=true|--silent]
```

```text
Compile every C solution in the workspace into a runnable binary.

Builds each `.c` file in `workspace/` (linking the runner harness) so it can
be evaluated and benchmarked; reports per-file success or the compiler
error. `eval --clean` and `benchmark` invoke this for you, so you rarely
call it directly.

Args:
    problem_number:     problem number to compile.
    clean:              When True, force a full rebuild instead of reusing up-to-date
                        build output. Defaults to False.
```

---

#### Command: `eval-evaluate` (`eval`)

Evaluate solutions against test cases.
* » supports `--silent`

```
eval-evaluate
[all|dev|main|extra ...]
[clean=true|--clean]
[timeout=<float>|none] (default None)
[disable_timeout=true|--disable-timeout]
[lang=*|py|c] (default *)
[runs=<int>] (default 1)
[show=true|--show]
[solution_index=<int>|none] (default None)
[verbose=true|--verbose]
[silent=true|--silent]
```

```text
Evaluate solutions against test cases.

Args:
*categories:        Test case categories to include. Accepts 'dev', 'main', 'extra', or 'all'
                    (which expands to all three). Defaults to 'dev', 'main' if omitted.
clean:              If True, force compiles C solutions. Defaults to False.
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

#### Command: `eval-set-problem` (`problem`)

Set the active problem

```
eval-set-problem <problem_number>
```

---

#### Command: `git-commit` (`commit`)

Commit everything, optionally resetting to origin/master.
* » supports `--silent`

```
git-commit
[reset=true|--reset]
[verify=false|--no-verify]
[silent=true|--silent]
```

```text
Stage and commit the solutions and workspace as a timestamped checkpoint.

Adds everything under `solutions/` and `workspace/` and commits it with a
`checkpoint <timestamp>` message — the routine "save my progress" step.

Args:
    reset:  When True, first soft-reset to `origin/master` so the new commit
            squashes all local commits into a single checkpoint (working
            tree untouched). Defaults to False.
    verify: When True (default), run the pre-commit hook (flake8 + mypy).
            When False, commit with `--no-verify`, skipping the hook.

Aliased as `commit`.
```

---

#### Command: `git-hooks` (`hooks`)

Run pre-commit hook and simulated pre-push hook.
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

#### Command: `git-publish` (`publish`)

Publish named targets (keys|scripts|solutions|solver) to remote.
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

#### Command: `git-status` (`status`)

Display sync state between local and origin/master.

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

```
git-sync
[dry_run=true|--dry-run]
```

```text
Bring the local repository in sync with origin/master.

Args:
    dry_run: Print the sync commands instead of running them. Defaults to False.
```

---

#### Command: `key-reconstruct`

Recover master key from shares and wrap it to the current user.

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

Split master key into shares; recovery by threshold num of shares.

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

Lint the workspace, fix with autoflake + autopep8 + isort.
* » supports `--silent`

```
lint
[auto_fix=true|--auto-fix]
[silent=true|--silent]
```

```text
Lint the workspace solution files, optionally auto-fixing them.

Checks the current problem's solution files for style and quality issues
(flake8, plus the configured checks). Reports any findings and reflects them
in the exit code.

Args:
    auto_fix:   When True, attempt to fix issues in place with autoflake
                (remove unused imports/variables), autopep8 (style), and
                isort (import order), then re-check. When False (default),
                only report. Fails if the workspace holds no problem.
```

---

#### Command: `manage-config`

Manage configuration settings.

```
manage-config
[param=all|server_port|timeout_multiple|timeout_single|ecb_usd_rate] (default all)
[value=<float>|none] (default None)
```

```text
Show or update a managed configuration setting.

The managed settings persist to `solver/config.json` and override the
defaults in `config.py`: `server_port` (the web server's port),
`timeout_single` / `timeout_multiple` (solution timeouts in seconds for a
single run and for repeated runs), and `ecb_usd_rate` (the rate `costs` uses).

Args:
    param:  Which setting to act on; 'all' (default) prints every setting.
    value:  When given, the new value to assign to `param` (coerced to the
            setting's type and saved). When omitted, the current value of
            `param` is printed instead.
```

---

#### Command: `mark` (`mark-solved`)

Mark the workspace problem as solved, after checking.
* » supports `--silent`

```
mark
[silent=true|--silent]
```

```text
Mark the workspace problem as solved — once its results confirm it.

Records the current workspace problem as solved (with today's date) in
`problems.json`, the same state `summary` maintains, so `{solved}`,
`progress`, and `solved` reflect it without re-importing the progress page.

It only proceeds after checking the recorded results: the workspace must
hold a problem, its `test_cases.json` must have a `main` case with an
answer, and `results.json` must contain a `correct` verdict for that `main`
case. Run `benchmark` (which records results) first; a problem already
marked solved is left unchanged.

Aliased as `mark-solved`.
```

---

#### Command: `new`

Generate new solution/test-case file in the workspace.
* » supports `--silent`

```
new
[py=true|--py]
[c=true|--c]
[tc=true|--tc]
[silent=true|--silent]
```

```text
Generate a new solution file for the problem in the given workspace.

The new file is named based on the problem's base filename and the number of existing
Python solution files in the workspace (e.g., "p0001_s0.py", "p0001_s1.py").

Prompts the user for confirmation before creating the file. The file is created from
the boilerplate template with the problem information substituted.
```

---

#### Command: `pause`

Pause for user confirmation to continue.

```
pause
```

```text
Pause the program execution until the user presses Enter.
```

---

#### Command: `pip-upgrade` (`upgrade`)

Upgrade dependency group (all|ai|core|dev|solutions|show).

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

Show list of problems (all|solved|unsolved|stale).

```
problems
[which=all|solved|unsolved] (default all)
```

```text
Print a list of problems and their count.

Args:
    which:  Which set to list — 'all' (default) every known problem,
            'solved' the problems with a recorded answer, 'unsolved' those
            without, or 'stale' those whose notes are older than their
            solution source. Mirrors the `{problems}` / `{solved}` /
            `{unsolved}` shell variables.
```

---

#### Command: `progress`

Print progress statistics about Euler problems.

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

#### Command: `search` (`find`)

Find content in the stack.

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

Open problem documentation in a browser.
* » supports `--silent`

```
show
[problem_number=<int>] (default 0)
[check_for_errors=true|--check-for-errors]
[silent=true|--silent]
```

```text
Open a problem's "problem.html" in the system browser.

When *problem_number* is "0" (default), opens the problem currently in the workspace.

Prints an error and returns early if:
- the "browser" command is not available, or
- the resolved "problem.html" file does not exist.

Arguments:
    problem_number: Problem to open; "0" means the current workspace.
    check_for_errors: Whether to check for rendering errors.
```

---

#### Command: `summary`

Parse .progress.html into problems.json.
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

#### Command: `update-docs`

Regenerate the generated sections of the docs/ guides.
* » supports `--silent`

```
update-docs
[check=true|--check]
[silent=true|--silent]
```

```text
Rebuild the registry-generated blocks in the `docs/` guides and the README.

Rewrites only the marked `<!-- GEN:... -->` sections — the command catalogue,
the in-index summary, the per-command reference, and the README package-layout
tree (built from each module's docstring) — from the live command registry and
the source tree, leaving all hand-written prose untouched. Run it after
changing any command's name, alias, help text, or signature, or a module's
first docstring line.

Args:
    check:  When True, write nothing and fail (non-zero) if any doc is out
            of date, listing the stale files. When False (default), rewrite
            the docs in place and report which were updated.
```

---

#### Command: `update-models`

Update Model enum, pricing, and USD→EUR rate.
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

Show user public key & enc-key access; --regen makes new key-pair.

```
user
[regen=true|--regen]
```

```text
Show the current identity and whether it can decrypt; create a key pair on first run or --regen.
```

---

#### Command: `user-authorize` (`authorize`)

Authorise another public key (hex) to access the enc key.

```
user-authorize <public_key>
```

```text
Wrap the current master key to `public_key` and add it to enc-key.json (proof-of-possession).
```
<!-- /GEN:command-index -->
