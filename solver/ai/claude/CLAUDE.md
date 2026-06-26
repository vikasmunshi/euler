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

# Run shell commands non-interactively (a command block; exits with its status)
solver "init 42; eval; reset"

# Launch the PTY-backed web front end (aiohttp); serves the terminal + viewer/editor
solver-web start        # also: stop | status | restart  (needs the `web` group: pip install -e ".[web]")
```

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
- `docs/solver-guide.md` — solving problems: the `@runner.main` decorator, test cases, the `init → stack` workflow.
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
  ai/
    api.py            — The `claude-api` command: generate solution artifacts (code / docs / test cases) via the Claude API.
    code.py           — Generate and re-document Project Euler solutions (Python and C) via the Claude API.
    docs.py           — Module to generate notes for solver solutions, leveraging AI.
    facts.py          — Utility function for gathering problem inputs for AI
    models.py         — Available models and their pricing, plus a utility function to calculate costs.
    skill.py          — The `claude-skill` command: run Claude Code in-shell against the locked workspace.
    update_models.py  — The `update-models` command: refresh the `Model` enum, pricing, and FX rate.
  core/
    download.py       — Utility for downloading and caching files via HTTP.
    evaluate.py       — Solution evaluation: runs standalone scripts against test cases and reports results.
    problems.py       — The Problem model plus the projecteuler.net problem scraper and on-disk cache.
    results.py        — Results: save and retrieve problem results.
    test_cases.py     — Load test cases for evaluation
  crypto/
    ciphers.py        — Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.
    gitfilter.py      — Transparent git clean/smudge encryption for tracked solution files.
    keys.py           — Cipher key management: create, persist, rotate and share the crypto key material.
  runners/
    runner.h          — Runner framework for Project Euler solutions with benchmarking and validation.
    runner.py         — Runner framework for Project Euler solutions with benchmarking and validation.
  shell/              — Shell framework (prompt-toolkit + rich): the readline → lexer → parser → interpreter pipeline.
    bash.py           — The `!` (`sh` / `bash`) built-in command: run a bash command in the workspace.
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
    gh.py             — Utility to retrieve authenticated GitHub user's email and repository owner's email.
    linter.py         — Utilities for linting code.
    loader.py         — Utility for loading modules.
    misc.py           — The `problems`, `manage-config`, and `lock-status` commands.
    path_utils.py     — Utility functions for file and directory operations.
    scripts.py        — A set of utilities to manage Git repository workflows.
    search.py         — 'find' command: grep the solution stack for a regular expression.
    shell_utils.py    — Utility for running shell commands and capturing their output.
    show.py           — Browser utilities for visualizing solutions.
    solution_files.py — The `new` command and solution-file formatting (black / isort / autoflake).
    summary.py        — Progress: parse .progress.html into problems.json and refresh in-memory state.
    update_doc.py     — Regenerate the machine-maintained sections of the guides under `docs/`.
  web/
    app.py            — aiohttp application: the SolverShell terminal, its PTY WebSocket, and the viewer.
    cli.py            — `solver-web`: lifecycle for the PTY-backed SolverShell web front end.
    pty_bridge.py     — PTY bridge: run an interactive `solver` shell on a pseudo-terminal.
```
<!-- /GEN:package-layout -->

### Command registration

Every shell command is a plain Python function decorated with `@register(help_text=..., aliases=..., pass_ctx=..., quietable=..., changes_workspace=...)` from `solver.shell`. The command name is derived from the function name (underscores → dashes; `usage` is synthesised from the signature). The decorator handles argument tokenisation (`shlex.split`), type coercion (Literal, bool, int, Optional, Enum), and tab-completion. Commands are collected at import time; `solver/modules.csv` (read by `shell/loader.py`) lists which modules to import on startup.

Functions still work as normal Python — they are not transformed, just registered. See `docs/developer-guide.md` for the full register contract.

### Command contract & blocks

Every command returns an `int` Unix exit code (`0` = success, non-zero = failure); the `@register`
adapter forwards it verbatim, and the `check_workspace_lock_command` / `check_workspace_lock_generic`
decorators (`core/lock.py`) preserve it. Input runs through a `lexer → parser → interpreter` pipeline
(authoritative spec: `docs/syntax.md`): commands compose with `;` (sequential), `&&` (on
success), `||` (on failure) and `{ … }` groups, nesting arbitrarily, with a newline as an implied `;`.
A statement is a command, a `name = expr` assignment, or a bare expression (`rcode` 0 when truthy, 1
when falsy) — so expressions gate `&&`/`||` chains. `loop <list>: <block>` is a language construct that
runs its `{ … }` (or inline) body once per element of a list, binding the current element to `{loop}`;
`break`/`continue`/`exit` are flow words. The lexer normalises input to a canonical guarded form (§8 of
docs/syntax.md). `solver <cmd>` exits with the block's status, so steps can be gated directly
(`solver "init 42 && eval && stack"`).

### Stack (solutions storage)

Solutions live in `solutions/<d0>/<d1>/<d2>/<d3>/` (one directory level per digit of the zero-padded four-digit problem number, e.g. problem 42 → `solutions/0/0/4/2/`).

- Problems 1–100: all files stored in plain text.
- Problems 101+: solution code, test cases, results, and notes are encrypted (AES-256, `.enc` suffix). `stack.py` handles transparent encrypt/decrypt via `read_stack_file` / `write_stack_file`.

The active workspace is `workspace/`. `init <n>` copies (unstacks) a problem's files there; `stack` saves them back (encrypting problems > 100), and `reset` re-stacks any changes then clears the workspace.

### Encryption key hierarchy

The crypto sub-package is three modules: `ciphers.py` (non-interactive: `config_dict` with all file
locations + git-filter wire constants — **no `solver.config` dependency** — plus load/lock/unlock and
encrypt/decrypt helpers), `keys.py` (all interactive create/persist/rotate/share and
the shell commands), and `gitfilter.py` (the git clean/smudge filter, depending only on `ciphers`).

- Per-user private key: `~/.solver/id` (X25519, PKCS8 PEM, password-protected). The password is read
  from `keys/.user-pass` (machine-local, a gitignored dotfile) so the load path needs no prompt.
- `keys/enc-key.json`: a single 32-byte master key, identified-by-public-key — `{<public-key-hex>:
  <master key wrapped to that key>}` plus a `verify` ciphertext for self-checking. One entry per
  authorised public key; no email is stored. Authority is proof-of-possession.
- Decryption path: read password → unlock private key → unwrap master key → verify → decrypt files.

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

Two AI entry points, both calling the Claude API. Install the optional deps with `pip install -e ".[ai]"` (`anthropic` + `python-dotenv`); the key is `ANTHROPIC_API_KEY`, read from the project `.env` (`models.py:get_api_key`).

- **`claude-api`** (`solver/ai/api.py`) generates solution artifacts, dispatching to per-target generators — `code.py` (Python/C), `docs.py` (notes), `facts.py` (test cases) — with prompts in `solver/templates/prompt_*.txt`. Default models: Opus for code (Python + C) and notes, Sonnet for test cases. The `costs` command (`models.py`) reports accumulated token spend.
- **`claude-skill`** (`solver/ai/skill.py`) launches Claude Code *inside* the running shell against the locked `workspace/`, via the `claude-euler-solver` skill (`.claude/skills/claude-euler-solver/`). Its actions are `solve` and `review`. The shell holds the workspace lock and the child Claude inherits it. The skill's standards live in the `docs/convention_*.md` guides (also injected into the `claude-api` prompts via `templates/engine.py`).

### Web front end (`solver-web`)

`solver-web` (`solver/web/cli.py`, console script + `python -m solver.web.cli`) runs a single localhost aiohttp server (default port `config.server_port` = 8080) as a **detached** child process, so it keeps serving after the launching shell exits. The detached child holds an exclusive `fcntl.flock` on a lock file (`.server.lock`) for its whole lifetime; that flock is the cross-process source of truth — any later `solver-web {status,stop,restart}` probes it (and reads the PID recorded in the file to signal it). The OS drops the lock on exit or crash, so there is no stale state and a recycled PID can never look "running". Actions: `start`, `stop`, `status` (default), `restart`; `--save` tees the shell's console output to the session log.

`build_app` (`solver/web/app.py`) wires three concerns into one server:
- **Terminal** — `GET /` serves an xterm.js page and `GET /ws` streams one interactive `solver` shell over a PTY (`solver/web/pty_bridge.py`). Only one PTY session is allowed at a time, since every session drives the shared `workspace/`.
- **Read-only viewer** — the summary/problem pages and problem files via `read_stack_file` (decrypting in memory, preferring the live workspace copy of the active problem). This replaced the retired `solver.utils.server`.
- **Edits** — `POST/DELETE /<n>/<file>` and `POST /<n>/eval` mutate or evaluate the active workspace problem; all are guarded by `check_workspace_lock_generic` and return HTTP 403 when the server is not authoritative over the workspace.

The detached server wraps its whole runtime in one `acquire_workspace_lock()` context: standalone it *acquires* the flock, launched from a running shell it *inherits* it, and every PTY child it forks re-enters and inherits the same lock (no flock conflict). The `show` command (`solver/utils/show.py`) calls `ensure_running()` to auto-start the server before opening a page; there is no separate `server` shell command any more.

## Solution Code Conventions

- Do NOT read solution files for problems > 100 (they are encrypted in the repo).
- For code structure and patterns, reference solutions in `solutions/0/0/*/` (problems 1–99).
- Build sieves, precomputed tables, and caches (`@cache`/`@lru_cache`, memo dicts) **inside** `solve()` (or in helpers it calls fresh each call), sized to the inputs — **not** at module level with a fixed bound. With `--runs=N` the harness times the repeated `solve()` calls, so anything built once at import (or a cache kept warm between runs) is excluded from the first run and free thereafter, understating the real cost. See `solutions/0/0/0/7/p0007_s0.py` (sieve sized to `n·ln n`) and `solutions/0/0/3/5/p0035_s0.py`.