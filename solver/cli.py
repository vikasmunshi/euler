#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Interactive solver shell with persistent history and command dispatch."""
from __future__ import annotations

from cmd import Cmd
from contextlib import redirect_stdout
from datetime import datetime
from functools import partial
from os import X_OK, access, devnull, environ
from pathlib import Path
from re import escape as re_escape, search as re_search, sub as re_sub
from readline import (backend as readline_backend, get_completer, get_completer_delims, parse_and_bind,
                      read_history_file, set_completer, set_completer_delims, set_history_length, write_history_file)
from subprocess import CalledProcessError, run
from sys import argv, modules as sys_modules
from types import TracebackType
from typing import Any, Callable, ClassVar, IO, Literal, cast, get_args, get_origin
from uuid import uuid7

from solver.cli_utils import bool_flags, coerce, dedup_history, func_info, safe_split
from solver.config import ColorCodes, root_dir, stack_dir
from solver.crypto import rekey, user
from solver.evaluate import evaluate
from solver.problems import problems
from solver.stack import backup_the_stack, restore_the_stack
from solver.utils import continue_on_error, format_command_line, show_value, upload_keys
from solver.workspace import clear_the_workspace, init_the_workspace, list_the_workspace, stack_the_workspace

__all__ = ['SolverShell', 'cli']

CYAN, GREEN, YELLOW, BLUE, BLACK, GRAY, RED, BOLD, RESET = (ColorCodes.CYAN, ColorCodes.GREEN, ColorCodes.YELLOW,
                                                            ColorCodes.BLUE, ColorCodes.BLACK, ColorCodes.GRAY,
                                                            ColorCodes.RED, ColorCodes.BOLD, ColorCodes.RESET)
BOLD = BOLD
C_CMD = BLUE
C_LBL = BLACK
C_TXT = GRAY
_lw, _cw = 7, 31  # label column width, command column width
banner: str = f"""\
{CYAN}{"─" * 100}
{GREEN}{BOLD}Project Euler Solver Shell{RESET}
{CYAN}{"─" * 100}
{C_LBL}{"Help":<{_lw}} {C_CMD}{"? | help":<{_cw}} {C_TXT}list commands and aliases
{C_LBL}{" ":<{_lw}} {C_CMD}{"?<cmd> | help <cmd>":<{_cw}} {C_TXT}show help on command
{C_LBL}{"Exit":<{_lw}} {C_CMD}Ctrl-D | exit
{C_LBL}{"Launch":<{_lw}} {C_CMD}{"solver":<{_cw}} {C_TXT}launch interactive shell
{C_LBL}{" ":<{_lw}} {C_CMD}{"solver \"cmd1; cmd2\"":<{_cw}} {C_TXT}execute commands and exit
{C_LBL}{" ":<{_lw}} {C_CMD}{"solver -c \"cmdline\"":<{_cw}} {C_TXT}execute cmdline continue in interactive shell
{C_LBL}{"Flags":<{_lw}} {C_CMD}{"--key-word | --no-key-word":<{_cw}} {C_TXT}boolean True / False
{C_LBL}{" ":<{_lw}} {C_CMD}{"--silent":<{_cw}} {C_TXT}suppress command output{RESET}"""


class SessionCapture:
    """Context-managed stdout tee: writes to both the terminal and a session log file."""
    __slots__ = ('_file', '_filename', 'original', 'solver')
    _file: IO[str]
    _filename: str
    original: IO[str]
    solver: SolverShell

    def __init__(self, solver: SolverShell) -> None:
        self._filename = f'{uuid7().hex}.txt'
        self.solver = solver

    def __enter__(self) -> SessionCapture:
        _sys = sys_modules['sys']
        (root_dir / 'sessions').mkdir(exist_ok=True)
        self.original = _sys.stdout
        self._file = (root_dir / 'sessions' / self._filename).open('w')
        _sys.stdout = cast(IO[str], cast(object, self))  # type: ignore [attr-defined]
        self.solver.stdout = _sys.stdout
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_value: BaseException | None,
                 tb: TracebackType | None) -> None:
        _sys = sys_modules['sys']
        _sys.stdout = self.original  # type: ignore [attr-defined]
        self.solver.stdout = _sys.stdout
        self._file.close()

    def write(self, s: str) -> int:
        self.original.write(s)
        self._file.write(s)
        return len(s)

    def flush(self) -> None:
        self.original.flush()
        self._file.flush()

    def writable(self) -> bool:
        return self.original.writable() and self._file.writable()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.original, name)


class SolverShell(Cmd):
    """The solver shell."""
    aliases: ClassVar[dict[str, str]] = {}
    allowed_prefixes: ClassVar[tuple[str, ...]] = ('/bin', '/sbin', '/usr', '/home')
    banner: ClassVar[str] = banner
    exe_cache: ClassVar[list[str]] = []
    history_file: ClassVar[Path] = root_dir / '.solver_history'
    identchars: str = Cmd.identchars + ':-'
    prompt = 'euler$ '
    workspace_dir: ClassVar[Path] = root_dir / 'euler'

    def __str__(self) -> str:
        return f'SolverShell(workspace_dir={self.workspace_dir.as_posix()!r})'

    def execute(self, intro: Any | None = None, commands: list[str] | None = None) -> int:
        """Run the shell session, invoking the 'pre/post' method hooks by name, and return 0 on clean exit."""
        if commands:
            self.cmdqueue.extend(commands)
        self.cmdloop(intro=intro)
        return 0

    def preloop(self) -> None:
        """Load readline history and print the welcome banner before the command loop starts."""
        set_completer_delims(get_completer_delims().replace(':', '').replace('-', ''))
        try:
            read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        self.do_help('')
        print(f'\n{CYAN}{"─" * 100}\n'
              f'{GREEN}{BOLD}Session started at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.\n'
              f'{CYAN}{"─" * 100}{RESET}')

    def postloop(self) -> None:
        """Deduplicate, cap at 1000 entries, and persist readline history when the command loop exits."""
        dedup_history()
        set_history_length(1000)
        write_history_file(self.history_file)
        if hasattr(self, 'do_ls'):
            print(f'\n{CYAN}{"─" * 100}')
            self.do_ls('')
        print(f'\n{CYAN}{"─" * 100}\n'
              f'{GREEN}{BOLD}Session complete — goodbye!\n'
              f'{CYAN}{"─" * 100}{RESET}')

    def completenames(self, text: str, *ignored: Any) -> list[str]:
        """Return command names and alias names that start with text."""
        return super().completenames(text, *ignored) + [a for a in self.aliases if a.startswith(text)]

    def precmd(self, line: str) -> str:
        """Expand aliases before execution: exact match only."""
        if alias := self.aliases.get(line.strip()):
            return alias
        return line

    def cmdloop(self, intro: Any | None = None) -> None:
        """Run the command loop, printing ^C at the prompt instead of exiting on Ctrl-C."""
        self.preloop()
        if self.use_rawinput and self.completekey:
            self.old_completer = get_completer()
            set_completer(self.complete)  # type: ignore [arg-type]
            if readline_backend == 'editline':
                command_string = ('bind ^I rl_complete' if self.completekey == 'tab'
                                  else f'bind {self.completekey} rl_complete')
            else:
                command_string = f'{self.completekey}: complete'
            parse_and_bind(command_string)
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + '\n')
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    try:
                        line = input(self.prompt)
                    except EOFError:
                        line = 'exit'
                    except KeyboardInterrupt:
                        print('^C')
                        continue
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                set_completer(self.old_completer)

    def handle_help_on_command(self, command: str, line: str) -> bool:
        """Handle -h | --help command line argument"""
        if line.strip() in ('-h', '--help'):
            self.do_help(command)
            return True
        return False

    @continue_on_error
    def do_alias(self, line: str) -> None:
        """Create or delete an alias for a command.
        syntax:
            to set      : alias <name>=<command>
            to unset    : alias <name>=
            to show     : alias <name>
            to show all : alias
        examples:
            alias eval-all='for n in 1 to 100: init n --silent; eval --record; stack --silent; clear --silent'
        """
        if self.handle_help_on_command('alias', line):
            return
        alias_name, sep, alias_command = line.partition('=')
        if not alias_name:
            if not self.aliases:
                print('no aliases defined')
                return
            longest_name = max(len(name) for name in self.aliases)
            for alias_name, alias_command in self.aliases.items():
                print(f'{C_LBL}{alias_name:<{longest_name}} {C_TXT}-> {C_CMD}{alias_command}{RESET}')
            return
        alias_name = alias_name.strip()
        if not sep:
            if alias_command := self.aliases.get(alias_name, ''):
                print(f'{C_LBL}{alias_name} {C_TXT}-> {C_CMD}{alias_command}{RESET}')
            else:
                print(f'{BOLD}{RED}[not defined] {RESET}{C_LBL}{alias_name} {C_TXT}->{RESET}')
            return
        if not alias_command:
            if alias_command := self.aliases.pop(alias_name, ''):
                print(f'{BOLD}{RED}[removed] {RESET}{C_LBL}{alias_name} {C_TXT}-> {C_CMD}{alias_command}{RESET}')
            else:
                print(f'{BOLD}{RED}[not defined] {RESET}{C_LBL}{alias_name} {C_TXT}->{RESET}')
            return
        alias_command = alias_command.strip()
        self.aliases[alias_name] = alias_command
        print(f'{BOLD}{GREEN}[set] {RESET}{C_LBL}{alias_name} {C_TXT}-> {C_CMD}{alias_command}{RESET}')

    @continue_on_error
    def complete_alias(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Complete alias names before '=' and command names/args after '='."""
        pre = line[:begidx]
        eq_pos = pre.find('=')
        if eq_pos == -1:
            return [alias for alias in self.aliases if alias.startswith(text)]
        cmd_fragment = pre[eq_pos + 1:].lstrip()
        if ' ' not in cmd_fragment:
            return self.completenames(text)
        cmd_name = safe_split(cmd_fragment)[0]
        completer = getattr(self, f'complete_{cmd_name}', None)
        if completer is not None:
            synthetic_line = cmd_fragment + text
            synthetic_begidx = len(cmd_fragment)
            synthetic_endidx = synthetic_begidx + len(text)
            return completer(text, synthetic_line, synthetic_begidx, synthetic_endidx) or []
        return []

    @continue_on_error
    def do_echo(self, line: str) -> None:
        """Print the given text to the console"""
        if self.handle_help_on_command('echo', line):
            return
        print(line)

    def do_exit(self, line: str) -> bool | None:
        """ Exit the shell and return to the command line."""
        if self.handle_help_on_command('exit', line):
            return None
        return True

    @continue_on_error
    def do_for(self, line: str) -> None:
        """Use "for <var> in <start> to <end>: <cmd>; <cmd> <var>; ..." for looping"""
        if self.handle_help_on_command('for', line):
            return
        syntax = 'for <var> in <start> to <end>: <cmd>; <cmd> <var>; ...'
        header, sep, body = line.partition(':')
        if not sep:
            print(f'Syntax error: missing ":" — expected: {syntax}')
            return
        parts = header.split()
        if len(parts) != 5 or parts[1] != 'in' or parts[3] != 'to':
            print(f'Syntax error: invalid loop header "{header.strip()}" — expected: {syntax}')
            return
        var, _, start_s, _, end_s = parts
        try:
            start, end = int(start_s), int(end_s)
        except ValueError as e:
            print(f'Syntax error: {e} — start and end must be integers')
            return
        commands = [c.strip() for c in body.split(';') if c.strip()]
        if not commands:
            print(f'Syntax error: no commands after ":" — expected: {syntax}')
            return
        for n in range(start, end + 1):
            for cmd in commands:
                self.onecmd(re_sub(rf'\b{re_escape(var)}\b', str(n), cmd))

    @continue_on_error
    def complete_for(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Tab completion for the for loop command."""
        pre = line[:begidx]
        colon_pos = pre.find(':')
        if colon_pos == -1:
            # In the header: for <var> in <start> to <end>
            tokens = safe_split(pre)[1:]  # drop 'for'
            n = len(tokens)
            if n == 1:
                return ['in'] if 'in'.startswith(text) else []
            if n == 3:
                return ['to'] if 'to'.startswith(text) else []
        else:
            # In the body: complete command names or their arguments per ';' segment
            body_pre = pre[colon_pos + 1:]
            cmd_fragment = body_pre[body_pre.rfind(';') + 1:].lstrip()
            if ' ' not in cmd_fragment:
                return self.completenames(text)
            # Delegate to the command's own completer
            cmd_name = safe_split(cmd_fragment)[0]
            completer = getattr(self, f'complete_{cmd_name}', None)
            if completer is not None:
                synthetic_line = cmd_fragment + text
                synthetic_begidx = len(cmd_fragment)
                synthetic_endidx = synthetic_begidx + len(text)
                cmd_completer = completer(text, synthetic_line, synthetic_begidx, synthetic_endidx)
                return cmd_completer  # type: ignore [no-any-return]
        return []

    def do_help(self, arg: str) -> None:
        """Show help for all commands, or detailed help for a specific command."""
        if arg == '' or arg[0] == '?':
            print(self.banner)
            names = sorted(name[3:] for name in self.get_names() if name.startswith('do_'))
            col_w = max(len(n) for n in names) + 2
            cols = max(1, 100 // col_w)
            print(f'{CYAN}{"─" * 100}\n'
                  f'{C_LBL}{ColorCodes.UNDERLINE}Commands:{RESET}')
            num_rows = -(-len(names) // cols)  # ceil division
            rows = [[names[r + c * num_rows] for c in range(cols) if r + c * num_rows < len(names)]
                    for r in range(num_rows)]
            for row in rows:
                print(''.join(f'{C_CMD}{n:<{col_w}}{RESET}' for n in row))
            print(f'{CYAN}{"─" * 100}\n'
                  f'{C_LBL}{ColorCodes.UNDERLINE}Aliases:{RESET}')
            self.do_alias('')
            print(f'{CYAN}{"─" * 100}{RESET}')
        else:
            super().do_help(arg)

    @continue_on_error
    def do_shell(self, line: str) -> None:
        """Run a shell command: !<command>"""
        if self.handle_help_on_command('shell', line):
            return
        try:
            process = run(line, shell=True, check=True, cwd=self.workspace_dir)
        except CalledProcessError as e:
            result = e.returncode
            print(f'> {line} -> {RED}{result}{RESET}')
        else:
            result = process.returncode
            print(f'> {line} -> {GREEN if result == 0 else RED}{result}{RESET}')

    @continue_on_error
    def complete_shell(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Tab completion for shell (!) commands: executables for the first token, workspace files thereafter."""
        tokens = safe_split(line[:begidx])
        if len(tokens) <= 1:
            if len(tokens) == 1 and (tokens[0] == '!' or tokens[0] == 'shell'):
                return self.executable_names(text)
        return self.workspace_files(text)

    @staticmethod
    def completions_for_param(param_name: str, hints: dict, partial_val: str) -> list[str]:
        """Return tab-completion candidates for a named parameter given a partial value."""
        ann = hints.get(param_name)
        if ann is bool:
            return [v for v in ('true', 'false') if v.startswith(partial_val)]
        if ann is int and param_name == 'problem_number':
            return [v for p in problems if (v := str(p)).startswith(partial_val)]
        if get_origin(ann) is Literal:
            return [str(v) for v in get_args(ann) if str(v).startswith(partial_val)]
        return []

    @classmethod
    def executable_names(cls, text: str) -> list[str]:
        """Return executable names on PATH that start with allowed_prefixes, cached after the first call."""
        if not cls.exe_cache:
            names: set[str] = set()
            for path_dir in environ.get('PATH', '').split(':'):
                if not path_dir.startswith(cls.allowed_prefixes):
                    continue
                try:
                    for entry in Path(path_dir).iterdir():
                        if entry.is_file() and access(entry, X_OK):
                            names.add(entry.name)
                except OSError:
                    pass
            cls.exe_cache.extend(sorted(names))
        return [n for n in cls.exe_cache if n.startswith(text)]

    def workspace_files(self, text: str) -> list[str]:
        """Return filenames in the workspace directory that start with text."""
        try:
            return sorted(item.name for item in self.workspace_dir.iterdir() if item.name.startswith(text))
        except OSError:
            return []

    @classmethod
    def make_cmd(cls, f: Callable, /, *, name: str) -> None:
        """Build a do_<name> and complete_<name> Cmd method that parses CLI tokens and dispatches to func."""
        sig, hints, pos_params, var_positional, kw_params, func = func_info(f, workspace_dir=cls.workspace_dir)

        def token_processor(token: str, pos: int) -> Any:
            """Process a token from the command line."""
            if token == '--silent':
                return 's'
            if '=' in token:
                key, val = token.split('=', 1)
                norm_key = key.replace('-', '_')
                value = coerce(val, hints.get(norm_key, str))
                return 'k', norm_key, value
            if token.startswith('--'):
                key = token[2:].replace('-', '_')
                if key.startswith('no-') or key.startswith('no_'):
                    return 'k', key[3:], False
                return 'k', key, True
            if pos < len(pos_params):
                return 'a', coerce(token, hints.get(pos_params[pos].name, str))
            if var_positional is not None:
                return 'a', coerce(token, hints.get(var_positional.name, str))
            raise TypeError(f'{name}() takes {len(pos_params)} argument(s) but got extra: {token!r}')

        def do_cmd(self: SolverShell, line: str) -> None:
            if self.handle_help_on_command(name, line):
                return
            try:
                tokens = safe_split(line)
                args: list[Any] = []
                kwargs: dict[str, Any] = {}
                silent: bool = False
                pos = 0
                for token in tokens:
                    match token_processor(token, pos):
                        case ('a', val):
                            args.append(val)
                            pos += 1
                        case ('k', var, val):
                            kwargs[var] = val
                        case 's':
                            silent = True
                if silent:
                    with open(devnull, 'w') as _devnull, redirect_stdout(_devnull):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                if result:
                    print(f'> {format_command_line(name, args, kwargs)} -> {result!s}')
            except KeyboardInterrupt:
                print('^C')
            except Exception as e:
                self.do_help(name)
                print(f'Error: {e!s}')

        @continue_on_error
        def complete_cmd(self: SolverShell, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
            pre = line[:begidx]
            kw_match = re_search(r'(\w+)=$', pre)
            if kw_match:
                return self.completions_for_param(kw_match.group(1), hints, text)
            tokens = safe_split(pre)[1:]
            pos_count = sum(1 for t in tokens if '=' not in t and not t.startswith('--'))
            completions: list[str] = []
            if text.startswith('--'):
                if '--silent'.startswith(text):
                    completions.append('--silent')
                for p in kw_params:
                    if hints.get(p.name) is bool:
                        completions.extend(bool_flags(p.name, text))
            else:
                if pos_count < len(pos_params):
                    completions.extend(self.completions_for_param(pos_params[pos_count].name, hints, text))
                elif var_positional is not None:
                    completions.extend(self.completions_for_param(var_positional.name, hints, text))
                if '--silent'.startswith(text):
                    completions.append('--silent')
                for p in kw_params:
                    kw_sug = f'{p.name}='
                    if kw_sug.startswith(text):
                        completions.append(kw_sug)
                    if hints.get(p.name) is bool:
                        completions.extend(bool_flags(p.name, text))
            return completions

        do_cmd.__name__ = f'do_{name}'
        complete_cmd.__name__ = f'complete_{name}'
        if isinstance(func, partial):
            do_cmd.__doc__ = f'{name}{sig}\n{getattr(func.func, "__doc__", None) or ""}'
        else:
            do_cmd.__doc__ = f'{name}{sig}\n{getattr(func, "__doc__", None) or ""}'
        setattr(cls, do_cmd.__name__, do_cmd)
        setattr(cls, complete_cmd.__name__, complete_cmd)


_commands: dict[str, Callable] = {
    'clear': clear_the_workspace,
    'eval': evaluate,
    'full-stack-backup': backup_the_stack,
    'full-stack-restore': restore_the_stack,
    'init': init_the_workspace,
    'ls': list_the_workspace,
    'problems': partial(show_value, problems),
    'rekey': rekey,
    'stack': stack_the_workspace,
    'upload_keys': upload_keys,
    'user': user,
}

_aliases: dict[str, str] = {
    'eval-pub': 'for n in 1 to 100: init n --silent; eval --record; clear --silent; echo evaluated n',
    'eval-show': 'for n in 1 to 100: init n --silent; eval --show; clear --silent; echo evaluated n',
    'gh-login': 'shell gh auth status || gh auth login',
    'gh-status': 'shell gh auth status',
    'git-add-stack': f'shell git add {stack_dir.as_posix()}/',
    'git-merge': 'shell git fetch origin && git merge --ff-only origin/master',
    'git-status': 'shell git status | less',
    'pre-commit': 'shell pre-commit run --all-files',
    'restack': f'for n in 1 to {max(p.number for p in problems)}: init n --silent; clear; echo restacked n',
}


def cli(
        commands: dict[str, Callable] | None = None,
        aliases: dict[str, str] | None = None,
        capture: bool = True,
) -> int:
    """Configure and launch the solver shell.

    Registers commands and aliases on SolverShell, then parses argv to extract any
    startup commands before entering the interactive loop.

    Args:
        commands: Mapping of command names to callables. Defaults to the built-in
                  command set (_commands) when None.
        aliases:  Mapping of alias names to command strings. Defaults to the built-in
                  alias set (_aliases) when None.
        capture:  Whether to capture stdout to a file. Defaults to True.
    Command-line usage (argv parsing):
        solver                      # interactive shell
        solver "cmd"                # run cmd, then stay interactive
        solver "cmd1; cmd2"         # run cmd1 then cmd2, then stay interactive
        solver -c "cmd1; cmd2"      # run cmd1 then cmd2, then exit

    The -c flag must be the first argument; the command string must be a single
    quoted argument (the shell interprets bare semicolons before the process sees
    them). Only one command string is accepted — additional argv tokens are ignored.

    Returns:
        0 on clean exit.
    """
    for name, func in (commands or _commands).items():
        SolverShell.make_cmd(func, name=name)
    for name, alias in (aliases or _aliases).items():
        SolverShell.aliases[name] = alias
    i: int = 1 + int(argv[1:2] == ['-c'])
    startup_commands = [c for r in ' '.join(argv[i:i + 1]).split(';') if (c := r.strip())]
    if startup_commands and i == 1:
        startup_commands.append('exit')
    if capture:
        with SessionCapture(SolverShell()) as session:
            return session.solver.execute(commands=startup_commands or None)
    else:
        return SolverShell().execute(commands=startup_commands or None)


if __name__ == '__main__':
    raise SystemExit(cli())
