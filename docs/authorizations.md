# Authorizations

The **authorization audit** for the shell and web command surface: every registered
command, the module it lives in, and which rungs may run it — authorization is a
plain rank comparison on the ladder `reader` → `contributor` → `maintainer` →
`admin`.

The table below is **generated from the live command registry** by the
`update-docs` command — do not edit it by hand. It mirrors each command's
`@register(requires='<profile>')` declaration; run `update-docs` after changing
any command's `requires`, name, or module.

`update-docs` is **admin-floored**, and this table is why. Registration is itself
profile-filtered — a command above your floor is never registered — so the registry
a lesser profile sees omits the admin-floored commands, and regenerating from it
would drop those rows silently, in the very document whose value is being complete.
Only an admin's registry holds the whole command set, so the audit is never
truncated.

This is the **audit view** — who holds which profile is decided in the deployed
system of record at `/etc/euler/authorizations.json` (root-owned, outside the
repo, mutated only through the sudo-gated `users` command). There is no policy
file in the repo: absent a deployed one, the built-in default maps nobody and the
checkout owner floors to `admin` by uid. See the
[web server guide](web-server-guide.md) for the model and how identity resolves to
a profile on each channel.

## Columns

- **Module** — the Python module the command is defined in.
- **Command** — the registered command name.
- **Reader · Contributor · Maintainer · Admin** — a `✓` on every rung that may
  run the command: those at or above its declared `requires` floor. Because the
  check is a rank comparison, each row is a run of ticks from its floor
  rightwards — a gap would be a bug. `requires` is mandatory on the decorator, so
  every command has a floor; none can be exposed by omitting one.

## Command authorization

<!-- GEN:authorization-table -->
| Module | Command | Reader | Contributor | Maintainer | Admin |
|--------|---------|:------:|:-----------:|:----------:|:-----:|
| `solver.ai.api` | `claude-api` |  | ✓ | ✓ | ✓ |
| `solver.ai.batch` | `claude-batch` |  |  | ✓ | ✓ |
| `solver.ai.models` | `costs` |  | ✓ | ✓ | ✓ |
| `solver.ai.skill` | `claude-blog` |  |  | ✓ | ✓ |
| `solver.ai.skill` | `claude-solve` |  | ✓ | ✓ | ✓ |
| `solver.ai.update_models` | `update-models` |  |  | ✓ | ✓ |
| `solver.core.evaluate` | `benchmark` |  | ✓ | ✓ | ✓ |
| `solver.core.evaluate` | `compile-c` |  | ✓ | ✓ | ✓ |
| `solver.core.evaluate` | `evaluate` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `gh-merge` |  |  | ✓ | ✓ |
| `solver.core.git` | `gh-merge-docs` |  |  | ✓ | ✓ |
| `solver.core.git` | `git-audit` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-commit` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-commit-amend` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-commit-docs` |  |  | ✓ | ✓ |
| `solver.core.git` | `git-filter` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-hooks` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-identity` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-publish` |  |  |  | ✓ |
| `solver.core.git` | `git-push` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-status` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-sync` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.list` | `ls` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.new` | `new` |  | ✓ | ✓ | ✓ |
| `solver.core.results` | `results` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `create-topic` |  |  | ✓ | ✓ |
| `solver.core.tags` | `tags` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `topic` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `topics` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `update-tags` |  |  | ✓ | ✓ |
| `solver.core.test_cases` | `test-cases` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.viewer` | `edit` |  | ✓ | ✓ | ✓ |
| `solver.core.viewer` | `show` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `key-reconstruct` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `key-rekey` |  |  |  | ✓ |
| `solver.crypto.keys` | `key-split` |  |  |  | ✓ |
| `solver.crypto.keys` | `user` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `user-authorize` |  |  |  | ✓ |
| `solver.crypto.keys` | `vault` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.bash` | `!` |  | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `?` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `clear` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `echo` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.linter` | `lint` |  | ✓ | ✓ | ✓ |
| `solver.utils.misc` | `manage-config` |  |  |  | ✓ |
| `solver.utils.misc` | `problems` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.scripts` | `pip-upgrade` |  |  |  | ✓ |
| `solver.utils.scripts` | `sys-setup` |  |  |  | ✓ |
| `solver.utils.search` | `search` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.shell_utils` | `pause` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.summary` | `mark` |  | ✓ | ✓ | ✓ |
| `solver.utils.summary` | `progress` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.summary` | `summary` |  |  | ✓ | ✓ |
| `solver.utils.update_doc` | `update-docs` |  |  |  | ✓ |
| `solver.utils.version` | `version` | ✓ | ✓ | ✓ | ✓ |
| `solver.web.auth.commands` | `users` |  |  |  | ✓ |
<!-- /GEN:authorization-table -->
