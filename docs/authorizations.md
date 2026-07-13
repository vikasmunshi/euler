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
- **Channels** — where the command is reachable (`terminal` / `web`).
- **Requires** — the `object:permission` grants the command declares. A command
  that declares nothing is fail-closed to `infra:execute` (admin-only).
- **Least profile** — the least-privileged profile whose expanded permissions
  satisfy every required grant; any profile at or above it may run the command.

## Command authorization

<!-- GEN:authorization-table -->
| Module | Command | Channels | Requires | Least profile |
|--------|---------|----------|----------|---------------|
| `solver.ai.api` | `claude-api` | terminal, web | `ai:execute` | `maintainer` |
| `solver.ai.models` | `costs` | terminal, web | `solver:execute` | `reader` |
| `solver.ai.skill` | `claude-skill` | terminal, web | `ai:execute` | `maintainer` |
| `solver.ai.update_models` | `update-models` | terminal | `infra:execute` | `admin` |
| `solver.core.evaluate` | `benchmark` | terminal, web | `solutions:execute` | `contributor` |
| `solver.core.evaluate` | `compile-c` | terminal, web | `solutions:execute` | `contributor` |
| `solver.core.evaluate` | `evaluate` | terminal, web | `solutions:execute` | `contributor` |
| `solver.core.list` | `ls` | terminal, web | `solutions:read` | `reader` |
| `solver.core.new` | `new` | terminal, web | `solutions:write` | `contributor` |
| `solver.core.results` | `results` | terminal, web | `solutions:read` | `reader` |
| `solver.core.test_cases` | `test-cases` | terminal, web | `solutions:read` | `reader` |
| `solver.core.viewer` | `edit` | terminal, web | `solutions:write` | `contributor` |
| `solver.core.viewer` | `show` | terminal, web | `solutions:read` | `reader` |
| `solver.crypto.keys` | `key-reconstruct` | terminal, web | `infra:execute` | `admin` |
| `solver.crypto.keys` | `key-rekey` | terminal, web | `infra:execute` | `admin` |
| `solver.crypto.keys` | `key-split` | terminal, web | `infra:execute` | `admin` |
| `solver.crypto.keys` | `user` | terminal, web | `infra:execute` | `admin` |
| `solver.crypto.keys` | `user-authorize` | terminal, web | `infra:execute` | `admin` |
| `solver.shell.bash` | `!` | terminal, web | `shell:execute` | `admin` |
| `solver.shell.builtins` | `?` | terminal, web | `solver:execute` | `reader` |
| `solver.shell.builtins` | `clear` | terminal, web | `solver:execute` | `reader` |
| `solver.shell.builtins` | `echo` | terminal, web | `solver:execute` | `reader` |
| `solver.utils.linter` | `lint` | terminal, web | `solutions:write` | `contributor` |
| `solver.utils.misc` | `manage-config` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.misc` | `problems` | terminal, web | `solutions:read` | `reader` |
| `solver.utils.scripts` | `git-commit` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-hooks` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-publish` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-status` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `git-sync` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `pip-upgrade` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.scripts` | `sys-setup` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.search` | `search` | terminal, web | `solutions:read` | `reader` |
| `solver.utils.shell_utils` | `pause` | terminal, web | `solver:execute` | `reader` |
| `solver.utils.summary` | `mark` | terminal, web | `solutions:execute` | `contributor` |
| `solver.utils.summary` | `progress` | terminal, web | `solutions:read` | `reader` |
| `solver.utils.summary` | `summary` | terminal, web | `infra:execute` | `admin` |
| `solver.utils.update_doc` | `update-docs` | terminal | `infra:execute` | `admin` |
| `solver.web.auth.commands` | `users` | terminal | `users:read` | `reader` |
<!-- /GEN:authorization-table -->
