## Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Mathematics and computing are not separate disciplines - they are two lenses on the same underlying structure.**
Project Euler sits at that intersection: problems that look like puzzles but reward the kind of thinking that
distinguishes an engineer from a programmer. The right algorithm does not just run faster; it reveals why brute
force was never the right question.

This repository is a record of that journey. Where multiple approaches were tried, all are sometimes kept:
the naïve solution alongside the elegant one, because the contrast is the lesson.

The framework around the solutions is deliberate. Problems are fetched, solutions are scaffolded and
benchmarked, and later problems are encrypted – all from a single interactive/web shell. An incorporated AI agent enables
reflection and learning: explore alternatives after solving a problem, translate Python to C for a performance
comparison, or articulate the mathematical insight in plain language.
**The point never is to get an answer but to understand why it is the answer.**

*In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), solutions and notes after the
first 100 problems are encrypted; for collaboration on those, please follow the instructions in
the [Key Exchange](docs/user-guide.md#7-key-exchange) section of the User Guide.*

---

### Documentation

The framework is documented in four guides under [`docs/`](docs/), plus the
authoritative command-language spec:

| Guide                                      | For                     | Covers                                                                           |
|--------------------------------------------|-------------------------|----------------------------------------------------------------------------------|
| [User Guide](docs/user-guide.md)           | using the shell         | launching, command blocks, variables, loops, the command catalogue, key exchange |
| [Solver Guide](docs/solver-guide.md)       | solving problems        | the `@runner.main` decorator, test cases, the solve workflow                     |
| [Developer Guide](docs/developer-guide.md) | extending the framework | the `@register` contract, command modules, the module loader                     |
| [Command Index](docs/commands-index.md)    | reference               | every command's aliases, flags, and exact usage                                  |
| [Language reference](docs/syntax.md)       | the command language    | surface syntax, canonical form, semantics                                        |

The command catalogue and command index are regenerated from the live registry by the
`update-docs` shell command - `solver "update-docs"` after changing any command's name,
alias, help, or usage (`solver "update-docs --check"` fails if they are stale).

This README covers everything *outside* those guides: installation, dependencies, and the
design notes.

---

### Installation

> **Prefer not to install?** A live instance of the web front end runs at
> **[euler.vikasmunshi.com](https://euler.vikasmunshi.com)** - the same `solver` shell,
> documentation viewer, and editor, all in the browser and served over HTTPS. Access is gated by a
> login (see [Access control](docs/access-control.md)); if you'd like an account to explore
> or collaborate, [reach out](mailto:vikas.munshi@gmail.com). To run your own copy, see the
> installation steps below.

Clone the repository and install system dependencies via [make](Makefile) or the bash [scripts](scripts);
the framework itself is installed with `pip`. Solutions can be written in any language – anything that runs as a
script or compiles to a binary will work.
The setup scripts and Makefile use `apt` and are tailored for Debian-based systems (Ubuntu). They are also
configured for Python and C, which is what I primarily use – feel free to adapt them for your own
OS, languages, and toolchains.
<details open>
<summary>one-line install (curl)</summary>

```bash
curl -fsSL https://raw.githubusercontent.com/vikasmunshi/euler/master/install.sh | bash
```

By default this clones to `~/euler` and runs `make install-all`. To choose a different path:

```bash
curl -fsSL https://raw.githubusercontent.com/vikasmunshi/euler/master/install.sh | bash -s -- --dir ~/projects/euler
```

</details>
<details>
<summary>or, install using make</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
make --version >/dev/null || sudo apt install build-essential
make install-all      # system deps + venv + all groups + git hooks + completions
source .venv/bin/activate
solver
```

Use `make install-minimal` instead to skip dev tools, AI dependencies, git hooks, and completions.
</details>
<details>
<summary>or, install using scripts and pip</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
./scripts/setup/dev_env.sh install python primesieve c
./scripts/setup/chrome.sh install
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[show,solutions]"   # add ai,dev groups for full install
solver
```

</details>

<a id="requirements"></a>
<details>
<summary><b>Requirements</b> - Python 3.14+ and optional dependency groups</summary>

Python 3.14+ and the dependencies listed in [`pyproject.toml`](pyproject.toml).
Dependencies are split into optional groups - install only what you need:

| Group       | Contents                                                                                                                 | When you need it                          |
|-------------|--------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| *(base)*    | `beautifulsoup4`, `cryptography`, `flake8`, `jsonschema`, `mypy`, `prompt-toolkit`, `requests`, `rich`, `types-requests` | using the solver framework                |
| `solutions` | `cython`, `mpmath`, `numpy`, `primesieve`, `setuptools`                                                                  | running some solutions                    |
| `show`      | `matplotlib`, `PyQt5`                                                                                                    | graphical output (`--show`)               |
| `ai`        | `anthropic`, `python-dotenv`                                                                                             | only when running `claude-api`            |
| `dev`       | `autoflake`, `autopep8`, `black`, `isort`                                                                                | `lint --auto-fix` and solution formatting |
| `web`       | `aiohttp`                                                                                                                | for `solver-web`                          |

</details>

### Quick start

[![Screenshot](docs/screenshot.png)](docs/screenshot.png)

```
$ solver
╭─ ▎ solver ───────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                      │
│  SOLVER  v2                                                                                          │
│    Your Euler problem solving companion in the terminal                                              │
│    Powered by claude.ai · prompt-toolkit · rich                                                      │
│                                                                                                      │
│    start with ls [number|next|random], then eval / benchmark                                         │
│    ? help                                                                                            │
│                                                                                                      │
╰──────────────────────────────────────────────────────────────────────── type exit or Ctrl-D to quit ─╯
▎ ❯ loop {solved}: {
▎ ·   benchmark {loop.number} --silent || break;
▎ ·   }
```

Launch the web-based solver shell with `solver-web` or launch the interactive terminal with `solver` (or
`python -m solver`); Type `?` for the command list, `? <cmd>` for usage, and `exit` / Ctrl-D to quit. `solver` can also
be driven non-interactively by passing a quoted command block (`solver "eval 42; benchmark 42"`), exiting with the
block's status. The full workflow - `new`, `eval`, `benchmark`, `mark` - is in
the [User Guide](docs/user-guide.md) and [Solver Guide](docs/solver-guide.md);
the [Command Index](docs/commands-index.md) lists every command.

A note on the AI assistance: two complementary paths are wired into the shell, both
aimed at deepening understanding rather than skipping it - the single-shot
**`claude-api`** (generate a solution, notes, or test cases) and the agentic
**`claude-skill`** / `! claude` (Claude Code working directly on a problem's solution files). Both need
the `ai` dependency group and an `ANTHROPIC_API_KEY`; see the
[User Guide](docs/user-guide.md#5-ai-assistance) for the trade-offs.

### For the nerds

- **Interactive shell** - `prompt-toolkit`-based REPL with persistent history, auto-suggest, tab
  completion (including bash-native completion for `!`-prefixed commands), `{name}` variables and
  side-effect-free expressions (comparisons, arithmetic, indexing/slicing, safe builtins), and a
  `loop <list>: <block>` construct over sliceable problem lists (`{problems}`, `{solved}`,
  `{unsolved}`). The command language - surface syntax, canonical form, and semantics - is specified in
  [`docs/syntax.md`](docs/syntax.md).
- **Rich UI** - `rich` panels, tables, and a themed colour palette throughout, so the terminal output is as
  readable as a rendered page.
- **Web front end** - `solver-web` runs a single localhost `aiohttp` server (port 8080) with three concerns
  in one place: a browser **terminal** (xterm.js over a PTY running a real `solver` shell), a read-only
  **viewer** that assembles each problem's page - statement, notes, and benchmark results - on the fly, and an
  in-browser **editor** that saves, evaluates, and deletes a problem's solution files. It runs detached
  (survives the launching shell); `solver-web start|stop|status|restart` manages it, and `show N` auto-starts
  it to open a problem (or the index) in the browser.
- **Hosted over HTTPS** - the web front end is served publicly at
  [euler.vikasmunshi.com](https://euler.vikasmunshi.com). **Caddy** terminates TLS and reverse-proxies to the
  loopback aiohttp server, loading a Let's Encrypt certificate that **acme.sh** issues and auto-renews through a
  name.com **DNS-01** challenge (no inbound port 80). Access is gated in the app - not Caddy - by browser-side
  **SRP-6a** login (the password never crosses the wire), with per-identity **profiles** (admin / user / guest)
  deciding which commands and routes each caller may use. The setup script
  (`scripts/setup/frontend.sh`) installs Caddy + acme.sh and issues the cert; the front end is being
  rebuilt as isolated services per the [secure web server](docs/secure-web-server.md) design (see
  also [access control](docs/access-control.md)).
- **Problem scraping** - fetches and caches problem statements directly from projecteuler.net; no manual copy-paste.
- **Solution evaluation** - subprocess-based test harness with configurable timeouts, result recording, and support for
  any language that compiles or runs as a script.
- **Transparent encryption** - solutions for #101+ are encrypted at rest with AES-256-GCM; each file-encryption key is
  itself wrapped by a per-user master key, delivered via X25519 ECDH + HKDF-SHA256 + ChaCha20-Poly1305, with
  n-of-m secret sharing for master-key recovery.
- **AI Agents** - two paths to an agentic assistant:
    - the single-shot Claude **API** (`claude-api py|c|notes|test-cases`) for solutions and documentation,
    - and full **Claude Code** driven from the shell both interactively (`! claude`)
      and headless (`claude-skill <action>`, via the `claude-euler-solver` skill);
    - API token costs per `solver` session are tracked, use the command `costs` to show.
- **Performance dashboard** - benchmarks solutions and records execution times, building a personal history of the
  journey through the problems.

<details>
<summary>architecture &amp; package layout</summary>

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
    skill.py          — The `claude-skill` command: run Claude Code in-shell against a problem's solution files.
    update_models.py  — The `update-models` command: refresh the `Model` enum, pricing, and FX rate.
  auth/               — The authorization kernel — identity, profiles, and permissions (DD-12).
    authorizations.py — The authorization policy — ``authorizations.json`` (DD-12).
    identity.py       — Identity resolution → a :class:`~solver.auth.subject.Subject` (DD-9/DD-12).
    subject.py        — The authorization **subject** — the resolved security principal (DD-12).
  core/
    download.py       — Utility for downloading and caching files via HTTP.
    evaluate.py       — Solution evaluation: runs standalone scripts against test cases and reports results.
    list.py           — List solution directory contents.
    new.py            — The `new` command and solution-file formatting (black / isort / autoflake).
    problems.py       — The Problem model plus the projecteuler.net problem scraper and on-disk cache.
    results.py        — Results: save and retrieve problem results.
    test_cases.py     — Load test cases for evaluation
    viewer.py         — Open a problem or its files in the web front end: the `show` and `edit` commands.
  crypto/
    ciphers.py        — Ciphers: read keys from disk and lock/unlock, encrypt/decrypt with no user interaction.
    config.py         — Crypto configuration: the single source of truth for every file location and git-filter wire constant.
    gitfilter.py      — Transparent git clean/smudge encryption for tracked solution files.
    keys.py           — Cipher key management: create, persist, rotate and share the crypto key material.
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
    gh.py             — Utility to retrieve authenticated GitHub user's email and repository owner's email.
    linter.py         — Utilities for linting code.
    loader.py         — Utility for loading command modules.
    misc.py           — The `problems` and `manage-config` commands.
    path_utils.py     — Utility functions for file and directory operations.
    scripts.py        — A set of utilities to manage Git repository workflows.
    search.py         — 'find' command: grep the solution stack for a regular expression.
    shell_utils.py    — Utility for running shell commands and capturing their output.
    summary.py        — Progress: parse .progress.html into problems.json and refresh in-memory state.
    update_doc.py     — Regenerate the machine-maintained sections of the guides under `docs/`.
  web/                — The web app services (see docs/secure-web-server.md).
    csp.py            — Content-Security-Policy middleware with a per-response nonce (shared, DD-5).
    auth/             — Web authentication: the auth service and its clients (DD-6/DD-7/DD-9).
      __main__.py     — Auth service entry point: ``python -m solver.web.auth`` (DD-5).
      admin.py        — The admin-plane CLI: run **under sudo** by the ``users`` shell command (DD-6/DD-12).
      app.py          — The auth service: public + admin aiohttp apps over unix sockets (DD-6/DD-9).
      client.py       — Minimal HTTP-over-unix-socket client for the auth service (stdlib only).
      commands.py     — The ``users`` shell command: account administration, split by permission (DD-12).
      config.py       — Auth-service runtime configuration, read from the environment (DD-5/DD-6).
      mail.py         — Outbound mail via the loopback relay (DD-8).
      pages.py        — The auth service's HTML pages: login, registration, reset, forgot (DD-7).
      pending.py      — Pending invite / reset store at ``<state>/pending.json`` (DD-7).
      policy.py       — Auth policy constants (lifetimes, cookie names, password and OTP rules).
      ratelimit.py    — A small in-memory sliding-window rate limiter for the auth endpoints.
      remember.py     — Persistent "remember me" tokens at ``<state>/remember.json`` (DD-6).
      sessions.py     — In-memory web session table (DD-6).
      srp.py          — Secure Remote Password (SRP-6a) primitives for web authentication.
      storage.py      — Shared JSON persistence for the auth stores (DD-6).
      tickets.py      — One-time shell tickets: web identity for PTY children (DD-9).
      users.py        — User store: the SRP verifier database at ``<state>/users.json`` (DD-6).
```
<!-- /GEN:package-layout -->

Every shell command is a plain Python function decorated with `@register(...)`
(defined in `solver/shell/register.py`, re-exported from `solver.shell`). The decorator handles
`shlex` tokenisation, type coercion (`Literal` / `bool` / `int` / `Optional`), and tab-completion;
commands are collected at import time, and `solver/modules.csv` lists the modules loaded
on startup. Framework built-ins (`echo`, `clear`, `?`, `!`) are registered the same way
from `shell/builtins.py` and `shell/bash.py`. The full contract is documented in
the [Developer Guide](docs/developer-guide.md).

Every command returns an `int` exit code (`0` = success), so the shell composes them into command
blocks - `;` (sequential), `&&` (on success), `||` (on failure), and `{ … }` groups - through the
`lexer → parser → interpreter` pipeline. `loop`, `break` / `continue` / `exit`, `{name}` variables, and
side-effect-free expressions are language constructs (not commands); `solver <cmd>` exits with the
block's status. The language is specified end-to-end in
[`docs/syntax.md`](docs/syntax.md).

</details>

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

### Third-party dependencies

The framework's Python dependencies are declared in [`pyproject.toml`](pyproject.toml), split into
the optional groups summarised under [Requirements](#requirements) above (`solutions`, `show`, `ai`,
`dev`, `web`) - install only what you need.

The web front end bundles its JavaScript/CSS assets locally so it runs fully offline, with no CDN
calls. These vendored assets live under `solver/web-content/vendor/` - xterm.js (MIT),
highlight.js (BSD-3-Clause), CodeJar (MIT), MathJax (Apache-2.0), and Devicon (MIT). Each is
redistributed under its permissive license; the full license texts and an inventory of every file
are in the [vendor README](solver/web-content/vendor/README.md).

### Authors

**Vikas Munshi** - [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)
If a problem catches your eye, or you want to collaborate on the encrypted ones, feel free to reach out.
Curiosity is always welcome and fun.

**Claude** (Anthropic) - pair-programmed the solver framework and AI integration from inside its own shell.

---
