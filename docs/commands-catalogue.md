# Command Catalogue

Every shell command on one page: name, aliases, the least profile that may run it, and
what it does. It is the *short* form — each name links into
[`commands-index.md`](commands-index.md), which carries the same command's full `?` panel
(usage, arguments, the whole description).

This page exists so the catalogue has **one home** rather than only a section inside
another guide: the web front end's terminal page renders it beside the shell, and the
[User Guide](user-guide.md) shows the same table in its own narrative. All three are the
same block, generated from the live registry by the `update-docs` command — do not edit
it by hand. To change what a row says, edit the command's docstring or its `@register`
declaration and run `update-docs`.

**Requires** is the least profile that may run the command; every rung above it may too,
and below it the command is not registered at all, so it does not appear in your own `?`
listing. What four columns cannot show — whether a command takes a problem number, whether
it supports `--silent`, what it asks for — is in its index entry, one click along its name.

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
| [`key-reconstruct`](commands-index.md#command-key-reconstruct) | — | `reader` | Reconstruct the master key from Shamir shares and store it for this user. |
| [`key-rekey`](commands-index.md#command-key-rekey-rekey) | `rekey` | `admin` | Rotate the master key and re-issue it to every registered public key. |
| [`key-split`](commands-index.md#command-key-split) | — | `maintainer` | Print Shamir shares of the current master key. |
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
| [`user-authorize`](commands-index.md#command-user-authorize-authorize) | `authorize` | `maintainer` | Wrap the master key for someone else and send it to them. |
| [`users`](commands-index.md#command-users) | — | `admin` | Administer accounts on the authorization map + the auth service. |
| [`vault`](commands-index.md#command-vault) | — | `reader` | Encrypt this user's `id` + `env` at rest under a password-derived vault key. |
| [`version`](commands-index.md#command-version) | — | `reader` | Print the installed build version, plus live git detail of the clone. |
<!-- /GEN:command-table -->
