# Config Guide — where a setting lives, and why

This guide covers **configuration**: the two files you can edit, the rules that decide which
one a setting belongs in, and the three categories of value that are deliberately not
settings at all. It is implemented in [`solver/config/`](../solver/config/).

The short version, for when that is all you need:

| I want to… | do this |
| --- | --- |
| see every setting | `{config}` in the shell (`{config.timeout_single}` for one) |
| change one | edit [`solver/config/values.conf`](../solver/config/values.conf) |
| change what a deployed service reads | edit that service's `/etc/euler/*.env`, not this repo |
| find which variable a service reads | [`solver/config/env.conf`](../solver/config/env.conf) |

There is no `manage-config` command and no `config.json`. Both existed; both are gone.
Reading the settings needed a command and an `admin` floor to see three numbers, and the
file it wrote was JSON, so it could carry no explanation of what any of them meant.

---

## 1. The shape

```
solver/config/
  __init__.py     the way in: `from solver.config import config`
  settings.py     every setting — its name, its type, its default
  values.conf     the editable half: what a person tunes
  values.py       reading values.conf
  env.conf        the web services' environment: variable name and default per setting
  env.py          reading env.conf
  paths.py        the anchors — package_root, repo_root(), secrets_dir(), share_file()
  identity.py     dynamic: the resolved Subject, and per-user state
  theme.py        dynamic: the rich theme and the prompt_toolkit style
```

Split by *what a value is*, not by who reads it. Every part of the solver reaches the same
singleton — the shell, the AI commands, the crypto package, the git filter — so there is one
answer to "where is the stack?" rather than one per caller. Four separate derivations of the
repo root drifted once, and the drift cost a collaborator their decryption (§5.2).

---

## 2. Two files, two species

They look similar and are not interchangeable.

**[`values.conf`](../solver/config/values.conf)** is *what a person tunes*. Solution
timeouts, the file names inside a problem directory, where the stack lives, the FX rate
`costs` converts with. It is tracked, so an edit is a commit and every clone gets it. Values
may name each other and the computed anchors:

```ini
[paths]
solutions_dir = ${root_dir}/solutions
env_file      = ${secrets_dir}/env
```

Available anchors: `${root_dir}`, `${package_dir}`, `${secrets_dir}`, `${home_dir}`.

**[`env.conf`](../solver/config/env.conf)** is *deployment wiring for the web services*.
Each runs as its own uid, from `/opt/euler`, with a scoped `EnvironmentFile=` under
`/etc/euler`. What lives here is not the value — it is the **map** from a setting to the
variable that carries it, and what it is worth when that variable is unset:

```ini
[auth]
state_dir   = EULER_AUTH_STATE_DIR | /var/lib/euler-auth
admin_token = EULER_ADMIN_TOKEN    | !required
```

`!required` means the service refuses to start without it, naming the variable. A secret or
a public URL with no sane default is better as a startup failure than a quiet wrong answer —
a guessed `EULER_BASE_URL` mails invite links that go nowhere.

`[common]` holds what several services share, so a default is stated once. `euler-web` used
to be written into five separate files, and a group name that disagrees with the Caddy
config is a socket nobody can connect to.

### Which file does my setting go in?

Ask **who sets it**. If the answer is a person with a clone, `values.conf`. If it is a
systemd unit on the host, `env.conf`. If it is neither — if the value is a consequence of
where the code is running, or something two machines must agree on byte for byte — it is not
a setting at all; see §5.

---

## 3. Precedence, and the two defaults

```
environment  >  the conf file  >  the default declared in code
```

Two environment variables outrank `values.conf`: `EULER_REPO_ROOT` (which decides
`root_dir`, and through it most of `[paths]`) and `EULER_BASE_URL`.

Every setting has its default written **twice** — once in `settings.py` as the field's
default, once in the conf file. That is deliberate, and it is the part most likely to look
like an accident:

- the **code default** is a safety net. A missing, truncated or mis-edited conf file must
  never be able to stop the shell from starting. It is also what a *direct* construction
  gets — `SiteConfig(...)` in a test, `site_config()` inside `UserConfig`.
- the **file default** is a catalogue. It makes the file a complete list of the knobs, each
  with a comment saying what it is for, rather than a sparse overlay you have to read the
  source to interpret.

Because they can drift, tests hold them to each other:
`test_values.ShippedValuesTests` builds the configuration with the file and without it and
requires every setting to agree, and `test_env` does the same for each service class against
its section. Both have already caught a real drift.

A value the file names but the code does not declare is **ignored**, and one that will not
coerce to its declared type leaves the default standing. Neither is fatal: the file is data,
not code, and it survives a release that retires a setting. Retiring `server_port` once made
every older config file raise `KeyError` at import, before anything could print an error
saying so.

`env.conf` is stricter — an uncoercible value there is a startup failure naming the
variable, because a variable someone deliberately set is a stated intention, not a stale
line in a file that shipped years ago.

---

## 4. Reading it

```
{config}                       every setting, one per line
{config.timeout_single}        one of them
{config.scripts.sync}          a script path
```

In Python, `from solver.config import config`, then attribute access. Item access
(`config['timeout_single']`) resolves the same way, including for the settings that are
computed rather than stored.

**Importing `solver.config` builds nothing.** The singleton is resolved on first *access*,
and that is load-bearing rather than tidy — see §5.3.

---

## 5. What is not a setting

Three categories, and the question that sorts them: **may I change this, and what happens if
I do?**

### 5.1 Protocol — [`solver/crypto/wire.py`](../solver/crypto/wire.py)

The magic bytes, the nonce length, the filter driver's name, the `.gitattributes` line, the
vault's KDF iteration count, the verify plaintext. Each is part of a format something else
already depends on: a blob in git, a file on another machine, a key the browser derives.
Changing one does not adjust behaviour — it makes existing data unreadable. None of it has
an override, and it lives in the crypto package as code.

This used to sit in the same table as the key *locations*, which are ordinary settings and
now live in `[crypto]` of `values.conf`. One table holding both could not answer the
question above, which is exactly why they were separated.

### 5.2 Discovered — [`solver/config/paths.py`](../solver/config/paths.py)

`root_dir` and `share_file` are not matters of opinion. The first is wherever the checkout
actually is; the second depends on whether this machine is a deployed host (`/etc/euler`)
or a plain clone (the secrets dir). Writing either into a conf file would be writing down an
answer that is only true on one machine.

`repo_root()` resolves in a fixed order — `EULER_REPO_ROOT`, then `git rev-parse` from the
cwd, then from this file's directory, then two levels up but **only** if it looks like the
checkout — and raises rather than guessing. That last guard is a scar: with the git filter
running under `-P`, `__file__` moved into `site-packages`, a laxer fallback adopted
site-packages as the repo, and the filter reported a private key missing from a path no key
had ever been at. A wrong root is worse than no root, because it turns "I cannot tell" into
a confident lie further downstream.

### 5.3 Computed — the service classes

`shell_argv` is this interpreter. `static_dir` is a path inside whatever tree was
discovered. The per-user socket's name embeds the instance's slug, which is only known once
the environment has been read. Each is computed in the class's `from_env` and documented
there; `test_env` requires every *other* field to be in the table, so a new one cannot be
quietly forgotten.

---

## 6. Two invariants, and why they exist

Both are pinned by [`tests/test_config.py`](../tests/test_config.py). Both look like style
until you know what they are load-bearing for.

**Importing configuration does nothing.** No `Config`, no chdir, no `PATH` rewrite, no
identity resolution, no `rich`. It used to do all of it, at import, on behalf of every
caller — including a git filter that wanted one path constant and got a relocated process
and a resolved security subject with it.

The sharp edge is the web tier: `euler-auth`, `euler-msg` and `euler-ws` run from
`/opt/euler` with **no working tree and no `EULER_REPO_ROOT`**, so `repo_root()` raises for
them by design. They read `env.conf`, so a `Config` built underneath them would kill
euler-auth at import — and Caddy authenticates every request through euler-auth, so the site
goes with it. That has happened once, for a neighbouring reason
([web-server-guide §11](web-server-guide.md)).

The shell's process move is therefore explicit: `enter_repo(config.root_dir)`, called by
`solver.main.main` at startup. Identity is a `cached_property`, forced by `main` at the one
moment the web shell's single-use ticket handoff can happen.

**No module in the package may be called `config`.** The static settings live in
`settings.py` for this reason alone. A submodule of that name would be bound over the
package's own `config` attribute by the import machinery the first time anything imported it
by path, and every `from solver.config import config` afterwards would quietly receive a
module — an `AttributeError` a long way from its cause, at every one of ~50 call sites. A
test asserts the name stays unclaimed.

---

## 7. The one value a command writes

`ecb_usd_rate` — euros per US dollar, for what `costs` reports. Currencies drift daily, so
`update-usd-rate` refreshes it from the European Central Bank's reference feed and writes it
back through `set_value`, which rewrites that one line and leaves the sections, the comments
and every other setting exactly as they were. A whole-file rewrite would round-trip the
values and discard everything around them, which is most of what makes the file worth
editing by hand.

It is the only setting a command may write, because it is the only one that is *maintained*
rather than chosen. Everything else in `values.conf` is somebody's decision.

---

## 8. Tests

| file | what it pins |
| --- | --- |
| [`tests/test_config.py`](../tests/test_config.py) | the two invariants of §6, the anchors, and that item and attribute access never disagree |
| [`tests/test_values.py`](../tests/test_values.py) | the shipped file and the declared defaults state the same thing; a retired key, a bad value and a malformed file are all survivable; `set_value` preserves the comments |
| [`tests/test_env.py`](../tests/test_env.py) | reading the table constructs no `Config`; the table and the five classes agree in both directions; `!required` exits naming its variable |

---

## 9. Files

| file | role |
| --- | --- |
| [`solver/config/settings.py`](../solver/config/settings.py) | every setting: name, type, default — and the `Config` class |
| [`solver/config/values.conf`](../solver/config/values.conf) | the editable half: what a person tunes |
| [`solver/config/values.py`](../solver/config/values.py) | reading it, and the surgical single-line write |
| [`solver/config/env.conf`](../solver/config/env.conf) | the web services' environment: variable name and default per setting |
| [`solver/config/env.py`](../solver/config/env.py) | reading it — importable by a service with no clone |
| [`solver/config/paths.py`](../solver/config/paths.py) | the anchors, and the shell's explicit `enter_repo()` |
| [`solver/config/identity.py`](../solver/config/identity.py) | the resolved `Subject` and per-user state, reached only lazily |
| [`solver/config/theme.py`](../solver/config/theme.py) | the one palette, in `rich` and `prompt_toolkit` dialects |
| [`solver/crypto/wire.py`](../solver/crypto/wire.py) | the formats that are not configuration (§5.1) |
| [`solver/web/*/config.py`](../solver/web/) | one class per service: the shape, and what a table cannot say |
