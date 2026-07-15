# Authorizations

The **authorization audit** for the shell and web command surface (DD-12,
re-simplified): every registered command with the module it lives in and the
**minimum profile** it declares — authorization is a plain rank comparison on
the ladder `reader` → `contributor` → `maintainer` → `admin`.

The table below is **generated from the live command registry** by the
`update-docs` command — do not edit it by hand. It mirrors each command's
`@register(requires='<profile>')` declaration; run `update-docs` after changing
any command's `requires`, name, or module. Because `update-docs` itself is
admin-only, the registry it reads always holds the complete command set, so the
audit is never truncated to a lesser profile.

This is the **audit view** — who holds which profile is decided in
[`solver/templates/authorizations.json`](../solver/templates/authorizations.json)
(the bundled default: an empty users map) and its deployed system of record at
`/etc/euler/authorizations.json`. See the [access-control guide](access-control.md)
for the model and how identity resolves to a profile on each channel.

## Columns

- **Module** — the Python module the command is defined in.
- **Command** — the registered command name.
- **Minimum profile** — the declared floor: any profile at or above it may run
  the command. A command that declares nothing is fail-closed to `admin`.

## Command authorization

<!-- GEN:authorization-table -->
| Module | Command | Minimum profile |
|--------|---------|-----------------|
| `solver.ai.api` | `claude-api` | `contributor` |
| `solver.ai.models` | `costs` | `contributor` |
| `solver.ai.skill` | `euler-solve` | `contributor` |
| `solver.ai.update_models` | `update-models` | `admin` |
| `solver.core.evaluate` | `benchmark` | `contributor` |
| `solver.core.evaluate` | `compile-c` | `contributor` |
| `solver.core.evaluate` | `evaluate` | `contributor` |
| `solver.core.list` | `ls` | `reader` |
| `solver.core.new` | `new` | `contributor` |
| `solver.core.results` | `results` | `reader` |
| `solver.core.test_cases` | `test-cases` | `reader` |
| `solver.core.viewer` | `edit` | `contributor` |
| `solver.core.viewer` | `show` | `reader` |
| `solver.crypto.keys` | `key-reconstruct` | `reader` |
| `solver.crypto.keys` | `key-rekey` | `admin` |
| `solver.crypto.keys` | `key-split` | `admin` |
| `solver.crypto.keys` | `user` | `reader` |
| `solver.crypto.keys` | `user-authorize` | `admin` |
| `solver.crypto.keys` | `vault` | `reader` |
| `solver.shell.bash` | `!` | `contributor` |
| `solver.shell.builtins` | `?` | `reader` |
| `solver.shell.builtins` | `clear` | `reader` |
| `solver.shell.builtins` | `echo` | `reader` |
| `solver.utils.linter` | `lint` | `contributor` |
| `solver.utils.misc` | `manage-config` | `admin` |
| `solver.utils.misc` | `problems` | `reader` |
| `solver.utils.scripts` | `git-commit` | `contributor` |
| `solver.utils.scripts` | `git-hooks` | `contributor` |
| `solver.utils.scripts` | `git-identity` | `contributor` |
| `solver.utils.scripts` | `git-merge` | `admin` |
| `solver.utils.scripts` | `git-publish` | `admin` |
| `solver.utils.scripts` | `git-push` | `contributor` |
| `solver.utils.scripts` | `git-status` | `reader` |
| `solver.utils.scripts` | `git-sync` | `reader` |
| `solver.utils.scripts` | `pip-upgrade` | `admin` |
| `solver.utils.scripts` | `sys-setup` | `admin` |
| `solver.utils.search` | `search` | `reader` |
| `solver.utils.shell_utils` | `pause` | `reader` |
| `solver.utils.summary` | `mark` | `contributor` |
| `solver.utils.summary` | `progress` | `reader` |
| `solver.utils.summary` | `summary` | `admin` |
| `solver.utils.update_doc` | `update-docs` | `admin` |
| `solver.web.auth.commands` | `users` | `reader` |
<!-- /GEN:authorization-table -->
