# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Environment

The project requires Python 3.14+, provided by the project virtualenv (`.venv`), which is on
`PATH` in this environment. Use the **bare** commands — `python`, `solver`, `mypy`, `flake8` —
not the `.venv/bin/...` paths: the permission allowlist in `.claude/settings.local.json` grants
`python:*`, `solver *`, `mypy *`, and `flake8 *`, so the bare forms run without a confirmation
prompt while `.venv/bin/python` would not match.

```bash
python -m solver        # run the interactive shell
solver                  # same, via entry point
```

## Common Commands

```bash
# Install (full developer setup)
make install-all

# Lint and type-check
scripts/linters/check.sh solver   # runs mypy + flake8 on the solver package

# Individually
mypy solver
flake8 solver                     # max-line-length 120

# Run the shell interactively
make run

# Full-tree audit (~25s): solutions/private encrypted at rest, no compiled binaries tracked.
# The git hooks run the same checks scoped to what you stage/push; this sweeps settled history.
make audit                        # also: the `git-audit` shell command

# Run shell commands non-interactively (a command block; exits with its status)
solver "eval 42; benchmark 42"

# Deploy the web front end (systemd services behind a TLS edge — needs sudo).
# There is no local server: see docs/web-server-guide.md.
make deploy-web         # also: remove-web | redeploy-web | upgrade-web

# Cut a release, then ship it (see "Versioning" below):
make release            # bump solver/version.py → commit → tag vX.Y.Z → push (ARGS=--dry-run|--no-push)
make redeploy-web       # gated on check-version: refuses if the tag isn't on origin
```

## Versioning

The version is a single tracked file, `solver/version.py` (`__version__ = 'X.Y.Z'`) — the
sole source of truth. `pyproject.toml` reads it at build time via
`[tool.setuptools.dynamic]` `attr:` (no setuptools-scm, no build-time git), and
`config.version` imports it at runtime, so the number in the file, the wheel, and the
`version` shell command always agree. It holds the last **released** number; between
releases it stays put while the `version` command's live `git describe` line shows how far
past the tag HEAD is.

**Never hand-edit the number.** `scripts/version/release.sh` (`make release`) is the only
writer: it derives the next SemVer bump from Conventional Commits, rewrites `version.py`,
commits `chore(release): vX.Y.Z`, tags the commit, and **pushes the commit + tag to origin**
(`--no-push` opts out; `--dry-run` previews). `make check-version` fails unless the version
`version.py` names has its `vX.Y.Z` tag on origin, and is a prerequisite of `redeploy-web` —
so a locally-tagged-but-unpushed release can't be deployed ahead of collaborator clones.
The deployed venv is only as current as the last release baked into it: **re-run
`make redeploy-web` after `make release`.** Full release flow: `make release` → `make redeploy-web`.

Make target verbs follow the two kinds of target, and always match the action the
underlying script in `scripts/setup/` takes:

- **local** (what the terminal solver needs — apt packages, `.venv`, hooks, completions,
  Chrome, Claude Code, Node.js): `install` / `uninstall`.
- **system** (what the solver web needs — root's systemd, the `euler-*` identities,
  `/etc/euler`, `/opt/euler`): `deploy` / `remove` / `redeploy`, plus `upgrade` on the
  kits where it differs from `deploy` (see docs/web-server-guide.md § 14.2).

## Git Hooks

The hooks are rendered from the templates in `scripts/setup/hooks/` (`pre-commit.template`, `pre-push.template`) into the **default** location `.git/hooks/` by `scripts/setup/githooks.sh install`. This runs via `make install-hooks` (and is part of `make install-all`), which also resets `core.hooksPath` to the default; `make uninstall-hooks` removes them. Edit the templates, not the installed copies, then re-run the installer.

Pre-commit hook (`.git/hooks/pre-commit`) auto-fixes trailing whitespace in staged text files (and checks for leftover whitespace / conflict markers), then runs `flake8` and `mypy` on the `solutions` and `solver` directories. All checks must pass for the commit to proceed.

Pre-push hook (`.git/hooks/pre-push`) runs additional checks before pushing to remote.

To test the pre-push hook without actually pushing:
```bash
echo "refs/heads/master $(git rev-parse HEAD) refs/heads/master $(git rev-parse origin/master)" | bash .git/hooks/pre-push
```

## Documentation

User- and developer-facing docs live under `docs/`:

- `docs/user-guide.md` — using the shell: invocation, command blocks, variables, loops, command catalogue.
- `docs/solver-guide.md` — solving problems: the `@runner.main` decorator, test cases, the solve workflow.
- `docs/developer-guide.md` — extending the framework: the `@register` contract, command modules, the loader.
- `docs/commands-index.md` — every command's aliases, flags, and exact usage.
- `docs/syntax.md` — the authoritative command-language reference.

The command catalogue (in `user-guide.md`) and `commands-index.md` are **generated** from the live
registry by the `update-docs` command (`solver/utils/update_doc.py`). After changing any command's
name, alias, `help_text`, or signature, run `update-docs` (`solver "update-docs --check"` verifies
they are current).

## Architecture

### Package layout

<!-- GEN:package-layout -->
```
solver/
  __main__.py         — Module entry point.
  config.py           — Singleton Config: all paths, constants, command modules, and managed settings.
  main.py             — Entry point for the "solver shell" CLI.
  version.py          — The solver build version — the single source of truth.
  ai/
    api.py            — The `claude-api` command: generate solution artifacts (code / docs / test cases) via the Claude API.
    code.py           — Generate and re-document Project Euler solutions (Python and C) via the Claude API.
    docs.py           — Module to generate notes for solver solutions, leveraging AI.
    facts.py          — Utility function for gathering problem inputs for AI
    models.py         — Available models and their pricing, plus a utility function to calculate costs.
    skill.py          — The `claude-solve` / `claude-blog` commands: run Claude Code in-shell via a skill.
    update_models.py  — The `update-models` command: refresh the `Model` enum, pricing, and FX rate.
  auth/               — The authorization kernel — identity, profiles, and the ladder.
    authorizations.py — The authorization policy — ``authorizations.json``.
    identity.py       — Identity resolution → a :class:`~solver.auth.subject.Subject`.
    subject.py        — The authorization **subject** — the resolved security principal.
  core/
    download.py       — Utility for downloading and caching files via HTTP.
    evaluate.py       — Solution evaluation: runs standalone scripts against test cases and reports results.
    git.py            — Git and GitHub (gh) commands and helpers — the repository workflow.
    list.py           — List solution directory contents.
    new.py            — The `new` command and solution-file formatting (black / isort / autoflake).
    osc.py            — The shell → browser control channel: `OSC 5379`.
    problems.py       — The Problem model plus the projecteuler.net problem scraper and on-disk cache.
    results.py        — Results: save and retrieve problem results.
    tags.py           — Tag/topic glue: the `topics`, `topic` and `update-tags` commands.
    test_cases.py     — Load test cases for evaluation
    viewer.py         — Open a problem or its files in the web front end: the `show` and `edit` commands.
  crypto/
    ciphers.py        — Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.
    config.py         — Crypto configuration: the single source of truth for every file location and git-filter wire constant.
    gitfilter.py      — Transparent git clean/smudge encryption for tracked solution files.
    keys.py           — Cipher key management: create, persist, rotate and share the crypto key material.
    readenv.py        — Print the authoring env (``~/.euler/env``) as plaintext — the setup scripts' reader.
    vault.py          — The per-user vault: envelope encryption that makes a user's secrets opaque to the operator at rest.
  runners/
    runner.h          — Runner framework for Project Euler solutions with benchmarking and validation.
    runner.py         — Runner framework for Project Euler solutions with benchmarking and validation.
  shell/              — Shell framework (prompt-toolkit + rich): the readline → lexer → parser → interpreter pipeline.
    bash.py           — The `!` (`sh` / `bash`) built-in command: run a bash command in the current
    builtins.py       — Built-in framework commands for shell v2: echo, clear, help.
    command.py        — Command framework for shell v2: Context, Command, registry, and decorator.
    interpreter.py    — Interpreter for shell v2: execute the parser's statements.
    lexer.py          — Lexer for shell v2: syntax-check a command block and normalise it.
    parser.py         — Parser for shell v2: canonical form (the lexer's output) → typed statements.
    register.py       — The `@register` decorator: register a function as a shell command with type-safe coercion and completion.
    session.py        — Session capture: tee shell output and typed input to a plain-text log file.
    shell.py          — Interactive shell for v2: readline → lexer → parser → interpreter.
    tty.py            — Terminal I/O: the shared rich console, the prompt-toolkit session, and the command-block reader.
    variables.py      — Variable store for shell v2.
  templates/
    engine.py         — Template rendering: the Templates enum and string.Template engine with shared prompt/solution vars.
    new.c             — Solution to Euler $problem.
    new.py            — Solution to Euler $problem.
  utils/
    linter.py         — Utilities for linting code.
    loader.py         — Utility for loading command modules.
    misc.py           — The `problems` and `manage-config` commands.
    path_utils.py     — Utility functions for file and directory operations.
    scripts.py        — Dependency and system-resource setup commands.
    search.py         — 'find' command: grep the solution stack for a regular expression.
    shell_utils.py    — Utility for running shell commands and capturing their output.
    summary.py        — Progress: parse .progress.html into problems.json and refresh in-memory state.
    update_doc.py     — Regenerate the machine-maintained sections of the guides under `docs/`.
    version.py        — The `version` command: report the running solver build's version.
  web/                — The web app services (see docs/web-server-guide.md).
    csp.py            — Content-Security-Policy middleware with a per-response nonce (shared).
    auth/             — Web authentication: the auth service and its clients.
      __main__.py     — Auth service entry point: ``python -m solver.web.auth``.
      admin.py        — The admin-plane CLI: run **under sudo** by the ``users`` shell command.
      app.py          — The auth service: public + admin aiohttp apps over unix sockets.
      client.py       — Minimal HTTP-over-unix-socket client for the auth service (stdlib only).
      commands.py     — The ``users`` shell command: account administration for the operator.
      config.py       — Auth-service runtime configuration, read from the environment.
      mail.py         — Outbound mail via the loopback relay.
      pages.py        — The auth service's HTML pages: login, registration, reset, forgot.
      pending.py      — Pending invite / reset store at ``<state>/pending.json``.
      policy.py       — Auth policy constants (lifetimes, cookie names, password and OTP rules).
      ratelimit.py    — A small in-memory sliding-window rate limiter for the auth endpoints.
      remember.py     — Persistent "remember me" tokens at ``<state>/remember.json``.
      requests.py     — Prospective-collaborator invite requests at ``<state>/requests.json``.
      sessions.py     — In-memory web session table.
      srp.py          — Secure Remote Password (SRP-6a) primitives for web authentication.
      storage.py      — Shared JSON persistence for the auth stores.
      tickets.py      — One-time shell tickets: web identity for PTY children.
      users.py        — User store: the SRP verifier database at ``<state>/users.json``.
    site/             — The content service — server-rendered pages + htmx fragments.
      __main__.py     — Content service entry point: ``python -m solver.web.site``.
      app.py          — The content service aiohttp app: identity from forward_auth, routes, gating.
      config.py       — Content-service runtime configuration, read from the environment.
      content.py      — Config-free readers for the content trees the service renders.
      gitstate.py     — The header chip's git state: three reads of this user's clone, by need.
      render.py       — The full-page-vs-block render contract (§4.5).
      validate.py     — The save gate: the checks every write passes.
    user/             — The per-user web service: one collaborator's content **and** web shell.
      __main__.py     — Per-user service entry point: ``python -m solver.web.user``.
      app.py          — The per-user aiohttp app: one collaborator's content **and** web shell.
      config.py       — Per-user service runtime configuration, read from the environment.
      vault_api.py    — Vault + account routes for the per-user service.
    ws/               — The web-shell service: the solver PTY terminal over WebSocket.
      __main__.py     — Web-shell service entry point: ``python -m solver.web.ws``.
      app.py          — The web-shell aiohttp app: identity from forward_auth, the /ws attach, teardown.
      config.py       — Web-shell service runtime configuration, read from the environment.
      manager.py      — Persistent per-user PTY shells: one long-lived solver shell per web user.
      pty.py          — PTY bridge: run an interactive ``solver`` shell on a pseudo-terminal.
```
<!-- /GEN:package-layout -->

### Command registration

Every shell command is a plain Python function decorated with `@register(help_text=..., aliases=..., pass_ctx=..., quietable=...)` from `solver.shell`. The command name is derived from the function name (underscores → dashes; `usage` is synthesised from the signature). The decorator handles argument tokenisation (`shlex.split`), type coercion (Literal, bool, int, Optional, Enum), and tab-completion. Commands are collected at import time; `solver/modules.csv` (read by `utils/loader.py`) lists which modules to import on startup.

Functions still work as normal Python — they are not transformed, just registered. See `docs/developer-guide.md` for the full register contract.

### Command contract & blocks

Every command returns an `int` Unix exit code (`0` = success, non-zero = failure); the `@register`
adapter forwards it verbatim. Input runs through a `lexer → parser → interpreter` pipeline
(authoritative spec: `docs/syntax.md`): commands compose with `;` (sequential), `&&` (on
success), `||` (on failure) and `{ … }` groups, nesting arbitrarily, with a newline as an implied `;`.
A statement is a command, a `name = expr` assignment, or a bare expression (`rcode` 0 when truthy, 1
when falsy) — so expressions gate `&&`/`||` chains. `loop <list>: <block>` is a language construct that
runs its `{ … }` (or inline) body once per element of a list, binding the current element to `{loop}`;
`break`/`continue`/`exit` are flow words. The lexer normalises input to a canonical guarded form (§8 of
docs/syntax.md). `solver <cmd>` exits with the block's status, so steps can be gated directly
(`solver "eval 42 && benchmark 42"`).

### Stack (solutions storage)

Solutions live under `solutions/`, one directory per problem: plaintext problems in `solutions/public/pNNNN/` (e.g. problem 42 → `solutions/public/p0042/`) and encrypted problems in `solutions/private/pXXXX_YYYY/pNNNN/`, bucketed by century (e.g. problem 101 → `solutions/private/p0100_0199/p0101/`).

- `solutions/public/`: all files stored in plain text.
- `solutions/private/`: solution code, test cases, results, and notes are encrypted at rest (AES-256) by a transparent git clean/smudge filter (`crypto/gitfilter.py`) — ciphertext in git, plaintext in the working tree once the master key is available.

Commands operate directly on each problem's files (resolved via `problem.solution_dir`); the git filter handles encryption on commit / decryption on checkout.

### Encryption key hierarchy

The crypto sub-package is three modules: `ciphers.py` (non-interactive: `config_dict` with all file
locations + git-filter wire constants — **no `solver.config` dependency** — plus load/lock/unlock and
encrypt/decrypt helpers), `keys.py` (all interactive create/persist/rotate/share and
the shell commands), and `gitfilter.py` (the git clean/smudge filter, depending only on `ciphers`).

- Per-user private key: `~/.euler/id` (X25519, PKCS8 PEM, **plain/unencrypted**). It lives in a
  machine-local `0600` secrets dir — a sibling dot-directory named for the repo (`~/euler` →
  `~/.euler`), **outside** the checkout — so file permissions are its protection and the load path
  needs no password.
- `keys/enc-key.json`: a single 32-byte master key, identified-by-public-key — `{<public-key-hex>:
  <master key wrapped to that key>}` plus a `verify` ciphertext for self-checking. One entry per
  authorised public key; no email is stored. Authority is proof-of-possession. (Stays in-repo:
  wrapped master keys are useless without a private key.)
- Decryption path: load private key → unwrap master key → verify → decrypt files.

### Solution file naming

`p<NNNN>_s<K>.<ext>` — problem number zero-padded to 4 digits, solution index starting at 0, extension `py` or `c`. Multiple solutions per problem are supported.

### Solution script interface

The runner framework (`solver/runners/`) supplies the harness; a solution only implements `solve()`:
- Python: decorate `solve(*args: str) -> str` with `@runner.main` (`from solver.runners import runner`).
  C: write `const char *solve(int argc, char *argv[])` and `#include "runner.h"`.
- The runner — `@runner.main` / `runner.h`'s `main()` — passes the test-case `input` values as
  positional args in order, parses `--runs=N` and `--show`, runs the timed loop, checks the result
  is consistent across runs, and prints the single stdout line `<runs> <avg_seconds> <result>`.
- `solve()` only *returns* the answer as a string; it must never print that final line itself, and
  exits non-zero on error.
- Argument/resource helpers live on the runner: `parse_int`, `parse_list`, `get_text_file`, and the
  `show` flag (Python `runner.show`, C `show`) gating `--show` diagnostics.

See `solver/templates/new.py` / `new.c` for the canonical templates.

### AI features

Two AI entry points, both calling the Claude API. Install the optional deps with `pip install -e ".[ai]"` (`anthropic` + `python-dotenv`); the key is `ANTHROPIC_API_KEY`, read from the project env file `~/.euler/env` (`config.env_file`, `models.py:get_api_key`).

- **`claude-api`** (`solver/ai/api.py`) generates solution artifacts, dispatching to per-target generators — `code.py` (Python/C), `docs.py` (notes), `facts.py` (test cases) — with prompts in `solver/templates/prompt_*.txt`. Default models: Opus for code (Python + C) and notes, Sonnet for test cases. The `costs` command (`models.py`) reports accumulated token spend.
- **`euler-solve`** (`solver/ai/skill.py`) launches Claude Code headless against a problem's solution files, via the `claude-euler-solver` skill (`solver/ai/claude/skills/claude-euler-solver/`). Invoked as `claude -p /claude-euler-solver <problem_number> <action>`, running at the repo root; its actions are `solve` and `review`. The skill's standards live in the `docs/convention_*.md` guides (also injected into the `claude-api` prompts via `templates/engine.py`).

### Web front end

There is **no local server and no `solver-web` script**. The front end is a deployed stack of isolated systemd services behind a Caddy TLS edge, each on its own unix socket under `/run/euler/`, run from the root-owned `/opt/euler` venv. The design of record is **`docs/web-server-guide.md`** — read it before changing anything under `solver/web/`.

The shape in one paragraph: Caddy terminates TLS, strips client identity headers, authenticates every request through the auth service's `forward_auth`, and routes by the returned `X-User-Slug` to **one service per collaborator** (`euler-user@<slug>`, `User=euler-user-<slug>`), which serves that user's content routes **and** their `/ws` terminal from their own `~/euler` clone. Authentication is browser-side SRP-6a (`solver/web/auth`); authorization is the profile ladder (`solver/auth`). Each collaborator has their own uid, home, clone, branch, and encrypted vault (`solver/crypto/vault.py`), so their keys are exposed only to their own code.

The `show`/`edit` commands (`solver/core/viewer.py`) drive the browser over a channel-aware bridge: from a **web** shell an `OSC 5379` sequence rides the PTY → WebSocket pipe and swaps the app shell's left pane; from a **terminal** they open `config.base_url` (`$EULER_BASE_URL`) in a named browser tab (`solver-doc`). Per-user shell state — history, session log, last active problem — lives under `.state/<slug>/`, the slug resolved by `solver/auth` and wired into `config`.

## Solution Code Conventions

- Solution files for problems > 100 live under `solutions/private/` — ciphertext in git, plaintext in the working tree once the master key is available (the git clean/smudge filter decrypts on checkout). Read and edit them like any other solution. **Hard rule: the decrypted plaintext must never leave the repo.** Never paste it into an external service, artifact, web page, log, chat, or any output that escapes the local working tree; never commit or push it unencrypted (only the git filter's ciphertext may land in git); never copy it outside `solutions/private/`. When in doubt, treat the plaintext as strictly confidential and keep it in-tree.
- For code structure and patterns, any solution serves as a reference — the plaintext `solutions/public/` ones (e.g. `solutions/public/p000*/`) are the most convenient since they need no key.
- Build sieves, precomputed tables, and caches (`@cache`/`@lru_cache`, memo dicts) **inside** `solve()` (or in helpers it calls fresh each call), sized to the inputs — **not** at module level with a fixed bound. With `--runs=N` the harness times the repeated `solve()` calls, so anything built once at import (or a cache kept warm between runs) is excluded from the first run and free thereafter, understating the real cost. See `solutions/public/p0007/p0007_s0.py` (sieve sized to `n·ln n`) and `solutions/public/p0035/p0035_s0.py`.