# Authorizations

The **authorization audit** for the shell and web command surface (DD-12): every
registered command with the OS/web module it lives in, the channels it is valid
in, the `object:permission` grants it requires, and the least-privileged profile
that satisfies those grants.

The table below is **generated from the live command registry** by the
`update-docs` command — do not edit it by hand. It mirrors each command's
`@register(requires=…, channels=…)` declaration; run `update-docs` after changing
any command's `requires`, `channels`, name, or module. Because `update-docs`
itself requires `infra:execute` (admin-only), the registry it reads always holds
the complete command set, so the audit is never truncated to a lesser profile.

This is the **audit view** — the authoritative policy is
[`solver/templates/authorizations.json`](../solver/templates/authorizations.json)
(the bundled default ladder) and its deployed system of record at
`/etc/euler/authorizations.json`. See the [access-control guide](access-control.md)
for the RBAC model: the profile ladder (`reader` → `contributor` → `maintainer` →
`admin`), the `object:permission` namespace, and how identity resolves to a
profile on each channel.

## Columns

- **Module** — the Python module the command is defined in.
- **Command** — the registered command name.
- **Requires** — the `object:permission` grants the command declares. A command
  that declares nothing is fail-closed to `infra:execute` (admin-only).
- **Least profile** — the least-privileged profile whose expanded permissions
  satisfy every required grant; any profile at or above it may run the command.

## Command authorization

<!-- GEN:authorization-table -->
| Module | Command | Requires | Least profile |
|--------|---------|----------|---------------|
| `solver.ai.api` | `claude-api` | `ai:execute` | `maintainer` |
| `solver.ai.models` | `costs` | `solver:execute` | `reader` |
| `solver.ai.skill` | `euler-solve` | `ai:execute` | `maintainer` |
| `solver.ai.update_models` | `update-models` | `infra:execute` | `admin` |
| `solver.core.evaluate` | `benchmark` | `solutions:execute` | `contributor` |
| `solver.core.evaluate` | `compile-c` | `solutions:execute` | `contributor` |
| `solver.core.evaluate` | `evaluate` | `solutions:execute` | `contributor` |
| `solver.core.list` | `ls` | `solutions:read` | `reader` |
| `solver.core.new` | `new` | `solutions:write` | `contributor` |
| `solver.core.results` | `results` | `solutions:read` | `reader` |
| `solver.core.test_cases` | `test-cases` | `solutions:read` | `reader` |
| `solver.core.viewer` | `edit` | `solutions:write` | `contributor` |
| `solver.core.viewer` | `show` | `solutions:read` | `reader` |
| `solver.crypto.keys` | `key-reconstruct` | `infra:execute` | `admin` |
| `solver.crypto.keys` | `key-rekey` | `infra:execute` | `admin` |
| `solver.crypto.keys` | `key-split` | `infra:execute` | `admin` |
| `solver.crypto.keys` | `user` | `infra:execute` | `admin` |
| `solver.crypto.keys` | `user-authorize` | `infra:execute` | `admin` |
| `solver.crypto.keys` | `vault` | `infra:execute` | `admin` |
| `solver.shell.bash` | `!` | `shell:execute` | `maintainer` |
| `solver.shell.builtins` | `?` | `solver:execute` | `reader` |
| `solver.shell.builtins` | `clear` | `solver:execute` | `reader` |
| `solver.shell.builtins` | `echo` | `solver:execute` | `reader` |
| `solver.utils.linter` | `lint` | `solutions:write` | `contributor` |
| `solver.utils.misc` | `manage-config` | `infra:execute` | `admin` |
| `solver.utils.misc` | `problems` | `solutions:read` | `reader` |
| `solver.utils.scripts` | `git-commit` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-hooks` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-publish` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-status` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-sync` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `pip-upgrade` | `infra:execute` | `admin` |
| `solver.utils.scripts` | `sys-setup` | `infra:execute` | `admin` |
| `solver.utils.search` | `search` | `solutions:read` | `reader` |
| `solver.utils.shell_utils` | `pause` | `solver:execute` | `reader` |
| `solver.utils.summary` | `mark` | `solutions:execute` | `contributor` |
| `solver.utils.summary` | `progress` | `solutions:read` | `reader` |
| `solver.utils.summary` | `summary` | `infra:execute` | `admin` |
| `solver.utils.update_doc` | `update-docs` | `infra:execute` | `admin` |
| `solver.web.auth.commands` | `users` | `users:read` | `reader` |
<!-- /GEN:authorization-table -->
