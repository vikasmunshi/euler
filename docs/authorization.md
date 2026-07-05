# Authorization for `solver-web` (command & route)

This guide covers what an authenticated identity may *do*. It is the third layer of
a three-part story: [TLS](tls-guide.md) secures the transport and
[authentication](authentication.md) establishes *who* the caller is (and assigns
their **profile**, stored in `keys/.users.json`). Here that profile decides which
shell commands and web routes the identity may use.

The shell is the same `solver` program everywhere, so two complementary layers
narrow it to the context:

| Layer | Question | Driven by | Enforced at |
|---|---|---|---|
| **Channel-based** | which command *modules* load at all | `solver/modules.csv` (`terminal` / `web` columns) | module import (`shell/loader.py`) |
| **User-based** | which loaded commands a *profile* may run | `solver/commands.csv` (`admin` / `user` / `guest` columns) | the `@command` decorator (`shell/command.py`) |

The layers compose. `modules.csv` decides what loads per channel — for example
`solver.utils.update_doc` is `web=False`, so `update-docs` never loads in a web
shell. `commands.csv` then applies per profile on top: the `users` command *does*
load in a web shell, but its row grants only `admin`, so only a web admin can run
it.

## Profiles

Every identity carries one **profile** — `admin`, `user`, or `guest`, in descending
privilege. It is resolved once at startup (`solver/utils/identity.py`) and exposed
as `config.user_profile`:

- **Web** — the SRP-authenticated email is looked up in `keys/.users.json` and its
  stored `profile` applies. The web tier vouches for the email — it ran the SRP
  handshake — when it forks the per-user shell with `SOLVER_USER=<email>`.
- **Local terminal** — with no identity configured, resolution falls through to the
  OS login name and grants **`admin`**: access to the checkout is itself the trust
  (the channel-based half of the model). A local operator may `export SOLVER_USER=…`
  to *drop* to a named account's lower profile, but cannot gain privilege that way.

An explicitly configured identity (via the environment, `keys/.user-email`, or
`.env`) that is not an enabled account in `.users.json` aborts startup with
`invalid user`.

## The policy file (`solver/commands.csv`)

It mirrors `modules.csv`: a `command` column followed by one boolean column per
profile, where a truthy cell grants that profile the command.

```csv
command,admin,user,guest
benchmark,True,True,
users,True,,
show,True,True,True
```

Semantics (`is_authorized` in `shell/command.py`):

- A command **listed** in the policy is allowed only for the profiles its row grants
  (`benchmark` → admin + user; `users` → admin only; `show` → everyone).
- A command **absent** from the policy is **admin-only** — a fail-safe default, so a
  freshly added command is never silently exposed to `user` or `guest` before it is
  added to `commands.csv`.

`update-docs` keeps `commands.csv` reconciled with the live registry: it appends new
commands with the default `admin` + `user` grant, drops rows for removed commands,
and preserves every existing grant verbatim.

## Enforcement in the shell (decoration time)

The check lives in the `@command` decorator. As each command module is imported,
`command()` derives the command name and calls `is_authorized(name)` against
`config.user_profile`. If the profile is not permitted, the command is simply **not
registered** — invisible to `?`/help and tab-completion, and `unknown command`
(exit `127`) if invoked. The function itself is returned unchanged, so it remains a
normal Python callable.

Because one shell process serves exactly one identity, the profile — and therefore
the registered command set — is fixed for the life of the process, and the policy is
read once and cached.

## Enforcement on the web routes

The web front end exposes some of the same power outside the shell: the file
save/delete, lint, and progress-save routes act directly on the solution tree rather
than by dispatching a shell command, so the `@command` check does not cover them.
They are gated by the **same policy** with a `requires(<command>)` decorator
(`solver/web/app.py`): a route declares the command capability it mirrors, and the
decorator admits a request only if the requester's profile may run that command. So
`commands.csv` stays the single source of truth across both surfaces.

| Route | Capability |
|---|---|
| `POST`/`DELETE /edit/{n}/{file}` (file writes) | `edit` |
| `POST /edit/lint` | `lint` |
| `POST /edit/progress` | `summary` |

The server process runs as `admin`, so the guard resolves the **requesting** user's
profile from `.users.json` (via `profile_for`), not its own; an authenticated but
unauthorized profile gets `403`. The read-only viewer (problem pages, docs, summary,
static assets), the **code editor** page (`GET /edit/{n}/{file}`), and the
**terminal** (`/ws`, `/cmd`) are ungated: viewing is harmless, the terminal belongs
to any authenticated user, and the shell running behind it restricts the commands it
will accept by this very policy.

`GET /authz?cmd=…` reports, for the requesting profile, whether each named command is
permitted. The front end uses it as a UI hint — dimming the editor's save/delete
buttons and hiding command-bar actions a profile may not use — but the server-side
guards above are the actual enforcement.

## Assigning a profile

`users add <email> [profile]` seeds the invite with the chosen profile (`admin` /
`user` / `guest`; default `user`). The profile is stored on the account and
preserved through registration and password resets:

```
users add alice@example.com          # a standard user
users add bob@example.com guest      # read-only browsing
users add carol@example.com admin    # full access
```

Per-command availability — both channel and profile — is listed in
[`commands-index.md`](commands-index.md).
