#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""Interactive solver shell with persistent history and command dispatch."""
from __future__ import annotations

from cmd import Cmd
from contextlib import redirect_stdout
from functools import partial
from inspect import get_annotations, signature
from os import X_OK, access, devnull, environ
from pathlib import Path
from re import escape as re_escape, search as re_search, sub as re_sub
from readline import (add_history, backend as readline_backend, clear_history, get_completer,
                      get_completer_delims, get_current_history_length, get_history_item,
                      parse_and_bind, read_history_file, set_completer, set_completer_delims, set_history_length,
                      write_history_file)
from shlex import split
from sys import argv
from typing import Any, Callable, Literal, NamedTuple, get_args, get_origin

from solver.config import ColorCodes, root_dir, stack_dir, workspace_dir
from solver.crypto import rekey, user
from solver.evaluate import evaluate
from solver.problems import problems
from solver.stack import backup_the_stack, restore_the_stack
from solver.utils import continue_on_error, format_command_line, run_command, show_value, upload_keys
from solver.workspace import clear_the_workspace, init_the_workspace, list_the_workspace, stack_the_workspace

__all__ = ['SolverShell', 'cli']

C, G, Y, B, D, R = (ColorCodes.CYAN, ColorCodes.GREEN, ColorCodes.YELLOW,
                    ColorCodes.BLUE, ColorCodes.GRAY, ColorCodes.RESET)


class FuncInfo(NamedTuple):
    """Cached inspection of a callable's signature and categorized parameters."""
    sig: Any
    hints: dict[str, Any]
    pos_params: list[Any]
    var_positional: Any
    kw_params: list[Any]


class SolverShell(Cmd):
    """The solver shell."""
    aliases: dict[str, str] = {}
    allowed_prefixes: tuple[str, ...] = ('/bin', '/sbin', '/usr', '/home')
    identchars: str = Cmd.identchars + ':-'
    doc_header: str = 'Commands:'
    exe_cache: list[str] = []
    func_info_cache: dict[str, FuncInfo] = {}
    history_file: Path = root_dir / '.solver_history'
    last_result: Any = None
    post: Any | None = None
    pre: Any | None = None
    prompt: str = 'euler$ '

    def execute(self,
                intro: Any | None = None,
                pre: str | None = None,
                post: str | None = None,
                commands: list[str] | None = None,
                ) -> int:
        """Run the shell session, invoking the 'pre/post' method hooks by name, and return 0 on clean exit."""
        if pre:
            self.pre = pre
        if post:
            self.post = post
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
        lw, cw = 7, 31  # label column width, command column width
        print(f'{C}{"─" * 100}{R}')
        print(f'{G}{ColorCodes.BOLD}Project Euler Solver Shell{R}')
        print(f'{C}{"─" * 100}{R}')
        print(f'{Y}{"Help":<{lw}}{R}  {B}{"? | help | <cmd> -h":<{cw}}{R}  '
              f'{D}list commands or describe a specific command{R}')
        print(f'{Y}{"Exit":<{lw}}{R}  {B}Ctrl-D | exit{R}')
        print(f'{Y}{"Launch":<{lw}}{R}  {B}{"solver \"cmd1; cmd2\"":<{cw}}{R}  '
              f'{D}preload commands and stay interactive{R}')
        print(f'{" ":<{lw}}  {B}{"solver -c \"cmd1; cmd2\"":<{cw}}{R}  '
              f'{D}preload commands and exit when done{R}')
        print(f'{Y}{"Flags":<{lw}}{R}  {B}{"--key-word | --no-key-word":<{cw}}{R}  '
              f'{D}boolean True / False{R}')
        print(f'{" ":<{lw}}  {B}{"--silent":<{cw}}{R}  '
              f'{D}suppress command output{R}')
        self.do_help('')
        if isinstance(self.pre, str) and (cmd := getattr(self, self.pre, None)):
            cmd('')
            print(f'{C}{"─" * 100}{R}')

    def postloop(self) -> None:
        """Deduplicate, cap at 1000 entries, and persist readline history when the command loop exits."""
        self.dedup_history()
        set_history_length(1000)
        write_history_file(self.history_file)
        print(f'\n{C}{"─" * 100}{R}')
        print(f'{G}{ColorCodes.BOLD}Session complete — goodbye!{R}')
        if isinstance(self.post, str) and (cmd := getattr(self, self.post, None)):
            cmd('')
        print(f'{C}{"─" * 100}{R}')

    def do_help(self, arg: str) -> None:
        if arg == '':
            names = sorted(name[3:] for name in self.get_names() if name.startswith('do_'))
            col_w = max(len(n) for n in names) + 2
            cols = max(1, 100 // col_w)
            print(f'{C}{"─" * 100}{R}')
            print(f'{Y}Commands:{R}')
            rows = [names[i:i + cols] for i in range(0, len(names), cols)]
            for row in rows:
                print(''.join(f'{G}{n:<{col_w}}{R}' for n in row))
            print(f'{C}{"─" * 100}{R}')
            print(f'{Y}Aliases:{R}')
            self.do_alias('')
            print(f'{C}{"─" * 100}{R}')
        else:
            super().do_help(arg)

    def completenames(self, text: str, *ignored: Any) -> list[str]:
        """Return command names and alias names that start with text."""
        return super().completenames(text, *ignored) + [a for a in self.aliases if a.startswith(text)]

    def precmd(self, line: str) -> str:
        """Expand aliases before execution: exact match first, then first-word match."""
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

    @staticmethod
    def dedup_history() -> None:
        """Remove duplicate entries from readline history, keeping the most recent occurrence of each."""
        length = get_current_history_length()
        items = [get_history_item(i) for i in range(1, length + 1)]
        seen: set[str] = set()
        unique: list[str] = []
        for item in reversed(items):
            if item not in seen:
                seen.add(item)
                unique.append(item)
        clear_history()
        for item in reversed(unique):
            add_history(item)

    def do_exit(self, line: str) -> bool | None:
        """ Exit the shell and return to the command line."""
        if line.strip() in ('-h', '--help'):
            self.do_help('exit')
            return None
        return True

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
        if line.strip() in ('-h', '--help'):
            self.do_help('alias')
            return
        alias_name, sep, alias_command = line.partition('=')
        if not alias_name:
            longest_name = max(len(name) for name in self.aliases)
            for alias_name, alias_command in self.aliases.items():
                print(f'{Y}{alias_name:<{longest_name}}{R}  {D}->{R}  {B}{alias_command}{R}')
            return
        alias_name = alias_name.strip()
        if not sep:
            if alias_command := self.aliases.get(alias_name, ''):
                print(f'{Y}{alias_name}{R}  {D}->{R}  {B}{alias_command}{R}')
            return
        if not alias_command:
            if alias_command := self.aliases.pop(alias_name, ''):
                print(f'{ColorCodes.RED}removed{R}  {Y}{alias_name}{R}  {D}->{R}  {alias_command}')
            return
        alias_command = alias_command.strip()
        self.aliases[alias_name] = alias_command
        print(f'{G}set{R}  {Y}{alias_name}{R}  {D}->{R}  {B}{alias_command}{R}')

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
        cmd_name = self.safe_split(cmd_fragment)[0]
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
        print(line)

    @continue_on_error
    def do_for(self, line: str) -> None:
        """Use "for <var> in <start> to <end>: <cmd>; <cmd> <var>; ..." for looping"""
        if line.strip() in ('-h', '--help'):
            self.do_help('for')
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
            tokens = self.safe_split(pre)[1:]  # drop 'for'
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
            cmd_name = self.safe_split(cmd_fragment)[0]
            completer = getattr(self, f'complete_{cmd_name}', None)
            if completer is not None:
                synthetic_line = cmd_fragment + text
                synthetic_begidx = len(cmd_fragment)
                synthetic_endidx = synthetic_begidx + len(text)
                cmd_completer = completer(text, synthetic_line, synthetic_begidx, synthetic_endidx)
                return cmd_completer  # type: ignore [no-any-return]
        return []

    @continue_on_error
    def do_shell(self, line: str) -> None:
        """Run a bash command: !<command>"""
        if line.strip() in ('-h', '--help'):
            self.do_help('shell')
            return
        result = run_command(line, cwd=workspace_dir, silent=False)
        if result:
            print(result)
        self.last_result = result

    @continue_on_error
    def complete_shell(self, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        """Tab completion for shell (!) commands: executables for the first token, workspace files thereafter."""
        tokens = self.safe_split(line[:begidx])
        if len(tokens) <= 1:
            if len(tokens) == 1 and (tokens[0] == '!' or tokens[0] == 'shell'):
                return self.executable_names(text)
        return self.workspace_files(text)

    @classmethod
    def inspect_func(cls, name: str, func: Callable) -> FuncInfo:
        """Return cached signature metadata for func, computing it on first access."""
        if name not in cls.func_info_cache:
            sig = signature(func)
            try:
                hints = get_annotations(func, eval_str=True)
            except NameError:
                hints = {}
            params = list(sig.parameters.values())
            cls.func_info_cache[name] = FuncInfo(
                sig=sig,
                hints=hints,
                pos_params=[p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)],
                var_positional=next((p for p in params if p.kind == p.VAR_POSITIONAL), None),
                kw_params=[p for p in params if p.kind in (p.KEYWORD_ONLY, p.POSITIONAL_OR_KEYWORD)],
            )
        return cls.func_info_cache[name]

    @staticmethod
    def coerce(value: str, annotation: Any) -> Any:
        """Coerce a raw string token to the type described by annotation."""
        if annotation is bool:
            return value.lower() in ('true', '1', 'yes')
        if annotation is int:
            try:
                return int(value.split(':')[0]) if ':' in value else int(value)
            except ValueError:
                return value
        if get_origin(annotation) is Literal:
            allowed = get_args(annotation)
            if value not in allowed:
                raise ValueError(f'got unexpected val {value!r}, expected one of {allowed}')
        return value

    @staticmethod
    def safe_split(s: str) -> list[str]:
        """Split a shell-style string, falling back to str.split on parse errors."""
        try:
            return split(s)
        except ValueError:
            return s.split()

    @staticmethod
    def bool_flags(p_name: str, text: str) -> list[str]:
        """Return --<name> and --no-<name> flag suggestions that start with text."""
        flag, no_flag = f'--{p_name.replace("_", "-")}', f'--no-{p_name.replace("_", "-")}'
        return [f for f in (flag, no_flag) if f.startswith(text)]

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

    @staticmethod
    def workspace_files(text: str) -> list[str]:
        """Return filenames in the workspace directory that start with text."""
        try:
            return sorted(item.name for item in workspace_dir.iterdir() if item.name.startswith(text))
        except OSError:
            return []

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


def make_do(name: str, func: Callable) -> Callable:
    """Build a do_<name> Cmd method that parses CLI tokens and dispatches to func."""
    cls = SolverShell
    sig, hints, pos_params, var_positional, _ = cls.inspect_func(name, func)

    def token_processor(token: str, pos: int) -> Any:
        """Process a token from the command line."""
        if token == '--silent':
            return 's'
        if '=' in token:
            key, val = token.split('=', 1)
            norm_key = key.replace('-', '_')
            value = cls.coerce(val, hints.get(norm_key, str))
            return 'k', norm_key, value
        if token.startswith('--'):
            key = token[2:].replace('-', '_')
            if key.startswith('no-') or key.startswith('no_'):
                return 'k', key[3:], False
            return 'k', key, True
        if pos < len(pos_params):
            return 'a', cls.coerce(token, hints.get(pos_params[pos].name, str))
        if var_positional is not None:
            return 'a', cls.coerce(token, hints.get(var_positional.name, str))
        raise TypeError(f'{name}() takes {len(pos_params)} argument(s) but got extra: {token!r}')

    def do_cmd(self: SolverShell, line: str) -> None:
        try:
            tokens = self.safe_split(line)
            if '-h' in tokens or '--h' in tokens or '--help' in tokens:
                self.do_help(name)
                return
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
            self.last_result = result
        except KeyboardInterrupt:
            print('^C')
        except Exception as e:
            self.do_help(name)
            print(f'Error: {e!s}')

    do_cmd.__name__ = f'do_{name}'
    if isinstance(func, partial) and func.func.__name__ == show_value.__name__:
        do_cmd.__doc__ = f'Show the value of "{name}"'
    else:
        do_cmd.__doc__ = f'{name}{sig}\n{getattr(func, "__doc__", ) or ""}'
    return do_cmd


def make_complete(name: str, func: Callable) -> Callable:
    """Build a complete_<name> Cmd method for tab-completion of func's arguments."""
    cls = SolverShell
    sig, hints, pos_params, var_positional, kw_params = cls.inspect_func(name, func)

    @continue_on_error
    def complete_cmd(self: SolverShell, text: str, line: str, begidx: int, _endidx: int) -> list[str]:
        pre = line[:begidx]
        kw_match = re_search(r'(\w+)=$', pre)
        if kw_match:
            return self.completions_for_param(kw_match.group(1), hints, text)
        tokens = self.safe_split(pre)[1:]
        pos_count = sum(1 for t in tokens if '=' not in t and not t.startswith('--'))
        completions: list[str] = []
        if text.startswith('--'):
            if '--silent'.startswith(text):
                completions.append('--silent')
            for p in kw_params:
                if hints.get(p.name) is bool:
                    completions.extend(self.bool_flags(p.name, text))
        else:
            if pos_count < len(pos_params):
                completions.extend(self.completions_for_param(pos_params[pos_count].name, hints, text))
            elif var_positional is not None:
                completions.extend(self.completions_for_param(var_positional.name, hints, text))
            for p in kw_params:
                kw_sug = f'{p.name}='
                if kw_sug.startswith(text):
                    completions.append(kw_sug)
                if hints.get(p.name) is bool:
                    completions.extend(self.bool_flags(p.name, text))
        return completions

    complete_cmd.__name__ = f'complete_{name}'
    return complete_cmd


def make_shell_command(name: str, command: str) -> Callable:
    """Wrap a fixed shell command as a zero-argument callable that runs in the workspace."""

    @continue_on_error
    def run() -> None:
        result = run_command(command, cwd=workspace_dir)
        if result:
            print(result)

    run.__doc__ = f'{name}: shell command wrapper for "{command}"'
    return run


_commands: dict[str, Callable] = {
    'eval': evaluate,
    'full-stack-backup': backup_the_stack,
    'full-stack-restore': restore_the_stack,
    'gh-login': make_shell_command('gh-login', 'gh auth status || gh auth login'),
    'gh-status': make_shell_command('gh-status', 'gh auth status'),
    'git-add-stack': make_shell_command('add', f'git add {stack_dir.as_posix()}/'),
    'git-merge': make_shell_command('git-merge', 'git fetch origin && git merge --ff-only origin/master'),
    'git-status': make_shell_command('git-status', 'git status'),
    'init': init_the_workspace,
    'ls': list_the_workspace,
    'problems': partial(show_value, problems),
    'rekey': rekey,
    'stack': stack_the_workspace,
    'stack-clear': clear_the_workspace,
    'upload_keys': upload_keys,
    'user': user,
}

_aliases: dict[str, str] = {
    'eval-pub': ('for n in 1 to 100: '
                 'init n --silent; '
                 'eval --record; '
                 'stack-clear --silent; '
                 'echo processed n'),
    'restack': (f'for n in 1 to {max(problems, key=lambda p: p.number).number}: '
                'init n; '
                'stack-clear --silent; '
                'echo processed n'),
    'pre-commit': 'shell pre-commit run --all-files'
}


def cli(
        commands: dict[str, Callable] | None = None,
        aliases: dict[str, str] | None = None,
        pre: str | None = None,
        post: str | None = 'do_ls',
) -> int:
    """Configure and launch the solver shell.

    Registers commands and aliases on SolverShell, then parses argv to extract any
    startup commands before entering the interactive loop.

    Args:
        commands: Mapping of command names to callables. Defaults to the built-in
                  command set (_commands) when None.
        aliases:  Mapping of alias names to command strings. Defaults to the built-in
                  alias set (_aliases) when None.
        pre:      Name of a do_<pre> method to invoke during preloop, before the
                  prompt appears. Defaults to None (no pre-hook).
        post:     Name of a do_<post> method to invoke during postloop, after the
                  session ends. Defaults to 'do_ls'.

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
    commands = commands or _commands
    aliases = aliases or _aliases
    for name, func in commands.items():
        setattr(SolverShell, f'do_{name}', make_do(name, func))
        setattr(SolverShell, f'complete_{name}', make_complete(name, func))
    for name, alias in aliases.items():
        SolverShell.aliases[name] = alias
    setattr(SolverShell, 'pre', pre)
    setattr(SolverShell, 'post', post)

    i: int = 1 + int(argv[1:2] == ['-c'])
    startup_commands = [c for r in ' '.join(argv[i:i + 1]).split(';') if (c := r.strip())]
    if startup_commands and i == 2:
        startup_commands.append('exit')
    return SolverShell().execute(commands=startup_commands or None)


if __name__ == '__main__':
    raise SystemExit(cli())
