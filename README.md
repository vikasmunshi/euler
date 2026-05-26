## Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Mathematics and computing are not separate disciplines - they are two lenses on the same underlying structure.**
Project Euler sits at that intersection: problems that look like puzzles but reward the kind of thinking that
distinguishes an engineer from a programmer. The right algorithm does not just run faster; it reveals why brute
force was never the right question.

This repository is a record of that journey. Every solution here was worked out by hand first -
the code is the proof, not the shortcut. Where multiple approaches were tried, both are sometimes kept:
the naïve solution alongside the elegant one, because the contrast is the lesson.

The framework around the solutions is deliberate. Problems are fetched, workspaces managed, solutions
benchmarked, and results encrypted - all from a single interactive shell. AI assists at the reflection
stage, not the discovery stage: to explore alternatives after you have solved a problem, translate
Python to C for a performance comparison, or articulate the mathematical insight in plain language.
The point is never to get an answer. The point is to understand why it is the answer.

**In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), only solutions to problems
numbered 1 through 100 are stored unencrypted**. Solutions and notes beyond problem #100 are encrypted at rest;
for collaboration on those, please follow the instructions in the [Key Exchange](#key-exchange) section.
---

### Installation

Clone the repository and install system dependencies via [make](Makefile) or the bash [scripts](scripts);
the framework itself is installed with `pip`. Solutions can be written in any language - anything that runs as a
script or compiles to a binary will work.
The setup scripts and Makefile use `apt` and are tailored for Debian-based systems (Ubuntu). They are also
configured for Python and C, which is what I primarily use - feel free to adapt them for your own
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
mkdir workspace
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

### Interactive Shell

The interactive shell is built on [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) and
[rich](https://rich.readthedocs.io/). It provides persistent history, auto-suggest, tab-completion, and typed
parameter dispatch.

```
$ solver
╭─ ▎ solver ──────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                     │
│  SOLVER                                                                                             │
│                                                                                                     │
│    Your Euler problem solving companion in the terminal                                             │
│    Powered by claude.ai · prompt-toolkit · rich                                                     │
│                                                                                                     │
│    start with init <problem number> to initialize the workspace with problem files                  │
│    show to read the problem documentation                                                           │
│    eval and benchmark to check your solutions                                                       │
│    stack/reset to save/discard                                                                      │
│                                                                                                     │
│    ? help   ! bash                                                                                  │
│                                                                                                     │
╰──────────────────────────────────────────────────────────── type exit or press Ctrl-D to quit ──────╯
▎ workspace ❯ server start
server started - http://localhost:8080
server('start') → ok
▎ workspace ❯
```

Launch with `solver`. Type `?` for a command list, `? <cmd>` for usage details,
or `exit` / Ctrl-D to quit.
A local HTTP server starts on port 8080; use `show` to open the current
problem or the index page in Chrome.

#### Command-line arguments

`solver` can be launched interactively or driven non-interactively by passing one or
more shell commands as positional arguments.

| Argument           | Description                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------------|
| `-v`, `--version`  | Print the version and exit                                                                         |
| `-c`, `--continue` | Stay interactive after the queued `cmdline` commands finish                                        |
| `-s`, `--save`     | Tee console output to the session log file                                                         |
| `-h`, `--help`     | Show the argparse help message and exit                                                            |
| `cmdline`          | One or more shell commands; quote and semicolon-separate. Exits after running unless `-c` is given |

Examples:

```bash
solver                                 # launch the interactive shell
solver "init 42; eval; reset"          # run commands, then exit
solver -c "init 42"                    # run commands, then stay interactive
solver -s "init 42; benchmark"         # also tee console output to the session log
```

<details>
<summary>Command reference</summary>

| Command                      | Aliases                | Description                                                      |
|------------------------------|------------------------|------------------------------------------------------------------|
| `help [cmd]`                 | `?`                    | List all commands, or show usage for a specific one              |
| `exit`                       | `quit`, `q`            | Exit the shell                                                   |
| `clear`                      | `cls`                  | Clear the screen                                                 |
| `! <cmd>`                    | `sh`, `bash`           | Run a bash command in the workspace directory                    |
| `for var in iterable { … }`  |                        | Loop over values executing a block of commands                   |
| `progress`                   |                        | Print solved/unsolved statistics                                 |
| `init <N>`                   |                        | Initialise the workspace for problem N                           |
| `reinit`                     |                        | Re-download and reinitialise the current problem                 |
| `list`                       | `ls`                   | List workspace files, highlighting differences against the stack |
| `stack`                      | `save`                 | Save workspace files back to the stack (runs linter first)       |
| `reset`                      |                        | Clear the workspace (optionally stacking changes first)          |
| `build`                      |                        | Compile all `.c` files in the workspace                          |
| `evaluate`                   | `eval`, `test`         | Run solutions against test cases                                 |
| `benchmark`                  |                        | Run solutions multiple times and record timing                   |
| `new`                        |                        | Create a new solution file from the template                     |
| `migrate`                    |                        | Migrate Python solutions to the current template                 |
| `mark-solved`                |                        | Check and mark the current workspace problem as solved           |
| `make <target>`              |                        | AI-generate a solution or documentation (see below)              |
| `costs`                      |                        | Show total Claude API cost for the session                       |
| `browser [N]`                | `show`, `view`, `open` | Open problem N (or current/index) in Chrome                      |
| `server [start/stop/status]` |                        | Manage the local HTTP server                                     |
| `summary`                    |                        | Regenerate the solutions index (`solutions/index.html`)          |
| `commit`                     |                        | Commit solutions and workspace to git                            |
| `publish [target]`           |                        | Push `solutions`, `solver`, `scripts`, or `keys` to remote       |
| `sync`                       |                        | Fetch and merge `origin/master`                                  |
| `status`                     |                        | Show diff between local branch and `origin/master`               |
| `upgrade [group]`            |                        | Upgrade pip packages for a dependency group                      |
| `git-hooks`                  | `hooks`                | Run pre-commit and simulated pre-push checks                     |
| `install <target>`           | `setup`                | Install `chrome`, `dev-env`, or `upgrade-service`                |
| `user`                       |                        | Show identity and master-key access; generate key if absent      |
| `rekey`                      |                        | *(admin only)* Rotate the encryption key pool                    |

#### user

`user` reports the current user's identity and indicates whether they have master-key
access (`✓ can encrypt/decrypt` in green, `✗ cannot` in red). It loads the X25519 private
key from `~/.ssh/id_solver`; if no key exists there - or `regen=true` is passed - a new
X25519 key pair is generated, persisted to `~/.ssh/id_solver`, and the corresponding
public key entry is written to `keys/keys.json` under the user's email.

```
user                        # show identity and access; generate a key pair on first run
user regen=true             # rotate to a freshly generated key pair
```

As a side effect, if the current user does not yet have master-key access, `user`
registers the `reconstruct` command for the rest of the shell session. It prompts for
`threshold` master-key shares (provided out-of-band by the admin user),
recovers the master key via [n-of-m secret sharing](solver/crypto/share.py), and
rewrites the user's `master_key` entry in `keys/keys.json`.

#### new

`new` creates a solution file scaffold in the workspace, named after the current problem and
numbered after any solutions already present (`p0042_s0.py`, `p0042_s1.py`, and so on).

```
new                         # create next Python solution file
new py_only=false           # create both .py and .c stubs
```

The generated file includes the standard `solve()` / `main()` structure that the test harness
expects. If `test_cases.json` does not yet exist in the workspace, an empty one is created.
Run `init <N>` first to set up the workspace before calling `new`.

#### eval

`eval` runs every solution in the workspace against the test cases and reports whether each
answer is correct, incorrect, or timed out. It is the primary correctness check.

```
eval                        # dev + main test cases, all solutions, single run
eval all                    # include extra test cases too
eval record=true            # persist results to results.json
eval show=true              # pass --show to the solution (graphical output)
eval lang=py                # restrict to Python solutions only
eval solution=p0042_s1.py   # run one specific solution
```

Test cases are tagged `dev` (examples from the problem statement), `main` (the real answer),
or `extra` (additional edge cases). `eval` defaults to `dev main`; pass `all` to include
`extra` as well. Results are not recorded by default - pass `record=true` to persist them.
`show=true` implies a single run and disables recording.

#### benchmark

`benchmark` measures execution time. It runs every solution across all test case categories,
repeats each run 21 times to average out noise, and always records the results.

```
benchmark                   # all categories, all solutions, 21 runs
benchmark runs=100          # more runs for tighter timing
benchmark lang=c            # C solutions only
benchmark reset=true        # clear previous results before recording
```

Use `eval` first to confirm correctness, then `benchmark` to measure and compare. The two
commands are complementary: one answers *is it right*, the other *how fast is it*.

#### for

`for` iterates over a sequence and dispatches each body line as a shell command, substituting
the loop variable by token match. It is most useful for bulk operations across many problems.

```
for n in solved {
  init n
  benchmark
  stack
  reinit
  stack
  reset
}
```

Supported iterable forms: `1..10` (inclusive range), `range(1, 11)`, `[1, 5, 10]`, `1,5,10`,
`problems` (all known problem numbers), `solved` (solved problem numbers only).

</details>

#### AI features

The goal of this repository is to make Project Euler a genuine learning exercise, not just a scoreboard.
The `make` command uses the Claude API to support that at each stage of the problem-solving lifecycle,
but the intent is always to deepen understanding, not to skip the thinking.

| Stage            | Command           | When to use                                                                                                                                                                                |
|------------------|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Before solving   | `make test-cases` | Most problems have well-defined test cases in the statement; this is mainly useful when they are implicit or when you want extra edge cases for validation.                                |
| After solving    | `make py`         | You have a working solution. Use this to explore alternative approaches - a different algorithm, a more Pythonic style, or a mathematical shortcut you hadn't considered.                  |
| Translating to C | `make c`          | Translate an existing Python solution to C for a performance comparison. The AI is given your Python code as context, so the output mirrors your approach rather than inventing a new one. |
| Reflecting       | `make notes`      | Summarise the mathematical insight behind the problem: what made it hard, what the key idea was, and what you learned. Useful for looking back at the journey later.                       |

`make` requires the `ai` dependency group (`pip install -e ".[ai]"`) and an `ANTHROPIC_API_KEY` in a
`.env` file at the repository root. Pass `model=<id>` to override the default, `force=true` to
overwrite an existing file. Use `costs` at any time to see accumulated token cost for the session.

### Key Exchange

Solutions for problems #101 and above are encrypted with AES-256 keys. Access to those keys is
controlled via a two-layer scheme described below.

#### keys/keys.json structure

```
keys.json
├── keys/               - pool of AES-256 file-encryption keys (min 32), each encrypted by the master key
│   └── <uuid7>
│       ├── value       - hex-encoded AES-256 key, encrypted with the master key
│       └── status      - active | reserved | retired
└── users/              - one entry per authorised user
    └── <email>
        ├── public_key  - user's X25519 public key (hex)
        └── master_key  - the master key wrapped for this user (null until granted by admin)
```

The **master key** is a 32-byte key used solely to encrypt and decrypt the file-encryption keys
in `keys`. It is never stored in the clear - each user holds their own encrypted copy, wrapped
with their X25519 public key using an ephemeral ECDH exchange (HKDF-SHA256 + ChaCha20-Poly1305).
When required the shell decrypts the master key from the user's `keys.json` entry using the private
key at `~/.ssh/id_solver`, then uses it to decrypt whichever file-encryption key a solution was
encrypted with.

#### Gaining access (new user)

```bash
solver user         # generates ~/.ssh/id_solver and registers your public key in keys/keys.json
solver publish keys # opens a pull request with the updated keys/keys.json
```

Once I merge the pull request, your `master_key` entry is populated, and you
can pull the update to gain access:

```bash
solver sync
solver user
```

#### Studying the solutions

To decrypt all problem files to the local `backup/` folder (gitignored, never committed):

```
for n in solved {
  init n
  ! cp -r workspace backup/n
  reset
}
```

Or use `browser N` to view any problem's statement, notes, and results directly in Chrome
via the built-in HTTP server without decrypting to disk.

#### Keys backup (admin only)

```bash
solver rekey backup=true
```

Writes the private key and master key entry to `backup/keys_backup.json` for offline storage.

### Requirements

Python 3.14+ and the dependencies listed in [`pyproject.toml`](pyproject.toml).
Dependencies are split into optional groups - install only what you need:

| Group       | Contents                                                                                                                 | When you need it                        |
|-------------|--------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| *(base)*    | `beautifulsoup4`, `cryptography`, `flake8`, `jsonschema`, `mypy`, `prompt-toolkit`, `requests`, `rich`, `types-requests` | using the solver framework              |
| `solutions` | `numpy`, `pyprimesieve`                                                                                                  | running some solutions                  |
| `show`      | `matplotlib`, `PyQt5`                                                                                                    | graphical output (`--show`)             |
| `ai`        | `anthropic`                                                                                                              | AI code/notes generation                |
| `dev`       | `autoflake`, `autopep8`, `black`, `isort`                                                                                | reformatting solution files (`migrate`) |

### For the nerds

- **Interactive shell** - `prompt-toolkit`-based REPL with persistent history, auto-suggest, tab
  completion (including bash-native completion for `!`-prefixed commands), and a `for`-loop construct
  with integer ranges, Python `range()`, list literals, and named iterables (`problems`, `solved`).
- **Rich UI** - `rich` panels, tables, and a themed colour palette throughout; a lightweight HTTP server
  (port 8080) serves solution files and the progress index so everything renders in a real browser.
- **Problem scraping** - fetches and caches problem statements directly from projecteuler.net; no manual copy-paste.
- **Solution evaluation** - subprocess-based test harness with configurable timeouts, result recording, and support for
  any language that compiles or runs as a script.
- **Transparent encryption** - X25519 ECDH key exchange, HKDF-SHA256 derivation, ChaCha20-Poly1305 encryption; solutions
  for #101+ are encrypted at rest with per-user master key access.
- **AI generation** - `make py|c|notes|test-cases` calls the Claude API to generate solutions and documentation;
  token costs are tracked per model and reported with `costs`.
- **Performance dashboard** - benchmarks solutions and records execution times, building a personal history of the
  journey through the problems.

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

### Author

**Vikas Munshi** - [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)
If a problem catches your eye, or you want to collaborate on the encrypted ones, feel free to reach out.
Curiosity is always welcome here.
---