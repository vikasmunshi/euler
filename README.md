## Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

I have always been drawn to mathematical puzzles - **the space where constraints and possibilities intersect is a source
of endless creative joy**.

Over the years I solved some Project Euler problems, only to lose the solutions each time a computer was replaced.
Eventually I decided to put them on GitHub with encryption so they would survive.[^1]

Beyond preservation, this repository is meant to document the journey: solving problems, uncovering the mathematical
insights behind efficient algorithms, and demonstrating how deeply mathematics and computing are intertwined.
The problems here are not just puzzles to be solved, but opportunities to learn and teach.

This is a Python package that provides an interactive shell for fetching problem statements, managing per-problem
workspaces, running solutions against test cases, and securely storing private solutions.

[^1]: This is my second framework - I lost the encrypted keys for the first one to yet another computer replacement.
**In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), only solutions to problems
numbered 1 through 100 are stored unencrypted**. Solutions beyond problem #100 are encrypted at rest; for collaboration
on those, please follow the instructions in the [Key Exchange](#key-exchange) section.

---

### Installation

Clone the repository and install system dependencies via [make](Makefile) or the bash [scripts](scripts);
the framework itself is installed with `pip`. Solutions can be written in any language - anything that runs as a
script or compiles to a binary will work.

The setup scripts and Makefile use `apt` and are tailored for Debian-based systems (Ubuntu). They are also
configured for Python and C, which is what I primarily use - feel free to adapt them for your own
OS, languages, and toolchains.

<details open>
<summary>install using make (cleanest)</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
make --version >/dev/null || sudo apt install build-essential
make install          # installs all groups: show, solutions, dev
source .venv/bin/activate
solver
```

</details>

<details>
<summary>or, alternatively, install using scripts and pip</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
./scripts/setup_dev_env.sh install python primesieve c
./scripts/setup_chrome.sh install
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[show,solutions]"   # add dev group for full install
solver
```

</details>


<details>
<summary>or, if you enjoy living dangerously, don't install</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m solver
```

</details>

### Interactive Shell

The interactive shell provides a command-line interface for managing and evaluating Project Euler solutions.
Invoke it with `solver` (or `python -m solver`) and type `help` at the prompt to list available commands.

```
$ solver
────────────────────────────────────────────────────────────────────────────────────────────────────
Project Euler Solver Shell
────────────────────────────────────────────────────────────────────────────────────────────────────
Help    ? | help                        list commands and aliases
        ?<cmd> | help <cmd>             show help on command
Exit    Ctrl-D | exit
Launch  solver                          launch interactive shell
        solver "cmd1; cmd2"             execute commands and exit
        solver -c "cmdline"             execute cmdline, then continue in interactive shell
Flags   --key-word | --no-key-word      boolean True / False
        --silent                        suppress command output
────────────────────────────────────────────────────────────────────────────────────────────────────
Commands:
alias               exit                help                rekey               upload_keys  
clear               for                 init                shell               user  
echo                full-stack-backup   ls                  show  
eval                full-stack-restore  problems            stack  
────────────────────────────────────────────────────────────────────────────────────────────────────
Aliases:
eval-pub      -> for n in 1 to 100: init n --silent; eval --record; clear --silent; echo evaluated n
eval-show     -> for n in 1 to 100: init n --silent; eval --show; clear --discard-changes --silent; echo evaluated n
gh-login      -> shell gh auth status || gh auth login
gh-status     -> shell gh auth status
git-add-stack -> shell git add <path>/euler/solutions/
git-merge     -> shell git fetch origin && git merge --ff-only origin/master
git-status    -> shell git status | less
pre-commit    -> shell pre-commit run --all-files
restack       -> for n in 1 to 988: init n --silent; clear; echo restacked n
────────────────────────────────────────────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────────────────────────────────────────────
Session started at YYYY-MM-DD hh:mm:ss.  
────────────────────────────────────────────────────────────────────────────────────────────────────  
euler$
```

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
solver upload_keys  # opens a pull request with the updated keys/keys.json
```

Once I merge the pull request, your `master_key` entry is populated, and you
can pull the update to gain access:

```bash
solver "git-merge; user"
```

#### Studying the solutions

To study or review solutions outside the shell, decrypt the entire stack to the local `backup/`
folder (gitignored, never committed):

```bash
solver full-stack-backup
```

This decrypts every problem's files from `stack/` into `backup/<problem-number>/`, mirroring the
directory structure. Before writing, the command automatically ensures `/backup/` is listed in
`.gitignore` - so the decrypted files can never accidentally be committed. The inverse,
`full-stack-restore`, re-encrypts them back into the stack.

#### Keys backup (admin only)

I maintain an offline backup of the master key via
`solver "rekey --backup"`, which writes my private key and master key entry to
`backup/keys_backup.json`.
Yes, this is specifically designed to survive computer replacements. Yes, it is kept in multiple
places. No, we are not going through a third framework.

### Requirements

Python 3.14+ and the dependencies listed in [`pyproject.toml`](pyproject.toml) & [`requirements.txt`](requirements.txt).
Dependencies are split into optional groups - install only what you need:

| Group       | Contents                                                                                    | When you need it                 |
|-------------|---------------------------------------------------------------------------------------------|----------------------------------|
| *(base)*    | `beautifulsoup4`, `cryptography`, `jsonschema`, `requests`                                  | using the solver framework       |
| `solutions` | `numpy`, `pyprimesieve`                                                                     | running some solutions           |
| `show`      | `matplotlib`, `PyQt5`                                                                       | graphical output (`--show`) |
| `dev`       | `black`, `flake8`, `mypy`, `isort`, `autopep8`, `autoflake`, `pre-commit`, `types-requests` | framework development            |

### For the nerds

- **Interactive shell** - `cmd.Cmd`-based REPL with readline history, tab completion, command aliases, and typed
  parameter dispatch.
- **Problem scraping** - fetches and caches problem statements directly from projecteuler.net; no manual copy-paste.
- **Solution evaluation** - subprocess-based test harness with configurable timeouts, result recording, and support for
  any language that compiles or runs as a script.
- **Transparent encryption** - X25519 ECDH key exchange, HKDF-SHA256 derivation, ChaCha20-Poly1305 encryption; solutions
  for #101+ are encrypted at rest with per-user master key access.
- **Performance dashboard** - benchmarks solutions and records execution times, building a personal history of the
  journey through the problems.

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

### Author

**Vikas Munshi** - [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)

If a problem catches your eye, or you want to collaborate on the encrypted ones, feel free to reach out.
Curiosity is always welcome here.

---

