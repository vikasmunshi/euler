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
system of record at `/etc/euler/authorizations.json` (`root:euler-authz 0640`, outside
the repo, mutated only through the sudo-gated `users` command). There is no policy
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
| `euler_webshell.msg.commands` | `msg` | ✓ | ✓ | ✓ | ✓ |
| `euler_webshell.shell.keys` | `host-authorize` |  |  |  | ✓ |
| `euler_webshell.shell.keys` | `key-split` |  |  | ✓ | ✓ |
| `euler_webshell.shell.keys` | `user-authorize` |  |  | ✓ | ✓ |
| `euler_webshell.users` | `users` |  |  |  | ✓ |
| `solver.ai.api` | `claude-api` |  | ✓ | ✓ | ✓ |
| `solver.ai.batch` | `claude-batch` |  |  | ✓ | ✓ |
| `solver.ai.models` | `costs` |  | ✓ | ✓ | ✓ |
| `solver.ai.skill` | `claude-blog` |  |  | ✓ | ✓ |
| `solver.ai.skill` | `claude-solve` |  | ✓ | ✓ | ✓ |
| `solver.ai.update_models` | `update-models` |  |  |  | ✓ |
| `solver.ai.update_usd_rate` | `update-usd-rate` |  |  | ✓ | ✓ |
| `solver.core.evaluate` | `benchmark` |  | ✓ | ✓ | ✓ |
| `solver.core.evaluate` | `compile-c` |  | ✓ | ✓ | ✓ |
| `solver.core.evaluate` | `evaluate` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `gh-merge` |  |  | ✓ | ✓ |
| `solver.core.git` | `git-audit` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-commit` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-filter` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-hooks` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-identity` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-publish` |  |  | ✓ | ✓ |
| `solver.core.git` | `git-push` |  | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-reset` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-status` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.git` | `git-sync` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.list` | `ls` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.new` | `new` |  | ✓ | ✓ | ✓ |
| `solver.core.results` | `results` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.summary` | `mark` |  | ✓ | ✓ | ✓ |
| `solver.core.summary` | `progress` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.summary` | `summary` |  |  | ✓ | ✓ |
| `solver.core.tags` | `create-topic` |  |  | ✓ | ✓ |
| `solver.core.tags` | `tags` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `topic` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `topics` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.tags` | `update-tags` |  | ✓ | ✓ | ✓ |
| `solver.core.test_cases` | `test-cases` | ✓ | ✓ | ✓ | ✓ |
| `solver.core.viewer` | `edit` |  | ✓ | ✓ | ✓ |
| `solver.core.viewer` | `show` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `host-unlock` |  |  |  | ✓ |
| `solver.crypto.keys` | `key-export` |  |  |  | ✓ |
| `solver.crypto.keys` | `key-reconstruct` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `key-rekey` |  |  |  | ✓ |
| `solver.crypto.keys` | `user` | ✓ | ✓ | ✓ | ✓ |
| `solver.crypto.keys` | `vault` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.bash` | `!` |  | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `?` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `clear` | ✓ | ✓ | ✓ | ✓ |
| `solver.shell.builtins` | `echo` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.doclint` | `check-commands` |  |  |  | ✓ |
| `solver.utils.linter` | `lint` |  | ✓ | ✓ | ✓ |
| `solver.utils.misc` | `problems` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.presentation` | `update-presentation-data` |  |  | ✓ | ✓ |
| `solver.utils.scripts` | `pip-upgrade` |  |  |  | ✓ |
| `solver.utils.scripts` | `sys-setup` |  |  |  | ✓ |
| `solver.utils.search` | `search` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.shell_utils` | `pause` | ✓ | ✓ | ✓ | ✓ |
| `solver.utils.update_doc` | `update-docs` |  |  |  | ✓ |
| `solver.utils.version` | `version` | ✓ | ✓ | ✓ | ✓ |
<!-- /GEN:authorization-table -->

## Where it is enforced

The floors above are a **guardrail**, not a boundary (docs/package-guide.md § 2.2): inside one
uid, someone who can edit their clone or run `!` can call any function the shell can. So
every `maintainer` and `admin` command was audited for where its **effect** lands, and what
stops someone below its floor there (phase 7). The answer is never "the floor":

- **own clone** — it changes the caller's own working tree. It reaches anyone else only by
  landing on `master`, and `master` is locked on GitHub (branch protection: pull request with
  one approving review, `lock_branch`; only the repository admin bypasses), so landing is
  GitHub's decision, made against the GitHub account, not the shell profile.
- **the master key** — it needs the master key, and holding the master key *is* the
  authority over it (proof of possession, § 9 of the web server guide): whoever can unwrap it
  can seal it to anyone, with or without this command.
- **sudo** — it goes through `sudo`; only the operator is in the `sudo` group, and no
  per-user uid is.
- **the spool** — `euler-msg` resolves the caller from `SO_PEERCRED` against the root-owned
  `authorizations.json` and refuses a staff verb (a notice to a named user, a staff dismiss)
  below `maintainer` itself.
- **euler-maint** — `/etc/euler/roster/` is `root:euler-maint 2775`, and the admin plane
  keeps that group at maintainer and above (`users add/change`), so writing the roster is a
  file permission.
- **relay firewall** — mail goes through the loopback relay, which nftables opens to the
  operator's uid and `euler-auth` only; every per-user uid is barred.

| Command | Floor | What it changes | Enforced by |
|---|---|---|---|
| `check-commands` | admin | nothing — reads docstrings | nothing to enforce |
| `host-authorize` | admin | mails the master key, sealed to a public key | the master key; relay firewall |
| `host-unlock` | admin | this machine's own enc-key file, only if it unwraps with this machine's private key | the private key: a block sealed to another machine is refused before anything is written |
| `key-export` | admin | prints the master key sealed to a public key | the master key |
| `key-rekey` | admin | rotates this clone's key, commits re-encrypted blobs, re-issues over the spool | the master key; own clone (landing: GitHub); the spool for the re-issue |
| `pip-upgrade` | admin | the running venv | file ownership: `/opt/euler` is root's, so from a web shell it fails; a terminal's own `.venv` is its owner's anyway |
| `sys-setup` | admin | system packages and services | sudo |
| `update-docs` | admin | generated docs, committed | own clone (landing: GitHub) |
| `update-models` | admin | the model catalogue, committed | own clone (landing: GitHub) |
| `users` | admin | accounts, profiles, instances (`list` is reader and read-only) | sudo (the wheel-gated admin plane) |
| `claude-batch` | maintainer | tags, via the Batches API | the caller's own API key (their vault); own clone (landing: GitHub) |
| `claude-blog` | maintainer | a topic article, via Claude Code | the caller's own Claude credentials; own clone (landing: GitHub) |
| `create-topic` | maintainer | a new topic article | own clone (landing: GitHub) |
| `gh-merge` | maintainer | merges a pull request onto `master` | GitHub: the merge is made as the caller's GitHub account, and `master` is locked to the repository admin |
| `git-publish` | maintainer | pushes and opens a pull request | GitHub (a direct push to `master` only for the repository owner's account) |
| `key-split` | maintainer | lays the host's half (first run), or sends a sealed half | the master key; sudo for `/etc/euler/share.json` (root's); the spool for the send; euler-maint for the roster record |
| `summary` | maintainer | `problems.json`, committed; a staff notice | own clone (landing: GitHub); the spool accepts a notice *to* staff from anyone |
| `update-presentation-data` | maintainer | the deck's data file, committed | own clone (landing: GitHub) |
| `update-usd-rate` | maintainer | `values.conf`, committed | own clone (landing: GitHub) |
| `user-authorize` | maintainer | records a public key, sends half the master key, dismisses the request | euler-maint for the roster; the master key and the spool for the send; the spool for the dismiss |

The site's write routes are the same shape: a file edit, a delete, a progress upload or a
topic edit changes only the signed-in user's own clone, through their own instance (their
uid), on a profile the auth service vouched for (`forward_auth`, a separate uid) — and
reaches anyone else only through GitHub.

**No gaps were found**: nothing above depends on the floor alone. `tests/test_enforcement_audit.py`
holds this table to the live registry, so a new `maintainer` or `admin` command fails the
tests until it has a row here.
