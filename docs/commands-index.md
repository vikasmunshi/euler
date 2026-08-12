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

A command's *flags* line lists the behaviours marked by these glyphs — the same
ones a command's `?` panel carries at the prompt. The table is generated from the
glyph constants themselves by `update-docs` — do not edit it by hand:

<!-- GEN:flags-legend -->
| glyph | meaning |
|-------|---------|
| `⚑` | the least profile that may run it — every rung above may too |
| `❏` | takes an optional problem number (defaults to the current problem) |
| `✎` | asks for anything you leave out |
| `»` | supports `--silent` to suppress its incidental output |
<!-- /GEN:flags-legend -->


In a usage string: `<required>`, `[optional]`, `a|b|c` is a choice, `key=value`
sets a named parameter, `--flag` / `--no-flag` toggle a boolean, and `...` marks
a parameter that accepts repetition.

---

### Commands

<details>
<summary>command catalogue (click to expand) — each name jumps to its entry below</summary>

<!-- GEN:command-summary -->
| Command | Aliases | Requires | Description |
|---------|---------|----------|-------------|
| [`!`](#command--sh-bash) | `sh`, `bash` | `contributor` | Run a shell command from the shell, returning its exit code. |
| [`?`](#command--help) | `help` | `reader` | List every command, or show detailed help for one command. |
| [`benchmark`](#command-benchmark) | — | `contributor` | Measure and record the execution time of the problem's solutions. |
| [`check-commands`](#command-check-commands) | — | `admin` | Report every command docstring that breaks the documented standard. |
| [`claude-api`](#command-claude-api) | — | `contributor` | Generate one of a problem's solution artifacts through the Claude API. |
| [`claude-batch`](#command-claude-batch) | — | `maintainer` | Bulk-tag a wave of problems in one Message Batches job, at half price. |
| [`claude-blog`](#command-claude-blog) | — | `maintainer` | Write (or flesh out) a topic article via the claude-euler-blogger skill. |
| [`claude-solve`](#command-claude-solve) | — | `contributor` | Run Claude Code over a problem's solution files, via a skill. |
| [`clear`](#command-clear-cls) | `cls` | `reader` | Clear the terminal screen and scrollback, then succeed. |
| [`compile-c`](#command-compile-c-compile) | `compile` | `contributor` | Compile every C solution for the problem into a runnable binary. |
| [`costs`](#command-costs) | — | `contributor` | Print what this session's AI tokens have cost, per model. |
| [`create-topic`](#command-create-topic) | — | `maintainer` | Seed a curated cross-cutting topic page. |
| [`echo`](#command-echo) | — | `reader` | Print the given text to the console, then succeed. |
| [`edit`](#command-edit-ed) | `ed` | `contributor` | Open a solution file in the web code editor. |
| [`evaluate`](#command-evaluate-eval) | `eval` | `contributor` | Evaluate a problem's solutions against its test cases. |
| [`gh-merge`](#command-gh-merge-merge) | `merge` | `maintainer` | List the open pull requests, or rebase-merge one onto master. |
| [`git-audit`](#command-git-audit-audit) | `audit` | `contributor` | Audit what git actually stores, across the whole tracked tree. |
| [`git-commit`](#command-git-commit-commit) | `commit` | `contributor` | Stage and commit the named targets — the one commit verb. |
| [`git-filter`](#command-git-filter-filter) | `filter` | `reader` | Report or wire the transparent encryption filter for `solutions/private`. |
| [`git-hooks`](#command-git-hooks-hooks) | `hooks` | `contributor` | Run the git pre-commit and (simulated) pre-push checks on demand. |
| [`git-identity`](#command-git-identity-identity) | `identity` | `contributor` | Configure your git identity and push credential from your GitHub login. |
| [`git-publish`](#command-git-publish-publish) | `publish` | `maintainer` | Publish changed files for named targets to the remote repository. |
| [`git-push`](#command-git-push-push) | `push` | `contributor` | Push the current branch to origin as yourself, then open its pull request. |
| [`git-reset`](#command-git-reset-reset) | `reset` | `reader` | Soft-reset your branch to origin/master — un-commit, keep every change. |
| [`git-status`](#command-git-status-status) | `status` | `reader` | Display the sync state between the local branch and origin/master. |
| [`git-sync`](#command-git-sync-sync) | `sync` | `reader` | Bring the local repository in sync with origin/master. |
| [`host-authorize`](#command-host-authorize) | — | `admin` | Mail the master key, sealed to one machine's public key — the off-host grant. |
| [`host-unlock`](#command-host-unlock) | — | `admin` | Take the mailed block from `host-authorize` and unlock this machine. |
| [`key-reconstruct`](#command-key-reconstruct) | — | `reader` | Unwrap the half you were sent, complete it from the repository, store the key. |
| [`key-rekey`](#command-key-rekey-rekey) | `rekey` | `admin` | Rotate the master key and re-issue it to every registered public key. |
| [`key-split`](#command-key-split) | — | `maintainer` | Send someone half the master key, sealed to their public key. |
| [`lint`](#command-lint) | — | `contributor` | Lint the problem's solution files, optionally auto-fixing them. |
| [`ls`](#command-ls) | — | `reader` | List the files in a problem's solution directory. |
| [`mark`](#command-mark-mark-solved) | `mark-solved` | `contributor` | Mark the current problem as solved — once its results confirm it. |
| [`msg`](#command-msg-messages) | `messages` | `reader` | Read and send messages: what is waiting for you, and what it asks you to do. |
| [`new`](#command-new) | — | `contributor` | Generate new solution and/or test-case files for the problem. |
| [`pause`](#command-pause) | — | `reader` | Wait for the user to press Enter before the block carries on. |
| [`pip-upgrade`](#command-pip-upgrade-upgrade) | `upgrade` | `admin` | Upgrade packages in the current venv for the given dependency groups. |
| [`problems`](#command-problems) | — | `reader` | Print a list of problems and their count. |
| [`progress`](#command-progress) | — | `reader` | Print overall progress through the Euler problems. |
| [`results`](#command-results) | — | `reader` | List the recorded results for a problem. |
| [`search`](#command-search-find) | `find` | `reader` | Search the solution stack for a case-insensitive regular expression. |
| [`show`](#command-show-open-view) | `open`, `view` | `reader` | Open a problem's documentation page, in a browser or the web viewer panel. |
| [`summary`](#command-summary) | — | `maintainer` | Refresh the solved/unsolved state from your Project Euler progress page. |
| [`sys-setup`](#command-sys-setup-install) | `install` | `admin` | Install or uninstall a system resource. |
| [`tags`](#command-tags) | — | `reader` | Report over the central tag vocabulary (`topics/tags.json`). |
| [`test-cases`](#command-test-cases) | — | `reader` | List a problem's test cases. |
| [`topic`](#command-topic) | — | `reader` | List a topic article's declared tags and what each one maps to. |
| [`topics`](#command-topics) | — | `reader` | List a problem's tags and the topic articles that cover them. |
| [`update-docs`](#command-update-docs) | — | `admin` | Rebuild the registry-generated blocks in the `docs/` guides and the README. |
| [`update-models`](#command-update-models) | — | `admin` | Refresh the model catalogue and its pricing. |
| [`update-tags`](#command-update-tags) | — | `contributor` | The glue for the double-entry tag graph. |
| [`update-usd-rate`](#command-update-usd-rate) | — | `maintainer` | Refresh the USD→EUR rate used to report API costs. |
| [`user`](#command-user) | — | `reader` | Show the solver user, the current identity, and whether it can decrypt. |
| [`user-authorize`](#command-user-authorize-authorize) | `authorize` | `maintainer` | Record someone's public key and send them half the master key. |
| [`users`](#command-users) | — | `admin` | Administer accounts on the authorization map + the auth service. |
| [`vault`](#command-vault) | — | `reader` | Encrypt this user's `id` + `env` at rest under a password-derived vault key. |
| [`version`](#command-version) | — | `reader` | Print the installed build version, plus live git detail of the clone. |
<!-- /GEN:command-summary -->

</details>

---

<!-- GEN:command-index -->
#### Command: `!` (`sh`, `bash`)

Run a shell command from the shell, returning its exit code.

* ⚑ needs contributor or above.

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

**usage**

```
! <command> [args]...
! sh → escape to a bash shell.
! py → escape to a python interpreter.
```

**arguments**

| argument | description |
|----------|-------------|
| `*args` | The command line to run, token by token — quoted before it reaches bash, so `! git log --oneline` arrives intact. With none, prints its own usage and fails. |

*Defined in* `solver.shell.bash._bash`.

---

#### Command: `?` (`help`)

List every command, or show detailed help for one command.

* ⚑ needs reader or above.

With no argument, prints the catalogue: command, aliases, the profile it needs, and its
description. Nothing there is abbreviated to a glyph — the facts one would stand for
(the problem a command takes, the `--silent` it supports) are spelled out in words in
the command's own panel, one `? <command>` away.

With a command name or alias, prints that command's own panel — its description, the
facts about it (the profile floor, and whether it takes a problem or supports
`--silent`), the prose and free sections of its docstring, its usage, and a row per
argument it accepts. It renders the same `HelpModel` that `update-docs` publishes as
`docs/commands-index.md`, so the guide and the prompt cannot disagree;
`docs/developer-guide.md` §3.8 is the docstring standard behind both. Returns non-zero
if the named command is unknown.

Aliased as `help`.

**usage**

```
? [command]
```

**arguments**

| argument | description |
|----------|-------------|
| `*args` | The command name or alias to describe. With none, lists every command. |

*Defined in* `solver.shell.builtins._help`.

---

#### Command: `benchmark`

Measure and record the execution time of the problem's solutions.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Like `eval`, runs every solution against the chosen test-case categories, but
always **records** the timings to `results.json` and repeats each case an
adaptive number of times (see "Repeats") instead of running once. Run `eval`
first to confirm correctness, then `benchmark` to measure; categories default
to all three ('dev', 'main', 'extra').

**usage**

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

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose solutions to benchmark. |
| `*categories` | Test-case categories to include: 'dev', 'main', 'extra', or 'all' (which expands to all three). Defaults to all three. |
| `clean` | When False, reuse up-to-date build output from previous compilations. Defaults to True. |
| `timeout` | Per-run timeout in seconds for a solution's execution. None uses the configured default. Defaults to None. |
| `disable_timeout` | Run without a timeout, and only once per test case — bypassing the adaptive repeat count above. Defaults to False. |
| `lang` | Which language to benchmark: '*', 'py' or 'c'. Defaults to '*'. |
| `solution_index` | Benchmark only this solution index. None benchmarks every solution. Defaults to None. |
| `reset` | Replace any existing persisted results with this run, on a clean completion; an interrupted run leaves them untouched. Defaults to False, which merges this run into the existing records as a running average. |
| `verbose` | Print error detail as each solution runs. Defaults to False. |
| `silent` | Suppress this command's output; errors and the result line still show. |

**repeats**

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

*Defined in* `solver.core.evaluate.benchmark`.

---

#### Command: `check-commands`

Report every command docstring that breaks the documented standard.

* ⚑ needs admin.
* » supports --silent to suppress output.

The standard is `docs/developer-guide.md` §3.8; the rules are listed in this module's
docstring. Findings print as `command | rule | detail` rows, and the exit code is
non-zero when there is at least one — so the command gates a chain and serves as the
docstring lane of `scripts/linters/check.sh solver`.

**Admin-floored on purpose, not out of caution.** Registration is itself
profile-filtered (`solver/shell/command.py`): a command above your floor is never
registered, so `registry.all()` returns only what *you* may run. Checking from a lesser
profile would pass by never looking at the commands it cannot see — the same reasoning
that floors `update-docs`.

**usage**

```
check-commands
[name=<str>] (default '')
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `name` | Check only the command (or alias) named, instead of the whole registry. Defaults to '', which checks every registered command. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.utils.doclint.check_commands`.

---

#### Command: `claude-api`

Generate one of a problem's solution artifacts through the Claude API.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* ✎ asks for anything you leave out.

Dispatches to the generator for *target*, prints the USD/EUR cost of the call, and fails
if the generator reports failure.

**usage**

```
claude-api
[problem=<n>] (default current)
[target=c|py|doc|notes|tags|test-cases] (asked)
[force=true|--force]
[major=true|--major]
[model=claude-fable-5|claude-opus-5|claude-opus-4-8|claude-opus-4-7|claude-opus-4-6|claude-opus-4-5|claude-sonnet-4-6|claude-sonnet-4-5|claude-sonnet-5|claude-haiku-4-5|none] (default None)
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem to generate for. |
| `target` | What to generate: 'c' or 'py' for code, 'doc' to refresh the in-source documentation, 'notes' for `notes.html`, 'tags' for `tags.json`, 'test-cases' for test cases. Offered as a menu when omitted. |
| `force` | Generate even when the target already exists, overwriting it. Defaults to False. |
| `major` | Regenerate after a major change — a new template or changed instructions — rather than an incremental one. Defaults to False. |
| `model` | The model to generate with. Defaults to None, which picks Opus for code, docs and notes, and Sonnet for tags and test cases. |

*Defined in* `solver.ai.api.claude_api`.

---

#### Command: `claude-batch`

Bulk-tag a wave of problems in one Message Batches job, at half price.

* ⚑ needs maintainer or above.

Solved problems get the full prompt (domain + per-index techniques + takeaways); unsolved
ones get the domain-only prompt. Run `update-tags` after each wave to promote the proposed
`new-tags` before submitting the next, so later waves are prompted with the settled vocabulary.

Note: the `costs` command counts batched tokens at standard list price, so its total
overstates a batch wave by roughly 2x; this command prints the true discounted cost.

**usage**

```
claude-batch
[action=run|submit|collect|list] (default run)
[target=solved|unsolved|untagged|all] (default untagged)
[limit=<int>] (default 250)
[start=<int>] (default 0)
[batch_id=<str>] (default '')
[problems_list=<str>] (default '')
[model=claude-fable-5|claude-opus-5|claude-opus-4-8|claude-opus-4-7|claude-opus-4-6|claude-opus-4-5|claude-sonnet-4-6|claude-sonnet-4-5|claude-sonnet-5|claude-haiku-4-5] (default claude-sonnet-5)
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | `run` submits, waits and collects; `submit` returns as soon as the job is queued; `collect` writes the results of an already-submitted job; `list` shows waves that were submitted but not yet collected. |
| `target` | Which problems to cover — `untagged` (no `tags.json` yet, the resumable default), `solved`, `unsolved`, or `all`. |
| `limit` | Maximum problems in this wave. Keep it to a few hundred so that `new-tags` proposals get reconciled often enough to avoid duplicate slugs. |
| `start` | Skip problems numbered below this. Paces a re-tag through the stack in waves, where `untagged` cannot help because every problem already has a file. |
| `batch_id` | The job to collect; required for `collect`. |
| `problems_list` | Comma-separated problem numbers to run instead of a `target` sweep — the targeted re-run after a vocabulary change (`23,39,146`). Overrides `target`. |
| `model` | The model to run the wave on. |

*Defined in* `solver.ai.batch.claude_batch`.

---

#### Command: `claude-blog`

Write (or flesh out) a topic article via the claude-euler-blogger skill.

* ⚑ needs maintainer or above.
* ✎ asks for anything you leave out.

*topic* names what to write about: a tag's `<facet>/<slug>` path (e.g.
`technique/sieve-of-eratosthenes`), a bare tag slug, or a curated topic path
(`number-theory/primes`). Tab-completion offers every topic in the article index
(`topics/articles.json`), unwritten and most-referenced first.
Launches Claude Code headless to research the covering problems and write the article
under `topics/`, then streams a live Markdown summary. Needs the `claude` CLI and an
`ANTHROPIC_API_KEY`.

A topic whose article the index reports as `final` is left alone — the skill marks a page
final when it is done writing it, and rewriting one is an explicit `--force`.

**usage**

```
claude-blog
[topic=<str>] (asked)
[additional_prompt=<str>] (asked)
[force=true|--force]
```

**arguments**

| argument | description |
|----------|-------------|
| `topic` | The tag or topic to write about. Offered as a menu of the article index when omitted; completion offers the same set. |
| `additional_prompt` | Extra free-text guidance for the writer. Asked for in an interactive shell when omitted — the web's Write / Rewrite actions type a bare `claude-blog <path>`, so a maintainer would otherwise never get to pass an angle. Enter skips it. Defaults to empty. |
| `force` | Rewrite the article even when it is already final. Defaults to False. |

*Defined in* `solver.ai.skill.claude_blog`.

---

#### Command: `claude-solve`

Run Claude Code over a problem's solution files, via a skill.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* ✎ asks for anything you leave out.

Launches Claude Code headless against the given problem's solution directory,
runs the requested action, and streams a
live-updating Markdown summary back into the shell, ending with a footer of
turns / duration / cost. Heavier and slower than `claude-api` — it actually
runs `solver` commands, edits files, evaluates, and iterates. Needs the
`claude` CLI on PATH and an `ANTHROPIC_API_KEY`.

**usage**

```
claude-solve
[problem=<n>] (default current)
[action=solve|review] (asked)
[additional_prompt=<str>] (default '')
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem to work on. |
| `action` | What to do — 'solve' writes and verifies a Python solution, translates it to C, then documents and summarises it; 'review' audits an existing solution for C↔Python parity, in-source documentation and `notes.html`. Offered as a menu when omitted. |
| `additional_prompt` | Extra free-text instructions appended to the skill invocation. Defaults to empty. |

*Defined in* `solver.ai.skill.claude_solve`.

---

#### Command: `clear` (`cls`)

Clear the terminal screen and scrollback, then succeed.

* ⚑ needs reader or above.

A convenience wrapper over the console's clear; equivalent to the shell `clear`. Takes
no arguments — any given are ignored. Aliased as `cls`.

**usage**

```
clear
```

*Defined in* `solver.shell.builtins._clear`.

---

#### Command: `compile-c` (`compile`)

Compile every C solution for the problem into a runnable binary.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Builds each `.c` file in `problem.solution_dir/` (linking the runner harness)
so it can be evaluated and benchmarked; reports per-file success or the compiler
error. `eval` and `benchmark` invoke this for you, so you rarely call it directly.

**usage**

```
compile-c
[problem=<n>] (default current)
[clean=false|--no-clean]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose C sources to compile. |
| `clean` | When False, reuse up-to-date build output from previous compilations. Defaults to True. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.evaluate.compile_c`.

---

#### Command: `costs`

Print what this session's AI tokens have cost, per model.

* ⚑ needs contributor or above.

Totals the charges across every model in `consumed_tokens` using its published USD price
per million tokens (cache writes at 1.25x and cache reads at 0.10x the input rate), then
converts to EUR. Prints "No charges so far." when nothing has been consumed; either way
it succeeds.

**usage**

```
costs
[ecb_usd_rate=<float>] (default 1.154)
```

**arguments**

| argument | description |
|----------|-------------|
| `ecb_usd_rate` | The conversion rate to price the total in EUR (1 € = N $). Defaults to the configured `ecb_usd_rate`. |

*Defined in* `solver.ai.models.costs`.

---

#### Command: `create-topic`

Seed a curated cross-cutting topic page.

* ⚑ needs maintainer or above.
* ✎ asks for anything you leave out.

A curated topic (e.g. `number-theory/primes`) gathers several tags under one idea,
unlike a tag's own auto-generated page.

*path* is the `folder/leaf` the page lives at under `topics/`. Give the tag slugs as
arguments to create non-interactively; give none and, in an interactive shell, pick them with
a search-and-select prompt. Every slug must exist in the vocabulary. The page is seeded from
the same template a tag page uses (its title is the leaf, title-cased — edit it when you
write the page) and reconciled straight away, so it appears in the draft index and its
Problems section is filled. Write it with `claude-blog <path>`.

**usage**

```
create-topic <path>
[tags=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `path` | The `folder/leaf` location under `topics/` (lowercase words and hyphens). |
| `*tags` | The tag slugs the page covers. Omit them and, in an interactive shell, pick them by search-and-select over the vocabulary. |

*Defined in* `solver.core.tags.create_topic`.

---

#### Command: `echo`

Print the given text to the console, then succeed.

* ⚑ needs reader or above.

Handy in command blocks to annotate progress or to surface a variable, since
`{...}` references are substituted before the command runs — e.g.
`echo solved {len(solved)} problems`.

**usage**

```
echo <text>
```

**arguments**

| argument | description |
|----------|-------------|
| `*args` | The words to print. They are joined with single spaces and printed literally, with no rich markup interpretation. |

*Defined in* `solver.shell.builtins._echo`.

---

#### Command: `edit` (`ed`)

Open a solution file in the web code editor.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* ✎ asks for anything you leave out.
* » supports --silent to suppress output.

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

**usage**

```
edit
[problem=<n>] (default current)
[filename=<str>] (asked)
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem owning the file. |
| `filename` | The solution-directory file to edit, as `ls` lists it. Offered as a menu when omitted. It must already exist. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.viewer.edit`.

---

#### Command: `evaluate` (`eval`)

Evaluate a problem's solutions against its test cases.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.

Compiles what needs compiling, then runs every solution the problem has — each
language, each solution index — against every test case in the chosen categories,
printing a verdict line per run: `correct`, `incorrect`, `error`, `overflow`, `timeout`
or `unknown` (a case with no recorded answer). Fails unless every run was correct, so it
gates a chain: `eval 42 && benchmark`.

This is the correctness check and it records nothing. `benchmark` is the measuring
counterpart — same runs, but written to `results.json` and repeated an adaptive number
of times.

**usage**

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

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose solutions to evaluate. |
| `*categories` | Test-case categories to include: 'dev', 'main', 'extra', or 'all' (which expands to all three). Defaults to 'dev' and 'main'. |
| `clean` | When False, reuse up-to-date build output from previous compilations. Defaults to True. |
| `timeout` | Timeout in seconds for a solution's execution. None uses the configured default. Defaults to None. |
| `disable_timeout` | Run without a timeout, and only once per test case. Defaults to False. |
| `lang` | Which language to evaluate: '*', 'py' or 'c'. Defaults to '*'. |
| `runs` | Number of times to run each solution per test case, useful for timing. Defaults to 1. |
| `show` | Append '--show' to the arguments passed to each solution, so it prints its own diagnostics. Defaults to False. |
| `solution_index` | Evaluate only this solution index. None evaluates every solution. Defaults to None. |
| `verbose` | Print error detail as each solution runs. Defaults to False. |

*Defined in* `solver.core.evaluate.evaluate`.

---

#### Command: `gh-merge` (`merge`)

List the open pull requests, or rebase-merge one onto master.

* ⚑ needs maintainer or above.
* ✎ asks for anything you leave out.
* » supports --silent to suppress output.

`list` (the default) shows what is waiting: number, title, branch. `merge` lands one
of them, named by number and offered as a menu when you leave it out. Merging is how a
collaborator's `user/<slug>` branch reaches master, each of its commits replayed onto
the tip; their next `git-sync` then rebases those already-applied commits away and
prunes the merged branch. It also **dismisses the notice** `git-push` filed for that
branch — the message asked for this review, and it is done.

Every file in the pull request must sit inside the allowlist: `solutions/`, `docs/`,
`topics/`, and the specific files the `update` target names — which is exactly what
`git-commit` can stage. One file outside it refuses the whole request. That is the
gate, and the only one: a request may carry as many commits, across as many targets,
as the work needed. What makes this a maintainer's command rather than an admin's is
that everything in it came from a commit verb they know the shape of; a branch that
also edits the framework, the scripts, or the keys is asking for something else
entirely, and belongs on GitHub in front of an admin who has read it.

Aliased as `merge`.

**usage**

```
gh-merge
[action=list|merge] (default list)
[pr_number=<int>] (asked)
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | 'list' shows the open queue; 'merge' lands one request. Defaults to 'list'. |
| `pr_number` | Which pull request to merge, by number. Offered as a menu of the open requests when omitted, so the number never has to be typed out; only ever required for `merge`. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.gh_merge`.

---

#### Command: `git-audit` (`audit`)

Audit what git actually stores, across the whole tracked tree.

* ⚑ needs contributor or above.
* » supports --silent to suppress output.

Two checks, each reading every tracked blob straight from the object store (so
no smudge filter runs): every file under `solutions/private` is stored as
ciphertext, and no file anywhere is a compiled binary. Both run even when the
first fails; a non-zero exit means one of them found something.

This is the periodic full sweep, and it takes ~25s. The git hooks run the same
two checks scoped to the blobs at hand — `git-hooks` (pre-commit) audits what
you staged, pre-push audits what the push would add — so committing and pushing
stay fast. The cost of that scoping is that neither hook re-examines history
already on origin; this is the command that does.

Aliased as `audit`.

**usage**

```
git-audit
[details=true|--details]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `details` | List every file audited. Defaults to False, which reports counts only; offenders are listed by path either way. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_audit`.

---

#### Command: `git-commit` (`commit`)

Stage and commit the named targets — the one commit verb.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* ✎ asks for anything you leave out.
* » supports --silent to suppress output.

The routine "save my progress" step. With no target it commits `solution`: everything
under this problem's directory, plus `solutions/problems.json` (the progress file `mark`
rewrites), and nothing else. Naming targets widens that to whichever bodies of work you
mean, and they compose — `git-commit docs update` lands a whole `update-docs` run as one
commit, `git-commit topics` lands both legs of the tag graph together. A target with
nothing to stage contributes nothing rather than failing, so composing is cheap.

`--amend` folds the same paths into HEAD with its message untouched — the "I forgot
something" step, so a checkpoint absorbs the fix instead of growing a "fix typo" commit
behind it. It is refused once HEAD is on origin (rewriting a pushed commit needs a
force-push, so committing again is the honest step there), and is a no-op, not a failure,
when those paths are clean. A message and `--amend` are mutually exclusive: exactly one
of them says what the commit is called.

Aliased as `commit`.

**usage**

```
git-commit
[problem=<n>] (default current)
[solution|solutions|docs|topics|update ...]
[message=<str>] (asked)
[amend=true|--amend]
[reset=true|--reset]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose solution directory the `solution` target stages. Ignored by every other target. |
| `*targets` | What to stage — 'solution' (this problem plus the progress file), 'solutions' (the whole solution tree), 'docs' (the guides), 'topics' (the articles and every problem's tag leg) or 'update' (what the `update-*` verbs write outside `docs/` — the README, the module registry, the settings file, the model block, the Claude guidance). Defaults to 'solution'. |
| `message` | The commit message. Required unless `amend` is set, and asked for at the prompt when it is left out. |
| `amend` | Fold the staged changes into HEAD instead of committing, keeping its message. Defaults to False. Refused with a message, with `reset`, or once HEAD is pushed. |
| `reset` | Soft-reset to `origin/master` first, so the new commit squashes all local commits into a single checkpoint (the working tree is untouched). Defaults to False. `git-reset` is the same move without the re-commit. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_commit`.

---

#### Command: `git-filter` (`filter`)

Report or wire the transparent encryption filter for `solutions/private`.

* ⚑ needs reader or above.

`status` shows the filter wiring and whether this session can unwrap the
master key. `install` verifies master-key access first (refusing cleanly
without it — nothing is wired), registers the clean/smudge filter in this
clone's git config, and re-checks out `solutions/private` so existing
ciphertext decrypts in place. The explicit form of what `git-sync` runs
automatically after a pull that delivers key access — use it when access
arrived some other way, e.g. right after `key-reconstruct` from shares.

Aliased as `filter`.

**usage**

```
git-filter
[action=status|install] (default status)
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | 'status' reports whether the filter is configured; 'install' configures it. Defaults to 'status'. |

*Defined in* `solver.core.git.git_filter`.

---

#### Command: `git-hooks` (`hooks`)

Run the git pre-commit and (simulated) pre-push checks on demand.

* ⚑ needs contributor or above.
* » supports --silent to suppress output.

Runs the same checks the git hooks run — the pre-commit hook (whitespace,
staged artifacts, shellcheck, flake8, mypy) and a simulation of the pre-push
hook — so you can verify your changes will pass before committing or pushing.
Reports the combined pass/fail in the exit code.

Aliased as `hooks`.

**usage**

```
git-hooks
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_hooks`.

---

#### Command: `git-identity` (`identity`)

Configure your git identity and push credential from your GitHub login.

* ⚑ needs contributor or above.

The one-time setup before `git-push`: runs `gh auth login` when you are not yet
signed in (interactive device flow — works in the web shell), makes gh the git
credential helper (`gh auth setup-git`), and sets this clone's `user.name` /
`user.email` from your GitHub profile, so your commits are authored and pushed
as **you**, never as a service identity.

Aliased as `identity`.

**usage**

```
git-identity
```

*Defined in* `solver.core.git.git_identity`.

---

#### Command: `git-publish` (`publish`)

Publish changed files for named targets to the remote repository.

* ⚑ needs maintainer or above.
* » supports --silent to suppress output.

Fails if any target is not one of the accepted scopes.

**usage**

```
git-publish
[scripts|solutions|solver ...]
[dry_run=true|--dry-run]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `*targets` | Scopes of files to publish — one or more of 'scripts', 'solutions' or 'solver'. There is no `keys` scope: key material is not distributed by git any more. A holder's enc-key file is machine-local, and issuing one is `user-authorize` sending it through the message spool. Defaults to 'solutions'. |
| `dry_run` | Print the push and pull-request commands instead of running them. Defaults to False. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_publish`.

---

#### Command: `git-push` (`push`)

Push the current branch to origin as yourself, then open its pull request.

* ⚑ needs contributor or above.
* » supports --silent to suppress output.

In a per-user clone the current branch is `user/<slug>`, pushed with your own
GitHub identity — `git-identity` is the one-time setup. Landing work on master
is a maintainer's `gh-merge`, never a direct push: pushing master requires
the `admin` floor, and force-pushing it is always refused.

The PR is the second half of the push: an unreviewed branch on origin is not
work anyone has been asked for. It is skipped on master (nothing to merge into
itself) and on a branch level with origin/master (nothing to review), and a
branch that already has one open keeps it. Opening one also **messages the
maintainers** that it is waiting, so the review does not depend on somebody
thinking to look; their verb is `gh-merge merge`.

**usage**

```
git-push
[force=true|--force]
[pr=false|--no-pr]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `force` | Push with `--force-with-lease` — needed after `git-sync` rebased your branch onto a moved origin/master. Refused on master. Defaults to False. |
| `pr` | Open a pull request onto master after a successful push. Defaults to True; `--no-pr` pushes and stops there. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_push`.

---

#### Command: `git-reset` (`reset`)

Soft-reset your branch to origin/master — un-commit, keep every change.

* ⚑ needs reader or above.
* » supports --silent to suppress output.

The undo `git-commit --reset` never lets you stop at: this runs
    `git reset --soft origin/master`, moving your branch tip back to origin/master
    while leaving the working tree untouched, so every local commit's changes survive
    as staged edits. From there re-commit differently (`git-commit`), restage
    selectively, or leave it — whereas `git-commit --reset` squashes straight into one
    fresh commit and gives you no such pause.

Makes no commit, so it runs no hooks and is a clean no-op — exit 0 — when your branch
    is already level with origin/master. Undone commits are not lost: they stay
    reachable through the reflog until git eventually prunes them.

Aliased as `reset`.

**usage**

```
git-reset
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.git.git_reset`.

---

#### Command: `git-status` (`status`)

Display the sync state between the local branch and origin/master.

* ⚑ needs reader or above.

Reports how far ahead and behind your branch is, and what is uncommitted in the working
tree — the read before deciding between `git-push`, `git-sync` and `git-commit`. It is
as fresh as the last fetch; `git-sync` is what refreshes it. Aliased as `status`.

**usage**

```
git-status
[details=true|--details]
```

**arguments**

| argument | description |
|----------|-------------|
| `details` | List every differing file and uncommitted change. Defaults to False, which shows file counts only. |

*Defined in* `solver.core.git.git_status`.

---

#### Command: `git-sync` (`sync`)

Bring the local repository in sync with origin/master.

* ⚑ needs reader or above.

On a per-user clone (branch `user/<slug>`) this is the pull flow: fetch
origin/master and merge/rebase it into your branch — bringing in merged work
merged work. Key material does not travel this way -- it is issued by message
(`user-authorize` / `msg act`), and that is what wires the filter.

Stale remote-tracking refs are pruned as part of the fetch, so a branch deleted
when its pull request merged stops shadowing the branch you push next.

**usage**

```
git-sync
[dry_run=true|--dry-run]
```

**arguments**

| argument | description |
|----------|-------------|
| `dry_run` | Print the sync commands instead of running them. Defaults to False. |

*Defined in* `solver.core.git.git_sync`.

---

#### Command: `host-authorize`

Mail the master key, sealed to one machine's public key — the off-host grant.

* ⚑ needs admin.
* ✎ asks for anything you leave out.

`key-split` needs both halves to be reachable: the sealed message, and the half sitting on
this host. A machine that is not *on* this host has no second half, so there is nothing to
complete — and the spool cannot reach it either. This is that case, and it trades the
split's third factor for a channel that actually arrives: the whole master key, sealed to
the machine's public key so it is inert to the mail provider and to every mailbox it
passes through, delivered by e-mail with a marked block to copy.

The far end runs `host-unlock` and pastes the block. Nothing is recorded here and nothing
is registered: an off-host machine has no account, no slug and no instance — which is why
this asks for a public key rather than an identity.

Mail is submitted through the loopback relay from **this terminal**, which the egress
firewall permits for the operator's uid and bars for every per-user one. When the relay
cannot be reached the block is printed instead, so the grant is never lost to a mail
problem — send it yourself, by any channel you trust.

**usage**

```
host-authorize
[public_key=<str>] (asked)
[email=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `public_key` | The 64-hex X25519 public key of the machine being authorized — what `user` prints there. |
| `email` | Where to send it. Their address, or your own if you intend to forward it by another route. |

*Defined in* `solver.crypto.keys.host_authorize`.

---

#### Command: `host-unlock`

Take the mailed block from `host-authorize` and unlock this machine.

* ⚑ needs admin.
* ✎ asks for anything you leave out.

The receiving half of the off-host grant, and the same proof as every other way in: the
payload must unwrap with **this machine's** private key and its `verify` must decrypt to
the known text. Only then does it replace what is here — the file it overwrites may be the
only thing between this machine and the whole private tree, so a bad or mistargeted block
has to fail before the write, not be discovered after it.

Paste everything between the markers; the surrounding prose is ignored, and so is whatever
the mail client did to the line breaks.

**usage**

```
host-unlock
[payload=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `payload` | The block from the mail. Asked for over several lines when it is not given — end with a blank line. |

*Defined in* `solver.crypto.keys.host_unlock`.

---

#### Command: `key-reconstruct`

Unwrap the half you were sent, complete it from the repository, store the key.

* ⚑ needs reader or above.
* ✎ asks for anything you leave out.

What `msg act` does with a `key-split` message, and what to run by hand when the share
reached you some other way. The half sent to you is **sealed to your public key**, so
only this machine's private key opens it; the other half is the one this machine already
holds (`/etc/euler/share.json` on the host). The reconstructed key is proved before
anything is written, and then stored wrapped to your public key. Needs a private key
already in place: run `user` first.

**usage**

```
key-reconstruct
[share=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `share` | The share from your message — the wrapped blob as sent, or a bare 262-hex share handed to you out of band. Asked for when it is not given. |

*Defined in* `solver.crypto.keys.key_reconstruct`.

---

#### Command: `key-rekey` (`rekey`)

Rotate the master key and re-issue it to every registered public key.

* ⚑ needs admin.

**Revocation lives here, and it is the only thing that revokes.** Dropping somebody's
access means rotating the key they hold and re-issuing the new one to everyone else.

The list of who "everyone else" is comes from the **roster** — each holder's `public_key`
in `/etc/euler/roster/users.json`, written by the grant that issued to them. It used to be
implicit in the shared enc-key file: every authorised key was in it, so a rekey re-wrapped
what it found. With one file per machine there is nothing central to read, so the registry
is explicit — and it holds only *public* keys, which is why losing it costs nothing but a
round of re-authorization.

Each holder is sent their own payload through the message spool, exactly as
`user-authorize` does; they run `msg act` on it to take it. An account with no registered
public key cannot be re-issued to and is named, not skipped silently — that person loses
access at this rotation, which is sometimes the intent and must never be a surprise.

Because the git filter is deterministic, every committed blob depends on the master key, so
a rotation re-encrypts the tracked private files via `git add --renormalize`.

**usage**

```
key-rekey
```

*Defined in* `solver.crypto.keys.key_rekey`.

---

#### Command: `key-split`

Send someone half the master key, sealed to their public key.

* ⚑ needs maintainer or above.
* ✎ asks for anything you leave out.

Two halves of a 2-of-2 split, and **neither is worth anything alone**. One sits on this
host (`/etc/euler/share.json`, readable by every uid there and written only by the
operator); the other is minted per recipient, **sealed to that recipient's X25519 public
key** — read from the roster — and sent through the message spool, which they take
with `msg act`: that runs `key-reconstruct`, unwraps their half, puts the two together,
and writes their enc-key file.

So a delivery has three independent parts and an attacker needs all of them: the message,
the private key that opens it, and access to the host. That is the difference from an
issued key, which is inert without the private key and nothing more — a stolen `~/.euler`
plus a copy of the spool is enough for one and not for the other.

The first run is the host's: with no local half yet (or one that predates the current
master key) this **writes it and stops**, so nobody is sent a half they could not
complete. Run it again to send. Off this host there is no shared half at all — use
`host-authorize`.

**usage**

```
key-split
[identity=<str>] (asked)
[public_key=<str>] (default '')
```

**arguments**

| argument | description |
|----------|-------------|
| `identity` | Who to send the other half to. Not asked — and not used — on the run that writes the repository's share. |
| `public_key` | The recipient's 64-hex public key, for somebody the roster has no key for yet — a first grant, before anyone has been authorised. Defaults to '', which reads it from the roster. |

*Defined in* `solver.crypto.keys.key_split`.

---

#### Command: `lint`

Lint the problem's solution files, optionally auto-fixing them.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Checks the current problem's solution files for style and quality issues
(flake8, plus the configured checks). Reports any findings and reflects them
in the exit code.

**usage**

```
lint
[problem=<n>] (default current)
[auto_fix=true|--auto-fix]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose solution files to lint. |
| `auto_fix` | Fix what can be fixed in place — autoflake (unused imports and variables), autopep8 (style) and isort (import order) — then re-check. Defaults to False, which only reports. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.utils.linter.lint`.

---

#### Command: `ls`

List the files in a problem's solution directory.

* ⚑ needs reader or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Walks the directory recursively and prints each file's canonical path, size, modified
time and MIME type, sorted by path; a solution file (`pNNNN_sK.*`) is flagged with a
trailing `*`. Files with no extension are skipped. Fails when the directory holds
nothing to list.

**usage**

```
ls
[problem=<n>] (default current)
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose solution directory to list. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.list.ls`.

---

#### Command: `mark` (`mark-solved`)

Mark the current problem as solved — once its results confirm it.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Records the current problem as solved (with today's date) in
`problems.json`, the same state `summary` maintains, so `{solved}`,
`progress`, and `solved` reflect it without re-importing the progress page.

It only proceeds after checking the recorded results: there must be a
selected problem, its `test_cases.json` must have a `main` case with an
answer, and `results.json` must contain a `correct` verdict for that `main`
case. Run `benchmark` (which records results) first; a problem already
marked solved is left unchanged.

Aliased as `mark-solved`.

**usage**

```
mark
[problem=<n>] (default current)
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem to mark solved. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.utils.summary.mark`.

---

#### Command: `msg` (`messages`)

Read and send messages: what is waiting for you, and what it asks you to do.

* ⚑ needs reader or above.
* ✎ asks for anything you leave out.

Every message has staff (`maintainer`+) at one end: you can ask them something,
they can answer, and they can send notices. There is deliberately no user-to-user
messaging. Delivery is asynchronous — the spool holds the message until you read it.

Five verbs, and each is one thing a person does with a message. `act` is the one worth
knowing: a message *knows* what it is for, so acting on one takes the key it carries,
grants the key it asks for, or merges the pull request it announces — and on anything
else it simply reads it. The header's message chip labels its rows from the same rule.

Typed bare, it walks you through the rest: pick a verb, then whatever that verb needs —
a message from your own list, or a subject and a body. Every answer can be given on the
command line instead, and a non-interactive shell asks nothing.

**usage**

```
msg
[action=list|read|send|dismiss|act] (asked)
[thread=<str>] (asked)
[subject=<str>] (asked)
[body=<str>] (asked)
[to=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | What to do — `list` everything waiting for you, newest first; `read` one message and mark it read; `send` a message; `dismiss` one you are done with; `act` on one, doing what it asks. Defaults to `list`. |
| `thread` | The message to act on, for `read` / `dismiss` / `act`. Offered as a menu of your own messages, so the id never has to be typed out. |
| `subject` | The subject line, for `send`. |
| `body` | The message text, for `send`. |
| `to` | Who a `send` goes to: `staff` (the default, and the only audience below the `maintainer` floor), `everyone`, or one or more identities, comma-separated. Staff are offered the known accounts as a menu where the roster can be read. |

*Defined in* `solver.web.msg.commands.msg`.

---

#### Command: `new`

Generate new solution and/or test-case files for the problem.

* ⚑ needs contributor or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

Solution files are named from the problem number and the next free solution
index (e.g. "p0001_s0.py", "p0001_s1.py") and are created from the boilerplate
template with the problem information substituted; Python files are made
executable (mode 0o755).

With neither `py` nor `c` given (and `tc` False), both a Python and a C file are
created.

**usage**

```
new
[problem=<n>] (default current)
[py=true|--py]
[c=true|--c]
[tc=true|--tc]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem to create files for. |
| `py` | Create a Python solution file. Defaults to False. |
| `c` | Create a C solution file — one per existing Python solution that lacks a matching ".c". Defaults to False. |
| `tc` | Create an empty test-cases file instead of solution files, unless one already exists. Defaults to False. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.new.new`.

---

#### Command: `pause`

Wait for the user to press Enter before the block carries on.

* ⚑ needs reader or above.

A beat in a command block — after a `show`, or between the steps of a walkthrough. With
nobody to wait for (a pipe, `< /dev/null`, `--silent`) it is a no-op rather than an error,
so a block that pauses is still scriptable.

**usage**

```
pause
```

*Defined in* `solver.utils.shell_utils.pause`.

---

#### Command: `pip-upgrade` (`upgrade`)

Upgrade packages in the current venv for the given dependency groups.

* ⚑ needs admin.

Groups are defined in pyproject.toml:   'core' for project.dependencies,
                                        'ai', 'dev', 'solutions', 'show' for optional-dependencies,
                                        'all' to upgrade everything.
                                        Defaults to 'all'.

**usage**

```
pip-upgrade
[all|ai|core|dev|solutions|show ...]
```

**arguments**

| argument | description |
|----------|-------------|
| `*groups` | One or more dependency group names, or 'all'. |

*Defined in* `solver.utils.scripts.pip_upgrade`.

---

#### Command: `problems`

Print a list of problems and their count.

* ⚑ needs reader or above.

The set comes from `problems.json`, the state `summary` imports from your Project Euler
progress page and `mark` updates as you solve — so "solved" means recorded there, not
merely present on disk.

**usage**

```
problems
[which=all|solved|unsolved] (default all)
```

**arguments**

| argument | description |
|----------|-------------|
| `which` | Which set to list — 'all' every known problem, 'solved' those with a recorded answer, 'unsolved' those without. Mirrors the `{problems}` / `{solved}` / `{unsolved}` shell variables. Defaults to 'all'. |

*Defined in* `solver.utils.misc.problems`.

---

#### Command: `progress`

Print overall progress through the Euler problems.

* ⚑ needs reader or above.

Shows a bar of solved vs. unsolved problems, the solved count and
percentage of the total known problems, and the next problem to solve (the
lowest-numbered unsolved one). Reads the state maintained by `summary`; run
`summary` first if your progress looks out of date.

**usage**

```
progress
```

*Defined in* `solver.utils.summary.progress`.

---

#### Command: `results`

List the recorded results for a problem.

* ⚑ needs reader or above.
* ❏ uses/sets current problem.

Reads the `results.json` that `benchmark` (and `eval --record`) writes in the problem's
solution directory, and prints one line per recorded run — verdict, average time, run
count, solution and arguments. Fails when there is no results file to read.

**usage**

```
results
[problem=<n>] (default current)
[all|dev|main|extra ...]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose results to list. |
| `*categories` | Test-case categories to include: 'dev', 'main', 'extra', or 'all' (which expands to all three). Defaults to all three. |

*Defined in* `solver.core.results.results`.

---

#### Command: `search` (`find`)

Search the solution stack for a case-insensitive regular expression.

* ⚑ needs reader or above.

For every problem in scope, each matching stack file is read (decrypted as
needed) and scanned line by line; every matching line is printed as
'<stack-dir>/<file>:<line> <text>' with the matched substring highlighted.
A blank line separates the matches of one problem from the next.

**usage**

```
search <query>
[*|py|c|html|json ...]
[scope=problems|solved] (default solved)
```

**arguments**

| argument | description |
|----------|-------------|
| `query` | Regular expression to search for, matched case-insensitively against each line (`re.search`, so it need not match the whole line). |
| `*files` | File extensions to include, without the leading dot. Defaults to 'py' and 'html'; '*' expands to the full set 'py c html json'. |
| `scope` | Which problems to search: 'solved' restricts to solved problems, 'problems' covers every known problem. Defaults to 'solved'. |

*Defined in* `solver.utils.search.search`.

---

#### Command: `show` (`open`, `view`)

Open a problem's documentation page, in a browser or the web viewer panel.

* ⚑ needs reader or above.
* ❏ uses/sets current problem.
* » supports --silent to suppress output.

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

**usage**

```
show
[problem=<n>] (default current)
[filename=<str>|none] (default None)
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem to open. |
| `filename` | A solution file to open in the code editor instead. Defaults to None, which opens the rendered documentation page. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.core.viewer.show`.

---

#### Command: `summary`

Refresh the solved/unsolved state from your Project Euler progress page.

* ⚑ needs maintainer or above.
* » supports --silent to suppress output.

Parses `solutions/.progress.html` (the saved Page Source of your
authenticated https://projecteuler.net/progress page) and updates
`problems.json` with which problems are solved and their metadata. This is
how the shell learns your real progress, driving `{solved}` / `{unsolved}`,
`progress`, and `solved`.

The import only ever **adds** solved problems: a problem `mark` recorded as solved
keeps that record, and its date, even when the page does not show it as solved —
which is the normal state of a problem solved here but whose answer has not been
registered on projecteuler.net yet. Each such disagreement is reported, and staff
are sent a message naming the problems.

Returns an error (with instructions) if `.progress.html` is missing: visit
the progress page, copy its Page Source into that file, and retry.

**usage**

```
summary
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.utils.summary.summary`.

---

#### Command: `sys-setup` (`install`)

Install or uninstall a system resource.

* ⚑ needs admin.
* ✎ asks for anything you leave out.

Runs the setup script for *target* under `sudo`, after confirming. Each script is
idempotent, so re-running an install is safe.

**usage**

```
sys-setup
[target=chrome|dev-env|upgrade-service] (asked)
[uninstall=true|--uninstall]
[show_help=true|--show-help]
```

**arguments**

| argument | description |
|----------|-------------|
| `target` | Which resource to act on: 'chrome', 'dev-env' or 'upgrade-service'. Offered as a menu when omitted. |
| `uninstall` | Uninstall the target instead of installing it. Defaults to False. |
| `show_help` | Print the target script's own help and stop, doing nothing else. Defaults to False. |

*Defined in* `solver.utils.scripts.sys_setup`.

---

#### Command: `tags`

Report over the central tag vocabulary (`topics/tags.json`).

* ⚑ needs reader or above.

The vocabulary's own shape, not any one problem's tags: how many tags each facet
(domain, technique, takeaway) defines, and — with `--details` — how evenly the problems
are spread across them, which is what shows a tag that has grown too broad or too
narrow to be worth an article. Use `topic <name>` for one tag's problems.

**usage**

```
tags
[details=true|--details]
```

**arguments**

| argument | description |
|----------|-------------|
| `details` | Add, per facet, a histogram of how many problems each tag maps to — min / median / max, then binned counts. Defaults to False, which prints just the number of tags in each facet. |

*Defined in* `solver.core.tags.tags`.

---

#### Command: `test-cases`

List a problem's test cases.

* ⚑ needs reader or above.
* ❏ uses/sets current problem.

Reads the problem's `test_cases.json` and prints one line per case — category,
arguments and expected answer — for the categories asked for. URL arguments are
abbreviated to their final path segment.

**usage**

```
test-cases
[problem=<n>] (default current)
[all|dev|main|extra ...]
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose test cases to list. |
| `*categories` | Test-case categories to include: 'dev', 'main', 'extra', or 'all' (which expands to all three). Defaults to all three. |

*Defined in* `solver.core.test_cases.test_cases`.

---

#### Command: `topic`

List a topic article's declared tags and what each one maps to.

* ⚑ needs reader or above.
* ✎ asks for anything you leave out.

Reads the article's `<!-- tags: [...] -->` declaration and, for each slug, prints its
facet and the problem/solution refs recorded on the central vocabulary's leg — the
other half of the double-entry graph `update-tags` keeps in step. Fails when no article
matches.

**usage**

```
topic
[name=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `name` | The article to report on: a `folder/leaf` path under `topics/`, or a bare leaf name when it is unambiguous. Offered as a menu when omitted; not strict, so a leaf name still works. |

*Defined in* `solver.core.tags.topic`.

---

#### Command: `topics`

List a problem's tags and the topic articles that cover them.

* ⚑ needs reader or above.
* ❏ uses/sets current problem.

Reads the problem's own `tags.json` — grouping the tags by facet (domain, technique per
solution index, takeaway) — then names every article under `topics/` that declares any
of them. Fails when the problem has no `tags.json`; `update-tags` reports which
problems are missing one.

**usage**

```
topics
[problem=<n>] (default current)
```

**arguments**

| argument | description |
|----------|-------------|
| `problem` | The problem whose tags to list. |

*Defined in* `solver.core.tags.topics`.

---

#### Command: `update-docs`

Rebuild the registry-generated blocks in the `docs/` guides and the README.

* ⚑ needs admin.
* » supports --silent to suppress output.

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

What it rewrote is committed — the guides, the README, the module registry, the
start-page summary and the Claude guidance, and nothing beside them.

**Admin-floored on purpose, not out of caution.** Registration is itself
profile-filtered (`solver/shell/command.py`): a command above your floor is never
registered, so `registry.all()` returns only what *you* may run. Regenerating from a
lesser profile's registry would drop every admin-floored command from the audit table
and the command index — silently, and in exactly the documents whose worth is being
complete. The floor is what keeps the generated view whole.

**usage**

```
update-docs
[check=true|--check]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `check` | Write nothing and fail if any doc is out of date, listing the stale files. Defaults to False, which rewrites the docs in place and reports which changed. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.utils.update_doc.update_docs`.

---

#### Command: `update-models`

Refresh the model catalogue and its pricing.

* ⚑ needs admin.
* » supports --silent to suppress output.

Lists the available Claude models from the Anthropic Models API, scrapes each model's base
input/output price (per million tokens) from the public pricing page, and rewrites the
`# GEN:models` block in `models.py` — the enum members, their inline comments, and the
`price` map. Curated per-model comments are kept; a newly discovered model is commented
with its display name. Nothing outside the markers is touched, and the USD→EUR rate is
`update-usd-rate`'s to refresh.

The header's date says when the catalogue last **changed**, not when it was last looked
at: a run that finds nothing new writes nothing, so `--check` passes on any day the
models and their prices have not moved.

A regenerated block is committed, staging `models.py` and nothing beside it.

**usage**

```
update-models
[check=true|--check]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `check` | Write nothing and fail if the generated block is out of date. Defaults to False, which rewrites it in place. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.ai.update_models.update_models`.

---

#### Command: `update-tags`

The glue for the double-entry tag graph.

* ⚑ needs contributor or above.

Order (maintainer beats solver/contributor): apply maintainer edits to the central
vocabulary (vs HEAD) into the per-problem files first; promote `new-tags` proposals into
the vocabulary; rebuild every central `refs` leg from the per-problem files; regenerate
the topic articles' problem lists and rewrite the article index `topics/articles.json`
(one row per writable topic: title, status, solved/problem counts, tags and refs). A
problem with notes but no `tags.json` is reported, not created here — the
`claude-api tags` target (or the skill) authors it.

The reconciled graph is committed — both legs together, and nothing beside them.

**usage**

```
update-tags
[check=true|--check]
```

**arguments**

| argument | description |
|----------|-------------|
| `check` | Write nothing: report unknown slugs, facet violations, unpromoted proposals, missing files and a stale article index, and fail if the graph is inconsistent. Defaults to False, which reconciles the graph in place. |

*Defined in* `solver.core.tags.update_tags`.

---

#### Command: `update-usd-rate`

Refresh the USD→EUR rate used to report API costs.

* ⚑ needs maintainer or above.
* » supports --silent to suppress output.

Fetches the euro reference rate from the European Central Bank's daily feed and writes it
to `ecb_usd_rate` in `values.conf`, the setting `costs` converts API spend with.
A rate within a rounding step of the stored one is left alone. Nothing else is touched.

A rate that moved is committed, staging that one file and nothing beside it.

**usage**

```
update-usd-rate
[check=true|--check]
[silent=true|--silent]
```

**arguments**

| argument | description |
|----------|-------------|
| `check` | Write nothing and fail if the stored rate is out of date. Defaults to False, which refreshes it in place. The rate drifts daily, so `--check` will usually report it as stale. |
| `silent` | Suppress this command's output; errors and the result line still show. |

*Defined in* `solver.ai.update_usd_rate.update_usd_rate`.

---

#### Command: `user`

Show the solver user, the current identity, and whether it can decrypt.

* ⚑ needs reader or above.

A key pair is created only when the identity file is **truly absent** (first run) or on
an explicitly confirmed `--regen`. An id file that *exists but cannot be read* — the
vault is locked, the session key is stale, the vault file was lost — is a **vault
failure to fix, never a reason to mint a new identity**: replacing the key would
silently orphan the real one, and with it any enc-key authorization it carries.

**usage**

```
user
[regen=true|--regen]
```

**arguments**

| argument | description |
|----------|-------------|
| `regen` | Replace the existing key pair with a fresh one, after confirmation, and re-wrap the master key to it. Defaults to False. |

*Defined in* `solver.crypto.keys.user`.

---

#### Command: `user-authorize` (`authorize`)

Record someone's public key and send them half the master key.

* ⚑ needs maintainer or above.
* ✎ asks for anything you leave out.

*target* is either form of the same act, told apart by shape:

- a **16-hex message id** — the key-authorization request their `user` command filed
  (`msg list` shows them). The key and the requester come from that message, the grant
  is confirmed, the half is sent as **its own message** for them to `msg act` on, and the
  request is dismissed — it is worked, and a queue that keeps worked requests is a queue
  nobody trusts;
- a **64-hex public key** — the same act by hand, for a key that reached you some other
  way. *identity* names who to send it to.

Two things happen, and the first is the durable one. The public key is written to the
**roster** (`/etc/euler/roster/users.json`), which is what a later rotation re-issues
against and what every shell — terminal or web — can read without `sudo`. Then delivery goes
through `key-split`: half the master key, sealed to that public key, against the half the
repository already carries. So a grant is never one artefact — the message, the private
key that opens it and a current clone are all needed, and the recipient's own
`key-reconstruct` proves the result before it writes anything.

That is why this needs the repository's half to be **committed and pushed first**: it
refuses rather than sending a half nobody can complete. `key-split` on its own lays that
half down. Aliased as `authorize`.

**usage**

```
user-authorize
[target=<str>] (asked)
[identity=<str>] (asked)
```

**arguments**

| argument | description |
|----------|-------------|
| `target` | The 16-hex id of a key-authorization message, or a 64-hex public key. Offered as a menu of the waiting requests when omitted; not strict, so a bare key can still be pasted. |
| `identity` | Who the key belongs to. Taken from the thread for the message form, so it is only asked for the bare-key form — where there is nobody to send it to otherwise. |

*Defined in* `solver.crypto.keys.user_authorize`.

---

#### Command: `users`

Administer accounts on the authorization map + the auth service.

* ⚑ needs admin.
* ✎ asks for anything you leave out.

The whole command is `admin`-floored and the account verbs re-execute the admin CLI
under `sudo` (the SoR + admin socket are root-only). There is no reader/maintainer
tier here — a web shell cannot get sudo, so nothing runs over the web.

Every account verb writes **both** places it needs to: the host's system of record
(profile, SRP state) through the sudo'd admin CLI, and the roster
(`/etc/euler/roster/users.json`) for the parts every rung must be able to read without
`sudo`. There is no separate registration step and no sweep to remember: a public key is
recorded by the grant that issues one (`user-authorize`), and `list` says so when the two
have drifted.

**usage**

```
users
[action=list|process-requests|add|change|enable|disable|remove|redeploy] (default list)
[identity=<str>] (asked)
[profile=reader|contributor|maintainer|admin] (default reader)
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | What to do — `list` the roster, pending invites and the invite-request queue; `process-requests` walks that queue interactively (accept / ignore / dismiss each); `add` a map entry (`@email` also provisions the account and mints an invite, a bare os-login is local-only); `change` reassigns a profile; `enable` / `disable` the web SRP state; `remove` drops the account or entry; `redeploy` re-asserts the per-user host layer and re-lays every collaborator's git hooks, dropping live shells. Defaults to `list`. |
| `identity` | Whose account to act on: a web email (with `@`) or a local OS login. Offered as a menu of the roster for the verbs that act on an account that already exists — `change` / `enable` / `disable` / `remove` — and not asked for the others, since `add` names one that does not yet and `list` / `process-requests` / `redeploy` name none. |
| `profile` | The profile to assign, for `add` / `change`. `admin` is valid only for a local os-login, never a web account. |

*Defined in* `solver.web.auth.commands.users`.

---

#### Command: `vault`

Encrypt this user's `id` + `env` at rest under a password-derived vault key.

* ⚑ needs reader or above.

- `status` (default): show whether the vault exists, which secret files are encrypted, and
  whether this session can decrypt them.
- `init`: create the vault and migrate the existing plaintext `id`/`env` into it in place, then
  unlock the current session. Prompts for a new password.
- `unlock`: unlock a locked session (the shell asks at startup; this is the retry — after a
  typo, or once you have the password to hand).
- `change-password`: re-wrap the vault key under a new password (the secrets are not
  re-encrypted).

The password is never stored: set `$EULER_VAULT_PASSWORD` for a non-interactive unlock
(a script, CI), otherwise you are asked once per shell.

**usage**

```
vault
[action=status|init|unlock|change-password] (default status)
```

**arguments**

| argument | description |
|----------|-------------|
| `action` | Which of the four operations above to run. Defaults to 'status'. |

*Defined in* `solver.crypto.keys.vault`.

---

#### Command: `version`

Print the installed build version, plus live git detail of the clone.

* ⚑ needs reader or above.

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

**usage**

```
version
```

*Defined in* `solver.utils.version.version`.
<!-- /GEN:command-index -->
