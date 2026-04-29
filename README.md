## Project Euler Solutions

[![Python](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

I have always been drawn to mathematical puzzles — **the space where constraints and possibilities intersect is a source
of endless creative joy**.

Over the years I solved some Project Euler problems, only to lose the solutions each time a computer was replaced.
Eventually I decided to put them on GitHub with encryption so they would survive.[^1]

Beyond preservation, this repository is meant to document the journey: solving problems, uncovering the mathematical
insights behind efficient algorithms, and demonstrating how deeply mathematics and computing are intertwined.
The problems here are not just puzzles to be solved, but opportunities to learn and teach.

This is a Python package that provides an interactive shell for fetching problem statements, managing per-problem
workspaces, running solutions against test cases, and securely storing private solutions.

[^1]: This is my second framework — I lost the encrypted keys for the first one to yet another computer replacement.
**In accordance with [Project Euler's guidelines](https://projecteuler.net/about#publish), only solutions to problems
numbered 1 through 100 are stored unencrypted**. Solutions beyond problem #100 are encrypted at rest; for collaboration
on those, please follow the instructions in the [Key Exchange](#key-exchange) section.

---

### Installation

Clone the repository and install system dependencies via [make](Makefile) or the bash [scripts](scripts);
the framework itself is installed with `pip`. Solutions can be written in any language — anything that runs as a
script or compiles to a binary will work.

The setup scripts and Makefile use `apt` and are tailored for Debian-based systems (Ubuntu). They are also
configured for Python and C, which is what I primarily use — feel free to adapt them for your own
OS, languages, and toolchains.

<details open>
<summary>install using make (cleanest)</summary>

```bash
git clone https://github.com/vikasmunshi/euler.git
cd euler
make --version >/dev/null || sudo apt install build-essential
make install
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
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
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
Help     ? | help | <cmd> -h              list commands or describe a specific command
Exit     Ctrl-D | exit
Launch   solver "cmd1; cmd2"              preload commands and stay interactive
         solver -c "cmd1; cmd2"           preload commands and exit when done
Flags    --key-word | --no-key-word       boolean True / False
         --silent                         suppress command output
────────────────────────────────────────────────────────────────────────────────────────────────────
Commands:
alias               eval                exit                for                 full-stack-backup  
full-stack-restore  gh-login            gh-status           git-add-stack       git-merge  
git-status          help                init                ls                  problems  
rekey               shell               stack               stack-clear         upload_keys  
user  
────────────────────────────────────────────────────────────────────────────────────────────────────
Aliases:
eval-pub    ->  for n in 1 to 100: init n --silent; eval --record; stack-clear --silent; shell echo processed n
restack     ->  for n in 1 to 988: init n; stack-clear --silent; shell echo processed n
pre-commit  ->  shell pre-commit run --all-files
────────────────────────────────────────────────────────────────────────────────────────────────────
euler$
```

### Key Exchange

Solutions for problems #101 and above are encrypted with AES-256 keys. Access to those keys is
controlled via a two-layer scheme described below.

#### keys/keys.json structure

```
keys.json
├── keys/          — pool of AES-256 file-encryption keys (min 32), each encrypted by the master key
│   └── <uuid7>
│       ├── value  — hex-encoded AES-256 key, encrypted with the master key
│       └── status — active | reserved | retired
└── users/         — one entry per authorised user
    └── <email>
        ├── public_key  — user's X25519 public key (hex)
        └── master_key  — the master key wrapped for this user (null until granted by admin)
```

The **master key** is a 32-byte key used solely to encrypt and decrypt the file-encryption keys
in `keys`. It is never stored in the clear — each user holds their own encrypted copy, wrapped
with their X25519 public key using an ephemeral ECDH exchange (HKDF-SHA256 + ChaCha20-Poly1305).

When required the shell decrypts the master key from the user's `keys.json` entry using the private
key at `~/.ssh/id_solver`, then uses it to decrypt whichever file-encryption key a solution was
encrypted with.

#### Gaining access (new user)

```bash
solver -c "user"         # generates ~/.ssh/id_solver and registers your public key in keys/keys.json
solver -c "upload_keys"  # opens a pull request with the updated keys/keys.json
```

Once I merge the pull request, your `master_key` entry is populated, and you
can pull the update to gain access:

```bash
solver -c "git-merge; user"
```

#### Studying the solutions

To study or review solutions outside the shell, decrypt the entire stack to the local `backup/`
folder (gitignored, never committed):

```bash
solver -c "full-stack-backup"
```

This decrypts every problem's files from `stack/` into `backup/<problem-number>/`, mirroring the
directory structure. Before writing, the command automatically ensures `/backup/` is listed in
`.gitignore` — so the decrypted files can never accidentally be committed. The inverse,
`full-stack-restore`, re-encrypts them back into the stack.

#### Keys backup (admin only)

I maintain an offline backup of the master key via
`solver -c "rekey --backup"`, which writes my private key and master key entry to
`backup/keys_backup.json`.
Yes, this is specifically designed to survive computer replacements. Yes, it is kept in multiple
places. No, we are not going through a third framework.

### Requirements

Python 3.14+ and the dependencies listed in [`pyproject.toml`](pyproject.toml). If your curiosity
brought you this far, the full list is worth a read — the packages are as interesting as the problems.

### For the nerds

- **Interactive shell** — `cmd.Cmd`-based REPL with readline history, tab completion, command aliases, and typed
  parameter dispatch.
- **Problem scraping** — fetches and caches problem statements directly from projecteuler.net; no manual copy-paste.
- **Solution evaluation** — subprocess-based test harness with configurable timeouts, result recording, and support for
  any language that compiles or runs as a script.
- **Transparent encryption** — X25519 ECDH key exchange, HKDF-SHA256 derivation, ChaCha20-Poly1305 encryption; solutions
  for #101+ are encrypted at rest with per-user master key access.
- **Performance dashboard** — benchmarks solutions and records execution times, building a personal history of the
  journey through the problems.

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

### Author

**Vikas Munshi** — [vikas.munshi@gmail.com](mailto:vikas.munshi@gmail.com)

If a problem catches your eye, or you want to collaborate on the encrypted ones, feel free to reach out.
Curiosity is always welcome here.

---

